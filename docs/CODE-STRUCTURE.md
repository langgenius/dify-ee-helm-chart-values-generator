# 代码结构说明

## 概述

项目代码已重构为模块化结构，提高了代码的可读性和可维护性。原来的单文件（近 2000 行）已拆分为多个模块文件。

## 目录结构

```
.
├── generate-values-prd.py    # 主入口文件（~100 行）
├── generator.py              # ValuesGenerator 核心类（~350 行）
├── version_manager.py        # 版本管理模块（~120 行）
├── utils/                    # 工具模块目录
│   ├── __init__.py          # 工具模块导出
│   ├── colors.py            # 终端颜色和打印函数
│   ├── prompts.py           # 用户交互提示函数
│   ├── downloader.py        # values.yaml 下载功能
│   └── secrets.py           # 密钥生成功能
└── modules/                  # 配置模块目录
    ├── __init__.py          # 模块导出
    ├── global_config.py     # 全局配置模块（~120 行）
    ├── infrastructure.py    # 基础设施配置模块（~550 行）
    ├── networking.py        # 网络配置模块（~140 行）
    ├── mail.py              # 邮件配置模块（~50 行）
    ├── plugins.py           # 插件配置模块（~185 行）
    └── services.py          # 服务配置模块（~50 行）
```

## 模块说明

### 1. 主入口文件 (`generate-values-prd.py`)

**职责**: 
- 命令行参数解析
- 调用下载和版本选择功能
- 初始化生成器并启动配置流程

**代码量**: ~100 行

### 2. 核心生成器 (`generator.py`)

**职责**:
- `ValuesGenerator` 类定义
- 模板文件加载和保存
- YAML 格式保留（使用 ruamel.yaml）
- 配置生成主流程

**关键方法**:
- `__init__()`: 初始化生成器
- `load_template()`: 加载 values.yaml 模板
- `save()`: 保存生成的配置
- `generate()`: 主配置生成流程
- `_update_dict_recursive()`: 递归更新字典，保留格式

**代码量**: ~350 行

### 3. 版本管理 (`version_manager.py`)

**职责**:
- 管理不同版本的 Dify EE 配置
- 定义版本与模块的映射关系
- 交互式版本选择
- 模块兼容性检查

**关键方法**:
- `get_available_versions()`: 获取可用版本列表
- `get_version_modules()`: 获取版本支持的模块
- `is_module_supported()`: 检查模块是否支持
- `prompt_version_selection()`: 交互式选择版本

**代码量**: ~120 行

### 4. 工具模块 (`utils/`)

#### `colors.py`
- `Colors` 类：终端颜色常量
- 打印函数：`print_header`, `print_section`, `print_info`, `print_success`, `print_warning`, `print_error`

#### `prompts.py`
- `prompt()`: 文本输入提示
- `prompt_yes_no()`: 是/否选择
- `prompt_choice()`: 多选提示

#### `downloader.py`
- `download_values_from_helm_repo()`: 从 Helm 仓库下载（必选，需要 Helm）
- `get_or_download_values()`: 获取或下载 values.yaml
- `download_and_extract_chart()`: 下载并解压 Helm Chart

#### `secrets.py`
- `generate_secret()`: 生成密钥（使用 openssl）

### 5. 配置模块 (`modules/`)

每个模块都是一个独立的函数，接收 `generator` 对象作为参数：

#### `global_config.py`
- `configure_global(generator)`: 全局配置
  - 密钥生成
  - 域名配置
  - RAG 配置

#### `infrastructure.py`
- `configure_infrastructure(generator)`: 基础设施配置
  - PostgreSQL 配置
  - Redis 配置
  - 向量数据库配置
  - 存储配置（S3/MinIO 等）

#### `networking.py`
- `configure_networking(generator)`: 网络配置
  - TLS 配置
  - Ingress 配置
  - cert-manager 支持

#### `mail.py`
- `configure_mail(generator)`: 邮件配置
  - SMTP 配置
  - Resend 配置

#### `plugins.py`
- `configure_plugins(generator)`: 插件配置
  - 镜像仓库配置
  - ECR 鉴权配置
  - 协议选择

#### `services.py`
- `configure_services(generator)`: 服务配置
  - Enterprise 配置
  - License 配置
  - 服务启用状态

## 代码组织原则

### 1. 单一职责原则
每个模块只负责一个特定的功能领域。

### 2. 依赖注入
配置模块函数接收 `generator` 对象作为参数，而不是直接访问全局状态。

### 3. 可扩展性
- 添加新版本：只需在 `VersionManager.VERSION_CONFIGS` 中添加配置
- 添加新模块：创建新的模块文件并在 `modules/__init__.py` 中导出
- 添加新工具：在 `utils/` 目录下创建新文件

### 4. 清晰的导入
使用 `__init__.py` 文件统一导出，简化导入语句。

## 使用示例

### 添加新版本

在 `version_manager.py` 中：

```python
VERSION_CONFIGS = {
    # ... 现有版本 ...
    "4.0": {
        "name": "Dify Enterprise Edition 4.0",
        "modules": ["global", "infrastructure", "networking", "mail", "plugins", "services"],
        "description": "新版本说明"
    }
}
```

### 添加新配置模块

1. 创建 `modules/new_module.py`:

```python
"""New configuration module"""

from utils import print_header, print_section, prompt
from version_manager import VersionManager

def configure_new_module(generator):
    """配置新模块"""
    if not VersionManager.is_module_supported(generator.version, "new_module"):
        print_warning(f"版本 {generator.version} 不支持新模块，跳过")
        return
    
    print_header("模块 X: 新模块配置")
    # ... 配置逻辑 ...
```

2. 在 `modules/__init__.py` 中导出：

```python
from .new_module import configure_new_module
```

3. 在 `generator.py` 的 `generate()` 方法中注册：

```python
module_configs = {
    # ... 现有模块 ...
    "new_module": configure_new_module,
}
```

## 优势

1. **可读性**: 每个文件职责明确，代码量适中
2. **可维护性**: 修改某个模块不影响其他模块
3. **可测试性**: 每个模块可以独立测试
4. **可扩展性**: 添加新功能只需添加新文件，无需修改现有代码
5. **团队协作**: 多人可以同时修改不同模块，减少冲突

## 文件大小对比

- **重构前**: 1 个文件，~2000 行
- **重构后**: 13 个文件，平均每个文件 ~150 行

## 注意事项

1. 所有模块函数都接收 `generator` 对象作为第一个参数
2. 使用 `generator.values` 访问配置字典
3. 使用 `generator.version` 访问当前版本
4. 模块函数应该检查版本兼容性（如 `plugins.py`）

