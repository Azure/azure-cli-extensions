##
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
##

from enum import Enum
# from azure.identity._constants import EnvironmentVariables as SdkEnvironmentVariables
# from azure.identity import _internal as AzureIdentityInternals
from ..azure_identity._constants import EnvironmentVariables as SdkEnvironmentVariables
from ..azure_identity import _internal as AzureIdentityInternals


class EnvironmentVariables:
    USER_AGENT_APPID = "AZURE_QUANTUM_PYTHON_APPID"
    QUANTUM_LOCATION = "AZURE_QUANTUM_WORKSPACE_LOCATION"
    LOCATION = "LOCATION"
    QUANTUM_RESOURCE_GROUP = "AZURE_QUANTUM_WORKSPACE_RG"
    RESOURCE_GROUP = "RESOURCE_GROUP"
    QUANTUM_SUBSCRIPTION_ID = "AZURE_QUANTUM_SUBSCRIPTION_ID"
    SUBSCRIPTION_ID = "SUBSCRIPTION_ID"
    WORKSPACE_NAME = "AZURE_QUANTUM_WORKSPACE_NAME"
    QUANTUM_ENV = "AZURE_QUANTUM_ENV"
    AZURE_CLIENT_ID = SdkEnvironmentVariables.AZURE_CLIENT_ID
    AZURE_CLIENT_SECRET = SdkEnvironmentVariables.AZURE_CLIENT_SECRET
    AZURE_CLIENT_CERTIFICATE_PATH = SdkEnvironmentVariables.AZURE_CLIENT_CERTIFICATE_PATH
    AZURE_CLIENT_SEND_CERTIFICATE_CHAIN = SdkEnvironmentVariables.AZURE_CLIENT_SEND_CERTIFICATE_CHAIN
    AZURE_TENANT_ID = SdkEnvironmentVariables.AZURE_TENANT_ID
    QUANTUM_TOKEN_FILE = "AZURE_QUANTUM_TOKEN_FILE"
    CONNECTION_STRING = "AZURE_QUANTUM_CONNECTION_STRING"
    ALL = [
        USER_AGENT_APPID,
        QUANTUM_LOCATION,
        LOCATION,
        QUANTUM_RESOURCE_GROUP,
        RESOURCE_GROUP,
        QUANTUM_SUBSCRIPTION_ID,
        SUBSCRIPTION_ID,
        WORKSPACE_NAME,
        QUANTUM_ENV,
        AZURE_CLIENT_ID,
        AZURE_CLIENT_SECRET,
        AZURE_CLIENT_CERTIFICATE_PATH,
        AZURE_CLIENT_SEND_CERTIFICATE_CHAIN,
        AZURE_TENANT_ID,
        QUANTUM_TOKEN_FILE,
        CONNECTION_STRING,
    ]


class EnvironmentKind(Enum):
    PRODUCTION = 1,
    CANARY = 2,
    DOGFOOD = 3


class WorkspaceKind(Enum):
    V1 = "V1"
    V2 = "V2"


class ConnectionConstants:
    DATA_PLANE_CREDENTIAL_SCOPE = "https://quantum.microsoft.com/.default"
    ARM_CREDENTIAL_SCOPE = "https://management.azure.com/.default"

    DEFAULT_ARG_API_VERSION = "2021-03-01"
    DEFAULT_WORKSPACE_API_VERSION = "2025-11-01-preview"

    MSA_TENANT_ID = "9188040d-6c67-4c5b-b112-36a304b66dad"

    AUTHORITY = AzureIdentityInternals.get_default_authority()
    DOGFOOD_AUTHORITY = "login.windows-ppe.net"

    # pylint: disable=unnecessary-lambda-assignment
    GET_QUANTUM_PRODUCTION_ENDPOINT = \
        lambda location: f"https://{location}.quantum.azure.com/"
    GET_QUANTUM_PRODUCTION_ENDPOINT_v2 = \
        lambda location: f"https://{location}-v2.quantum.azure.com/"
    GET_QUANTUM_CANARY_ENDPOINT = \
        lambda location: f"https://{location or 'eastus2euap'}.quantum.azure.com/"
    GET_QUANTUM_DOGFOOD_ENDPOINT = \
        lambda location: f"https://{location}.quantum-test.azure.com/"
    GET_QUANTUM_DOGFOOD_ENDPOINT_v2 = \
        lambda location: f"https://{location}-v2.quantum-test.azure.com/"

    ARM_PRODUCTION_ENDPOINT = "https://management.azure.com/"
    ARM_DOGFOOD_ENDPOINT = "https://api-dogfood.resources.windows-int.net/"

    VALID_RESOURCE_ID = (
        lambda subscription_id, resource_group, workspace_name:
        f"/subscriptions/{subscription_id}" +
        f"/resourceGroups/{resource_group}" +
        "/providers/Microsoft.Quantum/" +
        f"Workspaces/{workspace_name}"
    )

    VALID_CONNECTION_STRING = (
        lambda subscription_id, resource_group, workspace_name, api_key, quantum_endpoint:
        f"SubscriptionId={subscription_id};" +
        f"ResourceGroupName={resource_group};" +
        f"WorkspaceName={workspace_name};" +
        f"ApiKey={api_key};" +
        f"QuantumEndpoint={quantum_endpoint};"
    )

    QUANTUM_API_KEY_HEADER = "x-ms-quantum-api-key"

GUID_REGEX_PATTERN = (
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
)

VALID_WORKSPACE_NAME_PATTERN = r"^[a-zA-Z0-9]+(-*[a-zA-Z0-9])*$"

VALID_AZURE_REGIONS = {
    "australiacentral",
    "australiacentral2",
    "australiaeast",
    "australiasoutheast",
    "austriaeast",
    "belgiumcentral",
    "brazilsouth",
    "brazilsoutheast",
    "canadacentral",
    "canadaeast",
    "centralindia",
    "centralus",
    "centraluseuap",
    "chilecentral",
    "eastasia",
    "eastus",
    "eastus2",
    "eastus2euap",
    "francecentral",
    "francesouth",
    "germanynorth",
    "germanywestcentral",
    "indonesiacentral",
    "israelcentral",
    "italynorth",
    "japaneast",
    "japanwest",
    "koreacentral",
    "koreasouth",
    "malaysiawest",
    "mexicocentral",
    "newzealandnorth",
    "northcentralus",
    "northeurope",
    "norwayeast",
    "norwaywest",
    "polandcentral",
    "qatarcentral",
    "southafricanorth",
    "southafricawest",
    "southcentralus",
    "southindia",
    "southeastasia",
    "spaincentral",
    "swedencentral",
    "switzerlandnorth",
    "switzerlandwest",
    "uaecentral",
    "uaenorth",
    "uksouth",
    "ukwest",
    "westcentralus",
    "westeurope",
    "westindia",
    "westus",
    "westus2",
    "westus3",
}
