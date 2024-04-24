# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
L2Network tests scenarios
"""

from azure.cli.testsdk import ResourceGroupPreparer, ScenarioTest

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
    step_create(
        test,
        checks=[
            test.check("name", "{name}"),
            test.check("provisioningState", "Succeeded"),
        ],
    )
    step_update(
        test,
        checks=[
            test.check("tags", "{tagsUpdate}"),
            test.check("provisioningState", "Succeeded"),
        ],
    )
    step_show(test, checks=[])
    step_list_subscription(test, checks=[])
    step_list_resource_group(test, checks=[])
    step_delete(test, checks=[])
    cleanup_scenario1(test)


def step_create(test, checks=None):
    """L2Network create operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud l2network create --name {name} --extended-location "
        "name={extendedLocation} type={type} --location {location} "
        "--interface-name {interfaceName} "
        "--l2-isolation-domain-id {l2_isolation_domain_id} --tags "
        " {tags} --resource-group {rg}",
        checks=checks,
    )


def step_show(test, checks=None):
    """L2Network show operation"""
    if checks is None:
        checks = []
    test.cmd("az networkcloud l2network show --name {name} --resource-group {rg}")


def step_delete(test, checks=None):
    """L2Network delete operation"""
    if checks is None:
        checks = []
    test.cmd("az networkcloud l2network delete --name {name} --resource-group {rg} -y")


def step_list_resource_group(test, checks=None):
    """L2Network list by resource group operation"""
    if checks is None:
        checks = []
    test.cmd("az networkcloud l2network list --resource-group {rg}")


def step_list_subscription(test, checks=None):
    """L2Network list by subscription operation"""
    if checks is None:
        checks = []
    test.cmd("az networkcloud l2network list")


def step_update(test, checks=None):
    """L2Network update operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud l2network update --name {name} --tags {tagsUpdate} --resource-group {rg}"
    )


class L2NetworkScenarioTest(ScenarioTest):
    """L2Network scenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": self.create_random_name(prefix="cli-test-l2-", length=24),
                "location": CONFIG.get("L2_NETWORK", "location"),
                "extendedLocation": CONFIG.get("L2_NETWORK", "extended_location"),
                "tags": CONFIG.get("L2_NETWORK", "tags"),
                "tagsUpdate": CONFIG.get("L2_NETWORK", "tags_update"),
                "type": CONFIG.get("L2_NETWORK", "type"),
                "interfaceName": CONFIG.get("L2_NETWORK", "interface_name"),
                "l2_isolation_domain_id": CONFIG.get(
                    "L2_NETWORK", "l2_isolation_domain_id"
                ),
            }
        )

    @ResourceGroupPreparer(name_prefix="clitest_rg"[:7], key="rg", parameter_name="rg")
    def test_l2network_scenario1(self):
        """test scenario for L2Network CRUD operations"""
        call_scenario1(self)
