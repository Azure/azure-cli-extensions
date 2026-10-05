
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import errno
import os
import subprocess

import yaml
from azure.cli.core.azclierror import AzCLIError
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
    cluster_name: str,
    admin: bool = False,
    user="clusterUser",
) -> str:
    """Get AKS cluster kubeconfig."""

    credentialResults = None
    if admin:
        credentialResults = client.list_cluster_admin_credentials(
            resource_group_name, cluster_name)
    else:
        if user.lower() == 'clusteruser':
            credentialResults = client.list_cluster_user_credentials(
                resource_group_name, cluster_name)
        elif user.lower() == 'clustermonitoringuser':
            credentialResults = client.list_cluster_monitoring_user_credentials(
                resource_group_name, cluster_name)
        else:
            raise AzCLIError("invalid user type for get credentials: {}".format(user))

    if not credentialResults:
        raise CLIError("No Kubernetes credentials found.")

    kubeconfig = credentialResults.kubeconfigs[0].value.decode(
        encoding='UTF-8')
    kubeconfig_path = _get_kubeconfig_file_path(resource_group_name, cluster_name)

    # Ensure the kubeconfig file exists and write kubeconfig to it
    with os.fdopen(os.open(kubeconfig_path, os.O_RDWR | os.O_CREAT | os.O_TRUNC, 0o600), 'wt') as f:
        f.write(kubeconfig)
    try:
        # Check if kubeconfig requires kubelogin with devicecode and convert it
        if _uses_kubelogin_devicecode(kubeconfig):
            import shutil
            if shutil.which("kubelogin"):
                try:
                    # Run kubelogin convert-kubeconfig -l azurecli
                    subprocess.run(
                        ["kubelogin", "convert-kubeconfig", "-l", "azurecli", "--kubeconfig", kubeconfig_path],
                        check=True,
                    )
                    logger.info("Converted kubeconfig to use Azure CLI authentication.")
                except subprocess.CalledProcessError as e:
                    logger.warning("Failed to convert kubeconfig with kubelogin: %s", str(e))
                except Exception as e:  # pylint: disable=broad-except
                    logger.warning("Error running kubelogin: %s", str(e))
            else:
                raise AzCLIError(
                    "The kubeconfig uses devicecode authentication which requires kubelogin. "
                    "Please install kubelogin from https://github.com/Azure/kubelogin or run "
                    "'az aks install-cli' to install both kubectl and kubelogin. "
                    "If devicecode login fails, try running "
                    "'kubelogin convert-kubeconfig -l azurecli' to unblock yourself."
                )
    except (IndexError, ValueError) as exc:
        raise CLIError("Fail to find kubeconfig file.") from exc

    logger.info("Kubeconfig downloaded successfully to: %s", kubeconfig_path)
    return kubeconfig_path


def _uses_kubelogin_devicecode(kubeconfig: str) -> bool:
    try:
        config = yaml.safe_load(kubeconfig)

        # Check if users section exists and has at least one user
        if not config or not config.get('users') or len(config['users']) == 0:
            return False

        first_user = config['users'][0]
        user_info = first_user.get('user', {})
        exec_info = user_info.get('exec', {})

        # Check if command is kubelogin
        command = exec_info.get('command', '')
        if 'kubelogin' not in command:
            return False

        # Check if args contains --login and devicecode
        args = exec_info.get('args', [])
        # Join args into a string for easier pattern matching
        args_str = ' '.join(args)
        # Check for '--login devicecode' or '-l devicecode'
        if '--login devicecode' in args_str or '-l devicecode' in args_str:
            return True
        return False
    except (yaml.YAMLError, KeyError, TypeError, AttributeError) as e:
        # If there's any error parsing the kubeconfig, assume it doesn't require kubelogin
        logger.debug("Error parsing kubeconfig: %s", str(e))
        return False


def _get_kubeconfig_file_path(  # pylint: disable=unused-argument
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

    kubeconfig_filename = f"kubeconfig-{resource_group_name}-{cluster_name}"
    kubeconfig_path = os.path.join(kubeconfig_dir, kubeconfig_filename)

    return kubeconfig_path
