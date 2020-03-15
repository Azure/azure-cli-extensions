# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):

    from ._client_factory import cf_workflow
    logic_workflow = CliCommandType(
        operations_tmpl='azext_logic.vendored_sdks.logic.operations._workflow_operations#WorkflowOperations.{}',
        client_factory=cf_workflow)
    with self.command_group('logic workflow', logic_workflow, client_factory=cf_workflow) as g:
        g.custom_command('list', 'logic_workflow_list')
        g.custom_show_command('show', 'logic_workflow_show')
        g.custom_command('create', 'logic_workflow_create')
        g.custom_command('update', 'logic_workflow_update')
        g.custom_command('delete', 'logic_workflow_delete')
        g.custom_command('generate-upgraded-definition', 'logic_workflow_generate_upgraded_definition')
        g.custom_command('list-callback-url', 'logic_workflow_list_callback_url')
        g.custom_command('move', 'logic_workflow_move', supports_no_wait=True)
        g.custom_command('regenerate-access-key', 'logic_workflow_regenerate_access_key')
        g.custom_command('validate-by-resource-group', 'logic_workflow_validate_by_resource_group')
        g.custom_command('validate-by-location', 'logic_workflow_validate_by_location')
        g.custom_command('disable', 'logic_workflow_disable')
        g.custom_command('enable', 'logic_workflow_enable')
        g.custom_command('list-swagger', 'logic_workflow_list_swagger')
        g.wait_command('wait');

    from ._client_factory import cf_workflow_version
    logic_workflow_version = CliCommandType(
        operations_tmpl='azext_logic.vendored_sdks.logic.operations._workflow_version_operations#WorkflowVersionOperations.{}',
        client_factory=cf_workflow_version)
    with self.command_group('logic workflow-version', logic_workflow_version, client_factory=cf_workflow_version) as g:
        g.custom_command('list', 'logic_workflow_version_list')
        g.custom_show_command('show', 'logic_workflow_version_show')

    from ._client_factory import cf_workflow_trigger
    logic_workflow_trigger = CliCommandType(
        operations_tmpl='azext_logic.vendored_sdks.logic.operations._workflow_trigger_operations#WorkflowTriggerOperations.{}',
        client_factory=cf_workflow_trigger)
    with self.command_group('logic workflow-trigger', logic_workflow_trigger, client_factory=cf_workflow_trigger) as g:
        g.custom_command('list', 'logic_workflow_trigger_list')
        g.custom_show_command('show', 'logic_workflow_trigger_show')
        g.custom_command('reset', 'logic_workflow_trigger_reset')
        g.custom_command('run', 'logic_workflow_trigger_run')
        g.custom_command('list-callback-url', 'logic_workflow_trigger_list_callback_url')

    from ._client_factory import cf_workflow_version_trigger
    logic_workflow_version_trigger = CliCommandType(
        operations_tmpl='azext_logic.vendored_sdks.logic.operations._workflow_version_trigger_operations#WorkflowVersionTriggerOperations.{}',
        client_factory=cf_workflow_version_trigger)
    with self.command_group('logic workflow-version-trigger', logic_workflow_version_trigger, client_factory=cf_workflow_version_trigger) as g:
        g.custom_command('list-callback-url', 'logic_workflow_version_trigger_list_callback_url')

    from ._client_factory import cf_workflow_trigger_history
    logic_workflow_trigger_history = CliCommandType(
        operations_tmpl='azext_logic.vendored_sdks.logic.operations._workflow_trigger_history_operations#WorkflowTriggerHistoryOperations.{}',
        client_factory=cf_workflow_trigger_history)
    with self.command_group('logic workflow-trigger-history', logic_workflow_trigger_history, client_factory=cf_workflow_trigger_history) as g:
        g.custom_command('list', 'logic_workflow_trigger_history_list')
        g.custom_show_command('show', 'logic_workflow_trigger_history_show')
        g.custom_command('resubmit', 'logic_workflow_trigger_history_resubmit')

    from ._client_factory import cf_workflow_run
    logic_workflow_run = CliCommandType(
        operations_tmpl='azext_logic.vendored_sdks.logic.operations._workflow_run_operations#WorkflowRunOperations.{}',
        client_factory=cf_workflow_run)
    with self.command_group('logic workflow-run', logic_workflow_run, client_factory=cf_workflow_run) as g:
        g.custom_command('list', 'logic_workflow_run_list')
        g.custom_show_command('show', 'logic_workflow_run_show')
        g.custom_command('cancel', 'logic_workflow_run_cancel')

    from ._client_factory import cf_workflow_run_action
    logic_workflow_run_action = CliCommandType(
        operations_tmpl='azext_logic.vendored_sdks.logic.operations._workflow_run_action_operations#WorkflowRunActionOperations.{}',
        client_factory=cf_workflow_run_action)
    with self.command_group('logic workflow-run-action', logic_workflow_run_action, client_factory=cf_workflow_run_action) as g:
        g.custom_command('list', 'logic_workflow_run_action_list')
        g.custom_show_command('show', 'logic_workflow_run_action_show')
        g.custom_command('list-expression-trace', 'logic_workflow_run_action_list_expression_trace')

    from ._client_factory import cf_workflow_run_action_repetition
    logic_workflow_run_action_repetition = CliCommandType(
        operations_tmpl='azext_logic.vendored_sdks.logic.operations._workflow_run_action_repetition_operations#WorkflowRunActionRepetitionOperations.{}',
        client_factory=cf_workflow_run_action_repetition)
    with self.command_group('logic workflow-run-action-repetition', logic_workflow_run_action_repetition, client_factory=cf_workflow_run_action_repetition) as g:
        g.custom_command('list', 'logic_workflow_run_action_repetition_list')
        g.custom_show_command('show', 'logic_workflow_run_action_repetition_show')
        g.custom_command('list-expression-trace', 'logic_workflow_run_action_repetition_list_expression_trace')

    from ._client_factory import cf_workflow_run_action_repetition_request_history
    logic_workflow_run_action_repetition_request_history = CliCommandType(
        operations_tmpl='azext_logic.vendored_sdks.logic.operations._workflow_run_action_repetition_request_history_operations#WorkflowRunActionRepetitionRequestHistoryOperations.{}',
        client_factory=cf_workflow_run_action_repetition_request_history)
    with self.command_group('logic workflow-run-action-repetition-request-history', logic_workflow_run_action_repetition_request_history, client_factory=cf_workflow_run_action_repetition_request_history) as g:
        g.custom_command('list', 'logic_workflow_run_action_repetition_request_history_list')
        g.custom_show_command('show', 'logic_workflow_run_action_repetition_request_history_show')

    from ._client_factory import cf_workflow_run_action_request_history
    logic_workflow_run_action_request_history = CliCommandType(
        operations_tmpl='azext_logic.vendored_sdks.logic.operations._workflow_run_action_request_history_operations#WorkflowRunActionRequestHistoryOperations.{}',
        client_factory=cf_workflow_run_action_request_history)
    with self.command_group('logic workflow-run-action-request-history', logic_workflow_run_action_request_history, client_factory=cf_workflow_run_action_request_history) as g:
        g.custom_command('list', 'logic_workflow_run_action_request_history_list')
        g.custom_show_command('show', 'logic_workflow_run_action_request_history_show')

    from ._client_factory import cf_workflow_run_action_scope_repetition
    logic_workflow_run_action_scope_repetition = CliCommandType(
        operations_tmpl='azext_logic.vendored_sdks.logic.operations._workflow_run_action_scope_repetition_operations#WorkflowRunActionScopeRepetitionOperations.{}',
        client_factory=cf_workflow_run_action_scope_repetition)
    with self.command_group('logic workflow-run-action-scope-repetition', logic_workflow_run_action_scope_repetition, client_factory=cf_workflow_run_action_scope_repetition) as g:
        g.custom_command('list', 'logic_workflow_run_action_scope_repetition_list')
        g.custom_show_command('show', 'logic_workflow_run_action_scope_repetition_show')

    from ._client_factory import cf_workflow_run_operation
    logic_workflow_run_operation = CliCommandType(
        operations_tmpl='azext_logic.vendored_sdks.logic.operations._workflow_run_operation_operations#WorkflowRunOperationOperations.{}',
        client_factory=cf_workflow_run_operation)
    with self.command_group('logic workflow-run-operation', logic_workflow_run_operation, client_factory=cf_workflow_run_operation) as g:
        g.custom_show_command('show', 'logic_workflow_run_operation_show')

    from ._client_factory import cf_integration_account
    logic_integration_account = CliCommandType(
        operations_tmpl='azext_logic.vendored_sdks.logic.operations._integration_account_operations#IntegrationAccountOperations.{}',
        client_factory=cf_integration_account)
    with self.command_group('logic integration-account', logic_integration_account, client_factory=cf_integration_account) as g:
        g.custom_command('list', 'logic_integration_account_list')
        g.custom_show_command('show', 'logic_integration_account_show')
        g.custom_command('create', 'logic_integration_account_create')
        g.custom_command('update', 'logic_integration_account_update')
        g.custom_command('delete', 'logic_integration_account_delete')
        g.custom_command('list-callback-url', 'logic_integration_account_list_callback_url')
        g.custom_command('list-key-vault-key', 'logic_integration_account_list_key_vault_key')
        g.custom_command('log-tracking-event', 'logic_integration_account_log_tracking_event')
        g.custom_command('regenerate-access-key', 'logic_integration_account_regenerate_access_key')

    from ._client_factory import cf_integration_account_assembly
    logic_integration_account_assembly = CliCommandType(
        operations_tmpl='azext_logic.vendored_sdks.logic.operations._integration_account_assembly_operations#IntegrationAccountAssemblyOperations.{}',
        client_factory=cf_integration_account_assembly)
    with self.command_group('logic integration-account-assembly', logic_integration_account_assembly, client_factory=cf_integration_account_assembly) as g:
        g.custom_command('list', 'logic_integration_account_assembly_list')
        g.custom_show_command('show', 'logic_integration_account_assembly_show')
        g.custom_command('create', 'logic_integration_account_assembly_create')
        g.generic_update_command('update')
        g.custom_command('delete', 'logic_integration_account_assembly_delete')
        g.custom_command('list-content-callback-url', 'logic_integration_account_assembly_list_content_callback_url')

    from ._client_factory import cf_integration_account_batch_configuration
    logic_integration_account_batch_configuration = CliCommandType(
        operations_tmpl='azext_logic.vendored_sdks.logic.operations._integration_account_batch_configuration_operations#IntegrationAccountBatchConfigurationOperations.{}',
        client_factory=cf_integration_account_batch_configuration)
    with self.command_group('logic integration-account-batch-configuration', logic_integration_account_batch_configuration, client_factory=cf_integration_account_batch_configuration) as g:
        g.custom_command('list', 'logic_integration_account_batch_configuration_list')
        g.custom_show_command('show', 'logic_integration_account_batch_configuration_show')
        g.custom_command('create', 'logic_integration_account_batch_configuration_create')
        g.generic_update_command('update')
        g.custom_command('delete', 'logic_integration_account_batch_configuration_delete')

    from ._client_factory import cf_integration_account_schema
    logic_integration_account_schema = CliCommandType(
        operations_tmpl='azext_logic.vendored_sdks.logic.operations._integration_account_schema_operations#IntegrationAccountSchemaOperations.{}',
        client_factory=cf_integration_account_schema)
    with self.command_group('logic integration-account-schema', logic_integration_account_schema, client_factory=cf_integration_account_schema) as g:
        g.custom_command('list', 'logic_integration_account_schema_list')
        g.custom_show_command('show', 'logic_integration_account_schema_show')
        g.custom_command('create', 'logic_integration_account_schema_create')
        g.generic_update_command('update')
        g.custom_command('delete', 'logic_integration_account_schema_delete')
        g.custom_command('list-content-callback-url', 'logic_integration_account_schema_list_content_callback_url')

    from ._client_factory import cf_integration_account_map
    logic_integration_account_map = CliCommandType(
        operations_tmpl='azext_logic.vendored_sdks.logic.operations._integration_account_map_operations#IntegrationAccountMapOperations.{}',
        client_factory=cf_integration_account_map)
    with self.command_group('logic integration-account-map', logic_integration_account_map, client_factory=cf_integration_account_map) as g:
        g.custom_command('list', 'logic_integration_account_map_list')
        g.custom_show_command('show', 'logic_integration_account_map_show')
        g.custom_command('create', 'logic_integration_account_map_create')
        g.generic_update_command('update')
        g.custom_command('delete', 'logic_integration_account_map_delete')
        g.custom_command('list-content-callback-url', 'logic_integration_account_map_list_content_callback_url')

    from ._client_factory import cf_integration_account_partner
    logic_integration_account_partner = CliCommandType(
        operations_tmpl='azext_logic.vendored_sdks.logic.operations._integration_account_partner_operations#IntegrationAccountPartnerOperations.{}',
        client_factory=cf_integration_account_partner)
    with self.command_group('logic integration-account-partner', logic_integration_account_partner, client_factory=cf_integration_account_partner) as g:
        g.custom_command('list', 'logic_integration_account_partner_list')
        g.custom_show_command('show', 'logic_integration_account_partner_show')
        g.custom_command('create', 'logic_integration_account_partner_create')
        g.generic_update_command('update')
        g.custom_command('delete', 'logic_integration_account_partner_delete')
        g.custom_command('list-content-callback-url', 'logic_integration_account_partner_list_content_callback_url')

    from ._client_factory import cf_integration_account_agreement
    logic_integration_account_agreement = CliCommandType(
        operations_tmpl='azext_logic.vendored_sdks.logic.operations._integration_account_agreement_operations#IntegrationAccountAgreementOperations.{}',
        client_factory=cf_integration_account_agreement)
    with self.command_group('logic integration-account-agreement', logic_integration_account_agreement, client_factory=cf_integration_account_agreement) as g:
        g.custom_command('list', 'logic_integration_account_agreement_list')
        g.custom_show_command('show', 'logic_integration_account_agreement_show')
        g.custom_command('create', 'logic_integration_account_agreement_create')
        g.generic_update_command('update')
        g.custom_command('delete', 'logic_integration_account_agreement_delete')
        g.custom_command('list-content-callback-url', 'logic_integration_account_agreement_list_content_callback_url')

    from ._client_factory import cf_integration_account_certificate
    logic_integration_account_certificate = CliCommandType(
        operations_tmpl='azext_logic.vendored_sdks.logic.operations._integration_account_certificate_operations#IntegrationAccountCertificateOperations.{}',
        client_factory=cf_integration_account_certificate)
    with self.command_group('logic integration-account-certificate', logic_integration_account_certificate, client_factory=cf_integration_account_certificate) as g:
        g.custom_command('list', 'logic_integration_account_certificate_list')
        g.custom_show_command('show', 'logic_integration_account_certificate_show')
        g.custom_command('create', 'logic_integration_account_certificate_create')
        g.generic_update_command('update')
        g.custom_command('delete', 'logic_integration_account_certificate_delete')

    from ._client_factory import cf_integration_account_session
    logic_integration_account_session = CliCommandType(
        operations_tmpl='azext_logic.vendored_sdks.logic.operations._integration_account_session_operations#IntegrationAccountSessionOperations.{}',
        client_factory=cf_integration_account_session)
    with self.command_group('logic integration-account-session', logic_integration_account_session, client_factory=cf_integration_account_session) as g:
        g.custom_command('list', 'logic_integration_account_session_list')
        g.custom_show_command('show', 'logic_integration_account_session_show')
        g.custom_command('create', 'logic_integration_account_session_create')
        g.generic_update_command('update')
        g.custom_command('delete', 'logic_integration_account_session_delete')

    from ._client_factory import cf_integration_service_environment
    logic_integration_service_environment = CliCommandType(
        operations_tmpl='azext_logic.vendored_sdks.logic.operations._integration_service_environment_operations#IntegrationServiceEnvironmentOperations.{}',
        client_factory=cf_integration_service_environment)
    with self.command_group('logic integration-service-environment', logic_integration_service_environment, client_factory=cf_integration_service_environment) as g:
        g.custom_command('list', 'logic_integration_service_environment_list')
        g.custom_show_command('show', 'logic_integration_service_environment_show')
        g.custom_command('create', 'logic_integration_service_environment_create', supports_no_wait=True)
        g.custom_command('update', 'logic_integration_service_environment_update', supports_no_wait=True)
        g.custom_command('delete', 'logic_integration_service_environment_delete')
        g.custom_command('restart', 'logic_integration_service_environment_restart')
        g.wait_command('wait');

    from ._client_factory import cf_integration_service_environment_sku
    logic_integration_service_environment_sku = CliCommandType(
        operations_tmpl='azext_logic.vendored_sdks.logic.operations._integration_service_environment_sku_operations#IntegrationServiceEnvironmentSkuOperations.{}',
        client_factory=cf_integration_service_environment_sku)
    with self.command_group('logic integration-service-environment-sku', logic_integration_service_environment_sku, client_factory=cf_integration_service_environment_sku) as g:
        g.custom_command('list', 'logic_integration_service_environment_sku_list')

    from ._client_factory import cf_integration_service_environment_network_health
    logic_integration_service_environment_network_health = CliCommandType(
        operations_tmpl='azext_logic.vendored_sdks.logic.operations._integration_service_environment_network_health_operations#IntegrationServiceEnvironmentNetworkHealthOperations.{}',
        client_factory=cf_integration_service_environment_network_health)
    with self.command_group('logic integration-service-environment-network-health', logic_integration_service_environment_network_health, client_factory=cf_integration_service_environment_network_health) as g:
        g.custom_show_command('show', 'logic_integration_service_environment_network_health_show')

    from ._client_factory import cf_integration_service_environment_managed_api
    logic_integration_service_environment_managed_api = CliCommandType(
        operations_tmpl='azext_logic.vendored_sdks.logic.operations._integration_service_environment_managed_api_operations#IntegrationServiceEnvironmentManagedApiOperations.{}',
        client_factory=cf_integration_service_environment_managed_api)
    with self.command_group('logic integration-service-environment-managed-api', logic_integration_service_environment_managed_api, client_factory=cf_integration_service_environment_managed_api) as g:
        g.custom_command('list', 'logic_integration_service_environment_managed_api_list')
        g.custom_show_command('show', 'logic_integration_service_environment_managed_api_show')
        g.custom_command('delete', 'logic_integration_service_environment_managed_api_delete', supports_no_wait=True)
        g.custom_command('put', 'logic_integration_service_environment_managed_api_put', supports_no_wait=True)
        g.wait_command('wait');

    from ._client_factory import cf_integration_service_environment_managed_api_operation
    logic_integration_service_environment_managed_api_operation = CliCommandType(
        operations_tmpl='azext_logic.vendored_sdks.logic.operations._integration_service_environment_managed_api_operation_operations#IntegrationServiceEnvironmentManagedApiOperationOperations.{}',
        client_factory=cf_integration_service_environment_managed_api_operation)
    with self.command_group('logic integration-service-environment-managed-api-operation', logic_integration_service_environment_managed_api_operation, client_factory=cf_integration_service_environment_managed_api_operation) as g:
        g.custom_command('list', 'logic_integration_service_environment_managed_api_operation_list')
