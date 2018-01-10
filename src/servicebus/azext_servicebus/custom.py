# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines

from knack.util import CLIError

from azext_servicebus._utils import accessrights_converter

from azext_servicebus.servicebus.models import (SBNamespace, SBSku, SBQueue, SBTopic, SBSubscription, Rule, Action, SqlFilter, CorrelationFilter, ArmDisasterRecovery)


# Namespace Region
def cli_namespace_create(client, resource_group_name, namespace_name, location, tags=None, sku='Standard', skutier=None,
                         capacity=None):
    return client.create_or_update(resource_group_name, namespace_name, SBNamespace(location, tags,
                                                                                    SBSku(sku,
                                                                                          skutier,
                                                                                          capacity)))


def cli_namespace_list(client, resource_group_name=None, namespace_name=None):
    cmd_result = None
    if resource_group_name and namespace_name:
        cmd_result = client.get(resource_group_name, namespace_name)

    if resource_group_name and not namespace_name:
        cmd_result = client.list_by_resource_group(resource_group_name, namespace_name)

    if not resource_group_name and not namespace_name:
        cmd_result = client.list(resource_group_name, namespace_name)

    if not cmd_result:
        raise CLIError('--resource-group name required when namespace name is provided')

    return cmd_result


# Namespace Authorization rule:
def cli_namespaceautho_create(client, resource_group_name, namespace_name, name, accessrights=None):
    return client.create_or_update_authorization_rule(resource_group_name, namespace_name, name,
                                                      accessrights_converter(accessrights))


# Queue Region
def cli_sbqueue_create(client, resource_group_name, namespace_name, name, lock_duration=None,
                       max_size_in_megabytes=None, requires_duplicate_detection=None, requires_session=None,
                       default_message_time_to_live=None, dead_lettering_on_message_expiration=None,
                       duplicate_detection_history_time_window=None, max_delivery_count=None, status=None,
                       auto_delete_on_idle=None, enable_partitioning=None, enable_express=None,
                       forward_to=None, forward_dead_lettered_messages_to=None):

    queue_params = SBQueue(
        lock_duration=lock_duration,
        max_size_in_megabytes=max_size_in_megabytes,
        requires_duplicate_detection=requires_duplicate_detection,
        requires_session=requires_session,
        default_message_time_to_live=default_message_time_to_live,
        dead_lettering_on_message_expiration=dead_lettering_on_message_expiration,
        duplicate_detection_history_time_window=duplicate_detection_history_time_window,
        max_delivery_count=max_delivery_count,
        status=status,
        auto_delete_on_idle=auto_delete_on_idle,
        enable_partitioning=enable_partitioning,
        enable_express=enable_express,
        forward_to=forward_to,
        forward_dead_lettered_messages_to=forward_dead_lettered_messages_to
    )
    return client.create_or_update(resource_group_name, namespace_name, name, queue_params)


def cli_sbqueueautho_create(client, resource_group_name, namespace_name, queue_name, name, accessrights=None):
    return client.create_or_update_authorization_rule(resource_group_name, namespace_name, queue_name, name,
                                                      accessrights_converter(accessrights))


# Topic Region
def cli_sbtopic_create(client, resource_group_name, namespace_name, name, default_message_time_to_live=None,
                       max_size_in_megabytes=None, requires_duplicate_detection=None,
                       duplicate_detection_history_time_window=None,
                       enable_batched_operations=None, status=None, support_ordering=None, auto_delete_on_idle=None,
                       enable_partitioning=None, enable_express=None):
    topic_params = SBTopic(
        default_message_time_to_live=default_message_time_to_live,
        max_size_in_megabytes=max_size_in_megabytes,
        requires_duplicate_detection=requires_duplicate_detection,
        duplicate_detection_history_time_window=duplicate_detection_history_time_window,
        enable_batched_operations=enable_batched_operations,
        status=status,
        support_ordering=support_ordering,
        auto_delete_on_idle=auto_delete_on_idle,
        enable_partitioning=enable_partitioning,
        enable_express=enable_express
    )
    return client.create_or_update(resource_group_name, namespace_name, name, topic_params)


def cli_sbtopicautho_create(client, resource_group_name, namespace_name, topic_name, name, accessrights=None):
    return client.create_or_update_authorization_rule(resource_group_name, namespace_name, topic_name, name,
                                                      accessrights_converter(accessrights))


# Subscription Region
def cli_sbsubscription_create(client, resource_group_name, namespace_name, topic_name, name, lock_duration=None,
                              requires_session=None, default_message_time_to_live=None,
                              dead_lettering_on_message_expiration=None, duplicate_detection_history_time_window=None,
                              max_delivery_count=None, status=None, enable_batched_operations=None,
                              auto_delete_on_idle=None, forward_to=None, forward_dead_lettered_messages_to=None):
    subscription_params = SBSubscription(
        lock_duration=lock_duration,
        requires_session=requires_session,
        default_message_time_to_live=default_message_time_to_live,
        dead_lettering_on_message_expiration=dead_lettering_on_message_expiration,
        duplicate_detection_history_time_window=duplicate_detection_history_time_window,
        max_delivery_count=max_delivery_count,
        status=status,
        enable_batched_operations=enable_batched_operations,
        auto_delete_on_idle=auto_delete_on_idle,
        forward_to=forward_to,
        forward_dead_lettered_messages_to=forward_dead_lettered_messages_to
    )

    return client.create_or_update(resource_group_name, namespace_name, topic_name, name, subscription_params)


# Rule Region
def cli_rules_create(client, resource_group_name, namespace_name, topic_name, subscription_name, name,
                     action_sql_expression=None, action_compatibility_level=None, action_requires_preprocessing=None,
                     filter_sql_expression=None, filter_requires_preprocessing=None, correlation_id=None,
                     message_id=None, to=None, reply_to=None, label=None, session_id=None, reply_to_sessionid=None,
                     content_type=None, requires_preprocessing=None):
    rules_params = Rule()
    rules_params.action = Action(
        sql_expression=action_sql_expression,
        compatibility_level=action_compatibility_level,
        requires_preprocessing=action_requires_preprocessing
    )
    rules_params.sql_filter = SqlFilter(
        sql_expression=filter_sql_expression,
        requires_preprocessing=filter_requires_preprocessing
    )
    rules_params.correlation_filter = CorrelationFilter(
        correlation_id=correlation_id,
        to=to,
        message_id=message_id,
        reply_to=reply_to,
        label=label,
        session_id=session_id,
        reply_to_session_id=reply_to_sessionid,
        content_type=content_type,
        requires_preprocessing=requires_preprocessing
    )
    return client.create_or_update(resource_group_name, namespace_name, topic_name, subscription_name, name,
                                   rules_params)


# Geo DR - Disaster Recovery Configs - Alias Region
def cli_alias_create(client, resource_group_name, namespace_name, alias, partner_namespace, alternate_name):
    dr_params = ArmDisasterRecovery(
        partner_namespace=partner_namespace,
        alternate_name=alternate_name
    )
    return client.create_or_update(resource_group_name, namespace_name, alias, dr_params)
