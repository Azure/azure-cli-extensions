# pylint: disable=too-many-lines
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_aks_preview._client_factory import CUSTOM_MGMT_AKS_PREVIEW

from azure.cli.core.azclierror import RequiredArgumentMissingError

from azure.cli.core.util import sdk_no_wait


def parse_key_value_list(pairs):
    if pairs is None:
        return None
    if isinstance(pairs, dict):
        return pairs.copy()
    if isinstance(pairs, str):
        pairs = [pairs]
    result = {}
    for pair in pairs:
        if "=" not in pair:
            raise ValueError(f"Invalid format '{pair}'. Expected format key=value.")
        key, value = pair.split("=", 1)
        result[key.strip()] = value.strip()
    return result


def construct_flexnode_machine(cmd, raw_parameters, existed_machine=None):
    """Construct the minimal Machine payload supported by FlexNodes."""
    if raw_parameters.get("machine_name") is None:
        raise RequiredArgumentMissingError("Please specify --machine-name.")

    MachineKubernetesProfile = cmd.get_models(
        "MachineKubernetesProfile",
        resource_type=CUSTOM_MGMT_AKS_PREVIEW,
        operation_group="machines",
    )
    MachineProperties = cmd.get_models(
        "MachineProperties",
        resource_type=CUSTOM_MGMT_AKS_PREVIEW,
        operation_group="machines",
    )
    Machine = cmd.get_models(
        "Machine",
        resource_type=CUSTOM_MGMT_AKS_PREVIEW,
        operation_group="machines",
    )

    existing_kubernetes = None
    if existed_machine is not None and existed_machine.properties is not None:
        existing_kubernetes = existed_machine.properties.kubernetes

    labels = existing_kubernetes.node_labels if existing_kubernetes is not None else None
    if raw_parameters.get("labels") is not None:
        labels = parse_key_value_list(raw_parameters.get("labels"))

    node_taints = existing_kubernetes.node_taints if existing_kubernetes is not None else None
    if raw_parameters.get("node_taints") is not None:
        raw_taints = raw_parameters.get("node_taints")
        node_taints = [x.strip() for x in (raw_taints.split(",") if raw_taints else [])]

    # maxPods is create-only for FlexNode Machines; preserve it on update.
    max_pods = raw_parameters.get("max_pods")
    if existing_kubernetes is not None:
        max_pods = existing_kubernetes.max_pods

    kubernetes = MachineKubernetesProfile(
        node_labels=labels,
        node_taints=node_taints,
        orchestrator_version=(
            raw_parameters.get("kubernetes_version")
            if raw_parameters.get("kubernetes_version") is not None
            else existing_kubernetes.orchestrator_version
            if existing_kubernetes is not None
            else None
        ),
        max_pods=max_pods,
    )
    return Machine(properties=MachineProperties(kubernetes=kubernetes))


def add_flexnode_machine(cmd, client, raw_parameters, no_wait):
    machine = construct_flexnode_machine(cmd, raw_parameters)
    return sdk_no_wait(
        no_wait,
        client.begin_create_or_update,
        raw_parameters.get("resource_group_name"),
        raw_parameters.get("cluster_name"),
        raw_parameters.get("nodepool_name"),
        raw_parameters.get("machine_name"),
        machine,
    )


def update_flexnode_machine(cmd, client, raw_parameters, existed_machine, no_wait):
    machine = construct_flexnode_machine(cmd, raw_parameters, existed_machine)
    return sdk_no_wait(
        no_wait,
        client.begin_create_or_update,
        raw_parameters.get("resource_group_name"),
        raw_parameters.get("cluster_name"),
        raw_parameters.get("nodepool_name"),
        raw_parameters.get("machine_name"),
        machine,
    )


def add_machine(cmd, client, raw_parameters, no_wait):
    resource_group_name = raw_parameters.get("resource_group_name")
    cluster_name = raw_parameters.get("cluster_name")
    nodepool_name = raw_parameters.get("nodepool_name")
    machine_name = raw_parameters.get("machine_name")

    machine = constructMachine(cmd, raw_parameters, machine_name)

    return sdk_no_wait(
        no_wait,
        client.begin_create_or_update,
        resource_group_name,
        cluster_name,
        nodepool_name,
        machine_name,
        machine,
    )


def update_machine(client, raw_parameters, existedMachine, no_wait):
    resource_group_name = raw_parameters.get("resource_group_name")
    cluster_name = raw_parameters.get("cluster_name")
    nodepool_name = raw_parameters.get("nodepool_name")
    machine_name = raw_parameters.get("machine_name")

    updated_machine = updateMachine(raw_parameters, existedMachine)

    return sdk_no_wait(
        no_wait,
        client.begin_create_or_update,
        resource_group_name,
        cluster_name,
        nodepool_name,
        machine_name,
        updated_machine,
    )


def updateMachine(raw_parameters, existedMachine):
    existedMachine = update_machine_tags(raw_parameters, existedMachine)
    existedMachine.properties.kubernetes = update_machine_kubernetes_profile_taints_labels(
        raw_parameters,
        existedMachine
    )

    return existedMachine


def constructMachine(cmd, raw_parameters, machine_name):
    machine_name = raw_parameters.get("machine_name")
    if machine_name is None:
        raise RequiredArgumentMissingError(
            "Please specify --machine-name."
        )
    MachineProperties = cmd.get_models(
        "MachineProperties",
        resource_type=CUSTOM_MGMT_AKS_PREVIEW,
        operation_group="machines"
    )
    tags = raw_parameters.get("tags")
    priority = raw_parameters.get("priority")
    eviction_policy = raw_parameters.get("eviction_policy")
    machineProperties = MachineProperties(
        tags=tags,
        priority=priority,
        eviction_policy=eviction_policy,
        network=set_machine_network(cmd, raw_parameters),
        hardware=set_machine_hardware_profile(cmd, raw_parameters),
        kubernetes=set_machine_kubernetes_profile(cmd, raw_parameters),
        operating_system=set_machine_os_profile(cmd, raw_parameters),
        billing=set_machine_billing_profile(cmd, raw_parameters)
    )

    Machine = cmd.get_models(
        "Machine",
        resource_type=CUSTOM_MGMT_AKS_PREVIEW,
        operation_group="machines"
    )
    zones = raw_parameters.get("zones", [])
    machine = Machine(
        zones=zones,
        properties=machineProperties
    )
    return machine


def set_machine_hardware_profile(cmd, raw_parameters):
    enable_ultra_ssd = raw_parameters.get("enable_ultra_ssd")
    vm_size = raw_parameters.get("vm_size")
    if vm_size is None:
        raise RequiredArgumentMissingError(
            "Please specify --vm-size."
        )
    MachineHardwareProfile = cmd.get_models(
        "MachineHardwareProfile",
        resource_type=CUSTOM_MGMT_AKS_PREVIEW,
        operation_group="machines"
    )
    machine_hardware_profile = MachineHardwareProfile(
        vm_size=vm_size,
        ultra_ssd_enabled=enable_ultra_ssd
    )
    return machine_hardware_profile


def set_machine_network(cmd, raw_parameters):
    MachineNetworkProperties = cmd.get_models(
        "MachineNetworkProperties",
        resource_type=CUSTOM_MGMT_AKS_PREVIEW,
        operation_group="machines"
    )
    vnet_subnet_id = raw_parameters.get("vnet_subnet_id")
    pod_subnet_id = raw_parameters.get("pod_subnet_id")
    enable_node_public_ip = raw_parameters.get("enable_node_public_ip")
    node_public_ip_prefix_id = raw_parameters.get("node_public_ip_prefix_id")
    node_public_ip_tags = raw_parameters.get("node_public_ip_tags")
    machineNetworkProperties = MachineNetworkProperties(
        vnet_subnet_id=vnet_subnet_id,
        pod_subnet_id=pod_subnet_id,
        enable_node_public_ip=enable_node_public_ip,
        node_public_ip_prefix_id=node_public_ip_prefix_id,
        node_public_ip_tags=node_public_ip_tags
    )
    return machineNetworkProperties


def set_machine_kubernetes_profile(cmd, raw_parameters):
    kubernetes_version = raw_parameters.get("kubernetes_version")
    MachineKubernetesProfile = cmd.get_models(
        "MachineKubernetesProfile",
        resource_type=CUSTOM_MGMT_AKS_PREVIEW,
        operation_group="machines"
    )
    machineKubernetesProfile = MachineKubernetesProfile(
        orchestrator_version=kubernetes_version
    )
    return machineKubernetesProfile


def update_machine_tags(raw_parameters, existedMachine):
    tags = raw_parameters.get("tags")
    if tags is not None and len(tags) != 0:
        existedMachine.properties.tags = tags
    return existedMachine


def update_machine_kubernetes_profile_taints_labels(raw_parameters, existedMachine):
    taints_raw = raw_parameters.get("node_taints")
    if taints_raw is not None:
        node_taints = [x.strip() for x in (taints_raw.split(",") if taints_raw else [])]
        existedMachine.properties.kubernetes.node_taints = node_taints

    labels_raw = raw_parameters.get("labels")
    labels = parse_key_value_list(labels_raw)
    if labels is not None and len(labels) != 0:
        existedMachine.properties.kubernetes.node_labels = labels

    return existedMachine.properties.kubernetes


def set_machine_os_profile(cmd, raw_parameters):
    MachineOSProfile = cmd.get_models(
        "MachineOSProfile",
        resource_type=CUSTOM_MGMT_AKS_PREVIEW,
        operation_group="machines"
    )
    os_type = raw_parameters.get("os_type")
    os_sku = raw_parameters.get("os_sku")
    enable_fips = False
    if raw_parameters.get("enable_fips_image"):
        enable_fips = True
    if raw_parameters.get("disable_fips_image"):
        enable_fips = False
    machineOSProfile = MachineOSProfile(
        os_type=os_type,
        os_sku=os_sku,
        enable_fips=enable_fips
    )
    return machineOSProfile


def set_machine_billing_profile(cmd, raw_parameters):
    spot_max_price = raw_parameters.get("spot_max_price")
    MachineBillingProfile = cmd.get_models(
        "MachineBillingProfile",
        resource_type=CUSTOM_MGMT_AKS_PREVIEW,
        operation_group="machines"
    )
    machineBillingProfile = MachineBillingProfile(
        spot_max_price=spot_max_price
    )
    return machineBillingProfile
