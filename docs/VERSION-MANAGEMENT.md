# 版本管理系统

## 概述

版本管理系统允许用户为不同版本的 Dify Enterprise Edition 生成对应的配置文件。不同版本的 Dify EE 可能支持不同的配置模块，系统会根据选择的版本动态调整配置流程。

## 设计理念

### 可扩展性

版本管理系统采用配置驱动的方式，通过 `VersionManager.VERSION_CONFIGS` 字典定义每个版本支持的模块。添加新版本只需在配置字典中添加新的条目，无需修改核心代码逻辑。

### 模块化

每个配置模块（如 `configure_plugins`）都会检查当前版本是否支持该模块。如果不支持，会自动跳过，确保配置流程的灵活性。

## 支持的版本

### Dify EE 3.0

- **模块**: 全局配置、基础设施、网络、邮件、**插件**、服务
- **特点**: 完整支持所有功能模块，包括插件系统

### Dify EE 2.0

- **模块**: 全局配置、基础设施、网络、邮件、服务
- **特点**: 不支持插件模块

## 使用方法

### 交互式选择版本（推荐）

运行脚本后，系统会提示选择版本：

```bash
python generate-values-prd.py
```

输出示例：

```
============================================================
          Dify Enterprise Edition 版本选择
============================================================

ℹ 请选择要生成的 Dify EE 版本：

  1. Dify Enterprise Edition 3.0
     版本: 3.0
     说明: 支持插件功能的完整版本
     支持模块: global, infrastructure, networking, mail, plugins, services

  2. Dify Enterprise Edition 2.0
     版本: 2.0
     说明: 不包含插件功能的版本
     支持模块: global, infrastructure, networking, mail, services

请选择版本 [1-2] (默认: 1): 
```

### 命令行指定版本

使用 `--ee-version` 参数直接指定版本：

```bash
# 指定 Dify EE 3.0
python generate-values-prd.py --ee-version 3.0

# 指定 Dify EE 2.0
python generate-values-prd.py --ee-version 2.0
```

### 完整示例

```bash
# 指定 Helm Chart 版本和 Dify EE 版本
python generate-values-prd.py --chart-version 3.6.0 --ee-version 3.0

# 使用本地 values.yaml 并指定 Dify EE 版本
python generate-values-prd.py --local --ee-version 2.0
```

## 版本配置结构

每个版本的配置包含以下字段：

```python
{
    "版本号": {
        "name": "版本显示名称",
        "modules": ["模块列表"],
        "description": "版本说明"
    }
}
```

### 模块名称

- `global`: 全局配置模块
- `infrastructure`: 基础设施配置模块
- `networking`: 网络配置模块
- `mail`: 邮件配置模块
- `plugins`: 插件配置模块（仅 3.0+）
- `services`: 服务配置模块

## 添加新版本

### 步骤 1: 添加版本配置

在 `VersionManager.VERSION_CONFIGS` 中添加新版本：

```python
VERSION_CONFIGS = {
    # ... 现有版本 ...
    "4.0": {
        "name": "Dify Enterprise Edition 4.0",
        "modules": [
            "global",
            "infrastructure",
            "networking",
            "mail",
            "plugins",
            "services",
            "new_module"  # 新模块
        ],
        "description": "支持新功能的版本"
    }
}
```

### 步骤 2: 实现新模块（如需要）

如果新版本引入了新模块，需要实现对应的配置函数：

```python
def configure_new_module(self):
    """配置新模块"""
    if not VersionManager.is_module_supported(self.version, "new_module"):
        print_warning(f"版本 {self.version} 不支持新模块配置，跳过")
        return
    
    print_header("模块 X: 新模块配置")
    # ... 配置逻辑 ...
```

### 步骤 3: 注册模块

在 `generate()` 方法的 `module_configs` 字典中注册新模块：

```python
module_configs = {
    # ... 现有模块 ...
    "new_module": self.configure_new_module,
}
```

## 版本检测

系统支持从 `values.yaml` 中检测版本（如果可能）。`VersionManager.detect_version_from_values()` 方法可以根据 Chart 版本或其他标识符自动检测 Dify EE 版本。

**当前实现**: 返回 `None`，需要用户手动选择。未来可以增强自动检测功能。

## 模块兼容性检查

每个配置模块都应该检查版本兼容性：

```python
def configure_plugins(self):
    """配置插件"""
    # 检查版本是否支持插件模块
    if not VersionManager.is_module_supported(self.version, "plugins"):
        print_warning(f"版本 {self.version} 不支持插件配置模块，跳过")
        return
    
    # ... 配置逻辑 ...
```

## 最佳实践

1. **版本选择**: 建议在启动时交互式选择版本，确保用户了解版本差异
2. **模块检查**: 每个模块都应该检查版本兼容性
3. **清晰提示**: 当模块被跳过时，应该给出清晰的提示信息
4. **文档更新**: 添加新版本时，同步更新文档

## 故障排除

### 问题: 版本不存在

**错误信息**: `无效的 Dify EE 版本: X.X`

**解决方案**: 
- 检查版本号是否正确
- 使用 `--ee-version` 时，确保版本在可用列表中
- 查看 `VersionManager.get_available_versions()` 获取可用版本

### 问题: 模块未执行

**可能原因**: 
- 版本不支持该模块
- 模块配置函数未注册

**解决方案**:
- 检查版本配置中的 `modules` 列表
- 确认模块配置函数已添加到 `module_configs` 字典

## 相关文件

- `generate-values-prd.py`: 主脚本，包含版本管理器和配置生成器
- `docs/MODULES.md`: 模块划分说明
- `docs/FLOWCHART.md`: 配置流程图

## 未来改进

1. **自动版本检测**: 从 `values.yaml` 或 Chart 版本自动检测 Dify EE 版本
2. **版本迁移**: 支持从旧版本配置迁移到新版本
3. **版本验证**: 验证生成的配置是否与选择的版本兼容
4. **模块依赖**: 支持模块之间的依赖关系定义

