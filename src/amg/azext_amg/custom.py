# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import requests

from msrestazure.tools import is_valid_resource_id, parse_resource_id
from msrestazure.azure_exceptions import CloudError

from knack.log import get_logger

from azure.cli.core.commands import LongRunningOperation
from azure.cli.core.commands.client_factory import get_mgmt_service_client, get_subscription_id
from azure.cli.core.profiles import ResourceType, get_sdk
from azure.cli.core.util import should_disable_connection_verify
from azure.cli.core.azclierror import ArgumentUsageError, CLIInternalError

from ._client_factory import cf_amg
from .utils import get_yes_or_no_option, MGMT_SERVICE_CLIENT_API_VERSION

logger = get_logger(__name__)


grafana_endpoints = {}


def create_grafana(cmd, resource_group_name, grafana_name, location=None,
                   deterministic_outbound_ip=None, skip_system_assigned_identity=False, skip_role_assignments=False,
                   tags=None, zone_redundancy=None, principal_ids=None, principal_types=None):
    from azure.cli.core.commands.arm import resolve_role_id

    if skip_role_assignments and principal_ids:
        raise ArgumentUsageError("--skip-role-assignments | --assignee-object-ids")

    client = cf_amg(cmd.cli_ctx, subscription=None)
    resource = {
        "sku": {
            "name": "Standard"
        },
        "location": location,
        "identity": None if skip_system_assigned_identity else {"type": "SystemAssigned"},
        "tags": tags
    }
    resource["properties"] = {
        "zoneRedundancy": zone_redundancy,
        "deterministicOutboundIP": deterministic_outbound_ip
    }

    poller = client.grafana.begin_create(resource_group_name, grafana_name, resource)
    LongRunningOperation(cmd.cli_ctx)(poller)

    if skip_role_assignments:
        return poller
    resource = LongRunningOperation(cmd.cli_ctx)(poller)

    logger.warning("Grafana instance of '%s' was created. Now creating default role assignments for its "
                   "managed identity, and current CLI account unless --principal-ids are provided", grafana_name)

    subscription_scope = '/subscriptions/' + client._config.subscription_id  # pylint: disable=protected-access

    if not principal_ids:
        user_principal_id, user_principal_type = _get_login_account_principal_id(cmd.cli_ctx)
        principal_ids = [user_principal_id]
        principal_types = [user_principal_type]
    grafana_admin_role_id = resolve_role_id(cmd.cli_ctx, "Grafana Admin", subscription_scope)

    for p, t in zip(principal_ids, principal_types):
        _create_role_assignment(cmd.cli_ctx, p, t, grafana_admin_role_id, resource.id)

    if resource.identity:
        monitoring_reader_role_id = resolve_role_id(cmd.cli_ctx, "Monitoring Reader", subscription_scope)
        _create_role_assignment(cmd.cli_ctx, resource.identity.principal_id, "ServicePrincipal",
                                monitoring_reader_role_id, subscription_scope)

    return resource


# for injecting test seams to produce predictable role assignment id for playback
def _gen_guid():
    import uuid
    return uuid.uuid4()


def _get_login_account_principal_id(cli_ctx):
    from azure.graphrbac.models import GraphErrorException
    from azure.cli.core._profile import Profile, _USER_ENTITY, _USER_TYPE, _SERVICE_PRINCIPAL, _USER_NAME
    from azure.graphrbac import GraphRbacManagementClient
    profile = Profile(cli_ctx=cli_ctx)
    cred, _, tenant_id = profile.get_login_credentials(
        resource=cli_ctx.cloud.endpoints.active_directory_graph_resource_id)
    client = GraphRbacManagementClient(cred, tenant_id,
                                       base_url=cli_ctx.cloud.endpoints.active_directory_graph_resource_id)
    active_account = profile.get_subscription()
    assignee = active_account[_USER_ENTITY][_USER_NAME]
    principal_type = "User"
    try:
        if active_account[_USER_ENTITY][_USER_TYPE] == _SERVICE_PRINCIPAL:
            result = list(client.service_principals.list(
                filter=f"servicePrincipalNames/any(c:c eq '{assignee}')"))
            principal_type = "ServicePrincipal"
        else:
            result = [client.signed_in_user.get()]
    except GraphErrorException as ex:
        logger.warning("Graph query error %s", ex)
    if not result:
        raise CLIInternalError((f"Failed to retrieve principal id for '{assignee}', which is needed to create a "
                                f"role assignment. Consider using '--principal-ids' to bypass the lookup"))

    return result[0].object_id, principal_type


def _create_role_assignment(cli_ctx, principal_id, principal_type, role_definition_id, scope):
    import time
    from azure.core.exceptions import ResourceExistsError
    assignments_client = get_mgmt_service_client(cli_ctx, ResourceType.MGMT_AUTHORIZATION,
                                                 api_version=MGMT_SERVICE_CLIENT_API_VERSION).role_assignments
    RoleAssignmentCreateParameters = get_sdk(cli_ctx, ResourceType.MGMT_AUTHORIZATION,
                                             'RoleAssignmentCreateParameters', mod='models',
                                             operation_group='role_assignments')
    parameters = RoleAssignmentCreateParameters(role_definition_id=role_definition_id,
                                                principal_id=principal_id, principal_type=principal_type)

    logger.info("Creating an assignment with a role '%s' on the scope of '%s'", role_definition_id, scope)
    retry_times = 36
    assignment_name = _gen_guid()
    for retry_time in range(0, retry_times):
        try:
            assignments_client.create(scope=scope, role_assignment_name=assignment_name,
                                      parameters=parameters)
            break
        except ResourceExistsError:  # Exception from Track-2 SDK
            logger.info('Role assignment already exists')
            break
        except CloudError as ex:
            if 'role assignment already exists' in ex.message:  # Exception from Track-1 SDK
                logger.info('Role assignment already exists')
                break
            if retry_time < retry_times and ' does not exist in the directory ' in (ex.message or "").lower():
                time.sleep(5)
                logger.warning('Retrying role assignment creation: %s/%s', retry_time + 1,
                               retry_times)
                continue
            raise


def _delete_role_assignment(cli_ctx, principal_id):
    assignments_client = get_mgmt_service_client(cli_ctx, ResourceType.MGMT_AUTHORIZATION,
                                                 api_version=MGMT_SERVICE_CLIENT_API_VERSION).role_assignments
    f = f"principalId eq '{principal_id}'"
    assignments = list(assignments_client.list_for_subscription(filter=f))
    for a in assignments or []:
        assignments_client.delete_by_id(a.id)


def list_grafana(cmd, resource_group_name=None):
    client = cf_amg(cmd.cli_ctx, subscription=None)
    if resource_group_name:
        return client.grafana.list_by_resource_group(resource_group_name)
    return client.grafana.list()


def update_grafana(cmd, grafana_name, api_key_and_service_account=None, deterministic_outbound_ip=None,
                   public_network_access=None, smtp=None, host=None, user=None, password=None,
                   start_tls_policy=None, skip_verify=None, from_address=None, from_name=None,
                   major_version=None, resource_group_name=None, tags=None):

    if all(param is None for param in (api_key_and_service_account, deterministic_outbound_ip, public_network_access,
                                       smtp, host, user, password, start_tls_policy, skip_verify, from_address,
                                       from_name, major_version, tags)):
        raise ArgumentUsageError("Please supply at least one parameter value to update the Grafana workspace")

    client = cf_amg(cmd.cli_ctx, subscription=None)
    instance = client.grafana.get(resource_group_name, grafana_name)

    resource = {}
    resourceProperties = {}

    if api_key_and_service_account:
        resourceProperties["apiKey"] = api_key_and_service_account

    if deterministic_outbound_ip:
        resourceProperties["deterministicOutboundIP"] = deterministic_outbound_ip

    if public_network_access:
        resourceProperties["publicNetworkAccess"] = public_network_access

    if major_version:
        if major_version == "10":
            # prompt for confirmation, cancel operation if not confirmed
            if (not get_yes_or_no_option("You are trying to upgrade this workspace to Grafana version 10. By "
                                         "proceeding, you acknowledge that upgrading to Grafana version 10 is a "
                                         "permanent and irreversible operation and Grafana legacy alerting has been "
                                         "deprecated and any migrated legacy alert may require manual adjustments "
                                         "to function properly under the new alerting system. Do you wish to proceed? "
                                         "(Y/N): ")):
                return None
        resourceProperties["grafanaMajorVersion"] = major_version

    if tags:
        resource["tags"] = tags

    if not all(param is None for param in (smtp, host, user, password, start_tls_policy, from_address, from_name,
                                           skip_verify)):
        from azext_amg.vendored_sdks.models import GrafanaConfigurations, Smtp
        resourceProperties["grafanaConfigurations"] = GrafanaConfigurations()

        if not instance.properties.grafana_configurations.smtp:
            resourceProperties["grafanaConfigurations"].smtp = Smtp()
        else:
            resourceProperties["grafanaConfigurations"] = instance.properties.grafana_configurations

        if smtp:
            resourceProperties["grafanaConfigurations"].smtp.enabled = smtp == "Enabled"
        if host:
            resourceProperties["grafanaConfigurations"].smtp.host = host
        if user:
            resourceProperties["grafanaConfigurations"].smtp.user = user
        if password:
            resourceProperties["grafanaConfigurations"].smtp.password = password
        if start_tls_policy:
            resourceProperties["grafanaConfigurations"].smtp.start_tls_policy = start_tls_policy
        if skip_verify is not None:
            resourceProperties["grafanaConfigurations"].smtp.skip_verify = skip_verify
        if from_address:
            resourceProperties["grafanaConfigurations"].smtp.from_address = from_address
        if from_name:
            resourceProperties["grafanaConfigurations"].smtp.from_name = from_name

    if resourceProperties:
        resource["properties"] = resourceProperties

    # "update" uses PATCH
    return client.grafana.update(resource_group_name, grafana_name, resource)


def show_grafana(cmd, grafana_name, resource_group_name=None, subscription=None):
    client = cf_amg(cmd.cli_ctx, subscription=subscription)
    return client.grafana.get(resource_group_name, grafana_name)


def delete_grafana(cmd, grafana_name, resource_group_name=None):
    client = cf_amg(cmd.cli_ctx, subscription=None)
    grafana = client.grafana.get(resource_group_name, grafana_name)

    # delete first
    poller = client.grafana.begin_delete(resource_group_name, grafana_name)
    LongRunningOperation(cmd.cli_ctx)(poller)

    # delete role assignment
    logger.warning("Grafana instance of '%s' was deleted. Now removing role assignments for associated with its "
                   "managed identity", grafana_name)
    _delete_role_assignment(cmd.cli_ctx, grafana.identity.principal_id)


def backup_grafana(cmd, grafana_name, components=None, directory=None, folders_to_include=None,
                   folders_to_exclude=None, resource_group_name=None):
    import os
    from pathlib import Path
    from .backup import backup
    _health_endpoint_reachable(cmd, grafana_name, resource_group_name=resource_group_name)

    creds = _get_data_plane_creds(cmd, api_key_or_token=None, subscription=None)
    headers = {
        "content-type": "application/json",
        "authorization": "Bearer " + creds[1]
    }

    backup(grafana_name=grafana_name,
           grafana_url=_get_grafana_endpoint(cmd, resource_group_name, grafana_name, subscription=None),
           backup_dir=directory or os.path.join(Path.cwd(), "_backup"),
           components=components,
           http_headers=headers,
           folders_to_include=folders_to_include,
           folders_to_exclude=folders_to_exclude)


def restore_grafana(cmd, grafana_name, archive_file, components=None, remap_data_sources=None,
                    resource_group_name=None):
    _health_endpoint_reachable(cmd, grafana_name, resource_group_name=resource_group_name)
    creds = _get_data_plane_creds(cmd, api_key_or_token=None, subscription=None)
    headers = {
        "content-type": "application/json",
        "authorization": "Bearer " + creds[1]
    }
    from .restore import restore

    data_sources = []
    if remap_data_sources:
        data_sources = list_data_sources(cmd, grafana_name, resource_group_name,
                                         subscription=None)

    restore(grafana_url=_get_grafana_endpoint(cmd, resource_group_name, grafana_name, subscription=None),
            archive_file=archive_file,
            components=components,
            http_headers=headers,
            destination_datasources=data_sources)


def sync_dashboard(cmd, source, destination, folders_to_include=None, folders_to_exclude=None,
                   dashboards_to_include=None, dashboards_to_exclude=None, dry_run=None):
    # pylint: disable=too-many-locals, too-many-branches, too-many-statements
    if not is_valid_resource_id(source):
        raise ArgumentUsageError(f"'{source}' isn't a valid resource id, please refer to example commands in help")
    if not is_valid_resource_id(destination):
        raise ArgumentUsageError(f"'{destination}' isn't a valid resource id, please refer to example commands in help")

    if source.lower() == destination.lower():
        raise ArgumentUsageError("Destination workspace should be different from the source workspace")

    parsed_source = parse_resource_id(source)
    parsed_destination = parse_resource_id(destination)

    source_workspace, source_resource_group, source_subscription = (parsed_source["name"],
                                                                    parsed_source["resource_group"],
                                                                    parsed_source["subscription"])
    destination_workspace, destination_resource_group, destination_subscription = (parsed_destination["name"],
                                                                                   parsed_destination["resource_group"],
                                                                                   parsed_destination["subscription"])

    _health_endpoint_reachable(cmd, source_workspace, resource_group_name=source_resource_group,
                               subscription=source_subscription)
    _health_endpoint_reachable(cmd, destination_workspace, resource_group_name=destination_resource_group,
                               subscription=destination_subscription)

    # TODO: skip READ-ONLY destination dashboard (rare case)
    destination_folders = list_folders(cmd, destination_workspace, resource_group_name=destination_resource_group,
                                       subscription=destination_subscription)
    destination_folders = {f["title"].lower(): f["id"] for f in destination_folders}

    destination_data_sources = list_data_sources(cmd, destination_workspace, destination_resource_group,
                                                 subscription=destination_subscription)
    source_data_sources = list_data_sources(cmd, source_workspace, source_resource_group,
                                            subscription=source_subscription)

    from .utils import create_datasource_mapping, remap_datasource_uids
    uid_mapping = create_datasource_mapping(source_data_sources, destination_data_sources)

    source_dashboards = list_dashboards(cmd, source_workspace, resource_group_name=source_resource_group,
                                        subscription=source_subscription)

    summary = {
        "folders_created": [],
        "dashboards_synced": [],
        "dashboards_skipped": [],
    }
    data_source_missed = set()
    for dashboard in source_dashboards:
        uid = dashboard["uid"]
        source_dashboard = show_dashboard(cmd, source_workspace, uid, resource_group_name=source_resource_group,
                                          subscription=source_subscription)
        folder_title = source_dashboard["meta"]["folderTitle"]
        dashboard_title = source_dashboard["dashboard"]["title"]
        dashboard_path = folder_title + "/" + dashboard_title

        should_skip = False
        if source_dashboard["meta"].get("provisioned"):
            should_skip = True
        else:
            if folders_to_include:
                should_skip = not next((f for f in folders_to_include if folder_title.lower() == f.lower()), None)
            if not should_skip and folders_to_exclude:
                should_skip = next((f for f in folders_to_exclude if folder_title.lower() == f.lower()), None)
            if dashboards_to_include:
                should_skip = not next((p for p in dashboards_to_include if p.lower() == dashboard_title.lower()), None)
            if dashboards_to_exclude:
                should_skip = next((p for p in dashboards_to_exclude if p.lower() == dashboard_title.lower()), None)
        if should_skip:
            summary["dashboards_skipped"].append(dashboard_path)
            continue

        # Figure out whether we shall correct the data sources. It is possible the Uids are different
        remap_datasource_uids(source_dashboard.get("dashboard"), uid_mapping, data_source_missed)
        if not dry_run:
            delete_dashboard(cmd, destination_workspace, uid, resource_group_name=destination_resource_group,
                             ignore_error=True, subscription=destination_subscription)

        # ensure the folder exists at destination side
        if folder_title.lower() == "general":
            folder_id = None
        else:
            folder_id = destination_folders.get(folder_title.lower())
            if not folder_id:
                summary["folders_created"].append(folder_title)
                if not dry_run:
                    logger.warning("Creating folder: %s", folder_title)
                    new_folder = create_folder(cmd, destination_workspace, title=folder_title,
                                               resource_group_name=destination_resource_group,
                                               subscription=destination_subscription)
                    folder_id = new_folder["id"]
                destination_folders[folder_title.lower()] = folder_id or "dry run dummy"

        summary["dashboards_synced"].append(dashboard_path)
        if not dry_run:
            logger.warning("Syncing dashboard: %s", dashboard_path)
            _create_dashboard(cmd, destination_workspace, definition=source_dashboard, overwrite=True,
                              folder_id=folder_id, resource_group_name=destination_resource_group,
                              for_sync=True)
    if data_source_missed:
        logger.warning(("A few data sources used by dashboards are unavailable at destination: \"%s\""
                        ". Please configure them."), ", ".join(data_source_missed))
    return summary


def show_dashboard(cmd, grafana_name, uid, resource_group_name=None, api_key_or_token=None, subscription=None):
    response = _send_request(cmd, resource_group_name, grafana_name, "get", "/api/dashboards/uid/" + uid,
                             api_key_or_token=api_key_or_token, subscription=subscription)
    return json.loads(response.content)


def list_dashboards(cmd, grafana_name, resource_group_name=None, api_key_or_token=None, subscription=None):
    limit = 5000
    current_page = 1
    dashboards = []
    while True:
        response = _send_request(cmd, resource_group_name, grafana_name, "get",
                                 f"/api/search?type=dash-db&limit={limit}&page={current_page}",
                                 api_key_or_token=api_key_or_token, subscription=subscription)
        temp = json.loads(response.content)
        dashboards += temp
        if len(temp) == 0:
            break
        current_page += 1
    return dashboards


def create_dashboard(cmd, grafana_name, definition, title=None, folder=None, resource_group_name=None,
                     overwrite=None, api_key_or_token=None):
    folder_id = None
    if folder:
        folder_id = _find_folder(cmd, resource_group_name, grafana_name, folder)["id"]
    return _create_dashboard(cmd, grafana_name, definition=definition, title=title, folder_id=folder_id,
                             resource_group_name=resource_group_name, overwrite=overwrite,
                             api_key_or_token=api_key_or_token)


def _create_dashboard(cmd, grafana_name, definition, title=None, folder_id=None, resource_group_name=None,
                      overwrite=None, api_key_or_token=None, for_sync=True, subscription=None):
    if "dashboard" in definition:
        payload = definition
    else:
        logger.info("Adjust input by adding 'dashboard' field")
        payload = {}
        payload['dashboard'] = definition

    if title:
        payload['dashboard']['title'] = title

    if folder_id:
        payload['folderId'] = folder_id

    payload['overwrite'] = overwrite or False

    if "id" in payload['dashboard']:
        if not for_sync:
            logger.warning("Removing 'id' from dashboard to prevent the error of 'Not Found'")
        del payload['dashboard']['id']

    response = _send_request(cmd, resource_group_name, grafana_name, "post", "/api/dashboards/db",
                             payload, api_key_or_token=api_key_or_token, subscription=subscription)
    return json.loads(response.content)


def update_dashboard(cmd, grafana_name, definition, folder=None, resource_group_name=None, overwrite=None,
                     api_key_or_token=None):
    return create_dashboard(cmd, grafana_name, definition, folder=folder,
                            resource_group_name=resource_group_name,
                            overwrite=overwrite, api_key_or_token=api_key_or_token)


def import_dashboard(cmd, grafana_name, definition, folder=None, resource_group_name=None, overwrite=None,
                     api_key_or_token=None):
    import copy
    data = _try_load_dashboard_definition(cmd, resource_group_name, grafana_name, definition,
                                          api_key_or_token=api_key_or_token)
    if "dashboard" in data:
        payload = data
    else:
        logger.info("Adjust input by adding 'dashboard' field")
        payload = {}
        payload['dashboard'] = data

    if folder:
        folder = _find_folder(cmd, resource_group_name, grafana_name, folder)
        payload['folderId'] = folder['id']

    payload['overwrite'] = overwrite or False
    payload['inputs'] = []

    # provide parameter values for datasource
    data_sources = list_data_sources(cmd, grafana_name, resource_group_name)
    for parameter in payload['dashboard'].get('__inputs', []):
        if parameter.get("type") == "datasource":
            match = next((d for d in data_sources if d['type'] == parameter['pluginId']), None)
            if match:
                clone = copy.deepcopy(parameter)
                clone['value'] = match['uid']
                payload['inputs'].append(clone)
            else:
                logger.warning("No data source was found matching the required parameter of %s", parameter['pluginId'])

    response = _send_request(cmd, resource_group_name, grafana_name, "post", "/api/dashboards/import",
                             payload, api_key_or_token=api_key_or_token)
    return json.loads(response.content)


def _health_endpoint_reachable(cmd, grafana_name, resource_group_name=None, api_key_or_token=None, subscription=None):
    response = _send_request(cmd, resource_group_name, grafana_name, "get", "/api/health",
                             api_key_or_token=api_key_or_token,
                             raise_for_error_status=False, subscription=subscription)
    if response.status_code == 401:
        raise ArgumentUsageError(f"Access to \"{grafana_name}\" was denied")
    response.raise_for_status()


def _try_load_dashboard_definition(cmd, resource_group_name, grafana_name, definition, api_key_or_token=None):
    import re

    try:
        int(definition)
        # try load from Grafana gallery
        response = _send_request(cmd, resource_group_name, grafana_name, "get",
                                 "/api/gnet/dashboards/" + str(definition), api_key_or_token=api_key_or_token)
        definition = json.loads(response.content)["json"]
        return definition
    except ValueError:
        pass

    if re.match(r"^[a-z]+://", definition.lower()):
        response = requests.get(definition, verify=not should_disable_connection_verify())
        if response.status_code == 200:
            definition = json.loads(response.content.decode())
        else:
            raise ArgumentUsageError(f"Failed to dashboard definition from '{definition}'. Error: '{response}'.")
    else:
        definition = json.loads(_try_load_file_content(definition))

    return definition


def delete_dashboard(cmd, grafana_name, uid, resource_group_name=None, api_key_or_token=None,
                     ignore_error=False, subscription=None):
    _send_request(cmd, resource_group_name, grafana_name, "delete", "/api/dashboards/uid/" + uid,
                  api_key_or_token=api_key_or_token, raise_for_error_status=(not ignore_error),
                  subscription=subscription)


def create_data_source(cmd, grafana_name, definition, resource_group_name=None, api_key_or_token=None):
    response = _send_request(cmd, resource_group_name, grafana_name, "post", "/api/datasources", definition,
                             api_key_or_token=api_key_or_token)
    return json.loads(response.content)


def show_data_source(cmd, grafana_name, data_source, resource_group_name=None, api_key_or_token=None):
    return _find_data_source(cmd, resource_group_name, grafana_name, data_source, api_key_or_token=api_key_or_token)


def delete_data_source(cmd, grafana_name, data_source, resource_group_name=None, api_key_or_token=None):
    data = _find_data_source(cmd, resource_group_name, grafana_name, data_source)
    _send_request(cmd, resource_group_name, grafana_name, "delete", "/api/datasources/uid/" + data["uid"],
                  api_key_or_token=api_key_or_token)


def list_data_sources(cmd, grafana_name, resource_group_name=None, api_key_or_token=None, subscription=None):
    response = _send_request(cmd, resource_group_name, grafana_name, "get", "/api/datasources",
                             api_key_or_token=api_key_or_token, subscription=subscription)
    return json.loads(response.content)


def update_data_source(cmd, grafana_name, data_source, definition, resource_group_name=None, api_key_or_token=None):
    data = _find_data_source(cmd, resource_group_name, grafana_name, data_source, api_key_or_token=api_key_or_token)
    response = _send_request(cmd, resource_group_name, grafana_name, "put", "/api/datasources/" + str(data['id']),
                             definition, api_key_or_token=api_key_or_token)
    return json.loads(response.content)


def list_notification_channels(cmd, grafana_name, resource_group_name=None, short=False, api_key_or_token=None):
    if short is False:
        response = _send_request(cmd, resource_group_name, grafana_name, "get", "/api/alert-notifications",
                                 api_key_or_token=api_key_or_token)
    elif short is True:
        response = _send_request(cmd, resource_group_name, grafana_name, "get", "/api/alert-notifications/lookup",
                                 api_key_or_token=api_key_or_token)
    return json.loads(response.content)


def show_notification_channel(cmd, grafana_name, notification_channel, resource_group_name=None, api_key_or_token=None):
    return _find_notification_channel(cmd, resource_group_name, grafana_name, notification_channel,
                                      api_key_or_token=api_key_or_token)


def create_notification_channel(cmd, grafana_name, definition, resource_group_name=None, api_key_or_token=None):
    response = _send_request(cmd, resource_group_name, grafana_name, "post", "/api/alert-notifications", definition,
                             api_key_or_token=api_key_or_token)
    return json.loads(response.content)


def update_notification_channel(cmd, grafana_name, notification_channel, definition, resource_group_name=None,
                                api_key_or_token=None):
    data = _find_notification_channel(cmd, resource_group_name, grafana_name, notification_channel,
                                      api_key_or_token=api_key_or_token)
    definition['id'] = data['id']
    response = _send_request(cmd, resource_group_name, grafana_name, "put",
                             "/api/alert-notifications/" + str(data['id']),
                             definition, api_key_or_token=api_key_or_token)
    return json.loads(response.content)


def delete_notification_channel(cmd, grafana_name, notification_channel, resource_group_name=None,
                                api_key_or_token=None):
    data = _find_notification_channel(cmd, resource_group_name, grafana_name, notification_channel,
                                      api_key_or_token=api_key_or_token)
    _send_request(cmd, resource_group_name, grafana_name, "delete", "/api/alert-notifications/" + str(data["id"]),
                  api_key_or_token=api_key_or_token)


def test_notification_channel(cmd, grafana_name, notification_channel, resource_group_name=None, api_key_or_token=None):
    data = _find_notification_channel(cmd, resource_group_name, grafana_name, notification_channel,
                                      api_key_or_token=api_key_or_token)
    response = _send_request(cmd, resource_group_name, grafana_name, "post", "/api/alert-notifications/test",
                             data, api_key_or_token=api_key_or_token)
    return response


def create_folder(cmd, grafana_name, title, resource_group_name=None, api_key_or_token=None, subscription=None):
    payload = {
        "title": title
    }
    response = _send_request(cmd, resource_group_name, grafana_name, "post", "/api/folders", payload,
                             api_key_or_token=api_key_or_token, subscription=subscription)
    return json.loads(response.content)


def list_folders(cmd, grafana_name, resource_group_name=None, api_key_or_token=None, subscription=None):
    response = _send_request(cmd, resource_group_name, grafana_name, "get", "/api/folders",
                             api_key_or_token=api_key_or_token, subscription=subscription)
    return json.loads(response.content)


def update_folder(cmd, grafana_name, folder, title, resource_group_name=None, api_key_or_token=None):
    f = show_folder(cmd, grafana_name, folder, resource_group_name, api_key_or_token=api_key_or_token)
    version = f['version']
    data = {
        "title": title,
        "version": int(version)
    }
    response = _send_request(cmd, resource_group_name, grafana_name, "put", "/api/folders/" + f["uid"], data,
                             api_key_or_token=api_key_or_token)
    return json.loads(response.content)


def show_folder(cmd, grafana_name, folder, resource_group_name=None, api_key_or_token=None):
    return _find_folder(cmd, resource_group_name, grafana_name, folder, api_key_or_token=api_key_or_token)


def delete_folder(cmd, grafana_name, folder, resource_group_name=None, api_key_or_token=None):
    data = _find_folder(cmd, resource_group_name, grafana_name, folder)
    _send_request(cmd, resource_group_name, grafana_name, "delete", "/api/folders/" + data['uid'],
                  api_key_or_token=api_key_or_token)


def _find_folder(cmd, resource_group_name, grafana_name, folder, api_key_or_token=None):
    response = _send_request(cmd, resource_group_name, grafana_name, "get", "/api/folders/id/" + folder,
                             raise_for_error_status=False, api_key_or_token=api_key_or_token)
    if response.status_code >= 400 or not json.loads(response.content)['uid']:
        response = _send_request(cmd, resource_group_name, grafana_name, "get", "/api/folders/" + folder,
                                 raise_for_error_status=False, api_key_or_token=api_key_or_token)
        if response.status_code >= 400:
            response = _send_request(cmd, resource_group_name, grafana_name, "get", "/api/folders",
                                     api_key_or_token=api_key_or_token)
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


def list_api_keys(cmd, grafana_name, resource_group_name=None):
    response = _send_request(cmd, resource_group_name, grafana_name, "get",
                             "/api/auth/keys?includedExpired=false&accesscontrol=true")
    return json.loads(response.content)


def delete_api_key(cmd, grafana_name, key, resource_group_name=None):
    # Find the key id based on name
    try:
        int(key)
    except ValueError:
        # looks like a key name is provided, need to convert to id to delete
        keys = list_api_keys(cmd, grafana_name, resource_group_name=resource_group_name)
        temp = next((k for k in keys if k['name'].lower() == key.lower()), None)
        if temp:
            key = str(temp['id'])
    _send_request(cmd, resource_group_name, grafana_name, "delete", "/api/auth/keys/" + key)


def create_api_key(cmd, grafana_name, key, role=None, time_to_live=None, resource_group_name=None):
    seconds = _convert_duration_to_seconds(time_to_live)

    data = {
        "name": key,
        "role": role,
        "secondsToLive": seconds
    }
    response = _send_request(cmd, resource_group_name, grafana_name, "post", "/api/auth/keys", data)
    content = json.loads(response.content)
    logger.warning("You will only be able to view this key here once. Please save it in a secure place.")
    return content


def _convert_duration_to_seconds(time_to_live):
    unit_to_seconds = {
        "s": 1,
        "m": 60,
        "h": 3600,
        "d": 3600 * 24,
        "w": 3600 * 24 * 7,
        "M": 3600 * 24 * 30,
        "y": 3600 * 24 * 30 * 365
    }
    unit_name = time_to_live[len(time_to_live) - 1:]
    try:
        if unit_name in unit_to_seconds:
            seconds = int(time_to_live[: len(time_to_live) - 1]) * unit_to_seconds[unit_name]
        else:
            seconds = int(time_to_live)
    except ValueError:
        raise ArgumentUsageError("Please provide valid time duration") from None

    return seconds


def create_service_account(cmd, grafana_name, service_account, role=None, is_disabled=None, resource_group_name=None):
    data = {
        "name": service_account,
        "role": role
    }
    if is_disabled is not None:
        data["isDisabled"] = is_disabled
    response = _send_request(cmd, resource_group_name, grafana_name, "post", "/api/serviceaccounts", data)
    return json.loads(response.content)


def update_service_account(cmd, grafana_name, service_account, new_name=None,
                           role=None, is_disabled=None, resource_group_name=None):
    data = {}
    service_account_id = _get_service_account_id(cmd, resource_group_name, grafana_name, service_account)
    if new_name:
        data['name'] = new_name

    if role:
        data['role'] = role

    if is_disabled is not None:
        data["isDisabled"] = is_disabled

    response = _send_request(cmd, resource_group_name, grafana_name, "patch",
                             "/api/serviceaccounts/" + service_account_id, data)
    return json.loads(response.content)['serviceaccount']


def list_service_accounts(cmd, grafana_name, resource_group_name=None):
    response = _send_request(cmd, resource_group_name, grafana_name, "get", "/api/serviceaccounts/search")
    return json.loads(response.content)['serviceAccounts']


def show_service_account(cmd, grafana_name, service_account, resource_group_name=None):
    service_account_id = _get_service_account_id(cmd, resource_group_name, grafana_name, service_account)
    response = _send_request(cmd, resource_group_name, grafana_name, "get",
                             "/api/serviceaccounts/" + service_account_id)
    return json.loads(response.content)


def delete_service_account(cmd, grafana_name, service_account, resource_group_name=None):
    service_account_id = _get_service_account_id(cmd, resource_group_name, grafana_name, service_account)
    response = _send_request(cmd, resource_group_name, grafana_name, "delete",
                             "/api/serviceaccounts/" + service_account_id)
    return json.loads(response.content)


def _get_service_account_id(cmd, resource_group_name, grafana_name, service_account):
    try:
        int(service_account)
        return service_account
    except ValueError:
        accounts = list_service_accounts(cmd, grafana_name, resource_group_name)
        match = next((a for a in accounts if a['name'].lower() == service_account.lower()), None)
        # pylint: disable=raise-missing-from
        if not match:
            raise ArgumentUsageError(f"Could't find the service account '{service_account}'")
        return str(match['id'])


def create_service_account_token(cmd, grafana_name, service_account, token, time_to_live=None,
                                 resource_group_name=None):
    service_account_id = _get_service_account_id(cmd, resource_group_name, grafana_name, service_account)

    data = {
        "name": token,
    }

    if time_to_live:
        data['secondsToLive'] = _convert_duration_to_seconds(time_to_live)

    response = _send_request(cmd, resource_group_name, grafana_name, "post",
                             "/api/serviceaccounts/" + service_account_id + '/tokens', data)
    content = json.loads(response.content)
    logger.warning("You will only be able to view this token here once. Please save it in a secure place.")
    return content


def list_service_account_tokens(cmd, grafana_name, service_account, resource_group_name=None):
    service_account_id = _get_service_account_id(cmd, resource_group_name, grafana_name, service_account)
    response = _send_request(cmd, resource_group_name, grafana_name, "get",
                             "/api/serviceaccounts/" + service_account_id + '/tokens')
    return json.loads(response.content)


def delete_service_account_token(cmd, grafana_name, service_account, token, resource_group_name=None):
    service_account_id = _get_service_account_id(cmd, resource_group_name, grafana_name, service_account)
    token_id = _get_service_account_token_id(cmd, resource_group_name, grafana_name, service_account, token)

    response = _send_request(cmd, resource_group_name, grafana_name, "delete",
                             "/api/serviceaccounts/" + service_account_id + '/tokens' + '/' + token_id)
    return json.loads(response.content)


def _get_service_account_token_id(cmd, resource_group_name, grafana_name, service_account, token):
    try:
        int(token)
        return token
    except ValueError:
        accounts = list_service_account_tokens(cmd, grafana_name, service_account, resource_group_name)
        match = next((a for a in accounts if a['name'].lower() == token.lower()), None)
        # pylint: disable=raise-missing-from
        if not match:
            raise ArgumentUsageError(f"Could't find the service account token '{token}'")
        return str(match['id'])


def get_actual_user(cmd, grafana_name, resource_group_name=None, api_key_or_token=None):
    response = _send_request(cmd, resource_group_name, grafana_name, "get", "/api/user",
                             api_key_or_token=api_key_or_token)
    result = json.loads(response.content)
    result.pop('isGrafanaAdmin', None)
    return result


def list_users(cmd, grafana_name, resource_group_name=None, api_key_or_token=None):
    response = _send_request(cmd, resource_group_name, grafana_name, "get", "/api/org/users",
                             api_key_or_token=api_key_or_token)
    return json.loads(response.content)


def show_user(cmd, grafana_name, user, resource_group_name=None, api_key_or_token=None):
    users = list_users(cmd, grafana_name, resource_group_name=resource_group_name, api_key_or_token=api_key_or_token)
    match = next((u for u in users if u['name'].lower() == user.lower()), None)

    if match:
        return match
    raise ArgumentUsageError(f"Could't find the user '{user}'")


def query_data_source(cmd, grafana_name, data_source, time_from=None, time_to=None,
                      max_data_points=100, internal_ms=1000, query_format=None,
                      conditions=None, resource_group_name=None, api_key_or_token=None):
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

    data_source_id = _find_data_source(cmd, resource_group_name, grafana_name, data_source,
                                       api_key_or_token=api_key_or_token)["id"]

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

    response = _send_request(cmd, resource_group_name, grafana_name, "post", "/api/ds/query", data,
                             api_key_or_token=api_key_or_token)
    return json.loads(response.content)


def _find_data_source(cmd, resource_group_name, grafana_name, data_source, api_key_or_token=None):
    response = _send_request(cmd, resource_group_name, grafana_name, "get", "/api/datasources/name/" + data_source,
                             raise_for_error_status=False, api_key_or_token=api_key_or_token)
    if response.status_code >= 400:
        response = _send_request(cmd, resource_group_name, grafana_name, "get", "/api/datasources/" + data_source,
                                 raise_for_error_status=False, api_key_or_token=api_key_or_token)
        if response.status_code >= 400:
            response = _send_request(cmd, resource_group_name, grafana_name,
                                     "get", "/api/datasources/uid/" + data_source,
                                     raise_for_error_status=False, api_key_or_token=api_key_or_token)
    if response.status_code >= 400:
        raise ArgumentUsageError(f"Couldn't found data source {data_source}. Ex: {response.status_code}")
    return json.loads(response.content)


def _find_notification_channel(cmd, resource_group_name, grafana_name, notification_channel, api_key_or_token=None):
    response = _send_request(cmd, resource_group_name, grafana_name, "get",
                             "/api/alert-notifications/" + notification_channel,
                             raise_for_error_status=False, api_key_or_token=api_key_or_token)
    if response.status_code >= 400:
        response = _send_request(cmd, resource_group_name, grafana_name,
                                 "get", "/api/alert-notifications/uid/" + notification_channel,
                                 raise_for_error_status=False, api_key_or_token=api_key_or_token)
    if response.status_code >= 400:
        raise ArgumentUsageError(
            f"Couldn't found notification channel {notification_channel}. Ex: {response.status_code}")
    return json.loads(response.content)


# For UX: we accept a file path for complex payload such as dashboard/data-source definition
def _try_load_file_content(file_content):
    import os
    potentail_file_path = os.path.expanduser(file_content)
    if os.path.exists(potentail_file_path):
        from azure.cli.core.util import read_file_content
        file_content = read_file_content(potentail_file_path)
    return file_content


def _get_data_plane_creds(cmd, api_key_or_token, subscription):
    from azure.cli.core._profile import Profile
    profile = Profile(cli_ctx=cmd.cli_ctx)
    # this might be a cross tenant scenario, so pass subscription to get_raw_token
    subscription = subscription or get_subscription_id(cmd.cli_ctx)
    amg_first_party_app = ("7f525cdc-1f08-4afa-af7c-84709d42f5d3"
                           if "-ppe." in cmd.cli_ctx.cloud.endpoints.active_directory
                           else "ce34e7e5-485f-4d76-964f-b3d2b16d1e4f")
    if api_key_or_token:
        creds = [None, api_key_or_token]
    else:
        creds, _, _ = profile.get_raw_token(subscription=subscription,
                                            resource=amg_first_party_app)
    return creds


def _get_grafana_endpoint(cmd, resource_group_name, grafana_name, subscription):
    endpoint = grafana_endpoints.get(grafana_name)
    if not endpoint:
        grafana = show_grafana(cmd, grafana_name, resource_group_name, subscription=subscription)
        endpoint = grafana.properties.endpoint
        grafana_endpoints[grafana_name] = endpoint
    return endpoint


def _send_request(cmd, resource_group_name, grafana_name, http_method, path, body=None, raise_for_error_status=True,
                  api_key_or_token=None, subscription=None):
    endpoint = _get_grafana_endpoint(cmd, resource_group_name, grafana_name, subscription)

    creds = _get_data_plane_creds(cmd, api_key_or_token, subscription)

    headers = {
        "content-type": "application/json",
        "authorization": "Bearer " + creds[1]
    }

    # TODO: handle re-try on 429
    response = requests.request(http_method, url=endpoint + path, headers=headers, json=body, timeout=60,
                                verify=not should_disable_connection_verify())
    if response.status_code >= 400:
        if raise_for_error_status:
            logger.warning(str(response.content))
            response.raise_for_status()
    # TODO: log headers, requests and response
    return response
