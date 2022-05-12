# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import requests

from msrestazure.azure_exceptions import CloudError

from knack.log import get_logger

from azure.cli.core.commands import LongRunningOperation
from azure.cli.core.commands.client_factory import get_mgmt_service_client, get_subscription_id
from azure.cli.core.profiles import ResourceType, get_sdk
from azure.cli.core.util import should_disable_connection_verify
from azure.cli.core.azclierror import ArgumentUsageError, CLIInternalError

from ._client_factory import cf_amg

logger = get_logger(__name__)


grafana_endpoints = {}


def create_grafana(cmd, resource_group_name, grafana_name,
                   location=None, skip_system_assigned_identity=False, skip_role_assignments=False,
                   tags=None, zone_redundancy=None):
    from azure.cli.core.commands.arm import resolve_role_id

    client = cf_amg(cmd.cli_ctx)
    resource = {
        "sku": {
            "name": "standard"
        },
        "location": location,
        "identity": None if skip_system_assigned_identity else {"type": "SystemAssigned"},
        "tags": tags
    }
    resource["properties"] = {
        "zoneRedundancy": zone_redundancy
    }

    poller = client.grafana.begin_create(resource_group_name, grafana_name, resource)
    LongRunningOperation(cmd.cli_ctx)(poller)

    if skip_role_assignments:
        return poller
    resource = LongRunningOperation(cmd.cli_ctx)(poller)

    logger.warning("Grafana instance of '%s' was created. Now creating default role assignments for its "
                   "managed identity and current CLI user", grafana_name)

    subscription_scope = '/subscriptions/' + client._config.subscription_id  # pylint: disable=protected-access

    user_principal_id = _get_login_account_principal_id(cmd.cli_ctx)
    grafana_admin_role_id = resolve_role_id(cmd.cli_ctx, "Grafana Admin", subscription_scope)
    _create_role_assignment(cmd.cli_ctx, user_principal_id, grafana_admin_role_id, resource.id)

    if resource.identity:
        monitoring_reader_role_id = resolve_role_id(cmd.cli_ctx, "Monitoring Reader", subscription_scope)
        _create_role_assignment(cmd.cli_ctx, resource.identity.principal_id, monitoring_reader_role_id,
                                subscription_scope)

    return resource


def _get_login_account_principal_id(cli_ctx):
    from azure.cli.core._profile import Profile
    from azure.graphrbac import GraphRbacManagementClient
    profile = Profile(cli_ctx=cli_ctx)
    cred, _, tenant_id = profile.get_login_credentials(
        resource=cli_ctx.cloud.endpoints.active_directory_graph_resource_id)
    client = GraphRbacManagementClient(cred, tenant_id,
                                       base_url=cli_ctx.cloud.endpoints.active_directory_graph_resource_id)
    assignee = profile.get_current_account_user()
    result = list(client.users.list(filter=f"userPrincipalName eq '{assignee}'"))
    if not result:
        result = list(client.service_principals.list(
            filter=f"servicePrincipalNames/any(c:c eq '{assignee}')"))
    if not result:
        raise CLIInternalError((f"Failed to retrieve principal id for '{assignee}', which is needed to create a "
                                f"role assignment"))
    return result[0].object_id


def _create_role_assignment(cli_ctx, principal_id, role_definition_id, scope):
    import time
    import uuid
    assignments_client = get_mgmt_service_client(cli_ctx, ResourceType.MGMT_AUTHORIZATION).role_assignments
    RoleAssignmentCreateParameters = get_sdk(cli_ctx, ResourceType.MGMT_AUTHORIZATION,
                                             'RoleAssignmentCreateParameters', mod='models',
                                             operation_group='role_assignments')
    parameters = RoleAssignmentCreateParameters(role_definition_id=role_definition_id, principal_id=principal_id)

    logger.info("Creating an assignment with a role '%s' on the scope of '%s'", role_definition_id, scope)
    retry_times = 36
    assignment_name = uuid.uuid4()
    for retry_time in range(0, retry_times):
        try:
            assignments_client.create(scope=scope, role_assignment_name=assignment_name,
                                      parameters=parameters)
            break
        except CloudError as ex:
            if 'role assignment already exists' in ex.message:
                logger.info('Role assignment already exists')
                break
            if retry_time < retry_times and ' does not exist in the directory ' in ex.message:
                time.sleep(5)
                logger.warning('Retrying role assignment creation: %s/%s', retry_time + 1,
                               retry_times)
                continue
            raise


def _delete_role_assignment(cli_ctx, principal_id):
    assignments_client = get_mgmt_service_client(cli_ctx, ResourceType.MGMT_AUTHORIZATION).role_assignments
    f = f"principalId eq '{principal_id}'"
    assignments = list(assignments_client.list(filter=f))
    for a in assignments or []:
        assignments_client.delete_by_id(a.id)


def list_grafana(cmd, resource_group_name=None):
    client = cf_amg(cmd.cli_ctx)
    if resource_group_name:
        return client.grafana.list_by_resource_group(resource_group_name)
    return client.grafana.list()


def show_grafana(cmd, grafana_name, resource_group_name=None):
    client = cf_amg(cmd.cli_ctx)
    return client.grafana.get(resource_group_name, grafana_name)


def delete_grafana(cmd, grafana_name, resource_group_name=None):
    client = cf_amg(cmd.cli_ctx)
    grafana = client.grafana.get(resource_group_name, grafana_name)

    # delete first
    poller = client.grafana.begin_delete(resource_group_name, grafana_name)
    LongRunningOperation(cmd.cli_ctx)(poller)

    # delete role assignment
    logger.warning("Grafana instance of '%s' was delete. Now removing role assignments for associated with its "
                   "managed identity", grafana_name)
    _delete_role_assignment(cmd.cli_ctx, grafana.identity.principal_id)


def show_dashboard(cmd, grafana_name, uid, resource_group_name=None):
    response = _send_request(cmd, resource_group_name, grafana_name, "get", "/api/dashboards/uid/" + uid)
    return json.loads(response.content)


def list_dashboards(cmd, grafana_name, resource_group_name=None):
    response = _send_request(cmd, resource_group_name, grafana_name, "get", "/api/search?type=dash-db")
    return json.loads(response.content)


def create_dashboard(cmd, grafana_name, definition, title=None, folder=None, resource_group_name=None, overwrite=None):
    data = _try_load_dashboard_definition(cmd, resource_group_name, grafana_name, definition, for_import=False)
    if "dashboard" in data:
        payload = data
    else:
        logger.info("Adjust input by adding 'dashboard' field")
        payload = {}
        payload["dashboard"] = data

    if title:
        payload['dashboard']['title'] = title

    if folder:
        folder = _find_folder(cmd, resource_group_name, grafana_name, folder)
        payload['folderId'] = folder["id"]

    payload["overwrite"] = overwrite or False

    if "id" in payload["dashboard"]:
        logger.warning("Removing 'id' from dashboard to prevent the error of 'Not Found'")
        del payload["dashboard"]["id"]

    response = _send_request(cmd, resource_group_name, grafana_name, "post", "/api/dashboards/db",
                             payload)
    return json.loads(response.content)


def update_dashboard(cmd, grafana_name, definition, folder=None, resource_group_name=None, overwrite=None):
    return create_dashboard(cmd, grafana_name, definition, folder=folder,
                            resource_group_name=resource_group_name,
                            overwrite=overwrite)


def import_dashboard(cmd, grafana_name, definition, folder=None, resource_group_name=None, overwrite=None):
    import copy
    data = _try_load_dashboard_definition(cmd, resource_group_name, grafana_name, definition, for_import=True)
    if "dashboard" in data:
        payload = data
    else:
        logger.info("Adjust input by adding 'dashboard' field")
        payload = {}
        payload["dashboard"] = data

    if folder:
        folder = _find_folder(cmd, resource_group_name, grafana_name, folder)
        payload['folderId'] = folder["id"]

    payload["overwrite"] = overwrite or False

    payload["inputs"] = []

    # provide parameter values for datasource
    data_sources = list_data_sources(cmd, grafana_name, resource_group_name)
    for parameter in payload["dashboard"].get('__inputs', []):
        if parameter.get("type") == "datasource":
            match = next((d for d in data_sources if d["type"] == parameter["pluginId"]), None)
            if match:
                clone = copy.deepcopy(parameter)
                clone["value"] = match["uid"]
                payload["inputs"].append(clone)
            else:
                logger.warning("No data source was found matching the required parameter of %s", parameter['pluginId'])

    response = _send_request(cmd, resource_group_name, grafana_name, "post", "/api/dashboards/import",
                             payload)
    return json.loads(response.content)


def _try_load_dashboard_definition(cmd, resource_group_name, grafana_name, definition, for_import):
    import re

    if for_import:
        try:  # see whether it is a gallery id
            int(definition)
            response = _send_request(cmd, resource_group_name, grafana_name, "get",
                                     "/api/gnet/dashboards/" + definition)
            return json.loads(response.content)["json"]
        except ValueError:
            pass

    if re.match(r"^[a-z]+://", definition.lower()):
        response = requests.get(definition, verify=(not should_disable_connection_verify()))
        if response.status_code == 200:
            definition = json.loads(response.content.decode())
        else:
            raise ArgumentUsageError(f"Failed to dashboard definition from '{definition}'. Error: '{response}'.")
    else:
        definition = json.loads(_try_load_file_content(definition))

    return definition


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
            response = _send_request(cmd, resource_group_name, grafana_name, "get", "/api/folders")
            if response.status_code >= 400:
                raise ArgumentUsageError(f"Could't find the folder '{folder}'. Ex: {response.status_code}")
            result = json.loads(response.content)
            result = [f for f in result if f["title"] == folder]
            if len(result) == 0:
                raise ArgumentUsageError(f"Could't find the folder '{folder}'. Ex: {response.status_code}")
            if len(result) > 1:
                raise ArgumentUsageError((f"More than one folder has the same title of '{folder}'. Please use other "
                                          f"unique identifiers"))
            return result[0]

    return json.loads(response.content)


def get_actual_user(cmd, grafana_name, resource_group_name=None):
    response = _send_request(cmd, resource_group_name, grafana_name, "get", "/api/user")
    return json.loads(response.content)


def list_users(cmd, grafana_name, resource_group_name=None):
    response = _send_request(cmd, resource_group_name, grafana_name, "get", "/api/org/users")
    return json.loads(response.content)


def show_user(cmd, grafana_name, user, resource_group_name=None):
    users = list_users(cmd, grafana_name, resource_group_name=resource_group_name)
    match = next((u for u in users if u['name'].lower() == user.lower()), None)

    if match:
        return match
    raise ArgumentUsageError(f"Could't find the user '{user}'")


def query_data_source(cmd, grafana_name, data_source, time_from=None, time_to=None,
                      max_data_points=100, internal_ms=1000, query_format=None,
                      conditions=None, resource_group_name=None):
    import datetime
    import time
    from dateutil import parser
    right_now = datetime.datetime.now()

    if time_from:
        time_from = parser.parse(time_from)
    else:
        time_from = right_now - datetime.timedelta(hours=1)
    time_from_epoch = str(time.mktime(time_from.timetuple()) * 1000)

    if time_to:
        time_to = parser.parse(time_to)
    else:
        time_to = right_now
    time_to_epoch = str(time.mktime(time_to.timetuple()) * 1000)

    data_source_id = _find_data_source(cmd, resource_group_name, grafana_name, data_source)["id"]

    data = {
        "from": time_from_epoch,
        "to": time_to_epoch,
        "queries": [{
            "intervalMs": internal_ms,
            "maxDataPoints": max_data_points,
            "datasourceId": data_source_id,
            "format": query_format or "time_series",
            "refId": "A"
        }]
    }

    if conditions:
        for c in conditions:
            k, v = c.split("=", 1)
            data["queries"][0][k] = v

    response = _send_request(cmd, resource_group_name, grafana_name, "post", "/api/ds/query", data)
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
        raise ArgumentUsageError(f"Couldn't found data source {data_source}. Ex: {response.status_code}")
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
    endpoint = grafana_endpoints.get(grafana_name)
    if not endpoint:
        grafana = show_grafana(cmd, grafana_name, resource_group_name)
        endpoint = grafana.properties.endpoint
        grafana_endpoints[grafana_name] = endpoint

    from azure.cli.core._profile import Profile
    profile = Profile(cli_ctx=cmd.cli_ctx)
    # this might be a cross tenant scenario, so pass subscription to get_raw_token
    subscription = get_subscription_id(cmd.cli_ctx)
    amg_first_party_app = ("7f525cdc-1f08-4afa-af7c-84709d42f5d3"
                           if "-ppe." in cmd.cli_ctx.cloud.endpoints.active_directory
                           else "ce34e7e5-485f-4d76-964f-b3d2b16d1e4f")
    creds, _, _ = profile.get_raw_token(subscription=subscription,
                                        resource=amg_first_party_app)

    headers = {
        "content-type": "application/json",
        "authorization": "Bearer " + creds[1]
    }

    # TODO: handle re-try on 429
    response = requests.request(http_method,
                                url=endpoint + path,
                                headers=headers,
                                json=body,
                                timeout=60,
                                verify=(not should_disable_connection_verify()))
    if response.status_code >= 400:
        if raise_for_error_status:
            logger.warning(str(response.content))
            response.raise_for_status()
    # TODO: log headers, requests and response
    return response
