# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import requests

from knack.log import get_logger

from azure.cli.core.commands.client_factory import get_mgmt_service_client, get_subscription_id
from azure.cli.core.util import should_disable_connection_verify
from azure.cli.core.azclierror import ArgumentUsageError, CLIInternalError, InvalidArgumentValueError, ManualInterrupt
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.mgmt.authorization.models import RoleAssignmentCreateParameters, PrincipalType

from azure.cli.core.aaz import AAZBoolArg, AAZListArg, AAZStrArg
from .aaz.latest.grafana._create import Create as _GrafanaCreate
from .aaz.latest.grafana._delete import Delete as _GrafanaDelete
from .aaz.latest.grafana._update import Update as _GrafanaUpdate

from ._client_factory import cf_amg
from .utils import get_yes_or_no_option, search_folders

logger = get_logger(__name__)


grafana_endpoints = {}


class GrafanaCreate(_GrafanaCreate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema['skip_system_assigned_identity'] = AAZBoolArg(
            options=['--skip-system-assigned-identity', '--skip-identity'],
            help='Do not enable system assigned identity. Use this option if you want to manage the identity '
                 'yourself.',
            default=False,
        )
        args_schema['skip_role_assignments'] = AAZBoolArg(
            options=['--skip-role-assignments'],
            help='Skip creating default role assignments for the managed identity of the Grafana instance and '
                 'the current CLI account. Use this option if you want to manage role assignments yourself.',
            default=False,
        )
        args_schema['principal_ids'] = AAZListArg(
            options=['--principal-ids'],
            help='Space-separated Azure AD object ids for users, groups, etc. to be made as Grafana Admins. '
                 'Once provided, CLI won\'t make the current logged-in user as Grafana Admin',
        )
        args_schema['principal_ids'].Element = AAZStrArg()
        args_schema['identity']._registered = False  # pylint: disable=protected-access

        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        if args.skip_role_assignments and args.principal_ids:
            raise ArgumentUsageError("--skip-role-assignments | --principal-ids")

        if not args.skip_system_assigned_identity:
            args.identity = {"type": "SystemAssigned"}

        if args.sku_tier and str(args.sku_tier).lower() == "essential":
            raise ArgumentUsageError(
                "Creation of Grafana resources with the 'Essential' SKU tier is not supported. "
                "Supported SKU tiers are: 'Standard'. "
                "Please specify a supported SKU tier using the '--sku-tier' parameter."
            )

    # override the output method to create role assignments after instance creation
    def _output(self, *args, **kwargs):
        from azure.cli.core.commands.arm import resolve_role_id

        cli_ctx = self.ctx.cli_ctx
        args = self.ctx.args

        if not args.skip_role_assignments:
            logger.warning("Grafana instance of '%s' was created. Now creating default role assignments for its "
                           "managed identity, and current CLI account unless --principal-ids are provided.",
                           args.workspace_name)

            client = cf_amg(cli_ctx, subscription=None)
            subscription_scope = '/subscriptions/' + client._config.subscription_id  # pylint: disable=protected-access

            principal_ids = args.principal_ids
            if not principal_ids:
                user_principal_id = _get_login_account_principal_id(cli_ctx)
                principal_ids = [user_principal_id]
            grafana_admin_role_id = resolve_role_id(cli_ctx, "Grafana Admin", subscription_scope)

            for principal_id in principal_ids:
                _create_role_assignment(cli_ctx, principal_id, grafana_admin_role_id,
                                        self.ctx.vars.instance.id)

            if self.ctx.vars.instance.identity:
                monitoring_reader_role_id = resolve_role_id(cli_ctx, "Monitoring Reader", subscription_scope)
                _create_role_assignment(cli_ctx, self.ctx.vars.instance.identity.principal_id,
                                        monitoring_reader_role_id, subscription_scope)

        result = self.deserialize_output(self.ctx.vars.instance, client_flatten=True)
        return result


class GrafanaDelete(_GrafanaDelete):
    # store principal id for cleanup later
    principal_id = None

    def pre_operations(self):
        args = self.ctx.args
        client = cf_amg(self.ctx.cli_ctx, subscription=None)
        grafana = client.grafana.get(args.resource_group, args.workspace_name)
        self.principal_id = grafana.identity.principal_id

    def post_operations(self):
        args = self.ctx.args

        # delete role assignment
        logger.warning("Grafana instance of '%s' was deleted. Now removing role assignments for associated with its "
                       "managed identity.", args.workspace_name)
        _delete_role_assignment(self.ctx.cli_ctx, self.principal_id)


class GrafanaUpdate(_GrafanaUpdate):
    def pre_operations(self):
        args = self.ctx.args

        if args.grafana_major_version == "10":
            # prompt for confirmation, cancel operation if not confirmed
            if (not get_yes_or_no_option("You are trying to upgrade this workspace to Grafana version 10. By "
                                         "proceeding, you acknowledge that upgrading to Grafana version 10 is a "
                                         "permanent and irreversible operation and Grafana legacy alerting has been "
                                         "deprecated and any migrated legacy alert may require manual adjustments "
                                         "to function properly under the new alerting system. Do you wish to proceed? "
                                         "(y/n): ")):
                raise ManualInterrupt('Operation cancelled.')


# for injecting test seams to produce predictable role assignment id for playback
def _gen_guid():
    import uuid
    return uuid.uuid4()


def _get_login_account_principal_id(cli_ctx):
    from azure.cli.core._profile import Profile, _USER_ENTITY, _USER_TYPE, _SERVICE_PRINCIPAL, _USER_NAME
    from azure.cli.command_modules.role import graph_client_factory

    profile = Profile(cli_ctx=cli_ctx)
    active_account = profile.get_subscription()
    assignee = active_account[_USER_ENTITY][_USER_NAME]

    graph_client = graph_client_factory(cli_ctx)
    try:
        if active_account[_USER_ENTITY][_USER_TYPE] == _SERVICE_PRINCIPAL:
            result = list(graph_client.service_principal_list(
                filter=f"servicePrincipalNames/any(c:c eq '{assignee}')"))
        else:
            result = [graph_client.signed_in_user_get()]
    except Exception as error:
        raise CLIInternalError(f"Failed to get the current logged-in account. {error}")
    if not result:
        raise CLIInternalError((f"Failed to retrieve principal id for '{assignee}', which is needed to create a "
                                f"role assignment. Consider using '--principal-ids' to bypass the lookup"))
    return result[0]['id']


def _create_role_assignment(cli_ctx, principal_id, role_definition_id, scope):
    import time
    from azure.core.exceptions import HttpResponseError, ResourceExistsError

    assignments_client = get_mgmt_service_client(cli_ctx, AuthorizationManagementClient).role_assignments
    principal_types = [p.value for p in PrincipalType]
    current_principal_type = principal_types.pop(0)

    logger.info("Creating an assignment with a role '%s' on the scope of '%s'", role_definition_id, scope)
    retry_times = 36
    assignment_name = _gen_guid()
    for retry_time in range(0, retry_times):
        try:
            parameters = RoleAssignmentCreateParameters(role_definition_id=role_definition_id,
                                                        principal_id=principal_id,
                                                        principal_type=current_principal_type)
            assignments_client.create(scope=scope, role_assignment_name=assignment_name,
                                      parameters=parameters)
            break
        except ResourceExistsError:  # Exception from Track-2 SDK
            logger.info('Role assignment already exists')
            break
        except HttpResponseError as ex:
            if 'UnmatchedPrincipalType' in ex.message:  # try each principal_type until we get the right one
                logger.debug("Principal type '%s' is not matched", current_principal_type)
                try:
                    current_principal_type = principal_types.pop(0)
                except:
                    raise CLIInternalError("Failed to create a role assignment. No matching principal types found.")
                continue
            if 'role assignment already exists' in ex.message:  # Exception from Track-1 SDK
                logger.info('Role assignment already exists')
                break
            if retry_time < retry_times and ' does not exist in the directory ' in (ex.message or "").lower():
                time.sleep(5)
                logger.warning('Retrying role assignment creation: %s/%s', retry_time + 1,
                               retry_times)
                continue
            raise


def _delete_role_assignment(cli_ctx, principal_id, role_definition_id=None, scope=None):
    assignments_client = get_mgmt_service_client(cli_ctx, AuthorizationManagementClient).role_assignments
    f = f"principalId eq '{principal_id}'"

    if role_definition_id and scope:
        # delete specific role assignment
        assignments = list(assignments_client.list_for_scope(scope, filter=f))
        assignments_with_role = [a for a in assignments if a.role_definition_id.lower() == role_definition_id.lower()]
        for a in assignments_with_role:
            assignments_client.delete_by_id(a.id)
    else:
        # delete all role assignments for the principal
        assignments = list(assignments_client.list_for_subscription(filter=f))
        for a in assignments or []:
            assignments_client.delete_by_id(a.id)


def backup_grafana(cmd, grafana_name, components=None, directory=None, folders_to_include=None,
                   folders_to_exclude=None, resource_group_name=None, skip_folder_permissions=False):
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
           folders_to_exclude=folders_to_exclude,
           skip_folder_permissions=skip_folder_permissions)


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


def migrate_grafana(cmd, grafana_name, source_grafana_endpoint, source_grafana_token_or_api_key, dry_run=False,
                    overwrite=False, folders_to_include=None, folders_to_exclude=None, resource_group_name=None):
    from .migrate import migrate
    from .utils import get_health_endpoint, send_grafana_get

    # for source instance (backing up from)
    headers_src = {
        "content-type": "application/json",
        "authorization": "Bearer " + source_grafana_token_or_api_key
    }
    (status, _) = get_health_endpoint(source_grafana_endpoint, headers_src)
    if status == 400:
        # https://github.com/grafana/grafana/pull/27536
        # Some Grafana instances might block/not support "/api/health" endpoint
        (status, _) = send_grafana_get(f"{source_grafana_endpoint}/healthz", headers_src)

    if status == 401:
        raise ArgumentUsageError("Access to source grafana endpoint was denied")
    if status >= 400:
        raise ArgumentUsageError("Source grafana endpoint is not reachable")

    # for destination instance (restoring to)
    _health_endpoint_reachable(cmd, grafana_name, resource_group_name=resource_group_name)
    creds_dest = _get_data_plane_creds(cmd, api_key_or_token=None, subscription=None)
    headers_dest = {
        "content-type": "application/json",
        "authorization": "Bearer " + creds_dest[1]
    }

    migrate(backup_url=source_grafana_endpoint,
            backup_headers=headers_src,
            restore_url=_get_grafana_endpoint(cmd, resource_group_name, grafana_name, subscription=None),
            restore_headers=headers_dest,
            dry_run=dry_run,
            overwrite=overwrite,
            folders_to_include=folders_to_include,
            folders_to_exclude=folders_to_exclude)


def sync_dashboard(cmd, source, destination, folders_to_include=None, folders_to_exclude=None,
                   dashboards_to_include=None, dashboards_to_exclude=None, dry_run=None):
    from .sync import sync

    sync(cmd,
         source,
         destination,
         folders_to_include=folders_to_include,
         folders_to_exclude=folders_to_exclude,
         dashboards_to_include=dashboards_to_include,
         dashboards_to_exclude=dashboards_to_exclude,
         dry_run=dry_run)


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
    folder_uid = None
    if folder:
        folder_uid = _find_folder(cmd, resource_group_name, grafana_name, folder)["uid"]
    return _create_dashboard(cmd, grafana_name, definition=definition, title=title, folder_uid=folder_uid,
                             resource_group_name=resource_group_name, overwrite=overwrite,
                             api_key_or_token=api_key_or_token)


def _create_dashboard(cmd, grafana_name, definition, title=None, folder_uid=None, resource_group_name=None,
                      overwrite=None, api_key_or_token=None, for_sync=True, subscription=None):
    if "dashboard" in definition:
        payload = definition
    else:
        logger.info("Adjust input by adding 'dashboard' field")
        payload = {}
        payload['dashboard'] = definition

    if title:
        payload['dashboard']['title'] = title

    if folder_uid:
        payload['folderUid'] = folder_uid

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
    if data.get("meta", {}).get("isFolder", False):
        raise ArgumentUsageError("The provided definition is a folder, not a dashboard")

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

    response = _send_request(cmd, resource_group_name, grafana_name, "post", "/api/dashboards/db",
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
    else:
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
    return json.loads(response.content)


def create_folder(cmd, grafana_name, title, parent_folder=None, resource_group_name=None, api_key_or_token=None,
                  subscription=None):
    payload = {
        "title": title,
    }
    if parent_folder:
        data = _find_folder(cmd, resource_group_name, grafana_name, parent_folder, api_key_or_token=api_key_or_token)
        payload["parentUid"] = data["uid"]

    response = _send_request(cmd, resource_group_name, grafana_name, "post", "/api/folders", payload,
                             api_key_or_token=api_key_or_token, subscription=subscription)
    return json.loads(response.content)


def list_folders(cmd, grafana_name, resource_group_name=None, api_key_or_token=None, subscription=None):
    endpoint, headers = _get_grafana_request_context(cmd, resource_group_name, grafana_name, subscription,
                                                     api_key_or_token=api_key_or_token)

    status, content = search_folders(
        grafana_url=endpoint,
        http_get_headers=headers
    )

    if status >= 400:
        raise ArgumentUsageError(f"Failed to find folders. Error: {content}")

    return content


def update_folder(cmd, grafana_name, folder, title, resource_group_name=None, api_key_or_token=None):
    f = show_folder(cmd, grafana_name, folder, resource_group_name, api_key_or_token=api_key_or_token)
    data = {
        "title": title,
        "overwrite": True
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
    folders = list_folders(cmd, grafana_name, resource_group_name=resource_group_name,
                           api_key_or_token=api_key_or_token)

    # try uid first
    match = next((f for f in folders if f['uid'] == folder), None)
    if match:
        return match

    # If we get here, the folder is not found by uid, so we try by title
    match = next((f for f in folders if f['title'] == folder), None)
    if not match:
        raise ArgumentUsageError(f"Couldn't find the folder '{folder}'.")
    return match


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
    else:
        data['secondsToLive'] = _convert_duration_to_seconds("1d")

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


def link_monitor(cmd, grafana_name, monitor_name, monitor_resource_group_name, monitor_subscription_id=None,
                 resource_group_name=None, skip_role_assignments=False):
    from .integrations import link_amw_to_amg
    link_amw_to_amg(cmd, grafana_name, monitor_name, resource_group_name, monitor_resource_group_name,
                    monitor_subscription_id, skip_role_assignments)


def unlink_monitor(cmd, grafana_name, monitor_name, monitor_resource_group_name, monitor_subscription_id=None,
                   resource_group_name=None, skip_role_assignments=False):
    from .integrations import unlink_amw_from_amg
    unlink_amw_from_amg(cmd, grafana_name, monitor_name, resource_group_name, monitor_resource_group_name,
                        monitor_subscription_id, skip_role_assignments)


def list_monitors(cmd, grafana_name, resource_group_name=None):
    from .integrations import list_amw_linked_to_amg
    return list_amw_linked_to_amg(cmd, grafana_name, resource_group_name)


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
    potential_file_path = os.path.expanduser(file_content)
    if os.path.exists(potential_file_path):
        from azure.cli.core.util import read_file_content
        file_content = read_file_content(potential_file_path)
    else:
        raise InvalidArgumentValueError(f"Couldn't find the file '{file_content}'")
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
        client = cf_amg(cmd.cli_ctx, subscription=subscription)
        grafana = client.grafana.get(resource_group_name, grafana_name)
        endpoint = grafana.properties.endpoint
        grafana_endpoints[grafana_name] = endpoint
    return endpoint


def _send_request(cmd, resource_group_name, grafana_name, http_method, path, body=None, raise_for_error_status=True,
                  api_key_or_token=None, subscription=None):
    endpoint, headers = _get_grafana_request_context(cmd, resource_group_name, grafana_name, subscription,
                                                     api_key_or_token=api_key_or_token)

    # TODO: handle re-try on 429
    response = requests.request(http_method, url=endpoint + path, headers=headers, json=body, timeout=60,
                                verify=not should_disable_connection_verify())
    if response.status_code >= 400:
        if raise_for_error_status:
            logger.warning(str(response.content))
            response.raise_for_status()
    # TODO: log headers, requests and response
    return response


def _get_grafana_request_context(cmd, resource_group_name, grafana_name, subscription, api_key_or_token=None):
    endpoint = _get_grafana_endpoint(cmd, resource_group_name, grafana_name, subscription)
    creds = _get_data_plane_creds(cmd, api_key_or_token, subscription)
    headers = {
        "content-type": "application/json",
        "authorization": "Bearer " + creds[1]
    }

    return endpoint, headers
