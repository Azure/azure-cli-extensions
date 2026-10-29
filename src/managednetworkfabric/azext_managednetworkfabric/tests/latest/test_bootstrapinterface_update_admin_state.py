# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Bootstrap interface state updates using a Swagger-derived mock recording."""

from azure.cli.testsdk import ScenarioTest

from .config import CONFIG


def call_scenario1(test):
    """Verify interface admin state serialization, polling, and the response shape."""
    step_update_admin_state(
        test,
        checks=[test.check("configurationState", "Succeeded")],
    )
    test.assertTrue(test.cassette.all_played)


def step_update_admin_state(test, checks=None):
    """Update the configured bootstrap interface's admin state."""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric bootstrapinterface update-admin-state "
        "--resource-name {name} --resource-group {rg} "
        "--bootstrap-device {bootstrapDeviceName} "
        "--state {state} --resource-ids {resourceIds}",
        checks=checks,
    )


class GA_BootstrapInterfaceUpdateAdminStateScenarioTest1(ScenarioTest):
    """Bootstrap interface update-admin-state scenario."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("BOOTSTRAP_INTERFACE", "name"),
                "rg": CONFIG.get("BOOTSTRAP_INTERFACE", "resource_group"),
                "bootstrapDeviceName": CONFIG.get(
                    "BOOTSTRAP_INTERFACE", "bootstrap_device_name"
                ),
                "state": CONFIG.get("BOOTSTRAP_INTERFACE", "state_enable"),
                "resourceIds": CONFIG.get("BOOTSTRAP_INTERFACE", "resource_ids"),
            }
        )
        self.vcr.match_on = (*self.vcr.match_on, "body")

    def test_GA_bootstrapinterface_update_admin_state_scenario1(self):
        """Replay the bootstrap interface admin state update mock recording."""
        call_scenario1(self)
