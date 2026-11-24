# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods

"""Bootstrap Device run-rw-command test scenario."""

from azure.cli.testsdk import ScenarioTest

from .config import CONFIG
from .utils.output_checks import attr


def call_scenario1(test):
    """Test the Bootstrap Device read-write command."""
    step_run_rw_command(
        test,
        checks=[
            test.check("status", attr(test, "expectedStatus")),
            test.check(
                "properties.configurationState",
                attr(test, "expectedPropertiesConfigurationState"),
            ),
            test.check(
                "properties.outputUrl",
                attr(test, "expectedPropertiesOutputUrlRunRwCommand"),
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
                "expectedPropertiesConfigurationState": CONFIG.get(
                    "BOOTSTRAP_DEVICE", "expected_properties_configuration_state"
                ),
                "expectedPropertiesOutputUrlRunRwCommand": CONFIG.get(
                    "BOOTSTRAP_DEVICE", "expected_properties_output_url_run_rw_command"
                ),
                "expectedStatus": CONFIG.get("BOOTSTRAP_DEVICE", "expected_status"),
            }
        )

    def test_GA_bootstrapdevice_run_rw_command_scenario1(self):
        """Test the Bootstrap Device run-rw-command operation."""
        call_scenario1(self)
