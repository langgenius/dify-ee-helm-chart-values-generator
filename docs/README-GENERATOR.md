# Dify EE（企业版）Helm Chart Values 生成器使用说明

## 概述

`generate-values-prd.py` 是一个交互式脚本，用于生成生产环境的 `values-prd.yaml` 配置文件。脚本将配置过程分解为多个模块，并自动处理模块间的联动关系。

## 功能特点

- ✅ **模块化配置**: 将配置分为6个主要模块，逻辑清晰
- ✅ **自动处理联动**: 自动处理互斥选择和依赖关系
- ✅ **密钥自动生成**: 所有密钥按注释要求自动生成（使用 openssl）
  - `appSecretKey`: 42字节
  - `innerApiKey`: 42字节
  - `enterprise.appSecretKey`: 42字节
  - `enterprise.adminAPIsSecretKeySalt`: 42字节
  - `enterprise.passwordEncryptionKey`: 32字节（AES-256）
- ✅ **TLS联动检查**: TLS配置与Ingress联动，自动检查一致性避免CORS问题
- ✅ **RAG联动**: 自动处理RAG类型与unstructured模块的联动关系
- ✅ **交互式引导**: 友好的命令行交互界面，详细配置每个数据库和Redis连接
- ✅ **进度保存**: 支持中断后保存部分配置

## 前置要求

- Python 3.6+
- PyYAML 库（通常已包含在Python中）
- openssl（用于生成密钥，通常系统已自带）
- **ruamel.yaml（推荐）**：用于保留 YAML 文件的格式、注释和引号
- **helm（必选）**：用于从 Helm Chart 仓库下载 values.yaml。脚本需要 Helm 才能正常工作。

### 安装依赖

**使用 uv（推荐，更快）：**

uv 默认使用虚拟环境来管理依赖，推荐的工作流程：

```bash
# 1. 安装 uv（如果未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 创建虚拟环境（如果还没有）
uv venv

# 3. 激活虚拟环境（可选，uv 会自动检测）
# macOS/Linux:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

# 4. 使用 uv 安装依赖（会自动使用 .venv）
uv pip install -r requirements.txt

# 或者从 pyproject.toml 安装
uv pip install -e .

# 或者使用 uv 的项目管理功能（推荐）
uv sync  # 会自动创建 venv 并安装依赖
```

**不使用虚拟环境（不推荐）：**

如果要在系统 Python 中安装，使用 `--system` 标志：

```bash
uv pip install --system -r requirements.txt
```

**使用 pip（传统方式）：**

```bash
# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# 安装依赖
pip3 install -r requirements.txt
```

> **注意**：uv 默认会查找并使用项目目录下的 `.venv` 虚拟环境。如果没有虚拟环境，`uv pip install` 会报错，提示您创建虚拟环境或使用 `--system` 标志。

> **注意**：如果不安装 `ruamel.yaml`，脚本仍可使用，但生成的 YAML 文件可能会丢失：
> - 注释（如 `extraEnv` 的注释）
> - 字符串引号
> - 多行字符串格式（如 `squidConf`）
> 
> 强烈建议安装 `ruamel.yaml` 以获得最佳体验。

## 使用方法

### 基本使用

```bash
python3 generate-values-prd.py
```

或直接运行（已设置可执行权限）：
```bash
./generate-values-prd.py
```

### 配置流程

脚本会按以下顺序引导您完成配置：

1. **模块 1: 全局配置**
   - **密钥自动生成**（appSecretKey, innerApiKey）
   - 域名配置（7个域名）
   - RAG配置（自动联动unstructured模块）

2. **模块 2: 基础设施配置**
   - PostgreSQL（外部/内置）
     - 外部：交互式配置4个数据库的完整信息
     - 内置：自动生成root密码
   - Redis（外部/内置）
     - 外部：交互式配置，支持Sentinel/Cluster（互斥）
     - 内置：自动生成密码
   - 向量数据库（外部/内置）
   - 存储配置（local/s3/云存储）
     - S3：选择提供商（AWS S3/MinIO/其他），自动设置useAwsS3
     - AWS S3：支持两种授权方式
       - IRSA 模式（推荐）：使用 IAM Roles for Service Accounts
       - Access Key 模式（备选）：使用 Access Key 和 Secret Key
     - 可同时配置MinIO服务
   - MinIO配置（自动生成root密码）

3. **模块 3: 网络配置**
   - **TLS配置**（全局TLS，影响CORS）
   - Ingress配置
   - Ingress TLS配置（与全局TLS联动检查）
   - cert-manager支持

4. **模块 4: 邮件配置**
   - 邮件服务类型选择
   - 邮件服务凭证配置

5. **模块 5: 插件配置**
   - 镜像仓库类型选择（docker/ecr）
   - 镜像仓库前缀配置
   - ECR 鉴权方式选择（IRSA/K8s Secret）
   - 协议类型选择（HTTPS/HTTP）

6. **模块 6: 服务配置**
   - Enterprise服务配置（所有密钥自动生成）
   - License配置（online/offline）
   - 各服务启用状态

### 交互说明

- **文本输入**: 直接输入值，按回车确认
- **默认值**: 显示在 `[默认值]` 中，直接回车使用默认值
- **是/否选择**: 输入 `y`/`yes` 或 `n`/`no`，直接回车使用默认值
- **多选**: 输入数字选择对应选项
- **中断**: 按 `Ctrl+C` 可以中断，可选择保存部分配置

## 模块联动关系

详细的模块划分和联动关系请参考 [MODULES.md](./MODULES.md)

### 关键联动点

1. **密钥生成**: 所有密钥自动生成，无需手动输入
2. **RAG联动**: 
   - `rag.etlType = "dify"` → `unstructured.enabled = false`
   - `rag.etlType = "Unstructured"` → `unstructured.enabled = true`
3. **PostgreSQL**: `externalPostgres.enabled` 和 `postgresql.enabled` 互斥
4. **Redis**: `externalRedis.enabled` 和 `redis.enabled` 互斥，Sentinel和Cluster互斥
5. **VectorDB**: `vectorDB.useExternal` 决定使用外部还是内置
6. **存储**: `persistence.type` 决定存储类型和相关配置
   - S3类型：选择提供商自动设置 `useAwsS3`
   - 可同时配置MinIO服务
7. **TLS联动（重要）**: `global.useTLS` 与 `ingress.tls` 必须一致，避免CORS问题
8. **Enterprise**: 所有密钥自动生成，需要配置 License

## 示例

### 示例1: 使用外部数据库和Redis

```bash
$ python3 generate-values-prd.py

============================================================
          Dify EE（企业版）Helm Chart Values 生成器
============================================================

>>> 模块 1: 全局配置
ℹ 全局配置影响所有服务的运行

是否自动生成 appSecretKey? [Y/n]: [回车]
✓ 已生成 appSecretKey: xK9mP2nQ8rS5tU7vW...

>>> 模块 2: 基础设施配置
是否使用外部 PostgreSQL? [y/N]: y
PostgreSQL 地址: postgres.example.com
PostgreSQL 端口 [5432]: [回车]
...
```

### 示例2: 使用内置数据库

```bash
>>> 模块 2: 基础设施配置
是否使用外部 PostgreSQL? [y/N]: [回车]  # 使用默认值 N
将使用 Helm Chart 内置的 PostgreSQL
是否配置 PostgreSQL 密码? [Y/n]: [回车]
是否自动生成密码? [Y/n]: [回车]
✓ 已生成 PostgreSQL 密码
```

## 输出文件

脚本会生成 `values-prd.yaml` 文件，包含所有配置项。

### 使用生成的配置

```bash
# 检查配置
helm template . -f values-prd.yaml --debug

# 安装
helm install dify-prd . -f values-prd.yaml

# 升级
helm upgrade dify-prd . -f values-prd.yaml
```

## 注意事项

1. **密钥安全**: 
   - 所有密钥自动生成，会显示在终端，请妥善保管
   - 建议将密钥存储在密钥管理系统中
   - 密钥生成使用 `openssl rand -base64`，安全可靠

2. **TLS配置**:
   - **重要**: 全局TLS (`global.useTLS`) 与 Ingress TLS 必须保持一致
   - 不一致会导致CORS跨域问题
   - 脚本会自动检查并提供警告

3. **RAG配置**:
   - 选择 `dify` 类型会自动关闭 `unstructured` 模块
   - 选择 `Unstructured` 类型会自动启用 `unstructured` 模块

4. **存储配置**:
   - S3存储需要选择提供商，脚本会自动设置 `useAwsS3`
   - AWS S3 → `useAwsS3 = true`
     - 支持两种授权方式：IRSA 模式（推荐）或 Access Key 模式
     - IRSA 模式需要配置 ServiceAccount 和 IAM Role
     - Access Key 模式需要配置 Access Key 和 Secret Key
   - MinIO或其他兼容S3服务 → `useAwsS3 = false`

5. **配置验证**:
   - 生成后请仔细检查配置文件
   - 特别是数据库连接信息、存储配置等

6. **部分配置**:
   - 某些高级配置项可能需要在生成后手动调整
   - 如资源限制、节点选择器等

7. **环境差异**:
   - 开发、测试、生产环境可能需要不同的配置
   - 建议为每个环境生成独立的配置文件

## 故障排除

### 问题1: 无法生成密钥

如果 openssl 不可用，脚本会使用 Python 的 secrets 模块作为备选。

### 问题2: YAML格式错误或丢失注释/引号

**问题**：生成的 YAML 文件丢失了注释、引号或格式不正确。

**解决方案**：
1. 安装 `ruamel.yaml` 以获得更好的格式保留：
   ```bash
   pip3 install ruamel.yaml
   ```
2. 重新运行脚本生成配置文件

**验证**：运行测试脚本检查 ruamel.yaml 是否正常工作：
```bash
python3 test-ruamel.py
```

如果未安装 `ruamel.yaml`，脚本会回退到标准 yaml 库，但会丢失注释和格式。

**基础依赖**：确保 Python 版本 >= 3.6，并安装了 PyYAML：
```bash
pip3 install --upgrade pyyaml
```

### 问题3: 编码问题

脚本使用 UTF-8 编码，如果遇到编码问题，请检查终端设置。

## 扩展开发

脚本采用模块化设计，可以轻松扩展：

1. **添加新模块**: 在 `ValuesGenerator` 类中添加新的 `configure_*` 方法
2. **添加验证**: 在配置方法中添加验证逻辑
3. **添加联动**: 在相关模块中添加联动处理

## 相关文档

- [MODULES.md](./MODULES.md) - 模块划分和联动关系详细说明
- [KIND-NETWORKING.md](./KIND-NETWORKING.md) - Kind 集群网络配置指南
- [IMPROVEMENTS.md](./IMPROVEMENTS.md) - 脚本改进说明（格式保留、注释保留等）
- [values.yaml](./values.yaml) - 原始模板文件
- [Chart.yaml](./Chart.yaml) - Helm Chart 元数据

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个工具！

