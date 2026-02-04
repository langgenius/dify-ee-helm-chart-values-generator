# Dify EE (Enterprise Edition) Helm Chart Values Generator

> An interactive tool for generating production-ready Helm Chart values files for Dify Enterprise Edition

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![Code style: PEP 8](https://img.shields.io/badge/code%20style-PEP%208-orange.svg)](https://www.python.org/dev/peps/pep-0008/)

## 📋 Overview

This project provides a Python script `generate-values-prd.py` that interactively guides users through generating `values-prd.yaml` configuration files. The script uses a modular design and automatically handles relationships between configuration items to ensure consistency and correctness.

[English](README.md) | [中文](README.zh.md)

## ✨ Features

- ✅ **Modular Configuration**: Organized into 6 main modules with clear logic
- ✅ **Automatic Relationship Handling**: Automatically processes mutual exclusions and dependencies
- ✅ **Auto Key Generation**: All keys are automatically generated using `openssl`:
  - `appSecretKey`: 42 bytes
  - `innerApiKey`: 42 bytes
  - `enterprise.appSecretKey`: 42 bytes
  - `enterprise.adminAPIsSecretKeySalt`: 42 bytes
  - `enterprise.passwordEncryptionKey`: 32 bytes (AES-256)
- ✅ **TLS Consistency Check**: Automatically checks TLS configuration consistency with Ingress to avoid CORS issues
- ✅ **RAG Integration**: Automatically handles RAG type and unstructured module relationships
- ✅ **Interactive Guidance**: User-friendly CLI interface with detailed configuration for databases and Redis connections
- ✅ **Progress Preservation**: Supports saving partial configuration after interruption
- ✅ **Automated PR Review**: GitHub Actions bot automatically reviews PRs for code quality, formatting, and security issues

## 🚀 Quick Start

### Prerequisites

- Python 3.6+
- PyYAML library
- `openssl` (usually pre-installed on systems)
- `ruamel.yaml` (recommended): For preserving YAML file format, comments, and quotes
- `helm` (required): For downloading values.yaml from Helm Chart repository. The script requires Helm to be installed.

### Installation

**Using uv (recommended, faster):**

```bash
# 1. Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Create virtual environment
uv venv

# 3. Activate virtual environment (optional, uv auto-detects)
source .venv/bin/activate

# 4. Install dependencies
uv pip install -r requirements.txt
```

**Or using pip:**

```bash
pip install -r requirements.txt
```

### Usage

**Basic usage (automatically downloads latest values.yaml):**

```bash
python generate-values-prd.py
```

**Specify a version:**

```bash
python generate-values-prd.py --version 3.6.0
```

**Use local values.yaml:**

```bash
python generate-values-prd.py --local
```

**Force re-download:**

```bash
python generate-values-prd.py --force-download
```

**Command-line options:**

- `--version, -v`: Specify Helm Chart version (default: latest)
- `--local, -l`: Use local values.yaml file (don't download)
- `--force-download, -f`: Force re-download values.yaml (ignore cache)
- `--repo-url`: Custom Helm Chart repository URL

The script requires Helm to be installed. It will automatically download `values.yaml` from the official Dify Helm Chart repository if it's not found locally. Downloaded files are cached in `.cache/` directory.

The script will guide you through the following configuration modules:

1. **Global Configuration** - Affects all services
2. **Infrastructure Configuration** - Database, storage, cache (mutually exclusive choices)
3. **Network Configuration** - Ingress configuration
4. **Mail Configuration** - Email service configuration
5. **Plugin Configuration** - Plugin connector image repository configuration
6. **Service Configuration** - Application service configuration

The generated configuration file will be saved as `out/values-prd-{version}.yaml` (e.g., `out/values-prd-3.5.6.yaml`).

## 📁 Project Structure

```
.
├── generate-values-prd.py       # Main script file
├── generate-image-repo-secret.sh # Docker registry secret generator
├── generator.py                 # Core generator class
├── version_manager.py        # Version management
├── config.py                 # Configuration constants
├── pyproject.toml           # Python project configuration
├── requirements.txt         # Python dependencies
├── LICENSE                  # MIT License
├── CONTRIBUTING.md          # Contribution guidelines
├── .gitignore              # Git ignore configuration
├── modules/                # Configuration modules
├── utils/                  # Utility functions
├── i18n/                   # Internationalization
├── out/                    # Generated output files (gitignored)
└── docs/                   # Documentation directory
    ├── README-GENERATOR.md  # Detailed usage guide
    ├── MODULES.md          # Module structure and relationships
    ├── FLOWCHART.md        # Configuration flowcharts
    ├── KIND-NETWORKING.md  # Kind cluster networking guide
    ├── IMPROVEMENTS.md     # Improvement records
    └── CHANGELOG.md        # Changelog
```

## 📚 Documentation

Detailed documentation is available in the `docs/` directory:

- [README-GENERATOR.md](docs/README-GENERATOR.md) - Complete usage guide and examples
- [MODULES.md](docs/MODULES.md) - Module structure and relationship explanations
- [FLOWCHART.md](docs/FLOWCHART.md) - Configuration flowcharts
- [KIND-NETWORKING.md](docs/KIND-NETWORKING.md) - Kind cluster networking guide

## 🔧 Configuration Modules

### Module 1: Global Configuration
- Affects all services
- Includes keys, domains, RAG configuration, etc.

### Module 2: Infrastructure Configuration
- Database selection (PostgreSQL/MySQL)
- Storage selection (MinIO/S3/Azure Blob/etc.)
- Cache selection (Redis)
- Vector database selection (Qdrant/Weaviate/Milvus)

### Module 3: Network Configuration
- Ingress configuration
- TLS settings
- Certificate management (cert-manager support)

### Module 4: Mail Configuration
- SMTP server configuration
- Resend service configuration
- Email service settings

### Module 5: Plugin Configuration
- Image repository type (Docker/ECR)
- Authentication method (IRSA/K8s Secret)
- Protocol selection (HTTPS/HTTP)

### Module 6: Service Configuration
- Enterprise license configuration
- Service enable/disable toggles
- Resource limits

### Relationship Handling

The script automatically handles the following relationships:

- **RAG Integration**: `rag.etlType = "dify"` → `unstructured.enabled = false`
- **RAG Integration**: `rag.etlType = "Unstructured"` → `unstructured.enabled = true`
- **TLS Consistency**: TLS configuration automatically syncs with Ingress to avoid CORS issues
- **Infrastructure Mutex**: Database, storage, and cache selections are mutually exclusive

## 🔐 Docker Registry Secret

If you're using a private Docker registry (e.g., for Dify EE images), you can use the provided script to create an imagePullSecret:

```bash
./generate-image-repo-secret.sh
```

The script will interactively prompt you for:
- Docker Registry username
- Docker Registry password
- Kubernetes namespace (default: `default`)
- Registry URL (default: `https://index.docker.io/v1/`)

It creates a Kubernetes secret named `image-repo-secret` that can be referenced in your Helm values.

## 🔒 Security

- Generated `values-prd-{version}.yaml` files contain sensitive information and are gitignored
- All generated files are saved in `out/` directory which is gitignored
- Sensitive files like `email-server.txt` are excluded from the repository
- All keys are generated using `openssl` for security
- Supports IRSA (IAM Roles for Service Accounts) for AWS ECR authentication
- Never commit generated configuration files to version control

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

### Automated PR Review

This project uses an automated PR review bot powered by GitHub Actions. When you create or update a Pull Request, the bot will automatically:

- Check Python code style (flake8, pylint)
- Verify code formatting (black)
- Validate YAML files (yamllint)
- Check shell scripts (shellcheck)
- Scan for potential security issues

See [docs/PR-REVIEW.md](docs/PR-REVIEW.md) for more details.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Links

- [Dify Official Documentation](https://docs.dify.ai/)
- [Helm Chart Documentation](https://helm.sh/docs/)
- [Dify Enterprise Documentation](https://enterprise-docs.dify.ai/)

## 🙏 Acknowledgments

- Built for [Dify](https://github.com/langgenius/dify) Enterprise Edition
- Uses [ruamel.yaml](https://yaml.readthedocs.io/) for YAML processing
