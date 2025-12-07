
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import errno
import os

from knack.log import get_logger
from knack.util import CLIError

logger = get_logger(__name__)

# NOTE(mainred): we can use get_default_cli().invoke() to trigger `az aks get-credentials` to fetch the kubeconfig,
# but this command shows redundant warning log like
# "The behavior of this command has been altered by the following extension: aks-preview" when aks-preview is installed
# "Merged "<cluster_name>" as current context in <config_path>/<cluster_name>" when the kubeconfig file already exists
# and `--only-show-errors` does not suppress it for the global log handler has been initialized before invoking the
# command, in the "az aks agent" commands. Resetting the log level for get-credentials will break the log behavior of
# `az aks agent`. So we directly use the SDK to get the kubeconfig here, which makes sense for an aks extension.


def get_aks_credentials(
    client: str,
    resource_group_name: str,
    cluster_name: str
) -> str:
    """Get AKS cluster kubeconfig."""
    credentialResults = client.list_cluster_user_credentials(
        resource_group_name, cluster_name
    )
    if not credentialResults:
        raise CLIError("No Kubernetes credentials found.")

    kubeconfig = credentialResults.kubeconfigs[0].value.decode(
        encoding='UTF-8')

    kubeconfig_path = _get_kubeconfig_file_path(resource_group_name, cluster_name)

    # Ensure the kubeconfig file exists and write kubeconfig to it
    with os.fdopen(os.open(kubeconfig_path, os.O_CREAT | os.O_WRONLY, 0o600), 'wt') as f:
        f.write(kubeconfig)

    logger.info("Kubeconfig downloaded successfully to: %s", kubeconfig_path)
    return kubeconfig_path


def _get_kubeconfig_file_path(
    resource_group_name: str,
    cluster_name: str,
    subscription_id: str = None
):
    """Get the path to the kubeconfig file for the AKS cluster."""

    home_dir = os.path.expanduser("~")
    kubeconfig_dir = os.path.join(home_dir, ".aks-agent", "kube")

    # ensure that kube folder exists
    if kubeconfig_dir and not os.path.exists(kubeconfig_dir):
        try:
            os.makedirs(kubeconfig_dir)
        except OSError as ex:
            if ex.errno != errno.EEXIST:
                raise

    kubeconfig_filename = f"kubeconfig-{cluster_name}"
    kubeconfig_path = os.path.join(kubeconfig_dir, kubeconfig_filename)

    return kubeconfig_path
