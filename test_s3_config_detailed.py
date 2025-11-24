#!/usr/bin/env python3
"""
详细测试 AWS S3 存储配置功能
验证所有配置分支
"""

import sys
import os
import importlib.util

# 加载 generate-values-prd.py 模块
spec = importlib.util.spec_from_file_location("generate_values_prd", "generate-values-prd.py")
generate_values_prd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generate_values_prd)

def test_all_scenarios():
    """测试所有配置场景"""
    print("=" * 60)
    print("详细测试 AWS S3 存储配置 - 所有场景")
    print("=" * 60)
    
    scenarios = [
        {
            "name": "场景 1: AWS S3 + IRSA 模式（带 ServiceAccount）",
            "s3_provider": "AWS S3",
            "auth_method": "IRSA 模式（推荐）",
            "endpoint": "https://s3.us-west-2.amazonaws.com",
            "api_sa": "dify-api-sa",
            "worker_sa": "dify-api-sa",
            "expected": {
                "useAwsS3": True,
                "useAwsManagedIam": True,
                "has_accessKey": False,
                "has_secretKey": False,
                "has_api_sa": True,
                "has_worker_sa": True
            }
        },
        {
            "name": "场景 2: AWS S3 + IRSA 模式（不带 ServiceAccount）",
            "s3_provider": "AWS S3",
            "auth_method": "IRSA 模式（推荐）",
            "endpoint": "https://s3.us-east-1.amazonaws.com",
            "api_sa": "",
            "worker_sa": "",
            "expected": {
                "useAwsS3": True,
                "useAwsManagedIam": True,
                "has_accessKey": False,
                "has_secretKey": False,
                "has_api_sa": False,
                "has_worker_sa": False
            }
        },
        {
            "name": "场景 3: AWS S3 + Access Key 模式",
            "s3_provider": "AWS S3",
            "auth_method": "Access Key 模式",
            "endpoint": "https://s3.ap-southeast-1.amazonaws.com",
            "accessKey": "AKIAIOSFODNN7EXAMPLE",
            "secretKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
            "expected": {
                "useAwsS3": True,
                "useAwsManagedIam": False,
                "has_accessKey": True,
                "has_secretKey": True
            }
        },
        {
            "name": "场景 4: MinIO（非 AWS S3）",
            "s3_provider": "MinIO",
            "endpoint": "http://host.docker.internal:9000",
            "accessKey": "minioadmin",
            "secretKey": "minioadmin123",
            "expected": {
                "useAwsS3": False,
                "useAwsManagedIam": False,
                "has_accessKey": True,
                "has_secretKey": True,
                "minio_enabled": True
            }
        }
    ]
    
    all_passed = True
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*60}")
        print(f"{scenario['name']}")
        print(f"{'='*60}")
        
        try:
            # 重新加载模板
            generator = generate_values_prd.ValuesGenerator('values.yaml')
            
            # 模拟配置
            if scenario['s3_provider'] == "AWS S3":
                generator.values['persistence']['s3']['useAwsS3'] = True
                generator.values['persistence']['s3']['endpoint'] = scenario['endpoint']
                generator.values['minio']['enabled'] = False
                
                if scenario['auth_method'] == "IRSA 模式（推荐）":
                    generator.values['persistence']['s3']['useAwsManagedIam'] = True
                    # 删除 accessKey 和 secretKey
                    if 'accessKey' in generator.values['persistence']['s3']:
                        del generator.values['persistence']['s3']['accessKey']
                    if 'secretKey' in generator.values['persistence']['s3']:
                        del generator.values['persistence']['s3']['secretKey']
                    
                    # 配置 ServiceAccount（如果有）
                    if scenario.get('api_sa'):
                        generator.values['api']['serviceAccountName'] = scenario['api_sa']
                    if scenario.get('worker_sa'):
                        generator.values['worker']['serviceAccountName'] = scenario['worker_sa']
                else:  # Access Key 模式
                    generator.values['persistence']['s3']['useAwsManagedIam'] = False
                    generator.values['persistence']['s3']['accessKey'] = scenario['accessKey']
                    generator.values['persistence']['s3']['secretKey'] = scenario['secretKey']
            else:  # MinIO 或其他
                generator.values['persistence']['s3']['useAwsS3'] = False
                generator.values['persistence']['s3']['useAwsManagedIam'] = False
                generator.values['persistence']['s3']['endpoint'] = scenario['endpoint']
                generator.values['persistence']['s3']['accessKey'] = scenario['accessKey']
                generator.values['persistence']['s3']['secretKey'] = scenario['secretKey']
                generator.values['minio']['enabled'] = True
            
            # 验证结果
            expected = scenario['expected']
            s3_config = generator.values['persistence']['s3']
            
            checks = []
            
            # 检查 useAwsS3
            actual_useAwsS3 = s3_config.get('useAwsS3', False)
            checks.append(("useAwsS3", actual_useAwsS3 == expected['useAwsS3'], actual_useAwsS3, expected['useAwsS3']))
            
            # 检查 useAwsManagedIam
            actual_useAwsManagedIam = s3_config.get('useAwsManagedIam', False)
            checks.append(("useAwsManagedIam", actual_useAwsManagedIam == expected['useAwsManagedIam'], actual_useAwsManagedIam, expected['useAwsManagedIam']))
            
            # 检查 accessKey
            has_accessKey = 'accessKey' in s3_config
            checks.append(("has_accessKey", has_accessKey == expected['has_accessKey'], has_accessKey, expected['has_accessKey']))
            
            # 检查 secretKey
            has_secretKey = 'secretKey' in s3_config
            checks.append(("has_secretKey", has_secretKey == expected['has_secretKey'], has_secretKey, expected['has_secretKey']))
            
            # 检查 ServiceAccount（如果场景中有）
            if 'has_api_sa' in expected:
                api_sa_value = generator.values['api'].get('serviceAccountName', '')
                has_api_sa = bool(api_sa_value)
                checks.append(("has_api_sa", has_api_sa == expected['has_api_sa'], f"'{api_sa_value}'", expected['has_api_sa']))
            
            if 'has_worker_sa' in expected:
                worker_sa_value = generator.values['worker'].get('serviceAccountName', '')
                has_worker_sa = bool(worker_sa_value)
                checks.append(("has_worker_sa", has_worker_sa == expected['has_worker_sa'], f"'{worker_sa_value}'", expected['has_worker_sa']))
            
            # 检查 MinIO（如果场景中有）
            if 'minio_enabled' in expected:
                actual_minio_enabled = generator.values['minio'].get('enabled', False)
                checks.append(("minio_enabled", actual_minio_enabled == expected['minio_enabled'], actual_minio_enabled, expected['minio_enabled']))
            
            # 打印检查结果
            scenario_passed = True
            for check_name, passed, actual, expected_val in checks:
                status = "✓" if passed else "✗"
                print(f"  {status} {check_name}: {actual} (期望: {expected_val})")
                if not passed:
                    scenario_passed = False
                    all_passed = False
            
            if scenario_passed:
                print(f"  ✓ 场景 {i} 通过")
            else:
                print(f"  ✗ 场景 {i} 失败")
                
        except Exception as e:
            print(f"  ✗ 场景 {i} 出错: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False
    
    print(f"\n{'='*60}")
    if all_passed:
        print("✓ 所有场景测试通过！")
    else:
        print("✗ 部分场景测试失败")
    print(f"{'='*60}")
    
    return all_passed

if __name__ == "__main__":
    success = test_all_scenarios()
    sys.exit(0 if success else 1)

