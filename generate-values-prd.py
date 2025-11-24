#!/usr/bin/env python3
"""
Dify Helm Chart Values Generator
Interactive tool to generate values-prd.yaml configuration file

Module structure and relationships:
1. Global Configuration Module - affects all services
2. Infrastructure Module - database, storage, cache (mutually exclusive choices)
3. Network Module - Ingress configuration
4. Mail Module - email service configuration
5. Plugin Module - plugin configuration (3.0+ only)
6. Service Module - application service configuration
"""

import os
import sys

import config
from i18n import set_language, get_translator
from i18n.language import prompt_language_selection
from utils import print_info, print_error, print_warning, get_or_download_values
from utils.downloader import download_and_extract_chart
from utils.downloader import download_and_extract_chart
from version_manager import VersionManager
from generator import ValuesGenerator


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Dify Helm Chart Values Generator - Interactive values-prd.yaml generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use default settings (auto-download latest version, interactive Dify EE version selection)
  python generate-values-prd.py

  # Specify Helm Chart version and Dify EE version
  python generate-values-prd.py --chart-version 3.6.0 --ee-version 3.0

  # Use local values.yaml
  python generate-values-prd.py --local

  # Force re-download
  python generate-values-prd.py --force-download

  # Specify language
  python generate-values-prd.py --lang zh
        """
    )
    parser.add_argument(
        "--chart-version", "-c",
        type=str,
        default=None,
        help="Specify Helm Chart version (default: latest)"
    )
    parser.add_argument(
        "--ee-version", "-e",
        type=str,
        default=None,
        choices=VersionManager.get_available_versions(),
        help=f"Specify Dify EE version (default: interactive selection). Available: {', '.join(VersionManager.get_available_versions())}"
    )
    parser.add_argument(
        "--local", "-l",
        action="store_true",
        help="Use local values.yaml file (don't download)"
    )
    parser.add_argument(
        "--force-download", "-f",
        action="store_true",
        help="Force re-download values.yaml (ignore cache)"
    )
    parser.add_argument(
        "--lang", "--language",
        type=str,
        choices=['en', 'zh'],
        default=None,
        help="Language: en (English) or zh (Chinese). Default: interactive selection"
    )
    parser.add_argument(
        "--repo-url",
        type=str,
        default=config.HELM_REPO_URL,
        help=f"Helm Chart repository URL (default: {config.HELM_REPO_URL})"
    )
    parser.add_argument(
        "--chart-name",
        type=str,
        default=config.HELM_CHART_NAME,
        help=f"Helm Chart name (default: {config.HELM_CHART_NAME})"
    )
    parser.add_argument(
        "--repo-name",
        type=str,
        default=config.HELM_REPO_NAME,
        help=f"Helm repository name (default: {config.HELM_REPO_NAME})"
    )

    args = parser.parse_args()

    # Language selection
    if args.lang:
        set_language(args.lang)
    else:
        # Interactive language selection
        prompt_language_selection()

    # Initialize translator with selected language
    _t = get_translator()

    # Get values.yaml file
    if args.local:
        source_file = config.LOCAL_VALUES_FILE
        if not os.path.exists(source_file):
            print_error(f"{_t('file_not_found')}: {source_file}")
            print_info(_t('or_manual_download'))
            sys.exit(1)
        print_info(f"{_t('using_local')}: {source_file}")
    else:
        try:
            # If chart version is specified via CLI, don't prompt
            prompt_version = args.chart_version is None
            source_file = get_or_download_values(
                version=args.chart_version,
                force_download=args.force_download,
                prompt_version=prompt_version,
                repo_url=args.repo_url,
                repo_name=args.repo_name
            )

            # Download and extract Helm Chart
            chart_version = args.chart_version
            if not chart_version:
                # Extract version from source_file path if it's cached
                import re
                match = re.search(r'values-([\d.]+)\.yaml', source_file)
                if match:
                    chart_version = match.group(1)
                else:
                    # Get latest version
                    from utils.downloader import get_published_version
                    chart_version = get_published_version(repo_url=args.repo_url, repo_name=args.repo_name)

            if chart_version:
                chart_dir = download_and_extract_chart(
                    version=chart_version,
                    repo_url=args.repo_url,
                    repo_name=args.repo_name
                )
                if chart_dir:
                    print_info(f"{_t('chart_directory')}: {chart_dir}")
        except KeyboardInterrupt:
            print("\n")
            print_warning(_t('user_interrupted'))
            sys.exit(1)
        except Exception as e:
            print_error(f"{_t('download_failed')}: {e}")
            print_info("\n" + _t('check_helm_install'))
            print_info(_t('check_1'))
            print_info(_t('check_2'))
            print_info(_t('check_3'))
            sys.exit(1)

    # Verify file exists
    if not os.path.exists(source_file):
        print_error(f"{_t('file_not_found')}: {source_file}")
        sys.exit(1)
    
    # Select Dify EE version
    if args.ee_version:
        ee_version = args.ee_version
        version_info = VersionManager.get_version_info(ee_version)
        if version_info:
            print_info(f"{_t('selected')}: {version_info.get('name', ee_version)}")
        else:
            print_error(f"{_t('invalid_version')}: {ee_version}")
            sys.exit(1)
    else:
        # Interactive version selection
        ee_version = VersionManager.prompt_version_selection()

    # Generate configuration
    generator = ValuesGenerator(source_file, version=ee_version)
    generator.generate()


if __name__ == "__main__":
    main()
