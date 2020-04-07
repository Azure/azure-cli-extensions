# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_alertsmanagement(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from .vendored_sdks.alertsmanagement import AlertsManagementClient
    return get_mgmt_service_client(cli_ctx, AlertsManagementClient)


def cf_operations(cli_ctx, *_):
    return cf_alertsmanagement(cli_ctx).operations


def cf_alerts(cli_ctx, *_):
    return cf_alertsmanagement(cli_ctx).alerts


def cf_smart_groups(cli_ctx, *_):
    return cf_alertsmanagement(cli_ctx).smart_groups


def cf_action_rules(cli_ctx, *_):
    return cf_alertsmanagement(cli_ctx).action_rules


def cf_smart_detector_alert_rules(cli_ctx, *_):
    return cf_alertsmanagement(cli_ctx).smart_detector_alert_rules
