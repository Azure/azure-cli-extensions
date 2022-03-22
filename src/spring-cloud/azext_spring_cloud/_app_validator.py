# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-few-public-methods, unused-argument, redefined-builtin
from knack.log import get_logger
from azure.cli.core.azclierror import InvalidArgumentValueError
from msrestazure.azure_exceptions import CloudError
from azure.core.exceptions import (ResourceNotFoundError)
from azure.mgmt.core.tools import is_valid_resource_id
from ._resource_quantity import (validate_cpu as validate_cpu_value, validate_memory as validate_memory_value)
from ._client_factory import cf_spring_cloud_20220101preview


logger = get_logger(__name__)


# pylint: disable=line-too-long,raise-missing-from
NO_PRODUCTION_DEPLOYMENT_ERROR = "No production deployment found, use --deployment to specify deployment or create deployment with: az spring-cloud app deployment create"
NO_PRODUCTION_DEPLOYMENT_SET_ERROR = "This app has no production deployment, use \"az spring-cloud app deployment create\" to create a deployment and \"az spring-cloud app set-deployment\" to set production deployment."
OBSOLETE_APP_IDENTITY_REMOVE = "Remove managed identities without \"system-assigned\" or \"user-assigned\" parameters is obsolete, will only remove system-assigned managed identity, and will not be supported in the future."
WARNING_NO_USER_IDENTITY_RESOURCE_ID = "No resource ID of user-assigned managed identity is given for parameter \"user-assigned\", will remove ALL user-assigned managed identities."
OBSOLETE_APP_IDENTITY_ASSIGN = "Assign managed identities without \"system-assigned\" or \"user-assigned\" parameters is obsolete, will only enable system-assigned managed identity, and will not be supported in the future."

def fulfill_deployment_param(cmd, namespace):
    client = cf_spring_cloud_20220101preview(cmd.cli_ctx)
    name = _get_app_name_from_namespace(namespace)
    if not name or not namespace.service or not namespace.resource_group:
        return
    if namespace.deployment:
        namespace.deployment = _ensure_deployment_exist(client, namespace.resource_group, namespace.service, name, namespace.deployment)
    else:
        namespace.deployment = _ensure_active_deployment_exist_and_get(client, namespace.resource_group, namespace.service, name)


def fulfill_deployment_param_or_warning(cmd, namespace):
    client = cf_spring_cloud_20220101preview(cmd.cli_ctx)
    name = _get_app_name_from_namespace(namespace)
    if not name or not namespace.service or not namespace.resource_group:
        return
    if namespace.deployment:
        namespace.deployment = _ensure_deployment_exist(client, namespace.resource_group, namespace.service, name, namespace.deployment)
    else:
        namespace.deployment = _get_active_deployment(client, namespace.resource_group, namespace.service, name)
        if not namespace.deployment:
            logger.warning(NO_PRODUCTION_DEPLOYMENT_SET_ERROR)


def active_deployment_exist(cmd, namespace):
    name = _get_app_name_from_namespace(namespace)
    if not name or not namespace.service or not namespace.resource_group:
        return
    client = cf_spring_cloud_20220101preview(cmd.cli_ctx)
    deployment = _get_active_deployment(client, namespace.resource_group, namespace.service, name)
    if not deployment:
        raise InvalidArgumentValueError(NO_PRODUCTION_DEPLOYMENT_SET_ERROR)


def active_deployment_exist_or_warning(cmd, namespace):
    name = _get_app_name_from_namespace(namespace)
    if not name or not namespace.service or not namespace.resource_group:
        return
    client = cf_spring_cloud_20220101preview(cmd.cli_ctx)
    deployment = _get_active_deployment(client, namespace.resource_group, namespace.service, name)
    if not deployment:
        logger.warning(NO_PRODUCTION_DEPLOYMENT_SET_ERROR)


def ensure_not_active_deployment(cmd, namespace):
    """
    Validate namespace.deployment is not active
    """
    if not namespace.deployment or not namespace.resource_group or not namespace.service or not namespace.name:
        return
    client = cf_spring_cloud_20220101preview(cmd.cli_ctx)
    deployment = _ensure_deployment_exist(client, namespace.resource_group, namespace.service, namespace.name, namespace.deployment)
    if deployment.properties.active:
        raise InvalidArgumentValueError('Deployment {} is already the production deployment'.format(deployment.name))


def _ensure_deployment_exist(client, resource_group, service, app, deployment):
    try:
        return client.deployments.get(resource_group, service, app, deployment)
    except CloudError:
        raise InvalidArgumentValueError('Deployment {} not found under app {}'.format(deployment, app))


def _ensure_active_deployment_exist_and_get(client, resource_group, service, name):
    deployment_resource = _get_active_deployment(client, resource_group, service, name)
    if not deployment_resource:
        raise InvalidArgumentValueError(NO_PRODUCTION_DEPLOYMENT_ERROR)
    return deployment_resource


def _get_active_deployment(client, resource_group, service, name):
    try:
        deployments = client.deployments.list(resource_group, service, name)
        return next(iter(x for x in deployments if x.properties.active), None)
    except ResourceNotFoundError:
        raise InvalidArgumentValueError('App {} not found'.format(name))


def validate_deloy_path(namespace):
    arguments = [namespace.artifact_path, namespace.source_path, namespace.container_image]
    if all(not x for x in arguments):
        raise InvalidArgumentValueError('One of --artifact-path, --source-path, --container-image must be provided.')
    _deploy_path_mutual_exclusive(arguments)


def validate_deloyment_create_path(namespace):
    arguments = [namespace.artifact_path, namespace.source_path, namespace.container_image]
    _deploy_path_mutual_exclusive(arguments)


def _deploy_path_mutual_exclusive(args):
    valued_args = [x for x in args if x]
    if len(valued_args) > 1:
        raise InvalidArgumentValueError('At most one of --artifact-path, --source-path, --container-image must be provided.')


def validate_cpu(namespace):
    namespace.cpu = validate_cpu_value(namespace.cpu)


def validate_memory(namespace):
    namespace.memory = validate_memory_value(namespace.memory)


def _get_app_name_from_namespace(namespace):
    if hasattr(namespace, 'app'):
        return namespace.app
    elif hasattr(namespace, 'name'):
        return namespace.name
    return None


def validate_app_identity_remove_or_warning(namespace):
    if namespace.system_assigned is None and namespace.user_assigned is None:
        logger.warning(OBSOLETE_APP_IDENTITY_REMOVE)
    if namespace.user_assigned is not None:
        if not isinstance(namespace.user_assigned, list):
            raise InvalidArgumentValueError("Parameter value for \"user-assigned\" should be empty or a list of space-separated managed identity resource ID.")
        if len(namespace.user_assigned) == 0:
            logger.warning(WARNING_NO_USER_IDENTITY_RESOURCE_ID)
        namespace.user_assigned = _normalized_user_identitiy_resource_id_list(namespace.user_assigned)
        for resource_id in namespace.user_assigned:
            is_valid = _is_valid_user_assigned_managed_identity_resource_id(resource_id)
            if not is_valid:
                raise InvalidArgumentValueError("Invalid user-assigned managed identity resource ID \"{}\".".format(resource_id))


def _normalized_user_identitiy_resource_id_list(user_identity_resource_id_list):
    result = []
    if not user_identity_resource_id_list:
        return result
    for id in user_identity_resource_id_list:
        result.append(id.strip().lower())
    return result


def _is_valid_user_assigned_managed_identity_resource_id(resource_id):
    if not is_valid_resource_id(resource_id.lower()):
        return False
    if "/providers/Microsoft.ManagedIdentity/userAssignedIdentities/".lower() not in resource_id.lower():
        return False
    return True


def validate_app_identity_assign_or_warning(namespace):
    _warn_if_no_identity_type_params(namespace)
    _validate_role_and_scope_should_use_together(namespace)
    _validate_role_and_scope_should_not_use_with_user_identity(namespace)
    _validate_user_identity_resource_id(namespace)
    _normalize_user_identity_resource_id(namespace)


def _warn_if_no_identity_type_params(namespace):
    if namespace.system_assigned is None and namespace.user_assigned is None:
        logger.warning(OBSOLETE_APP_IDENTITY_ASSIGN)


def _validate_role_and_scope_should_use_together(namespace):
    if _has_role_or_scope(namespace) and not _has_role_and_scope(namespace):
        raise InvalidArgumentValueError("Parameter \"role\" and \"scope\" should be used together.")


def _validate_role_and_scope_should_not_use_with_user_identity(namespace):
    if _has_role_and_scope(namespace) and _only_has_user_assigned(namespace):
        raise InvalidArgumentValueError("Invalid to use parameter \"role\" and \"scope\" with \"user-assigned\" parameter.")


def _has_role_and_scope(namespace):
    return namespace.role and namespace.scope


def _has_role_or_scope(namespace):
    return namespace.role or namespace.scope


def _only_has_user_assigned(namespace):
    return (namespace.user_assigned) and (not namespace.system_assigned)


def _validate_user_identity_resource_id(namespace):
    if namespace.user_assigned:
        for resource_id in namespace.user_assigned:
            if not _is_valid_user_assigned_managed_identity_resource_id(resource_id):
                raise InvalidArgumentValueError("Invalid user-assigned managed identity resource ID \"{}\".".format(resource_id))


def _normalize_user_identity_resource_id(namespace):
    if namespace.user_assigned:
        namespace.user_assigned = _normalized_user_identitiy_resource_id_list(namespace.user_assigned)


def validate_create_app_with_user_identity_or_warning(namespace):
    _validate_user_identity_resource_id(namespace)
    _normalize_user_identity_resource_id(namespace)


def validate_create_app_with_system_identity_or_warning(namespace):
    if namespace.system_assigned is not None and namespace.assign_identity is not None:
        raise InvalidArgumentValueError('Parameter "system-assigned" should not use together with "assign-identity".')
