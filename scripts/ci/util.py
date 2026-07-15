# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import logging
import os
import shlex
import json
import zipfile

from subprocess import check_output

logger = logging.getLogger(__name__)

def get_repo_root():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(current_dir, 'CONTRIBUTING.rst')):
        current_dir = os.path.dirname(current_dir)
    return current_dir


def _get_extension_modname(ext_dir):
    # Modification of https://github.com/Azure/azure-cli/blob/dev/src/azure-cli-core/azure/cli/core/extension.py#L153
    EXTENSIONS_MOD_PREFIX = 'azext_'
    pos_mods = [n for n in os.listdir(ext_dir)
                if n.startswith(EXTENSIONS_MOD_PREFIX) and os.path.isdir(os.path.join(ext_dir, n))]
    if len(pos_mods) != 1:
        raise AssertionError("Expected 1 module to load starting with "
                             "'{}': got {}".format(EXTENSIONS_MOD_PREFIX, pos_mods))
    return pos_mods[0]


def _get_azext_metadata(ext_dir):
    # Modification of https://github.com/Azure/azure-cli/blob/dev/src/azure-cli-core/azure/cli/core/extension.py#L109
    AZEXT_METADATA_FILENAME = 'azext_metadata.json'
    azext_metadata = None
    ext_modname = _get_extension_modname(ext_dir=ext_dir)
    azext_metadata_filepath = os.path.join(ext_dir, ext_modname, AZEXT_METADATA_FILENAME)
    if os.path.isfile(azext_metadata_filepath):
        with open(azext_metadata_filepath) as f:
            azext_metadata = json.load(f)
    return azext_metadata


def get_ext_metadata(ext_dir, ext_file, ext_name):
    # Modification of https://github.com/Azure/azure-cli/blob/dev/src/azure-cli-core/azure/cli/core/extension.py#L89
    # Read spec-defined wheel metadata via pkginfo so we don't depend on the
    # legacy wheel-0.30.0 only ``metadata.json`` artifact. Imported lazily so
    # that modules importing util for unrelated helpers (SRC_PATH, get_repo_root,
    # get_index_data, ...) do not require azdev to be installed.
    from azdev.operations.extensions.metadata import pkginfo_to_dict
    generated_metadata = pkginfo_to_dict(ext_file)
    with zipfile.ZipFile(ext_file, 'r') as zip_ref:
        zip_ref.extractall(ext_dir)
    metadata = {}

    azext_metadata = _get_azext_metadata(ext_dir)
    if not azext_metadata:
        raise ValueError('azext_metadata.json for Extension "{}" Metadata is missing'.format(ext_name))
    metadata.update(azext_metadata)
    metadata.update(generated_metadata)
    return metadata


def get_whl_from_url(url, filename, tmp_dir, whl_cache=None):
    if not whl_cache:
        whl_cache = {}
    if url in whl_cache:
        return whl_cache[url]
    import requests
    TRIES = 3
    for try_number in range(TRIES):
        try:
            r = requests.get(url, stream=True)
            assert r.status_code == 200, "Request to {} failed with {}".format(url, r.status_code)
            break
        except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as err:
            import time
            time.sleep(0.5)
            continue

    ext_file = os.path.join(tmp_dir, filename)
    with open(ext_file, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # ignore keep-alive new chunks
                f.write(chunk)
    whl_cache[url] = ext_file
    return ext_file


def get_sha256sum(a_file):
    """Compute the SHA-256 hex digest of a file."""
    import hashlib
    sha256 = hashlib.sha256()
    with open(a_file, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def fetch_github_index(repo, branch, token=None):
    """Fetch index.json from GitHub raw content.

    Args:
        repo: GitHub repo in owner/repo format (e.g. 'Azure/azure-cli-extensions')
        branch: Branch name (e.g. 'main')
        token: Optional GitHub PAT for private repos

    Returns:
        dict: Parsed index.json content

    Raises:
        RuntimeError: If the fetch fails
    """
    import requests
    url = 'https://raw.githubusercontent.com/{}/{}/src/index.json'.format(repo, branch)
    headers = {}
    if token:
        headers['Authorization'] = 'token {}'.format(token)
    try:
        r = requests.get(url, headers=headers, timeout=30)
        if r.status_code != 200:
            raise RuntimeError("Failed to fetch index.json from GitHub: HTTP {}".format(r.status_code))
        try:
            return r.json()
        except ValueError as exc:
            raise RuntimeError("Failed to parse index.json from GitHub: {}".format(exc))
    except requests.exceptions.RequestException as exc:
        raise RuntimeError("Failed to fetch index.json from GitHub: {}".format(exc))


def upload_wheel_no_overwrite(whl_path, storage_account, storage_container, blob_prefix=None):
    """Upload a wheel to Azure Blob Storage without overwriting.

    Returns:
        str: The blob URL if upload succeeded (new blob created).
        None: If the blob already exists (upload was rejected).

    Raises:
        RuntimeError: On unexpected upload failure.
    """
    from subprocess import run as subprocess_run
    whl_file = os.path.basename(whl_path)
    blob_name = '{}/{}'.format(blob_prefix, whl_file) if blob_prefix else whl_file

    cmd = [
        'az', 'storage', 'blob', 'upload',
        '--container-name', storage_container,
        '--account-name', storage_account,
        '--name', blob_name,
        '--file', os.path.abspath(whl_path),
        '--auth-mode', 'login',
        '--overwrite', 'false',
    ]
    logger.info("Uploading wheel (no overwrite): %s", whl_file)
    result = subprocess_run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        url = get_blob_url(storage_account, storage_container, blob_name)
        return url

    stderr = result.stderr or ''
    # Azure CLI returns error when blob already exists with --overwrite false
    if 'BlobAlreadyExists' in stderr or 'ResourceExistsError' in stderr or '409' in stderr:
        logger.info("Blob '%s' already exists. Skipping upload.", blob_name)
        return None

    raise RuntimeError("Failed to upload '{}': {}".format(whl_file, stderr))


def download_blob(storage_account, storage_container, blob_name, dest_path):
    """Download a blob from Azure Blob Storage to a local path.

    Raises:
        RuntimeError: On download failure.
    """
    from subprocess import run as subprocess_run
    cmd = [
        'az', 'storage', 'blob', 'download',
        '--container-name', storage_container,
        '--account-name', storage_account,
        '--name', blob_name,
        '--file', dest_path,
        '--auth-mode', 'login',
    ]
    logger.info("Downloading blob '%s' to '%s'", blob_name, dest_path)
    result = subprocess_run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError("Failed to download blob '{}': {}".format(
            blob_name, result.stderr))
    logger.info("Download complete: %s", dest_path)


def get_blob_url(storage_account, storage_container, blob_name):
    """Get the public URL of a blob.

    Returns:
        str: The blob URL.

    Raises:
        RuntimeError: On failure.
    """
    from subprocess import run as subprocess_run
    cmd = [
        'az', 'storage', 'blob', 'url',
        '--container-name', storage_container,
        '--account-name', storage_account,
        '--name', blob_name,
        '--auth-mode', 'login',
        '-otsv',
    ]
    result = subprocess_run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError("Failed to get blob URL for '{}': {}".format(
            blob_name, result.stderr))
    return result.stdout.strip()


SRC_PATH = os.path.join(get_repo_root(), 'src')
INDEX_PATH = os.path.join(SRC_PATH, 'index.json')


def _catch_dup_keys(pairs):
    seen = {}
    for k, v in pairs:
        if k in seen:
            raise ValueError("duplicate key {}".format(k))
        seen[k] = v
    return seen


def get_index_data():
    try:
        with open(INDEX_PATH) as f:
            return json.load(f, object_pairs_hook=_catch_dup_keys)
    except ValueError as err:
        raise AssertionError("Invalid JSON in {}: {}".format(INDEX_PATH, err))


def diff_code(start, end):
    diff_ref = []

    for src_d in os.listdir(SRC_PATH):
        src_d_full = os.path.join(SRC_PATH, src_d)
        if not os.path.isdir(src_d_full):
            continue
        pkg_name = next((d for d in os.listdir(src_d_full) if d.startswith('azext_')), None)

        # If running in Travis CI, only run tests for edited extensions
        commit_range = os.environ.get('TRAVIS_COMMIT_RANGE')
        if commit_range and not check_output(
                ['git', '--no-pager', 'diff', '--name-only', commit_range, '--', src_d_full]):
            continue

        # Running in Azure DevOps
        cmd_tpl = 'git --no-pager diff --name-only origin/{start} {end} -- {code_dir}'
        # ado_branch_last_commit = os.environ.get('ADO_PULL_REQUEST_LATEST_COMMIT')
        # ado_target_branch = os.environ.get('ADO_PULL_REQUEST_TARGET_BRANCH')
        if start and end:
            if end == '$(System.PullRequest.SourceCommitId)':
                # default value if ADO_PULL_REQUEST_LATEST_COMMIT not set in ADO
                continue
            elif start == '$(System.PullRequest.TargetBranch)':
                # default value if ADO_PULL_REQUEST_TARGET_BRANCH not set in ADO
                continue
            else:
                cmd = cmd_tpl.format(start=start, end=end,
                                     code_dir=src_d_full)
                if not check_output(shlex.split(cmd)):
                    continue

        diff_ref.append((pkg_name, src_d_full))

    logger.warning(f'start: {start}, '
                   f'end: {end}, '
                   f'diff_ref: {diff_ref}.')
    return diff_ref
