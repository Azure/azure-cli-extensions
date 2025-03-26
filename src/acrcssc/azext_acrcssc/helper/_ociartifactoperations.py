# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""A module to handle ORAS calls to the registry."""
# pylint: disable=line-too-long
# pylint: disable=logging-fstring-interpolation
import os
import dataclasses
import tempfile
import shutil
import subprocess

from oras.client import OrasClient
from azure.cli.core.azclierror import AzCLIError
from azure.cli.command_modules.acr.repository import acr_repository_delete
from azure.mgmt.core.tools import parse_resource_id
from jsonschema.exceptions import ValidationError
from knack.log import get_logger
from ._constants import (
    BEARER_TOKEN_USERNAME,
    CONTINUOUSPATCH_CONFIG_SCHEMA_V1,
    CONTINUOUSPATCH_OCI_ARTIFACT_CONFIG,
    CONTINUOUSPATCH_OCI_ARTIFACT_CONFIG_TAG_V1,
    CONTINUOUSPATCH_OCI_ARTIFACT_CONFIG_TAG_DRYRUN,
    CONTINUOUSPATCH_TASK_SCANREGISTRY_NAME,
    CSSC_WORKFLOW_POLICY_REPOSITORY,
    SUBSCRIPTION
)
from ._utility import (
    convert_cron_to_schedule,
    get_task
)

logger = get_logger(__name__)


def create_oci_artifact_continuous_patch(registry, cssc_config_file, dryrun):
    logger.debug(f"Entering create_oci_artifact_continuouspatching with parameters: {registry.name} {cssc_config_file} {dryrun}")

    oras_client = None
    temp_artifact_name = None
    try:
        oras_client = _oras_client(registry)
        # we might have to handle the tag lock/unlock for the cssc config file,
        # to make it harder for the user to change it by mistake

        # the ORAS client can only work with files under the current directory
        temp_artifact = tempfile.NamedTemporaryFile(
            prefix="cssc_config_tmp_",
            mode="w+b",
            dir=os.getcwd(),
            delete=False)

        temp_artifact_name = temp_artifact.name
        user_artifact = open(cssc_config_file, "rb")
        shutil.copyfileobj(user_artifact, temp_artifact)
        temp_artifact.close()

        if dryrun:
            oci_target_name = f"{CSSC_WORKFLOW_POLICY_REPOSITORY}/{CONTINUOUSPATCH_OCI_ARTIFACT_CONFIG}:{CONTINUOUSPATCH_OCI_ARTIFACT_CONFIG_TAG_DRYRUN}"
        else:
            oci_target_name = f"{CSSC_WORKFLOW_POLICY_REPOSITORY}/{CONTINUOUSPATCH_OCI_ARTIFACT_CONFIG}:{CONTINUOUSPATCH_OCI_ARTIFACT_CONFIG_TAG_V1}"

        oras_client.push(
            target=oci_target_name,
            files=[temp_artifact.name])
    except Exception as exception:
        raise AzCLIError(f"Failed to push OCI artifact to ACR: {exception}")
    finally:
        if oras_client:
            oras_client.logout(hostname=str.lower(registry.login_server))
        if temp_artifact_name and os.path.exists(temp_artifact_name):
            os.remove(temp_artifact_name)


def get_oci_artifact_continuous_patch(cmd, registry):
    logger.debug("Entering get_oci_artifact_continuous_patch with parameter: %s", registry.login_server)
    config = None
    file_name = None
    try:
        oras_client = _oras_client(registry)

        oci_target_name = f"{CSSC_WORKFLOW_POLICY_REPOSITORY}/{CONTINUOUSPATCH_OCI_ARTIFACT_CONFIG}:{CONTINUOUSPATCH_OCI_ARTIFACT_CONFIG_TAG_V1}"

        oci_artifacts = oras_client.pull(target=oci_target_name,
                                         stream=True)
        trigger_task = get_task(cmd, registry, CONTINUOUSPATCH_TASK_SCANREGISTRY_NAME)
        file_name = oci_artifacts[0]
        config = ContinuousPatchConfig().from_file(file_name, trigger_task)
    except Exception as exception:
        raise AzCLIError(f"Failed to get OCI artifact from ACR: {exception}")
    finally:
        oras_client.logout(hostname=str.lower(registry.login_server))

    return config, file_name


def delete_oci_artifact_continuous_patch(cmd, registry):
    logger.debug(f"Entering delete_oci_artifact_continuous_patch with parameters {registry}")
    resourceid = parse_resource_id(registry.id)
    subscription = resourceid[SUBSCRIPTION]

    try:
        token = _get_acr_token(registry.name, subscription)

        # Delete repository, removing only image isn't deleting the repository always (Bug)
        acr_repository_delete(
            cmd=cmd,
            registry_name=registry.name,
            repository=f"{CSSC_WORKFLOW_POLICY_REPOSITORY}/{CONTINUOUSPATCH_OCI_ARTIFACT_CONFIG}",
            username=BEARER_TOKEN_USERNAME,
            password=token,
            yes=True)
        logger.debug("Call to acr_repository_delete completed successfully")
    except Exception as exception:
        logger.debug(exception)
        logger.error(f"{CSSC_WORKFLOW_POLICY_REPOSITORY}/{CONTINUOUSPATCH_OCI_ARTIFACT_CONFIG}:{CONTINUOUSPATCH_OCI_ARTIFACT_CONFIG_TAG_V1} might not exist or attempt to delete failed.")
        raise


def _oras_client(registry):
    resourceid = parse_resource_id(registry.id)
    subscription = resourceid[SUBSCRIPTION]

    try:
        token = _get_acr_token(registry.name, subscription)
        client = OrasClient(hostname=str.lower(registry.login_server))
        client.login(BEARER_TOKEN_USERNAME, token)
    except Exception as exception:
        raise AzCLIError(f"Failed to login to Artifact Store ACR {registry.name}: {exception}")

    return client


def _get_acr_token(registry_name, subscription):
    logger.debug(f"Using CLI user credentials to log into {registry_name}")
    acr_login_with_token_cmd = [
        str(shutil.which("az")),
        "acr", "login",
        "--name", registry_name,
        "--subscription", subscription,
        "--expose-token",
        "--output", "tsv",
        "--query", "accessToken",
    ]

    try:
        result = subprocess.run(
            acr_login_with_token_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,  # Ensures output is returned as a string
            check=True  # Raises CalledProcessError for non-zero exit codes
        )
        token = result.stdout.strip()
        if not token or token == "":
            logger.debug("Failed to retrieve ACR token: Token is empty.")
            raise AzCLIError("Failed to retrieve ACR token. The token is empty.")
        return token
    except subprocess.CalledProcessError as error:
        logger.debug(f"Error while retrieving ACR token: {error.stderr.strip()}")

        unauthorized = (error.stderr
                        and (" 401" in error.stderr or "unauthorized" in error.stderr))

        if unauthorized:
            # As we shell out the the subprocess, I think checking for these
            # strings is the best check we can do for permission failures.
            raise AzCLIError(
                " Failed to login to Artifact Store ACR.\n"
                " It looks like you do not have permissions. You need to have"
                " the AcrPush role over the"
                " registry in order to be able to upload to the new"
                " artifact store."
            ) from error

        raise AzCLIError(f"Failed to retrieve ACR token: {error.stderr.strip()}") from error


class ContinuousPatchConfig:
    def __init__(self):
        self.version = ""
        self.repositories = []
        self.schedule = None

    def from_file(self, file_path, trigger_task=None):
        with open(file_path, "r") as file:
            return self.from_json(file.read(), trigger_task)

    def from_json(self, json_str, trigger_task=None):
        import json
        from jsonschema import validate

        try:
            json_config = json.loads(json_str)
            validate(json_config, CONTINUOUSPATCH_CONFIG_SCHEMA_V1)
        except ValidationError as e:
            logger.error("Error validating the continuous patch config file: %s", e)
            return None

        self.version = json_config.get("version", "")
        repositories = json_config.get("repositories", [])
        for repo in repositories:
            enabled = repo.get("enabled", True)  # optional field, default to True
            repository = Repository(repo["repository"], repo["tags"], enabled)
            self.repositories.append(repository)

        if trigger_task:
            trigger = trigger_task.trigger
            if trigger and trigger.timer_triggers:
                self.schedule = convert_cron_to_schedule(trigger.timer_triggers[0].schedule, just_days=True)

        return self

    def get_enabled_images(self):
        enabled_images = []
        for repository in self.repositories:
            if repository.enabled:
                for tag in repository.tags:
                    image = f"{repository.repository}:{tag}"
                    enabled_images.append(image)
        return enabled_images


@dataclasses.dataclass
class Repository:
    repository: str
    tags: list[str]
    enabled: bool
