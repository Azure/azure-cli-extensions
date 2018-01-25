# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.parameters import (tags_type, get_enum_type, resource_group_name_type)


# pylint: disable=line-too-long
def load_arguments_namespace(self, _):
    with self.argument_context('eventhubs') as c:
        c.argument('resource_group_name', arg_type=resource_group_name_type)
        c.argument('namespace_name', options_list=['--namespace-name'], help='name of the Namespace')

    with self.argument_context('eventhubs namespace exists') as c:
        c.argument('namespace_name', options_list=['--name', '-n'], help='name of the Namespace')

    with self.argument_context('eventhubs namespace create') as c:
        c.argument('namespace_name', options_list=['--name', '-n'], help='name of the Namespace')
        c.argument('tags', options_list=['--tags', '-t'], arg_type=tags_type, help='tags for the namespace in Key value pair format')
        c.argument('sku', options_list=['--sku-name'], arg_type=get_enum_type(['Basic', 'Standard']))
        c.argument('location', options_list=['--location', '-l'], help='Location')
        c.argument('skutier', options_list=['--sku-tier'], arg_type=get_enum_type(['Basic', 'Standard']))
        c.argument('capacity', options_list=['--capacity'], type=int, help='Capacity for Sku')
        c.argument('is_auto_inflate_enabled', options_list=['--is-auto-inflate-enabled'], type=bool, help='Value that indicates whether AutoInflate is enabled for eventhub namespace.')
        c.argument('maximum_throughput_units', options_list=['--maximum-throughput-units'], type=int, help='Upper limit of throughput units when AutoInflate is enabled, vaule should be within 0 to 20 throughput units. ( 0 if AutoInflateEnabled = true)')

    # region Namespace Get
    for scope in ['eventhubs namespace show', 'eventhubs namespace delete']:
        with self.argument_context(scope) as c:
            c.argument('namespace_name', options_list=['--name', '-n'], help='name of the Namespace')

    # region Namespace Authorizationrule
    for scope in ['eventhubs namespace authorizationrule', 'eventhubs namespace authorizationrule keys list', 'eventhubs namespace authorizationrule keys renew']:
        with self.argument_context(scope) as c:
            c.argument('authorization_rule_name', options_list=['--name', '-n'], help='name of the Namespace AuthorizationRule')

    with self.argument_context('eventhubs namespace authorizationrule create') as c:
        c.argument('accessrights', options_list=['--access-rights'], arg_type=get_enum_type(['Send', 'Listen', 'Manage']), help='Authorization rule rights of type list')

    with self.argument_context('eventhubs namespace authorizationrule keys renew') as c:
        c.argument('key_type', options_list=['--key-name'], arg_type=get_enum_type(['PrimaryKey', 'SecondaryKey']), help='specifies Primary or Secondary key needs to be reset')


# region - Eventhub Create
def load_arguments_eventhub(self, _):
    with self.argument_context('eventhubs eventhub') as c:
        c.argument('event_hub_name', options_list=['--name', '-n'], help='Name of Eventhub')

    with self.argument_context('eventhubs eventhub create') as c:
        c.argument('message_retention_in_days', options_list=['--message-retention-in-days'], type=int, help='Number of days to retain the events for this Event Hub, value should be 1 to 7 days')
        c.argument('partition_count', options_list=['--partition-count'], type=int, help='Number of partitions created for the Event Hub, allowed values are from 1 to 32 partitions.')
        c.argument('status', options_list=['--status'], arg_type=get_enum_type(['Active', 'Disabled', 'Restoring', 'SendDisabled', 'ReceiveDisabled', 'Creating', 'Deleting', 'Renaming', 'Unknown']), help='Status of Eventhub')
        c.argument('enabled', options_list=['--enabled'], type=bool, help='A value that indicates whether capture description is enabled.')
        c.argument('encoding', options_list=['--encoding'], arg_type=get_enum_type(['Avro']), help='Enumerates the possible values for the encoding format of capture description.')
        c.argument('capture_interval_seconds', type=int, options_list=['--capture-interval-seconds'], help='The time window allows you to set the frequency with which the capture to Azure Blobs will happen, value should between 60 to 900 seconds')
        c.argument('capture_size_limit_bytes', options_list=['--capture-size-limit-bytes'], type=int, help='The size window defines the amount of data built up in your Event Hub before an capture operation, value should be between 10485760 to 524288000 bytes')
        c.argument('destination_name', options_list=['--destination-name'], help='Name for capture destination')
        c.argument('storage_account_resource_id', options_list=['--storage-account-resource-id'], help='Resource id of the storage account to be used to create the blobs')
        c.argument('blob_container', options_list=['--blob-container'], help='Blob container Name')
        c.argument('archive_name_format', options_list=['--archive-name-format'], help='Blob naming convention for archive, e.g. {Namespace}/{EventHub}/{PartitionId}/{Year}/{Month}/{Day}/{Hour}/{Minute}/{Second}. Here all the parameters (Namespace,EventHub .. etc) are mandatory irrespective of order')

    # region EventHub Authorizationrule
    for scope in ['eventhubs eventhub authorizationrule', 'eventhubs eventhub authorizationrule keys list', 'eventhubs eventhub authorizationrule keys renew']:
        with self.argument_context(scope) as c:
            c.argument('authorization_rule_name', options_list=['--name', '-n'], help='name of the EventHub AuthorizationRule')
            c.argument('event_hub_name', options_list=['--event-hub-name'], help='name of the EventHub')

    with self.argument_context('eventhubs eventhub authorizationrule create') as c:
        c.argument('accessrights', options_list=['--access-rights'], arg_type=get_enum_type(['Send', 'Listen', 'Manage']), help='AuthorizationRule rights of type list')

    with self.argument_context('eventhubs eventhub authorizationrule keys renew') as c:
        c.argument('key_type', options_list=['--key-name'], arg_type=get_enum_type(['PrimaryKey', 'SecondaryKey']))


# - ConsumerGroup Region
def load_arguments_consumergroup(self, _):
    with self.argument_context('eventhubs consumergroup') as c:
        c.argument('event_hub_name', options_list=['--event-hub-name'], help='name of the Eventhub')
        c.argument('consumer_group_name', options_list=['--name', '-n'], help='Name of ConsumerGroup')

    with self.argument_context('eventhubs consumergroup create') as c:
        c.argument('user_metadata', options_list=['--user-metadata'], help='Usermetadata is a placeholder to store user-defined string data with maximum length 1024. e.g. it can be used to store descriptive data, such as list of teams and their contact information also user-defined configuration settings can be stored.')

    with self.argument_context('eventhubs consumergroup list') as c:
        c.argument('event_hub_name', options_list=['--event-hub-name'], help='name of the EventHub')


#   : Region
def load_arguments_geodr(self, _):
    with self.argument_context('eventhubs georecovery-alias') as c:
        c.argument('alias', options_list=['--alias'], help='Name of the Alias (Disaster Recovery)')

    with self.argument_context('eventhubs georecovery-alias exists') as c:
        c.argument('name', options_list=['--name', '-n'], help='Name of the Geo Recovery Configs - Alias to check availability')

    with self.argument_context('eventhubs georecovery-alias create') as c:
        c.argument('partner_namespace', options_list=['--partner-namespace'], help='ARM Id of the Primary/Secondary eventhub namespace name, which is part of GEO DR pairing')
        c.argument('alternate_name', options_list=['--alternate-name'], help='Alternate Name for the Alias, when the Namespace name and Alias name are same')

    for scope in ['eventhubs georecovery-alias authorizationrule show', 'eventhubs georecovery-alias authorizationrule keys lists']:
        with self.argument_context(scope)as c:
            c.argument('authorization_rule_name', options_list=['--name', '-n'], help='name of the Namespace AuthorizationRule')
