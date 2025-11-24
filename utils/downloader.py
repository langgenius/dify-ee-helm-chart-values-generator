"""Values.yaml download utilities"""

import os
import subprocess
import sys
import shutil
import json
import urllib.request
import yaml
import tarfile
from typing import Optional, List
from pathlib import Path

from .colors import print_info, print_success, print_warning, print_error
from .prompts import prompt_choice
from i18n import get_translator
import config

_t = get_translator()


def get_helm_chart_versions(
    chart_name: Optional[str] = None,
    repo_url: Optional[str] = None,
    repo_name: Optional[str] = None
) -> List[str]:
    """
    Get all available versions by directly downloading index.yaml

    This function is used for displaying version list to users.
    It directly downloads index.yaml for faster and more reliable access.

    Args:
        chart_name: Chart name, defaults to config.HELM_CHART_NAME
        repo_url: Helm Chart repository URL, defaults to config.HELM_REPO_URL
        repo_name: Repository name, defaults to config.HELM_REPO_NAME (not used, kept for compatibility)

    Returns:
        List of available versions (sorted, latest first)
    """
    # Use global config defaults if not provided
    chart_name = chart_name or config.HELM_CHART_NAME
    repo_url = repo_url or config.HELM_REPO_URL

    versions = []

    # Directly download index.yaml to get all versions
    try:
        index_url = f"{repo_url.rstrip('/')}/index.yaml"
        print_info(_t('fetching_versions_from_index'))
        with urllib.request.urlopen(index_url, timeout=config.DOWNLOAD_TIMEOUT) as response:
            index_data = yaml.safe_load(response.read())
            if index_data and 'entries' in index_data:
                chart_entries = index_data['entries'].get(chart_name, [])
                versions = [entry.get('version', '') for entry in chart_entries if entry.get('version')]
    except Exception as e:
        print_warning(f"{_t('failed_to_fetch_versions')}: {e}")

    # Sort versions (semantic versioning, latest first)
    def version_key(v):
        try:
            parts = v.split('.')
            return tuple(int(p) if p.isdigit() else 0 for p in parts)
        except:
            return (0, 0, 0)

    versions = sorted(set(versions), key=version_key, reverse=True)
    return versions


def get_published_version(
    chart_name: Optional[str] = None,
    repo_url: Optional[str] = None,
    repo_name: Optional[str] = None,
    version: Optional[str] = None
) -> Optional[str]:
    """
    Get published version using Helm command

    This function is used when downloading values.yaml for a specific version.
    It uses Helm command to ensure the version is actually published and available.

    Args:
        chart_name: Chart name, defaults to config.HELM_CHART_NAME
        repo_url: Helm Chart repository URL, defaults to config.HELM_REPO_URL
        repo_name: Repository name, defaults to config.HELM_REPO_NAME
        version: Specific version to check, if None returns latest published version

    Returns:
        Version string if found, None otherwise
    """
    # Use global config defaults if not provided
    chart_name = chart_name or config.HELM_CHART_NAME
    repo_url = repo_url or config.HELM_REPO_URL
    repo_name = repo_name or config.HELM_REPO_NAME

    try:
        # Ensure repository is added
        check_repo_cmd = ["helm", "repo", "list", "-o", "json"]
        try:
            repo_list = json.loads(subprocess.check_output(check_repo_cmd, stderr=subprocess.STDOUT).decode())
            repos = [r.get("name", "") for r in repo_list]
            if repo_name not in repos:
                subprocess.check_call(
                    ["helm", "repo", "add", repo_name, repo_url],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE
                )
            subprocess.check_call(
                ["helm", "repo", "update", repo_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE
            )
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            try:
                subprocess.check_call(
                    ["helm", "repo", "add", repo_name, repo_url],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE
                )
                subprocess.check_call(
                    ["helm", "repo", "update", repo_name],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE
                )
            except subprocess.CalledProcessError:
                return None

        # Get versions using helm search
        versions_cmd = ["helm", "search", "repo", f"{repo_name}/{chart_name}", "--versions", "-o", "json"]
        versions_output = subprocess.check_output(versions_cmd, stderr=subprocess.PIPE).decode()
        versions_data = json.loads(versions_output)
        if versions_data:
            if version:
                # Check if specific version exists
                for item in versions_data:
                    if item.get("version") == version:
                        return version
                return None
            else:
                # Return latest version
                if len(versions_data) > 0:
                    return versions_data[0].get("version")
    except Exception:
        pass

    return None


def get_published_versions(
    chart_name: Optional[str] = None,
    repo_url: Optional[str] = None,
    repo_name: Optional[str] = None
) -> List[str]:
    """
    Get published versions using Helm command

    This function uses Helm command to get versions that are actually published and available.

    Args:
        chart_name: Chart name, defaults to config.HELM_CHART_NAME
        repo_url: Helm Chart repository URL, defaults to config.HELM_REPO_URL
        repo_name: Repository name, defaults to config.HELM_REPO_NAME

    Returns:
        List of published versions (sorted, latest first)
    """
    # Use global config defaults if not provided
    chart_name = chart_name or config.HELM_CHART_NAME
    repo_url = repo_url or config.HELM_REPO_URL
    repo_name = repo_name or config.HELM_REPO_NAME

    versions = []

    try:
        # Ensure repository is added
        check_repo_cmd = ["helm", "repo", "list", "-o", "json"]
        try:
            repo_list = json.loads(subprocess.check_output(check_repo_cmd, stderr=subprocess.STDOUT).decode())
            repos = [r.get("name", "") for r in repo_list]
            if repo_name not in repos:
                subprocess.check_call(
                    ["helm", "repo", "add", repo_name, repo_url],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE
                )
            subprocess.check_call(
                ["helm", "repo", "update", repo_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE
            )
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            try:
                subprocess.check_call(
                    ["helm", "repo", "add", repo_name, repo_url],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE
                )
                subprocess.check_call(
                    ["helm", "repo", "update", repo_name],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE
                )
            except subprocess.CalledProcessError:
                return []

        # Get versions using helm search
        versions_cmd = ["helm", "search", "repo", f"{repo_name}/{chart_name}", "--versions", "-o", "json"]
        versions_output = subprocess.check_output(versions_cmd, stderr=subprocess.PIPE).decode()
        versions_data = json.loads(versions_output)
        if versions_data:
            versions = [item.get("version", "") for item in versions_data if item.get("version")]
    except Exception:
        pass

    # Sort versions (semantic versioning, latest first)
    def version_key(v):
        try:
            parts = v.split('.')
            return tuple(int(p) if p.isdigit() else 0 for p in parts)
        except:
            return (0, 0, 0)

    versions = sorted(set(versions), key=version_key, reverse=True)
    return versions


def prompt_helm_chart_version(
    chart_name: Optional[str] = None,
    repo_url: Optional[str] = None,
    repo_name: Optional[str] = None
) -> Optional[str]:
    """
    Prompt user to select Helm Chart version

    Args:
        chart_name: Chart name, defaults to config.HELM_CHART_NAME
        repo_url: Repository URL, defaults to config.HELM_REPO_URL
        repo_name: Repository name, defaults to config.HELM_REPO_NAME

    Returns:
        Selected version string, or None for latest
    """
    # Use global config defaults if not provided
    chart_name = chart_name or config.HELM_CHART_NAME
    repo_url = repo_url or config.HELM_REPO_URL
    repo_name = repo_name or config.HELM_REPO_NAME

    # Prompt user to choose version source
    print_info("")
    version_source = prompt_choice(
        _t('select_version_source'),
        [_t('published_versions'), _t('all_versions')],
        default=_t('published_versions')
    )

    # Fetch versions based on user's choice
    if version_source == _t('published_versions'):
        print_info(_t('fetching_published_versions'))
        versions = get_published_versions(chart_name, repo_url, repo_name)
    else:
        print_info(_t('fetching_available_versions'))
        versions = get_helm_chart_versions(chart_name, repo_url, repo_name)

    if not versions:
        print_warning(_t('no_versions_found'))
        print_info(_t('using_latest_version'))
        return None

    # Get the latest version (first in sorted list, which is already reverse sorted)
    latest_version = versions[0] if versions else None

    # Prepare options with "Latest" showing actual version number
    # Format: "3.5.6 (latest version)" instead of just "latest version"
    if latest_version:
        latest_option = f"{latest_version} ({_t('latest_version')})"
    else:
        latest_option = _t('latest_version')

    # Reverse the versions list to show oldest first, latest last
    # versions is already sorted reverse (newest first), so reverse it to oldest first
    reversed_versions = list(reversed(versions))

    # Build options list: older versions first, latest version (with label) last
    # Exclude latest version from the list to avoid duplication
    # Only include versions that are NOT the latest version
    other_versions = [v for v in reversed_versions if v != latest_version]
    options = other_versions + [latest_option]

    # Display versions in reverse order (oldest to newest, with latest at the end)
    # Use reverse numbering: oldest version gets highest number, latest gets 1
    print_info("")
    print_info(_t('available_versions'))
    total_count = len(options)

    # Display with reverse numbering
    for i, option in enumerate(options, 1):
        display_number = total_count - i + 1  # Reverse numbering: last item is 1
        if i == total_count:  # Last item (latest version)
            print_info(f"  {display_number}. {option} ({_t('recommended')}) [{_t('default')}]")
        else:
            print_info(f"  {display_number}. {option}")

    # Custom prompt for reverse numbering
    # Map reverse display numbers to actual option indices
    default_marker = _t('default')
    select_text = _t('select_range')
    if latest_option:
        prompt_str = f"\n{select_text} [1-{total_count}] ({default_marker}: {latest_option}): "
    else:
        prompt_str = f"\n{select_text} [1-{total_count}]: "

    while True:
        value = input(prompt_str).strip()
        if not value and latest_option:
            selected = latest_option
            break

        try:
            display_num = int(value)
            # Convert reverse display number to actual index
            # Display 1 -> index total_count-1 (last item)
            # Display total_count -> index 0 (first item)
            actual_idx = total_count - display_num
            if 0 <= actual_idx < len(options):
                selected = options[actual_idx]
                break
        except ValueError:
            pass

        range_text = _t('enter_number_range')
        from .colors import print_error
        print_error(f"{range_text} 1-{total_count}")

    # selected is already set above

    # Check if user selected the latest option (with version number)
    # If selected matches latest_option format, return the actual version number
    if selected == latest_option:
        # Return the actual latest version number, not None
        # This ensures we use the exact version the user selected (e.g., 3.6.0-beta.1)
        return latest_version
    # Return the selected version (which is not the latest)
    return selected


def download_and_extract_chart(
    chart_name: Optional[str] = None,
    repo_url: Optional[str] = None,
    version: Optional[str] = None,
    repo_name: Optional[str] = None,
    extract_dir: Optional[str] = None
) -> Optional[str]:
    """
    Download and extract Helm Chart to local directory

    Args:
        chart_name: Chart name, defaults to config.HELM_CHART_NAME
        repo_url: Helm Chart repository URL, defaults to config.HELM_REPO_URL
        version: Chart version, if None uses latest version
        repo_name: Repository name, defaults to config.HELM_REPO_NAME
        extract_dir: Directory to extract chart, defaults to dify-{version}

    Returns:
        Path to extracted chart directory, or None if failed
    """
    # Use global config defaults if not provided
    chart_name = chart_name or config.HELM_CHART_NAME
    repo_url = repo_url or config.HELM_REPO_URL
    repo_name = repo_name or config.HELM_REPO_NAME

    # Check if helm command is available
    helm_available = shutil.which("helm") is not None
    if not helm_available:
        print_error(_t('helm_not_found'))
        return None

    try:
        # Ensure repository is added
        check_repo_cmd = ["helm", "repo", "list", "-o", "json"]
        try:
            repo_list = json.loads(subprocess.check_output(check_repo_cmd, stderr=subprocess.STDOUT).decode())
            repos = [r.get("name", "") for r in repo_list]
            if repo_name not in repos:
                print_info(f"{_t('adding_repo')}: {repo_name}")
                subprocess.check_call(
                    ["helm", "repo", "add", repo_name, repo_url],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE
                )
            subprocess.check_call(
                ["helm", "repo", "update", repo_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE
            )
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            try:
                subprocess.check_call(
                    ["helm", "repo", "add", repo_name, repo_url],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE
                )
                subprocess.check_call(
                    ["helm", "repo", "update", repo_name],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE
                )
            except subprocess.CalledProcessError as e:
                print_error(f"{_t('add_repo_failed')}: {e}")
                return None

        # Get actual version if not specified
        if not version:
            actual_version = get_published_version(chart_name, repo_url, repo_name)
            if not actual_version:
                print_error(_t('failed_to_get_latest_version'))
                return None
            version = actual_version

        # Determine extract directory
        if not extract_dir:
            extract_dir = f"dify-{version}"
        extract_path = Path(extract_dir)

        # Check if already extracted
        if extract_path.exists() and extract_path.is_dir():
            print_warning(f"{_t('chart_directory_exists')}: {extract_path}")
            choice = prompt_choice(
                _t('chart_directory_exists_prompt'),
                [_t('use_existing_directory'), _t('overwrite_existing_directory')],
                default=_t('use_existing_directory')
            )
            if choice == _t('use_existing_directory'):
                print_info(f"{_t('using_existing_directory')}: {extract_path}")
                return str(extract_path)
            else:
                # User chose to overwrite
                print_info(_t('removing_existing_directory'))
                shutil.rmtree(extract_path)

        # Download chart using helm pull
        print_info(_t('downloading_chart'))
        chart_ref = f"{repo_name}/{chart_name}"

        # Use a temporary directory for extraction, then move to final location
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            helm_cmd = ["helm", "pull", chart_ref, "--version", version, "--untar", "--untardir", str(temp_path)]

            try:
                subprocess.check_call(
                    helm_cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE
                )

                # Helm pull --untar extracts to {chart_name} directory (without version)
                # Find the extracted directory
                extracted_chart_dir = temp_path / chart_name
                if not extracted_chart_dir.exists():
                    # Try alternative naming: {chart_name}-{version}
                    extracted_chart_dir = temp_path / f"{chart_name}-{version}"
                if not extracted_chart_dir.exists():
                    # Try to find any directory that was created
                    extracted_dirs = [d for d in temp_path.iterdir() if d.is_dir()]
                    if extracted_dirs:
                        extracted_chart_dir = extracted_dirs[0]
                    else:
                        # List what's actually in temp directory for debugging
                        actual_contents = list(temp_path.iterdir())
                        print_error(f"{_t('chart_extract_error')}: Extracted directory not found in {temp_path}")
                        print_error(f"Actual contents: {[str(p) for p in actual_contents]}")
                        return None

                # Remove target directory if exists
                if extract_path.exists():
                    shutil.rmtree(extract_path)
                # Move extracted directory to final location
                extracted_chart_dir.rename(extract_path)
                print_success(f"{_t('chart_extracted_to')}: {extract_path}")
                return str(extract_path)

            except subprocess.CalledProcessError as e:
                # Get stderr for better error message
                try:
                    result = subprocess.run(
                        helm_cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    error_msg = result.stderr.strip() if result.stderr else str(e)
                    print_error(f"{_t('chart_download_failed')}: {error_msg}")
                except:
                    print_error(f"{_t('chart_download_failed')}: {e}")
                return None

    except Exception as e:
        print_error(f"{_t('chart_extract_error')}: {e}")
        return None


def download_values_from_helm_repo(
    chart_name: Optional[str] = None,
    repo_url: Optional[str] = None,
    version: Optional[str] = None,
    cache_dir: Optional[str] = None,
    repo_name: Optional[str] = None
) -> str:
    """
    Download values.yaml from Helm Chart repository

    Args:
        chart_name: Chart name, defaults to config.HELM_CHART_NAME
        repo_url: Helm Chart repository URL, defaults to config.HELM_REPO_URL
        version: Chart version, if None uses latest version
        cache_dir: Cache directory, defaults to config.CACHE_DIR
        repo_name: Repository name, defaults to config.HELM_REPO_NAME

    Returns:
        Path to values.yaml file

    Raises:
        SystemExit: If Helm is not installed or download fails
    """
    # Use global config defaults if not provided
    chart_name = chart_name or config.HELM_CHART_NAME
    repo_url = repo_url or config.HELM_REPO_URL
    repo_name = repo_name or config.HELM_REPO_NAME
    cache_dir = cache_dir or config.CACHE_DIR

    cache_path = Path(cache_dir)
    cache_path.mkdir(exist_ok=True)

    # Check if helm command is available
    helm_available = shutil.which("helm") is not None

    if not helm_available:
        print_error(_t('helm_not_found'))
        print_info("")
        print_info(_t('install_helm'))
        print_info(_t('install_helm_macos'))
        print_info(_t('install_helm_linux'))
        print_info(_t('install_helm_windows'))
        print_info("")
        print_info(_t('or_manual_download'))
        sys.exit(1)

    try:
        # Use helm show values to get values.yaml
        print_info(_t('downloading_from_repo'))
        print_info(f"{_t('repository')}: {repo_url}")
        if version:
            print_info(f"{_t('version')}: {version}")
        else:
            print_info(f"{_t('version')}: {_t('latest')}")

        # Add repository if not exists
        check_repo_cmd = ["helm", "repo", "list", "-o", "json"]
        try:
            repo_list = json.loads(subprocess.check_output(check_repo_cmd, stderr=subprocess.STDOUT).decode())
            repos = [r.get("name", "") for r in repo_list]
            if repo_name not in repos:
                print_info(f"{_t('adding_repo')}: {repo_name}")
                subprocess.check_call(
                    ["helm", "repo", "add", repo_name, repo_url],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE
                )
                subprocess.check_call(
                    ["helm", "repo", "update", repo_name],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE
                )
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            # If command fails, try adding repository
            try:
                subprocess.check_call(
                    ["helm", "repo", "add", repo_name, repo_url],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE
                )
                subprocess.check_call(
                    ["helm", "repo", "update", repo_name],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE
                )
            except subprocess.CalledProcessError as e:
                print_error(f"{_t('add_repo_failed')}: {e}")
                print_info(_t('check_network_repo_url'))
                sys.exit(1)

        # Build helm show values command
        chart_ref = f"{repo_name}/{chart_name}"

        # Get values.yaml
        print_info(_t('getting_values'))
        helm_cmd = ["helm", "show", "values", chart_ref]
        if version:
            helm_cmd.extend(["--version", version])

        values_content = subprocess.check_output(
            helm_cmd,
            stderr=subprocess.PIPE
        ).decode('utf-8')

        # Determine cache filename
        if version:
            cache_file = cache_path / f"values-{version}.yaml"
        else:
            # Get actual published version using Helm command
            actual_version = get_published_version(chart_name, repo_url, repo_name)
            if actual_version:
                cache_file = cache_path / f"values-{actual_version}.yaml"
                print_info(f"{_t('detected_version')}: {actual_version}")
            else:
                cache_file = cache_path / "values-latest.yaml"

        # Save to cache file
        cache_file.write_text(values_content, encoding='utf-8')
        print_success(f"{_t('saved_to')}: {cache_file}")

        return str(cache_file)

    except subprocess.CalledProcessError as e:
        print_error(f"{_t('helm_command_failed')}: {e}")
        print_info(_t('check_helm_install'))
        print_info(_t('check_1'))
        print_info(_t('check_2'))
        print_info(_t('check_3'))
        print_info("")
        print_info(_t('or_manual_download'))
        sys.exit(1)
    except Exception as e:
        print_error(f"{_t('download_failed')}: {e}")
        print_info(_t('check_network_or_manual'))
        sys.exit(1)


def get_or_download_values(
    version: Optional[str] = None,
    force_download: bool = False,
    prompt_version: bool = True,
    repo_url: Optional[str] = None,
    repo_name: Optional[str] = None
) -> tuple[str, Optional[str]]:
    """
    Get values.yaml file, download if not exists

    Args:
        version: Chart version, if None uses latest version
        force_download: Whether to force re-download
        prompt_version: Whether to prompt user for version selection if version is None
        repo_url: Helm Chart repository URL, defaults to config.HELM_REPO_URL
        repo_name: Repository name, defaults to config.HELM_REPO_NAME

    Returns:
        Tuple of (path to values.yaml file, actual version used)
    """
    # Use global config defaults if not provided
    repo_url = repo_url or config.HELM_REPO_URL
    repo_name = repo_name or config.HELM_REPO_NAME

    # First check if values.yaml exists in current directory
    local_values = Path(config.LOCAL_VALUES_FILE)
    if local_values.exists() and not force_download:
        print_info(f"{_t('using_local')}: {local_values}")
        # Try to get version from cache or use latest
        actual_version = None
        cache_path = Path(config.CACHE_DIR)
        # Check if we can find version from cache files
        if cache_path.exists():
            cache_files = list(cache_path.glob("values-*.yaml"))
            if cache_files:
                import re
                for cf in cache_files:
                    match = re.search(r'values-([\d.]+(?:-[a-zA-Z0-9.]+)?)\.yaml', cf.name)
                    if match:
                        actual_version = match.group(1)
                        break
        return str(local_values), actual_version

    # Prompt for version selection if not specified
    selected_version = version
    if version is None and prompt_version:
        print_info("")
        selected_version = prompt_helm_chart_version(repo_url=repo_url, repo_name=repo_name)

    # Check cache
    cache_path = Path(config.CACHE_DIR)
    if selected_version:
        cache_file = cache_path / f"values-{selected_version}.yaml"
    else:
        cache_file = cache_path / "values-latest.yaml"

    if cache_file.exists() and not force_download:
        print_info(f"{_t('using_cached')}: {cache_file}")
        return str(cache_file), selected_version

    # Download values.yaml
    print_info(_t('not_found_downloading'))
    source_file = download_values_from_helm_repo(version=selected_version, repo_url=repo_url, repo_name=repo_name)

    # Extract actual version from downloaded file
    actual_version = selected_version
    if not actual_version:
        import re
        match = re.search(r'values-([\d.]+(?:-[a-zA-Z0-9.]+)?)\.yaml', source_file)
        if match:
            actual_version = match.group(1)

    return source_file, actual_version

