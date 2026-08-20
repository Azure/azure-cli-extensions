# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods

"""Device run-diagnostic test scenario."""

from azure.cli.testsdk import ScenarioTest

from .config import CONFIG


def call_scenario1(test):
    """Test both Device diagnostic operation types."""
    step_run_support_bundle_diagnostic(
        test,
        checks=[
            test.check("status", "Succeeded"),
            test.check(
                "properties.diagnosticsUrl",
                "https://example.blob.core.windows.net/results/device-support.zip",
            ),
        ],
    )
    step_run_runtime_diagnostic(
        test,
        checks=[
            test.check("status", "Succeeded"),
            test.check(
                "properties.diagnosticsUrl",
                "https://example.blob.core.windows.net/results/device-runtime.json",
            ),
        ],
    )


def step_run_support_bundle_diagnostic(test, checks=None):
    """Collect a support bundle from a Device."""
    test.cmd(
        "az networkfabric device run-diagnostic --resource-name {name} "
        "--resource-group {rg} --operation-type {diagnosticOperationType} "
        "--support-bundle case-number={caseNumber}",
        checks=checks or [],
    )


def step_run_runtime_diagnostic(test, checks=None):
    """Collect runtime configuration from a Device."""
    test.cmd(
        "az networkfabric device run-diagnostic --resource-name {name} "
        "--resource-group {rg} "
        "--operation-type {runtimeDiagnosticOperationType} "
        "--runtime-config {runtimeConfig}",
        checks=checks or [],
    )


class DeviceRunDiagnosticScenarioTest(ScenarioTest):
    """Device run-diagnostic scenario test."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("NETWORK_DEVICE", "name"),
                "rg": CONFIG.get("NETWORK_DEVICE", "resource_group"),
                "diagnosticOperationType": CONFIG.get(
                    "NETWORK_DEVICE", "diagnostic_operation_type"
                ),
                "runtimeDiagnosticOperationType": CONFIG.get(
                    "NETWORK_DEVICE", "runtime_diagnostic_operation_type"
                ),
                "runtimeConfig": CONFIG.get(
                    "NETWORK_DEVICE", "diagnostic_runtime_config"
                ),
                "caseNumber": CONFIG.get("NETWORK_DEVICE", "diagnostic_case_number"),
            }
        )

    def test_device_run_diagnostic_scenario1(self):
        """Test the Device run-diagnostic operation."""
        call_scenario1(self)
