# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=unused-argument


def datashare_account_list(cmd, client,
                           resource_group_name=None,
                           skip_token=None):
    if resource_group_name is not None:
        return client.list_by_resource_group(resource_group_name=resource_group_name, skip_token=skip_token)
    return client.list_by_subscription(skip_token=skip_token)


def datashare_account_show(cmd, client,
                           resource_group_name,
                           account_name):
    return client.get(resource_group_name=resource_group_name, account_name=account_name)


def datashare_account_create(cmd, client,
                             resource_group_name,
                             account_name,
                             identity,
                             location=None,
                             tags=None):
    return client.begin_create(resource_group_name=resource_group_name, account_name=account_name, location=location, tags=tags, identity=identity)


def datashare_account_update(cmd, client,
                             resource_group_name,
                             account_name,
                             tags=None):
    return client.update(resource_group_name=resource_group_name, account_name=account_name, tags=tags)


def datashare_account_delete(cmd, client,
                             resource_group_name,
                             account_name):
    return client.begin_delete(resource_group_name=resource_group_name, account_name=account_name)


def datashare_consumer_invitation_list(cmd, client,
                                       skip_token=None):
    return client.list_invitation(skip_token=skip_token)


def datashare_consumer_invitation_show(cmd, client,
                                       location,
                                       invitation_id):
    return client.get(location=location, invitation_id=invitation_id)


def datashare_consumer_invitation_reject_invitation(cmd, client,
                                                    location,
                                                    properties_invitation_id):
    return client.reject_invitation(location=location, invitation_id=properties_invitation_id)


def datashare_data_set_list(cmd, client,
                            resource_group_name,
                            account_name,
                            share_name,
                            skip_token=None):
    return client.list_by_share(resource_group_name=resource_group_name, account_name=account_name, share_name=share_name, skip_token=skip_token)


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
                              kind):
    return client.create(resource_group_name=resource_group_name, account_name=account_name, share_name=share_name, data_set_name=data_set_name, kind=kind)


def datashare_data_set_delete(cmd, client,
                              resource_group_name,
                              account_name,
                              share_name,
                              data_set_name):
    return client.begin_delete(resource_group_name=resource_group_name, account_name=account_name, share_name=share_name, data_set_name=data_set_name)


def datashare_data_set_mapping_list(cmd, client,
                                    resource_group_name,
                                    account_name,
                                    share_subscription_name,
                                    skip_token=None):
    return client.list_by_share_subscription(resource_group_name=resource_group_name, account_name=account_name, share_subscription_name=share_subscription_name, skip_token=skip_token)


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
                                      kind):
    return client.create(resource_group_name=resource_group_name, account_name=account_name, share_subscription_name=share_subscription_name, data_set_mapping_name=data_set_mapping_name, kind=kind)


def datashare_data_set_mapping_delete(cmd, client,
                                      resource_group_name,
                                      account_name,
                                      share_subscription_name,
                                      data_set_mapping_name):
    return client.delete(resource_group_name=resource_group_name, account_name=account_name, share_subscription_name=share_subscription_name, data_set_mapping_name=data_set_mapping_name)


def datashare_invitation_list(cmd, client,
                              resource_group_name,
                              account_name,
                              share_name,
                              skip_token=None):
    return client.list_by_share(resource_group_name=resource_group_name, account_name=account_name, share_name=share_name, skip_token=skip_token)


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
                                properties_target_active_directory_id=None,
                                properties_target_email=None,
                                properties_target_object_id=None):
    return client.create(resource_group_name=resource_group_name, account_name=account_name, share_name=share_name, invitation_name=invitation_name, target_active_directory_id=properties_target_active_directory_id, target_email=properties_target_email, target_object_id=properties_target_object_id)


def datashare_invitation_delete(cmd, client,
                                resource_group_name,
                                account_name,
                                share_name,
                                invitation_name):
    return client.delete(resource_group_name=resource_group_name, account_name=account_name, share_name=share_name, invitation_name=invitation_name)


def datashare_share_list(cmd, client,
                         resource_group_name,
                         account_name,
                         skip_token=None):
    return client.list_by_account(resource_group_name=resource_group_name, account_name=account_name, skip_token=skip_token)


def datashare_share_show(cmd, client,
                         resource_group_name,
                         account_name,
                         share_name):
    return client.get(resource_group_name=resource_group_name, account_name=account_name, share_name=share_name)


def datashare_share_create(cmd, client,
                           resource_group_name,
                           account_name,
                           share_name,
                           properties_description=None,
                           properties_share_kind=None,
                           properties_terms=None):
    return client.create(resource_group_name=resource_group_name, account_name=account_name, share_name=share_name, description=properties_description, share_kind=properties_share_kind, terms=properties_terms)


def datashare_share_delete(cmd, client,
                           resource_group_name,
                           account_name,
                           share_name):
    return client.begin_delete(resource_group_name=resource_group_name, account_name=account_name, share_name=share_name)


def datashare_share_list_synchronization_detail(cmd, client,
                                                resource_group_name,
                                                account_name,
                                                share_name,
                                                skip_token=None,
                                                consumer_email=None,
                                                consumer_name=None,
                                                consumer_tenant_name=None,
                                                duration_ms=None,
                                                end_time=None,
                                                message=None,
                                                start_time=None,
                                                status=None,
                                                synchronization_id=None):
    return client.list_synchronization_detail(resource_group_name=resource_group_name, account_name=account_name, share_name=share_name, skip_token=skip_token, consumer_email=consumer_email, consumer_name=consumer_name, consumer_tenant_name=consumer_tenant_name, duration_ms=duration_ms, end_time=end_time, message=message, start_time=start_time, status=status, synchronization_id=synchronization_id)


def datashare_share_list_synchronization(cmd, client,
                                         resource_group_name,
                                         account_name,
                                         share_name,
                                         skip_token=None):
    return client.list_synchronization(resource_group_name=resource_group_name, account_name=account_name, share_name=share_name, skip_token=skip_token)


def datashare_provider_share_subscription_list(cmd, client,
                                               resource_group_name,
                                               account_name,
                                               share_name,
                                               skip_token=None):
    return client.list_by_share(resource_group_name=resource_group_name, account_name=account_name, share_name=share_name, skip_token=skip_token)


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
                                                 provider_share_subscription_id):
    return client.begin_revoke(resource_group_name=resource_group_name, account_name=account_name, share_name=share_name, provider_share_subscription_id=provider_share_subscription_id)


def datashare_provider_share_subscription_reinstate(cmd, client,
                                                    resource_group_name,
                                                    account_name,
                                                    share_name,
                                                    provider_share_subscription_id):
    return client.reinstate(resource_group_name=resource_group_name, account_name=account_name, share_name=share_name, provider_share_subscription_id=provider_share_subscription_id)


def datashare_share_subscription_list(cmd, client,
                                      resource_group_name,
                                      account_name,
                                      skip_token=None):
    return client.list_by_account(resource_group_name=resource_group_name, account_name=account_name, skip_token=skip_token)


def datashare_share_subscription_show(cmd, client,
                                      resource_group_name,
                                      account_name,
                                      share_subscription_name):
    return client.get(resource_group_name=resource_group_name, account_name=account_name, share_subscription_name=share_subscription_name)


def datashare_share_subscription_create(cmd, client,
                                        resource_group_name,
                                        account_name,
                                        share_subscription_name,
                                        properties_invitation_id,
                                        properties_source_share_location):
    return client.create(resource_group_name=resource_group_name, account_name=account_name, share_subscription_name=share_subscription_name, invitation_id=properties_invitation_id, source_share_location=properties_source_share_location)


def datashare_share_subscription_delete(cmd, client,
                                        resource_group_name,
                                        account_name,
                                        share_subscription_name):
    return client.begin_delete(resource_group_name=resource_group_name, account_name=account_name, share_subscription_name=share_subscription_name)


def datashare_share_subscription_list_synchronization_detail(cmd, client,
                                                             resource_group_name,
                                                             account_name,
                                                             share_subscription_name,
                                                             synchronization_id,
                                                             skip_token=None):
    return client.list_synchronization_detail(resource_group_name=resource_group_name, account_name=account_name, share_subscription_name=share_subscription_name, skip_token=skip_token, synchronization_id=synchronization_id)


def datashare_share_subscription_synchronize(cmd, client,
                                             resource_group_name,
                                             account_name,
                                             share_subscription_name,
                                             synchronization_mode=None):
    return client.begin_synchronize(resource_group_name=resource_group_name, account_name=account_name, share_subscription_name=share_subscription_name, synchronization_mode=synchronization_mode)


def datashare_share_subscription_cancel_synchronization(cmd, client,
                                                        resource_group_name,
                                                        account_name,
                                                        share_subscription_name,
                                                        synchronization_id):
    return client.begin_cancel_synchronization(resource_group_name=resource_group_name, account_name=account_name, share_subscription_name=share_subscription_name, synchronization_id=synchronization_id)


def datashare_share_subscription_list_source_share_synchronization_setting(cmd, client,
                                                                           resource_group_name,
                                                                           account_name,
                                                                           share_subscription_name,
                                                                           skip_token=None):
    return client.list_source_share_synchronization_setting(resource_group_name=resource_group_name, account_name=account_name, share_subscription_name=share_subscription_name, skip_token=skip_token)


def datashare_share_subscription_list_synchronization(cmd, client,
                                                      resource_group_name,
                                                      account_name,
                                                      share_subscription_name,
                                                      skip_token=None):
    return client.list_synchronization(resource_group_name=resource_group_name, account_name=account_name, share_subscription_name=share_subscription_name, skip_token=skip_token)


def datashare_consumer_source_data_set_list(cmd, client,
                                            resource_group_name,
                                            account_name,
                                            share_subscription_name,
                                            skip_token=None):
    return client.list_by_share_subscription(resource_group_name=resource_group_name, account_name=account_name, share_subscription_name=share_subscription_name, skip_token=skip_token)


def datashare_synchronization_setting_list(cmd, client,
                                           resource_group_name,
                                           account_name,
                                           share_name,
                                           skip_token=None):
    return client.list_by_share(resource_group_name=resource_group_name, account_name=account_name, share_name=share_name, skip_token=skip_token)


def datashare_synchronization_setting_show(cmd, client,
                                           resource_group_name,
                                           account_name,
                                           share_name,
                                           synchronization_setting_name):
    return client.get(resource_group_name=resource_group_name, account_name=account_name, share_name=share_name, synchronization_setting_name=synchronization_setting_name)


def datashare_synchronization_setting_create(cmd, client,
                                             resource_group_name,
                                             account_name,
                                             share_name,
                                             synchronization_setting_name,
                                             kind):
    return client.create(resource_group_name=resource_group_name, account_name=account_name, share_name=share_name, synchronization_setting_name=synchronization_setting_name, kind=kind)


def datashare_synchronization_setting_delete(cmd, client,
                                             resource_group_name,
                                             account_name,
                                             share_name,
                                             synchronization_setting_name):
    return client.begin_delete(resource_group_name=resource_group_name, account_name=account_name, share_name=share_name, synchronization_setting_name=synchronization_setting_name)


def datashare_trigger_list(cmd, client,
                           resource_group_name,
                           account_name,
                           share_subscription_name,
                           skip_token=None):
    return client.list_by_share_subscription(resource_group_name=resource_group_name, account_name=account_name, share_subscription_name=share_subscription_name, skip_token=skip_token)


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
                             kind):
    return client.begin_create(resource_group_name=resource_group_name, account_name=account_name, share_subscription_name=share_subscription_name, trigger_name=trigger_name, kind=kind)


def datashare_trigger_delete(cmd, client,
                             resource_group_name,
                             account_name,
                             share_subscription_name,
                             trigger_name):
    return client.begin_delete(resource_group_name=resource_group_name, account_name=account_name, share_subscription_name=share_subscription_name, trigger_name=trigger_name)
