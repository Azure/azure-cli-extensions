# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable= too-many-lines, too-many-locals, unused-argument, too-many-branches, too-many-statements
# pylint: disable= consider-using-dict-items, consider-using-f-string

from azure.cli.command_modules.acs._client_factory import get_resources_client
from azure.cli.core.util import sdk_no_wait
from azure.cli.core.azclierror import (
    UnrecognizedArgumentError,
    RequiredArgumentMissingError,
    MutuallyExclusiveArgumentError,
    InvalidArgumentValueError,
)
from azure.core.exceptions import ResourceNotFoundError  # type: ignore
from msrestazure.tools import is_valid_resource_id

from .pwinput import pwinput
from .vmware_utils import get_resource_id
from .vmware_constants import (
    VCENTER_KIND_GET_API_VERSION,
    MACHINES_RESOURCE_TYPE,
    VMWARE_NAMESPACE,
    VCENTER_RESOURCE_TYPE,
    RESOURCEPOOL_RESOURCE_TYPE,
    CLUSTER_RESOURCE_TYPE,
    HOST_RESOURCE_TYPE,
    DATASTORE_RESOURCE_TYPE,
    VMTEMPLATE_RESOURCE_TYPE,
    VIRTUALNETWORK_RESOURCE_TYPE,
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
    UNIT_NUMBER,
    VM_SYSTEM_ASSIGNED_INDENTITY_TYPE,
    GUEST_AGENT_PROVISIONING_ACTION_INSTALL,
    EXTENSIONS_RESOURCE_TYPE,
    HCRP_NAMESPACE,
)

from .vendored_sdks.connectedvmware.models import (
    DiskMode,
    HardwareProfile,
    InfrastructureProfile,
    InventoryItem,
    InventoryType,
    IPAddressAllocationMethod,
    NetworkInterface,
    NetworkInterfaceUpdate,
    NetworkProfile,
    NetworkProfileUpdate,
    NicIPSettings,
    NICType,
    OsProfileForVMInstance,
    PowerOnBootOption,
    ResourcePool,
    Cluster,
    Datastore,
    Host,
    StorageProfile,
    StorageProfileUpdate,
    VCenter,
    VICredential,
    VirtualDisk,
    VirtualDiskUpdate,
    VirtualMachineInstance,
    VirtualMachineInstanceUpdate,
    VirtualMachineTemplate,
    VirtualNetwork,
    ExtendedLocation,
    StopVirtualMachineOptions,
    GuestAgent,
    GuestCredential,
    PlacementProfile,
    HttpProxyConfiguration,
)

from .vendored_sdks.hybridcompute.models import (
    Identity,
    Machine,
    MachineExtension,
    MachineExtensionUpdate,
    MachineUpdate,
)

from .vendored_sdks.connectedvmware.operations import (
    VCentersOperations,
    ResourcePoolsOperations,
    ClustersOperations,
    DatastoresOperations,
    HostsOperations,
    VirtualNetworksOperations,
    VirtualMachineTemplatesOperations,
    VirtualMachineInstancesOperations,
    VMInstanceGuestAgentsOperations,
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

# region VCenters


def connect_vcenter(
    cmd,
    client: VCentersOperations,
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

    creds_ok = all(inp is not None for inp in [fqdn, username, password])
    while not creds_ok:
        creds = {
            'fqdn': fqdn,
            'username': username,
            'password': password,
        }
        while not creds['fqdn']:
            print('Please provide vcenter FQDN or IP address: ', end='')
            creds['fqdn'] = input()
            if not creds['fqdn']:
                print('Parameter is required, please try again')
        while not creds['username']:
            print('Please provide vcenter username: ', end='')
            creds['username'] = input()
            if not creds['username']:
                print('Parameter is required, please try again')
        while not creds['password']:
            creds['password'] = pwinput('Please provide vcenter password: ')
            if not creds['password']:
                print('Parameter is required, please try again')
                continue
            passwdConfim = pwinput('Please confirm vcenter password: ')
            if creds['password'] != passwdConfim:
                print('Passwords do not match, please try again')
                creds['password'] = None
        print('Confirm vcenter details? [Y/n]: ', end='')
        res = input().lower()
        if res in ['y', '']:
            fqdn, username, password = creds['fqdn'], creds['username'], creds['password']
            creds_ok = True
        elif res != 'n':
            print('Please type y/n or leave empty.')
    assert fqdn

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
        tags=tags
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

# region InventoryItems


def show_inventory_item(
    cmd,
    client: InventoryItemsOperations,
    resource_group_name,
    vcenter,
    inventory_item
):

    inventory_item_id = get_resource_id(
        cmd,
        resource_group_name,
        VMWARE_NAMESPACE,
        VCENTER_RESOURCE_TYPE,
        vcenter,
        child_type_1=INVENTORY_ITEM_TYPE,
        child_name_1=inventory_item,
    )
    assert inventory_item_id is not None
    vcenter_sub = inventory_item_id.split("/")[2]
    resources_client = get_resources_client(cmd.cli_ctx, vcenter_sub)
    return resources_client.get_by_id(inventory_item_id, VCENTER_KIND_GET_API_VERSION)


def list_inventory_item(
    client: InventoryItemsOperations, resource_group_name, vcenter
):

    return client.list_by_v_center(resource_group_name, vcenter.split('/')[-1])


# endregion

# region ResourcePools


def create_resource_pool(
    cmd,
    client: ResourcePoolsOperations,
    resource_group_name,
    resource_name,
    custom_location,
    location,
    vcenter,
    inventory_item,
    tags=None,
    no_wait=False,
):

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

    inventory_item_id = get_resource_id(
        cmd,
        resource_group_name,
        VMWARE_NAMESPACE,
        VCENTER_RESOURCE_TYPE,
        vcenter,
        child_type_1=INVENTORY_ITEM_TYPE,
        child_name_1=inventory_item,
    )

    resource_pool = ResourcePool(
        location=location,
        extended_location=extended_location,
        inventory_item_id=inventory_item_id,
        tags=tags
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

# region Clusters


def create_cluster(
    cmd,
    client: ClustersOperations,
    resource_group_name,
    resource_name,
    custom_location,
    location,
    vcenter,
    inventory_item,
    tags=None,
    no_wait=False,
):

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

    inventory_item_id = get_resource_id(
        cmd,
        resource_group_name,
        VMWARE_NAMESPACE,
        VCENTER_RESOURCE_TYPE,
        vcenter,
        child_type_1=INVENTORY_ITEM_TYPE,
        child_name_1=inventory_item,
    )

    cluster = Cluster(
        location=location,
        extended_location=extended_location,
        inventory_item_id=inventory_item_id,
        tags=tags
    )

    return sdk_no_wait(
        no_wait, client.begin_create, resource_group_name, resource_name, cluster
    )


def delete_cluster(
    client: ClustersOperations,
    resource_group_name,
    resource_name,
    force=False,
    no_wait=False,
):

    return sdk_no_wait(
        no_wait, client.begin_delete, resource_group_name, resource_name, force
    )


def show_cluster(
    client: ClustersOperations, resource_group_name, resource_name
):

    return client.get(resource_group_name, resource_name)


def list_cluster(client: ClustersOperations, resource_group_name=None):

    if resource_group_name:
        return client.list_by_resource_group(resource_group_name)
    return client.list()


# endregion

# region Datastores


def create_datastore(
    cmd,
    client: DatastoresOperations,
    resource_group_name,
    resource_name,
    custom_location,
    location,
    vcenter,
    inventory_item,
    tags=None,
    no_wait=False,
):

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

    inventory_item_id = get_resource_id(
        cmd,
        resource_group_name,
        VMWARE_NAMESPACE,
        VCENTER_RESOURCE_TYPE,
        vcenter,
        child_type_1=INVENTORY_ITEM_TYPE,
        child_name_1=inventory_item,
    )

    datastore = Datastore(
        location=location,
        extended_location=extended_location,
        inventory_item_id=inventory_item_id,
        tags=tags
    )

    return sdk_no_wait(
        no_wait, client.begin_create, resource_group_name, resource_name, datastore
    )


def delete_datastore(
    client: DatastoresOperations,
    resource_group_name,
    resource_name,
    force=False,
    no_wait=False,
):

    return sdk_no_wait(
        no_wait, client.begin_delete, resource_group_name, resource_name, force
    )


def show_datastore(
    client: DatastoresOperations, resource_group_name, resource_name
):

    return client.get(resource_group_name, resource_name)


def list_datastore(client: DatastoresOperations, resource_group_name=None):

    if resource_group_name:
        return client.list_by_resource_group(resource_group_name)
    return client.list()


# endregion

# region Hosts


def create_host(
    cmd,
    client: HostsOperations,
    resource_group_name,
    resource_name,
    custom_location,
    location,
    vcenter,
    inventory_item,
    tags=None,
    no_wait=False,
):

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

    inventory_item_id = get_resource_id(
        cmd,
        resource_group_name,
        VMWARE_NAMESPACE,
        VCENTER_RESOURCE_TYPE,
        vcenter,
        child_type_1=INVENTORY_ITEM_TYPE,
        child_name_1=inventory_item,
    )

    host = Host(
        location=location,
        extended_location=extended_location,
        inventory_item_id=inventory_item_id,
        tags=tags
    )

    return sdk_no_wait(
        no_wait, client.begin_create, resource_group_name, resource_name, host
    )


def delete_host(
    client: HostsOperations,
    resource_group_name,
    resource_name,
    force=False,
    no_wait=False,
):

    return sdk_no_wait(
        no_wait, client.begin_delete, resource_group_name, resource_name, force
    )


def show_host(
    client: HostsOperations, resource_group_name, resource_name
):

    return client.get(resource_group_name, resource_name)


def list_host(client: HostsOperations, resource_group_name=None):

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
    vcenter,
    inventory_item,
    tags=None,
    no_wait=False,
):

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

    inventory_item_id = get_resource_id(
        cmd,
        resource_group_name,
        VMWARE_NAMESPACE,
        VCENTER_RESOURCE_TYPE,
        vcenter,
        child_type_1=INVENTORY_ITEM_TYPE,
        child_name_1=inventory_item,
    )

    virtual_network = VirtualNetwork(
        location=location,
        extended_location=extended_location,
        inventory_item_id=inventory_item_id,
        tags=tags
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
    vcenter,
    inventory_item,
    tags=None,
    no_wait=True,
):

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

    inventory_item_id = get_resource_id(
        cmd,
        resource_group_name,
        VMWARE_NAMESPACE,
        VCENTER_RESOURCE_TYPE,
        vcenter,
        child_type_1=INVENTORY_ITEM_TYPE,
        child_name_1=inventory_item,
    )

    vm_template = VirtualMachineTemplate(
        location=location,
        extended_location=extended_location,
        inventory_item_id=inventory_item_id,
        tags=tags
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


def create_vm(
    cmd,
    client: VirtualMachineInstancesOperations,
    resource_group_name,
    resource_name,
    custom_location,
    location=None,
    vcenter=None,
    vm_template=None,
    resource_pool=None,
    cluster=None,
    host=None,
    datastore=None,
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
    if not any([vm_template, inventory_item, datastore]):
        raise RequiredArgumentMissingError(
            "either vm_template, inventory_item id or datastore must be provided."
        )

    if vm_template is not None or datastore is not None:
        if not any([resource_pool, cluster, host]):
            raise RequiredArgumentMissingError(
                "either resource_pool, cluster or host must be provided while creating a VM."
            )

    if len([i for i in [resource_pool, cluster, host] if i is not None]) > 1:
        raise MutuallyExclusiveArgumentError(
            "at max one of resource_pool, cluster or host can be provided."
        )

    if inventory_item is not None:
        if vm_template is not None:
            raise MutuallyExclusiveArgumentError(
                "both vm_template and inventory_item id cannot be provided together."
            )

        if any([resource_pool, cluster, host, datastore]):
            raise MutuallyExclusiveArgumentError(
                "Placement input cannot be provided together with inventory_item."
            )

        if not is_valid_resource_id(inventory_item) and not vcenter:
            raise RequiredArgumentMissingError(
                "Cannot determine inventory item ID. " +
                "vCenter name or ID is required when inventory item name is specified."
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
        os_profile = OsProfileForVMInstance(
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

    vm = None

    # infrastructure profile parametes
    infrastructure_profile = None
    inventory_item_id = None
    vcenter_id = None
    vm_template_id = None

    # placement profile parameters
    placement_profile = None
    resource_pool_id = None
    cluster_id = None
    host_id = None
    datastore_id = None

    if inventory_item is not None:
        inventory_item_id = get_resource_id(
            cmd,
            resource_group_name,
            VMWARE_NAMESPACE,
            VCENTER_RESOURCE_TYPE,
            vcenter,
            child_type_1=INVENTORY_ITEM_TYPE,
            child_name_1=inventory_item,
        )
        assert inventory_item_id is not None

        vcenter_id = "/".join(inventory_item_id.rstrip("/").split("/")[:-2])

        infrastructure_profile = InfrastructureProfile(
            inventory_item_id=inventory_item_id,
        )
    else:
        if vcenter is None:
            raise RequiredArgumentMissingError("Missing parameter, provide vcenter name or id.")

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

        if cluster is not None:
            cluster_id = get_resource_id(
                cmd,
                resource_group_name,
                VMWARE_NAMESPACE,
                CLUSTER_RESOURCE_TYPE,
                cluster,
            )

        if host is not None:
            host_id = get_resource_id(
                cmd,
                resource_group_name,
                VMWARE_NAMESPACE,
                HOST_RESOURCE_TYPE,
                host,
            )

        if datastore is not None:
            datastore_id = get_resource_id(
                cmd,
                resource_group_name,
                VMWARE_NAMESPACE,
                DATASTORE_RESOURCE_TYPE,
                datastore,
            )

        placement_profile = PlacementProfile(
            resource_pool_id=resource_pool_id,
            cluster_id=cluster_id,
            host_id=host_id,
            datastore_id=datastore_id,
        )

        infrastructure_profile = InfrastructureProfile(
            v_center_id=vcenter_id,
            template_id=vm_template_id,
        )

    vm = VirtualMachineInstance(
        extended_location=extended_location,
        placement_profile=placement_profile,
        hardware_profile=hardware_profile,
        os_profile=os_profile,
        network_profile=network_profile,
        storage_profile=storage_profile,
        infrastructure_profile=infrastructure_profile,
    )

    assert vcenter_id is not None

    # The subscription of the vCenter can be different from the machine resource.
    # There was no straightforward way to change the subscription for vcenter client factory.
    # Hence using the generic get client.
    vcenter_sub = vcenter_id.split("/")[2]
    resources_client = get_resources_client(cmd.cli_ctx, vcenter_sub)
    vcenter = resources_client.get_by_id(vcenter_id, VCENTER_KIND_GET_API_VERSION)

    machine_client = cf_machine(cmd.cli_ctx)
    machine = None
    try:
        machine = machine_client.get(resource_group_name, resource_name)
        machine_kind = None
        if f"{machine.kind}".lower() != f"{vcenter.kind}".lower():
            if machine.kind:
                raise InvalidArgumentValueError(
                    "The existing Machine resource is not of the same kind as the vCenter. " +
                    f"Machine kind: '{machine.kind}', vCenter kind: '{vcenter.kind}'"
                )
            machine_kind = vcenter.kind
        if location is not None and machine.location != location:
            raise InvalidArgumentValueError(
                "The location of the existing Machine cannot be updated. " +
                "Either specify the existing location or keep the location unspecified. " +
                f"Existing location: {machine.location}, Provided location: {location}"
            )
        if any(x is not None for x in [machine_kind, tags]):
            m = MachineUpdate(
                kind=machine_kind,
                tags=tags,
            )
            machine = machine_client.update(resource_group_name, resource_name, m)
    except ResourceNotFoundError as e:
        if location is None:
            raise RequiredArgumentMissingError(
                "The parent Machine resource does not exist, " +
                "location is required while creating a new machine."
            ) from e
        m = Machine(
            location=location,
            kind=vcenter.kind,
            tags=tags,
        )
        machine = machine_client.create_or_update(resource_group_name, resource_name, m)

    assert machine.id is not None
    return sdk_no_wait(
        no_wait, client.begin_create_or_update, machine.id, vm
    )


def update_vm(
    cmd,
    client: VirtualMachineInstancesOperations,
    resource_group_name,
    resource_name,
    num_CPUs=None,
    num_cores_per_socket=None,
    memory_size=None,
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

    if (
        num_CPUs is None and
        num_cores_per_socket is None and
        memory_size is None and
        tags is None
    ):
        raise RequiredArgumentMissingError("No inputs were given to update the vm.")

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

    if hardware_profile is None:
        return client.get(machine_id)

    vm_update = VirtualMachineInstanceUpdate(
        hardware_profile=hardware_profile,
    )

    return sdk_no_wait(
        no_wait,
        client.begin_update,
        machine_id,
        vm_update
    )


def delete_vm(
    cmd,
    client: VirtualMachineInstancesOperations,
    resource_group_name,
    resource_name,
    force=None,
    delete_from_host=None,
    delete_machine=None,
    retain=None,
    no_wait=False,
):

    if retain and delete_from_host:
        raise MutuallyExclusiveArgumentError(
            "Arguments --retain and --delete-from-host cannot be used together." +
            "VM is retained in VMWare by default, it is deleted when --delete-from-host is provided."
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
                "Cannot delete VMWare VM from host when --no-wait and --delete-machine is provided."
            )
        machine_client.delete(resource_group_name, resource_name)
        return

    try:
        op = sdk_no_wait(
            no_wait, client.begin_delete, machine_id, delete_from_host, force,
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


def list_vm(
    cmd,
    resource_group_name=None,
):
    resources_filter = "resourceType eq 'Microsoft.ConnectedVMwarevSphere/VirtualMachineInstances'"
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
    skip_shutdown=False,
    no_wait=False,
):
    machine_id = get_hcrp_machine_id(
        cmd,
        resource_group_name,
        resource_name,
    )
    body = StopVirtualMachineOptions(skip_shutdown=skip_shutdown)

    return sdk_no_wait(
        no_wait,
        client.begin_stop,
        machine_id,
        body
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
        no_wait, client.begin_restart, machine_id,
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
                raise UnrecognizedArgumentError(
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
                raise UnrecognizedArgumentError(
                    'Invalid parameter: {name} specified for disk.'.format(name=key)
                )
        disks.append(disk)
    return disks


# endregion

# region VirtualMachine Nics.


def add_nic(
    cmd,
    client: VirtualMachineInstancesOperations,
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

    machine_id = get_hcrp_machine_id(
        cmd,
        resource_group_name,
        vm_name,
    )

    nics_update = []
    vm = client.get(machine_id)
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
    vm_update = VirtualMachineInstanceUpdate(network_profile=network_profile)

    return sdk_no_wait(
        no_wait, client.begin_update, machine_id, vm_update
    )


def update_nic(
    cmd,
    client: VirtualMachineInstancesOperations,
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
        raise RequiredArgumentMissingError(
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

    machine_id = get_hcrp_machine_id(
        cmd,
        resource_group_name,
        vm_name,
    )

    nics_update = []
    nic_found = False
    vm = client.get(machine_id)
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
                    raise InvalidArgumentValueError(
                        "Incorrect nic-name and device-key combination, Expected " +
                        "nic-name: " +
                        str(nic.name) +
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
        raise InvalidArgumentValueError("Given nic is not present in the virtual machine.")

    network_profile = NetworkProfileUpdate(network_interfaces=nics_update)
    vm_update = VirtualMachineInstanceUpdate(network_profile=network_profile)

    return sdk_no_wait(
        no_wait, client.begin_update, machine_id, vm_update
    )


def list_nics(
    cmd,
    client: VirtualMachineInstancesOperations,
    resource_group_name,
    vm_name,
):
    """
    List details of a virtual machine nics.
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
    resource_group_name,
    vm_name,
    nic_name,
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
        vm.network_profile is not None and
        vm.network_profile.network_interfaces is not None
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
    nics_to_delete = {}
    for nic_name in nic_names:
        nics_to_delete[nic_name] = True

    nics_update = []
    vm = client.get(machine_id)
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
        raise InvalidArgumentValueError(
            "Nics with name " +
            not_found_nics +
            'not present in the given virtual machine.'
        )

    network_profile = NetworkProfileUpdate(network_interfaces=nics_update)
    vm_update = VirtualMachineInstanceUpdate(network_profile=network_profile)

    return sdk_no_wait(
        no_wait, client.begin_update, machine_id, vm_update
    )


# endregion

# region VirtualMachine Disks.


def add_disk(
    cmd,
    client: VirtualMachineInstancesOperations,
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
                disk_mode=disk.disk_mode,
                controller_key=disk.controller_key,
                unit_number=disk.unit_number,
                device_key=disk.device_key,
            )
            disks_update.append(disk_update)

    disks_update.append(disk_to_add)
    storage_profile = StorageProfileUpdate(disks=disks_update)
    vm_update = VirtualMachineInstanceUpdate(storage_profile=storage_profile)

    return sdk_no_wait(
        no_wait, client.begin_update, machine_id, vm_update
    )


def update_disk(
    cmd,
    client: VirtualMachineInstancesOperations,
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
        raise RequiredArgumentMissingError(
            "Either disk name or device key must be specified to update the disk."
        )

    machine_id = get_hcrp_machine_id(
        cmd,
        resource_group_name,
        vm_name,
    )

    disks_update = []
    disk_found = False
    vm = client.get(machine_id)
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
                    raise InvalidArgumentValueError(
                        "Incorrect disk-name and device-key combination, Expected "
                        "disk-name: " +
                        str(disk.name) +
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
        raise InvalidArgumentValueError("The provided disk is not present in the virtual machine.")

    storage_profile = StorageProfileUpdate(disks=disks_update)
    vm_update = VirtualMachineInstanceUpdate(storage_profile=storage_profile)

    return sdk_no_wait(
        no_wait, client.begin_update, machine_id, vm_update
    )


def list_disks(
    cmd,
    client: VirtualMachineInstancesOperations,
    resource_group_name,
    vm_name,
):
    """
    List details of a virtual machine disks.
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
    disks_to_delete = {}
    for disk_name in disk_names:
        disks_to_delete[disk_name] = True

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
        raise InvalidArgumentValueError(
            "Disks with name " +
            not_found_disks +
            "not present in the given virtual machine."
        )

    storage_profile = StorageProfileUpdate(disks=disks_update)
    vm_update = VirtualMachineInstanceUpdate(storage_profile=storage_profile)

    return sdk_no_wait(
        no_wait, client.begin_update, machine_id, vm_update
    )


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


def connectedvmware_extension_list(
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


def connectedvmware_extension_show(
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


def connectedvmware_extension_create(
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
        child_name_1=name
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


def connectedvmware_extension_update(
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


def connectedvmware_extension_delete(
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
