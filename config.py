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
OUTPUT_DIR = "out"
OUTPUT_FILE_PREFIX = "values-prd"

# Timeout Configuration (in seconds)
DOWNLOAD_TIMEOUT = 10

# Version Configuration
DEFAULT_CHART_VERSION = None  # None means latest
DEFAULT_EE_VERSION = None  # None means interactive selection

# CI Mode Configuration
class _Config:
    """Internal configuration state"""
    ci_mode: bool = False


_config = _Config()


def set_ci_mode(enabled: bool = True):
    """Enable or disable CI mode globally"""
    _config.ci_mode = enabled


def is_ci_mode() -> bool:
    """Check if CI mode is enabled"""
    return _config.ci_mode

