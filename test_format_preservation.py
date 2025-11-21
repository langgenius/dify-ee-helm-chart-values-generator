#!/usr/bin/env python3
"""
测试脚本：验证格式保留功能
测试双引号、注释和未更新字段的保留
"""

import os
import sys

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入生成器类
import importlib.util
spec = importlib.util.spec_from_file_location("generate_values_prd", "generate-values-prd.py")
generate_values_prd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generate_values_prd)
ValuesGenerator = generate_values_prd.ValuesGenerator

def test_format_preservation():
    """测试格式保留功能"""
    print("=" * 60)
    print("测试格式保留功能")
    print("=" * 60)
    
    source_file = "values.yaml"
    output_file = "values-test-output.yaml"
    
    if not os.path.exists(source_file):
        print(f"错误: 模板文件 {source_file} 不存在")
        return False
    
    # 创建生成器
    print(f"\n1. 加载模板文件: {source_file}")
    generator = ValuesGenerator(source_file)
    
    # 只修改几个字段进行测试
    print("\n2. 修改测试字段...")
    generator.values['global']['appSecretKey'] = "test-secret-key-12345"
    generator.values['global']['consoleApiDomain'] = "test.console.local"
    
    # 保存文件
    print(f"\n3. 保存到: {output_file}")
    generator.save(output_file)
    
    # 验证结果
    print("\n4. 验证结果...")
    
    # 读取原始文件和生成文件
    with open(source_file, 'r', encoding='utf-8') as f:
        original_lines = f.readlines()
    
    with open(output_file, 'r', encoding='utf-8') as f:
        generated_lines = f.readlines()
    
    # 检查关键点
    checks = {
        '注释保留': False,
        '引号保留': False,
        '未更新字段保留': False,
        '修改字段更新': False
    }
    
    # 检查注释（查找包含 # 的行）
    original_comments = [line for line in original_lines if line.strip().startswith('#')]
    generated_comments = [line for line in generated_lines if line.strip().startswith('#')]
    
    if len(generated_comments) >= len(original_comments) * 0.8:  # 至少保留80%的注释
        checks['注释保留'] = True
        print(f"  ✓ 注释保留: {len(generated_comments)}/{len(original_comments)} 条注释")
    else:
        print(f"  ✗ 注释保留失败: {len(generated_comments)}/{len(original_comments)} 条注释")
    
    # 检查引号（查找带引号的字符串）
    original_quoted = [line for line in original_lines if ':"' in line or ":'" in line]
    generated_quoted = [line for line in generated_lines if ':"' in line or ":'" in line]
    
    if len(generated_quoted) >= len(original_quoted) * 0.7:  # 至少保留70%的引号
        checks['引号保留'] = True
        print(f"  ✓ 引号保留: {len(generated_quoted)}/{len(original_quoted)} 个带引号的字段")
    else:
        print(f"  ✗ 引号保留失败: {len(generated_quoted)}/{len(original_quoted)} 个带引号的字段")
    
    # 检查修改的字段是否更新
    app_secret_found = False
    console_domain_found = False
    
    for line in generated_lines:
        if 'appSecretKey:' in line and 'test-secret-key-12345' in line:
            app_secret_found = True
        if 'consoleApiDomain:' in line and 'test.console.local' in line:
            console_domain_found = True
    
    if app_secret_found and console_domain_found:
        checks['修改字段更新'] = True
        print("  ✓ 修改字段已更新")
    else:
        print(f"  ✗ 修改字段更新失败: appSecretKey={app_secret_found}, consoleApiDomain={console_domain_found}")
    
    # 检查未更新字段（例如 innerApiKey）
    original_inner_api = None
    generated_inner_api = None
    
    for line in original_lines:
        if 'innerApiKey:' in line:
            original_inner_api = line.strip()
            break
    
    for line in generated_lines:
        if 'innerApiKey:' in line:
            generated_inner_api = line.strip()
            break
    
    if original_inner_api and generated_inner_api and original_inner_api == generated_inner_api:
        checks['未更新字段保留'] = True
        print(f"  ✓ 未更新字段保留: innerApiKey 保持不变")
    else:
        print(f"  ✗ 未更新字段保留失败")
        print(f"    原始: {original_inner_api}")
        print(f"    生成: {generated_inner_api}")
    
    # 总结
    print("\n" + "=" * 60)
    print("测试结果总结:")
    print("=" * 60)
    
    all_passed = all(checks.values())
    
    for check_name, passed in checks.items():
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"  {check_name}: {status}")
    
    if all_passed:
        print("\n🎉 所有测试通过！格式保留功能正常工作。")
        return True
    else:
        print("\n⚠️  部分测试失败，请检查生成的文件。")
        return False

if __name__ == "__main__":
    success = test_format_preservation()
    sys.exit(0 if success else 1)

