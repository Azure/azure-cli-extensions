# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_logic(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from ..vendored_sdks.logic import LogicManagementClient
    return get_mgmt_service_client(cli_ctx, LogicManagementClient)


def cf_workflow(cli_ctx, *_):
    return cf_logic(cli_ctx).workflow


def cf_workflow_version(cli_ctx, *_):
    return cf_logic(cli_ctx).workflow_version


def cf_workflow_trigger(cli_ctx, *_):
    return cf_logic(cli_ctx).workflow_trigger


def cf_workflow_version_trigger(cli_ctx, *_):
    return cf_logic(cli_ctx).workflow_version_trigger


def cf_workflow_trigger_history(cli_ctx, *_):
    return cf_logic(cli_ctx).workflow_trigger_history


def cf_workflow_run(cli_ctx, *_):
    return cf_logic(cli_ctx).workflow_run


def cf_workflow_run_action(cli_ctx, *_):
    return cf_logic(cli_ctx).workflow_run_action


def cf_workflow_run_action_repetition(cli_ctx, *_):
    return cf_logic(cli_ctx).workflow_run_action_repetition


def cf_workflow_run_action_repetition_request_history(cli_ctx, *_):
    return cf_logic(cli_ctx).workflow_run_action_repetition_request_history


def cf_workflow_run_action_request_history(cli_ctx, *_):
    return cf_logic(cli_ctx).workflow_run_action_request_history


def cf_workflow_run_action_scope_repetition(cli_ctx, *_):
    return cf_logic(cli_ctx).workflow_run_action_scope_repetition


def cf_workflow_run_operation(cli_ctx, *_):
    return cf_logic(cli_ctx).workflow_run_operation


def cf_integration_account(cli_ctx, *_):
    return cf_logic(cli_ctx).integration_account


def cf_integration_account_assembly(cli_ctx, *_):
    return cf_logic(cli_ctx).integration_account_assembly


def cf_integration_account_batch_configuration(cli_ctx, *_):
    return cf_logic(cli_ctx).integration_account_batch_configuration


def cf_integration_account_schema(cli_ctx, *_):
    return cf_logic(cli_ctx).integration_account_schema


def cf_integration_account_map(cli_ctx, *_):
    return cf_logic(cli_ctx).integration_account_map


def cf_integration_account_partner(cli_ctx, *_):
    return cf_logic(cli_ctx).integration_account_partner


def cf_integration_account_agreement(cli_ctx, *_):
    return cf_logic(cli_ctx).integration_account_agreement


def cf_integration_account_certificate(cli_ctx, *_):
    return cf_logic(cli_ctx).integration_account_certificate


def cf_integration_account_session(cli_ctx, *_):
    return cf_logic(cli_ctx).integration_account_session


def cf_integration_service_environment(cli_ctx, *_):
    return cf_logic(cli_ctx).integration_service_environment


def cf_integration_service_environment_sku(cli_ctx, *_):
    return cf_logic(cli_ctx).integration_service_environment_sku


def cf_integration_service_environment_network_health(cli_ctx, *_):
    return cf_logic(cli_ctx).integration_service_environment_network_health


def cf_integration_service_environment_managed_api(cli_ctx, *_):
    return cf_logic(cli_ctx).integration_service_environment_managed_api


def cf_integration_service_environment_managed_api_operation(cli_ctx, *_):
    return cf_logic(cli_ctx).integration_service_environment_managed_api_operation
