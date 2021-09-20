AZURE_PUBLIC_CLOUD_ENDPOINTS = {
    "activeDirectory": "https://login.microsoftonline.com/",
    "activeDirectoryDataLakeResourceId": "https://datalake.azure.net/",
    "activeDirectoryGraphResourceId": "https://graph.windows.net/",
    "activeDirectoryResourceId": "https://management.core.windows.net/",
    "appInsightsResourceId": "https://api.applicationinsights.io",
    "appInsightsTelemetryChannelResourceId": "https://dc.applicationinsights.azure.com/v2/track",
    "batchResourceId": "https://batch.core.windows.net/",
    "gallery": "https://gallery.azure.com/",
    "logAnalyticsResourceId": "https://api.loganalytics.io",
    "management": "https://management.core.windows.net/",
    "mediaResourceId": "https://rest.media.azure.net",
    "microsoftGraphResourceId": "https://graph.microsoft.com/",
    "ossrdbmsResourceId": "https://ossrdbms-aad.database.windows.net",
    "resourceManager": "https://management.azure.com/",
    "sqlManagement": "https://management.core.windows.net:8443/",
    "vmImageAliasDoc": "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/master/arm-compute/quickstart-templates/aliases.json"
}

AZURE_DOGFOOD_ENDPOINTS = {
    "activeDirectory": "https://login.windows-ppe.net/",
    "activeDirectoryDataLakeResourceId": None,
    "activeDirectoryGraphResourceId": "https://graph.ppe.windows.net/",
    "activeDirectoryResourceId": "https://management.core.windows.net/",
    "appInsightsResourceId": None,
    "appInsightsTelemetryChannelResourceId": None,
    "batchResourceId": None,
    "gallery": "https://df.gallery.azure-test.net/",
    "logAnalyticsResourceId": None,
    "management": "https://management-preview.core.windows-int.net/",
    "mediaResourceId": None,
    "microsoftGraphResourceId": None,
    "ossrdbmsResourceId": None,
    "resourceManager": "https://api-dogfood.resources.windows-int.net/",
    "sqlManagement": None,
    "vmImageAliasDoc": None
}

AZURE_FAIRFAX_ENDPOINTS = {
    "activeDirectory": "https://login.microsoftonline.us/",
    "activeDirectoryDataLakeResourceId": None,
    "activeDirectoryGraphResourceId": "https://graph.windows.net/",
    "activeDirectoryResourceId": "https://management.core.usgovcloudapi.net/",
    "appInsightsResourceId": "https://api.applicationinsights.us",
    "appInsightsTelemetryChannelResourceId": "https://dc.applicationinsights.us/v2/track",
    "attestationResourceId": None,
    "batchResourceId": "https://batch.core.usgovcloudapi.net/",
    "gallery": "https://gallery.usgovcloudapi.net/",
    "logAnalyticsResourceId": "https://api.loganalytics.us",
    "management": "https://management.core.usgovcloudapi.net/",
    "mediaResourceId": "https://rest.media.usgovcloudapi.net",
    "microsoftGraphResourceId": "https://graph.microsoft.us/",
    "ossrdbmsResourceId": "https://ossrdbms-aad.database.usgovcloudapi.net",
    "portal": "https://portal.azure.us",
    "resourceManager": "https://management.usgovcloudapi.net/",
    "sqlManagement": "https://management.core.usgovcloudapi.net:8443/",
    "synapseAnalyticsResourceId": "https://dev.azuresynapse.usgovcloudapi.net",
    "vmImageAliasDoc": "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/master/arm-compute/quickstart-templates/aliases.json"
}

AZURE_CLOUD_DICT = {"AZURE_PUBLIC_CLOUD" : AZURE_PUBLIC_CLOUD_ENDPOINTS, "AZURE_DOGFOOD": AZURE_DOGFOOD_ENDPOINTS, "AZURE_FAIRFAX": AZURE_FAIRFAX_ENDPOINTS}

DEFAULT_RELEASE_TRAIN = 'stable'
HELM_CHART_PATH = 'azure-arc-k8sagents'
HELM_RELEASE_NAME = 'azure-arc'
HELM_RELEASE_NAMESPACE = 'default'
KUBERNETES_DISTRIBUTION = 'generic'
KUBERNETES_INFRASTRUCTURE = 'generic'
ARC_HELM_CHART_PARAMS_DICT = {}
TIMEOUT = 500

AZURE_ARC_NAMESPACE = 'azure-arc'

CLUSTER_METADATA_CRD_GROUP = 'arc.azure.com'
CLUSTER_METADATA_CRD_VERSION = 'v1beta1'
CLUSTER_METADATA_CRD_PLURAL = 'connectedclusters'
CLUSTER_METADATA_CRD_NAME = 'clustermetadata'
CLUSTER_METADATA_DICT = {'kubernetes_version': 0, 'total_node_count': 0, 'total_core_count': 0, 'agent_version': 0, 'last_connectivity_time': 0, 'managed_identity_certificate_expiration_time': 0}

CLUSTER_TYPE = 'connectedClusters'

AZURE_IDENTITY_CERTIFICATE_SECRET = 'azure-identity-certificate'
AZURE_IDENTITY_CERTIFICATE_EXPIRATION_TIME = 'azure-identity-certificate-expiration-time'
AZURE_IDENTITY_TOKEN_SECRET = 'config-agent-identity-request-token'
ARC_CONFIG_NAME = 'azure-clusterconfig'
CLUSTER_IDENTITY_CRD_GROUP = 'clusterconfig.azure.com'
CLUSTER_IDENTITY_CRD_VERSION = 'v1beta1'
CLUSTER_IDENTITY_CRD_PLURAL = 'azureclusteridentityrequests'
CLUSTER_IDENTITY_CRD_NAME = 'config-agent-identity-request'
IDENTITY_TOKEN_REFERENCE_DICTIONARY = {'dataName': 'cluster-identity-token', 'secretName': 'config-agent-identity-request-token'}
