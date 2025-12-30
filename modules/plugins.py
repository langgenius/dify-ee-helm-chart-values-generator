"""Plugin configuration module"""

from utils import (
    print_header, print_section, print_info, print_success, print_warning, print_error,
    prompt, prompt_choice, prompt_yes_no, generate_secret
)
from version_manager import VersionManager
from i18n import get_translator
from modules.features import apply_features

_t = get_translator()


def configure_plugins(generator):
    """Configure plugins"""
    # Check if version supports plugin module
    if not VersionManager.is_module_supported(generator.version, "plugins"):
        print_warning(f"{_t('version')} {generator.version} {_t('does_not_support_plugins')}, {_t('skipping')}")
        return

    print_header(_t('module_plugins'))

    # Plugin Connector Image Repository Configuration
    print_section(_t('plugin_connector_image_repo_config'))
    print_info(_t('config_plugin_connector_image_repo'))

    # Ensure plugin_connector configuration exists
    if 'plugin_connector' not in generator.values:
        generator.values['plugin_connector'] = {}

    # First select image repository type
    image_repo_type = prompt_choice(
        _t('image_repo_type'),
        ["docker", "ecr"],
        default=generator.values.get('plugin_connector', {}).get('imageRepoType', 'docker')
    )
    generator.values['plugin_connector']['imageRepoType'] = image_repo_type

    # If ECR, need to configure region, account ID and authentication method
    ecr_region = None
    ecr_account_id = None
    ecr_auth_method = None
    if image_repo_type == "ecr":
        ecr_region = prompt(
            _t('ecr_region'),
            default=generator.values.get('plugin_connector', {}).get('ecrRegion', 'us-east-1'),
            required=False
        )
        generator.values['plugin_connector']['ecrRegion'] = ecr_region if ecr_region else "us-east-1"
        print_info(f"{_t('ecr_region_set_to')}: {generator.values['plugin_connector']['ecrRegion']}")

        # Get ECR Account ID
        ecr_account_id = prompt(
            _t('ecr_account_id'),
            default="",
            required=False
        )

        # imageRepoPrefix: Image repository prefix (configured after account ID)
        # ECR format: {account_id}.dkr.ecr.{region}.amazonaws.com/{prefix}
        if ecr_account_id and ecr_region:
            default_prefix = f"{ecr_account_id}.dkr.ecr.{ecr_region}.amazonaws.com"
        else:
            default_prefix = "{account_id}.dkr.ecr.{region}.amazonaws.com"
        print_info(_t('ecr_prefix_format'))
        print_info(_t('ecr_prefix_note'))
        print_info(_t('ecr_prefix_example'))
        print_info(_t('ecr_prefix_example_with_prefix'))

        image_repo_prefix = prompt(
            _t('image_repo_prefix'),
            default=default_prefix,
            required=False
        )
        generator.values['plugin_connector']['imageRepoPrefix'] = image_repo_prefix if image_repo_prefix else default_prefix

        # Select ECR authentication method
        print_info("")
        print_info("=" * 60)
        print_info(_t('ecr_auth_method_config'))
        print_info("=" * 60)
        print_info(_t('ecr_auth_methods'))
        print_info(_t('ecr_irsa_mode_recommended'))
        print_info(_t('ecr_k8s_secret_mode'))
        print_info("=" * 60)
        print_info("")

        ecr_auth_method = prompt_choice(
            _t('ecr_auth_method'),
            [_t('irsa_mode'), _t('k8s_secret_mode')],
            default=_t('irsa_mode')
        )

        if ecr_auth_method == _t('irsa_mode'):
            print_info("")
            print_info("=" * 60)
            print_info(_t('irsa_config_note'))
            print_info("=" * 60)
            print_info(_t('irsa_config_instructions'))
            print_info(_t('irsa_config_docs'))
            print_info(_t('irsa_config_docs_url'))
            print_info("")
            print_info(_t('ecr_irsa_serviceaccounts'))
            print_info(_t('custom_serviceaccount_note'))
            print_info(_t('runner_serviceaccount_note'))
            print_info("=" * 60)
            print_info("")

            # Configure customServiceAccount
            custom_service_account = prompt(
                _t('custom_serviceaccount'),
                default=generator.values.get('plugin_connector', {}).get('customServiceAccount', ''),
                required=False
            )
            generator.values['plugin_connector']['customServiceAccount'] = custom_service_account if custom_service_account else ""

            # Configure runnerServiceAccount
            runner_service_account = prompt(
                _t('runner_serviceaccount'),
                default=generator.values.get('plugin_connector', {}).get('runnerServiceAccount', ''),
                required=False
            )
            generator.values['plugin_connector']['runnerServiceAccount'] = runner_service_account if runner_service_account else ""

        else:  # K8s Secret Mode
            print_info("")
            print_info("=" * 60)
            print_info(_t('k8s_secret_mode_config_note'))
            print_info("=" * 60)
            print_info(_t('k8s_secret_mode_desc'))
            print_info(_t('image_repo_secret_desc'))
            print_info(_t('secret_must_be_created'))
            print_info(_t('k8s_secret_docs_url'))
            print_info("")
            print_info(_t('image_repo_secret_must_match'))
            print_info(_t('default_image_repo_secret'))
            print_info("=" * 60)
            print_info("")

            image_repo_secret = prompt(
                _t('image_repo_secret_name'),
                default=generator.values.get('plugin_connector', {}).get('imageRepoSecret', 'image-repo-secret'),
                required=False
            )
            generator.values['plugin_connector']['imageRepoSecret'] = image_repo_secret if image_repo_secret else "image-repo-secret"
    else:
        # Docker mode image repository prefix configuration
        default_prefix = generator.values.get('plugin_connector', {}).get('imageRepoPrefix', 'docker.io/your-image-repo-prefix')
        print_info(_t('docker_prefix_example'))

        image_repo_prefix = prompt(
            _t('image_repo_prefix'),
            default=default_prefix,
            required=False
        )
        generator.values['plugin_connector']['imageRepoPrefix'] = image_repo_prefix if image_repo_prefix else default_prefix

    # imageRepoSecret: Image repository Secret name (Docker mode)
    # ECR K8s Secret mode already handled above, here only handle Docker mode
    if image_repo_type != "ecr":
        print_info("")
        print_info("=" * 60)
        print_info(_t('image_repo_secret_config_note'))
        print_info("=" * 60)
        print_info(_t('image_repo_secret_desc'))
        print_info(_t('secret_must_be_created'))
        print_info(_t('container_registry_docs_url'))
        print_info("")
        print_info(_t('image_repo_secret_must_match'))
        print_info(_t('default_image_repo_secret'))
        print_info("=" * 60)
        print_info("")
        image_repo_secret = prompt(
            _t('image_repo_secret_name'),
            default=generator.values.get('plugin_connector', {}).get('imageRepoSecret', 'image-repo-secret'),
            required=False
        )
        generator.values['plugin_connector']['imageRepoSecret'] = image_repo_secret if image_repo_secret else "image-repo-secret"
    elif image_repo_type == "ecr" and ecr_auth_method == _t('irsa_mode'):
        # IRSA mode doesn't need imageRepoSecret
        if 'imageRepoSecret' in generator.values.get('plugin_connector', {}):
            del generator.values['plugin_connector']['imageRepoSecret']

    # insecureImageRepo: Select image repository protocol type
    print_info("")
    print_warning(_t('http_not_recommended'))
    protocol_choice = prompt_choice(
        _t('image_repo_protocol_type'),
        [_t('https_recommended'), _t('http_not_recommended_option')],
        default=_t('https_recommended')
    )
    insecure_repo = (protocol_choice == _t('http_not_recommended_option'))
    generator.values['plugin_connector']['insecureImageRepo'] = insecure_repo
    if insecure_repo:
        print_warning(_t('http_selected'))
    else:
        print_success(_t('https_selected'))

    # Apply version-specific features for plugins module
    # Features are automatically discovered based on chart_version
    apply_features(generator, "plugins")

