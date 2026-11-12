# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""Recorded bootstrap interface administrative-state scenario."""

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
    """Verify the administrative-state update and final interface state."""
    setup_scenario1(test)
    step_update_admin_state(
        test,
        checks=[test.check("@", {})],
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
    """Update the configured bootstrap interface's admin state."""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric bootstrapinterface update-admin-state "
        "--resource-name {name} --resource-group {rg} "
        "--bootstrap-device {bootstrapDeviceName} "
        "--state {state} --resource-ids {resourceIds}",
        checks=checks,
    )


def step_show(test, checks=None):
    """Bootstrap interface show operation."""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric bootstrapinterface show "
        "--resource-name {name} --resource-group {rg} "
        "--bootstrap-device {bootstrapDeviceName}",
        checks=checks,
    )


class GA_BootstrapInterfaceUpdateAdminStateScenarioTest1(ScenarioTest):
    """Bootstrap interface update-admin-state scenario."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("BOOTSTRAP_INTERFACE", "name"),
                "rg": CONFIG.get("BOOTSTRAP_INTERFACE", "resource_group"),
                "bootstrapDeviceName": CONFIG.get(
                    "BOOTSTRAP_INTERFACE", "bootstrap_device_name"
                ),
                "state": CONFIG.get("BOOTSTRAP_INTERFACE", "state_disable"),
                "resourceIds": CONFIG.get("BOOTSTRAP_INTERFACE", "resource_ids"),
            }
        )

    def test_GA_bootstrapinterface_update_admin_state_scenario1(self):
        """Verify bootstrap interface administrative-state update completion."""
        call_scenario1(self)
