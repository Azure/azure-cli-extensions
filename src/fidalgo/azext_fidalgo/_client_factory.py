# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

def cf_fidalgo_dataplane(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azext_fidalgo.vendored_sdks.fidalgo_dataplane import FidalgoDataplaneClient   

    return get_mgmt_service_client(cli_ctx, 
                                   FidalgoDataplaneClient,
                                   subscription_bound=False,
                                   base_url_bound=False)


def cf_project(cli_ctx, *_):
    return cf_fidalgo_dataplane(cli_ctx).project


def cf_pool(cli_ctx, *_):
    return cf_fidalgo_dataplane(cli_ctx).pool


def cf_virtual_machine(cli_ctx, *_):
    return cf_fidalgo_dataplane(cli_ctx).virtual_machine
