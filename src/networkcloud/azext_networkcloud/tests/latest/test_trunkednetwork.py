# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
TrunkedNetwork tests scenarios
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
    """TrunkedNetwork create operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud trunkednetwork create --name {name} --extended-location "
        ' name={extendedLocation} type="CustomLocation" --location {location} '
        '--interface-name "{interfaceName}" '
        "--isolation-domain-ids  {isolationDomainIds} --vlans {vlans} "
        "--tags {tags} --resource-group {rg}",
        checks=checks,
    )


def step_show(test, checks=None):
    """TrunkedNetwork show operation"""
    if checks is not None:
        test.cmd(
            "az networkcloud trunkednetwork show --name {name} --resource-group {rg}",
            checks=checks,
        )
        return

    result = test.cmd(
        "az networkcloud trunkednetwork show --name {name} --resource-group {rg}"
    ).get_output_in_json()
    context = "Trunkednetwork show"
    assert result.get("name") is not None, missing_field_message(
        context, "name", result
    )
    assert result.get("id"), missing_field_message(context, "id", result)
    properties = result.get("properties")
    assert properties.get("interfaceName") == get_value(
        test, "interfaceName"
    ), properties_key_mismatch_message("interfaceName")

    assert properties.get("isolationDomainIds") == get_value(
        test, "isolationDomainIds"
    ), properties_key_mismatch_message("isolationDomainIds")

    assert properties.get("vlans") == get_value(
        test, "vlans"
    ), properties_key_mismatch_message("vlans")


def step_delete(test, checks=None):
    """TrunkedNetwork delete operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud trunkednetwork delete --name {name} --resource-group {rg} -y"
    )


def step_list_resource_group(test, checks=None):
    """TrunkedNetwork list by resource group operation"""
    if checks is None:
        checks = []
    test.cmd("az networkcloud trunkednetwork list --resource-group {rg}")


def step_list_subscription(test, checks=None):
    """TrunkedNetwork list by subscription operation"""
    if checks is None:
        checks = []
    test.cmd("az networkcloud trunkednetwork list")


def step_update(test, checks=None):
    """TrunkedNetwork update operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud trunkednetwork update --name {name} --tags {tagsUpdate} --resource-group {rg}"
    )


class TrunkedNetworkScenarioTest(ScenarioTest):
    """TrunkedNetwork scenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": self.create_random_name(
                    prefix="cli-test-trunkednw-", length=24
                ),
                "location": CONFIG.get("TRUNKED_NETWORK", "location"),
                "extendedLocation": CONFIG.get("TRUNKED_NETWORK", "extended_location"),
                "tags": CONFIG.get("TRUNKED_NETWORK", "tags"),
                "tagsUpdate": CONFIG.get("TRUNKED_NETWORK", "tags_update"),
                "type": CONFIG.get("TRUNKED_NETWORK", "type"),
                "vlans": CONFIG.get("TRUNKED_NETWORK", "vlans"),
                "interfaceName": CONFIG.get("TRUNKED_NETWORK", "interface_name"),
                "isolationDomainIds": CONFIG.get(
                    "TRUNKED_NETWORK", "isolation_domain_ids"
                ),
            }
        )

    @ResourceGroupPreparer(name_prefix="clitest_rg"[:7], key="rg", parameter_name="rg")
    def test_trunkednetwork_scenario1(self):
        """test scenario for TrunkedNetwork CRUD operations"""
        call_scenario1(self)
