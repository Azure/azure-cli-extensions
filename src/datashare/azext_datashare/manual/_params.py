# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=unused-import

from knack.arguments import CLIArgumentType
from azure.cli.core.commands.parameters import (
    tags_type,
    get_enum_type,
    resource_group_name_type,
    get_location_type,
    get_datetime_type
)
from azure.cli.core.commands.validators import get_default_location_from_resource_group, validate_file_or_dict
from azext_datashare.vendored_sdks.datashare.models._data_share_management_client_enums import ShareKind, Kind, SynchronizationMode, SynchronizationKind, RecurrenceInterval
from azext_datashare.manual._validators import invitation_id_validator


def load_arguments(self, _):

    with self.argument_context('datashare account list') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified

    with self.argument_context('datashare account show') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', options_list=['--name', '-n'], id_part='name', help='The name of the share account.')  # modified

    with self.argument_context('datashare account create') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', options_list=['--name', '-n'], help='The name of the share account.')  # modified
        c.argument('location', arg_type=get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)  # modified
        c.argument('tags', tags_type)  # modified
        c.ignore('identity')  # Only system assigned identity is supported, we can omit this option

    with self.argument_context('datashare account update') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', options_list=['--name', '-n'], id_part='name', help='The name of the share account.')  # modified
        c.argument('tags', tags_type)  # modified

    with self.argument_context('datashare account delete') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', options_list=['--name', '-n'], id_part='name', help='The name of the share account.')

    with self.argument_context('datashare account wait') as c:
        c.argument('account_name', options_list=['--name', '-n'], id_part='name', help='The name of the share account.')  # modified

    with self.argument_context('datashare list') as c:  # modified
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')

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

    with self.argument_context('datashare wait') as c:
        c.argument('account_name', id_part='name', help='The name of the share account.')  # modified
        c.argument('share_name', options_list=['--name', '-n'], id_part='child_name_1', help='The name of the share.')  # modified

    with self.argument_context('datashare dataset list') as c:  # modified
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_name', help='The name of the share.')

    with self.argument_context('datashare dataset show') as c:  # modified
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', id_part='name', help='The name of the share account.')  # modified
        c.argument('share_name', id_part='child_name_1', help='The name of the share.')  # modified
        c.argument('data_set_name', options_list=['--name', '-n'], id_part='child_name_2', help='The name of the dataset.')  # modified

    with self.argument_context('datashare dataset create') as c:  # modified
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_name', help='The name of the share.')
        c.argument('data_set_name', options_list=['--name', '-n'], help='The name of the dataset.')  # modified
        c.argument('data_set', options_list=['--dataset'], type=validate_file_or_dict, help='Dataset parameters in JSON string or path to JSON file.')  # modified

    with self.argument_context('datashare dataset delete') as c:  # modified
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', id_part='name', help='The name of the share account.')  # modified
        c.argument('share_name', id_part='child_name_1', help='The name of the share.')  # modified
        c.argument('data_set_name', options_list=['--name', '-n'], id_part='child_name_2', help='The name of the dataset.')  # modified

    with self.argument_context('datashare dataset wait') as c:
        c.argument('account_name', id_part='name', help='The name of the share account.')  # modified
        c.argument('share_name', id_part='child_name_1', help='The name of the share.')  # modified
        c.argument('data_set_name', options_list=['--name', '-n'], id_part='child_name_2', help='The name of the dataset.')  # modified

    with self.argument_context('datashare invitation list') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_name', help='The name of the share.')

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

    with self.argument_context('datashare synchronization-setting list') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_name', help='The name of the share.')

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
        c.argument('recurrence_interval', arg_type=get_enum_type(RecurrenceInterval), arg_group='Synchronization Setting', help='Synchronization Recurrence Interval.')
        c.argument('synchronization_time', arg_group='Synchronization Setting', arg_type=get_datetime_type(help='Synchronization time.'))
        c.argument('kind', arg_type=get_enum_type(SynchronizationKind), arg_group='Synchronization Setting', default='ScheduleBased', help='Kind of synchronization.')

    with self.argument_context('datashare synchronization-setting delete') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', id_part='name', help='The name of the share account.')  # modified
        c.argument('share_name', id_part='child_name_1', help='The name of the share.')  # modified
        c.argument('synchronization_setting_name', options_list=['--name', '-n'], id_part='child_name_2', help='The name of the synchronizationSetting.')  # modified

    with self.argument_context('datashare synchronization-setting wait') as c:
        c.argument('account_name', id_part='name', help='The name of the share account.')  # modified
        c.argument('share_name', id_part='child_name_1', help='The name of the share.')  # modified
        c.argument('synchronization_setting_name', options_list=['--name', '-n'], id_part='child_name_2', help='The name of the synchronizationSetting.')  # modified

    with self.argument_context('datashare synchronization list-detail') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')  # modified
        c.argument('share_name', help='The name of the share.')  # modified
        c.argument('synchronization_id', help='The synchronization GUID.')

    with self.argument_context('datashare synchronization list') as c:  # modified
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')  # modified
        c.argument('share_name', help='The name of the share.')  # modified

    with self.argument_context('datashare provider-share-subscription list') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_name', help='The name of the share.')

    with self.argument_context('datashare provider-share-subscription show') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', id_part='name', help='The name of the share account.')  # modified
        c.argument('share_name', id_part='child_name_1', help='The name of the share.')  # modified
        c.argument('provider_share_subscription_id', options_list=['--share-subscription'], id_part='child_name_2', help='To locate share subscription')  # modified TODO validator

    with self.argument_context('datashare provider-share-subscription revoke') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', id_part='name', help='The name of the share account.')  # modified
        c.argument('share_name', id_part='child_name_1', help='The name of the share.')  # modified
        c.argument('provider_share_subscription_id', options_list=['--share-subscription'], id_part='child_name_2', help='To locate share subscription')  # modified

    with self.argument_context('datashare provider-share-subscription reinstate') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', id_part='name', help='The name of the share account.')  # modified
        c.argument('share_name', id_part='child_name_1', help='The name of the share.')  # modified
        c.argument('provider_share_subscription_id', options_list=['--share-subscription'], id_part='child_name_2', help='To locate share subscription')  # modified

    with self.argument_context('datashare provider-share-subscription wait') as c:
        c.argument('account_name', id_part='name', help='The name of the share account.')  # modified
        c.argument('share_name', id_part='child_name_1', help='The name of the share.')  # modified
        c.argument('provider_share_subscription_id', options_list=['--share-subscription'], id_part='child_name_2', help='To locate share subscription')  # modified

    with self.argument_context('datashare consumer invitation list') as c:
        pass

    with self.argument_context('datashare consumer invitation show') as c:
        c.argument('location', arg_type=get_location_type(self.cli_ctx))  # modified
        c.argument('invitation_id', validator=invitation_id_validator, help='An invitation id')

    with self.argument_context('datashare consumer invitation reject') as c:
        c.argument('location', arg_type=get_location_type(self.cli_ctx))  # modified
        c.argument('invitation_id', validator=invitation_id_validator, help='An invitation id')  # modified

    with self.argument_context('datashare consumer share-subscription list') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')

    with self.argument_context('datashare consumer share-subscription show') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', id_part='name', help='The name of the share account.')  # modified
        c.argument('share_subscription_name', options_list=['--name', '-n'], id_part='child_name_1', help='The name of the share subscription.')  # modified

    with self.argument_context('datashare consumer share-subscription create') as c:
        from azure.cli.core.commands.parameters import get_location_name_type, get_location_completion_list
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', options_list=['--name', '-n'], help='The name of the share subscription.')  # modified
        c.argument('invitation_id', validator=invitation_id_validator, help='The invitation id.')  # modified
        c.argument('source_share_location', type=get_location_name_type(self.cli_ctx), help='Source share location.', completer=get_location_completion_list)  # modified

    with self.argument_context('datashare consumer share-subscription delete') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', id_part='name', help='The name of the share account.')  # modified
        c.argument('share_subscription_name', options_list=['--name', '-n'], id_part='child_name_1', help='The name of the share subscription.')  # modified

    with self.argument_context('datashare consumer share-subscription list-source-share-synchronization-setting') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of the share subscription.')

    with self.argument_context('datashare consumer share-subscription list-source-dataset') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of the share subscription.')

    with self.argument_context('datashare consumer share-subscription wait') as c:
        c.argument('account_name', id_part='name', help='The name of the share account.')
        c.argument('share_subscription_name', options_list=['--name', '-n'], id_part='child_name_1', help='The name of the share subscription.')  # modified

    with self.argument_context('datashare consumer share-subscription synchronization start') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of the share subscription.')
        c.argument('synchronization_mode', arg_type=get_enum_type(SynchronizationMode), help='Synchronization mode')  # modified

    with self.argument_context('datashare consumer share-subscription synchronization cancel') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of the share subscription.')
        c.argument('synchronization_id', help='The synchronization GUID')

    with self.argument_context('datashare consumer share-subscription synchronization wait') as c:
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of the share subscription.')
        c.argument('synchronization_id', help='The synchronization GUID')

    with self.argument_context('datashare consumer share-subscription synchronization list') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of the share subscription.')

    with self.argument_context('datashare consumer share-subscription synchronization list-detail') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of the share subscription.')
        c.argument('synchronization_id', help='Synchronization id')

    with self.argument_context('datashare consumer dataset-mapping list') as c:  # modified
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of the share subscription.')

    with self.argument_context('datashare consumer dataset-mapping show') as c:  # modified
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', id_part='name', help='The name of the share account.')
        c.argument('share_subscription_name', id_part='child_name_1', help='The name of the share subscription.')
        c.argument('data_set_mapping_name', id_part='child_name_2', options_list=['--name', '-n'], help='The name of the datasetMapping.')  # modified

    with self.argument_context('datashare consumer dataset-mapping create') as c:  # modified
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of the share subscription.')
        c.argument('data_set_mapping_name', options_list=['--name', '-n'], help='The name of the datasetMapping.')  # modified
        c.argument('data_set_mapping', options_list=['--mapping'], type=validate_file_or_dict, help='Dataset mapping in JSON string or path to JSON file.')  # modified

    with self.argument_context('datashare consumer dataset-mapping delete') as c:  # modified
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', id_part='name', help='The name of the share account.')
        c.argument('share_subscription_name', id_part='child_name_1', help='The name of the share subscription.')
        c.argument('data_set_mapping_name', id_part='child_name_2', options_list=['--name', '-n'], help='The name of the datasetMapping.')  # modified

    with self.argument_context('datashare consumer dataset-mapping wait') as c:
        c.argument('account_name', id_part='name', help='The name of the share account.')
        c.argument('share_subscription_name', id_part='child_name_1', help='The name of the share subscription.')
        c.argument('data_set_mapping_name', id_part='child_name_2', options_list=['--name', '-n'], help='The name of the datasetMapping.')  # modified

    with self.argument_context('datashare consumer trigger list') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of the share subscription.')

    with self.argument_context('datashare consumer trigger show') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', id_part='name', help='The name of the share account.')
        c.argument('share_subscription_name', id_part='child_name_1', help='The name of the share subscription.')
        c.argument('trigger_name', options_list=['--name', '-n'], id_part='child_name_2', help='The name of the trigger.')

    with self.argument_context('datashare consumer trigger create') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', help='The name of the share account.')
        c.argument('share_subscription_name', help='The name of the share subscription.')
        c.argument('trigger_name', options_list=['--name', '-n'], help='The name of the trigger.')  # modified
        c.argument('recurrence_interval', arg_type=get_enum_type(RecurrenceInterval), arg_group='Synchronization Setting', help='Synchronization Recurrence Interval.')
        c.argument('synchronization_time', arg_group='Synchronization Setting', arg_type=get_datetime_type(help='Synchronization time.'))
        c.argument('kind', arg_type=get_enum_type(SynchronizationKind), arg_group='Synchronization Setting', default='ScheduleBased', help='Kind of synchronization.')

    with self.argument_context('datashare consumer trigger delete') as c:
        c.argument('resource_group_name', resource_group_name_type)  # modified
        c.argument('account_name', id_part='name', help='The name of the share account.')  # modified
        c.argument('share_subscription_name', id_part='child_name_1', help='The name of the share subscription.')  # modified
        c.argument('trigger_name', options_list=['--name', '-n'], id_part='child_name_2', help='The name of the trigger.')  # modified

    with self.argument_context('datashare consumer trigger wait') as c:
        c.argument('trigger_name', options_list=['--name', '-n'], id_part='child_name_2', help='The name of the trigger.')  # modified
