# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

CONST_OUTBOUND_TYPE_LOAD_BALANCER = "loadBalancer"
CONST_OUTBOUND_TYPE_USER_DEFINED_ROUTING = "userDefinedRouting"

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

# Azure Defender addon configuration keys
CONST_AZURE_DEFENDER_ADDON_NAME = "azureDefender"
CONST_AZURE_DEFENDER_LOG_ANALYTICS_WORKSPACE_RESOURCE_ID = CONST_MONITORING_LOG_ANALYTICS_WORKSPACE_RESOURCE_ID

ADDONS = {
    'azure-defender': CONST_AZURE_DEFENDER_ADDON_NAME,
    'http_application_routing': CONST_HTTP_APPLICATION_ROUTING_ADDON_NAME,
    'monitoring': CONST_MONITORING_ADDON_NAME,
    'virtual-node': CONST_VIRTUAL_NODE_ADDON_NAME,
    'azure-policy': CONST_AZURE_POLICY_ADDON_NAME,
    'kube-dashboard': CONST_KUBE_DASHBOARD_ADDON_NAME,
    'ingress-appgw': CONST_INGRESS_APPGW_ADDON_NAME,
    'open-service-mesh': CONST_OPEN_SERVICE_MESH_ADDON_NAME,
    "confcom": CONST_CONFCOM_ADDON_NAME,
    'gitops': 'gitops',
    'azure-keyvault-secrets-provider': CONST_AZURE_KEYVAULT_SECRETS_PROVIDER_ADDON_NAME
}

CONST_MANAGED_IDENTITY_OPERATOR_ROLE = 'Managed Identity Operator'
CONST_MANAGED_IDENTITY_OPERATOR_ROLE_ID = 'f1a07417-d97a-45cb-824c-7a7467783830'
