# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods

"""Bootstrap Interface update-administrative-state test scenario."""

from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

from .config import CONFIG


def step_update_administrative_state(test, checks=None):
    """Update the Bootstrap Interface administrative state."""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric bootstrapinterface update-admin-state "
        "--resource-name {name} --resource-group {rg} "
        "--bootstrap-device {bootstrapDeviceName} --state {state} "
        "--resource-ids {resourceIds}",
        checks=checks,
    )


class BootstrapInterfaceUpdateAdminStateScenarioTest(ScenarioTest):
    """Bootstrap Interface update-admin-state scenario test."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("BOOTSTRAP_INTERFACE", "name"),
                "rg": CONFIG.get("BOOTSTRAP_INTERFACE", "resource_group"),
                "bootstrapDeviceName": CONFIG.get(
                    "BOOTSTRAP_INTERFACE", "bootstrap_device_name"
                ),
                "state": CONFIG.get("BOOTSTRAP_INTERFACE", "state"),
                "resourceIds": CONFIG.get("BOOTSTRAP_INTERFACE", "resource_ids"),
            }
        )

    @AllowLargeResponse()
    def test_bootstrapinterface_update_admin_state(self):
        """Test the Bootstrap Interface update-admin-state operation."""
        step_update_administrative_state(self)
