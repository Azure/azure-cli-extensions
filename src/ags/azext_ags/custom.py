# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import requests

from knack.util import CLIError
from knack.log import get_logger

from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.profiles import ResourceType
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.util import should_disable_connection_verify

logger = get_logger(__name__)


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
    odata_filter = " and ".join(filters)

    expand = "createdTime,changedTime,provisioningState"
    client = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES)
    resources = client.resources.list(filter=odata_filter, expand=expand)
    return list(resources)


def show_grafana(cmd, grafana_name, resource_group_name=None):
    client = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES)
    return client.resources.get(resource_group_name, "Microsoft.Dashboard",
                                "", "grafana", grafana_name, "2021-09-01-preview")


def delete_grafana(cmd, grafana_name, yes=False, resource_group_name=None):
    from azure.cli.core.util import user_confirmation
    user_confirmation("Are you sure you want to delete the Grafana workspace '{}'?".format(grafana_name), yes)
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
    return show_dashboard(cmd, resource_group_name=resource_group_name,
                          grafana_name=grafana_name, show_home_dashboard=None)


def create_dashboard(cmd, grafana_name, definition, resource_group_name=None):
    definition = _try_load_file_content(definition)
    response = _send_request(cmd, resource_group_name, grafana_name, "post", "/api/dashboards/db",
                             json.loads(definition))
    return json.loads(response.content)


def update_dashboard(cmd, grafana_name, definition, resource_group_name=None):
    return create_dashboard(cmd, grafana_name, definition, resource_group_name)


def delete_dashboard(cmd, grafana_name, uid, resource_group_name=None):
    _send_request(cmd, resource_group_name, grafana_name, "delete", "/api/dashboards/uid/" + uid)


def create_data_source(cmd, grafana_name, definition, resource_group_name=None):
    definition = _try_load_file_content(definition)
    payload = json.loads(definition)
    response = _send_request(cmd, resource_group_name, grafana_name, "post", "/api/datasources", payload)
    return json.loads(response.content)


def show_data_source(cmd, grafana_name, data_source, resource_group_name=None):
    return _find_data_source(cmd, resource_group_name, grafana_name, data_source)


def delete_data_source(cmd, grafana_name, data_source, resource_group_name=None):
    data = _find_data_source(cmd, resource_group_name, grafana_name, data_source)
    _send_request(cmd, resource_group_name, grafana_name, "delete", "/api/datasources/uid/" + data["uid"])


def list_data_sources(cmd, grafana_name, resource_group_name=None):
    response = _send_request(cmd, resource_group_name, grafana_name, "get", "/api/datasources")
    return json.loads(response.content)


def update_data_source(cmd, grafana_name, data_source, definition, resource_group_name=None):
    definition = _try_load_file_content(definition)
    data = _find_data_source(cmd, resource_group_name, grafana_name, data_source)
    response = _send_request(cmd, resource_group_name, grafana_name, "put", "/api/datasources/" + str(data['id']),
                             json.loads(definition))
    return json.loads(response.content)


def create_folder(cmd, grafana_name, title, resource_group_name=None):
    payload = {
        "title": title
    }
    response = _send_request(cmd, resource_group_name, grafana_name, "post", "/api/folders", payload)
    return json.loads(response.content)


def list_folders(cmd, grafana_name, resource_group_name=None):
    response = _send_request(cmd, resource_group_name, grafana_name, "get", "/api/folders")
    return json.loads(response.content)


def update_folder(cmd, grafana_name, folder, title, resource_group_name=None):
    f = show_folder(cmd, grafana_name, folder, resource_group_name)
    version = f['version']
    data = {
        "title": title,
        "version": int(version)
    }
    response = _send_request(cmd, resource_group_name, grafana_name, "put", "/api/folders/" + f["uid"], data)
    return json.loads(response.content)


def show_folder(cmd, grafana_name, folder, resource_group_name=None):
    return _find_folder(cmd, resource_group_name, grafana_name, folder)


def delete_folder(cmd, grafana_name, folder, resource_group_name=None):
    data = _find_folder(cmd, resource_group_name, grafana_name, folder)
    _send_request(cmd, resource_group_name, grafana_name, "delete", "/api/folders/" + data['uid'])


def _find_folder(cmd, resource_group_name, grafana_name, folder):
    response = _send_request(cmd, resource_group_name, grafana_name, "get", "/api/folders/id/" + folder,
                             raise_for_error_status=False)
    if response.status_code >= 400 or not json.loads(response.content)['uid']:
        response = _send_request(cmd, resource_group_name, grafana_name, "get", "/api/folders/" + folder,
                                 raise_for_error_status=False)
    if response.status_code >= 400:
        raise CLIError("Not found. Ex: {}".format(response.status_code))
    return json.loads(response.content)


def get_actual_user(cmd, grafana_name, resource_group_name=None):
    response = _send_request(cmd, resource_group_name, grafana_name, "get", "/api/user")
    return json.loads(response.content)


def list_users(cmd, grafana_name, resource_group_name=None):
    response = _send_request(cmd, resource_group_name, grafana_name, "get", "/api/org/users")
    return json.loads(response.content)


def show_user(cmd, grafana_name, user, resource_group_name=None):
    if "@" in user:
        uri = "/api/org/users/lookup?loginOrEmail="
    else:
        raise CLIError("Searching by id other than login name or email is not yet supported")

    response = _send_request(cmd, resource_group_name, grafana_name, "get", uri + user)
    return json.loads(response.content)


def query_data_source(cmd, grafana_name, data_source, time_from=None, time_to=None,
                      max_data_points=100, internal_ms=1000, conditions=None, resource_group_name=None):
    import datetime
    import time
    from dateutil import parser
    right_now = datetime.datetime.now()

    if time_from:
        time_from = parser.parse(time_from)
    else:
        time_from = right_now - datetime.timedelta(hours=1)
    time_from_epoch = time.mktime(time_from.timetuple()) * 1000

    if time_to:
        time_to = parser.parse(time_to)
    else:
        time_to = right_now
    time_to_epoch = time.mktime(time_to.timetuple()) * 1000

    data_source_id = _find_data_source(cmd, resource_group_name, grafana_name, data_source)["id"]

    data = {
        "from": time_from_epoch,
        "to": time_to_epoch,
        "queries": [{
            "intervalMs": internal_ms,
            "maxDataPoints": max_data_points,
            "datasourceId": data_source_id,
            "format": "time_series"
        }]
    }

    if conditions:
        for c in json.loads(conditions):
            k, v = c.split("=", 1)
            data["queries"][k] = v

    response = _send_request(cmd, resource_group_name, grafana_name, "post", "/api/tsdb/query")
    return json.loads(response.content)


def _find_data_source(cmd, resource_group_name, grafana_name, data_source):
    response = _send_request(cmd, resource_group_name, grafana_name, "get", "/api/datasources/name/" + data_source,
                             raise_for_error_status=False)
    if response.status_code >= 400:
        response = _send_request(cmd, resource_group_name, grafana_name, "get", "/api/datasources/" + data_source,
                                 raise_for_error_status=False)
        if response.status_code >= 400:
            response = _send_request(cmd, resource_group_name, grafana_name,
                                     "get", "/api/datasources/uid/" + data_source,
                                     raise_for_error_status=False)
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


def _send_request(cmd, resource_group_name, grafana_name, http_method, path, body=None, raise_for_error_status=True):
    grafana = show_grafana(cmd, grafana_name, resource_group_name)
    endpoint = grafana.properties["endpoint"]

    from azure.cli.core._profile import Profile
    profile = Profile(cli_ctx=cmd.cli_ctx)
    # this might be a cross tenant scenario, so pass subscription to get_raw_token
    subscription = get_subscription_id(cmd.cli_ctx)
    ags_first_party_app = ("7f525cdc-1f08-4afa-af7c-84709d42f5d3"
                           if "-ppe." in cmd.cli_ctx.cloud.endpoints.active_directory
                           else "ce34e7e5-485f-4d76-964f-b3d2b16d1e4f")
    creds, _, _ = profile.get_raw_token(subscription=subscription,
                                        resource=ags_first_party_app + "/.default")

    headers = {
        "content-type": "application/json",
        "authorization": "Bearer " + creds[1]
    }

    # TODO: handle re-try on 429
    response = requests.request(http_method,
                                url=endpoint + path,
                                headers=headers,
                                json=body,
                                verify=(not should_disable_connection_verify()))
    if response.status_code >= 400:
        if raise_for_error_status:
            logger.warning(str(response.content))
            response.raise_for_status()
    # TODO: log headers, requests and response
    return response
