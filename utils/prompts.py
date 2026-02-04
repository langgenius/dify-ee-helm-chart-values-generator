"""User interaction prompts"""

from typing import Optional
from .colors import Colors, print_error, print_info
from i18n import get_translator
import config

_t = get_translator()


def prompt(prompt_text: str, default: Optional[str] = None, required: bool = True) -> str:
    """Prompt user for input. In CI mode, returns default value automatically."""
    # CI mode: return default without prompting
    if config.is_ci_mode():
        if default:
            print_info(f"[CI] {prompt_text}: {default}")
            return default
        elif not required:
            print_info(f"[CI] {prompt_text}: (empty)")
            return ""
        else:
            # Required field with no default - use placeholder
            print_info(f"[CI] {prompt_text}: (required, using placeholder)")
            return "ci-placeholder"

    if default:
        prompt_str = f"{Colors.BOLD}{prompt_text}{Colors.ENDC} [{default}]: "
    else:
        prompt_str = f"{Colors.BOLD}{prompt_text}{Colors.ENDC}: "

    while True:
        value = input(prompt_str).strip()
        if value:
            return value
        elif default:
            return default
        elif not required:
            return ""
        else:
            print_error(_t('field_required'))


def prompt_yes_no(prompt_text: str, default: bool = True) -> bool:
    """Prompt yes/no choice. In CI mode, returns default value automatically."""
    # CI mode: return default without prompting
    if config.is_ci_mode():
        result_str = "Yes" if default else "No"
        print_info(f"[CI] {prompt_text}: {result_str}")
        return default

    default_str = "Y/n" if default else "y/N"
    prompt_str = f"{Colors.BOLD}{prompt_text}{Colors.ENDC} [{default_str}]: "

    while True:
        value = input(prompt_str).strip().lower()
        if not value:
            return default
        if value in ['y', 'yes']:
            return True
        elif value in ['n', 'no']:
            return False
        else:
            print_error(_t('enter_y_or_n'))


def prompt_choice(prompt_text: str, choices: list, default: Optional[str] = None) -> str:
    """Prompt for choice. In CI mode, returns default or first choice automatically."""
    # CI mode: return default or first choice without prompting
    if config.is_ci_mode():
        result = default if default else choices[0]
        print_info(f"[CI] {prompt_text}: {result}")
        return result

    print(f"\n{Colors.BOLD}{prompt_text}{Colors.ENDC}")
    default_marker = _t('default')
    for i, choice in enumerate(choices, 1):
        marker = f" [{default_marker}]" if choice == default else ""
        print(f"  {i}. {choice}{marker}")

    while True:
        select_text = _t('select_range')
        if default:
            prompt_str = f"{select_text} [1-{len(choices)}] ({default_marker}: {default}): "
        else:
            prompt_str = f"{select_text} [1-{len(choices)}]: "

        value = input(prompt_str).strip()
        if not value and default:
            return default

        try:
            idx = int(value) - 1
            if 0 <= idx < len(choices):
                return choices[idx]
        except ValueError:
            pass

        range_text = _t('enter_number_range')
        print_error(f"{range_text} 1-{len(choices)}")

