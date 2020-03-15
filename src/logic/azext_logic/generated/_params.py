# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from argcomplete.completers import FilesCompleter
from azure.cli.core.commands.parameters import (
    tags_type,
    resource_group_name_type,
    get_location_type,
    file_type
)

from azext_logic.action import (
    AddWorkflow,
    AddParameters,
    AddListCallbackUrl,
    AddMove,
    AddKeyType,
    AddValidate,
    AddSetState,
    AddIntegrationAccount,
    AddListKeyVaultKeys,
    AddLogTrackingEvents,
    AddRegenerateAccessKey,
    AddAssemblyArtifact,
    AddBatchConfiguration,
    AddSchema,
    AddListContentCallbackUrl,
    AddMap,
    AddPartner,
    AddAgreement,
    AddCertificate,
    AddSession,
    AddIntegrationServiceEnvironment
)


def load_arguments(self, _):

    with self.argument_context('logic workflow list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('top', help='The number of items to be included in the result.')
        c.argument('filter', help='The filter to apply on the operation. Options for filters include: State, Trigger, and ReferencedResourceId.')

    with self.argument_context('logic workflow show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('workflow_name', help='The workflow name.')

    with self.argument_context('logic workflow create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('workflow_name', help='The workflow name.')
        c.argument('location', type=str, help='the location of the resouce grouop')
        c.argument('workflow_file_path', type=file_type, help='Path to a workflow JSON file', completer=FilesCompleter())

    with self.argument_context('logic workflow update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('workflow_name', help='The workflow name.')
        #c.argument('password', options_list=['--password', '-p'], help='Optional password for the admin user account to be created on each compute node.')
        c.argument('tags', tags_type)

    with self.argument_context('logic workflow delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('workflow_name', help='The workflow name.')

    with self.argument_context('logic workflow generate-upgraded-definition') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('workflow_name', help='The workflow name.')
        c.argument('parameters', help='Parameters for generating an upgraded definition.', action=AddParameters, nargs='+')

    with self.argument_context('logic workflow list-callback-url') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('workflow_name', help='The workflow name.')
        c.argument('list_callback_url', help='Which callback url to list.', action=AddListCallbackUrl, nargs='+')

    with self.argument_context('logic workflow move') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('workflow_name', help='The workflow name.')
        c.argument('move', help='The workflow to move.', action=AddMove, nargs='+')

    with self.argument_context('logic workflow regenerate-access-key') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('workflow_name', help='The workflow name.')
        c.argument('key_type', help='The access key type.', action=AddKeyType, nargs='+')

    with self.argument_context('logic workflow validate-by-resource-group') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('workflow_name', help='The workflow name.')
        c.argument('validate', help='The workflow.', action=AddValidate, nargs='+')

    with self.argument_context('logic workflow validate-by-location') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('workflow_name', help='The workflow name.')

    with self.argument_context('logic workflow disable') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('workflow_name', help='The workflow name.')

    with self.argument_context('logic workflow enable') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('workflow_name', help='The workflow name.')

    with self.argument_context('logic workflow list-swagger') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('workflow_name', help='The workflow name.')

    with self.argument_context('logic workflow-version list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('workflow_name', help='The workflow name.')
        c.argument('top', help='The number of items to be included in the result.')

    with self.argument_context('logic workflow-version show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('workflow_name', help='The workflow name.')
        c.argument('version_id', help='The workflow versionId.')

    with self.argument_context('logic workflow-trigger list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('workflow_name', help='The workflow name.')
        c.argument('top', help='The number of items to be included in the result.')
        c.argument('filter', help='The filter to apply on the operation. Options for filters include: State, Trigger, and ReferencedResourceId.')

    with self.argument_context('logic workflow-trigger show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('workflow_name', help='The workflow name.')
        c.argument('trigger_name', help='The workflow trigger name.')

    with self.argument_context('logic workflow-trigger reset') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('workflow_name', help='The workflow name.')
        c.argument('trigger_name', help='The workflow trigger name.')
        c.argument('set_state', help='The workflow trigger state.', action=AddSetState, nargs='+')

    with self.argument_context('logic workflow-trigger run') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('workflow_name', help='The workflow name.')
        c.argument('trigger_name', help='The workflow trigger name.')

    with self.argument_context('logic workflow-trigger list-callback-url') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('workflow_name', help='The workflow name.')
        c.argument('trigger_name', help='The workflow trigger name.')

    with self.argument_context('logic workflow-version-trigger list-callback-url') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('workflow_name', help='The workflow name.')
        c.argument('version_id', help='The workflow versionId.')
        c.argument('trigger_name', help='The workflow trigger name.')
        c.argument('parameters', help='The callback URL parameters.', action=AddParameters, nargs='+')

    with self.argument_context('logic workflow-trigger-history list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('workflow_name', help='The workflow name.')
        c.argument('trigger_name', help='The workflow trigger name.')
        c.argument('top', help='The number of items to be included in the result.')
        c.argument('filter', help='The filter to apply on the operation. Options for filters include: State, Trigger, and ReferencedResourceId.')

    with self.argument_context('logic workflow-trigger-history show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('workflow_name', help='The workflow name.')
        c.argument('trigger_name', help='The workflow trigger name.')
        c.argument('history_name', help='The workflow trigger history name. Corresponds to the run name for triggers that resulted in a run.')

    with self.argument_context('logic workflow-trigger-history resubmit') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('workflow_name', help='The workflow name.')
        c.argument('trigger_name', help='The workflow trigger name.')
        c.argument('history_name', help='The workflow trigger history name. Corresponds to the run name for triggers that resulted in a run.')

    with self.argument_context('logic workflow-run list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('workflow_name', help='The workflow name.')
        c.argument('top', help='The number of items to be included in the result.')
        c.argument('filter', help='The filter to apply on the operation. Options for filters include: State, Trigger, and ReferencedResourceId.')

    with self.argument_context('logic workflow-run show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('workflow_name', help='The workflow name.')
        c.argument('run_name', help='The workflow run name.')

    with self.argument_context('logic workflow-run cancel') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('workflow_name', help='The workflow name.')
        c.argument('run_name', help='The workflow run name.')

    with self.argument_context('logic workflow-run-action list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('workflow_name', help='The workflow name.')
        c.argument('run_name', help='The workflow run name.')
        c.argument('top', help='The number of items to be included in the result.')
        c.argument('filter', help='The filter to apply on the operation. Options for filters include: State, Trigger, and ReferencedResourceId.')

    with self.argument_context('logic workflow-run-action show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('workflow_name', help='The workflow name.')
        c.argument('run_name', help='The workflow run name.')
        c.argument('action_name', help='The workflow action name.')

    with self.argument_context('logic workflow-run-action list-expression-trace') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('workflow_name', help='The workflow name.')
        c.argument('run_name', help='The workflow run name.')
        c.argument('action_name', help='The workflow action name.')

    with self.argument_context('logic workflow-run-action-repetition list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('workflow_name', help='The workflow name.')
        c.argument('run_name', help='The workflow run name.')
        c.argument('action_name', help='The workflow action name.')

    with self.argument_context('logic workflow-run-action-repetition show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('workflow_name', help='The workflow name.')
        c.argument('run_name', help='The workflow run name.')
        c.argument('action_name', help='The workflow action name.')
        c.argument('repetition_name', help='The workflow repetition.')

    with self.argument_context('logic workflow-run-action-repetition list-expression-trace') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('workflow_name', help='The workflow name.')
        c.argument('run_name', help='The workflow run name.')
        c.argument('action_name', help='The workflow action name.')
        c.argument('repetition_name', help='The workflow repetition.')

    with self.argument_context('logic workflow-run-action-repetition-request-history list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('workflow_name', help='The workflow name.')
        c.argument('run_name', help='The workflow run name.')
        c.argument('action_name', help='The workflow action name.')
        c.argument('repetition_name', help='The workflow repetition.')

    with self.argument_context('logic workflow-run-action-repetition-request-history show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('workflow_name', help='The workflow name.')
        c.argument('run_name', help='The workflow run name.')
        c.argument('action_name', help='The workflow action name.')
        c.argument('repetition_name', help='The workflow repetition.')
        c.argument('request_history_name', help='The request history name.')

    with self.argument_context('logic workflow-run-action-request-history list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('workflow_name', help='The workflow name.')
        c.argument('run_name', help='The workflow run name.')
        c.argument('action_name', help='The workflow action name.')

    with self.argument_context('logic workflow-run-action-request-history show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('workflow_name', help='The workflow name.')
        c.argument('run_name', help='The workflow run name.')
        c.argument('action_name', help='The workflow action name.')
        c.argument('request_history_name', help='The request history name.')

    with self.argument_context('logic workflow-run-action-scope-repetition list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('workflow_name', help='The workflow name.')
        c.argument('run_name', help='The workflow run name.')
        c.argument('action_name', help='The workflow action name.')

    with self.argument_context('logic workflow-run-action-scope-repetition show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('workflow_name', help='The workflow name.')
        c.argument('run_name', help='The workflow run name.')
        c.argument('action_name', help='The workflow action name.')
        c.argument('repetition_name', help='The workflow repetition.')

    with self.argument_context('logic workflow-run-operation show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('workflow_name', help='The workflow name.')
        c.argument('run_name', help='The workflow run name.')
        c.argument('operation_id', help='The workflow operation id.')

    with self.argument_context('logic integration-account list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('top', help='The number of items to be included in the result.')

    with self.argument_context('logic integration-account show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')

    with self.argument_context('logic integration-account create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('integration_file_path', type=file_type, help='Path to a intergration account JSON file', completer=FilesCompleter())

    with self.argument_context('logic integration-account update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('integration_account', help='The integration account.', action=AddIntegrationAccount, nargs='+')

    with self.argument_context('logic integration-account delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')

    with self.argument_context('logic integration-account list-callback-url') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('parameters', help='The callback URL parameters.', action=AddParameters, nargs='+')

    with self.argument_context('logic integration-account list-key-vault-key') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('list_key_vault_keys', help='The key vault parameters.', action=AddListKeyVaultKeys, nargs='+')

    with self.argument_context('logic integration-account log-tracking-event') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('log_tracking_events', help='The callback URL parameters.', action=AddLogTrackingEvents, nargs='+')

    with self.argument_context('logic integration-account regenerate-access-key') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('regenerate_access_key', help='The access key type.', action=AddRegenerateAccessKey, nargs='+')

    with self.argument_context('logic integration-account-assembly list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')

    with self.argument_context('logic integration-account-assembly show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('assembly_artifact_name', help='The assembly artifact name.')

    with self.argument_context('logic integration-account-assembly create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('assembly_artifact_name', help='The assembly artifact name.')
        c.argument('assembly_artifact', help='The assembly artifact.', action=AddAssemblyArtifact, nargs='+')

    with self.argument_context('logic integration-account-assembly update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('assembly_artifact_name', help='The assembly artifact name.')
        c.argument('assembly_artifact', help='The assembly artifact.', action=AddAssemblyArtifact, nargs='+')

    with self.argument_context('logic integration-account-assembly delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('assembly_artifact_name', help='The assembly artifact name.')

    with self.argument_context('logic integration-account-assembly list-content-callback-url') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('assembly_artifact_name', help='The assembly artifact name.')

    with self.argument_context('logic integration-account-batch-configuration list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')

    with self.argument_context('logic integration-account-batch-configuration show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('batch_configuration_name', help='The batch configuration name.')

    with self.argument_context('logic integration-account-batch-configuration create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('batch_configuration_name', help='The batch configuration name.')
        c.argument('batch_configuration', help='The batch configuration.', action=AddBatchConfiguration, nargs='+')

    with self.argument_context('logic integration-account-batch-configuration update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('batch_configuration_name', help='The batch configuration name.')
        c.argument('batch_configuration', help='The batch configuration.', action=AddBatchConfiguration, nargs='+')

    with self.argument_context('logic integration-account-batch-configuration delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('batch_configuration_name', help='The batch configuration name.')

    with self.argument_context('logic integration-account-schema list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('top', help='The number of items to be included in the result.')
        c.argument('filter', help='The filter to apply on the operation. Options for filters include: State, Trigger, and ReferencedResourceId.')

    with self.argument_context('logic integration-account-schema show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('schema_name', help='The integration account schema name.')

    with self.argument_context('logic integration-account-schema create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('schema_name', help='The integration account schema name.')
        c.argument('schema', help='The integration account schema.', action=AddSchema, nargs='+')

    with self.argument_context('logic integration-account-schema update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('schema_name', help='The integration account schema name.')
        c.argument('schema', help='The integration account schema.', action=AddSchema, nargs='+')

    with self.argument_context('logic integration-account-schema delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('schema_name', help='The integration account schema name.')

    with self.argument_context('logic integration-account-schema list-content-callback-url') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('schema_name', help='The integration account schema name.')
        c.argument('list_content_callback_url', help='', action=AddListContentCallbackUrl, nargs='+')

    with self.argument_context('logic integration-account-map list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('top', help='The number of items to be included in the result.')
        c.argument('filter', help='The filter to apply on the operation. Options for filters include: State, Trigger, and ReferencedResourceId.')

    with self.argument_context('logic integration-account-map show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('map_name', help='The integration account map name.')

    with self.argument_context('logic integration-account-map create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('map_name', help='The integration account map name.')
        c.argument('map', help='The integration account map.', action=AddMap, nargs='+')

    with self.argument_context('logic integration-account-map update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('map_name', help='The integration account map name.')
        c.argument('map', help='The integration account map.', action=AddMap, nargs='+')

    with self.argument_context('logic integration-account-map delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('map_name', help='The integration account map name.')

    with self.argument_context('logic integration-account-map list-content-callback-url') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('map_name', help='The integration account map name.')
        c.argument('list_content_callback_url', help='', action=AddListContentCallbackUrl, nargs='+')

    with self.argument_context('logic integration-account-partner list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('top', help='The number of items to be included in the result.')
        c.argument('filter', help='The filter to apply on the operation. Options for filters include: State, Trigger, and ReferencedResourceId.')

    with self.argument_context('logic integration-account-partner show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('partner_name', help='The integration account partner name.')

    with self.argument_context('logic integration-account-partner create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('partner_name', help='The integration account partner name.')
        c.argument('partner', help='The integration account partner.', action=AddPartner, nargs='+')

    with self.argument_context('logic integration-account-partner update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('partner_name', help='The integration account partner name.')
        c.argument('partner', help='The integration account partner.', action=AddPartner, nargs='+')

    with self.argument_context('logic integration-account-partner delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('partner_name', help='The integration account partner name.')

    with self.argument_context('logic integration-account-partner list-content-callback-url') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('partner_name', help='The integration account partner name.')
        c.argument('list_content_callback_url', help='', action=AddListContentCallbackUrl, nargs='+')

    with self.argument_context('logic integration-account-agreement list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('top', help='The number of items to be included in the result.')
        c.argument('filter', help='The filter to apply on the operation. Options for filters include: State, Trigger, and ReferencedResourceId.')

    with self.argument_context('logic integration-account-agreement show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('agreement_name', help='The integration account agreement name.')

    with self.argument_context('logic integration-account-agreement create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('agreement_name', help='The integration account agreement name.')
        c.argument('agreement', help='The integration account agreement.', action=AddAgreement, nargs='+')

    with self.argument_context('logic integration-account-agreement update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('agreement_name', help='The integration account agreement name.')
        c.argument('agreement', help='The integration account agreement.', action=AddAgreement, nargs='+')

    with self.argument_context('logic integration-account-agreement delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('agreement_name', help='The integration account agreement name.')

    with self.argument_context('logic integration-account-agreement list-content-callback-url') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('agreement_name', help='The integration account agreement name.')
        c.argument('list_content_callback_url', help='', action=AddListContentCallbackUrl, nargs='+')

    with self.argument_context('logic integration-account-certificate list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('top', help='The number of items to be included in the result.')

    with self.argument_context('logic integration-account-certificate show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('certificate_name', help='The integration account certificate name.')

    with self.argument_context('logic integration-account-certificate create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('certificate_name', help='The integration account certificate name.')
        c.argument('certificate', help='The integration account certificate.', action=AddCertificate, nargs='+')

    with self.argument_context('logic integration-account-certificate update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('certificate_name', help='The integration account certificate name.')
        c.argument('certificate', help='The integration account certificate.', action=AddCertificate, nargs='+')

    with self.argument_context('logic integration-account-certificate delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('certificate_name', help='The integration account certificate name.')

    with self.argument_context('logic integration-account-session list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('top', help='The number of items to be included in the result.')
        c.argument('filter', help='The filter to apply on the operation. Options for filters include: State, Trigger, and ReferencedResourceId.')

    with self.argument_context('logic integration-account-session show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('session_name', help='The integration account session name.')

    with self.argument_context('logic integration-account-session create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('session_name', help='The integration account session name.')
        c.argument('session', help='The integration account session.', action=AddSession, nargs='+')

    with self.argument_context('logic integration-account-session update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('session_name', help='The integration account session name.')
        c.argument('session', help='The integration account session.', action=AddSession, nargs='+')

    with self.argument_context('logic integration-account-session delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('integration_account_name', help='The integration account name.')
        c.argument('session_name', help='The integration account session name.')

    with self.argument_context('logic integration-service-environment list') as c:
        c.argument('resource_group', help='The resource group.')
        c.argument('top', help='The number of items to be included in the result.')

    with self.argument_context('logic integration-service-environment show') as c:
        c.argument('resource_group', help='The resource group.')
        c.argument('integration_service_environment_name', help='The integration service environment name.')

    with self.argument_context('logic integration-service-environment create') as c:
        c.argument('resource_group', help='The resource group.')
        c.argument('integration_service_environment_name', help='The integration service environment name.')
        c.argument('integration_service_environment', help='The integration service environment.', action=AddIntegrationServiceEnvironment, nargs='+')

    with self.argument_context('logic integration-service-environment update') as c:
        c.argument('resource_group', help='The resource group.')
        c.argument('integration_service_environment_name', help='The integration service environment name.')
        c.argument('integration_service_environment', help='The integration service environment.', action=AddIntegrationServiceEnvironment, nargs='+')

    with self.argument_context('logic integration-service-environment delete') as c:
        c.argument('resource_group', help='The resource group.')
        c.argument('integration_service_environment_name', help='The integration service environment name.')

    with self.argument_context('logic integration-service-environment restart') as c:
        c.argument('resource_group', help='The resource group.')
        c.argument('integration_service_environment_name', help='The integration service environment name.')

    with self.argument_context('logic integration-service-environment-sku list') as c:
        c.argument('resource_group', help='The resource group.')
        c.argument('integration_service_environment_name', help='The integration service environment name.')

    with self.argument_context('logic integration-service-environment-network-health show') as c:
        c.argument('resource_group', help='The resource group.')
        c.argument('integration_service_environment_name', help='The integration service environment name.')

    with self.argument_context('logic integration-service-environment-managed-api list') as c:
        c.argument('resource_group', help='The resource group.')
        c.argument('integration_service_environment_name', help='The integration service environment name.')

    with self.argument_context('logic integration-service-environment-managed-api show') as c:
        c.argument('resource_group', help='The resource group.')
        c.argument('integration_service_environment_name', help='The integration service environment name.')
        c.argument('api_name', help='The api name.')

    with self.argument_context('logic integration-service-environment-managed-api delete') as c:
        c.argument('resource_group', help='The resource group.')
        c.argument('integration_service_environment_name', help='The integration service environment name.')
        c.argument('api_name', help='The api name.')

    with self.argument_context('logic integration-service-environment-managed-api put') as c:
        c.argument('resource_group', help='The resource group.')
        c.argument('integration_service_environment_name', help='The integration service environment name.')
        c.argument('api_name', help='The api name.')

    with self.argument_context('logic integration-service-environment-managed-api-operation list') as c:
        c.argument('resource_group', help='The resource group.')
        c.argument('integration_service_environment_name', help='The integration service environment name.')
        c.argument('api_name', help='The api name.')
