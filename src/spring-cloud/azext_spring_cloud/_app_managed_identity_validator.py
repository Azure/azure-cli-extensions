# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.mgmt.core.tools import is_valid_resource_id
from knack.log import get_logger


logger = get_logger(__name__)


OBSOLETE_APP_IDENTITY_REMOVE = "Remove managed identities without \"system-assigned\" or \"user-assigned\" parameters is obsolete, will only remove system-assigned managed identity, and will not be supported in a future release."
WARNING_NO_USER_IDENTITY_RESOURCE_ID = "No resource ID of user-assigned managed identity is given for parameter \"user-assigned\", will remove ALL user-assigned managed identities."
OBSOLETE_APP_IDENTITY_ASSIGN = "Assign managed identities without \"system-assigned\" or \"user-assigned\" parameters is obsolete, will only enable system-assigned managed identity, and will not be supported in a future release."
ENABLE_LOWER = "enable"
DISABLE_LOWER = "disable"


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
    """
    Note: assign_identity is deprecated, use system_assigned instead.
    """
    if namespace.system_assigned is not None and namespace.assign_identity is not None:
        raise InvalidArgumentValueError('Parameter "system-assigned" should not use together with "assign-identity".')
    if namespace.assign_identity is not None:
        namespace.system_assigned = namespace.assign_identity


def validate_app_force_set_system_identity_or_warning(namespace):
    if namespace.system_assigned is None:
        raise InvalidArgumentValueError('Parameter "system-assigned" expected at least one argument.')
    namespace.system_assigned = namespace.system_assigned.strip().lower()
    if namespace.system_assigned.strip().lower() not in (ENABLE_LOWER, DISABLE_LOWER):
        raise InvalidArgumentValueError('Allowed values for "system-assigned" are: {}, {}.'.format(ENABLE_LOWER, DISABLE_LOWER))


def validate_app_force_set_user_identity_or_warning(namespace):
    if namespace.user_assigned is None or len(namespace.user_assigned) == 0:
        raise InvalidArgumentValueError('Parameter "user-assigned" expected at least one argument.')
    if len(namespace.user_assigned) == 1:
        single_element = namespace.user_assigned[0].strip().lower()
        if single_element != DISABLE_LOWER and not _is_valid_user_assigned_managed_identity_resource_id(single_element):
            raise InvalidArgumentValueError('Allowed values for "user-assigned" are: {}, space-separated user-assigned managed identity resource IDs.'.format(DISABLE_LOWER))
        elif single_element == DISABLE_LOWER:
            namespace.user_assigned = [DISABLE_LOWER]
        else:
            _normalize_user_identity_resource_id(namespace)
    else:
        _validate_user_identity_resource_id(namespace)
        _normalize_user_identity_resource_id(namespace)
