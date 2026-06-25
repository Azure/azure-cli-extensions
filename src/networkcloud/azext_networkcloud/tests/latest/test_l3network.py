# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
L3Network tests scenarios
"""

from azure.cli.testsdk import ResourceGroupPreparer, ScenarioTest

from .config import CONFIG
from .utils.assert_messages import (
    missing_field_message,
    properties_key_mismatch_message,
)
from .utils.output_checks import get_value


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
    """L3Network create operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud l3network create --name {name} --extended-location "
        'name={extendedLocation} type="CustomLocation" --location {location} '
        '--interface-name "eth0"  --ip-allocation-type {ipAllocationType} '
        "--ipv4-connected-prefix {ipv4prefix} --ipv6-connected-prefix {ipv6prefix} "
        "--l3-isolation-domain-id {l3_isolation_domain_id} --vlan {vlan} --tags "
        " {tags} --resource-group {rg}",
        checks=checks,
    )


def step_show(test, checks=None):
    """L3Network show operation"""
    if checks is not None:
        test.cmd(
            "az networkcloud l3network show --name {name} --resource-group {rg}",
            checks=checks,
        )
        return

    result = test.cmd(
        "az networkcloud l3network show --name {name} --resource-group {rg}"
    ).get_output_in_json()
    context = "L3Network show"
    assert result.get("name") is not None, missing_field_message(
        context, "name", result
    )
    properties = result.get("properties")
    assert properties is not None, missing_field_message(context, "properties", result)
    assert properties.get("vlan") == get_value(
        test, "vlan"
    ), properties_key_mismatch_message("vlan")

    assert properties.get("ipAllocationType") == get_value(
        test, "ipAllocationType"
    ), properties_key_mismatch_message("ipAllocationType")

    assert properties.get("ipv4ConnectedPrefix") == get_value(
        test, "ipv4prefix"
    ), properties_key_mismatch_message("ipv4ConnectedPrefix")

    assert properties.get("ipv6ConnectedPrefix") == get_value(
        test, "ipv6prefix"
    ), properties_key_mismatch_message("ipv6ConnectedPrefix")

    assert properties.get("l3IsolationDomainId") == get_value(
        test, "l3_isolation_domain_id"
    ), properties_key_mismatch_message("l3IsolationDomainId")


def step_delete(test, checks=None):
    """L3Network delete operation"""
    if checks is None:
        checks = []
    test.cmd("az networkcloud l3network delete --name {name} --resource-group {rg} -y")


def step_list_resource_group(test, checks=None):
    """L3Network list by resource group operation"""
    if checks is None:
        checks = []
    test.cmd("az networkcloud l3network list --resource-group {rg}")


def step_list_subscription(test, checks=None):
    """L3Network list by subscription operation"""
    if checks is None:
        checks = []
    test.cmd("az networkcloud l3network list")


def step_update(test, checks=None):
    """L3Network update operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud l3network update --name {name} --tags {tagsUpdate} --resource-group {rg}"
    )


class L3NetworkScenarioTest(ScenarioTest):
    """L3Network scenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": self.create_random_name(prefix="cli-test-l3-", length=24),
                "location": CONFIG.get("L3_NETWORK", "location"),
                "extendedLocation": CONFIG.get("L3_NETWORK", "extended_location"),
                "tags": CONFIG.get("L3_NETWORK", "tags"),
                "tagsUpdate": CONFIG.get("L3_NETWORK", "tags_update"),
                "type": CONFIG.get("L3_NETWORK", "type"),
                "vlan": CONFIG.get("L3_NETWORK", "vlan"),
                "ipAllocationType": CONFIG.get("L3_NETWORK", "ip_allocation_type"),
                "ipv4prefix": CONFIG.get("L3_NETWORK", "ipv4prefix"),
                "ipv6prefix": CONFIG.get("L3_NETWORK", "ipv6prefix"),
                "l3_isolation_domain_id": CONFIG.get(
                    "L3_NETWORK", "l3_isolation_domain_id"
                ),
            }
        )

    @ResourceGroupPreparer(name_prefix="clitest_rg"[:7], key="rg", parameter_name="rg")
    def test_l3network_scenario1(self):
        """test scenario for L3Network CRUD operations"""
        call_scenario1(self)
