# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import requests

from knack.util import CLIError

from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.profiles import ResourceType
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.util import should_disable_connection_verify


def create_grafana(cmd, resource_group_name, grafana_name,
                   enable_system_assigned_identity=True, location=None):
    client = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES)
    resource = {
        "sku": {
            "name": "standard"
        },
        "location": location,
        "identity": {"type": "SystemAssigned"} if enable_system_assigned_identity else None
    }
    return client.resources.begin_create_or_update(resource_group_name, "Microsoft.Dashboard", "",
                                                   "grafana", grafana_name, "2021-09-01-preview", resource)


def list_grafana(cmd, resource_group_name=None):
    filters = []
    if resource_group_name:
        filters.append("resourceGroup eq '{}'".format(resource_group_name))
    filters.append("resourceType eq 'Microsoft.Dashboard/grafana'")
    odata_filter = ' and '.join(filters)

    expand = "createdTime,changedTime,provisioningState"
    client = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES)
    resources = client.resources.list(filter=odata_filter, expand=expand)
    return list(resources)


def show_grafana(cmd, grafana_name, resource_group_name=None):
    client = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES)
    return client.resources.get(resource_group_name, "Microsoft.Dashboard",
                                "", "grafana", grafana_name, "2021-09-01-preview")


def delete_grafana(cmd, grafana_name, resource_group_name=None):
    client = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES)
    return client.resources.begin_delete(resource_group_name, "Microsoft.Dashboard",
                                         "", "grafana", grafana_name, "2021-09-01-preview")


def show_dashboard(cmd, grafana_name, uid=None, show_home_dashboard=None, resource_group_name=None):
    if uid:
        path = "/api/dashboards/uid/" + uid
    elif show_home_dashboard:
        path = "/api/dashboards/home"
    else:
        path = "/api/search"

    response = _send_request(cmd, resource_group_name, grafana_name, "get", path)
    return json.loads(response.content)


def list_dashboards(cmd, grafana_name, resource_group_name=None):
    return show_dashboard(cmd, resource_group_name=resource_group_name, grafana_name=grafana_name, show_home_dashboard=None)


def create_dashboard(cmd, grafana_name, dashboard_definition, resource_group_name):
    dashboard_definition = _try_load_file_content(dashboard_definition)
    response = _send_request(cmd, resource_group_name, grafana_name, "post", "/api/dashboards/db", dashboard_definition)
    return json.loads(response.content)


def update_dashboard(cmd, resource_group_name, grafana_name, dashboard_definition):
    return create_dashboard(cmd, grafana_name, dashboard_definition, resource_group_name)


def delete_dashboard(cmd, grafana_name, uid, resource_group_name):
    _send_request(cmd, resource_group_name, grafana_name, "delete", "/api/dashboards/uid/" + uid)


def list_data_sources(cmd, resource_group_name, grafana_name):
    response = _send_request(cmd, resource_group_name, grafana_name, "get", "/api/datasources")
    return json.loads(response.content)


def show_data_source(cmd, resource_group_name, grafana_name, data_source):
    return _find_data_source(cmd, resource_group_name, grafana_name, data_source)


def create_data_source(cmd, resource_group_name, grafana_name, definition):
    response = _send_request(cmd, resource_group_name, grafana_name, "post", "/api/datasources", definition)
    return json.loads(response.content)


def delete_data_source(cmd, resource_group_name, grafana_name, data_source):
    data = _find_data_source(cmd, resource_group_name, grafana_name, data_source)
    _send_request(cmd, resource_group_name, grafana_name, "delete", "/api/datasources/uid/" + data['uid'])


def query_data_source(cmd, resource_group_name, grafana_name, data_source, time_from=None, time_to=None,
                      max_data_points=100, internal_ms=1000, conditions=None):
    if not time_from or not time_to:  # TODO accept tiem string
        import datetime, time
        right_now = datetime.datetime.now()
        if not time_from:
            time_from = time.mktime((right_now - datetime.timedelta(hours=1)).timetuple()) * 1000
        if not time_to:
            time_to = time.mktime(right_now.timetuple()) * 1000
    data_source_id = _find_data_source(cmd, resource_group_name, grafana_name, data_source)['id']

    data = {
        "from": time_from,
        "to": time_to,
        "queries":[{
            "intervalMs": internal_ms,
            "maxDataPoints": max_data_points,
            "datasourceId": data_source_id,
            "format": "time_series"
        }]
    }

    if conditions:
        for c in json.loads(conditions):
            k, v = c.split('=', 1)
            data['queries'][k] = v

    response = _send_request(cmd, resource_group_name, grafana_name, "post", "/api/tsdb/query")
    return json.loads(response.content)


def _find_data_source(cmd, resource_group_name, grafana_name, data_source):
    response = _send_request(cmd, resource_group_name, grafana_name, "get", "/api/datasources/name/" + data_source)
    if response.status_code >= 400:
        response = _send_request(cmd, resource_group_name, grafana_name, "get", "/api/datasources/" + data_source)
        if response.status_code >= 400:
            response = _send_request(cmd, resource_group_name, grafana_name, "get", "/api/datasources/uid/" + data_source)
    if response.status_code >= 400:
        raise CLIError("Not found. Ex: {}".format(response.status_code))
    return json.loads(response.content)


# For UX: we accept a file path for complex payload such as dashboard/data-source definition
def _try_load_file_content(file_content):
    import os
    potentail_file_path = os.path.expanduser(file_content)
    if os.path.exists(potentail_file_path):
        from azure.cli.core.util import read_file_content
        file_content = read_file_content(potentail_file_path)
    return file_content


def _send_request(cmd, resource_group_name, grafana_name, http_method, path, body=None):
    grafana = show_grafana(cmd, grafana_name, resource_group_name)
    endpoint = grafana.properties["endpoint"]

    from azure.cli.core._profile import Profile
    profile = Profile(cli_ctx=cmd.cli_ctx)
    # this might be a cross tenant scenario, so pass subscription to get_raw_token
    subscription = get_subscription_id(cmd.cli_ctx)
    creds, _, _ = profile.get_raw_token(subscription=subscription,
                                        resource="ce34e7e5-485f-4d76-964f-b3d2b16d1e4f")  # TODO, support dogfood

    headers = {
        'Content-Type': 'application/json',
        'authorization': 'Bearer ' + creds[1]
    }

    return requests.request(http_method, 
                            url=endpoint + path, 
                            headers=headers, 
                            data=body,
                            verify=(not should_disable_connection_verify()))
