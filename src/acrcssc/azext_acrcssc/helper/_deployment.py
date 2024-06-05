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
from azure.mgmt.resource.resources.models import (
    DeploymentExtended,
    DeploymentProperties,
    DeploymentMode,
    Deployment
)

from knack.log import get_logger

logger = get_logger(__name__)
#need a parameter to enable/disable immediate run of the task

def deploy_task_via_sdk(cmd_ctx, registry, resource_group: str,
                        task_name: str, task_yaml: str, dryrun: Optional[bool] = False):
    # not sure how much I should invest in this, or just try to do it via a CLI, or force the arm deployment
    # task_client = cf_acr_tasks(cmd_ctx)
    # task_client.
    raise AzCLIError("Not implemented yet")

def validate_and_deploy_template(cmd_ctx, registry, resource_group: str, deployment_name: str,
                                 template_file_name: str, parameters: dict, dryrun: Optional[bool] = False):
    logger.debug("Validating and deploying template")
    logger.debug('Working with resource group %s, template %s', resource_group, template_file_name)

    deployment_path = os.path.dirname(
        os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)),
            "../templates/")) # needs to be a constant

    arm_path = os.path.join(deployment_path, "arm")
    template_path = os.path.join(arm_path, template_file_name)
    template = DeploymentProperties(
        template = get_file_json(template_path),
        parameters = parameters,
        mode=DeploymentMode.incremental)
    try:
        validate_template(cmd_ctx, resource_group, deployment_name, template)
        if (dryrun):
            logger.debug("Dry run, skipping deployment")
            return None

        return deploy_template(cmd_ctx, resource_group, deployment_name, template)
    except Exception as exception:
        logger.error('Failed to validate and deploy template: %s', exception)
        raise AzCLIError('Failed to validate and deploy template: %s' % exception)

def validate_template(cmd_ctx, resource_group, deployment_name, template):
    # Validation is automatically re-attempted in live runs, but not in test
    # playback, causing them to fail. This explicitly re-attempts validation to
    # ensure the tests pass
    api_clients = cf_resources(cmd_ctx)
    validation_res = None
    deployment = Deployment(
        properties = template,
        # tags = { "test": CSSC_TAGS }, #we need to know if tagging
        # is something that will help ust, tasks are proxy resources, 
        # so not sure how that would work
    )

    for validation_attempt in range(2):
        try:
            validation = (
                api_clients.deployments.begin_validate(
                    resource_group_name = resource_group,
                    deployment_name = deployment_name,
                    parameters = deployment
                )
            )
            validation_res = LongRunningOperation(
                cmd_ctx, "Validating ARM template..."
            )(validation)
            break
        except Exception:  # pylint: disable=broad-except
            if validation_attempt == 1:
                raise

    if not validation_res:
        # Don't expect to hit this but it appeases mypy
        raise RuntimeError(f"Validation of template {template} failed.")

    logger.debug("Validation Result %s", validation_res)
    if validation_res.error:
        # Validation failed so don't even try to deploy
        logger.error(
            (
                "Template for resource group %s has failed validation. The message"
                " was: %s. See logs for additional details."
            ),
            resource_group,
            validation_res.error.message,
        )
        logger.debug(
            (
                "Template for resource group %s failed validation."
                " Full error details: %s"
            ),
            resource_group,
            validation_res.error,
        )
        raise RuntimeError("Azure template validation failed.")

    # Validation succeeded so proceed with deployment
    logger.debug("Successfully validated resources for %s", resource_group)

def deploy_template(cmd_ctx, resource_group, deployment_name, template):
    api_client = cf_resources(cmd_ctx)
    
    deployment = Deployment(
        properties = template,
        # tags = { "test": CSSC_TAGS },
        #we need to know if tagging is something that will help ust,
        # tasks are proxy resources, so not sure how that would work
    )

    poller = api_client.deployments.begin_create_or_update(
            resource_group_name=resource_group,
            deployment_name=deployment_name,
            parameters = deployment
        )
    logger.debug(poller)

    # Wait for the deployment to complete and get the outputs
    deployment: DeploymentExtended = LongRunningOperation(
        cmd_ctx,
        "Deploying ARM template"
    )(poller)
    logger.debug("Finished deploying")

    if deployment.properties is not None:
        depl_props = deployment.properties
    else:
        raise RuntimeError("The deployment has no properties.\nAborting")
    logger.debug("Deployed: %s %s %s", deployment.name, deployment.id, depl_props)

    if depl_props.provisioning_state != "Succeeded":
        logger.debug("Failed to provision: %s", depl_props)
        raise RuntimeError(
            "Deploy of template to resource group"
            f" {resource_group} proceeded but the provisioning"
            f" state returned is {depl_props.provisioning_state}."
            "\nAborting"
        )
    logger.debug(
        "Provisioning state of deployment %s : %s",
        resource_group,
        depl_props.provisioning_state,
    )

    return depl_props.outputs
