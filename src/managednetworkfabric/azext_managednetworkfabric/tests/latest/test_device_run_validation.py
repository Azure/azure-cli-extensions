# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods

"""Device run-validation test scenario."""

from azure.cli.testsdk import ScenarioTest

from .config import CONFIG


def call_scenario1(test):
    """Test Device validation with all generated body options."""
    step_run_validation(
        test,
        checks=[
            test.check("status", "Succeeded"),
            test.check("properties.validationResult", "Passed"),
            test.check(
                "properties.targetVersion", test.kwargs["targetVersion"].strip('"')
            ),
        ],
    )


def step_run_validation(test, checks=None):
    """Run validation on a Device."""
    test.cmd(
        "az networkfabric device run-validation --resource-name {name} "
        "--resource-group {rg} --validation-type {validationType} "
        "--target-version {targetVersion} --command-config {commandConfig} "
        "--metrics-config {metricsConfig} --override-checks {overrideChecks}",
        checks=checks or [],
    )


class DeviceRunValidationScenarioTest(ScenarioTest):
    """Device run-validation scenario test."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("NETWORK_DEVICE", "name"),
                "rg": CONFIG.get("NETWORK_DEVICE", "resource_group"),
                "validationType": CONFIG.get("NETWORK_DEVICE", "validation_type"),
                "targetVersion": CONFIG.get("NETWORK_DEVICE", "upgrade_version"),
                "commandConfig": CONFIG.get(
                    "NETWORK_DEVICE", "validation_command_config"
                ),
                "metricsConfig": CONFIG.get(
                    "NETWORK_DEVICE", "validation_metrics_config"
                ),
                "overrideChecks": CONFIG.get(
                    "NETWORK_DEVICE", "validation_override_checks"
                ),
            }
        )

    def test_device_run_validation_scenario1(self):
        """Test the Device run-validation operation."""
        call_scenario1(self)
