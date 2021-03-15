# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from knack.util import CLIError
from azure.graphrbac.models import Application, ServicePrincipal, AppRole


def list_app_roles(cmd, app: str):
    client = _get_client(cmd.cli_ctx)
    app = _get_managed_application(client, app)

    return app.app_roles


def list_role_assignments(cmd, service_principal: str):
    client = _get_client(cmd.cli_ctx)
    sp = _get_service_principal(client, service_principal)

    role_assignments = raw_call(
        cmd,
        "get",
        f"https://graph.microsoft.com/beta/servicePrincipals/{sp.object_id}/appRoleAssignments",
    )["value"]
    ras = list()

    for assignment in role_assignments:
        app_service_principal_id = assignment["resourceId"]
        app: Application = client.service_principals.get(app_service_principal_id)
        role_name = None
        for role in app.app_roles:
            if role.id == assignment["appRoleId"]:
                role_name = role.value
                break

        ra = {
            "assignment_id": assignment["id"],
            "role_name": role_name,
            "app_id": app.app_id,
            "app_display_name": app.display_name,
            "service_principal_id": sp.object_id,
            "service_principal_display_name": sp.display_name,
        }
        ras.append(ra)

    return ras


def add_role_assignment(cmd, service_principal: str, app: str, role: str):
    client = _get_client(cmd.cli_ctx)
    sp = _get_service_principal(client, service_principal)

    app = _get_managed_application(client, app)

    app_role: AppRole = None
    for r in app.app_roles:
        if r.value == role:
            app_role = r
            break

    assignment = {}
    assignment["principalId"] = sp.object_id
    assignment["resourceId"] = app.object_id
    assignment["appRoleId"] = app_role.id

    result = raw_call(
        cmd,
        "post",
        f"https://graph.microsoft.com/beta/servicePrincipals/{sp.object_id}/appRoleAssignedTo",
        json.dumps(assignment),
    )
    return result


def remove_role_assignment(cmd, service_principal: str, role_assignment_id: str):
    client = _get_client(cmd.cli_ctx)
    sp = _get_service_principal(client, service_principal)
    return raw_call(
        cmd,
        "delete",
        f"https://graph.microsoft.com/beta/servicePrincipals/{sp.object_id}/appRoleAssignedTo/{role_assignment_id}",
    )


def _get_managed_application(client, app: str):
    import re

    query = f"displayName eq '{app}'"
    if re.match(
            "[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}",
            app,
    ):
        query = f"appId eq '{app}'"

    apps = list(client.service_principals.list(filter=query))

    if len(apps) > 1:
        raise CLIError(
            "More than one application was found - try using application id instead"
        )

    if not apps:
        raise CLIError("No application was found looking for " + app)
    app: Application = apps[0]
    return app


def _get_service_principal(client, service_principal: str):
    import re

    query = f"servicePrincipalNames/any(c:c eq '{service_principal}') or displayName eq '{service_principal}'"
    guid_pattern = (
        "[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}"
    )
    if re.match(
            guid_pattern,
            service_principal,
    ):
        query = f"objectId eq '{service_principal}'"

    service_principals = list(client.service_principals.list(filter=query))
    if len(service_principals) > 1:
        raise CLIError(
            "More than one service principal matched - try using object id instead"
        )

    if not service_principals:
        raise CLIError(
            "No service principal was found looking for " + service_principal
        )

    sp: ServicePrincipal = service_principals[0]
    return sp


def _get_client(cli_ctx):
    from azure.cli.core._profile import Profile
    from azure.graphrbac import GraphRbacManagementClient

    profile = Profile(cli_ctx=cli_ctx)
    cred, _, tenant_id = profile.get_login_credentials(
        resource=cli_ctx.cloud.endpoints.active_directory_graph_resource_id
    )
    graph_client = GraphRbacManagementClient(
        cred,
        tenant_id,
        base_url=cli_ctx.cloud.endpoints.active_directory_graph_resource_id,
    )
    return graph_client


def raw_call(cmd, method, url, body=None):
    from azure.cli.core.util import send_raw_request

    r = send_raw_request(cmd.cli_ctx, method, url, body=body)
    if r.content:
        return r.json()
    return None
