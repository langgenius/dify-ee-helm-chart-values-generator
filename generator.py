"""Values Generator - Core class for generating Helm Chart values"""

import os
import sys
import re
import yaml
from typing import Dict, Any, Optional

from utils import print_success, print_error, print_info, print_header, print_warning, prompt, prompt_yes_no
from version_manager import VersionManager
from i18n import get_translator
import config

_t = get_translator()


class ValuesGenerator:
    """Values generator"""

    def __init__(self, source_file: str, version: Optional[str] = None):
        """Initialize"""
        self.source_file = source_file
        self.values = {}
        self.yaml_data = None  # ruamel.yaml data object (preserves comments and format)
        self.yaml_loader = None  # ruamel.yaml loader instance
        self.version = version or "3.0"  # Default version
        self.version_modules = VersionManager.get_version_modules(self.version)
        self.load_template()

    def load_template(self):
        """Load template file"""
        try:
            # Must use ruamel.yaml
            from ruamel.yaml import YAML

            self.yaml_loader = YAML()
            self.yaml_loader.preserve_quotes = True
            self.yaml_loader.width = 120
            self.yaml_loader.indent(mapping=2, sequence=4)
            self.yaml_loader.default_flow_style = False
            self.yaml_loader.default_style = None  # Preserve original style

            # Read original file (preserves comments and format)
            with open(self.source_file, 'r', encoding='utf-8') as f:
                self.yaml_data = self.yaml_loader.load(f)

            # Also load as standard dict for configuration logic
            with open(self.source_file, 'r', encoding='utf-8') as f:
                self.values = yaml.safe_load(f)

            print_success(f"{_t('template_loaded')}: {self.source_file} ({_t('using_ruamel')})")

        except ImportError:
            print_error(_t('ruamel_not_installed'))
            print_error(_t('install_ruamel'))
            sys.exit(1)
        except Exception as e:
            print_error(f"{_t('load_template_failed')}: {e}")
            sys.exit(1)

    def set_value(self, key_path: str, value: Any) -> None:
        """
        Set value (updates both yaml_data and values)

        Args:
            key_path: Key path, e.g. 'global.appSecretKey'
            value: New value
        """
        keys = key_path.split('.')

        # Update standard dict
        current = self.values
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value

        # Update ruamel.yaml data object
        if self.yaml_data is not None:
            try:
                from ruamel.yaml.comments import CommentedMap
                current = self.yaml_data
                for key in keys[:-1]:
                    if key not in current:
                        current[key] = CommentedMap()
                    current = current[key]
                current[keys[-1]] = value
            except Exception:
                # If update fails, at least standard dict is updated
                pass

    def save(self, output_file: str):
        """
        Save to file - uses ruamel.yaml to preserve comments and format
        """
        try:
            # Must use ruamel.yaml
            from ruamel.yaml import YAML

            # If yaml_loader exists, use it; otherwise create new one
            if self.yaml_loader is None:
                yaml_loader = YAML()
                yaml_loader.preserve_quotes = True
                yaml_loader.width = 120
                yaml_loader.indent(mapping=2, sequence=4)
                yaml_loader.default_flow_style = False
                yaml_loader.default_style = None  # Preserve original style

                # Reload original file (preserves comments and format)
                with open(self.source_file, 'r', encoding='utf-8') as f:
                    data = yaml_loader.load(f)
            else:
                # Use loaded data, or reload to ensure latest
                if self.yaml_data is not None:
                    data = self.yaml_data
                else:
                    with open(self.source_file, 'r', encoding='utf-8') as f:
                        data = self.yaml_loader.load(f)
                yaml_loader = self.yaml_loader

            # Recursively update values (apply self.values changes to data)
            self._update_dict_recursive(data, self.values)

            # Save
            with open(output_file, 'w', encoding='utf-8') as f:
                yaml_loader.dump(data, f)

            print_success(f"{_t('config_saved_to')}: {output_file}")
            print_info(_t('format_preserved'))

        except ImportError:
            print_error(_t('ruamel_not_installed'))
            print_error(_t('install_ruamel'))
            sys.exit(1)
        except Exception as e:
            print_error(f"{_t('save_failed')}: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    def _update_dict_recursive(self, target: dict, source: dict):
        """Recursively update dict, preserving ruamel.yaml format and comments"""
        # Must use ruamel.yaml
        from ruamel.yaml.scalarstring import ScalarString, DoubleQuotedScalarString, SingleQuotedScalarString
        from ruamel.yaml.comments import CommentedMap, CommentedSeq

        for key, value in source.items():
            if key in target:
                if isinstance(value, dict) and isinstance(target[key], dict):
                    self._update_dict_recursive(target[key], value)
                elif isinstance(value, list) and isinstance(target[key], list):
                    # Handle list - only update when value actually changes
                    if value != target[key]:
                        target[key] = value
                else:
                    # Get actual value of original (remove ScalarString wrapper)
                    original_actual_value = target[key]
                    if isinstance(original_actual_value, ScalarString):
                        original_actual_value = str(original_actual_value)

                    # Only update when value actually changes, preserve original format and comments
                    if str(value) != str(original_actual_value):
                        # Update scalar value, preserve original quote format
                        original_value = target[key]
                        new_value = value

                        # Check if original value has quote format
                        if isinstance(original_value, DoubleQuotedScalarString):
                            # Original has double quotes, new value should also have double quotes
                            new_value = DoubleQuotedScalarString(str(value))
                        elif isinstance(original_value, SingleQuotedScalarString):
                            # Original has single quotes, new value should also have single quotes
                            new_value = SingleQuotedScalarString(str(value))
                        elif isinstance(original_value, ScalarString):
                            # Original is other type of ScalarString, preserve format
                            new_value = type(original_value)(str(value))
                        elif isinstance(value, str) and isinstance(original_value, str):
                            # Original is plain string, new value is also string
                            # If new value contains special characters, use double quotes for format consistency
                            needs_quotes = (
                                ':' in value or
                                '/' in value or
                                ' ' in value or
                                value.startswith('*') or
                                value.startswith('#') or
                                value == '' or
                                value.startswith('http://') or
                                value.startswith('https://') or
                                value.endswith('.local') or
                                value.endswith('.ai') or
                                value.endswith('.com') or
                                value.endswith('.tech') or
                                '+' in value or  # base64 strings usually contain +
                                '=' in value     # base64 strings usually contain =
                            )

                            if needs_quotes:
                                new_value = DoubleQuotedScalarString(value)
                            # Otherwise keep plain string format (direct assignment, ruamel.yaml will handle automatically)

                        target[key] = new_value
                    # If value hasn't changed, don't update, preserve original format, comments and quotes

    def _save_with_text_replacement(self, output_file: str):
        """Save using text replacement method, preserve comments and format"""
        # First copy template file
        content = self.template_content

        # Get original values for comparison
        with open(self.source_file, 'r', encoding='utf-8') as f:
            original_data = yaml.safe_load(f)

        # Find all values that need updating
        def find_changes(new_dict: dict, old_dict: dict, path: str = ""):
            changes = []
            for k, v in new_dict.items():
                current_path = f"{path}.{k}" if path else k
                if k not in old_dict:
                    changes.append((current_path, v))
                elif isinstance(v, dict) and isinstance(old_dict[k], dict):
                    changes.extend(find_changes(v, old_dict[k], current_path))
                elif v != old_dict[k]:
                    changes.append((current_path, v))
            return changes

        changes = find_changes(self.values, original_data)

        # Text replacement for each change
        for path, new_value in changes:
            keys = path.split('.')

            # Build regex matching pattern
            if len(keys) == 1:
                # Simple key: match "key: value" format
                # Need to handle multi-line values (like comments, multi-line strings)
                pattern = rf'^(\s*){re.escape(keys[0])}\s*:(.*?)(?=\n\s*\w+\s*:|\n\s*$|\Z)'

                def replace_func(match):
                    indent = match.group(1)
                    old_value_part = match.group(2)

                    # Generate new value
                    if new_value is None:
                        return f"{indent}{keys[0]}:"
                    elif isinstance(new_value, str):
                        # Check if original value has quotes
                        old_stripped = old_value_part.strip()
                        has_quotes = old_stripped.startswith('"') or old_stripped.startswith("'")
                        # Check if quotes are needed
                        needs_quotes = (has_quotes or new_value == '' or
                                       ':' in new_value or new_value.startswith('*') or
                                       new_value.startswith('#') or ' ' in new_value)
                        if needs_quotes:
                            return f"{indent}{keys[0]}: \"{new_value}\""
                        else:
                            return f"{indent}{keys[0]}: {new_value}"
                    elif isinstance(new_value, bool):
                        return f"{indent}{keys[0]}: {str(new_value).lower()}"
                    elif isinstance(new_value, (int, float)):
                        return f"{indent}{keys[0]}: {new_value}"
                    elif isinstance(new_value, list):
                        if len(new_value) == 0:
                            return f"{indent}{keys[0]}: []"
                        else:
                            result = f"{indent}{keys[0]}:\n"
                            for item in new_value:
                                if isinstance(item, dict):
                                    for k, v in item.items():
                                        result += f"{indent}  {k}: {v}\n"
                                else:
                                    result += f"{indent}  - {item}\n"
                            return result.rstrip()
                    else:
                        return f"{indent}{keys[0]}: {new_value}"

                # Use multi-line mode matching
                content = re.sub(pattern, replace_func, content, flags=re.MULTILINE | re.DOTALL)

        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print_success(f"{_t('config_saved_to')}: {output_file}")
        print_warning(_t('text_replacement_warning'))

    def generate(self):
        """Generate configuration"""
        from modules import (
            configure_global,
            configure_infrastructure,
            configure_networking,
            configure_mail,
            configure_plugins,
            configure_services,
        )

        print_header(_t('generator_title'))
        print_info(_t('guide_message'))
        print_info(f"{_t('target_version')}: {VersionManager.get_version_info(self.version).get('name', self.version)}")
        print_info(_t('press_ctrl_c'))

        try:
            # Dynamically configure modules based on version
            module_configs = {
                "global": configure_global,
                "infrastructure": configure_infrastructure,
                "networking": configure_networking,
                "mail": configure_mail,
                "plugins": configure_plugins,
                "services": configure_services,
            }

            # Configure each module in order (based on version support)
            for module_name in self.version_modules:
                if module_name in module_configs:
                    module_configs[module_name](self)
                else:
                    print_warning(f"{_t('module_not_found')} '{module_name}', {_t('skipping')}")

            # Save file
            output_file = config.OUTPUT_FILE
            if os.path.exists(output_file):
                overwrite_prompt = f"{output_file} {_t('file_exists_overwrite')}"
                if not prompt_yes_no(overwrite_prompt, default=False):
                    output_file = prompt(_t('enter_new_filename'), default=config.OUTPUT_FILE, required=False)
                    if not output_file:
                        output_file = config.OUTPUT_FILE

            self.save(output_file)

            print_header(_t('config_complete'))
            print_success(f"{_t('config_saved_to')}: {output_file}")
            print_info(_t('check_and_adjust'))
            print_info(_t('helm_install_command'))

        except KeyboardInterrupt:
            print("\n\n")
            print_warning(_t('user_interrupted'))
            if prompt_yes_no(_t('save_progress'), default=False):
                partial_output = config.OUTPUT_FILE.replace('.yaml', '-partial.yaml')
                output_file = prompt(_t('enter_filename'), default=partial_output, required=False)
                if output_file:
                    self.save(output_file)
                    print_success(f"{_t('partial_config_saved')}: {output_file}")
            sys.exit(0)
        except Exception as e:
            print_error(f"{_t('generation_error')}: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
