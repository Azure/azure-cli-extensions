# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import time
import json
from dataclasses import asdict
from typing import Any, Dict
from pathlib import Path
from azure.cli.core import AzCli
from azure.cli.core.azclierror import AzCLIError
from azure.cli.core.commands import LongRunningOperation
from azure.core import exceptions as azure_exceptions
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import DeploymentExtended
from knack.log import get_logger
from azext_aosm.common.command_context import CommandContext
from azext_aosm.common.utils import convert_bicep_to_arm
from azext_aosm.configuration_models.common_parameters_config import (
    BaseCommonParametersConfig,
    CoreVNFCommonParametersConfig,
    NFDCommonParametersConfig,
    NSDCommonParametersConfig
)
from azext_aosm.definition_folder.reader.base_definition import BaseDefinitionElement
from azext_aosm.common.constants import ManifestsExist

logger = get_logger(__name__)


class BicepDefinitionElement(BaseDefinitionElement):
    """Bicep definition"""

    @staticmethod
    def _validate_and_deploy_arm_template(
        cli_ctx: AzCli,
        template: Any,
        parameters: Dict[Any, Any],
        resource_group: str,
        resource_client: ResourceManagementClient,
    ) -> Any:
        """
        Validate and deploy an individual ARM template.

        This ARM template will be created in the resource group passed in.

        :param template: The JSON contents of the template to deploy
        :param parameters: The JSON contents of the parameters file
        :param resource_group: The name of the resource group that has been deployed

        :return: Output dictionary from the bicep template.
        :raise RuntimeError if validation or deploy fails
        """
        # Add a timestamp to the deployment name to ensure it is unique
        current_time = int(time.time())
        deployment_name = f"AOSM_CLI_deployment_{current_time}"

        # Validation is automatically re-attempted in live runs, but not in test
        # playback, causing them to fail. This explicitly re-attempts validation to
        # ensure the tests pass
        validation_res = None
        for validation_attempt in range(2):
            try:
                validation = resource_client.deployments.begin_validate(
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
                validation_res = LongRunningOperation(
                    cli_ctx, "Validating ARM template..."
                )(validation)
                break
            except azure_exceptions.HttpResponseError as e:
                logger.error(
                    "When attempting to validate an ARM template, we hit an error."
                    " Do you have the permissions required by AOSM (see documentation)?"
                    "\n\nOriginal error:"
                )
                raise e
            except Exception:  # pylint: disable=broad-except
                if validation_attempt == 1:
                    raise

        if not validation_res or validation_res.error:
            raise RuntimeError(f"Validation of template {template} failed.")

        # Validation succeeded so proceed with deployment
        poller = resource_client.deployments.begin_create_or_update(
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

        # Wait for the deployment to complete and get the outputs
        deployment: DeploymentExtended = LongRunningOperation(
            cli_ctx, "Deploying ARM template"
        )(poller)

        if deployment.properties is None:
            raise RuntimeError("The deployment has no properties.\nAborting")

        if deployment.properties.provisioning_state != "Succeeded":
            raise RuntimeError(
                "Deploy of template to resource group"
                f" {resource_group} proceeded but the provisioning"
                f" state returned is {deployment.properties.provisioning_state}."
                "\nAborting"
            )

        return deployment.properties.outputs

    @staticmethod
    def _artifact_manifests_exist(
        config: BaseCommonParametersConfig, command_context: CommandContext
    ) -> ManifestsExist:
        """

        Returns True if all required manifests exist, False if none do, and raises an
        AzCLIError if some but not all exist.

        Current code only allows one manifest for ACR, and one manifest for SA (if applicable),
        so that's all we check for.
        """
        try:
            command_context.aosm_client.artifact_manifests.get(
                resource_group_name=config.publisherResourceGroupName,
                publisher_name=config.publisherName,
                artifact_store_name=config.acrArtifactStoreName,
                artifact_manifest_name=config.acrManifestName,
            )
            acr_manifest_exists = True
        except azure_exceptions.ResourceNotFoundError:
            acr_manifest_exists = False
        # TODO: test config type change works
        if isinstance(config, CoreVNFCommonParametersConfig):
            try:
                command_context.aosm_client.artifact_manifests.get(
                    resource_group_name=config.publisherResourceGroupName,
                    publisher_name=config.publisherName,
                    artifact_store_name=config.saArtifactStoreName,
                    artifact_manifest_name=config.saManifestName,
                )
                sa_manifest_exists = True
            except azure_exceptions.ResourceNotFoundError:
                sa_manifest_exists = False

            if acr_manifest_exists != sa_manifest_exists:
                return ManifestsExist.SOME

        if acr_manifest_exists:
            return ManifestsExist.ALL

        return ManifestsExist.NONE

    @staticmethod
    def _base_resources_exist(
        config: BaseCommonParametersConfig, command_context: CommandContext
    ) -> bool:
        """

        Returns True if all base resources exist, False if even one does not.

        Current code only allows one manifest for ACR, and one manifest for SA (if applicable),
        so that's all we check for.
        """
        try:
            command_context.aosm_client.publishers.get(
                resource_group_name=config.publisherResourceGroupName,
                publisher_name=config.publisherName,
            )
        except azure_exceptions.ResourceNotFoundError:
            return False

        try:
            command_context.aosm_client.artifact_stores.get(
                resource_group_name=config.publisherResourceGroupName,
                publisher_name=config.publisherName,
                artifact_store_name=config.acrArtifactStoreName,
            )
        except azure_exceptions.ResourceNotFoundError:
            return False

        if isinstance(config, NFDCommonParametersConfig):
            try:
                command_context.aosm_client.network_function_definition_groups.get(
                    resource_group_name=config.publisherResourceGroupName,
                    publisher_name=config.publisherName,
                    network_function_definition_group_name=config.nfDefinitionGroup,
                )
            except azure_exceptions.ResourceNotFoundError:
                return False

        if isinstance(config, CoreVNFCommonParametersConfig):
            try:
                command_context.aosm_client.storage_accounts.get(
                    resource_group_name=config.publisherResourceGroupName,
                    publisher_name=config.publisherName,
                    storgae_account_name=config.saArtifactStoreName,
                )
            except azure_exceptions.ResourceNotFoundError:
                return False

        if isinstance(config, NSDCommonParametersConfig):
            try:
                command_context.aosm_client.network_service_design_groups.get(
                    resource_group_name=config.publisherResourceGroupName,
                    publisher_name=config.publisherName,
                    network_service_design_group_name=config.nsDesignGroup,
                )
            except azure_exceptions.ResourceNotFoundError:
                return False

        return True

    def deploy(
        self, config: BaseCommonParametersConfig, command_context: CommandContext
    ):
        """Deploy the element."""
        # TODO: Deploying base takes about 4 minutes, even if everything is already deployed.
        # artifact manifests return an error if it already exists, so they need special handling.
        # Currently, _only_ manifests are special, but if we need to add any more custom code,
        # breaking this into a separate class (like we do for artifacts) is probably the right
        # thing to do.
        if self.path.name == "base":
            base_resources_exist = self._base_resources_exist(
                config=config, command_context=command_context
            )
            if base_resources_exist:
                logger.info("Base resources already exist; skipping deployment.")
                return

        if self.path.name == "artifactManifest":
            manifests_exist = self._artifact_manifests_exist(
                config=config, command_context=command_context
            )
            if manifests_exist == ManifestsExist.ALL:  # pylint: disable=no-else-return
                # The manifest(s) already exist so nothing else to do for this template
                logger.info("Artifact manifest(s) already exist; skipping deployment.")
                return
            elif manifests_exist == ManifestsExist.SOME:
                # We don't know why we're in this state, and the safest thing to do is to delete
                # the NFDV/NSDV and start again, but we shouldn't do this ourselves.
                raise AzCLIError(
                    "Unexpected state: A subset of artifact manifest exists; expected"
                    " all or none so cannot proceed.\nPlease delete the NFDV or NSDV"
                    " (as appropriate) using the `az aosm nfd delete` or `az aosm nsd"
                    " delete` command."
                )
            else:
                assert manifests_exist == ManifestsExist.NONE
                # If none of the manifests exist, we can just go ahead and deploy the template
                # as normal.

        logger.info(
            "Converting bicep to ARM for '%s' template. This can take a few seconds.",
            self.path.name,
        )
        arm_json = convert_bicep_to_arm(self.path / "deploy.bicep")
        logger.info("Deploying ARM template for %s", self.path.name)

        # TODO: handle creating the resource group if it doesn't exist

        # Create the deploy parameters with only the parameters needed by this template
        parameters_in_template = arm_json["parameters"]
        parameters = {
            k: {"value": v}
            for (k, v) in asdict(config).items()
            if k in parameters_in_template
        }

        if self.path.name == "snsDefinition":
            resource_group_name = config.operatorResourceGroupName
            with open(Path(self.path).parent / 'deploy_input.jsonc', 'r') as f:
                data = json.load(f)
            # Get the 'nfvis' value
            nfvis_value = data.get('nfvis_list', [])
            cgvs = data.get('cgv_list', [])
            # Ensure 'nfvis_value' is an object
            if isinstance(nfvis_value, str):
                nfvis_value = json.loads(nfvis_value)
            if isinstance(cgvs, str):
                cgvs = json.loads(cgvs)
            logger.debug("NFVIS Value: %s", nfvis_value)
            parameters['nfviList'] = {"value": nfvis_value}
            parameters['cgvs'] = {"value": cgvs}
        else:
            resource_group_name = config.publisherResourceGroupName

        logger.debug("All parameters provided by user: %s", config)
        logger.debug(
            "Parameters required by %s in built ARM template:%s ",
            self.path.name,
            parameters_in_template,
        )
        logger.debug("Filtered parameters: %s", parameters)

        self._validate_and_deploy_arm_template(
            cli_ctx=command_context.cli_ctx,
            template=arm_json,
            parameters=parameters,
            resource_group=resource_group_name,
            resource_client=command_context.resources_client,
        )

    def delete(
        self, config: BaseCommonParametersConfig, command_context: CommandContext
    ):
        """Delete the element."""
        # TODO: Implement.
        raise NotImplementedError
