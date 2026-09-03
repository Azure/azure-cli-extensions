# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods

"""Fabric run-diagnostic test scenario."""

from azure.cli.testsdk import ScenarioTest

from .config import CONFIG


def call_scenario1(test):
    """Test Fabric runtime diagnostics."""
    step_run_diagnostic(
        test,
        checks=[
            test.check("status", "Succeeded"),
            test.check(
                "properties.diagnosticsUrl",
                "https://example.blob.core.windows.net/results/fabric-runtime.json",
            ),
        ],
    )


def step_run_diagnostic(test, checks=None):
    """Collect runtime configuration from a Fabric."""
    test.cmd(
        "az networkfabric fabric run-diagnostic --resource-name {name} "
        "--resource-group {rg} --operation-type {diagnosticOperationType} "
        "--runtime-config {runtimeConfig}",
        checks=checks or [],
    )


class FabricRunDiagnosticScenarioTest(ScenarioTest):
    """Fabric run-diagnostic scenario test."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("NETWORK_FABRIC", "name"),
                "rg": CONFIG.get("NETWORK_FABRIC", "resource_group"),
                "diagnosticOperationType": CONFIG.get(
                    "NETWORK_FABRIC", "diagnostic_operation_type"
                ),
                "runtimeConfig": CONFIG.get(
                    "NETWORK_FABRIC", "diagnostic_runtime_config"
                ),
            }
        )

    def test_fabric_run_diagnostic_scenario1(self):
        """Test the Fabric run-diagnostic operation."""
        call_scenario1(self)
