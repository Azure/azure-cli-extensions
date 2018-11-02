# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

from knack.log import get_logger

logger = get_logger(__name__)


def execute_query(client, application, analytics_query, timespan=None, applications=None):
    """Executes a query against the provided Application Insights application."""
    from .vendored_sdks.applicationinsights.models import QueryBody
    return client.query.execute(application, QueryBody(query=analytics_query, timespan=timespan, applications=applications))

def get_events(client, application, event_type, event_id, timespan=None):
    return client.events.get(application, event_type, event_id, timespan=timespan)

def get_events_by_type(client, application, event_type, event_id, timespan=None):
    return client.events.get(application, event_type, event_id, timespan=timespan)

def get_metric(client, application, metric_id, timespan=None, aggregation=None, segment=None, top=None, orderby=None, filter_arg=None):
    return client.metrics.get(application, metric_id, timespan=timespan, aggregation=aggregation, segment=segment, top=top, orderby=orderby, filter_arg=filter_arg)

def get_metrics(client, application, metric_id, timespan=None, aggregation=None, segment=None, top=None, orderby=None, filter_arg=None):
    return client.metrics.get(application, metric_id, timespan=timespan, aggregation=aggregation, segment=segment, top=top, orderby=orderby, filter_arg=filter_arg)

def get_metrics_metadata(client, application):
    return client.metrics.get_metadata(application)