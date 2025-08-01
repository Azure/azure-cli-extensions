# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_fleet._client_factory import (
    cf_fleets,
    cf_fleet_members,
    cf_update_runs,
    cf_fleet_update_strategies,
    cf_auto_upgrade_profiles,
    cf_auto_upgrade_profile_operations,
    cf_gates
)


def load_command_table(self, _):

    fleets_sdk = CliCommandType(
        operations_tmpl="azext_fleet.vendored_sdks.operations._fleets_operations#FleetsOperations.{}",
        operation_group="fleets",
        client_factory=cf_fleets
    )

    fleet_members_sdk = CliCommandType(
        operations_tmpl="azext_fleet.vendored_sdks.operations._fleet_members_operations#FleetMembersOperations.{}",
        operation_group="fleet_members",
        client_factory=cf_fleet_members
    )

    update_runs_sdk = CliCommandType(
        operations_tmpl="azext_fleet.vendored_sdks.operations._update_runs_operations#UpdateRunsOperations.{}",
        operation_group="update_runs",
        client_factory=cf_update_runs
    )

    fleet_update_strategy_sdk = CliCommandType(
        operations_tmpl="azext_fleet.vendored_sdks.operations._fleet_update_strategies_operations#FleetUpdateStrategiesOperations.{}",
        operation_group="fleet_update_strategies",
        client_factory=cf_fleet_update_strategies
    )

    auto_upgrade_profiles_sdk = CliCommandType(
        operations_tmpl="azext_fleet.vendored_sdks.operations._auto_upgrade_profiles_operations#AutoUpgradeProfilesOperations.{}",
        operation_group="auto_upgrade_profiles",
        client_factory=cf_auto_upgrade_profiles
    )

    auto_upgrade_profile_operations_sdk = CliCommandType(
        operations_tmpl="azext_fleet.vendored_sdks.operations._auto_upgrade_profile_operations_operations#AutoUpgradeProfileOperationsOperations.{}",
        operation_group="auto_upgrade_profile_operations",
        client_factory=cf_auto_upgrade_profile_operations
    )

    gates_sdk = CliCommandType(
        operations_tmpl="azext_fleet.vendored_sdks.operations._gates_operations#GatesOperations.{}",
        operation_group="gates",
        client_factory=cf_gates
    )

    # fleets command group
    with self.command_group("fleet", fleets_sdk, client_factory=cf_fleets) as g:
        g.custom_command("create", "create_fleet", supports_no_wait=True)
        g.custom_command("update", "update_fleet", supports_no_wait=True)
        g.custom_show_command("show", "show_fleet")
        g.custom_command("list", "list_fleet")
        g.custom_command("delete", "delete_fleet", supports_no_wait=True, confirmation=True)
        g.custom_command("get-credentials", "get_credentials")
        g.custom_command("reconcile", "reconcile_fleet", supports_no_wait=True)
        g.wait_command("wait")

    # fleet members command group
    with self.command_group("fleet member", fleet_members_sdk, client_factory=cf_fleet_members) as g:
        g.custom_command("create", "create_fleet_member", supports_no_wait=True)
        g.custom_command("update", "update_fleet_member")
        g.custom_command("delete", "delete_fleet_member", supports_no_wait=True, confirmation=True)
        g.custom_command("list", "list_fleet_member")
        g.custom_show_command("show", "show_fleet_member")
        g.custom_command("reconcile", "reconcile_fleet_member", supports_no_wait=True)
        g.wait_command("wait")

    # fleet update runs command group
    with self.command_group("fleet updaterun", update_runs_sdk, client_factory=cf_update_runs) as g:
        g.custom_command("create", "create_update_run", supports_no_wait=True)
        g.custom_show_command("show", "show_update_run")
        g.custom_command("list", "list_update_run")
        g.custom_command("delete", "delete_update_run", supports_no_wait=True, confirmation=True)
        g.custom_command("start", "start_update_run", supports_no_wait=True)
        g.custom_command("stop", "stop_update_run", supports_no_wait=True)
        g.custom_command("skip", "skip_update_run", supports_no_wait=True)
        g.wait_command("wait")

    # fleet update strategies command group
    with self.command_group("fleet updatestrategy", fleet_update_strategy_sdk, client_factory=cf_fleet_update_strategies) as g:
        g.custom_command("create", "create_fleet_update_strategy", supports_no_wait=True)
        g.custom_show_command("show", "show_fleet_update_strategy")
        g.custom_command("list", "list_fleet_update_strategies")
        g.custom_command("delete", "delete_fleet_update_strategy", supports_no_wait=True, confirmation=True)
        g.wait_command("wait")

    # auto upgrade profiles command group
    with self.command_group("fleet autoupgradeprofile", auto_upgrade_profiles_sdk, client_factory=cf_auto_upgrade_profiles) as g:
        g.custom_command("create", "create_auto_upgrade_profile", supports_no_wait=True)
        g.custom_show_command("show", "show_auto_upgrade_profile")
        g.custom_command("list", "list_auto_upgrade_profiles")
        g.custom_command("delete", "delete_auto_upgrade_profile", supports_no_wait=True, confirmation=True)
        g.wait_command("wait")

    # auto upgrade profiles operation command group
    with self.command_group("fleet autoupgradeprofile", auto_upgrade_profile_operations_sdk, client_factory=cf_auto_upgrade_profile_operations) as g:
        g.custom_command("generate-update-run", "generate_update_run", supports_no_wait=True)

    # fleet gates command group
    with self.command_group("fleet gate", gates_sdk, client_factory=cf_gates) as g:
        g.custom_command("list", "list_gates_by_fleet")
        g.custom_show_command("show", "show_gate")
        g.custom_command("update", "update_gate")
        g.custom_command("approve", "approve_gate")
