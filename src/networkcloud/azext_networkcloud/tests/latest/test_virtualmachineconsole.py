# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
VirtualMachine console tests scenarios
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
    step_list(test, checks=[])
    step_delete(test, checks=[])
    cleanup_scenario1(test)


def step_create(test, checks=None):
    """VirtualMachine console create operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud virtualmachine console create "
        '--extended-location name={extendedLocation} type="CustomLocation" --location {location} '
        "--enabled {enabled} --expiration {expiration} --tags {tags} "
        "--ssh-public-key {sshPublicKey} --resource-group {resourceGroup} "
        "--virtual-machine-name {virtualMachineName}",
        checks=checks,
    )


def step_update(test, checks=None):
    """VirtualMachine console update operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud virtualmachine console update "
        "--enabled {enabled} --expiration {newExpiration}  "
        "--ssh-public-key {sshPublicKey} --tags {tagsUpdate} "
        "--resource-group {resourceGroup} --virtual-machine-name {virtualMachineName}",
        checks=checks,
    )


def step_show(test, checks=None):
    """VirtualMachine console show operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud virtualmachine console show "
        "--resource-group {resourceGroup} --virtual-machine-name {virtualMachineName}",
        checks=checks,
    )


def step_list(test, checks=None):
    """VirtualMachine console list operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud virtualmachine console list "
        "--resource-group {resourceGroup} --virtual-machine-name {virtualMachineName}",
        checks=checks,
    )


def step_delete(test, checks=None):
    """VirtualMachine console delete operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud virtualmachine console delete --resource-group {resourceGroup} "
        "--virtual-machine-name {virtualMachineName} --yes",
        checks=checks,
    )


class VirtualMachineConsoleScenarioTest(ScenarioTest):
    """VirtualMachine console scenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "location": CONFIG.get("VIRTUALMACHINE_CONSOLE", "location"),
                "extendedLocation": CONFIG.get(
                    "VIRTUALMACHINE_CONSOLE", "extended_location"
                ),
                "resourceGroup": CONFIG.get("VIRTUALMACHINE_CONSOLE", "resource_group"),
                "tags": CONFIG.get("VIRTUALMACHINE_CONSOLE", "tags"),
                "tagsUpdate": CONFIG.get("VIRTUALMACHINE_CONSOLE", "tags_update"),
                "enabled": CONFIG.get("VIRTUALMACHINE_CONSOLE", "enabled"),
                "expiration": CONFIG.get("VIRTUALMACHINE_CONSOLE", "expiration"),
                "newExpiration": CONFIG.get("VIRTUALMACHINE_CONSOLE", "new_expiration"),
                "sshPublicKey": CONFIG.get("VIRTUALMACHINE_CONSOLE", "ssh_public_key"),
                "virtualMachineName": CONFIG.get(
                    "VIRTUALMACHINE_CONSOLE", "virtual_machine_name"
                ),
            }
        )

    def test_virtualmachineconsole_scenario1(self):
        """test scenario for VirtualMachine console CRUD operations"""
        call_scenario1(self)
