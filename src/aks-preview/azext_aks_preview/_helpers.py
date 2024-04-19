# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import errno
import os
import platform
import re
import stat
import tempfile
from typing import TypeVar

import yaml
from azext_aks_preview._client_factory import (
    get_mc_snapshots_client,
    get_nodepool_snapshots_client,
)
from azure.cli.command_modules.acs._helpers import map_azure_error_to_cli_error
from azure.cli.command_modules.acs._validators import extract_comma_separated_string
from azure.cli.core.azclierror import (
    FileOperationError,
    InvalidArgumentValueError,
    ResourceNotFoundError,
)
from azure.core.exceptions import AzureError
from knack.log import get_logger
from knack.prompting import NoTTYException, prompt_y_n
from knack.util import CLIError

logger = get_logger(__name__)

# type variables
ManagedCluster = TypeVar("ManagedCluster")


def which(binary):
    path_var = os.getenv('PATH')
    if platform.system() == 'Windows':
        binary = binary + '.exe'
        parts = path_var.split(';')
    else:
        parts = path_var.split(':')

    for part in parts:
        bin_path = os.path.join(part, binary)
        if os.path.exists(bin_path) and os.path.isfile(bin_path) and os.access(bin_path, os.X_OK):
            return bin_path

    return None


def print_or_merge_credentials(path, kubeconfig, overwrite_existing, context_name):
    """Merge an unencrypted kubeconfig into the file at the specified path, or print it to
    stdout if the path is "-".
    """
    # Special case for printing to stdout
    if path == "-":
        print(kubeconfig)
        return

    # ensure that at least an empty ~/.kube/config exists
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except OSError as ex:
            if ex.errno != errno.EEXIST:
                raise
    if not os.path.exists(path):
        with os.fdopen(os.open(path, os.O_CREAT | os.O_WRONLY, 0o600), 'wt'):
            pass

    # merge the new kubeconfig into the existing one
    fd, temp_path = tempfile.mkstemp()
    additional_file = os.fdopen(fd, 'w+t')
    try:
        additional_file.write(kubeconfig)
        additional_file.flush()
        _merge_kubernetes_configurations(
            path, temp_path, overwrite_existing, context_name)
    except yaml.YAMLError as ex:
        logger.warning(
            'Failed to merge credentials to kube config file: %s', ex)
    finally:
        additional_file.close()
        os.remove(temp_path)


def _merge_kubernetes_configurations(existing_file, addition_file, replace, context_name=None):
    existing = _load_kubernetes_configuration(existing_file)
    addition = _load_kubernetes_configuration(addition_file)

    if context_name is not None:
        addition['contexts'][0]['name'] = context_name
        addition['contexts'][0]['context']['cluster'] = context_name
        addition['clusters'][0]['name'] = context_name
        addition['current-context'] = context_name

    # rename the admin context so it doesn't overwrite the user context
    for ctx in addition.get('contexts', []):
        try:
            if ctx['context']['user'].startswith('clusterAdmin'):
                admin_name = ctx['name'] + '-admin'
                addition['current-context'] = ctx['name'] = admin_name
                break
        except (KeyError, TypeError):
            continue

    if addition is None:
        raise CLIError(f'failed to load additional configuration from {addition_file}')

    if existing is None:
        existing = addition
    else:
        _handle_merge(existing, addition, 'clusters', replace)
        _handle_merge(existing, addition, 'users', replace)
        _handle_merge(existing, addition, 'contexts', replace)
        existing['current-context'] = addition['current-context']

    # check that ~/.kube/config is only read- and writable by its owner
    if platform.system() != "Windows" and not os.path.islink(existing_file):
        # pylint: disable=consider-using-f-string
        existing_file_perms = "{:o}".format(stat.S_IMODE(os.lstat(existing_file).st_mode))
        if not existing_file_perms.endswith("600"):
            logger.warning(
                '%s has permissions "%s".\nIt should be readable and writable only by its owner.',
                existing_file,
                existing_file_perms,
            )

    with open(existing_file, 'w+', encoding="utf-8") as stream:
        yaml.safe_dump(existing, stream, default_flow_style=False)

    current_context = addition.get('current-context', 'UNKNOWN')
    msg = f'Merged "{current_context}" as current context in {existing_file}'
    logger.warning(msg)


def _load_kubernetes_configuration(filename):
    try:
        with open(filename, encoding="utf-8") as stream:
            return yaml.safe_load(stream)
    except (IOError, OSError) as ex:
        if getattr(ex, 'errno', 0) == errno.ENOENT:
            raise CLIError(f'{filename} does not exist') from ex
        raise
    except (yaml.parser.ParserError, UnicodeDecodeError) as ex:
        raise CLIError(f'Error parsing {filename} ({str(ex)})') from ex


def _handle_merge(existing, addition, key, replace):
    if not addition.get(key, False):
        return
    if key not in existing:
        raise FileOperationError(
            f"No such key '{key}' in existing config, please confirm whether it is a valid config file. "
            "May back up this config file, delete it and retry the command."
        )
    if not existing.get(key):
        existing[key] = addition[key]
        return

    for i in addition[key]:
        for j in existing[key]:
            if not i.get('name', False) or not j.get('name', False):
                continue
            if i['name'] == j['name']:
                if replace or i == j:
                    existing[key].remove(j)
                else:
                    msg = 'A different object named {} already exists in your kubeconfig file.\nOverwrite?'
                    overwrite = False
                    try:
                        overwrite = prompt_y_n(msg.format(i['name']))
                    except NoTTYException:
                        pass
                    if overwrite:
                        existing[key].remove(j)
                    else:
                        msg = 'A different object named {} already exists in {} in your kubeconfig file.'
                        raise CLIError(msg.format(i['name'], key))
        existing[key].append(i)


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
            return similar_word(b, a)  # pylint: disable=arguments-out-of-order
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
        subscription_id = match.group(1)
        resource_group_name = match.group(2)
        snapshot_name = match.group(3)
        return get_nodepool_snapshot(cli_ctx, subscription_id, resource_group_name, snapshot_name)
    raise InvalidArgumentValueError(f"Cannot parse snapshot name from provided resource id '{snapshot_id}'.")


def get_nodepool_snapshot(cli_ctx, subscription_id, resource_group_name, snapshot_name):
    snapshot_client = get_nodepool_snapshots_client(cli_ctx, subscription_id=subscription_id)
    try:
        snapshot = snapshot_client.get(resource_group_name, snapshot_name)
    # track 2 sdk raise exception from azure.core.exceptions
    except AzureError as ex:
        if "not found" in ex.message:
            # pylint: disable=raise-missing-from
            raise ResourceNotFoundError(f"Snapshot '{snapshot_name}' not found.")
        raise map_azure_error_to_cli_error(ex) from ex
    return snapshot


def get_cluster_snapshot_by_snapshot_id(cli_ctx, snapshot_id):
    _re_mc_snapshot_resource_id = re.compile(
        r"/subscriptions/(.*?)/resourcegroups/(.*?)/providers/microsoft.containerservice/managedclustersnapshots/(.*)",
        flags=re.IGNORECASE,
    )
    snapshot_id = snapshot_id.lower()
    match = _re_mc_snapshot_resource_id.search(snapshot_id)
    if match:
        subscription_id = match.group(1)
        resource_group_name = match.group(2)
        snapshot_name = match.group(3)
        return get_cluster_snapshot(cli_ctx, subscription_id, resource_group_name, snapshot_name)
    raise InvalidArgumentValueError(
        f"Cannot parse snapshot name from provided resource id {snapshot_id}."
    )


def get_cluster_snapshot(cli_ctx, subscription_id, resource_group_name, snapshot_name):
    snapshot_client = get_mc_snapshots_client(cli_ctx, subscription_id)
    try:
        snapshot = snapshot_client.get(resource_group_name, snapshot_name)
    # track 2 sdk raise exception from azure.core.exceptions
    except AzureError as ex:
        if "not found" in ex.message:
            # pylint: disable=raise-missing-from
            raise ResourceNotFoundError(f"Managed cluster snapshot '{snapshot_name}' not found.")
        raise map_azure_error_to_cli_error(ex) from ex
    return snapshot


def check_is_private_link_cluster(mc: ManagedCluster) -> bool:
    """Check `mc` object to determine whether private link cluster is enabled.
    :return: bool
    """
    return check_is_private_cluster(mc) and not check_is_apiserver_vnet_integration_cluster(mc)


def check_is_private_cluster(mc: ManagedCluster) -> bool:
    """Check `mc` object to determine whether private cluster is enabled.
    :return: bool
    """
    if mc and mc.api_server_access_profile:
        return bool(mc.api_server_access_profile.enable_private_cluster)
    return False


def check_is_apiserver_vnet_integration_cluster(mc: ManagedCluster) -> bool:
    """Check `mc` object to determine whether apiserver vnet integration is enabled.
    :return: bool
    """
    if mc and mc.api_server_access_profile:
        return bool(mc.api_server_access_profile.enable_vnet_integration)
    return False


def setup_common_safeguards_profile(level, version, excludedNamespaces, mc: ManagedCluster, models) -> ManagedCluster:
    if (level is not None or version is not None or excludedNamespaces is not None) and mc.safeguards_profile is None:
        mc.safeguards_profile = models.SafeguardsProfile(
            level=level,
            version=version
        )
    # replace values with provided values
    if excludedNamespaces is not None:
        mc.safeguards_profile.excluded_namespaces = extract_comma_separated_string(
            excludedNamespaces, enable_strip=True, keep_none=True, default_value=[])

    return mc


def process_message_for_run_command(message):
    result = message.split("\n")
    if result[-2] != "[stderr]":
        raise CLIError("Error: " + result[-2])

    for line in result[2:len(result) - 2]:
        print(line)
