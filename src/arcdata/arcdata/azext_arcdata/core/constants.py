# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

import os
from enum import Enum

BASE = os.path.dirname(os.path.realpath(__file__))
"""
Base directory
"""

IO_DELIM = "(?<!\\\\),(?=[\w/.$]+)"
"""
Defines the IO delimiter for json key/value pairs on config set.
"""

KEY_VALUE_SPLIT = "(?<!\\\\)(?<!=)=(?!=)"
"""
Defines the key/value delimiter.
"""

IS_WINDOWS = os.name == "nt"
"""
Boolean for whether the CLI is in the Windows env.
"""

PASSWORD_MIN_LENGTH = 8
"""
Minimum length for a password in arc
"""

PASSWORD_REQUIRED_GROUPS = 3
"""
Number of character groups required for a password in arc
"""

AZDATA_USERNAME = "AZDATA_USERNAME"
"""
Defines the username env variable for login.
"""

AZDATA_PASSWORD = "AZDATA_PASSWORD"
"""
Defines the password env variable for login.
"""

LOGSUI_USERNAME = "AZDATA_LOGSUI_USERNAME"
"""
Defines username env variable for Logsui login.
"""

LOGSUI_PASSWORD = "AZDATA_LOGSUI_PASSWORD"
"""
Defines password env variable for Logsui login.
"""

METRICSUI_USERNAME = "AZDATA_METRICSUI_USERNAME"
"""
Defines username env variable for Metricsui login.
"""

METRICSUI_PASSWORD = "AZDATA_METRICSUI_PASSWORD"
"""
Defines password env variable for Metricsui login.
"""

DEFAULT_LOGSUI_CERT_SECRET_NAME = "logsui-certificate-secret"
"""
Default secret name that holds the logsui certificate
"""

DEFAULT_METRICSUI_CERT_SECRET_NAME = "metricsui-certificate-secret"
"""
Default secret name that holds the metricsui certificate
"""

DOMAIN_SERVICE_ACCOUNT_USERNAME = "DOMAIN_SERVICE_ACCOUNT_USERNAME"
"""
Defines the username env variable for domain service account.
"""

DOMAIN_SERVICE_ACCOUNT_PASSWORD = "DOMAIN_SERVICE_ACCOUNT_PASSWORD"
"""
Defines the password env variable for domain service account.
"""

DOCKER_USERNAME = "DOCKER_USERNAME"
"""
Defines the username env variable for docker private registries.
"""

DOCKER_PASSWORD = "DOCKER_PASSWORD"
"""
Defines the password env variable for docker private registries.
"""

REGISTRY_USERNAME = "REGISTRY_USERNAME"
"""
Alternative definition for the username env variable for docker private registries.
"""

REGISTRY_PASSWORD = "REGISTRY_PASSWORD"
"""
Alternative definition for the password env variable for docker private registries.
"""

PUBLIC_DOCKER_REGISTRY = "mcr.microsoft.com"
"""
The default public image registry.
"""

DEFAULT_REGISTRY = PUBLIC_DOCKER_REGISTRY
"""
The default docker image registry.
"""

DEFAULT_REPOSITORY = "arcdata"
"""
The default docker image repository
"""

DEFAULT_IMAGE_TAG = "v1.42.0_2025-10-14"
"""
The default docker image tag.
NOTE: This needs to be updated before every release
"""

DEFAULT_IMAGE_POLICY = "Always"
"""
The default docker image pull policy
"""

CERT_ARGUMENT_ERROR_TEMPLATE = """Kubernetes secret '{}'
                        already exists while private key or public key 
                        files are provided on the command line. If you intend 
                        to use the secret, please remove the file parameters 
                        and try again. If you intend to use the files 
                        provided to the command, use a different secret name 
                        or delete the existing secret."""

# ------------------------------------------------------------------------------
# Arc constants for convenience of not rereading data controller CRD file for
# multiple API calls across command modules
# ------------------------------------------------------------------------------
ARC_GROUP = "arcdata.microsoft.com"
"""
Defines the group for Arc CRDs.
"""

ARC_NAMESPACE_LABEL = "{}/namespace".format(ARC_GROUP)
"""
Arc managed namespaces have a {arcdata.microsoft.com/namespace: <namespace>} label.

Example: 'arcdata.microsoft.com/namespace: test'
"""

ARC_WEBHOOK_PREFIX = "{}-webhook".format(ARC_GROUP)
"""
Prefix for the arc webhook name. Example: 'arcdata.microsoft.com-webhook-test'
"""

ARC_API_V1BETA1 = "v1beta1"
"""
Defines the kubernetes api version v1beta1 for Arc CRDs.
"""

ARC_API_V1BETA2 = "v1beta2"
"""
Defines the kubernetes api version v1beta2 for Arc CRDs.
"""

ARC_API_V1BETA3 = "v1beta3"
"""
Defines the kubernetes api version v1beta3 for Arc CRDs.
"""

ARC_API_V1BETA4 = "v1beta4"
"""
Defines the kubernetes api version v1beta4 for Arc CRDs.
"""

ARC_API_V1BETA5 = "v1beta5"
"""
Defines the kubernetes api version v1beta5 for Arc CRDs.
"""

ARC_API_V1BETA6 = "v1beta6"
"""
Defines the kubernetes api version v1beta6 for Arc CRDs.
"""

ARC_API_V1 = "v1"
"""
Defines the kubernetes api version v1 for Arc CRDs.
"""

ARC_API_V2 = "v2"
"""
Defines the kubernetes api version v2 for Arc CRDs.
"""

ARC_API_V3 = "v3"
"""
Defines the kubernetes api version v3 for Arc CRDs.
"""

ARC_API_V4 = "v4"
"""
Defines the kubernetes api version v4 for Arc CRDs.
"""

ARC_API_V5 = "v5"
"""
Defines the kubernetes api version v5 for Arc CRDs.
"""

ARC_API_V6 = "v6"
"""
Defines the kubernetes api version v6 for Arc CRDs.
"""

ARC_API_V7 = "v7"
"""
Defines the kubernetes api version v7 for Arc CRDs.
"""

ARC_API_V8 = "v8"
"""
Defines the kubernetes api version v8 for Arc CRDs.
"""

KUBERNETES_LABEL_PREFIX = "app.kubernetes.io/"
"""
Defines the prefix for common Kubernetes labels
https://kubernetes.io/docs/concepts/overview/working-with-objects/common-labels/
"""

ARC_INSTANCE_LABEL = KUBERNETES_LABEL_PREFIX + "instance"
"""
Defines the instance label for Arc resources
"""

ARC_RESOURCE_KIND_LABEL = KUBERNETES_LABEL_PREFIX + "part-of"
"""
Defines the resource kind label for Arc resources
"""

DATA_CONTROLLER_PLURAL = "datacontrollers"
"""
Defines the plural name of data controllers.
"""

DATA_CONTROLLER_CRD_VERSION = ARC_API_V5
"""
Defines the kubernetes api version for DataController CRD.
"""

MGMT_PROXY = "mgmtproxy-svc-external"
"""
Name of management proxy service.
"""

DNS_NAME_REQUIREMENTS = (
    "resource name must contain only alphanumeric characters or '-', be lowercase, "
    "start with an alphabetic character, and end with an alphanumeric character."
)
"""
Requirements for a DNS name
"""

MIN_PORT_NUMBER = 0
"""
Minimum number for a port
"""

MAX_PORT_NUBMER = 65535
"""
Max number for a port
"""

PORT_REQUIREMENTS = (
    "Port number must be a positive integer between {} and {}".format(
        MIN_PORT_NUMBER, MAX_PORT_NUBMER
    )
)
"""
Requirements for a port number
"""

USE_K8S_TEXT = "Use local Kubernetes APIs to perform this action."
"""
Help text for --use-k8s parameter
"""

USE_K8S_EXCEPTION_TEXT = "Please include the --use-k8s argument."
"""
Text to use when --use-k8s parameter is missing
"""

CONNECTION_MODE = "connectionMode"
DISPLAY_NAME = "displayName"
LOCATION = "location"
RESOURCE_GROUP = "resourceGroup"
SUBSCRIPTION = "subscription"

# ------------------------------------------------------------------------------
# Helpful constants and Enums for dealing with kubernetes resource quantities
# ------------------------------------------------------------------------------

# SI Suffixes
ONE_k = 10**3
ONE_M = 10**6
ONE_G = 10**9
ONE_T = 10**12
ONE_P = 10**15
ONE_E = 10**18

# Base two equivalents
ONE_Ki = 2**10
ONE_Mi = 2**20
ONE_Gi = 2**30
ONE_Ti = 2**40
ONE_Pi = 2**50
ONE_Ei = 2**60

# Millicores
MILLICORES_PER_CORE = 10**3

# A table for converting SI suffixes or their base two equivalents
# into their sizes in bytes
UNIT_TABLE = {
    "k": ONE_k,
    "Ki": ONE_Ki,
    "M": ONE_M,
    "Mi": ONE_Mi,
    "G": ONE_G,
    "Gi": ONE_Gi,
    "T": ONE_T,
    "Ti": ONE_Ti,
    "P": ONE_P,
    "Pi": ONE_Pi,
    "E": ONE_E,
    "Ei": ONE_Ei,
}

# Helper regexps for numbers
# NOTE: cannot format these as regex since python automatically adds anchors
# to them
INTEGER = r"[0-9]+"
STRICT_POS_INTEGER = r"[0-9]*[1-9]+[0-9]*"
FLOAT = r"[0-9]*\.[0-9]+"
STRICT_POS_FLOAT = r"({}\.[0-9]*)|([0-9]*\.{})".format(
    STRICT_POS_INTEGER, STRICT_POS_INTEGER
)
NUMBER = r"{}|{}".format(INTEGER, FLOAT)
STRICT_POS_NUMBER = r"({})|({})".format(STRICT_POS_FLOAT, STRICT_POS_INTEGER)

# Maximum decimals for kubernetes resource quantity
KUBE_QUANTITY_PRECISION = 3


class ResourceType(Enum):
    """
    Represents the supported resource request/limit types.
    """

    MEMORY = "memory"
    CPU = "cpu"

    def __eq__(self, other):
        return self.value == other.value


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

CLI_ARG_GROUP_INDIRECT_TEXT = "Kubernetes API – targeted"
"""
Argument text for indirect mode argument group.
"""

CLI_ARG_GROUP_DIRECT_TEXT = "Azure Resource Manager – targeted"
"""
Argument text for direct mode argument group.
"""

CLI_ARG_GROUP_AD_TEXT = "Active Directory"
"""
Argument text for Active Directory argument group.
"""

CLI_ARG_GROUP_USE_K8S = "Maintenance window"
"""
Argument text for arguments that may only be used with the --use-k8s parameter
"""

CLI_ARG_RESOURCE_GROUP_TEXT = "The Azure resource group in which the data controller resource should be added."

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
    "germanywestcentral",
    "italynorth",
    "japanwest",
]
"""
Supported Azure regions for data controller. This list does not include EUAP regions.
"""

SUPPORTED_EUAP_REGIONS = ["eastus2euap", "centraluseuap", "eastasia"]
"""
Supported Azure EUAP regions for data controller.
"""
