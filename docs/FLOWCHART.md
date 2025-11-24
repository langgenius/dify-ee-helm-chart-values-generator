# Dify EE（企业版）Helm Chart Values 生成器流程图

## 主流程图

```mermaid
flowchart TD
    Start([开始]) --> LoadTemplate[加载 values.yaml 模板]
    LoadTemplate --> ShowHeader[显示欢迎信息]
    ShowHeader --> Module1[模块1: 全局配置]
    
    Module1 --> Module2[模块2: 基础设施配置]
    Module2 --> Module3[模块3: 网络配置]
    Module3 --> Module4[模块4: 邮件配置]
    Module4 --> Module5[模块5: 插件配置]
    Module5 --> Module6[模块6: 服务配置]
    
    Module5 --> CheckFile{文件是否存在?}
    CheckFile -->|是| AskOverwrite{是否覆盖?}
    CheckFile -->|否| SaveFile[保存 values-prd.yaml]
    AskOverwrite -->|是| SaveFile
    AskOverwrite -->|否| NewFileName[输入新文件名]
    NewFileName --> SaveFile
    
    SaveFile --> Success([配置完成])
    
    Start -.->|Ctrl+C| Interrupt[用户中断]
    Interrupt --> AskSave{保存进度?}
    AskSave -->|是| SavePartial[保存部分配置]
    AskSave -->|否| Exit([退出])
    SavePartial --> Exit
    
    style Start fill:#90EE90
    style Success fill:#90EE90
    style Exit fill:#FFB6C1
    style Interrupt fill:#FFB6C1
```

## 模块1: 全局配置流程图

```mermaid
flowchart TD
    Start([模块1开始]) --> GenAppSecret[自动生成 appSecretKey<br/>openssl rand -base64 42]
    GenAppSecret --> GenInnerSecret[自动生成 innerApiKey<br/>openssl rand -base64 42]
    
    GenInnerSecret --> Domains[配置域名<br/>consoleApiDomain<br/>consoleWebDomain<br/>serviceApiDomain<br/>appApiDomain<br/>appWebDomain<br/>filesDomain<br/>enterpriseDomain]
    
    Domains --> DBMigration[数据库迁移开关]
    DBMigration --> RAGType[选择RAG ETL类型<br/>dify/Unstructured]
    
    RAGType --> RAGCheck{RAG类型?}
    RAGCheck -->|dify| DisableUnstructured[关闭unstructured模块<br/>unstructured.enabled = false]
    RAGCheck -->|Unstructured| EnableUnstructured[启用unstructured模块<br/>unstructured.enabled = true]
    
    DisableUnstructured --> RAGConfig
    EnableUnstructured --> RAGConfig
    
    RAGConfig[配置RAG参数<br/>keywordDataSourceType<br/>topKMaxValue<br/>indexingMaxSegmentationTokensLength]
    
    RAGConfig --> End([模块1完成])
    
    style Start fill:#E6F3FF
    style End fill:#E6F3FF
    style RAGCheck fill:#FFF4E6
    style DisableUnstructured fill:#FFE6E6
    style EnableUnstructured fill:#E6FFE6
```

## 模块2: 基础设施配置流程图

```mermaid
flowchart TD
    Start([模块2开始]) --> PostgresChoice{使用外部<br/>PostgreSQL?}
    
    PostgresChoice -->|是| ExtPostgres[配置外部PostgreSQL<br/>address, port<br/>交互式配置4个数据库]
    PostgresChoice -->|否| IntPostgres[使用内置PostgreSQL<br/>自动生成root密码]
    
    ExtPostgres --> PostgresDBs[配置每个数据库<br/>dify: 数据库名/用户名/密码/SSL<br/>plugin_daemon: 完整配置<br/>enterprise: 完整配置<br/>audit: 完整配置]
    PostgresDBs --> RedisChoice
    IntPostgres --> RedisChoice
    
    RedisChoice{使用外部<br/>Redis?} -->|是| ExtRedis[配置外部Redis<br/>host, port, password<br/>username, db, useSSL]
    RedisChoice -->|否| IntRedis[使用内置Redis<br/>自动生成密码]
    
    ExtRedis --> RedisMode{Redis模式?}
    RedisMode -->|Sentinel| RedisSentinel[配置Sentinel<br/>nodes, serviceName<br/>username, password<br/>socketTimeout]
    RedisMode -->|Cluster| RedisCluster[配置Cluster<br/>nodes, password]
    RedisMode -->|标准| VectorDBChoice
    
    RedisSentinel --> VectorDBChoice
    RedisCluster --> VectorDBChoice
    IntRedis --> VectorDBChoice
    
    VectorDBChoice{使用外部<br/>向量数据库?} -->|是| ExtVectorDB[选择类型<br/>qdrant/weaviate/milvus等<br/>配置连接信息]
    VectorDBChoice -->|否| IntVectorDB[选择内置类型<br/>qdrant/weaviate<br/>配置API Key]
    
    ExtVectorDB --> StorageType
    IntVectorDB --> StorageType
    
    StorageType[选择存储类型<br/>local/s3/azure-blob等] --> StorageConfig{存储类型?}
    
    StorageConfig -->|local| LocalStorage[配置本地存储<br/>mountPath<br/>storageClass<br/>size]
    StorageConfig -->|s3| S3Provider[选择S3提供商<br/>AWS S3/MinIO/Cloudflare R2/其他]
    StorageConfig -->|其他| CloudStorage[配置云存储<br/>对应凭证]
    
    S3Provider --> S3Config{提供商?}
    S3Config -->|AWS S3| S3Endpoint[配置S3 Endpoint URL<br/>必填，英文]
    S3Config -->|MinIO/其他| S3Compatible[配置S3兼容<br/>useAwsS3 = false<br/>endpoint/credentials/bucket<br/>minio.enabled = true]
    
    S3Endpoint --> S3Auth{授权方式?}
    S3Auth -->|IRSA模式<br/>推荐| S3IRSA[配置IRSA模式<br/>useAwsManagedIam = true<br/>配置ServiceAccount<br/>删除accessKey/secretKey<br/>参考AWS文档]
    S3Auth -->|Access Key模式| S3AK[配置Access Key模式<br/>useAwsManagedIam = false<br/>配置Access Key/Secret Key]
    
    S3IRSA --> S3Region[配置Region和Bucket<br/>minio.enabled = false]
    S3AK --> S3Region
    S3Region --> End
    S3Compatible --> ConfigMinIO[配置MinIO<br/>自动生成rootPassword<br/>rootUser]
    
    LocalStorage --> MinIOCheck
    CloudStorage --> MinIOCheck
    
    MinIOCheck[存储类型不是s3<br/>minio.enabled = true] --> ConfigMinIO
    
    ConfigMinIO --> End([模块2完成])
    
    style Start fill:#E6F3FF
    style End fill:#E6F3FF
    style PostgresChoice fill:#FFF4E6
    style RedisChoice fill:#FFF4E6
    style RedisMode fill:#FFF4E6
    style StorageConfig fill:#FFF4E6
    style S3Provider fill:#FFF4E6
    style S3Config fill:#FFF4E6
    style S3MinIO fill:#FFF4E6
    style MinIO fill:#FFF4E6
    style RedisChoice fill:#FFF4E6
    style VectorDBChoice fill:#FFF4E6
    style StorageConfig fill:#FFF4E6
    style MinIO fill:#FFF4E6
```

## 模块3: 网络配置流程图

```mermaid
flowchart TD
    Start([模块3开始]) --> TLSConfig[配置全局TLS<br/>global.useTLS<br/>影响内部服务通信和CORS]
    
    TLSConfig --> EnableIngress{启用<br/>Ingress?}
    
    EnableIngress -->|是| ConfigIngress[配置Ingress<br/>className]
    EnableIngress -->|否| End
    
    ConfigIngress --> IngressTLS{配置Ingress<br/>TLS?}
    
    IngressTLS -->|是| TLSDetails[配置TLS详情<br/>hosts列表<br/>secretName]
    IngressTLS -->|否| TLSCheck
    
    TLSDetails --> CertManager{使用cert-manager?}
    CertManager -->|是| CertConfig[配置ClusterIssuer<br/>添加annotations]
    CertManager -->|否| TLSCheck
    
    CertConfig --> TLSCheck
    TLSCheck{检查TLS<br/>一致性}
    
    TLSCheck -->|不一致| TLSWarning[警告: CORS问题<br/>提示修复]
    TLSWarning --> TLSAutoFix{自动修复?}
    TLSAutoFix -->|是| TLSDetails
    TLSAutoFix -->|否| End
    
    TLSCheck -->|一致| UseIpHost[配置useIpAsHost<br/>仅非企业版]
    UseIpHost --> End([模块3完成])
    
    style Start fill:#E6F3FF
    style End fill:#E6F3FF
    style TLSConfig fill:#FFE6E6
    style EnableIngress fill:#FFF4E6
    style IngressTLS fill:#FFF4E6
    style TLSCheck fill:#FFE6E6
    style TLSWarning fill:#FFB6C1
```

## 模块4: 邮件配置流程图

```mermaid
flowchart TD
    Start([模块4开始]) --> MailType[选择邮件类型<br/>空/resend/smtp]
    
    MailType --> TypeCheck{邮件类型?}
    
    TypeCheck -->|空| End
    TypeCheck -->|resend| ResendConfig[配置Resend<br/>apiKey<br/>apiUrl]
    TypeCheck -->|smtp| SMTPConfig[配置SMTP<br/>server, port<br/>username, password<br/>useTLS]
    
    ResendConfig --> DefaultSender
    SMTPConfig --> DefaultSender
    
    DefaultSender[配置默认发件人] --> End([模块4完成])
    
    style Start fill:#E6F3FF
    style End fill:#E6F3FF
```

## 模块5: 插件配置流程图

```mermaid
flowchart TD
    Start([模块5开始]) --> RepoType[选择镜像仓库类型<br/>docker/ecr]
    
    RepoType --> TypeCheck{仓库类型?}
    
    TypeCheck -->|docker| DockerPrefix[配置镜像仓库前缀<br/>docker.io/your-image-repo-prefix]
    TypeCheck -->|ecr| ECRRegion[配置ECR区域<br/>us-east-1等]
    
    ECRRegion --> ECRAccount[配置ECR账户ID<br/>AWS Account ID]
    
    ECRAccount --> ECRPrefix["配置镜像仓库前缀<br/>&#123;account_id&#125;.dkr.ecr.&#123;region&#125;.amazonaws.com/&#123;prefix&#125;"]
    
    ECRPrefix --> AuthMethod{ECR鉴权方式?}
    DockerPrefix --> DockerSecret[配置imageRepoSecret<br/>参考容器镜像仓库文档]
    
    AuthMethod -->|IRSA模式| IRSAServiceAccount[配置ServiceAccount<br/>customServiceAccount<br/>runnerServiceAccount]
    AuthMethod -->|K8s Secret| ECRSecret[配置imageRepoSecret<br/>参考AWS文档]
    
    IRSAServiceAccount --> Protocol
    ECRSecret --> Protocol
    DockerSecret --> Protocol
    
    Protocol[选择协议类型<br/>HTTPS推荐/HTTP不推荐] --> End([模块5完成])
    
    style Start fill:#E6F3FF
    style End fill:#E6F3FF
    style TypeCheck fill:#FFF4E6
    style AuthMethod fill:#FFF4E6
    style Protocol fill:#FFE6E6
```

## 模块6: 服务配置流程图

```mermaid
flowchart TD
    Start([模块6开始]) --> CheckEnterprise{Enterprise<br/>已启用?}
    
    CheckEnterprise -->|是| GenEnterpriseKeys[自动生成Enterprise密钥<br/>appSecretKey: 42字节<br/>adminAPIsSecretKeySalt: 42字节<br/>passwordEncryptionKey: 32字节]
    
    GenEnterpriseKeys --> LicenseMode[配置License模式<br/>online/offline]
    
    LicenseMode --> LicenseCheck{License模式?}
    LicenseCheck -->|online| LicenseServer[配置License服务器<br/>licenseServer URL]
    LicenseCheck -->|offline| ServiceToggle
    
    LicenseServer --> ServiceToggle
    CheckEnterprise -->|否| ServiceToggle
    
    ServiceToggle{配置服务<br/>启用状态?}
    
    ServiceToggle -->|是| ToggleServices[逐个配置服务<br/>api, worker, web等<br/>enterprise, enterpriseAudit等]
    ServiceToggle -->|否| End
    
    ToggleServices --> End([模块6完成])
    
    style Start fill:#E6F3FF
    style End fill:#E6F3FF
    style GenEnterpriseKeys fill:#E6FFE6
    style LicenseCheck fill:#FFF4E6
```

## 完整交互流程图

```mermaid
flowchart TD
    Start([脚本启动]) --> Init[初始化ValuesGenerator]
    Init --> LoadYAML[加载values.yaml模板]
    LoadYAML --> MainFlow[主流程开始]
    
    MainFlow --> M1[模块1: 全局配置]
    M1 --> M1Q2[自动生成密钥]
    M1Q2 --> M1Q3[配置域名]
    M1Q3 --> M1Q4[配置RAG]
    
    M1Q4 --> M2[模块2: 基础设施]
    M2 --> M2Q1{PostgreSQL选择}
    M2Q1 -->|外部| M2Q1A[配置外部连接]
    M2Q1 -->|内置| M2Q1B[配置内置密码]
    
    M2Q1A --> M2Q2
    M2Q1B --> M2Q2{Redis选择}
    M2Q2 -->|外部| M2Q2A[配置外部连接]
    M2Q2 -->|内置| M2Q2B[配置内置密码]
    
    M2Q2A --> M2Q3
    M2Q2B --> M2Q3{VectorDB选择}
    M2Q3 -->|外部| M2Q3A[配置外部连接]
    M2Q3 -->|内置| M2Q3B[配置内置]
    
    M2Q3A --> M2Q4
    M2Q3B --> M2Q4{存储类型}
    M2Q4 --> M2Q4A[配置存储]
    M2Q4A --> M2Q5{配置MinIO?}
    M2Q5 --> M3
    
    M3[模块3: 网络] --> M3Q1{启用Ingress?}
    M3Q1 --> M4
    
    M4[模块4: 邮件] --> M4Q1{邮件类型}
    M4Q1 --> M5
    
    M5[模块5: 插件] --> M5Q1{镜像仓库类型}
    M5Q1 -->|docker| M5Q1A[配置Docker]
    M5Q1 -->|ecr| M5Q1B[配置ECR]
    M5Q1A --> M5Q2{鉴权方式}
    M5Q1B --> M5Q2{鉴权方式}
    M5Q2 --> M6
    
    M6[模块6: 服务] --> M6Q1{Enterprise配置}
    M6Q1 --> M6Q2{服务状态}
    M6Q2 --> Save
    
    Save[保存文件] --> Validate[验证配置]
    Validate --> Success([完成])
    
    Start -.->|异常| Error[错误处理]
    Error --> Exit([退出])
    
    style Start fill:#90EE90
    style Success fill:#90EE90
    style Error fill:#FFB6C1
    style Exit fill:#FFB6C1
```

## 决策点说明

### 关键决策点

1. **PostgreSQL选择** (互斥)
   - 外部: `externalPostgres.enabled = true`
   - 内置: `postgresql.enabled = true`

2. **Redis选择** (互斥)
   - 外部: `externalRedis.enabled = true`
   - 内置: `redis.enabled = true`

3. **VectorDB选择** (互斥)
   - 外部: `vectorDB.useExternal = true`
   - 内置: `qdrant.enabled` 或 `weaviate.enabled = true`

4. **存储类型** (单选)
   - local, s3, azure-blob, aliyun-oss, google-storage, tencent-cos, volcengine-tos, huawei-obs

5. **邮件类型** (单选)
   - 空(不配置), resend, smtp

### 联动关系

- **存储类型 → MinIO**: 如果 `persistence.type != "s3"`，需要配置MinIO
- **外部服务 → 连接信息**: 选择外部服务后，必须配置对应的连接信息
- **Enterprise → License**: Enterprise服务需要License配置

## 使用示例流程

```mermaid
sequenceDiagram
    participant User as 用户
    participant Script as 生成脚本
    participant File as values-prd.yaml
    
    User->>Script: 运行脚本
    Script->>User: 显示欢迎信息
    Script->>Script: 自动生成密钥
    Script->>User: 显示已生成密钥
    Script->>User: 配置域名
    User->>Script: 输入域名
    Script->>User: 模块2: PostgreSQL选择
    User->>Script: 外部
    Script->>User: 输入连接信息
    User->>Script: 输入信息
    Script->>User: 模块3-5: 继续配置
    User->>Script: 完成所有配置
    Script->>File: 保存配置
    Script->>User: 显示完成信息
```

