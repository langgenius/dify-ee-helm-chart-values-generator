"""Global configuration module"""

from utils import (
    print_header, print_section, print_info, print_success, print_warning, print_error,
    prompt, prompt_choice, prompt_yes_no, generate_secret
)
from version_manager import VersionManager
from i18n import get_translator

_t = get_translator()


def configure_global(generator):
    """Configure global settings"""
    print_header(_t('module_global'))

    print_info(_t('global_affects_all'))

    # Secret Keys - All keys are auto-generated as per comments
    print_section(_t('secret_config'))
    print_info(_t('app_secret_key_desc'))
    print_info(_t('auto_generate_openssl'))
    generator.values['global']['appSecretKey'] = generate_secret(42)
    print_success(f"{_t('generated')} appSecretKey: {generator.values['global']['appSecretKey'][:20]}...")

    print_info(_t('inner_api_key_desc'))
    print_info(_t('auto_generate_openssl'))
    generator.values['global']['innerApiKey'] = generate_secret(42)
    print_success(f"{_t('generated')} innerApiKey: {generator.values['global']['innerApiKey'][:20]}...")

    # Domain configuration
    print_section(_t('domain_config'))
    print_info(_t('empty_use_same'))

    generator.values['global']['consoleApiDomain'] = prompt(
        _t('console_api_domain'),
        default="console.dify.local",
        required=False
    )

    generator.values['global']['consoleWebDomain'] = prompt(
        _t('console_web_domain'),
        default="console.dify.local",
        required=False
    )

    generator.values['global']['serviceApiDomain'] = prompt(
        _t('service_api_domain'),
        default="api.dify.local",
        required=False
    )

    generator.values['global']['appApiDomain'] = prompt(
        _t('app_api_domain'),
        default="app.dify.local",
        required=False
    )

    generator.values['global']['appWebDomain'] = prompt(
        _t('app_web_domain'),
        default="app.dify.local",
        required=False
    )

    generator.values['global']['filesDomain'] = prompt(
        _t('files_domain'),
        default="files.dify.local",
        required=False
    )

    generator.values['global']['enterpriseDomain'] = prompt(
        _t('enterprise_domain'),
        default="enterprise.dify.local",
        required=False
    )

    # Database migration
    generator.values['global']['dbMigrationEnabled'] = prompt_yes_no(
        _t('enable_db_migration'),
        default=True
    )

    # RAG configuration
    print_section(_t('rag_config'))
    rag_etl_type = prompt_choice(
        _t('rag_etl_type'),
        ["dify", "Unstructured"],
        default="dify"
    )
    generator.values['global']['rag']['etlType'] = rag_etl_type

    # Relationship: If dify is selected, disable unstructured module
    if rag_etl_type == "dify":
        generator.values['unstructured']['enabled'] = False
        print_info(_t('auto_disabled_unstructured'))
    else:
        generator.values['unstructured']['enabled'] = True
        print_info(_t('auto_enabled_unstructured'))

    # Keyword data source type configuration - Add detailed description
    print_section(_t('keyword_data_source'))
    print_info("=" * 60)
    print_info(f"{_t('important_note')}: {_t('keyword_data_source')}")
    print_info("=" * 60)
    print_info(_t('keyword_data_source_desc'))
    print_info("")
    print_info(_t('option_explanation') + ":")
    print_info(f"  • {_t('option_object_storage')}")
    print_info(_t('option_object_storage_desc'))
    print_info(f"    - {_t('needs_object_storage')}")
    print_info("")
    print_info(f"  • {_t('option_database')}")
    print_info(_t('option_database_desc'))
    print_info(f"    - {_t('uses_postgresql')}")
    print_info("=" * 60)
    print_info("")
    generator.values['global']['rag']['keywordDataSourceType'] = prompt_choice(
        _t('select_keyword_source'),
        ["object_storage", "database"],
        default="object_storage"
    )

    top_k = prompt(_t('rag_top_k'), default="10", required=False)
    try:
        generator.values['global']['rag']['topKMaxValue'] = int(top_k)
    except ValueError:
        print_warning(f"{_t('invalid_number_use_default')} 10")

    seg_tokens = prompt(_t('doc_segmentation_tokens'), default="4000", required=False)
    try:
        generator.values['global']['rag']['indexingMaxSegmentationTokensLength'] = int(seg_tokens)
    except ValueError:
        print_warning(f"{_t('invalid_number_use_default')} 4000")

    # ==================== 模块 2: 基础设施配置 ====================
