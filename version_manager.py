"""Version management for Dify EE"""

import sys
from typing import Dict, Any, Optional

from utils import Colors, print_header, print_info, print_success, print_error, print_warning
from i18n import get_translator

_t = get_translator()


class VersionManager:
    """Version manager - manages Dify EE configuration modules for different versions"""

    # Version configuration: defines modules supported by each version
    VERSION_CONFIGS = {
        "3.0": {
            "name": "Dify Enterprise Edition 3.0",
            "modules": [
                "global",
                "infrastructure",
                "networking",
                "mail",
                "plugins",  # Version 3.0 supports plugin module
                "services"
            ],
            "description": "Full version with plugin support"
        },
        "2.0": {
            "name": "Dify Enterprise Edition 2.0",
            "modules": [
                "global",
                "infrastructure",
                "networking",
                "mail",
                # Version 2.0 does not support plugin module
                "services"
            ],
            "description": "Version without plugin support"
        },
        # More version configurations can be added here
    }

    @classmethod
    def get_available_versions(cls) -> list:
        """Get list of available versions"""
        return list(cls.VERSION_CONFIGS.keys())

    @classmethod
    def get_version_info(cls, version: str) -> Optional[Dict[str, Any]]:
        """Get version information"""
        return cls.VERSION_CONFIGS.get(version)

    @classmethod
    def get_version_modules(cls, version: str) -> list:
        """Get list of modules supported by version"""
        config = cls.get_version_info(version)
        if config:
            return config.get("modules", [])
        return []

    @classmethod
    def is_module_supported(cls, version: str, module: str) -> bool:
        """Check if version supports a module"""
        modules = cls.get_version_modules(version)
        return module in modules

    @classmethod
    def prompt_version_selection(cls) -> str:
        """Interactive version selection"""
        print_header(_t('select_dify_version'))
        print_info(_t('select_version_prompt'))
        print()

        versions = cls.get_available_versions()
        version_options = []

        for i, version in enumerate(versions, 1):
            config = cls.get_version_info(version)
            name = config.get("name", f"Version {version}")
            desc = config.get("description", "")
            modules = config.get("modules", [])

            print(f"  {i}. {name}")
            print(f"     {_t('version')}: {version}")
            if desc:
                print(f"     {_t('description')}: {desc}")
            print(f"     {_t('supported_modules')}: {', '.join(modules)}")
            print()

            version_options.append(version)

        while True:
            try:
                default_text = _t('default')
                choice = input(f"{Colors.BOLD}{_t('select_version_range')} [1-{len(versions)}] ({default_text}: 1): {Colors.ENDC}").strip()

                if not choice:
                    choice = "1"

                idx = int(choice) - 1
                if 0 <= idx < len(versions):
                    selected_version = version_options[idx]
                    config = cls.get_version_info(selected_version)
                    print_success(f"{_t('selected')}: {config.get('name', selected_version)}")
                    return selected_version
                else:
                    range_text = _t('enter_number_range')
                    print_error(f"{_t('invalid_selection')} {range_text} 1-{len(versions)}")
            except ValueError:
                print_error(_t('enter_valid_number'))
            except KeyboardInterrupt:
                print("\n")
                print_warning(_t('user_interrupted'))
                sys.exit(0)

    @classmethod
    def detect_version_from_values(cls, values: Dict[str, Any]) -> Optional[str]:
        """Detect version from values.yaml if possible"""
        # Try to detect version from Chart.yaml or other sources
        # This can be implemented based on actual requirements
        # For now, return None to let user manually select
        return None

