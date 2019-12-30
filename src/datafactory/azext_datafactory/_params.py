# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from azure.cli.core.commands.parameters import (
    tags_type,
    get_enum_type,
    resource_group_name_type,
    get_location_type,
    get_three_state_flag
)
'''
from azext_datafactory.action import (
    PeeringAddActivities,
    PeeringAddDatasets,
    PeeringAddLinkedServices,
    PeeringAddSourceSettings
)
'''


def load_arguments(self, _):

    with self.argument_context('datafactory list') as c:
        pass

    with self.argument_context('datafactory create') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The factory name.')
        c.argument('factory_resource_id', id_part=None, help='The factory resource id.')
        c.argument('account_name', id_part=None, help='Account name.')
        c.argument('repository_name', id_part=None, help='Repository name.')
        c.argument('collaboration_branch', id_part=None, help='Collaboration branch.')
        c.argument('root_folder', id_part=None, help='Root folder.')
        c.argument('last_commit_id', id_part=None, help='Last commit id.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)
        c.argument('additional_properties', id_part=None, help='Unmatched properties from the message are deserialized this collection')
        c.argument('_type', options_list=['--type'], id_part=None, help='The identity type. Currently the only supported type is \'SystemAssigned\'.')
        c.argument('repo_configuration_account_name', id_part=None, help='Account name.')
        c.argument('repo_configuration_repository_name', id_part=None, help='Repository name.')
        c.argument('repo_configuration_collaboration_branch', id_part=None, help='Collaboration branch.')
        c.argument('repo_configuration_root_folder', id_part=None, help='Root folder.')
        c.argument('repo_configuration_last_commit_id', id_part=None, help='Last commit id.')
        c.argument('git_hub_access_code', id_part=None, help='GitHub access code.')
        c.argument('git_hub_client_id', id_part=None, help='GitHub application client ID.')
        c.argument('git_hub_access_token_base_url', id_part=None, help='GitHub access token base URL.')
        c.argument('permissions', id_part=None, help='The string with permissions for Data Plane access. Currently only \'r\' is supported which grants read only access.')
        c.argument('access_resource_path', id_part=None, help='The resource path to get access relative to factory. Currently only empty string is supported which corresponds to the factory resource.')
        c.argument('profile_name', id_part=None, help='The name of the profile. Currently only the default is supported. The default value is DefaultProfile.')
        c.argument('start_time', id_part=None, help='Start time for the token. If not specified the current time will be used.')
        c.argument('expire_time', id_part=None, help='Expiration time for the token. Maximum duration for the token is eight hours and by default the token will expire in eight hours.')

    with self.argument_context('datafactory update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The factory name.')
        c.argument('factory_resource_id', id_part=None, help='The factory resource id.')
        c.argument('account_name', id_part=None, help='Account name.')
        c.argument('repository_name', id_part=None, help='Repository name.')
        c.argument('collaboration_branch', id_part=None, help='Collaboration branch.')
        c.argument('root_folder', id_part=None, help='Root folder.')
        c.argument('last_commit_id', id_part=None, help='Last commit id.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)
        c.argument('additional_properties', id_part=None, help='Unmatched properties from the message are deserialized this collection')
        c.argument('_type', options_list=['--type'], id_part=None, help='The identity type. Currently the only supported type is \'SystemAssigned\'.')
        c.argument('repo_configuration_account_name', id_part=None, help='Account name.')
        c.argument('repo_configuration_repository_name', id_part=None, help='Repository name.')
        c.argument('repo_configuration_collaboration_branch', id_part=None, help='Collaboration branch.')
        c.argument('repo_configuration_root_folder', id_part=None, help='Root folder.')
        c.argument('repo_configuration_last_commit_id', id_part=None, help='Last commit id.')
        c.argument('git_hub_access_code', id_part=None, help='GitHub access code.')
        c.argument('git_hub_client_id', id_part=None, help='GitHub application client ID.')
        c.argument('git_hub_access_token_base_url', id_part=None, help='GitHub access token base URL.')
        c.argument('permissions', id_part=None, help='The string with permissions for Data Plane access. Currently only \'r\' is supported which grants read only access.')
        c.argument('access_resource_path', id_part=None, help='The resource path to get access relative to factory. Currently only empty string is supported which corresponds to the factory resource.')
        c.argument('profile_name', id_part=None, help='The name of the profile. Currently only the default is supported. The default value is DefaultProfile.')
        c.argument('start_time', id_part=None, help='Start time for the token. If not specified the current time will be used.')
        c.argument('expire_time', id_part=None, help='Expiration time for the token. Maximum duration for the token is eight hours and by default the token will expire in eight hours.')

    with self.argument_context('datafactory delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The factory name.')

    with self.argument_context('datafactory show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The factory name.')

    with self.argument_context('datafactory list') as c:
        c.argument('resource_group', resource_group_name_type)

    with self.argument_context('datafactory configure_factory_repo') as c:
        c.argument('location_id', id_part=None, help='The location identifier.')

    with self.argument_context('datafactory get_git_hub_access_token') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The factory name.')

    with self.argument_context('datafactory get_data_plane_access') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The factory name.')

    with self.argument_context('datafactory get-feature-value get_feature_value') as c:
        c.argument('location_id', id_part=None, help='The location identifier.')

    with self.argument_context('datafactory get-feature-value get_feature_value_by_factory') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The factory name.')

    with self.argument_context('datafactory integration-runtime create') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('name', id_part=None, help='The integration runtime name.')
        c.argument('additional_properties', id_part=None, help='Unmatched properties from the message are deserialized this collection')
        c.argument('description', id_part=None, help='Integration runtime description.')
        c.argument('auto_update', arg_type=get_enum_type(['On', 'Off']), id_part=None, help='Enables or disables the auto-update feature of the self-hosted integration runtime. See https://go.microsoft.com/fwlink/?linkid=854189.')
        c.argument('update_delay_offset', id_part=None, help='The time offset (in hours) in the day, e.g., PT03H is 3 hours. The integration runtime auto update will happen on that time.')
        c.argument('key_name', arg_type=get_enum_type(['authKey1', 'authKey2']), id_part=None, help='The name of the authentication key to regenerate.')
        c.argument('subscription_id', id_part=None, help='The ID of the subscription that the linked integration runtime belongs to.')
        c.argument('data_factory_name', id_part=None, help='The name of the data factory that the linked integration runtime belongs to.')
        c.argument('data_factory_location', id_part=None, help='The location of the data factory that the linked integration runtime belongs to.')

    with self.argument_context('datafactory integration-runtime update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('name', id_part=None, help='The integration runtime name.')
        c.argument('additional_properties', id_part=None, help='Unmatched properties from the message are deserialized this collection')
        c.argument('description', id_part=None, help='Integration runtime description.')
        c.argument('auto_update', arg_type=get_enum_type(['On', 'Off']), id_part=None, help='Enables or disables the auto-update feature of the self-hosted integration runtime. See https://go.microsoft.com/fwlink/?linkid=854189.')
        c.argument('update_delay_offset', id_part=None, help='The time offset (in hours) in the day, e.g., PT03H is 3 hours. The integration runtime auto update will happen on that time.')
        c.argument('key_name', arg_type=get_enum_type(['authKey1', 'authKey2']), id_part=None, help='The name of the authentication key to regenerate.')
        c.argument('subscription_id', id_part=None, help='The ID of the subscription that the linked integration runtime belongs to.')
        c.argument('data_factory_name', id_part=None, help='The name of the data factory that the linked integration runtime belongs to.')
        c.argument('data_factory_location', id_part=None, help='The location of the data factory that the linked integration runtime belongs to.')

    with self.argument_context('datafactory integration-runtime delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('name', id_part=None, help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtime show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('name', id_part=None, help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtime list') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')

    with self.argument_context('datafactory integration-runtime get_status') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('name', id_part=None, help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtime get_connection_info') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('name', id_part=None, help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtime regenerate_auth_key') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('name', id_part=None, help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtime create_linked_integration_runtime') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('name', id_part=None, help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtime start') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('name', id_part=None, help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtime stop') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('name', id_part=None, help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtime sync_credentials') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('name', id_part=None, help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtime get_monitoring_data') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('name', id_part=None, help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtime upgrade') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('name', id_part=None, help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtime remove_links') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('name', id_part=None, help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtime list_auth_keys') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('name', id_part=None, help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtime refresh-object-metadata refresh') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('name', id_part=None, help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtime refresh-object-metadata get') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('name', id_part=None, help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtime node update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('integration_runtime_name', id_part=None, help='The integration runtime name.')
        c.argument('name', id_part=None, help='The integration runtime node name.')
        c.argument('concurrent_jobs_limit', id_part=None, help='The number of concurrent jobs permitted to run on the integration runtime node. Values between 1 and maxConcurrentJobs(inclusive) are allowed.')

    with self.argument_context('datafactory integration-runtime node delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('integration_runtime_name', id_part=None, help='The integration runtime name.')
        c.argument('name', id_part=None, help='The integration runtime node name.')

    with self.argument_context('datafactory integration-runtime node show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('integration_runtime_name', id_part=None, help='The integration runtime name.')
        c.argument('name', id_part=None, help='The integration runtime node name.')

    with self.argument_context('datafactory integration-runtime node get_ip_address') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('integration_runtime_name', id_part=None, help='The integration runtime name.')
        c.argument('name', id_part=None, help='The integration runtime node name.')

    with self.argument_context('datafactory linkedservice create') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('name', id_part=None, help='The linked service name.')
        c.argument('additional_properties', id_part=None, help='Unmatched properties from the message are deserialized this collection')
        c.argument('connect_via_type', id_part=None, help='Type of integration runtime.')
        c.argument('connect_via_reference_name', id_part=None, help='Reference integration runtime name.')
        c.argument('connect_via_parameters', id_part=None, help='Arguments for integration runtime.')
        c.argument('description', id_part=None, help='Linked service description.')
        c.argument('parameters', id_part=None, help='Parameters for linked service.')
        c.argument('annotations', id_part=None, help='List of tags that can be used for describing the linked service.', nargs='+')

    with self.argument_context('datafactory linkedservice update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('name', id_part=None, help='The linked service name.')
        c.argument('additional_properties', id_part=None, help='Unmatched properties from the message are deserialized this collection')
        c.argument('connect_via_type', id_part=None, help='Type of integration runtime.')
        c.argument('connect_via_reference_name', id_part=None, help='Reference integration runtime name.')
        c.argument('connect_via_parameters', id_part=None, help='Arguments for integration runtime.')
        c.argument('description', id_part=None, help='Linked service description.')
        c.argument('parameters', id_part=None, help='Parameters for linked service.')
        c.argument('annotations', id_part=None, help='List of tags that can be used for describing the linked service.', nargs='+')

    with self.argument_context('datafactory linkedservice delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('name', id_part=None, help='The linked service name.')

    with self.argument_context('datafactory linkedservice show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('name', id_part=None, help='The linked service name.')

    with self.argument_context('datafactory linkedservice list') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')

    with self.argument_context('datafactory dataset create') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('name', id_part=None, help='The dataset name.')
        c.argument('additional_properties', id_part=None, help='Unmatched properties from the message are deserialized this collection')
        c.argument('description', id_part=None, help='Dataset description.')
        c.argument('structure', id_part=None, help='Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.')
        c.argument('schema', id_part=None, help='Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.')
        c.argument('linked_service_name_type', id_part=None, help='Linked service reference type.')
        c.argument('linked_service_name_reference_name', id_part=None, help='Reference LinkedService name.')
        c.argument('linked_service_name_parameters', id_part=None, help='Arguments for LinkedService.')
        c.argument('parameters', id_part=None, help='Parameters for dataset.')
        c.argument('annotations', id_part=None, help='List of tags that can be used for describing the Dataset.', nargs='+')
        c.argument('folder_name', id_part=None, help='The name of the folder that this Dataset is in.')

    with self.argument_context('datafactory dataset update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('name', id_part=None, help='The dataset name.')
        c.argument('additional_properties', id_part=None, help='Unmatched properties from the message are deserialized this collection')
        c.argument('description', id_part=None, help='Dataset description.')
        c.argument('structure', id_part=None, help='Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.')
        c.argument('schema', id_part=None, help='Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.')
        c.argument('linked_service_name_type', id_part=None, help='Linked service reference type.')
        c.argument('linked_service_name_reference_name', id_part=None, help='Reference LinkedService name.')
        c.argument('linked_service_name_parameters', id_part=None, help='Arguments for LinkedService.')
        c.argument('parameters', id_part=None, help='Parameters for dataset.')
        c.argument('annotations', id_part=None, help='List of tags that can be used for describing the Dataset.', nargs='+')
        c.argument('folder_name', id_part=None, help='The name of the folder that this Dataset is in.')

    with self.argument_context('datafactory dataset delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('name', id_part=None, help='The dataset name.')

    with self.argument_context('datafactory dataset show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('name', id_part=None, help='The dataset name.')

    with self.argument_context('datafactory dataset list') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')

    with self.argument_context('datafactory pipeline create') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('pipeline_name', id_part=None, help='The pipeline name.')
        c.argument('additional_properties', id_part=None, help='Unmatched properties from the message are deserialized this collection')
        c.argument('description', id_part=None, help='The description of the pipeline.')
        #c.argument('activities', id_part=None, help='List of activities in pipeline.', action=PeeringAddActivities, nargs='+')
        c.argument('parameters', id_part=None, help='List of parameters for pipeline.')
        c.argument('variables', id_part=None, help='List of variables for pipeline.')
        c.argument('concurrency', id_part=None, help='The max number of concurrent runs for the pipeline.')
        c.argument('annotations', id_part=None, help='List of tags that can be used for describing the Pipeline.', nargs='+')
        c.argument('run_dimensions', id_part=None, help='Dimensions emitted by Pipeline.')
        c.argument('folder_name', id_part=None, help='The name of the folder that this Pipeline is in.')

    with self.argument_context('datafactory pipeline update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('pipeline_name', id_part=None, help='The pipeline name.')
        c.argument('additional_properties', id_part=None, help='Unmatched properties from the message are deserialized this collection')
        c.argument('description', id_part=None, help='The description of the pipeline.')
        #c.argument('activities', id_part=None, help='List of activities in pipeline.', action=PeeringAddActivities, nargs='+')
        c.argument('parameters', id_part=None, help='List of parameters for pipeline.')
        c.argument('variables', id_part=None, help='List of variables for pipeline.')
        c.argument('concurrency', id_part=None, help='The max number of concurrent runs for the pipeline.')
        c.argument('annotations', id_part=None, help='List of tags that can be used for describing the Pipeline.', nargs='+')
        c.argument('run_dimensions', id_part=None, help='Dimensions emitted by Pipeline.')
        c.argument('folder_name', id_part=None, help='The name of the folder that this Pipeline is in.')

    with self.argument_context('datafactory pipeline delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('pipeline_name', id_part=None, help='The pipeline name.')

    with self.argument_context('datafactory pipeline show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('pipeline_name', id_part=None, help='The pipeline name.')

    with self.argument_context('datafactory pipeline list') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')

    with self.argument_context('datafactory pipeline create_run') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('pipeline_name', id_part=None, help='The pipeline name.')
        c.argument('reference_pipeline_run_id', id_part=None, help='The pipeline run identifier. If run ID is specified the parameters of the specified run will be used to create a new run.')
        c.argument('is_recovery', arg_type=get_three_state_flag(), id_part=None, help='Recovery mode flag. If recovery mode is set to true, the specified referenced pipeline run and the new run will be grouped under the same groupId.')
        c.argument('name', id_part=None, help='In recovery mode, the rerun will start from this activity. If not specified, all activities will run.')
        c.argument('parameters', id_part=None, help='Parameters of the pipeline run. These parameters will be used only if the runId is not specified.')

    with self.argument_context('datafactory query-pipeline-run query_by_factory') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The factory name.')

    with self.argument_context('datafactory query-pipeline-run cancel') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The factory name.')
        c.argument('run_id', id_part=None, help='The pipeline run identifier.')
        c.argument('is_recursive', arg_type=get_three_state_flag(), id_part=None, help='If true, cancel all the Child pipelines that are triggered by the current pipeline.')

    with self.argument_context('datafactory query-pipeline-run get') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The factory name.')
        c.argument('run_id', id_part=None, help='The pipeline run identifier.')

    with self.argument_context('datafactory pipelinerun query-activityrun query_by_pipeline_run') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The factory name.')
        c.argument('run_id', id_part=None, help='The pipeline run identifier.')

    with self.argument_context('datafactory trigger create') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('name', id_part=None, help='The trigger name.')
        c.argument('additional_properties', id_part=None, help='Unmatched properties from the message are deserialized this collection')
        c.argument('description', id_part=None, help='Trigger description.')
        c.argument('annotations', id_part=None, help='List of tags that can be used for describing the trigger.', nargs='+')

    with self.argument_context('datafactory trigger update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('name', id_part=None, help='The trigger name.')
        c.argument('additional_properties', id_part=None, help='Unmatched properties from the message are deserialized this collection')
        c.argument('description', id_part=None, help='Trigger description.')
        c.argument('annotations', id_part=None, help='List of tags that can be used for describing the trigger.', nargs='+')

    with self.argument_context('datafactory trigger delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('name', id_part=None, help='The trigger name.')

    with self.argument_context('datafactory trigger show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('name', id_part=None, help='The trigger name.')

    with self.argument_context('datafactory trigger list') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')

    with self.argument_context('datafactory trigger subscribe_to_events') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('name', id_part=None, help='The trigger name.')

    with self.argument_context('datafactory trigger get_event_subscription_status') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('name', id_part=None, help='The trigger name.')

    with self.argument_context('datafactory trigger unsubscribe_from_events') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('name', id_part=None, help='The trigger name.')

    with self.argument_context('datafactory trigger start') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('name', id_part=None, help='The trigger name.')

    with self.argument_context('datafactory trigger stop') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('name', id_part=None, help='The trigger name.')

    with self.argument_context('datafactory trigger trigger-run rerun rerun') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('name', id_part=None, help='The trigger name.')
        c.argument('run_id', id_part=None, help='The pipeline run identifier.')

    with self.argument_context('datafactory trigger trigger-run rerun query_by_factory') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')

    with self.argument_context('datafactory trigger rerun-trigger create') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('trigger_name', id_part=None, help='The trigger name.')
        c.argument('name', id_part=None, help='The rerun trigger name.')
        c.argument('start_time', id_part=None, help='The start time for the time period for which restatement is initiated. Only UTC time is currently supported.')
        c.argument('end_time', id_part=None, help='The end time for the time period for which restatement is initiated. Only UTC time is currently supported.')
        c.argument('max_concurrency', id_part=None, help='The max number of parallel time windows (ready for execution) for which a rerun is triggered.')

    with self.argument_context('datafactory trigger rerun-trigger update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('trigger_name', id_part=None, help='The trigger name.')
        c.argument('name', id_part=None, help='The rerun trigger name.')
        c.argument('start_time', id_part=None, help='The start time for the time period for which restatement is initiated. Only UTC time is currently supported.')
        c.argument('end_time', id_part=None, help='The end time for the time period for which restatement is initiated. Only UTC time is currently supported.')
        c.argument('max_concurrency', id_part=None, help='The max number of parallel time windows (ready for execution) for which a rerun is triggered.')

    with self.argument_context('datafactory trigger rerun-trigger list') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('trigger_name', id_part=None, help='The trigger name.')

    with self.argument_context('datafactory trigger rerun-trigger start') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('trigger_name', id_part=None, help='The trigger name.')
        c.argument('name', id_part=None, help='The rerun trigger name.')

    with self.argument_context('datafactory trigger rerun-trigger stop') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('trigger_name', id_part=None, help='The trigger name.')
        c.argument('name', id_part=None, help='The rerun trigger name.')

    with self.argument_context('datafactory trigger rerun-trigger cancel') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('trigger_name', id_part=None, help='The trigger name.')
        c.argument('name', id_part=None, help='The rerun trigger name.')

    with self.argument_context('datafactory dataflow create') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('name', id_part=None, help='The data flow name.')
        c.argument('description', id_part=None, help='The description of the data flow.')
        c.argument('annotations', id_part=None, help='List of tags that can be used for describing the data flow.', nargs='+')
        c.argument('folder_name', id_part=None, help='The name of the folder that this data flow is in.')

    with self.argument_context('datafactory dataflow update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('name', id_part=None, help='The data flow name.')
        c.argument('description', id_part=None, help='The description of the data flow.')
        c.argument('annotations', id_part=None, help='List of tags that can be used for describing the data flow.', nargs='+')
        c.argument('folder_name', id_part=None, help='The name of the folder that this data flow is in.')

    with self.argument_context('datafactory dataflow delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('name', id_part=None, help='The data flow name.')

    with self.argument_context('datafactory dataflow show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')
        c.argument('name', id_part=None, help='The data flow name.')

    with self.argument_context('datafactory dataflow list') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('factory_name', id_part=None, help='The factory name.')

    with self.argument_context('datafactory create-data-flow-debug-session create') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The factory name.')
        c.argument('compute_type', id_part=None, help='Compute type of the cluster. The value will be overwritten by the same setting in integration runtime if provided.')
        c.argument('core_count', id_part=None, help='Core count of the cluster. The value will be overwritten by the same setting in integration runtime if provided.')
        c.argument('time_to_live', id_part=None, help='Time to live setting of the cluster in minutes.')
        c.argument('properties_additional_properties', id_part=None, help='Unmatched properties from the message are deserialized this collection')
        c.argument('properties_description', id_part=None, help='Integration runtime description.')
        c.argument('additional_properties', id_part=None, help='Unmatched properties from the message are deserialized this collection')
        c.argument('session_id', id_part=None, help='The ID of data flow debug session.')
        c.argument('properties_annotations', id_part=None, help='List of tags that can be used for describing the data flow.', nargs='+')
        c.argument('properties_folder_name', id_part=None, help='The name of the folder that this data flow is in.')
        #c.argument('datasets', id_part=None, help='List of datasets.', action=PeeringAddDatasets, nargs='+')
        #c.argument('linked_services', id_part=None, help='List of linked services.', action=PeeringAddLinkedServices, nargs='+')
        c.argument('linked_service_type', id_part=None, help='Linked service reference type.')
        c.argument('linked_service_reference_name', id_part=None, help='Reference LinkedService name.')
        c.argument('linked_service_parameters', id_part=None, help='Arguments for LinkedService.')
        c.argument('folder_path', id_part=None, help='Folder path for staging blob.')
        #c.argument('source_settings', id_part=None, help='Source setting for data flow debug.', action=PeeringAddSourceSettings, nargs='+')
        c.argument('parameters', id_part=None, help='Data flow parameters.')
        c.argument('dataset_parameters', id_part=None, help='Parameters for dataset.')
        c.argument('command', arg_type=get_enum_type(['executePreviewQuery', 'executeStatisticsQuery', 'executeExpressionQuery']), id_part=None, help='The command type.')
        c.argument('stream_name', id_part=None, help='The stream name which is used for preview.')
        c.argument('row_limits', id_part=None, help='Row limits for preview response.')
        c.argument('columns', id_part=None, help='Array of column names.', nargs='+')
        c.argument('expression', id_part=None, help='The expression which is used for preview.')

    with self.argument_context('datafactory create-data-flow-debug-session query_by_factory') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The factory name.')

    with self.argument_context('datafactory create-data-flow-debug-session add_data_flow') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The factory name.')

    with self.argument_context('datafactory create-data-flow-debug-session delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The factory name.')

    with self.argument_context('datafactory create-data-flow-debug-session execute_command') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The factory name.')
