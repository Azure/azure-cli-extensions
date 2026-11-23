# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
KubernetesVersion tests scenarios
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
    step_update(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "provisioningState")),
            test.check("tags", attr(test, "tagsUpdate")),
        ],
    )
    step_show(
        test,
        checks=[
            test.exists("name"),
            test.exists("id"),
            test.check("provisioningState", attr(test, "provisioningState")),
        ],
    )
    step_list_subscription(test, checks=[])
    step_list_resource_group(test, checks=[])
    cleanup_scenario1(test)


def step_show(test, checks=None):
    """KubernetesVersion show operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud kubernetesversion show --name {name} --resource-group {rg}",
        checks=checks,
    )


def step_list_resource_group(test, checks=None):
    """KubernetesVersion list by resource group operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud kubernetesversion list --resource-group {rg}", checks=checks
    )


def step_list_subscription(test, checks=None):
    """KubernetesVersion list by subscription operation"""
    if checks is None:
        checks = []
    test.cmd("az networkcloud kubernetesversion list", checks=checks)


def step_update(test, checks=None):
    """KubernetesVersion update operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud kubernetesversion update --name {name} --tags {tagsUpdate} --resource-group {rg}",
        checks=checks,
    )


class KubernetesVersionScenarioTest(ScenarioTest):
    """KubernetesVersion scenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("KUBERNETES_VERSION", "name"),
                "provisioningState": CONFIG.get(
                    "KUBERNETES_VERSION", "provisioning_state"
                ),
                "location": CONFIG.get("KUBERNETES_VERSION", "location"),
                "extendedLocation": CONFIG.get("TRUNKED_NETWORK", "extended_location"),
                "tags": CONFIG.get("TRUNKED_NETWORK", "tags"),
                "tagsUpdate": CONFIG.get("TRUNKED_NETWORK", "tags_update"),
                "type": CONFIG.get("TRUNKED_NETWORK", "type"),
            }
        )

    @ResourceGroupPreparer(name_prefix="clitest_rg"[:7], key="rg", parameter_name="rg")
    def test_kubernetesversion_scenario1(self):
        """test scenario for KubernetesVersion CRUD operations"""
        call_scenario1(self)
