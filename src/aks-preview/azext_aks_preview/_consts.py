# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

CONST_OUTBOUND_TYPE_LOAD_BALANCER = "loadBalancer"
CONST_OUTBOUND_TYPE_USER_DEFINED_ROUTING = "userDefinedRouting"
CONST_OUTBOUND_TYPE_MANAGED_NAT_GATEWAY = "managedNATGateway"
CONST_OUTBOUND_TYPE_USER_ASSIGNED_NAT_GATEWAY = "userAssignedNATGateway"

CONST_SCALE_SET_PRIORITY_REGULAR = "Regular"
CONST_SCALE_SET_PRIORITY_SPOT = "Spot"

CONST_SPOT_EVICTION_POLICY_DELETE = "Delete"
CONST_SPOT_EVICTION_POLICY_DEALLOCATE = "Deallocate"

# consts for upgrade channel
CONST_RAPID_UPGRADE_CHANNEL = "rapid"
CONST_STABLE_UPGRADE_CHANNEL = "stable"
CONST_PATCH_UPGRADE_CHANNEL = "patch"
CONST_NODE_IMAGE_UPGRADE_CHANNEL = "node-image"
CONST_NONE_UPGRADE_CHANNEL = "none"

CONST_HTTP_APPLICATION_ROUTING_ADDON_NAME = "httpApplicationRouting"

CONST_MONITORING_ADDON_NAME = "omsagent"
CONST_MONITORING_LOG_ANALYTICS_WORKSPACE_RESOURCE_ID = "logAnalyticsWorkspaceResourceID"
CONST_MONITORING_USING_AAD_MSI_AUTH = "useAADAuth"

CONST_VIRTUAL_NODE_ADDON_NAME = "aciConnector"
CONST_VIRTUAL_NODE_SUBNET_NAME = "SubnetName"

CONST_AZURE_POLICY_ADDON_NAME = "azurepolicy"

CONST_KUBE_DASHBOARD_ADDON_NAME = "kubeDashboard"

CONST_OS_DISK_TYPE_MANAGED = "Managed"
CONST_OS_DISK_TYPE_EPHEMERAL = "Ephemeral"

# IngressApplicaitonGateway configuration keys
CONST_INGRESS_APPGW_ADDON_NAME = "ingressApplicationGateway"
CONST_INGRESS_APPGW_APPLICATION_GATEWAY_NAME = "applicationGatewayName"
CONST_INGRESS_APPGW_APPLICATION_GATEWAY_ID = "applicationGatewayId"
CONST_INGRESS_APPGW_SUBNET_ID = "subnetId"
CONST_INGRESS_APPGW_SUBNET_CIDR = "subnetCIDR"
CONST_INGRESS_APPGW_WATCH_NAMESPACE = "watchNamespace"

# Open Service Mesh configuration keys
CONST_OPEN_SERVICE_MESH_ADDON_NAME = "openServiceMesh"

# Gitops configuration keys
CONST_GITOPS_ADDON_NAME = "gitops"

CONST_NODEPOOL_MODE_SYSTEM = "System"
CONST_NODEPOOL_MODE_USER = "User"

# refer https://docs.microsoft.com/en-us/rest/api/storageservices/
# naming-and-referencing-containers--blobs--and-metadata#container-names
CONST_CONTAINER_NAME_MAX_LENGTH = 63

# confcom addon keys
CONST_CONFCOM_ADDON_NAME = "ACCSGXDevicePlugin"
CONST_ACC_SGX_QUOTE_HELPER_ENABLED = "ACCSGXQuoteHelperEnabled"

# private dns zone mode
CONST_PRIVATE_DNS_ZONE_SYSTEM = "system"
CONST_PRIVATE_DNS_ZONE_NONE = "none"

# Azure Keyvault Secrets Provider configuration keys
CONST_AZURE_KEYVAULT_SECRETS_PROVIDER_ADDON_NAME = "azureKeyvaultSecretsProvider"
CONST_SECRET_ROTATION_ENABLED = "enableSecretRotation"

# Scale Down Mode
CONST_SCALE_DOWN_MODE_DELETE = "Delete"
CONST_SCALE_DOWN_MODE_DEALLOCATE = "Deallocate"

ADDONS = {
    'http_application_routing': CONST_HTTP_APPLICATION_ROUTING_ADDON_NAME,
    'monitoring': CONST_MONITORING_ADDON_NAME,
    'virtual-node': CONST_VIRTUAL_NODE_ADDON_NAME,
    'azure-policy': CONST_AZURE_POLICY_ADDON_NAME,
    'kube-dashboard': CONST_KUBE_DASHBOARD_ADDON_NAME,
    'ingress-appgw': CONST_INGRESS_APPGW_ADDON_NAME,
    'open-service-mesh': CONST_OPEN_SERVICE_MESH_ADDON_NAME,
    "confcom": CONST_CONFCOM_ADDON_NAME,
    'gitops': CONST_GITOPS_ADDON_NAME,
    'azure-keyvault-secrets-provider': CONST_AZURE_KEYVAULT_SECRETS_PROVIDER_ADDON_NAME
}

ADDONS_DESCRIPTIONS = {
    CONST_HTTP_APPLICATION_ROUTING_ADDON_NAME: '- configure ingress with automatic public DNS name creation',
    CONST_MONITORING_ADDON_NAME: '- turn on Log Analytics monitoring. Uses the Log Analytics Default Workspace if it exists, else creates one. Specify "--workspace-resource-id" to use an existing workspace.\nIf monitoring addon is enabled --no-wait argument will have no effect.',
    CONST_VIRTUAL_NODE_ADDON_NAME: '- enable AKS Virtual Node. Requires --aci-subnet-name to provide the name of an existing subnet for the Virtual Node to use.\naci-subnet-name must be in the same vnet which is specified by --vnet-subnet-id (required as well).',
    CONST_AZURE_POLICY_ADDON_NAME: '- enable Azure policy. The Azure Policy add-on for AKS enables at-scale enforcements and safeguards on your clusters in a centralized, consistent manner.\nLearn more at aka.ms/aks/policy.',
    CONST_KUBE_DASHBOARD_ADDON_NAME: '- n/a',
    CONST_INGRESS_APPGW_ADDON_NAME: '- enable Application Gateway Ingress Controller addon (PREVIEW).',
    CONST_OPEN_SERVICE_MESH_ADDON_NAME: '- enable Open Service Mesh addon (PREVIEW).',
    CONST_CONFCOM_ADDON_NAME: '- enable confcom addon, this will enable SGX device plugin by default (PREVIEW).',
    CONST_GITOPS_ADDON_NAME: '- enable GitOps (PREVIEW).',
    CONST_AZURE_KEYVAULT_SECRETS_PROVIDER_ADDON_NAME: '- enable Azure Keyvault Secrets Provider addon (PREVIEW).'
}

CONST_WORKLOAD_RUNTIME_OCI_CONTAINER = "OCIContainer"
CONST_WORKLOAD_RUNTIME_WASM_WASI = "WasmWasi"

CONST_MANAGED_IDENTITY_OPERATOR_ROLE = 'Managed Identity Operator'
CONST_MANAGED_IDENTITY_OPERATOR_ROLE_ID = 'f1a07417-d97a-45cb-824c-7a7467783830'

CONST_GPU_INSTANCE_PROFILE_MIG1_G = "MIG1g"
CONST_GPU_INSTANCE_PROFILE_MIG2_G = "MIG2g"
CONST_GPU_INSTANCE_PROFILE_MIG3_G = "MIG3g"
CONST_GPU_INSTANCE_PROFILE_MIG4_G = "MIG4g"
CONST_GPU_INSTANCE_PROFILE_MIG7_G = "MIG7g"
