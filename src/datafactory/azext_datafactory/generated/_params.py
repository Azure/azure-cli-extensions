# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from azure.cli.core.commands.parameters import (
    tags_type,
    get_three_state_flag,
    get_enum_type,
    resource_group_name_type,
    get_location_type
)
from azext_datafactory.action import (
    AddActivities,
    AddAnnotations,
    AddFilters,
    AddOrderBy,
    AddDatasets,
    AddLinkedServices
)


def load_arguments(self, _):

    with self.argument_context('datafactory factory list') as c:
        c.argument('resource_group_name', resource_group_name_type)

    with self.argument_context('datafactory factory show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')

    with self.argument_context('datafactory factory create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)
        c.argument('factory_identity', help='Identity properties of the factory resource.')
        c.argument('factory_repo_configuration', help='Factory\'s git repo information.')

    with self.argument_context('datafactory factory update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('tags', tags_type)
        c.argument('factory_update_parameters_identity', help='Identity properties of the factory resource.')

    with self.argument_context('datafactory factory delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')

    with self.argument_context('datafactory factory get-data-plane-access') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('policy_permissions', help='The string with permissions for Data Plane access. Currently only \'r\' is supported which grants read only access.')
        c.argument('policy_access_resource_path', help='The resource path to get access relative to factory. Currently only empty string is supported which corresponds to the factory resource.')
        c.argument('policy_profile_name', help='The name of the profile. Currently only the default is supported. The default value is DefaultProfile.')
        c.argument('policy_start_time', help='Start time for the token. If not specified the current time will be used.')
        c.argument('policy_expire_time', help='Expiration time for the token. Maximum duration for the token is eight hours and by default the token will expire in eight hours.')

    with self.argument_context('datafactory factory get-git-hub-access-token') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('git_hub_access_token_request_git_hub_access_code', help='GitHub access code.')
        c.argument('git_hub_access_token_request_git_hub_client_id', help='GitHub application client ID.')
        c.argument('git_hub_access_token_request_git_hub_access_token_base_url', help='GitHub access token base URL.')

    with self.argument_context('datafactory factory configure-factory-repo') as c:
        c.argument('location_id', help='The location identifier.')
        c.argument('factory_repo_update_factory_resource_id', help='The factory resource id.')
        c.argument('factory_repo_update_repo_configuration', help='Factory\'s git repo information.')

    with self.argument_context('datafactory exposure-control get-feature-value-by-factory') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('exposure_control_request_feature_name', help='The feature name.')
        c.argument('exposure_control_request_feature_type', help='The feature type.')

    with self.argument_context('datafactory exposure-control get-feature-value') as c:
        c.argument('location_id', help='The location identifier.')
        c.argument('exposure_control_request_feature_name', help='The feature name.')
        c.argument('exposure_control_request_feature_type', help='The feature type.')

    with self.argument_context('datafactory integration-runtime list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')

    with self.argument_context('datafactory integration-runtime show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtime create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')
        c.argument('integration_runtime_properties', help='Azure Data Factory nested object which serves as a compute resource for activities.')

    with self.argument_context('datafactory integration-runtime update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')
        c.argument('update_integration_runtime_request_auto_update', arg_type=get_enum_type(['On', 'Off']), help='The state of integration runtime auto update.')
        c.argument('update_integration_runtime_request_update_delay_offset', help='The time offset (in hours) in the day, e.g., PT03H is 3 hours. The integration runtime auto update will happen on that time.')

    with self.argument_context('datafactory integration-runtime delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtime create-linked-integration-runtime') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')
        c.argument('create_linked_integration_runtime_request_name', help='The name of the linked integration runtime.')
        c.argument('create_linked_integration_runtime_request_data_factory_name', help='The name of the data factory that the linked integration runtime belongs to.')
        c.argument('create_linked_integration_runtime_request_data_factory_location', help='The location of the data factory that the linked integration runtime belongs to.')

    with self.argument_context('datafactory integration-runtime regenerate-auth-key') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')
        c.argument('regenerate_key_parameters_key_name', arg_type=get_enum_type(['authKey1', 'authKey2']), help='The name of the authentication key to regenerate.')

    with self.argument_context('datafactory integration-runtime remove-link') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')
        c.argument('linked_integration_runtime_request_linked_factory_name', help='The data factory name for linked integration runtime.')

    with self.argument_context('datafactory integration-runtime get-status') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtime get-connection-info') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtime list-auth-key') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtime start') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtime stop') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtime sync-credentials') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtime get-monitoring-data') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtime upgrade') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtime-object-metadata get') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')
        c.argument('get_metadata_request_metadata_path', help='Metadata path.')

    with self.argument_context('datafactory integration-runtime-object-metadata refresh') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtime-node show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')
        c.argument('node_name', help='The integration runtime node name.')

    with self.argument_context('datafactory integration-runtime-node update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')
        c.argument('node_name', help='The integration runtime node name.')
        c.argument('update_integration_runtime_node_request_concurrent_jobs_limit', help='The number of concurrent jobs permitted to run on the integration runtime node. Values between 1 and maxConcurrentJobs(inclusive) are allowed.')

    with self.argument_context('datafactory integration-runtime-node delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')
        c.argument('node_name', help='The integration runtime node name.')

    with self.argument_context('datafactory integration-runtime-node get-ip-address') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')
        c.argument('node_name', help='The integration runtime node name.')

    with self.argument_context('datafactory linked-service list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')

    with self.argument_context('datafactory linked-service show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('linked_service_name', help='The linked service name.')

    with self.argument_context('datafactory linked-service create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('linked_service_name', help='The linked service name.')
        c.argument('linked_service_properties', help='The Azure Data Factory nested object which contains the information and credential which can be used to connect with related store or compute resource.')

    with self.argument_context('datafactory linked-service update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('linked_service_name', help='The linked service name.')
        c.argument('linked_service_properties', help='The Azure Data Factory nested object which contains the information and credential which can be used to connect with related store or compute resource.')

    with self.argument_context('datafactory linked-service delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('linked_service_name', help='The linked service name.')

    with self.argument_context('datafactory dataset list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')

    with self.argument_context('datafactory dataset show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('dataset_name', help='The dataset name.')

    with self.argument_context('datafactory dataset create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('dataset_name', help='The dataset name.')
        c.argument('dataset_properties', help='The Azure Data Factory nested object which identifies data within different data stores, such as tables, files, folders, and documents.')

    with self.argument_context('datafactory dataset update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('dataset_name', help='The dataset name.')
        c.argument('dataset_properties', help='The Azure Data Factory nested object which identifies data within different data stores, such as tables, files, folders, and documents.')

    with self.argument_context('datafactory dataset delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('dataset_name', help='The dataset name.')

    with self.argument_context('datafactory pipeline list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')

    with self.argument_context('datafactory pipeline show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('pipeline_name', help='The pipeline name.')

    with self.argument_context('datafactory pipeline create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('pipeline_name', help='The pipeline name.')
        c.argument('pipeline_description', help='The description of the pipeline.')
        c.argument('pipeline_activities', help='List of activities in pipeline.', action=AddActivities, nargs='+')
        c.argument('pipeline_parameters', help='Definition of all parameters for an entity.')
        c.argument('pipeline_variables', help='Definition of variable for a Pipeline.')
        c.argument('pipeline_concurrency', help='The max number of concurrent runs for the pipeline.')
        c.argument('pipeline_annotations', help='List of tags that can be used for describing the Pipeline.', action=AddAnnotations, nargs='+')
        c.argument('pipeline_run_dimensions', help='Dimensions emitted by Pipeline.')
        c.argument('pipeline_folder', help='The folder that this Pipeline is in. If not specified, Pipeline will appear at the root level.')

    with self.argument_context('datafactory pipeline update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('pipeline_name', help='The pipeline name.')
        c.argument('pipeline_description', help='The description of the pipeline.')
        c.argument('pipeline_activities', help='List of activities in pipeline.', action=AddActivities, nargs='+')
        c.argument('pipeline_parameters', help='Definition of all parameters for an entity.')
        c.argument('pipeline_variables', help='Definition of variable for a Pipeline.')
        c.argument('pipeline_concurrency', help='The max number of concurrent runs for the pipeline.')
        c.argument('pipeline_annotations', help='List of tags that can be used for describing the Pipeline.', action=AddAnnotations, nargs='+')
        c.argument('pipeline_run_dimensions', help='Dimensions emitted by Pipeline.')
        c.argument('pipeline_folder', help='The folder that this Pipeline is in. If not specified, Pipeline will appear at the root level.')

    with self.argument_context('datafactory pipeline delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('pipeline_name', help='The pipeline name.')

    with self.argument_context('datafactory pipeline create-run') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('pipeline_name', help='The pipeline name.')
        c.argument('reference_pipeline_run_id', help='The pipeline run identifier. If run ID is specified the parameters of the specified run will be used to create a new run.')
        c.argument('is_recovery', arg_type=get_three_state_flag(), help='Recovery mode flag. If recovery mode is set to true, the specified referenced pipeline run and the new run will be grouped under the same groupId.')
        c.argument('start_activity_name', help='In recovery mode, the rerun will start from this activity. If not specified, all activities will run.')
        c.argument('start_from_failure', arg_type=get_three_state_flag(), help='In recovery mode, if set to true, the rerun will start from failed activities. The property will be used only if startActivityName is not specified.')
        c.argument('parameters', help='Parameters of the pipeline run. These parameters will be used only if the runId is not specified.')

    with self.argument_context('datafactory pipeline-run show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('run_id', help='The pipeline run identifier.')

    with self.argument_context('datafactory pipeline-run query-by-factory') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('filter_parameters_continuation_token', help='The continuation token for getting the next page of results. Null for first page.')
        c.argument('filter_parameters_last_updated_after', help='The time at or after which the run event was updated in \'ISO 8601\' format.')
        c.argument('filter_parameters_last_updated_before', help='The time at or before which the run event was updated in \'ISO 8601\' format.')
        c.argument('filter_parameters_filters', help='List of filters.', action=AddFilters, nargs='+')
        c.argument('filter_parameters_order_by', help='List of OrderBy option.', action=AddOrderBy, nargs='+')

    with self.argument_context('datafactory pipeline-run cancel') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('run_id', help='The pipeline run identifier.')
        c.argument('is_recursive', arg_type=get_three_state_flag(), help='If true, cancel all the Child pipelines that are triggered by the current pipeline.')

    with self.argument_context('datafactory activity-run query-by-pipeline-run') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('run_id', help='The pipeline run identifier.')
        c.argument('filter_parameters_continuation_token', help='The continuation token for getting the next page of results. Null for first page.')
        c.argument('filter_parameters_last_updated_after', help='The time at or after which the run event was updated in \'ISO 8601\' format.')
        c.argument('filter_parameters_last_updated_before', help='The time at or before which the run event was updated in \'ISO 8601\' format.')
        c.argument('filter_parameters_filters', help='List of filters.', action=AddFilters, nargs='+')
        c.argument('filter_parameters_order_by', help='List of OrderBy option.', action=AddOrderBy, nargs='+')

    with self.argument_context('datafactory trigger list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')

    with self.argument_context('datafactory trigger show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('trigger_name', help='The trigger name.')

    with self.argument_context('datafactory trigger create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('trigger_name', help='The trigger name.')
        c.argument('trigger_properties', help='Azure data factory nested object which contains information about creating pipeline run')

    with self.argument_context('datafactory trigger update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('trigger_name', help='The trigger name.')
        c.argument('trigger_properties', help='Azure data factory nested object which contains information about creating pipeline run')

    with self.argument_context('datafactory trigger delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('trigger_name', help='The trigger name.')

    with self.argument_context('datafactory trigger query-by-factory') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('filter_parameters_continuation_token', help='The continuation token for getting the next page of results. Null for first page.')
        c.argument('filter_parameters_parent_trigger_name', help='The name of the parent TumblingWindowTrigger to get the child rerun triggers')

    with self.argument_context('datafactory trigger subscribe-to-event') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('trigger_name', help='The trigger name.')

    with self.argument_context('datafactory trigger get-event-subscription-status') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('trigger_name', help='The trigger name.')

    with self.argument_context('datafactory trigger unsubscribe-from-event') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('trigger_name', help='The trigger name.')

    with self.argument_context('datafactory trigger start') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('trigger_name', help='The trigger name.')

    with self.argument_context('datafactory trigger stop') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('trigger_name', help='The trigger name.')

    with self.argument_context('datafactory trigger-run query-by-factory') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('filter_parameters_continuation_token', help='The continuation token for getting the next page of results. Null for first page.')
        c.argument('filter_parameters_last_updated_after', help='The time at or after which the run event was updated in \'ISO 8601\' format.')
        c.argument('filter_parameters_last_updated_before', help='The time at or before which the run event was updated in \'ISO 8601\' format.')
        c.argument('filter_parameters_filters', help='List of filters.', action=AddFilters, nargs='+')
        c.argument('filter_parameters_order_by', help='List of OrderBy option.', action=AddOrderBy, nargs='+')

    with self.argument_context('datafactory trigger-run rerun') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('trigger_name', help='The trigger name.')
        c.argument('run_id', help='The pipeline run identifier.')

    with self.argument_context('datafactory data-flow list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')

    with self.argument_context('datafactory data-flow show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('data_flow_name', help='The data flow name.')

    with self.argument_context('datafactory data-flow create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('data_flow_name', help='The data flow name.')
        c.argument('data_flow_properties', help='Azure Data Factory nested object which contains a flow with data movements and transformations.')

    with self.argument_context('datafactory data-flow update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('data_flow_name', help='The data flow name.')
        c.argument('data_flow_properties', help='Azure Data Factory nested object which contains a flow with data movements and transformations.')

    with self.argument_context('datafactory data-flow delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('data_flow_name', help='The data flow name.')

    with self.argument_context('datafactory data-flow-debug-session create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('request_compute_type', help='Compute type of the cluster. The value will be overwritten by the same setting in integration runtime if provided.')
        c.argument('request_core_count', help='Core count of the cluster. The value will be overwritten by the same setting in integration runtime if provided.')
        c.argument('request_time_to_live', help='Time to live setting of the cluster in minutes.')
        c.argument('request_integration_runtime', help='Integration runtime debug resource.')

    with self.argument_context('datafactory data-flow-debug-session delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('request_session_id', help='The ID of data flow debug session.')

    with self.argument_context('datafactory data-flow-debug-session add-data-flow') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('request_session_id', help='The ID of data flow debug session.')
        c.argument('request_data_flow', help='Data flow debug resource.')
        c.argument('request_datasets', help='List of datasets.', action=AddDatasets, nargs='+')
        c.argument('request_linked_services', help='List of linked services.', action=AddLinkedServices, nargs='+')
        c.argument('request_staging', help='Staging info for execute data flow activity.')
        c.argument('request_debug_settings', help='Data flow debug settings.')

    with self.argument_context('datafactory data-flow-debug-session execute-command') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
        c.argument('request_session_id', help='The ID of data flow debug session.')
        c.argument('request_command', arg_type=get_enum_type(['executePreviewQuery', 'executeStatisticsQuery', 'executeExpressionQuery']), help='The command type.')
        c.argument('request_command_payload', help='Structure of command payload.')

    with self.argument_context('datafactory data-flow-debug-session query-by-factory') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', help='The factory name.')
