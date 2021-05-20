# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable= too-many-lines, too-many-locals, unused-argument

from knack.util import CLIError
from azext_connectedvmware.vmware_utils import get_resource_id
from azure.cli.core.util import sdk_no_wait
from .vmware_constants import (
    VMWARE_NAMESPACE,
    VCENTER_RESOURCE_TYPE,
    RESOURCEPOOL_RESOURCE_TYPE,
    VMTEMPLATE_RESOURCE_TYPE,
    VIRTUALNETWORK_RESOURCE_TYPE,
    DEFAULT_VCENTER_PORT,
    EXTENDED_LOCATION_NAMESPACE,
    CUSTOM_LOCATION_RESOURCE_TYPE,
    EXTENDED_LOCATION_TYPE,
    INVENTORY_ITEM_TYPE,
    NAME_PARAMETER,
    DEVICE_KEY,
    NETWORK,
    NIC_TYPE,
    POWER_ON_BOOT,
    ALLOCATION_METHOD,
    IP_ADDRESS,
    SUBNET_MASK,
    GATEWAY,
    GATEWAY_SEPERATOR,
    DISK_SIZE,
    DISK_MODE,
    CONTROLLER_KEY,
    UNIT_NUMBER
)

from .vendored_sdks.models import (
    DiskMode,
    HardwareProfile,
    IPAddressAllocationMethod,
    NetworkInterface,
    NetworkInterfaceUpdate,
    NetworkProfile,
    NetworkProfileUpdate,
    NicIPSettings,
    NICType,
    OsProfile,
    PowerOnBootOption,
    ResourcePool,
    StorageProfile,
    StorageProfileUpdate,
    VCenter,
    VICredential,
    VirtualDisk,
    VirtualDiskUpdate,
    VirtualMachine,
    VirtualMachineTemplate,
    VirtualMachineUpdate,
    VirtualNetwork,
    ExtendedLocation,
    StopVirtualMachineOptions,
)

from .vendored_sdks.operations import (
    VCentersOperations,
    ResourcePoolsOperations,
    VirtualNetworksOperations,
    VirtualMachineTemplatesOperations,
    VirtualMachinesOperations,
    InventoryItemsOperations,
)

# endregion

# region VCenters


def connect_vcenter(
    cmd,
    client: VCentersOperations,
    resource_group_name,
    resource_name,
    fqdn,
    custom_location,
    location,
    username=None,
    password=None,
    port=DEFAULT_VCENTER_PORT,
    tags=None,
    no_wait=False,
):

    if username is None or password is None:
        raise CLIError("Missing vcenter credentials, provide username/password")

    username_creds = VICredential(username=username, password=password)

    custom_location_id = get_resource_id(
        cmd,
        resource_group_name,
        EXTENDED_LOCATION_NAMESPACE,
        CUSTOM_LOCATION_RESOURCE_TYPE,
        custom_location,
    )

    extended_location = ExtendedLocation(
        type=EXTENDED_LOCATION_TYPE, name=custom_location_id
    )

    vcenter = VCenter(
        location=location,
        fqdn=fqdn,
        port=port,
        extended_location=extended_location,
        credentials=username_creds,
    )

    return sdk_no_wait(
        no_wait, client.begin_create, resource_group_name, resource_name, vcenter
    )


def delete_vcenter(
    client: VCentersOperations,
    resource_group_name,
    resource_name,
    force=False,
    no_wait=False,
):

    return sdk_no_wait(
        no_wait, client.begin_delete, resource_group_name, resource_name, force
    )


def show_vcenter(client: VCentersOperations, resource_group_name, resource_name):

    return client.get(resource_group_name, resource_name)


def list_vcenter(client: VCentersOperations, resource_group_name=None):

    if resource_group_name:
        return client.list_by_resource_group(resource_group_name)
    return client.list()


# endregion

# region ResourcePools


def create_resource_pool(
    cmd,
    client: ResourcePoolsOperations,
    resource_group_name,
    resource_name,
    custom_location,
    location,
    vcenter=None,
    mo_ref_id=None,
    inventory_item=None,
    tags=None,
    no_wait=False,
):

    if mo_ref_id is None and inventory_item is None:
        raise CLIError(
            "Missing parameter, provide either mo_ref_id or inventory_item id."
        )

    custom_location_id = get_resource_id(
        cmd,
        resource_group_name,
        EXTENDED_LOCATION_NAMESPACE,
        CUSTOM_LOCATION_RESOURCE_TYPE,
        custom_location,
    )

    extended_location = ExtendedLocation(
        type=EXTENDED_LOCATION_TYPE, name=custom_location_id
    )

    inventory_item_id = None
    vcenter_id = None

    if inventory_item is not None:
        inventory_item_id = get_resource_id(
            cmd,
            resource_group_name,
            VMWARE_NAMESPACE,
            VCENTER_RESOURCE_TYPE,
            vcenter,
            INVENTORY_ITEM_TYPE,
            inventory_item,
        )
    else:
        if vcenter is None:
            raise CLIError("Missing parameter, provide vcenter name or id.")

        vcenter_id = get_resource_id(
            cmd, resource_group_name, VMWARE_NAMESPACE, VCENTER_RESOURCE_TYPE, vcenter
        )

    if inventory_item_id is not None:
        resource_pool = ResourcePool(
            location=location,
            extended_location=extended_location,
            inventory_item_id=inventory_item_id,
        )
    else:
        resource_pool = ResourcePool(
            location=location,
            extended_location=extended_location,
            v_center_id=vcenter_id,
            mo_ref_id=mo_ref_id,
        )

    return sdk_no_wait(
        no_wait, client.begin_create, resource_group_name, resource_name, resource_pool
    )


def delete_resource_pool(
    client: ResourcePoolsOperations,
    resource_group_name,
    resource_name,
    force=False,
    no_wait=False,
):

    return sdk_no_wait(
        no_wait, client.begin_delete, resource_group_name, resource_name, force
    )


def show_resource_pool(
    client: ResourcePoolsOperations, resource_group_name, resource_name
):

    return client.get(resource_group_name, resource_name)


def list_resource_pool(client: ResourcePoolsOperations, resource_group_name=None):

    if resource_group_name:
        return client.list_by_resource_group(resource_group_name)
    return client.list()


# endregion

# region VirtualNetworks


def create_virtual_network(
    cmd,
    client: VirtualNetworksOperations,
    resource_group_name,
    resource_name,
    custom_location,
    location,
    vcenter=None,
    mo_ref_id=None,
    inventory_item=None,
    tags=None,
    no_wait=False,
):

    if mo_ref_id is None and inventory_item is None:
        raise CLIError(
            "Missing parameter, provide either mo_ref_id or inventory_item id."
        )

    custom_location_id = get_resource_id(
        cmd,
        resource_group_name,
        EXTENDED_LOCATION_NAMESPACE,
        CUSTOM_LOCATION_RESOURCE_TYPE,
        custom_location,
    )

    extended_location = ExtendedLocation(
        type=EXTENDED_LOCATION_TYPE, name=custom_location_id
    )

    inventory_item_id = None
    vcenter_id = None

    if inventory_item is not None:
        inventory_item_id = get_resource_id(
            cmd,
            resource_group_name,
            VMWARE_NAMESPACE,
            VCENTER_RESOURCE_TYPE,
            vcenter,
            INVENTORY_ITEM_TYPE,
            inventory_item,
        )
    else:
        if vcenter is None:
            raise CLIError("Missing parameter, provide vcenter name or id.")

        vcenter_id = get_resource_id(
            cmd, resource_group_name, VMWARE_NAMESPACE, VCENTER_RESOURCE_TYPE, vcenter
        )

    if inventory_item_id is not None:
        virtual_network = VirtualNetwork(
            location=location,
            extended_location=extended_location,
            inventory_item_id=inventory_item_id,
        )
    else:
        virtual_network = VirtualNetwork(
            location=location,
            extended_location=extended_location,
            v_center_id=vcenter_id,
            mo_ref_id=mo_ref_id,
        )

    return sdk_no_wait(
        no_wait,
        client.begin_create,
        resource_group_name,
        resource_name,
        virtual_network,
    )


def delete_virtual_network(
    client: VirtualNetworksOperations,
    resource_group_name,
    resource_name,
    force=False,
    no_wait=False,
):

    return sdk_no_wait(
        no_wait, client.begin_delete, resource_group_name, resource_name, force
    )


def show_virtual_network(
    client: VirtualNetworksOperations, resource_group_name, resource_name
):

    return client.get(resource_group_name, resource_name)


def list_virtual_network(
    client: VirtualNetworksOperations, resource_group_name=None
):

    if resource_group_name:
        return client.list_by_resource_group(resource_group_name)
    return client.list()


# endregion

# region VirtualMachineTemplates


def create_vm_template(
    cmd,
    client: VirtualMachineTemplatesOperations,
    resource_group_name,
    resource_name,
    custom_location,
    location,
    vcenter=None,
    mo_ref_id=None,
    inventory_item=None,
    tags=None,
    no_wait=True,
):

    if mo_ref_id is None and inventory_item is None:
        raise CLIError(
            "Missing parameter, provide either mo_ref_id or inventory_item id."
        )

    custom_location_id = get_resource_id(
        cmd,
        resource_group_name,
        EXTENDED_LOCATION_NAMESPACE,
        CUSTOM_LOCATION_RESOURCE_TYPE,
        custom_location,
    )

    extended_location = ExtendedLocation(
        type=EXTENDED_LOCATION_TYPE, name=custom_location_id
    )

    inventory_item_id = None
    vcenter_id = None

    if inventory_item is not None:
        inventory_item_id = get_resource_id(
            cmd,
            resource_group_name,
            VMWARE_NAMESPACE,
            VCENTER_RESOURCE_TYPE,
            vcenter,
            INVENTORY_ITEM_TYPE,
            inventory_item,
        )
    else:
        if vcenter is None:
            raise CLIError("Missing parameter, provide vcenter name or id.")

        vcenter_id = get_resource_id(
            cmd, resource_group_name, VMWARE_NAMESPACE, VCENTER_RESOURCE_TYPE, vcenter
        )

    if inventory_item_id is not None:
        vm_template = VirtualMachineTemplate(
            location=location,
            extended_location=extended_location,
            inventory_item_id=inventory_item_id,
        )
    else:
        vm_template = VirtualMachineTemplate(
            location=location,
            extended_location=extended_location,
            v_center_id=vcenter_id,
            mo_ref_id=mo_ref_id,
        )

    return sdk_no_wait(
        no_wait, client.begin_create, resource_group_name, resource_name, vm_template
    )


def delete_vm_template(
    client: VirtualMachineTemplatesOperations,
    resource_group_name,
    resource_name,
    force=False,
    no_wait=False,
):

    return sdk_no_wait(
        no_wait, client.begin_delete, resource_group_name, resource_name, force
    )


def show_vm_template(
    client: VirtualMachineTemplatesOperations, resource_group_name, resource_name
):

    return client.get(resource_group_name, resource_name)


def list_vm_template(
    client: VirtualMachineTemplatesOperations, resource_group_name=None
):

    if resource_group_name:
        return client.list_by_resource_group(resource_group_name)
    return client.list()


# endregion

# region VirtualMachines

def create_vm(
    cmd,
    client: VirtualMachinesOperations,
    resource_group_name,
    resource_name,
    custom_location,
    location,
    vcenter=None,
    resource_pool=None,
    vm_template=None,
    inventory_item=None,
    admin_username=None,
    admin_password=None,
    num_CPUs=None,
    num_cores_per_socket=None,
    memory_size=None,
    nics=None,
    disks=None,
    tags=None,
    no_wait=False,
):

    if vm_template is None and inventory_item is None:
        raise CLIError(
            "Missing parameter, provide either vm_template or inventory_item id."
        )

    hardware_profile = None
    os_profile = None
    network_profile = None
    storage_profile = None

    if num_CPUs is not None or memory_size is not None:
        hardware_profile = HardwareProfile(
            memory_size_mb=memory_size,
            num_cp_us=num_CPUs,
            num_cores_per_socket=num_cores_per_socket,
        )

    if admin_password is not None:
        os_profile = OsProfile(
            admin_username=admin_username, admin_password=admin_password
        )

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

    custom_location_id = get_resource_id(
        cmd,
        resource_group_name,
        EXTENDED_LOCATION_NAMESPACE,
        CUSTOM_LOCATION_RESOURCE_TYPE,
        custom_location,
    )

    extended_location = ExtendedLocation(
        type=EXTENDED_LOCATION_TYPE, name=custom_location_id
    )

    inventory_item_id = None
    vcenter_id = None
    vm_template_id = None
    resource_pool_id = None

    if inventory_item is not None:
        inventory_item_id = get_resource_id(
            cmd,
            resource_group_name,
            VMWARE_NAMESPACE,
            VCENTER_RESOURCE_TYPE,
            vcenter,
            INVENTORY_ITEM_TYPE,
            inventory_item,
        )
    else:
        if vcenter is None:
            raise CLIError("Missing parameter, provide vcenter name or id.")

        vcenter_id = get_resource_id(
            cmd, resource_group_name, VMWARE_NAMESPACE, VCENTER_RESOURCE_TYPE, vcenter
        )

    if vm_template is not None:
        vm_template_id = get_resource_id(
            cmd,
            resource_group_name,
            VMWARE_NAMESPACE,
            VMTEMPLATE_RESOURCE_TYPE,
            vm_template,
        )

    if resource_pool is not None:
        resource_pool_id = get_resource_id(
            cmd,
            resource_group_name,
            VMWARE_NAMESPACE,
            RESOURCEPOOL_RESOURCE_TYPE,
            resource_pool,
        )

    if inventory_item_id is not None:
        vm = VirtualMachine(
            location=location,
            extended_location=extended_location,
            hardware_profile=hardware_profile,
            os_profile=os_profile,
            network_profile=network_profile,
            storage_profile=storage_profile,
            inventory_item_id=inventory_item_id,
        )
    else:
        vm = VirtualMachine(
            location=location,
            extended_location=extended_location,
            v_center_id=vcenter_id,
            resource_pool_id=resource_pool_id,
            template_id=vm_template_id,
            hardware_profile=hardware_profile,
            os_profile=os_profile,
            network_profile=network_profile,
            storage_profile=storage_profile,
        )

    return sdk_no_wait(
        no_wait, client.begin_create, resource_group_name, resource_name, vm
    )


def update_vm(
    client: VirtualMachinesOperations,
    resource_group_name,
    resource_name,
    num_CPUs=None,
    num_cores_per_socket=None,
    memory_size=None,
    tags=None,
    no_wait=False,
):

    hardware_profile = None

    if (
        num_CPUs is None and
        num_cores_per_socket is None and
        memory_size is None and
        tags is None
    ):
        raise CLIError("No inputs were given to update the vm.")

    if (
        num_CPUs is not None or
        num_cores_per_socket is not None or
        memory_size is not None
    ):
        hardware_profile = HardwareProfile(
            memory_size_mb=memory_size,
            num_cp_us=num_CPUs,
            num_cores_per_socket=num_cores_per_socket,
        )

    vm_update = VirtualMachineUpdate(hardware_profile=hardware_profile)
    return sdk_no_wait(
        no_wait,
        client.begin_update,
        resource_group_name,
        resource_name,
        vm_update,
        tags,
    )


def delete_vm(
    client: VirtualMachinesOperations,
    resource_group_name,
    resource_name,
    force=False,
    no_wait=False,
):

    return sdk_no_wait(
        no_wait, client.begin_delete, resource_group_name, resource_name, force
    )


def show_vm(client: VirtualMachinesOperations, resource_group_name, resource_name):

    return client.get(resource_group_name, resource_name)


def list_vm(client: VirtualMachinesOperations, resource_group_name=None):

    if resource_group_name:
        return client.list_by_resource_group(resource_group_name)
    return client.list()


def start_vm(
    client: VirtualMachinesOperations,
    resource_group_name,
    resource_name,
    no_wait=False,
):

    return sdk_no_wait(no_wait, client.begin_start, resource_group_name, resource_name)


def stop_vm(
    client: VirtualMachinesOperations,
    resource_group_name,
    resource_name,
    skip_shutdown=False,
    no_wait=False,
):
    body = StopVirtualMachineOptions(skip_shutdown=skip_shutdown)

    return sdk_no_wait(
        no_wait,
        client.begin_stop,
        resource_group_name,
        resource_name,
        body
    )


def restart_vm(
    client: VirtualMachinesOperations,
    resource_group_name,
    resource_name,
    no_wait=False,
):

    return sdk_no_wait(
        no_wait, client.begin_restart, resource_group_name, resource_name
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
            power_on_boot=PowerOnBootOption.enabled, nic_type=NICType.vmxnet3
        )

        ip_settings = NicIPSettings(allocation_method=IPAddressAllocationMethod.dynamic)

        for key, value in input_nic.items():
            if key == NETWORK:
                nic.network_id = get_resource_id(
                    cmd,
                    resource_group_name,
                    VMWARE_NAMESPACE,
                    VIRTUALNETWORK_RESOURCE_TYPE,
                    value,
                )
            elif key == NAME_PARAMETER:
                nic.name = value
            elif key == DEVICE_KEY:
                nic.device_key = value
            elif key == NIC_TYPE:
                nic.nic_type = value
            elif key == POWER_ON_BOOT:
                nic.power_on_boot = value
            elif key == ALLOCATION_METHOD:
                ip_settings.allocation_method = value
            elif key == IP_ADDRESS:
                ip_settings.ip_address = value
            elif key == SUBNET_MASK:
                ip_settings.subnet_mask = value
            elif key == GATEWAY:
                ip_settings.gateway = value.split(GATEWAY_SEPERATOR)
            else:
                raise CLIError(
                    'Invalid parameter: {name} specified for nic.'.format(name=key)
                )

        nic.ip_settings = ip_settings
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
            elif key == DEVICE_KEY:
                disk.device_key = value
            elif key == DISK_MODE:
                disk.disk_mode = value
            elif key == DISK_SIZE:
                disk.disk_size_gb = value
            elif key == CONTROLLER_KEY:
                disk.controller_key = value
            elif key == UNIT_NUMBER:
                disk.unit_number = value
            else:
                raise CLIError(
                    'Invalid parameter: {name} specified for disk.'.format(name=key)
                )
        disks.append(disk)
    return disks


# endregion

# region VirtualMachine Nics.


def add_nic(
    cmd,
    client: VirtualMachinesOperations,
    resource_group_name,
    vm_name,
    nic_name,
    network,
    nic_type=NICType.vmxnet3.name,
    power_on_boot=PowerOnBootOption.disabled.name,
    no_wait=False,
):
    """
    Add virtual network interface to a virtual machine.
    """

    network_id = get_resource_id(
        cmd,
        resource_group_name,
        VMWARE_NAMESPACE,
        VIRTUALNETWORK_RESOURCE_TYPE,
        network,
    )

    nic_to_add = NetworkInterfaceUpdate(
        name=nic_name,
        network_id=network_id,
        power_on_boot=power_on_boot,
        nic_type=nic_type,
    )

    nics_update = []
    vm = client.get(resource_group_name, vm_name)
    if (
        vm.network_profile is not None and
        vm.network_profile.network_interfaces is not None
    ):
        for nic in vm.network_profile.network_interfaces:
            nic_update = NetworkInterfaceUpdate(
                name=nic.name,
                network_id=nic.network_id,
                power_on_boot=nic.power_on_boot,
                nic_type=nic.nic_type,
                device_key=nic.device_key,
            )
            nics_update.append(nic_update)

    nics_update.append(nic_to_add)
    network_profile = NetworkProfileUpdate(network_interfaces=nics_update)
    vm_update = VirtualMachineUpdate(network_profile=network_profile)

    return sdk_no_wait(
        no_wait, client.begin_update, resource_group_name, vm_name, vm_update
    )


def update_nic(
    cmd,
    client: VirtualMachinesOperations,
    resource_group_name,
    vm_name,
    nic_name=None,
    network=None,
    power_on_boot=None,
    device_key=None,
    no_wait=False,
):
    """
    Update virtual network interface of a virtual machine.
    """

    if nic_name is None and device_key is None:
        raise CLIError(
            "Either nic name or device key must be specified to update the nic."
        )

    network_id = None
    if network is not None:
        network_id = get_resource_id(
            cmd,
            resource_group_name,
            VMWARE_NAMESPACE,
            VIRTUALNETWORK_RESOURCE_TYPE,
            network,
        )

    nics_update = []
    nic_found = False
    vm = client.get(resource_group_name, vm_name)
    if (
        vm.network_profile is not None and
        vm.network_profile.network_interfaces is not None
    ):
        for nic in vm.network_profile.network_interfaces:
            nic_update = NetworkInterfaceUpdate(
                name=nic.name,
                network_id=nic.network_id,
                power_on_boot=nic.power_on_boot,
                nic_type=nic.nic_type,
                device_key=nic.device_key,
            )

            if (nic_name is not None and nic.name == nic_name) or (
                device_key is not None and nic.device_key == device_key
            ):

                # Validate nic name is matching with the expected device key if both were given in
                # the input when name is already assigned to the nic.
                if (
                    nic_name is not None and
                    nic.name is not None and
                    nic.name != nic_name
                ) or (device_key is not None and nic.device_key != device_key):
                    raise CLIError(
                        "Incorrect nic-name and device-key combination, Expected " +
                        "nic-name: " +
                        nic.name +
                        ", device-key: " +
                        str(nic.device_key) +
                        "."
                    )

                nic_found = True
                if nic.name is None and nic_name is not None:
                    nic_update.name = nic_name
                if network_id is not None:
                    nic_update.network_id = network_id
                if power_on_boot is not None:
                    nic_update.power_on_boot = power_on_boot

            nics_update.append(nic_update)

    if not nic_found:
        raise CLIError("Given nic is not present in the virtual machine.")

    network_profile = NetworkProfileUpdate(network_interfaces=nics_update)
    vm_update = VirtualMachineUpdate(network_profile=network_profile)

    return sdk_no_wait(
        no_wait, client.begin_update, resource_group_name, vm_name, vm_update
    )


def list_nics(client: VirtualMachinesOperations, resource_group_name, vm_name):
    """
    List details of a virtual machine nics.
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
        vm.network_profile is not None and
        vm.network_profile.network_interfaces is not None
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
    nics_to_delete = {}
    for nic_name in nic_names:
        nics_to_delete[nic_name] = True

    nics_update = []
    vm = client.get(resource_group_name, vm_name)
    if (
        vm.network_profile is not None and
        vm.network_profile.network_interfaces is not None
    ):
        for nic in vm.network_profile.network_interfaces:
            if nic.name in nics_to_delete:
                nics_to_delete[nic.name] = False
                continue
            nic_update = NetworkInterfaceUpdate(
                name=nic.name,
                network_id=nic.network_id,
                power_on_boot=nic.power_on_boot,
                nic_type=nic.nic_type,
                device_key=nic.device_key,
            )
            nics_update.append(nic_update)

    not_found_nics = ""
    for nic_name in nics_to_delete:
        if nics_to_delete[nic_name]:
            not_found_nics = not_found_nics + nic_name + ", "
    if not_found_nics != "":
        raise CLIError(
            "Nics with name " +
            not_found_nics +
            'not present in the given virtual machine.'
        )

    network_profile = NetworkProfileUpdate(network_interfaces=nics_update)
    vm_update = VirtualMachineUpdate(network_profile=network_profile)

    return sdk_no_wait(
        no_wait, client.begin_update, resource_group_name, vm_name, vm_update
    )


# endregion

# region VirtualMachine Disks.


def add_disk(
    client: VirtualMachinesOperations,
    resource_group_name,
    vm_name,
    disk_name,
    disk_size,
    controller_key,
    disk_mode=DiskMode.persistent.name,
    unit_number=None,
    no_wait=False,
):
    """
    Add virtual disk to a virtual machine.
    """

    disk_to_add = VirtualDiskUpdate(
        name=disk_name,
        disk_size_gb=disk_size,
        disk_mode=disk_mode,
        controller_key=controller_key,
        unit_number=unit_number,
    )

    disks_update = []
    vm = client.get(resource_group_name, vm_name)
    if vm.storage_profile is not None and vm.storage_profile.disks is not None:
        for disk in vm.storage_profile.disks:
            disk_update = VirtualDiskUpdate(
                name=disk.name,
                disk_size_gb=disk.disk_size_gb,
                disk_mode=disk.disk_mode,
                controller_key=disk.controller_key,
                unit_number=disk.unit_number,
                device_key=disk.device_key,
            )
            disks_update.append(disk_update)

    disks_update.append(disk_to_add)
    storage_profile = StorageProfileUpdate(disks=disks_update)
    vm_update = VirtualMachineUpdate(storage_profile=storage_profile)

    return sdk_no_wait(
        no_wait, client.begin_update, resource_group_name, vm_name, vm_update
    )


def update_disk(
    client: VirtualMachinesOperations,
    resource_group_name,
    vm_name,
    disk_name=None,
    disk_size=None,
    controller_key=None,
    disk_mode=None,
    unit_number=None,
    device_key=None,
    no_wait=False,
):
    """
    Update virtual disk of a virtual machine.
    """

    if disk_name is None and device_key is None:
        raise CLIError(
            "Either disk name or device key must be specified to update the disk."
        )

    disks_update = []
    disk_found = False
    vm = client.get(resource_group_name, vm_name)
    if vm.storage_profile is not None and vm.storage_profile.disks is not None:
        for disk in vm.storage_profile.disks:
            disk_update = VirtualDiskUpdate(
                name=disk.name,
                disk_size_gb=disk.disk_size_gb,
                disk_mode=disk.disk_mode,
                controller_key=disk.controller_key,
                unit_number=disk.unit_number,
                device_key=disk.device_key,
            )

            if (disk_name is not None and disk.name == disk_name) or (
                device_key is not None and disk.device_key == device_key
            ):

                # Validate disk name is matching with the expected device key if both were given in
                # the input when name is already assigned to the disk.
                if (
                    disk_name is not None and
                    disk.name is not None and
                    disk.name != disk_name
                ) or (device_key is not None and disk.device_key != device_key):
                    raise CLIError(
                        "Incorrect disk-name and device-key combination, Expected "
                        "disk-name: " +
                        disk.name +
                        ", device-key: " +
                        str(disk.device_key) +
                        "."
                    )

                disk_found = True
                if disk.name is None and disk_name is not None:
                    disk_update.name = disk_name
                if disk_size is not None:
                    disk_update.disk_size_gb = disk_size
                if disk_mode is not None:
                    disk_update.disk_mode = disk_mode
                if controller_key is not None:
                    disk_update.controller_key = controller_key
                if unit_number is not None:
                    disk_update.unit_number = unit_number

            disks_update.append(disk_update)

    if not disk_found:
        raise CLIError("Given disk is not present in the virtual machine.")

    storage_profile = StorageProfileUpdate(disks=disks_update)
    vm_update = VirtualMachineUpdate(storage_profile=storage_profile)

    return sdk_no_wait(
        no_wait, client.begin_update, resource_group_name, vm_name, vm_update
    )


def list_disks(client: VirtualMachinesOperations, resource_group_name, vm_name):
    """
    List details of a virtual machine disks.
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
    disks_to_delete = {}
    for disk_name in disk_names:
        disks_to_delete[disk_name] = True

    disks_update = []
    vm = client.get(resource_group_name, vm_name)
    if vm.storage_profile is not None and vm.storage_profile.disks is not None:
        for disk in vm.storage_profile.disks:
            if disk.name in disks_to_delete:
                disks_to_delete[disk.name] = False
                continue
            disk_update = VirtualDiskUpdate(
                name=disk.disk_name,
                disk_size_gb=disk.disk_size_gb,
                disk_mode=disk.disk_mode,
                controller_key=disk.controller_key,
                unit_number=disk.unit_number,
                device_key=disk.device_key,
            )
            disks_update.append(disk_update)

    not_found_disks = ""
    for disk_name in disks_to_delete:
        if disks_to_delete[disk_name]:
            not_found_disks = not_found_disks + disk_name + ", "
    if not_found_disks != "":
        raise CLIError(
            "Disks with name " +
            not_found_disks +
            "not present in the given virtual machine."
        )

    storage_profile = StorageProfileUpdate(disks=disks_update)
    vm_update = VirtualMachineUpdate(storage_profile=storage_profile)

    return sdk_no_wait(
        no_wait, client.begin_update, resource_group_name, vm_name, vm_update
    )


# endregion

# region InventoryItems


def show_inventory_item(
    client: InventoryItemsOperations,
    resource_group_name,
    vcenter_name,
    inventory_item_name
):

    return client.get(resource_group_name, vcenter_name, inventory_item_name)


def list_inventory_item(
    client: InventoryItemsOperations, resource_group_name, vcenter_name
):

    return client.list_by_v_center(resource_group_name, vcenter_name)


# endregion
