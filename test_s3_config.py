#!/usr/bin/env python3
"""
测试 AWS S3 存储配置功能
"""

import sys
import os
import importlib.util

# 加载 generate-values-prd.py 模块
spec = importlib.util.spec_from_file_location("generate_values_prd", "generate-values-prd.py")
generate_values_prd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generate_values_prd)

def test_s3_config():
    """测试 S3 配置逻辑"""
    print("=" * 60)
    print("测试 AWS S3 存储配置")
    print("=" * 60)
    
    # 检查 values.yaml 是否存在
    if not os.path.exists('values.yaml'):
        print("✗ 错误: values.yaml 文件不存在")
        return False
    
    try:
        # 创建 ValuesGenerator 实例
        generator = generate_values_prd.ValuesGenerator('values.yaml')
        print("✓ ValuesGenerator 初始化成功")
        
        # 检查 persistence 配置结构
        if 'persistence' not in generator.values:
            print("✗ 错误: persistence 配置不存在")
            return False
        print("✓ persistence 配置存在")
        
        if 's3' not in generator.values['persistence']:
            print("✗ 错误: s3 配置不存在")
            return False
        print("✓ s3 配置存在")
        
        # 检查初始值
        s3_config = generator.values['persistence']['s3']
        print(f"\n初始配置:")
        print(f"  - useAwsS3: {s3_config.get('useAwsS3', '未设置')}")
        print(f"  - useAwsManagedIam: {s3_config.get('useAwsManagedIam', '未设置')}")
        print(f"  - endpoint: {s3_config.get('endpoint', '未设置')}")
        print(f"  - accessKey: {'已设置' if 'accessKey' in s3_config else '未设置'}")
        print(f"  - secretKey: {'已设置' if 'secretKey' in s3_config else '未设置'}")
        
        # 模拟 AWS S3 + IRSA 模式配置
        print("\n" + "=" * 60)
        print("模拟配置: AWS S3 + IRSA 模式")
        print("=" * 60)
        
        generator.values['persistence']['s3']['useAwsS3'] = True
        generator.values['persistence']['s3']['endpoint'] = "https://s3.us-west-2.amazonaws.com"
        generator.values['persistence']['s3']['useAwsManagedIam'] = True
        
        # 删除 accessKey 和 secretKey（IRSA 模式不需要）
        if 'accessKey' in generator.values['persistence']['s3']:
            del generator.values['persistence']['s3']['accessKey']
        if 'secretKey' in generator.values['persistence']['s3']:
            del generator.values['persistence']['s3']['secretKey']
        
        generator.values['persistence']['s3']['region'] = "us-west-2"
        generator.values['persistence']['s3']['bucketName'] = "test-bucket"
        
        # 配置 ServiceAccount
        generator.values['api']['serviceAccountName'] = "dify-api-sa"
        generator.values['worker']['serviceAccountName'] = "dify-api-sa"
        
        print("✓ IRSA 模式配置完成")
        print(f"  - useAwsS3: {generator.values['persistence']['s3']['useAwsS3']}")
        print(f"  - useAwsManagedIam: {generator.values['persistence']['s3']['useAwsManagedIam']}")
        print(f"  - endpoint: {generator.values['persistence']['s3']['endpoint']}")
        print(f"  - accessKey: {'已设置' if 'accessKey' in generator.values['persistence']['s3'] else '已删除（IRSA模式）'}")
        print(f"  - secretKey: {'已设置' if 'secretKey' in generator.values['persistence']['s3'] else '已删除（IRSA模式）'}")
        print(f"  - api.serviceAccountName: {generator.values['api'].get('serviceAccountName', '未设置')}")
        print(f"  - worker.serviceAccountName: {generator.values['worker'].get('serviceAccountName', '未设置')}")
        
        # 模拟 AWS S3 + Access Key 模式配置
        print("\n" + "=" * 60)
        print("模拟配置: AWS S3 + Access Key 模式")
        print("=" * 60)
        
        generator.values['persistence']['s3']['useAwsS3'] = True
        generator.values['persistence']['s3']['endpoint'] = "https://s3.us-east-1.amazonaws.com"
        generator.values['persistence']['s3']['useAwsManagedIam'] = False
        generator.values['persistence']['s3']['accessKey'] = "AKIAIOSFODNN7EXAMPLE"
        generator.values['persistence']['s3']['secretKey'] = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        generator.values['persistence']['s3']['region'] = "us-east-1"
        generator.values['persistence']['s3']['bucketName'] = "test-bucket-2"
        
        print("✓ Access Key 模式配置完成")
        print(f"  - useAwsS3: {generator.values['persistence']['s3']['useAwsS3']}")
        print(f"  - useAwsManagedIam: {generator.values['persistence']['s3']['useAwsManagedIam']}")
        print(f"  - endpoint: {generator.values['persistence']['s3']['endpoint']}")
        print(f"  - accessKey: {'已设置' if 'accessKey' in generator.values['persistence']['s3'] else '未设置'}")
        print(f"  - secretKey: {'已设置' if 'secretKey' in generator.values['persistence']['s3'] else '未设置'}")
        
        print("\n" + "=" * 60)
        print("✓ 所有测试通过！")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_s3_config()
    sys.exit(0 if success else 1)

