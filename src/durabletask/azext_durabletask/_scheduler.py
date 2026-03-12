# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from .aaz.latest.durabletask.scheduler import Create as _SchedulerCreate
from .aaz.latest.durabletask.scheduler import Update as _SchedulerUpdate
from .aaz.latest.durabletask.scheduler import Show as _SchedulerShow
from .aaz.latest.durabletask.taskhub import Show as _TaskHubShow
from azure.cli.core.azclierror import ValidationError, ResourceNotFoundError
from azure.core.exceptions import HttpResponseError

import logging
logger = logging.getLogger(__name__)

RESOURCE_TYPE_MAP = {
    "microsoft.web/sites": "functionapp",
    "microsoft.app/containerapps": "containerapp",
}


def _parse_target(target):
    """Parse a target resource ID and return (target_type, name, rg, subscription)."""
    from azure.mgmt.core.tools import parse_resource_id

    parsed = parse_resource_id(target)
    name = parsed.get("name")
    rg = parsed.get("resource_group")
    sub = parsed.get("subscription")
    namespace = parsed.get("namespace", "")
    rtype = parsed.get("type", "")
    provider_key = f"{namespace}/{rtype}".lower()
    target_type = RESOURCE_TYPE_MAP.get(provider_key)
    if not target_type or not name or not rg or not sub:
        raise ValidationError(
            f"Invalid target resource ID: '{target}'. "
            "Expected a Function App (Microsoft.Web/sites) or "
            "Container App (Microsoft.App/containerApps) resource ID."
        )
    return target_type, name, rg, sub


ROLE_TYPE_MAP = {
    "worker": "Durable Task Worker",
    "contributor": "Durable Task Data Contributor",
    "reader": "Durable Task Data Reader",
}


class CreateScheduler(_SchedulerCreate):
    """Create a Durabletask scheduler."""

    def pre_operations(self):
        """Validate SKU parameters before executing the operation."""
        args = self.ctx.args

        if not args.sku_name or args.sku_name.to_serialized_data() is None:
            raise ValidationError("The --sku-name parameter is required.")

        if args.sku_name.to_serialized_data() == "Dedicated":
            if not args.sku_capacity or args.sku_capacity.to_serialized_data() is None:
                raise ValidationError(
                    "The --sku-capacity parameter is required when --sku-name is 'Dedicated'."
                )


class UpdateScheduler(_SchedulerUpdate):
    """Update a Durabletask scheduler."""

    def post_instance_update(self, instance):
        """Remove sku capacity from the payload if it is not set or is 0."""
        sku = instance.properties.sku
        capacity = sku.capacity.to_serialized_data()
        if capacity is None or capacity == 0:
            sku.capacity = None


def _get_caller_object_id(cli_ctx):
    """Get the current caller's Entra ID object ID from the access token."""
    from azure.cli.core._profile import Profile
    import json
    import base64

    profile = Profile(cli_ctx=cli_ctx)
    cred, _, _ = profile.get_raw_token()
    token = cred[1]
    parts = token.split('.')
    if len(parts) < 2:
        return None
    payload = parts[1]
    payload += '=' * (-len(payload) % 4)
    claims = json.loads(base64.urlsafe_b64decode(payload))
    return claims.get('oid')


def _check_access(cli_ctx, scope, actions, resource_label):
    """Check whether the caller has the required actions on a resource.

    Uses the Check Access API which resolves permissions inherited through
    Entra ID group memberships, unlike permissions.list_for_resource().
    Missing permissions are logged as warnings rather than hard errors.
    """
    from azure.cli.core.util import send_raw_request
    import json

    caller_oid = _get_caller_object_id(cli_ctx)
    if not caller_oid:
        logger.warning("Could not determine caller object ID; skipping permission check on %s.", resource_label)
        return

    arm_endpoint = cli_ctx.cloud.endpoints.resource_manager.rstrip('/')
    url = (f"{arm_endpoint}{scope}/providers/Microsoft.Authorization"
           f"/checkAccess?api-version=2022-04-01")
    body = json.dumps({
        "Subject": {"ObjectId": caller_oid},
        "Actions": [{"Id": a} for a in actions],
    })

    try:
        response = send_raw_request(cli_ctx, 'POST', url, body=body)
        data = response.json()
    except Exception as ex:  # pylint: disable=broad-exception-caught
        logger.warning("Failed to check access on %s: %s. Proceeding anyway.", resource_label, ex)
        return

    results = data if isinstance(data, list) else data.get("value", [])
    for result in results:
        action_id = result.get("actionId", "")
        decision = result.get("accessDecision", "")
        if decision != "Allowed":
            logger.warning(
                "Permission check on %s: action '%s' returned '%s'. "
                "The operation may fail if access is insufficient.",
                resource_label, action_id, decision,
            )


def _resolve_user_assigned_identity(cli_ctx, identity_resource_id):
    """Look up a user-assigned managed identity and return (principal_id, client_id)."""
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.msi import ManagedServiceIdentityClient
    from azure.mgmt.core.tools import parse_resource_id

    parsed = parse_resource_id(identity_resource_id)
    rg = parsed.get("resource_group")
    name = parsed.get("name")
    sub = parsed.get("subscription")
    if not rg or not name:
        raise ValidationError(
            f"Invalid user-assigned identity resource ID: '{identity_resource_id}'. "
            "Expected format: /subscriptions/{{sub}}/resourceGroups/{{rg}}"
            "/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{{name}}"
        )

    msi_client = get_mgmt_service_client(cli_ctx, ManagedServiceIdentityClient,
                                         subscription_id=sub)
    try:
        identity = msi_client.user_assigned_identities.get(rg, name)
    except HttpResponseError as ex:
        if ex.status_code == 404:
            raise ResourceNotFoundError(
                f"User-assigned identity '{identity_resource_id}' not found. "
                "Please verify the resource ID."
            ) from ex
        raise

    if identity is None or identity.principal_id is None:
        raise ResourceNotFoundError(
            f"User-assigned identity '{identity_resource_id}' could not be read."
        )

    return identity.principal_id, identity.client_id


def _ensure_identity_on_functionapp(cli_ctx, target_name, target_resource_group,
                                    target_subscription, identity_resource_id):
    """Ensure a user-assigned identity is attached to the Function App."""
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.web import WebSiteManagementClient
    from azure.mgmt.web.models import ManagedServiceIdentity

    web_client = get_mgmt_service_client(cli_ctx, WebSiteManagementClient,
                                         subscription_id=target_subscription)
    app = web_client.web_apps.get(target_resource_group, target_name)

    existing_ua = {}
    if app.identity and app.identity.user_assigned_identities:
        existing_ua = app.identity.user_assigned_identities

    normalized_id = identity_resource_id.lower()
    if any(k.lower() == normalized_id for k in existing_ua):
        logger.info("User-assigned identity already attached to function app '%s'.", target_name)
        return

    existing_ua[identity_resource_id] = {}
    has_system = app.identity and app.identity.type and "SystemAssigned" in app.identity.type
    identity_type = "SystemAssigned,UserAssigned" if has_system else "UserAssigned"

    web_client.web_apps.update(
        target_resource_group, target_name,
        {"identity": ManagedServiceIdentity(type=identity_type,
                                            user_assigned_identities=existing_ua)},
    )
    logger.info("User-assigned identity attached to function app '%s'.", target_name)


def _ensure_identity_on_containerapp(cli_ctx, target_name, target_resource_group,
                                     target_subscription, identity_resource_id):
    """Ensure a user-assigned identity is attached to the Container App."""
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.appcontainers import ContainerAppsAPIClient
    from azure.mgmt.appcontainers.models import ManagedServiceIdentity

    ca_client = get_mgmt_service_client(cli_ctx, ContainerAppsAPIClient,
                                        subscription_id=target_subscription,
                                        api_version='2024-03-01')
    app = ca_client.container_apps.get(target_resource_group, target_name)

    existing_ua = {}
    if app.identity and app.identity.user_assigned_identities:
        existing_ua = app.identity.user_assigned_identities

    normalized_id = identity_resource_id.lower()
    if any(k.lower() == normalized_id for k in existing_ua):
        logger.info("User-assigned identity already attached to container app '%s'.", target_name)
        return

    existing_ua[identity_resource_id] = {}
    has_system = app.identity and app.identity.type and "SystemAssigned" in app.identity.type
    identity_type = "SystemAssigned,UserAssigned" if has_system else "UserAssigned"

    ca_client.container_apps.begin_update(
        target_resource_group, target_name,
        {"identity": ManagedServiceIdentity(type=identity_type,
                                            user_assigned_identities=existing_ua)},
    ).result()
    logger.info("User-assigned identity attached to container app '%s'.", target_name)


def _get_functionapp_identity(cli_ctx, target_name, target_resource_group, target_subscription):
    """Retrieve the managed identity principal ID from a Function App."""
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.web import WebSiteManagementClient

    web_client = get_mgmt_service_client(cli_ctx, WebSiteManagementClient,
                                         subscription_id=target_subscription)
    try:
        app = web_client.web_apps.get(target_resource_group, target_name)
    except HttpResponseError as ex:
        if ex.status_code == 404:
            raise ResourceNotFoundError(
                f"Function app '{target_name}' not found in resource group "
                f"'{target_resource_group}'. Please verify the name and resource group."
            ) from ex
        raise

    if app is None or app.name is None:
        raise ResourceNotFoundError(
            f"Function app '{target_name}' not found in resource group "
            f"'{target_resource_group}'."
        )

    identity = app.identity
    if identity is None or identity.principal_id is None:
        raise ValidationError(
            f"Function app '{target_name}' does not have a managed identity enabled. "
            "Please enable a system-assigned managed identity with: "
            f"az functionapp identity assign -g {target_resource_group} -n {target_name}"
        )
    return identity.principal_id


def _get_containerapp_identity(cli_ctx, target_name, target_resource_group, target_subscription):
    """Retrieve the managed identity principal ID from a Container App."""
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.appcontainers import ContainerAppsAPIClient

    ca_client = get_mgmt_service_client(cli_ctx, ContainerAppsAPIClient,
                                        subscription_id=target_subscription,
                                        api_version='2024-03-01')
    try:
        app = ca_client.container_apps.get(target_resource_group, target_name)
    except HttpResponseError as ex:
        if ex.status_code == 404:
            raise ResourceNotFoundError(
                f"Container app '{target_name}' not found in resource group "
                f"'{target_resource_group}'. Please verify the name and resource group."
            ) from ex
        raise

    if app is None or app.name is None:
        raise ResourceNotFoundError(
            f"Container app '{target_name}' not found in resource group "
            f"'{target_resource_group}'."
        )

    identity = app.identity
    if identity is None or identity.principal_id is None:
        raise ValidationError(
            f"Container app '{target_name}' does not have a managed identity enabled. "
            "Please enable a system-assigned managed identity with: "
            f"az containerapp identity assign -g {target_resource_group} -n {target_name}"
        )
    return identity.principal_id


def _check_target_permissions(cli_ctx, target_type, target_id):
    """Check that the caller has the required permissions on the target resource."""
    if target_type == "functionapp":
        required_actions = [
            "Microsoft.Web/sites/config/list/action",
            "Microsoft.Web/sites/config/write",
        ]
    else:  # containerapp
        required_actions = [
            "Microsoft.App/containerApps/read",
            "Microsoft.App/containerApps/write",
        ]

    logger.info("Checking permissions on target...")
    _check_access(cli_ctx, target_id, required_actions,
                  f"{target_type} '{target_id}'")


def _update_functionapp_settings(cli_ctx, target_name, target_resource_group, target_subscription,
                                 endpoint, task_hub_name, client_id=None):
    """Update a Function App's application settings with scheduler connection info."""
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.web import WebSiteManagementClient
    from azure.mgmt.web.models import StringDictionary

    web_client = get_mgmt_service_client(cli_ctx, WebSiteManagementClient,
                                         subscription_id=target_subscription)
    existing_settings = web_client.web_apps.list_application_settings(
        target_resource_group, target_name)
    app_settings = dict(existing_settings.properties) if existing_settings.properties else {}

    conn_str = f"Endpoint={endpoint};Authentication=ManagedIdentity"
    if client_id:
        conn_str += f";ClientID={client_id}"
    app_settings["DURABLE_TASK_SCHEDULER_CONNECTION_STRING"] = conn_str
    app_settings["TASKHUB_NAME"] = task_hub_name

    web_client.web_apps.update_application_settings(
        target_resource_group, target_name,
        StringDictionary(properties=app_settings),
    )
    logger.info("App settings updated successfully.")


def _update_containerapp_env_vars(cli_ctx, target_name, target_resource_group, target_subscription,
                                  endpoint, task_hub_name, client_id=None):
    """Update a Container App's environment variables with scheduler connection info.

    Only the template is patched to ensure existing identity, configuration,
    and other properties are not removed.
    """
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.appcontainers import ContainerAppsAPIClient

    ca_client = get_mgmt_service_client(cli_ctx, ContainerAppsAPIClient,
                                        subscription_id=target_subscription,
                                        api_version='2024-03-01')
    app = ca_client.container_apps.get(target_resource_group, target_name)

    template = app.template
    if not template or not template.containers:
        raise ValidationError(
            f"Container app '{target_name}' has no containers in its template."
        )

    conn_str = f"Endpoint={endpoint};Authentication=ManagedIdentity"
    if client_id:
        conn_str += f";ClientID={client_id}"
    env_map = {"DURABLE_TASK_SCHEDULER_CONNECTION_STRING": conn_str,
               "TASKHUB_NAME": task_hub_name}

    from azure.mgmt.appcontainers.models import EnvironmentVar

    # Apply the environment variables to all containers in the template.
    for container in template.containers:
        env_vars = list(container.env or [])
        for name, value in env_map.items():
            found = False
            for ev in env_vars:
                if ev.name == name:
                    ev.value = value
                    found = True
                    break
            if not found:
                env_vars.append(EnvironmentVar(name=name, value=value))
        container.env = env_vars
    ca_client.container_apps.begin_update(
        target_resource_group, target_name,
        {"template": template},
    ).result()
    logger.info("Container app environment variables updated successfully.")


def attach_scheduler(cmd, resource_group_name, scheduler_name, task_hub_name,  # pylint: disable=too-many-locals
                     target, role_type, identity=None):
    """Attach a Durable Task scheduler to a Function App or Container App."""
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.cli.core.commands.arm import resolve_role_id
    from azure.mgmt.authorization import AuthorizationManagementClient
    from azure.mgmt.authorization.models import RoleAssignmentCreateParameters
    from azure.core.exceptions import ResourceExistsError
    import uuid

    cli_ctx = cmd.cli_ctx
    client_id = None

    # Parse the target resource ID
    target_type, target_name, target_rg, target_sub = _parse_target(target)

    # Step 1: Get the scheduler to retrieve its endpoint
    logger.info("Retrieving scheduler '%s' in resource group '%s'...", scheduler_name, resource_group_name)
    scheduler = _SchedulerShow(cli_ctx=cli_ctx)(command_args={
        "resource_group": resource_group_name,
        "name": scheduler_name,
    })
    provisioning_state = scheduler.get("properties", {}).get("provisioningState", "")
    if provisioning_state != "Succeeded":
        raise ValidationError(
            f"Scheduler '{scheduler_name}' is not ready (provisioningState: '{provisioning_state}'). "
            "Please wait until the scheduler is fully provisioned."
        )
    endpoint = scheduler.get("properties", {}).get("endpoint")
    if not endpoint:
        raise ValidationError(
            f"Scheduler '{scheduler_name}' does not have an endpoint. "
            "Ensure the scheduler is fully provisioned."
        )

    # Step 1b: Verify the task hub exists under the scheduler
    logger.info("Verifying task hub '%s' exists under scheduler '%s'...", task_hub_name, scheduler_name)
    try:
        _TaskHubShow(cli_ctx=cli_ctx)(command_args={
            "resource_group": resource_group_name,
            "scheduler_name": scheduler_name,
            "name": task_hub_name,
        })
    except HttpResponseError as ex:
        if ex.status_code == 404:
            raise ResourceNotFoundError(
                f"Task hub '{task_hub_name}' not found under scheduler '{scheduler_name}' "
                f"in resource group '{resource_group_name}'. "
                "Please verify the task hub name."
            ) from ex
        raise

    # Step 2: Resolve the identity to use for role assignment
    if identity:
        # User-assigned identity: look it up and attach to the target if needed
        logger.info("Resolving user-assigned identity '%s'...", identity)
        principal_id, client_id = _resolve_user_assigned_identity(cli_ctx, identity)
        logger.info("User-assigned identity principal ID: %s, client ID: %s", principal_id, client_id)

        logger.info("Ensuring identity is attached to %s '%s'...", target_type, target_name)
        if target_type == "functionapp":
            _ensure_identity_on_functionapp(
                cli_ctx, target_name, target_rg,
                target_sub, identity)
        else:
            _ensure_identity_on_containerapp(
                cli_ctx, target_name, target_rg,
                target_sub, identity)
    else:
        # System-assigned identity: retrieve from the target resource
        logger.info("Retrieving %s '%s' in resource group '%s'...",
                    target_type, target_name, target_rg)
        if target_type == "functionapp":
            principal_id = _get_functionapp_identity(
                cli_ctx, target_name, target_rg, target_sub)
        else:
            principal_id = _get_containerapp_identity(
                cli_ctx, target_name, target_rg, target_sub)
    logger.info("Managed identity principal ID: %s", principal_id)

    # Step 2b: Check permissions on the target and scheduler
    _check_target_permissions(cli_ctx, target_type, target)

    scheduler_id = scheduler.get("id")
    logger.info("Checking permissions on scheduler '%s'...", scheduler_name)
    _check_access(cli_ctx, scheduler_id, [
        "Microsoft.Authorization/roleAssignments/write",
    ], f"scheduler '{scheduler_name}'")

    # Step 3: Assign the selected role to the target's managed identity
    role_name = ROLE_TYPE_MAP[role_type]
    subscription_scope = "/subscriptions/" + cli_ctx.data["subscription_id"]
    role_definition_id = resolve_role_id(cli_ctx, role_name, subscription_scope)

    logger.info("Assigning '%s' role to principal '%s' on scope '%s'...",
                role_name, principal_id, scheduler_id)
    assignments_client = get_mgmt_service_client(cli_ctx, AuthorizationManagementClient).role_assignments
    assignment_name = str(uuid.uuid4())
    try:
        assignments_client.create(
            scope=scheduler_id,
            role_assignment_name=assignment_name,
            parameters=RoleAssignmentCreateParameters(
                role_definition_id=role_definition_id,
                principal_id=principal_id,
                principal_type="ServicePrincipal",
            ),
        )
        logger.info("Role assignment created successfully.")
    except ResourceExistsError:
        logger.info("Role assignment already exists, skipping.")
    except HttpResponseError as ex:
        if "role assignment already exists" in (ex.message or "").lower():
            logger.info("Role assignment already exists, skipping.")
        else:
            raise

    # Step 4: Update the target's app settings / environment variables
    logger.info("Updating settings for %s '%s'...", target_type, target_name)
    if target_type == "functionapp":
        _update_functionapp_settings(
            cli_ctx, target_name, target_rg,
            target_sub, endpoint, task_hub_name, client_id)
    else:
        _update_containerapp_env_vars(
            cli_ctx, target_name, target_rg,
            target_sub, endpoint, task_hub_name, client_id)

    conn_str = f"Endpoint={endpoint};Authentication=ManagedIdentity"
    if client_id:
        conn_str += f";ClientID={client_id}"

    result = {
        "schedulerName": scheduler_name,
        "resourceGroupName": resource_group_name,
        "taskHubName": task_hub_name,
        "targetResourceId": target,
        "targetType": target_type,
        "connectionString": conn_str,
        "identityPrincipalId": principal_id,
        "roleAssigned": role_name,
    }
    if identity:
        result["identityResourceId"] = identity
        result["identityClientId"] = client_id
    return result
