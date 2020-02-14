# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_notificationhubs(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from .vendored_sdks.notificationhubs import NotificationHubsManagementClient
    return get_mgmt_service_client(cli_ctx, NotificationHubsManagementClient)


def cf_operations(cli_ctx, *_):
    return cf_notificationhubs(cli_ctx).operations


def cf_namespaces(cli_ctx, *_):
    return cf_notificationhubs(cli_ctx).namespaces


def cf_notification_hubs(cli_ctx, *_):
    return cf_notificationhubs(cli_ctx).notification_hubs
