# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from knack.arguments import CLIArgumentType
from azure.cli.core.commands.parameters import (
    tags_type,
    get_enum_type,
    resource_group_name_type,
    get_location_type
)
from azure.cli.core.commands.validators import get_default_location_from_resource_group, validate_file_or_dict
from azext_datashare.action import AddIdentity
from ..vendored_sdks.datashare.models._data_share_management_client_enums import ShareKind, Kind, SynchronizationMode

dataset_type = CLIArgumentType(
    type=validate_file_or_dict,
    options_list=['--dataset'],
    help='Dataset parameters in JSON string or path to JSON file.'
)

def load_arguments(self, _):

    with self.argument_context('datashare account list') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('skip_token', help='Continuation token')

    with self.argument_context('datashare account show') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', options_list=['--name', '-n'], id_part='name', help='The name of the share account.')  # modified

    with self.argument_context('datashare account create') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', options_list=['--name', '-n'], help='The name of the share account.')  # modified
        c.argument('location', arg_type=get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)  # modified
        c.argument('tags', tags_type)  # modified
        c.argument('identity', action=AddIdentity, nargs='+', help='Identity of resource')

    with self.argument_context('datashare account update') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', options_list=['--name', '-n'], id_part='name', help='The name of the share account.')  # modified
        c.argument('tags', tags_type, help='Tags on the azure resource.')

    with self.argument_context('datashare account delete') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', options_list=['--name', '-n'], id_part='name', help='The name of the share account.')

    with self.argument_context('datashare account wait') as c:
        c.argument('account_name', options_list=['--name', '-n'], id_part='name', help='The name of the share account.')  # modified

    with self.argument_context('datashare consumer-invitation list') as c:
        c.argument('skip_token', help='Continuation token')

    with self.argument_context('datashare consumer-invitation show') as c:
        c.argument('location', arg_type=get_location_type(self.cli_ctx))  # modified
        c.argument('invitation_id', help='An invitation id')

    with self.argument_context('datashare consumer-invitation reject-invitation') as c:
        c.argument('location', arg_type=get_location_type(self.cli_ctx))  # modified
        c.argument('invitation_id', help='Unique id of the invitation.')  # modified

    with self.argument_context('datashare dataset list') as c:  # modified
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_name', help='The name of the share.')
        c.argument('skip_token', help='Continuation token')

    with self.argument_context('datashare dataset show') as c:  # modified
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', id_part='name', help='The name of the share account.')  # modified
        c.argument('share_name', id_part='child_name_1', help='The name of the share.')  # modified
        c.argument('data_set_name', options_list=['--name', '-n'], id_part='child_name_2', help='The name of the dataSet.')  # modified

    with self.argument_context('datashare dataset create') as c:  # modified
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_name', help='The name of the share.')
        c.argument('data_set_name', options_list=['--name', '-n'], help='The name of the dataSet.')  # modified
        c.argument('kind', arg_type=get_enum_type(Kind), help='Kind of data set.')  # modified
        c.argument('dataset', arg_type=dataset_type)  # modified

    with self.argument_context('datashare dataset delete') as c:  # modified
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', id_part='name', help='The name of the share account.')  # modified
        c.argument('share_name', id_part='child_name_1', help='The name of the share.')  # modified
        c.argument('data_set_name', options_list=['--name', '-n'], id_part='child_name_2', help='The name of the dataSet.')  # modified

    with self.argument_context('datashare dataset-mapping list') as c:  # modified
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of the shareSubscription.')
        c.argument('skip_token', help='Continuation token')

    with self.argument_context('datashare dataset-mapping show') as c:  # modified
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of the shareSubscription.')
        c.argument('data_set_mapping_name', options_list=['--name', '-n'], help='The name of the dataSetMapping.')  # modified

    with self.argument_context('datashare dataset-mapping create') as c:  # modified
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of the shareSubscription.')
        c.argument('data_set_mapping_name', options_list=['--name', '-n'], help='The name of the dataSetMapping.')  # modified
        c.argument('kind', arg_type=get_enum_type(Kind), help='Kind of data set.')  # modified

    with self.argument_context('datashare dataset-mapping delete') as c:  # modified
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of the shareSubscription.')
        c.argument('data_set_mapping_name', options_list=['--name', '-n'], help='The name of the dataSetMapping.')  # modified

    with self.argument_context('datashare invitation list') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_name', help='The name of the share.')
        c.argument('skip_token', help='Continuation token')

    with self.argument_context('datashare invitation show') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', id_part='name', help='The name of the share account.')  # modified
        c.argument('share_name', id_part='child_name_1', help='The name of the share.')  # modified
        c.argument('invitation_name', options_list=['--name', '-n'], id_part='child_name_2', help='The name of the invitation.')  # modified

    with self.argument_context('datashare invitation create') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_name', help='The name of the share.')
        c.argument('invitation_name', options_list=['--name', '-n'], help='The name of the invitation.')  # modified
        c.argument('target_active_directory_id', help='The target Azure AD Id. Can\'t be combined with email.')  # modified
        c.argument('target_email', help='The email the invitation is directed to.')  # modified
        c.argument('target_object_id', help='The target user or application Id that invitation is being sent to. Must be specified along TargetActiveDirectoryId. This enables sending invitations to specific users or applications in an AD tenant.')  # modified

    with self.argument_context('datashare invitation delete') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', id_part='name', help='The name of the share account.')  # modified
        c.argument('share_name', id_part='child_name_1', help='The name of the share.')  # modified
        c.argument('invitation_name', options_list=['--name', '-n'], id_part='child_name_2', help='The name of the invitation.')  # modified

    with self.argument_context('datashare list') as c:  # modified
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')
        c.argument('skip_token', help='Continuation token')

    with self.argument_context('datashare show') as c:  # modified
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', id_part='name', help='The name of the share account.')  # modified
        c.argument('share_name', options_list=['--name', '-n'], id_part='child_name_1', help='The name of the share.')  # modified

    with self.argument_context('datashare create') as c:  # modified
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_name', options_list=['--name', '-n'], help='The name of the share.')  # modified
        c.argument('description', help='Share description.')  # modified
        c.argument('share_kind', arg_type=get_enum_type(ShareKind), help='Share kind.')  # modified
        c.argument('terms', help='Share terms.')  # modified

    with self.argument_context('datashare delete') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', id_part='name', help='The name of the share account.')  # modified
        c.argument('share_name', options_list=['--name', '-n'], id_part='child_name_1', help='The name of the share.')  # modified

    with self.argument_context('datashare list-synchronization-detail') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', id_part='name', help='The name of the share account.')  # modified
        c.argument('share_name', options_list=['--name', '-n'], id_part='child_name_1', help='The name of the share.')  # modified
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

    with self.argument_context('datashare list-synchronization') as c:  # modified
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', id_part='name', help='The name of the share account.')  # modified
        c.argument('share_name', options_list=['--name', '-n'], id_part='child_name_1', help='The name of the share.')  # modified
        c.argument('skip_token', help='Continuation token')

    with self.argument_context('datashare provider-share-subscription list') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_name', help='The name of the share.')
        c.argument('skip_token', help='Continuation token')

    with self.argument_context('datashare provider-share-subscription show') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', id_part='name', help='The name of the share account.')  # modified
        c.argument('share_name', id_part='child_name_1', help='The name of the share.')  # modified
        c.argument('provider_share_subscription_id', options_list=['--share-subscription'], id_part='child_name_2', help='To locate shareSubscription')  # modified

    with self.argument_context('datashare provider-share-subscription revoke') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', id_part='name', help='The name of the share account.')  # modified
        c.argument('share_name', id_part='child_name_1', help='The name of the share.')  # modified
        c.argument('provider_share_subscription_id', options_list=['--share-subscription'], id_part='child_name_2', help='To locate shareSubscription')  # modified

    with self.argument_context('datashare provider-share-subscription reinstate') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', id_part='name', help='The name of the share account.')  # modified
        c.argument('share_name', id_part='child_name_1', help='The name of the share.')  # modified
        c.argument('provider_share_subscription_id', options_list=['--share-subscription'], id_part='child_name_2', help='To locate shareSubscription')  # modified

    with self.argument_context('datashare share-subscription list') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')
        c.argument('skip_token', help='Continuation token')

    with self.argument_context('datashare share-subscription show') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', id_part='name', help='The name of the share account.')  # modified
        c.argument('share_subscription_name', options_list=['--name', '-n'], id_part='child_name_1', help='The name of the shareSubscription.')  # modified

    with self.argument_context('datashare share-subscription create') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of the shareSubscription.')  # modified
        c.argument('invitation_id', help='The invitation id.')  # modified
        c.argument('source_share_location', help='Source share location.')  # modified

    with self.argument_context('datashare share-subscription delete') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', id_part='name', help='The name of the share account.')  # modified
        c.argument('share_subscription_name', options_list=['--name', '-n'], id_part='child_name_1', help='The name of the shareSubscription.')  # modified

    with self.argument_context('datashare share-subscription list-synchronization-detail') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of the shareSubscription.')
        c.argument('skip_token', help='Continuation token')
        c.argument('synchronization_id', help='Synchronization id')

    with self.argument_context('datashare share-subscription synchronize') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of the shareSubscription.')
        c.argument('synchronization_mode', arg_type=get_enum_type(SynchronizationMode), help='Synchronization mode')  # modified

    with self.argument_context('datashare share-subscription cancel-synchronization') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of the shareSubscription.')
        c.argument('synchronization_id', help='Synchronization id')

    with self.argument_context('datashare share-subscription list-source-share-synchronization-setting') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of the shareSubscription.')
        c.argument('skip_token', help='Continuation token')

    with self.argument_context('datashare share-subscription list-synchronization') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of the shareSubscription.')
        c.argument('skip_token', help='Continuation token')

    with self.argument_context('datashare consumer-source-dataset list') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of the shareSubscription.')
        c.argument('skip_token', help='Continuation token')

    with self.argument_context('datashare synchronization-setting list') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_name', help='The name of the share.')
        c.argument('skip_token', help='Continuation token')

    with self.argument_context('datashare synchronization-setting show') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', id_part='name', help='The name of the share account.')  # modified
        c.argument('share_name', id_part='child_name_1', help='The name of the share.')  # modified
        c.argument('synchronization_setting_name', options_list=['--name', '-n'], id_part='child_name_2', help='The name of the synchronizationSetting.')  # modified

    with self.argument_context('datashare synchronization-setting create') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_name', help='The name of the share.')
        c.argument('synchronization_setting_name', options_list=['--name', '-n'], help='The name of the synchronizationSetting.')  # modified
        c.argument('kind', arg_type=get_enum_type(Kind), help='Kind of data set.')  # modified

    with self.argument_context('datashare synchronization-setting delete') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', id_part='name', help='The name of the share account.')  # modified
        c.argument('share_name', id_part='child_name_1', help='The name of the share.')  # modified
        c.argument('synchronization_setting_name', options_list=['--name', '-n'], id_part='child_name_2', help='The name of the synchronizationSetting.')  # modified

    with self.argument_context('datashare trigger list') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of the shareSubscription.')
        c.argument('skip_token', help='Continuation token')

    with self.argument_context('datashare trigger show') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', id_part='name', help='The name of the share account.')
        c.argument('share_subscription_name', id_part='child_name_1', help='The name of the shareSubscription.')
        c.argument('trigger_name', options_list=['--name', '-n'], id_part='child_name_2', help='The name of the trigger.')

    with self.argument_context('datashare trigger create') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of the shareSubscription.')
        c.argument('trigger_name', options_list=['--name', '-n'], help='The name of the trigger.')  # modified
        c.argument('kind', arg_type=get_enum_type(Kind), help='Kind of data set.')  # modified

    with self.argument_context('datashare trigger delete') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', id_part='name', help='The name of the share account.')  # modified
        c.argument('share_subscription_name', id_part='child_name_1', help='The name of the shareSubscription.')  # modified
        c.argument('trigger_name', options_list=['--name', '-n'], id_part='child_name_2', help='The name of the trigger.')  # modified
