# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

from azure.cli.core.commands import CliCommandType
from ._client_factory import (
    reservation_mgmt_client_factory, reservation_order_mgmt_client_factory, base_mgmt_client_factory)
from ._exception_handler import reservations_exception_handler


def load_command_table(self, _):
    def reservations_type(*args, **kwargs):
        return CliCommandType(*args, exception_handler=reservations_exception_handler, **kwargs)
