# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.parameters import (tags_type, get_enum_type, resource_group_name_type, name_type)

from azext_servicebus._validators import _validate_auto_delete_on_idle, \
    _validate_duplicate_detection_history_time_window, _validate_default_message_time_to_live, _validate_lock_duration


# pylint: disable=line-too-long
def load_arguments_namespace(self, _):

    with self.argument_context('servicebus') as c:
        c.argument('resource_group_name', arg_type=resource_group_name_type)
        c.argument('namespace_name', options_list=['--namespace-name'], help='name of the Namespace')

    with self.argument_context('servicebus namespace create') as c:
        c.argument('namespace_name', options_list=['--name', '-n'], help='name of the Namespace')
        c.argument('tags', options_list=['--tags', '-t'], arg_type=tags_type, help='tags for the namespace in '
                                                                                   'Key value pair format')
        c.argument('sku', options_list=['--sku-name'], arg_type=get_enum_type(['Basic', 'Standard', 'Premium']))
        c.argument('location', options_list=['--location', '-l'], help='Location')
        c.argument('skutier', options_list=['--sku-tier'], arg_type=get_enum_type(['Basic', 'Standard', 'Premium']))
        c.argument('capacity', options_list=['--capacity'], help='Capacity for Sku')

    # region Namespace Get
    for scope in ['servicebus namespace show', 'servicebus namespace delete']:
        with self.argument_context(scope) as c:
            c.argument('namespace_name', options_list=['--name', '-n'], help='name of the Namespace')

    # region Namespace Authorizationrule
    with self.argument_context('servicebus namespace authorizationrule') as c:
        c.argument('authorization_rule_name', options_list=['--name', '-n'], help='name of the Namespace AuthorizationRule')

    with self.argument_context('servicebus namespace authorizationrule create') as c:
        c.argument('accessrights', options_list=['--access-rights'],
                   help='Authorization rule rights of type list, allowed values are Send, Listen or Manage')

    with self.argument_context('servicebus namespace authorizationrule keys renew') as c:
        c.argument('key_type', options_list=['--key-name'], arg_type=get_enum_type(['PrimaryKey', 'SecondaryKey']))


def load_arguments_queue(self, _):
    # region Queue
    with self.argument_context('servicebus queue') as c:
        c.argument('queue_name', options_list=['--name', '-n'], help='Name of Queue')

    # region - Queue Create
    with self.argument_context('servicebus queue create') as c:
        c.argument('lock_duration', options_list=['--lock-duration'], validator=_validate_lock_duration, help='String ISO 8601 timespan duration of a peek-lock; that is, the amount of time that the message is locked for other receivers. The maximum value for LockDuration is 5 minutes; the default value is 1 minute.')
        c.argument('max_size_in_megabytes', options_list=['--max-size-in-megabytes'], type=int, choices=[1024, 2048, 3072, 4096, 5120], help='The maximum size of the queue in megabytes, which is the size of memory allocated for the queue. Default is 1024.')
        c.argument('requires_duplicate_detection', options_list=['--requires-duplicate-detection'], action='store_true', help='A boolean value indicating if this queue requires duplicate detection.')
        c.argument('requires_session', options_list=['--requires-session'], action='store_true', help='A boolean value that indicates whether the queue supports the concept of sessions.')
        c.argument('default_message_time_to_live', options_list=['--default-message-time-to-live'], validator=_validate_default_message_time_to_live, help='ISO 8601 default message timespan to live value. This is the duration after which the message expires, starting from when the message is sent to Service Bus. This is the default value used when TimeToLive is not set on a message itself.')
        c.argument('dead_lettering_on_message_expiration', options_list=['--dead-lettering-on-message-expiration'], action='store_true', help='A boolean value that indicates whether this queue has dead letter support when a message expires.')
        c.argument('duplicate_detection_history_time_window', options_list=['--duplicate-detection-history-time-window'], validator=_validate_duplicate_detection_history_time_window, help='ISO 8601 timeSpan structure that defines the duration of the duplicate detection history. The default value is 10 minutes.')
        c.argument('max_delivery_count', options_list=['--max-delivery-count'], type=int, help='The maximum delivery count. A message is automatically deadlettered after this number of deliveries. default value is 10.')
        c.argument('status', options_list=['--status'], arg_type=get_enum_type(['Active', 'Disabled', 'Restoring', 'SendDisabled', 'ReceiveDisabled', 'Creating', 'Deleting', 'Renaming', 'Unknown']), help='Enumerates the possible values for the status of a messaging entity.')
        c.argument('auto_delete_on_idle', options_list=['--auto-delete-on-idle'], validator=_validate_auto_delete_on_idle, help='ISO 8601 timeSpan idle interval after which the queue is automatically deleted. The minimum duration is 5 minutes.')
        c.argument('enable_partitioning', options_list=['--enable-partitioning'], action='store_true', help='A boolean value that indicates whether the queue is to be partitioned across multiple message brokers.')
        c.argument('enable_express', options_list=['--enable-express'], action='store_true', help='A boolean value that indicates whether Express Entities are enabled. An express queue holds a message in memory temporarily before writing it to persistent storage.')
        c.argument('forward_to', options_list=['--forward-to'], arg_type=name_type, help='Queue/Topic name to forward the messages')
        c.argument('forward_dead_lettered_messages_to', arg_type=name_type, options_list=['--forward-dead-lettered-messages-to'], help='Queue/Topic name to forward the Dead Letter message')

    # region Queue Authorizationrule
    with self.argument_context('servicebus queue authorizationrule') as c:
        c.argument('authorization_rule_name', options_list=['--name', '-n'], help='name of the Queue AuthorizationRule')
        c.argument('queue_name', options_list=['--queue-name'], help='name of the Queue')

    with self.argument_context('servicebus queue authorizationrule create') as c:
        c.argument('accessrights', options_list=['--access-rights'], help='Authorization rule rights of type list, allowed values are Send, Listen or Manage')

    with self.argument_context('servicebus queue authorizationrule keys renew') as c:
        c.argument('key_type', options_list=['--key-name'], arg_type=get_enum_type(['PrimaryKey', 'SecondaryKey']))


# - Topic Region
def load_arguments_topic(self, _):
    # region Topic Get
    with self.argument_context('servicebus topic') as c:
        c.argument('topic_name', options_list=['--name', '-n'], help='Topic Name')

    # region - Topic Create
    with self.argument_context('servicebus topic create') as c:
        c.argument('default_message_time_to_live', options_list=['--default-message-time-to-live'], validator=_validate_default_message_time_to_live, help='ISO 8601 Default message timespan to live value. This is the duration after which the message expires, starting from when the message is sent to Service Bus. This is the default value used when TimeToLive is not set on a message itself.')
        c.argument('max_size_in_megabytes', options_list=['--max-size-in-megabytes'], choices=[1024, 2048, 3072, 4096, 5120], help='Maximum size of the topic in megabytes, which is the size of the memory allocated for the topic. Default is 1024.')
        c.argument('requires_duplicate_detection', options_list=['--requires-duplicate-detection'], action='store_true', help='Value indicating if this topic requires duplicate detection.')
        c.argument('duplicate_detection_history_time_window', options_list=['--duplicate-detection-history-time-window'], validator=_validate_duplicate_detection_history_time_window, help='ISO8601 timespan structure that defines the duration of the duplicate detection history. The default value is 10 minutes.')
        c.argument('enable_batched_operations', options_list=['--enable-batched-operations'], action='store_true', help='Value that indicates whether server-side batched operations are enabled.')
        c.argument('status', options_list=['--status'], arg_type=get_enum_type(['Active', 'Disabled', 'Restoring', 'SendDisabled', 'ReceiveDisabled', 'Creating', 'Deleting', 'Renaming', 'Unknown']), help='Enumerates the possible values for the status of a messaging entity.')
        c.argument('support_ordering', options_list=['--support-ordering'], action='store_true', help='Value that indicates whether the topic supports ordering.')
        c.argument('auto_delete_on_idle', options_list=['--auto-delete-on-idle'], validator=_validate_auto_delete_on_idle, help='ISO 8601 timespan idle interval after which the topic is automatically deleted. The minimum duration is 5 minutes.')
        c.argument('enable_partitioning', options_list=['--enable-partitioning'], action='store_true', help='Value that indicates whether the topic to be partitioned across multiple message brokers is enabled.')
        c.argument('enable_express', options_list=['--enable-express'], action='store_true', help='Value that indicates whether Express Entities are enabled. An express topic holds a message in memory temporarily before writing it to persistent storage.')

    # region Topic Authorizationrule
    with self.argument_context('servicebus topic authorizationrule') as c:
        c.argument('authorization_rule_name', options_list=['--name', '-n'], help='name of the Topic AuthorizationRule')
        c.argument('topic_name', options_list=['--topic-name'], help='name of the Topic')

    with self.argument_context('servicebus topic authorizationrule create') as c:
        c.argument('accessrights', options_list=['--access-rights'], help='Authorization rule rights of type list, allowed values are Send, Listen or Manage')

    with self.argument_context('servicebus topic authorizationrule keys renew') as c:
        c.argument('key_type', options_list=['--key-name'], arg_type=get_enum_type(['PrimaryKey', 'SecondaryKey']))


# Subscription Region
def load_arguments_subscription(self, _):
    with self.argument_context('servicebus subscription') as c:
        c.argument('subscription_name', options_list=['--name', '-n'], help='Subscription Name')
        c.argument('topic_name', options_list=['--topic-name'], help='Topic Name')

    # region - Subscription Create
    with self.argument_context('servicebus subscription create') as c:
        c.argument('lock_duration', options_list=['--lock-duration'], validator=_validate_lock_duration, help='ISO 8601 lock duration timespan for the subscription. The default value is 1 minute.')
        c.argument('requires_session', options_list=['--enable-express'], action='store_true', help='A boolean value that indicates whether Express Entities are enabled. An express queue holds a message in memory temporarily before writing it to persistent storage.')
        c.argument('default_message_time_to_live', options_list=['--default-message-time-to-live'], validator=_validate_default_message_time_to_live, help='ISO 8601 Default message timespan to live value. This is the duration after which the message expires, starting from when the message is sent to Service Bus. This is the default value used when TimeToLive is not set on a message itself.')
        c.argument('dead_lettering_on_message_expiration', options_list=['--dead-lettering-on-message-expiration'], action='store_true', help='A boolean Value that indicates whether a subscription has dead letter support when a message expires.')
        c.argument('duplicate_detection_history_time_window', options_list=['--duplicate-detection-history-time-window'], validator=_validate_duplicate_detection_history_time_window, help='ISO 8601 timeSpan structure that defines the duration of the duplicate detection history. The default value is 10 minutes.')
        c.argument('max_delivery_count', options_list=['--max-delivery-count'], type=int, help='Number of maximum deliveries.')
        c.argument('status', options_list=['--status'], arg_type=get_enum_type(['Active', 'Disabled', 'Restoring', 'SendDisabled', 'ReceiveDisabled', 'Creating', 'Deleting', 'Renaming', 'Unknown']))
        c.argument('enable_batched_operations', action='store_true', options_list=['--enable-batched-operations'], help='Value that indicates whether server-side batched operations are enabled.')
        c.argument('auto_delete_on_idle', validator=_validate_auto_delete_on_idle, options_list=['--auto-delete-on-idle'], help='ISO 8601 timeSpan idle interval after which the topic is automatically deleted. The minimum duration is 5 minutes.')
        c.argument('forward_to', options_list=['--forward-to'], help='Queue/Topic name to forward the messages')
        c.argument('forward_dead_lettered_messages_to', options_list=['--forward-dead-lettered-messages-to'], help='Queue/Topic name to forward the Dead Letter message')

# ### Region Subscription Rules
# Rules Create


def load_arguments_rule(self, _):
    with self.argument_context('servicebus rule') as c:
        c.argument('topic_name', options_list=['--topic-name'], help='Topic Name')
        c.argument('subscription_name', options_list=['--subscription-name'], help='Subscription Name')
        c.argument('rule_name', options_list=['--name', '-n'], help='Rule Name')

    with self.argument_context('servicebus rule create') as c:
        c.argument('action_sql_expression', options_list=['--action-sql-expression'], help='Action SQL expression.')
        c.argument('action_compatibility_level', options_list=['--action-compatibility-level'], type=int, help='This property is reserved for future use. An integer value showing the compatibility level, currently hard-coded to 20.')
        c.argument('action_requires_preprocessing', action='store_true', options_list=['--action-requires-preprocessing'], help='Value that indicates whether the rule action requires preprocessing.')
        c.argument('filter_sql_expression', options_list=['--filter-sql-expression'], help='SQL expression. e.g.')
        c.argument('filter_requires_preprocessing', action='store_true', options_list=['--sql-requires-preprocessing'], help='Value that indicates whether the rule action requires preprocessing.')
        c.argument('correlation_id', options_list=['--correlation-id'], help='Identifier of the correlation.')
        c.argument('message_id', options_list=['--message-id'], help='Identifier of the message.')
        c.argument('to', options_list=['--to'], help='Address to send to.')
        c.argument('reply_to', options_list=['--reply-to'], help='Address of the queue to reply to.')
        c.argument('label', options_list=['--label'], help='Application specific label.')
        c.argument('session_id', options_list=['--session-id'], help='Session identifier')
        c.argument('reply_to_session_d', options_list=['--reply-to-session-id'], help='Session identifier to reply to.')
        c.argument('content_type', options_list=['--content-type'], help='Content type of the message.')
        c.argument('requires_preprocessing', action='store_true', options_list=['--requires-preprocessing'], help='Value that indicates whether the rule action requires preprocessing.')

    with self.argument_context('servicebus rules list') as c:
        c.argument('topic_name', options_list=['--topic-name'], help='Topic Name')
        c.argument('subscription_name', options_list=['--subscription-name'], help='Subscription Name')


# # # # Geo DR - Disaster Recovery Configs - Alias  : Region

def load_arguments_geodr(self, _):
    with self.argument_context('servicebus georecovery-alias exists') as c:
        c.argument('name', options_list=['--name', '-n'], help='Name of the Alias (Disaster Recovery) to check availability')

    with self.argument_context('servicebus georecovery-alias') as c:
        c.argument('alias', options_list=['--alias'], help='Name of the Alias (Disaster Recovery)')

    with self.argument_context('servicebus georecovery-alias create') as c:
        c.argument('alias', options_list=['--alias'], help='Name of the Alias (Disaster Recovery)')
        c.argument('partner_namespace', options_list=['--partner-namespace'], help='ARM Id of the Primary/Secondary eventhub namespace name, which is part of GEO DR pairing')
        c.argument('alternate_name', options_list=['--alternate-name'], help='Alternate Name for the Alias, when the Namespace name and Alias name are same')

    for scope in ['servicebus georecovery-alias authorizationrule show', 'servicebus georecovery-alias authorizationrule keys list']:
        with self.argument_context(scope)as c:
            c.argument('authorization_rule_name', options_list=['--name', '-n'], help='name of the Namespace AuthorizationRule')
