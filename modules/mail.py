"""Mail configuration module"""

from utils import (
    print_header, print_section, print_info, print_success, print_warning, print_error,
    prompt, prompt_choice, prompt_yes_no, generate_secret
)
from version_manager import VersionManager
from i18n import get_translator

_t = get_translator()


def configure_mail(generator):
    """Configure mail"""
    print_header(_t('module_mail'))

    mail_type = prompt_choice(
        _t('select_mail_service_type'),
        ["", "resend", "smtp"],
        default=""
    )

    generator.values['mail']['type'] = mail_type

    if mail_type:
        generator.values['mail']['defaultSender'] = prompt(
            _t('default_sender_address'),
            default="YOUR EMAIL FROM (eg: no-reply <no-reply@dify.ai>)",
            required=False
        )

        if mail_type == "resend":
            generator.values['mail']['resend']['apiKey'] = prompt(
                _t('resend_api_key'),
                required=True
            )
            generator.values['mail']['resend']['apiUrl'] = prompt(
                _t('resend_api_url'),
                default="https://api.resend.com",
                required=False
            )
        elif mail_type == "smtp":
            generator.values['mail']['smtp']['server'] = prompt(
                _t('smtp_server'),
                required=True
            )
            port = prompt(_t('smtp_port'), default="587", required=False)
            try:
                generator.values['mail']['smtp']['port'] = int(port)
            except ValueError:
                generator.values['mail']['smtp']['port'] = 587

            generator.values['mail']['smtp']['username'] = prompt(
                _t('smtp_username'),
                required=True
            )
            generator.values['mail']['smtp']['password'] = prompt(
                _t('smtp_password'),
                required=True
            )
            generator.values['mail']['smtp']['useTLS'] = prompt_yes_no(
                _t('use_tls'),
                default=False
            )

    # ==================== 模块 5: 插件配置 ====================
