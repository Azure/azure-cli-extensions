# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType

from azure.cli.core.commands.parameters import (
    resource_group_name_type,
    get_resource_name_completion_list,
    get_three_state_flag,
    get_location_type,
    get_enum_type,
    tags_type,
    name_type
)

from .advanced_filter import EventSubscriptionAddFilter

included_event_types_type = CLIArgumentType(
    help="A space-separated list of event types. Example: Microsoft.Storage.BlobCreated Microsoft.Storage.BlobDeleted. To subscribe to all event types, the string \"All\" should be specified.",
    nargs='+'
)

labels_type = CLIArgumentType(
    help="A space-separated list of labels to associate with this event subscription.",
    nargs='+'
)

input_schema_type = CLIArgumentType(
    help="Schema in which incoming events will be published to this topic/domain. If you specify customeventschema as the value for this parameter, you must also provide values for at least one of --input_mapping_default_values / --input_mapping_fields.",
    arg_type=get_enum_type(['eventgridschema', 'customeventschema', 'cloudeventv01schema'], default='eventgridschema')
)

input_mapping_fields_type = CLIArgumentType(
    help="When input-schema is specified as customeventschema, this parameter is used to specify input mappings based on field names. Specify space separated mappings in 'key=value' format. Allowed key names are 'id', 'topic', 'eventtime', 'subject', 'eventtype', 'dataversion'. The corresponding value names should specify the names of the fields in the custom input schema. If a mapping for either 'id' or 'eventtime' is not provided, Event Grid will auto-generate a default value for these two fields.",
    arg_type=tags_type
)

input_mapping_default_values_type = CLIArgumentType(
    help="When input-schema is specified as customeventschema, this parameter can be used to specify input mappings based on default values. You can use this parameter when your custom schema does not include a field that corresponds to one of the three fields supported by this parameter. Specify space separated mappings in 'key=value' format. Allowed key names are 'subject', 'eventtype', 'dataversion'. The corresponding value names should specify the default values to be used for the mapping and they will be used only when the published event doesn't have a valid mapping for a particular field.",
    arg_type=tags_type
)


def load_arguments(self, _):
    with self.argument_context('eventgrid') as c:
        c.argument('resource_group_name', arg_type=resource_group_name_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', arg_type=tags_type)
        c.argument('included_event_types', arg_type=included_event_types_type)
        c.argument('labels', arg_type=labels_type)
        c.argument('endpoint_type', arg_type=get_enum_type(['webhook', 'eventhub', 'storagequeue', 'hybridconnection'], default='webhook'))
        c.argument('source_resource_id', help="Fully qualified identifier of the source Azure resource.")
        c.argument('resource_id', deprecate_info=c.deprecate(redirect="--source-resource-id", expiration='2.1.0', hide=True), help="Fully qualified identifier of the Azure resource.")
        c.argument('endpoint', help="Endpoint where EventGrid should deliver events matching this event subscription. For webhook endpoint type, this should be the corresponding webhook URL. For other endpoint types, this should be the Azure resource identifier of the endpoint.")
        c.argument('event_subscription_name', help="Name of the event subscription.")
        c.argument('subject_begins_with', help="An optional string to filter events for an event subscription based on a prefix. Wildcard characters are not supported.")
        c.argument('subject_ends_with', help="An optional string to filter events for an event subscription based on a suffix. Wildcard characters are not supported.")
        c.argument('topic_type_name', help="Name of the topic type.")
        c.argument('is_subject_case_sensitive', arg_type=get_three_state_flag(), options_list=['--subject-case-sensitive'], help="Specify to indicate whether the subject fields should be compared in a case sensitive manner. True if flag present.", )
        c.argument('input_mapping_fields', arg_type=input_mapping_fields_type)
        c.argument('input_mapping_default_values', arg_type=input_mapping_default_values_type)
        c.argument('input_schema', arg_type=input_schema_type)

    with self.argument_context('eventgrid topic') as c:
        c.argument('topic_name', arg_type=name_type, help='Name of the topic', id_part='name', completer=get_resource_name_completion_list('Microsoft.EventGrid/topics'))

    with self.argument_context('eventgrid topic key list') as c:
        c.argument('topic_name', arg_type=name_type, help='Name of the topic', id_part=None, completer=get_resource_name_completion_list('Microsoft.EventGrid/topics'))

    with self.argument_context('eventgrid domain') as c:
        c.argument('domain_name', arg_type=name_type, help='Name of the domain', id_part='name', completer=get_resource_name_completion_list('Microsoft.EventGrid/domains'))

    with self.argument_context('eventgrid domain key list') as c:
        c.argument('domain_name', arg_type=name_type, help='Name of the domain', id_part=None, completer=get_resource_name_completion_list('Microsoft.EventGrid/domains'))

    with self.argument_context('eventgrid domain topic list') as c:
        c.argument('domain_name', arg_type=name_type, help='Name of the domain', id_part=None, completer=get_resource_name_completion_list('Microsoft.EventGrid/domains'))

    with self.argument_context('eventgrid event-subscription') as c:
        c.argument('topic_name', deprecate_info=c.deprecate(expiration='2.1.0', hide=True), help='Name of Event Grid topic', options_list=['--topic-name'], completer=get_resource_name_completion_list('Microsoft.EventGrid/topics'))
        c.argument('event_subscription_name', arg_type=name_type, help='Name of the event subscription')
        c.argument('event_delivery_schema', arg_type=get_enum_type(['eventgridschema', 'custominputschema', 'cloudeventv01schema']), help='The schema in which events should be delivered for this event subscription. By default, events will be delivered in the same schema in which they are published (based on the corresponding topic\'s input schema).')
        c.argument('max_delivery_attempts', help="Maximum number of delivery attempts. Must be a number between 1 and 30.")
        c.argument('event_ttl', help="Event time to live (in minutes). Must be a number between 1 and 1440.")
        c.argument('deadletter_endpoint', help="The Azure resource ID of an Azure Storage blob container destination where EventGrid should deadletter undeliverable events for this event subscription.")
        c.argument('advanced_filter', action=EventSubscriptionAddFilter, nargs='+')
        c.argument('expiration_date', help="Date or datetime (in UTC, e.g. '2018-11-30T11:59:59+00:00' or '2018-11-30') after which the event subscription would expire. By default, there is no expiration for the event subscription.")

    with self.argument_context('eventgrid event-subscription create') as c:
        c.argument('resource_group_name', deprecate_info=c.deprecate(expiration='2.1.0', hide=True), arg_type=resource_group_name_type)

    with self.argument_context('eventgrid event-subscription delete') as c:
        c.argument('resource_group_name', deprecate_info=c.deprecate(expiration='2.1.0', hide=True), arg_type=resource_group_name_type)

    with self.argument_context('eventgrid event-subscription update') as c:
        c.argument('resource_group_name', deprecate_info=c.deprecate(expiration='2.1.0', hide=True), arg_type=resource_group_name_type)

    with self.argument_context('eventgrid event-subscription show') as c:
        c.argument('resource_group_name', deprecate_info=c.deprecate(expiration='2.1.0', hide=True), arg_type=resource_group_name_type)
        c.argument('include_full_endpoint_url', arg_type=get_three_state_flag(), options_list=['--include-full-endpoint-url'], help="Specify to indicate whether the full endpoint URL should be returned. True if flag present.", )

    with self.argument_context('eventgrid topic-type') as c:
        c.argument('topic_type_name', arg_type=name_type, help="Name of the topic type.", completer=get_resource_name_completion_list('Microsoft.EventGrid/topictypes'))
