# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import datetime
import json
import os
import subprocess
import tempfile
import time
from enum import Flag, auto

import colorama
from azext_aks_preview._client_factory import cf_agent_pools, get_storage_client
from azext_aks_preview._consts import (
    CONST_CONTAINER_NAME_MAX_LENGTH,
    CONST_PERISCOPE_CONTAINER_REGISTRY,
    CONST_PERISCOPE_IMAGE_VERSION,
    CONST_PERISCOPE_NAMESPACE,
    CONST_PERISCOPE_RELEASE_TAG,
    CONST_PERISCOPE_REPO_ORG,
)
from azext_aks_preview._helpers import print_or_merge_credentials, which
from azure.cli.command_modules.acs._params import _get_default_install_location
from azure.cli.command_modules.acs.custom import k8s_install_kubelogin
from azure.cli.core.commands.client_factory import (
    get_mgmt_service_client,
    get_subscription_id,
)
from knack.log import get_logger
from knack.prompting import prompt_y_n
from knack.util import CLIError
from msrestazure.azure_exceptions import CloudError
from packaging import version
from tabulate import tabulate

logger = get_logger(__name__)


class ClusterFeatures(Flag):
    NONE = 0
    WIN_HPC = auto()


# pylint: disable=line-too-long
def aks_kollect_cmd(cmd,    # pylint: disable=too-many-statements,too-many-locals
                    client,
                    resource_group_name: str,
                    name: str,
                    storage_account: str,
                    sas_token: str,
                    container_logs: str,
                    kube_objects: str,
                    node_logs: str,
                    node_logs_windows: str) -> None:
    colorama.init()

    mc = client.get(resource_group_name, name)

    if not which('kubectl'):
        raise CLIError('Can not find kubectl executable in PATH')

    storage_account_id = None
    if storage_account is None:
        print("No storage account specified. Try getting storage account from diagnostic settings")
        storage_account_id = _get_storage_account_from_diag_settings(
            cmd.cli_ctx, resource_group_name, name)
        if storage_account_id is None:
            raise CLIError(
                "A storage account must be specified, since there isn't one in the diagnostic settings.")

    from msrestazure.tools import (is_valid_resource_id, parse_resource_id,
                                   resource_id)
    if storage_account_id is None:
        if not is_valid_resource_id(storage_account):
            storage_account_id = resource_id(
                subscription=get_subscription_id(cmd.cli_ctx),
                resource_group=resource_group_name,
                namespace='Microsoft.Storage', type='storageAccounts',
                name=storage_account
            )
        else:
            storage_account_id = storage_account

    if is_valid_resource_id(storage_account_id):
        try:
            parsed_storage_account = parse_resource_id(storage_account_id)
        except CloudError as ex:
            raise CLIError(ex.message) from ex
    else:
        raise CLIError(f"Invalid storage account id {storage_account_id}")

    storage_account_name = parsed_storage_account['name']

    readonly_sas_token = None
    if sas_token is None:
        storage_client = get_storage_client(
            cmd.cli_ctx, parsed_storage_account['subscription'])
        storage_account_keys = storage_client.storage_accounts.list_keys(parsed_storage_account['resource_group'],
                                                                         storage_account_name)
        kwargs = {
            'account_name': storage_account_name,
            'account_key': storage_account_keys.keys[0].value
        }
        cloud_storage_client = _cloud_storage_account_service_factory(
            cmd.cli_ctx, kwargs)

        sas_token = cloud_storage_client.generate_shared_access_signature(
            'b',
            'sco',
            'rwdlacup',
            datetime.datetime.utcnow() + datetime.timedelta(days=1))

        readonly_sas_token = cloud_storage_client.generate_shared_access_signature(
            'b',
            'sco',
            'rl',
            datetime.datetime.utcnow() + datetime.timedelta(days=1))

        readonly_sas_token = readonly_sas_token.strip('?')

    print()
    print('This will deploy a daemon set to your cluster to collect logs and diagnostic information and '
          f'save them to the storage account '
          f'{colorama.Style.BRIGHT}{colorama.Fore.GREEN}{storage_account_name}{colorama.Style.RESET_ALL} as '
          f'outlined in {_format_hyperlink("http://aka.ms/AKSPeriscope")}.')
    print()
    print('If you share access to that storage account to Azure support, you consent to the terms outlined'
          f' in {_format_hyperlink("http://aka.ms/DiagConsent")}.')
    print()
    if not prompt_y_n('Do you confirm?', default="n"):
        return

    print()
    print(f"Getting credentials for cluster {name}")
    temp_kubeconfig_path = _get_temp_kubeconfig_path(cmd, client, resource_group_name, name, mc.aad_profile is not None)

    print()
    print(f"Starts collecting diag info for cluster {name}")

    # Base the container name on the fqdn (or private fqdn) of the managed cluster
    container_name = _generate_container_name(mc.fqdn, mc.private_fqdn)
    sas_token = sas_token.strip('?')

    cluster_features = _get_cluster_features(cmd.cli_ctx, resource_group_name, name)

    run_id = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")
    kustomize_yaml = _get_kustomize_yaml(storage_account_name, sas_token, container_name, run_id, cluster_features, container_logs, kube_objects, node_logs, node_logs_windows)
    kustomize_folder = tempfile.mkdtemp()
    kustomize_file_path = os.path.join(kustomize_folder, "kustomization.yaml")
    try:
        with os.fdopen(os.open(kustomize_file_path, os.O_RDWR | os.O_CREAT), 'w+t') as kustomize_file:
            kustomize_file.write(kustomize_yaml)

        try:
            print()
            print("Cleaning up aks-periscope resources if existing")

            subprocess.call(["kubectl", "--kubeconfig", temp_kubeconfig_path, "delete",
                             "serviceaccount,configmap,daemonset,secret",
                             "--all", "-n", CONST_PERISCOPE_NAMESPACE, "--ignore-not-found"],
                            stderr=subprocess.STDOUT)

            subprocess.call(["kubectl", "--kubeconfig", temp_kubeconfig_path, "delete",
                             "ClusterRoleBinding",
                             "aks-periscope-role-binding", "--ignore-not-found"],
                            stderr=subprocess.STDOUT)

            subprocess.call(["kubectl", "--kubeconfig", temp_kubeconfig_path, "delete",
                             "ClusterRoleBinding",
                             "aks-periscope-role-binding-view", "--ignore-not-found"],
                            stderr=subprocess.STDOUT)

            subprocess.call(["kubectl", "--kubeconfig", temp_kubeconfig_path, "delete",
                             "ClusterRole",
                             "aks-periscope-role", "--ignore-not-found"],
                            stderr=subprocess.STDOUT)

            subprocess.call(["kubectl", "--kubeconfig", temp_kubeconfig_path, "delete",
                             "--all",
                             "apd", "-n", CONST_PERISCOPE_NAMESPACE, "--ignore-not-found"],
                            stderr=subprocess.DEVNULL)

            subprocess.call(["kubectl", "--kubeconfig", temp_kubeconfig_path, "delete",
                             "CustomResourceDefinition",
                             "diagnostics.aks-periscope.azure.github.com", "--ignore-not-found"],
                            stderr=subprocess.STDOUT)

            print()
            print("Deploying aks-periscope")

            subprocess.check_output(["kubectl", "--kubeconfig", temp_kubeconfig_path, "apply", "-k",
                                     kustomize_folder, "-n", CONST_PERISCOPE_NAMESPACE], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as err:
            raise CLIError(err.output) from err
    finally:
        os.remove(kustomize_file_path)
        os.rmdir(kustomize_folder)

    print()

    token_in_storage_account_url = readonly_sas_token if readonly_sas_token is not None else sas_token
    log_storage_account_url = f"https://{storage_account_name}.blob.core.windows.net/" \
                              f"{container_name}?{token_in_storage_account_url}"

    print(f'{colorama.Fore.GREEN}Your logs are being uploaded to storage account {_format_bright(storage_account_name)}')

    print()
    print(f'You can download Azure Storage Explorer here '
          f'{_format_hyperlink("https://azure.microsoft.com/en-us/features/storage-explorer/")}'
          f' to check the logs by adding the storage account using the following URL:')
    print(f'{_format_hyperlink(log_storage_account_url)}')

    print()
    if not prompt_y_n('Do you want to see analysis results now?', default="n"):
        print(f"You can run 'az aks kanalyze -g {resource_group_name} -n {name}' "
              f"anytime to check the analysis results.")
    else:
        _display_diagnostics_report(temp_kubeconfig_path)


def aks_kanalyze_cmd(cmd, client, resource_group_name: str, name: str) -> None:
    colorama.init()

    mc = client.get(resource_group_name, name)

    temp_kubeconfig_path = _get_temp_kubeconfig_path(cmd, client, resource_group_name, name, mc.aad_profile is not None)

    _display_diagnostics_report(temp_kubeconfig_path)


def _get_temp_kubeconfig_path(cmd, client, resource_group_name: str, name: str, has_aad_profile: bool) -> str:
    _, temp_kubeconfig_path = tempfile.mkstemp()

    # Use normal user credentials, not admin credentials (admin creds will not be supplied if local accounts are disabled).
    credentialResults = client.list_cluster_user_credentials(resource_group_name, name, None)
    kubeconfig = credentialResults.kubeconfigs[0].value.decode(encoding='UTF-8')
    print_or_merge_credentials(temp_kubeconfig_path, kubeconfig, False, None)

    if has_aad_profile:
        # The current credentials require interactive login. We need to use kubelogin to update the kubeconfig credential.
        if not which('kubelogin'):
            # No kubelogin found...but we can install it if the user wants.
            if not prompt_y_n('Can not find kubelogin executable in PATH. Install now?', default="y"):
                # The user doesn't want us to install kubelogin automatically, so we cannot continue.
                raise CLIError('kubelogin not found. Use az aks install-cli to install.')

            # Install kubelogin
            kubelogin_install_location = _get_default_install_location('kubelogin')
            k8s_install_kubelogin(cmd, 'latest', kubelogin_install_location)

        # kubelogin is installed. Run it to populate user credentials that don't require interactive login.
        subprocess.check_output(["kubelogin", "convert-kubeconfig", "--kubeconfig", temp_kubeconfig_path, "--login", "azurecli"], stderr=subprocess.STDOUT)

    return temp_kubeconfig_path


def _get_kustomize_yaml(storage_account_name,
                        sas_token,
                        container_name,
                        run_id,
                        cluster_features,
                        container_logs=None,
                        kube_objects=None,
                        node_logs_linux=None,
                        node_logs_windows=None):
    components = {
        'win-hpc': bool(cluster_features & ClusterFeatures.WIN_HPC)
    }

    component_content = "\n".join(f'- https://github.com/{CONST_PERISCOPE_REPO_ORG}/aks-periscope//deployment/components/{c}?ref={CONST_PERISCOPE_RELEASE_TAG}' for c, enabled in components.items() if enabled)

    diag_config_vars = {
        'DIAGNOSTIC_RUN_ID': run_id,
        'DIAGNOSTIC_CONTAINERLOGS_LIST': container_logs,
        'DIAGNOSTIC_KUBEOBJECTS_LIST': kube_objects,
        'DIAGNOSTIC_NODELOGS_LIST_LINUX': node_logs_linux,
        'DIAGNOSTIC_NODELOGS_LIST_WINDOWS': node_logs_windows
    }

    # Create YAML list items for each config variable that has a value
    diag_content = "\n".join(f'  - {k}="{v}"' for k, v in diag_config_vars.items() if v is not None)

    # Build a Kustomize overlay referencing a base for a known release, and using the images from MCR
    # for that release.
    return f"""
resources:
- https://github.com/{CONST_PERISCOPE_REPO_ORG}/aks-periscope//deployment/base?ref={CONST_PERISCOPE_RELEASE_TAG}

components:
{component_content}

namespace: {CONST_PERISCOPE_NAMESPACE}

images:
- name: periscope-linux
  newName: {CONST_PERISCOPE_CONTAINER_REGISTRY}/aks/periscope
  newTag: {CONST_PERISCOPE_IMAGE_VERSION}
- name: periscope-windows
  newName: {CONST_PERISCOPE_CONTAINER_REGISTRY}/aks/periscope-win
  newTag: {CONST_PERISCOPE_IMAGE_VERSION}

configMapGenerator:
- name: diagnostic-config
  behavior: merge
  literals:
{diag_content}

secretGenerator:
- name: azureblob-secret
  behavior: replace
  literals:
  - AZURE_BLOB_ACCOUNT_NAME={storage_account_name}
  - AZURE_BLOB_SAS_KEY=?{sas_token}
  - AZURE_BLOB_CONTAINER_NAME={container_name}
"""


def _get_storage_account_from_diag_settings(cli_ctx, resource_group_name, name):
    from azure.mgmt.monitor import MonitorManagementClient
    diag_settings_client = get_mgmt_service_client(
        cli_ctx, MonitorManagementClient).diagnostic_settings
    subscription_id = get_subscription_id(cli_ctx)
    aks_resource_id = (
        f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/"
        f"Microsoft.ContainerService/managedClusters/{name}"
    )
    diag_settings = diag_settings_client.list(aks_resource_id)
    for _, diag_setting in enumerate(diag_settings):
        if diag_setting:
            return diag_setting.storage_account_id

    print("No diag settings specified")
    return None


def _generate_container_name(fqdn: str, private_fqdn: str) -> str:
    """
    Generates a container name unique to the specified managed cluster, that
    conforms to the Azure naming restrictions defined here:
    https://docs.microsoft.com/en-us/rest/api/storageservices/naming-and-referencing-containers--blobs--and-metadata#container-names

    This is done based on fqdn (falling back to private_fqdn), and shortened
    to strip everything including and after ".hcp.".
    In case the result is excessively long, and also for private clusters which
    may not contain "-hcp-", the resulting name is truncated at 63 characters,
    with any trailing hyphens removed.

    :param fqdn: FQDN of managed cluster
    :param private_fqdn: Private FQDN of managed cluster
    :return: container_name: Compliant Azure Storage container name for the cluster
    """
    container_name = fqdn if fqdn is not None else private_fqdn
    container_name = container_name[:container_name.find(".hcp.")]
    container_name = container_name.replace('.', '-')
    container_name = container_name[:CONST_CONTAINER_NAME_MAX_LENGTH].rstrip('-')
    return container_name


def _get_cluster_features(cli_ctx, resource_group_name, cluster_name):
    agent_pool_client = cf_agent_pools(cli_ctx)
    agent_pool_items = agent_pool_client.list(resource_group_name, cluster_name)
    agent_pools = list(agent_pool_items)

    features = ClusterFeatures.NONE
    if _is_windows_hpc_supported(agent_pools):
        features |= ClusterFeatures.WIN_HPC

    return features


def _is_windows_hpc_supported(agent_pools):
    # https://docs.microsoft.com/en-us/rest/api/aks/agent-pools/list?tabs=HTTP#agentpool
    # The full (major.minor.patch) version *may* be stored in currentOrchestratorVersion.
    # If not, it'll be in orchestratorVersion.
    windows_k8s_versions = [p.current_orchestrator_version or p.orchestrator_version for p in agent_pools if p.os_type.casefold() == "Windows".casefold()]
    return all((version.parse(v) >= version.parse("1.23.0") for v in windows_k8s_versions))


def _display_diagnostics_report(temp_kubeconfig_path):   # pylint: disable=too-many-statements
    if not which('kubectl'):
        raise CLIError('Can not find kubectl executable in PATH')

    nodes = subprocess.check_output(
        ["kubectl", "--kubeconfig", temp_kubeconfig_path,
            "get", "node", "--no-headers"],
        universal_newlines=True)
    logger.debug(nodes)
    node_lines = nodes.splitlines()
    ready_nodes = {}
    for node_line in node_lines:
        columns = node_line.split()
        logger.debug(node_line)
        if columns[1] != "Ready":
            logger.warning(
                "Node %s is not Ready. Current state is: %s.", columns[0], columns[1])
        else:
            ready_nodes[columns[0]] = False

    logger.debug('There are %s ready nodes in the cluster',
                 str(len(ready_nodes)))

    if not ready_nodes:
        logger.warning(
            'No nodes are ready in the current cluster. Diagnostics info might not be available.')

    network_config_array = []
    network_status_array = []
    apds_created = False

    max_retry = 10
    for retry in range(0, max_retry):
        if not apds_created:
            apd = subprocess.check_output(
                ["kubectl", "--kubeconfig", temp_kubeconfig_path, "get",
                    "apd", "-n", CONST_PERISCOPE_NAMESPACE, "--no-headers"],
                universal_newlines=True
            )
            apd_lines = apd.splitlines()
            if apd_lines and 'No resources found' in apd_lines[0]:
                apd_lines.pop(0)

            print(f"Got {len(apd_lines)} diagnostic results for {len(ready_nodes)} ready nodes{'.' * retry}\r", end='')
            if len(apd_lines) < len(ready_nodes):
                time.sleep(3)
            else:
                apds_created = True
                print()
        else:
            for node_name, node_ready in ready_nodes.items():
                if node_ready:
                    continue
                apdName = "aks-periscope-diagnostic-" + node_name
                try:
                    network_config = subprocess.check_output(
                        ["kubectl", "--kubeconfig", temp_kubeconfig_path,
                         "get", "apd", apdName, "-n",
                         CONST_PERISCOPE_NAMESPACE, "-o=jsonpath={.spec.networkconfig}"],
                        universal_newlines=True)
                    logger.debug('Dns status for node %s is %s',
                                 node_name, network_config)
                    network_status = subprocess.check_output(
                        ["kubectl", "--kubeconfig", temp_kubeconfig_path,
                         "get", "apd", apdName, "-n",
                         CONST_PERISCOPE_NAMESPACE, "-o=jsonpath={.spec.networkoutbound}"],
                        universal_newlines=True)
                    logger.debug('Network status for node %s is %s',
                                 node_name, network_status)

                    if not network_config or not network_status:
                        print(
                            f"The diagnostics information for node {node_name} is not ready yet. "
                            "Will try again in 10 seconds."
                        )
                        time.sleep(10)
                        break

                    network_config_array += json.loads(
                        '[' + network_config + ']')
                    network_status_object = json.loads(network_status)
                    network_status_array += _format_diag_status(
                        network_status_object)
                    ready_nodes[node_name] = True
                except subprocess.CalledProcessError as err:
                    raise CLIError(err.output) from err

    print()
    if network_config_array:
        print("Below are the network configuration for each node: ")
        print()
        print(tabulate(network_config_array, headers="keys", tablefmt='simple'))
        print()
    else:
        logger.warning("Could not get network config. "
                       "Please run 'az aks kanalyze' command later to get the analysis results.")

    if network_status_array:
        print("Below are the network connectivity results for each node:")
        print()
        print(tabulate(network_status_array, headers="keys", tablefmt='simple'))
    else:
        logger.warning("Could not get networking status. "
                       "Please run 'az aks kanalyze' command later to get the analysis results.")


def _cloud_storage_account_service_factory(cli_ctx, kwargs):
    from azure.cli.core.profiles import ResourceType, get_sdk
    t_cloud_storage_account = get_sdk(
        cli_ctx, ResourceType.DATA_STORAGE, 'common#CloudStorageAccount')
    account_name = kwargs.pop('account_name', None)
    account_key = kwargs.pop('account_key', None)
    sas_token = kwargs.pop('sas_token', None)
    kwargs.pop('connection_string', None)
    return t_cloud_storage_account(account_name, account_key, sas_token)


def _format_hyperlink(the_link):
    return f'\033[1m{colorama.Style.BRIGHT}{colorama.Fore.BLUE}{the_link}{colorama.Style.RESET_ALL}'


def _format_bright(msg):
    return f'\033[1m{colorama.Style.BRIGHT}{msg}{colorama.Style.RESET_ALL}'


def _format_diag_status(diag_status):
    for diag in diag_status:
        if diag["Status"]:
            if "Error:" in diag["Status"]:
                diag["Status"] = f'{colorama.Fore.RED}{diag["Status"]}{colorama.Style.RESET_ALL}'
            else:
                diag["Status"] = f'{colorama.Fore.GREEN}{diag["Status"]}{colorama.Style.RESET_ALL}'

    return diag_status
