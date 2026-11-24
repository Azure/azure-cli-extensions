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
from .utils.output_checks import attr


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


def step_show(test, checks=None):
    """Show the Bootstrap Interface after its administrative-state update."""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric bootstrapinterface show "
        "--resource-name {name} --resource-group {rg} "
        "--bootstrap-device {bootstrapDeviceName}",
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
                "state": CONFIG.get("BOOTSTRAP_INTERFACE", "state_disable"),
                "resourceIds": CONFIG.get("BOOTSTRAP_INTERFACE", "resource_ids"),
                "expectedAdministrativeStateShow": CONFIG.get(
                    "BOOTSTRAP_INTERFACE", "expected_administrative_state_show"
                ),
                "expectedConfigurationState": CONFIG.get(
                    "BOOTSTRAP_INTERFACE", "expected_configuration_state"
                ),
                "expectedProvisioningState": CONFIG.get(
                    "BOOTSTRAP_INTERFACE", "expected_provisioning_state"
                ),
                "expectedStatus": CONFIG.get("BOOTSTRAP_INTERFACE", "expected_status"),
            }
        )
        self.vcr.match_on = (*self.vcr.match_on, "body")

    @AllowLargeResponse()
    def test_GA_bootstrapinterface_update_admin_state_scenario1(self):
        """Verify administrative-state update completion and final interface state."""
        self.kwargs["resourceIds"] = self.kwargs["resourceIds"].replace(
            "00000000-0000-0000-0000-000000000000", self.get_subscription_id()
        )
        step_update_administrative_state(
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
