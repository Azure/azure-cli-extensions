# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=unused-argument,too-many-lines

from getpass import getpass
from azure.cli.command_modules.acs._client_factory import get_resources_client
from azure.cli.core.azclierror import (
    UnrecognizedArgumentError,
    RequiredArgumentMissingError,
    MutuallyExclusiveArgumentError,
    InvalidArgumentValueError,
)
from azure.cli.core.util import sdk_no_wait
from azure.core.exceptions import ResourceNotFoundError  # type: ignore
from msrestazure.tools import is_valid_resource_id
from .scvmm_utils import get_resource_id, get_extended_location
from .scvmm_constants import (
    AVAILABILITYSET_RESOURCE_TYPE,
    SCVMM_NAMESPACE,
    CLOUD_RESOURCE_TYPE,
    VMMSERVER_RESOURCE_TYPE,
    VIRTUALNETWORK_RESOURCE_TYPE,
    VMTEMPLATE_RESOURCE_TYPE,
    INVENTORY_ITEM_TYPE,
    MACHINE_KIND_SCVMM,
    DEFAULT_VMMSERVER_PORT,
    EXTENDED_LOCATION_NAMESPACE,
    CUSTOM_LOCATION_RESOURCE_TYPE,
    MACHINES_RESOURCE_TYPE,
    EXTENSIONS_RESOURCE_TYPE,
    HCRP_NAMESPACE,
    VM_SYSTEM_ASSIGNED_INDENTITY_TYPE,
    GUEST_AGENT_PROVISIONING_ACTION_INSTALL,
    NAME_PARAMETER,
    NETWORK,
    IPV4_ADDRESS_TYPE,
    IPV6_ADDRESS_TYPE,
    MAC_ADDRESS_TYPE,
    MAC_ADDRESS,
    TEMPLATE_DISK_ID,
    DISK_SIZE,
    BUS_TYPE,
    BUS,
    LUN,
    VHD_TYPE,
    QOS_NAME,
    QOS_ID,
    BusType,
    VHDType,
)
from .vendored_sdks.scvmm.models import (
    Cloud,
    HardwareProfile,
    HardwareProfileUpdate,
    InfrastructureProfile,
    OsProfileForVMInstance,
    VirtualMachineInstance,
    VirtualMachineInstanceUpdate,
    VirtualMachineCreateCheckpoint,
    VirtualMachineDeleteCheckpoint,
    VirtualMachineRestoreCheckpoint,
    VirtualMachineTemplate,
    VirtualNetwork,
    VMMServer,
    VMMCredential,
    AllocationMethod,
    NetworkInterface,
    NetworkProfile,
    NetworkInterfaceUpdate,
    NetworkProfileUpdate,
    StorageQoSPolicyDetails,
    VirtualDisk,
    VirtualDiskUpdate,
    StorageProfile,
    StorageProfileUpdate,
    ResourcePatch,
    StopVirtualMachineOptions,
    AvailabilitySetListItem,
    AvailabilitySet,
    GuestAgent,
    GuestCredential,
    HttpProxyConfiguration,
)

from .vendored_sdks.hybridcompute.models import (
    Identity,
    Machine,
    MachineExtension,
    MachineExtensionUpdate,
    MachineUpdate,
)

from .vendored_sdks.scvmm.operations import (
    VmmServersOperations,
    CloudsOperations,
    VirtualNetworksOperations,
    VirtualMachineTemplatesOperations,
    VirtualMachineInstancesOperations,
    VMInstanceGuestAgentsOperations,
    AvailabilitySetsOperations,
    InventoryItemsOperations,
)

from .vendored_sdks.hybridcompute.operations import (
    MachinesOperations,
    MachineExtensionsOperations,
)

from ._client_factory import (
    cf_machine,
    cf_virtual_machine_instance,
)

# region VMMServers


def connect_vmmserver(
    cmd,
    client: VmmServersOperations,
    resource_group_name,
    resource_name,
    custom_location,
    location,
    fqdn=None,
    username=None,
    password=None,
    port=None,
    tags=None,
    no_wait=False,
):

    creds_ok = all(inp is not None for inp in [fqdn, port, username, password])
    while not creds_ok:
        creds = {
            'fqdn': fqdn,
            'port': port,
            'username': username,
            'password': password,
        }
        while not creds['fqdn']:
            print('Please provide vmmserver FQDN or IP address: ', end='')
            creds['fqdn'] = input()
            if not creds['fqdn']:
                print('Parameter is required, please try again')
        while not creds['port']:
            print('Please provide vmmserver port (Default: 8100): ', end='')
            try:
                creds['port'] = input()
                if not creds['port']:
                    creds['port'] = DEFAULT_VMMSERVER_PORT
                creds['port'] = int(f"{creds['port']}")
            except ValueError:
                print('Port must be a number, please try again')
                creds['port'] = None
        while not creds['username']:
            print('Please provide vmmserver username: ', end='')
            creds['username'] = input()
            if not creds['username']:
                print('Parameter is required, please try again')
        while not creds['password']:
            creds['password'] = getpass('Please provide vmmserver password: ')
            if not creds['password']:
                print('Parameter is required, please try again')
            passwdConfim = getpass('Please confirm vmmserver password: ')
            if creds['password'] != passwdConfim:
                print('Passwords do not match, please try again')
                creds['password'] = None
        print('Confirm vmmserver details? [Y/n]: ', end='')
        res = input().lower()
        if res in ['y', '']:
            fqdn, port, username, password = (
                creds['fqdn'],
                creds['port'],
                creds['username'],
                creds['password'],
            )
            creds_ok = True
        elif res != 'n':
            print('Please type y/n or leave empty.')
    assert fqdn

    username_creds = VMMCredential(
        username=username, password=password
    )

    custom_location_id = get_resource_id(
        cmd,
        resource_group_name,
        EXTENDED_LOCATION_NAMESPACE,
        CUSTOM_LOCATION_RESOURCE_TYPE,
        custom_location,
    )

    vmmserver = VMMServer(
        location=location,
        extended_location=get_extended_location(custom_location_id),
        fqdn=fqdn,
        port=port,
        credentials=username_creds,
        tags=tags,
    )

    return sdk_no_wait(
        no_wait,
        client.begin_create_or_update,
        resource_group_name,
        resource_name,
        vmmserver,
    )


def update_vmmserver(
    cmd,
    client: VmmServersOperations,
    resource_group_name,
    resource_name,
    tags=None,
    no_wait=False,
):
    vmmserver_update = ResourcePatch(tags=tags)
    return sdk_no_wait(
        no_wait,
        client.begin_update,
        resource_group_name,
        resource_name,
        vmmserver_update,
    )


def delete_vmmserver(
    cmd,
    client: VmmServersOperations,
    resource_group_name,
    resource_name,
    force=None,
    no_wait=False,
):
    return sdk_no_wait(
        no_wait, client.begin_delete, resource_group_name, resource_name, force
    )


def show_vmmserver(
    cmd, client: VmmServersOperations, resource_group_name, resource_name
):
    return client.get(resource_group_name, resource_name)


def list_vmmserver(cmd, client: VmmServersOperations, resource_group_name=None):
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name)
    return client.list_by_subscription()


# endregion

# region Clouds


def create_cloud(
    cmd,
    client: CloudsOperations,
    resource_group_name,
    resource_name,
    custom_location,
    location,
    vmmserver=None,
    uuid=None,
    inventory_item=None,
    tags=None,
    no_wait=False,
):

    cloud = Cloud(
        location=location,
        extended_location=get_extended_location(custom_location),
        vmm_server_id=vmmserver,
        uuid=uuid,
        inventory_item_id=inventory_item,
        tags=tags,
    )

    return sdk_no_wait(
        no_wait,
        client.begin_create_or_update,
        resource_group_name,
        resource_name,
        cloud,
    )


def update_cloud(
    cmd,
    client: CloudsOperations,
    resource_group_name,
    resource_name,
    tags=None,
    no_wait=False,
):
    cloud_update = ResourcePatch(tags=tags)
    return sdk_no_wait(
        no_wait,
        client.begin_update,
        resource_group_name,
        resource_name,
        cloud_update,
    )


def delete_cloud(
    cmd,
    client: CloudsOperations,
    resource_group_name,
    resource_name,
    force=None,
    no_wait=False,
):
    return sdk_no_wait(
        no_wait, client.begin_delete, resource_group_name, resource_name, force
    )


def show_cloud(cmd, client: CloudsOperations, resource_group_name, resource_name):
    return client.get(resource_group_name, resource_name)


def wait_cloud(cmd, client: CloudsOperations, resource_group_name, cloud_name):
    return client.get(resource_group_name, cloud_name)


def list_cloud(cmd, client: CloudsOperations, resource_group_name=None):
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name)
    return client.list_by_subscription()


# endregion

# region VirtualNetworks


def create_virtual_network(
    cmd,
    client: VirtualNetworksOperations,
    resource_group_name,
    resource_name,
    custom_location,
    location,
    vmmserver=None,
    uuid=None,
    inventory_item=None,
    tags=None,
    no_wait=False,
):
    virtual_network = VirtualNetwork(
        location=location,
        extended_location=get_extended_location(custom_location),
        vmm_server_id=vmmserver,
        uuid=uuid,
        inventory_item_id=inventory_item,
        tags=tags,
    )

    return sdk_no_wait(
        no_wait,
        client.begin_create_or_update,
        resource_group_name,
        resource_name,
        virtual_network,
    )


def update_virtual_network(
    cmd,
    client: VirtualNetworksOperations,
    resource_group_name,
    resource_name,
    tags=None,
    no_wait=False,
):
    virtual_network_update = ResourcePatch(tags=tags)
    return sdk_no_wait(
        no_wait,
        client.begin_update,
        resource_group_name,
        resource_name,
        virtual_network_update,
    )


def delete_virtual_network(
    cmd,
    client: VirtualNetworksOperations,
    resource_group_name,
    resource_name,
    force=None,
    no_wait=False,
):
    return sdk_no_wait(
        no_wait, client.begin_delete, resource_group_name, resource_name, force
    )


def show_virtual_network(
    cmd, client: VirtualNetworksOperations, resource_group_name, resource_name
):
    return client.get(resource_group_name, resource_name)


def list_virtual_network(
    cmd, client: VirtualNetworksOperations, resource_group_name=None
):
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name)
    return client.list_by_subscription()


# endregion

# region VirtualMachineTemplates


def create_vm_template(
    cmd,
    client: VirtualMachineTemplatesOperations,
    resource_group_name,
    resource_name,
    custom_location,
    location,
    vmmserver=None,
    uuid=None,
    inventory_item=None,
    tags=None,
    no_wait=False,
):
    vm_template = VirtualMachineTemplate(
        location=location,
        extended_location=get_extended_location(custom_location),
        vmm_server_id=vmmserver,
        uuid=uuid,
        inventory_item_id=inventory_item,
        tags=tags,
    )

    return sdk_no_wait(
        no_wait,
        client.begin_create_or_update,
        resource_group_name,
        resource_name,
        vm_template,
    )


def update_vm_template(
    cmd,
    client: VirtualMachineTemplatesOperations,
    resource_group_name,
    resource_name,
    tags=None,
    no_wait=False,
):
    vm_template_update = ResourcePatch(tags=tags)
    return sdk_no_wait(
        no_wait,
        client.begin_update,
        resource_group_name,
        resource_name,
        vm_template_update,
    )


def delete_vm_template(
    cmd,
    client: VirtualMachineTemplatesOperations,
    resource_group_name,
    resource_name,
    force=None,
    no_wait=False,
):
    return sdk_no_wait(
        no_wait, client.begin_delete, resource_group_name, resource_name, force
    )


def show_vm_template(
    cmd, client: VirtualMachineTemplatesOperations, resource_group_name, resource_name
):
    return client.get(resource_group_name, resource_name)


def list_vm_template(
    cmd, client: VirtualMachineTemplatesOperations, resource_group_name=None
):
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name)
    return client.list_by_subscription()


# endregion

# region VirtualMachines

def get_hcrp_machine_id(
    cmd,
    resource_group_name,
    resource_name,
):
    machine_id = get_resource_id(
        cmd,
        resource_group_name,
        HCRP_NAMESPACE,
        MACHINES_RESOURCE_TYPE,
        resource_name,
    )
    assert machine_id is not None
    return machine_id


# pylint: disable=too-many-locals
def create_vm(
    cmd,
    client: VirtualMachineInstancesOperations,
    resource_group_name,
    resource_name,
    custom_location,
    location=None,
    vmmserver=None,
    inventory_item=None,
    vm_template=None,
    cloud=None,
    admin_password=None,
    cpu_count=None,
    memory_size=None,
    dynamic_memory_enabled=None,
    dynamic_memory_max=None,
    dynamic_memory_min=None,
    nics=None,
    disks=None,
    availability_sets=None,
    tags=None,
    no_wait=False,
):
    hardware_profile = None
    os_profile = None
    network_profile = None
    storage_profile = None
    infrastructure_profile = None

    if inventory_item is not None:
        if not is_valid_resource_id(inventory_item) and not vmmserver:
            raise RequiredArgumentMissingError(
                "Cannot determine inventory item ID. "
                "VMMServer name or ID is required when inventory item name is specified."
            )

    if any(
        prop is not None
        for prop in [
            cpu_count,
            memory_size,
            dynamic_memory_enabled,
            dynamic_memory_min,
            dynamic_memory_max,
        ]
    ):
        hardware_profile = HardwareProfile(
            cpu_count=cpu_count,
            memory_mb=memory_size,
            dynamic_memory_enabled=dynamic_memory_enabled,
            dynamic_memory_min_mb=dynamic_memory_min,
            dynamic_memory_max_mb=dynamic_memory_max,
        )

    if admin_password is not None:
        os_profile = OsProfileForVMInstance(admin_password=admin_password)

    if nics is not None:
        network_profile = NetworkProfile(
            network_interfaces=get_network_interfaces(
                cmd, resource_group_name, nics
            )
        )

    if disks is not None:
        storage_profile = StorageProfile(
            disks=get_disks(disks)
        )

    availability_sets = get_availability_sets(
        cmd, resource_group_name, availability_sets
    )

    if inventory_item is not None:
        inventory_item_id = get_resource_id(
            cmd,
            resource_group_name,
            SCVMM_NAMESPACE,
            VMMSERVER_RESOURCE_TYPE,
            vmmserver,
            child_type_1=INVENTORY_ITEM_TYPE,
            child_name_1=inventory_item,
        )
        infrastructure_profile = InfrastructureProfile(
            inventory_item_id=inventory_item_id,
        )
    else:
        vmmserver_id = get_resource_id(
            cmd,
            resource_group_name,
            SCVMM_NAMESPACE,
            VMMSERVER_RESOURCE_TYPE,
            vmmserver,
        )

        cloud_id = get_resource_id(
            cmd,
            resource_group_name,
            SCVMM_NAMESPACE,
            CLOUD_RESOURCE_TYPE,
            cloud,
        )

        template_id = get_resource_id(
            cmd,
            resource_group_name,
            SCVMM_NAMESPACE,
            VMTEMPLATE_RESOURCE_TYPE,
            vm_template,
        )

        infrastructure_profile = InfrastructureProfile(
            vmm_server_id=vmmserver_id,
            cloud_id=cloud_id,
            template_id=template_id,
        )

    custom_location_id = get_resource_id(
        cmd,
        resource_group_name,
        EXTENDED_LOCATION_NAMESPACE,
        CUSTOM_LOCATION_RESOURCE_TYPE,
        custom_location,
    )
    extended_location = get_extended_location(custom_location_id)

    vm = VirtualMachineInstance(
        extended_location=extended_location,
        hardware_profile=hardware_profile,
        os_profile=os_profile,
        network_profile=network_profile,
        storage_profile=storage_profile,
        infrastructure_profile=infrastructure_profile,
        availability_sets=availability_sets,
        tags=tags,
    )

    machine_client = cf_machine(cmd.cli_ctx)
    machine = None
    try:
        machine = machine_client.get(resource_group_name, resource_name)
        if machine.kind and machine.kind.lower() != MACHINE_KIND_SCVMM.lower():
            raise InvalidArgumentValueError(
                f"A machine already exists with kind {machine.kind} "
                f"Machine kind cannot be updated to {MACHINE_KIND_SCVMM}"
            )
        if location is not None and machine.location != location:
            raise InvalidArgumentValueError(
                "The location of the existing Machine cannot be updated. "
                "Either specify the existing location or keep the location unspecified. "
                f"Existing location: {machine.location}, Provided location: {location}"
            )
        if tags is not None:
            m = MachineUpdate(
                tags=tags,
            )
            machine = machine_client.update(resource_group_name, resource_name, m)
    except ResourceNotFoundError as e:
        if location is None:
            raise InvalidArgumentValueError(
                "The parent Machine resource does not exist, "
                "location is required while creating a new machine."
            ) from e
        m = Machine(
            location=location,
            kind=MACHINE_KIND_SCVMM,
            tags=tags,
        )
        machine = machine_client.create_or_update(resource_group_name, resource_name, m)

    assert machine.id is not None

    return sdk_no_wait(
        no_wait,
        client.begin_create_or_update,
        machine.id,
        vm,
    )


def update_vm(
    cmd,
    client: VirtualMachineInstancesOperations,
    resource_group_name,
    resource_name,
    cpu_count=None,
    memory_size=None,
    dynamic_memory_enabled=None,
    dynamic_memory_max=None,
    dynamic_memory_min=None,
    availability_sets=None,
    tags=None,
    no_wait=False,
):

    machine_client = cf_machine(cmd.cli_ctx)
    machine_id = get_hcrp_machine_id(
        cmd,
        resource_group_name,
        resource_name,
    )

    if tags is not None:
        m = MachineUpdate(
            tags=tags,
        )
        machine_client.update(resource_group_name, resource_name, m)

    hardware_profile = None

    if availability_sets is not None:
        availability_sets = get_availability_sets(
            cmd, resource_group_name, availability_sets
        )

    if any(
        prop is not None
        for prop in [
            cpu_count,
            memory_size,
            dynamic_memory_enabled,
            dynamic_memory_min,
            dynamic_memory_max,
        ]
    ):
        hardware_profile = HardwareProfileUpdate(
            cpu_count=cpu_count,
            memory_mb=memory_size,
            dynamic_memory_enabled=dynamic_memory_enabled,
            dynamic_memory_min_mb=dynamic_memory_min,
            dynamic_memory_max_mb=dynamic_memory_max,
        )

    if hardware_profile is None and availability_sets is None:
        return client.get(machine_id)

    vm_update = VirtualMachineInstanceUpdate(
        hardware_profile=hardware_profile,
        availability_sets=availability_sets,
    )

    return sdk_no_wait(
        no_wait,
        client.begin_update,
        machine_id,
        vm_update,
    )


def delete_vm(
    cmd,
    client: VirtualMachineInstancesOperations,
    resource_group_name,
    resource_name,
    retain=None,
    force=None,
    deleteFromHost=None,
    delete_from_host=None,
    delete_machine=None,
    no_wait=False,
):
    if delete_from_host is None:
        delete_from_host = deleteFromHost

    if retain and delete_from_host:
        raise MutuallyExclusiveArgumentError(
            "Arguments --retain and --delete-from-host cannot be used together. "
            "VM is retained in SCVMM by default, it is deleted when --delete-from-host is provided."
        )

    machine_id = get_hcrp_machine_id(
        cmd,
        resource_group_name,
        resource_name,
    )

    machine_client = cf_machine(cmd.cli_ctx)

    if no_wait and delete_machine:
        if delete_from_host:
            raise MutuallyExclusiveArgumentError(
                "Cannot delete SCVMM VM from host when --no-wait and --delete-machine is provided."
            )
        machine_client.delete(resource_group_name, resource_name)
        return

    try:
        # TODO (snaskar): Add deleteFromHost to SDK
        op = sdk_no_wait(
            no_wait, client.begin_delete, machine_id, force, delete_from_host,
        )
    except ResourceNotFoundError:
        # Nothing to delete if the parent machine does not exist.
        return

    op.result()
    if delete_machine:
        # Wait for the VM to be deleted from the host.
        machine_client.delete(resource_group_name, resource_name)


def show_vm(
    cmd,
    client: VirtualMachineInstancesOperations,
    resource_group_name,
    resource_name,
):
    machine_id = get_hcrp_machine_id(
        cmd,
        resource_group_name,
        resource_name,
    )
    return client.get(machine_id)


def wait_vm(
    cmd,
    client: VirtualMachineInstancesOperations,
    resource_group_name,
    virtual_machine_name,
):
    machine_id = get_hcrp_machine_id(
        cmd,
        resource_group_name,
        virtual_machine_name,
    )
    return client.get(machine_id)


def list_vm(
    cmd,
    resource_group_name=None,
):
    resources_filter = "resourceType eq 'Microsoft.SCVMM/VirtualMachineInstances'"
    resources_client = get_resources_client(cmd.cli_ctx)
    if resource_group_name is not None:
        return list(resources_client.list_by_resource_group(resource_group_name, filter=resources_filter))
    return list(resources_client.list(filter=resources_filter))


def start_vm(
    cmd,
    client: VirtualMachineInstancesOperations,
    resource_group_name,
    resource_name,
    no_wait=False,
):
    machine_id = get_hcrp_machine_id(
        cmd,
        resource_group_name,
        resource_name,
    )
    return sdk_no_wait(no_wait, client.begin_start, machine_id)


def stop_vm(
    cmd,
    client: VirtualMachineInstancesOperations,
    resource_group_name,
    resource_name,
    skip_shutdown=None,
    no_wait=False,
):
    machine_id = get_hcrp_machine_id(
        cmd,
        resource_group_name,
        resource_name,
    )
    body = StopVirtualMachineOptions(skip_shutdown=skip_shutdown)
    return sdk_no_wait(
        no_wait, client.begin_stop, machine_id, body
    )


def restart_vm(
    cmd,
    client: VirtualMachineInstancesOperations,
    resource_group_name,
    resource_name,
    no_wait=False,
):
    machine_id = get_hcrp_machine_id(
        cmd,
        resource_group_name,
        resource_name,
    )
    return sdk_no_wait(
        no_wait, client.begin_restart, machine_id
    )


def create_vm_checkpoint(
    cmd,
    client: VirtualMachineInstancesOperations,
    resource_group_name,
    resource_name,
    checkpoint_name,
    checkpoint_description,
    no_wait=False,
):
    machine_id = get_hcrp_machine_id(
        cmd,
        resource_group_name,
        resource_name,
    )
    body = VirtualMachineCreateCheckpoint(name=checkpoint_name, description=checkpoint_description)
    return sdk_no_wait(
        no_wait, client.begin_create_checkpoint, machine_id, body
    )


def delete_vm_checkpoint(
    cmd,
    client: VirtualMachineInstancesOperations,
    resource_group_name,
    resource_name,
    checkpoint_id,
    no_wait=False,
):
    machine_id = get_hcrp_machine_id(
        cmd,
        resource_group_name,
        resource_name,
    )
    body = VirtualMachineDeleteCheckpoint(id=checkpoint_id)
    return sdk_no_wait(
        no_wait, client.begin_delete_checkpoint, machine_id, body
    )


def restore_vm_checkpoint(
    cmd,
    client: VirtualMachineInstancesOperations,
    resource_group_name,
    resource_name,
    checkpoint_id,
    no_wait=False,
):
    machine_id = get_hcrp_machine_id(
        cmd,
        resource_group_name,
        resource_name,
    )
    body = VirtualMachineRestoreCheckpoint(id=checkpoint_id)
    return sdk_no_wait(
        no_wait, client.begin_restore_checkpoint, machine_id, body
    )


def get_network_interfaces(
    cmd, resource_group_name, input_nics
):
    """
    Gets network interfaces from the given input.
    """

    nics = []

    for input_nic in input_nics:
        nic = NetworkInterface(
            ipv4_address_type=AllocationMethod.dynamic.value,
            ipv6_address_type=AllocationMethod.dynamic.value,
            mac_address_type=AllocationMethod.dynamic.value,
        )

        for key, value in input_nic.items():
            if key == NETWORK:
                nic.virtual_network_id = get_resource_id(
                    cmd,
                    resource_group_name,
                    SCVMM_NAMESPACE,
                    VIRTUALNETWORK_RESOURCE_TYPE,
                    value,
                )
            elif key == NAME_PARAMETER:
                nic.name = value
            elif key == IPV4_ADDRESS_TYPE:
                nic.ipv4_address_type = value
            elif key == IPV6_ADDRESS_TYPE:
                nic.ipv6_address_type = value
            elif key == MAC_ADDRESS_TYPE:
                nic.mac_address_type = value
            elif key == MAC_ADDRESS:
                nic.mac_address = value
            else:
                raise UnrecognizedArgumentError(
                    f'Invalid parameter: {key} specified for nic.'
                )
        nics.append(nic)
    return nics


def get_disks(input_disks):
    """
    Gets disks from the given input.
    """

    disks = []
    for input_disk in input_disks:
        disk = VirtualDisk()
        for key, value in input_disk.items():
            if key == NAME_PARAMETER:
                disk.name = value
            elif key == TEMPLATE_DISK_ID:
                disk.template_disk_id = value
            elif key == DISK_SIZE:
                disk.disk_size_gb = value
            elif key == BUS_TYPE:
                disk.bus_type = value
            elif key == BUS:
                disk.bus = value
            elif key == LUN:
                disk.lun = value
            elif key == VHD_TYPE:
                disk.vhd_type = value
            elif key == QOS_NAME:
                disk.storage_qo_s_policy = StorageQoSPolicyDetails(name=value)
            elif key == QOS_ID:
                disk.storage_qo_s_policy = StorageQoSPolicyDetails(id=value)
            else:
                raise UnrecognizedArgumentError(
                    f'Invalid parameter: {key} specified for disk.'
                )
        disks.append(disk)
    return disks


def get_availability_sets(cmd, resource_group_name, availability_sets):
    if availability_sets is not None:
        availability_sets = [
            AvailabilitySetListItem(
                id=get_resource_id(
                    cmd,
                    resource_group_name,
                    SCVMM_NAMESPACE,
                    AVAILABILITYSET_RESOURCE_TYPE,
                    x,
                )
            )
            for x in availability_sets
        ]
    return availability_sets


# endregion

# region VirtualMachine Nics.


def add_nic(
    cmd,
    client: VirtualMachineInstancesOperations,
    resource_group_name,
    vm_name,
    nic_name,
    network=None,
    ipv4_address_type=AllocationMethod.dynamic.value,
    ipv6_address_type=AllocationMethod.dynamic.value,
    mac_address_type=AllocationMethod.dynamic.value,
    mac_address=None,
    no_wait=False,
):
    """
    Add virtual network interface to a virtual machine.
    """

    virtual_network_id = get_resource_id(
        cmd, resource_group_name, SCVMM_NAMESPACE, VIRTUALNETWORK_RESOURCE_TYPE, network
    )

    nic_to_add = NetworkInterfaceUpdate(
        name=nic_name,
        ipv4_address_type=ipv4_address_type,
        ipv6_address_type=ipv6_address_type,
        mac_address_type=mac_address_type,
        mac_address=mac_address,
        virtual_network_id=virtual_network_id,
    )

    machine_id = get_hcrp_machine_id(
        cmd,
        resource_group_name,
        vm_name,
    )

    nics_update = []
    vm = client.get(machine_id)
    if (
        vm.network_profile is not None
        and vm.network_profile.network_interfaces is not None  # noqa: W503
    ):
        for nic in vm.network_profile.network_interfaces:
            nic_update = NetworkInterfaceUpdate(
                name=nic.name,
                ipv4_address_type=nic.ipv4_address_type,
                ipv6_address_type=nic.ipv6_address_type,
                mac_address_type=nic.mac_address_type,
                mac_address=nic.mac_address,
                virtual_network_id=nic.virtual_network_id,
                nic_id=nic.nic_id,
            )
            nics_update.append(nic_update)

    nics_update.append(nic_to_add)
    network_profile = NetworkProfileUpdate(network_interfaces=nics_update)
    vm_update = VirtualMachineInstanceUpdate(network_profile=network_profile)

    return sdk_no_wait(
        no_wait,
        client.begin_update,
        machine_id,
        vm_update,
    )


def update_nic(
    cmd,
    client: VirtualMachineInstancesOperations,
    resource_group_name,
    vm_name,
    nic_name=None,
    nic_id=None,
    network=None,
    disconnect=False,
    ipv4_address_type=None,
    ipv6_address_type=None,
    mac_address_type=None,
    no_wait=False,
):
    """
    Update virtual network interface of a virtual machine.
    """

    if nic_name is None and nic_id is None:
        raise RequiredArgumentMissingError(
            'Either nic name or nic id must be specified to update the nic.'
        )

    if disconnect:
        if network is not None:
            raise MutuallyExclusiveArgumentError(
                'A NIC can either be disconnected or connected to a network.'
                'Please spicify only one of these two options.'
            )

    virtual_network_id = None
    if network is not None:
        virtual_network_id = get_resource_id(
            cmd,
            resource_group_name,
            SCVMM_NAMESPACE,
            VIRTUALNETWORK_RESOURCE_TYPE,
            network,
        )

    machine_id = get_hcrp_machine_id(
        cmd,
        resource_group_name,
        vm_name,
    )

    nics_update = []
    nic_found = False
    vm = client.get(machine_id)
    if (
        vm.network_profile is not None
        and vm.network_profile.network_interfaces is not None  # noqa: W503
    ):
        for nic in vm.network_profile.network_interfaces:
            nic_update = NetworkInterfaceUpdate(
                name=nic.name,
                ipv4_address_type=nic.ipv4_address_type,
                ipv6_address_type=nic.ipv6_address_type,
                mac_address_type=nic.mac_address_type,
                mac_address=nic.mac_address,
                virtual_network_id=nic.virtual_network_id,
                nic_id=nic.nic_id,
            )
            if (nic_name is not None and nic.name == nic_name) or (
                nic_id is not None and nic.nic_id == nic_id
            ):
                if (nic_name is not None and nic_name != nic.name) or (
                    nic_id is not None and nic_id != nic.nic_id
                ):
                    raise InvalidArgumentValueError(
                        'Incorrect nic-name and nic-id combination, '
                        + f'Expected nic-name : {nic_name}, nic-id : {nic_id}'  # noqa: W503
                    )
                nic_found = True
                if nic.name is None and nic_name is not None:
                    nic_update.name = nic_name
                if ipv4_address_type is not None:
                    nic_update.ipv4_address_type = ipv4_address_type
                if ipv6_address_type is not None:
                    nic_update.ipv6_address_type = ipv6_address_type
                if mac_address_type is not None:
                    nic_update.mac_address_type = mac_address_type
                if virtual_network_id is not None or disconnect:
                    nic_update.virtual_network_id = virtual_network_id

            nics_update.append(nic_update)

    if not nic_found:
        raise InvalidArgumentValueError(
            'Given nic is not present in the virtual machine.'
        )

    network_profile = NetworkProfileUpdate(network_interfaces=nics_update)
    vm_update = VirtualMachineInstanceUpdate(network_profile=network_profile)

    return sdk_no_wait(
        no_wait,
        client.begin_update,
        machine_id,
        vm_update,
    )


def list_nics(
    cmd,
    client: VirtualMachineInstancesOperations,
    resource_group_name, vm_name
):
    """
    List details of the nics present in a virtual machine.
    """
    machine_id = get_hcrp_machine_id(
        cmd,
        resource_group_name,
        vm_name,
    )

    vm = client.get(machine_id)
    if vm.network_profile is not None:
        return vm.network_profile.network_interfaces
    return None


def show_nic(
    cmd,
    client: VirtualMachineInstancesOperations,
    resource_group_name, vm_name, nic_name
):
    """
    Get the details of a virtual machine nic.
    """

    machine_id = get_hcrp_machine_id(
        cmd,
        resource_group_name,
        vm_name,
    )

    vm = client.get(machine_id)
    if (
        vm.network_profile is not None
        and vm.network_profile.network_interfaces is not None  # noqa: W503
    ):
        for nic in vm.network_profile.network_interfaces:
            if nic.name == nic_name:
                return nic
    return None


def delete_nics(
    cmd,
    client: VirtualMachineInstancesOperations,
    resource_group_name,
    vm_name,
    nic_names,
    no_wait=False,
):
    """
    Delete virtual network interfaces from virtual machine.
    """

    machine_id = get_hcrp_machine_id(
        cmd,
        resource_group_name,
        vm_name,
    )

    # Dictionary to maintain the nics to delete.
    nics_to_delete = {nic_name: True for nic_name in nic_names}

    nics_update = []
    vm = client.get(machine_id)
    if (
        vm.network_profile is not None
        and vm.network_profile.network_interfaces is not None  # noqa: W503
    ):
        for nic in vm.network_profile.network_interfaces:
            if nic.name in nics_to_delete:
                nics_to_delete[nic.name] = False
                continue
            nic_update = NetworkInterfaceUpdate(
                name=nic.name,
                ipv4_address_type=nic.ipv4_address_type,
                ipv6_address_type=nic.ipv6_address_type,
                mac_address_type=nic.mac_address_type,
                mac_address=nic.mac_address,
                virtual_network_id=nic.virtual_network_id,
                nic_id=nic.nic_id,
            )
            nics_update.append(nic_update)

    not_found_nics = [
        nic_name for nic_name in nics_to_delete if nics_to_delete[nic_name]
    ]
    if not_found_nics:
        raise InvalidArgumentValueError(
            f'Nics with name {not_found_nics} not present in the given virtual machine.'
        )

    network_profile = NetworkProfileUpdate(network_interfaces=nics_update)
    vm_update = VirtualMachineInstanceUpdate(network_profile=network_profile)

    return sdk_no_wait(
        no_wait,
        client.begin_update,
        machine_id,
        vm_update,
    )


# endregion

# region VirtualMachine Disks.


def add_disk(
    cmd,
    client: VirtualMachineInstancesOperations,
    resource_group_name,
    vm_name,
    disk_name,
    disk_size_gb,
    bus,
    lun=None,
    bus_type=BusType.scsi.value,
    vhd_type=VHDType.dynamic.value,
    qos_name=None,
    qos_id=None,
    no_wait=False,
):
    """
    Add virtual disk to a virtual machine.
    """

    storage_qos_policy = None
    if qos_name is not None and qos_id is not None:
        raise MutuallyExclusiveArgumentError(
            'Both name and id of Storage QoS Policy cannot be specified.'
        )
    if qos_name is not None:
        storage_qos_policy = StorageQoSPolicyDetails(name=qos_name)
    if qos_id is not None:
        storage_qos_policy = StorageQoSPolicyDetails(id=qos_id)

    disk_to_add = VirtualDiskUpdate(
        name=disk_name,
        disk_size_gb=disk_size_gb,
        bus=bus,
        lun=lun,
        bus_type=bus_type,
        vhd_type=vhd_type,
        storage_qo_s_policy=storage_qos_policy,
    )

    machine_id = get_hcrp_machine_id(
        cmd,
        resource_group_name,
        vm_name,
    )

    disks_update = []
    vm = client.get(machine_id)
    if vm.storage_profile is not None and vm.storage_profile.disks is not None:
        for disk in vm.storage_profile.disks:
            disk_update = VirtualDiskUpdate(
                name=disk.name,
                disk_size_gb=disk.disk_size_gb,
                bus=disk.bus,
                lun=disk.lun,
                bus_type=disk.bus_type,
                vhd_type=vhd_type,
                storage_qo_s_policy=storage_qos_policy,
                disk_id=disk.disk_id,
            )
            disks_update.append(disk_update)

    disks_update.append(disk_to_add)
    storage_profile = StorageProfileUpdate(disks=disks_update)
    vm_update = VirtualMachineInstanceUpdate(storage_profile=storage_profile)

    return sdk_no_wait(
        no_wait,
        client.begin_update,
        machine_id,
        vm_update,
    )


def update_disk(
    cmd,
    client: VirtualMachineInstancesOperations,
    resource_group_name,
    vm_name,
    disk_name=None,
    disk_id=None,
    disk_size_gb=None,
    bus=None,
    lun=None,
    bus_type=None,
    vhd_type=None,
    qos_name=None,
    qos_id=None,
    no_wait=False,
):
    """
    Update virtual disk of a virtual machine.
    """

    if disk_name is None and disk_id is None:
        raise RequiredArgumentMissingError(
            'Either disk name or disk id must be specified to update the disk.'
        )

    machine_id = get_hcrp_machine_id(
        cmd,
        resource_group_name,
        vm_name,
    )

    storage_qos_policy = None
    if qos_name is not None and qos_id is not None:
        raise MutuallyExclusiveArgumentError(
            'Both name and id of Storage QoS Policy cannot be specified.'
        )
    if qos_name is not None:
        storage_qos_policy = StorageQoSPolicyDetails(name=qos_name)
    if qos_id is not None:
        storage_qos_policy = StorageQoSPolicyDetails(id=qos_id)

    disks_update = []
    disk_found = False
    vm = client.get(machine_id)
    if vm.storage_profile is not None and vm.storage_profile.disks is not None:
        for disk in vm.storage_profile.disks:
            disk: VirtualDisk = disk
            disk_update = VirtualDiskUpdate(
                name=disk.name,
                disk_size_gb=disk.disk_size_gb,
                bus=disk.bus,
                lun=disk.lun,
                bus_type=disk.bus_type,
                vhd_type=disk.vhd_type,
                storage_qo_s_policy=disk.storage_qo_s_policy,
                disk_id=disk.disk_id,
            )
            if (disk_name is not None and disk.name == disk_name) or (
                disk_id is not None and disk.disk_id == disk_id
            ):
                if (disk_name is not None and disk_name != disk.name) or (
                    disk_id is not None and disk_id != disk.disk_id
                ):
                    raise InvalidArgumentValueError(
                        'Incorrect disk-name and disk-id combination, '
                        + f'Expected disk-name : {disk_name}, disk-id : {disk_id}'  # noqa: W503
                    )
                disk_found = True
                if disk.name is None and disk_name is not None:
                    disk_update.name = disk_name
                if disk_size_gb is not None:
                    disk_update.disk_size_gb = disk_size_gb
                if bus is not None:
                    disk_update.bus = bus
                if lun is not None:
                    disk_update.lun = lun
                if bus_type is not None:
                    disk_update.bus_type = bus_type
                if vhd_type is not None:
                    disk_update.vhd_type = vhd_type
                if storage_qos_policy is not None:
                    disk_update.storage_qo_s_policy = storage_qos_policy
            disks_update.append(disk_update)

    if not disk_found:
        raise InvalidArgumentValueError(
            'Given disk is not present in the virtual machine.'
        )

    storage_profile = StorageProfileUpdate(disks=disks_update)
    vm_update = VirtualMachineInstanceUpdate(storage_profile=storage_profile)

    return sdk_no_wait(
        no_wait,
        client.begin_update,
        machine_id,
        vm_update,
    )


def list_disks(
    cmd,
    client: VirtualMachineInstancesOperations,
    resource_group_name,
    vm_name,
):
    """
    List details of the disks present in a virtual machine.
    """

    machine_id = get_hcrp_machine_id(
        cmd,
        resource_group_name,
        vm_name,
    )

    vm = client.get(machine_id)
    if vm.storage_profile is not None:
        return vm.storage_profile.disks
    return None


def show_disk(
    cmd,
    client: VirtualMachineInstancesOperations,
    resource_group_name,
    vm_name,
    disk_name,
):
    """
    Get the details of a virtual machine disk.
    """

    machine_id = get_hcrp_machine_id(
        cmd,
        resource_group_name,
        vm_name,
    )

    vm = client.get(machine_id)
    if vm.storage_profile is not None and vm.storage_profile.disks is not None:
        for disk in vm.storage_profile.disks:
            if disk.name == disk_name:
                return disk
    return None


def delete_disks(
    cmd,
    client: VirtualMachineInstancesOperations,
    resource_group_name,
    vm_name,
    disk_names,
    no_wait=False,
):
    """
    Delete virtual disks from virtual machine.
    """

    # Dictionary to maintain the disks to delete.
    disks_to_delete = {disk_name: True for disk_name in disk_names}

    machine_id = get_hcrp_machine_id(
        cmd,
        resource_group_name,
        vm_name,
    )

    disks_update = []
    vm = client.get(machine_id)
    if vm.storage_profile is not None and vm.storage_profile.disks is not None:
        for disk in vm.storage_profile.disks:
            if disk.name in disks_to_delete:
                disks_to_delete[disk.name] = False
                continue
            disk_update = VirtualDiskUpdate(
                name=disk.name,
                disk_size_gb=disk.disk_size_gb,
                bus=disk.bus,
                lun=disk.lun,
                bus_type=disk.bus_type,
                vhd_type=disk.vhd_type,
                storage_qo_s_policy=disk.storage_qo_s_policy,
                disk_id=disk.disk_id,
            )
            disks_update.append(disk_update)

    not_found_disks = [
        disk_name for disk_name in disks_to_delete if disks_to_delete[disk_name]
    ]
    if not_found_disks:
        raise InvalidArgumentValueError(
            f'Disks with name {not_found_disks} not present in the given virtual machine.'
        )

    storage_profile = StorageProfileUpdate(disks=disks_update)
    vm_update = VirtualMachineInstanceUpdate(storage_profile=storage_profile)

    return sdk_no_wait(
        no_wait,
        client.begin_update,
        machine_id,
        vm_update,
    )


# endregion


# region Availability Sets


def create_avset(
    cmd,
    client: AvailabilitySetsOperations,
    resource_group_name,
    location,
    custom_location,
    resource_name,
    vmmserver,
    avset_name,
    tags=None,
    no_wait=False,
):

    avset = AvailabilitySet(
        location=location,
        extended_location=get_extended_location(custom_location),
        vmm_server_id=vmmserver,
        availability_set_name=avset_name,
        tags=tags,
    )

    return sdk_no_wait(
        no_wait,
        client.begin_create_or_update,
        resource_group_name,
        resource_name,
        avset,
    )


def update_avset(
    cmd,
    client: AvailabilitySetsOperations,
    resource_group_name,
    resource_name,
    tags=None,
    no_wait=False,
):
    avset_update = ResourcePatch(tags=tags)
    return sdk_no_wait(
        no_wait,
        client.begin_update,
        resource_group_name,
        resource_name,
        avset_update,
    )


def delete_avset(
    cmd,
    client: AvailabilitySetsOperations,
    resource_group_name,
    resource_name,
    force=None,
    no_wait=False,
):
    return sdk_no_wait(
        no_wait, client.begin_delete, resource_group_name, resource_name, force
    )


def show_avset(
    cmd, client: AvailabilitySetsOperations, resource_group_name, resource_name
):
    return client.get(resource_group_name, resource_name)


def wait_avset(
    cmd, client: AvailabilitySetsOperations, resource_group_name, availability_set_name
):
    return client.get(resource_group_name, availability_set_name)


def list_avsets(cmd, client: AvailabilitySetsOperations, resource_group_name=None):
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name)
    return client.list_by_subscription()


# endregion

# region InventoryItems


def show_inventory_item(
    client: InventoryItemsOperations, resource_group_name, vmmserver, inventory_item
):
    return client.get(
        resource_group_name, vmmserver.split('/')[-1], inventory_item.split('/')[-1]
    )


def list_inventory_items(
    client: InventoryItemsOperations, resource_group_name, vmmserver
):
    return client.list_by_vmm_server(resource_group_name, vmmserver.split('/')[-1])


# endregion

# region GuestAgent


def is_system_identity_enabled(machine: Machine):
    """
    Check whether system identity is enable or not on this vm.
    """

    if machine.identity is not None and machine.identity.type == VM_SYSTEM_ASSIGNED_INDENTITY_TYPE:
        return True

    return False


def enable_system_identity(
    client: MachinesOperations,
    resource_group_name,
    vm_name,
):
    """
    Enable system assigned identity on this vm.
    """

    system_identity = Identity(type=VM_SYSTEM_ASSIGNED_INDENTITY_TYPE)
    vm_update = MachineUpdate(identity=system_identity)
    return client.update(resource_group_name, vm_name, vm_update)


def enable_guest_agent(
    cmd,
    client: VMInstanceGuestAgentsOperations,
    resource_group_name,
    vm_name,
    username,
    password,
    https_proxy=None,
    no_wait=False,
):
    """
    Enable guest agent on the given virtual machine.
    """

    machine_client = cf_machine(cmd.cli_ctx)
    machine = machine_client.get(resource_group_name, vm_name)
    assert machine.id is not None

    # To ensure that the VirtualMachineInstance resource is present
    # before patching identity to SystemAssigned.
    vm_client = cf_virtual_machine_instance(cmd.cli_ctx)
    vm_client.get(machine.id)

    if not is_system_identity_enabled(machine):
        machine = enable_system_identity(machine_client, resource_group_name, vm_name)

    vm_creds = GuestCredential(username=username, password=password)

    https_proxy_config = None
    if https_proxy:
        https_proxy_config = HttpProxyConfiguration(https_proxy=https_proxy)

    guest_agent = GuestAgent(
        credentials=vm_creds,
        http_proxy_config=https_proxy_config,
        provisioning_action=GUEST_AGENT_PROVISIONING_ACTION_INSTALL,
    )

    return sdk_no_wait(
        no_wait,
        client.begin_create,
        machine.id,
        guest_agent
    )


def show_guest_agent(
    cmd,
    client: VMInstanceGuestAgentsOperations,
    resource_group_name,
    vm_name,
):
    """
    Show the guest agent of the given vm and guest agent.
    """

    machine_id = get_hcrp_machine_id(
        cmd,
        resource_group_name,
        vm_name,
    )

    return client.get(machine_id)


# endregion

# region Extenstion


def scvmm_extension_list(
    client: MachineExtensionsOperations,
    resource_group_name,
    vm_name,
    expand=None
):
    """
    List all the vm extension of a given vm.
    """

    return client.list(resource_group_name=resource_group_name,
                       machine_name=vm_name,
                       expand=expand)


def scvmm_extension_show(
    client: MachineExtensionsOperations,
    resource_group_name,
    vm_name,
    name
):
    """
    Get the details of the vm extension of a given vm.
    """

    return client.get(resource_group_name=resource_group_name,
                      machine_name=vm_name,
                      extension_name=name)


def scvmm_extension_create(
    cmd,
    client: MachineExtensionsOperations,
    resource_group_name,
    vm_name,
    name,
    location,
    tags=None,
    force_update_tag=None,
    publisher=None,
    type_=None,
    type_handler_version=None,
    enable_auto_upgrade=None,
    auto_upgrade_minor=None,
    settings=None,
    protected_settings=None,
    no_wait=False
):
    """
    Create the vm extension of a given vm.
    """

    resource_id = get_resource_id(
        cmd,
        resource_group_name,
        HCRP_NAMESPACE,
        MACHINES_RESOURCE_TYPE,
        vm_name,
        child_type_1=EXTENSIONS_RESOURCE_TYPE,
        child_name_1=name,
    )

    machine_extension = MachineExtension(
        location=location,
        tags=tags,
        name=name,
        id=resource_id,
        force_update_tag=force_update_tag,
        publisher=publisher,
        type_properties_type=type_,
        type_handler_version=type_handler_version,
        enable_automatic_upgrade=enable_auto_upgrade,
        auto_upgrade_minor_version=auto_upgrade_minor,
        settings=settings,
        protected_settings=protected_settings,
    )

    return sdk_no_wait(no_wait,
                       client.begin_create_or_update,
                       resource_group_name=resource_group_name,
                       machine_name=vm_name,
                       extension_name=name,
                       extension_parameters=machine_extension)


def scvmm_extension_update(
    client: MachineExtensionsOperations,
    resource_group_name,
    vm_name,
    name,
    tags=None,
    force_update_tag=None,
    publisher=None,
    type_=None,
    type_handler_version=None,
    enable_auto_upgrade=None,
    auto_upgrade_minor=None,
    settings=None,
    protected_settings=None,
    no_wait=False
):
    """
    Update the vm extension of a given vm.
    """

    machine_extension = MachineExtensionUpdate(
        tags=tags,
        force_update_tag=force_update_tag,
        publisher=publisher,
        type=type_,
        type_handler_version=type_handler_version,
        enable_automatic_upgrade=enable_auto_upgrade,
        auto_upgrade_minor_version=auto_upgrade_minor,
        settings=settings,
        protected_settings=protected_settings,
    )

    return sdk_no_wait(no_wait,
                       client.begin_update,
                       resource_group_name=resource_group_name,
                       machine_name=vm_name,
                       extension_name=name,
                       extension_parameters=machine_extension)


def scvmm_extension_delete(
    client: MachineExtensionsOperations,
    resource_group_name,
    vm_name,
    name,
    no_wait=False
):
    """
    Delete the vm extension of a given vm.
    """

    return sdk_no_wait(no_wait,
                       client.begin_delete,
                       resource_group_name=resource_group_name,
                       machine_name=vm_name,
                       extension_name=name)


# endregion
