# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=unused-argument
from azure.cli.core.util import sdk_no_wait


def datashare_account_list(cmd, client,
                           resource_group_name=None):
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name=resource_group_name)
    return client.list_by_subscription()


def datashare_account_show(cmd, client,
                           resource_group_name,
                           account_name):
    return client.get(resource_group_name=resource_group_name, account_name=account_name)


def datashare_account_create(cmd, client,
                             resource_group_name,
                             account_name,
                             identity=None,
                             location=None,
                             tags=None,
                             no_wait=False):
    if identity is None:
        identity = {'type': 'SystemAssigned'}
    return sdk_no_wait(no_wait,
                       client.begin_create,
                       resource_group_name=resource_group_name,
                       account_name=account_name,
                       location=location,
                       tags=tags,
                       identity=identity)


def datashare_account_update(cmd, client,
                             resource_group_name,
                             account_name,
                             tags=None):
    return client.update(resource_group_name=resource_group_name, account_name=account_name, tags=tags)


def datashare_account_delete(cmd, client,
                             resource_group_name,
                             account_name,
                             no_wait=False):
    return sdk_no_wait(no_wait,
                       client.begin_delete,
                       resource_group_name=resource_group_name,
                       account_name=account_name)


def datashare_consumer_invitation_list(cmd, client):
    return client.list_invitation()


def datashare_consumer_invitation_show(cmd, client,
                                       location,
                                       invitation_id):
    return client.get(location=location, invitation_id=invitation_id)


def datashare_consumer_invitation_reject_invitation(cmd, client,
                                                    location,
                                                    invitation_id):
    return client.reject_invitation(location=location, invitation_id=invitation_id)


def datashare_data_set_list(cmd, client,
                            resource_group_name,
                            account_name,
                            share_name):
    return client.list_by_share(resource_group_name=resource_group_name,
                                account_name=account_name,
                                share_name=share_name)


def datashare_data_set_show(cmd, client,
                            resource_group_name,
                            account_name,
                            share_name,
                            data_set_name):
    return client.get(resource_group_name=resource_group_name, account_name=account_name, share_name=share_name, data_set_name=data_set_name)


def datashare_data_set_create(cmd, client,
                              resource_group_name,
                              account_name,
                              share_name,
                              data_set_name,
                              data_set):
    from azure.cli.core.commands.client_factory import get_subscription_id
    if 'resource_group' not in data_set:
        data_set['resource_group'] = resource_group_name
    if 'subscription_id' not in data_set:
        data_set['subscription_id'] = get_subscription_id(cmd.cli_ctx)
    return client.create(resource_group_name=resource_group_name,
                         account_name=account_name,
                         share_name=share_name,
                         data_set_name=data_set_name,
                         data_set=data_set)


def datashare_data_set_delete(cmd, client,
                              resource_group_name,
                              account_name,
                              share_name,
                              data_set_name,
                              no_wait=False):
    return sdk_no_wait(no_wait,
                       client.begin_delete,
                       resource_group_name=resource_group_name,
                       account_name=account_name,
                       share_name=share_name,
                       data_set_name=data_set_name)


def datashare_data_set_mapping_list(cmd, client,
                                    resource_group_name,
                                    account_name,
                                    share_subscription_name):
    return client.list_by_share_subscription(resource_group_name=resource_group_name,
                                             account_name=account_name,
                                             share_subscription_name=share_subscription_name)


def datashare_data_set_mapping_show(cmd, client,
                                    resource_group_name,
                                    account_name,
                                    share_subscription_name,
                                    data_set_mapping_name):
    return client.get(resource_group_name=resource_group_name, account_name=account_name, share_subscription_name=share_subscription_name, data_set_mapping_name=data_set_mapping_name)


def datashare_data_set_mapping_create(cmd, client,
                                      resource_group_name,
                                      account_name,
                                      share_subscription_name,
                                      data_set_mapping_name,
                                      data_set_mapping):
    from azure.cli.core.commands.client_factory import get_subscription_id
    if 'resource_group' not in data_set_mapping:
        data_set_mapping['resource_group'] = resource_group_name
    if 'subscription_id' not in data_set_mapping:
        data_set_mapping['subscription_id'] = get_subscription_id(cmd.cli_ctx)
    return client.create(resource_group_name=resource_group_name,
                         account_name=account_name,
                         share_subscription_name=share_subscription_name,
                         data_set_mapping_name=data_set_mapping_name,
                         data_set_mapping=data_set_mapping)


def datashare_data_set_mapping_delete(cmd, client,
                                      resource_group_name,
                                      account_name,
                                      share_subscription_name,
                                      data_set_mapping_name):
    return client.delete(resource_group_name=resource_group_name, account_name=account_name, share_subscription_name=share_subscription_name, data_set_mapping_name=data_set_mapping_name)


def datashare_invitation_list(cmd, client,
                              resource_group_name,
                              account_name,
                              share_name):
    return client.list_by_share(resource_group_name=resource_group_name,
                                account_name=account_name,
                                share_name=share_name)


def datashare_invitation_show(cmd, client,
                              resource_group_name,
                              account_name,
                              share_name,
                              invitation_name):
    return client.get(resource_group_name=resource_group_name, account_name=account_name, share_name=share_name, invitation_name=invitation_name)


def datashare_invitation_create(cmd, client,
                                resource_group_name,
                                account_name,
                                share_name,
                                invitation_name,
                                target_active_directory_id=None,
                                target_email=None,
                                target_object_id=None):
    return client.create(resource_group_name=resource_group_name, account_name=account_name, share_name=share_name, invitation_name=invitation_name, target_active_directory_id=target_active_directory_id, target_email=target_email, target_object_id=target_object_id)


def datashare_invitation_delete(cmd, client,
                                resource_group_name,
                                account_name,
                                share_name,
                                invitation_name):
    return client.delete(resource_group_name=resource_group_name, account_name=account_name, share_name=share_name, invitation_name=invitation_name)


def datashare_share_list(cmd, client,
                         resource_group_name,
                         account_name):
    return client.list_by_account(resource_group_name=resource_group_name, account_name=account_name)


def datashare_share_show(cmd, client,
                         resource_group_name,
                         account_name,
                         share_name):
    return client.get(resource_group_name=resource_group_name, account_name=account_name, share_name=share_name)


def datashare_share_create(cmd, client,
                           resource_group_name,
                           account_name,
                           share_name,
                           description=None,
                           share_kind=None,
                           terms=None):
    return client.create(resource_group_name=resource_group_name, account_name=account_name, share_name=share_name, description=description, share_kind=share_kind, terms=terms)


def datashare_share_delete(cmd, client,
                           resource_group_name,
                           account_name,
                           share_name,
                           no_wait=False):
    return sdk_no_wait(no_wait,
                       client.begin_delete,
                       resource_group_name=resource_group_name,
                       account_name=account_name,
                       share_name=share_name)


def datashare_share_list_synchronization_detail(cmd, client,
                                                resource_group_name,
                                                account_name,
                                                share_name,
                                                synchronization_id=None):
    return client.list_synchronization_detail(resource_group_name=resource_group_name,
                                              account_name=account_name,
                                              share_name=share_name,
                                              synchronization_id=synchronization_id)


def datashare_share_list_synchronization(cmd, client,
                                         resource_group_name,
                                         account_name,
                                         share_name):
    return client.list_synchronization(resource_group_name=resource_group_name,
                                       account_name=account_name,
                                       share_name=share_name)


def datashare_provider_share_subscription_list(cmd, client,
                                               resource_group_name,
                                               account_name,
                                               share_name):
    return client.list_by_share(resource_group_name=resource_group_name,
                                account_name=account_name,
                                share_name=share_name)


def datashare_provider_share_subscription_show(cmd, client,
                                               resource_group_name,
                                               account_name,
                                               share_name,
                                               provider_share_subscription_id):
    return client.get_by_share(resource_group_name=resource_group_name, account_name=account_name, share_name=share_name, provider_share_subscription_id=provider_share_subscription_id)


def datashare_provider_share_subscription_revoke(cmd, client,
                                                 resource_group_name,
                                                 account_name,
                                                 share_name,
                                                 provider_share_subscription_id,
                                                 no_wait=False):
    return sdk_no_wait(no_wait,
                       client.begin_revoke,
                       resource_group_name=resource_group_name,
                       account_name=account_name,
                       share_name=share_name,
                       provider_share_subscription_id=provider_share_subscription_id)


def datashare_provider_share_subscription_reinstate(cmd, client,
                                                    resource_group_name,
                                                    account_name,
                                                    share_name,
                                                    provider_share_subscription_id):
    return client.reinstate(resource_group_name=resource_group_name, account_name=account_name, share_name=share_name, provider_share_subscription_id=provider_share_subscription_id)


def datashare_share_subscription_list(cmd, client,
                                      resource_group_name,
                                      account_name):
    return client.list_by_account(resource_group_name=resource_group_name, account_name=account_name)


def datashare_share_subscription_show(cmd, client,
                                      resource_group_name,
                                      account_name,
                                      share_subscription_name):
    return client.get(resource_group_name=resource_group_name, account_name=account_name, share_subscription_name=share_subscription_name)


def datashare_share_subscription_create(cmd, client,
                                        resource_group_name,
                                        account_name,
                                        share_subscription_name,
                                        invitation_id,
                                        source_share_location):
    return client.create(resource_group_name=resource_group_name, account_name=account_name, share_subscription_name=share_subscription_name, invitation_id=invitation_id, source_share_location=source_share_location)


def datashare_share_subscription_delete(cmd, client,
                                        resource_group_name,
                                        account_name,
                                        share_subscription_name,
                                        no_wait=False):
    return sdk_no_wait(no_wait,
                       client.begin_delete,
                       resource_group_name=resource_group_name,
                       account_name=account_name,
                       share_subscription_name=share_subscription_name)


def datashare_share_subscription_list_synchronization_detail(cmd, client,
                                                             resource_group_name,
                                                             account_name,
                                                             share_subscription_name,
                                                             synchronization_id):
    return client.list_synchronization_detail(resource_group_name=resource_group_name,
                                              account_name=account_name,
                                              share_subscription_name=share_subscription_name,
                                              synchronization_id=synchronization_id)


def datashare_share_subscription_synchronize(cmd, client,
                                             resource_group_name,
                                             account_name,
                                             share_subscription_name,
                                             synchronization_mode=None,
                                             no_wait=False):
    return sdk_no_wait(no_wait,
                       client.begin_synchronize,
                       resource_group_name=resource_group_name,
                       account_name=account_name,
                       share_subscription_name=share_subscription_name,
                       synchronization_mode=synchronization_mode)


def datashare_share_subscription_cancel_synchronization(cmd, client,
                                                        resource_group_name,
                                                        account_name,
                                                        share_subscription_name,
                                                        synchronization_id,
                                                        no_wait=False):
    return sdk_no_wait(no_wait,
                       client.begin_cancel_synchronization,
                       resource_group_name=resource_group_name,
                       account_name=account_name,
                       share_subscription_name=share_subscription_name,
                       synchronization_id=synchronization_id)


def datashare_share_subscription_list_source_share_synchronization_setting(cmd, client,
                                                                           resource_group_name,
                                                                           account_name,
                                                                           share_subscription_name):
    return client.list_source_share_synchronization_setting(resource_group_name=resource_group_name,
                                                            account_name=account_name,
                                                            share_subscription_name=share_subscription_name)


def datashare_share_subscription_list_synchronization(cmd, client,
                                                      resource_group_name,
                                                      account_name,
                                                      share_subscription_name):
    return client.list_synchronization(resource_group_name=resource_group_name,
                                       account_name=account_name,
                                       share_subscription_name=share_subscription_name)


def _datashare_share_subscription_get_synchronization(cmd, client,
                                                      resource_group_name,
                                                      account_name,
                                                      share_subscription_name,
                                                      synchronization_id):
    from knack.util import todict
    from azure.cli.core.commands import AzCliCommandInvoker
    result = client.list_synchronization(resource_group_name=resource_group_name,
                                         account_name=account_name,
                                         share_subscription_name=share_subscription_name)
    result = todict(list(result), AzCliCommandInvoker.remove_additional_prop_layer)
    return next((x for x in result if x['synchronizationId'] == synchronization_id), None)


def datashare_consumer_source_data_set_list(cmd, client,
                                            resource_group_name,
                                            account_name,
                                            share_subscription_name):
    return client.list_by_share_subscription(resource_group_name=resource_group_name, account_name=account_name, share_subscription_name=share_subscription_name)


def datashare_synchronization_setting_list(cmd, client,
                                           resource_group_name,
                                           account_name,
                                           share_name):
    return client.list_by_share(resource_group_name=resource_group_name,
                                account_name=account_name,
                                share_name=share_name)


def datashare_synchronization_setting_show(cmd, client,
                                           resource_group_name,
                                           account_name,
                                           share_name,
                                           synchronization_setting_name):
    return client.get(resource_group_name=resource_group_name, account_name=account_name, share_name=share_name, synchronization_setting_name=synchronization_setting_name)


# def _format_datetime(date_string):
#     from dateutil.parser import parse
#     try:
#         return parse(date_string).strftime("%Y-%m-%dT%H:%M:%SZ")
#     except ValueError:
#         # logger.debug("Unable to parse date_string '%s'", date_string)
#         return date_string or ' '


def datashare_synchronization_setting_create(cmd, client,
                                             resource_group_name,
                                             account_name,
                                             share_name,
                                             synchronization_setting_name,
                                             recurrence_interval,
                                             synchronization_time,
                                             kind=None):
    synchronization_setting = {
        'synchronizationTime': synchronization_time,
        'recurrenceInterval': recurrence_interval,
        'kind': kind
    }
    return client.create(resource_group_name=resource_group_name,
                         account_name=account_name,
                         share_name=share_name,
                         synchronization_setting_name=synchronization_setting_name,
                         synchronization_setting=synchronization_setting)


def datashare_synchronization_setting_delete(cmd, client,
                                             resource_group_name,
                                             account_name,
                                             share_name,
                                             synchronization_setting_name,
                                             no_wait=False):
    return sdk_no_wait(no_wait,
                       client.begin_delete,
                       resource_group_name=resource_group_name,
                       account_name=account_name,
                       share_name=share_name,
                       synchronization_setting_name=synchronization_setting_name)


def datashare_trigger_list(cmd, client,
                           resource_group_name,
                           account_name,
                           share_subscription_name):
    return client.list_by_share_subscription(resource_group_name=resource_group_name,
                                             account_name=account_name,
                                             share_subscription_name=share_subscription_name)


def datashare_trigger_show(cmd, client,
                           resource_group_name,
                           account_name,
                           share_subscription_name,
                           trigger_name):
    return client.get(resource_group_name=resource_group_name, account_name=account_name, share_subscription_name=share_subscription_name, trigger_name=trigger_name)


def datashare_trigger_create(cmd, client,
                             resource_group_name,
                             account_name,
                             share_subscription_name,
                             trigger_name,
                             recurrence_interval,
                             synchronization_time,
                             kind=None,
                             no_wait=False):
    synchronization_setting = {
        'synchronizationTime': synchronization_time,
        'recurrenceInterval': recurrence_interval,
        'kind': kind
    }
    return sdk_no_wait(no_wait,
                       client.begin_create,
                       resource_group_name=resource_group_name,
                       account_name=account_name,
                       share_subscription_name=share_subscription_name,
                       trigger_name=trigger_name,
                       trigger=synchronization_setting)


def datashare_trigger_delete(cmd, client,
                             resource_group_name,
                             account_name,
                             share_subscription_name,
                             trigger_name,
                             no_wait=False):
    return sdk_no_wait(no_wait,
                       client.begin_delete,
                       resource_group_name=resource_group_name,
                       account_name=account_name,
                       share_subscription_name=share_subscription_name,
                       trigger_name=trigger_name)
