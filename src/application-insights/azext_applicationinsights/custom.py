# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

from knack.log import get_logger
from .util import get_id_from_azure_resource, get_query_targets

logger = get_logger(__name__)


def execute_query(cmd, client, application, analytics_query, timespan=None, resource_group_name=None):
    """Executes a query against the provided Application Insights application."""
    from .vendored_sdks.applicationinsights.models import QueryBody
    targets = get_query_targets(cmd.cli_ctx, application, resource_group_name)
    return client.query.execute(targets[0], QueryBody(query=analytics_query, timespan=timespan, applications=targets[1:]))


def get_events(cmd, client, application, event_type, event=None, timespan=None, resource_group_name=None):
    if event:
        return client.events.get(get_id_from_azure_resource(cmd.cli_ctx, application, resource_group=resource_group_name), event_type, event, timespan=timespan)
    return client.events.get_by_type(get_id_from_azure_resource(cmd.cli_ctx, application, resource_group=resource_group_name), event_type, timespan=timespan)
    

def get_metric(cmd, client, application, metric, timespan=None, aggregation=None, segment=None, top=None, orderby=None, filter_arg=None, resource_group_name=None):
    return client.metrics.get(get_id_from_azure_resource(cmd.cli_ctx, application, resource_group=resource_group_name), metric, timespan=timespan, aggregation=aggregation, segment=segment, top=top, orderby=orderby, filter_arg=filter_arg)


def get_metrics_metadata(cmd, client, application, resource_group_name=None):
    return client.metrics.get_metadata(get_id_from_azure_resource(cmd.cli_ctx, application, resource_group=resource_group_name))
