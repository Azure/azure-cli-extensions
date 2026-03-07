# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""A module to handle deployment functions related to tasks."""
import os
from typing import Optional
from .._client_factory import cf_resources
from azure.cli.core.util import get_file_json
from azure.cli.core.azclierror import AzCLIError
from azure.cli.core.commands import LongRunningOperation
from azure.mgmt.resource.deployments.models import (
    DeploymentExtended,
    DeploymentProperties,
    DeploymentMode,
    Deployment
)
from knack.log import get_logger
# pylint: disable=line-too-long
# pylint: disable=logging-fstring-interpolation
logger = get_logger(__name__)


def validate_and_deploy_template(cmd_ctx,
                                 registry,
                                 resource_group: str,
                                 deployment_name: str,
                                 template_file_name: str,
                                 parameters: dict,
                                 dryrun: Optional[bool] = False):
    logger.debug(f'Working with resource group {resource_group}, registry {registry} template {template_file_name}')

    deployment_path = os.path.dirname(
        os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)),
            "../templates/"))

    arm_path = os.path.join(deployment_path, "arm")
    template_path = os.path.join(arm_path, template_file_name)
    template = DeploymentProperties(
        template=get_file_json(template_path),
        parameters=parameters,
        mode=DeploymentMode.incremental)
    try:
        validate_template(cmd_ctx, resource_group, deployment_name, template)
        if dryrun:
            logger.debug("Dry run, skipping deployment")
            return None

        return deploy_template(cmd_ctx, resource_group, deployment_name, template)
    except Exception as exception:
        raise AzCLIError(f'Failed to validate and deploy template: {exception}')


def validate_template(cmd_ctx, resource_group, deployment_name, template):
    # Validation is automatically re-attempted in live runs, but not in test
    # playback, causing them to fail. This explicitly re-attempts validation to
    # ensure the tests pass
    api_clients = cf_resources(cmd_ctx)
    validation_res = None
    deployment = Deployment(
        properties=template
    )

    for validation_attempt in range(2):
        try:
            validation = (
                api_clients.deployments.begin_validate(
                    resource_group_name=resource_group,
                    deployment_name=deployment_name,
                    parameters=deployment
                )
            )
            validation_res = LongRunningOperation(
                cmd_ctx, "Validating ARM template..."
            )(validation)
            break
        except Exception as exception:  # pylint: disable=broad-except
            logger.debug(f"Validation attempt {validation_attempt + 1} failed for template {template}, exception: {exception}")
            if validation_attempt == 1:
                raise

    if not validation_res:
        # Don't expect to hit this but it appeases mypy
        raise RuntimeError(f"Validation of template {template} failed.")

    logger.debug(f"Validation Result {validation_res}")
    if validation_res.error:
        # Validation failed so don't even try to deploy
        logger.error(
            (
                f"Template for resource group {resource_group} has failed validation. The message"
                f" was: {validation_res.error.message}. See logs for additional details."
            )
        )
        logger.debug(
            (
                f"Template for resource group {resource_group} failed validation."
                f" Full error details: {validation_res.error}"
            )
        )
        raise RuntimeError("Azure template validation failed.")

    # Validation succeeded so proceed with deployment
    logger.debug(f"Successfully validated resources for {resource_group}")


def deploy_template(cmd_ctx, resource_group, deployment_name, template):
    api_client = cf_resources(cmd_ctx)

    deployment = Deployment(
        properties=template
    )

    poller = api_client.deployments.begin_create_or_update(
        resource_group_name=resource_group,
        deployment_name=deployment_name,
        parameters=deployment)

    # Wait for the deployment to complete and get the outputs
    deployment: DeploymentExtended = LongRunningOperation(
        cmd_ctx
    )(poller)
    logger.debug("Finished deploying")

    if deployment.properties is None:
        raise RuntimeError("The deployment has no properties.\nAborting")

    depl_props = deployment.properties
    logger.debug(f"Deployed: {deployment.name} {deployment.id} {depl_props}")

    if depl_props.provisioning_state != "Succeeded":
        logger.error(f"Failed to provision: {depl_props}")
        raise RuntimeError(
            "Deploy of template to resource group"
            f" {resource_group} proceeded but the provisioning"
            f" state returned is {depl_props.provisioning_state}."
            "\nAborting"
        )
    logger.debug(f"Provisioning state of deployment {resource_group} : {depl_props.provisioning_state}")

    return depl_props.outputs
