# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=protected-access,duplicate-code

"""
This code inherits the auto-generated code for Device run read command, and adds retrieval of
custom properties.
"""
from azext_managednetworkfabric.aaz.latest.networkfabric.device import (
    RunRo as _RunReadCommand,
)
from azext_managednetworkfabric.operations.run_command_options import RunCommandOptions
from azext_managednetworkfabric.operations.custom_properties import (
    CustomActionProperties,
)


class RunReadCommand(RunCommandOptions, _RunReadCommand):
    """Custom class for networkfabric device run-ro"""

    # Handle custom properties returned by the actions
    # when run read command is executed.
    # The properties object is defined as an interface in the Azure common spec.
    def _output(self, *args, **kwargs):
        return CustomActionProperties._output(self, args, kwargs)
