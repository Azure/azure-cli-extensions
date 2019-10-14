# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_networkexperiment(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from .vendored_sdks.networkexperiment profiles import FrontDoorManagementClient
    return get_mgmt_service_client(cli_ctx, FrontDoorManagementClient)


def cf_network_experiment_profiles(cli_ctx, *_):
    return cf_networkexperiment(cli_ctx).network_experiment_profiles


def cf_experiments(cli_ctx, *_):
    return cf_networkexperiment(cli_ctx).experiments


def cf_front_doors(cli_ctx, *_):
    return cf_networkexperiment(cli_ctx).front_doors


def cf_policies(cli_ctx, *_):
    return cf_networkexperiment(cli_ctx).policies
