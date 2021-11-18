# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from ._validators import validate_export_options, validate_import_options, validate_keyvault_secret_uri, validate_pipeline_type, validate_storage_account_container_uri, validate_user_assigned_identity_resource_id, validate_top


def load_arguments(self, _):
    from azure.cli.core.commands.parameters import tags_type, get_three_state_flag
    from azure.cli.core.commands.validators import get_default_location_from_resource_group

    with self.argument_context('acr') as c:
        c.argument('tags', tags_type)
        c.argument('location', validator=get_default_location_from_resource_group)
        c.argument('registry_name', options_list=['--registry', '-r'], help='Name of registry.')
        c.argument('storage_account_container_uri', options_list=['--storage-container-uri', '-c'], validator=validate_storage_account_container_uri, help='Storage account container URI of the source or target storage account container of the form https://$MyStorageAccount.blob.core.windows.net/$MyContainer. Note that the URI may be different outside of AzureCloud.')
        c.argument('keyvault_secret_uri', options_list=['--secret-uri', '-s'], validator=validate_keyvault_secret_uri, help='Keyvault secret URI containing a valid SAS token to the associated storage account of the form https://$MyKeyvault.vault.azure.net/secrets/$MySecret. Note that the URI may be different outside of AzureCloud.')
        c.argument('user_assigned_identity_resource_id', options_list=['--assign-identity', '-i'], validator=validate_user_assigned_identity_resource_id, help='User assigned identity resource ID of the form /subscriptions/$MySubID/resourceGroups/$MyRG/providers/Microsoft.ManagedIdentity/userAssignedIdentities/$MyIdentity.')

    with self.argument_context('acr import-pipeline') as c:
        c.argument('options', options_list=['--options', '-z'], nargs='+', validator=validate_import_options, help='Space-separated list of options. May only contain the following options: DeleteSourceBlobOnSuccess,OverwriteTags,ContinueOnErrors,DisableSourceTrigger.')
        c.argument('import_pipeline_name', options_list=['--name', '-n'], help='Name of the import pipeline.')
        c.argument('source_trigger_enabled', options_list=['--source-trigger-enabled', '-e'], arg_type=get_three_state_flag(), help='Boolean parameter that determines whether source trigger is enabled on the pipeline. Must be either True or False. True by default.')

    with self.argument_context('acr export-pipeline') as c:
        c.argument('options', options_list=['--options', '-z'], nargs='+', validator=validate_export_options, help='Space-separated list of options. May only container the following options: OverwriteBlobs,ContinueOnErrors.')
        c.argument('export_pipeline_name', options_list=['--name', '-n'], help='Name of the export pipeline.')

    with self.argument_context('acr pipeline-run') as c:
        c.argument('pipeline_name', options_list=['--pipeline', '-p'], help='Name of the pipeline to run.')
        c.argument('pipeline_type', options_list=['--pipeline-type', '-t'], validator=validate_pipeline_type, help='Type of pipeline. Must be either import or export.')
        c.argument('pipeline_run_name', options_list=['--name', '-n'], help='Name of the pipeline run.')
        c.argument('force_update_tag', options_list=['--force-redeploy', '-f'], action='store_true', help='Flag that forces ARM to redeploy resource even if no parameters have changed.')
        c.argument('storage_blob_name', options_list=['--storage-blob', '-b'], help='Name of the storage blob to be imported or exported.')
        c.argument('artifacts', options_list=['--artifacts', '-a'], nargs='+', help='Space-separated list of container artifacts. Artifacts must be either of the form `repository:tag` or `repository@digest` such as hello-world:latest or hello-world@sha256:90659bf80b44ce6be8234e6ff90a1ac34acbeb826903b02cfa0da11c82cbc042.')
        c.argument('top', validator=validate_top, help='List only the last n pipeline-runs. Must be an integer.')

    with self.argument_context('acr pipeline-run clean') as c:
        c.argument('dry_run', action='store_true', help='List the failed pipeline-runs that would have been deleted, but do not delete any.')
