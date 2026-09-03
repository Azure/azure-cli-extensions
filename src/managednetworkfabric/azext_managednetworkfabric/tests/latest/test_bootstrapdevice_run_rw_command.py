# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods

"""Bootstrap Device run-rw-command test scenario."""

from azure.cli.testsdk import ScenarioTest

from .config import CONFIG


def call_scenario1(test):
    """Test the Bootstrap Device read-write command."""
    step_run_rw_command(
        test,
        checks=[
            test.check("status", "Succeeded"),
            test.check(
                "properties.outputUrl",
                "https://example.blob.core.windows.net/results/bootstrap-rw.txt",
            ),
        ],
    )


def step_run_rw_command(test, checks=None):
    """Run a read-write command on a Bootstrap Device."""
    test.cmd(
        "az networkfabric bootstrapdevice run-rw-command "
        "--resource-name {name} --resource-group {rg} "
        "--command {rwCommand} --command-url {rwCommandUrl}",
        checks=checks or [],
    )


class BootstrapDeviceRunRwCommandScenarioTest(ScenarioTest):
    """Bootstrap Device run-rw-command scenario test."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("BOOTSTRAP_DEVICE", "name"),
                "rg": CONFIG.get("BOOTSTRAP_DEVICE", "resource_group"),
                "rwCommand": CONFIG.get("BOOTSTRAP_DEVICE", "rw_command"),
                "rwCommandUrl": CONFIG.get("BOOTSTRAP_DEVICE", "rw_command_url"),
            }
        )

    def test_bootstrapdevice_run_rw_command_scenario1(self):
        """Test the Bootstrap Device run-rw-command operation."""
        call_scenario1(self)
