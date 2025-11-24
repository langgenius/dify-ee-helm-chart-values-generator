"""
Project configuration constants

This module contains all configurable constants for the project.
Modify these values to adapt to different Helm Chart repositories or deployment scenarios.
"""

# Helm Chart Configuration
HELM_CHART_NAME = "dify"
HELM_REPO_URL = "https://langgenius.github.io/dify-helm"
HELM_REPO_NAME = "dify-helm"

# Cache Configuration
CACHE_DIR = ".cache"
LOCAL_VALUES_FILE = "values.yaml"

# Output Configuration
OUTPUT_FILE = "values-prd.yaml"

# Timeout Configuration (in seconds)
DOWNLOAD_TIMEOUT = 10

# Version Configuration
DEFAULT_CHART_VERSION = None  # None means latest
DEFAULT_EE_VERSION = None  # None means interactive selection

