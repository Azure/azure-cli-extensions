# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=protected-access,duplicate-code

"""
This custom code inherits the auto-generated code for BMM run command and adds:
 - retrieval of custom properties returned on the success using CustomActionProperties class.
"""
from azext_networkcloud.aaz.latest.networkcloud.baremetalmachine import (
    RunCommand as _RunCommand,
)
from azext_networkcloud.operations.custom_properties import CustomActionProperties
from azext_networkcloud.operations.run_command_options import RunCommandOptions


class RunCommand(RunCommandOptions, _RunCommand):
    """Custom class for baremetalmachine run command"""

    # Handle custom properties returned by the actions
    # when run command is executed.
    # The properties object is defined as an interface in the Azure common spec.
    def _output(self, *args, **kwargs):
        return CustomActionProperties._output(self, args, kwargs)

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        return cls._add_output_directory_argument(
            cls, "BareMetalMachineRunCommandParameters", *args, **kwargs
        )
