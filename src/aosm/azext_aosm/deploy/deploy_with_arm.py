# --------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT
# License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------
"""Contains class for deploying generated definitions using the Python SDK."""
import json
import logging
import os
import shutil
import subprocess  # noqa
from functools import cached_property
from typing import Any, Dict

from knack.log import get_logger
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.v2021_04_01.models import DeploymentExtended

from azext_aosm.vendored_sdks import HybridNetworkManagementClient
from azext_aosm.vendored_sdks.models import (
    NetworkFunctionDefinitionVersion,
    NetworkServiceDesignVersion,
    ArtifactStoreType,
    ArtifactType,
    ArtifactManifest,
)
from azext_aosm.deploy.pre_deploy import PreDeployerViaSDK


logger = get_logger(__name__)


class DeployerViaArm:
    """A class to deploy Artifact Manifests, NFDs and NSDs from a bicep template using ARM."""
    # @@@TODO - not sure this class is required as we can't publish complex objects
    # using the SDK
    
    def __init__(
        self,
        aosm_client: HybridNetworkManagementClient,
        resource_client: ResourceManagementClient,
        subscription_id: str, 
        resource_group: str
    ) -> None:
        """
        Initializes a new instance of the Deployer class.

        :param aosm_client: The client to use for managing AOSM resources.
        :type aosm_client: HybridNetworkManagementClient
        :param resource_client: The client to use for managing Azure resources.
        :type resource_client: ResourceManagementClient
        """
        logger.debug("Create ARM/Bicep Deployer")
        self.aosm_client = aosm_client

        self.subscription_id = subscription_id
        self.credentials = DefaultAzureCredential()
        self.resource_group = resource_group
        self.pre_deployer = PreDeployerViaSDK(aosm_client, self.resource_client)
        
    @cached_property
    def resource_client(self) -> ResourceManagementClient:
        """
        Create a client that can create resources on Azure.

        :return: A ResourceManagementClient
        """
        logger.debug("Create resource client")
        return ResourceManagementClient(self.credentials, self.subscription_id)

    def deploy_bicep_template(
        self, bicep_template_path: str, parameters: Dict[Any, Any]
    ) -> Any:
        """
        Deploy a bicep template.

        :param bicep_template_path: Path to the bicep template
        :param parameters: Parameters for the bicep template
        """
        logger.info("Deploy %s", bicep_template_path)
        arm_template_json = self.convert_bicep_to_arm(bicep_template_path)

        return self.validate_and_deploy_arm_template(
            arm_template_json, parameters, self.resource_group
        )

    def resource_exists(self, resource_name: str) -> bool:
        """
        Determine if a resource with the given name exists.

        :param resource_name: The name of the resource to check.
        """
        logger.debug("Check if %s exists", resource_name)
        resources = self.resource_client.resources.list_by_resource_group(
            resource_group_name=self.resource_group
        )

        resource_exists = False

        for resource in resources:
            if resource.name == resource_name:
                resource_exists = True
                break

        return resource_exists

    def validate_and_deploy_arm_template(
        self, template: Any, parameters: Dict[Any, Any], resource_group: str
    ) -> Any:
        """
        Validate and deploy an individual ARM template.

        This ARM template will be created in the resource group passed in.

        :param template: The JSON contents of the template to deploy
        :param parameters: The JSON contents of the parameters file
        :param resource_group: The name of the resource group that has been deployed

        :raise RuntimeError if validation or deploy fails
        :return: Output dictionary from the bicep template.
        """
        deployment_name = f"nfd_into_{resource_group}"

        validation = self.resource_client.deployments.begin_validate(
            resource_group_name=resource_group,
            deployment_name=deployment_name,
            parameters={
                "properties": {
                    "mode": "Incremental",
                    "template": template,
                    "parameters": parameters,
                }
            },
        )

        validation_res = validation.result()
        logger.debug(f"Validation Result {validation_res}")
        if validation_res.error:
            # Validation failed so don't even try to deploy
            logger.error(
                f"Template for resource group {resource_group} "
                f"has failed validation. The message was: "
                f"{validation_res.error.message}. See logs for additional details."
            )
            logger.debug(
                f"Template for resource group {resource_group} "
                f"failed validation. Full error details: {validation_res.error}."
            )
            raise RuntimeError("Azure template validation failed.")

        # Validation succeeded so proceed with deployment
        logger.debug(f"Successfully validated resources for {resource_group}")

        poller = self.resource_client.deployments.begin_create_or_update(
            resource_group_name=resource_group,
            deployment_name=deployment_name,
            parameters={
                "properties": {
                    "mode": "Incremental",
                    "template": template,
                    "parameters": parameters,
                }
            },
        )
        logger.debug(poller)

        # Wait for the deployment to complete and get the outputs
        deployment: DeploymentExtended = poller.result()

        if deployment.properties is not None:
            depl_props = deployment.properties
        else:
            raise RuntimeError("The deployment has no properties.\nAborting")
        logger.debug(f"Deployed: {deployment.name} {deployment.id} {depl_props}")

        if depl_props.provisioning_state != "Succeeded":
            logger.debug(f"Failed to provision: {depl_props}")
            raise RuntimeError(
                f"Deploy of template to resource group"
                f" {resource_group} proceeded but the provisioning"
                f" state returned is {depl_props.provisioning_state}. "
                f"\nAborting"
            )
        logger.debug(
            f"Provisioning state of {resource_group}"
            f": {depl_props.provisioning_state}"
        )

        return depl_props.outputs

    def convert_bicep_to_arm(self, bicep_template: str) -> Any:
        """
        Convert a bicep template into an ARM template.

        :param bicep_template: The path to the bicep template to be converted

        :raise RuntimeError if az CLI is not installed.
        :return: Output dictionary from the bicep template.
        """
        if not shutil.which("az"):
            logger.error(
                "The Azure CLI is not installed - follow "
                "https://github.com/Azure/bicep/blob/main/docs/installing.md#linux"
            )
            raise RuntimeError(
                "The Azure CLI is not installed - cannot render ARM templates."
            )
        logger.debug(f"Converting {bicep_template} to ARM template")

        arm_template_name = bicep_template.replace(".bicep", ".json")

        try:
            bicep_output = subprocess.run(  # noqa
                [
                    str(shutil.which("az")),
                    "bicep",
                    "build",
                    "--file",
                    bicep_template,
                    "--outfile",
                    arm_template_name,
                ],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            logger.debug("az bicep output: %s", str(bicep_output))
        except subprocess.CalledProcessError as e:
            logger.error(
                "ARM template compilation failed! See logs for full "
                "output. The failing command was %s",
                e.cmd,
            )
            logger.debug("bicep build stdout: %s", e.stdout)
            logger.debug("bicep build stderr: %s", e.stderr)
            raise

        with open(arm_template_name, "r", encoding="utf-8") as template_file:
            arm_json = json.loads(template_file.read())

        os.remove(arm_template_name)

        return arm_json
        
