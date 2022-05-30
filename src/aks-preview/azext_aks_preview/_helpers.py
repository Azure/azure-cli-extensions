# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import re

from azure.cli.command_modules.acs._helpers import map_azure_error_to_cli_error
from azure.cli.core.azclierror import InvalidArgumentValueError, ResourceNotFoundError
from azure.core.exceptions import AzureError

from azext_aks_preview._client_factory import cf_nodepool_snapshots, cf_mc_snapshots
from azext_aks_preview._consts import CONST_CONTAINER_NAME_MAX_LENGTH


def _trim_fqdn_name_containing_hcp(normalized_fqdn: str) -> str:
    """
    Trims the storage blob name and takes everything prior to "-hcp-".
    Currently it is displayed wrong: i.e. at time of creation cli has
    following limitation:
    https://docs.microsoft.com/en-us/azure/azure-resource-manager/templates/
    error-storage-account-name

    :param normalized_fqdn: storage blob name
    :return: storage_name_without_hcp: Storage name without the hcp value
    attached
    """
    storage_name_without_hcp, _, _ = normalized_fqdn.partition('-hcp-')
    if len(storage_name_without_hcp) > CONST_CONTAINER_NAME_MAX_LENGTH:
        storage_name_without_hcp = storage_name_without_hcp[:CONST_CONTAINER_NAME_MAX_LENGTH]
    return storage_name_without_hcp.rstrip('-')


def _fuzzy_match(query, arr):
    """
    will compare all elements in @arr against the @query to see if they are similar

    similar implies one is a substring of the other or the two words are 1 change apart

    Ex. bird and bord are similar
    Ex. bird and birdwaj are similar
    Ex. bird and bead are not similar
    """
    def similar_word(a, b):
        a_len = len(a)
        b_len = len(b)
        if a_len > b_len:  # @a should always be the shorter string
            return similar_word(b, a)
        if a in b:
            return True
        if b_len - a_len > 1:
            return False
        i = 0
        j = 0
        found_difference = False
        while i < a_len:
            if a[i] != b[j]:
                if found_difference:
                    return False
                found_difference = True
                if a_len == b_len:
                    i += 1
                j += 1
            else:
                i += 1
                j += 1
        return True

    matches = []

    for word in arr:
        if similar_word(query, word):
            matches.append(word)

    return matches


def get_nodepool_snapshot_by_snapshot_id(cli_ctx, snapshot_id):
    _re_snapshot_resource_id = re.compile(
        r"/subscriptions/(.*?)/resourcegroups/(.*?)/providers/microsoft.containerservice/snapshots/(.*)",
        flags=re.IGNORECASE,
    )
    snapshot_id = snapshot_id.lower()
    match = _re_snapshot_resource_id.search(snapshot_id)
    if match:
        resource_group_name = match.group(2)
        snapshot_name = match.group(3)
        return get_nodepool_snapshot(cli_ctx, resource_group_name, snapshot_name)
    raise InvalidArgumentValueError("Cannot parse snapshot name from provided resource id '{}'.".format(snapshot_id))


def get_nodepool_snapshot(cli_ctx, resource_group_name, snapshot_name):
    snapshot_client = cf_nodepool_snapshots(cli_ctx)
    try:
        snapshot = snapshot_client.get(resource_group_name, snapshot_name)
    # track 2 sdk raise exception from azure.core.exceptions
    except AzureError as ex:
        if "not found" in ex.message:
            raise ResourceNotFoundError("Snapshot '{}' not found.".format(snapshot_name))
        raise map_azure_error_to_cli_error(ex)
    return snapshot


def get_cluster_snapshot_by_snapshot_id(cli_ctx, snapshot_id):
    _re_mc_snapshot_resource_id = re.compile(
        r"/subscriptions/(.*?)/resourcegroups/(.*?)/providers/microsoft.containerservice/managedclustersnapshots/(.*)",
        flags=re.IGNORECASE,
    )
    snapshot_id = snapshot_id.lower()
    match = _re_mc_snapshot_resource_id.search(snapshot_id)
    if match:
        resource_group_name = match.group(2)
        snapshot_name = match.group(3)
        return get_cluster_snapshot(cli_ctx, resource_group_name, snapshot_name)
    raise InvalidArgumentValueError(
        "Cannot parse snapshot name from provided resource id {}.".format(snapshot_id))


def get_cluster_snapshot(cli_ctx, resource_group_name, snapshot_name):
    snapshot_client = cf_mc_snapshots(cli_ctx)
    try:
        snapshot = snapshot_client.get(resource_group_name, snapshot_name)
    # track 2 sdk raise exception from azure.core.exceptions
    except AzureError as ex:
        if "not found" in ex.message:
            raise ResourceNotFoundError("Managed cluster snapshot '{}' not found.".format(snapshot_name))
        raise map_azure_error_to_cli_error(ex)
    return snapshot
