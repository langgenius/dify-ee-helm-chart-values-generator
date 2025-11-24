# Dify EE（企业版）Helm Chart Values 生成器

> 一个交互式工具，用于生成 Dify Enterprise Edition 的生产环境 Helm Chart values 配置文件

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![Code style: PEP 8](https://img.shields.io/badge/code%20style-PEP%208-orange.svg)](https://www.python.org/dev/peps/pep-0008/)

[English](README.md) | **中文**

## 📋 项目简介

本项目提供了一个 Python 脚本 `generate-values-prd.py`，通过交互式引导帮助用户生成 `values-prd.yaml` 配置文件。脚本采用模块化设计，自动处理配置项之间的联动关系，确保配置的一致性和正确性。

## ✨ 功能特点

- ✅ **模块化配置**: 将配置分为 6 个主要模块，逻辑清晰
- ✅ **自动处理联动**: 自动处理互斥选择和依赖关系
- ✅ **密钥自动生成**: 所有密钥按注释要求自动生成（使用 openssl）
  - `appSecretKey`: 42 字节
  - `innerApiKey`: 42 字节
  - `enterprise.appSecretKey`: 42 字节
  - `enterprise.adminAPIsSecretKeySalt`: 42 字节
  - `enterprise.passwordEncryptionKey`: 32 字节（AES-256）
- ✅ **TLS 联动检查**: TLS 配置与 Ingress 联动，自动检查一致性避免 CORS 问题
- ✅ **RAG 联动**: 自动处理 RAG 类型与 unstructured 模块的联动关系
- ✅ **交互式引导**: 友好的命令行交互界面，详细配置每个数据库和 Redis 连接
- ✅ **进度保存**: 支持中断后保存部分配置

## 🚀 快速开始

### 前置要求

- Python 3.6+
- PyYAML 库
- `openssl`（用于生成密钥，通常系统已自带）
- `ruamel.yaml`（推荐）：用于保留 YAML 文件的格式、注释和引号
- `helm`（必选）：用于从 Helm Chart 仓库下载 values.yaml。脚本需要 Helm 才能正常工作。

### 安装依赖

**使用 uv（推荐，更快）：**

```bash
# 1. 安装 uv（如果未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 创建虚拟环境
uv venv

# 3. 激活虚拟环境（可选，uv 会自动检测）
source .venv/bin/activate

# 4. 安装依赖
uv pip install -r requirements.txt
```

**或使用 pip：**

```bash
pip install -r requirements.txt
```

### 使用方法

**基本使用（自动下载最新版本的 values.yaml）：**

```bash
python generate-values-prd.py
```

**指定 Helm Chart 版本：**

```bash
python generate-values-prd.py --chart-version 3.5.6
```

**使用本地 values.yaml（必须指定版本）：**

```bash
python generate-values-prd.py --local --chart-version 3.5.6
```

**强制重新下载：**

```bash
python generate-values-prd.py --force-download
```

**指定语言：**

```bash
python generate-values-prd.py --lang zh
```

**命令行选项：**

- `--chart-version, -c`: 指定 Helm Chart 版本（默认：交互式选择）
- `--local, -l`: 使用本地 values.yaml 文件（需要指定 --chart-version）
- `--force-download, -f`: 强制重新下载 values.yaml（忽略缓存）
- `--lang, --language`: 语言选择（en/zh，默认：交互式选择）
- `--repo-url`: 自定义 Helm Chart 仓库 URL

**注意：** Dify EE 版本会根据 Helm Chart 版本自动确定。Chart 版本 3.x 映射到 EE 3.x，Chart 版本 2.x 映射到 EE 2.x，以此类推。

脚本需要安装 Helm 才能正常工作。它会自动从官方 Dify Helm Chart 仓库下载 `values.yaml`（如果本地不存在）。下载的文件会缓存在 `.cache/` 目录中。

脚本会引导你完成以下配置模块：

1. **全局配置模块** - 影响所有服务
2. **基础设施模块** - 数据库、存储、缓存（互斥选择）
3. **网络配置模块** - Ingress 配置
4. **邮件配置模块** - 邮件服务配置
5. **插件配置模块** - 插件连接器镜像仓库配置（仅 3.x 版本）
6. **服务配置模块** - 应用服务配置

生成的配置文件将保存为 `out/values-prd-{version}.yaml`（例如：`out/values-prd-3.5.6.yaml`）。

## 📁 项目结构

```
.
├── generate-values-prd.py    # 主脚本文件
├── values.yaml               # 基础配置文件模板（自动从 Helm Chart 仓库下载）
├── values-prd.yaml          # 生成的生产环境配置（gitignore）
├── .cache/                  # 缓存目录（存储下载的 values.yaml）
├── pyproject.toml           # Python 项目配置
├── requirements.txt         # Python 依赖列表
├── LICENSE                  # MIT 许可证
├── CONTRIBUTING.md          # 贡献指南
├── .gitignore              # Git 忽略文件配置
└── docs/                   # 文档目录
    ├── README-GENERATOR.md  # 详细使用说明
    ├── MODULES.md          # 模块划分说明
    ├── FLOWCHART.md        # 流程图
    ├── KIND-NETWORKING.md  # Kind 网络配置说明
    ├── IMPROVEMENTS.md     # 改进记录
    └── CHANGELOG.md        # 更新日志
```

## 📚 文档

详细的文档请参考 `docs/` 目录：

- [README-GENERATOR.md](docs/README-GENERATOR.md) - 完整的使用说明和示例
- [MODULES.md](docs/MODULES.md) - 模块划分与联动关系说明
- [FLOWCHART.md](docs/FLOWCHART.md) - 配置流程图
- [KIND-NETWORKING.md](docs/KIND-NETWORKING.md) - Kind 集群网络配置说明

## 🔧 配置模块

### 模块 1: 全局配置
- 影响所有服务
- 包括密钥、域名、RAG 配置等

### 模块 2: 基础设施配置
- 数据库选择（PostgreSQL/MySQL）
- 存储选择（MinIO/S3/Azure Blob 等）
- 缓存选择（Redis）
- 向量数据库选择（Qdrant/Weaviate/Milvus）

### 模块 3: 网络配置
- Ingress 配置
- TLS 设置
- 证书管理（支持 cert-manager）

### 模块 4: 邮件配置
- SMTP 服务器配置
- Resend 服务配置
- 邮件服务设置

### 模块 5: 插件配置
- 镜像仓库类型（Docker/ECR）
- 鉴权方式（IRSA/K8s Secret）
- 协议选择（HTTPS/HTTP）

### 模块 6: 服务配置
- Enterprise 许可证配置
- 服务启用/禁用开关
- 资源限制

### 联动关系

脚本会自动处理以下联动关系：

- **RAG 联动**: `rag.etlType = "dify"` → `unstructured.enabled = false`
- **RAG 联动**: `rag.etlType = "Unstructured"` → `unstructured.enabled = true`
- **TLS 联动**: TLS 配置与 Ingress 自动同步，避免 CORS 问题
- **基础设施互斥**: 数据库、存储、缓存的选择互斥

## 🔒 安全注意事项

- 生成的 `values-prd.yaml` 包含敏感信息，已添加到 `.gitignore`
- `email-server.txt` 等敏感文件不会被提交到仓库
- 所有密钥使用 `openssl` 自动生成，确保安全性
- 支持 IRSA（IAM Roles for Service Accounts）用于 AWS ECR 认证

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解贡献指南和代码规范。

## 📝 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🔗 相关链接

- [Dify 官方文档](https://docs.dify.ai/)
- [Helm Chart 文档](https://helm.sh/docs/)
- [Dify Enterprise 文档](https://enterprise-docs.dify.ai/)

## 🙏 致谢

- 为 [Dify](https://github.com/langgenius/dify) Enterprise Edition 构建
- 使用 [ruamel.yaml](https://yaml.readthedocs.io/) 进行 YAML 处理

