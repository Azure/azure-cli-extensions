# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Local validation for Cosmos DB database/container recovery.

Logical database/container names are case-sensitive. ARM identity/resource IDs are
not. Keep this validation separate from the shared Blob, AKS and Elastic SAN paths.
"""

import re
import unicodedata

from azure.cli.core.azclierror import (
    InvalidArgumentValueError,
    MutuallyExclusiveArgumentError,
    RequiredArgumentMissingError,
)


def reject_unsupported_options(**options):
    unsupported = ['--' + name.replace('_', '-') for name, value in options.items() if value is not None]
    if unsupported:
        raise InvalidArgumentValueError(
            'AzureCosmosDB restore does not support {}.'.format(', '.join(unsupported)))


def validate_resource_identifiers(resource_identifiers):
    """Validate an ordered JSON list without normalizing or expanding names."""
    if resource_identifiers is None:
        raise RequiredArgumentMissingError(
            '--resource-identifiers is required for AzureCosmosDB. Specify database or database/container names.')
    if not isinstance(resource_identifiers, list) or not 1 <= len(resource_identifiers) <= 50:
        raise InvalidArgumentValueError(
            'AzureCosmosDB --resource-identifiers must be a list of 1 to 50 database or database/container names.')

    seen = set()
    databases = set()
    for identifier in resource_identifiers:
        if not isinstance(identifier, str) or not identifier.strip():
            raise InvalidArgumentValueError('Each Cosmos DB resource identifier must be a nonblank string.')
        segments = identifier.split('/')
        if (len(segments) > 2 or any(not segment.strip() for segment in segments) or
                any(char in '\\?#' or unicodedata.category(char) == 'Cc' for char in identifier)):
            raise InvalidArgumentValueError(
                'Cosmos DB resource identifiers must be database or database/container names, '
                'without empty segments, backslashes, ?, # or control characters.')
        if identifier in seen:
            raise InvalidArgumentValueError('Cosmos DB resource identifiers must not contain exact duplicates.')
        seen.add(identifier)
        if len(segments) == 1:
            databases.add(identifier)

    if any('/' in identifier and identifier.split('/')[0] in databases for identifier in resource_identifiers):
        raise InvalidArgumentValueError('Select a Cosmos DB database or its containers, not both.')
    return list(resource_identifiers)


def get_restore_configuration(resource_identifiers):
    return {
        'object_type': 'GenericRestoreDatasourceCriteria',
        'resource_selectors': {
            'object_type': 'ResourceListSelectionCriteria',
            'resource_identifiers': validate_resource_identifiers(resource_identifiers),
        },
    }


def _normalize_keys(value, key_pairs, description):
    """Copy only known schema aliases; never recurse into caller-owned maps."""
    if not isinstance(value, dict):
        raise InvalidArgumentValueError('{} must be a JSON object.'.format(description))
    result = dict(value)
    for client_key, wire_key in key_pairs.items():
        if wire_key in result:
            if client_key in result:
                raise InvalidArgumentValueError(
                    '{} cannot contain both {} and {}.'.format(description, client_key, wire_key))
            result[client_key] = result.pop(wire_key)
    return result


def validate_restore_configuration(restore_configuration):
    if restore_configuration is None:
        raise RequiredArgumentMissingError(
            '--restore-configuration is required for AzureCosmosDB item recovery. '
            'Use backup-instance initialize-restoreconfig --resource-identifiers.')
    config = _normalize_keys(restore_configuration, {
        'object_type': 'objectType', 'resource_selectors': 'resourceSelectors',
    }, 'Cosmos DB restore configuration')
    if (set(config) != {'object_type', 'resource_selectors'} or
            config.get('object_type') != 'GenericRestoreDatasourceCriteria'):
        raise InvalidArgumentValueError(
            'Cosmos DB restore configuration must contain one GenericRestoreDatasourceCriteria object.')
    selectors = _normalize_keys(config['resource_selectors'], {
        'object_type': 'objectType', 'resource_identifiers': 'resourceIdentifiers',
        'resource_name_overrides': 'resourceNameOverrides',
    }, 'Cosmos DB resource selectors')
    if (set(selectors) - {'object_type', 'resource_identifiers', 'resource_name_overrides'} or
            selectors.get('object_type') != 'ResourceListSelectionCriteria'):
        raise InvalidArgumentValueError('Cosmos DB restore requires ResourceListSelectionCriteria.')
    if 'resource_name_overrides' in selectors:
        overrides = selectors['resource_name_overrides']
        if overrides is not None and (not isinstance(overrides, dict) or overrides):
            raise InvalidArgumentValueError('Cosmos DB restore does not support resource name overrides.')
    return get_restore_configuration(selectors.get('resource_identifiers'))


def _validate_arm_id(value, provider, resource_type, option):
    subscription = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
    pattern = (r'/subscriptions/' + subscription + r'/resourceGroups/([^/]+)/providers/' +
               re.escape(provider) + '/' + re.escape(resource_type) + r'/([^/]+)')
    match = re.fullmatch(pattern, value, re.IGNORECASE) if isinstance(value, str) else None
    if (match is None or any(not segment.strip() for segment in match.groups()) or
            any(char in '\\?#' or unicodedata.category(char) == 'Cc' for char in value)):
        raise InvalidArgumentValueError(
            '{} must be an account-level ARM ID for {}/{}.'.format(option, provider, resource_type))


def validate_restore_target(target_resource_id, backup_instance_id=None):
    if backup_instance_id is not None:
        raise InvalidArgumentValueError(
            'AzureCosmosDB item recovery supports alternate-location restore only. '
            'Use --target-resource-id for an existing, empty NoSQL account, not --backup-instance-id.')
    if target_resource_id is None:
        raise RequiredArgumentMissingError(
            '--target-resource-id is required for AzureCosmosDB item recovery; '
            'specify an existing, empty NoSQL account.')
    _validate_arm_id(target_resource_id, 'Microsoft.DocumentDB', 'databaseAccounts', '--target-resource-id')


def get_restore_identity_details(use_system_assigned_identity, user_assigned_identity_arm_url):
    if use_system_assigned_identity is not None and not isinstance(use_system_assigned_identity, bool):
        raise InvalidArgumentValueError('--mi-system-assigned must be true or false for AzureCosmosDB.')
    if user_assigned_identity_arm_url is not None:
        _validate_arm_id(user_assigned_identity_arm_url, 'Microsoft.ManagedIdentity',
                         'userAssignedIdentities', '--uami')
        if use_system_assigned_identity:
            raise MutuallyExclusiveArgumentError('--mi-system-assigned true cannot be combined with --uami.')
        # Retain the existing CLI convention: a UAMI alone implies system-assigned false.
        return {'useSystemAssignedIdentity': False, 'userAssignedIdentityArmUrl': user_assigned_identity_arm_url}
    if use_system_assigned_identity is False:
        raise RequiredArgumentMissingError('--uami is required when --mi-system-assigned is false for AzureCosmosDB.')
    if use_system_assigned_identity:
        return {'useSystemAssignedIdentity': True}
    return None


def prepare_restore_permissions(restore_request, user_assigned_identity_arm_url):
    """Normalize the supported Cosmos client/wire shape and reconcile identity.

    This does not contact Azure, enumerate source resources, or mutate the request.
    Only schema members consumed by the permission helper are normalized.
    """
    request = _normalize_keys(restore_request, {
        'object_type': 'objectType', 'restore_target_info': 'restoreTargetInfo',
        'identity_details': 'identityDetails',
    }, '--restore-request-object')
    target = _normalize_keys(request.get('restore_target_info'), {
        'object_type': 'objectType', 'datasource_info': 'datasourceInfo',
    }, 'Cosmos DB restore target')
    datasource = _normalize_keys(target.get('datasource_info'), {
        'datasource_type': 'datasourceType', 'resource_id': 'resourceID',
        'resource_name': 'resourceName',
    }, 'Cosmos DB restore datasource')
    if datasource.get('datasource_type') != 'Microsoft.DocumentDB/databaseAccounts':
        raise InvalidArgumentValueError('--restore-request-object is not compatible with AzureCosmosDB.')
    validate_restore_target(datasource.get('resource_id'))
    target['datasource_info'] = datasource
    request['restore_target_info'] = target

    # Validate an explicitly supplied permission flag, including empty/whitespace IDs.
    if user_assigned_identity_arm_url is not None:
        get_restore_identity_details(None, user_assigned_identity_arm_url)
    if 'identity_details' in request:
        identity = _normalize_keys(request['identity_details'], {
            'use_system_assigned_identity': 'useSystemAssignedIdentity',
            'user_assigned_identity_arm_url': 'userAssignedIdentityArmUrl',
        }, 'Cosmos DB restore identity')
        if set(identity) - {'use_system_assigned_identity', 'user_assigned_identity_arm_url'}:
            raise InvalidArgumentValueError('Cosmos DB restore identity contains unsupported fields.')
        # CLI flags may infer false from a lone UAMI, but an existing request
        # must already express the same identity on the actual restore wire.
        if not isinstance(identity.get('use_system_assigned_identity'), bool):
            raise InvalidArgumentValueError(
                'Cosmos DB restore identity must explicitly set useSystemAssignedIdentity to true or false.')
        if 'user_assigned_identity_arm_url' in identity and identity['user_assigned_identity_arm_url'] is None:
            raise InvalidArgumentValueError(
                'Cosmos DB restore identity cannot contain a null userAssignedIdentityArmUrl.')
        details = get_restore_identity_details(identity.get('use_system_assigned_identity'),
                                               identity.get('user_assigned_identity_arm_url'))
        if details is None:
            raise InvalidArgumentValueError(
                'Cosmos DB restore identity must select a system or user-assigned identity.')
        requested_uami = details.get('userAssignedIdentityArmUrl')
        if user_assigned_identity_arm_url is not None and (
                requested_uami is None or requested_uami.casefold() != user_assigned_identity_arm_url.casefold()):
            raise InvalidArgumentValueError('--uami must match the identity selected in --restore-request-object.')
        user_assigned_identity_arm_url = requested_uami
    return request, user_assigned_identity_arm_url


def get_vault_identity(backup_vault, user_assigned_identity_arm_url):
    """Resolve exactly the selected attached identity, without SAMI fallback."""
    if not isinstance(backup_vault, dict):
        raise InvalidArgumentValueError('The backup vault must contain a managed identity.')
    identity = _normalize_keys(backup_vault.get('identity'), {
        'principal_id': 'principalId', 'user_assigned_identities': 'userAssignedIdentities',
    }, 'Backup vault identity')
    identity_type = identity.get('type')
    types = identity_type.replace(' ', '').split(',') if isinstance(identity_type, str) else []
    if user_assigned_identity_arm_url is not None:
        if 'UserAssigned' not in types:
            raise InvalidArgumentValueError('The selected user-assigned identity is not attached to the backup vault.')
        attached = identity.get('user_assigned_identities')
        if not isinstance(attached, dict):
            raise InvalidArgumentValueError('The backup vault has no usable attached user-assigned identities.')
        matches = [value for key, value in attached.items()
                   if isinstance(key, str) and key.casefold() == user_assigned_identity_arm_url.casefold()]
        if len(matches) != 1:
            raise InvalidArgumentValueError(
                'The selected user-assigned identity must match exactly one vault attachment.')
        selected = _normalize_keys(matches[0], {'principal_id': 'principalId'}, 'Selected vault identity')
        principal_id = selected.get('principal_id')
    else:
        if 'SystemAssigned' not in types:
            raise InvalidArgumentValueError('The backup vault does not have a system-assigned identity.')
        principal_id = identity.get('principal_id')
    if not isinstance(principal_id, str) or not principal_id.strip():
        raise InvalidArgumentValueError('The selected backup vault identity does not have a principal ID.')
    return principal_id