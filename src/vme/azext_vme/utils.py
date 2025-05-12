# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# Standard library imports
import json
import os
import platform
import shutil
import stat
import subprocess
import time
from subprocess import PIPE, Popen
from oras.client import OrasClient
from azure.core.exceptions import ResourceNotFoundError

# Azure CLI imports
from azure.cli.core import telemetry
from azure.cli.core.azclierror import (
    CLIInternalError,
    ClientRequestError
)

# Knack imports
from knack.util import CLIError
from knack.log import get_logger

# Local imports
from azext_vme import consts


logger = get_logger(__name__)


def call_subprocess_raise_output(cmd: list, logcmd: bool = True) -> str:
    """
    Call a subprocess and raise a CLIError with the output if it fails.

    :param cmd: command to run, in list format
    :raise CLIError: if the subprocess fails
    """
    log_cmd = cmd.copy()
    if "--password" in log_cmd:
        # Do not log out passwords.
        log_cmd[log_cmd.index("--password") + 1] = "[REDACTED]"
    log_cmd[0] = "az"

    if logcmd:
        # Log the command to be run, but do not log the password.
        print(f"Running command: {' '.join(log_cmd)}")

    try:
        called_process = subprocess.run(
            cmd, encoding="utf-8", capture_output=True, text=True, check=True
        )
        logger.debug(
            "Output from %s: %s. Error: %s",
            log_cmd,
            called_process.stdout,
            called_process.stderr,
        )

        return called_process.stdout
    except subprocess.CalledProcessError as error:
        all_output: str = (
            f"Command: {' '.join(log_cmd)}\n"
            f"stdout: {error.stdout}\n"
            f"stderr: {error.stderr}\n"
            f"Return code: {error.returncode}"
        )
        logger.debug("The following command failed to run:\n%s", all_output)
        # Raise the error without the original exception, which may contain secrets.
        raise CLIError(all_output) from None


def get_release_namespace(
    kube_config: str | None,
    kube_context: str | None,
    helm_client_location: str,
    release_name: str = "azure-arc",
) -> str | None:
    cmd_helm_release = [
        helm_client_location,
        "list",
        "-a",
        "--all-namespaces",
        "--output",
        "json",
    ]
    if kube_config:
        cmd_helm_release.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_release.extend(["--kube-context", kube_context])
    response_helm_release = Popen(cmd_helm_release, stdout=PIPE, stderr=PIPE)
    output_helm_release, error_helm_release = response_helm_release.communicate()
    if response_helm_release.returncode != 0:
        error = error_helm_release.decode("ascii")
        if "forbidden" in error or "Kubernetes cluster unreachable" in error:
            telemetry.set_user_fault()

        telemetry.set_exception(
            exception=error,
            fault_type="helm-list-release-error",
            summary="Unable to list helm release",
        )
        raise CLIInternalError(f"Helm list release failed: {error}")

    output_helm_release_str = output_helm_release.decode("ascii")
    try:
        output_helm_release_dict = json.loads(output_helm_release_str)
    except json.decoder.JSONDecodeError:
        return None
    for release in output_helm_release_dict:
        if release["name"] == release_name:
            namespace: str = release["namespace"]
            return namespace
    return None


def get_agent_version(helm_client_location, release_namespace, kube_config, kube_context) -> str:
    helm_cmd = [
        helm_client_location, "list", "-n", release_namespace, "--filter", "azure-arc", "--output", "json"]

    if kube_config:
        helm_cmd.extend(["--kubeconfig", kube_config])
    if kube_context:
        helm_cmd.extend(["--kube-context", kube_context])

    result = subprocess.run(helm_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        logger.error("Helm list error: %s", result.stderr)

    helm_data = json.loads(result.stdout)
    chart_version = helm_data[0]["chart"].replace("azure-arc-k8sagents-", "")
    return chart_version


def extract_feature_flag_value(cluster):
    if consts.ArcAgentryConfigurations in cluster.properties:
        features = cluster.properties[consts.ArcAgentryConfigurations]
        for feature in features:
            if (
                feature.get("feature") == consts.ArcAgentryBundleFeatureName
                and feature.get("settings", {}).get(consts.ArcAgentryBundleSettingsName)
            ):
                return feature["settings"][consts.ArcAgentryBundleSettingsName]

    return None


def extract_auto_upgrade_value(cluster):
    if consts.ArcAgentProfile in cluster.properties:
        agentProfile = cluster.properties[consts.ArcAgentProfile]
        if agentProfile[consts.ArcAgentAutoUpgrade] == "Enabled":
            return "true"

    return "false"


def install_helm_client() -> str:
    # Return helm client path set by user
    helm_client_path = os.getenv("HELM_CLIENT_PATH")
    if helm_client_path:
        return helm_client_path

    helm_client_path = shutil.which("helm")
    if helm_client_path:
        return helm_client_path

    # Fetch system related info
    operating_system = platform.system().lower()

    # Set helm binary download & install locations
    if operating_system == "windows":
        download_location_string = f".azure\\helm\\{consts.HELM_VERSION}"
        download_file_name = f"helm-{consts.HELM_VERSION}-{operating_system}-amd64.zip"
        install_location_string = (
            f".azure\\helm\\{consts.HELM_VERSION}\\{operating_system}-amd64\\helm.exe"
        )
        artifactTag = f"helm-{consts.HELM_VERSION}-{operating_system}-amd64"
    elif operating_system == "linux" or operating_system == "darwin":
        download_location_string = f".azure/helm/{consts.HELM_VERSION}"
        download_file_name = (
            f"helm-{consts.HELM_VERSION}-{operating_system}-amd64.tar.gz"
        )
        install_location_string = (
            f".azure/helm/{consts.HELM_VERSION}/{operating_system}-amd64/helm"
        )
        artifactTag = f"helm-{consts.HELM_VERSION}-{operating_system}-amd64"
    else:
        raise ClientRequestError(
            f"The {operating_system} platform is not currently supported for installing helm client."
        )

    download_location = os.path.expanduser(os.path.join("~", download_location_string))
    download_dir = os.path.dirname(download_location)
    install_location = os.path.expanduser(os.path.join("~", install_location_string))

    # Download compressed Helm binary if not already present
    if not os.path.isfile(install_location):
        # Creating the helm folder if it doesnt exist
        if not os.path.exists(download_dir):
            try:
                os.makedirs(download_dir)
            except Exception as e:
                raise ClientRequestError("Failed to create helm directory." + str(e))

        # Downloading compressed helm client executable
        logger.warning(
            "Downloading helm client for first time. This can take few minutes..."
        )
        client = OrasClient()
        retry_count = 3
        retry_delay = 5
        for i in range(retry_count):
            try:
                client.pull(
                    target=f"{consts.HELM_MCR_URL}:{artifactTag}",
                    outdir=download_location,
                )
                break
            # pylint: disable=broad-exception-caught
            except Exception as e:
                if i == retry_count - 1:
                    raise CLIInternalError(
                        f"Failed to download helm client: {e}",
                        recommendation="Please check your internet connection.",
                    )
                time.sleep(retry_delay)

        # Extract the archive.
        try:
            extract_dir = download_location
            download_location = os.path.expanduser(
                os.path.join(download_location, download_file_name)
            )
            shutil.unpack_archive(download_location, extract_dir)
            os.chmod(install_location, os.stat(install_location).st_mode | stat.S_IXUSR)
        except Exception as e:
            reco_str = f"Please ensure that you delete the directory '{extract_dir}' before trying again."
            raise ClientRequestError(
                "Failed to extract helm executable." + str(e), recommendation=reco_str
            )

    print(f"Helm client installed at {install_location}")
    return install_location


def check_and_add_cli_extension(cli_extension_name):
    # Check if the extension is installed
    command = [
        str(shutil.which("az")),
        "extension",
        "list",
        "--query",
        "[?name=='{}'].name".format(cli_extension_name),
        "-o",
        "tsv"
    ]
    result = call_subprocess_raise_output(command, False)

    if not (cli_extension_name in result.strip()):
        print(f"{cli_extension_name} is not installed. Adding it now...")
        command = [
            str(shutil.which("az")),
            "extension",
            "add",
            "--name",
            cli_extension_name
        ]
        call_subprocess_raise_output(command)


def check_and_enable_bundle_feature_flag(
        cluster, resource_group_name, cluster_name, kube_config=None, kube_context=None):
    """Enable the bundle feature flag for the given cluster if it's not already enabled."""

    # Install helm client
    helm_client_location = install_helm_client()

    # Check Release Existence
    release_namespace = get_release_namespace(
        kube_config, kube_context, helm_client_location
    )

    if not release_namespace:
        raise CLIError(
            "The azure-arc release namespace couldn't be retrieved, "
            "please check --kube-config/--kube-context set correctly."
        )

    auto_upgrade = extract_auto_upgrade_value(cluster)

    # Check whether the cluster's bundle feature flag is enabled
    featureflag = extract_feature_flag_value(cluster)
    if not featureflag or featureflag != "Enabled":
        print("Enabling the bundle feature flag first before installing the extensions...")
        command = [
            str(shutil.which("az")),
            "connectedk8s",
            "update",
            "--resource-group", resource_group_name,
            "--name", cluster_name,
            "--auto-upgrade", auto_upgrade,
            "--config", f"{consts.ArcAgentryBundleFeatureName}.{consts.ArcAgentryBundleSettingsName}=Enabled"
        ]

        if kube_config:
            command.extend(["--kube-config", kube_config])
        if kube_context:
            command.extend(["--kube-context", kube_context])

        call_subprocess_raise_output(command)

        # Wait for the feature flag to be enabled on the dp side
        time.sleep(5)

    agent_version = get_agent_version(helm_client_location, release_namespace, kube_config, kube_context)
    return agent_version


def check_deployment_status(resources, deployment, timestamp):
    """Handles deployment status checks and logs appropriate messages."""
    if deployment.properties.provisioning_state == consts.SUCCEEDED:
        print(f"[{timestamp}] {consts.UPGRADE_SUCCEEDED_MSG}")
        return True
    if deployment.properties.provisioning_state == consts.CANCELLED:
        print(f"[{timestamp}] {consts.UPGRADE_CANCELED_MSG}")
        return True
    if deployment.properties.provisioning_state == consts.FAILED:
        handle_failure(resources, deployment, timestamp)
        return True

    print(f"[{timestamp}] {consts.UPGRADE_IN_PROGRESS_MSG}")
    return False


def handle_failure(resources, deployment, timestamp):
    """Handles deployment failures and extracts error details."""
    if deployment.properties.error.details:
        reserr = deployment.properties.error.details[0]
        if reserr.code == "ResourceDeploymentFailure":
            try:
                resource = resources.get_by_id(reserr.target, "2022-11-01")
            except ResourceNotFoundError:
                logger.warning("The '%s' doesn't exist.", reserr.target)
                return
            errmsg = f"{resource.as_dict()['properties']['statuses'][0]['message']}"
            raise CLIError(
                f"[{timestamp}] {consts.UPGRADE_FAILED_MSG + deployment.properties.error.message} "
                f"'{reserr.target}' failed: {errmsg}"
            )

    raise CLIError(f"[{timestamp}] {consts.UPGRADE_FAILED_MSG + deployment.properties.error.message}")
