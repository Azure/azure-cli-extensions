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


def call_scenario1(test, bmm_name="bmmScenario1"):
    """Testcase: scenario1"""
    setup_scenario1(test)
    step_show(test, bmm_name, checks=[])
    step_update(test, bmm_name, checks=[])
    step_list_subscription(test, checks=[])
    step_list_resource_group(test, checks=[])
    cleanup_scenario1(test)


def setup_scenario2(test):
    pass


def cleanup_scenario2(test):
    pass


def call_scenario2(test, bmm_name="bmmScenario2"):
    setup_scenario2(test)
    step_run_command(test, bmm_name, checks=[])
    step_run_data_extract(test, bmm_name, checks=[])
    step_run_read_command(test, bmm_name, checks=[])
    cleanup_scenario2(test)


def setup_scenario3(test):
    pass


def cleanup_scenario3(test):
    pass


def call_scenario3(test, bmm_name="bmmScenario3"):
    setup_scenario3(test)
    step_cordon(test, bmm_name, checks=[])
    step_uncordon(test, bmm_name, checks=[])
    cleanup_scenario3(test)


def setup_scenario4(test):
    pass


def cleanup_scenario4(test):
    pass


def call_scenario4(test, bmm_name="bmmScenario4"):
    setup_scenario4(test)
    step_restart(test, bmm_name, checks=[])
    step_power_off(test, bmm_name, checks=[])
    step_start(test, bmm_name, checks=[])
    step_reimage(test, bmm_name, checks=[])
    step_replace(test, bmm_name, checks=[])
    cleanup_scenario4(test)


def setup_scenario5(test):
    pass


def cleanup_scenario5(test):
    pass


def call_scenario5(test, bmm_name="bmmScenario5"):
    setup_scenario5(test)
    step_run_data_extracts_restricted(test, bmm_name, checks=[])
    cleanup_scenario5(test)


def step_show(test, bmm_name, checks=None):
    """BareMetalMachine show operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud baremetalmachine show --name {"
        + bmm_name
        + "} --resource-group {resourceGroup}"
    )


def step_update(test, bmm_name, checks=None):
    """BareMetalMachine update operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud baremetalmachine update --name {"
        + bmm_name
        + "} --tags {tagsUpdate} --machine-details {machineDetails} --resource-group {resourceGroup}"
    )


def step_list_subscription(test, checks=None):
    """BareMetalMachine list by subscription operation"""
    if checks is None:
        checks = []
    test.cmd("az networkcloud baremetalmachine list --top 10")


def step_list_resource_group(test, checks=None):
    """BareMetalMachine list by resource group operation"""
    if checks is None:
        checks = []
    test.cmd("az networkcloud baremetalmachine list --resource-group {resourceGroup}")


def step_run_command(test, bmm_name, checks=None):
    """BareMetalMachine run command operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud baremetalmachine run-command --name {"
        + bmm_name
        + "} --resource-group {resourceGroup} --arguments {runCommandArguments} --limit-time-seconds {limitTimeSeconds} --script {script}"
    )


def step_run_data_extract(test, bmm_name, checks=None):
    """BareMetalMachine run data extract operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud baremetalmachine run-data-extract --name {"
        + bmm_name
        + "} --resource-group {resourceGroup} --limit-time-seconds {limitTimeSeconds} --commands {dataExtractCommands}"
    )


def step_run_data_extracts_restricted(test, bmm_name, checks=None):
    """BareMetalMachine run data extracts restricted operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud baremetalmachine run-data-extracts-restricted --name {"
        + bmm_name
        + "} --resource-group {resourceGroup} --limit-time-seconds {limitTimeSeconds} --commands {dataExtractsRestrictedCommands}"
    )


def step_run_read_command(test, bmm_name, checks=None):
    """BareMetalMachine run read command operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud baremetalmachine run-read-command --name {"
        + bmm_name
        + "} --resource-group {resourceGroup} --limit-time-seconds {limitTimeSeconds} --commands {runReadCommands}"
    )


def step_cordon(test, bmm_name, checks=None):
    """BareMetalMachine cordon operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud baremetalmachine cordon --evacuate {cordonEvacuate} --name {"
        + bmm_name
        + "} --resource-group {resourceGroup}"
    )


def step_uncordon(test, bmm_name, checks=None):
    """BareMetalMachine uncordon operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud baremetalmachine uncordon --name {"
        + bmm_name
        + "} --resource-group {resourceGroup}"
    )


def step_restart(test, bmm_name, checks=None):
    """BareMetalMachine restart operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud baremetalmachine restart --name {"
        + bmm_name
        + "} --resource-group {resourceGroup}"
    )


def step_power_off(test, bmm_name, checks=None):
    """BareMetalMachine power off operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud baremetalmachine power-off --name {"
        + bmm_name
        + "} --skip-shutdown {skipShutdown} --resource-group {resourceGroup}"
    )


def step_start(test, bmm_name, checks=None):
    """BareMetalMachine start operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud baremetalmachine start --name {"
        + bmm_name
        + "} --resource-group {resourceGroup}"
    )


def step_reimage(test, bmm_name, checks=None):
    """BareMetalMachine reimage operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud baremetalmachine reimage --name {"
        + bmm_name
        + "} --resource-group {resourceGroup}"
    )


def step_replace(test, bmm_name, checks=None):
    """BareMetalMachine replace operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud baremetalmachine replace --name {"
        + bmm_name
        + "} --resource-group {resourceGroup} --bmc-credentials {bmcCreds} --bmc-mac-address {bmcMacAddress} --boot-mac-address {bootMacAddress} --machine-name {newBmmName} --serial-number {serialNumber} --safeguard-mode {safeguardMode} --storage-policy {storagePolicy}"
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
                "tags": CONFIG.get("BAREMETALMACHINE", "tags"),
                "tagsUpdate": CONFIG.get("BAREMETALMACHINE", "tags_update"),
                "machineDetails": CONFIG.get("BAREMETALMACHINE", "machine_details"),
                "resourceGroup": CONFIG.get("BAREMETALMACHINE", "resource_group"),
                "bmmScenario1": CONFIG.get("BAREMETALMACHINE", "bmm_scenario1"),
                "bmmScenario2": CONFIG.get("BAREMETALMACHINE", "bmm_scenario2"),
                "bmmScenario3": CONFIG.get("BAREMETALMACHINE", "bmm_scenario3"),
                "bmmScenario4": CONFIG.get("BAREMETALMACHINE", "bmm_scenario4"),
                "bmmScenario5": CONFIG.get("BAREMETALMACHINE", "bmm_scenario5"),
                "runCommandArguments": CONFIG.get(
                    "BAREMETALMACHINE", "run_command_arguments"
                ),
                "dataExtractCommands": CONFIG.get(
                    "BAREMETALMACHINE", "data_extract_commands"
                ),
                "dataExtractsRestrictedCommands": CONFIG.get(
                    "BAREMETALMACHINE", "data_extract_restricted_commands"
                ),
                "runReadCommands": CONFIG.get("BAREMETALMACHINE", "run_read_commands"),
                "limitTimeSeconds": CONFIG.get(
                    "BAREMETALMACHINE", "limit_time_seconds"
                ),
                "script": CONFIG.get("BAREMETALMACHINE", "script"),
                "cordonEvacuate": CONFIG.get("BAREMETALMACHINE", "cordon_evacuate"),
                "skipShutdown": CONFIG.get("BAREMETALMACHINE", "skip_shutdown"),
                "bmcCreds": CONFIG.get("BAREMETALMACHINE", "bmc_creds"),
                "bmcMacAddress": CONFIG.get("BAREMETALMACHINE", "bmc_mac_address"),
                "bootMacAddress": CONFIG.get("BAREMETALMACHINE", "boot_mac_address"),
                "serialNumber": CONFIG.get("BAREMETALMACHINE", "serial_number"),
                "newBmmName": CONFIG.get("BAREMETALMACHINE", "new_bmm_name"),
                "validationCategory": CONFIG.get(
                    "BAREMETALMACHINE", "validation_category"
                ),
                "safeguardMode": CONFIG.get("BAREMETALMACHINE", "safeguard_mode"),
                "storagePolicy": CONFIG.get("BAREMETALMACHINE", "storage_policy"),
            }
        )

    @AllowLargeResponse()
    def test_bmm_crud_scenario1(self):
        """test scenario for BareMetalMachine CRUD operations"""
        call_scenario1(self, "bmmScenario1")

    @AllowLargeResponse()
    def test_bmm_commands_scenario1(self):
        """test scenario for BareMetalMachine run command operations"""
        call_scenario2(self, "bmmScenario2")

    @AllowLargeResponse()
    def test_bmm_cordon_scenario1(self):
        """test scenario for BareMetalMachine cordon operations"""
        call_scenario3(self, "bmmScenario3")

    # Power, reimage, and replace are mutually exclusive and cannot be simultaneously ran on the same BMM
    def test_bmm_power_reimage_replace_scenario1(self):
        """test scenario for BareMetalMachine power, reimage, and replace operations"""
        call_scenario4(self, "bmmScenario4")

    @AllowLargeResponse()
    def test_bmm_run_data_extracted_scenario1(self):
        """test scenario for BareMetalMachine run data extracted operations"""
        call_scenario5(self, "bmmScenario5")
