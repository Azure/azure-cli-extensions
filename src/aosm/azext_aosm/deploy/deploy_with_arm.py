# --------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT
# License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------
"""Contains class for deploying generated definitions using ARM."""
import json
import os
import shutil
import subprocess  # noqa
from typing import Any, Dict, Optional
import tempfile
import time

from knack.log import get_logger
from azure.mgmt.resource.resources.models import DeploymentExtended

from azext_aosm.deploy.artifact_manifest import ArtifactManifestOperator
from azext_aosm.util.management_clients import ApiClients
from azext_aosm.deploy.pre_deploy import PreDeployerViaSDK
from azext_aosm._configuration import NFConfiguration, NSConfiguration, VNFConfiguration
from azext_aosm.util.constants import (
    NSD_DEFINITION_BICEP_FILE,
    NSD_ARTIFACT_MANIFEST_BICEP_FILE,
    NF_DEFINITION_BICEP_FILE,
    VNF_DEFINITION_BICEP_TEMPLATE,
    VNF_MANIFEST_BICEP_TEMPLATE,
    NSD,
    VNF,
)



logger = get_logger(__name__)


class DeployerViaArm:
    """
    A class to deploy Artifact Manifests, NFDs and NSDs from bicep templates using ARM.

    Uses the SDK to pre-deploy less complex resources and then ARM to deploy the bicep
    templates.
    """

    def __init__(
        self,
        api_clients: ApiClients,
        config: NFConfiguration or NSConfiguration,
    ) -> None:
        """
        Initializes a new instance of the Deployer class.

        :param api_clients: ApiClients object for AOSM and ResourceManagement
        :param config: The configuration for this NF
        """
        logger.debug("Create ARM/Bicep Deployer")
        self.api_clients = api_clients
        self.config = config
        self.pre_deployer = PreDeployerViaSDK(api_clients, self.config)

    def deploy_vnfd_from_bicep(
        self,
        bicep_path: Optional[str] = None,
        parameters_json_file: Optional[str] = None,
        manifest_bicep_path: Optional[str] = None,
        manifest_parameters_json_file: Optional[str] = None,
    ) -> None:
        """
        Deploy the bicep template defining the VNFD.

        Also ensure that all required predeploy resources are deployed.

        :param bicep_template_path: The path to the bicep template of the nfdv :type
        bicep_template_path: str :parameters_json_
        file:
        path to an override file of set parameters for the nfdv        :param
        manifest_bicep_path: The path to the bicep template of the manifest
        :manifest_parameters_json_
        file:
        :param bicep_template_path: The path to the bicep template of the nfdv
        :type bicep_template_path: str
        :parameters_json_file: path to an override file of set parameters for the nfdv
        :param manifest_bicep_path: The path to the bicep template of the manifest
        :manifest_parameters_json_file: path to an override file of set parameters for
                the manifest
        """
        assert isinstance(self.config, VNFConfiguration)

        if not bicep_path:
            # User has not passed in a bicep template, so we are deploying the default
            # one produced from building the NFDV using this CLI
            bicep_path = os.path.join(
                self.config.build_output_folder_name,
                VNF_DEFINITION_BICEP_TEMPLATE,
            )

        if parameters_json_file:
            message = f"Use parameters from file {parameters_json_file}"
            logger.info(message)
            print(message)
            with open(parameters_json_file, "r", encoding="utf-8") as f:
                parameters = json.loads(f.read())

        else:
            # User has not passed in parameters file, so we use the parameters required
            # from config for the default bicep template produced from building the
            # NFDV using this CLI
            logger.debug("Create parameters for default NFDV template.")
            parameters = self.construct_vnfd_parameters()

        logger.debug(parameters)

        # Create or check required resources
        deploy_manifest_template = not self.vnfd_predeploy()
        if deploy_manifest_template:
            self.deploy_manifest_template(
                manifest_parameters_json_file, manifest_bicep_path, VNF
            )
        else:
            print(
                f"Artifact manifests exist for NFD {self.config.nf_name} "
                f"version {self.config.version}"
            )
        message = (
            f"Deploy bicep template for NFD {self.config.nf_name} version {self.config.version} "
            f"into {self.config.publisher_resource_group_name} under publisher "
            f"{self.config.publisher_name}"
        )
        print(message)
        logger.info(message)
        self.deploy_bicep_template(bicep_path, parameters)
        print(f"Deployed NFD {self.config.nf_name} version {self.config.version}.")

        storage_account_manifest = ArtifactManifestOperator(
            self.config,
            self.api_clients,
            self.config.blob_artifact_store_name,
            self.config.sa_manifest_name,
        )
        acr_manifest = ArtifactManifestOperator(
            self.config,
            self.api_clients,
            self.config.acr_artifact_store_name,
            self.config.acr_manifest_name,
        )

        vhd_artifact = storage_account_manifest.artifacts[0]
        arm_template_artifact = acr_manifest.artifacts[0]

        print("Uploading VHD artifact")
        vhd_artifact.upload(self.config.vhd)
        print("Uploading ARM template artifact")
        arm_template_artifact.upload(self.config.arm_template)
        print("Done")

    def vnfd_predeploy(self) -> bool:
        """
        All the predeploy steps for a VNF. Create publisher, artifact stores and NFDG.

        VNF specific return True if artifact manifest already exists, False otherwise
        """
        logger.debug("Ensure all required resources exist")
        self.pre_deployer.ensure_config_resource_group_exists()
        self.pre_deployer.ensure_config_publisher_exists()
        self.pre_deployer.ensure_acr_artifact_store_exists()
        self.pre_deployer.ensure_sa_artifact_store_exists()
        self.pre_deployer.ensure_config_nfdg_exists()
        return self.pre_deployer.do_config_artifact_manifests_exist()

    def construct_vnfd_parameters(self) -> Dict[str, Any]:
        """
        Create the parmeters dictionary for vnfdefinitions.bicep. VNF specific.

        :param config: The contents of the configuration file.
        """
        assert isinstance(self.config, VNFConfiguration)
        return {
            "location": {"value": self.config.location},
            "publisherName": {"value": self.config.publisher_name},
            "acrArtifactStoreName": {"value": self.config.acr_artifact_store_name},
            "saArtifactStoreName": {"value": self.config.blob_artifact_store_name},
            "nfName": {"value": self.config.nf_name},
            "nfDefinitionGroup": {"value": self.config.nfdg_name},
            "nfDefinitionVersion": {"value": self.config.version},
            "vhdVersion": {"value": self.config.vhd.version},
            "armTemplateVersion": {"value": self.config.arm_template.version},
        }

    def construct_manifest_parameters(self) -> Dict[str, Any]:
        """Create the parmeters dictionary for VNF or NSD."""
        if isinstance(self.config, VNFConfiguration):
            return {
                "location": {"value": self.config.location},
                "publisherName": {"value": self.config.publisher_name},
                "acrArtifactStoreName": {"value": self.config.acr_artifact_store_name},
                "saArtifactStoreName": {"value": self.config.blob_artifact_store_name},
                "acrManifestName": {"value": self.config.acr_manifest_name},
                "saManifestName": {"value": self.config.sa_manifest_name},
                "vhdName": {"value": self.config.vhd.artifact_name},
                "vhdVersion": {"value": self.config.vhd.version},
                "armTemplateName": {"value": self.config.arm_template.artifact_name},
                "armTemplateVersion": {"value": self.config.arm_template.version},
            }
        if isinstance(self.config, NSConfiguration):
            return {
                "location": {"value": self.config.location},
                "publisherName": {"value": self.config.publisher_name},
                "acrArtifactStoreName": {"value": self.config.acr_artifact_store_name},
                "acrManifestName": {"value": self.config.acr_manifest_name},
                "armTemplateName": {"value": self.config.arm_template.artifact_name},
                "armTemplateVersion": {"value": self.config.arm_template.version},
            }
        raise ValueError("Unknown configuration type")

    def deploy_nsd_from_bicep(
        self,
        bicep_path: Optional[str] = None,
        parameters_json_file: Optional[str] = None,
        manifest_bicep_path: Optional[str] = None,
        manifest_parameters_json_file: Optional[str] = None,
    ) -> None:
        """
        Deploy the bicep template defining the VNFD.

        Also ensure that all required predeploy resources are deployed.

        :param bicep_template_path: The path to the bicep template of the nfdv
        :type bicep_template_path: str
        :parameters_json_file: path to an override file of set parameters for the nfdv
        :param manifest_bicep_path: The path to the bicep template of the manifest
        :param manifest_parameters_json_file: path to an override file of set parameters for the manifest
        """
        assert isinstance(self.config, NSConfiguration)

        if not bicep_path:
            # User has not passed in a bicep template, so we are deploying the default
            # one produced from building the NSDV using this CLI
            bicep_path = os.path.join(
                self.config.build_output_folder_name,
                NSD_DEFINITION_BICEP_FILE,
            )

        if parameters_json_file:
            message = f"Use parameters from file {parameters_json_file}"
            logger.info(message)
            print(message)
            with open(parameters_json_file, "r", encoding="utf-8") as f:
                parameters = json.loads(f.read())

        else:
            # User has not passed in parameters file, so we use the parameters required
            # from config for the default bicep template produced from building the
            # NSDV using this CLI
            logger.debug("Create parameters for default NSDV template.")
            parameters = self.construct_nsd_parameters()

        logger.debug(parameters)

        # Create or check required resources
        deploy_manifest_template = not self.nsd_predeploy()

        if deploy_manifest_template:
            self.deploy_manifest_template(
                manifest_parameters_json_file, manifest_bicep_path, NSD
            )
        else:
            print(f"Artifact manifests {self.config.acr_manifest_name} already exists")

        message = (
            f"Deploy bicep template for NSDV {self.config.nsd_version} "
            f"into {self.config.publisher_resource_group_name} under publisher "
            f"{self.config.publisher_name}"
        )
        print(message)
        logger.info(message)
        self.deploy_bicep_template(bicep_path, parameters)
        print(
            f"Deployed NSD {self.config.acr_manifest_name} version {self.config.nsd_version}."
        )
        acr_manifest = ArtifactManifestOperator(
            self.config,
            self.api_clients,
            self.config.acr_artifact_store_name,
            self.config.acr_manifest_name,
        )

        arm_template_artifact = acr_manifest.artifacts[0]

        ## Convert the NF bicep to ARM
        arm_template_artifact_json = self.convert_bicep_to_arm(
            os.path.join(self.config.build_output_folder_name, NF_DEFINITION_BICEP_FILE)
        )

        with open(self.config.arm_template.file_path, "w", encoding="utf-8") as file:
            file.write(json.dumps(arm_template_artifact_json, indent=4))

        print("Uploading ARM template artifact")
        arm_template_artifact.upload(self.config.arm_template)
        print("Done")

    def deploy_manifest_template(
        self, manifest_parameters_json_file, manifest_bicep_path, configuration_type
    ) -> None:
        """
        Deploy the bicep template defining the manifest.

        :param manifest_parameters_json_file: path to an override file of set parameters for the manifest
        :param manifest_bicep_path: The path to the bicep template of the manifest
        :param configuration_type: The type of configuration to deploy
        """
        print("Deploy bicep template for Artifact manifests")
        logger.debug("Deploy manifest bicep")

        if not manifest_bicep_path:
            if configuration_type == NSD:
                file_name = NSD_ARTIFACT_MANIFEST_BICEP_FILE
            elif configuration_type == VNF:
                file_name = VNF_MANIFEST_BICEP_TEMPLATE

            manifest_bicep_path = os.path.join(
                self.config.build_output_folder_name,
                file_name,
            )
        if not manifest_parameters_json_file:
            manifest_params = self.construct_manifest_parameters()
        else:
            logger.info("Use provided manifest parameters")
            with open(manifest_parameters_json_file, "r", encoding="utf-8") as f:
                manifest_params = json.loads(f.read())
        self.deploy_bicep_template(manifest_bicep_path, manifest_params)

    def nsd_predeploy(self) -> bool:
        """
        All the predeploy steps for a NSD. Check if the RG, publisher, ACR, NSDG and
        artifact manifest exist.

        Return True if artifact manifest already exists, False otherwise
        """
        logger.debug("Ensure all required resources exist")
        self.pre_deployer.ensure_config_resource_group_exists()
        self.pre_deployer.ensure_config_publisher_exists()
        self.pre_deployer.ensure_acr_artifact_store_exists()
        self.pre_deployer.ensure_config_nsdg_exists()
        return self.pre_deployer.do_config_artifact_manifests_exist()

    def construct_nsd_parameters(self) -> Dict[str, Any]:
        """Create the parmeters dictionary for nsd_definition.bicep."""
        assert isinstance(self.config, NSConfiguration)
        return {
            "location": {"value": self.config.location},
            "publisherName": {"value": self.config.publisher_name},
            "acrArtifactStoreName": {"value": self.config.acr_artifact_store_name},
            "nsDesignGroup": {"value": self.config.nsdg_name},
            "nsDesignVersion": {"value": self.config.nsd_version},
            "nfviSiteName": {"value": self.config.nfvi_site_name},
            "armTemplateVersion": {"value": self.config.arm_template.version},
        }

    def deploy_bicep_template(
        self, bicep_template_path: str, parameters: Dict[Any, Any]
    ) -> Any:
        """
        Deploy a bicep template.

        :param bicep_template_path: Path to the bicep template
        :param parameters: Parameters for the bicep template         :return Any output
                that the template produces
        """
        logger.info("Deploy %s", bicep_template_path)
        arm_template_json = self.convert_bicep_to_arm(bicep_template_path)

        return self.validate_and_deploy_arm_template(
            arm_template_json, parameters, self.config.publisher_resource_group_name
        )

    def resource_exists(self, resource_name: str) -> bool:
        """
        Determine if a resource with the given name exists.

        :param resource_name: The name of the resource to check.
        """
        logger.debug("Check if %s exists", resource_name)
        resources = self.api_clients.resource_client.resources.list_by_resource_group(
            resource_group_name=self.config.publisher_resource_group_name
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
        # Get current time from the time module and remove all digits after the decimal point
        current_time = str(time.time()).split(".")[0] # pylint: disable=use-maxsplit-arg

        # Add a timestamp to the deployment name to ensure it is unique
        deployment_name = f"AOSM_CLI_deployment_into_{resource_group}_{current_time}"

        validation = self.api_clients.resource_client.deployments.begin_validate(
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
        logger.debug("Validation Result %s", validation_res)
        if validation_res.error:
            # Validation failed so don't even try to deploy
            logger.error(
                "Template for resource group %s has failed validation. The message was: %s.\
                See logs for additional details.", resource_group, validation_res.error.message
            )
            logger.debug(
                "Template for resource group %s failed validation. \
                Full error details: %s",resource_group,validation_res.error
            )
            raise RuntimeError("Azure template validation failed.")

        # Validation succeeded so proceed with deployment
        logger.debug("Successfully validated resources for %s", resource_group)

        poller = self.api_clients.resource_client.deployments.begin_create_or_update(
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
        logger.debug("Finished deploying")

        if deployment.properties is not None:
            depl_props = deployment.properties
        else:
            raise RuntimeError("The deployment has no properties.\nAborting")
        logger.debug("Deployed: %s %s %s", deployment.name, deployment.id, depl_props)

        if depl_props.provisioning_state != "Succeeded":
            logger.debug("Failed to provision: %s", depl_props)
            raise RuntimeError(
                f"Deploy of template to resource group"
                f" {resource_group} proceeded but the provisioning"
                f" state returned is {depl_props.provisioning_state}. "
                f"\nAborting"
            )
        logger.debug(
            "Provisioning state of deployment %s : %s", resource_group, depl_props.provisioning_state
        )

        return depl_props.outputs

    def convert_bicep_to_arm(self, bicep_template_path: str) -> Any:
        """
        Convert a bicep template into an ARM template.

        :param bicep_template_path: The path to the bicep template to be converted
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
        logger.debug("Converting %s to ARM template", bicep_template_path)

        with tempfile.TemporaryDirectory() as tmpdir:
            bicep_filename = os.path.basename(bicep_template_path)
            arm_template_name = bicep_filename.replace(".bicep", ".json")

            try:
                bicep_output = subprocess.run(  # noqa
                    [
                        str(shutil.which("az")),
                        "bicep",
                        "build",
                        "--file",
                        bicep_template_path,
                        "--outfile",
                        os.path.join(tmpdir, arm_template_name),
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

            with open(
                os.path.join(tmpdir, arm_template_name), "r", encoding="utf-8"
            ) as template_file:
                arm_json = json.loads(template_file.read())

        return arm_json
