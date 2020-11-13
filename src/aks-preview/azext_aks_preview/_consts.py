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
CONST_INGRESS_APPGW_ADDON_NAME = "IngressApplicationGateway"
CONST_INGRESS_APPGW_APPLICATION_GATEWAY_NAME = "applicationGatewayName"
CONST_INGRESS_APPGW_APPLICATION_GATEWAY_ID = "applicationGatewayId"
CONST_INGRESS_APPGW_SUBNET_ID = "subnetId"
CONST_INGRESS_APPGW_SUBNET_PREFIX = "subnetPrefix"
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

ADDONS = {
    'http_application_routing': CONST_HTTP_APPLICATION_ROUTING_ADDON_NAME,
    'monitoring': CONST_MONITORING_ADDON_NAME,
    'virtual-node': CONST_VIRTUAL_NODE_ADDON_NAME,
    'azure-policy': CONST_AZURE_POLICY_ADDON_NAME,
    'kube-dashboard': CONST_KUBE_DASHBOARD_ADDON_NAME,
    'ingress-appgw': CONST_INGRESS_APPGW_ADDON_NAME,
    'open-service-mesh': CONST_OPEN_SERVICE_MESH_ADDON_NAME,
    "confcom": CONST_CONFCOM_ADDON_NAME,
    'gitops': 'gitops'
}
