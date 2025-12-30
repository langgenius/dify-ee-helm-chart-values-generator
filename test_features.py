#!/usr/bin/env python3
"""
Test script for version-specific features

This script tests:
1. Version parsing and comparison
2. Feature registration and discovery
3. Feature applicability based on chart version
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.features.base import (
    parse_version,
    compare_versions,
    version_satisfies,
    FeatureRegistry
)


def test_version_parsing():
    """Test version parsing"""
    print("\n=== 测试版本解析 ===")
    
    test_cases = [
        ("3.6.0", (3, 6, 0, 999, 0)),
        ("3.7.0", (3, 7, 0, 999, 0)),
        ("3.6.0-beta.1", (3, 6, 0, 2, 1)),
        ("3.6.0-alpha.2", (3, 6, 0, 1, 2)),
        ("3.6.0-rc.1", (3, 6, 0, 3, 1)),
    ]
    
    for version_str, expected in test_cases:
        result = parse_version(version_str)
        status = "✓" if result == expected else "✗"
        print(f"  {status} parse_version('{version_str}') = {result}")
        if result != expected:
            print(f"      Expected: {expected}")


def test_version_comparison():
    """Test version comparison"""
    print("\n=== 测试版本比较 ===")
    
    test_cases = [
        ("3.6.0", "3.7.0", -1),  # 3.6.0 < 3.7.0
        ("3.7.0", "3.6.0", 1),   # 3.7.0 > 3.6.0
        ("3.7.0", "3.7.0", 0),   # 3.7.0 == 3.7.0
        ("3.6.0-beta.1", "3.6.0", -1),  # beta < release
        ("3.6.0-alpha.1", "3.6.0-beta.1", -1),  # alpha < beta
        ("3.7.0", "3.6.5", 1),   # 3.7.0 > 3.6.5
    ]
    
    for v1, v2, expected in test_cases:
        result = compare_versions(v1, v2)
        status = "✓" if result == expected else "✗"
        op = "<" if result < 0 else (">" if result > 0 else "==")
        print(f"  {status} {v1} {op} {v2}")


def test_version_satisfies():
    """Test version constraint checking"""
    print("\n=== 测试版本约束 ===")
    
    test_cases = [
        ("3.7.0", "3.7.0", None, True),   # 3.7.0 >= 3.7.0
        ("3.6.5", "3.7.0", None, False),  # 3.6.5 < 3.7.0
        ("3.7.2", "3.7.0", None, True),   # 3.7.2 >= 3.7.0
        ("3.8.0", "3.7.0", "3.8.0", True),  # 3.7.0 <= 3.8.0 <= 3.8.0
        ("3.9.0", "3.7.0", "3.8.0", False),  # 3.9.0 > 3.8.0
    ]
    
    for version, min_v, max_v, expected in test_cases:
        result = version_satisfies(version, min_v, max_v)
        status = "✓" if result == expected else "✗"
        constraint = f">= {min_v}" + (f", <= {max_v}" if max_v else "")
        print(f"  {status} {version} satisfies ({constraint}) = {result}")


def test_feature_registry():
    """Test feature registry"""
    print("\n=== 测试特性注册表 ===")
    
    # Import features to trigger registration
    import modules.features  # This auto-discovers features
    
    # Test for different versions
    test_versions = ["3.6.0", "3.6.5", "3.7.0", "3.7.2"]
    
    for version in test_versions:
        print(f"\n  Chart 版本: {version}")
        features = FeatureRegistry.get_all_features(version)
        
        if not features:
            print("    (无适用特性)")
        else:
            for module, feature_list in features.items():
                for feature in feature_list:
                    print(f"    → [{module}] {feature.name or feature.__class__.__name__}")


def test_feature_order():
    """Test that triggerDomain is configured in domain section"""
    print("\n=== 检查 triggerDomain 配置位置 ===")
    
    # Read global_config.py to check where triggerDomain is configured
    global_config_path = Path(__file__).parent / "modules" / "global_config.py"
    content = global_config_path.read_text()
    
    # Check if triggerDomain is in domain config section
    domain_section_start = content.find("# Domain configuration")
    domain_section_end = content.find("# Database migration")
    
    # Check if there's any triggerDomain in domain section
    domain_section = content[domain_section_start:domain_section_end] if domain_section_start >= 0 and domain_section_end >= 0 else ""
    
    if "triggerDomain" in domain_section:
        print("  ✓ triggerDomain 在域名配置区域")
        # Check for version guard
        if "version_satisfies" in domain_section and "3.7.0" in domain_section:
            print("  ✓ triggerDomain 有版本检测 (>= 3.7.0)")
        else:
            print("  ✗ triggerDomain 缺少版本检测")
    else:
        print("  ✗ triggerDomain 不在域名配置区域")
        print("    → 建议：应该和其他域名一起在域名配置区域中配置")


def test_ssrf_proxy_sandbox_host():
    """Test that ssrfProxy.sandboxHost is configured as advanced option"""
    print("\n=== 检查 ssrfProxy.sandboxHost 配置 ===")
    
    # Read infrastructure.py to check sandboxHost configuration
    infra_config_path = Path(__file__).parent / "modules" / "infrastructure.py"
    content = infra_config_path.read_text()
    
    # Check if sandboxHost is in advanced config section
    if "sandboxHost" in content:
        print("  ✓ ssrfProxy.sandboxHost 已配置")
        if "config_advanced_options" in content:
            print("  ✓ 作为高级选项配置")
        else:
            print("  ✗ 不是高级选项")
    else:
        print("  ✗ ssrfProxy.sandboxHost 未配置")
    
    # Check i18n translations
    translations_path = Path(__file__).parent / "i18n" / "translations.py"
    translations_content = translations_path.read_text()
    
    if "ssrf_proxy_sandbox_host" in translations_content:
        print("  ✓ i18n 翻译已添加")
    else:
        print("  ✗ i18n 翻译缺失")


def test_global_config_trigger_domain():
    """Test that triggerDomain is properly shown based on version"""
    print("\n=== 测试 triggerDomain 版本检测 ===")
    
    from modules.features.base import version_satisfies
    
    test_cases = [
        ("3.6.0", False, "3.6.0 不应显示 triggerDomain"),
        ("3.6.5", False, "3.6.5 不应显示 triggerDomain"),
        ("3.7.0", True, "3.7.0 应显示 triggerDomain"),
        ("3.7.2", True, "3.7.2 应显示 triggerDomain"),
        ("3.8.0", True, "3.8.0 应显示 triggerDomain"),
    ]
    
    for version, expected, desc in test_cases:
        result = version_satisfies(version, "3.7.0")
        status = "✓" if result == expected else "✗"
        print(f"  {status} {desc}: {result}")


def test_all_features_for_versions():
    """Comprehensive test of all features across versions"""
    print("\n=== 完整版本特性矩阵 ===")
    
    import modules.features
    from modules.features.base import FeatureRegistry, version_satisfies
    
    versions = ["3.5.6", "3.6.0", "3.6.5", "3.7.0", "3.7.2"]
    
    # Build feature matrix
    print("\n  版本特性支持矩阵:")
    print("  " + "-" * 70)
    
    # Header
    header = "  特性名称".ljust(35)
    for v in versions:
        header += f" {v}".center(8)
    print(header)
    print("  " + "-" * 70)
    
    # Collect unique features across all versions
    all_feature_info = {}
    for v in versions:
        features_dict = FeatureRegistry.get_all_features(v)
        for module, feature_list in features_dict.items():
            for feature in feature_list:
                key = feature.__class__.__name__
                if key not in all_feature_info:
                    all_feature_info[key] = {
                        'name': getattr(feature, 'name', feature.__class__.__name__),
                        'min_version': getattr(feature, 'min_version', None),
                        'max_version': getattr(feature, 'max_version', None),
                        'module': module
                    }
    
    # Display matrix
    for key, info in all_feature_info.items():
        name = f"[{info['module']}] {info['name']}"[:32]
        row = f"  {name}".ljust(35)
        
        for v in versions:
            supported = version_satisfies(v, info['min_version'], info['max_version'])
            row += ("  ✓".center(8) if supported else "  -".center(8))
        print(row)
    
    print("  " + "-" * 70)


def main():
    print("=" * 60)
    print("Dify EE Helm Chart Values Generator - Feature Tests")
    print("=" * 60)
    
    test_version_parsing()
    test_version_comparison()
    test_version_satisfies()
    test_feature_registry()
    test_feature_order()
    test_global_config_trigger_domain()
    test_ssrf_proxy_sandbox_host()
    test_all_features_for_versions()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()

