# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.profiles import ResourceType
from .vendored_sdks.appplatform.v2020_07_01 import AppPlatformManagementClient
from .vendored_sdks.appplatform.v2020_11_01_preview import (
    AppPlatformManagementClient as AppPlatformManagementClient_20201101preview
)
from .vendored_sdks.appplatform.v2022_01_01_preview import (
    AppPlatformManagementClient as AppPlatformManagementClient_20220101preview
)
from .vendored_sdks.appplatform.v2022_03_01_preview import (
    AppPlatformManagementClient as AppPlatformManagementClient_20220301preview
)
from .vendored_sdks.appplatform.v2021_06_01_preview import (
    AppPlatformManagementClient as AppPlatformManagementClient_20210601preview
)
from .vendored_sdks.appplatform.v2021_09_01_preview import (
    AppPlatformManagementClient as AppPlatformManagementClient_20210901preview
)


def cf_spring_cloud_20220301preview(cli_ctx, *_):
    return get_mgmt_service_client(cli_ctx, AppPlatformManagementClient_20220301preview)


def cf_spring_cloud_20220101preview(cli_ctx, *_):
    return get_mgmt_service_client(cli_ctx, AppPlatformManagementClient_20220101preview)


def cf_spring_cloud(cli_ctx, *_):
    return get_mgmt_service_client(cli_ctx, AppPlatformManagementClient)


def cf_spring_cloud_20201101preview(cli_ctx, *_):
    return get_mgmt_service_client(cli_ctx, AppPlatformManagementClient_20201101preview)


def cf_spring_cloud_20210601preview(cli_ctx, *_):
    return get_mgmt_service_client(cli_ctx, AppPlatformManagementClient_20210601preview)


def cf_spring_cloud_20210901preview(cli_ctx, *_):
    return get_mgmt_service_client(cli_ctx, AppPlatformManagementClient_20210901preview)


def cf_resource_groups(cli_ctx, subscription_id=None):
    return get_mgmt_service_client(cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES,
                                   subscription_id=subscription_id).resource_groups


def cf_app_services(cli_ctx, *_):
    return cf_spring_cloud(cli_ctx).services


def cf_apps(cli_ctx, *_):
    return cf_spring_cloud(cli_ctx).apps


def cf_deployments(cli_ctx, *_):
    return cf_spring_cloud(cli_ctx).deployments


def cf_bindings(cli_ctx, *_):
    return cf_spring_cloud(cli_ctx).bindings


def cf_config_servers(cli_ctx, *_):
    return cf_spring_cloud(cli_ctx).config_servers


def cf_certificates(cli_ctx, *_):
    return cf_spring_cloud(cli_ctx).certificates


def cf_custom_domains(cli_ctx, *_):
    return cf_spring_cloud(cli_ctx).custom_domains
