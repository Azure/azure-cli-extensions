# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import filecmp
import os
import sys
from azure.cli.core import get_default_cli
from azure.cli.core._session import Session
from azure.cli.core.commands import _load_extension_command_loader
from azure.cli.core.extension import get_extension_modname, get_extension_path
from azure.storage.blob import BlockBlobService
from sync_extensions import download_file

STORAGE_ACCOUNT_KEY = os.getenv('AZURE_EXTENSION_CMD_TREE_STORAGE_ACCOUNT_KEY')
STORAGE_ACCOUNT = os.getenv('AZURE_EXTENSION_CMD_TREE_STORAGE_ACCOUNT')
STORAGE_CONTAINER = os.getenv('AZURE_EXTENSION_CMD_TREE_STORAGE_CONTAINER')

az_cli = get_default_cli()
file_name = 'extCmdTreeToUpload.json'


def merge(data, key, value):
    if isinstance(value, str):
        if key in data:
            raise Exception(f"Key: {key} already exists. 2 extensions cannot have the same command!")
        data[key] = value
    else:
        data.setdefault(key, {})
        for k, v in value.items():
            merge(data[key], k, v)


def update_cmd_tree(ext_name):
    print(f"Processing {ext_name}")

    ext_dir = get_extension_path(ext_name)
    ext_mod = get_extension_modname(ext_name, ext_dir=ext_dir)

    invoker = az_cli.invocation_cls(cli_ctx=az_cli, commands_loader_cls=az_cli.commands_loader_cls,
                                    parser_cls=az_cli.parser_cls, help_cls=az_cli.help_cls)
    az_cli.invocation = invoker

    sys.path.append(ext_dir)
    extension_command_table, _ = _load_extension_command_loader(invoker.commands_loader,
                                                                "", ext_mod)

    EXT_CMD_TREE_TO_UPLOAD = Session()
    EXT_CMD_TREE_TO_UPLOAD.load(os.path.expanduser(os.path.join('~', '.azure', file_name)))
    root = {}
    for cmd_name, _ in extension_command_table.items():
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
    downloaded_file_name = 'extCmdTreeDownloaded.json'
    file_path = os.path.expanduser(os.path.join('~', '.azure', file_name))

    client = BlockBlobService(account_name=STORAGE_ACCOUNT, account_key=STORAGE_ACCOUNT_KEY)
    client.create_blob_from_path(container_name=STORAGE_CONTAINER, blob_name=blob_file_name,
                                 file_path=file_path)

    url = client.make_blob_url(container_name=STORAGE_CONTAINER, blob_name=blob_file_name)

    download_file_path = os.path.expanduser(os.path.join('~', '.azure', downloaded_file_name))
    download_file(url, download_file_path)
    if filecmp.cmp(file_path, download_file_path):
        print("extensionCommandTree.json uploaded successfully. URL: {}".format(url))
    else:
        raise Exception("Failed to update extensionCommandTree.json in the storage account")


if __name__ == '__main__':
    for ext in sys.argv[1:]:
        update_cmd_tree(ext)
    upload_cmd_tree()
