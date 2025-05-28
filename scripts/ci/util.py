# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import logging
import os
import re
import shlex
import json
import zipfile

from subprocess import check_output

logger = logging.getLogger(__name__)

# copy from wheel==0.30.0
WHEEL_INFO_RE = re.compile(
    r"""^(?P<namever>(?P<name>.+?)(-(?P<ver>\d.+?))?)
    ((-(?P<build>\d.*?))?-(?P<pyver>.+?)-(?P<abi>.+?)-(?P<plat>.+?)
    \.whl|\.dist-info)$""",
    re.VERBOSE).match


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
    WHL_METADATA_FILENAME = 'metadata.json'
    zip_ref = zipfile.ZipFile(ext_file, 'r')
    zip_ref.extractall(ext_dir)
    zip_ref.close()
    metadata = {}
    dist_info_dirs = [f for f in os.listdir(ext_dir) if f.endswith('.dist-info')]

    azext_metadata = _get_azext_metadata(ext_dir)

    if not azext_metadata:
        raise ValueError('azext_metadata.json for Extension "{}" Metadata is missing'.format(ext_name))

    metadata.update(azext_metadata)

    for dist_info_dirname in dist_info_dirs:
        parsed_dist_info_dir = WHEEL_INFO_RE(dist_info_dirname)
        if parsed_dist_info_dir and parsed_dist_info_dir.groupdict().get('name') == ext_name.replace('-', '_'):
            whl_metadata_filepath = os.path.join(ext_dir, dist_info_dirname, WHL_METADATA_FILENAME)
            if os.path.isfile(whl_metadata_filepath):
                with open(whl_metadata_filepath) as f:
                    metadata.update(json.load(f))
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
