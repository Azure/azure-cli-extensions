# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""A module to handle ORAS calls to the registry."""

import os
import tempfile
import shutil
import subprocess

from oras.client import OrasClient
from azure.cli.core.azclierror import AzCLIError
from azure.cli.command_modules.acr.repository import acr_repository_delete
from azure.mgmt.core.tools import parse_resource_id
from knack.log import get_logger
from ._constants import (
    BEARER_TOKEN_USERNAME,
    CONTINUOSPATCH_OCI_ARTIFACT_CONFIG,
    CONTINUOSPATCH_OCI_ARTIFACT_CONFIG_TAG_V1,
    CONTINUOSPATCH_OCI_ARTIFACT_CONFIG_TAG_DRYRUN,
    CSSC_WORKFLOW_POLICY_REPOSITORY,
    RESOURCE_GROUP,
    SUBSCRIPTION
)

logger = get_logger(__name__)


def create_oci_artifact_continuous_patch(cmd, registry, cssc_config_file, dryrun):
    logger.debug("Entering create_oci_artifact_continuouspatching with parameters: %s %s %s", registry, cssc_config_file, dryrun)

    try:
        oras_client = _oras_client(cmd, registry)
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
            oci_target_name = f"{CSSC_WORKFLOW_POLICY_REPOSITORY}/{CONTINUOSPATCH_OCI_ARTIFACT_CONFIG}:{CONTINUOSPATCH_OCI_ARTIFACT_CONFIG_TAG_DRYRUN}"
        else:
            oci_target_name = f"{CSSC_WORKFLOW_POLICY_REPOSITORY}/{CONTINUOSPATCH_OCI_ARTIFACT_CONFIG}:{CONTINUOSPATCH_OCI_ARTIFACT_CONFIG_TAG_V1}"

        oras_client.push(
            target=oci_target_name,
            files=[temp_artifact.name])
    except Exception as exception:
        raise AzCLIError(f"Failed to push OCI artifact to ACR: {exception}")
    finally:
        oras_client.logout(hostname=str.lower(registry.login_server))
        os.path.exists(temp_artifact_name) and os.remove(temp_artifact_name)


def delete_oci_artifact_continuous_patch(cmd, registry, dryrun):
    logger.debug("Entering delete_oci_artifact_continuous_patch with parameters %s %s", registry, dryrun)
    resourceid = parse_resource_id(registry.id)
    resource_group = resourceid[RESOURCE_GROUP]
    subscription = resourceid[SUBSCRIPTION]

    if dryrun:
        logger.warning("Dry run flag is set, no changes will be made")
        return
    try:
        token = _get_acr_token(registry.name, resource_group, subscription)

        # Delete repository, removing only image isn't deleting the repository always (Bug)
        acr_repository_delete(
            cmd=cmd,
            registry_name=registry.name,
            repository=f"{CSSC_WORKFLOW_POLICY_REPOSITORY}/{CONTINUOSPATCH_OCI_ARTIFACT_CONFIG}",
            # image=f"{CSSC_WORKFLOW_POLICY_REPOSITORY}/{CONTINUOSPATCH_OCI_ARTIFACT_CONFIG}:{CONTINUOSPATCH_OCI_ARTIFACT_CONFIG_TAG_V1}",
            username=BEARER_TOKEN_USERNAME,
            password=token,
            yes=not dryrun)
        logger.debug("Call to acr_repository_delete completed successfully")
    except Exception as exception:
        logger.debug("%s", exception)
        logger.error("%s/%s:%s might not existing or attempt to delete failed. Please verify once the presence of repository before attempting to re-delete.", CSSC_WORKFLOW_POLICY_REPOSITORY, CONTINUOSPATCH_OCI_ARTIFACT_CONFIG, CONTINUOSPATCH_OCI_ARTIFACT_CONFIG_TAG_V1)
        raise


def _oras_client(cmd, registry):
    resourceid = parse_resource_id(registry.id)
    resource_group = resourceid[RESOURCE_GROUP]
    subscription = resourceid[SUBSCRIPTION]

    try:
        token = _get_acr_token(registry.name, resource_group, subscription)
        client = OrasClient(hostname=str.lower(registry.login_server))
        client.login(BEARER_TOKEN_USERNAME, token)
    except Exception as exception:
        raise AzCLIError("Failed to login to Artifact Store ACR %s: %s ", registry.name, exception)

    return client


# Need to check on this method once, if there's alternative to this
def _get_acr_token(registry_name, resource_group, subscription):
    logger.debug("Using CLI user credentials to log into %s", registry_name)
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
        proc = subprocess.Popen(
            acr_login_with_token_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        token = proc.stdout.read().strip().decode("utf-8")
        # this suppresses the 'login' warning from the ACR request, if we need the error and does not come from the exception we can take it from here
        # error_stderr=proc.stderr.read()
    except subprocess.CalledProcessError as error:
        unauthorized = (
            error.stderr
            and (" 401" in error.stderr or "unauthorized" in error.stderr)
        ) or (
            error.stdout
            and (" 401" in error.stdout or "unauthorized" in error.stdout)
        )

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

    return token
