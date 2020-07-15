from azure.cli.core import get_default_cli
az_cli = get_default_cli()

from azure.cli.core.commands import _load_extension_command_loader
import sys
ext_name = sys.argv[1]
print(f"Processing {ext_name}")
from azure.cli.core.extension import get_extension_modname, get_extension_path

ext_dir = get_extension_path(ext_name)
ext_mod = get_extension_modname(ext_name, ext_dir=ext_dir)

invoker = az_cli.invocation_cls(cli_ctx=az_cli, commands_loader_cls=az_cli.commands_loader_cls,
                                     parser_cls=az_cli.parser_cls, help_cls=az_cli.help_cls)
az_cli.invocation = invoker

sys.path.append(ext_dir)
extension_command_table, extension_group_table = _load_extension_command_loader(invoker.commands_loader, "", ext_mod)

from azure.cli.core._session import Session
EXT_CMD_INDEX = Session()
import os
EXT_CMD_INDEX.load(os.path.join(az_cli.config.config_dir, 'extCmdIndex.json'))
root = {}
for cmd_name, cmd in extension_command_table.items():
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

def merge(data, key, value):
    if isinstance(value, str):
        if key in data:
            raise Exception(f"{key} already in index")
        data[key] = value
    else:
        data.setdefault(key, {})
        for k, v in value.items():
            merge(data[key], k, v)

print(root)
for key, value in root.items():
    merge(EXT_CMD_INDEX.data, key, value)
EXT_CMD_INDEX.save_with_retry()
