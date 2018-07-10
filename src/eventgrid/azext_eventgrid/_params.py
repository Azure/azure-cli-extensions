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

included_event_types_type = CLIArgumentType(
    help="A space-separated list of event types. To subscribe to all event types, the string \"All\" should be specified.",
    nargs='+'
)

labels_type = CLIArgumentType(
    help="A space-separated list of labels to associate with this event subscription.",
    nargs='+'
)


def load_arguments(self, _):
    with self.argument_context('eventgrid') as c:
        c.argument('resource_group_name', arg_type=resource_group_name_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', arg_type=tags_type)
        c.argument('included_event_types', arg_type=included_event_types_type)
        c.argument('labels', arg_type=labels_type)
        c.argument('endpoint_type', arg_type=get_enum_type(['webhook', 'eventhub', 'storagequeue', 'hybridconnection'], default='webhook'))
        c.argument('resource_id', help="Fully qualified identifier of the Azure resource.")
        c.argument('endpoint', help="Endpoint where EventGrid should deliver events matching this event subscription. For webhook endpoint type, this should be the corresponding webhook URL. For other endpoint types, this should be the Azure resource identifier of the endpoint.")
        c.argument('event_subscription_name', help="Name of the event subscription.")
        c.argument('subject_begins_with', help="An optional string to filter events for an event subscription based on a prefix. Wildcard characters are not supported.")
        c.argument('subject_ends_with', help="An optional string to filter events for an event subscription based on a suffix. Wildcard characters are not supported.")
        c.argument('topic_type_name', help="Name of the topic type.")
        c.argument('is_subject_case_sensitive', arg_type=get_three_state_flag(), options_list=['--subject-case-sensitive'], help="Specify to indicate whether the subject fields should be compared in a case sensitive manner. True if flag present.", )

    with self.argument_context('eventgrid topic') as c:
        c.argument('topic_name', arg_type=name_type, help='Name of the topic', id_part='name', completer=get_resource_name_completion_list('Microsoft.EventGrid/topics'))
        c.argument('input_mapping_fields', arg_type=tags_type, help="When input-schema is specified as customeventschema, this parameter is used to specify input mappings based on field names. Specify space separated mappings in 'key=value' format. Allowed key names are 'id', 'topic', 'eventtime', 'subject', 'eventtype', 'dataversion'. The corresponding value names should specify the names of the fields in the custom input schema.")
        c.argument('input_mapping_default_values', arg_type=tags_type, help="When input-schema is specified as customeventschema, this parameter is used to specify input mappings based on default values. Specify space separated mappings in 'key=value' format. Allowed key names are 'subject', 'eventtype', 'dataversion'. The corresponding value names should specify the default values to be used for the mapping.")
        c.argument('input_schema', arg_type=get_enum_type(['eventgridschema', 'customeventschema', 'cloudeventv01schema'], default='eventgridschema'), help='Schema in which incoming events will be published for this topic. If customeventschema is specified, either input_mapping_default_values or input_mapping_fields must be specified as well.')

    with self.argument_context('eventgrid event-subscription') as c:
        c.argument('topic_name', help='Name of the Event Grid topic', options_list=['--topic-name'], completer=get_resource_name_completion_list('Microsoft.EventGrid/topics'))
        c.argument('event_subscription_name', arg_type=name_type, help='Name of the event subscription')
        c.argument('event_delivery_schema', arg_type=get_enum_type(['eventgridschema', 'inputeventschema', 'cloudeventv01schema'], default='inputeventschema'), help='The schema in which events should be delivered for this event subscription. By default, events are delivered in the same schema in which they are published (inputeventschema).')
        c.argument('max_delivery_attempts', help="Maximum number of delivery attempts. Must be a number between 1 and 30.")
        c.argument('event_ttl', help="Event time to live (in minutes). Must be a number between 1 and 1440.")
        c.argument('deadletter_endpoint', help="The Azure resource ID of an Azure Storage blob container destination where EventGrid should deadletter undeliverable events for this event subscription.")

    with self.argument_context('eventgrid event-subscription create') as c:
        c.argument('topic_name', help='Name of the Event Grid topic to which the event subscription needs to be created.', options_list=['--topic-name'], completer=get_resource_name_completion_list('Microsoft.EventGrid/topics'))
        c.argument('event_subscription_name', arg_type=name_type, help='Name of the new event subscription')
        c.argument('resource_id', help="Fully qualified identifier of the Azure resource to which the event subscription needs to be created.")

    with self.argument_context('eventgrid event-subscription delete') as c:
        c.argument('topic_name', help='Name of the Event Grid topic whose event subscription needs to be deleted.', options_list=['--topic-name'], completer=get_resource_name_completion_list('Microsoft.EventGrid/topics'))
        c.argument('event_subscription_name', arg_type=name_type, help='Name of the event subscription')
        c.argument('resource_id', help="Fully qualified identifier of the Azure resource whose event subscription needs to be deleted.")

    with self.argument_context('eventgrid event-subscription show') as c:
        c.argument('include_full_endpoint_url', arg_type=get_three_state_flag(), options_list=['--include-full-endpoint-url'], help="Specify to indicate whether the full endpoint URL should be returned. True if flag present.", )

    with self.argument_context('eventgrid topic-type') as c:
        c.argument('topic_type_name', arg_type=name_type, help="Name of the topic type.", completer=get_resource_name_completion_list('Microsoft.EventGrid/topictypes'))
