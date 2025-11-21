# 脚本更新日志

## 最新更新 (2024)

### AWS S3 存储配置增强

1. **AWS S3 授权方式选择**
   - ✅ 支持两种授权方式：
     - **IRSA 模式（推荐）**：使用 IAM Roles for Service Accounts
       - 自动设置 `useAwsManagedIam = true`
       - 可选配置 ServiceAccount（`api.serviceAccountName` 和 `worker.serviceAccountName`）
       - 自动删除 `accessKey` 和 `secretKey`
       - 提供详细的 AWS IRSA 配置文档链接
     - **Access Key 模式（备选）**：使用 Access Key 和 Secret Key
       - 自动设置 `useAwsManagedIam = false`
       - 配置 `accessKey` 和 `secretKey`
       - 提示确保 IAM 用户只具备 S3 访问权限

2. **AWS S3 Endpoint URL 配置**
   - ✅ Endpoint URL 使用英文提示（"S3 Endpoint URL"）
   - ✅ 设置为必填项（`required=True`）
   - ✅ 格式示例：`https://s3.us-west-2.amazonaws.com`

3. **配置流程优化**
   - ✅ 先配置 Endpoint URL
   - ✅ 然后选择授权方式（IRSA/Access Key）
   - ✅ 根据授权方式自动配置相关参数
   - ✅ 最后配置 Region 和 Bucket Name

### 插件配置模块新增（模块 5）

1. **独立的插件配置模块**
   - ✅ 从服务配置模块中分离出插件配置
   - ✅ 新增模块 5: 插件配置（Plugin Configuration）
   - ✅ 原服务配置模块调整为模块 6

2. **镜像仓库配置**
   - ✅ 支持 Docker 和 ECR 两种镜像仓库类型
   - ✅ ECR 自动生成镜像仓库前缀格式：`{account_id}.dkr.ecr.{region}.amazonaws.com/{prefix}`
   - ✅ 支持可选的 prefix 部分（如 `dify-ee`）

3. **ECR 鉴权方式**
   - ✅ IRSA 模式（推荐）：使用 IAM Roles for Service Accounts
     - 配置 `customServiceAccount` 和 `runnerServiceAccount`
     - 提供详细的 AWS 文档链接
   - ✅ K8s Secret 模式：使用 Kubernetes Secret 存储凭证
     - 配置 `imageRepoSecret`
     - 提供详细的配置文档链接

4. **配置顺序优化**
   - ✅ 先选择镜像仓库类型
   - ✅ ECR 模式：先配置区域和账户ID，再配置镜像仓库前缀
   - ✅ 然后选择鉴权方式（ECR）或配置 Secret（Docker/ECR K8s Secret）
   - ✅ 最后选择协议类型（HTTPS/HTTP）

5. **协议类型选择**
   - ✅ 使用选择方式替代双重否定询问
   - ✅ 选项1（默认）：HTTPS (推荐)
   - ✅ 选项2：HTTP (不推荐，仅备选)
   - ✅ 明确标注 HTTP 为不推荐方案

### 格式保留改进

1. **YAML 格式保留**
   - ✅ 修复双引号丢失问题
   - ✅ 修复结构变化问题
   - ✅ 要求必须安装 ruamel.yaml，未安装时直接报错
   - ✅ 只在值真正改变时才更新，确保未更新字段完全保留

2. **注释和格式保留**
   - ✅ 保留所有注释
   - ✅ 保留原始格式和缩进
   - ✅ 保留引号格式（双引号/单引号）

## 历史更新 (2024)

### 全局配置模块改进

1. **密钥自动生成**
   - ✅ 所有密钥（`appSecretKey`, `innerApiKey`）都按照注释要求自动生成
   - ✅ 使用 `openssl rand -base64 42` 生成42字节密钥
   - ✅ 移除了手动输入选项，统一使用自动生成

2. **TLS 配置联动**
   - ✅ TLS 配置从全局配置模块移到网络配置模块
   - ✅ TLS 配置与 Ingress 配置联动，避免 CORS 跨域问题
   - ✅ 自动检查 TLS 一致性，提供警告和建议

3. **RAG 联动关系**
   - ✅ 当 RAG ETL 类型选择 `dify` 时，自动关闭 `unstructured` 模块
   - ✅ 当选择 `Unstructured` 时，自动启用 `unstructured` 模块

### 基础设施配置模块改进

1. **PostgreSQL 配置增强**
   - ✅ 每个数据库（dify, plugin_daemon, enterprise, audit）的配置信息完全交互式获取
   - ✅ 包括：数据库名、用户名、密码、SSL模式、额外参数、字符集、URI方案
   - ✅ 清晰的数据库描述和配置提示

2. **Redis 配置增强**
   - ✅ 完整的交互式配置，包括所有连接参数
   - ✅ Sentinel 和 Cluster 配置互斥选择
   - ✅ Sentinel 配置包括：节点列表、服务名、用户名、密码、socket超时
   - ✅ Cluster 配置包括：节点列表、密码

3. **存储配置改进**
   - ✅ `persistence.type = s3` 时也可以配置 MinIO
   - ✅ S3 服务提供商选择（AWS S3 / MinIO / Cloudflare R2 / 其他兼容S3服务）
   - ✅ `useAwsS3` 自动设置：
     - AWS S3 → `useAwsS3 = true`
     - MinIO 或其他兼容S3服务 → `useAwsS3 = false`
   - ✅ 支持 S3 地址类型配置（path-style/virtual-hosted-style）

### 网络配置模块新增

1. **TLS 配置**
   - ✅ TLS 配置移至网络配置模块
   - ✅ 与 Ingress 配置联动
   - ✅ 自动检查 TLS 一致性
   - ✅ 支持 cert-manager 自动证书管理
   - ✅ 提供 TLS 主机列表配置

2. **Ingress 配置增强**
   - ✅ 完整的 TLS 配置支持
   - ✅ cert-manager 集成
   - ✅ useIpAsHost 配置

### Enterprise 配置改进

1. **密钥自动生成**
   - ✅ `appSecretKey` 自动生成（42字节）
   - ✅ `adminAPIsSecretKeySalt` 自动生成（42字节）
   - ✅ `passwordEncryptionKey` 自动生成（32字节，AES-256密钥）

## 配置联动关系总结

### 1. TLS 联动
```
全局 TLS (global.useTLS) ↔ Ingress TLS
- 必须保持一致，否则会出现 CORS 跨域问题
- 脚本会自动检查并提示
```

### 2. RAG 联动
```
RAG ETL 类型 = "dify" → unstructured.enabled = false
RAG ETL 类型 = "Unstructured" → unstructured.enabled = true
```

### 3. PostgreSQL 联动
```
externalPostgres.enabled = true ↔ postgresql.enabled = false (互斥)
```

### 4. Redis 联动
```
externalRedis.enabled = true ↔ redis.enabled = false (互斥)
Sentinel 和 Cluster 互斥
```

### 5. VectorDB 联动
```
vectorDB.useExternal = true ↔ qdrant/weaviate.enabled = false (互斥)
```

### 6. 存储联动
```
persistence.type = "s3" + 选择 MinIO → 可以同时配置 MinIO 服务
persistence.type != "s3" → 可以配置 MinIO 作为对象存储
useAwsS3 = true (仅当选择 AWS S3)
useAwsS3 = false (MinIO 或其他兼容S3服务)
```

## 使用建议

1. **密钥管理**
   - 所有密钥自动生成，请妥善保管
   - 建议将密钥存储在密钥管理系统中

2. **TLS 配置**
   - 生产环境建议启用 TLS
   - 确保全局 TLS 和 Ingress TLS 配置一致

3. **存储配置**
   - 如果使用 S3 兼容存储，注意 `useAwsS3` 设置
   - MinIO 可以作为独立服务或 S3 兼容存储使用

4. **数据库配置**
   - 外部数据库需要完整配置所有4个数据库的凭证
   - 注意 SSL 模式设置，生产环境建议使用 `require` 或更高

