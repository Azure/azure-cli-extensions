# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
StorageAppliance tests scenarios
"""

from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

from .config import CONFIG


def setup_scenario1(test):
    """Env setup_scenario1"""
    pass


def cleanup_scenario1(test):
    """Env cleanup_scenario1"""
    pass


def call_scenario1(test):
    """# Testcase: scenario1"""
    setup_scenario1(test)
    step_enable_remote_vendor_management(
        test,
        checks=[test.check("status", "Succeeded")],
    )
    step_disable_remote_vendor_management(
        test,
        checks=[test.check("status", "Succeeded")],
    )
    step_show(test, checks=[])
    step_list_subscription(test, checks=[])
    step_list_resource_group(test, checks=[])
    step_update(
        test,
        checks=[
            test.check("tags", "{tagsUpdate}"),
            test.check("provisioningState", "Succeeded"),
        ],
    )
    cleanup_scenario1(test)


def step_enable_remote_vendor_management(test, checks=None):
    """StorageAppliance enable remote vendor management operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud storageappliance enable-remote-vendor-management --resource-group {resourceGroup} --storage-appliance-name {name}",
        checks=checks,
    )


def step_disable_remote_vendor_management(test, checks=None):
    """StorageAppliance disable remote vendor management operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud storageappliance disable-remote-vendor-management --resource-group {resourceGroup} --storage-appliance-name {name}",
        checks=checks,
    )


def step_show(test, checks=None):
    """StorageAppliance show operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud storageappliance show --resource-group {resourceGroup} --storage-appliance-name {name}"
    )


def step_list_resource_group(test, checks=None):
    """StorageAppliance list by resource group operation"""
    if checks is None:
        checks = []
    test.cmd("az networkcloud storageappliance list --resource-group {resourceGroup}")


def step_list_subscription(test, checks=None):
    """StorageAppliance list by subscription operation"""
    if checks is None:
        checks = []
    test.cmd("az networkcloud storageappliance list")


# skip run-read-command as it's not implemented yet
# def step_run_read_command(test, checks=None):


def step_update(test, checks=None):
    """StorageAppliance update operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud storageappliance update --resource-group {resourceGroup} --storage-appliance-name {name} --serial-number {serialNumber} --tags {tagsUpdate}"
    )


# As storage appliance is hydrated resource, it won't be provisioned in a testing rg
# instead, we will use a pre-provisioned storage appliance (from an actual lab) for testing
class StorageApplianceScenarioTest(ScenarioTest):
    """StorageAppliance scenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("STORAGE_APPLIANCE", "name"),
                "resourceGroup": CONFIG.get("STORAGE_APPLIANCE", "resource_group"),
                "tagsUpdate": CONFIG.get("STORAGE_APPLIANCE", "tags_update"),
                "serialNumber": CONFIG.get("STORAGE_APPLIANCE", "serial_number"),
            }
        )

    @AllowLargeResponse()
    def test_storage_appliance_scenario1(self):
        """test scenario for StorageAppliance CRUD operations"""
        call_scenario1(self)
