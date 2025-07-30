# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import shutil
from azext_vme import consts, utils
from knack.util import CLIError
from knack.log import get_logger
import time
from azure.cli.core.commands.client_factory import get_subscription_id
from ._client_factory import cf_deployments, cf_resources
from azure.core.exceptions import ResourceNotFoundError

logger = get_logger(__name__)


def install_vme(
        cmd,
        resource_group_name: str,
        cluster_name: str,
        include_extension_types: list[str],
        kube_config: str | None = None,
        kube_context: str | None = None):
    if 'all' in include_extension_types:
        include_extension_types = consts.BundleExtensionTypes
    subscription_id = get_subscription_id(cmd.cli_ctx)

    # Check whether the cluster exists
    resources = cf_resources(cmd.cli_ctx, subscription_id)
    cluster_resource_id = '/subscriptions/{0}/resourceGroups/{1}/providers/{2}/{3}/{4}'.format(
        subscription_id, resource_group_name, consts.CONNECTEDCLUSTER_RP, consts.CONNECTEDCLUSTER_TYPE, cluster_name)
    cluster = resources.get_by_id(cluster_resource_id, '2024-12-01-preview')

    utils.check_and_add_cli_extension("connectedk8s")
    utils.check_and_add_cli_extension("k8s-extension")
    utils.check_and_enable_bundle_feature_flag(
        cmd, subscription_id, cluster, resource_group_name, cluster_name, kube_config, kube_context)

    # Install the bundle extensions one by one
    for extension_type in include_extension_types:
        extension_resource_id = (
            f"{cluster_resource_id}/Providers/Microsoft.KubernetesConfiguration/"
            f"extensions/{consts.BundleExtensionTypeNames[extension_type]}"
        )
        try:
            ext = resources.get_by_id(extension_resource_id, '2022-11-01')
            if ext.properties['provisioningState'] == 'Failed':
                raise ResourceNotFoundError()
            print(f"Extension {extension_type} already exists, skipping installation.")
            continue
        except ResourceNotFoundError:
            # The extension does not exist, proceed with installation
            print(f"Installing extension {extension_type}...", flush=True)
            command = [
                str(shutil.which("az")),
                "k8s-extension",
                "create",
                "--resource-group",
                resource_group_name,
                "--cluster-name",
                cluster_name,
                "--cluster-type",
                consts.CONNECTEDCLUSTER_TYPE,
                "--name",
                consts.BundleExtensionTypeNames[extension_type],
                "--extension-type",
                extension_type,
                "--scope",
                "cluster"
            ]
            result = utils.call_subprocess_raise_output(command)
            print(f"Installed extension {extension_type} successfully.", flush=True)
            print(result)

    if len(include_extension_types) > 1:
        print("All extensions installed successfully.")


def uninstall_vme(
        cmd,
        resource_group_name: str,
        cluster_name: str,
        include_extension_types: list[str],
        force=False):
    if 'all' in include_extension_types:
        include_extension_types = consts.BundleExtensionTypes
    subscription_id = get_subscription_id(cmd.cli_ctx)

    # Check whether the cluster exists
    resources = cf_resources(cmd.cli_ctx, subscription_id)
    cluster_resource_id = '/subscriptions/{0}/resourceGroups/{1}/providers/{2}/{3}/{4}'.format(
        subscription_id, resource_group_name, consts.CONNECTEDCLUSTER_RP, consts.CONNECTEDCLUSTER_TYPE, cluster_name)
    resources.get_by_id(cluster_resource_id, '2024-12-01-preview')

    utils.check_and_add_cli_extension("k8s-extension")

    # Uninstall the bundle extensions one by one
    for extension_type in include_extension_types:
        print(f"Uninstalling extension {extension_type}...", flush=True)
        command = [str(shutil.which("az")),
                   "k8s-extension",
                   "delete",
                   "--resource-group",
                   resource_group_name,
                   "--cluster-name",
                   cluster_name,
                   "--cluster-type",
                   "connectedClusters",
                   "--name",
                   consts.BundleExtensionTypeNames[extension_type],
                   "--yes"]
        if force:
            command.append("--force")
        utils.call_subprocess_raise_output(command)
        print(f"Uninstalled extension {extension_type} successfully.", flush=True)
    if len(include_extension_types) > 1:
        print("All extensions uninstalled successfully.")


def upgrade_vme(
        cmd,
        resource_group_name: str,
        cluster_name: str,
        kube_config: str | None = None,
        kube_context: str | None = None,
        wait: bool = False,
        timeout: str = "3600"):
    subscription_id = get_subscription_id(cmd.cli_ctx)

    # Check whether the cluster exists
    resources = cf_resources(cmd.cli_ctx, subscription_id)
    cluster_resource_id = '/subscriptions/{0}/resourceGroups/{1}/providers/{2}/{3}/{4}'.format(
        subscription_id, resource_group_name, consts.CONNECTEDCLUSTER_RP, consts.CONNECTEDCLUSTER_TYPE, cluster_name)
    cluster = resources.get_by_id(cluster_resource_id, '2024-12-01-preview')
    agent_version = cluster.properties.get('agentVersion', None)

    if not agent_version:
        raise CLIError("Agent version not found in the cluster properties.")

    utils.check_and_add_cli_extension("connectedk8s")
    utils.check_and_enable_bundle_feature_flag(
        cmd, subscription_id, cluster, resource_group_name, cluster_name, kube_config, kube_context)
    deployment_name = (consts.ARC_UPDATE_PREFIX + cluster_name).lower()
    print(f"Checking arm template deployment '{deployment_name}' for '{cluster_resource_id}' "
          f"which has agent version '{agent_version}'", flush=True)

    client = cf_deployments(cmd.cli_ctx, subscription_id)

    # Retry logic to get the deployment
    wait_timeout = int(timeout)
    start_time = time.time()
    deployment = None
    while time.time() - start_time < wait_timeout:
        # Get current timestamp
        timestamp = utils.get_utctimestring()
        try:
            deployment = client.get(resource_group_name, deployment_name)
            if (not deployment or not deployment.tags):
                print(f"[{timestamp}] {consts.UPGRADE_NOTSTARTED_MSG}")
                time.sleep(consts.UPGRADE_CHECK_INTERVAL)
                continue

            deployment_agent_version = deployment.tags.get(consts.AGENT_VERSION_TAG)
            if (deployment_agent_version != agent_version):
                msg = (
                    f"[{timestamp}] The current deployment {deployment_name} is for {deployment_agent_version} "
                    f"instead of current agent version {agent_version}. {consts.UPGRADE_NOTSTARTED_MSG}"
                )
                print(msg, flush=True)
                time.sleep(consts.UPGRADE_CHECK_INTERVAL)
                continue
            if utils.check_deployment_status(resources, deployment, timestamp):
                break

            if not wait:
                break

            time.sleep(consts.UPGRADE_CHECK_INTERVAL)

        except ResourceNotFoundError:
            print(f"[{timestamp}] {consts.UPGRADE_NOTSTARTED_MSG}")
            time.sleep(consts.UPGRADE_CHECK_INTERVAL)

    if (not deployment):
        raise CLIError(consts.UPGRADE_TIMEOUT_MSG.format(wait_timeout))


def list_vme(
        cmd,
        resource_group_name: str,
        cluster_name: str):
    subscription_id = get_subscription_id(cmd.cli_ctx)

    # Check whether the cluster exists
    resources = cf_resources(cmd.cli_ctx, subscription_id)
    cluster_resource_id = '/subscriptions/{0}/resourceGroups/{1}/providers/{2}/{3}/{4}'.format(
        subscription_id, resource_group_name, consts.CONNECTEDCLUSTER_RP, consts.CONNECTEDCLUSTER_TYPE, cluster_name)
    resources.get_by_id(cluster_resource_id, '2024-12-01-preview')

    results = []
    extension_names = consts.BundleExtensionNames
    for extension_name in extension_names:
        extension_resource_id = (
            f"{cluster_resource_id}/Providers/Microsoft.KubernetesConfiguration/"
            f"extensions/{extension_name}"
        )
        try:
            ext = resources.get_by_id(extension_resource_id, '2022-11-01')
            results.append(ext)
        except ResourceNotFoundError:
            continue

    return results
