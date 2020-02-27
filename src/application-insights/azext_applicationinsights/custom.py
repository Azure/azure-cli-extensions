# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

from knack.util import CLIError
from knack.log import get_logger
from .util import get_id_from_azure_resource, get_query_targets, get_timespan, get_linked_properties

logger = get_logger(__name__)


def execute_query(cmd, client, application, analytics_query, start_time=None, end_time=None, offset='1h', resource_group_name=None):
    """Executes a query against the provided Application Insights application."""
    from .vendored_sdks.applicationinsights.models import QueryBody
    targets = get_query_targets(cmd.cli_ctx, application, resource_group_name)
    return client.query.execute(targets[0], QueryBody(query=analytics_query, timespan=get_timespan(cmd.cli_ctx, start_time, end_time, offset), applications=targets[1:]))


def get_events(cmd, client, application, event_type, event=None, start_time=None, end_time=None, offset='1h', resource_group_name=None):
    timespan = get_timespan(cmd.cli_ctx, start_time, end_time, offset)
    if event:
        return client.events.get(get_id_from_azure_resource(cmd.cli_ctx, application, resource_group=resource_group_name), event_type, event, timespan=timespan)
    return client.events.get_by_type(get_id_from_azure_resource(cmd.cli_ctx, application, resource_group=resource_group_name), event_type, timespan=get_timespan(cmd.cli_ctx, start_time, end_time, offset))


def get_metric(cmd, client, application, metric, start_time=None, end_time=None, offset='1h', interval=None, aggregation=None, segment=None, top=None, orderby=None, filter_arg=None, resource_group_name=None):
    return client.metrics.get(get_id_from_azure_resource(cmd.cli_ctx, application, resource_group=resource_group_name), metric, timespan=get_timespan(cmd.cli_ctx, start_time, end_time, offset), interval=interval, aggregation=aggregation, segment=segment, top=top, orderby=orderby, filter_arg=filter_arg)


def get_metrics_metadata(cmd, client, application, resource_group_name=None):
    return client.metrics.get_metadata(get_id_from_azure_resource(cmd.cli_ctx, application, resource_group=resource_group_name))


def create_or_update_component(client, application, resource_group_name, location, tags=None, kind="web", application_type='web'):
    from .vendored_sdks.mgmt_applicationinsights.models import ApplicationInsightsComponent
    component = ApplicationInsightsComponent(location, kind, application_type=application_type, tags=tags)
    return client.create_or_update(resource_group_name, application, component)


def update_component(client, application, resource_group_name, kind=None):
    existing_component = client.get(resource_group_name, application)
    if kind:
        existing_component.kind = kind
    return client.create_or_update(resource_group_name, application, existing_component)


def update_component_tags(client, application, resource_group_name, tags):
    return client.update_tags(resource_group_name, application, tags)


def get_component(client, application, resource_group_name):
    return client.get(resource_group_name, application)


def show_components(client, application=None, resource_group_name=None):
    if application:
        if resource_group_name:
            return client.get(resource_group_name, application)
        raise CLIError("Application provided without resource group. Either specify app with resource group, or remove app.")
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name)
    return client.list()


def delete_component(client, application, resource_group_name):
    return client.delete(resource_group_name, application)


def create_api_key(cmd, client, application, resource_group_name, api_key, read_properties=None, write_properties=None):
    from .vendored_sdks.mgmt_applicationinsights.models import APIKeyRequest
    if read_properties is None:
        read_properties = ['ReadTelemetry', 'AuthenticateSDKControlChannel']
    if write_properties is None:
        write_properties = ['WriteAnnotations']
    linked_read_properties, linked_write_properties = get_linked_properties(cmd.cli_ctx, application, resource_group_name, read_properties, write_properties)
    api_key_request = APIKeyRequest(api_key, linked_read_properties, linked_write_properties)
    return client.create(resource_group_name, application, api_key_request)


def show_api_key(client, application, resource_group_name, api_key=None):
    if api_key is None:
        return client.list(resource_group_name, application)
    result = list(filter(lambda result: result.name == api_key, client.list(resource_group_name, application)))
    if len(result) == 1:
        return result[0]
    if len(result) > 1:
        return result
    return None


def delete_api_key(client, application, resource_group_name, api_key):
    existing_key = list(filter(lambda result: result.name == api_key, client.list(resource_group_name, application)))
    if existing_key != []:
        return client.delete(resource_group_name, application, existing_key[0].id.split('/')[-1])
    raise CLIError('--api-key provided but key not found for deletion.')


def show_component_billing(client, application, resource_group_name):
    return client.get(resource_group_name=resource_group_name, resource_name=application)


def update_component_billing(client, application, resource_group_name, cap=None, stop_sending_notification_when_hitting_cap=None):
    billing_features = client.get(resource_group_name=resource_group_name, resource_name=application)
    if cap is not None:
        billing_features.data_volume_cap.cap = cap
    if stop_sending_notification_when_hitting_cap is not None:
        billing_features.data_volume_cap.stop_send_notification_when_hit_cap = stop_sending_notification_when_hitting_cap
    return client.update(resource_group_name=resource_group_name,
                         resource_name=application,
                         data_volume_cap=billing_features.data_volume_cap,
                         current_billing_features=billing_features.current_billing_features)
