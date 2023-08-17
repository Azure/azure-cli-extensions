# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
BareMetalMachine test scenarios
"""

from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

from .config import CONFIG


def setup_scenario1(test):
    """Env setup_scenario1"""
    pass


def cleanup_scenario1(test):
    """Env cleanup_scenario1"""
    pass


def call_scenario1(test):
    """Testcase: scenario1"""
    setup_scenario1(test)
    step_show(test, checks=[])
    step_update(test, checks=[])
    step_list_subscription(test, checks=[])
    step_list_resource_group(test, checks=[])
    cleanup_scenario1(test)


def setup_scenario2(test):
    pass


def cleanup_scenario2(test):
    pass


def call_scenario2(test):
    setup_scenario2(test)
    step_run_command(test, checks=[])
    step_run_data_extract(test, checks=[])
    step_run_read_command(test, checks=[])
    cleanup_scenario2(test)


def setup_scenario3(test):
    pass


def cleanup_scenario3(test):
    pass


def call_scenario3(test):
    setup_scenario3(test)
    step_cordon(test, checks=[])
    step_uncordon(test, checks=[])
    cleanup_scenario3(test)


def setup_scenario4(test):
    pass


def cleanup_scenario4(test):
    pass


def call_scenario4(test):
    setup_scenario4(test)
    step_restart(test, checks=[])
    step_power_off(test, checks=[])
    step_start(test, checks=[])
    cleanup_scenario4(test)


def setup_scenario5(test):
    pass


def cleanup_scenario5(test):
    pass


def call_scenario5(test):
    setup_scenario5(test)
    step_reimage(test, checks=[])
    cleanup_scenario5(test)


def setup_scenario6(test):
    pass


def cleanup_scenario6(test):
    pass


def call_scenario6(test):
    setup_scenario6(test)
    step_replace(test, checks=[])
    cleanup_scenario6(test)


def setup_scenario7(test):
    pass


def cleanup_scenario7(test):
    pass


def call_scenario7(test):
    setup_scenario7(test)
    step_validate_hardware(test, checks=[])
    cleanup_scenario7(test)


def step_show(test, checks=None):
    """BareMetalMachine show operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud baremetalmachine show --name {nameCrud} --resource-group {rgCrud}"
    )


def step_update(test, checks=None):
    """BareMetalMachine update operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud baremetalmachine update --name {nameCrud} --tags {tagsUpdate} --machine-details {machineDetails} --resource-group {rgCrud}"
    )


def step_list_subscription(test, checks=None):
    """BareMetalMachine list by subscription operation"""
    if checks is None:
        checks = []
    test.cmd("az networkcloud baremetalmachine list")


def step_list_resource_group(test, checks=None):
    """BareMetalMachine list by resource group operation"""
    if checks is None:
        checks = []
    test.cmd("az networkcloud baremetalmachine list --resource-group {rgCrud}")


def step_run_command(test, checks=None):
    """BareMetalMachine run command operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud baremetalmachine run-command --name {nameRunCommand} --resource-group {rgCommands} --arguments {runCommandArguments} --limit-time-seconds {limitTimeSeconds} --script {script}"
    )


def step_run_data_extract(test, checks=None):
    """BareMetalMachine run data extract operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud baremetalmachine run-data-extract --name {nameRunDataExtract} --resource-group {rgCommands} --limit-time-seconds {limitTimeSeconds} --commands {dataExtractCommands}"
    )


def step_run_read_command(test, checks=None):
    """BareMetalMachine run read command operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud baremetalmachine run-read-command --name {nameRunReadCommand} --resource-group {rgCommands} --limit-time-seconds {limitTimeSeconds} --commands {runReadCommands}"
    )


def step_cordon(test, checks=None):
    """BareMetalMachine cordon operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud baremetalmachine cordon --evacuate {cordonEvacuate} --name {nameCordon} --resource-group {rgCordon}"
    )


def step_uncordon(test, checks=None):
    """BareMetalMachine uncordon operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud baremetalmachine uncordon --name {nameCordon} --resource-group {rgCordon}"
    )


def step_restart(test, checks=None):
    """BareMetalMachine restart operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud baremetalmachine restart --name {nameRestart} --resource-group {rgPower}"
    )


def step_power_off(test, checks=None):
    """BareMetalMachine power off operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud baremetalmachine power-off --name {namePower} --skip-shutdown {skipShutdown} --resource-group {rgPower}"
    )


def step_start(test, checks=None):
    """BareMetalMachine start operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud baremetalmachine start --name {namePower} --resource-group {rgPower}"
    )


def step_reimage(test, checks=None):
    """BareMetalMachine reimage operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud baremetalmachine reimage --name {nameReimage} --resource-group {rgValidate}"
    )


def step_replace(test, checks=None):
    """BareMetalMachine replace operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud baremetalmachine replace --name {nameReplace} --resource-group {rgReplace} --bmc-credentials {bmcCreds} --bmc-mac-address {bmcMacAddress} --boot-mac-address {bootMacAddress} --machine-name {newBmmName} --serial-number {serialNumber}"
    )


def step_validate_hardware(test, checks=None):
    """BareMetalMachine validate hardware operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud baremetalmachine validate-hardware --name {nameValidate} --resource-group {rgValidate} --validation-category {validationCategory}"
    )


class BareMetalMachineScenarioTest1(ScenarioTest):
    """BMMScenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                # We are unable to create hydrated resources from the CLI,
                # so we are using existing baremetalmachine names and
                # resource groups.
                "nameCrud": CONFIG.get("BAREMETALMACHINE", "name_crud"),
                "rgCrud": CONFIG.get("BAREMETALMACHINE", "resource_group_crud"),
                "tags": CONFIG.get("BAREMETALMACHINE", "tags"),
                "tagsUpdate": CONFIG.get("BAREMETALMACHINE", "tags_update"),
                "machineDetails": CONFIG.get("BAREMETALMACHINE", "machine_details"),
                "nameRunCommand": CONFIG.get("BAREMETALMACHINE", "name_run_command"),
                "nameRunDataExtract": CONFIG.get(
                    "BAREMETALMACHINE", "name_run_data_extract"
                ),
                "nameRunReadCommand": CONFIG.get(
                    "BAREMETALMACHINE", "name_run_read_command"
                ),
                "runCommandArguments": CONFIG.get(
                    "BAREMETALMACHINE", "run_command_arguments"
                ),
                "dataExtractCommands": CONFIG.get(
                    "BAREMETALMACHINE", "data_extract_commands"
                ),
                "runReadCommands": CONFIG.get("BAREMETALMACHINE", "run_read_commands"),
                "rgCommands": CONFIG.get("BAREMETALMACHINE", "resource_group_commands"),
                "limitTimeSeconds": CONFIG.get(
                    "BAREMETALMACHINE", "limit_time_seconds"
                ),
                "script": CONFIG.get("BAREMETALMACHINE", "script"),
                "nameCordon": CONFIG.get("BAREMETALMACHINE", "name_cordon"),
                "rgCordon": CONFIG.get("BAREMETALMACHINE", "resource_group_cordon"),
                "cordonEvacuate": CONFIG.get("BAREMETALMACHINE", "cordon_evacuate"),
                "nameRestart": CONFIG.get("BAREMETALMACHINE", "name_restart"),
                "namePower": CONFIG.get("BAREMETALMACHINE", "name_power"),
                "rgPower": CONFIG.get("BAREMETALMACHINE", "resource_group_power"),
                "skipShutdown": CONFIG.get("BAREMETALMACHINE", "skip_shutdown"),
                "nameReimage": CONFIG.get("BAREMETALMACHINE", "name_reimage"),
                "nameReplace": CONFIG.get("BAREMETALMACHINE", "name_replace"),
                "nameValidate": CONFIG.get("BAREMETALMACHINE", "name_validate"),
                "rgValidate": CONFIG.get("BAREMETALMACHINE", "resource_group_validate"),
                "rgReplace": CONFIG.get("BAREMETALMACHINE", "resource_group_replace"),
                "bmcCreds": CONFIG.get("BAREMETALMACHINE", "bmc_creds"),
                "bmcMacAddress": CONFIG.get("BAREMETALMACHINE", "bmc_mac_address"),
                "bootMacAddress": CONFIG.get("BAREMETALMACHINE", "boot_mac_address"),
                "serialNumber": CONFIG.get("BAREMETALMACHINE", "serial_number"),
                "newBmmName": CONFIG.get("BAREMETALMACHINE", "new_bmm_name"),
                "validationCategory": CONFIG.get(
                    "BAREMETALMACHINE", "validation_category"
                ),
            }
        )

    @AllowLargeResponse()
    def test_bmm_crud_scenario1(self):
        """test scenario for BareMetalMachine CRUD operations"""
        call_scenario1(self)

    @AllowLargeResponse()
    def test_bmm_commands_scenario1(self):
        """test scenario for BareMetalMachine run command operations"""
        call_scenario2(self)

    @AllowLargeResponse()
    def test_bmm_cordon_scenario1(self):
        """test scenario for BareMetalMachine cordon operations"""
        call_scenario3(self)

    def test_bmm_power_scenario1(self):
        """test scenario for BareMetalMachine power operations"""
        call_scenario4(self)

    def test_bmm_reimage_scenario1(self):
        """test scenario for BareMetalMachine reimage operation"""
        call_scenario5(self)

    def test_bmm_replace_scenario1(self):
        """test scenario for BareMetalMachine replace operation"""
        call_scenario6(self)
