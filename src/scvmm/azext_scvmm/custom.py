# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=unused-argument,too-many-lines

from pwinput import pwinput
from azure.cli.core.azclierror import (
    UnrecognizedArgumentError,
    RequiredArgumentMissingError,
    MutuallyExclusiveArgumentError,
    InvalidArgumentValueError,
)
from azure.cli.core.util import sdk_no_wait
from .scvmm_utils import get_resource_id, get_extended_location
from .scvmm_constants import (
    AVAILABILITYSET_RESOURCE_TYPE,
    SCVMM_NAMESPACE,
    VIRTUALNETWORK_RESOURCE_TYPE,
    DEFAULT_VMMSERVER_PORT,
    EXTENDED_LOCATION_NAMESPACE,
    CUSTOM_LOCATION_RESOURCE_TYPE,
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
from .vendored_sdks.models import (
    Cloud,
    HardwareProfile,
    HardwareProfileUpdate,
    OsProfile,
    VirtualMachine,
    VirtualMachineUpdate,
    VirtualMachineUpdateProperties,
    VirtualMachineTemplate,
    VirtualNetwork,
    VMMServer,
    VMMServerPropertiesCredentials,
    AllocationMethod,
    NetworkInterfaces,
    NetworkProfile,
    NetworkInterfacesUpdate,
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
)
from .vendored_sdks.operations import (
    VmmServersOperations,
    CloudsOperations,
    VirtualNetworksOperations,
    VirtualMachineTemplatesOperations,
    VirtualMachinesOperations,
    AvailabilitySetsOperations,
    InventoryItemsOperations,
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
                creds['port'] = int(creds['port'])
            except ValueError:
                print('Port must be a number, please try again')
                creds['port'] = None
        while not creds['username']:
            print('Please provide vmmserver username: ', end='')
            creds['username'] = input()
            if not creds['username']:
                print('Parameter is required, please try again')
        while not creds['password']:
            creds['password'] = pwinput('Please provide vmmserver password: ')
            if not creds['password']:
                print('Parameter is required, please try again')
            passwdConfim = pwinput('Please confirm vmmserver password: ')
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

    username_creds = VMMServerPropertiesCredentials(
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

# pylint: disable=too-many-locals
def create_vm(
    cmd,
    client: VirtualMachinesOperations,
    resource_group_name,
    resource_name,
    custom_location,
    location,
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
        os_profile = OsProfile(admin_password=admin_password)

    if nics is not None:
        network_profile = NetworkProfile(
            network_interfaces=get_network_interfaces(
                cmd, client, resource_group_name, nics
            )
        )

    if disks is not None:
        storage_profile = StorageProfile(
            disks=get_disks(cmd, client, resource_group_name, disks)
        )

    availability_sets = get_availability_sets(
        cmd, resource_group_name, availability_sets
    )

    vm = VirtualMachine(
        location=location,
        extended_location=get_extended_location(custom_location),
        inventory_item_id=inventory_item,
        cloud_id=cloud,
        template_id=vm_template,
        hardware_profile=hardware_profile,
        os_profile=os_profile,
        network_profile=network_profile,
        storage_profile=storage_profile,
        availability_sets=availability_sets,
        tags=tags,
    )

    return sdk_no_wait(
        no_wait,
        client.begin_create_or_update,
        resource_group_name,
        resource_name,
        vm,
    )


def update_vm(
    cmd,
    client: VirtualMachinesOperations,
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
    vm_update_props = None

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
        vm_update_props = VirtualMachineUpdateProperties(
            hardware_profile=hardware_profile,
            availability_sets=availability_sets,
        )

    vm_update = VirtualMachineUpdate(properties=vm_update_props, tags=tags)
    return sdk_no_wait(
        no_wait,
        client.begin_update,
        resource_group_name,
        resource_name,
        vm_update,
    )


def delete_vm(
    cmd,
    client: VirtualMachinesOperations,
    resource_group_name,
    resource_name,
    retain=None,
    force=None,
    no_wait=False,
):
    return sdk_no_wait(
        no_wait,
        client.begin_delete,
        resource_group_name,
        resource_name,
        retain,
        force,
    )


def show_vm(cmd, client: VirtualMachinesOperations, resource_group_name, resource_name):
    return client.get(resource_group_name, resource_name)


def list_vm(cmd, client: VirtualMachinesOperations, resource_group_name=None):
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name)
    return client.list_by_subscription()


def start_vm(
    cmd,
    client: VirtualMachinesOperations,
    resource_group_name,
    resource_name,
    no_wait=False,
):
    return sdk_no_wait(no_wait, client.begin_start, resource_group_name, resource_name)


def stop_vm(
    cmd,
    client: VirtualMachinesOperations,
    resource_group_name,
    resource_name,
    skip_shutdown=False,
    no_wait=False,
):
    body = StopVirtualMachineOptions(skip_shutdown=skip_shutdown)
    return sdk_no_wait(
        no_wait, client.begin_stop, resource_group_name, resource_name, body
    )


def restart_vm(
    cmd,
    client: VirtualMachinesOperations,
    resource_group_name,
    resource_name,
    no_wait=False,
):
    return sdk_no_wait(
        no_wait, client.begin_restart, resource_group_name, resource_name
    )


def get_network_interfaces(
    cmd, client: VirtualMachinesOperations, resource_group_name, input_nics
):
    """
    Gets network interfaces from the given input.
    """

    nics = []

    for input_nic in input_nics:
        nic = NetworkInterfaces(
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


def get_disks(cmd, client: VirtualMachinesOperations, resource_group_name, input_disks):
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
    client: VirtualMachinesOperations,
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

    nic_to_add = NetworkInterfacesUpdate(
        name=nic_name,
        ipv4_address_type=ipv4_address_type,
        ipv6_address_type=ipv6_address_type,
        mac_address_type=mac_address_type,
        mac_address=mac_address,
        virtual_network_id=virtual_network_id,
    )

    nics_update = []
    vm: VirtualMachine = client.get(resource_group_name, vm_name)
    if (
        vm.network_profile is not None
        and vm.network_profile.network_interfaces is not None  # noqa: W503
    ):
        for nic in vm.network_profile.network_interfaces:
            nic_update = NetworkInterfacesUpdate(
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
    vm_update_props = VirtualMachineUpdateProperties(network_profile=network_profile)
    vm_update = VirtualMachineUpdate(properties=vm_update_props, tags=vm.tags)

    return sdk_no_wait(
        no_wait,
        client.begin_update,
        resource_group_name,
        vm_name,
        vm_update,
    )


def update_nic(
    cmd,
    client: VirtualMachinesOperations,
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

    nics_update = []
    nic_found = False
    vm = client.get(resource_group_name, vm_name)
    if (
        vm.network_profile is not None
        and vm.network_profile.network_interfaces is not None  # noqa: W503
    ):
        for nic in vm.network_profile.network_interfaces:
            nic_update = NetworkInterfacesUpdate(
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
    vm_update_props = VirtualMachineUpdateProperties(network_profile=network_profile)
    vm_update = VirtualMachineUpdate(properties=vm_update_props, tags=vm.tags)

    return sdk_no_wait(
        no_wait,
        client.begin_update,
        resource_group_name,
        vm_name,
        vm_update,
    )


def list_nics(client: VirtualMachinesOperations, resource_group_name, vm_name):
    """
    List details of the nics present in a virtual machine.
    """

    vm = client.get(resource_group_name, vm_name)
    if vm.network_profile is not None:
        return vm.network_profile.network_interfaces
    return None


def show_nic(client: VirtualMachinesOperations, resource_group_name, vm_name, nic_name):
    """
    Get the details of a virtual machine nic.
    """

    vm = client.get(resource_group_name, vm_name)
    if (
        vm.network_profile is not None
        and vm.network_profile.network_interfaces is not None  # noqa: W503
    ):
        for nic in vm.network_profile.network_interfaces:
            if nic.name == nic_name:
                return nic
    return None


def delete_nics(
    client: VirtualMachinesOperations,
    resource_group_name,
    vm_name,
    nic_names,
    no_wait=False,
):
    """
    Delete virtual network interfaces from virtual machine.
    """

    # Dictionary to maintain the nics to delete.
    nics_to_delete = {nic_name: True for nic_name in nic_names}

    nics_update = []
    vm = client.get(resource_group_name, vm_name)
    if (
        vm.network_profile is not None
        and vm.network_profile.network_interfaces is not None  # noqa: W503
    ):
        for nic in vm.network_profile.network_interfaces:
            if nic.name in nics_to_delete:
                nics_to_delete[nic.name] = False
                continue
            nic_update = NetworkInterfacesUpdate(
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
    vm_update_props = VirtualMachineUpdateProperties(network_profile=network_profile)
    vm_update = VirtualMachineUpdate(properties=vm_update_props, tags=vm.tags)

    return sdk_no_wait(
        no_wait,
        client.begin_update,
        resource_group_name,
        vm_name,
        vm_update,
    )


# endregion

# region VirtualMachine Disks.


def add_disk(
    cmd,
    client: VirtualMachinesOperations,
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

    disks_update = []
    vm: VirtualMachine = client.get(resource_group_name, vm_name)
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
    vm_update_props = VirtualMachineUpdateProperties(storage_profile=storage_profile)
    vm_update = VirtualMachineUpdate(properties=vm_update_props, tags=vm.tags)

    return sdk_no_wait(
        no_wait,
        client.begin_update,
        resource_group_name,
        vm_name,
        vm_update,
    )


def update_disk(
    cmd,
    client: VirtualMachinesOperations,
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
    vm: VirtualMachine = client.get(resource_group_name, vm_name)
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
    vm_update_props = VirtualMachineUpdateProperties(storage_profile=storage_profile)
    vm_update = VirtualMachineUpdate(properties=vm_update_props, tags=vm.tags)

    return sdk_no_wait(
        no_wait,
        client.begin_update,
        resource_group_name,
        vm_name,
        vm_update,
    )


def list_disks(client: VirtualMachinesOperations, resource_group_name, vm_name):
    """
    List details of the disks present in a virtual machine.
    """

    vm = client.get(resource_group_name, vm_name)
    if vm.storage_profile is not None:
        return vm.storage_profile.disks
    return None


def show_disk(
    client: VirtualMachinesOperations, resource_group_name, vm_name, disk_name
):
    """
    Get the details of a virtual machine disk.
    """

    vm = client.get(resource_group_name, vm_name)
    if vm.storage_profile is not None and vm.storage_profile.disks is not None:
        for disk in vm.storage_profile.disks:
            if disk.name == disk_name:
                return disk
    return None


def delete_disks(
    client: VirtualMachinesOperations,
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

    disks_update = []
    vm: VirtualMachine = client.get(resource_group_name, vm_name)
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
    vm_update_props = VirtualMachineUpdateProperties(storage_profile=storage_profile)
    vm_update = VirtualMachineUpdate(properties=vm_update_props, tags=vm.tags)

    return sdk_no_wait(
        no_wait,
        client.begin_update,
        resource_group_name,
        vm_name,
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
