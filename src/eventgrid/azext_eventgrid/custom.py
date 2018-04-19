# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from six.moves.urllib.parse import quote  # pylint: disable=import-error
import re
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
EVENTGRID_SCHEMA = "eventgridschema"
CUSTOM_SCHEMA = "customeventschema"
CLOUDEVENTV01_SCHEMA = "cloudeventv01schema"


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
    if input_schema is EVENTGRID_SCHEMA or input_schema is CLOUDEVENTV01_SCHEMA:
        # Ensure that custom input mappings are not specified
        if input_mapping_fields is not None or input_mapping_default_values is not None:
            raise CLIError('input_mapping_default_values and input_mapping_fields are applicable only when input_schema is set to customeventschema.')

    if input_schema is CUSTOM_SCHEMA:
        # Ensure that custom input mappings are specified
        if input_mapping_fields is not None and input_mapping_default_values is not None:
            raise CLIError('Either input_mapping_default_values or input_mapping_fields must be specified when input_schema is set to customeventschema.')

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
    scope = _get_scope_for_event_subscription(cmd.cli_ctx, resource_id, topic_name, resource_group_name)

    if endpoint_type.lower() == WEBHOOK_DESTINATION.lower():
        destination = WebHookEventSubscriptionDestination(endpoint)
    elif endpoint_type.lower() == EVENTHUB_DESTINATION.lower():
        destination = EventHubEventSubscriptionDestination(endpoint)
    elif endpoint_type.lower() == HYBRIDCONNECTION_DESTINATION.lower():
        destination = HybridConnectionEventSubscriptionDestination(endpoint)
    elif endpoint_type.lower() == STORAGEQUEUE_DESTINATION.lower():
        # Supplied endpoint would be in the format /subscriptions/id/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/sa1/queueServices/default/queues/{queueName}))
        # and we need to break it up into /subscriptions/id/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/sa1 and queueName
        storage_queue_items = re.split(
            "/queueServices/default/queues/", endpoint, flags=re.IGNORECASE)

        if len(storage_queue_items) != 2 or storage_queue_items[0] is None or storage_queue_items[1] is None:
            raise CLIError("Argument Error: Expected format of Storage queue endpoint is: /subscriptions/id/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/sa1/queueServices/default/queues/queueName")

        destination = StorageQueueEventSubscriptionDestination(
            storage_queue_items[0], storage_queue_items[1])

    event_subscription_filter = EventSubscriptionFilter(
        subject_begins_with,
        subject_ends_with,
        included_event_types,
        is_subject_case_sensitive)

    retry_policy = RetryPolicy(max_delivery_attempts, event_ttl)

    if deadlettter_endpoint is not None:
        storage_blob_items = re.split(
            "/blobServices/default/containers/", endpoint, flags=re.IGNORECASE)

        if len(storage_blob_items) != 2 or storage_blob_items[0] is None or storage_blob_items[1] is None:
            raise CLIError("Argument Error: Expected format of deadletter destination is: /subscriptions/id/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/sa1/blobServices/default/containers/containerName")

        deadletter_destination = StorageBlobDeadLetterDestination(
            storage_blob_items[0], storage_blob_items[1])

    event_subscription_info = EventSubscription(
        destination, event_subscription_filter, labels, event_delivery_schema, retry_policy, deadletter_destination)

    if endpoint_type.lower() == WEBHOOK_DESTINATION.lower() and "azure" not in endpoint and "hookbin" not in endpoint:
        print("If the endpoint doesn't support subscription validation response, please visit the validation URL manually to complete the validation handshake.")

    async_event_subscription_create = client.create_or_update(
        scope,
        event_subscription_name,
        event_subscription_info)
    created_event_subscription = async_event_subscription_create.result()
    return created_event_subscription


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
            raise CLIError('Since ResourceId is specified, topic-name and resource-group-name should not be specified.')

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
            raise CLIError('Since topic-name is specified, resource-group-name must also be specified.')

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
            raise CLIError("When topic name is specified, the resource group name must also be specified.")

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

       for key_value_pair in input_mapping_fields:
           split_key_value_pairs = key_value_pair.split("=")
           if split_key_value_pairs[0].lower() == "id":
               input_schema_mapping.id.source_field = split_key_value_pairs[1]
           elif split_key_value_pairs[0].lower() == "eventtime":
               input_schema_mapping.event_time.source_field = split_key_value_pairs[1]
           elif split_key_value_pairs[0].lower() == "topic":
               input_schema_mapping.topic.source_field = split_key_value_pairs[1]
           elif split_key_value_pairs[0].lower() == "subject":
               input_schema_mapping.subject.source_field = split_key_value_pairs[1]
           elif split_key_value_pairs[0].lower() == "dataversion":
               input_schema_mapping.data_version.source_field = split_key_value_pairs[1]
           elif split_key_value_pairs[0].lower() == "eventtype":
               input_schema_mapping.event_type.source_field = split_key_value_pairs[1]

       for key_value_pair2 in input_mapping_default_values:
           split_key_value_pairs2 = key_value_pair2.split("=")
           if split_key_value_pairs2[0].lower() == "subject":
               input_schema_mapping.subject.default_value = split_key_value_pairs2[1]
           elif split_key_value_pairs2[0].lower() == "dataversion":
               input_schema_mapping.data_version.default_value = split_key_value_pairs2[1]
           elif split_key_value_pairs2[0].lower() == "eventtype":
               input_schema_mapping.event_type.default_value = split_key_value_pairs2[1]

   return input_schema_mapping


def update_event_subscription(
        instance,
        endpoint=None,
        endpoint_type=WEBHOOK_DESTINATION,
        subject_begins_with=None,
        subject_ends_with=None,
        included_event_types=None,
        labels=None):
    event_subscription_destination = None
    event_subscription_labels = instance.labels
    event_subscription_filter = instance.filter

    if endpoint is not None:
        if endpoint_type.lower() == WEBHOOK_DESTINATION.lower():
            event_subscription_destination = WebHookEventSubscriptionDestination(endpoint)
        elif endpoint_type.lower() == EVENTHUB_DESTINATION.lower():
            event_subscription_destination = EventHubEventSubscriptionDestination(endpoint)

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
        labels=event_subscription_labels
    )

    return params
