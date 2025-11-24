"""Services configuration module"""

from utils import (
    print_header, print_section, print_info, print_success, print_warning, print_error,
    prompt, prompt_choice, prompt_yes_no, generate_secret
)
from version_manager import VersionManager
from i18n import get_translator

_t = get_translator()


def configure_services(generator):
    """Configure services"""
    print_header(_t('module_services'))

    # Enterprise related configuration
    if generator.values.get('enterprise', {}).get('enabled', True):
        print_section(_t('enterprise_service_config'))

        # All keys are auto-generated as per comments
        print_info(_t('enterprise_app_secret_key_auto'))
        generator.values['enterprise']['appSecretKey'] = generate_secret(42)
        print_success(f"{_t('generated')} Enterprise appSecretKey: {generator.values['enterprise']['appSecretKey'][:20]}...")

        print_info(_t('admin_apis_secret_key_salt_auto'))
        generator.values['enterprise']['adminAPIsSecretKeySalt'] = generate_secret(42)
        print_success(f"{_t('generated')} adminAPIsSecretKeySalt: {generator.values['enterprise']['adminAPIsSecretKeySalt'][:20]}...")

        print_info(_t('password_encryption_key_auto'))
        generator.values['enterprise']['passwordEncryptionKey'] = generate_secret(32)
        print_success(f"{_t('generated')} passwordEncryptionKey: {generator.values['enterprise']['passwordEncryptionKey'][:20]}...")

        license_mode = prompt_choice(
            _t('license_mode'),
            ["online", "offline"],
            default="online"
        )
        generator.values['enterprise']['licenseMode'] = license_mode

        if license_mode == "online":
            # Use default License server URL, don't ask user
            generator.values['enterprise']['licenseServer'] = "https://licenses.dify.ai/server"
            print_info(f"{_t('license_server_url')}: {generator.values['enterprise']['licenseServer']}")

    print_section(_t('service_enablement_status'))
    print_info(_t('can_skip_use_defaults'))

    if prompt_yes_no(_t('config_service_enablement'), default=False):
        services = ['api', 'worker', 'workerBeat', 'web', 'sandbox',
                   'enterprise', 'enterpriseAudit', 'enterpriseFrontend',
                   'ssrfProxy', 'unstructured', 'plugin_daemon', 'plugin_manager']

        for service in services:
            if service in generator.values:
                current = generator.values[service].get('enabled', True)
                generator.values[service]['enabled'] = prompt_yes_no(
                    f"{_t('enable_service')} {service}?",
                    default=current
                )

    # ==================== 主流程 ====================
