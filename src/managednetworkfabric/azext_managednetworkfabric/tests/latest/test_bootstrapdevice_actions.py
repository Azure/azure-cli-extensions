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
from .utils.output_checks import attr


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


def step_upgrade(test, checks=None):
    """Upgrade the Bootstrap Device version."""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric bootstrapdevice upgrade "
        "--resource-name {name} --resource-group {rg} --version {version}",
        checks=checks,
    )


def step_show(test, checks=None):
    """Show the Bootstrap Device after an action completes."""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric bootstrapdevice show "
        "--resource-name {name} --resource-group {rg}",
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
                "state": CONFIG.get("BOOTSTRAP_DEVICE", "state_disable"),
                "resourceIds": CONFIG.get("BOOTSTRAP_DEVICE", "resource_ids"),
                "version": CONFIG.get("BOOTSTRAP_DEVICE", "version"),
                "expectedAdministrativeState": CONFIG.get(
                    "BOOTSTRAP_DEVICE", "expected_administrative_state"
                ),
                "expectedAdministrativeStateShow": CONFIG.get(
                    "BOOTSTRAP_DEVICE", "expected_administrative_state_show"
                ),
                "expectedConfigurationState": CONFIG.get(
                    "BOOTSTRAP_DEVICE", "expected_configuration_state"
                ),
                "expectedProvisioningState": CONFIG.get(
                    "BOOTSTRAP_DEVICE", "expected_provisioning_state"
                ),
                "expectedStatus": CONFIG.get("BOOTSTRAP_DEVICE", "expected_status"),
            }
        )
        self.vcr.match_on = (*self.vcr.match_on, "body")

    @AllowLargeResponse()
    def test_GA_bootstrapdevice_reboot_scenario1(self):
        """Verify reboot completion and final device state."""
        step_reboot(
            self,
            checks=[
                self.check("status", attr(self, "expectedStatus")),
            ],
        )
        step_show(
            self,
            checks=[
                self.check(
                    "provisioningState", attr(self, "expectedProvisioningState")
                ),
                self.check(
                    "configurationState", attr(self, "expectedConfigurationState")
                ),
                self.check(
                    "administrativeState", attr(self, "expectedAdministrativeState")
                ),
            ],
        )
        self.assertTrue(self.cassette.all_played)

    @AllowLargeResponse()
    def test_GA_bootstrapdevice_refresh_config_scenario1(self):
        """Verify configuration refresh completion and final device state."""
        step_refresh_configuration(
            self,
            checks=[
                self.check("status", attr(self, "expectedStatus")),
            ],
        )
        step_show(
            self,
            checks=[
                self.check(
                    "provisioningState", attr(self, "expectedProvisioningState")
                ),
                self.check(
                    "configurationState", attr(self, "expectedConfigurationState")
                ),
            ],
        )
        self.assertTrue(self.cassette.all_played)

    @AllowLargeResponse()
    def test_GA_bootstrapdevice_resync_password_scenario1(self):
        """Verify password resync completion and final device state."""
        step_resync_password(
            self,
            checks=[
                self.check("status", attr(self, "expectedStatus")),
            ],
        )
        step_show(
            self,
            checks=[
                self.check(
                    "provisioningState", attr(self, "expectedProvisioningState")
                ),
                self.check(
                    "configurationState", attr(self, "expectedConfigurationState")
                ),
            ],
        )
        self.assertTrue(self.cassette.all_played)

    @AllowLargeResponse()
    def test_GA_bootstrapdevice_update_admin_state_scenario1(self):
        """Verify administrative-state update completion and final device state."""
        self.kwargs["resourceIds"] = self.kwargs["resourceIds"].replace(
            "00000000-0000-0000-0000-000000000000", self.get_subscription_id()
        )
        step_update_admin_state(
            self,
            checks=[
                self.check("status", attr(self, "expectedStatus")),
            ],
        )
        step_show(
            self,
            checks=[
                self.check(
                    "provisioningState", attr(self, "expectedProvisioningState")
                ),
                self.check(
                    "configurationState", attr(self, "expectedConfigurationState")
                ),
                self.check(
                    "administrativeState", attr(self, "expectedAdministrativeStateShow")
                ),
            ],
        )
        self.assertTrue(self.cassette.all_played)

    @AllowLargeResponse()
    def test_GA_bootstrapdevice_upgrade_scenario1(self):
        """Verify upgrade completion, requested version, and final device state."""
        step_upgrade(
            self,
            checks=[
                self.check("status", attr(self, "expectedStatus")),
            ],
        )
        step_show(
            self,
            checks=[
                self.check(
                    "provisioningState", attr(self, "expectedProvisioningState")
                ),
                self.check(
                    "configurationState", attr(self, "expectedConfigurationState")
                ),
                self.check(
                    "administrativeState", attr(self, "expectedAdministrativeStateShow")
                ),
                self.check("version", attr(self, "version")),
            ],
        )
        self.assertTrue(self.cassette.all_played)
