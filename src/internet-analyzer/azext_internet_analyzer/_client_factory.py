# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_internet_analyzer(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from .vendored_sdks.frontdoor import FrontDoorManagementClient
    return get_mgmt_service_client(cli_ctx, FrontDoorManagementClient)


def cf_network_experiment_profiles(cli_ctx, *_):
    return cf_internet_analyzer(cli_ctx).network_experiment_profiles


def cf_preconfigured_endpoints(cli_ctx, *_):
    return cf_internet_analyzer(cli_ctx).preconfigured_endpoints


def cf_experiments(cli_ctx, *_):
    return cf_internet_analyzer(cli_ctx).experiments


def cf_reports(cli_ctx, *_):
    return cf_internet_analyzer(cli_ctx).reports


def cf_front_doors(cli_ctx, *_):
    return cf_internet_analyzer(cli_ctx).front_doors


def cf_frontend_endpoints(cli_ctx, *_):
    return cf_internet_analyzer(cli_ctx).frontend_endpoints


def cf_policies(cli_ctx, *_):
    return cf_internet_analyzer(cli_ctx).policies


def cf_managed_rule_sets(cli_ctx, *_):
    return cf_internet_analyzer(cli_ctx).managed_rule_sets
