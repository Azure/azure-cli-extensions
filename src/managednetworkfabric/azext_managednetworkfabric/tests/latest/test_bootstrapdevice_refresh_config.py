# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""Recorded bootstrap device configuration refresh scenario."""

from azure.cli.testsdk import ScenarioTest

from .config import CONFIG


def setup_scenario1(test):
    """Env setup_scenario1"""
    pass


def cleanup_scenario1(test):
    """Env cleanup_scenario1"""
    pass


def call_scenario1(test):
    """Verify configuration refresh, polling, and the final operation result."""
    setup_scenario1(test)
    step_refresh_config(
        test,
        checks=[test.check("status", "Succeeded")],
    )
    step_show(
        test,
        checks=[
            test.check("provisioningState", "Succeeded"),
            test.check("configurationState", "Succeeded"),
        ],
    )
    cleanup_scenario1(test)


def step_refresh_config(test, checks=None):
    """Refresh the configured bootstrap device's configuration."""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric bootstrapdevice refresh-config "
        "--resource-name {name} --resource-group {rg}",
        checks=checks,
    )


def step_show(test, checks=None):
    """Bootstrap device show operation."""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric bootstrapdevice show "
        "--resource-name {name} --resource-group {rg}",
        checks=checks,
    )


class GA_BootstrapDeviceRefreshConfigScenarioTest1(ScenarioTest):
    """Bootstrap device configuration refresh scenario."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("BOOTSTRAP_DEVICE", "name"),
                "rg": CONFIG.get("BOOTSTRAP_DEVICE", "resource_group"),
            }
        )

    def test_GA_bootstrapdevice_refresh_config_scenario1(self):
        """Verify bootstrap device configuration refresh completion."""
        call_scenario1(self)
