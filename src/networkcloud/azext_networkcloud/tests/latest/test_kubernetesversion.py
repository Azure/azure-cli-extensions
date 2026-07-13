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


def setup_scenario1(test):
    """Env setup_scenario1"""
    pass


def cleanup_scenario1(test):
    """Env cleanup_scenario1"""
    pass


def call_scenario1(test):
    """# Testcase: scenario1"""
    setup_scenario1(test)
    step_create(test, checks=[])
    step_update(test, checks=[])
    step_show(test, checks=[])
    step_list_subscription(test, checks=[])
    step_list_resource_group(test, checks=[])
    step_delete(test, checks=[])
    cleanup_scenario1(test)


def step_create(test, checks=None):
    """KubernetesVersion create operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud kubernetesversion create --name {name} --extended-location "
        ' name={extendedLocation} type="CustomLocation" --location {location} '
        "--tags {tags} --resource-group {rg}",
        checks=checks,
    )


def step_show(test, checks=None):
    """KubernetesVersion show operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud kubernetesversion show --name {name} --resource-group {rg}"
    )


def step_delete(test, checks=None):
    """KubernetesVersion delete operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud kubernetesversion delete --name {name} --resource-group {rg} -y"
    )


def step_list_resource_group(test, checks=None):
    """KubernetesVersion list by resource group operation"""
    if checks is None:
        checks = []
    test.cmd("az networkcloud kubernetesversion list --resource-group {rg}")


def step_list_subscription(test, checks=None):
    """KubernetesVersion list by subscription operation"""
    if checks is None:
        checks = []
    test.cmd("az networkcloud kubernetesversion list")


def step_update(test, checks=None):
    """KubernetesVersion update operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud kubernetesversion update --name {name} --tags {tagsUpdate} --resource-group {rg}"
    )


class KubernetesVersionScenarioTest(ScenarioTest):
    """KubernetesVersion scenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("KUBERNETES_VERSION", "name"),
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
