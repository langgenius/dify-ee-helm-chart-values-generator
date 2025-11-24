"""User interaction prompts"""

from typing import Optional
from .colors import Colors, print_error
from i18n import get_translator

_t = get_translator()


def prompt(prompt_text: str, default: Optional[str] = None, required: bool = True) -> str:
    """Prompt user for input"""
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
    """Prompt yes/no choice"""
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
    """Prompt for choice"""
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

