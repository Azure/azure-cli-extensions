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
    # r = '{{"sku": {{"name": "Basic"}}, "location": "{0}"}}'.format(location)
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


def show_grafana(cmd, resource_group_name, grafana_name):
    client = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES)
    return client.resources.get(resource_group_name, "Microsoft.Dashboard",
                                "", "grafana", grafana_name, "2021-09-01-preview")


def delete_grafana(cmd, resource_group_name, grafana_name):
    client = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES)
    return client.resources.begin_delete(resource_group_name, "Microsoft.Dashboard",
                                         "", "grafana", grafana_name, "2021-09-01-preview")


def show_dashboard(cmd, resource_group_name, grafana_name, uid=None, show_home_dashboard=None):
    if uid:
        path = "/api/dashboards/uid/" + uid
    elif show_home_dashboard:
        path = "/api/dashboards/home"
    else:
        path = "/api/search"

    response = _send_request(cmd, resource_group_name, grafana_name, "get", path)
    return json.loads(response.content)


def list_dashboards(cmd, resource_group_name, grafana_name):
    return show_dashboard(cmd, resource_group_name, grafana_name, None)


def create_dashboard(cmd, resource_group_name, grafana_name, dashboard_definition):
    import os
    potentail_file_path = os.path.expanduser(dashboard_definition)
    if os.path.exists(potentail_file_path):
        from azure.cli.core.util import read_file_content
        dashboard_definition = read_file_content(potentail_file_path)
    response = _send_request(cmd, resource_group_name, grafana_name, "post", "/api/dashboards/db", dashboard_definition)
    return json.loads(response.content)


def update_dashboard(cmd, resource_group_name, grafana_name, dashboard_definition):
    return create_dashboard(cmd, resource_group_name, grafana_name, dashboard_definition)


def delete_dashboard(cmd, resource_group_name, grafana_name, uid):
    _send_request(cmd, resource_group_name, grafana_name, "delete", "/api/dashboards/uid/" + uid)


def list_data_sources(cmd, resource_group_name, grafana_name):
    response = _send_request(cmd, resource_group_name, grafana_name, "get", "/api/datasources")
    return json.loads(response.content)


def create_data_source(cmd, resource_group_name, grafana_name, data_source_type, data_source_subscription=None, data_source_name=None):
    # TODO make it easier

    #data_source = {
    #    "access": "proxy",
    #    "basicAuth": False,
    #    # "database": "",
    #    # "id": 1,
    #    # "isDefault": false,
    #    "jsonData": {
    #        "azureAuthType": "msi",
    #        "subscriptionId": data_source_subscription or get_subscription_id(cmd.cli_ctx)
    #    },
    #    "name": data_source_name or data_source_type,  # "Azure Monitor",
    #    # "orgId": 1,
    #    # "password": "",
    #    # "readOnly": false,
    #    "type": data_source_type,  # "grafana-azure-monitor-datasource",
    #    # "typeLogoUrl": "public/app/plugins/datasource/grafana-azure-monitor-datasource/img/logo.jpg",
    #    # "typeName": "Azure Monitor",
    #    # "uid": "azure-monitor-oob",
    #    # "url": "",
    #    # "user": ""
    #}

    response = _send_request(cmd, resource_group_name, grafana_name, "post", "/api/datasources", data_source)
    return json.loads(response.content)


def _send_request(cmd, resource_group_name, grafana_name, http_method, path, body=None):
    grafana = show_grafana(cmd, resource_group_name, grafana_name)
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
