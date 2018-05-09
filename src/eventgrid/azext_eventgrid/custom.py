# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import re
from six.moves.urllib.parse import quote  # pylint: disable=import-error,relative-import
from knack.log import get_logger
from knack.util import CLIError
from msrestazure.tools import parse_resource_id

from azure.cli.core.commands.client_factory import get_subscription_id
from azext_eventgrid.mgmt.eventgrid.models import (
    EventSubscription,
    EventSubscriptionUpdateParameters,
    WebHookEventSubscriptionDestination,
    Topic,
    JsonInputSchemaMapping,
    JsonField,
    JsonFieldWithDefault,
    RetryPolicy,
    EventHubEventSubscriptionDestination,
    StorageQueueEventSubscriptionDestination,
    HybridConnectionEventSubscriptionDestination,
    StorageBlobDeadLetterDestination,
    EventSubscriptionFilter)

logger = get_logger(__name__)

EVENTGRID_NAMESPACE = "Microsoft.EventGrid"
RESOURCES_NAMESPACE = "Microsoft.Resources"
SUBSCRIPTIONS = "subscriptions"
RESOURCE_GROUPS = "resourcegroups"
EVENTGRID_TOPICS = "topics"
WEBHOOK_DESTINATION = "webhook"
EVENTHUB_DESTINATION = "eventhub"
STORAGEQUEUE_DESTINATION = "storagequeue"
HYBRIDCONNECTION_DESTINATION = "hybridconnection"
EVENTGRID_SCHEMA = "EventGridSchema"
CLOUDEVENTV01_SCHEMA = "CloudEventV01Schema"
CUSTOM_EVENT_SCHEMA = "CustomEventSchema"
INPUT_EVENT_SCHEMA = "InputEventSchema"

# Constants for the target field names of the mapping
TOPIC = "topic"
SUBJECT = "subject"
ID = "id"
EVENTTIME = "eventtime"
EVENTTYPE = "eventtype"
DATAVERSION = "dataversion"


def cli_topic_list(
        client,
        resource_group_name=None):
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name)

    return client.list_by_subscription()


def cli_topic_create_or_update(
        client,
        resource_group_name,
        topic_name,
        location,
        tags=None,
        input_schema=EVENTGRID_SCHEMA,
        input_mapping_fields=None,
        input_mapping_default_values=None):
    if input_schema.lower() == EVENTGRID_SCHEMA.lower():
        input_schema = EVENTGRID_SCHEMA
    elif input_schema.lower() == CUSTOM_EVENT_SCHEMA.lower():
        input_schema = CUSTOM_EVENT_SCHEMA
    elif input_schema.lower() == CLOUDEVENTV01_SCHEMA.lower():
        input_schema = CLOUDEVENTV01_SCHEMA
    else:
        raise CLIError('The provided --input-schema is not valid. The supported values are: ' +
                       EVENTGRID_SCHEMA + ',' + CUSTOM_EVENT_SCHEMA + ',' + CLOUDEVENTV01_SCHEMA)

    if input_schema == EVENTGRID_SCHEMA or input_schema == CLOUDEVENTV01_SCHEMA:
        # Ensure that custom input mappings are not specified
        if input_mapping_fields is not None or input_mapping_default_values is not None:
            raise CLIError('--input-mapping-default-values and --input-mapping-fields should be ' +
                           'specified only when --input-schema is set to customeventschema.')

    if input_schema == CUSTOM_EVENT_SCHEMA:
        # Ensure that custom input mappings are specified
        if input_mapping_fields is None and input_mapping_default_values is None:
            raise CLIError('Either --input-mapping-default-values or --input-mapping-fields must be ' +
                           'specified when --input-schema is set to customeventschema.')

    input_schema_mapping = get_input_schema_mapping(
        input_mapping_fields,
        input_mapping_default_values)

    topic_info = Topic(location, tags, input_schema, input_schema_mapping)

    async_topic_create = client.create_or_update(
        resource_group_name,
        topic_name,
        topic_info)
    created_topic = async_topic_create.result()
    return created_topic


def cli_eventgrid_event_subscription_create(
        cmd,
        client,
        event_subscription_name,
        endpoint,
        resource_id=None,
        resource_group_name=None,
        topic_name=None,
        endpoint_type=WEBHOOK_DESTINATION,
        included_event_types=None,
        subject_begins_with=None,
        subject_ends_with=None,
        is_subject_case_sensitive=False,
        max_delivery_attempts=30,
        event_ttl=1440,
        event_delivery_schema=EVENTGRID_SCHEMA,
        deadletter_endpoint=None,
        labels=None):
    # Construct RetryPolicy based on max_delivery_attempts and event_ttl
    max_delivery_attempts = int(max_delivery_attempts)
    event_ttl = int(event_ttl)
    _validate_retry_policy(max_delivery_attempts, event_ttl)
    retry_policy = RetryPolicy(max_delivery_attempts, event_ttl)

    # Get event_delivery_schema in the right case
    event_delivery_schema = _get_event_delivery_schema(event_delivery_schema)

    destination = _get_endpoint_destination(endpoint_type, endpoint)

    event_subscription_filter = EventSubscriptionFilter(
        subject_begins_with,
        subject_ends_with,
        included_event_types,
        is_subject_case_sensitive)

    deadletter_destination = None
    if deadletter_endpoint is not None:
        deadletter_destination = _get_deadletter_destination(deadletter_endpoint)

    scope = _get_scope_for_event_subscription(
        cmd.cli_ctx,
        resource_id,
        topic_name,
        resource_group_name)

    event_subscription_info = EventSubscription(
        destination,
        event_subscription_filter,
        labels,
        event_delivery_schema,
        retry_policy,
        deadletter_destination)

    _warn_if_manual_handshake_needed(endpoint_type, endpoint)

    async_event_subscription_create = client.create_or_update(
        scope,
        event_subscription_name,
        event_subscription_info)
    return async_event_subscription_create.result()


def event_subscription_setter(
        cmd,
        client,
        parameters,
        event_subscription_name,
        resource_id=None,
        resource_group_name=None,
        topic_name=None):
    scope = _get_scope_for_event_subscription(cmd.cli_ctx, resource_id, topic_name, resource_group_name)

    async_event_subscription_update = client.update(
        scope,
        event_subscription_name,
        parameters)
    updated_event_subscription = async_event_subscription_update.result()
    return updated_event_subscription


def cli_eventgrid_event_subscription_get(
        cmd,
        client,
        event_subscription_name,
        resource_id=None,
        resource_group_name=None,
        topic_name=None,
        include_full_endpoint_url=False):
    scope = _get_scope_for_event_subscription(cmd.cli_ctx, resource_id, topic_name, resource_group_name)
    retrieved_event_subscription = client.get(scope, event_subscription_name)
    destination = retrieved_event_subscription.destination
    if include_full_endpoint_url and isinstance(destination, WebHookEventSubscriptionDestination):
        full_endpoint_url = client.get_full_url(scope, event_subscription_name)
        destination.endpoint_url = full_endpoint_url.endpoint_url

    return retrieved_event_subscription


def cli_eventgrid_event_subscription_delete(
        cmd,
        client,
        event_subscription_name,
        resource_id=None,
        resource_group_name=None,
        topic_name=None):
    scope = _get_scope_for_event_subscription(cmd.cli_ctx, resource_id, topic_name, resource_group_name)
    return client.delete(scope, event_subscription_name)


def cli_event_subscription_list(   # pylint: disable=too-many-return-statements
        client,
        resource_id=None,
        resource_group_name=None,
        topic_name=None,
        location=None,
        topic_type_name=None):
    if resource_id:
        # Resource ID is specified, we need to list only for the particular resource.
        if resource_group_name is not None or topic_name is not None:
            raise CLIError('Since --resource-id is specified, --topic-name and --resource-group-name should not '
                           'be specified.')

        id_parts = parse_resource_id(resource_id)
        rg_name = id_parts['resource_group']
        resource_name = id_parts['name']
        provider_namespace = id_parts['namespace']
        resource_type = id_parts['resource_type']

        return client.list_by_resource(
            rg_name,
            provider_namespace,
            resource_type,
            resource_name)

    if topic_name:
        if resource_group_name is None:
            raise CLIError('Since --topic-name is specified, --resource-group-name must also be specified.')

        return client.list_by_resource(
            resource_group_name,
            EVENTGRID_NAMESPACE,
            EVENTGRID_TOPICS,
            topic_name)

    if topic_type_name:
        if location:
            if resource_group_name:
                return client.list_regional_by_resource_group_for_topic_type(
                    resource_group_name,
                    location,
                    topic_type_name)

            return client.list_regional_by_subscription_for_topic_type(
                location,
                topic_type_name)

        if resource_group_name:
            return client.list_global_by_resource_group_for_topic_type(
                resource_group_name,
                topic_type_name)

        return client.list_global_by_subscription_for_topic_type(topic_type_name)

    if location:
        if resource_group_name:
            return client.list_regional_by_resource_group(
                resource_group_name,
                location)

        return client.list_regional_by_subscription(location)

    if resource_group_name:
        return client.list_global_by_resource_group(resource_group_name)

    return client.list_global_by_subscription()


def _get_scope(
        cli_ctx,
        resource_group_name,
        provider_namespace,
        resource_type,
        resource_name):
    subscription_id = get_subscription_id(cli_ctx)

    if provider_namespace == RESOURCES_NAMESPACE:
        if resource_group_name:
            scope = (
                '/subscriptions/{}/resourceGroups/{}'
                .format(quote(subscription_id),
                        quote(resource_group_name)))
        else:
            scope = (
                '/subscriptions/{}'
                .format(quote(subscription_id)))
    else:
        scope = (
            '/subscriptions/{}/resourceGroups/{}/providers/{}/{}/{}'
            .format(quote(subscription_id),
                    quote(resource_group_name),
                    quote(provider_namespace),
                    quote(resource_type),
                    quote(resource_name)))

    return scope


def _get_scope_for_event_subscription(
        cli_ctx,
        resource_id,
        topic_name,
        resource_group_name):
    if resource_id:
        # Resource ID is provided, use that as the scope for the event subscription.
        scope = resource_id
    elif topic_name:
        # Topic name is provided, use the topic and resource group to build a scope for the user topic
        if resource_group_name is None:
            raise CLIError("When --topic-name is specified, the --resource-group-name must also be specified.")

        scope = _get_scope(cli_ctx, resource_group_name, EVENTGRID_NAMESPACE, EVENTGRID_TOPICS, topic_name)
    elif resource_group_name:
        # Event subscription to a resource group.
        scope = _get_scope(cli_ctx, resource_group_name, RESOURCES_NAMESPACE, RESOURCE_GROUPS, resource_group_name)
    else:
        scope = _get_scope(cli_ctx, None, RESOURCES_NAMESPACE, SUBSCRIPTIONS, get_subscription_id(cli_ctx))

    return scope


def event_subscription_getter(
        cmd,
        client,
        event_subscription_name,
        resource_id=None,
        resource_group_name=None,
        topic_name=None):
    scope = _get_scope_for_event_subscription(cmd.cli_ctx, resource_id, topic_name, resource_group_name)
    retrieved_event_subscription = client.get(scope, event_subscription_name)
    return retrieved_event_subscription


def get_input_schema_mapping(
        input_mapping_fields=None,
        input_mapping_default_values=None):
    input_schema_mapping = None

    if input_mapping_fields is not None or input_mapping_default_values is not None:
        input_schema_mapping = JsonInputSchemaMapping()

        input_schema_mapping.id = JsonField()
        input_schema_mapping.topic = JsonField()
        input_schema_mapping.event_time = JsonField()
        input_schema_mapping.subject = JsonFieldWithDefault()
        input_schema_mapping.event_type = JsonFieldWithDefault()
        input_schema_mapping.data_version = JsonFieldWithDefault()

        for field_mapping_pair in input_mapping_fields:
            field_mapping = field_mapping_pair.split("=")
            target = field_mapping[0]
            source = field_mapping[1]

            if target.lower() == ID.lower():
                input_schema_mapping.id.source_field = source
            elif target.lower() == EVENTTIME.lower():
                input_schema_mapping.event_time.source_field = source
            elif target.lower() == TOPIC.lower():
                input_schema_mapping.topic.source_field = source
            elif target.lower() == SUBJECT.lower():
                input_schema_mapping.subject.source_field = source
            elif target.lower() == DATAVERSION.lower():
                input_schema_mapping.data_version.source_field = source
            elif target.lower() == EVENTTYPE.lower():
                input_schema_mapping.event_type.source_field = source

        for default_value_mapping_pair in input_mapping_default_values:
            default_value_mapping = default_value_mapping_pair.split("=")
            target = default_value_mapping[0]
            source = default_value_mapping[1]

            if target.lower() == SUBJECT.lower():
                input_schema_mapping.subject.default_value = source
            elif target.lower() == DATAVERSION.lower():
                input_schema_mapping.data_version.default_value = source
            elif target.lower() == EVENTTYPE.lower():
                input_schema_mapping.event_type.default_value = source

    return input_schema_mapping


def update_event_subscription(
        instance,
        endpoint=None,
        endpoint_type=WEBHOOK_DESTINATION,
        subject_begins_with=None,
        subject_ends_with=None,
        included_event_types=None,
        labels=None,
        deadletter_endpoint=None):
    event_subscription_destination = None
    deadletter_destination = None
    event_subscription_labels = instance.labels
    event_subscription_filter = instance.filter

    # TODO: These are not currently updatable, make them updatable.
    event_delivery_schema = instance.event_delivery_schema
    retry_policy = instance.retry_policy

    if event_delivery_schema is None:
        event_delivery_schema = EVENTGRID_SCHEMA

    if endpoint is not None:
        event_subscription_destination = _get_endpoint_destination(endpoint_type, endpoint)

    if deadletter_endpoint is not None:
        deadletter_destination = _get_deadletter_destination(deadletter_endpoint)

    if subject_begins_with is not None:
        event_subscription_filter.subject_begins_with = subject_begins_with

    if subject_ends_with is not None:
        event_subscription_filter.subject_ends_with = subject_ends_with

    if included_event_types is not None:
        event_subscription_filter.included_event_types = included_event_types

    if labels is not None:
        event_subscription_labels = labels

    params = EventSubscriptionUpdateParameters(
        destination=event_subscription_destination,
        filter=event_subscription_filter,
        labels=event_subscription_labels,
        retry_policy=retry_policy,
        dead_letter_destination=deadletter_destination,
        event_delivery_schema=event_delivery_schema
    )

    return params


def _get_endpoint_destination(endpoint_type, endpoint):
    if endpoint_type.lower() == WEBHOOK_DESTINATION.lower():
        destination = WebHookEventSubscriptionDestination(endpoint)
    elif endpoint_type.lower() == EVENTHUB_DESTINATION.lower():
        destination = EventHubEventSubscriptionDestination(endpoint)
    elif endpoint_type.lower() == HYBRIDCONNECTION_DESTINATION.lower():
        destination = HybridConnectionEventSubscriptionDestination(endpoint)
    elif endpoint_type.lower() == STORAGEQUEUE_DESTINATION.lower():
        destination = _get_storage_queue_destination(endpoint)

    return destination


def _get_storage_queue_destination(endpoint):
    # Supplied endpoint would be in the following format:
    # /subscriptions/.../storageAccounts/sa1/queueServices/default/queues/{queueName}))
    # and we need to break it up into:
    # /subscriptions/.../storageAccounts/sa1 and queueName
    queue_items = re.split(
        "/queueServices/default/queues/", endpoint, flags=re.IGNORECASE)

    if len(queue_items) != 2 or queue_items[0] is None or queue_items[1] is None:
        raise CLIError('Argument Error: Expected format of --endpoint for storage queue is:' +
                       '/subscriptions/id/resourceGroups/rg/providers/Microsoft.Storage/' +
                       'storageAccounts/sa1/queueServices/default/queues/queueName')

    destination = StorageQueueEventSubscriptionDestination(
        queue_items[0], queue_items[1])

    return destination


def _get_deadletter_destination(deadletter_endpoint):
    blob_items = re.split(
        "/blobServices/default/containers/", deadletter_endpoint, flags=re.IGNORECASE)

    if len(blob_items) != 2 or blob_items[0] is None or blob_items[1] is None:
        raise CLIError('Argument Error: Expected format of --deadletter-endpoint is:' +
                       '/subscriptions/id/resourceGroups/rg/providers/Microsoft.Storage/' +
                       'storageAccounts/sa1/blobServices/default/containers/containerName')

    deadletter_destination = StorageBlobDeadLetterDestination(
        blob_items[0], blob_items[1])

    return deadletter_destination


def _validate_retry_policy(max_delivery_attempts, event_ttl):
    if max_delivery_attempts < 1 or max_delivery_attempts > 30:
        raise CLIError('--max-delivery-attempts should be a number between 1 and 30.')

    if event_ttl < 1 or event_ttl > 1440:
        raise CLIError('--event-ttl should be a number between 1 and 1440.')


def _get_event_delivery_schema(event_delivery_schema):
    if event_delivery_schema.lower() == EVENTGRID_SCHEMA.lower():
        event_delivery_schema = EVENTGRID_SCHEMA
    elif event_delivery_schema.lower() == INPUT_EVENT_SCHEMA.lower():
        event_delivery_schema = INPUT_EVENT_SCHEMA
    elif event_delivery_schema.lower() == CLOUDEVENTV01_SCHEMA.lower():
        event_delivery_schema = CLOUDEVENTV01_SCHEMA
    else:
        raise CLIError('The provided --event-delivery-schema is not valid. The supported '
                       ' values are:' + EVENTGRID_SCHEMA + ',' + INPUT_EVENT_SCHEMA +
                       ',' + CLOUDEVENTV01_SCHEMA)

    return event_delivery_schema


def _warn_if_manual_handshake_needed(endpoint_type, endpoint):
    # If the endpoint belongs to a service that we know implements the subscription validation
    # handshake, there's no need to show this message, hence we check for those services
    # before showing this message. This list includes Azure Automation, EventGrid Trigger based
    # Azure functions, and Azure Logic Apps.
    if endpoint_type.lower() == WEBHOOK_DESTINATION.lower() and \
       "azure-automation" not in endpoint.lower() and \
       "eventgridextension" not in endpoint.lower() and \
       "logic.azure.com" not in endpoint.lower() and \
       "hookbin" not in endpoint.lower():
        logger.warning("If the provided endpoint doesn't support subscription validation " +
                       "handshake, navigate to the validation URL that you receive in the " +
                       "subscription validation event, in order to complete the event " +
                       "subscription creation or update. For more details, " +
                       "please visit http://aka.ms/esvalidation")
