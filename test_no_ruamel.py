#!/usr/bin/env python3
"""
测试脚本：验证没有 ruamel.yaml 时会报错
"""

import sys
import os

# 临时移除 ruamel.yaml
original_modules = sys.modules.copy()

# 移除 ruamel.yaml 相关模块
modules_to_remove = [k for k in sys.modules.keys() if 'ruamel' in k]
for mod in modules_to_remove:
    del sys.modules[mod]

# 模拟 ImportError
class MockImportError:
    def __init__(self, name):
        self.name = name
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        pass

# 测试导入
print("测试：模拟没有 ruamel.yaml 的情况...")
print("=" * 60)

try:
    # 尝试导入生成器
    import importlib.util
    spec = importlib.util.spec_from_file_location("generate_values_prd", "generate-values-prd.py")
    generate_values_prd = importlib.util.module_from_spec(spec)
    
    # 临时修改 sys.modules 来模拟 ImportError
    import builtins
    original_import = builtins.__import__
    
    def mock_import(name, *args, **kwargs):
        if name == 'ruamel.yaml' or name.startswith('ruamel.'):
            raise ImportError(f"No module named '{name}'")
        return original_import(name, *args, **kwargs)
    
    builtins.__import__ = mock_import
    
    try:
        spec.loader.exec_module(generate_values_prd)
        ValuesGenerator = generate_values_prd.ValuesGenerator
        
        # 尝试创建生成器（应该会报错）
        print("尝试创建 ValuesGenerator...")
        generator = ValuesGenerator("values.yaml")
        print("✗ 错误：应该报错但没有报错！")
        sys.exit(1)
    except SystemExit as e:
        if e.code == 1:
            print("✓ 正确：检测到 ruamel.yaml 未安装，已报错退出")
            print("✓ 测试通过！")
            sys.exit(0)
        else:
            print(f"✗ 错误：退出码不正确: {e.code}")
            sys.exit(1)
    except Exception as e:
        print(f"✗ 错误：发生了意外异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        builtins.__import__ = original_import
        
except Exception as e:
    print(f"✗ 测试设置失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

