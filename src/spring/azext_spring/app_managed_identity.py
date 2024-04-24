# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ._clierror import ConflictRequestError
from ._utils import wait_till_end
from .vendored_sdks.appplatform.v2024_05_01_preview import models
from azure.cli.core.azclierror import (AzureInternalError, CLIInternalError)
from azure.core.exceptions import HttpResponseError
from msrestazure.azure_exceptions import CloudError
from azure.cli.core.commands import arm as _arm
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.profiles import (ResourceType, get_sdk)
from knack.log import get_logger
from time import sleep


logger = get_logger(__name__)


ENABLE_LOWER = "enable"
DISABLE_LOWER = "disable"
UPDATING_LOWER = "updating"
DELETING_LOWER = "deleting"
APP_CREATE_OR_UPDATE_SLEEP_INTERVAL = 2


def app_identity_assign(cmd,
                        client,
                        resource_group,
                        service,
                        name,
                        role=None,
                        scope=None,
                        system_assigned=None,
                        user_assigned=None):
    """
    Note: Always use sync method to operate managed identity to avoid data inconsistency.
    :param role: role name of role assignment for system-assigned managed identity.
    :param scope: scope of role assignment for system-assigned managed identity.
    :param system_assigned: 1. None or False: Don't change system-assigned managed identity.
                            2. Enable system-assigned managed identity on app.
    :param user_assigned: 1. None: Don't change user-assigned managed identities.
                          2. A non-empty list of user-assigned managed identity resource id to app.
                          3. A empty list: should be blocked by validator.
    """
    # TODO(jiec): Retire legacy identity assign after migration.
    poller = None
    if _is_legacy_identity_assign(system_assigned, user_assigned):
        poller = _legacy_app_identity_assign(cmd, client, resource_group, service, name)
    else:
        poller = _new_app_identity_assign(cmd, client, resource_group, service, name, system_assigned, user_assigned)
    wait_till_end(poller)
    poller.result()
    if "succeeded" != poller.status().lower():
        return poller

    if role and scope:
        _create_role_assignment(cmd, client, resource_group, service, name, role, scope)

    return client.apps.get(resource_group, service, name)


def app_identity_remove(cmd,
                        client,
                        resource_group,
                        service,
                        name,
                        system_assigned=None,
                        user_assigned=None):
    """
    Note: Always use sync method to operate managed identity to avoid data inconsistency.
    :param system_assigned: 1) None or False: Don't change system-assigned managed identity.
                            2) True: remove system-assigned managed identity
    :param user_assigned: 1) None: Don't change user-assigned managed identities.
                          2) An empty list: remove all user-assigned managed identities.
                          3) A non-empty list of user-assigned managed identity resource id to remove.
    """
    app = client.apps.get(resource_group, service, name)
    if _app_not_updatable(app):
        raise ConflictRequestError("Failed to remove managed identities since app is in {} state.".format(app.properties.provisioning_state))

    if not app.identity:
        logger.warning("Skip remove managed identity since no identities assigned to app.")
        return
    if not app.identity.type:
        raise AzureInternalError("Invalid existed identity type {}.".format(app.identity.type))
    if app.identity.type == models.ManagedIdentityType.NONE:
        logger.warning("Skip remove managed identity since identity type is {}.".format(app.identity.type))
        return

    # TODO(jiec): For back-compatible, convert to remove system-assigned only case. Remove code after migration.
    if system_assigned is None and user_assigned is None:
        system_assigned = True

    new_user_identities = _get_new_user_identities_for_remove(app.identity.user_assigned_identities, user_assigned)
    new_identity_type = _get_new_identity_type_for_remove(app.identity.type, system_assigned, new_user_identities)
    user_identity_payload = _get_user_identity_payload_for_remove(new_identity_type, user_assigned)

    target_identity = models.ManagedIdentityProperties()
    target_identity.type = new_identity_type
    target_identity.user_assigned_identities = user_identity_payload

    app_resource = models.AppResource()
    app_resource.identity = target_identity

    poller = client.apps.begin_update(resource_group, service, name, app_resource)
    wait_till_end(cmd, poller)
    poller.result()
    if "succeeded" != poller.status().lower():
        return poller
    else:
        return client.apps.get(resource_group, service, name)


def app_identity_force_set(cmd,
                           client,
                           resource_group,
                           service,
                           name,
                           system_assigned,
                           user_assigned):
    """
    :param system_assigned: string, disable or enable
    :param user_assigned: 1. A single-element string list with 'disable'
                          2. A non-empty list of user-assigned managed identity resource ID.
    """
    exist_app = client.apps.get(resource_group, service, name)
    if _app_not_updatable(exist_app):
        raise ConflictRequestError("Failed to force set managed identities since app is in {} state.".format(
            exist_app.properties.provisioning_state))

    new_identity_type = _get_new_identity_type_for_force_set(system_assigned, user_assigned)
    user_identity_payload = _get_user_identity_payload_for_force_set(user_assigned)

    target_identity = models.ManagedIdentityProperties()
    target_identity.type = new_identity_type
    target_identity.user_assigned_identities = user_identity_payload

    # All read-only attributes will be droped by SDK automatically.
    exist_app.identity = target_identity
    exist_app.properties.secrets = None

    poller = client.apps.begin_create_or_update(resource_group, service, name, exist_app)
    wait_till_end(cmd, poller)
    poller.result()
    if "succeeded" != poller.status().lower():
        return poller
    else:
        return client.apps.get(resource_group, service, name)


def app_identity_show(cmd, client, resource_group, service, name):
    app = client.apps.get(resource_group, service, name)
    return app.identity


def _is_legacy_identity_assign(system_assigned, user_assigned):
    return not system_assigned and not user_assigned


def _legacy_app_identity_assign(cmd, client, resource_group, service, name):
    """
    Enable system-assigned managed identity on app.
    """
    app = client.apps.get(resource_group, service, name)
    if _app_not_updatable(app):
        raise ConflictRequestError("Failed to enable system-assigned managed identity since app is in {} state.".format(
            app.properties.provisioning_state))

    new_identity_type = models.ManagedIdentityType.SYSTEM_ASSIGNED
    if app.identity and app.identity.type in (models.ManagedIdentityType.USER_ASSIGNED,
                                              models.ManagedIdentityType.SYSTEM_ASSIGNED_USER_ASSIGNED):
        new_identity_type = models.ManagedIdentityType.SYSTEM_ASSIGNED_USER_ASSIGNED
    target_identity = models.ManagedIdentityProperties(type=new_identity_type)
    app_resource = models.AppResource(identity=target_identity)

    logger.warning("Start to enable system-assigned managed identity.")
    return client.apps.begin_update(resource_group, service, name, app_resource)


def _new_app_identity_assign(cmd, client, resource_group, service, name, system_assigned, user_assigned):
    app = client.apps.get(resource_group, service, name)
    if _app_not_updatable(app):
        raise ConflictRequestError(
            "Failed to assign managed identities since app is in {} state.".format(app.properties.provisioning_state))

    new_identity_type = _get_new_identity_type_for_assign(app, system_assigned, user_assigned)
    user_identity_payload = _get_user_identity_payload_for_assign(new_identity_type, user_assigned)

    identity_payload = models.ManagedIdentityProperties()
    identity_payload.type = new_identity_type
    identity_payload.user_assigned_identities = user_identity_payload

    app_resource = models.AppResource(identity=identity_payload)

    logger.warning("Start to assign managed identities to app.")
    return client.apps.begin_update(resource_group, service, name, app_resource)


def _get_new_identity_type_for_assign(app, system_assigned, user_assigned):
    new_identity_type = None

    if app.identity and app.identity.type:
        new_identity_type = app.identity.type
    else:
        new_identity_type = models.ManagedIdentityType.NONE

    if system_assigned:
        if new_identity_type in (models.ManagedIdentityType.USER_ASSIGNED,
                                 models.ManagedIdentityType.SYSTEM_ASSIGNED_USER_ASSIGNED):
            new_identity_type = models.ManagedIdentityType.SYSTEM_ASSIGNED_USER_ASSIGNED
        else:
            new_identity_type = models.ManagedIdentityType.SYSTEM_ASSIGNED

    if user_assigned:
        if new_identity_type in (models.ManagedIdentityType.SYSTEM_ASSIGNED,
                                 models.ManagedIdentityType.SYSTEM_ASSIGNED_USER_ASSIGNED):
            new_identity_type = models.ManagedIdentityType.SYSTEM_ASSIGNED_USER_ASSIGNED
        else:
            new_identity_type = models.ManagedIdentityType.USER_ASSIGNED

    if not new_identity_type or new_identity_type == models.ManagedIdentityType.NONE:
        raise CLIInternalError("Internal error: invalid new identity type:{}.".format(new_identity_type))

    return new_identity_type


def _get_user_identity_payload_for_assign(new_identity_type, new_user_identity_rid_list):
    """
    :param new_user_identity_rid_list: 1. None object.
                                       2. A non-empty list of user-assigned managed identity resource ID.
    :return 1. None object.
            2. A dict from user-assigned managed identity to an empty object.
    """
    uid_payload = {}
    if new_identity_type == models.ManagedIdentityType.SYSTEM_ASSIGNED:
        pass
    elif new_identity_type in (models.ManagedIdentityType.USER_ASSIGNED,
                               models.ManagedIdentityType.SYSTEM_ASSIGNED_USER_ASSIGNED):
        if new_user_identity_rid_list:
            for rid in new_user_identity_rid_list:
                uid_payload[rid] = models.UserAssignedManagedIdentity()

    if len(uid_payload) == 0:
        uid_payload = None

    return uid_payload


def _create_role_assignment(cmd, client, resource_group, service, name, role, scope):
    app = client.apps.get(resource_group, service, name)

    if not app.identity or not app.identity.principal_id:
        raise AzureInternalError(
            "Failed to create role assignment without object ID(principal ID) of system-assigned managed identity.")

    identity_role_id = _arm.resolve_role_id(cmd.cli_ctx, role, scope)
    assignments_client = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_AUTHORIZATION).role_assignments
    RoleAssignmentCreateParameters = get_sdk(cmd.cli_ctx, ResourceType.MGMT_AUTHORIZATION,
                                             'RoleAssignmentCreateParameters', mod='models',
                                             operation_group='role_assignments')
    parameters = RoleAssignmentCreateParameters(role_definition_id=identity_role_id,
                                                principal_id=app.identity.principal_id)
    logger.warning("Creating an assignment with a role '%s' on the scope of '%s'", identity_role_id, scope)
    retry_times = 36
    assignment_name = _arm._gen_guid()
    for i in range(0, retry_times):
        try:
            assignments_client.create(scope=scope, role_assignment_name=assignment_name,
                                      parameters=parameters)
            break
        except (HttpResponseError, CloudError) as ex:
            if 'role assignment already exists' in ex.message:
                logger.warning('Role assignment already exists')
                break
            elif i < retry_times and ' does not exist in the directory ' in ex.message:
                sleep(APP_CREATE_OR_UPDATE_SLEEP_INTERVAL)
                logger.warning('Retrying role assignment creation: %s/%s', i + 1,
                               retry_times)
                continue
            else:
                raise


def _get_new_user_identities_for_remove(exist_user_identity_dict, user_identity_list_to_remove):
    """
    :param exist_user_identity_dict: A dict from user-assigned managed identity resource id to identity objecct.
    :param user_identity_list_to_remove: None, an empty list or a list of string of user-assigned managed identity resource id to remove.
    :return A list of string of user-assigned managed identity resource ID.
    """
    if not exist_user_identity_dict:
        return []

    # None
    if user_identity_list_to_remove is None:
        return list(exist_user_identity_dict.keys())

    # Empty list means remove all user-assigned managed identities
    if len(user_identity_list_to_remove) == 0:
        return []

    # Non-empty list
    new_identities = []
    for id in exist_user_identity_dict.keys():
        if not id.lower() in user_identity_list_to_remove:
            new_identities.append(id)

    return new_identities


def _get_new_identity_type_for_remove(exist_identity_type, is_remove_system_identity, new_user_identities):
    new_identity_type = exist_identity_type

    exist_identity_type_str = exist_identity_type.lower()

    if exist_identity_type_str == models.ManagedIdentityType.NONE.lower():
        new_identity_type = models.ManagedIdentityType.NONE
    elif exist_identity_type_str == models.ManagedIdentityType.SYSTEM_ASSIGNED.lower():
        if is_remove_system_identity:
            new_identity_type = models.ManagedIdentityType.NONE
        else:
            new_identity_type = models.ManagedIdentityType.SYSTEM_ASSIGNED
    elif exist_identity_type_str == models.ManagedIdentityType.USER_ASSIGNED.lower():
        if not new_user_identities:
            new_identity_type = models.ManagedIdentityType.NONE
        else:
            new_identity_type = models.ManagedIdentityType.USER_ASSIGNED
    elif exist_identity_type_str == models.ManagedIdentityType.SYSTEM_ASSIGNED_USER_ASSIGNED.lower():
        if is_remove_system_identity and not new_user_identities:
            new_identity_type = models.ManagedIdentityType.NONE
        elif not is_remove_system_identity and not new_user_identities:
            new_identity_type = models.ManagedIdentityType.SYSTEM_ASSIGNED
        elif is_remove_system_identity and new_user_identities:
            new_identity_type = models.ManagedIdentityType.USER_ASSIGNED
        else:
            new_identity_type = models.ManagedIdentityType.SYSTEM_ASSIGNED_USER_ASSIGNED
    else:
        raise AzureInternalError("Invalid identity type: {}.".format(exist_identity_type_str))

    return new_identity_type


def _get_user_identity_payload_for_remove(new_identity_type, user_identity_list_to_remove):
    """
    :param new_identity_type: ManagedIdentityType
    :param user_identity_list_to_remove: None, an empty list or a list of string of user-assigned managed identity resource id to remove.
    :return None object or a non-empty dict from user-assigned managed identity resource id to None object
    """
    user_identity_payload = {}
    if new_identity_type in (models.ManagedIdentityType.USER_ASSIGNED,
                             models.ManagedIdentityType.SYSTEM_ASSIGNED_USER_ASSIGNED):
        # empty list means remove all user-assigned managed identites
        if user_identity_list_to_remove is not None and len(user_identity_list_to_remove) == 0:
            raise CLIInternalError("When remove all user-assigned managed identities, "
                                   "target identity type should not be {}.".format(new_identity_type))
        # non-empty list
        elif user_identity_list_to_remove:
            for id in user_identity_list_to_remove:
                user_identity_payload[id] = None

    if not user_identity_payload:
        user_identity_payload = None

    return user_identity_payload


def _get_new_identity_type_for_force_set(system_assigned, user_assigned):
    new_identity_type = models.ManagedIdentityType.NONE
    if DISABLE_LOWER == system_assigned and DISABLE_LOWER != user_assigned[0]:
        new_identity_type = models.ManagedIdentityType.USER_ASSIGNED
    elif ENABLE_LOWER == system_assigned and DISABLE_LOWER == user_assigned[0]:
        new_identity_type = models.ManagedIdentityType.SYSTEM_ASSIGNED
    elif ENABLE_LOWER == system_assigned and DISABLE_LOWER != user_assigned[0]:
        new_identity_type = models.ManagedIdentityType.SYSTEM_ASSIGNED_USER_ASSIGNED
    return new_identity_type


def _get_user_identity_payload_for_force_set(user_assigned):
    if DISABLE_LOWER == user_assigned[0]:
        return None
    user_identity_payload = {}
    for user_identity_resource_id in user_assigned:
        user_identity_payload[user_identity_resource_id] = models.UserAssignedManagedIdentity()
    if not user_identity_payload:
        user_identity_payload = None
    return user_identity_payload


def _app_not_updatable(app):
    return app.properties \
        and app.properties.provisioning_state \
        and app.properties.provisioning_state.lower() in [UPDATING_LOWER, DELETING_LOWER]
