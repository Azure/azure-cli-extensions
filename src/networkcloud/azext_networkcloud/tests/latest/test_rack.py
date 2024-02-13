# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
Rack test scenarios
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
    step_update(
        test,
        checks=[
            test.check("tags", "{tagsUpdate}"),
            test.check("provisioningState", "Succeeded"),
        ],
    )
    step_show(test, checks=[])
    step_list_subscription(test)
    step_list_resource_group(test, checks=[])
    cleanup_scenario1(test)


def step_show(test, checks=None):
    """Rack show operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud rack show --name {name} " "--resource-group {rg}",
        checks=checks,
    )


def step_list_resource_group(test=None, checks=None):
    """Rack list by resource group operation"""
    if checks is None:
        checks = []
    test.cmd("az networkcloud rack list --resource-group {rg}")


@AllowLargeResponse
def step_list_subscription(test):
    """Rack list by subscription operation"""
    test.cmd("az networkcloud rack list")


def step_update(test, checks=None):
    """Rack update operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud rack update --name {name} "
        "--rack-location {rackLocation} "
        "--rack-serial-number {serialNumber} "
        "--tags {tagsUpdate} --resource-group {rg}"
    )


# As Rack is a hydrated resource, it won't be provisioned in a testing rg
# instead, we will use a resource created as a part of cluster deployment for testing
class RackScenarioTest(ScenarioTest):
    """Rack scenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("RACK", "name"),
                "location": CONFIG.get("RACK", "location"),
                "rackLocation": CONFIG.get("RACK", "rack_location"),
                "rg": CONFIG.get("RACK", "resource_group"),
                "serialNumber": CONFIG.get("RACK", "serial_number"),
                "tags": CONFIG.get("RACK", "tags"),
                "tagsUpdate": CONFIG.get("RACK", "tags_update"),
            }
        )

    def test_rack_scenario1(self):
        """test scenario for Rack read and update operations"""
        call_scenario1(self)
