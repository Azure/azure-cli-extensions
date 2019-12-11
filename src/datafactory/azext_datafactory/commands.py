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
    with self.command_group('datafactory', datafactory_operations, client_factory=cf_operations) as g:
        g.custom_command('list', 'list_datafactory')

    from ._client_factory import cf_factories
    datafactory_factories = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._factories_operations#FactoriesOperations.{}',
        client_factory=cf_factories)
    with self.command_group('datafactory', datafactory_factories, client_factory=cf_factories) as g:
        g.custom_command('create', 'create_datafactory')
        g.custom_command('update', 'update_datafactory')
        g.custom_command('delete', 'delete_datafactory')
        g.custom_command('show', 'get_datafactory')
        g.custom_command('list', 'list_datafactory')
        g.custom_command('configure_factory_repo', 'configure_factory_repo_datafactory')
        g.custom_command('get_git_hub_access_token', 'get_git_hub_access_token_datafactory')
        g.custom_command('get_data_plane_access', 'get_data_plane_access_datafactory')

    from ._client_factory import cf_exposure_control
    datafactory_exposure_control = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._exposure_control_operations#ExposureControlOperations.{}',
        client_factory=cf_exposure_control)
    with self.command_group('datafactory get-feature-value', datafactory_exposure_control, client_factory=cf_exposure_control) as g:
        g.custom_command('get_feature_value', 'get_feature_value_datafactory_get_feature_value')
        g.custom_command('get_feature_value_by_factory', 'get_feature_value_by_factory_datafactory_get_feature_value')

    from ._client_factory import cf_integration_runtimes
    datafactory_integration_runtimes = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._integration_runtimes_operations#IntegrationRuntimesOperations.{}',
        client_factory=cf_integration_runtimes)
    with self.command_group('datafactory integration-runtime', datafactory_integration_runtimes, client_factory=cf_integration_runtimes) as g:
        g.custom_command('create', 'create_datafactory_integration_runtime')
        g.custom_command('update', 'update_datafactory_integration_runtime')
        g.custom_command('delete', 'delete_datafactory_integration_runtime')
        g.custom_command('show', 'get_datafactory_integration_runtime')
        g.custom_command('list', 'list_datafactory_integration_runtime')
        g.custom_command('get_status', 'get_status_datafactory_integration_runtime')
        g.custom_command('get_connection_info', 'get_connection_info_datafactory_integration_runtime')
        g.custom_command('regenerate_auth_key', 'regenerate_auth_key_datafactory_integration_runtime')
        g.custom_command('create_linked_integration_runtime', 'create_linked_integration_runtime_datafactory_integration_runtime')
        g.custom_command('start', 'start_datafactory_integration_runtime')
        g.custom_command('stop', 'stop_datafactory_integration_runtime')
        g.custom_command('sync_credentials', 'sync_credentials_datafactory_integration_runtime')
        g.custom_command('get_monitoring_data', 'get_monitoring_data_datafactory_integration_runtime')
        g.custom_command('upgrade', 'upgrade_datafactory_integration_runtime')
        g.custom_command('remove_links', 'remove_links_datafactory_integration_runtime')
        g.custom_command('list_auth_keys', 'list_auth_keys_datafactory_integration_runtime')

    from ._client_factory import cf_integration_runtime_object_metadata
    datafactory_integration_runtime_object_metadata = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._integration_runtime_object_metadata_operations#IntegrationRuntimeObjectMetadataOperations.{}',
        client_factory=cf_integration_runtime_object_metadata)
    with self.command_group('datafactory integration-runtime refresh-object-metadata', datafactory_integration_runtime_object_metadata, client_factory=cf_integration_runtime_object_metadata) as g:
        g.custom_command('refresh', 'refresh_datafactory_integration_runtime_refresh_object_metadata')
        g.custom_command('get', 'get_datafactory_integration_runtime_refresh_object_metadata')

    from ._client_factory import cf_integration_runtime_nodes
    datafactory_integration_runtime_nodes = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._integration_runtime_nodes_operations#IntegrationRuntimeNodesOperations.{}',
        client_factory=cf_integration_runtime_nodes)
    with self.command_group('datafactory integration-runtime node', datafactory_integration_runtime_nodes, client_factory=cf_integration_runtime_nodes) as g:
        g.custom_command('update', 'update_datafactory_integration_runtime_node')
        g.custom_command('delete', 'delete_datafactory_integration_runtime_node')
        g.custom_command('show', 'get_datafactory_integration_runtime_node')
        g.custom_command('get_ip_address', 'get_ip_address_datafactory_integration_runtime_node')

    from ._client_factory import cf_linked_services
    datafactory_linked_services = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._linked_services_operations#LinkedServicesOperations.{}',
        client_factory=cf_linked_services)
    with self.command_group('datafactory linkedservice', datafactory_linked_services, client_factory=cf_linked_services) as g:
        g.custom_command('create', 'create_datafactory_linkedservice')
        g.custom_command('update', 'update_datafactory_linkedservice')
        g.custom_command('delete', 'delete_datafactory_linkedservice')
        g.custom_command('show', 'get_datafactory_linkedservice')
        g.custom_command('list', 'list_datafactory_linkedservice')

    from ._client_factory import cf_datasets
    datafactory_datasets = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._datasets_operations#DatasetsOperations.{}',
        client_factory=cf_datasets)
    with self.command_group('datafactory dataset', datafactory_datasets, client_factory=cf_datasets) as g:
        g.custom_command('create', 'create_datafactory_dataset')
        g.custom_command('update', 'update_datafactory_dataset')
        g.custom_command('delete', 'delete_datafactory_dataset')
        g.custom_command('show', 'get_datafactory_dataset')
        g.custom_command('list', 'list_datafactory_dataset')

    from ._client_factory import cf_pipelines
    datafactory_pipelines = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._pipelines_operations#PipelinesOperations.{}',
        client_factory=cf_pipelines)
    with self.command_group('datafactory pipeline', datafactory_pipelines, client_factory=cf_pipelines) as g:
        g.custom_command('create', 'create_datafactory_pipeline')
        g.custom_command('update', 'update_datafactory_pipeline')
        g.custom_command('delete', 'delete_datafactory_pipeline')
        g.custom_command('show', 'get_datafactory_pipeline')
        g.custom_command('list', 'list_datafactory_pipeline')
        g.custom_command('create_run', 'create_run_datafactory_pipeline')

    from ._client_factory import cf_pipeline_runs
    datafactory_pipeline_runs = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._pipeline_runs_operations#PipelineRunsOperations.{}',
        client_factory=cf_pipeline_runs)
    with self.command_group('datafactory query-pipeline-run', datafactory_pipeline_runs, client_factory=cf_pipeline_runs) as g:
        g.custom_command('query_by_factory', 'query_by_factory_datafactory_query_pipeline_run')
        g.custom_command('cancel', 'cancel_datafactory_query_pipeline_run')
        g.custom_command('get', 'get_datafactory_query_pipeline_run')

    from ._client_factory import cf_activity_runs
    datafactory_activity_runs = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._activity_runs_operations#ActivityRunsOperations.{}',
        client_factory=cf_activity_runs)
    with self.command_group('datafactory pipelinerun query-activityrun', datafactory_activity_runs, client_factory=cf_activity_runs) as g:
        g.custom_command('query_by_pipeline_run', 'query_by_pipeline_run_datafactory_pipelinerun_query_activityrun')

    from ._client_factory import cf_triggers
    datafactory_triggers = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._triggers_operations#TriggersOperations.{}',
        client_factory=cf_triggers)
    with self.command_group('datafactory trigger', datafactory_triggers, client_factory=cf_triggers) as g:
        g.custom_command('create', 'create_datafactory_trigger')
        g.custom_command('update', 'update_datafactory_trigger')
        g.custom_command('delete', 'delete_datafactory_trigger')
        g.custom_command('show', 'get_datafactory_trigger')
        g.custom_command('list', 'list_datafactory_trigger')
        g.custom_command('subscribe_to_events', 'subscribe_to_events_datafactory_trigger')
        g.custom_command('get_event_subscription_status', 'get_event_subscription_status_datafactory_trigger')
        g.custom_command('unsubscribe_from_events', 'unsubscribe_from_events_datafactory_trigger')
        g.custom_command('start', 'start_datafactory_trigger')
        g.custom_command('stop', 'stop_datafactory_trigger')

    from ._client_factory import cf_trigger_runs
    datafactory_trigger_runs = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._trigger_runs_operations#TriggerRunsOperations.{}',
        client_factory=cf_trigger_runs)
    with self.command_group('datafactory trigger trigger-run rerun', datafactory_trigger_runs, client_factory=cf_trigger_runs) as g:
        g.custom_command('rerun', 'rerun_datafactory_trigger_trigger_run_rerun')
        g.custom_command('query_by_factory', 'query_by_factory_datafactory_trigger_trigger_run_rerun')

    from ._client_factory import cf_rerun_triggers
    datafactory_rerun_triggers = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._rerun_triggers_operations#RerunTriggersOperations.{}',
        client_factory=cf_rerun_triggers)
    with self.command_group('datafactory trigger rerun-trigger', datafactory_rerun_triggers, client_factory=cf_rerun_triggers) as g:
        g.custom_command('create', 'create_datafactory_trigger_rerun_trigger')
        g.custom_command('update', 'update_datafactory_trigger_rerun_trigger')
        g.custom_command('list', 'list_datafactory_trigger_rerun_trigger')
        g.custom_command('start', 'start_datafactory_trigger_rerun_trigger')
        g.custom_command('stop', 'stop_datafactory_trigger_rerun_trigger')
        g.custom_command('cancel', 'cancel_datafactory_trigger_rerun_trigger')

    from ._client_factory import cf_data_flows
    datafactory_data_flows = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._data_flows_operations#DataFlowsOperations.{}',
        client_factory=cf_data_flows)
    with self.command_group('datafactory dataflow', datafactory_data_flows, client_factory=cf_data_flows) as g:
        g.custom_command('create', 'create_datafactory_dataflow')
        g.custom_command('update', 'update_datafactory_dataflow')
        g.custom_command('delete', 'delete_datafactory_dataflow')
        g.custom_command('show', 'get_datafactory_dataflow')
        g.custom_command('list', 'list_datafactory_dataflow')

    from ._client_factory import cf_data_flow_debug_session
    datafactory_data_flow_debug_session = CliCommandType(
        operations_tmpl='azext_datafactory.vendored_sdks.datafactory.operations._data_flow_debug_session_operations#DataFlowDebugSessionOperations.{}',
        client_factory=cf_data_flow_debug_session)
    with self.command_group('datafactory create-data-flow-debug-session', datafactory_data_flow_debug_session, client_factory=cf_data_flow_debug_session) as g:
        g.custom_command('create', 'create_datafactory_create_data_flow_debug_session')
        g.custom_command('query_by_factory', 'query_by_factory_datafactory_create_data_flow_debug_session')
        g.custom_command('add_data_flow', 'add_data_flow_datafactory_create_data_flow_debug_session')
        g.custom_command('delete', 'delete_datafactory_create_data_flow_debug_session')
        g.custom_command('execute_command', 'execute_command_datafactory_create_data_flow_debug_session')
