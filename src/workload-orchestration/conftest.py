# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Root conftest - install mock azure.cli modules before package discovery."""

import logging
import sys
import types

# Create mock azure.cli modules so the extension __init__.py can be imported
# without a full azure-cli installation.
_azure = types.ModuleType("azure")
_azure.__path__ = []
_azure_cli = types.ModuleType("azure.cli")
_azure_cli.__path__ = []
_azure_cli_core = types.ModuleType("azure.cli.core")
_azure_cli_core.__path__ = []
_azure_cli_core.AzCommandsLoader = type("AzCommandsLoader", (), {
    "__init__": lambda self, *a, **kw: None,
    "command_table": {},
    "load_command_table": lambda self, args: {},
    "load_arguments": lambda self, command: None,
})
_azure_cli_commands = types.ModuleType("azure.cli.core.commands")
_azure_cli_commands.__path__ = []
_azure_cli_commands.CliCommandType = type("CliCommandType", (), {"__init__": lambda self, **kw: None})
_azure_cli_aaz = types.ModuleType("azure.cli.core.aaz")
_azure_cli_aaz.__path__ = []
_azure_cli_aaz.load_aaz_command_table = lambda **kw: None
# Mock AAZ decorators and base classes used by __cmd_group.py files
_azure_cli_aaz.register_command_group = lambda *a, **kw: (lambda cls: cls)
_azure_cli_aaz.register_command = lambda *a, **kw: (lambda cls: cls)
_azure_cli_aaz.AAZCommandGroup = type("AAZCommandGroup", (), {})
_azure_cli_aaz.AAZCommand = type("AAZCommand", (), {
    "__init__": lambda self, *a, **kw: None,
})
# Expose as module globals for `from azure.cli.core.aaz import *`
_azure_cli_aaz.__all__ = [
    "register_command_group", "register_command", "AAZCommandGroup",
    "AAZCommand", "load_aaz_command_table",
]
_azure_cli_params = types.ModuleType("azure.cli.core.commands.parameters")
_azure_cli_params.get_enum_type = lambda x: x
_azure_cli_azclierror = types.ModuleType("azure.cli.core.azclierror")
_azure_cli_azclierror.CLIError = Exception
_knack = types.ModuleType("knack")
_knack.__path__ = []
_knack_log = types.ModuleType("knack.log")
_knack_log.get_logger = logging.getLogger
_knack_help = types.ModuleType("knack.help_files")
_knack_help.helps = {}

for mod_name, mod in [
    ("azure", _azure),
    ("azure.cli", _azure_cli),
    ("azure.cli.core", _azure_cli_core),
    ("azure.cli.core.commands", _azure_cli_commands),
    ("azure.cli.core.aaz", _azure_cli_aaz),
    ("azure.cli.core.commands.parameters", _azure_cli_params),
    ("azure.cli.core.azclierror", _azure_cli_azclierror),
    ("knack", _knack),
    ("knack.log", _knack_log),
    ("knack.help_files", _knack_help),
]:
    # Install mocks — use setdefault to not break if real modules exist
    sys.modules.setdefault(mod_name, mod)
