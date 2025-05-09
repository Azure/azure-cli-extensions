# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from enum import Enum
from datetime import datetime
import dateutil.parser  # pylint: disable=import-error
from azure.mgmt.core.tools import is_valid_resource_id, parse_resource_id
from azext_applicationinsights._client_factory import applicationinsights_mgmt_plane_client


class EventType(str, Enum):
    all = "$all"
    traces = "traces"
    custom_events = "customEvents"
    page_views = "pageViews"
    browser_timings = "browserTimings"
    requests = "requests"
    dependencies = "dependencies"
    exceptions = "exceptions"
    availability_results = "availabilityResults"
    performance_counters = "performanceCounters"
    custom_metrics = "customMetrics"


def get_id_from_azure_resource(cli_ctx, app, resource_group=None):
    if is_valid_resource_id(app):
        parsed = parse_resource_id(app)
        resource_group, name, subscription = parsed["resource_group"], parsed["name"], parsed["subscription"]
        client = applicationinsights_mgmt_plane_client(cli_ctx, subscription_id=subscription,
                                                       api_version='2015-05-01').components
        return client.get(resource_group, name).app_id
    if resource_group:
        client = applicationinsights_mgmt_plane_client(cli_ctx, api_version='2015-05-01').components
        return client.get(resource_group, app).app_id
    return app


def get_query_targets(cli_ctx, apps, resource_group):
    """Produces a list of uniform GUIDs representing applications to query."""
    if isinstance(apps, list):
        if resource_group:
            return [get_id_from_azure_resource(cli_ctx, apps[0], resource_group)]
        return list(map(lambda x: get_id_from_azure_resource(cli_ctx, x), apps))
    if resource_group:
        return [get_id_from_azure_resource(cli_ctx, apps, resource_group)]
    return apps


def get_timespan(_, start_time=None, end_time=None, offset=None):
    if not start_time and not end_time:
        # if neither value provided, end_time is now
        end_time = datetime.utcnow().isoformat()
    if not start_time:
        # if no start_time, apply offset backwards from end_time
        start_time = (dateutil.parser.parse(end_time) - offset).isoformat()
    elif not end_time:
        # if no end_time, apply offset fowards from start_time
        end_time = (dateutil.parser.parse(start_time) + offset).isoformat()
    timespan = f'{start_time}/{end_time}'
    return timespan


def get_linked_properties(cli_ctx, app, resource_group, read_properties=None, write_properties=None):
    """Maps user-facing role names to strings used to identify them on resources."""
    roles = {
        "ReadTelemetry": "api",
        "WriteAnnotations": "annotations",
        "AuthenticateSDKControlChannel": "agentconfig"
    }

    sub_id = cli_ctx.subscription_id
    tmpl = f'/subscriptions/{sub_id}/resourceGroups/{resource_group}/providers/microsoft.insights/components/{app}'
    linked_read_properties, linked_write_properties = [], []

    if isinstance(read_properties, list):
        propLen = len(read_properties)
        linked_read_properties = [f'{tmpl}/{roles[read_properties[i]]}' for i in range(propLen) if read_properties[i]]  # pylint: disable=line-too-long
    else:
        linked_read_properties = [f'{tmpl}/{roles[read_properties]}']
    if isinstance(write_properties, list):
        propLen = len(write_properties)
        linked_write_properties = [f'{tmpl}/{roles[write_properties[i]]}' for i in range(propLen) if write_properties[i]]  # pylint: disable=line-too-long
    else:
        linked_write_properties = [f'{tmpl}/{roles[write_properties]}']
    return linked_read_properties, linked_write_properties
