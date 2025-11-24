# 配置说明 (Configuration Guide)

## 概述

项目使用 `config.py` 文件集中管理所有配置常量，提高了代码的可维护性和可扩展性。

## 配置文件位置

`config.py` - 项目根目录下的配置文件

## 配置项说明

### Helm Chart 配置

```python
HELM_CHART_NAME = "dify"                    # Helm Chart 名称
HELM_REPO_URL = "https://langgenius.github.io/dify-helm"  # Helm 仓库 URL
HELM_REPO_NAME = "dify-helm"                # Helm 仓库名称
```

**用途**: 用于从 Helm 仓库下载和查询 Chart 信息。

**修改场景**: 
- 使用不同的 Helm Chart 仓库
- 使用不同的 Chart 名称
- 切换到私有仓库

### 缓存配置

```python
CACHE_DIR = ".cache"                        # 缓存目录
LOCAL_VALUES_FILE = "values.yaml"           # 本地 values.yaml 文件名
```

**用途**: 控制缓存和本地文件的存储位置。

**修改场景**:
- 更改缓存目录位置
- 使用不同的本地文件名

### 输出配置

```python
OUTPUT_FILE = "values-prd.yaml"            # 输出文件名
```

**用途**: 指定生成的配置文件名称。

**修改场景**:
- 使用不同的输出文件名
- 支持多环境配置（如 `values-dev.yaml`, `values-prod.yaml`）

### 超时配置

```python
DOWNLOAD_TIMEOUT = 10                       # 下载超时时间（秒）
```

**用途**: 控制网络请求的超时时间。

**修改场景**:
- 网络较慢时增加超时时间
- 快速失败场景下减少超时时间

### 版本配置

```python
DEFAULT_CHART_VERSION = None                # 默认 Chart 版本（None 表示最新）
DEFAULT_EE_VERSION = None                    # 默认 Dify EE 版本（None 表示交互式选择）
```

**用途**: 设置默认版本，避免每次都需要选择。

**修改场景**:
- 固定使用特定版本
- 设置默认版本以减少交互

## 使用方式

### 在代码中引用配置

```python
import config

# 使用配置常量
chart_name = config.HELM_CHART_NAME
repo_url = config.HELM_REPO_URL
output_file = config.OUTPUT_FILE
```

### 函数参数默认值

所有相关函数都支持通过参数覆盖配置，同时使用配置作为默认值：

```python
from utils.downloader import get_or_download_values

# 使用默认配置
values_file = get_or_download_values()

# 覆盖配置
values_file = get_or_download_values(
    repo_url="https://custom-repo.example.com",
    repo_name="custom-repo"
)
```

## 扩展性

### 支持不同的 Helm Chart 仓库

修改 `config.py`:

```python
HELM_CHART_NAME = "my-chart"
HELM_REPO_URL = "https://my-repo.example.com/helm"
HELM_REPO_NAME = "my-repo"
```

### 支持多环境配置

可以创建多个配置文件：

- `config.py` - 默认配置
- `config.dev.py` - 开发环境
- `config.prod.py` - 生产环境

然后通过环境变量或命令行参数选择：

```bash
# 使用开发配置
CONFIG_FILE=config.dev python generate-values-prd.py

# 使用生产配置
CONFIG_FILE=config.prod python generate-values-prd.py
```

### 命令行参数覆盖

所有配置都可以通过命令行参数覆盖：

```bash
# 覆盖仓库 URL
python generate-values-prd.py --repo-url https://custom-repo.example.com

# 覆盖 Chart 名称和仓库名称
python generate-values-prd.py --chart-name my-chart --repo-name my-repo
```

## 最佳实践

1. **集中管理**: 所有配置常量都在 `config.py` 中定义
2. **默认值**: 函数参数使用配置常量作为默认值
3. **可覆盖**: 支持通过函数参数或命令行参数覆盖配置
4. **文档化**: 每个配置项都有清晰的注释说明用途

## 配置项列表

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `HELM_CHART_NAME` | str | `"dify"` | Helm Chart 名称 |
| `HELM_REPO_URL` | str | `"https://langgenius.github.io/dify-helm"` | Helm 仓库 URL |
| `HELM_REPO_NAME` | str | `"dify-helm"` | Helm 仓库名称 |
| `CACHE_DIR` | str | `".cache"` | 缓存目录 |
| `LOCAL_VALUES_FILE` | str | `"values.yaml"` | 本地 values.yaml 文件名 |
| `OUTPUT_FILE` | str | `"values-prd.yaml"` | 输出文件名 |
| `DOWNLOAD_TIMEOUT` | int | `10` | 下载超时时间（秒） |
| `DEFAULT_CHART_VERSION` | Optional[str] | `None` | 默认 Chart 版本 |
| `DEFAULT_EE_VERSION` | Optional[str] | `None` | 默认 Dify EE 版本 |

## 示例

### 示例 1: 切换到私有仓库

```python
# config.py
HELM_REPO_URL = "https://private-repo.example.com/helm"
HELM_REPO_NAME = "private-repo"
```

### 示例 2: 使用不同的输出文件名

```python
# config.py
OUTPUT_FILE = "values-production.yaml"
```

### 示例 3: 增加下载超时时间

```python
# config.py
DOWNLOAD_TIMEOUT = 30  # 30 秒
```

## 注意事项

1. 修改配置后，需要重新运行脚本才能生效
2. 命令行参数优先级高于配置文件
3. 确保配置值的格式正确（URL、文件名等）
4. 修改仓库 URL 时，确保仓库可访问且格式正确

