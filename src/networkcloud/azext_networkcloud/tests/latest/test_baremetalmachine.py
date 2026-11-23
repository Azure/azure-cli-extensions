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
from azure.cli.testsdk.checkers import NoneCheck
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

from .config import CONFIG
from .utils.output_checks import ResourceOutputChecker, attr


def setup_scenario1(test):
    """Env setup_scenario1"""
    pass


def cleanup_scenario1(test):
    """Env cleanup_scenario1"""
    pass


def call_scenario1(test):
    """Testcase: scenario1"""
    setup_scenario1(test)
    step_show(
        test,
        checks=[
            test.check("name", attr(test, "bmmScenario1")),
            test.exists("id"),
            test.check("bmcMacAddress", attr(test, "bmcMacAddressScenario1")),
            test.check("bootMacAddress", attr(test, "bootMacAddressScenario1")),
            test.check("serialNumber", attr(test, "serialNumberScenario1")),
        ],
    )
    step_update(
        test,
        checks=[test.check("machineDetails", attr(test, "machineDetails"))],
    )
    step_list_subscription(test)
    step_list_resource_group(test)
    cleanup_scenario1(test)


def setup_scenario2(test):
    pass


def cleanup_scenario2(test):
    pass


def call_scenario2(test):
    setup_scenario2(test)
    step_run_command(test, checks=[NoneCheck()])
    step_run_data_extract(test, checks=[NoneCheck()])
    step_run_read_command(test, checks=[NoneCheck()])
    cleanup_scenario2(test)


def setup_scenario3(test):
    pass


def cleanup_scenario3(test):
    pass


def call_scenario3(test):
    setup_scenario3(test)
    step_cordon(test, checks=[test.check("status", attr(test, "operationStatus"))])
    step_uncordon(test, checks=[test.check("status", attr(test, "operationStatus"))])
    cleanup_scenario3(test)


def setup_scenario4(test):
    pass


def cleanup_scenario4(test):
    pass


def call_scenario4(test):
    setup_scenario4(test)
    step_restart(test, checks=[test.check("status", attr(test, "operationStatus"))])
    step_power_off(test, checks=[test.check("status", attr(test, "operationStatus"))])
    step_start(test, checks=[test.check("status", attr(test, "operationStatus"))])
    step_reimage(test, checks=[test.check("status", attr(test, "operationStatus"))])
    step_replace(test, checks=[test.check("status", attr(test, "operationStatus"))])
    cleanup_scenario4(test)


def setup_scenario5(test):
    pass


def cleanup_scenario5(test):
    pass


def call_scenario5(test):
    setup_scenario5(test)
    step_run_data_extracts_restricted(test, checks=[NoneCheck()])
    cleanup_scenario5(test)


def step_show(test, checks=None):
    """BareMetalMachine show operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud baremetalmachine show --name {bmmScenario1} "
        "--resource-group {resourceGroup}",
        checks=checks,
    )


def step_update(test, checks=None):
    """BareMetalMachine update operation"""
    if checks is None:
        checks = ResourceOutputChecker().build_update_checks().get_checks()
    test.cmd(
        "az networkcloud baremetalmachine update --name {bmmScenario1} "
        "--tags {tagsUpdate} --machine-details {machineDetails} --resource-group {resourceGroup}",
        checks=checks,
    )


def step_list_subscription(test, checks=None):
    """BareMetalMachine list by subscription operation"""
    if checks is None:
        checks = []
    test.cmd("az networkcloud baremetalmachine list --top 10", checks=checks)


def step_list_resource_group(test, checks=None):
    """BareMetalMachine list by resource group operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud baremetalmachine list --resource-group {resourceGroup}",
        checks=checks,
    )


def step_run_command(test, checks=None):
    """BareMetalMachine run command operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud baremetalmachine run-command --name {bmmScenario2} "
        "--resource-group {resourceGroup} --arguments {runCommandArguments} --limit-time-seconds {limitTimeSeconds} --script {script}",
        checks=checks,
    )


def step_run_data_extract(test, checks=None):
    """BareMetalMachine run data extract operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud baremetalmachine run-data-extract --name {bmmScenario2} "
        "--resource-group {resourceGroup} --limit-time-seconds {limitTimeSeconds} --commands {dataExtractCommands}",
        checks=checks,
    )


def step_run_data_extracts_restricted(test, checks=None):
    """BareMetalMachine run data extracts restricted operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud baremetalmachine run-data-extracts-restricted --name {bmmScenario5} "
        "--resource-group {resourceGroup} --limit-time-seconds {limitTimeSeconds} --commands {dataExtractsRestrictedCommands}",
        checks=checks,
    )


def step_run_read_command(test, checks=None):
    """BareMetalMachine run read command operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud baremetalmachine run-read-command --name {bmmScenario2} "
        "--resource-group {resourceGroup} --limit-time-seconds {limitTimeSeconds} --commands {runReadCommands}",
        checks=checks,
    )


def step_cordon(test, checks=None):
    """BareMetalMachine cordon operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud baremetalmachine cordon --evacuate {cordonEvacuate} "
        "--name {bmmScenario3} --resource-group {resourceGroup}",
        checks=checks,
    )


def step_uncordon(test, checks=None):
    """BareMetalMachine uncordon operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud baremetalmachine uncordon --name {bmmScenario3} "
        "--resource-group {resourceGroup}",
        checks=checks,
    )


def step_restart(test, checks=None):
    """BareMetalMachine restart operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud baremetalmachine restart --name {bmmScenario4} "
        "--resource-group {resourceGroup}",
        checks=checks,
    )


def step_power_off(test, checks=None):
    """BareMetalMachine power off operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud baremetalmachine power-off --name {bmmScenario4} "
        "--skip-shutdown {skipShutdown} --resource-group {resourceGroup}",
        checks=checks,
    )


def step_start(test, checks=None):
    """BareMetalMachine start operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud baremetalmachine start --name {bmmScenario4} "
        "--resource-group {resourceGroup}",
        checks=checks,
    )


def step_reimage(test, checks=None):
    """BareMetalMachine reimage operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud baremetalmachine reimage --name {bmmScenario4} "
        "--resource-group {resourceGroup}",
        checks=checks,
    )


def step_replace(test, checks=None):
    """BareMetalMachine replace operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud baremetalmachine replace --name {bmmScenario4} "
        "--resource-group {resourceGroup} --bmc-credentials {bmcCreds} --bmc-mac-address {bmcMacAddress} --boot-mac-address {bootMacAddress} --machine-name {newBmmName} --serial-number {serialNumber} --safeguard-mode {safeguardMode} --storage-policy {storagePolicy}",
        checks=checks,
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
                "bmcMacAddressScenario1": CONFIG.get(
                    "BAREMETALMACHINE", "bmc_mac_address_scenario1"
                ),
                "bootMacAddressScenario1": CONFIG.get(
                    "BAREMETALMACHINE", "boot_mac_address_scenario1"
                ),
                "serialNumberScenario1": CONFIG.get(
                    "BAREMETALMACHINE", "serial_number_scenario1"
                ),
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
                "operationStatus": CONFIG.get("BAREMETALMACHINE", "operation_status"),
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

    # Power, reimage, and replace are mutually exclusive and cannot be simultaneously ran on the same BMM
    def test_bmm_power_reimage_replace_scenario1(self):
        """test scenario for BareMetalMachine power, reimage, and replace operations"""
        call_scenario4(self)

    @AllowLargeResponse()
    def test_bmm_run_data_extracted_scenario1(self):
        """test scenario for BareMetalMachine run data extracted operations"""
        call_scenario5(self)
