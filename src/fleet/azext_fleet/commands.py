# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_fleet._client_factory import cf_fleets, cf_fleet_members


def load_command_table(self, _):

    fleets_sdk = CliCommandType(
        operations_tmpl="azext_fleet.vendored_sdks.operations._fleets_operations#FleetsOperations.{}",
        operation_group="fleets",
        client_factory=cf_fleets
    )

    fleet_members_sdk = CliCommandType(
        operations_tmpl="azext_fleet.vendored_sdks.operations._fleet_members_operations#FleetMembersOperations.{}",
        operation_group="fleets",
        client_factory=cf_fleets
    )

    # fleets command group
    with self.command_group("fleet", fleets_sdk, client_factory=cf_fleets) as g:
        g.custom_command("create", "create_fleet", supports_no_wait=True)
        g.custom_command("delete", "delete_fleet", supports_no_wait=True)
        g.custom_command("credentials list", "list_credentials")

    # fleet members command group
    with self.command_group("fleet member", fleet_members_sdk, client_factory=cf_fleet_members) as g:
        g.custom_command("join", "join_fleet_member", supports_no_wait=True)
        g.custom_command("remove", "remove_fleet_member", supports_no_wait=True)
        g.custom_command("list", "list_fleet_member")
