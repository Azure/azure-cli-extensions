# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import filecmp
import json
import os
import sys
import subprocess

from azure.cli.core import get_default_cli
from azure.cli.core._session import Session
from azure.cli.core.commands import _load_extension_command_loader
from azure.cli.core.extension import get_extension_modname, get_extension_path
from sync_extensions import download_file
from util import run_az_cmd

STORAGE_ACCOUNT = os.getenv('AZURE_EXTENSION_CMD_TREE_STORAGE_ACCOUNT')
STORAGE_CONTAINER = os.getenv('AZURE_EXTENSION_CMD_TREE_STORAGE_CONTAINER')
BLOB_PREFIX = os.getenv('AZURE_EXTENSION_CMD_TREE_BLOB_PREFIX')

az_cli = get_default_cli()
file_name = 'extCmdTreeToUpload.json'


def execute_command(command):
    """Execute a shell command and return the output."""
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"Error: {result.stderr.strip()}"
    except Exception as e:
        return f"Exception: {str(e)}"


def get_package_version(package_name):
    """Get the current version of a Python package."""
    command = ["pip", "show", package_name]
    output = execute_command(command)
    if "Version:" in output:
        for line in output.splitlines():
            if line.startswith("Version:"):
                version = line.split(":")[1].strip()
                print(f"{package_name} current version: {version}")


def upgrade_package(package_name):
    """Upgrade a Python package to the latest version."""
    command = ["pip", "install", "--upgrade", package_name]
    print(f"{command}")
    return execute_command(command)


def merge(data, key, value):
    if isinstance(value, str):
        if key in data:
            raise Exception(f"Key: {key} already exists in {data[key]}. 2 extensions cannot have the same command!")
        data[key] = value
    else:
        data.setdefault(key, {})
        for k, v in value.items():
            merge(data[key], k, v)


def update_cmd_tree(ext_name):
    print(f"Processing {ext_name}")
    if ext_name == 'ml':
        get_package_version("azure-storage-blob")
        upgrade_package("azure-storage-blob")
        get_package_version("azure-storage-blob")
        get_package_version("rpds")
        upgrade_package("rpds")
        get_package_version("rpds")
        get_package_version("rpds-py")
        upgrade_package("rpds-py")
        get_package_version("rpds-py")

    ext_dir = get_extension_path(ext_name)
    ext_mod = get_extension_modname(ext_name, ext_dir=ext_dir)

    invoker = az_cli.invocation_cls(cli_ctx=az_cli, commands_loader_cls=az_cli.commands_loader_cls,
                                    parser_cls=az_cli.parser_cls, help_cls=az_cli.help_cls)
    az_cli.invocation = invoker

    sys.path.append(ext_dir)
    extension_command_table, _ = _load_extension_command_loader(invoker.commands_loader, None, ext_mod)

    EXT_CMD_TREE_TO_UPLOAD = Session(encoding='utf-8')
    EXT_CMD_TREE_TO_UPLOAD.load(os.path.expanduser(os.path.join('~', '.azure', file_name)))
    root = {}
    for cmd_name, ext_cmd in extension_command_table.items():
        try:
            # do not include hidden deprecated command
            if ext_cmd.deprecate_info.hide:
                print(f"Skip hidden deprecated command: {cmd_name}")
                continue
        except AttributeError:
            pass
        parts = cmd_name.split()
        parent = root
        for i, part in enumerate(parts):
            if part in parent:
                pass
            elif i == len(parts) - 1:
                parent[part] = ext_name
            else:
                parent[part] = {}
            parent = parent[part]
    print(root)
    for k, v in root.items():
        merge(EXT_CMD_TREE_TO_UPLOAD.data, k, v)
    EXT_CMD_TREE_TO_UPLOAD.save_with_retry()


def upload_cmd_tree():
    blob_file_name = 'extensionCommandTree.json'
    if BLOB_PREFIX:
        blob_file_name = f'{BLOB_PREFIX}/{blob_file_name}'
    downloaded_file_name = 'extCmdTreeDownloaded.json'
    file_path = os.path.expanduser(os.path.join('~', '.azure', file_name))

    cmd = ['az', 'storage', 'blob', 'upload', '--container-name', f'{STORAGE_CONTAINER}', '--account-name',
           f'{STORAGE_ACCOUNT}', '--name', f'{blob_file_name}', '--file', f'{file_path}', '--auth-mode', 'login',
           '--overwrite']
    message = f"Uploading '{blob_file_name}' to the storage"
    run_az_cmd(cmd, message=message, raise_error=True)

    cmd = ['az', 'storage', 'blob', 'url', '--container-name', f'{STORAGE_CONTAINER}', '--account-name',
           f'{STORAGE_ACCOUNT}', '--name', f'{blob_file_name}', '--auth-mode', 'login']
    message = f"Getting the URL for '{blob_file_name}'"
    result = run_az_cmd(cmd, message=message, raise_error=True)
    url = json.loads(result.stdout)

    download_file_path = os.path.expanduser(os.path.join('~', '.azure', downloaded_file_name))
    download_file(url, download_file_path)
    if filecmp.cmp(file_path, download_file_path):
        print("extensionCommandTree.json uploaded successfully. URL: {}".format(url))
    else:
        raise Exception("Failed to update extensionCommandTree.json in the storage account")


if __name__ == '__main__':
    for ext in sys.argv[1:]:
        update_cmd_tree(ext)
        print()
    upload_cmd_tree()
