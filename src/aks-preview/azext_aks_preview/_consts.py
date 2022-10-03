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

# vm set type
CONST_VIRTUAL_MACHINE_SCALE_SETS = "VirtualMachineScaleSets"
CONST_AVAILABILITY_SET = "AvailabilitySet"

# vm size
CONST_DEFAULT_NODE_VM_SIZE = "Standard_DS2_v2"
CONST_DEFAULT_WINDOWS_NODE_VM_SIZE = "Standard_D2s_v3"

# workload runtime
CONST_WORKLOAD_RUNTIME_OCI_CONTAINER = "OCIContainer"
CONST_WORKLOAD_RUNTIME_WASM_WASI = "WasmWasi"

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

# outbound type
CONST_OUTBOUND_TYPE_LOAD_BALANCER = "loadBalancer"
CONST_OUTBOUND_TYPE_USER_DEFINED_ROUTING = "userDefinedRouting"
CONST_OUTBOUND_TYPE_MANAGED_NAT_GATEWAY = "managedNATGateway"
CONST_OUTBOUND_TYPE_USER_ASSIGNED_NAT_GATEWAY = "userAssignedNATGateway"

# load balancer backend pool type
CONST_LOAD_BALANCER_BACKEND_POOL_TYPE_NODE_IP = "nodeIP"
CONST_LOAD_BALANCER_BACKEND_POOL_TYPE_NODE_IPCONFIGURATION = "nodeIPConfiguration"

# private dns zone mode
CONST_PRIVATE_DNS_ZONE_SYSTEM = "system"
CONST_PRIVATE_DNS_ZONE_NONE = "none"

# used to set identity profile (for kubelet)
CONST_MANAGED_IDENTITY_OPERATOR_ROLE = 'Managed Identity Operator'
CONST_MANAGED_IDENTITY_OPERATOR_ROLE_ID = 'f1a07417-d97a-45cb-824c-7a7467783830'

# consts for upgrade channel
CONST_RAPID_UPGRADE_CHANNEL = "rapid"
CONST_STABLE_UPGRADE_CHANNEL = "stable"
CONST_PATCH_UPGRADE_CHANNEL = "patch"
CONST_NODE_IMAGE_UPGRADE_CHANNEL = "node-image"
CONST_NONE_UPGRADE_CHANNEL = "none"

# network plugin
CONST_NETWORK_PLUGIN_KUBENET = "kubenet"
CONST_NETWORK_PLUGIN_AZURE = "azure"
CONST_NETWORK_PLUGIN_NONE = "none"

# network plugin mode
CONST_NETWORK_PLUGIN_MODE_OVERLAY = "overlay"

# networkprofile eBPF dataplane
CONST_EBPF_DATAPLANE_CILIUM = "cilium"

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
    'http_application_routing': CONST_HTTP_APPLICATION_ROUTING_ADDON_NAME,
    'monitoring': CONST_MONITORING_ADDON_NAME,
    'virtual-node': CONST_VIRTUAL_NODE_ADDON_NAME,
    'kube-dashboard': CONST_KUBE_DASHBOARD_ADDON_NAME,
    'azure-policy': CONST_AZURE_POLICY_ADDON_NAME,
    'ingress-appgw': CONST_INGRESS_APPGW_ADDON_NAME,
    "confcom": CONST_CONFCOM_ADDON_NAME,
    'open-service-mesh': CONST_OPEN_SERVICE_MESH_ADDON_NAME,
    'azure-keyvault-secrets-provider': CONST_AZURE_KEYVAULT_SECRETS_PROVIDER_ADDON_NAME,
    'gitops': CONST_GITOPS_ADDON_NAME,
    'web_application_routing': CONST_WEB_APPLICATION_ROUTING_KEY_NAME
}

ADDONS_DESCRIPTIONS = {
    CONST_HTTP_APPLICATION_ROUTING_ADDON_NAME: '- configure ingress with automatic public DNS name creation',
    CONST_MONITORING_ADDON_NAME: '- turn on Log Analytics monitoring. Uses the Log Analytics Default Workspace if it exists, else creates one. Specify "--workspace-resource-id" to use an existing workspace.\nIf monitoring addon is enabled --no-wait argument will have no effect.',
    CONST_VIRTUAL_NODE_ADDON_NAME: '- enable AKS Virtual Node. Requires --aci-subnet-name to provide the name of an existing subnet for the Virtual Node to use.\naci-subnet-name must be in the same vnet which is specified by --vnet-subnet-id (required as well).',
    CONST_KUBE_DASHBOARD_ADDON_NAME: '- n/a',
    CONST_AZURE_POLICY_ADDON_NAME: '- enable Azure policy. The Azure Policy add-on for AKS enables at-scale enforcements and safeguards on your clusters in a centralized, consistent manner.\nLearn more at aka.ms/aks/policy.',
    CONST_INGRESS_APPGW_ADDON_NAME: '- enable Application Gateway Ingress Controller addon (PREVIEW).',
    CONST_CONFCOM_ADDON_NAME: '- enable confcom addon, this will enable SGX device plugin by default (PREVIEW).',
    CONST_OPEN_SERVICE_MESH_ADDON_NAME: '- enable Open Service Mesh addon (PREVIEW).',
    CONST_AZURE_KEYVAULT_SECRETS_PROVIDER_ADDON_NAME: '- enable Azure Keyvault Secrets Provider addon (PREVIEW).',
    CONST_GITOPS_ADDON_NAME: '- enable GitOps (PREVIEW).',
    CONST_WEB_APPLICATION_ROUTING_KEY_NAME: '- enable web application routing (PREVIEW).'
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
