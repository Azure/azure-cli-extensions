# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import sys
from azure.cli.core import get_default_cli
from azure.cli.core._session import Session
from azure.cli.core.commands import _load_extension_command_loader
from azure.cli.core.extension import get_extension_modname, get_extension_path


def merge(data, key, value):
    if isinstance(value, str):
        if key in data:
            raise Exception(f"{key} already in index")
        data[key] = value
    else:
        data.setdefault(key, {})
        for k, v in value.items():
            merge(data[key], k, v)


def main():
    az_cli = get_default_cli()
    ext_name = sys.argv[1]
    print(f"Processing {ext_name}")

    ext_dir = get_extension_path(ext_name)
    ext_mod = get_extension_modname(ext_name, ext_dir=ext_dir)

    invoker = az_cli.invocation_cls(cli_ctx=az_cli, commands_loader_cls=az_cli.commands_loader_cls,
                                    parser_cls=az_cli.parser_cls, help_cls=az_cli.help_cls)
    az_cli.invocation = invoker

    sys.path.append(ext_dir)
    extension_command_table, _ = _load_extension_command_loader(invoker.commands_loader,
                                                                "", ext_mod)

    EXT_CMD_INDEX = Session()
    EXT_CMD_INDEX.load(os.path.expanduser(os.path.join('~', '.azure', 'extCmdIndexToUpload.json')))
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
        merge(EXT_CMD_INDEX.data, k, v)
    EXT_CMD_INDEX.save_with_retry()

if __name__ == '__main__':
    main()
