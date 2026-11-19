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
    step_create(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "provisioningState")),
        ],
    )
    step_update(
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
            test.check("interfaceName", attr(test, "interfaceName")),
            test.check("vlans", attr(test, "vlans")),
            test.check("isolationDomainIds", attr(test, "isolationDomainIdsResponse")),
        ],
    )
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
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud trunkednetwork show --name {name} --resource-group {rg}",
        checks=checks,
    )


def step_delete(test, checks=None):
    """TrunkedNetwork delete operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud trunkednetwork delete --name {name} --resource-group {rg} --yes",
        checks=checks,
    )


def step_list_resource_group(test, checks=None):
    """TrunkedNetwork list by resource group operation"""
    if checks is None:
        checks = []
    test.cmd("az networkcloud trunkednetwork list --resource-group {rg}", checks=checks)


def step_list_subscription(test, checks=None):
    """TrunkedNetwork list by subscription operation"""
    if checks is None:
        checks = []
    test.cmd("az networkcloud trunkednetwork list", checks=checks)


def step_update(test, checks=None):
    """TrunkedNetwork update operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud trunkednetwork update --name {name} --tags {tagsUpdate} --resource-group {rg}",
        checks=checks,
    )


class TrunkedNetworkScenarioTest(ScenarioTest):
    """TrunkedNetwork scenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("TRUNKED_NETWORK", "name"),
                "location": CONFIG.get("TRUNKED_NETWORK", "location"),
                "extendedLocation": CONFIG.get("TRUNKED_NETWORK", "extended_location"),
                "tags": CONFIG.get("TRUNKED_NETWORK", "tags"),
                "tagsUpdate": CONFIG.get("TRUNKED_NETWORK", "tags_update"),
                "provisioningState": CONFIG.get(
                    "TRUNKED_NETWORK", "provisioning_state"
                ),
                "type": CONFIG.get("TRUNKED_NETWORK", "type"),
                "vlans": CONFIG.get("TRUNKED_NETWORK", "vlans"),
                "interfaceName": CONFIG.get("TRUNKED_NETWORK", "interface_name"),
                "isolationDomainIds": CONFIG.get(
                    "TRUNKED_NETWORK", "isolation_domain_ids"
                ),
                "isolationDomainIdsResponse": CONFIG.get(
                    "TRUNKED_NETWORK", "isolation_domain_ids_response"
                ),
            }
        )

    @ResourceGroupPreparer(name_prefix="clitest_rg"[:7], key="rg", parameter_name="rg")
    def test_trunkednetwork_scenario1(self):
        """test scenario for TrunkedNetwork CRUD operations"""
        call_scenario1(self)
