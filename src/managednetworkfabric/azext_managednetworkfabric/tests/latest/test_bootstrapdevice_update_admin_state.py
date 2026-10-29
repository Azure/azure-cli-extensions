# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Bootstrap device state updates using a Swagger-derived mock recording."""

from azure.cli.testsdk import ScenarioTest

from .config import CONFIG


def call_scenario1(test):
    """Verify admin-state serialization and the final operation result."""
    step_update_admin_state(
        test,
        checks=[
            test.check("status", "Succeeded"),
            test.check("percentComplete", 100),
        ],
    )
    test.assertTrue(test.cassette.all_played)


def step_update_admin_state(test, checks=None):
    """Update the configured bootstrap device's admin state."""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric bootstrapdevice update-admin-state "
        "--resource-name {name} --resource-group {rg} "
        "--state {state} --resource-ids {resourceIds}",
        checks=checks,
    )


class GA_BootstrapDeviceUpdateAdminStateScenarioTest1(ScenarioTest):
    """Bootstrap device update-admin-state scenario."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("BOOTSTRAP_DEVICE", "name"),
                "rg": CONFIG.get("BOOTSTRAP_DEVICE", "resource_group"),
                "state": CONFIG.get("BOOTSTRAP_DEVICE", "state_enable"),
                "resourceIds": CONFIG.get("BOOTSTRAP_DEVICE", "resource_ids"),
            }
        )
        self.vcr.match_on = (*self.vcr.match_on, "body")

    def test_GA_bootstrapdevice_update_admin_state_scenario1(self):
        """Replay the bootstrap device admin state update mock recording."""
        call_scenario1(self)
