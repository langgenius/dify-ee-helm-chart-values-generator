"""Services configuration module"""

from utils import (
    print_header, print_section, print_info, print_success, print_warning, print_error,
    prompt, prompt_choice, prompt_yes_no, generate_secret
)
from version_manager import VersionManager
from i18n import get_translator
from modules.features import apply_features

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

        # License mode selection (online/offline)
        # Note: licenseServer URL is not set - users should configure it manually in values.yaml
        license_mode = prompt_choice(
            _t('license_mode'),
            ["online", "offline"],
            default="online"
        )
        generator.values['enterprise']['licenseMode'] = license_mode
        print_info(f"{_t('license_mode')}: {license_mode}")
        if license_mode == "online":
            print_info(_t('license_server_manual_config_note'))

    # Configure replica counts for services (using default values from template)
    # Note: Service enablement is not configurable here (except unstructured which is handled in global_config)
    print_section(_t('service_replica_config'))
    print_info(_t('service_replica_config_note'))

    # Services with replica configuration
    # Note: workerBeat does not have replicas (it's a singleton scheduler)
    services_with_replicas = [
        'api', 'worker', 'web', 'sandbox', 'enterprise', 'enterpriseAudit',
        'enterpriseFrontend', 'ssrfProxy', 'unstructured', 'plugin_daemon',
        'plugin_controller', 'plugin_connector', 'plugin_manager'
    ]

    # Ask user if they want to configure replica counts
    configure_replicas = prompt_yes_no(_t('config_service_replicas'), default=False)

    for service in services_with_replicas:
        if service in generator.values:
            # Skip replica configuration if service is disabled
            service_enabled = generator.values[service].get('enabled', True)
            if not service_enabled:
                print_info(f"  {service}: {_t('service_disabled_skip_replica')}")
                continue

            # Get default replica count from template (default to 1 if not found)
            default_replicas = generator.values[service].get('replicas', 1)

            if configure_replicas:
                # User wants to configure replica counts
                replica_input = prompt(
                    _t('replica_count_for').format(service=service),
                    default=str(default_replicas),
                    required=True
                )
                try:
                    replica_count = int(replica_input)
                    if replica_count < 1:
                        print_warning(f"{_t('invalid_replica_count')}, {_t('using_default')}: {default_replicas}")
                        replica_count = default_replicas
                    generator.values[service]['replicas'] = replica_count
                    print_success(f"  {service}: {replica_count} {_t('replica')}(s)")
                except ValueError:
                    print_warning(f"{_t('invalid_replica_count')}, {_t('using_default')}: {default_replicas}")
                    generator.values[service]['replicas'] = default_replicas
                    print_info(f"  {service}: {default_replicas} {_t('replica')}(s)")
            else:
                # Use default values
                generator.values[service]['replicas'] = default_replicas
                print_info(f"  {service}: {default_replicas} {_t('replica')}(s)")

    # Note: unstructured.enabled is automatically configured in global_config based on RAG etlType
    # No need to configure service enablement here

    # Apply version-specific features for services module
    # Features are automatically discovered based on chart_version
    apply_features(generator, "services")
