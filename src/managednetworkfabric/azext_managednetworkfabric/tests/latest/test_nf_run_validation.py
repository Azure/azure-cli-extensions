# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods

"""Fabric run-validation test scenario."""

from azure.cli.testsdk import ScenarioTest

from .config import CONFIG
from .utils.output_checks import attr


def call_scenario1(test):
    """Test Fabric validation with inline device commands."""
    step_run_validation_inline(
        test,
        checks=[
            test.check("status", attr(test, "expectedStatus")),
            test.check(
                "properties.checkResults", attr(test, "expectedPropertiesCheckResults")
            ),
            test.check(
                "properties.currentVersion",
                attr(test, "expectedPropertiesCurrentVersion"),
            ),
            test.check(
                "properties.failedDevices",
                attr(test, "expectedPropertiesFailedDevices"),
            ),
            test.check(
                "properties.resultUrl", attr(test, "expectedPropertiesResultUrl")
            ),
            test.check(
                "properties.successfulDevices",
                attr(test, "expectedPropertiesSuccessfulDevices"),
            ),
            test.check("properties.targetVersion", attr(test, "targetVersion")),
            test.check(
                "properties.validationId", attr(test, "expectedPropertiesValidationId")
            ),
            test.check(
                "properties.validationResult",
                attr(test, "expectedPropertiesValidationResult"),
            ),
        ],
    )


def call_scenario2(test):
    """Test Fabric validation with a device commands file."""
    step_run_validation_file(
        test,
        checks=[
            test.check("status", attr(test, "expectedStatus")),
            test.check(
                "properties.checkResults", attr(test, "expectedPropertiesCheckResults")
            ),
            test.check(
                "properties.currentVersion",
                attr(test, "expectedPropertiesCurrentVersion"),
            ),
            test.check(
                "properties.failedDevices",
                attr(test, "expectedPropertiesFailedDevices"),
            ),
            test.check(
                "properties.resultUrl",
                attr(test, "expectedPropertiesResultUrlRunValidationFile"),
            ),
            test.check(
                "properties.successfulDevices",
                attr(test, "expectedPropertiesSuccessfulDevices"),
            ),
            test.check("properties.targetVersion", attr(test, "targetVersion")),
            test.check(
                "properties.validationId",
                attr(test, "expectedPropertiesValidationIdRunValidationFile"),
            ),
            test.check(
                "properties.validationResult",
                attr(test, "expectedPropertiesValidationResult"),
            ),
        ],
    )


def step_run_validation_inline(test, checks=None):
    """Run validation on a Fabric with inline commands."""
    test.cmd(
        "az networkfabric fabric run-validation --resource-name {name} "
        "--resource-group {rg} --validation-type {validationType} "
        "--target-version {targetVersion} --command-config {validationInlineCommands} "
        "--device-filter {deviceFilter} --metrics-config {metricsConfig} "
        "--override-checks {overrideChecks}",
        checks=checks or [],
    )


def step_run_validation_file(test, checks=None):
    """Run validation on a Fabric with a commands file."""
    test.cmd(
        "az networkfabric fabric run-validation --resource-name {name} "
        "--resource-group {rg} --validation-type {validationType} "
        "--target-version {targetVersion} --command-config {validationCommandsUrl} "
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
                "validationInlineCommands": CONFIG.get(
                    "NETWORK_FABRIC", "validation_inline_commands"
                ),
                "validationCommandsUrl": CONFIG.get(
                    "NETWORK_FABRIC", "validation_commands_url"
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
                "expectedPropertiesCheckResults": CONFIG.get(
                    "NETWORK_FABRIC", "expected_properties_check_results"
                ),
                "expectedPropertiesCurrentVersion": CONFIG.get(
                    "NETWORK_FABRIC", "expected_properties_current_version"
                ),
                "expectedPropertiesFailedDevices": CONFIG.get(
                    "NETWORK_FABRIC", "expected_properties_failed_devices"
                ),
                "expectedPropertiesResultUrl": CONFIG.get(
                    "NETWORK_FABRIC", "expected_properties_result_url"
                ),
                "expectedPropertiesResultUrlRunValidationFile": CONFIG.get(
                    "NETWORK_FABRIC",
                    "expected_properties_result_url_run_validation_file",
                ),
                "expectedPropertiesSuccessfulDevices": CONFIG.get(
                    "NETWORK_FABRIC", "expected_properties_successful_devices"
                ),
                "expectedPropertiesValidationId": CONFIG.get(
                    "NETWORK_FABRIC", "expected_properties_validation_id"
                ),
                "expectedPropertiesValidationIdRunValidationFile": CONFIG.get(
                    "NETWORK_FABRIC",
                    "expected_properties_validation_id_run_validation_file",
                ),
                "expectedPropertiesValidationResult": CONFIG.get(
                    "NETWORK_FABRIC", "expected_properties_validation_result"
                ),
                "expectedStatus": CONFIG.get("NETWORK_FABRIC", "expected_status"),
            }
        )

    def test_GA_fabric_run_validation_scenario1(self):
        """Test Fabric run-validation with inline commands."""
        call_scenario1(self)

    def test_GA_fabric_run_validation_scenario2(self):
        """Test Fabric run-validation with a commands file."""
        call_scenario2(self)
