from azure.cli.core.util import sdk_no_wait

def add_machine(cmd, client, raw_parameters, no_wait):
    resource_group_name = raw_parameters.get("resource_group_name")
    cluster_name = raw_parameters.get("cluster_name")
    agentpool_name = raw_parameters.get("agentpool_name")
    machine_name = raw_parameters.get("machine_name")

    namespace_config = constructNamespace(cmd, raw_parameters, namespace_name)
    namespace_config.location = get_cluster_location(cmd, resource_group_name, cluster_name)

    return sdk_no_wait(
        no_wait,
        client.begin_create_or_update,
        resource_group_name,
        cluster_name,
        namespace_name,
        namespace_config,
        headers=headers,
    )

def constructMachine(cmd, raw_parameters, machine_name):
    tags = raw_parameters.get("tags", {})
    labels_raw = raw_parameters.get("labels")
    labels = parse_key_value_list(labels_raw)
    annotations_raw = raw_parameters.get("annotations")
    annotations = parse_key_value_list(annotations_raw)
    zones = raw_parameters.get("zones", [])

    MachineProperties = cmd.get_models(
        "MachineProperties",
        resource_type=CUSTOM_MGMT_AKS_PREVIEW,
        operation_group="machines"
    )

    machine_properties = MachineProperties(
        hardware_profile=set_vm_size(raw_parameters),
        labels=labels,
        annotations=annotations,
        default_resource_quota=setResourceQuota(cmd, raw_parameters),
        default_network_policy=setNetworkPolicyRule(cmd, raw_parameters),
        adoption_policy=setAdoptionPolicy(raw_parameters),
        delete_policy=setDeletePolicy(raw_parameters)
    )

    Machine = cmd.get_models(
        "Machine", 
        resource_type=CUSTOM_MGMT_AKS_PREVIEW,
        operation_group="machines"
    )
    machine = Machine()
    machine.zones = zones
    machine.properties = machine_properties
    return machine

def set_vm_size(raw_parameters):
    vm_size = raw_parameters.get("vm_size")
    if not vm_size:
        raise ValueError("VM size is required for machine creation.")
    MachineHardwareProfile = cmd.get_models(
        "MachineHardwareProfile",
        resource_type=CUSTOM_MGMT_AKS_PREVIEW,
        operation_group="machines"
    )
    mhp = MachineHardwareProfile(vm_size=vm_size)
    return mhp