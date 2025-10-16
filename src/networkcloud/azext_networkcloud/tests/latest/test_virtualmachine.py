# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

# customizations-ignore-deprecations={"virtualmachine_create": ["--nd", "--network-data", "--ud", "--user-data"]}
# customizations-ignore-removed={"virtualmachine_create": ["--ssh-public-keys"], "virtualmachine_update": ["--ssh-public-keys"]}
# customizations-custom-params={"virtualmachine_create":["--ssh-key-values"]}

"""
VirtualMachine tests scenarios
"""

from azure.cli.testsdk import ResourceGroupPreparer, ScenarioTest
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

from .config import CONFIG


def setup_scenario1(test):
    """Env setup_scenario1"""
    pass


def cleanup_scenario1(test):
    """Env cleanup_scenario1"""
    pass


def setup_scenario(test):
    """Env setup_scenario"""
    pass


def cleanup_scenario(test):
    """Env cleanup_scenario"""
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
    step_update_scenario1(
        test,
        checks=[
            test.check("tags", "{tagsUpdate}"),
            test.check("provisioningState", "Succeeded"),
        ],
    )
    step_show(test, checks=[])
    step_list_subscription(test, checks=[])
    step_list_resource_group(test, checks=[])
    step_reimage(test, checks=[])
    step_restart(test, checks=[])
    step_power_off(test, checks=[])
    step_start(test, checks=[])
    step_assign_relay(test, checks=[])
    step_delete(test, checks=[])
    cleanup_scenario1(test)


def call_scenario2(test):
    """# Testcase: scenario2"""
    setup_scenario(test)
    step_create_with_userassigned_identity(
        test,
        checks=[
            test.check("name", "{name}"),
            test.check("provisioningState", "Succeeded"),
        ],
    )
    step_update_UA_to_SA_managedidentity_scenario1(
        test,
        checks=[
            test.check("tags", "{tagsUpdate}"),
            test.check("provisioningState", "Succeeded"),
        ],
    )
    step_update_scenario2(
        test,
        checks=[
            test.check("tags", "{tagsUpdate}"),
            test.check("provisioningState", "Succeeded"),
        ],
    )
    step_show(test, checks=[])
    step_list_resource_group(test, checks=[])
    step_delete(test, checks=[])
    cleanup_scenario(test)


def call_scenario3(test):
    """# Testcase: scenario3"""
    setup_scenario(test)
    step_create_systemassigned_managedidentity(
        test,
        checks=[
            test.check("name", "{name}"),
            test.check("provisioningState", "Succeeded"),
        ],
    )
    step_update_UA_to_SA_managedidentity_scenario2(
        test,
        checks=[
            test.check("tags", "{tagsUpdate}"),
            test.check("provisioningState", "Succeeded"),
        ],
    )
    step_show(test, checks=[])
    step_list_resource_group(test, checks=[])
    step_delete(test, checks=[])
    cleanup_scenario(test)


def call_scenario4(test):
    """# Testcase: scenario4"""
    setup_scenario1(test)
    step_create_UA_SA_managedidentity(
        test,
        checks=[
            test.check("name", "{name}"),
            test.check("provisioningState", "Succeeded"),
        ],
    )
    step_show(test, checks=[])
    step_list_resource_group(test, checks=[])
    step_delete(test, checks=[])
    cleanup_scenario1(test)


def step_create(test, checks=None):
    """VirtualMachine create operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud virtualmachine create --name {name} --extended-location "
        'name={extendedLocation} type="CustomLocation" --location {location} '
        "--console-extended-location "
        'name={extendedLocation} type="CustomLocation" --location {location} '
        "--admin-username {adminUserName} --boot-method {bootMethod} "
        "--cloud-services-network-attachment  attached-network-id={attachedNetworkID} "
        "--cpu-cores {cpuCores} "
        "--memory-size {memorySize} --network-attachments {networkAttachments} "
        "--network-data-content {networkDataContent} --placement-hints {placementHints} "
        "--ssh-key-values {sshKeyValues} --storage-profile disk-size={diskSize} create-option={createOpt} "
        " delete-option={deleteOpt} --tags {tags} "
        "--user-data-content {userDataContent} --vm-device-model {vmDeviceModel} "
        "--vm-image {vmName} --vm-image-repository-credentials password={password} "
        "registry-url={registryURL} username={userName} --resource-group {rg}",
        checks=checks,
    )


def step_create_with_userassigned_identity(test, checks=None):
    """VirtualMachine create operation with user assigned managed identity"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud virtualmachine create --name {name} --extended-location "
        'name={extendedLocation} type="CustomLocation" --location {location} '
        "--ce-location "
        'name={extendedLocation} type="CustomLocation" --location {location} '
        "--admin-username {adminUserName} --boot-method {bootMethod} "
        "--cloud-services-network-attachment  attached-network-id={attachedNetworkID} "
        "--cpu-cores {cpuCores} "
        "--memory-size-gb {memorySize} --na {networkAttachments} "
        "--ndc {networkDataContent} --ph {placementHints} "
        "--ssh-key-values {sshKeyValues} --storage-profile disk-size={diskSize} create-option={createOpt} "
        " delete-option={deleteOpt} --tags {tags} "
        "--udc {userDataContent} --vm-device-model {vmDeviceModel} "
        "--vm-image {vmName} --vmi-creds password={password} "
        "registry-url={registryURL} username={userName} --resource-group {rg} --user-assigned {miUserAssigned}",
        checks=checks,
    )


def step_create_systemassigned_managedidentity(test, checks=None):
    """VirtualMachine create operation with user assigned managed identity"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud virtualmachine create --virtual-machine-name {name} --extended-location "
        'name={extendedLocation} type="CustomLocation" --location {location} '
        "--admin-username {adminUserName} --boot-method {bootMethod} "
        "--csn  attached-network-id={attachedNetworkID} "
        "--cpu-cores {cpuCores} "
        "--memory-size-gib {memorySize} --network-attachments {networkAttachments} "
        "--network-data-content {networkDataContent} --placement-hints {placementHints} "
        "--ssh-key-values {sshKeyValues} --storage-profile disk-size={diskSize} create-option={createOpt} "
        " delete-option={deleteOpt} --tags {tags} "
        "--user-data-content {userDataContent} --vm-device-model {vmDeviceModel} "
        "--vm-image {vmName} --vm-image-repository-credentials password={password} "
        "registry-url={registryURL} username={userName} --resource-group {rg} --system-assigned",
        checks=checks,
    )


def step_create_UA_SA_managedidentity(test, checks=None):
    """VirtualMachine create operation with system assigned and user assigned managed identity"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud virtualmachine create --name {name} --extended-location "
        'name={extendedLocation} type="CustomLocation" --location {location} '
        "--admin-username {adminUserName} --boot-method {bootMethod} "
        "--cloud-services-network-attachment  attached-network-id={attachedNetworkID} "
        "--cpu-cores {cpuCores} "
        "--memory-size {memorySize} --network-attachments {networkAttachments} "
        "--network-data-content {networkDataContent} --placement-hints {placementHints} "
        "--ssh-key-values {sshKeyValues} --storage-profile disk-size={diskSize} create-option={createOpt} "
        " delete-option={deleteOpt} --tags {tags} "
        "--user-data-content {userDataContent} --vm-device-model {vmDeviceModel} "
        "--vm-image {vmName} --vm-image-repository-credentials password={password} "
        "registry-url={registryURL} username={userName} --resource-group {rg} "
        "--mi-user-assigned {miUserAssigned} --mi-system-assigned",
        checks=checks,
    )


def step_show(test, checks=None):
    """VirtualMachine show operation"""
    if checks is None:
        checks = []
    test.cmd("az networkcloud virtualmachine show --name {name} --resource-group {rg}")


def step_reimage(test, checks=None):
    """VirtualMachine reimage operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud virtualmachine reimage --name {name} --resource-group {rg} "
    )


def step_restart(test, checks=None):
    """VirtualMachine restart operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud virtualmachine restart --name {name} --resource-group {rg} "
    )


def step_power_off(test, checks=None):
    """VirtualMachine power off operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud virtualmachine power-off --name {name} --resource-group {rg} "
        '--skip-shutdown "True"'
    )


def step_start(test, checks=None):
    """VirtualMachine start operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud virtualmachine start --name {name} --resource-group {rg} "
    )


def step_assign_relay(test, checks=None):
    """VirtualMachine assign relay operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud virtualmachine assign-relay --name {name} --resource-group {rg}  --machine-id {machineID} --relay-type {relayType} "
    )


def step_delete(test, checks=None):
    """VirtualMachine delete operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud virtualmachine delete --name {name} --resource-group {rg} -y"
    )


def step_list_resource_group(test, checks=None):
    """VirtualMachine list by resource group operation"""
    if checks is None:
        checks = []
    test.cmd("az networkcloud virtualmachine list --resource-group {rg}")


def step_list_subscription(test, checks=None):
    """VirtualMachine list by subscription operation"""
    if checks is None:
        checks = []
    test.cmd("az networkcloud virtualmachine list")


def step_update_scenario1(test, checks=None):
    """VirtualMachine update operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud virtualmachine update --name {name} "
        "--vm-image-repository-credentials password={password} registry-url={registryURL} username={userName} "
        "--tags {tagsUpdate} --resource-group {rg} --vmi-creds password={password} "
        "registry-url={registryURL} username={userName} --user-assigned {miUserAssigned}"
    )


def step_update_scenario2(test, checks=None):
    """VirtualMachine update operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud virtualmachine update --name {name} "
        "--vm-image-repository-credentials password={password} registry-url={registryURL} username={userName} "
        "--tags {tagsUpdate} --resource-group {rg} --vmi-creds password={password} "
        "registry-url={registryURL} username={userName} --mi-user-assigned {miUserAssigned}"
    )


def step_update_UA_to_SA_managedidentity_scenario1(test, checks=None):
    """VirtualMachine update operation UA to SA"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud virtualmachine update --virtual-machine-name {name} "
        "--vm-image-repository-credentials password={password} registry-url={registryURL} username={userName} "
        "--tags {tagsUpdate} --resource-group {rg} "
        "--mi-system-assigned"
    )


def step_update_UA_to_SA_managedidentity_scenario2(test, checks=None):
    """VirtualMachine update operation UA to SA"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud virtualmachine update --virtual-machine-name {name} "
        "--vm-image-repository-credentials password={password} registry-url={registryURL} username={userName} "
        "--tags {tagsUpdate} --resource-group {rg} "
        "--system-assigned"
    )


class VirtualMachineScenarioTest(ScenarioTest):
    """VirtualMachine scenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": self.create_random_name(prefix="cliTestVM", length=24),
                "location": CONFIG.get("VIRTUALMACHINE", "location"),
                "extendedLocation": CONFIG.get("VIRTUALMACHINE", "extended_location"),
                "adminUserName": CONFIG.get("VIRTUALMACHINE", "admin_user_name"),
                "bootMethod": CONFIG.get("VIRTUALMACHINE", "boot_method"),
                "attachedNetworkID": CONFIG.get(
                    "VIRTUALMACHINE", "attached_network_id"
                ),
                "cpuCores": CONFIG.get("VIRTUALMACHINE", "cpu_cores"),
                "memorySize": CONFIG.get("VIRTUALMACHINE", "memory_size"),
                "networkAttachments": CONFIG.get(
                    "VIRTUALMACHINE", "network_attachments"
                ),
                "networkDataContent": CONFIG.get(
                    "VIRTUALMACHINE", "network_data_content"
                ),
                "placementHints": CONFIG.get("VIRTUALMACHINE", "placement_hints"),
                "sshKeyValues": CONFIG.get("VIRTUALMACHINE", "ssh_key_values"),
                "diskSize": CONFIG.get("VIRTUALMACHINE", "disk_size"),
                "createOpt": CONFIG.get("VIRTUALMACHINE", "create_opt"),
                "deleteOpt": CONFIG.get("VIRTUALMACHINE", "delete_opt"),
                "tags": CONFIG.get("VIRTUALMACHINE", "tags"),
                "tagsUpdate": CONFIG.get("VIRTUALMACHINE", "tags_update"),
                "userDataContent": CONFIG.get("VIRTUALMACHINE", "user_data_content"),
                "vmDeviceModel": CONFIG.get("VIRTUALMACHINE", "vm_device_model"),
                "vmName": CONFIG.get("VIRTUALMACHINE", "vm_name"),
                "password": CONFIG.get("VIRTUALMACHINE", "password"),
                "registryURL": CONFIG.get("VIRTUALMACHINE", "registry_url"),
                "userName": CONFIG.get("VIRTUALMACHINE", "user_name"),
                "miUserAssigned": CONFIG.get("VIRTUALMACHINE", "mi_user_assigned"),
                "machineID": CONFIG.get("VIRTUALMACHINE", "machine_id"),
                "relayType": CONFIG.get("VIRTUALMACHINE", "relay_type"),
            }
        )

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix="clitest_rg"[:7], key="rg", parameter_name="rg")
    def test_virtualmachine_scenario1(self):
        """test scenario for VirtualMachine CRUD operations"""
        call_scenario1(self)

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix="clitest_rg"[:7], key="rg", parameter_name="rg")
    def test_virtualmachine_scenario2(self):
        """test scenario for VirtualMachine operations with userassigned identity"""
        call_scenario2(self)

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix="clitest_rg"[:7], key="rg", parameter_name="rg")
    def test_virtualmachine_scenario3(self):
        """test scenario for VirtualMachine operations with system assigned identity"""
        call_scenario3(self)

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix="clitest_rg"[:7], key="rg", parameter_name="rg")
    def test_virtualmachine_scenario4(self):
        """test scenario for VirtualMachine operations with UA and system assigned identity"""
        call_scenario4(self)
