# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import importlib
from pathlib import Path
from azure.cli.core import AzCommandsLoader
from azext_zones._help import helps  # pylint: disable=unused-import
from knack.log import get_logger


class ZonesCommandsLoader(AzCommandsLoader):
    _logger = get_logger(__name__)

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azext_zones._client_factory import cf_zones
        zones_custom = CliCommandType(
            operations_tmpl='azext_zones.custom#{}',
            client_factory=cf_zones)
        self.load_validators()
        super(ZonesCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                  custom_command_type=zones_custom)

    def load_command_table(self, args):
        from azext_zones.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_zones._params import load_arguments
        load_arguments(self, command)

    def load_validators(self):
        # Import all the resource type validator modules dynamically:
        validators_dir = Path(__file__).parent / "resource_type_validators"
        self._logger.debug("Starting resource type validator module import from %s", validators_dir)

        try:
            if validators_dir.exists():
                for file in validators_dir.glob("*.py"):
                    if file.name != "__init__.py":
                        try:
                            self._logger.debug("Importing resource type validator module: %s", file.name)
                            module_name = f".resource_type_validators.{file.stem}"
                            importlib.import_module(module_name, package=__package__)
                        except ImportError as e:
                            self._logger.warning("Failed to import module %s: %s", module_name, str(e))
            else:
                self._logger.error("Resource type validators directory not found: %s", validators_dir)

        except Exception as e:  # pylint: disable=broad-except
            self._logger.warning("Error scanning for resource type validator modules: %s", str(e))


COMMAND_LOADER_CLS = ZonesCommandsLoader
