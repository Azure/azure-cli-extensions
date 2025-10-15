# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=protected-access,duplicate-code

"""
This code inherits the auto-generated code for internetgateway list command.
"""
from azext_managednetworkfabric.aaz.latest.networkfabric.internetgateway import (
    List as _ListCommand,
)
from azext_managednetworkfabric.operations.show_list_options import ShowListOptions
from azext_managednetworkfabric.operations.reconcile_flatten import (
    ReconcileFlatten,
)


class ListCommand(ShowListOptions, _ListCommand):
    """Custom class for networkfabric internetgateway list"""

    # Handle custom properties returned by the actions
    # when run read command is executed.
    # The properties object is defined as an interface in the Azure common spec.
    def _output(self, *args, **kwargs):
        return ReconcileFlatten._output_internet_gateway_list(self, args, kwargs)
