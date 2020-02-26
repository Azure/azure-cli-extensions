# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_datafactory(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from .vendored_sdks.datafactory import DataFactoryManagementClient
    return get_mgmt_service_client(cli_ctx, DataFactoryManagementClient)


def cf_operations(cli_ctx, *_):
    return cf_datafactory(cli_ctx).operations


def cf_factories(cli_ctx, *_):
    return cf_datafactory(cli_ctx).factories


def cf_exposure_control(cli_ctx, *_):
    return cf_datafactory(cli_ctx).exposure_control


def cf_integration_runtimes(cli_ctx, *_):
    return cf_datafactory(cli_ctx).integration_runtimes


def cf_integration_runtime_object_metadata(cli_ctx, *_):
    return cf_datafactory(cli_ctx).integration_runtime_object_metadata


def cf_integration_runtime_nodes(cli_ctx, *_):
    return cf_datafactory(cli_ctx).integration_runtime_nodes


def cf_linked_services(cli_ctx, *_):
    return cf_datafactory(cli_ctx).linked_services


def cf_datasets(cli_ctx, *_):
    return cf_datafactory(cli_ctx).datasets


def cf_pipelines(cli_ctx, *_):
    return cf_datafactory(cli_ctx).pipelines


def cf_pipeline_runs(cli_ctx, *_):
    return cf_datafactory(cli_ctx).pipeline_runs


def cf_activity_runs(cli_ctx, *_):
    return cf_datafactory(cli_ctx).activity_runs


def cf_triggers(cli_ctx, *_):
    return cf_datafactory(cli_ctx).triggers


def cf_trigger_runs(cli_ctx, *_):
    return cf_datafactory(cli_ctx).trigger_runs


def cf_data_flows(cli_ctx, *_):
    return cf_datafactory(cli_ctx).data_flows


def cf_data_flow_debug_session(cli_ctx, *_):
    return cf_datafactory(cli_ctx).data_flow_debug_session
