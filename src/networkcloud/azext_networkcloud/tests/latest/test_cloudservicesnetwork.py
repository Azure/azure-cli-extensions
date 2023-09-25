# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
CloudServicesNetwork tests scenarios
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
    """cloudservicesnetwork create operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud cloudservicesnetwork create --name {name} --extended-location "
        'name={extendedLocation} type="CustomLocation" --location {location} '
        "--additional-egress-endpoints {additionalEgressEndpoint} "
        "--enable-default-egress-endpoints  {defaultEgressEndpoint} "
        " --tags {tags} "
        " --resource-group {rg}",
        checks=checks,
    )


def step_show(test, checks=None):
    """cloudservicesnetwork show operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud cloudservicesnetwork show --name {name} --resource-group {rg}"
    )


def step_delete(test, checks=None):
    """cloudservicesnetwork delete operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud cloudservicesnetwork delete --name {name} --resource-group {rg} -y"
    )


def step_list_resource_group(test, checks=None):
    """cloudservicesnetwork list by resource group operation"""
    if checks is None:
        checks = []
    test.cmd("az networkcloud cloudservicesnetwork list --resource-group {rg}")


def step_list_subscription(test, checks=None):
    """cloudservicesnetwork list by subscription operation"""
    if checks is None:
        checks = []
    test.cmd("az networkcloud cloudservicesnetwork list")


def step_update(test, checks=None):
    """cloudservicesnetwork update operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud cloudservicesnetwork update --name {name} "
        "--additional-egress-endpoints {additionalEgressEndpoint} "
        "--enable-default-egress-endpoints  {defaultEgressEndpoint} "
        "--tags {tagsUpdate} "
        "--resource-group {rg}"
    )


class CloudServicesNetworkScenarioTest(ScenarioTest):
    """CloudServicesNetwork scenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": self.create_random_name(prefix="cli-test-csn-", length=24),
                "location": CONFIG.get("CLOUD_SERVICES_NETWORK", "location"),
                "extendedLocation": CONFIG.get(
                    "CLOUD_SERVICES_NETWORK", "extended_location"
                ),
                "additionalEgressEndpoint": CONFIG.get(
                    "CLOUD_SERVICES_NETWORK", "additional_egress_endpoint"
                ),
                "defaultEgressEndpoint": CONFIG.get(
                    "CLOUD_SERVICES_NETWORK", "default_egress_endpoint"
                ),
                "tags": CONFIG.get("CLOUD_SERVICES_NETWORK", "tags"),
                "tagsUpdate": CONFIG.get("CLOUD_SERVICES_NETWORK", "tags_update"),
            }
        )

    @ResourceGroupPreparer(name_prefix="clitest_rg"[:7], key="rg", parameter_name="rg")
    def test_cloudservicesnetwork_scenario1(self):
        """test scenario for CloudServicesNetwork CRUD operations"""
        call_scenario1(self)
