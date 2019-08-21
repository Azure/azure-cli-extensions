# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from .vendored_sdks.microservices4spring import Microservices4SpringManagementClient


def cf_asc(cli_ctx, *_):
    return get_mgmt_service_client(cli_ctx, Microservices4SpringManagementClient)


def cf_app_clusters(cli_ctx, *_):
    return cf_asc(cli_ctx).app_clusters


def cf_apps(cli_ctx, *_):
    return cf_asc(cli_ctx).apps


def cf_deployments(cli_ctx, *_):
    return cf_asc(cli_ctx).deployments


def cf_bindings(cli_ctx, *_):
    return cf_asc(cli_ctx).bindings
