# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Bootstrap device password resync using a Swagger-derived mock recording."""

from azure.cli.testsdk import ScenarioTest

from .config import CONFIG


def call_scenario1(test):
    """Verify password resync, polling, and the final operation result."""
    step_resync_password(
        test,
        checks=[
            test.check("status", "Succeeded"),
            test.check("percentComplete", 100),
        ],
    )
    test.assertTrue(test.cassette.all_played)


def step_resync_password(test, checks=None):
    """Resync passwords on the configured bootstrap device."""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric bootstrapdevice resync-password "
        "--resource-name {name} --resource-group {rg}",
        checks=checks,
    )


class GA_BootstrapDeviceResyncPasswordScenarioTest1(ScenarioTest):
    """Bootstrap device password resync scenario."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("BOOTSTRAP_DEVICE", "name"),
                "rg": CONFIG.get("BOOTSTRAP_DEVICE", "resource_group"),
            }
        )
        self.vcr.match_on = (*self.vcr.match_on, "body")

    def test_GA_bootstrapdevice_resync_password_scenario1(self):
        """Replay the bootstrap device password resync mock recording."""
        call_scenario1(self)
