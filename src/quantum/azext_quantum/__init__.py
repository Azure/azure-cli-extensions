# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

import azext_quantum._help  # pylint: disable=unused-import


# This is the version reported by the CLI to the service when submitting requests.
# This should be in sync with the extension version in 'setup.py', unless we need to
# submit using a different version.
CLI_REPORTED_VERSION = "0.7.0"


class QuantumCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        super(QuantumCommandsLoader, self).__init__(cli_ctx=cli_ctx)
        
        # Once each day, see if the user is running the latest version of the quantum extension.
        # If not, recommend upgrading. 
        from datetime import datetime
        from azure.cli.core.extension.operations import list_versions
        from azure.cli.core.util import ConfiguredDefaultSetter
        from .operations.workspace import _show_tip

        today = str(datetime.today()).split(' ')[0]
        try:
            with ConfiguredDefaultSetter(cli_ctx.config, False):
                date_checked = cli_ctx.config.get('quantum', 'version_check_date', None)

            if date_checked is None or date_checked != today:
                with ConfiguredDefaultSetter(cli_ctx.config, False):
                    cli_ctx.config.set_value('quantum', 'version_check_date', today)

                available_versions = list_versions("quantum")
                latest_version_dict = available_versions[len(available_versions) - 1]
                latest_version = latest_version_dict['version'].split(' ')[0]
                
                if CLI_REPORTED_VERSION != latest_version:
                    _show_tip(f"\nVersion {CLI_REPORTED_VERSION} of the quantum extension is installed locally, but Version {latest_version} is now available.\nYou can use ‘az extension update -n quantum’ to upgrade.\n")
        except:
            # If an error occurs, we ignore it!
            return

    def load_command_table(self, args):
        from azext_quantum.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_quantum._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = QuantumCommandsLoader
