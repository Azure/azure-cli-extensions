# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

# API VERSIONS -----------------------------------------

SOURCE_CONTROL_API_VERSION = "2022-03-01"
FLUXCONFIG_API_VERSION = "2024-04-01-preview"
EXTENSION_API_VERSION = "2022-07-01"

# ERROR/HELP TEXT DEFINITIONS -----------------------------------------

KUSTOMIZATION_REQUIRED_VALUES_MISSING_ERROR = (
    "Error! Kustomization definition is invalid, required values {} not found"
)
KUSTOMIZATION_REQUIRED_VALUES_MISSING_HELP = (
    "Add the required values to the Kustomization object and try again"
)

REPOSITORY_REF_REQUIRED_VALUES_MISSING_ERROR = "Error! Repository reference is invalid"
REPOSITORY_REF_REQUIRED_VALUES_MISSING_HELP = (
    "Specifying one of [--branch, --tag, --semver, --commit] is required"
)

REPOSITORY_REF_TOO_MANY_VALUES_ERROR = "Error! Repository reference is invalid"
REPOSITORY_REF_TOO_MANY_VALUES_HELP = (
    "Specifying more than one repository ref argument is invalid"
)

REQUIRED_VALUES_MISSING_ERROR = (
    "Error! Required properties [{}] were not specified for kind '{}'"
)
REQUIRED_VALUES_MISSING_HELP = "Add the missing required properties and try again"

REQUIRED_BUCKET_VALUES_MISSING_ERROR = (
    "Error! Auth properties must be specified for kind 'bucket'"
)
REQUIRED_BUCKET_VALUES_MISSING_HELP = (
    "Provide either both of '--secret-key' and '--access-key' or '--local-auth-ref'"
)
REQUIRED_AZURE_BLOB_SERVICE_PRINCIPAL_VALUES_MISSING_ERROR = (
    "Error! Service principal is invalid because it is missing value(s)"
)
REQUIRED_AZURE_BLOB_SERVICE_PRINCIPAL_VALUES_MISSING_HELP = (
    "Provide '--sp-client-id', '--sp-tenant-id', and either '--sp-client-secret' or '--sp-client-cert'"
)
REQUIRED_AZURE_BLOB_SERVICE_PRINCIPAL_AUTH_ERROR = (
    "Error! Too many authentication methods provided for service principal"
)
REQUIRED_AZURE_BLOB_SERVICE_PRINCIPAL_AUTH_HELP = (
    "Provide either '--sp-client-secret' or '--sp-client-cert'"
)
REQUIRED_AZURE_BLOB_SERVICE_PRINCIPAL_CERT_VALUES_MISSING_ERROR = (
    "Error! Service principal certificate password is invalid"
)
REQUIRED_AZURE_BLOB_SERVICE_PRINCIPAL_CERT_VALUES_MISSING_HELP = (
    "Provide '--sp-client-id', '--sp-tenant-id', and '--sp-client-cert' with your '--sp-cert-password"
)
REQUIRED_AZURE_BLOB_AUTH_ERROR = (
    "Error! Too many authentication methods provided for Azure Blob"
)
REQUIRED_AZURE_BLOB_AUTH_HELP = (
    "Specify one of the available authentication methods from the list: '--local-auth-ref', '--account-key', '--sas-token', '--mi-client-id', or service principal with '--sp-client-id', '--sp-tenant-id', and either '--sp-client-secret' or '--sp-client-cert'"
)
EXTRA_VALUES_PROVIDED_ERROR = (
    "Error! Invalid properties [{}] were specified for kind '{}'"
)
EXTRA_VALUES_PROVIDED_HELP = "Valid properties for kind '{}' include [{}]"

INVALID_DURATION_ERROR = "Error! Invalid {0}."
INVALID_DURATION_HELP = "Specify a valid Go duration and try again (i.e. 1h2m5s)"

INVALID_URL_ERROR = "Error! Invalid --url."
INVALID_URL_HELP = (
    "Url must begin with one of ['http://', 'https://', 'git@', 'ssh://']"
)

INVALID_KUBERNETES_NAME_LENGTH_ERROR = "Error! Invalid {0}"
INVALID_KUBERNETES_NAME_LENGTH_HELP = "Parameter {0} can be a maximum of {1} characters. Specify a shorter name and try again."

INVALID_KUBERNETES_NAME_HYPHEN_ERROR = "Error! Invalid {0}"
INVALID_KUBERNETES_NAME_HYPHEN_HELP = "Parameter {0} cannot begin or end with a hyphen."

INVALID_KUBERNETES_NAME_PERIOD_ERROR = "Error! Invalid {0}"
INVALID_KUBERNETES_NAME_PERIOD_HELP = "Parameter {0} cannot begin or end with a period."

INVALID_KUBERNETES_DNS_NAME_ERROR = "Error! Invalid {0}"
INVALID_KUBERNETES_DNS_NAME_HELP = (
    "Parameter {0} can only contain lowercase alphanumeric characters and hyphens"
)

INVALID_KUBERNETES_DNS_SUBDOMAIN_NAME_ERROR = "Error! Invalid {0}"
INVALID_KUBERNETES_DNS_SUBDOMAIN_NAME_HELP = "Parameter {0} can only contain lowercase alphanumeric characters, hyphens, and periods"

DUPLICATE_KUSTOMIZATION_NAME_ERROR = "Error! Invalid kustomization list. Kustomization name '{0}' duplicated in multiple Kustomization objects"
DUPLICATE_KUSTOMIZATION_NAME_HELP = (
    "Ensure that all Kustomization names are unique and try again"
)

KUSTOMIZATION_NAME_TOO_LONG_ERROR = "Error! Invalid Kustomization list. Flux configuration name '{0}' combined with kustomization name '{1}' cannot be greater than 62 characters"
KUSTOMIZATION_NAME_TOO_LONG_HELP = (
    "Shorten the flux configuration or the kustomization name and try again"
)

CREATE_KUSTOMIZATION_EXIST_ERROR = "Error! Cannot create a kustomization that already exists. Kustomization name '{0}' already exists on configuration '{1}'"
CREATE_KUSTOMIZATION_EXIST_HELP = "You can update an already created kustomization with 'az k8s-configuration flux kustomization update'"

UPDATE_KUSTOMIZATION_NO_EXIST_ERROR = "Error! Cannot update a kustomization that doesn't exist. Kustomization name '{0}' does not exist on configuration '{1}'"
UPDATE_KUSTOMIZATION_NO_EXIST_HELP = "You can add the kustomization to the configuration with 'az k8s-configuration flux kustomization create'"

DELETE_KUSTOMIZATION_NO_EXIST_ERROR = (
    "Error! Cannot delete a kustomization that doesn't exist."
)
DELETE_KUSTOMIZATION_NO_EXIST_HELP = "You can view all kustomizations on a configuration with 'az k8s-configuration flux kustomization list'"

SHOW_KUSTOMIZATION_NO_EXIST_ERROR = (
    "Error! Kustomization with name '{0}' does not exist on configuration '{1}'."
)
SHOW_KUSTOMIZATION_NO_EXIST_HELP = "You can view all kustomizations on a configuration with 'az k8s-configuration flux kustomization list'"

SHOW_DEPLOYED_OBJECT_NO_EXIST_ERROR = "Error! Deployed object with name '{0}', namespace '{1}', and kind '{2}' does not exist on configuration '{3}'."
SHOW_DEPLOYED_OBJECT_NO_EXIST_HELP = "You can view all deployed objects on a configuration with 'az k8s-configuration flux deployed-object list'"

SSH_PRIVATE_KEY_WITH_HTTP_URL_ERROR = (
    "Error! An --ssh-private-key cannot be used with an http(s) url"
)
SSH_PRIVATE_KEY_WITH_HTTP_URL_HELP = (
    "Verify the url provided is a valid ssh url and not an http(s) url"
)

KNOWN_HOSTS_WITH_HTTP_URL_ERROR = (
    "Error! --ssh-known-hosts cannot be used with an http(s) url"
)
KNOWN_HOSTS_WITH_HTTP_URL_HELP = (
    "Verify the url provided is a valid ssh url and not an http(s) url"
)

HTTPS_AUTH_WITH_SSH_URL_ERROR = "Error! https auth (--https-user and --https-key) cannot be used with a non-http(s) url"
HTTPS_AUTH_WITH_SSH_URL_HELP = (
    "Verify the url provided is a valid http(s) url and not an ssh url"
)

KNOWN_HOSTS_BASE64_ENCODING_ERROR = (
    "Error! ssh known_hosts is not a valid utf-8 base64 encoded string"
)
KNOWN_HOSTS_BASE64_ENCODING_HELP = (
    "Verify that the string provided safely decodes into a valid utf-8 format"
)

KNOWN_HOSTS_FORMAT_ERROR = "Error! ssh known_hosts provided in wrong format"
KNOWN_HOSTS_FORMAT_HELP = "Verify that all lines in the known_hosts contents are provided in a valid sshd(8) format"

SSH_PRIVATE_KEY_ERROR = "Error! --ssh-private-key provided in invalid format"
SSH_PRIVATE_KEY_HELP = "Verify the key provided is a valid PEM-formatted key of type RSA, ECC, DSA, or Ed25519"

HTTPS_USER_KEY_MATCH_ERROR = (
    "Error! --https-user and --https-key cannot be used separately"
)
HTTPS_USER_KEY_MATCH_HELP = "Try providing both --https-user and --https-key together"

KEY_FILE_READ_ERROR = "Error! Unable to read key file specified with: {0}"
KEY_FILE_READ_HELP = (
    "Verify that the filepath specified exists and contains valid utf-8 data"
)

KEY_AND_FILE_TOGETHER_ERROR = (
    "Error! Both textual key and key filepath cannot be provided"
)
KEY_AND_FILE_TOGETHER_HELP = (
    "Try providing the file parameter without providing the plaintext parameter"
)

SCC_EXISTS_ON_CLUSTER_ERROR = (
    "Error! Flux v1 configurations already exist on the cluster"
)
SCC_EXISTS_ON_CLUSTER_HELP = "Try removing all Flux v1 configurations from the cluster before attempting to add Flux v2 configurations"

FLUX_EXTENSION_NOT_SUCCEEDED_OR_CREATING_ERROR = "Error! 'Microsoft.Flux' extension is installed but not in a succeeded state on the cluster. Unable to proceed with Flux v2 configuration install."
FLUX_EXTENSION_NOT_SUCCEEDED_OR_CREATING_HELP = "Try resolving the extension error on the cluster or removing and re-installing the extension."

FLUX_EXTENSION_CREATING_ERROR = "Error! 'Microsoft.Flux' extension is currently installing on the cluster. Unable to proceed with Flux v2 configuration install."
FLUX_EXTENSION_CREATING_HELP = "Try again in a few minutes when the 'Microsoft.Flux' extension installation has completed."

NO_KUSTOMIZATIONS_WARNING = "Warning! No kustomizations were specified for this configuration. A kustomization will be generated with the default name 'kustomization-1'."
DEFAULT_KUSTOMIZATION_NAME = "kustomization-1"

# PROVIDER REGISTRATION -----------------------------------------

CC_REGISTRATION_WARNING = "'Flux Configuration' cannot be used because '%s' provider has not been registered. More details for registering this provider can be found here - %s"
CC_REGISTRATION_LINK = "https://aka.ms/RegisterKubernetesConfigurationProvider"
CC_REGISTRATION_ERROR = "Unable to fetch registration state of '{0}' provider. Failed to enable 'flux configuration' feature..."
CC_PROVIDER_NAMESPACE = "Microsoft.KubernetesConfiguration"
REGISTERED = "Registered"
CREATING = "Creating"
SUCCEEDED = "Succeeded"

FLUX_EXTENSION_TYPE = "microsoft.flux"

SSH_PRIVATE_KEY_KEY = "sshPrivateKey"
HTTPS_USER_KEY = "httpsUser"
HTTPS_KEY_KEY = "httpsKey"
BUCKET_SECRET_KEY_KEY = "bucketSecretKey"

GIT_REPO_REQUIRED_PARAMS = {"url"}
GIT_REPO_VALID_PARAMS = {
    "url",
    "branch",
    "tag",
    "semver",
    "commit",
    "sync_interval",
    "timeout",
    "ssh_private_key",
    "ssh_private_key_file",
    "https_user",
    "https_key",
    "https_ca_cert",
    "https_ca_cert_file",
    "known_hosts",
    "known_hosts_file",
    "local_auth_ref",
}

BUCKET_REQUIRED_PARAMS = {"url", "bucket_name"}
BUCKET_VALID_PARAMS = {
    "url",
    "bucket_name",
    "sync_interval",
    "timeout",
    "bucket_access_key",
    "bucket_secret_key",
    "bucket_insecure",
    "local_auth_ref",
}

AZUREBLOB_REQUIRED_PARAMS = {"url", "container_name"}
AZUREBLOB_VALID_PARAMS = {
    "url",
    "container_name",
    "sync_interval",
    "timeout",
    "account_key",
    "local_auth_ref",
    "sp_tenant_id",
    "sp_client_id",
    "sp_client_cert",
    "sp_client_cert_password",
    "sp_client_secret",
    "sp_client_cert_send_chain",
    "sas_token",
    "mi_client_id",
}

DEPENDENCY_KEYS = ["dependencies", "depends_on", "dependsOn", "depends"]
SYNC_INTERVAL_KEYS = ["interval", "sync_interval", "syncInterval"]
RETRY_INTERVAL_KEYS = ["retryInterval", "retry_interval"]
TIMEOUT_KEYS = ["timeout"]
REQUIRED_KUSTOMIZATION_KEYS = {"name"}
WAIT_KUSTOMIZATION_KEYS = ["disable-health-check"]

VALID_DURATION_REGEX = r"((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?"
VALID_GIT_URL_REGEX = r"^(((http|https|ssh)://)|(git@))"
VALID_BUCKET_URL_REGEX = r"^(((http|https)://))"
VALID_AZUREBLOB_URL_REGEX = r"^(((http|https)://))"

VALID_KUBERNETES_DNS_SUBDOMAIN_NAME_REGEX = r"^[a-z0-9]([\.\-a-z0-9]*[a-z0-9])?$"
VALID_KUBERNETES_DNS_NAME_REGEX = r"^[a-z0-9]([\-a-z0-9]*[a-z0-9])?$"

GIT = "git"
BUCKET = "bucket"
BUCKET_CAPS = "Bucket"
AZBLOB = "azblob"
AZURE_BLOB = "AzureBlob"
GIT_REPOSITORY = "GitRepository"

CONNECTED_CLUSTER_TYPE = "connectedclusters"
MANAGED_CLUSTER_TYPE = "managedclusters"
APPLIANCE_TYPE = "appliances"
PROVISIONED_CLUSTER_TYPE = "provisionedclusters"

MANAGED_CLUSTER_RP = "Microsoft.ContainerService"
CONNECTED_CLUSTER_RP = "Microsoft.Kubernetes"
APPLIANCE_RP = "Microsoft.ResourceConnector"
HYBRIDCONTAINERSERVICE_RP = "microsoft.hybridcontainerservice"

CONNECTED_CLUSTER_API_VERSION = "2021-10-01"
MANAGED_CLUSTER_API_VERSION = "2021-10-01"
APPLIANCE_API_VERSION = "2021-10-31-preview"
HYBRIDCONTAINERSERVICE_API_VERSION = "2022-05-01-preview"

KUBERNETES_MAX_NAME_SIZE = 63

DF_RM_ENDPOINT = "https://api-dogfood.resources.windows-int.net/"

FLUX_EXTENSION_RELEASETRAIN = "FLUX_EXTENSION_RELEASETRAIN"
FLUX_EXTENSION_VERSION = "FLUX_EXTENSION_VERSION"
