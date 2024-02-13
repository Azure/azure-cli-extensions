# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import time
import uuid

from azure.cli.command_modules.acs._client_factory import (
    get_auth_management_client,
)
from azure.cli.command_modules.acs._graph import resolve_object_id
from azure.cli.command_modules.acs._roleassignments import build_role_scope, resolve_role_id
from azure.cli.core.azclierror import AzCLIError
from azure.cli.core.profiles import ResourceType, get_sdk
from azure.core.exceptions import HttpResponseError, ResourceExistsError
from knack.log import get_logger
from msrestazure.azure_exceptions import CloudError

logger = get_logger(__name__)

# pylint: disable=protected-access


# temp workaround for the breaking change caused by default API version bump of the auth SDK
def add_role_assignment(cmd, role, service_principal_msi_id, is_service_principal=True, delay=2, scope=None):
    from azure.cli.core import __version__ as core_version
    if core_version <= "2.45.0":
        return _add_role_assignment_old(cmd, role, service_principal_msi_id, is_service_principal, delay, scope)
    return _add_role_assignment_new(cmd, role, service_principal_msi_id, is_service_principal, delay, scope)


# TODO(fuming): remove and replaced by import from azure.cli.command_modules.acs once dependency bumped to 2.47.0
def _add_role_assignment_executor_new(cmd, role, assignee, resource_group_name=None, scope=None, resolve_assignee=True):
    factory = get_auth_management_client(cmd.cli_ctx, scope)
    assignments_client = factory.role_assignments
    definitions_client = factory.role_definitions

    # FIXME: is this necessary?
    if assignments_client._config is None:
        raise AzCLIError("Assignments client config is undefined.")

    scope = build_role_scope(resource_group_name, scope, assignments_client._config.subscription_id)

    # XXX: if role is uuid, this function's output cannot be used as role assignment defintion id
    # ref: https://github.com/Azure/azure-cli/issues/2458
    role_id = resolve_role_id(role, scope, definitions_client)

    # If the cluster has service principal resolve the service principal client id to get the object id,
    # if not use MSI object id.
    object_id = resolve_object_id(cmd.cli_ctx, assignee) if resolve_assignee else assignee

    assignment_name = uuid.uuid4()
    custom_headers = None

    RoleAssignmentCreateParameters = get_sdk(
        cmd.cli_ctx,
        ResourceType.MGMT_AUTHORIZATION,
        "RoleAssignmentCreateParameters",
        mod="models",
        operation_group="role_assignments",
    )
    if cmd.supported_api_version(min_api="2018-01-01-preview", resource_type=ResourceType.MGMT_AUTHORIZATION):
        parameters = RoleAssignmentCreateParameters(role_definition_id=role_id, principal_id=object_id,
                                                    principal_type=None)
        return assignments_client.create(scope, assignment_name, parameters, headers=custom_headers)

    # for backward compatibility
    RoleAssignmentProperties = get_sdk(
        cmd.cli_ctx,
        ResourceType.MGMT_AUTHORIZATION,
        "RoleAssignmentProperties",
        mod="models",
        operation_group="role_assignments",
    )
    properties = RoleAssignmentProperties(role_definition_id=role_id, principal_id=object_id)
    return assignments_client.create(scope, assignment_name, properties, headers=custom_headers)


# TODO(fuming): remove and replaced by import from azure.cli.command_modules.acs once dependency bumped to 2.47.0
def _add_role_assignment_new(cmd, role, service_principal_msi_id, is_service_principal=True, delay=2, scope=None):
    # AAD can have delays in propagating data, so sleep and retry
    hook = cmd.cli_ctx.get_progress_controller(True)
    hook.add(message="Waiting for AAD role to propagate", value=0, total_val=1.0)
    logger.info("Waiting for AAD role to propagate")
    for x in range(0, 10):
        hook.add(message="Waiting for AAD role to propagate", value=0.1 * x, total_val=1.0)
        try:
            # TODO: break this out into a shared utility library
            _add_role_assignment_executor_new(
                cmd,
                role,
                service_principal_msi_id,
                scope=scope,
                resolve_assignee=is_service_principal,
            )
            break
        except (CloudError, HttpResponseError) as ex:
            if isinstance(ex, ResourceExistsError) or "The role assignment already exists." in ex.message:
                break
            logger.info(ex.message)
        except Exception as ex:  # pylint: disable=broad-except
            logger.error(str(ex))
        time.sleep(delay + delay * x)
    else:
        return False
    hook.add(message="AAD role propagation done", value=1.0, total_val=1.0)
    logger.info("AAD role propagation done")
    return True


# TODO(fuming): remove this once dependency bumped to 2.47.0
def _add_role_assignment_executor_old(cmd, role, assignee, resource_group_name=None, scope=None, resolve_assignee=True):
    factory = get_auth_management_client(cmd.cli_ctx, scope)
    assignments_client = factory.role_assignments
    definitions_client = factory.role_definitions

    # FIXME: is this necessary?
    if assignments_client.config is None:
        raise AzCLIError("Assignments client config is undefined.")

    scope = build_role_scope(resource_group_name, scope, assignments_client.config.subscription_id)

    # XXX: if role is uuid, this function's output cannot be used as role assignment defintion id
    # ref: https://github.com/Azure/azure-cli/issues/2458
    role_id = resolve_role_id(role, scope, definitions_client)

    # If the cluster has service principal resolve the service principal client id to get the object id,
    # if not use MSI object id.
    object_id = resolve_object_id(cmd.cli_ctx, assignee) if resolve_assignee else assignee

    assignment_name = uuid.uuid4()
    custom_headers = None

    RoleAssignmentCreateParameters = get_sdk(
        cmd.cli_ctx,
        ResourceType.MGMT_AUTHORIZATION,
        "RoleAssignmentCreateParameters",
        mod="models",
        operation_group="role_assignments",
    )
    if cmd.supported_api_version(min_api="2018-01-01-preview", resource_type=ResourceType.MGMT_AUTHORIZATION):
        parameters = RoleAssignmentCreateParameters(role_definition_id=role_id, principal_id=object_id)
        return assignments_client.create(scope, assignment_name, parameters, custom_headers=custom_headers)

    # for backward compatibility
    RoleAssignmentProperties = get_sdk(
        cmd.cli_ctx,
        ResourceType.MGMT_AUTHORIZATION,
        "RoleAssignmentProperties",
        mod="models",
        operation_group="role_assignments",
    )
    properties = RoleAssignmentProperties(role_definition_id=role_id, principal_id=object_id)
    return assignments_client.create(scope, assignment_name, properties, custom_headers=custom_headers)


# TODO(fuming): remove this once dependency bumped to 2.47.0
def _add_role_assignment_old(cmd, role, service_principal_msi_id, is_service_principal=True, delay=2, scope=None):
    # AAD can have delays in propagating data, so sleep and retry
    hook = cmd.cli_ctx.get_progress_controller(True)
    hook.add(message="Waiting for AAD role to propagate", value=0, total_val=1.0)
    logger.info("Waiting for AAD role to propagate")
    for x in range(0, 10):
        hook.add(message="Waiting for AAD role to propagate", value=0.1 * x, total_val=1.0)
        try:
            # TODO: break this out into a shared utility library
            _add_role_assignment_executor_old(
                cmd,
                role,
                service_principal_msi_id,
                scope=scope,
                resolve_assignee=is_service_principal,
            )
            break
        except (CloudError, HttpResponseError) as ex:
            if ex.message == "The role assignment already exists.":
                break
            logger.info(ex.message)
        except Exception as ex:  # pylint: disable=broad-except
            logger.error(str(ex))
        time.sleep(delay + delay * x)
    else:
        return False
    hook.add(message="AAD role propagation done", value=1.0, total_val=1.0)
    logger.info("AAD role propagation done")
    return True
