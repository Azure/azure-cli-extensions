# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

from azure.cli.core.util import sdk_no_wait, user_confirmation


def _get_identity_dict(cluster):
    """Extract the identity dict from a cluster resource."""
    try:
        return cluster["identity"] or {}
    except KeyError:
        return {}


def _get_user_assigned_identities(cluster):
    """Extract userAssignedIdentities from cluster identity."""
    identity = _get_identity_dict(cluster)
    return identity.get("userAssignedIdentities") or {}


def horizondb_identity_assign(client, resource_group_name, cluster_name, identity, no_wait=False):
    cluster = client.get(resource_group_name=resource_group_name, cluster_name=cluster_name)
    current_identities = _get_user_assigned_identities(cluster)

    for identity_id in identity:
        current_identities[identity_id] = {}

    patch_body = {
        "identity": {
            "type": "UserAssigned",
            "userAssignedIdentities": current_identities
        }
    }

    return sdk_no_wait(no_wait, client.begin_update,
                       resource_group_name=resource_group_name,
                       cluster_name=cluster_name,
                       properties=patch_body)


def horizondb_identity_list(client, resource_group_name, cluster_name):
    cluster = client.get(resource_group_name=resource_group_name, cluster_name=cluster_name)
    return _get_user_assigned_identities(cluster)


def horizondb_identity_remove(cmd, client, resource_group_name, cluster_name, identity, no_wait=False, yes=False):
    if not yes:
        user_confirmation(
            "Are you sure you want to remove the specified identities from cluster '{0}' "
            "in resource group '{1}'".format(cluster_name, resource_group_name), yes=yes)

    cluster = client.get(resource_group_name=resource_group_name, cluster_name=cluster_name)
    current_identities = _get_user_assigned_identities(cluster)

    identities_to_remove = {identity_id: None for identity_id in identity}

    remaining = {k: v for k, v in current_identities.items() if k not in identities_to_remove}

    patch_body = {
        "identity": {
            "type": "UserAssigned" if remaining else "None",
            "userAssignedIdentities": identities_to_remove
        }
    }

    return sdk_no_wait(no_wait, client.begin_update,
                       resource_group_name=resource_group_name,
                       cluster_name=cluster_name,
                       properties=patch_body)


def horizondb_identity_show(client, resource_group_name, cluster_name, identity):
    cluster = client.get(resource_group_name=resource_group_name, cluster_name=cluster_name)
    user_assigned = _get_user_assigned_identities(cluster)

    if identity not in user_assigned:
        from azure.cli.core.azclierror import ResourceNotFoundError
        raise ResourceNotFoundError(
            "Identity '{}' not found on cluster '{}'.".format(identity, cluster_name))

    return {identity: user_assigned[identity]}
