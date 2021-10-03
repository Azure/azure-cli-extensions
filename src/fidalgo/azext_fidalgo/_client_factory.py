# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

def cf_fidalgo_dataplane(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azext_fidalgo.vendored_sdks.fidalgo_dataplane import FidalgoDataplaneClient   

    # Override the client to use Fidalgo resource rather than ARM's. The .default scope will be appended by the mgmt service client
    cli_ctx.cloud.endpoints.active_directory_resource_id = 'https://devcenters.fidalgo.azure.com'
    return get_mgmt_service_client(cli_ctx, FidalgoDataplaneClient, subscription_bound=False, base_url_bound=False)


def cf_project(cli_ctx, *_):
    return cf_fidalgo_dataplane(cli_ctx).project


def cf_pool(cli_ctx, *_):
    return cf_fidalgo_dataplane(cli_ctx).pool


def cf_virtual_machine(cli_ctx, *_):
    return cf_fidalgo_dataplane(cli_ctx).virtual_machine


def cf_environment(cli_ctx, *_):
    return cf_fidalgo_dataplane(cli_ctx).environments


def cf_deployment(cli_ctx, *_):
    return cf_fidalgo_dataplane(cli_ctx).deployments


def cf_catalog_item(cli_ctx, *_):
    return cf_fidalgo_dataplane(cli_ctx).catalog_item


def cf_environment_type(cli_ctx, *_):
    return cf_fidalgo_dataplane(cli_ctx).environment_type