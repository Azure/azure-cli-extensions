# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=protected-access,duplicate-code

"""
This code inherits the auto-generated code for BMM run data extract restricted command, and adds retrieval
of custom properties. It also processes the output directory if given and downloads
the results of the command.
"""

from azext_networkcloud.aaz.latest.networkcloud.baremetalmachine import (
    RunDataExtractsRestricted as _RunDataExtractsRestricted,
)
from azext_networkcloud.operations.custom_properties import CustomActionProperties
from azext_networkcloud.operations.run_command_options import RunCommandOptions


class RunDataExtractsRestricted(RunCommandOptions, _RunDataExtractsRestricted):
    """Custom class for baremetalmachine run data extracts restricted command"""

    # Handle custom properties returned by the actions
    # when run data extracts restricted command is executed.
    # The properties object is defined as an interface in the Azure common spec.
    def _output(self, *args, **kwargs):
        return CustomActionProperties._output(self, args, kwargs)

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        return cls._add_output_directory_argument(
            cls, "BareMetalMachineRunDataExtractsRestrictedParameters", *args, **kwargs
        )
