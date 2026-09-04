# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

from collections import OrderedDict


RESOURCE_PROVIDER_NAMESPACE = "Microsoft.AzureArcData"
"""
Resource provider namespace
"""

API_VERSION = "2023-01-15-preview"
"""
Microsoft.AzureArcData API version
NOTE: This needs to be updated if the API version changes
"""

PG_API_VERSION = API_VERSION
"""
Postgres Resource provider API version
"""

RESOURCE_URI = (
    "/subscriptions/{}/resourcegroups/{}/providers/Microsoft.AzureArcData/{}/{}"
)
"""
Azure Resource URI
"""

RESOURCE_TYPE_POSTGRES = "Microsoft.AzureArcData/postgresInstances"
"""
Postgres resource type
"""

RESOURCE_TYPE_SQL = "Microsoft.AzureArcData/sqlManagedInstances"
"""
SQL instance resource type
"""

RESOURCE_TYPE_DATA_CONTROLLER = "Microsoft.AzureArcData/dataControllers"
"""
Data controller Azure resource type
"""

INSTANCE_TYPE_POSTGRES = "postgresInstances"
"""
Postgres instance type
"""

INSTANCE_TYPE_SQL = "sqlManagedInstances"
"""
SQL instance type
"""

INSTANCE_TYPE_DATA_CONTROLLER = "dataControllers"
"""
Arc data controller type
"""

INSTANCE_TYPE_AD_CONNECTOR = "activeDirectoryConnectors"
"""
Active Directory connector type
"""

INSTANCE_TYPE_FAILOVER_GROUP = "failoverGroups"
"""
Arc-enabled failover group type
"""

RESOURCE_KIND_DATA_CONTROLLER = "dataController"
"""
Resource kind for Arc data controller
"""

RESOURCE_KIND_POSTGRES = "PostgreSql"
"""
Resource kind for Postgres
"""

RESOURCE_KIND_SQL = "SqlManagedInstance"
"""
SQL instance resource kind
"""

METRICS_SQL_NAMESPACE = "SQL Server"
"""
SQL instance metrics namespace in Azure monitoring
"""

METRICS_POSTGRES_NAMESPACE = "Postgres"
"""
Postgres instance metrics namespace in Azure monitoring
"""

DEFAULT_NAMESPACE = "default"
"""
The default namespace in k8s
"""

DIRECT_CONNECTIVITY_MODE = "direct"
"""
The direct connectivity mode
"""

INDIRECT_CONNECTIVITY_MODE = "indirect"
"""
The indirect connectivity mode
"""

RESOURCE_TYPE_FOR_KIND = {
    RESOURCE_KIND_DATA_CONTROLLER: INSTANCE_TYPE_DATA_CONTROLLER,
    RESOURCE_KIND_SQL: INSTANCE_TYPE_SQL,
    RESOURCE_KIND_POSTGRES: INSTANCE_TYPE_POSTGRES,
}
"""
Instance type to resource type lookup
"""

RESOURCE_TYPES_OF_DATA_SERVICES = {
    INSTANCE_TYPE_SQL: RESOURCE_TYPE_SQL,
    INSTANCE_TYPE_POSTGRES: RESOURCE_TYPE_POSTGRES,
}
"""
Instance type of data service
"""

PATCH_PAYLOAD_LIMIT = 1024 * 1000
"""
Azure patch payload limit
"""

BILLING_MODEL_COMSUMPTION = "consumption"
"""
Consumption based billing model
"""

BILLING_MODEL_CAPCITY = "capacity"
"""
Capacity based billing model
"""

CLUSTER_CONNECTION_MODE_CONNECTED = "connected"
"""
Connected cluster
"""

CLUSTER_CONNECTION_MODE_DISCONNECTED = "disconnected"
"""
Disconnected cluster
"""

DEFAULT_DATA_CONTROLLER_NAME = "DataController"
"""
Default data controller name
"""

AZURE_ARM_URL = "https://management.azure.com"
"""
Azure ARM URL
"""

AZURE_ARM_API_VERSION_STR = "?api-version="
"""
Azure ARM API version string in header
"""

AAD_LOGIN_URL = "https://login.microsoftonline.com/"
"""
AAD login URL
"""

AZURE_ARM_SCOPE = ["https://management.azure.com/.default"]
"""
Azure ARM SCOPE
"""

AAD_PROFILE_FILENAME = "aad-profile.json"
"""
AAD token cache file name
"""

AZURE_AF_SCOPE = ["https://azurearcdata.billing.publiccloudapi.net/.default"]
"""
Azure ARM SCOPE
"""

SPN_ENV_KEYS = {
    "authority": "SPN_AUTHORITY",
    "tenant_id": "SPN_TENANT_ID",
    "client_id": "SPN_CLIENT_ID",
    "client_secret": "SPN_CLIENT_SECRET",
}
"""
Environment variables' name of SPN for metric upload
"""

METRICS_CONFIG_FILENAME = "metrics-config.json"
"""
Metric config file name
"""

AZURE_METRICS_SCOPE = ["https://monitoring.azure.com//.default"]
"""
Azure Custom Metrics url
"""

PUBLIC_CLOUD_LOGIN_URL = "https://login.microsoftonline.com"
"""
Azure public cloud AAD login url
"""

API_LOG = "/api/logs"
"""
Log upload api resource value
"""

MONITORING_METRICS_PUBLISHER_ROLE_ID = "3913510d-42f4-4e42-8a64-420c390055eb"
ROLE_DESCRIPTIONS = {
    MONITORING_METRICS_PUBLISHER_ROLE_ID: "Monitoring Metrics Publisher"
}

ARC_DATA_SERVICES_EXTENSION_API_VERSION = "2021-09-01"

RESOURCE_HYDRATION_API_VERSION = "2021-08-31-preview"

ROLE_ASSIGNMENTS_API_VERSION = "2022-04-01"

CUSTOM_LOCATION_API_VERSION = "2021-08-15"

CONNECTED_CLUSTER_API_VERSION = "2021-10-01"

ARC_DATASERVICES_EXTENSION_RELEASE_TRAIN = "stable"

ARC_DATASERVICES_EXTENSION_VERSION = "1.33.0"
"""
The latest Arc data services extension helm chart version
NOTE: This needs to be updated before every release
"""


##############################################################
# The following is a mapping of the Arc data services release
# image tag to the corresponding extension helm chart version.
# NOTE: This needs to be updated before every release
###############################################################
IMAGE_TAG_EXT_VERSION_MAP = OrderedDict(
    [
        ("v1.42.0_2025-10-14", "1.42.0"),
        ("v1.41.0_2025-09-09", "1.41.0"),
        ("v1.40.0_2025-08-12", "1.40.0"),
        ("v1.39.0_2025-05-13", "1.39.0"),
        ("v1.38.0_2025-04-08", "1.38.0"),
        ("v1.37.0_2025-03-11", "1.37.0"),
        ("v1.36.0_2025-02-11", "1.36.0"),
        ("v1.35.0_2024-11-12", "1.35.0"),
        ("v1.34.0_2024-10-08", "1.34.0"),
        ("v1.33.0_2024-09-10", "1.33.0"),
        ("v1.32.0_2024-08-13", "1.32.0"),
        ("v1.31.0_2024-07-09", "1.31.0"),
        ("v1.30.0_2024-06-11", "1.30.0"),
        ("v1.29.0_2024-04-09", "1.29.0"),
        ("v1.28.0_2024-03-12", "1.28.0"),
        ("v1.27.0_2024-02-13", "1.27.0"),
        ("v1.26.0_2023-12-12", "1.26.0"),
        ("v1.25.0_2023-11-14", "1.25.0"),
        ("v1.24.0_2023-10-10", "1.24.0"),
        ("v1.23.0_2023-09-12", "1.23.0"),
        ("v1.22.0_2023-08-08", "1.22.0"),
        ("v1.21.0_2023-07-11", "1.21.0"),
        ("v1.20.0_2023-06-13", "1.20.0"),
        ("v1.19.0_2023-05-09", "1.19.0"),
        ("v1.18.0_2023-04-11", "1.18.0"),
        ("v1.17.0_2023-03-14", "1.17.0"),
        ("v1.16.0_2023-02-14", "1.16.0"),
        ("v1.15.0_2023-01-10", "1.15.0"),
        ("v1.14.0_2022-12-13", "1.14.0"),
        ("v1.13.0_2022-11-08", "1.13.0"),
        ("v1.12.0_2022-10-11", "1.12.0"),
        ("v1.11.0_2022-09-13", "1.11.0"),
        ("v1.10.0_2022-08-09", "1.2.20381002"),
        ("v1.9.0_2022-07-12", "1.2.20031002"),
        ("v1.8.0_2022-06-14", "1.2.19831003"),
        ("v1.7.0_2022-05-24", "1.2.19581002"),
        ("v1.6.0_2022-05-02", "1.2.19481002"),
        ("v1.5.0_2022-04-05", "1.1.19211001"),
        ("v1.4.1_2022-03-08", "1.1.18911000"),
        ("v1.4.0_2022-02-25", "1.1.18791000"),
        ("v1.3.0_2022-01-27", "1.1.18501004"),
        ("v1.2.0_2021-12-15", "1.1.18031001"),
        ("v1.1.0_2021-11-02", "1.1.17561007"),
    ]
)

##############################################################
# The following is a mapping of the Arc data services extension
# version to the latest ARM API version it supports.
# This is used to determine the ARM API version to use when
# deploying a new resource.
# NOTE: This needs to be updated before every release
###############################################################
EXT_VERSION_ARM_API_VERSION_MAP = OrderedDict(
    [
        ("1.42.0", "2023-01-15-preview"),
        ("1.41.0", "2023-01-15-preview"),
        ("1.40.0", "2023-01-15-preview"),
        ("1.39.0", "2023-01-15-preview"),
        ("1.38.0", "2023-01-15-preview"),
        ("1.37.0", "2023-01-15-preview"),
        ("1.36.0", "2023-01-15-preview"),
        ("1.35.0", "2023-01-15-preview"),
        ("1.34.0", "2023-01-15-preview"),
        ("1.33.0", "2023-01-15-preview"),
        ("1.32.0", "2023-01-15-preview"),
        ("1.31.0", "2023-01-15-preview"),
        ("1.30.0", "2023-01-15-preview"),
        ("1.29.0", "2023-01-15-preview"),
        ("1.28.0", "2023-01-15-preview"),
        ("1.27.0", "2023-01-15-preview"),
        ("1.26.0", "2023-01-15-preview"),
        ("1.25.0", "2023-01-15-preview"),
        ("1.24.0", "2023-01-15-preview"),
        ("1.23.0", "2023-01-15-preview"),
        ("1.22.0", "2023-01-15-preview"),
        ("1.21.0", "2023-01-15-preview"),
        ("1.20.0", "2023-01-15-preview"),
        ("1.19.0", "2023-01-15-preview"),
        ("1.18.0", "2023-01-15-preview"),
        ("1.17.0", "2022-03-01-preview"),
        ("1.16.0", "2022-03-01-preview"),
        ("1.15.0", "2022-03-01-preview"),
        ("1.14.0", "2022-03-01-preview"),
        ("1.13.0", "2022-03-01-preview"),
        ("1.12.0", "2022-03-01-preview"),
        ("1.11.0", "2022-03-01-preview"),
        ("1.2.20381002", "2022-03-01-preview"),
        ("1.2.20031002", "2022-03-01-preview"),
        ("1.2.19831003", "2022-03-01-preview"),
        ("1.2.19581002", "2022-03-01-preview"),
        ("1.2.19481002", "2022-03-01-preview"),
        ("1.1.19211001", "2021-11-01"),
        ("1.1.18911000", "2021-11-01"),
        ("1.1.18791000", "2021-11-01"),
        ("1.1.18501004", "2021-11-01"),
        ("1.1.18031001", "2021-11-01"),
        ("1.1.17561007", "2021-11-01"),
    ]
)

##############################################################
# The following is a mapping of each Arc data services resource
# type to the earliest extension version that can be used to
# deploy it.
# NOTE: This needs to be updated only if we add a new resource type
###############################################################
RESOURCE_TYPE_EXT_VERSION_MAP = {
    INSTANCE_TYPE_DATA_CONTROLLER: "1.1.17561007",
    INSTANCE_TYPE_POSTGRES: "1.1.17561007",
    INSTANCE_TYPE_SQL: "1.1.17561007",
    INSTANCE_TYPE_AD_CONNECTOR: "1.2.19481002",
    INSTANCE_TYPE_FAILOVER_GROUP: "1.18.0",
}
