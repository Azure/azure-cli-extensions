# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):

    from azext_datafactory.generated._client_factory import cf_factory
    datafactory_factory = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._factory_operations#FactoryOperations.{}',
        client_factory=cf_factory)
    with self.command_group('datafactory factory', datafactory_factory, client_factory=cf_factory) as g:
        g.custom_command('list', 'datafactory_factory_list')
        g.custom_show_command('show', 'datafactory_factory_show')
        g.custom_command('create', 'datafactory_factory_create')
        g.custom_command('update', 'datafactory_factory_update')
        g.custom_command('delete', 'datafactory_factory_delete')
        g.custom_command('get-git-hub-access-token', 'datafactory_factory_get_git_hub_access_token')
        g.custom_command('get-data-plane-access', 'datafactory_factory_get_data_plane_access')
        g.custom_command('configure-factory-repo', 'datafactory_factory_configure_factory_repo')

    from azext_datafactory.generated._client_factory import cf_exposure_control
    datafactory_exposure_control = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._exposure_control_operations#ExposureControlOperations.{}',
        client_factory=cf_exposure_control)
    with self.command_group('datafactory exposure-control', datafactory_exposure_control, client_factory=cf_exposure_control) as g:
        g.custom_command('get-feature-value-by-factory', 'datafactory_exposure_control_get_feature_value_by_factory')
        g.custom_command('get-feature-value', 'datafactory_exposure_control_get_feature_value')

    from azext_datafactory.generated._client_factory import cf_integration_runtime
    datafactory_integration_runtime = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._integration_runtime_operations#IntegrationRuntimeOperations.{}',
        client_factory=cf_integration_runtime)
    with self.command_group('datafactory integration-runtime', datafactory_integration_runtime, client_factory=cf_integration_runtime) as g:
        g.custom_command('list', 'datafactory_integration_runtime_list')
        g.custom_show_command('show', 'datafactory_integration_runtime_show')
        g.custom_command('create', 'datafactory_integration_runtime_create')
        g.custom_command('update', 'datafactory_integration_runtime_update')
        g.custom_command('delete', 'datafactory_integration_runtime_delete')
        g.custom_command('get-status', 'datafactory_integration_runtime_get_status')
        g.custom_command('get-connection-info', 'datafactory_integration_runtime_get_connection_info')
        g.custom_command('regenerate-auth-key', 'datafactory_integration_runtime_regenerate_auth_key')
        g.custom_command('create-linked-integration-runtime', 'datafactory_integration_runtime_create_linked_integration_runtime')
        g.custom_command('start', 'datafactory_integration_runtime_start', supports_no_wait=True)
        g.custom_command('stop', 'datafactory_integration_runtime_stop', supports_no_wait=True)
        g.custom_command('sync-credentials', 'datafactory_integration_runtime_sync_credentials')
        g.custom_command('get-monitoring-data', 'datafactory_integration_runtime_get_monitoring_data')
        g.custom_command('upgrade', 'datafactory_integration_runtime_upgrade')
        g.custom_command('remove-link', 'datafactory_integration_runtime_remove_link')
        g.custom_command('list-auth-key', 'datafactory_integration_runtime_list_auth_key')
        g.wait_command('wait')

    from azext_datafactory.generated._client_factory import cf_integration_runtime_object_metadata
    datafactory_integration_runtime_object_metadata = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._integration_runtime_object_metadata_operations#IntegrationRuntimeObjectMetadataOperations.{}',
        client_factory=cf_integration_runtime_object_metadata)
    with self.command_group('datafactory integration-runtime-object-metadata', datafactory_integration_runtime_object_metadata, client_factory=cf_integration_runtime_object_metadata) as g:
        g.custom_command('refresh', 'datafactory_integration_runtime_object_metadata_refresh', supports_no_wait=True)
        g.custom_command('get', 'datafactory_integration_runtime_object_metadata_get')
        g.wait_command('wait')

    from azext_datafactory.generated._client_factory import cf_integration_runtime_node
    datafactory_integration_runtime_node = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._integration_runtime_node_operations#IntegrationRuntimeNodeOperations.{}',
        client_factory=cf_integration_runtime_node)
    with self.command_group('datafactory integration-runtime-node', datafactory_integration_runtime_node, client_factory=cf_integration_runtime_node) as g:
        g.custom_show_command('show', 'datafactory_integration_runtime_node_show')
        g.custom_command('update', 'datafactory_integration_runtime_node_update')
        g.custom_command('delete', 'datafactory_integration_runtime_node_delete')
        g.custom_command('get-ip-address', 'datafactory_integration_runtime_node_get_ip_address')

    from azext_datafactory.generated._client_factory import cf_linked_service
    datafactory_linked_service = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._linked_service_operations#LinkedServiceOperations.{}',
        client_factory=cf_linked_service)
    with self.command_group('datafactory linked-service', datafactory_linked_service, client_factory=cf_linked_service) as g:
        g.custom_command('list', 'datafactory_linked_service_list')
        g.custom_show_command('show', 'datafactory_linked_service_show')
        g.custom_command('create', 'datafactory_linked_service_create')
        g.generic_update_command('update')
        g.custom_command('delete', 'datafactory_linked_service_delete')

    from azext_datafactory.generated._client_factory import cf_dataset
    datafactory_dataset = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._dataset_operations#DatasetOperations.{}',
        client_factory=cf_dataset)
    with self.command_group('datafactory dataset', datafactory_dataset, client_factory=cf_dataset) as g:
        g.custom_command('list', 'datafactory_dataset_list')
        g.custom_show_command('show', 'datafactory_dataset_show')
        g.custom_command('create', 'datafactory_dataset_create')
        g.generic_update_command('update')
        g.custom_command('delete', 'datafactory_dataset_delete')

    from azext_datafactory.generated._client_factory import cf_pipeline
    datafactory_pipeline = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._pipeline_operations#PipelineOperations.{}',
        client_factory=cf_pipeline)
    with self.command_group('datafactory pipeline', datafactory_pipeline, client_factory=cf_pipeline) as g:
        g.custom_command('list', 'datafactory_pipeline_list')
        g.custom_show_command('show', 'datafactory_pipeline_show')
        g.custom_command('create', 'datafactory_pipeline_create')
        g.generic_update_command('update')
        g.custom_command('delete', 'datafactory_pipeline_delete')
        g.custom_command('create-run', 'datafactory_pipeline_create_run')

    from azext_datafactory.generated._client_factory import cf_pipeline_run
    datafactory_pipeline_run = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._pipeline_run_operations#PipelineRunOperations.{}',
        client_factory=cf_pipeline_run)
    with self.command_group('datafactory pipeline-run', datafactory_pipeline_run, client_factory=cf_pipeline_run) as g:
        g.custom_show_command('show', 'datafactory_pipeline_run_show')
        g.custom_command('cancel', 'datafactory_pipeline_run_cancel')
        g.custom_command('query-by-factory', 'datafactory_pipeline_run_query_by_factory')

    from azext_datafactory.generated._client_factory import cf_activity_run
    datafactory_activity_run = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._activity_run_operations#ActivityRunOperations.{}',
        client_factory=cf_activity_run)
    with self.command_group('datafactory activity-run', datafactory_activity_run, client_factory=cf_activity_run) as g:
        g.custom_command('query-by-pipeline-run', 'datafactory_activity_run_query_by_pipeline_run')

    from azext_datafactory.generated._client_factory import cf_trigger
    datafactory_trigger = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._trigger_operations#TriggerOperations.{}',
        client_factory=cf_trigger)
    with self.command_group('datafactory trigger', datafactory_trigger, client_factory=cf_trigger) as g:
        g.custom_command('list', 'datafactory_trigger_list')
        g.custom_show_command('show', 'datafactory_trigger_show')
        g.custom_command('create', 'datafactory_trigger_create')
        g.generic_update_command('update')
        g.custom_command('delete', 'datafactory_trigger_delete')
        g.custom_command('subscribe-to-event', 'datafactory_trigger_subscribe_to_event', supports_no_wait=True)
        g.custom_command('get-event-subscription-status', 'datafactory_trigger_get_event_subscription_status')
        g.custom_command('unsubscribe-from-event', 'datafactory_trigger_unsubscribe_from_event', supports_no_wait=True)
        g.custom_command('start', 'datafactory_trigger_start', supports_no_wait=True)
        g.custom_command('stop', 'datafactory_trigger_stop', supports_no_wait=True)
        g.custom_command('query-by-factory', 'datafactory_trigger_query_by_factory')
        g.wait_command('wait')

    from azext_datafactory.generated._client_factory import cf_trigger_run
    datafactory_trigger_run = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._trigger_run_operations#TriggerRunOperations.{}',
        client_factory=cf_trigger_run)
    with self.command_group('datafactory trigger-run', datafactory_trigger_run, client_factory=cf_trigger_run) as g:
        g.custom_command('rerun', 'datafactory_trigger_run_rerun')
        g.custom_command('query-by-factory', 'datafactory_trigger_run_query_by_factory')

    from azext_datafactory.generated._client_factory import cf_data_flow
    datafactory_data_flow = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._data_flow_operations#DataFlowOperations.{}',
        client_factory=cf_data_flow)
    with self.command_group('datafactory data-flow', datafactory_data_flow, client_factory=cf_data_flow) as g:
        g.custom_command('list', 'datafactory_data_flow_list')
        g.custom_show_command('show', 'datafactory_data_flow_show')
        g.custom_command('create', 'datafactory_data_flow_create')
        g.generic_update_command('update')
        g.custom_command('delete', 'datafactory_data_flow_delete')

    from azext_datafactory.generated._client_factory import cf_data_flow_debug_session
    datafactory_data_flow_debug_session = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._data_flow_debug_session_operations#DataFlowDebugSessionOperations.{}',
        client_factory=cf_data_flow_debug_session)
    with self.command_group('datafactory data-flow-debug-session', datafactory_data_flow_debug_session, client_factory=cf_data_flow_debug_session) as g:
        g.custom_command('create', 'datafactory_data_flow_debug_session_create', supports_no_wait=True)
        g.custom_command('delete', 'datafactory_data_flow_debug_session_delete')
        g.custom_command('query-by-factory', 'datafactory_data_flow_debug_session_query_by_factory')
        g.custom_command('add-data-flow', 'datafactory_data_flow_debug_session_add_data_flow')
        g.custom_command('execute-command', 'datafactory_data_flow_debug_session_execute_command', supports_no_wait=True)
        g.wait_command('wait')
