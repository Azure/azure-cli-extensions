# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods

"""Bootstrap Device action test scenarios."""

from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

from .config import CONFIG


def step_reboot(test, checks=None):
    """Reboot the Bootstrap Device."""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric bootstrapdevice reboot "
        "--resource-name {name} --resource-group {rg}",
        checks=checks,
    )


def step_refresh_configuration(test, checks=None):
    """Refresh the Bootstrap Device configuration."""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric bootstrapdevice refresh-config "
        "--resource-name {name} --resource-group {rg}",
        checks=checks,
    )


def step_resync_password(test, checks=None):
    """Resync the Bootstrap Device password."""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric bootstrapdevice resync-password "
        "--resource-name {name} --resource-group {rg}",
        checks=checks,
    )


def step_update_admin_state(test, checks=None):
    """Update the Bootstrap Device administrative state."""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric bootstrapdevice update-admin-state "
        "--resource-name {name} --resource-group {rg} --state {state} "
        "--resource-ids {resourceIds}",
        checks=checks,
    )


class BootstrapDeviceActionsScenarioTest(ScenarioTest):
    """Bootstrap Device action scenario tests."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("BOOTSTRAP_DEVICE", "name"),
                "rg": CONFIG.get("BOOTSTRAP_DEVICE", "resource_group"),
                "state": CONFIG.get("BOOTSTRAP_DEVICE", "state"),
                "resourceIds": CONFIG.get("BOOTSTRAP_DEVICE", "resource_ids"),
            }
        )

    @AllowLargeResponse()
    def test_bootstrapdevice_reboot(self):
        """Test the Bootstrap Device reboot operation."""
        step_reboot(self, checks=[self.check("status", "Succeeded")])

    @AllowLargeResponse()
    def test_bootstrapdevice_refresh_configuration(self):
        """Test the Bootstrap Device refresh-config operation."""
        step_refresh_configuration(self, checks=[self.check("status", "Succeeded")])

    @AllowLargeResponse()
    def test_bootstrapdevice_resync_password(self):
        """Test the Bootstrap Device resync-password operation."""
        step_resync_password(self, checks=[self.check("status", "Succeeded")])

    @AllowLargeResponse()
    def test_bootstrapdevice_update_admin_state(self):
        """Test the Bootstrap Device update-admin-state operation."""
        step_update_admin_state(self, checks=[self.check("status", "Succeeded")])
