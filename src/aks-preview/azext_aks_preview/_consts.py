# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# consts for AgentPool
# priority
CONST_SCALE_SET_PRIORITY_REGULAR = "Regular"
CONST_SCALE_SET_PRIORITY_SPOT = "Spot"

# eviction policy
CONST_SPOT_EVICTION_POLICY_DELETE = "Delete"
CONST_SPOT_EVICTION_POLICY_DEALLOCATE = "Deallocate"

# Scale Down Mode
CONST_SCALE_DOWN_MODE_DELETE = "Delete"
CONST_SCALE_DOWN_MODE_DEALLOCATE = "Deallocate"

# os disk type
CONST_OS_DISK_TYPE_MANAGED = "Managed"
CONST_OS_DISK_TYPE_EPHEMERAL = "Ephemeral"

# mode
CONST_NODEPOOL_MODE_SYSTEM = "System"
CONST_NODEPOOL_MODE_USER = "User"

# os type
CONST_DEFAULT_NODE_OS_TYPE = "Linux"

# os sku
CONST_OS_SKU_UBUNTU = "Ubuntu"
CONST_OS_SKU_CBLMARINER = "CBLMariner"
CONST_OS_SKU_MARINER = "Mariner"
CONST_OS_SKU_WINDOWS2019 = "Windows2019"
CONST_OS_SKU_WINDOWS2022 = "Windows2022"
CONST_OS_SKU_AZURELINUX = "AzureLinux"

# vm set type
CONST_VIRTUAL_MACHINE_SCALE_SETS = "VirtualMachineScaleSets"
CONST_AVAILABILITY_SET = "AvailabilitySet"
CONST_VIRTUAL_MACHINES = "VirtualMachines"

# vm size
CONST_DEFAULT_NODE_VM_SIZE = "Standard_DS2_v2"
CONST_DEFAULT_AUTOMATIC_SKU_NODE_VM_SIZE = "Standard_DS4_v2"
CONST_DEFAULT_WINDOWS_NODE_VM_SIZE = "Standard_D2s_v3"

# workload runtime
CONST_WORKLOAD_RUNTIME_OCI_CONTAINER = "OCIContainer"
CONST_WORKLOAD_RUNTIME_WASM_WASI = "WasmWasi"
CONST_WORKLOAD_RUNTIME_KATA_MSHV_VM_ISOLATION = "KataMshvVmIsolation"
CONST_WORKLOAD_RUNTIME_KATA_CC_ISOLATION = "KataCcIsolation"

# gpu instance
CONST_GPU_INSTANCE_PROFILE_MIG1_G = "MIG1g"
CONST_GPU_INSTANCE_PROFILE_MIG2_G = "MIG2g"
CONST_GPU_INSTANCE_PROFILE_MIG3_G = "MIG3g"
CONST_GPU_INSTANCE_PROFILE_MIG4_G = "MIG4g"
CONST_GPU_INSTANCE_PROFILE_MIG7_G = "MIG7g"

# consts for ManagedCluster
# load balancer sku
CONST_LOAD_BALANCER_SKU_BASIC = "basic"
CONST_LOAD_BALANCER_SKU_STANDARD = "standard"

# ManagedClusterSKU Tier
CONST_MANAGED_CLUSTER_SKU_TIER_FREE = "free"
CONST_MANAGED_CLUSTER_SKU_TIER_STANDARD = "standard"
CONST_MANAGED_CLUSTER_SKU_TIER_PREMIUM = "premium"

# ManagedClusterSKU Name
CONST_MANAGED_CLUSTER_SKU_NAME_BASE = "base"
CONST_MANAGED_CLUSTER_SKU_NAME_AUTOMATIC = "automatic"

CONST_OUTBOUND_MIGRATION_MULTIZONE_TO_NATGATEWAY_MSG = (
    "Warning: this AKS cluster has multi-zonal nodepools, but NAT Gateway is not currently zone redundant. "
    "Migrating outbound connectivity to NAT Gateway could lead to a reduction in zone redundancy for this cluster. "
    "Continue?"
)
# load balancer backend pool type
CONST_LOAD_BALANCER_BACKEND_POOL_TYPE_NODE_IP = "nodeIP"
CONST_LOAD_BALANCER_BACKEND_POOL_TYPE_NODE_IPCONFIGURATION = "nodeIPConfiguration"

# private dns zone mode
CONST_PRIVATE_DNS_ZONE_SYSTEM = "system"
CONST_PRIVATE_DNS_ZONE_NONE = "none"

# used to set identity profile (for kubelet)
CONST_MANAGED_IDENTITY_OPERATOR_ROLE = "Managed Identity Operator"
CONST_MANAGED_IDENTITY_OPERATOR_ROLE_ID = "f1a07417-d97a-45cb-824c-7a7467783830"

# consts for upgrade channel
CONST_RAPID_UPGRADE_CHANNEL = "rapid"
CONST_STABLE_UPGRADE_CHANNEL = "stable"
CONST_PATCH_UPGRADE_CHANNEL = "patch"
CONST_NODE_IMAGE_UPGRADE_CHANNEL = "node-image"
CONST_NONE_UPGRADE_CHANNEL = "none"

# consts for node os upgrade channel
CONST_NODE_OS_CHANNEL_NODE_IMAGE = "NodeImage"
CONST_NODE_OS_CHANNEL_NONE = "None"
CONST_NODE_OS_CHANNEL_SECURITY_PATCH = "SecurityPatch"
CONST_NODE_OS_CHANNEL_UNMANAGED = "Unmanaged"

# consts for nrg-lockdown restriction level
CONST_NRG_LOCKDOWN_RESTRICTION_LEVEL_READONLY = "ReadOnly"
CONST_NRG_LOCKDOWN_RESTRICTION_LEVEL_UNRESTRICTED = "Unrestricted"

# network plugin
CONST_NETWORK_PLUGIN_KUBENET = "kubenet"
CONST_NETWORK_PLUGIN_AZURE = "azure"
CONST_NETWORK_PLUGIN_NONE = "none"

# network plugin mode
CONST_NETWORK_PLUGIN_MODE_OVERLAY = "overlay"

# network dataplane
CONST_NETWORK_DATAPLANE_AZURE = "azure"
CONST_NETWORK_DATAPLANE_CILIUM = "cilium"

# network policy
CONST_NETWORK_POLICY_AZURE = "azure"
CONST_NETWORK_POLICY_CALICO = "calico"
CONST_NETWORK_POLICY_CILIUM = "cilium"
CONST_NETWORK_POLICY_NONE = "none"

# network pod ip allocation mode
CONST_NETWORK_POD_IP_ALLOCATION_MODE_DYNAMIC_INDIVIDUAL = "DynamicIndividual"
CONST_NETWORK_POD_IP_ALLOCATION_MODE_STATIC_BLOCK = "StaticBlock"

# disk driver versions
CONST_DISK_DRIVER_V1 = "v1"
CONST_DISK_DRIVER_V2 = "v2"

# consts for addons
# http application routing
CONST_HTTP_APPLICATION_ROUTING_ADDON_NAME = "httpApplicationRouting"

# monitoring
CONST_MONITORING_ADDON_NAME = "omsagent"
CONST_MONITORING_LOG_ANALYTICS_WORKSPACE_RESOURCE_ID = "logAnalyticsWorkspaceResourceID"
CONST_MONITORING_USING_AAD_MSI_AUTH = "useAADAuth"

# virtual node
CONST_VIRTUAL_NODE_ADDON_NAME = "aciConnector"
CONST_VIRTUAL_NODE_SUBNET_NAME = "SubnetName"

# dashboard
CONST_KUBE_DASHBOARD_ADDON_NAME = "kubeDashboard"

# azure policy
CONST_AZURE_POLICY_ADDON_NAME = "azurepolicy"

# ingressApplicaitonGateway configuration keys
CONST_INGRESS_APPGW_ADDON_NAME = "ingressApplicationGateway"
CONST_INGRESS_APPGW_APPLICATION_GATEWAY_NAME = "applicationGatewayName"
CONST_INGRESS_APPGW_APPLICATION_GATEWAY_ID = "applicationGatewayId"
CONST_INGRESS_APPGW_SUBNET_ID = "subnetId"
CONST_INGRESS_APPGW_SUBNET_CIDR = "subnetCIDR"
CONST_INGRESS_APPGW_WATCH_NAMESPACE = "watchNamespace"

# confcom
CONST_CONFCOM_ADDON_NAME = "ACCSGXDevicePlugin"
CONST_ACC_SGX_QUOTE_HELPER_ENABLED = "ACCSGXQuoteHelperEnabled"

# open service mesh
CONST_OPEN_SERVICE_MESH_ADDON_NAME = "openServiceMesh"

# azure keyvault secrets provider
CONST_AZURE_KEYVAULT_SECRETS_PROVIDER_ADDON_NAME = "azureKeyvaultSecretsProvider"
CONST_SECRET_ROTATION_ENABLED = "enableSecretRotation"
CONST_ROTATION_POLL_INTERVAL = "rotationPollInterval"

# gitops
CONST_GITOPS_ADDON_NAME = "gitops"

# web application routing
# only used as the key of the corresponding description, not to map to the key name in addonProfiles,
# since its configuration is actually stored in a separate ingress profile
CONST_WEB_APPLICATION_ROUTING_KEY_NAME = "ingress/webApplicationRouting"

# all supported addons
ADDONS = {
    "http_application_routing": CONST_HTTP_APPLICATION_ROUTING_ADDON_NAME,
    "monitoring": CONST_MONITORING_ADDON_NAME,
    "virtual-node": CONST_VIRTUAL_NODE_ADDON_NAME,
    "kube-dashboard": CONST_KUBE_DASHBOARD_ADDON_NAME,
    "azure-policy": CONST_AZURE_POLICY_ADDON_NAME,
    "ingress-appgw": CONST_INGRESS_APPGW_ADDON_NAME,
    "confcom": CONST_CONFCOM_ADDON_NAME,
    "open-service-mesh": CONST_OPEN_SERVICE_MESH_ADDON_NAME,
    "azure-keyvault-secrets-provider": CONST_AZURE_KEYVAULT_SECRETS_PROVIDER_ADDON_NAME,
    "gitops": CONST_GITOPS_ADDON_NAME,
    "web_application_routing": CONST_WEB_APPLICATION_ROUTING_KEY_NAME,
}

ADDONS_DESCRIPTIONS = {
    CONST_HTTP_APPLICATION_ROUTING_ADDON_NAME: "- configure ingress with automatic public DNS name creation",
    CONST_MONITORING_ADDON_NAME: (
        "- turn on Log Analytics monitoring. Uses the Log Analytics Default Workspace if it exists, "
        'else creates one. Specify "--workspace-resource-id" to use an existing workspace.\n'
        "If monitoring addon is enabled --no-wait argument will have no effect."
    ),
    CONST_VIRTUAL_NODE_ADDON_NAME: (
        "- enable AKS Virtual Node. Requires --aci-subnet-name to provide the name of an existing subnet for "
        "the Virtual Node to use.\naci-subnet-name must be in the same vnet which is specified by "
        "--vnet-subnet-id (required as well)."
    ),
    CONST_KUBE_DASHBOARD_ADDON_NAME: "- n/a",
    CONST_AZURE_POLICY_ADDON_NAME: (
        "- enable Azure policy. The Azure Policy add-on for AKS enables at-scale enforcements and safeguards on "
        "your clusters in a centralized, consistent manner.\nLearn more at aka.ms/aks/policy."
    ),
    CONST_INGRESS_APPGW_ADDON_NAME: "- enable Application Gateway Ingress Controller addon (PREVIEW).",
    CONST_CONFCOM_ADDON_NAME: "- enable confcom addon, this will enable SGX device plugin by default (PREVIEW).",
    CONST_OPEN_SERVICE_MESH_ADDON_NAME: "- enable Open Service Mesh addon (PREVIEW).",
    CONST_AZURE_KEYVAULT_SECRETS_PROVIDER_ADDON_NAME: "- enable Azure Keyvault Secrets Provider addon.",
    CONST_GITOPS_ADDON_NAME: "- enable GitOps (PREVIEW).",
    CONST_WEB_APPLICATION_ROUTING_KEY_NAME: "- enable web application routing (PREVIEW).",
}

# consts for credential
# credential format
CONST_CREDENTIAL_FORMAT_AZURE = "azure"
CONST_CREDENTIAL_FORMAT_EXEC = "exec"

# refer https://docs.microsoft.com/en-us/rest/api/storageservices/
# naming-and-referencing-containers--blobs--and-metadata#container-names
CONST_CONTAINER_NAME_MAX_LENGTH = 63

CONST_PERISCOPE_REPO_ORG = "azure"
CONST_PERISCOPE_CONTAINER_REGISTRY = "mcr.microsoft.com"
CONST_PERISCOPE_RELEASE_TAG = "0.0.10"
CONST_PERISCOPE_IMAGE_VERSION = "0.0.10"
CONST_PERISCOPE_NAMESPACE = "aks-periscope"

CONST_AZURE_KEYVAULT_NETWORK_ACCESS_PUBLIC = "Public"
CONST_AZURE_KEYVAULT_NETWORK_ACCESS_PRIVATE = "Private"

# refer https://api.github.com/repos/Azure/draft/releases/latest
# tag_name gives latest version released.
# Moving away from 1:n release to avoid unwanted breaking changes with auto upgrades.
CONST_DRAFT_CLI_VERSION = "v0.0.22"

CONST_CUSTOM_CA_TEST_CERT = (
    "-----BEGIN CERTIFICATE-----\n"
    "MIICljCCAX4CCQC9zUAgqqqrWzANBgkqhkiG9w0BAQsFADANMQswCQYDVQQGEwJQ\n"
    "TDAeFw0yMjA5MTQwNjIzMjdaFw0yMjA5MTUwNjIzMjdaMA0xCzAJBgNVBAYTAlBM\n"
    "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAopKNIIbvvcPCw9fc4KLX\n"
    "KDtRZobp5L+/1hCN+3OGhk5NvSTpSUrFifxqc0o3IF7YkO3K1n2jAvCMXO16Bf9b\n"
    "OAR7VkCrwGFVkXNjM4wvXAX8CNNvjqd1zDPXSKdE7Wd8k3fTzx6nGUM0UgljIPhH\n"
    "yh4a4Zujd5Ig2P/ZSX0pGJm47JTtMu7MDFHVM5wRWcCrN/H0TCYPIvEOs0B8AZxc\n"
    "p3TF7A6veT5U9pVhQ3Xl9JN6LvvLqPxG3ea10rdv9DYzaiXmSY3ujI3Ri1Q11uWC\n"
    "dtrFIpFu5cHW2OBW+jBXxL0v8xQmkxTLik4BR/PLCl30wxKQNsq3pjDgu0mutKuu\n"
    "5wIDAQABMA0GCSqGSIb3DQEBCwUAA4IBAQAVEAIs/hLwTVCwpEXdoXR24LelNNuB\n"
    "/8ptK6lyjE11XwfMN3yy7F2oB1lrA4rI3j9obpDsHDJBNB13bi/lKgvAcbIn/Tyu\n"
    "RKThtUdPgxNnqDUyxnb3OofMF3gB8ePTu+jZpd3zrlEuxdl40ByATCSyOgR6DHMt\n"
    "SDd+joypnOHFAeSM+V0AaTelXSCK9OAWSAp5e6S76a6lRx+D5Xl3hBedBI0tX59h\n"
    "tEYNEGZaRElFU79WcEF0cH+ZW0+jJ95xE3thZffRz6QI6yF63m8aC9l9bbdJS2zg\n"
    "Yv8W+lCZi//ODeOBUugr++z9uj+vGk47JDSpV0n4JOun3ALUDJ0gqmcS\n"
    "-----END CERTIFICATE-----"
)

# consts for maintenance configuration schedule type
CONST_DAILY_MAINTENANCE_SCHEDULE = "Daily"
CONST_WEEKLY_MAINTENANCE_SCHEDULE = "Weekly"
CONST_ABSOLUTEMONTHLY_MAINTENANCE_SCHEDULE = "AbsoluteMonthly"
CONST_RELATIVEMONTHLY_MAINTENANCE_SCHEDULE = "RelativeMonthly"

CONST_WEEKINDEX_FIRST = "First"
CONST_WEEKINDEX_SECOND = "Second"
CONST_WEEKINDEX_THIRD = "Third"
CONST_WEEKINDEX_FOURTH = "Fourth"
CONST_WEEKINDEX_LAST = "Last"

CONST_DEFAULT_CONFIGURATION_NAME = "default"
CONST_AUTOUPGRADE_CONFIGURATION_NAME = "aksManagedAutoUpgradeSchedule"
CONST_NODEOSUPGRADE_CONFIGURATION_NAME = "aksManagedNodeOSUpgradeSchedule"

# Guardrails Level Consts
CONST_SAFEGUARDSLEVEL_OFF = "Off"
CONST_SAFEGUARDSLEVEL_WARNING = "Warning"
CONST_SAFEGUARDSLEVEL_ENFORCEMENT = "Enforcement"

CONST_AZURE_SERVICE_MESH_MODE_DISABLED = "Disabled"
CONST_AZURE_SERVICE_MESH_MODE_ISTIO = "Istio"
CONST_AZURE_SERVICE_MESH_INGRESS_MODE_EXTERNAL = "External"
CONST_AZURE_SERVICE_MESH_INGRESS_MODE_INTERNAL = "Internal"
CONST_AZURE_SERVICE_MESH_UPGRADE_COMMAND_START = "Start"
CONST_AZURE_SERVICE_MESH_UPGRADE_COMMAND_COMPLETE = "Complete"
CONST_AZURE_SERVICE_MESH_UPGRADE_COMMAND_ROLLBACK = "Rollback"

# Node Provisioning Mode Consts
CONST_NODE_PROVISIONING_MODE_MANUAL = "Manual"
CONST_NODE_PROVISIONING_MODE_AUTO = "Auto"

# Node Provisioning State Consts
CONST_NODE_PROVISIONING_STATE_SUCCEEDED = "Succeeded"

# Node Image Version Consts
CONST_MIN_NODE_IMAGE_VERSION = "202403.13.0"

# SSH Access Consts
CONST_SSH_ACCESS_DISABLED = "disabled"
CONST_SSH_ACCESS_LOCALUSER = "localuser"

# Dns zone contributor role
CONST_PRIVATE_DNS_ZONE_CONTRIBUTOR_ROLE = "Private DNS Zone Contributor"
CONST_DNS_ZONE_CONTRIBUTOR_ROLE = "DNS Zone Contributor"

# Cluster service health probe mode
CONST_CLUSTER_SERVICE_HEALTH_PROBE_MODE_SERVICE_NODE_PORT = "Servicenodeport"
CONST_CLUSTER_SERVICE_HEALTH_PROBE_MODE_SHARED = "Shared"

CONST_ARTIFACT_SOURCE_DIRECT = "Direct"
CONST_ARTIFACT_SOURCE_CACHE = "Cache"
