# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""Recorded bootstrap device password resync scenario."""

from azure.cli.testsdk import ScenarioTest

from .config import CONFIG


def setup_scenario1(test):
    """Env setup_scenario1"""
    pass


def cleanup_scenario1(test):
    """Env cleanup_scenario1"""
    pass


def call_scenario1(test):
    """Verify password resync, polling, and the final operation result."""
    setup_scenario1(test)
    step_resync_password(
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


def step_resync_password(test, checks=None):
    """Resync passwords on the configured bootstrap device."""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric bootstrapdevice resync-password "
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

    def test_GA_bootstrapdevice_resync_password_scenario1(self):
        """Verify bootstrap device password resync completion."""
        call_scenario1(self)
