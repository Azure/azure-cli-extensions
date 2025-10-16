# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

import os

from azext_arcdata.ad_connector.constants import AD_CONNECTOR_SPEC
from azext_arcdata.core.constants import (
    ARC_API_V1,
    ARC_API_V1BETA1,
    ARC_API_V2,
    ARC_API_V3,
    ARC_API_V4,
    ARC_API_V5,
)
from azext_arcdata.postgres.constants import (
    POSTGRES_SPEC,
    POSTGRESQL_RESTORE_TASK_SPEC,
)
from azext_arcdata.sqlmi.constants import (
    SQLMI_REPROVISION_REPLICA_TASK_SPEC,
    SQLMI_RESTORE_TASK_SPEC,
    SQLMI_SPEC,
)
from azext_arcdata.failover_group.constants import (
    FOG_SPEC,
)

################################################################################
# Data Controller
################################################################################

CONNECTION_MODE = "connectionMode"
DISPLAY_NAME = "displayName"
LOCATION = "location"
RESOURCE_GROUP = "resourceGroup"
SUBSCRIPTION = "subscription"

ARC_NAME = "arc"
"""
Command group constant
"""

DATA_CONTROLLER_CUSTOM_RESOURCE = "datacontroller"
"""
Name of control plane custom resource
"""

CONTROLLER_LOGIN_SECRET_NAME = "controller-login-secret"
"""
Secret that hold the controller login credentials
"""

LOGSUI_LOGIN_SECRET_NAME = "logsui-admin-secret"
"""
Secret that hold the logsui login credentials
"""

METRICSUI_LOGIN_SECRET_NAME = "metricsui-admin-secret"
"""
Secret that hold the metricsui admin credentials
"""

EXPORT_TASK_CUSTOM_RESOURCE = "export"
"""
Name of export task custom resource
"""

CONTROLLER_LABEL = "controller"
"""
Name of the controller app label
"""

CONTROLLER_SVC = "controller-external-svc"
"""
Name of external controller service
"""

MGMT_PROXY = "mgmtproxy-svc-external"
"""
Name of management proxy service
"""

MONITOR_PLURAL = "monitors"
"""
Plural name for Monitor custom resource.
"""

MONITOR_CRD_VERSION = ARC_API_V2
"""
Defines the kubernetes api version for Monitor CRD.
"""

MONITOR_RESOURCE = "monitorstack"
"""
Monitor resource.
"""

OTEL_COLLECTOR_PLURAL = "telemetrycollectors"
"""
Plural name for TelemetryCollector custom resource.
"""

TELEMETRY_COLLECTOR_CRD_VERSION = ARC_API_V1BETA1
"""
Defines the kubernetes api version for otel collector CRD.
"""

OTEL_COLLECTOR_RESOURCE = "telemetrycollector"
"""
Otel collector resource.
"""

BASE = os.path.dirname(os.path.realpath(__file__))
"""
Base directory
"""

CONFIG_DIR = os.path.join(BASE, "deployment-configs")
"""
Config directory
"""

TEMPLATE_DIR = os.path.join(BASE, "templates")
"""
Custom resource definition directory
"""

DATA_CONTROLLER_CRD_NAME = "datacontrollers.arcdata.microsoft.com"
"""
Well known name of the datacontroller crd
"""

MONITOR_CRD_NAME = "monitors.arcdata.microsoft.com"
"""
Well known name of the monitor crd
"""

TELEMETRY_COLLECTOR_CRD = os.path.join(
    TEMPLATE_DIR, "telemetry_collector_crd.yaml"
)
"""
File location for otel collector CRD.
"""

TELEMETRY_COLLECTOR_CRD_NAME = "telemetrycollectors.arcdata.microsoft.com"
"""
Well known name of the otel collector crd
"""

KAFKA_CRD = os.path.join(TEMPLATE_DIR, "kafka_crd.yaml")
"""
File location for Kafka CRD.
"""

KAFKA_CRD_NAME = "kafkas.arcdata.microsoft.com"
"""
Well known name of the Kafka crd
"""

ACTIVE_DIRECTORY_CONNECTOR_CRD_NAME = (
    "activedirectoryconnectors.arcdata.microsoft.com"
)
"""
Well known name of the active directory connector crd
"""

POSTGRES_CRD_NAME = "postgresqls.arcdata.microsoft.com"
"""
Well known name of the postgres crd
"""

POSTGRESQL_RESTORE_TASK_CRD_NAME = (
    "postgresqlrestoretasks.tasks.postgresql.arcdata.microsoft.com"
)
"""
Well known name of the postgres restore task crd
"""

SQLMI_CRD_NAME = "sqlmanagedinstances.sql.arcdata.microsoft.com"
"""
Well known name of the sqlmi-arc crd
"""

SQLMI_RESTORE_TASK_CRD_NAME = (
    "sqlmanagedinstancerestoretasks.tasks.sql.arcdata.microsoft.com"
)
"""
Well known name of the sqlmi-restore-task CRD
"""

SQLMI_REPROVISION_REPLICA_TASK_CRD_NAME = (
    "sqlmanagedinstancereprovisionreplicatasks.tasks.sql.arcdata.microsoft.com"
)
"""
Well known name of the sqlmi-reprovision-replica-task CRD
"""

FOG_CRD_NAME = "failovergroups.sql.arcdata.microsoft.com"
"""
Well known name of the Failover Group CRD
"""

EXPORT_TASK_CRD_NAME = "exporttasks.tasks.arcdata.microsoft.com"
"""
Well known name of the export task crd
"""

DATA_CONTROLLER_SPEC = os.path.join(TEMPLATE_DIR, "data_controller_spec.json")
"""
File location for data controller SPEC.
"""

MONITOR_SPEC = os.path.join(TEMPLATE_DIR, "monitor_spec.json")
"""
File location for monitor SPEC.
"""

EXPORT_TASK_SPEC = os.path.join(TEMPLATE_DIR, "export_task_spec.json")
"""
File location for export task SPEC.
"""


EXPORT_TASK_CRD_VERSION = ARC_API_V2
"""
Defines the kubernetes api version for Export task CRD.
"""


HELP_DIR = os.path.join(CONFIG_DIR, "help")
"""
Help config directory
"""

CONTROL_CONFIG_FILENAME = "control.json"
"""
Control config file name
"""

CONFIG_FILES = [CONTROL_CONFIG_FILENAME]
"""
Array of config file names from profiles
"""

LAST_BILLING_USAGE_FILE = "usage-{}.json"
"""
Name of last usage file exported before deleting data controller
"""

LAST_USAGE_UPLOAD_FLAG = "end_usage"
"""
Key of flag in usage file indicating last usage upload
"""

EXPORT_TASK_RESOURCE_KIND = "ExportTask"
"""
Defines the export resource kind name.
"""

EXPORT_TASK_RESOURCE_KIND_PLURAL = "exporttasks"
"""
Defines the export resource kind plural name.
"""

TASK_API_GROUP = "tasks.arcdata.microsoft.com"
"""
Defines the API group.
"""

MAX_POLLING_ATTEMPTS = 12
"""
Max retry attepts to get custom resource status
"""

EXPORT_COMPLETED_STATE = "Completed"
"""
Export completed state
"""

DEFAULT_METRIC_QUERY_WINDOW_IN_MINUTE = 28
"""
Default metric query window in minute
"""

DEFAULT_LOG_QUERY_WINDOW_IN_MINUTE = 14 * 24 * 60
"""
Default log query window in minute
"""

DEFAULT_USAGE_QUERY_WINDOW_IN_MINUTE = 62 * 24 * 60
"""
Default usage query window in minute
"""

DEFAULT_QUERY_WINDOW = {
    "metrics": DEFAULT_METRIC_QUERY_WINDOW_IN_MINUTE,
    "logs": DEFAULT_LOG_QUERY_WINDOW_IN_MINUTE,
    "usage": DEFAULT_USAGE_QUERY_WINDOW_IN_MINUTE,
}

"""
Default query window for three types of data
"""

############################################################################
# Data Controller constants
############################################################################

GUID_REGEX = r"[0-9a-f]{8}\-([0-9a-f]{4}\-){3}[0-9a-f]{12}"
"""
Used to validate subscription IDs
"""

DIRECT = "direct"
"""
Direct connection mode
"""

INDIRECT = "indirect"
"""
Indirect connection mode
"""

CONNECTIVITY_TYPES = [DIRECT, INDIRECT]
"""
Supported connectivity types for data controller
"""

SUPPORTED_REGIONS = [
    "eastus",
    "eastus2",
    "centralus",
    "westeurope",
    "southeastasia",
    "westus2",
    "japaneast",
    "australiaeast",
    "koreacentral",
    "northeurope",
    "uksouth",
    "francecentral",
    "westus3",
    "southcentralus",
    "northcentralus",
    "canadacentral",
    "westcentralus",
    "centralindia",
    "switzerlandnorth",
    "canadaeast",
    "brazilsouth",
    "southafricanorth",
    "uaenorth",
    "norwayeast",
    "ukwest",
    "swedencentral",
    "germanywestcentral",
    "italynorth",
    "japanwest",
]
"""
Supported Azure regions for data controller. This list does not include EUAP
regions.
"""

SUPPORTED_EUAP_REGIONS = ["eastus2euap", "centraluseuap", "eastasia"]
"""
Supported Azure EUAP regions for data controller.
"""

INFRASTRUCTURE_AWS = "aws"
INFRASTRUCTURE_GCP = "gcp"
INFRASTRUCTURE_AZURE = "azure"
INFRASTRUCTURE_ALIBABA = "alibaba"
INFRASTRUCTURE_ONPREMISES = "onpremises"
INFRASTRUCTURE_OTHER = "other"
INFRASTRUCTURE_AUTO = "auto"
INFRASTRUCTURE_PARAMETER_DEFAULT_VALUE = INFRASTRUCTURE_AUTO
# these are the allowed parameter values in the cli
INFRASTRUCTURE_PARAMETER_ALLOWED_VALUES = [
    INFRASTRUCTURE_AWS,
    INFRASTRUCTURE_GCP,
    INFRASTRUCTURE_AZURE,
    INFRASTRUCTURE_ALIBABA,
    INFRASTRUCTURE_ONPREMISES,
    INFRASTRUCTURE_OTHER,
    INFRASTRUCTURE_AUTO,
]
# these are the allowed values in the CR (different from allowed parameters, as the parameters accept "auto" which is not a valid value in the CR)
INFRASTRUCTURE_CR_ALLOWED_VALUES = [
    INFRASTRUCTURE_AWS,
    INFRASTRUCTURE_GCP,
    INFRASTRUCTURE_AZURE,
    INFRASTRUCTURE_ALIBABA,
    INFRASTRUCTURE_ONPREMISES,
    INFRASTRUCTURE_OTHER,
]

INFRASTRUCTURE_PARAMETER_INVALID_VALUE_MSG = (
    "Please input a valid infrastructure. Supported values are:"
    " " + ", ".join(INFRASTRUCTURE_PARAMETER_ALLOWED_VALUES) + "."
)

INFRASTRUCTURE_CR_INVALID_VALUE_MSG = (
    "Please input a valid infrastructure. Supported values are:"
    " " + ", ".join(INFRASTRUCTURE_CR_ALLOWED_VALUES) + "."
)

CRD_SUPPORTED_IMAGE_VERSIONS = {
    ARC_API_V1: ["v1.0.0"],
    ARC_API_V2: ["v1.1.0", "v1.2.0", "v1.3.0"],
    ARC_API_V3: ["v1.4.0", "v1.4.1"],
    ARC_API_V4: ["v1.5.0"],
    ARC_API_V5: [
        "v1.6.0",
        "v1.7.0",
        "v1.8.0",
        "v1.9.0",
        "v1.10.0",
        "v1.11.0",
        "v1.12.0",
        "v1.13.0",
        "v1.14.0",
        "v1.15.0",
        "v1.16.0",
        "v1.17.0",
        "v1.18.0",
        "v1.19.0",
        "v1.20.0",
        "v1.21.0",
        "v1.22.0",
        "v1.23.0",
        "v1.24.0",
        "v1.25.0",
        "v1.26.0",
        "v1.27.0",
        "v1.28.0",
        "v1.29.0",
        "v1.30.0",
        "v1.31.0",
        "v1.32.0",
        "v1.33.0",
        "v1.34.0",
        "v1.35.0",
        "v1.36.0",
        "v1.37.0",
        "v1.38.0",
        "v1.39.0",
        "v1.40.0",
        "v1.41.0",
        "v1.42.0",
    ],
}

MINIMUM_IMAGE_VERSION_SUPPORTED = "v1.9.0_2022-07-12"
"""
Minimum image supported (as required by bootstrapper helm chart)
TODO: update when the release is determined.
"""

RESOURCE_KIND_DATA_CONTROLLER = "dataController"
"""
Resource kind for Arc data controller
"""

BOOTSTRAP_TEMPLATE_DIR = os.path.join(TEMPLATE_DIR, "bootstrap")
"""
Bootstrap template directory
"""


class BOOTSTRAP_TEMPLATES:
    CLUSTER_ROLE = os.path.join(
        BOOTSTRAP_TEMPLATE_DIR, "cluster-role.yaml.tmpl"
    )
    """
    Template for cluster role for bootstrap job for deployment and upgrade.
    """

    CLUSTER_ROLE_BINDING = os.path.join(
        BOOTSTRAP_TEMPLATE_DIR, "cluster-role-binding.yaml.tmpl"
    )
    """
    Template for cluster role binding for bootstrap job for deployment and upgrade.
    """

    BOOTSTRAPPER_ROLE = os.path.join(
        BOOTSTRAP_TEMPLATE_DIR, "role-bootstrapper.yaml.tmpl"
    )
    """
    Template for bootstrapper role, for granting during deployment and upgrade.
    """

    DEPLOYER_ROLE = os.path.join(
        BOOTSTRAP_TEMPLATE_DIR, "deployer-role.yaml.tmpl"
    )
    """
    Template for deployer role for bootstrap job for deployment and upgrade.
    """

    ROLE_BINDING = os.path.join(
        BOOTSTRAP_TEMPLATE_DIR, "role-binding.yaml.tmpl"
    )
    """
    Template for role binding for bootstrap job for deployment and upgrade.
    """

    SERVICE_ACCOUNT = os.path.join(
        BOOTSTRAP_TEMPLATE_DIR, "service-account.yaml.tmpl"
    )
    """
    Template for service account for bootstrap job for deployment and upgrade.
    """

    JOB = os.path.join(BOOTSTRAP_TEMPLATE_DIR, "job.yaml.tmpl")
    """
    Template for bootstrap job for deployment and upgrade.
    """

    CLUSTER_ROLE_NAME_FORMAT = "{0}:cr-deployer"
    """
    the name format to use for the cluster_role name. The parameter {0} should be the namespace.
    """

    CLUSTER_ROLE_BINDING_NAME_FORMAT = "{0}:crb-deployer"
    """
    the name format to use for the cluster_role_binding name. The parameter {0} should be the namespace.
    """

    SERVICE_ACCOUNT_NAME = "sa-arc-deployer"
    """
    the name of the arc deployer service account.
    """

    JOB_NAME = "arc-bootstrapper-job"
    """
    the name of the bootstrapper job name.
    """

    BOOTSTRAPPER_IMAGE_NAME = "arc-bootstrapper"
    """
    the name of the bootstrapper image.
    """

    def get_cluster_role_name(namespace):
        """
        Returns the cluster role name for a given namespace
        """
        return BOOTSTRAP_TEMPLATES.CLUSTER_ROLE_NAME_FORMAT.format(namespace)

    def get_cluster_role_binding_name(namespace):
        """
        Returns the cluster role binding name for a given namespace.
        """
        return BOOTSTRAP_TEMPLATES.CLUSTER_ROLE_BINDING_NAME_FORMAT.format(
            namespace
        )
