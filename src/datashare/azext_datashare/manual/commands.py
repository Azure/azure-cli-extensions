# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements

from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):

    from azext_datashare.generated._client_factory import cf_account
    datashare_account = CliCommandType(
        operations_tmpl='azext_datashare.vendored_sdks.datashare.operations._account_operations#AccountOperations.{}',
        client_factory=cf_account)
    with self.command_group('datashare account', datashare_account, client_factory=cf_account) as g:
        g.custom_command('list', 'datashare_account_list')
        g.custom_show_command('show', 'datashare_account_show')
        g.custom_command('create', 'datashare_account_create', supports_no_wait=True)
        g.custom_command('update', 'datashare_account_update')
        g.custom_command('delete', 'datashare_account_delete', supports_no_wait=True, confirmation=True)
        g.wait_command('wait')

    from azext_datashare.generated._client_factory import cf_consumer_invitation
    datashare_consumer_invitation = CliCommandType(
        operations_tmpl='azext_datashare.vendored_sdks.datashare.operations._consumer_invitation_operations#ConsumerInvitationOperations.{}',
        client_factory=cf_consumer_invitation)
    with self.command_group('datashare consumer invitation', datashare_consumer_invitation, client_factory=cf_consumer_invitation) as g:
        g.custom_command('list', 'datashare_consumer_invitation_list')
        g.custom_show_command('show', 'datashare_consumer_invitation_show')
        g.custom_command('reject', 'datashare_consumer_invitation_reject_invitation')

    from azext_datashare.generated._client_factory import cf_data_set
    datashare_data_set = CliCommandType(
        operations_tmpl='azext_datashare.vendored_sdks.datashare.operations._data_set_operations#DataSetOperations.{}',
        client_factory=cf_data_set)
    with self.command_group('datashare dataset', datashare_data_set, client_factory=cf_data_set) as g:  # modified
        g.custom_command('list', 'datashare_data_set_list')
        g.custom_show_command('show', 'datashare_data_set_show')
        g.custom_command('create', 'datashare_data_set_create')
        g.custom_command('delete', 'datashare_data_set_delete', supports_no_wait=True, confirmation=True)
        g.wait_command('wait')

    from azext_datashare.generated._client_factory import cf_data_set_mapping
    datashare_data_set_mapping = CliCommandType(
        operations_tmpl='azext_datashare.vendored_sdks.datashare.operations._data_set_mapping_operations#DataSetMappingOperations.{}',
        client_factory=cf_data_set_mapping)
    with self.command_group('datashare consumer dataset-mapping', datashare_data_set_mapping, client_factory=cf_data_set_mapping) as g:  # modified
        g.custom_command('list', 'datashare_data_set_mapping_list')
        g.custom_show_command('show', 'datashare_data_set_mapping_show')
        g.custom_command('create', 'datashare_data_set_mapping_create')
        g.custom_command('delete', 'datashare_data_set_mapping_delete', confirmation=True)

    from azext_datashare.generated._client_factory import cf_invitation
    datashare_invitation = CliCommandType(
        operations_tmpl='azext_datashare.vendored_sdks.datashare.operations._invitation_operations#InvitationOperations.{}',
        client_factory=cf_invitation)
    with self.command_group('datashare invitation', datashare_invitation, client_factory=cf_invitation) as g:
        g.custom_command('list', 'datashare_invitation_list')
        g.custom_show_command('show', 'datashare_invitation_show')
        g.custom_command('create', 'datashare_invitation_create')
        g.custom_command('delete', 'datashare_invitation_delete', confirmation=True)

    from azext_datashare.generated._client_factory import cf_share
    datashare_share = CliCommandType(
        operations_tmpl='azext_datashare.vendored_sdks.datashare.operations._share_operations#ShareOperations.{}',
        client_factory=cf_share)
    with self.command_group('datashare', datashare_share, client_factory=cf_share, is_experimental=True) as g:  # modified
        g.custom_command('list', 'datashare_share_list')
        g.custom_show_command('show', 'datashare_share_show')
        g.custom_command('create', 'datashare_share_create')
        g.custom_command('delete', 'datashare_share_delete', supports_no_wait=True, confirmation=True)
        g.wait_command('wait')

    with self.command_group('datashare synchronization', datashare_share, client_factory=cf_share, is_experimental=True) as g:
        g.custom_command('list-detail', 'datashare_share_list_synchronization_detail')
        g.custom_command('list', 'datashare_share_list_synchronization')

    from azext_datashare.generated._client_factory import cf_provider_share_subscription
    datashare_provider_share_subscription = CliCommandType(
        operations_tmpl='azext_datashare.vendored_sdks.datashare.operations._provider_share_subscription_operations#ProviderShareSubscriptionOperations.{}',
        client_factory=cf_provider_share_subscription)
    with self.command_group('datashare provider-share-subscription', datashare_provider_share_subscription, client_factory=cf_provider_share_subscription) as g:
        g.custom_command('list', 'datashare_provider_share_subscription_list')
        g.custom_show_command('show', 'datashare_provider_share_subscription_show')
        g.custom_command('revoke', 'datashare_provider_share_subscription_revoke', supports_no_wait=True)
        g.custom_command('reinstate', 'datashare_provider_share_subscription_reinstate')
        g.wait_command('wait', getter_name='get_by_share')

    from azext_datashare.generated._client_factory import cf_share_subscription
    datashare_share_subscription = CliCommandType(
        operations_tmpl='azext_datashare.vendored_sdks.datashare.operations._share_subscription_operations#ShareSubscriptionOperations.{}',
        client_factory=cf_share_subscription)
    with self.command_group('datashare consumer share-subscription', datashare_share_subscription, client_factory=cf_share_subscription) as g:
        g.custom_command('list', 'datashare_share_subscription_list')
        g.custom_show_command('show', 'datashare_share_subscription_show')
        g.custom_command('create', 'datashare_share_subscription_create')
        g.custom_command('delete', 'datashare_share_subscription_delete', supports_no_wait=True, confirmation=True)
        g.custom_command('list-source-share-synchronization-setting', 'datashare_share_subscription_list_source_share_synchronization_setting')
        g.wait_command('wait')

    with self.command_group('datashare consumer share-subscription synchronization', datashare_share_subscription, client_factory=cf_share_subscription) as g:
        g.custom_command('list', 'datashare_share_subscription_list_synchronization')
        g.custom_command('list-detail', 'datashare_share_subscription_list_synchronization_detail')
        g.custom_command('start', 'datashare_share_subscription_synchronize', supports_no_wait=True)
        g.custom_command('cancel', 'datashare_share_subscription_cancel_synchronization', supports_no_wait=True)
        g.custom_wait_command('wait', '_datashare_share_subscription_get_synchronization')

    from azext_datashare.generated._client_factory import cf_consumer_source_data_set
    datashare_consumer_source_data_set = CliCommandType(
        operations_tmpl='azext_datashare.vendored_sdks.datashare.operations._consumer_source_data_set_operations#ConsumerSourceDataSetOperations.{}',
        client_factory=cf_consumer_source_data_set)
    with self.command_group('datashare consumer share-subscription', datashare_consumer_source_data_set, client_factory=cf_consumer_source_data_set) as g:
        g.custom_command('list-source-dataset', 'datashare_consumer_source_data_set_list')

    from azext_datashare.generated._client_factory import cf_synchronization_setting
    datashare_synchronization_setting = CliCommandType(
        operations_tmpl='azext_datashare.vendored_sdks.datashare.operations._synchronization_setting_operations#SynchronizationSettingOperations.{}',
        client_factory=cf_synchronization_setting)
    with self.command_group('datashare synchronization-setting', datashare_synchronization_setting, client_factory=cf_synchronization_setting) as g:
        g.custom_command('list', 'datashare_synchronization_setting_list')
        g.custom_show_command('show', 'datashare_synchronization_setting_show')
        g.custom_command('create', 'datashare_synchronization_setting_create')
        g.custom_command('delete', 'datashare_synchronization_setting_delete', supports_no_wait=True, confirmation=True)
        g.wait_command('wait')

    from azext_datashare.generated._client_factory import cf_trigger
    datashare_trigger = CliCommandType(
        operations_tmpl='azext_datashare.vendored_sdks.datashare.operations._trigger_operations#TriggerOperations.{}',
        client_factory=cf_trigger)
    with self.command_group('datashare consumer trigger', datashare_trigger, client_factory=cf_trigger) as g:
        g.custom_command('list', 'datashare_trigger_list')
        g.custom_show_command('show', 'datashare_trigger_show')
        g.custom_command('create', 'datashare_trigger_create', supports_no_wait=True)
        g.custom_command('delete', 'datashare_trigger_delete', supports_no_wait=True, confirmation=True)
        g.wait_command('wait')
