# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

from knack.log import get_logger
from .util import get_id_from_azure_resource

logger = get_logger(__name__)


def execute_query(cmd, client, application, analytics_query, timespan=None, applications=None):
    """Executes a query against the provided Application Insights application."""
    from .vendored_sdks.applicationinsights.models import QueryBody
    return client.query.execute(get_id_from_azure_resource(cmd.cli_ctx, application), QueryBody(query=analytics_query, timespan=timespan, applications=applications))


def get_event(cmd, client, application, event_type, event, timespan=None):
    return client.events.get(get_id_from_azure_resource(cmd.cli_ctx, application), event_type, event, timespan=timespan)


def get_events_by_type(cmd, client, application, event_type, timespan=None):
    return client.events.get_by_type(get_id_from_azure_resource(cmd.cli_ctx, application), event_type, timespan=timespan)


def get_metric(cmd, client, application, metric, timespan=None, aggregation=None, segment=None, top=None, orderby=None, filter_arg=None):
    return client.metrics.get(get_id_from_azure_resource(cmd.cli_ctx, application), metric, timespan=timespan, aggregation=aggregation, segment=segment, top=top, orderby=orderby, filter_arg=filter_arg)


def get_metrics_metadata(cmd, client, application):
    return client.metrics.get_metadata(get_id_from_azure_resource(cmd.cli_ctx, application))
