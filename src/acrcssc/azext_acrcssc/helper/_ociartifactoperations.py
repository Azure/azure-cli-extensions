# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""A module to handle ORAS calls to the registry."""
# pylint: disable=line-too-long
# pylint: disable=logging-fstring-interpolation
import os
import dataclasses
import shutil
import subprocess
import json

from oras.client import OrasClient
from azure.cli.core.azclierror import AzCLIError, InvalidArgumentValueError
from azure.cli.command_modules.acr.repository import acr_repository_delete
from azure.mgmt.core.tools import parse_resource_id
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from knack.log import get_logger
from tempfile import NamedTemporaryFile
from ._constants import (
    BEARER_TOKEN_USERNAME,
    CONTINUOUSPATCH_CONFIG_SCHEMA_V1,
    CONTINUOUSPATCH_OCI_ARTIFACT_CONFIG,
    CONTINUOUSPATCH_OCI_ARTIFACT_CONFIG_TAG_V1,
    CONTINUOUSPATCH_OCI_ARTIFACT_CONFIG_TAG_DRYRUN,
    CONTINUOUSPATCH_TASK_SCANREGISTRY_NAME,
    CSSC_WORKFLOW_POLICY_REPOSITORY,
    ERROR_MESSAGE_INVALID_JSON_PARSE,
    ERROR_MESSAGE_INVALID_JSON_SCHEMA,
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
    try:
        oras_client = _oras_client(registry)

        # the ORAS client can only work with files under the current directory
        with NamedTemporaryFile(
            prefix="cssc_config_tmp_",
            mode="w+b",
            dir=os.getcwd(),
            delete=False
        ) as temp_artifact, open(cssc_config_file, "rb") as user_artifact:
            shutil.copyfileobj(user_artifact, temp_artifact)
            temp_artifact.flush()  # Ensure all data is written to disk
            temp_artifact_name = temp_artifact.name

            if dryrun:
                oci_target_name = f"{CSSC_WORKFLOW_POLICY_REPOSITORY}/{CONTINUOUSPATCH_OCI_ARTIFACT_CONFIG}:{CONTINUOUSPATCH_OCI_ARTIFACT_CONFIG_TAG_DRYRUN}"
            else:
                oci_target_name = f"{CSSC_WORKFLOW_POLICY_REPOSITORY}/{CONTINUOUSPATCH_OCI_ARTIFACT_CONFIG}:{CONTINUOUSPATCH_OCI_ARTIFACT_CONFIG_TAG_V1}"

            logger.debug(f"Publish OCI artifact to: {oci_target_name}")
            oras_client.push(
                target=oci_target_name,
                files=[temp_artifact_name])
    except Exception as exception:
        raise AzCLIError(f"Failed to push OCI artifact to ACR: {exception}")
    finally:
        if oras_client:
            oras_client.logout(hostname=str.lower(registry.login_server))


def get_oci_artifact_continuous_patch(cmd, registry):
    logger.debug("Entering get_oci_artifact_continuous_patch with parameter: %s", registry.login_server)
    config = None
    file_name = None
    oras_client = None
    try:
        oras_client = _oras_client(registry)

        oci_target_name = f"{CSSC_WORKFLOW_POLICY_REPOSITORY}/{CONTINUOUSPATCH_OCI_ARTIFACT_CONFIG}:{CONTINUOUSPATCH_OCI_ARTIFACT_CONFIG_TAG_V1}"

        logger.debug(f"Pull OCI artifact from: {oci_target_name}")
        oci_artifacts = oras_client.pull(target=oci_target_name,
                                         overwrite=True)

        if not oci_artifacts:
            raise AzCLIError(f"Failed to pull OCI artifact from ACR: {oci_target_name}")

        trigger_task = get_task(cmd, registry, CONTINUOUSPATCH_TASK_SCANREGISTRY_NAME)
        file_name = oci_artifacts[0]
        logger.debug(f"OCI artifact file name: {file_name}, trigger task: {trigger_task}")
        config = ContinuousPatchConfig().from_file(file_name, trigger_task)
    except Exception as exception:
        raise AzCLIError(f"Failed to get OCI artifact from ACR: {exception}")
    finally:
        if oras_client:
            oras_client.logout(hostname=str.lower(registry.login_server))

    return config, file_name


def delete_oci_artifact_continuous_patch(cmd, registry):
    logger.debug(f"Entering delete_oci_artifact_continuous_patch with parameters {registry}")
    resourceid = parse_resource_id(registry.id)
    subscription = resourceid[SUBSCRIPTION]

    try:
        token = _get_acr_token(registry.name, subscription)
        oci_target_name = f"{CSSC_WORKFLOW_POLICY_REPOSITORY}/{CONTINUOUSPATCH_OCI_ARTIFACT_CONFIG}"
        # Delete repository, removing only image isn't deleting the repository always (Bug)
        acr_repository_delete(
            cmd=cmd,
            registry_name=registry.name,
            repository=oci_target_name,
            username=BEARER_TOKEN_USERNAME,
            password=token,
            yes=True)
        logger.debug("Call to acr_repository_delete completed successfully")
    except Exception as exception:
        logger.debug(exception)
        logger.error(f"{oci_target_name}:{CONTINUOUSPATCH_OCI_ARTIFACT_CONFIG_TAG_V1} might not exist or attempt to delete failed.")
        raise


def _oras_client(registry):
    resourceid = parse_resource_id(registry.id)
    subscription = resourceid[SUBSCRIPTION]

    try:
        token = _get_acr_token(registry.name, subscription)
        client = OrasClient(hostname=str.lower(registry.login_server), auth_backend="token")
        client.login(BEARER_TOKEN_USERNAME, token)
        logger.debug(f"Login to ACR {registry.name} completed successfully.")
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
            raise AzCLIError("Failed to retrieve ACR token. The token is empty.")
        return token
    except subprocess.CalledProcessError as error:
        stderr = error.stderr.strip()
        logger.debug(f"Error while retrieving ACR token: {stderr}")
        unauthorized = "401" in stderr or "unauthorized" in stderr.lower()

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

        raise AzCLIError(f"Failed to retrieve ACR token: {stderr}") from error


class ContinuousPatchConfig:
    def __init__(self):
        self.version = ""
        self.repositories = []
        self.schedule = None

    def from_file(self, file_path, trigger_task=None):
        with open(file_path, "r") as file:
            return self.from_json(file.read(), trigger_task)

    def from_json(self, json_str, trigger_task=None):
        try:
            json_config = json.loads(json_str)
            validate(json_config, CONTINUOUSPATCH_CONFIG_SCHEMA_V1)
        except json.JSONDecodeError as e:
            raise AzCLIError(ERROR_MESSAGE_INVALID_JSON_PARSE) from e
        except ValidationError as e:
            logger.error(f"Error validating the continuous patch config file: {e}")
            raise AzCLIError(ERROR_MESSAGE_INVALID_JSON_SCHEMA) from e
        except Exception as e:
            logger.error(f"Error validating the continuous patch config file: {e}")
            if json_str:
                logger.debug(f"Config file content: {json_str}")
            raise InvalidArgumentValueError(ERROR_MESSAGE_INVALID_JSON_PARSE) from e

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
