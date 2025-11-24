"""Language selection utilities"""

import sys
from utils import Colors, print_header, print_info, print_success, print_error
from .translations import set_language, get_language, Translations

_t = Translations.get


def prompt_language_selection() -> str:
    """Prompt user to select language"""
    print_header(_t('select_language', language='en'))

    languages = [
        ('en', 'English'),
        ('zh', '中文 (Chinese)'),
    ]

    print_info(_t('select_language_prompt', language='en'))
    print()

    for i, (code, name) in enumerate(languages, 1):
        print(f"  {i}. {name}")

    while True:
        try:
            choice = input(f"\n{Colors.BOLD}Please select / 请选择 [1-{len(languages)}] (default: 1): {Colors.ENDC}").strip()

            if not choice:
                choice = "1"

            idx = int(choice) - 1
            if 0 <= idx < len(languages):
                selected_lang = languages[idx][0]
                set_language(selected_lang)
                print_success(f"Language set to: {languages[idx][1]}")
                return selected_lang
            else:
                print_error(f"Invalid selection, please enter 1-{len(languages)}")
        except ValueError:
            print_error("Please enter a valid number")
        except KeyboardInterrupt:
            print("\n")
            sys.exit(0)

