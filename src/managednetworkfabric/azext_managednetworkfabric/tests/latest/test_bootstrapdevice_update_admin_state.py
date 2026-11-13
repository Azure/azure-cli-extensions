# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""Recorded bootstrap device administrative-state scenario."""

from azure.cli.testsdk import ScenarioTest

from .config import CONFIG


def setup_scenario1(test):
    """Env setup_scenario1"""
    test.kwargs["resourceIds"] = test.kwargs["resourceIds"].replace(
        "00000000-0000-0000-0000-000000000000", test.get_subscription_id()
    )


def cleanup_scenario1(test):
    """Env cleanup_scenario1"""
    pass


def call_scenario1(test):
    """Verify the administrative-state update and final device state."""
    setup_scenario1(test)
    step_update_admin_state(
        test,
        checks=[test.check("status", "Succeeded")],
    )
    step_show(
        test,
        checks=[
            test.check("administrativeState", "Disabled"),
            test.check("provisioningState", "Succeeded"),
            test.check("configurationState", "Succeeded"),
        ],
    )
    cleanup_scenario1(test)


def step_update_admin_state(test, checks=None):
    """Update the configured bootstrap device's admin state."""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric bootstrapdevice update-admin-state "
        "--resource-name {name} --resource-group {rg} "
        "--state {state} --resource-ids {resourceIds}",
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


class GA_BootstrapDeviceUpdateAdminStateScenarioTest1(ScenarioTest):
    """Bootstrap device update-admin-state scenario."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("BOOTSTRAP_DEVICE", "name"),
                "rg": CONFIG.get("BOOTSTRAP_DEVICE", "resource_group"),
                "state": CONFIG.get("BOOTSTRAP_DEVICE", "state_disable"),
                "resourceIds": CONFIG.get("BOOTSTRAP_DEVICE", "resource_ids"),
            }
        )

    def test_GA_bootstrapdevice_update_admin_state_scenario1(self):
        """Verify bootstrap device administrative-state update completion."""
        call_scenario1(self)
