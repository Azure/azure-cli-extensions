# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from knack.arguments import CLIArgumentType
from azure.cli.core.commands.parameters import (
    tags_type,
    get_enum_type,
    resource_group_name_type,
    get_location_type
)
from azext_datashare.action import AddIdentity


def load_arguments(self, _):

    with self.argument_context('datashare account list') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('skip_token', help='Continuation token')

    with self.argument_context('datashare account show') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')

    with self.argument_context('datashare account create') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx), help='Location of the azure resource.')
        c.argument('tags', tags_type, help='Tags on the azure resource.')
        c.argument('identity', action=AddIdentity, nargs='+', help='Identity Info on the Account')

    with self.argument_context('datashare account update') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('tags', tags_type, help='Tags on the azure resource.')

    with self.argument_context('datashare account delete') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')

    with self.argument_context('datashare consumer-invitation list') as c:
        c.argument('skip_token', help='The continuation token')

    with self.argument_context('datashare consumer-invitation show') as c:
        c.argument('location', arg_type=get_location_type(self.cli_ctx), help='Location of the invitation')
        c.argument('invitation_id', help='An invitation id')

    with self.argument_context('datashare consumer-invitation reject-invitation') as c:
        c.argument('location', arg_type=get_location_type(self.cli_ctx), help='Location of the invitation')
        c.argument('properties_invitation_id', help='Unique id of the invitation.')

    with self.argument_context('datashare data-set list') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_name', help='The name of the share.')
        c.argument('skip_token', help='continuation token')

    with self.argument_context('datashare data-set show') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_name', help='The name of the share.')
        c.argument('data_set_name', help='The name of the dataSet.')

    with self.argument_context('datashare data-set create') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_name', help='The name of the share to add the data set to.')
        c.argument('data_set_name', help='The name of the dataSet.')
        c.argument('data_set', arg_type=CLIArgumentType(options_list=['--data-set'], help='The new data set information'
                   '.'))

    with self.argument_context('datashare data-set delete') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_name', help='The name of the share.')
        c.argument('data_set_name', help='The name of the dataSet.')

    with self.argument_context('datashare data-set-mapping list') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of the share subscription.')
        c.argument('skip_token', help='Continuation token')

    with self.argument_context('datashare data-set-mapping show') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of the shareSubscription.')
        c.argument('data_set_mapping_name', help='The name of the dataSetMapping.')

    with self.argument_context('datashare data-set-mapping create') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of the share subscription which will hold the data set sin'
                   'k.')
        c.argument('data_set_mapping_name', help='The name of the data set mapping to be created.')
        c.argument('data_set_mapping', arg_type=CLIArgumentType(options_list=['--data-set-mapping'], help='Destination '
                   'data set configuration details.'))

    with self.argument_context('datashare data-set-mapping delete') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of the shareSubscription.')
        c.argument('data_set_mapping_name', help='The name of the dataSetMapping.')

    with self.argument_context('datashare invitation list') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_name', help='The name of the share.')
        c.argument('skip_token', help='The continuation token')

    with self.argument_context('datashare invitation show') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_name', help='The name of the share.')
        c.argument('invitation_name', help='The name of the invitation.')

    with self.argument_context('datashare invitation create') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_name', help='The name of the share to send the invitation for.')
        c.argument('invitation_name', help='The name of the invitation.')
        c.argument('properties_target_active_directory_id', help='The target Azure AD Id. Can\'t be combined with email'
                   '.')
        c.argument('properties_target_email', help='The email the invitation is directed to.')
        c.argument('properties_target_object_id', help='The target user or application Id that invitation is being sent'
                   ' to. Must be specified along TargetActiveDirectoryId. This enables sending invitations to specific '
                   'users or applications in an AD tenant.')

    with self.argument_context('datashare invitation delete') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_name', help='The name of the share.')
        c.argument('invitation_name', help='The name of the invitation.')

    with self.argument_context('datashare share list') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('skip_token', help='Continuation Token')

    with self.argument_context('datashare share show') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_name', help='The name of the share to retrieve.')

    with self.argument_context('datashare share create') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_name', help='The name of the share.')
        c.argument('properties_description', help='Share description.')
        c.argument('properties_share_kind', arg_type=get_enum_type(['CopyBased', 'InPlace']), help='Share kind.')
        c.argument('properties_terms', help='Share terms.')

    with self.argument_context('datashare share delete') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_name', help='The name of the share.')

    with self.argument_context('datashare share list-synchronization') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_name', help='The name of the share.')
        c.argument('skip_token', help='Continuation token')

    with self.argument_context('datashare share list-synchronization-detail') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_name', help='The name of the share.')
        c.argument('skip_token', help='Continuation token')
        c.argument('consumer_email', help='Email of the user who created the synchronization')
        c.argument('consumer_name', help='Name of the user who created the synchronization')
        c.argument('consumer_tenant_name', help='Tenant name of the consumer who created the synchronization')
        c.argument('duration_ms', help='synchronization duration')
        c.argument('end_time', help='End time of synchronization')
        c.argument('message', help='message of synchronization')
        c.argument('start_time', help='start time of synchronization')
        c.argument('status', help='Raw Status')
        c.argument('synchronization_id', help='Synchronization id')

    with self.argument_context('datashare provider-share-subscription list') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_name', help='The name of the share.')
        c.argument('skip_token', help='Continuation Token')

    with self.argument_context('datashare provider-share-subscription show') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_name', help='The name of the share.')
        c.argument('provider_share_subscription_id', help='To locate shareSubscription')

    with self.argument_context('datashare provider-share-subscription revoke') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_name', help='The name of the share.')
        c.argument('provider_share_subscription_id', help='To locate shareSubscription')

    with self.argument_context('datashare provider-share-subscription reinstate') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_name', help='The name of the share.')
        c.argument('provider_share_subscription_id', help='To locate shareSubscription')

    with self.argument_context('datashare share-subscription list') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('skip_token', help='Continuation Token')

    with self.argument_context('datashare share-subscription show') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of the shareSubscription.')

    with self.argument_context('datashare share-subscription create') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of the shareSubscription.')
        c.argument('properties_invitation_id', help='The invitation id.')
        c.argument('properties_source_share_location', help='Source share location.')

    with self.argument_context('datashare share-subscription delete') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of the shareSubscription.')

    with self.argument_context('datashare share-subscription list-source-share-synchronization-setting') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of the shareSubscription.')
        c.argument('skip_token', help='Continuation token')

    with self.argument_context('datashare share-subscription list-synchronization') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of the share subscription.')
        c.argument('skip_token', help='Continuation token')

    with self.argument_context('datashare share-subscription list-synchronization-detail') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of the share subscription.')
        c.argument('skip_token', help='Continuation token')
        c.argument('synchronization_id', help='Synchronization id')

    with self.argument_context('datashare share-subscription synchronize') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of share subscription')
        c.argument('synchronization_mode', arg_type=get_enum_type(['Incremental', 'FullSync']), help='Mode of synchroni'
                   'zation used in triggers and snapshot sync. Incremental by default')

    with self.argument_context('datashare share-subscription cancel-synchronization') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of the shareSubscription.')
        c.argument('synchronization_id', help='Synchronization id')

    with self.argument_context('datashare consumer-source-data-set list') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of the shareSubscription.')
        c.argument('skip_token', help='Continuation token')

    with self.argument_context('datashare synchronization-setting list') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_name', help='The name of the share.')
        c.argument('skip_token', help='continuation token')

    with self.argument_context('datashare synchronization-setting show') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_name', help='The name of the share.')
        c.argument('synchronization_setting_name', help='The name of the synchronizationSetting.')

    with self.argument_context('datashare synchronization-setting create') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_name', help='The name of the share to add the synchronization setting to.')
        c.argument('synchronization_setting_name', help='The name of the synchronizationSetting.')
        c.argument('synchronization_setting', arg_type=CLIArgumentType(options_list=['--synchronization-setting'],
                   help='The new synchronization setting information.'))

    with self.argument_context('datashare synchronization-setting delete') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_name', help='The name of the share.')
        c.argument('synchronization_setting_name', help='The name of the synchronizationSetting .')

    with self.argument_context('datashare trigger list') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of the share subscription.')
        c.argument('skip_token', help='Continuation token')

    with self.argument_context('datashare trigger show') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of the shareSubscription.')
        c.argument('trigger_name', help='The name of the trigger.')

    with self.argument_context('datashare trigger create') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of the share subscription which will hold the data set sin'
                   'k.')
        c.argument('trigger_name', help='The name of the trigger.')
        c.argument('trigger', arg_type=CLIArgumentType(options_list=['--trigger'], help='Trigger details.'))

    with self.argument_context('datashare trigger delete') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of the shareSubscription.')
        c.argument('trigger_name', help='The name of the trigger.')
