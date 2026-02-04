"""Secret generation utilities"""

import subprocess
from .colors import print_warning
from i18n import get_translator

_t = get_translator()


def generate_secret(length: int = 42) -> str:
    """Generate secret key"""
    try:
        result = subprocess.run(
            ['openssl', 'rand', '-base64', str(length)],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_warning(_t('openssl_fallback'))
        import secrets
        return secrets.token_urlsafe(length)

