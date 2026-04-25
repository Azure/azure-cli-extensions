# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.mgmt.cloudhealth import CloudHealthMgmtClient


def cf_cloud_health(cli_ctx, *_):
    return get_mgmt_service_client(cli_ctx, CloudHealthMgmtClient)


def cf_health_models(cli_ctx, *_):
    return cf_cloud_health(cli_ctx).health_models


def cf_entities(cli_ctx, *_):
    return cf_cloud_health(cli_ctx).entities


def cf_signal_definitions(cli_ctx, *_):
    return cf_cloud_health(cli_ctx).signal_definitions


def cf_relationships(cli_ctx, *_):
    return cf_cloud_health(cli_ctx).relationships


def cf_authentication_settings(cli_ctx, *_):
    return cf_cloud_health(cli_ctx).authentication_settings


def cf_discovery_rules(cli_ctx, *_):
    return cf_cloud_health(cli_ctx).discovery_rules
