# Dify EE（企业版）Helm Chart Values 配置模块划分与联动关系

## 模块划分

### 模块 1: 全局配置 (Global Configuration)
**影响范围**: 所有服务

**配置项**:
- `global.appSecretKey`: 会话签名和数据库加密密钥，**自动生成** (`openssl rand -base64 42`)
- `global.innerApiKey`: 内部API调用密钥，**自动生成** (`openssl rand -base64 42`)
- `global.*Domain`: 各种域名配置（影响CORS和API端点）
- `global.dbMigrationEnabled`: 数据库迁移开关
- `global.rag`: RAG相关配置
  - `rag.etlType`: RAG ETL类型 (dify/Unstructured)
  - `rag.keywordDataSourceType`: 关键词数据源类型
    - **说明**: RAG 关键词检索（Keyword Search）时的关键词存储位置
    - `object_storage`: 存储在对象存储中（如 MinIO、S3）
    - `database`: 存储在数据库中
  - `rag.topKMaxValue`: Top-K最大值
  - `rag.indexingMaxSegmentationTokensLength`: 文档分块最大token长度
- `global.integrations`: 第三方集成配置（如Notion）
- `global.marketplace`: 市场配置

**联动关系**:
- `global.appSecretKey` 与 `enterprise.appSecretKey` 可以相同或不同（都自动生成）
- **RAG联动**: `rag.etlType = "dify"` → `unstructured.enabled = false`
- **RAG联动**: `rag.etlType = "Unstructured"` → `unstructured.enabled = true`
- 域名配置影响 Ingress 和 CORS 设置
- **注意**: `global.useTLS` 已移至网络配置模块，与 Ingress TLS 联动

---

### 模块 2: 基础设施配置 (Infrastructure)
**影响范围**: 数据持久化和服务依赖

#### 2.1 PostgreSQL 数据库
**互斥选择**:
- `externalPostgres.enabled = true` → 使用外部PostgreSQL
- `postgresql.enabled = true` → 使用Helm Chart内置PostgreSQL

**联动关系**:
- 如果使用外部PostgreSQL，需要**交互式配置**4个数据库的完整信息：
  - `dify`: 主数据库（数据库名、用户名、密码、SSL模式、额外参数、字符集、URI方案）
  - `plugin_daemon`: 插件守护进程数据库（完整配置）
  - `enterprise`: 企业版数据库（完整配置）
  - `audit`: 审计数据库（完整配置）
- 如果使用内置PostgreSQL，会自动创建这些数据库，root密码自动生成

#### 2.2 Redis 缓存
**互斥选择**:
- `externalRedis.enabled = true` → 使用外部Redis
- `redis.enabled = true` → 使用Helm Chart内置Redis

**联动关系**:
- Redis Sentinel 和 Cluster 配置**互斥**
- 如果使用外部Redis，需要**交互式配置**完整连接信息：
  - 基础配置：host, port, password, username, db, useSSL
  - Sentinel模式（可选）：nodes, serviceName, username, password, socketTimeout
  - Cluster模式（可选）：nodes, password
- 如果使用内置Redis，密码自动生成

#### 2.3 向量数据库 (VectorDB)
**互斥选择**:
- `vectorDB.useExternal = true` → 使用外部向量数据库
- `vectorDB.useExternal = false` → 使用内置向量数据库（qdrant/weaviate）

**联动关系**:
- 如果使用外部向量数据库：
  - `vectorDB.externalType` 决定配置哪个外部服务
  - 根据类型配置对应的连接信息（如 `externalQdrant`, `externalWeaviate`）
- 如果使用内置向量数据库：
  - `qdrant.enabled = true` 或 `weaviate.enabled = true`（互斥）

#### 2.4 存储配置 (Persistence)
**选择**: `persistence.type` 决定存储类型
- `local`: 本地存储（需要PVC）
- `s3`: S3兼容存储（AWS S3, Cloudflare R2等）
- `azure-blob`: Azure Blob Storage
- `aliyun-oss`: 阿里云OSS
- `google-storage`: Google Cloud Storage
- `tencent-cos`: 腾讯云COS
- `volcengine-tos`: 火山引擎TOS
- `huawei-obs`: 华为云OBS

**联动关系**:
- 如果 `persistence.type = "s3"`：
  - 需要选择S3服务提供商（AWS S3 / MinIO / Cloudflare R2 / 其他兼容S3服务）
  - **`useAwsS3` 自动设置**：
    - AWS S3 → `useAwsS3 = true`
    - MinIO 或其他兼容S3服务 → `useAwsS3 = false`
  - **AWS S3 授权方式（二选一）**：
    - **IRSA 模式（推荐）**：
      - `useAwsManagedIam = true`
      - 需要配置 ServiceAccount（`api.serviceAccountName` 和 `worker.serviceAccountName`）
      - 不配置 `accessKey` 和 `secretKey`
      - 详细配置参考：[AWS IRSA 模式配置文档](https://enterprise-docs.dify.ai/versions/3-0-x/zh-cn/deployment/cloud-infrastructure/aws-setup#三、irsa-模式配置)
    - **Access Key 模式（备选）**：
      - `useAwsManagedIam = false`
      - 需要配置 `accessKey` 和 `secretKey`
      - 确保 IAM 用户只具备 S3 访问权限
  - **AWS S3 Endpoint URL**：
    - 必填项，使用英文提示
    - 格式示例：`https://s3.us-west-2.amazonaws.com`
- 如果使用 `local` 存储，需要配置 StorageClass 和 PVC 大小
- 如果使用云存储，需要配置对应的访问凭证

#### 2.5 MinIO 对象存储
**联动关系（重要）**:
- **内置 MinIO 的启用逻辑**：
  - `persistence.type = "s3"` && `useAwsS3 = true` (AWS S3) → `minio.enabled = false`（不启用）
  - `persistence.type = "s3"` && `useAwsS3 = false` (MinIO或其他S3兼容) → `minio.enabled = true`（启用）
  - `persistence.type != "s3"` (local/azure-blob等) → `minio.enabled = true`（启用）
- **注意**: 对象存储不能使用内置的 MinIO，内置 MinIO 仅在 persistence 不是 AWS S3 时需要开启
- MinIO的root密码自动生成

---

### 模块 3: 网络配置 (Networking)
**配置项**:
- `global.useTLS`: **TLS配置已移至此处**，影响内部服务通信和CORS设置
- `ingress.enabled`: 是否启用Ingress
- `ingress.className`: Ingress Controller类名
- `ingress.annotations`: Ingress注解（支持cert-manager）
- `ingress.tls`: Ingress TLS配置（hosts列表、secretName）
- `ingress.useIpAsHost`: 是否使用IP地址作为主机名（仅非企业版）

**联动关系**:
- **TLS联动（重要）**: `global.useTLS` 与 `ingress.tls` **必须保持一致**，否则会出现CORS跨域问题
- 脚本会自动检查TLS一致性，并提供警告和建议
- Ingress配置影响域名访问
- 与 `global.*Domain` 配置联动
- 支持cert-manager自动证书管理（通过annotations配置ClusterIssuer）

---

### 模块 4: 邮件配置 (Mail Configuration)
**选择**: `mail.type` 决定邮件服务类型
- `""`: 不配置邮件
- `resend`: 使用Resend服务
- `smtp`: 使用SMTP服务器

**联动关系**:
- 根据类型配置对应的凭证和端点
- 影响用户注册、密码重置等功能的邮件发送

---

### 模块 5: 插件配置 (Plugin Configuration)
**影响范围**: 插件系统的镜像仓库和认证

**配置项**:
- `plugin_connector.imageRepoType`: 镜像仓库类型
  - `docker`: Docker Hub 或其他兼容 Docker 的仓库
  - `ecr`: AWS ECR
- `plugin_connector.imageRepoPrefix`: 镜像仓库前缀
  - Docker格式: `docker.io/your-image-repo-prefix` 或 `registry.example.com/namespace`
  - ECR格式: `{account_id}.dkr.ecr.{region}.amazonaws.com/{prefix}`（prefix可选）
- `plugin_connector.imageRepoSecret`: 镜像仓库 Secret 名称（K8s Secret 模式）
- `plugin_connector.insecureImageRepo`: 是否不使用 HTTPS 协议（不推荐）
- `plugin_connector.ecrRegion`: ECR 区域（如果使用 ECR）
- `plugin_connector.customServiceAccount`: 插件构建 ServiceAccount（IRSA 模式）
- `plugin_connector.runnerServiceAccount`: 插件运行 ServiceAccount（IRSA 模式）

**ECR 鉴权方式**:
- **IRSA 模式（推荐）**: 使用 IAM Roles for Service Accounts
  - 需要配置 `customServiceAccount` 和 `runnerServiceAccount`
  - 详细配置参考: https://enterprise-docs.dify.ai/versions/3-0-x/zh-cn/deployment/cloud-infrastructure/aws-setup#三、irsa-模式配置
  - 不需要配置 `imageRepoSecret`
- **K8s Secret 模式**: 使用 Kubernetes Secret 存储 AWS 凭证
  - 需要配置 `imageRepoSecret`
  - 详细配置参考: https://enterprise-docs.dify.ai/versions/3-0-x/zh-cn/deployment/cloud-infrastructure/aws-setup#步骤-2：创建-kubernetes-secret

**配置顺序**:
1. 选择镜像仓库类型（docker/ecr）
2. 如果选择 ECR：
   - 配置 ECR 区域
   - 配置 ECR 账户ID
   - 配置镜像仓库前缀（自动生成格式）
3. 配置镜像仓库前缀（Docker 模式）
4. 如果选择 ECR，选择鉴权方式：
   - IRSA 模式：配置 ServiceAccount
   - K8s Secret 模式：配置 imageRepoSecret
5. 如果选择 Docker，配置 imageRepoSecret
6. 选择协议类型（HTTPS/HTTP）

**联动关系**:
- ECR 模式需要根据鉴权方式配置不同的字段
- IRSA 模式不需要 imageRepoSecret
- K8s Secret 模式需要 imageRepoSecret

---

### 模块 6: 服务配置 (Services Configuration)
**服务列表**:
- `api`: API服务
- `worker`: 工作进程
- `workerBeat`: 定时任务
- `web`: Web前端
- `sandbox`: 沙箱环境
- `enterprise`: 企业版服务
- `enterpriseAudit`: 企业版审计服务
- `enterpriseFrontend`: 企业版前端
- `ssrfProxy`: SSRF代理
- `unstructured`: 非结构化数据处理
- `plugin_daemon`: 插件守护进程
- `plugin_manager`: 插件管理器
- `plugin_controller`: 插件控制器
- `plugin_connector`: 插件连接器
- `gateway`: 网关服务

**联动关系**:
- Enterprise相关服务需要License配置
- **所有Enterprise密钥自动生成**：
  - `enterprise.appSecretKey`: 42字节 (`openssl rand -base64 42`)
  - `enterprise.adminAPIsSecretKeySalt`: 42字节 (`openssl rand -base64 42`)
  - `enterprise.passwordEncryptionKey`: 32字节 (`openssl rand -base64 32`，AES-256密钥)
- License模式选择（online/offline）：
  - online: 需要配置licenseServer URL
  - offline: 不需要licenseServer
- 服务之间的依赖关系：
  - API → PostgreSQL, Redis, VectorDB
  - Worker → PostgreSQL, Redis
  - Enterprise → PostgreSQL, Redis
  - Sandbox → SSRF Proxy

---

## 配置流程建议

### 推荐顺序
1. **全局配置** → 设置基础密钥和域名
2. **基础设施配置** → 配置数据库、缓存、存储
3. **网络配置** → 配置Ingress和TLS
4. **邮件配置** → 配置邮件服务（可选）
5. **插件配置** → 配置插件镜像仓库和认证
6. **服务配置** → 调整服务启用状态和Enterprise配置

### 关键联动点检查清单

- [x] `global.appSecretKey` 和 `enterprise.appSecretKey` **自动生成**
- [x] `global.innerApiKey` **自动生成**
- [x] `enterprise.passwordEncryptionKey` **自动生成**
- [ ] PostgreSQL: `externalPostgres.enabled` 和 `postgresql.enabled` 是否互斥
- [ ] Redis: `externalRedis.enabled` 和 `redis.enabled` 是否互斥
- [ ] Redis: Sentinel 和 Cluster 是否互斥
- [ ] VectorDB: `vectorDB.useExternal` 与 `qdrant.enabled`/`weaviate.enabled` 是否一致
- [ ] RAG联动: `rag.etlType = "dify"` → `unstructured.enabled = false`
- [ ] RAG联动: `rag.etlType = "Unstructured"` → `unstructured.enabled = true`
- [ ] 存储: `persistence.type` 与对应的存储配置是否匹配
- [ ] S3存储: `useAwsS3` 是否正确设置（AWS S3 = true，其他 = false）
- [ ] AWS S3授权: 
  - IRSA模式：`useAwsManagedIam = true`，已配置ServiceAccount，无accessKey/secretKey
  - Access Key模式：`useAwsManagedIam = false`，已配置accessKey和secretKey
- [ ] MinIO: 如果 `persistence.type != "s3"` 或选择MinIO作为S3提供商，是否配置了MinIO
- [ ] **TLS联动（重要）**: `global.useTLS` 与 `ingress.tls` 是否一致（避免CORS问题）
- [ ] Ingress: 如果启用，域名配置是否完整
- [ ] Enterprise: 如果启用，License配置是否完整（online模式需要licenseServer）

---

## 使用脚本生成配置

运行交互式脚本：
```bash
python3 generate-values-prd.py
```

脚本会按模块顺序引导您完成配置，并自动处理模块间的联动关系。

