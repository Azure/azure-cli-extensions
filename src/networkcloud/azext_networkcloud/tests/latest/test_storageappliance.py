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
from azure.cli.testsdk.checkers import NoneCheck
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

from .config import CONFIG
from .utils.output_checks import attr


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
        checks=[test.check("status", attr(test, "status"))],
    )
    step_disable_remote_vendor_management(
        test,
        checks=[test.check("status", attr(test, "status"))],
    )
    step_run_read_command(
        test,
        checks=[NoneCheck()],
    )
    step_show(
        test,
        checks=[
            test.exists("name"),
            test.exists("id"),
            test.check("serialNumber", attr(test, "serialNumberInitial")),
        ],
    )
    step_list_subscription(test, checks=[])
    step_list_resource_group(test, checks=[])
    step_update(
        test,
        checks=[
            test.check("tags", attr(test, "tagsUpdateResponse")),
            test.check("provisioningState", attr(test, "provisioningState")),
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


def step_run_read_command(test, checks=None):
    """StorageAppliance run read command operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud storageappliance run-read-command --name {name} --resource-group {resourceGroup} --limit-time-seconds {limitTimeSeconds} --commands {runReadCommands}",
        checks=checks,
    )


def step_show(test, checks=None):
    """StorageAppliance show operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud storageappliance show --resource-group {resourceGroup} --storage-appliance-name {name}",
        checks=checks,
    )


def step_list_resource_group(test, checks=None):
    """StorageAppliance list by resource group operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud storageappliance list --resource-group {resourceGroup}",
        checks=checks,
    )


def step_list_subscription(test, checks=None):
    """StorageAppliance list by subscription operation"""
    if checks is None:
        checks = []
    test.cmd("az networkcloud storageappliance list", checks=checks)


def step_update(test, checks=None):
    """StorageAppliance update operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud storageappliance update --resource-group {resourceGroup} --storage-appliance-name {name} --serial-number {serialNumber} --tags {tagsUpdate}",
        checks=checks,
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
                "tagsUpdateResponse": CONFIG.get(
                    "STORAGE_APPLIANCE", "tags_update_response"
                ),
                "provisioningState": CONFIG.get(
                    "STORAGE_APPLIANCE", "provisioning_state"
                ),
                "status": CONFIG.get("STORAGE_APPLIANCE", "status"),
                "serialNumber": CONFIG.get("STORAGE_APPLIANCE", "serial_number"),
                "serialNumberInitial": CONFIG.get(
                    "STORAGE_APPLIANCE", "serial_number_initial"
                ),
                "runReadCommands": CONFIG.get("STORAGE_APPLIANCE", "run_read_commands"),
                "limitTimeSeconds": CONFIG.get(
                    "STORAGE_APPLIANCE", "limit_time_seconds"
                ),
            }
        )

    @AllowLargeResponse()
    def test_storage_appliance_scenario1(self):
        """test scenario for StorageAppliance CRUD operations"""
        call_scenario1(self)
