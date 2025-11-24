"""Infrastructure configuration module"""

from utils import (
    print_header, print_section, print_info, print_success, print_warning, print_error,
    prompt, prompt_choice, prompt_yes_no, generate_secret
)
from version_manager import VersionManager
from i18n import get_translator

_t = get_translator()


def configure_infrastructure(generator):
    """Configure infrastructure"""
    print_header(_t('module_infrastructure'))

    # PostgreSQL
    print_section(_t('postgresql_config'))
    print_info("=" * 60)
    print_info(_t('network_address_note'))
    print_info("=" * 60)
    print_info(_t('kind_cluster_external'))
    print_info(_t('use_host_docker_internal'))
    print_info(_t('or_use_host_ip'))
    print_info(_t('or_use_localhost'))
    print_info("")
    print_info(_t('service_in_cluster'))
    print_info(_t('use_service_name_example'))
    print_info(_t('or_use_short_name'))
    print_info("=" * 60)
    print_info("")
    # Default to external PostgreSQL (recommended for Enterprise)
    use_external_postgres = True
    print_info(_t('default_external_postgres'))

    if use_external_postgres:
        generator.values['externalPostgres']['enabled'] = True
        generator.values['postgresql']['enabled'] = False

        print_info(_t('config_external_postgres'))
        print_warning(_t('kind_cluster_tip'))
        generator.values['externalPostgres']['address'] = prompt(
            _t('postgresql_address'),
            default="host.docker.internal",
            required=True
        )

        port = prompt(_t('postgresql_port'), default="5432", required=False)
        try:
            generator.values['externalPostgres']['port'] = int(port)
        except ValueError:
            generator.values['externalPostgres']['port'] = 5432

        # Configure credentials for each database - interactively get configuration for each database
        databases_config = [
            {'key': 'dify', 'name': 'dify', 'desc': _t('main_database')},
            {'key': 'plugin_daemon', 'name': 'plugin_daemon', 'desc': _t('plugin_daemon_database')},
            {'key': 'enterprise', 'name': 'enterprise', 'desc': _t('enterprise_database')},
            {'key': 'audit', 'name': 'audit', 'desc': _t('audit_database')}
        ]

        for db_config in databases_config:
            print(f"\n{'='*60}")
            print(f"{_t('config_database')}: {db_config['name']} ({db_config['desc']})")
            print(f"{'='*60}")

            db_key = db_config['key']

            generator.values['externalPostgres']['credentials'][db_key]['database'] = prompt(
                f"{db_config['name']} {_t('database_name')}",
                default=db_config['name'],
                required=False
            )

            generator.values['externalPostgres']['credentials'][db_key]['username'] = prompt(
                f"{db_config['name']} {_t('username')}",
                default="postgres",
                required=False
            )

            generator.values['externalPostgres']['credentials'][db_key]['password'] = prompt(
                f"{db_config['name']} {_t('password')}",
                required=True
            )

            generator.values['externalPostgres']['credentials'][db_key]['sslmode'] = prompt_choice(
                f"{db_config['name']} {_t('ssl_mode')}",
                ["disable", "require", "verify-ca", "verify-full"],
                default="require"
            )

            # Set default values (no longer asking)
            generator.values['externalPostgres']['credentials'][db_key]['extras'] = ''
            generator.values['externalPostgres']['credentials'][db_key]['charset'] = ''
            generator.values['externalPostgres']['credentials'][db_key]['uriScheme'] = 'postgresql'
    else:
        generator.values['externalPostgres']['enabled'] = False
        generator.values['postgresql']['enabled'] = True

        print_info(_t('use_builtin_postgresql'))
        if prompt_yes_no(_t('config_postgresql_password'), default=True):
            if prompt_yes_no(_t('auto_generate_password'), default=True):
                generator.values['postgresql']['global']['postgresql']['auth']['postgresPassword'] = generate_secret(32)
                print_success(_t('postgresql_password_generated'))
            else:
                generator.values['postgresql']['global']['postgresql']['auth']['postgresPassword'] = prompt(
                    _t('postgresql_root_password'),
                    required=True
                )

    # Redis
    print_section(_t('redis_config'))
    use_external_redis = prompt_yes_no(_t('use_external_redis'), default=True)

    if use_external_redis:
        generator.values['externalRedis']['enabled'] = True
        generator.values['redis']['enabled'] = False

        print_info(_t('config_external_redis'))
        print_warning(_t('kind_cluster_tip'))
        generator.values['externalRedis']['host'] = prompt(
            _t('redis_host'),
            default="host.docker.internal",
            required=True
        )

        port = prompt(_t('redis_port'), default="6379", required=False)
        try:
            generator.values['externalRedis']['port'] = int(port)
        except ValueError:
            generator.values['externalRedis']['port'] = 6379

        generator.values['externalRedis']['useSSL'] = prompt_yes_no(_t('use_ssl'), default=False)

        generator.values['externalRedis']['username'] = prompt(
            _t('redis_username'),
            default="",
            required=False
        )

        generator.values['externalRedis']['password'] = prompt(
            _t('redis_password'),
            required=True
        )

        db_num = prompt(_t('redis_db_number'), default="0", required=False)
        try:
            generator.values['externalRedis']['db'] = int(db_num)
        except ValueError:
            generator.values['externalRedis']['db'] = 0

        # Sentinel/Cluster configuration - mutually exclusive
        use_sentinel = prompt_yes_no(_t('use_sentinel'), default=False)
        use_cluster = False

        if use_sentinel:
            generator.values['externalRedis']['sentinel']['enabled'] = True
            generator.values['externalRedis']['cluster']['enabled'] = False

            generator.values['externalRedis']['sentinel']['nodes'] = prompt(
                _t('sentinel_nodes'),
                required=True
            )
            generator.values['externalRedis']['sentinel']['serviceName'] = prompt(
                _t('sentinel_service_name'),
                required=True
            )
            generator.values['externalRedis']['sentinel']['username'] = prompt(
                _t('sentinel_username'),
                default="",
                required=False
            )
            generator.values['externalRedis']['sentinel']['password'] = prompt(
                _t('sentinel_password'),
                required=True
            )
            socket_timeout = prompt(
                _t('socket_timeout'),
                default="0.1",
                required=False
            )
            try:
                generator.values['externalRedis']['sentinel']['socketTimeout'] = float(socket_timeout)
            except ValueError:
                generator.values['externalRedis']['sentinel']['socketTimeout'] = 0.1
        else:
            generator.values['externalRedis']['sentinel']['enabled'] = False
            use_cluster = prompt_yes_no(_t('use_cluster'), default=False)

        if use_cluster:
            generator.values['externalRedis']['cluster']['enabled'] = True
            generator.values['externalRedis']['cluster']['nodes'] = prompt(
                _t('cluster_nodes'),
                required=True
            )
            generator.values['externalRedis']['cluster']['password'] = prompt(
                _t('cluster_password'),
                required=True
            )
        else:
            generator.values['externalRedis']['cluster']['enabled'] = False
    else:
        generator.values['externalRedis']['enabled'] = False
        generator.values['redis']['enabled'] = True

        print_info(_t('use_builtin_redis'))
        if prompt_yes_no(_t('config_redis_password'), default=True):
            if prompt_yes_no(_t('auto_generate_password'), default=True):
                generator.values['redis']['global']['redis']['password'] = generate_secret(32)
                print_success(_t('redis_password_generated'))
            else:
                generator.values['redis']['global']['redis']['password'] = prompt(
                    _t('redis_password'),
                    required=True
                )

    # VectorDB
    print_section(_t('vectordb_config'))
    use_external_vectordb = prompt_yes_no(_t('use_external_vectordb'), default=True)

    generator.values['vectorDB']['useExternal'] = use_external_vectordb

    if use_external_vectordb:
        vectordb_type = prompt_choice(_t('select_vectordb_type'),
            ["qdrant", "weaviate", "milvus", "relyt", "pgvecto-rs",
             "tencent", "opensearch", "elasticsearch", "analyticdb", "lindorm"],
            default="qdrant"
        )
        generator.values['vectorDB']['externalType'] = vectordb_type

        print_info(f"{_t('config_external_vectordb')} {vectordb_type} {_t('connection_info')}")
        print_warning(_t('kind_cluster_tip'))

        if vectordb_type == "qdrant":
            generator.values['vectorDB']['externalQdrant']['endpoint'] = prompt(
                _t('qdrant_endpoint'),
                default="http://host.docker.internal:6333",
                required=True
            )
            generator.values['vectorDB']['externalQdrant']['apiKey'] = prompt(
                _t('qdrant_api_key'),
                required=False
            )
        elif vectordb_type == "weaviate":
            generator.values['vectorDB']['externalWeaviate']['endpoint'] = prompt(
                _t('weaviate_endpoint'),
                default="http://weaviate:8080",
                required=True
            )
            generator.values['vectorDB']['externalWeaviate']['apiKey'] = prompt(
                _t('weaviate_api_key'),
                required=False
            )
        # Other types can be extended similarly
    else:
        # Use built-in vector database
        vectordb_choice = prompt_choice(_t('select_builtin_vectordb'),
            ["qdrant", "weaviate"],
            default="qdrant"
        )

        if vectordb_choice == "qdrant":
            generator.values['qdrant']['enabled'] = True
            generator.values['weaviate']['enabled'] = False

            api_key = prompt(_t('qdrant_api_key'), default="dify123456", required=False)
            generator.values['qdrant']['apiKey'] = api_key

            replica_count = prompt(_t('qdrant_replica_count'), default="3", required=False)
            try:
                generator.values['qdrant']['replicaCount'] = int(replica_count)
            except ValueError:
                generator.values['qdrant']['replicaCount'] = 3
        else:
            generator.values['qdrant']['enabled'] = False
            generator.values['weaviate']['enabled'] = True

    # Storage configuration
    print_section(_t('storage_config'))
    storage_options = ["local", _t('s3_storage_option'), "azure-blob", "aliyun-oss", "google-storage",
                       "tencent-cos", "volcengine-tos", "huawei-obs"]
    storage_type = prompt_choice(_t('select_storage_type'),
        storage_options,
        default="local"
    )

    # Process storage type selection, convert display name to actual value
    if storage_type == _t('s3_storage_option'):
        storage_type = "s3"
    generator.values['persistence']['type'] = storage_type

    if storage_type == "local":
        print_info(_t('config_local_storage'))
        generator.values['persistence']['local']['mountPath'] = prompt(
            _t('mount_path'),
            default="/app/api/storage",
            required=False
        )

        storage_class = prompt(
            _t('storage_class_name'),
            default="",
            required=False
        )
        if storage_class:
            generator.values['persistence']['local']['persistentVolumeClaim']['storageClass'] = storage_class

        size = prompt(_t('storage_size'), default="5Gi", required=False)
        generator.values['persistence']['local']['persistentVolumeClaim']['size'] = size

    elif storage_type == "s3":
        print_info(_t('config_s3_storage'))

        # Determine if AWS S3 or other S3-compatible service (like MinIO)
        s3_provider_options = ["AWS S3", "MinIO", "Cloudflare R2", _t('other_s3_compatible')]
        s3_provider = prompt_choice(_t('s3_provider'),
            s3_provider_options,
            default="AWS S3"
        )

        if s3_provider == "AWS S3":
            generator.values['persistence']['s3']['useAwsS3'] = True
            print_info(_t('config_aws_s3'))
            # AWS S3 doesn't need built-in MinIO
            generator.values['minio']['enabled'] = False
            print_info(_t('auto_disable_minio'))

            # AWS S3 Endpoint URL (Required, English)
            generator.values['persistence']['s3']['endpoint'] = prompt(
                _t('s3_endpoint_url'),
                default="",
                required=True
            )

            # AWS S3 Authentication Method Selection
            print_info("")
            print_info("=" * 60)
            print_info(_t('s3_auth_method'))
            print_info("=" * 60)
            print_info(_t('s3_auth_methods'))
            print_info(_t('irsa_mode_recommended'))
            print_info(_t('access_key_mode'))
            print_info("=" * 60)
            print_info("")

            s3_auth_method = prompt_choice(
                _t('s3_auth_method'),
                [_t('irsa_mode'), _t('access_key_mode_option')],
                default=_t('irsa_mode')
            )

            if s3_auth_method == _t('irsa_mode'):
                print_info("")
                print_info("=" * 60)
                print_info(_t('irsa_config_note'))
                print_info("=" * 60)
                print_info(_t('irsa_config_instructions'))
                print_info(_t('irsa_config_docs'))
                print_info(_t('irsa_config_docs_url'))
                print_info("")
                print_info(_t('use_irsa_mode'))
                print_info(_t('api_serviceaccount_note'))
                print_info(_t('worker_serviceaccount_note'))
                print_info("=" * 60)
                print_info("")

                # Set useAwsManagedIam = true
                generator.values['persistence']['s3']['useAwsManagedIam'] = True
                print_success(_t('irsa_mode_selected'))
                print_info("")

                # Configure ServiceAccount name (optional, if ServiceAccount already created)
                print_info(_t('config_serviceaccount'))
                api_sa = prompt(
                    _t('api_serviceaccount'),
                    default="",
                    required=False
                )
                if api_sa:
                    generator.values['api']['serviceAccountName'] = api_sa

                worker_sa = prompt(
                    _t('worker_serviceaccount'),
                    default="",
                    required=False
                )
                if worker_sa:
                    generator.values['worker']['serviceAccountName'] = worker_sa

                if not api_sa and not worker_sa:
                    print_info(_t('serviceaccount_note'))

                print_info("")
                print_info(_t('ensure_irsa_configured'))

                # Don't configure accessKey and secretKey
                if 'accessKey' in generator.values['persistence']['s3']:
                    del generator.values['persistence']['s3']['accessKey']
                if 'secretKey' in generator.values['persistence']['s3']:
                    del generator.values['persistence']['s3']['secretKey']
            else:  # Access Key Mode
                print_info("")
                print_info("=" * 60)
                print_info(_t('access_key_config_note'))
                print_info("=" * 60)
                print_info(_t('access_key_config_instructions'))
                print_info(_t('ensure_iam_permissions'))
                print_info("=" * 60)
                print_info("")

                # Set useAwsManagedIam = false
                generator.values['persistence']['s3']['useAwsManagedIam'] = False

                # Configure Access Key and Secret Key
                generator.values['persistence']['s3']['accessKey'] = prompt(
                    _t('access_key'),
                    default="",
                    required=True
                )
                generator.values['persistence']['s3']['secretKey'] = prompt(
                    _t('secret_key'),
                    default="",
                    required=True
                )

            # Configure Region and Bucket
            generator.values['persistence']['s3']['region'] = prompt(
                _t('region'),
                default="us-east-1",
                required=False
            )
            generator.values['persistence']['s3']['bucketName'] = prompt(
                _t('bucket_name'),
                default="your-bucket-name",
                required=True
            )
        else:
            # Non-AWS S3 configuration (MinIO, Cloudflare R2, etc.)
            generator.values['persistence']['s3']['useAwsS3'] = False
            generator.values['persistence']['s3']['useAwsManagedIam'] = False
            print_info(f"{_t('config_non_aws_s3')} {s3_provider} (S3 Compatible)")
            # 非 AWS S3 需要内置 MinIO
            generator.values['minio']['enabled'] = True
            print_info(_t('auto_enable_minio'))

            # MinIO special configuration instructions
            if s3_provider == "MinIO":
                print_info("")
                print_info("=" * 60)
                print_info(_t('external_minio_note'))
                print_info("=" * 60)
                print_info(_t('external_minio_desc'))
                print_info(_t('minio_access_key_note'))
                print_info(_t('minio_secret_key_note'))
                print_info("=" * 60)
                print_info("")
                default_endpoint = "http://host.docker.internal:9000"
                default_access_key = "minioadmin"
                default_secret_key = "minioadmin123"
            else:
                default_endpoint = "https://xxx.r2.cloudflarestorage.com"
                default_access_key = ""
                default_secret_key = ""

            generator.values['persistence']['s3']['endpoint'] = prompt(
                _t('s3_endpoint_url'),
                default=default_endpoint,
                required=True
            )

            if s3_provider == "MinIO":
                print_info("")
                print_info(_t('minio_auth_info'))
                print_info(_t('minio_access_key_note'))
                print_info(_t('minio_secret_key_note'))
                print_info("")

            generator.values['persistence']['s3']['accessKey'] = prompt(
                f"{_t('minio_access_key') if s3_provider == 'MinIO' else _t('access_key')}",
                default=default_access_key,
                required=True
            )
            generator.values['persistence']['s3']['secretKey'] = prompt(
                f"{_t('minio_secret_key') if s3_provider == 'MinIO' else _t('secret_key')}",
                default=default_secret_key,
                required=True
            )
            generator.values['persistence']['s3']['region'] = prompt(
                _t('region'),
                default="us-east-1",
                required=False
            )
            generator.values['persistence']['s3']['bucketName'] = prompt(
                _t('bucket_name'),
                default="your-bucket-name",
                required=True
            )

        address_type = prompt(
            _t('address_type'),
            default="",
            required=False
        )
        if address_type:
            generator.values['persistence']['s3']['addressType'] = address_type

        # If MinIO is enabled, configure MinIO
        if generator.values['minio'].get('enabled', False):
            print_section(_t('config_builtin_minio'))
            print_info("=" * 60)
            print_info(_t('builtin_minio_note'))
            print_info("=" * 60)
            print_info(_t('builtin_minio_desc'))
            print_info(_t('business_storage_note'))
            print_info("=" * 60)
            print_info("")
            if prompt_yes_no(_t('auto_generate_minio_password'), default=True):
                generator.values['minio']['rootPassword'] = generate_secret(32)
                print_success(_t('minio_password_generated'))
            else:
                generator.values['minio']['rootPassword'] = prompt(
                    _t('minio_root_password'),
                    required=True
                )

            generator.values['minio']['rootUser'] = prompt(
                _t('minio_root_user'),
                default="minioadmin",
                required=False
            )

    # MinIO configuration - If storage type is not s3, need to enable built-in MinIO
    if storage_type != "s3":
        print_section(_t('config_builtin_minio'))
        print_info("=" * 60)
        print_info(_t('builtin_minio_note'))
        print_info("=" * 60)
        print_info(_t('builtin_minio_desc'))
        print_info(_t('business_storage_note'))
        print_info("=" * 60)
        print_info("")
        generator.values['minio']['enabled'] = True

        if prompt_yes_no(_t('auto_generate_minio_password'), default=True):
            generator.values['minio']['rootPassword'] = generate_secret(32)
            print_success(_t('minio_password_generated'))
        else:
            generator.values['minio']['rootPassword'] = prompt(
                _t('minio_root_password'),
                required=True
            )

        generator.values['minio']['rootUser'] = prompt(
            _t('minio_root_user'),
            default="minioadmin",
            required=False
        )

    # ==================== 模块 3: 网络配置 ====================
