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
from azext_datafactory.actions import (
    AddAnnotations,
    AddActivities,
    AddFilters,
    AddOrderBy,
    AddDatasets,
    AddLinkedServices,
    AddSourceSettings,
    AddColumns
)


def load_arguments(self, _):

    with self.argument_context('datafactory operations list') as c:
        pass

    with self.argument_context('datafactory factories list') as c:
        c.argument('resource_group_name', resource_group_name_type)

    with self.argument_context('datafactory factories show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')

    with self.argument_context('datafactory factories create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', tags_type, nargs='+')
        c.argument('repo_configuration_type_repo_configuration', id_part=None, help='Type of repo configuration.')
        c.argument('repo_configuration_account_name', id_part=None, help='Account name.')
        c.argument('repo_configuration_repository_name', id_part=None, help='Repository name.')
        c.argument('repo_configuration_collaboration_branch', id_part=None, help='Collaboration branch.')
        c.argument('repo_configuration_root_folder', id_part=None, help='Root folder.')
        c.argument('repo_configuration_last_commit_id', id_part=None, help='Last commit id.')

    with self.argument_context('datafactory factories update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('tags', tags_type, nargs='+')

    with self.argument_context('datafactory factories delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')

    with self.argument_context('datafactory factories configure-factory-repo') as c:
        c.argument('location_id', id_part=None, help='The location identifier.')
        c.argument('factory_resource_id', id_part=None, help='The factory resource id.')
        c.argument('repo_configuration_type', id_part=None, help='Type of repo configuration.')
        c.argument('repo_configuration_account_name', id_part=None, help='Account name.')
        c.argument('repo_configuration_repository_name', id_part=None, help='Repository name.')
        c.argument('repo_configuration_collaboration_branch', id_part=None, help='Collaboration branch.')
        c.argument('repo_configuration_root_folder', id_part=None, help='Root folder.')
        c.argument('repo_configuration_last_commit_id', id_part=None, help='Last commit id.')

    with self.argument_context('datafactory factories get-data-plane-access') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('permissions', id_part=None, help='The string with permissions for Data Plane access. Currently only \'r\' is supported which grants read only access.')
        c.argument('access_resource_path', id_part=None, help='The resource path to get access relative to factory. Currently only empty string is supported which corresponds to the factory resource.')
        c.argument('profile_name', id_part=None, help='The name of the profile. Currently only the default is supported. The default value is DefaultProfile.')
        c.argument('start_time', id_part=None, help='Start time for the token. If not specified the current time will be used.')
        c.argument('expire_time', id_part=None, help='Expiration time for the token. Maximum duration for the token is eight hours and by default the token will expire in eight hours.')

    with self.argument_context('datafactory factories get-git-hub-access-token') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('git_hub_access_code', id_part=None, help='GitHub access code.')
        c.argument('git_hub_client_id', id_part=None, help='GitHub application client ID.')
        c.argument('git_hub_access_token_base_url', id_part=None, help='GitHub access token base URL.')

    with self.argument_context('datafactory exposure-control get-feature-value-by-factory') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('feature_name', id_part=None, help='The feature name.')
        c.argument('feature_type', id_part=None, help='The feature type.')

    with self.argument_context('datafactory exposure-control get-feature-value') as c:
        c.argument('location_id', id_part=None, help='The location identifier.')
        c.argument('feature_name', id_part=None, help='The feature name.')
        c.argument('feature_type', id_part=None, help='The feature type.')

    with self.argument_context('datafactory integration-runtimes list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')

    with self.argument_context('datafactory integration-runtimes show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('integration_runtime_name', id_part=None, help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtimes create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('integration_runtime_name', id_part=None, help='The integration runtime name.')
        c.argument('properties_type', arg_type=get_enum_type(['Managed', 'SelfHosted']), id_part=None, help='The type of integration runtime.')
        c.argument('properties_description', id_part=None, help='Integration runtime description.')

    with self.argument_context('datafactory integration-runtimes update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('integration_runtime_name', id_part=None, help='The integration runtime name.')
        c.argument('auto_update', arg_type=get_enum_type(['On', 'Off']), id_part=None, help='The state of integration runtime auto update.')
        c.argument('update_delay_offset', id_part=None, help='The time offset (in hours) in the day, e.g., PT03H is 3 hours. The integration runtime auto update will happen on that time.')

    with self.argument_context('datafactory integration-runtimes delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('integration_runtime_name', id_part=None, help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtimes create-linked-integration-runtime') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('integration_runtime_name', id_part=None, help='The integration runtime name.')
        c.argument('name', id_part=None, help='The name of the linked integration runtime.')
        c.argument('create_linked_integration_runtime_request_subscription_id', id_part=None, help='The ID of the subscription that the linked integration runtime belongs to.')
        c.argument('data_factory_name', id_part=None, help='The name of the data factory that the linked integration runtime belongs to.')
        c.argument('data_factory_location', id_part=None, help='The location of the data factory that the linked integration runtime belongs to.')

    with self.argument_context('datafactory integration-runtimes regenerate-auth-key') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('integration_runtime_name', id_part=None, help='The integration runtime name.')
        c.argument('key_name', arg_type=get_enum_type(['authKey1', 'authKey2']), id_part=None, help='The name of the authentication key to regenerate.')

    with self.argument_context('datafactory integration-runtimes remove-links') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('integration_runtime_name', id_part=None, help='The integration runtime name.')
        c.argument('linked_factory_name', id_part=None, help='The data factory name for linked integration runtime.')

    with self.argument_context('datafactory integration-runtimes get-status') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('integration_runtime_name', id_part=None, help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtimes get-connection-info') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('integration_runtime_name', id_part=None, help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtimes list-auth-keys') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('integration_runtime_name', id_part=None, help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtimes start') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('integration_runtime_name', id_part=None, help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtimes stop') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('integration_runtime_name', id_part=None, help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtimes sync-credentials') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('integration_runtime_name', id_part=None, help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtimes get-monitoring-data') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('integration_runtime_name', id_part=None, help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtimes upgrade') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('integration_runtime_name', id_part=None, help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtime-object-metadata get') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('integration_runtime_name', id_part=None, help='The integration runtime name.')
        c.argument('metadata_path', id_part=None, help='Metadata path.')

    with self.argument_context('datafactory integration-runtime-object-metadata refresh') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('integration_runtime_name', id_part=None, help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtime-nodes show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('integration_runtime_name', id_part=None, help='The integration runtime name.')
        c.argument('node_name', id_part=None, help='The integration runtime node name.')

    with self.argument_context('datafactory integration-runtime-nodes update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('integration_runtime_name', id_part=None, help='The integration runtime name.')
        c.argument('node_name', id_part=None, help='The integration runtime node name.')
        c.argument('concurrent_jobs_limit', id_part=None, help='The number of concurrent jobs permitted to run on the integration runtime node. Values between 1 and maxConcurrentJobs(inclusive) are allowed.')

    with self.argument_context('datafactory integration-runtime-nodes delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('integration_runtime_name', id_part=None, help='The integration runtime name.')
        c.argument('node_name', id_part=None, help='The integration runtime node name.')

    with self.argument_context('datafactory integration-runtime-nodes get-ip-address') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('integration_runtime_name', id_part=None, help='The integration runtime name.')
        c.argument('node_name', id_part=None, help='The integration runtime node name.')

    with self.argument_context('datafactory linked-services list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')

    with self.argument_context('datafactory linked-services show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('linked_service_name', id_part=None, help='The linked service name.')

    with self.argument_context('datafactory linked-services create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('linked_service_name', id_part=None, help='The linked service name.')
        c.argument('properties_type', id_part=None, help='Type of linked service.')
        c.argument('reference_name', id_part=None, help='Reference integration runtime name.')
        c.argument('parameters', id_part=None, help='An object mapping parameter names to argument values.', nargs='+')
        c.argument('properties_description', id_part=None, help='Linked service description.')
        c.argument('properties_parameters_properties', id_part=None, help='Definition of all parameters for an entity.', nargs='+')
        c.argument('properties_annotations', id_part=None, help='List of tags that can be used for describing the linked service.', action=AddAnnotations, nargs='+')

    with self.argument_context('datafactory linked-services update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('linked_service_name', id_part=None, help='The linked service name.')
        c.argument('properties_type', id_part=None, help='Type of linked service.')
        c.argument('reference_name', id_part=None, help='Reference integration runtime name.')
        c.argument('parameters', id_part=None, help='An object mapping parameter names to argument values.', nargs='+')
        c.argument('properties_description', id_part=None, help='Linked service description.')
        c.argument('properties_parameters_properties', id_part=None, help='Definition of all parameters for an entity.', nargs='+')
        c.argument('properties_annotations', id_part=None, help='List of tags that can be used for describing the linked service.', action=AddAnnotations, nargs='+')

    with self.argument_context('datafactory linked-services delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('linked_service_name', id_part=None, help='The linked service name.')

    with self.argument_context('datafactory datasets list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')

    with self.argument_context('datafactory datasets show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('dataset_name', id_part=None, help='The dataset name.')

    with self.argument_context('datafactory datasets create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('dataset_name', id_part=None, help='The dataset name.')
        c.argument('properties_type', id_part=None, help='Type of dataset.')
        c.argument('properties_description', id_part=None, help='Dataset description.')
        c.argument('reference_name', id_part=None, help='Reference LinkedService name.')
        c.argument('parameters', id_part=None, help='An object mapping parameter names to argument values.', nargs='+')
        c.argument('properties_parameters_properties', id_part=None, help='Definition of all parameters for an entity.', nargs='+')
        c.argument('properties_annotations', id_part=None, help='List of tags that can be used for describing the Dataset.', action=AddAnnotations, nargs='+')
        c.argument('name', id_part=None, help='The name of the folder that this Dataset is in.')

    with self.argument_context('datafactory datasets update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('dataset_name', id_part=None, help='The dataset name.')
        c.argument('properties_type', id_part=None, help='Type of dataset.')
        c.argument('properties_description', id_part=None, help='Dataset description.')
        c.argument('reference_name', id_part=None, help='Reference LinkedService name.')
        c.argument('parameters', id_part=None, help='An object mapping parameter names to argument values.', nargs='+')
        c.argument('properties_parameters_properties', id_part=None, help='Definition of all parameters for an entity.', nargs='+')
        c.argument('properties_annotations', id_part=None, help='List of tags that can be used for describing the Dataset.', action=AddAnnotations, nargs='+')
        c.argument('name', id_part=None, help='The name of the folder that this Dataset is in.')

    with self.argument_context('datafactory datasets delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('dataset_name', id_part=None, help='The dataset name.')

    with self.argument_context('datafactory pipelines list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')

    with self.argument_context('datafactory pipelines show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('pipeline_name', id_part=None, help='The pipeline name.')

    with self.argument_context('datafactory pipelines create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('pipeline_name', id_part=None, help='The pipeline name.')
        c.argument('description', id_part=None, help='The description of the pipeline.')
        c.argument('activities', id_part=None, help='List of activities in pipeline.', action=AddActivities, nargs='+')
        c.argument('parameters', id_part=None, help='Definition of all parameters for an entity.', nargs='+')
        c.argument('variables', id_part=None, help='Definition of variable for a Pipeline.', nargs='+')
        c.argument('concurrency', id_part=None, help='The max number of concurrent runs for the pipeline.')
        c.argument('annotations', id_part=None, help='List of tags that can be used for describing the Pipeline.', action=AddAnnotations, nargs='+')
        c.argument('run_dimensions', id_part=None, help='Dimensions emitted by Pipeline.', nargs='+')
        c.argument('folder_name', id_part=None, help='The name of the folder that this Pipeline is in.')

    with self.argument_context('datafactory pipelines update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('pipeline_name', id_part=None, help='The pipeline name.')
        c.argument('description', id_part=None, help='The description of the pipeline.')
        c.argument('activities', id_part=None, help='List of activities in pipeline.', action=AddActivities, nargs='+')
        c.argument('parameters', id_part=None, help='Definition of all parameters for an entity.', nargs='+')
        c.argument('variables', id_part=None, help='Definition of variable for a Pipeline.', nargs='+')
        c.argument('concurrency', id_part=None, help='The max number of concurrent runs for the pipeline.')
        c.argument('annotations', id_part=None, help='List of tags that can be used for describing the Pipeline.', action=AddAnnotations, nargs='+')
        c.argument('run_dimensions', id_part=None, help='Dimensions emitted by Pipeline.', nargs='+')
        c.argument('folder_name', id_part=None, help='The name of the folder that this Pipeline is in.')

    with self.argument_context('datafactory pipelines delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('pipeline_name', id_part=None, help='The pipeline name.')

    with self.argument_context('datafactory pipelines create-run') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('pipeline_name', id_part=None, help='The pipeline name.')
        c.argument('reference_pipeline_run_id', id_part=None, help='The pipeline run identifier. If run ID is specified the parameters of the specified run will be used to create a new run.')
        c.argument('is_recovery', arg_type=get_three_state_flag(), id_part=None, help='Recovery mode flag. If recovery mode is set to true, the specified referenced pipeline run and the new run will be grouped under the same groupId.')
        c.argument('start_activity_name', id_part=None, help='In recovery mode, the rerun will start from this activity. If not specified, all activities will run.')
        c.argument('start_from_failure', arg_type=get_three_state_flag(), id_part=None, help='In recovery mode, if set to true, the rerun will start from failed activities. The property will be used only if startActivityName is not specified.')
        c.argument('parameters', id_part=None, help='Parameters of the pipeline run. These parameters will be used only if the runId is not specified.', nargs='+')

    with self.argument_context('datafactory pipeline-runs show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('run_id', id_part=None, help='The pipeline run identifier.')

    with self.argument_context('datafactory pipeline-runs query-by-factory') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('continuation_token', id_part=None, help='The continuation token for getting the next page of results. Null for first page.')
        c.argument('last_updated_after', id_part=None, help='The time at or after which the run event was updated in \'ISO 8601\' format.')
        c.argument('last_updated_before', id_part=None, help='The time at or before which the run event was updated in \'ISO 8601\' format.')
        c.argument('filters', id_part=None, help='List of filters.', action=AddFilters, nargs='+')
        c.argument('order_by', id_part=None, help='List of OrderBy option.', action=AddOrderBy, nargs='+')

    with self.argument_context('datafactory pipeline-runs cancel') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('run_id', id_part=None, help='The pipeline run identifier.')
        c.argument('is_recursive', arg_type=get_three_state_flag(), id_part=None, help='If true, cancel all the Child pipelines that are triggered by the current pipeline.')

    with self.argument_context('datafactory activity-runs query-by-pipeline-run') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('run_id', id_part=None, help='The pipeline run identifier.')
        c.argument('continuation_token', id_part=None, help='The continuation token for getting the next page of results. Null for first page.')
        c.argument('last_updated_after', id_part=None, help='The time at or after which the run event was updated in \'ISO 8601\' format.')
        c.argument('last_updated_before', id_part=None, help='The time at or before which the run event was updated in \'ISO 8601\' format.')
        c.argument('filters', id_part=None, help='List of filters.', action=AddFilters, nargs='+')
        c.argument('order_by', id_part=None, help='List of OrderBy option.', action=AddOrderBy, nargs='+')

    with self.argument_context('datafactory triggers list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')

    with self.argument_context('datafactory triggers show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('trigger_name', id_part=None, help='The trigger name.')

    with self.argument_context('datafactory triggers create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('trigger_name', id_part=None, help='The trigger name.')
        c.argument('properties_type', id_part=None, help='Trigger type.')
        c.argument('properties_description', id_part=None, help='Trigger description.')
        c.argument('properties_annotations', id_part=None, help='List of tags that can be used for describing the trigger.', action=AddAnnotations, nargs='+')

    with self.argument_context('datafactory triggers update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('trigger_name', id_part=None, help='The trigger name.')
        c.argument('properties_type', id_part=None, help='Trigger type.')
        c.argument('properties_description', id_part=None, help='Trigger description.')
        c.argument('properties_annotations', id_part=None, help='List of tags that can be used for describing the trigger.', action=AddAnnotations, nargs='+')

    with self.argument_context('datafactory triggers delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('trigger_name', id_part=None, help='The trigger name.')

    with self.argument_context('datafactory triggers query-by-factory') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('continuation_token', id_part=None, help='The continuation token for getting the next page of results. Null for first page.')
        c.argument('parent_trigger_name', id_part=None, help='The name of the parent TumblingWindowTrigger to get the child rerun triggers')

    with self.argument_context('datafactory triggers subscribe-to-events') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('trigger_name', id_part=None, help='The trigger name.')

    with self.argument_context('datafactory triggers get-event-subscription-status') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('trigger_name', id_part=None, help='The trigger name.')

    with self.argument_context('datafactory triggers unsubscribe-from-events') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('trigger_name', id_part=None, help='The trigger name.')

    with self.argument_context('datafactory triggers start') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('trigger_name', id_part=None, help='The trigger name.')

    with self.argument_context('datafactory triggers stop') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('trigger_name', id_part=None, help='The trigger name.')

    with self.argument_context('datafactory trigger-runs query-by-factory') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('continuation_token', id_part=None, help='The continuation token for getting the next page of results. Null for first page.')
        c.argument('last_updated_after', id_part=None, help='The time at or after which the run event was updated in \'ISO 8601\' format.')
        c.argument('last_updated_before', id_part=None, help='The time at or before which the run event was updated in \'ISO 8601\' format.')
        c.argument('filters', id_part=None, help='List of filters.', action=AddFilters, nargs='+')
        c.argument('order_by', id_part=None, help='List of OrderBy option.', action=AddOrderBy, nargs='+')

    with self.argument_context('datafactory trigger-runs rerun') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('trigger_name', id_part=None, help='The trigger name.')
        c.argument('run_id', id_part=None, help='The pipeline run identifier.')

    with self.argument_context('datafactory data-flows list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')

    with self.argument_context('datafactory data-flows show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('data_flow_name', id_part=None, help='The data flow name.')

    with self.argument_context('datafactory data-flows create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('data_flow_name', id_part=None, help='The data flow name.')
        c.argument('properties_type', id_part=None, help='Type of data flow.')
        c.argument('properties_description', id_part=None, help='The description of the data flow.')
        c.argument('properties_annotations', id_part=None, help='List of tags that can be used for describing the data flow.', action=AddAnnotations, nargs='+')
        c.argument('name', id_part=None, help='The name of the folder that this data flow is in.')

    with self.argument_context('datafactory data-flows update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('data_flow_name', id_part=None, help='The data flow name.')
        c.argument('properties_type', id_part=None, help='Type of data flow.')
        c.argument('properties_description', id_part=None, help='The description of the data flow.')
        c.argument('properties_annotations', id_part=None, help='List of tags that can be used for describing the data flow.', action=AddAnnotations, nargs='+')
        c.argument('name', id_part=None, help='The name of the folder that this data flow is in.')

    with self.argument_context('datafactory data-flows delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('data_flow_name', id_part=None, help='The data flow name.')

    with self.argument_context('datafactory data-flow-debug-session create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('compute_type', id_part=None, help='Compute type of the cluster. The value will be overwritten by the same setting in integration runtime if provided.')
        c.argument('core_count', id_part=None, help='Core count of the cluster. The value will be overwritten by the same setting in integration runtime if provided.')
        c.argument('time_to_live', id_part=None, help='Time to live setting of the cluster in minutes.')
        c.argument('integration_runtime_name', id_part=None, help='The resource name.')
        c.argument('_type', options_list=['--type'], arg_type=get_enum_type(['Managed', 'SelfHosted']), id_part=None, help='The type of integration runtime.')
        c.argument('description', id_part=None, help='Integration runtime description.')

    with self.argument_context('datafactory data-flow-debug-session delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('session_id', id_part=None, help='The ID of data flow debug session.')

    with self.argument_context('datafactory data-flow-debug-session add-data-flow') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('session_id', id_part=None, help='The ID of data flow debug session.')
        c.argument('data_flow_name', id_part=None, help='The resource name.')
        c.argument('_type', options_list=['--type'], id_part=None, help='Type of data flow.')
        c.argument('description', id_part=None, help='The description of the data flow.')
        c.argument('annotations', id_part=None, help='List of tags that can be used for describing the data flow.', action=AddAnnotations, nargs='+')
        c.argument('name_data_flow_properties_folder', id_part=None, help='The name of the folder that this data flow is in.')
        c.argument('datasets', id_part=None, help='List of datasets.', action=AddDatasets, nargs='+')
        c.argument('linked_services', id_part=None, help='List of linked services.', action=AddLinkedServices, nargs='+')
        c.argument('reference_name', id_part=None, help='Reference LinkedService name.')
        c.argument('parameters', id_part=None, help='An object mapping parameter names to argument values.', nargs='+')
        c.argument('staging_folder_path', id_part=None, help='Folder path for staging blob.')
        c.argument('debug_settings_source_settings', id_part=None, help='Source setting for data flow debug.', action=AddSourceSettings, nargs='+')
        c.argument('debug_settings_parameters_debug_settings', id_part=None, help='An object mapping parameter names to argument values.', nargs='+')

    with self.argument_context('datafactory data-flow-debug-session execute-command') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('session_id', id_part=None, help='The ID of data flow debug session.')
        c.argument('command', arg_type=get_enum_type(['executePreviewQuery', 'executeStatisticsQuery', 'executeExpressionQuery']), id_part=None, help='The command type.')
        c.argument('command_payload_stream_name', id_part=None, help='The stream name which is used for preview.')
        c.argument('command_payload_row_limits', id_part=None, help='Row limits for preview response.')
        c.argument('command_payload_columns', id_part=None, help='Array of column names.', action=AddColumns, nargs='+')
        c.argument('command_payload_expression', id_part=None, help='The expression which is used for preview.')

    with self.argument_context('datafactory data-flow-debug-session query-by-factory') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
