# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
Volume tests scenarios
"""

from azure.cli.testsdk import ScenarioTest

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
    step_list_by_resource_group(test, checks=[])
    step_list_by_subscription(test, checks=[])
    step_delete(test, checks=[])
    cleanup_scenario1(test)


def step_create(test, checks=None):
    """Volume create operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud volume create --resource-group {resourceGroup} "
        "--name {name} --location {location} "
        '--extended-location name={extendedLocation} type="CustomLocation" '
        "--size {size} --tags {tags}"
    )


def step_update(test, checks=None):
    """Volume update operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud volume update --resource-group {resourceGroup} "
        "--name {name} --tags {tagsUpdate}"
    )


def step_show(test, checks=None):
    """Volume show operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud volume show --resource-group {resourceGroup} " "--name {name}",
        checks=checks,
    )


def step_list_by_resource_group(test, checks=None):
    """Volume list by resource group operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud volume list --resource-group {resourceGroup}", checks=checks
    )


def step_list_by_subscription(test, checks=None):
    """Volume list by subscription operation"""
    if checks is None:
        checks = []
    test.cmd("az networkcloud volume list", checks=checks)


def step_delete(test, checks=None):
    """Volume delete operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud volume delete --resource-group {resourceGroup} "
        " --name {name} -y"
    )


class VolumeScenarioTest(ScenarioTest):
    """Volume scenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": self.create_random_name(prefix="cli-test-volume-", length=24),
                "location": CONFIG.get("VOLUME", "location"),
                "extendedLocation": CONFIG.get("VOLUME", "extended_location"),
                "resourceGroup": CONFIG.get("VOLUME", "resource_group"),
                "tags": CONFIG.get("VOLUME", "tags"),
                "tagsUpdate": CONFIG.get("VOLUME", "tags_update"),
                "size": CONFIG.get("VOLUME", "size"),
            }
        )

    def test_volume_scenario1(self):
        """test scenario for volume CRUD operations"""
        call_scenario1(self)
