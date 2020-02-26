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

    from ._client_factory import cf_operations
    datafactory_operations = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._operations_operations#OperationsOperations.{}',
        client_factory=cf_operations)
    with self.command_group('datafactory operations', datafactory_operations, client_factory=cf_operations) as g:
        g.custom_command('list', 'datafactory_operations_list')

    from ._client_factory import cf_factories
    datafactory_factories = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._factories_operations#FactoriesOperations.{}',
        client_factory=cf_factories)
    with self.command_group('datafactory factories', datafactory_factories, client_factory=cf_factories) as g:
        g.custom_command('list', 'datafactory_factories_list')
        g.custom_show_command('show', 'datafactory_factories_show')
        g.custom_command('create', 'datafactory_factories_create')
        g.custom_command('update', 'datafactory_factories_update')
        g.custom_command('delete', 'datafactory_factories_delete')
        g.custom_command('configure-factory-repo', 'datafactory_factories_configure_factory_repo')
        g.custom_command('get-data-plane-access', 'datafactory_factories_get_data_plane_access')
        g.custom_command('get-git-hub-access-token', 'datafactory_factories_get_git_hub_access_token')

    from ._client_factory import cf_exposure_control
    datafactory_exposure_control = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._exposure_control_operations#ExposureControlOperations.{}',
        client_factory=cf_exposure_control)
    with self.command_group('datafactory exposure-control', datafactory_exposure_control, client_factory=cf_exposure_control) as g:
        g.custom_command('get-feature-value-by-factory', 'datafactory_exposure_control_get_feature_value_by_factory')
        g.custom_command('get-feature-value', 'datafactory_exposure_control_get_feature_value')

    from ._client_factory import cf_integration_runtimes
    datafactory_integration_runtimes = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._integration_runtimes_operations#IntegrationRuntimesOperations.{}',
        client_factory=cf_integration_runtimes)
    with self.command_group('datafactory integration-runtimes', datafactory_integration_runtimes, client_factory=cf_integration_runtimes) as g:
        g.custom_command('list', 'datafactory_integration_runtimes_list')
        g.custom_show_command('show', 'datafactory_integration_runtimes_show')
        g.custom_command('create', 'datafactory_integration_runtimes_create')
        g.custom_command('update', 'datafactory_integration_runtimes_update')
        g.custom_command('delete', 'datafactory_integration_runtimes_delete')
        g.custom_command('create-linked-integration-runtime', 'datafactory_integration_runtimes_create_linked_integration_runtime')
        g.custom_command('regenerate-auth-key', 'datafactory_integration_runtimes_regenerate_auth_key')
        g.custom_command('remove-links', 'datafactory_integration_runtimes_remove_links')
        g.custom_command('get-status', 'datafactory_integration_runtimes_get_status')
        g.custom_command('get-connection-info', 'datafactory_integration_runtimes_get_connection_info')
        g.custom_command('list-auth-keys', 'datafactory_integration_runtimes_list_auth_keys')
        g.custom_command('start', 'datafactory_integration_runtimes_start')
        g.custom_command('stop', 'datafactory_integration_runtimes_stop')
        g.custom_command('sync-credentials', 'datafactory_integration_runtimes_sync_credentials')
        g.custom_command('get-monitoring-data', 'datafactory_integration_runtimes_get_monitoring_data')
        g.custom_command('upgrade', 'datafactory_integration_runtimes_upgrade')

    from ._client_factory import cf_integration_runtime_object_metadata
    datafactory_integration_runtime_object_metadata = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._integration_runtime_object_metadata_operations#IntegrationRuntimeObjectMetadataOperations.{}',
        client_factory=cf_integration_runtime_object_metadata)
    with self.command_group('datafactory integration-runtime-object-metadata', datafactory_integration_runtime_object_metadata, client_factory=cf_integration_runtime_object_metadata) as g:
        g.custom_command('get', 'datafactory_integration_runtime_object_metadata_get')
        g.custom_command('refresh', 'datafactory_integration_runtime_object_metadata_refresh')

    from ._client_factory import cf_integration_runtime_nodes
    datafactory_integration_runtime_nodes = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._integration_runtime_nodes_operations#IntegrationRuntimeNodesOperations.{}',
        client_factory=cf_integration_runtime_nodes)
    with self.command_group('datafactory integration-runtime-nodes', datafactory_integration_runtime_nodes, client_factory=cf_integration_runtime_nodes) as g:
        g.custom_show_command('show', 'datafactory_integration_runtime_nodes_show')
        g.custom_command('update', 'datafactory_integration_runtime_nodes_update')
        g.custom_command('delete', 'datafactory_integration_runtime_nodes_delete')
        g.custom_command('get-ip-address', 'datafactory_integration_runtime_nodes_get_ip_address')

    from ._client_factory import cf_linked_services
    datafactory_linked_services = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._linked_services_operations#LinkedServicesOperations.{}',
        client_factory=cf_linked_services)
    with self.command_group('datafactory linked-services', datafactory_linked_services, client_factory=cf_linked_services) as g:
        g.custom_command('list', 'datafactory_linked_services_list')
        g.custom_show_command('show', 'datafactory_linked_services_show')
        g.custom_command('create', 'datafactory_linked_services_create')
        g.custom_command('update', 'datafactory_linked_services_update')
        g.custom_command('delete', 'datafactory_linked_services_delete')

    from ._client_factory import cf_datasets
    datafactory_datasets = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._datasets_operations#DatasetsOperations.{}',
        client_factory=cf_datasets)
    with self.command_group('datafactory datasets', datafactory_datasets, client_factory=cf_datasets) as g:
        g.custom_command('list', 'datafactory_datasets_list')
        g.custom_show_command('show', 'datafactory_datasets_show')
        g.custom_command('create', 'datafactory_datasets_create')
        g.custom_command('update', 'datafactory_datasets_update')
        g.custom_command('delete', 'datafactory_datasets_delete')

    from ._client_factory import cf_pipelines
    datafactory_pipelines = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._pipelines_operations#PipelinesOperations.{}',
        client_factory=cf_pipelines)
    with self.command_group('datafactory pipelines', datafactory_pipelines, client_factory=cf_pipelines) as g:
        g.custom_command('list', 'datafactory_pipelines_list')
        g.custom_show_command('show', 'datafactory_pipelines_show')
        g.custom_command('create', 'datafactory_pipelines_create')
        g.custom_command('update', 'datafactory_pipelines_update')
        g.custom_command('delete', 'datafactory_pipelines_delete')
        g.custom_command('create-run', 'datafactory_pipelines_create_run')

    from ._client_factory import cf_pipeline_runs
    datafactory_pipeline_runs = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._pipeline_runs_operations#PipelineRunsOperations.{}',
        client_factory=cf_pipeline_runs)
    with self.command_group('datafactory pipeline-runs', datafactory_pipeline_runs, client_factory=cf_pipeline_runs) as g:
        g.custom_show_command('show', 'datafactory_pipeline_runs_show')
        g.custom_command('query-by-factory', 'datafactory_pipeline_runs_query_by_factory')
        g.custom_command('cancel', 'datafactory_pipeline_runs_cancel')

    from ._client_factory import cf_activity_runs
    datafactory_activity_runs = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._activity_runs_operations#ActivityRunsOperations.{}',
        client_factory=cf_activity_runs)
    with self.command_group('datafactory activity-runs', datafactory_activity_runs, client_factory=cf_activity_runs) as g:
        g.custom_command('query-by-pipeline-run', 'datafactory_activity_runs_query_by_pipeline_run')

    from ._client_factory import cf_triggers
    datafactory_triggers = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._triggers_operations#TriggersOperations.{}',
        client_factory=cf_triggers)
    with self.command_group('datafactory triggers', datafactory_triggers, client_factory=cf_triggers) as g:
        g.custom_command('list', 'datafactory_triggers_list')
        g.custom_show_command('show', 'datafactory_triggers_show')
        g.custom_command('create', 'datafactory_triggers_create')
        g.custom_command('update', 'datafactory_triggers_update')
        g.custom_command('delete', 'datafactory_triggers_delete')
        g.custom_command('query-by-factory', 'datafactory_triggers_query_by_factory')
        g.custom_command('subscribe-to-events', 'datafactory_triggers_subscribe_to_events')
        g.custom_command('get-event-subscription-status', 'datafactory_triggers_get_event_subscription_status')
        g.custom_command('unsubscribe-from-events', 'datafactory_triggers_unsubscribe_from_events')
        g.custom_command('start', 'datafactory_triggers_start')
        g.custom_command('stop', 'datafactory_triggers_stop')

    from ._client_factory import cf_trigger_runs
    datafactory_trigger_runs = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._trigger_runs_operations#TriggerRunsOperations.{}',
        client_factory=cf_trigger_runs)
    with self.command_group('datafactory trigger-runs', datafactory_trigger_runs, client_factory=cf_trigger_runs) as g:
        g.custom_command('query-by-factory', 'datafactory_trigger_runs_query_by_factory')
        g.custom_command('rerun', 'datafactory_trigger_runs_rerun')

    from ._client_factory import cf_data_flows
    datafactory_data_flows = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._data_flows_operations#DataFlowsOperations.{}',
        client_factory=cf_data_flows)
    with self.command_group('datafactory data-flows', datafactory_data_flows, client_factory=cf_data_flows) as g:
        g.custom_command('list', 'datafactory_data_flows_list')
        g.custom_show_command('show', 'datafactory_data_flows_show')
        g.custom_command('create', 'datafactory_data_flows_create')
        g.custom_command('update', 'datafactory_data_flows_update')
        g.custom_command('delete', 'datafactory_data_flows_delete')

    from ._client_factory import cf_data_flow_debug_session
    datafactory_data_flow_debug_session = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._data_flow_debug_session_operations#DataFlowDebugSessionOperations.{}',
        client_factory=cf_data_flow_debug_session)
    with self.command_group('datafactory data-flow-debug-session', datafactory_data_flow_debug_session, client_factory=cf_data_flow_debug_session) as g:
        g.custom_command('create', 'datafactory_data_flow_debug_session_create')
        g.custom_command('delete', 'datafactory_data_flow_debug_session_delete')
        g.custom_command('add-data-flow', 'datafactory_data_flow_debug_session_add_data_flow')
        g.custom_command('execute-command', 'datafactory_data_flow_debug_session_execute_command')
        g.custom_command('query-by-factory', 'datafactory_data_flow_debug_session_query_by_factory')
