# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods

"""Bootstrap Device run-ro-command test scenario."""

from azure.cli.testsdk import ScenarioTest

from .config import CONFIG


def call_scenario1(test):
    """Test the Bootstrap Device read-only command."""
    step_run_ro_command(
        test,
        checks=[
            test.check("status", "Succeeded"),
            test.check("properties.configurationState", "Succeeded"),
        ],
    )


def step_run_ro_command(test, checks=None):
    """Run a read-only command on a Bootstrap Device."""
    test.cmd(
        "az networkfabric bootstrapdevice run-ro-command "
        "--resource-name {name} --resource-group {rg} "
        "--command {roCommand}",
        checks=checks or [],
    )


class BootstrapDeviceRunRoCommandScenarioTest(ScenarioTest):
    """Bootstrap Device run-ro-command scenario test."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("BOOTSTRAP_DEVICE", "name"),
                "rg": CONFIG.get("BOOTSTRAP_DEVICE", "resource_group"),
                "roCommand": CONFIG.get("BOOTSTRAP_DEVICE", "ro_command"),
            }
        )

    def test_bootstrapdevice_run_ro_command_scenario1(self):
        """Test the Bootstrap Device run-ro-command operation."""
        call_scenario1(self)
