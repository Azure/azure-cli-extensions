# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=protected-access,duplicate-code

"""
This code inherits the auto-generated code for Storage appliance run read command, and adds retrieval of
custom properties. It also processes the output directory if given and downloads the results
of the command.
"""
from azext_networkcloud.aaz.latest.networkcloud.storageappliance import (
    RunReadCommand as _RunReadCommand,
)
from azext_networkcloud.operations.custom_properties import CustomActionProperties
from azext_networkcloud.operations.run_command_options import RunCommandOptions


class RunReadCommand(RunCommandOptions, _RunReadCommand):
    """Custom class for storage appliance run read command"""

    # Handle custom properties returned by the actions
    # when run read command is executed.
    # The properties object is defined as an interface in the Azure common spec.
    def _output(self, *args, **kwargs):
        return CustomActionProperties._output(self, args, kwargs)

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        return cls._add_output_directory_argument(
            cls, "StorageApplianceRunReadCommandsParameters", *args, **kwargs
        )
