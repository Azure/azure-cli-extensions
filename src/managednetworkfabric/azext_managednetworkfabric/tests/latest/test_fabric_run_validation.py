# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods

"""Fabric run-validation test scenario."""

from azure.cli.testsdk import ScenarioTest

from .config import CONFIG


def call_scenario1(test):
    """Test Fabric validation with all generated body options."""
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
    """Run validation on a Fabric."""
    test.cmd(
        "az networkfabric fabric run-validation --resource-name {name} "
        "--resource-group {rg} --validation-type {validationType} "
        "--target-version {targetVersion} --command-config {commandConfig} "
        "--device-filter {deviceFilter} --metrics-config {metricsConfig} "
        "--override-checks {overrideChecks}",
        checks=checks or [],
    )


class FabricRunValidationScenarioTest(ScenarioTest):
    """Fabric run-validation scenario test."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("NETWORK_FABRIC", "name"),
                "rg": CONFIG.get("NETWORK_FABRIC", "resource_group"),
                "validationType": CONFIG.get("NETWORK_FABRIC", "validation_type"),
                "targetVersion": CONFIG.get("NETWORK_FABRIC", "upgrade_version"),
                "commandConfig": CONFIG.get(
                    "NETWORK_FABRIC", "validation_command_config"
                ),
                "deviceFilter": CONFIG.get(
                    "NETWORK_FABRIC", "validation_device_filter"
                ),
                "metricsConfig": CONFIG.get(
                    "NETWORK_FABRIC", "validation_metrics_config"
                ),
                "overrideChecks": CONFIG.get(
                    "NETWORK_FABRIC", "validation_override_checks"
                ),
            }
        )

    def test_fabric_run_validation_scenario1(self):
        """Test the Fabric run-validation operation."""
        call_scenario1(self)
