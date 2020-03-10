# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import re
from six.moves.urllib.parse import quote  # pylint: disable=import-error,relative-import
from knack.log import get_logger
from knack.util import CLIError
from msrestazure.tools import parse_resource_id
from dateutil.parser import parse   # pylint: disable=import-error,relative-import

from azure.cli.core.commands.client_factory import get_subscription_id
from azext_eventgrid.vendored_sdks.eventgrid.models import (
    EventSubscription,
    EventSubscriptionUpdateParameters,
    WebHookEventSubscriptionDestination,
    Topic,
    Domain,
    JsonInputSchemaMapping,
    JsonField,
    JsonFieldWithDefault,
    RetryPolicy,
    EventHubEventSubscriptionDestination,
    StorageQueueEventSubscriptionDestination,
    HybridConnectionEventSubscriptionDestination,
    ServiceBusQueueEventSubscriptionDestination,
    ServiceBusTopicEventSubscriptionDestination,
    AzureFunctionEventSubscriptionDestination,
    StorageBlobDeadLetterDestination,
    EventSubscriptionFilter,
    TopicUpdateParameters,
    DomainUpdateParameters)

logger = get_logger(__name__)

EVENTGRID_NAMESPACE = "Microsoft.EventGrid"
RESOURCES_NAMESPACE = "Microsoft.Resources"
SUBSCRIPTIONS = "subscriptions"
RESOURCE_GROUPS = "resourcegroups"
EVENTGRID_DOMAINS = "domains"
EVENTGRID_TOPICS = "topics"
EVENTGRID_DOMAIN_TOPICS = "domaintopics"
WEBHOOK_DESTINATION = "webhook"
EVENTHUB_DESTINATION = "eventhub"
STORAGEQUEUE_DESTINATION = "storagequeue"
HYBRIDCONNECTION_DESTINATION = "hybridconnection"
SERVICEBUSQUEUE_DESTINATION = "servicebusqueue"
SERVICEBUSTOPIC_DESTINATION = "servicebustopic"
AZUREFUNCTION_DESTINATION = "azurefunction"
EVENTGRID_SCHEMA = "EventGridSchema"
CLOUDEVENTV1_0_SCHEMA = "CloudEventSchemaV1_0"
CUSTOM_EVENT_SCHEMA = "CustomEventSchema"
CUSTOM_INPUT_SCHEMA = "CustomInputSchema"
GLOBAL = "global"

# Deprecated event delivery schema values
INPUT_EVENT_SCHEMA = "InputEventSchema"
CLOUDEVENTV01SCHEMA = "CloudEventV01Schema"

# Constants for the target field names of the mapping
TOPIC = "topic"
SUBJECT = "subject"
ID = "id"
EVENTTIME = "eventtime"
EVENTTYPE = "eventtype"
DATAVERSION = "dataversion"
DEFAULT_TOP = 100


def cli_topic_list(
        client,
        resource_group_name=None,
        odata_query=None):

    if resource_group_name:
        return client.list_by_resource_group(resource_group_name, odata_query, DEFAULT_TOP)

    return client.list_by_subscription(odata_query, DEFAULT_TOP)


def cli_topic_create_or_update(
        client,
        resource_group_name,
        topic_name,
        location,
        tags=None,
        input_schema=EVENTGRID_SCHEMA,
        input_mapping_fields=None,
        input_mapping_default_values=None,
        allow_traffic_from_all_ips=None,
        inbound_ip_rules=None):
    final_input_schema, input_schema_mapping = _get_input_schema_and_mapping(
        input_schema,
        input_mapping_fields,
        input_mapping_default_values)
    topic_info = Topic(
        location=location,
        tags=tags,
        input_schema=final_input_schema,
        input_schema_mapping=input_schema_mapping,
        allow_traffic_from_all_ips=allow_traffic_from_all_ips,
        inbound_ip_rules=inbound_ip_rules)

    return client.create_or_update(
        resource_group_name,
        topic_name,
        topic_info)


def cli_topic_update(
        client,
        resource_group_name,
        topic_name,
        tags=None,
        allow_traffic_from_all_ips=None,
        inbound_ip_rules=None):
    topic_update_parameters = TopicUpdateParameters(
        tags=tags,
        allow_traffic_from_all_ips=allow_traffic_from_all_ips,
        inbound_ip_rules=inbound_ip_rules)

    return client.update(
        resource_group_name=resource_group_name,
        topic_name=topic_name,
        topic_update_parameters=topic_update_parameters)


def cli_domain_update(
        client,
        resource_group_name,
        domain_name,
        tags=None,
        allow_traffic_from_all_ips=None,
        inbound_ip_rules=None):
    domain_update_parameters = DomainUpdateParameters(
        tags=tags,
        allow_traffic_from_all_ips=allow_traffic_from_all_ips,
        inbound_ip_rules=inbound_ip_rules)

    return client.update(
        resource_group_name,
        domain_name,
        domain_update_parameters)


def cli_domain_list(
        client,
        resource_group_name=None,
        odata_query=None):

    if resource_group_name:
        return client.list_by_resource_group(resource_group_name, odata_query, DEFAULT_TOP)

    return client.list_by_subscription(odata_query, DEFAULT_TOP)


def cli_domain_create_or_update(
        client,
        resource_group_name,
        domain_name,
        location,
        tags=None,
        input_schema=EVENTGRID_SCHEMA,
        input_mapping_fields=None,
        input_mapping_default_values=None,
        allow_traffic_from_all_ips=None,
        inbound_ip_rules=None):
    final_input_schema, input_schema_mapping = _get_input_schema_and_mapping(
        input_schema,
        input_mapping_fields,
        input_mapping_default_values)
    domain_info = Domain(
        location=location,
        tags=tags,
        input_schema=final_input_schema,
        input_schema_mapping=input_schema_mapping,
        allow_traffic_from_all_ips=allow_traffic_from_all_ips,
        inbound_ip_rules=inbound_ip_rules)

    return client.create_or_update(
        resource_group_name,
        domain_name,
        domain_info)


def cli_domain_topic_create_or_update(
        client,
        resource_group_name,
        domain_name,
        domain_topic_name):
    return client.create_or_update(
        resource_group_name,
        domain_name,
        domain_topic_name)


def cli_domain_topic_delete(
        client,
        resource_group_name,
        domain_name,
        domain_topic_name):
    return client.delete(
        resource_group_name,
        domain_name,
        domain_topic_name)


def cli_domain_topic_list(
        client,
        resource_group_name,
        domain_name,
        odata_query=None):
    return client.list_by_domain(resource_group_name, domain_name, odata_query, DEFAULT_TOP)


def cli_eventgrid_event_subscription_create(   # pylint: disable=too-many-locals
        client,
        event_subscription_name,
        endpoint,
        source_resource_id=None,
        endpoint_type=WEBHOOK_DESTINATION,
        included_event_types=None,
        subject_begins_with=None,
        subject_ends_with=None,
        is_subject_case_sensitive=False,
        max_delivery_attempts=30,
        event_ttl=1440,
        max_events_per_batch=None,
        preferred_batch_size_in_kilobytes=None,
        event_delivery_schema=None,
        deadletter_endpoint=None,
        labels=None,
        expiration_date=None,
        advanced_filter=None,
        azure_active_directory_tenant_id=None,
        azure_active_directory_application_id_or_uri=None):

    if included_event_types is not None and len(included_event_types) == 1 and included_event_types[0].lower() == 'all':
        logger.warning('The usage of \"All\" for --included-event-types is not allowed starting from Azure Event Grid'
                       ' API Version 2019-02-01-preview. However, the call here is still permitted by replacing'
                       ' \"All\" with None in order to return all the event types (for the custom topics and'
                       ' domains case) or default event types (for other topic types case). In any future calls,'
                       ' please consider leaving --included-event-types unspecified or use None instead.')
        included_event_types = None

    # Construct RetryPolicy based on max_delivery_attempts and event_ttl
    max_delivery_attempts = int(max_delivery_attempts)
    event_ttl = int(event_ttl)
    _validate_retry_policy(max_delivery_attempts, event_ttl)
    retry_policy = RetryPolicy(max_delivery_attempts=max_delivery_attempts, event_time_to_live_in_minutes=event_ttl)

    if max_events_per_batch is not None:
        if endpoint_type not in (WEBHOOK_DESTINATION, AZUREFUNCTION_DESTINATION):
            raise CLIError('usage error: max-events-per-batch is applicable only for '
                           'endpoint types WebHook and AzureFunction.')
        max_events_per_batch = int(max_events_per_batch)
        if max_events_per_batch > 5000:
            raise CLIError('usage error: max-events-per-batch must be a number between 1 and 5000.')

    if preferred_batch_size_in_kilobytes is not None:
        if endpoint_type not in (WEBHOOK_DESTINATION, AZUREFUNCTION_DESTINATION):
            raise CLIError('usage error: preferred-batch-size-in-kilobytes is applicable only for '
                           'endpoint types WebHook and AzureFunction.')
        preferred_batch_size_in_kilobytes = int(preferred_batch_size_in_kilobytes)
        if preferred_batch_size_in_kilobytes > 1024:
            raise CLIError('usage error: preferred-batch-size-in-kilobytes must be a number '
                           'between 1 and 1024.')

    if azure_active_directory_tenant_id is not None:
        if endpoint_type is not WEBHOOK_DESTINATION:
            raise CLIError('usage error: azure-active-directory-tenant-id is applicable only for '
                           'endpoint types WebHook.')
        if azure_active_directory_application_id_or_uri is None:
            raise CLIError('usage error: azure-active-directory-application-id-or-uri is missing. '
                           'It should include an Azure Active Directory Application Id or Uri.')

    if azure_active_directory_application_id_or_uri is not None:
        if endpoint_type is not WEBHOOK_DESTINATION:
            raise CLIError('usage error: azure-active-directory-application-id-or-uri is applicable only for '
                           'endpoint types WebHook.')
        if azure_active_directory_tenant_id is None:
            raise CLIError('usage error: azure-active-directory-tenant-id is missing. '
                           'It should include an Azure Active Directory Tenant Id.')

    tennant_id = None
    application_id = None

    if endpoint_type.lower() == WEBHOOK_DESTINATION.lower():
        tennant_id = azure_active_directory_tenant_id
        application_id = azure_active_directory_application_id_or_uri

    destination = _get_endpoint_destination(
        endpoint_type,
        endpoint,
        max_events_per_batch,
        preferred_batch_size_in_kilobytes,
        tennant_id,
        application_id)

    event_subscription_filter = EventSubscriptionFilter(
        subject_begins_with=subject_begins_with,
        subject_ends_with=subject_ends_with,
        included_event_types=included_event_types,
        is_subject_case_sensitive=is_subject_case_sensitive,
        advanced_filters=advanced_filter)

    deadletter_destination = None
    if deadletter_endpoint is not None:
        deadletter_destination = _get_deadletter_destination(deadletter_endpoint)

    if expiration_date is not None:
        expiration_date = parse(expiration_date)

    event_subscription_info = EventSubscription(
        destination=destination,
        filter=event_subscription_filter,
        labels=labels,
        event_delivery_schema=_get_event_delivery_schema(event_delivery_schema),
        retry_policy=retry_policy,
        expiration_time_utc=expiration_date,
        dead_letter_destination=deadletter_destination)

    _warn_if_manual_handshake_needed(endpoint_type, endpoint)

    return client.create_or_update(
        source_resource_id,
        event_subscription_name,
        event_subscription_info)


def cli_eventgrid_event_subscription_delete(
        client,
        event_subscription_name,
        source_resource_id=None):
    return client.delete(
        source_resource_id,
        event_subscription_name)


def event_subscription_setter(
        client,
        parameters,
        event_subscription_name,
        source_resource_id=None):

    return client.update(
        source_resource_id,
        event_subscription_name,
        parameters)


def cli_eventgrid_event_subscription_get(
        client,
        event_subscription_name,
        source_resource_id=None,
        include_full_endpoint_url=False):

    retrieved_event_subscription = client.get(source_resource_id, event_subscription_name)
    destination = retrieved_event_subscription.destination
    if include_full_endpoint_url and isinstance(destination, WebHookEventSubscriptionDestination):
        full_endpoint_url = client.get_full_url(source_resource_id, event_subscription_name)
        destination.endpoint_url = full_endpoint_url.endpoint_url

    return retrieved_event_subscription


def cli_event_subscription_list(   # pylint: disable=too-many-return-statements
        client,
        source_resource_id=None,
        location=None,
        resource_group_name=None,
        topic_type_name=None,
        odata_query=None):
    if source_resource_id is not None:
        # If Source Resource ID is specified, we need to list event subscriptions for that particular resource.
        # Since a full resource ID is specified, it should override all other defaults such as default location and RG
        # No other parameters must be specified
        if topic_type_name is not None:
            raise CLIError('usage error: Since --source-resource-id is specified, none of the other parameters must '
                           'be specified.')

        return _list_event_subscriptions_by_resource_id(client, source_resource_id, odata_query, DEFAULT_TOP)

    if location is None:
        # Since resource-id was not specified, location must be specified: e.g. "westus2" or "global". If not error
        # OUT.
        raise CLIError('usage error: --source-resource-id ID | --location LOCATION'
                       ' [--resource-group RG] [--topic-type-name TOPIC_TYPE_NAME]')

    if topic_type_name is None:
        # No topic-type is specified: return event subscriptions across all topic types for this location.
        if location.lower() == GLOBAL.lower():
            if resource_group_name:
                return client.list_global_by_resource_group(resource_group_name, odata_query, DEFAULT_TOP)
            return client.list_global_by_subscription(odata_query, DEFAULT_TOP)

        if resource_group_name:
            return client.list_regional_by_resource_group(resource_group_name, location, odata_query, DEFAULT_TOP)
        return client.list_regional_by_subscription(location, odata_query, DEFAULT_TOP)

    # Topic type name is specified
    if location.lower() == GLOBAL.lower():
        if not _is_topic_type_global_resource(topic_type_name):
            raise CLIError('Invalid usage: Global cannot be specified for the location '
                           'as the specified topic type is a regional topic type with '
                           'regional event subscriptions. Specify a location value such '
                           'as westus. Global can be used only for global topic types: '
                           'Microsoft.Resources.Subscriptions and Microsoft.Resources.ResourceGroups.')
        if resource_group_name:
            return client.list_global_by_resource_group_for_topic_type(
                resource_group_name,
                topic_type_name,
                odata_query,
                DEFAULT_TOP)
        return client.list_global_by_subscription_for_topic_type(topic_type_name, odata_query, DEFAULT_TOP)

    if resource_group_name:
        return client.list_regional_by_resource_group_for_topic_type(
            resource_group_name,
            location,
            topic_type_name,
            odata_query,
            DEFAULT_TOP)
    return client.list_regional_by_subscription_for_topic_type(
        location,
        topic_type_name,
        odata_query,
        DEFAULT_TOP)


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


def event_subscription_getter(
        client,
        event_subscription_name,
        source_resource_id=None):
    return client.get(source_resource_id, event_subscription_name)


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

        if input_mapping_fields is not None:
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

        if input_mapping_default_values is not None:
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
        advanced_filter=None,
        labels=None,
        deadletter_endpoint=None):
    event_subscription_destination = instance.destination
    deadletter_destination = None
    event_subscription_labels = instance.labels
    event_subscription_filter = instance.filter

    event_delivery_schema = instance.event_delivery_schema
    retry_policy = instance.retry_policy

    if endpoint_type.lower() != WEBHOOK_DESTINATION.lower() and endpoint is None:
        raise CLIError('Invalid usage: Since --endpoint-type is specified, a valid endpoint must also be specified.')

    tennant_id = None
    application_id = None

    # for the update path, endpoint_type can be None but it does not mean that this is webhook,
    # as it can be other types too.
    if event_subscription_destination is not None and \
       hasattr(event_subscription_destination, 'azure_active_directory_tenant_id'):
        tennant_id = event_subscription_destination.azure_active_directory_tenant_id

    if event_subscription_destination is not None and \
       hasattr(event_subscription_destination, 'azure_active_directory_application_id_or_uri'):
        application_id = event_subscription_destination.azure_active_directory_application_id_or_uri

    if endpoint is not None:
        event_subscription_destination = _get_endpoint_destination(
            endpoint_type,
            endpoint,
            event_subscription_destination.max_events_per_batch,
            event_subscription_destination.preferred_batch_size_in_kilobytes,
            tennant_id,
            application_id)

    if deadletter_endpoint is not None:
        deadletter_destination = _get_deadletter_destination(deadletter_endpoint)

    if subject_begins_with is not None:
        event_subscription_filter.subject_begins_with = subject_begins_with

    if subject_ends_with is not None:
        event_subscription_filter.subject_ends_with = subject_ends_with

    if included_event_types is not None:
        event_subscription_filter.included_event_types = included_event_types

    if advanced_filter is not None:
        event_subscription_filter.advanced_filters = advanced_filter

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


def _get_endpoint_destination(
        endpoint_type,
        endpoint,
        max_events_per_batch,
        preferred_batch_size_in_kilobytes,
        azure_active_directory_tenant_id,
        azure_active_directory_application_id_or_uri):

    if endpoint_type.lower() == WEBHOOK_DESTINATION.lower():
        destination = WebHookEventSubscriptionDestination(
            endpoint_url=endpoint,
            max_events_per_batch=max_events_per_batch,
            preferred_batch_size_in_kilobytes=preferred_batch_size_in_kilobytes,
            azure_active_directory_tenant_id=azure_active_directory_tenant_id,
            azure_active_directory_application_id_or_uri=azure_active_directory_application_id_or_uri)
    elif endpoint_type.lower() == EVENTHUB_DESTINATION.lower():
        destination = EventHubEventSubscriptionDestination(resource_id=endpoint)
    elif endpoint_type.lower() == HYBRIDCONNECTION_DESTINATION.lower():
        destination = HybridConnectionEventSubscriptionDestination(resource_id=endpoint)
    elif endpoint_type.lower() == STORAGEQUEUE_DESTINATION.lower():
        destination = _get_storage_queue_destination(endpoint)
    elif endpoint_type.lower() == SERVICEBUSQUEUE_DESTINATION.lower():
        destination = ServiceBusQueueEventSubscriptionDestination(resource_id=endpoint)
    elif endpoint_type.lower() == SERVICEBUSTOPIC_DESTINATION.lower():
        destination = ServiceBusTopicEventSubscriptionDestination(resource_id=endpoint)
    elif endpoint_type.lower() == AZUREFUNCTION_DESTINATION.lower():
        destination = AzureFunctionEventSubscriptionDestination(
            resource_id=endpoint,
            max_events_per_batch=max_events_per_batch,
            preferred_batch_size_in_kilobytes=preferred_batch_size_in_kilobytes)
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
        resource_id=queue_items[0], queue_name=queue_items[1])

    return destination


def _get_deadletter_destination(deadletter_endpoint):
    blob_items = re.split(
        "/blobServices/default/containers/", deadletter_endpoint, flags=re.IGNORECASE)

    if len(blob_items) != 2 or blob_items[0] is None or blob_items[1] is None:
        raise CLIError('Argument Error: Expected format of --deadletter-endpoint is:' +
                       '/subscriptions/id/resourceGroups/rg/providers/Microsoft.Storage/' +
                       'storageAccounts/sa1/blobServices/default/containers/containerName')

    return StorageBlobDeadLetterDestination(resource_id=blob_items[0], blob_container_name=blob_items[1])


def _validate_retry_policy(max_delivery_attempts, event_ttl):
    if max_delivery_attempts < 1 or max_delivery_attempts > 30:
        raise CLIError('--max-delivery-attempts should be a number between 1 and 30.')

    if event_ttl < 1 or event_ttl > 1440:
        raise CLIError('--event-ttl should be a number between 1 and 1440.')


def _get_event_delivery_schema(event_delivery_schema):
    if event_delivery_schema is None:
        return None
    if event_delivery_schema.lower() == EVENTGRID_SCHEMA.lower():
        event_delivery_schema = EVENTGRID_SCHEMA
    elif event_delivery_schema.lower() == CUSTOM_INPUT_SCHEMA.lower():
        event_delivery_schema = CUSTOM_INPUT_SCHEMA
    elif event_delivery_schema.lower() == CLOUDEVENTV1_0_SCHEMA.lower():
        event_delivery_schema = CLOUDEVENTV1_0_SCHEMA
    else:
        raise CLIError('usage error: --event-delivery-schema supported values are'
                       ' :' + EVENTGRID_SCHEMA + ',' + CUSTOM_INPUT_SCHEMA +
                       ',' + CLOUDEVENTV1_0_SCHEMA)

    return event_delivery_schema


def _warn_if_manual_handshake_needed(endpoint_type, endpoint):
    # If the endpoint belongs to a service that we know implements the subscription validation
    # handshake, there's no need to show this message, hence we check for those services
    # before showing this message. This list includes Azure Automation, EventGrid Trigger based
    # Azure functions, and Azure Logic Apps.
    if endpoint_type.lower() == WEBHOOK_DESTINATION.lower() and \
       "azure-automation" not in endpoint.lower() and \
       "eventgridextension" not in endpoint.lower() and \
       "logic.azure" not in endpoint.lower():
        logger.warning('If the provided endpoint does not support subscription validation '
                       'handshake, navigate to the validation URL that you receive in the '
                       'subscription validation event, in order to complete the event '
                       'subscription creation or update. For more details, '
                       'please visit http://aka.ms/esvalidation')


def _get_input_schema_and_mapping(
        input_schema=EVENTGRID_SCHEMA,
        input_mapping_fields=None,
        input_mapping_default_values=None):
    if input_schema.lower() == EVENTGRID_SCHEMA.lower():
        input_schema = EVENTGRID_SCHEMA
    elif input_schema.lower() == CUSTOM_EVENT_SCHEMA.lower():
        input_schema = CUSTOM_EVENT_SCHEMA
    elif input_schema.lower() == CLOUDEVENTV1_0_SCHEMA.lower():
        input_schema = CLOUDEVENTV1_0_SCHEMA
    else:
        raise CLIError('The provided --input-schema is not valid. The supported values are: ' +
                       EVENTGRID_SCHEMA + ',' + CUSTOM_EVENT_SCHEMA + ',' + CLOUDEVENTV1_0_SCHEMA)

    if input_schema == EVENTGRID_SCHEMA:
        # Ensure that custom input mappings are not specified
        if input_mapping_fields is not None or input_mapping_default_values is not None:
            raise CLIError('--input-mapping-default-values and --input-mapping-fields should not be ' +
                           'specified when --input-schema is set to eventgridschema.')

    if input_schema == CLOUDEVENTV1_0_SCHEMA:
        # Ensure that input_mapping_default_values is not specified.
        if input_mapping_default_values is not None:
            raise CLIError('--input-mapping-default-values should be ' +
                           'specified only when --input-schema is set to customeventschema.')

    if input_schema == CUSTOM_EVENT_SCHEMA:
        # Ensure that custom input mappings are specified
        if input_mapping_fields is None and input_mapping_default_values is None:
            raise CLIError('Either --input-mapping-default-values or --input-mapping-fields must be ' +
                           'specified when --input-schema is set to customeventschema.')

    input_schema_mapping = get_input_schema_mapping(
        input_mapping_fields,
        input_mapping_default_values)

    return input_schema, input_schema_mapping


def _list_event_subscriptions_by_resource_id(client, resource_id, oDataQuery, top):
    # parse_resource_id doesn't handle resource_ids for Azure subscriptions and RGs
    # so, first try to look for those two patterns.
    if resource_id is not None:
        id_parts = list(filter(None, resource_id.split('/')))
        if len(id_parts) < 5:
            # Azure subscriptions or Resource group
            if id_parts[0].lower() != "subscriptions":
                raise CLIError('The specified value for resource-id is not in the'
                               ' expected format. It should start with /subscriptions.')

            subscription_id = id_parts[1]
            _validate_subscription_id_matches_default_subscription_id(
                default_subscription_id=client.config.subscription_id,
                provided_subscription_id=subscription_id)

            if len(id_parts) == 2:
                return client.list_global_by_subscription_for_topic_type(
                    "Microsoft.Resources.Subscriptions",
                    oDataQuery,
                    top)

            if len(id_parts) == 4 and id_parts[2].lower() == "resourcegroups":
                resource_group_name = id_parts[3]
                if resource_group_name is None:
                    raise CLIError('The specified value for resource-id is not'
                                   ' in the expected format. A valid value for'
                                   ' resource group must be provided.')
                return client.list_global_by_resource_group_for_topic_type(
                    resource_group_name,
                    "Microsoft.Resources.ResourceGroups",
                    oDataQuery,
                    top)

    id_parts = parse_resource_id(resource_id)
    subscription_id = id_parts.get('subscription')
    _validate_subscription_id_matches_default_subscription_id(
        default_subscription_id=client.config.subscription_id,
        provided_subscription_id=subscription_id)

    rg_name = id_parts.get('resource_group')
    resource_name = id_parts.get('name')
    namespace = id_parts.get('namespace')
    resource_type = id_parts.get('type')

    if (subscription_id is None or rg_name is None or resource_name is None or
            namespace is None or resource_type is None):
        raise CLIError('The specified value for resource-id is not'
                       ' in the expected format.')

    # If this is for a domain topic, invoke the appropriate operation
    if (namespace.lower() == EVENTGRID_NAMESPACE.lower() and resource_type.lower() == EVENTGRID_DOMAINS.lower()):
        child_resource_type = id_parts.get('child_type_1')
        child_resource_name = id_parts.get('child_name_1')

        if (child_resource_type is not None and child_resource_type.lower() == EVENTGRID_TOPICS.lower() and
                child_resource_name is not None):
            return client.list_by_domain_topic(rg_name, resource_name, child_resource_name, oDataQuery, top)

    # Not a domain topic, invoke the standard list_by_resource
    return client.list_by_resource(
        rg_name,
        namespace,
        resource_type,
        resource_name,
        oDataQuery,
        top)


def _is_topic_type_global_resource(topic_type_name):
    # TODO: Add here if any other global topic types get added in the future.
    TOPIC_TYPE_AZURE_SUBSCRIPTIONS = "Microsoft.Resources.Subscriptions"
    TOPIC_TYPE_AZURE_RESOURCE_GROUP = "Microsoft.Resources.ResourceGroups"
    TOPIC_TYPE_MAPS_ACCOUNTS = "Microsoft.Maps.Accounts"

    if (topic_type_name.lower() == TOPIC_TYPE_AZURE_SUBSCRIPTIONS.lower() or
            topic_type_name.lower() == TOPIC_TYPE_MAPS_ACCOUNTS or
            topic_type_name.lower() == TOPIC_TYPE_AZURE_RESOURCE_GROUP.lower()):
        return True

    return False


def _validate_subscription_id_matches_default_subscription_id(
        default_subscription_id,
        provided_subscription_id):
    # The CLI/SDK infrastructure doesn't support overriding the subscription ID.
    # Hence, we validate that the provided subscription ID is the same as the default
    # configured subscription.
    if provided_subscription_id.lower() != default_subscription_id.lower():
        raise CLIError('The subscription ID in the specified resource-id'
                       ' does not match the default subscription ID. To set the default subscription ID,'
                       ' use az account set ID_OR_NAME, or use the global argument --subscription ')
