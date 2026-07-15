#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Idempotent extension release pipeline.

This script implements a race-condition-safe release flow for Azure CLI
extensions.  The key invariant is:

    The blob in storage is IMMUTABLE and is the single source of truth.
    The SHA-256 is always computed from that blob.
    index.json must match storage — if it doesn't, we fix index.json.

Steps:

  Step 1 — Upload (no overwrite):
      Upload the wheel to Azure Blob Storage *without* overwriting.
        * Upload succeeds        -> the local wheel IS the authoritative copy.
        * Upload fails (exists)  -> download the existing blob; use that.
      Either way, the SHA-256 is computed from the file that actually lives
      in storage — never from a local rebuild.

  Step 2 — Build index.json:
      Update the local ``src/index.json`` with the authoritative SHA-256,
      download URL, filename and metadata extracted from the wheel.
      Compare with the original file to determine if a commit is needed.

Usage::

    python idempotent_release.py \\
        --wheel-path ./dist/my_ext-1.0.0-py3-none-any.whl \\
        --storage-account azcliprod \\
        --storage-container cli-extensions \\
        [--blob-prefix edge] \\
        [--github-repo Azure/azure-cli-extensions] \\
        [--github-branch main]

Exit codes::

    0  — success (COMMIT_NEEDED or ALREADY_UP_TO_DATE)
    2  — unexpected error
"""

from __future__ import print_function

import argparse
import json
import logging
import os
import re
import sys
import tempfile

# Ensure this script can import sibling modules when run from any cwd.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from util import (  # noqa: E402
    download_blob,
    fetch_github_index,
    get_blob_url,
    get_ext_metadata,
    get_sha256sum,
    upload_wheel_no_overwrite,
)

logger = logging.getLogger(__name__)

NAME_REGEX = r'^(.*?)-\d+\.\d+\.\d+'

# -- status constants ---------------------------------------------------------
COMMIT_NEEDED = 'COMMIT_NEEDED'
ALREADY_UP_TO_DATE = 'ALREADY_UP_TO_DATE'
NEW_EXTENSION = 'NEW_EXTENSION'


# =============================================================================
# Step 1 — Upload
# =============================================================================

def step_upload(whl_path, storage_account, storage_container, blob_prefix):
    """Upload the wheel without overwriting. Return (authoritative_whl_path, blob_url).

    If the blob already exists the existing copy is downloaded to a temp
    directory so the caller always gets the *authoritative* wheel — the one
    that is actually in storage.
    """
    whl_file = os.path.basename(whl_path)
    blob_name = '{}/{}'.format(blob_prefix, whl_file) if blob_prefix else whl_file

    blob_url = upload_wheel_no_overwrite(
        whl_path, storage_account, storage_container, blob_prefix)

    if blob_url is not None:
        # Upload succeeded — the local file IS the authoritative copy.
        print("[Step 1] Upload succeeded: {}".format(blob_url))
        return whl_path, blob_url

    # Blob already existed — download the authoritative copy.
    print("[Step 1] Blob already exists. Downloading authoritative copy...")
    tmp_dir = tempfile.mkdtemp()
    dest = os.path.join(tmp_dir, whl_file)
    download_blob(storage_account, storage_container, blob_name, dest)
    blob_url = get_blob_url(storage_account, storage_container, blob_name)
    print("[Step 1] Using existing blob: {}".format(blob_url))
    return dest, blob_url


# =============================================================================
# Step 2 — Build index.json and determine if commit is needed
# =============================================================================

def step_build_index(authoritative_whl, blob_url, github_repo='Azure/azure-cli-extensions',
                     github_branch='main'):
    """Update index.json from the authoritative wheel.

    Compares the file before and after to determine if a commit is needed.

    Returns:
        tuple: (extension_name, computed_hash, decision)
            decision is COMMIT_NEEDED or ALREADY_UP_TO_DATE
    """
    whl_filename = os.path.basename(blob_url)

    # Parse extension name from the wheel filename.
    match = re.match(NAME_REGEX, whl_filename)
    if not match:
        raise ValueError('Unable to parse extension name from {}'.format(whl_filename))
    extension_name = match.group(1).replace('_', '-')

    computed_hash = get_sha256sum(authoritative_whl)
    print("[Step 2] Computed sha256Digest: {}".format(computed_hash))

    # Check the remote GitHub index.json to see if it already has the correct
    # SHA-256 for this extension. This handles the case where a concurrent
    # pipeline already committed the update — we skip the local update entirely,
    # avoiding a git conflict during the commit step.
    try:
        github_token = os.environ.get('GITHUB_TOKEN')
        remote_index = fetch_github_index(github_repo, github_branch, github_token)
        remote_entries = remote_index.get('extensions', {}).get(extension_name, [])
        remote_sha = remote_entries[0].get('sha256Digest') if remote_entries else None
        if remote_sha == computed_hash:
            print("[Step 2] Remote GitHub index.json already has correct SHA-256 "
                  "for '{}' -> ALREADY_UP_TO_DATE".format(extension_name))
            return extension_name, computed_hash, ALREADY_UP_TO_DATE
        if remote_sha:
            print("[Step 2] Remote SHA '{}' differs from computed '{}'".format(
                remote_sha, computed_hash))
        else:
            print("[Step 2] Extension '{}' not found in remote index (new or missing)".format(
                extension_name))
    except Exception as exc:
        # Non-fatal: if we can't reach GitHub, fall through to the local check.
        print("[Step 2] WARNING: Could not check remote index.json: {}".format(exc))

    # Extract metadata from the wheel.
    extensions_dir = tempfile.mkdtemp()
    ext_dir = tempfile.mkdtemp(dir=extensions_dir)
    metadata = get_ext_metadata(ext_dir, authoritative_whl, extension_name)

    # Read current local index.json.
    index_path = os.path.join('src', 'index.json')
    with open(index_path, 'r') as f:
        original_content = f.read()
    curr_index = json.loads(original_content)

    # If this is a brand-new extension (first release), signal the caller
    # to use azdev extension update-index — the proven tool for creating
    # new index entries with the correct structure.
    if extension_name not in curr_index.get('extensions', {}):
        print("[Step 2] Extension '{}' is new — needs azdev extension update-index".format(
            extension_name))
        return extension_name, computed_hash, NEW_EXTENSION

    # Check if the SHA-256 already matches — if so, no update needed.
    entry = curr_index['extensions'][extension_name]
    existing_sha = entry[0].get('sha256Digest')
    if existing_sha == computed_hash:
        print("[Step 2] index.json already has correct SHA-256 for '{}' -> ALREADY_UP_TO_DATE".format(
            extension_name))
        return extension_name, computed_hash, ALREADY_UP_TO_DATE

    # Update the entry.
    print("[Step 2] Updating index.json: existing SHA '{}' -> '{}'".format(
        existing_sha, computed_hash))
    entry[0]['downloadUrl'] = blob_url
    entry[0]['sha256Digest'] = computed_hash
    entry[0]['filename'] = whl_filename
    entry[0]['metadata'] = metadata

    curr_index['extensions'][extension_name] = entry
    with open(index_path, 'w') as f:
        f.write(json.dumps(curr_index, indent=4, sort_keys=True))

    print("[Step 2] Updated local index.json for '{}' -> COMMIT_NEEDED".format(extension_name))
    return extension_name, computed_hash, COMMIT_NEEDED


# =============================================================================
# Main
# =============================================================================

def parse_args(argv=None):
    p = argparse.ArgumentParser(
        description='Idempotent extension release: upload, index, commit-decision.')
    p.add_argument('--wheel-path', required=True,
                   help='Local path to the built .whl file')
    p.add_argument('--storage-account', required=True,
                   help='Azure Storage account name')
    p.add_argument('--storage-container', required=True,
                   help='Azure Storage container name')
    p.add_argument('--blob-prefix', default=None,
                   help='Optional blob name prefix (e.g. "edge")')
    p.add_argument('--github-repo', default='Azure/azure-cli-extensions',
                   help='GitHub repo in owner/repo format (default: Azure/azure-cli-extensions)')
    p.add_argument('--github-branch', default='main',
                   help='Branch to check remote index.json from (default: main)')
    return p.parse_args(argv)


def main(argv=None):
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    args = parse_args(argv)

    if not os.path.isfile(args.wheel_path):
        print("ERROR: Wheel file not found: {}".format(args.wheel_path), file=sys.stderr)
        return 2

    try:
        # Step 1 — Upload (never overwrite)
        authoritative_whl, blob_url = step_upload(
            args.wheel_path,
            args.storage_account,
            args.storage_container,
            args.blob_prefix,
        )

        # Step 2 — Build index.json from the authoritative wheel
        extension_name, computed_hash, decision = step_build_index(
            authoritative_whl, blob_url,
            github_repo=args.github_repo,
            github_branch=args.github_branch,
        )

        print("\n=== RESULT: {} ===".format(decision))
        return 0

    except Exception as exc:
        print("ERROR: {}".format(exc), file=sys.stderr)
        logger.exception("Unexpected error")
        return 2


if __name__ == '__main__':
    sys.exit(main())
