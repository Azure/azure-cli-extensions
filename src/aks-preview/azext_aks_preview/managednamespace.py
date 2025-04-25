# pylint: disable=too-many-lines
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.azclierror import (
    InvalidArgumentValueError,
    RequiredArgumentMissingError,
)

from azext_aks_preview._consts import (
    CONST_NAMESPACE_NETWORK_POLICY_RULE_DENYALL,
    CONST_NAMESPACE_NETWORK_POLICY_RULE_ALLOWALL,
    CONST_NAMESPACE_NETWORK_POLICY_RULE_ALLOWSAMENAMESPACE,
    CONST_NAMESPACE_ADOPTION_POLICY_NEVER,
    CONST_NAMESPACE_ADOPTION_POLICY_IFIDENTICAL,
    CONST_NAMESPACE_ADOPTION_POLICY_ALWAYS,
    CONST_NAMESPACE_DELETE_POLICY_KEEP,
    CONST_NAMESPACE_DELETE_POLICY_DELETE
)

from azext_aks_preview._client_factory import CUSTOM_MGMT_AKS_PREVIEW

def aks_managed_namespace_add(cmd, client, raw_parameters, headers):
    resource_group_name = raw_parameters.get("resource_group_name")
    cluster_name = raw_parameters.get("cluster_name")
    namespace_name = raw_parameters.get("name")
    namespace_config = constructNamespace(cmd, raw_parameters)

    return client.begin_create_or_update(
        resource_group_name=resource_group_name,
        resource_name=cluster_name,
        namespace_name=namespace_name,
        parameters=namespace_config,
        headers=headers
    )

def constructNamespace(cmd, raw_parameters):
    namespace_name = raw_parameters.get("name")
    tags = raw_parameters.get("tags", {})
    labels_raw = raw_parameters.get("labels")
    labels = parse_key_value_list(labels_raw)
    annotations_raw = raw_parameters.get("annotations")
    annotations = parse_key_value_list(annotations_raw)

    NamespaceProperties = cmd.get_models(
        "NamespaceProperties",
        resource_type = CUSTOM_MGMT_AKS_PREVIEW,
        operation_group = "namespaces"
    )
    
    namespace_properties = NamespaceProperties(
        labels = labels,
        annotations = annotations,
        default_resource_quota = setResourceQuota(cmd, raw_parameters),
        default_network_policy = setNetworkPolicyRule(cmd, raw_parameters),
        adoption_policy = setAdoptionPolicy(cmd, raw_parameters),
        delete_policy = setDeletePolicy(cmd, raw_parameters)
    )

    Namespace = cmd.get_models(
        "Namespace",
        resource_type = CUSTOM_MGMT_AKS_PREVIEW,
        operation_group = "namespaces"
    )
    
    namespace_config = Namespace()
    print(namespace_config)
    namespace_config.name = namespace_name
    namespace_config.tags = tags
    namespace_config.properties = namespace_properties
    return namespace_config

def setResourceQuota(cmd, raw_parameters):
    cpu_request = raw_parameters.get("cpu_request")
    cpu_limit = raw_parameters.get("cpu_limit")
    memory_request = raw_parameters.get("memory_request")
    memory_limit = raw_parameters.get("memory_limit")

    if any(param is None for param in [cpu_request, cpu_limit, memory_request, memory_limit]):
        raise RequiredArgumentMissingError(
            "Please specify --cpu-request, --cpu-limit, --memory-request, and --memory-limit."
    )
    
    ResourceQuota = cmd.get_models(
        "ResourceQuota",
        resource_type = CUSTOM_MGMT_AKS_PREVIEW,
        operation_group = "namespaces"
    )

    rq = ResourceQuota(
        cpu_request = cpu_request,
        cpu_limit = cpu_limit,
        memory_request = memory_request,
        memory_limit = memory_limit
    )
    
    return rq

def setNetworkPolicyRule(cmd, raw_parameters):
    ingress_rule = raw_parameters.get("ingress_rule", CONST_NAMESPACE_NETWORK_POLICY_RULE_ALLOWSAMENAMESPACE)
    egress_rule = raw_parameters.get("egress_rule", CONST_NAMESPACE_NETWORK_POLICY_RULE_ALLOWALL)

    valid_network_policy_rules = {
        CONST_NAMESPACE_NETWORK_POLICY_RULE_DENYALL,
        CONST_NAMESPACE_NETWORK_POLICY_RULE_ALLOWSAMENAMESPACE,
        CONST_NAMESPACE_NETWORK_POLICY_RULE_ALLOWALL
    }

    if ingress_rule not in valid_network_policy_rules:
        raise InvalidArgumentValueError(
            f"Invalid ingress_rule '{ingress_rule}'. Must be one of: "
            f"{', '.join(valid_network_policy_rules)}"
        )
    
    if egress_rule not in valid_network_policy_rules:
        raise InvalidArgumentValueError(
            f"Invalid egress_rule '{egress_rule}'. Must be one of: "
            f"{', '.join(valid_network_policy_rules)}"
        )

    NetworkPolicies = cmd.get_models(
        "NetworkPolicies",
        resource_type=CUSTOM_MGMT_AKS_PREVIEW,
        operation_group="namespaces"
    )

    np = NetworkPolicies(
        ingress = ingress_rule,
        egress = egress_rule
    )
    
    return np

def setAdoptionPolicy(cmd, raw_parameters):
    adoption_policy = raw_parameters.get("adoption_policy", CONST_NAMESPACE_ADOPTION_POLICY_NEVER)
    
    valid_adoption_policy = {
        CONST_NAMESPACE_ADOPTION_POLICY_NEVER,
        CONST_NAMESPACE_ADOPTION_POLICY_IFIDENTICAL,
        CONST_NAMESPACE_ADOPTION_POLICY_ALWAYS
    }

    if adoption_policy not in valid_adoption_policy:
        raise InvalidArgumentValueError(
            f"Invalid adoption policy '{adoption_policy}'. Must be one of: "
            f"{', '.join(valid_adoption_policy)}"
        )
    
    return adoption_policy

def setDeletePolicy(cmd, raw_parameters):
    delete_policy = raw_parameters.get("delete_policy", CONST_NAMESPACE_DELETE_POLICY_KEEP)
    
    valid_delete_policy = {
        CONST_NAMESPACE_DELETE_POLICY_KEEP,
        CONST_NAMESPACE_DELETE_POLICY_DELETE
    }

    if delete_policy not in valid_delete_policy:
        raise InvalidArgumentValueError(
            f"Invalid delete policy '{delete_policy}'. Must be one of: "
            f"{', '.join(valid_delete_policy)}"
        )
    
    return delete_policy

def parse_key_value_list(pairs):
    result = {}
    if pairs is None:
        return result
    for pair in pairs:
        if "=" not in pair:
            raise ValueError(f"Invalid format '{pair}'. Expected format key=value.")
        key, value = pair.split("=", 1)
        result[key.strip()] = value.strip()
    return result
