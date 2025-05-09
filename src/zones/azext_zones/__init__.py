# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import importlib
from pathlib import Path
from azure.cli.core import AzCommandsLoader
from azext_zones._help import helps  # pylint: disable=unused-import

# Import all the resource type validator modules dynamically:
validators_dir = Path(__file__).parent / "resource_type_validators"
for file in validators_dir.glob("*.py"):
    if file.name != "__init__.py":
        module_name = f".resource_type_validators.{file.stem}"
        importlib.import_module(module_name, package=__package__)


class ZonesCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azext_zones._client_factory import cf_zones
        zones_custom = CliCommandType(
            operations_tmpl='azext_zones.custom#{}',
            client_factory=cf_zones)
        super(ZonesCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                  custom_command_type=zones_custom)

    def load_command_table(self, args):
        from azext_zones.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_zones._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = ZonesCommandsLoader
