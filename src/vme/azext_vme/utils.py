# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import shutil
import subprocess
import time
import sys
from azure.core.exceptions import ResourceNotFoundError
from knack.util import CLIError
from knack.log import get_logger
from azext_vme import consts
import threading
from ._client_factory import cf_deployments

logger = get_logger(__name__)


def supports_animation():
    return sys.stdout.isatty()


class PollingAnimation:
    def __init__(self):
        self.tickers = ["/", "|", "\\", "-", "/", "|", "\\", "-"]
        self.currTicker = 0
        self.running = True

    def tick(self):
        while self.running:  # Keep the animation going
            sys.stdout.write('\r' + self.tickers[self.currTicker] + " Running ..")
            sys.stdout.flush()
            self.currTicker = (self.currTicker + 1) % len(self.tickers)
            time.sleep(0.5)  # Adjust speed if needed

    def flush(self):
        self.running = False  # Stop the animation
        sys.stdout.write("\r\033[K")  # Clears the line
        sys.stdout.flush()


def call_subprocess_raise_output(cmd: list, logcmd: bool = False, logstatus: bool = True) -> str:
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

    if not supports_animation():
        logstatus = False
    if logstatus:
        animation = PollingAnimation()
        spinner_thread = threading.Thread(target=animation.tick)
        spinner_thread.start()

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

        if logstatus:
            animation.running = False
            spinner_thread.join()
            animation.flush()
        return called_process.stdout
    except subprocess.CalledProcessError as error:
        if logstatus:
            animation.running = False
            spinner_thread.join()
            animation.flush()
        all_output: str = (
            f"Command: {' '.join(log_cmd)}\n"
            f"{error.stderr}"
        )

        # Raise the error without the original exception, which may contain secrets.
        raise CLIError(all_output) from None


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
    result = call_subprocess_raise_output(command, False, False)

    if not (cli_extension_name in result.strip()):
        print(f"Installing az cli extension {cli_extension_name}...")
        command = [
            str(shutil.which("az")),
            "extension",
            "add",
            "--name",
            cli_extension_name
        ]
        call_subprocess_raise_output(command)
        print(f"Installed az cli extension {cli_extension_name} successfully.")


def check_and_enable_bundle_feature_flag(
        cmd, subscription_id, cluster, resource_group_name, cluster_name, kube_config=None, kube_context=None):
    """Enable the bundle feature flag for the given cluster if it's not already enabled."""

    auto_upgrade = extract_auto_upgrade_value(cluster)

    # Check whether the cluster's bundle feature flag is enabled
    featureflag = extract_feature_flag_value(cluster)
    if not featureflag or featureflag.lower() != "enabled":
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

        # Wait for the feature flag to be enabled on the dp side.
        wait_timeout = 300
        start_time = time.time()
        deployment_name = (consts.ARC_UPDATE_PREFIX + cluster_name).lower()
        client = cf_deployments(cmd.cli_ctx, subscription_id)
        deployment = None
        while time.time() - start_time < wait_timeout:
            try:
                deployment = client.get(resource_group_name, deployment_name)
                break
            except ResourceNotFoundError:
                print(f"[{get_utctimestring()}] Waiting for the bundle feature flag to propagate...")
                time.sleep(5)

        if (not deployment):
            raise CLIError("The bundle feature flag failed to propagate within the timeout period.")
        print("Enabled the bundle feature flag successfully.")


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
                raise CLIError(f"[{timestamp}] {consts.UPGRADE_FAILED_MSG + deployment.properties.error.message}")
            statuses = resource.as_dict().get("properties", {}).get("statuses", [])
            errmsg = statuses[0]["message"] if statuses else "Unknown error occurred."
            raise CLIError(
                f"[{timestamp}] {consts.UPGRADE_FAILED_MSG + deployment.properties.error.message} "
                f"'{reserr.target}' failed: {errmsg}"
            )

    raise CLIError(f"[{timestamp}] {consts.UPGRADE_FAILED_MSG + deployment.properties.error.message}")


def get_utctimestring() -> str:
    return time.strftime("%Y-%m-%dT%H-%M-%SZ", time.gmtime())
