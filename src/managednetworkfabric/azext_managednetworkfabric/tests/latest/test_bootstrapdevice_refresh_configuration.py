# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Bootstrap device configuration refresh using a Swagger-derived mock recording."""

from azure.cli.testsdk import ScenarioTest

from .config import CONFIG


def call_scenario1(test):
    """Verify configuration refresh, polling, and the final operation result."""
    step_refresh_configuration(
        test,
        checks=[
            test.check("status", "Succeeded"),
            test.check("percentComplete", 100),
        ],
    )
    test.assertTrue(test.cassette.all_played)


def step_refresh_configuration(test, checks=None):
    """Refresh the configured bootstrap device's configuration."""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric bootstrapdevice refresh-configuration "
        "--resource-name {name} --resource-group {rg}",
        checks=checks,
    )


class GA_BootstrapDeviceRefreshConfigurationScenarioTest1(ScenarioTest):
    """Bootstrap device configuration refresh scenario."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("BOOTSTRAP_DEVICE", "name"),
                "rg": CONFIG.get("BOOTSTRAP_DEVICE", "resource_group"),
            }
        )
        self.vcr.match_on = (*self.vcr.match_on, "body")

    def test_GA_bootstrapdevice_refresh_configuration_scenario1(self):
        """Replay the bootstrap device configuration refresh mock recording."""
        call_scenario1(self)
