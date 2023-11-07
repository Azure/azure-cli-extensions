# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
MANAGED_ENVIRONMENT_TYPE = "managed"
CONNECTED_ENVIRONMENT_TYPE = "connected"
MANAGED_ENVIRONMENT_RESOURCE_TYPE = "managedEnvironments"
CONNECTED_ENVIRONMENT_RESOURCE_TYPE = "connectedEnvironments"
CUSTOM_LOCATION_RESOURCE_TYPE = "customLocations"

MAXIMUM_SECRET_LENGTH = 20
MAXIMUM_CONTAINER_APP_NAME_LENGTH = 32

SHORT_POLLING_INTERVAL_SECS = 3
LONG_POLLING_INTERVAL_SECS = 10

ACR_IMAGE_SUFFIX = ".azurecr.io"

CONTAINER_APPS_SDK_MODELS = "azext_containerapp._sdk_models"

LOG_ANALYTICS_RP = "Microsoft.OperationalInsights"
CONTAINER_APPS_RP = "Microsoft.App"
SERVICE_LINKER_RP = "Microsoft.ServiceLinker"
EXTENDED_LOCATION_RP = "Microsoft.ExtendedLocation"
CONTAINER_APP_EXTENSION_TYPE = "microsoft.app.environment"

MANAGED_CERTIFICATE_RT = "managedCertificates"
PRIVATE_CERTIFICATE_RT = "certificates"

DAPR_SUPPORTED_STATESTORE_DEV_SERVICE_LIST = ["postgres", "redis"]
DAPR_SUPPORTED_PUBSUB_DEV_SERVICE_LIST = ["kafka", "redis"]

DEV_SERVICE_LIST = ["kafka", "postgres", "redis", "mariadb", "qdrant", "milvus"]

DEV_KAFKA_IMAGE = 'kafka'
DEV_KAFKA_SERVICE_TYPE = 'kafka'
DEV_KAFKA_CONTAINER_NAME = 'kafka'

DEV_POSTGRES_IMAGE = 'postgres'
DEV_POSTGRES_SERVICE_TYPE = 'postgres'
DEV_POSTGRES_CONTAINER_NAME = 'postgres'

DEV_REDIS_IMAGE = 'redis'
DEV_REDIS_SERVICE_TYPE = 'redis'
DEV_REDIS_CONTAINER_NAME = 'redis'

DEV_MARIADB_IMAGE = 'mariadb'
DEV_MARIADB_SERVICE_TYPE = 'mariadb'
DEV_MARIADB_CONTAINER_NAME = 'mariadb'

DEV_QDRANT_IMAGE = 'qdrant'
DEV_QDRANT_SERVICE_TYPE = 'qdrant'
DEV_QDRANT_CONTAINER_NAME = 'qdrant'

DEV_MILVUS_IMAGE = 'milvus'
DEV_MILVUS_SERVICE_TYPE = 'milvus'
DEV_MILVUS_CONTAINER_NAME = 'milvus'

PENDING_STATUS = "Pending"
SUCCEEDED_STATUS = "Succeeded"
UPDATING_STATUS = "Updating"

BLOB_STORAGE_TOKEN_STORE_SECRET_SETTING_NAME = "blob-storage-token-store-sasurl-secret"

MICROSOFT_SECRET_SETTING_NAME = "microsoft-provider-authentication-secret"
FACEBOOK_SECRET_SETTING_NAME = "facebook-provider-authentication-secret"
GITHUB_SECRET_SETTING_NAME = "github-provider-authentication-secret"
GOOGLE_SECRET_SETTING_NAME = "google-provider-authentication-secret"
MSA_SECRET_SETTING_NAME = "msa-provider-authentication-secret"
TWITTER_SECRET_SETTING_NAME = "twitter-provider-authentication-secret"
APPLE_SECRET_SETTING_NAME = "apple-provider-authentication-secret"
UNAUTHENTICATED_CLIENT_ACTION = ['RedirectToLoginPage', 'AllowAnonymous', 'Return401', 'Return403']
FORWARD_PROXY_CONVENTION = ['NoProxy', 'Standard', 'Custom']
CHECK_CERTIFICATE_NAME_AVAILABILITY_TYPE = "Microsoft.App/managedEnvironments/certificates"
CONNECTED_ENV_CHECK_CERTIFICATE_NAME_AVAILABILITY_TYPE = "Microsoft.App/connectedEnvironments/certificates"

NAME_INVALID = "Invalid"
NAME_ALREADY_EXISTS = "AlreadyExists"

LOG_TYPE_CONSOLE = "console"
LOG_TYPE_SYSTEM = "system"

ACR_TASK_TEMPLATE = """version: v1.1.0
steps:
  - cmd: mcr.microsoft.com/oryx/cli:debian-buster-20230222.1 oryx dockerfile --bind-port {{target_port}} --output ./Dockerfile .
    timeout: 28800
  - build: -t $Registry/{{image_name}} -f Dockerfile .
    timeout: 28800
  - push: ["$Registry/{{image_name}}"]
    timeout: 1800
"""

ACA_BUILDER_BULLSEYE_IMAGE = "mcr.microsoft.com/oryx/builder:debian-bullseye-20231025.1"
ACA_BUILDER_BOOKWORM_IMAGE = "mcr.microsoft.com/oryx/builder:debian-bookworm-20231025.1"

DEFAULT_PORT = 8080  # used for no dockerfile scenario; not the hello world image

HELLO_WORLD_IMAGE = "mcr.microsoft.com/k8se/quickstart:latest"

LOGS_STRING = '[{"category":"ContainerAppConsoleLogs","categoryGroup":null,"enabled":true,"retentionPolicy":{"days":0,"enabled":false}},{"category":"ContainerAppSystemLogs","categoryGroup":null,"enabled":true,"retentionPolicy":{"days":0,"enabled":false}}]'  # pylint: disable=line-too-long
