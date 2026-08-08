# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure.cli.testsdk import ResourceGroupPreparer, ScenarioTest
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

TEST_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))


class ManagedopsScenario(ScenarioTest):
    """Scenario tests for the `az managedops` extension.

    ManagedOps is a subscription-scoped singleton resource whose name is
    fixed to ``default`` (enforced by the AAZ ``pattern=default`` on the
    name argument), so there can only be one instance per subscription at
    a time. To stay safe under ``pytest-xdist`` (``azdev test --live``
    runs with parallel workers), this file exposes a single lifecycle test
    that owns the singleton for its entire run.

    Note on LRO handling:
        The RP finalizes ``properties.provisioningState`` on the resource
        *before* the ``Azure-AsyncOperation`` tracker reaches a terminal
        state, so a ``--no-wait`` + ``managedops wait --created`` pattern
        can return prematurely and cause the next ``PUT`` to fail with
        409 ``InvalidResourceOperation``. Each mutating command is therefore
        issued *without* ``--no-wait`` so the CLI's built-in LRO poller
        (which follows the async-operation URL) drives completion.
    """

    @AllowLargeResponse(size_kb=10240)
    @ResourceGroupPreparer(name_prefix="cli_test_managedops_", location="eastus")
    def test_managedops_lifecycle(self, resource_group):
        """End-to-end lifecycle for the ManagedOps singleton.

        Steps:
            1. Provision Azure Monitor Workspace, Log Analytics Workspace and
               a User-Assigned Managed Identity in the preparer's resource group.
            2. ``managedops create`` (LRO waits for async-operation tracker).
            3. ``managedops show`` with JMESPath assertions.
            4. A single ``managedops update`` flipping both defender toggles.
            5. ``managedops delete --yes``.
            6. ``managedops wait --deleted`` to confirm the resource is gone.
        """

        self.kwargs.update({
            "rg": resource_group,
            "loc": "eastus",
            "managedops_name": "default",
            "amw_name": self.create_random_name(prefix="cliamw", length=20),
            "law_name": self.create_random_name(prefix="clilaw", length=20),
            "mi_name": self.create_random_name(prefix="climi", length=20),
        })

        # --- Provision dependent resources ----------------------------------

        amw = self.cmd(
            "az monitor account create -g {rg} -n {amw_name} -l {loc}"
        ).get_output_in_json()
        self.kwargs["amw_id"] = amw["id"]

        law = self.cmd(
            "az monitor log-analytics workspace create -g {rg} -n {law_name} -l {loc}"
        ).get_output_in_json()
        self.kwargs["law_id"] = law["id"]

        mi = self.cmd(
            "az identity create -g {rg} -n {mi_name} -l {loc}"
        ).get_output_in_json()
        self.kwargs["mi_id"] = mi["id"]

        # --- Create --------------------------------------------------------
        # No --no-wait: the CLI's built-in LRO poller follows the
        # Azure-AsyncOperation header, so the next PUT will not race the
        # tail of this operation.

        self.cmd(
            "az managedops managedops create "
            "--managed-ops-name {managedops_name} "
            '--sku "{{name:ManagedOps,tier:Essential}}" '
            "--azure-monitor-workspace-id {amw_id} "
            "--log-analytics-workspace-id {law_id} "
            "--user-assigned-managed-identity-id {mi_id} "
            "--defender-cspm Disable "
            "--defender-for-servers Disable",
            checks=[
                self.check("name", "{managedops_name}"),
                self.check("properties.provisioningState", "Succeeded"),
                self.check("properties.sku.name", "ManagedOps"),
                self.check("properties.sku.tier", "Essential"),
                self.check(
                    "properties.desiredConfiguration.azureMonitorInsights.azureMonitorWorkspaceId",
                    "{amw_id}",
                ),
                self.check(
                    "properties.desiredConfiguration.changeTrackingAndInventory.logAnalyticsWorkspaceId",
                    "{law_id}",
                ),
                self.check(
                    "properties.desiredConfiguration.userAssignedManagedIdentityId",
                    "{mi_id}",
                ),
                self.check("properties.desiredConfiguration.defenderCspm", "Disable"),
                self.check("properties.desiredConfiguration.defenderForServers", "Disable"),
            ],
        )

        # --- Show -----------------------------------------------------------

        self.cmd(
            "az managedops managedops show --managed-ops-name {managedops_name}",
            checks=[
                self.check("name", "{managedops_name}"),
                self.check("properties.provisioningState", "Succeeded"),
                self.exists("properties.services"),
            ],
        )

        # --- Update --------------------------------------------------------
        # Flip both defender toggles in a single LRO to keep the test short
        # and to avoid back-to-back PUTs on the same singleton.

        self.cmd(
            "az managedops managedops update "
            "--managed-ops-name {managedops_name} "
            "--defender-cspm Enable "
            "--defender-for-servers Enable",
            checks=[
                self.check("properties.provisioningState", "Succeeded"),
                self.check("properties.desiredConfiguration.defenderCspm", "Enable"),
                self.check("properties.desiredConfiguration.defenderForServers", "Enable"),
            ],
        )

        # --- Delete + verify ------------------------------------------------

        self.cmd(
            "az managedops managedops delete "
            "--managed-ops-name {managedops_name} --yes"
        )

        self.cmd(
            "az managedops managedops show --managed-ops-name {managedops_name}",
            expect_failure=True,
        )


if __name__ == "__main__":
    unittest.main()
