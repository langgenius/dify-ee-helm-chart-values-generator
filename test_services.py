#!/usr/bin/env python3
"""
Test Module 6: Service Configuration
单独测试服务配置模块
"""

import os
import sys
from i18n import set_language, get_translator
from i18n.language import prompt_language_selection
from generator import ValuesGenerator
from modules.services import configure_services

def test_services_module():
    """Test services configuration module"""
    print("=" * 60)
    print("Test Module 6: Service Configuration")
    print("=" * 60)
    
    # Language selection
    prompt_language_selection()
    _t = get_translator()
    
    # Check if values.yaml exists
    source_file = "values.yaml"
    if not os.path.exists(source_file):
        print_error(f"{_t('file_not_found')}: {source_file}")
        print_info("Please download values.yaml first or use --local with --chart-version")
        return False
    
    try:
        # Initialize ValuesGenerator
        print_info(f"Loading template from: {source_file}")
        generator = ValuesGenerator(
            source_file=source_file,
            version="3.x",  # Use 3.x for testing
            chart_version="3.5.6"  # Use a test version
        )
        print_success("ValuesGenerator initialized successfully")
        
        # Check enterprise configuration structure
        if 'enterprise' not in generator.values:
            print_warning("enterprise configuration not found, creating default structure")
            generator.values['enterprise'] = {'enabled': True}
        
        print_info("\nInitial enterprise configuration:")
        enterprise_config = generator.values.get('enterprise', {})
        print(f"  - enabled: {enterprise_config.get('enabled', 'Not set')}")
        print(f"  - licenseMode: {enterprise_config.get('licenseMode', 'Not set')}")
        print(f"  - licenseServer: {enterprise_config.get('licenseServer', 'Not set')}")
        print(f"  - appSecretKey: {'Set' if 'appSecretKey' in enterprise_config else 'Not set'}")
        print(f"  - adminAPIsSecretKeySalt: {'Set' if 'adminAPIsSecretKeySalt' in enterprise_config else 'Not set'}")
        print(f"  - passwordEncryptionKey: {'Set' if 'passwordEncryptionKey' in enterprise_config else 'Not set'}")
        
        # Check service enablement status
        print_info("\nInitial service enablement status:")
        services = ['api', 'worker', 'workerBeat', 'web', 'sandbox',
                   'enterprise', 'enterpriseAudit', 'enterpriseFrontend',
                   'ssrfProxy', 'unstructured', 'plugin_daemon', 'plugin_manager']
        for service in services:
            if service in generator.values:
                enabled = generator.values[service].get('enabled', True)
                print(f"  - {service}: {enabled}")
        
        # Run the services configuration module
        print("\n" + "=" * 60)
        print("Running configure_services module...")
        print("=" * 60)
        
        configure_services(generator)
        
        # Display results
        print("\n" + "=" * 60)
        print("Configuration Results:")
        print("=" * 60)
        
        enterprise_config = generator.values.get('enterprise', {})
        print("\nEnterprise Configuration:")
        print(f"  - enabled: {enterprise_config.get('enabled', 'Not set')}")
        print(f"  - licenseMode: {enterprise_config.get('licenseMode', 'Not set')}")
        if 'licenseMode' in enterprise_config and enterprise_config['licenseMode'] == 'online':
            print(f"  - licenseServer: {enterprise_config.get('licenseServer', 'Not set (needs manual configuration)')}")
        print(f"  - appSecretKey: {enterprise_config.get('appSecretKey', 'Not set')[:20]}..." if 'appSecretKey' in enterprise_config else "  - appSecretKey: Not set")
        print(f"  - adminAPIsSecretKeySalt: {enterprise_config.get('adminAPIsSecretKeySalt', 'Not set')[:20]}..." if 'adminAPIsSecretKeySalt' in enterprise_config else "  - adminAPIsSecretKeySalt: Not set")
        print(f"  - passwordEncryptionKey: {enterprise_config.get('passwordEncryptionKey', 'Not set')[:20]}..." if 'passwordEncryptionKey' in enterprise_config else "  - passwordEncryptionKey: Not set")
        
        print("\nService Enablement Status:")
        for service in services:
            if service in generator.values:
                enabled = generator.values[service].get('enabled', True)
                print(f"  - {service}: {enabled}")
        
        print_success("\n✓ Service configuration module test completed successfully!")
        return True
        
    except Exception as e:
        print_error(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    from utils import print_info, print_error, print_success, print_warning
    success = test_services_module()
    sys.exit(0 if success else 1)

