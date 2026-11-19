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
from .utils.output_checks import attr


def setup_scenario1(test):
    """Env setup_scenario1"""
    pass


def cleanup_scenario(test):
    """Env cleanup_scenario1"""
    pass


def call_scenario1(test):
    """# Testcase: scenario1"""
    setup_scenario1(test)
    step_create_scenario1(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "provisioningState")),
        ],
    )
    step_update_scenario1(
        test,
        checks=[
            test.check("tags", attr(test, "tagsUpdate")),
            test.check("provisioningState", attr(test, "provisioningState")),
        ],
    )
    step_show(
        test,
        checks=[
            test.exists("name"),
            test.exists("id"),
            test.check(
                "additionalEgressEndpoints", attr(test, "additionalEgressEndpoint")
            ),
            test.check(
                "enableDefaultEgressEndpoints", attr(test, "defaultEgressEndpoint")
            ),
        ],
    )
    step_list_subscription(test, checks=[])
    step_list_resource_group(test, checks=[])
    step_delete(test, checks=[])
    cleanup_scenario(test)


def call_scenario2(test):
    """# Testcase: scenario2"""
    setup_scenario1(test)
    step_create_scenario2(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "provisioningState")),
        ],
    )
    step_update_scenario2(
        test,
        checks=[
            test.check("tags", attr(test, "tagsUpdate")),
            test.check("provisioningState", attr(test, "provisioningState")),
        ],
    )
    step_show(
        test,
        checks=[
            test.exists("name"),
            test.exists("id"),
            test.check("storageOptions.mode", attr(test, "mode")),
            test.check("storageOptions.sizeMiB", attr(test, "sizeMiB")),
            test.check(
                "storageOptions.storageApplianceId", attr(test, "storageApplianceId")
            ),
        ],
    )
    cleanup_scenario(test)


def step_create_scenario1(test, checks=None):
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


def step_create_scenario2(test, checks=None):
    """cloudservicesnetwork create operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud cloudservicesnetwork create --name {name} --extended-location "
        'name={extendedLocation} type="CustomLocation" --location {location} '
        "--additional-endpoints {additionalEgressEndpoint} "
        "--enable-endpoints  {defaultEgressEndpoint} "
        " --tags {tags} "
        " --resource-group {rg} "
        " --storage-options mode={mode} size-mi-b={sizeMiB} storage-appliance-id={storageApplianceId} ",
        checks=checks,
    )


def step_show(test, checks=None):
    """cloudservicesnetwork show operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud cloudservicesnetwork show --name {name} --resource-group {rg}",
        checks=checks,
    )


def step_delete(test, checks=None):
    """cloudservicesnetwork delete operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud cloudservicesnetwork delete --name {name} --resource-group {rg} --yes",
        checks=checks,
    )


def step_list_resource_group(test, checks=None):
    """cloudservicesnetwork list by resource group operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud cloudservicesnetwork list --resource-group {rg}", checks=checks
    )


def step_list_subscription(test, checks=None):
    """cloudservicesnetwork list by subscription operation"""
    if checks is None:
        checks = []
    test.cmd("az networkcloud cloudservicesnetwork list", checks=checks)


def step_update_scenario1(test, checks=None):
    """cloudservicesnetwork update operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud cloudservicesnetwork update --name {name} "
        "--additional-egress-endpoints {additionalEgressEndpoint} "
        "--enable-default-egress-endpoints {defaultEgressEndpoint} "
        "--tags {tagsUpdate} "
        "--resource-group {rg}",
        checks=checks,
    )


def step_update_scenario2(test, checks=None):
    """cloudservicesnetwork update operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud cloudservicesnetwork update --name {name} "
        "--additional-endpoints {additionalEgressEndpoint} "
        "--enable-endpoints {defaultEgressEndpoint} "
        "--tags {tagsUpdate} "
        "--resource-group {rg} "
        "--storage-options mode={mode} size-mi-b={sizeMiB} storage-appliance-id={storageApplianceId}",
        checks=checks,
    )


class CloudServicesNetworkScenarioTest(ScenarioTest):
    """CloudServicesNetwork scenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("CLOUD_SERVICES_NETWORK", "name"),
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
                "provisioningState": CONFIG.get(
                    "CLOUD_SERVICES_NETWORK", "provisioning_state"
                ),
                "mode": CONFIG.get("CLOUD_SERVICES_NETWORK", "storage_mode"),
                "sizeMiB": CONFIG.get("CLOUD_SERVICES_NETWORK", "storage_size_mi_b"),
                "storageApplianceId": CONFIG.get(
                    "CLOUD_SERVICES_NETWORK", "storage_appliance_id"
                ),
            }
        )

    @ResourceGroupPreparer(name_prefix="clitest_rg"[:7], key="rg", parameter_name="rg")
    def test_cloudservicesnetwork_scenario1(self):
        """test scenario for CloudServicesNetwork CRUD operations"""
        call_scenario1(self)

    @ResourceGroupPreparer(name_prefix="clitest_rg"[:7], key="rg", parameter_name="rg")
    def test_cloudservicesnetwork_scenario2(self):
        """test scenario for CloudServicesNetwork storage create, update and show operations"""
        call_scenario2(self)
