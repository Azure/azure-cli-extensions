# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from knack.arguments import CLIArgumentType
from azure.cli.core.commands.parameters import (
    tags_type,
    get_three_state_flag,
    get_enum_type,
    resource_group_name_type,
    get_location_type
)
from azext_datafactory.action import (
    AddIdentity,
    AddRunDimensions,
    AddFolder,
    AddParameters,
    AddFilters,
    AddOrderBy,
    AddCommandPayload
)


def load_arguments(self, _):

    with self.argument_context('datafactory factory list') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')

    with self.argument_context('datafactory factory show') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('if_none_match', help='ETag of the factory entity. Should only be specified for get. If the ETag mat'
                   'ches the existing entity tag, or if * was provided, then no content will be returned.')

    with self.argument_context('datafactory factory create') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('if_match', help='ETag of the factory entity. Should only be specified for update, for which it shou'
                   'ld match existing entity or can be * for unconditional update.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx), help='The resource location.')
        c.argument('tags', tags_type, help='The resource tags.')
        c.argument('identity', action=AddIdentity, nargs='+', help='Managed service identity of the factory.')
        c.argument('properties_repo_configuration', arg_type=CLIArgumentType(options_list=['--properties-repo-configura'
                   'tion'], help='Git repo information of the factory.'))

    with self.argument_context('datafactory factory update') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('tags', tags_type, help='The resource tags.')
        c.argument('identity', action=AddIdentity, nargs='+', help='Managed service identity of the factory.')

    with self.argument_context('datafactory factory delete') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')

    with self.argument_context('datafactory factory get-git-hub-access-token') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('git_hub_access_code', help='GitHub access code.')
        c.argument('git_hub_client_id', help='GitHub application client ID.')
        c.argument('git_hub_access_token_base_url', help='GitHub access token base URL.')

    with self.argument_context('datafactory factory get-data-plane-access') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('permissions', help='The string with permissions for Data Plane access. Currently only \'r\' is supp'
                   'orted which grants read only access.')
        c.argument('access_resource_path', help='The resource path to get access relative to factory. Currently only em'
                   'pty string is supported which corresponds to the factory resource.')
        c.argument('profile_name', help='The name of the profile. Currently only the default is supported. The default '
                   'value is DefaultProfile.')
        c.argument('start_time', help='Start time for the token. If not specified the current time will be used.')
        c.argument('expire_time', help='Expiration time for the token. Maximum duration for the token is eight hours an'
                   'd by default the token will expire in eight hours.')

    with self.argument_context('datafactory factory configure-factory-repo') as c:
        c.argument('location_id', help='The location identifier.')
        c.argument('factory_resource_id', help='The factory resource id.')
        c.argument('repo_configuration', arg_type=CLIArgumentType(options_list=['--repo-configuration'], help='Git repo'
                   ' information of the factory.'))

    with self.argument_context('datafactory exposure-control get-feature-value-by-factory') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('feature_name', help='The feature name.')
        c.argument('feature_type', help='The feature type.')

    with self.argument_context('datafactory exposure-control get-feature-value') as c:
        c.argument('location_id', help='The location identifier.')
        c.argument('feature_name', help='The feature name.')
        c.argument('feature_type', help='The feature type.')

    with self.argument_context('datafactory integration-runtime list') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')

    with self.argument_context('datafactory integration-runtime show') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')
        c.argument('if_none_match', help='ETag of the integration runtime entity. Should only be specified for get. If '
                   'the ETag matches the existing entity tag, or if * was provided,'
                   'then no content will be returned.')

    with self.argument_context('datafactory integration-runtime create') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')
        c.argument('if_match', help='ETag of the integration runtime entity. Should only be specified for update, for w'
                   'hich it should match existing entity or can be * for unconditional update.')
        c.argument('properties', arg_type=CLIArgumentType(options_list=['--properties'], help='Integration runtime prop'
                   'erties.'))

    with self.argument_context('datafactory integration-runtime update') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')
        c.argument('auto_update', arg_type=get_enum_type(['On', 'Off']), help='Enables or disables the auto-update feat'
                   'ure of the self-hosted integration runtime. See https://go.microsoft.com/fwlink/?linkid=854189.')
        c.argument('update_delay_offset', help='The time offset (in hours) in the day, e.g., PT03H is 3 hours. The inte'
                   'gration runtime auto update will happen on that time.')

    with self.argument_context('datafactory integration-runtime delete') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtime get-status') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtime get-connection-info') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtime regenerate-auth-key') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')
        c.argument('key_name', arg_type=get_enum_type(['authKey1', 'authKey2']), help='The name of the authentication k'
                   'ey to regenerate.')

    with self.argument_context('datafactory integration-runtime list-auth-key') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtime start') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtime stop') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtime sync-credentials') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtime get-monitoring-data') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtime upgrade') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtime remove-link') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')
        c.argument('linked_factory_name', help='The data factory name for linked integration runtime.')

    with self.argument_context('datafactory integration-runtime create-linked-integration-runtime') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')
        c.argument('name', help='The name of the linked integration runtime.')
        c.argument('subscription_id',
                   help='The ID of the subscription that the linked integration runtime belongs to.')
        c.argument('data_factory_name', help='The name of the data factory that the linked integration runtime belongs '
                   'to.')
        c.argument('data_factory_location', help='The location of the data factory that the linked integration runtime '
                   'belongs to.')

    with self.argument_context('datafactory integration-runtime-object-metadata refresh') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')

    with self.argument_context('datafactory integration-runtime-object-metadata get') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')
        c.argument('metadata_path', help='Metadata path.')

    with self.argument_context('datafactory integration-runtime-node show') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')
        c.argument('node_name', help='The integration runtime node name.')

    with self.argument_context('datafactory integration-runtime-node update') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')
        c.argument('node_name', help='The integration runtime node name.')
        c.argument('concurrent_jobs_limit', help='The number of concurrent jobs permitted to run on the integration run'
                   'time node. Values between 1 and maxConcurrentJobs(inclusive) are allowed.')

    with self.argument_context('datafactory integration-runtime-node delete') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')
        c.argument('node_name', help='The integration runtime node name.')

    with self.argument_context('datafactory integration-runtime-node get-ip-address') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('integration_runtime_name', help='The integration runtime name.')
        c.argument('node_name', help='The integration runtime node name.')

    with self.argument_context('datafactory linked-service list') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')

    with self.argument_context('datafactory linked-service show') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('linked_service_name', help='The linked service name.')
        c.argument('if_none_match', help='ETag of the linked service entity. Should only be specified for get. If the E'
                   'Tag matches the existing entity tag, or if * was provided, then no content will be returned.')

    with self.argument_context('datafactory linked-service create') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('linked_service_name', help='The linked service name.')
        c.argument('if_match', help='ETag of the linkedService entity.  Should only be specified for update, for which '
                   'it should match existing entity or can be * for unconditional update.')
        c.argument('properties', arg_type=CLIArgumentType(options_list=['--properties'], help='Properties of linked ser'
                   'vice.'))

    with self.argument_context('datafactory linked-service update') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('linked_service_name', help='The linked service name.')
        c.argument('if_match', help='ETag of the linkedService entity.  Should only be specified for update, for which '
                   'it should match existing entity or can be * for unconditional update.')
        c.argument('properties', arg_type=CLIArgumentType(options_list=['--properties'], help='Properties of linked ser'
                   'vice.'))

    with self.argument_context('datafactory linked-service delete') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('linked_service_name', help='The linked service name.')

    with self.argument_context('datafactory dataset list') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')

    with self.argument_context('datafactory dataset show') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('dataset_name', help='The dataset name.')
        c.argument('if_none_match', help='ETag of the dataset entity. Should only be specified for get. If the ETag mat'
                   'ches the existing entity tag, or if * was provided, then no content will be returned.')

    with self.argument_context('datafactory dataset create') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('dataset_name', help='The dataset name.')
        c.argument('if_match', help='ETag of the dataset entity.  Should only be specified for update, for which it sho'
                   'uld match existing entity or can be * for unconditional update.')
        c.argument('properties', arg_type=CLIArgumentType(options_list=['--properties'], help='Dataset properties.'))

    with self.argument_context('datafactory dataset update') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('dataset_name', help='The dataset name.')
        c.argument('if_match', help='ETag of the dataset entity.  Should only be specified for update, for which it sho'
                   'uld match existing entity or can be * for unconditional update.')
        c.argument('properties', arg_type=CLIArgumentType(options_list=['--properties'], help='Dataset properties.'))

    with self.argument_context('datafactory dataset delete') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('dataset_name', help='The dataset name.')

    with self.argument_context('datafactory pipeline list') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')

    with self.argument_context('datafactory pipeline show') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('pipeline_name', help='The pipeline name.')
        c.argument('if_none_match', help='ETag of the pipeline entity. Should only be specified for get. If the ETag ma'
                   'tches the existing entity tag, or if * was provided, then no content will be returned.')

    with self.argument_context('datafactory pipeline create') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('pipeline_name', help='The pipeline name.')
        c.argument('if_match', help='ETag of the pipeline entity.  Should only be specified for update, for which it sh'
                   'ould match existing entity or can be * for unconditional update.')
        c.argument('properties_description', help='The description of the pipeline.')
        c.argument('properties_activities', arg_type=CLIArgumentType(options_list=['--properties-activities'], help='Li'
                   'st of activities in pipeline.'))
        c.argument('properties_parameters', arg_type=CLIArgumentType(options_list=['--properties-parameters'], help='Li'
                   'st of parameters for pipeline.'))
        c.argument('properties_variables', arg_type=CLIArgumentType(options_list=['--properties-variables'], help='List'
                   ' of variables for pipeline.'))
        c.argument('properties_concurrency', help='The max number of concurrent runs for the pipeline.')
        c.argument('properties_annotations', nargs='+', help='List of tags that can be used for describing the Pipeline'
                   '.')
        c.argument('properties_run_dimensions', action=AddRunDimensions, nargs='+', help='Dimensions emitted by Pipelin'
                   'e.')
        c.argument('properties_folder', action=AddFolder, nargs='+', help='The folder that this Pipeline is in. If not '
                   'specified, Pipeline will appear at the root level.')

    with self.argument_context('datafactory pipeline update') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('pipeline_name', help='The pipeline name.')
        c.argument('if_match', help='ETag of the pipeline entity.  Should only be specified for update, for which it sh'
                   'ould match existing entity or can be * for unconditional update.')
        c.argument('properties_description', help='The description of the pipeline.')
        c.argument('properties_activities', arg_type=CLIArgumentType(options_list=['--properties-activities'], help='Li'
                   'st of activities in pipeline.'))
        c.argument('properties_parameters', arg_type=CLIArgumentType(options_list=['--properties-parameters'], help='Li'
                   'st of parameters for pipeline.'))
        c.argument('properties_variables', arg_type=CLIArgumentType(options_list=['--properties-variables'], help='List'
                   ' of variables for pipeline.'))
        c.argument('properties_concurrency', help='The max number of concurrent runs for the pipeline.')
        c.argument('properties_annotations', nargs='+', help='List of tags that can be used for describing the Pipeline'
                   '.')
        c.argument('properties_run_dimensions', action=AddRunDimensions, nargs='+', help='Dimensions emitted by Pipelin'
                   'e.')
        c.argument('properties_folder', action=AddFolder, nargs='+', help='The folder that this Pipeline is in. If not '
                   'specified, Pipeline will appear at the root level.')

    with self.argument_context('datafactory pipeline delete') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('pipeline_name', help='The pipeline name.')

    with self.argument_context('datafactory pipeline create-run') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('pipeline_name', help='The pipeline name.')
        c.argument('reference_pipeline_run_id', help='The pipeline run identifier. If run ID is specified the parameter'
                   's of the specified run will be used to create a new run.')
        c.argument('is_recovery', arg_type=get_three_state_flag(), help='Recovery mode flag. If recovery mode is set to'
                   ' true, the specified referenced pipeline run and the new run will be grouped under the same groupId'
                   '.')
        c.argument('start_activity_name', help='In recovery mode, the rerun will start from this activity. If not speci'
                   'fied, all activities will run.')
        c.argument('start_from_failure', arg_type=get_three_state_flag(), help='In recovery mode, if set to true, the r'
                   'erun will start from failed activities. The property will be used only if startActivityName is not '
                   'specified.')
        c.argument('parameters', action=AddParameters, nargs='+', help='Parameters of the pipeline run. These parameter'
                   's will be used only if the runId is not specified.')

    with self.argument_context('datafactory pipeline-run show') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('run_id', help='The pipeline run identifier.')

    with self.argument_context('datafactory pipeline-run cancel') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('run_id', help='The pipeline run identifier.')
        c.argument('is_recursive', arg_type=get_three_state_flag(), help='If true, cancel all the Child pipelines that '
                   'are triggered by the current pipeline.')

    with self.argument_context('datafactory pipeline-run query-by-factory') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('continuation_token', help='The continuation token for getting the next page of results. Null for fi'
                   'rst page.')
        c.argument('last_updated_after', help='The time at or after which the run event was updated in \'ISO 8601\' for'
                   'mat.')
        c.argument('last_updated_before', help='The time at or before which the run event was updated in \'ISO 8601\' f'
                   'ormat.')
        c.argument('filters', action=AddFilters, nargs='+', help='List of filters.')
        c.argument('order_by', action=AddOrderBy, nargs='+', help='List of OrderBy option.')

    with self.argument_context('datafactory activity-run query-by-pipeline-run') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('run_id', help='The pipeline run identifier.')
        c.argument('continuation_token', help='The continuation token for getting the next page of results. Null for fi'
                   'rst page.')
        c.argument('last_updated_after', help='The time at or after which the run event was updated in \'ISO 8601\' for'
                   'mat.')
        c.argument('last_updated_before', help='The time at or before which the run event was updated in \'ISO 8601\' f'
                   'ormat.')
        c.argument('filters', action=AddFilters, nargs='+', help='List of filters.')
        c.argument('order_by', action=AddOrderBy, nargs='+', help='List of OrderBy option.')

    with self.argument_context('datafactory trigger list') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')

    with self.argument_context('datafactory trigger show') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('trigger_name', help='The trigger name.')
        c.argument('if_none_match', help='ETag of the trigger entity. Should only be specified for get. If the ETag mat'
                   'ches the existing entity tag, or if * was provided, then no content will be returned.')

    with self.argument_context('datafactory trigger create') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('trigger_name', help='The trigger name.')
        c.argument('if_match', help='ETag of the trigger entity.  Should only be specified for update, for which it sho'
                   'uld match existing entity or can be * for unconditional update.')
        c.argument('properties', arg_type=CLIArgumentType(options_list=['--properties'], help='Properties of the trigge'
                   'r.'))

    with self.argument_context('datafactory trigger update') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('trigger_name', help='The trigger name.')
        c.argument('if_match', help='ETag of the trigger entity.  Should only be specified for update, for which it sho'
                   'uld match existing entity or can be * for unconditional update.')
        c.argument('properties', arg_type=CLIArgumentType(options_list=['--properties'], help='Properties of the trigge'
                   'r.'))

    with self.argument_context('datafactory trigger delete') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('trigger_name', help='The trigger name.')

    with self.argument_context('datafactory trigger subscribe-to-event') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('trigger_name', help='The trigger name.')

    with self.argument_context('datafactory trigger get-event-subscription-status') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('trigger_name', help='The trigger name.')

    with self.argument_context('datafactory trigger unsubscribe-from-event') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('trigger_name', help='The trigger name.')

    with self.argument_context('datafactory trigger start') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('trigger_name', help='The trigger name.')

    with self.argument_context('datafactory trigger stop') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('trigger_name', help='The trigger name.')

    with self.argument_context('datafactory trigger query-by-factory') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('continuation_token', help='The continuation token for getting the next page of results. Null for fi'
                   'rst page.')
        c.argument('parent_trigger_name', help='The name of the parent TumblingWindowTrigger to get the child rerun tri'
                   'ggers')

    with self.argument_context('datafactory trigger-run rerun') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('trigger_name', help='The trigger name.')
        c.argument('run_id', help='The pipeline run identifier.')

    with self.argument_context('datafactory trigger-run query-by-factory') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('continuation_token', help='The continuation token for getting the next page of results. Null for fi'
                   'rst page.')
        c.argument('last_updated_after', help='The time at or after which the run event was updated in \'ISO 8601\' for'
                   'mat.')
        c.argument('last_updated_before', help='The time at or before which the run event was updated in \'ISO 8601\' f'
                   'ormat.')
        c.argument('filters', action=AddFilters, nargs='+', help='List of filters.')
        c.argument('order_by', action=AddOrderBy, nargs='+', help='List of OrderBy option.')

    with self.argument_context('datafactory data-flow list') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')

    with self.argument_context('datafactory data-flow show') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('data_flow_name', help='The data flow name.')
        c.argument('if_none_match', help='ETag of the data flow entity. Should only be specified for get. If the ETag m'
                   'atches the existing entity tag, or if * was provided, then no content will be returned.')

    with self.argument_context('datafactory data-flow create') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('data_flow_name', help='The data flow name.')
        c.argument('if_match', help='ETag of the data flow entity. Should only be specified for update, for which it sh'
                   'ould match existing entity or can be * for unconditional update.')
        c.argument('properties', arg_type=CLIArgumentType(options_list=['--properties'],
                   help='Data flow properties.'))

    with self.argument_context('datafactory data-flow update') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('data_flow_name', help='The data flow name.')
        c.argument('if_match', help='ETag of the data flow entity. Should only be specified for update, for which it sh'
                   'ould match existing entity or can be * for unconditional update.')
        c.argument('properties', arg_type=CLIArgumentType(options_list=['--properties'],
                   help='Data flow properties.'))

    with self.argument_context('datafactory data-flow delete') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('data_flow_name', help='The data flow name.')

    with self.argument_context('datafactory data-flow-debug-session create') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('compute_type', help='Compute type of the cluster. The value will be overwritten by the same setting'
                   ' in integration runtime if provided.')
        c.argument('core_count', help='Core count of the cluster. The value will be overwritten by the same setting in '
                   'integration runtime if provided.')
        c.argument('time_to_live', help='Time to live setting of the cluster in minutes.')
        c.argument('integration_runtime', arg_type=CLIArgumentType(options_list=['--integration-runtime'], help='Set to'
                   ' use integration runtime setting for data flow debug session.'))

    with self.argument_context('datafactory data-flow-debug-session delete') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('session_id', help='The ID of data flow debug session.')

    with self.argument_context('datafactory data-flow-debug-session query-by-factory') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')

    with self.argument_context('datafactory data-flow-debug-session add-data-flow') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('session_id', help='The ID of data flow debug session.')
        c.argument('data_flow', arg_type=CLIArgumentType(options_list=['--data-flow'], help='Data flow instance.'))
        c.argument('datasets', arg_type=CLIArgumentType(options_list=['--datasets'], help='List of datasets.'))
        c.argument('linked_services', arg_type=CLIArgumentType(options_list=['--linked-services'], help='List of linked'
                   ' services.'))
        c.argument('staging', arg_type=CLIArgumentType(options_list=['--staging'], help='Staging info for debug session'
                   '.'))
        c.argument('debug_settings', arg_type=CLIArgumentType(options_list=['--debug-settings'], help='Data flow debug '
                   'settings.'))

    with self.argument_context('datafactory data-flow-debug-session execute-command') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('factory_name', help='The factory name.')
        c.argument('session_id', help='The ID of data flow debug session.')
        c.argument('command', arg_type=get_enum_type(['executePreviewQuery', 'executeStatisticsQuery', 'executeExpressi'
                   'onQuery']), help='The command type.')
        c.argument('command_payload', action=AddCommandPayload, nargs='+', help='The command payload object.')
