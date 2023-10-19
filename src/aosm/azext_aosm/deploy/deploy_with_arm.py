# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Contains class for deploying generated definitions using ARM."""
import json
import os
import shutil
import subprocess  # noqa
import tempfile
import time
from typing import Any, Dict, Optional

from azure.cli.core.azclierror import ValidationError
from azure.cli.core.commands import LongRunningOperation
from azure.mgmt.resource.resources.models import DeploymentExtended
from knack.log import get_logger
from knack.util import CLIError

from azext_aosm._configuration import (
    ArtifactConfig,
    CNFConfiguration,
    Configuration,
    NFConfiguration,
    NFDRETConfiguration,
    NSConfiguration,
    VNFConfiguration,
)
from azext_aosm.deploy.artifact import Artifact
from azext_aosm.deploy.artifact_manifest import ArtifactManifestOperator
from azext_aosm.deploy.pre_deploy import PreDeployerViaSDK
from azext_aosm.util.constants import (
    ARTIFACT_UPLOAD,
    BICEP_PUBLISH,
    CNF,
    CNF_DEFINITION_BICEP_TEMPLATE_FILENAME,
    CNF_MANIFEST_BICEP_TEMPLATE_FILENAME,
    IMAGE_UPLOAD,
    NSD,
    NSD_ARTIFACT_MANIFEST_BICEP_FILENAME,
    NSD_BICEP_FILENAME,
    VNF,
    VNF_DEFINITION_BICEP_TEMPLATE_FILENAME,
    VNF_MANIFEST_BICEP_TEMPLATE_FILENAME,
    DeployableResourceTypes,
    SkipSteps,
)
from azext_aosm.util.management_clients import ApiClients

logger = get_logger(__name__)


class DeployerViaArm:  # pylint: disable=too-many-instance-attributes
    """
    A class to deploy Artifact Manifests, NFDs and NSDs from bicep templates using ARM.

    Uses the SDK to pre-deploy less complex resources and then ARM to deploy the bicep
    templates.
    """

    def __init__(
        self,
        api_clients: ApiClients,
        resource_type: DeployableResourceTypes,
        config: Configuration,
        bicep_path: Optional[str] = None,
        parameters_json_file: Optional[str] = None,
        manifest_bicep_path: Optional[str] = None,
        manifest_params_file: Optional[str] = None,
        skip: Optional[SkipSteps] = None,
        cli_ctx: Optional[object] = None,
        use_manifest_permissions: bool = False,
    ):
        """
        :param api_clients: ApiClients object for AOSM and ResourceManagement
        :param config: The configuration for this NF
        :param bicep_path: The path to the bicep template of the nfdv
        :param parameters_json_file: path to an override file of set parameters for the nfdv
        :param manifest_bicep_path: The path to the bicep template of the manifest
        :param manifest_params_file: path to an override file of set parameters for
        the manifest
        :param skip: options to skip, either publish bicep or upload artifacts
        :param cli_ctx: The CLI context. Used with CNFs and all LongRunningOperations
        :param use_manifest_permissions:
            CNF definition_type publish only - ignored for VNF or NSD. Causes the image
            artifact copy from a source ACR to be done via docker pull and push,
            rather than `az acr import`. This is slower but does not require
            Contributor (or importImage action) permissions on the publisher
            subscription. Also uses manifest permissions for helm chart upload.
            Requires Docker to be installed locally.
        """
        self.api_clients = api_clients
        self.resource_type = resource_type
        self.config = config
        self.bicep_path = bicep_path
        self.parameters_json_file = parameters_json_file
        self.manifest_bicep_path = manifest_bicep_path
        self.manifest_params_file = manifest_params_file
        self.skip = skip
        self.cli_ctx = cli_ctx
        self.pre_deployer = PreDeployerViaSDK(
            self.api_clients, self.config, self.cli_ctx
        )
        self.use_manifest_permissions = use_manifest_permissions

    def deploy_nfd_from_bicep(self) -> None:
        """
        Deploy the bicep template defining the NFD.

        Also ensure that all required predeploy resources are deployed.
        """
        assert isinstance(self.config, NFConfiguration)
        if self.skip == BICEP_PUBLISH:
            print("Skipping bicep manifest publish")
        else:
            # 1) Deploy Artifact manifest bicep
            # Create or check required resources
            deploy_manifest_template = not self.nfd_predeploy()
            if deploy_manifest_template:
                self.deploy_manifest_template()
            else:
                print(
                    f"Artifact manifests exist for NFD {self.config.nf_name} "
                    f"version {self.config.version}"
                )

        if self.skip == ARTIFACT_UPLOAD:
            print("Skipping artifact upload")
        else:
            # 2) Upload artifacts - must be done before nfd deployment
            if self.resource_type == VNF:
                self._vnfd_artifact_upload()
            if self.resource_type == CNF:
                self._cnfd_artifact_upload()

        if self.skip == BICEP_PUBLISH:
            print("Skipping bicep nfd publish")
            print("Done")
            return

        # 3) Deploy NFD bicep
        if not self.bicep_path:
            # User has not passed in a bicep template, so we are deploying the default
            # one produced from building the NFDV using this CLI
            if self.resource_type == VNF:
                file_name = VNF_DEFINITION_BICEP_TEMPLATE_FILENAME
            if self.resource_type == CNF:
                file_name = CNF_DEFINITION_BICEP_TEMPLATE_FILENAME
            bicep_path = os.path.join(self.config.output_directory_for_build, file_name)
        message = (
            f"Deploy bicep template for NFD {self.config.nf_name} version"
            f" {self.config.version} into"
            f" {self.config.publisher_resource_group_name} under publisher"
            f" {self.config.publisher_name}"
        )
        print(message)
        logger.info(message)
        logger.debug(
            "Parameters used for NF definition bicep deployment: %s",
            self.parameters,
        )
        self.deploy_bicep_template(bicep_path, self.parameters)
        print(f"Deployed NFD {self.config.nf_name} version {self.config.version}.")

    def _vnfd_artifact_upload(self) -> None:
        """Uploads the VHD and ARM template artifacts."""
        assert isinstance(self.config, VNFConfiguration)
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
            self.config.acr_manifest_names[0],
        )

        vhd_artifact = storage_account_manifest.artifacts[0]
        arm_template_artifact = acr_manifest.artifacts[0]

        vhd_config = self.config.vhd
        arm_template_config = self.config.arm_template

        assert isinstance(vhd_config, ArtifactConfig)
        assert isinstance(arm_template_config, ArtifactConfig)

        if self.skip == IMAGE_UPLOAD:
            print("Skipping VHD artifact upload")
        else:
            print("Uploading VHD artifact")
            vhd_artifact.upload(vhd_config)

        print("Uploading ARM template artifact")
        arm_template_artifact.upload(arm_template_config)

    def _cnfd_artifact_upload(self) -> None:
        """Uploads the Helm chart and any additional images."""
        assert isinstance(self.config, CNFConfiguration)
        acr_properties = self.api_clients.aosm_client.artifact_stores.get(
            resource_group_name=self.config.publisher_resource_group_name,
            publisher_name=self.config.publisher_name,
            artifact_store_name=self.config.acr_artifact_store_name,
        )
        if not acr_properties.properties.storage_resource_id:
            raise CLIError(
                f"Artifact store {self.config.acr_artifact_store_name} "
                "has no storage resource id linked"
            )

        # The artifacts from the manifest which has been deployed by bicep
        acr_manifest = ArtifactManifestOperator(
            self.config,
            self.api_clients,
            self.config.acr_artifact_store_name,
            self.config.acr_manifest_names[0],
        )

        # Create a new dictionary of artifacts from the manifest, keyed by artifact name
        artifact_dictionary = {}

        for artifact in acr_manifest.artifacts:
            artifact_dictionary[artifact.artifact_name] = artifact

        for helm_package in self.config.helm_packages:
            # Go through the helm packages in the config that the user has provided
            helm_package_name = helm_package.name  # type: ignore

            if helm_package_name not in artifact_dictionary:
                # Helm package in the config file but not in the artifact manifest
                raise CLIError(
                    f"Artifact {helm_package_name} not found in the artifact manifest"
                )
            # Get the artifact object that came from the manifest
            manifest_artifact = artifact_dictionary[helm_package_name]

            print(f"Uploading Helm package: {helm_package_name}")

            # The artifact object will use the correct client (ORAS) to upload the
            # artifact
            manifest_artifact.upload(helm_package, self.use_manifest_permissions)  # type: ignore

            print(f"Finished uploading Helm package: {helm_package_name}")

            # Remove this helm package artifact from the dictionary.
            artifact_dictionary.pop(helm_package_name)

        # All the remaining artifacts are not in the helm_packages list. We assume that
        # they are images that need to be copied from another ACR or uploaded from a
        # local image.
        if self.skip == IMAGE_UPLOAD:
            print("Skipping upload of images")
            return

        # This is the first time we have easy access to the number of images to upload
        # so we validate the config file here.
        if (
            len(artifact_dictionary.values()) > 1
            and self.config.images.source_local_docker_image  # type: ignore
        ):
            raise ValidationError(
                "Multiple image artifacts found to upload and a local docker image"
                " was specified in the config file. source_local_docker_image is only "
                "supported if there is a single image artifact to upload."
            )
        for artifact in artifact_dictionary.values():
            assert isinstance(artifact, Artifact)
            artifact.upload(self.config.images, self.use_manifest_permissions)  # type: ignore

    def nfd_predeploy(self) -> bool:
        """
        All the predeploy steps for a NFD. Create publisher, artifact stores and NFDG.

        Return True if artifact manifest already exists, False otherwise
        """
        logger.debug("Ensure all required resources exist")
        self.pre_deployer.ensure_config_resource_group_exists()
        self.pre_deployer.ensure_config_publisher_exists()
        self.pre_deployer.ensure_acr_artifact_store_exists()
        if self.resource_type == VNF:
            self.pre_deployer.ensure_sa_artifact_store_exists()
        self.pre_deployer.ensure_config_nfdg_exists()
        return self.pre_deployer.do_config_artifact_manifests_exist()

    @property
    def parameters(self) -> Dict[str, Any]:
        if self.parameters_json_file:
            message = f"Use parameters from file {self.parameters_json_file}"
            logger.info(message)
            print(message)
            with open(self.parameters_json_file, "r", encoding="utf-8") as f:
                parameters_json = json.loads(f.read())
                parameters = parameters_json["parameters"]
        else:
            # User has not passed in parameters file, so we use the parameters
            # required from config for the default bicep template produced from
            # building the NFDV using this CLI
            logger.debug("Create parameters for default template.")
            parameters = self.construct_parameters()

        return parameters

    def construct_parameters(self) -> Dict[str, Any]:
        """
        Create the parmeters dictionary for vnfdefinitions.bicep.

        VNF specific.
        """
        if self.resource_type == VNF:
            assert isinstance(self.config, VNFConfiguration)
            assert isinstance(self.config.vhd, ArtifactConfig)
            assert isinstance(self.config.arm_template, ArtifactConfig)
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
        if self.resource_type == CNF:
            assert isinstance(self.config, CNFConfiguration)
            return {
                "location": {"value": self.config.location},
                "publisherName": {"value": self.config.publisher_name},
                "acrArtifactStoreName": {"value": self.config.acr_artifact_store_name},
                "nfDefinitionGroup": {"value": self.config.nfdg_name},
                "nfDefinitionVersion": {"value": self.config.version},
            }
        if self.resource_type == NSD:
            assert isinstance(self.config, NSConfiguration)
            return {
                "location": {"value": self.config.location},
                "publisherName": {"value": self.config.publisher_name},
                "acrArtifactStoreName": {"value": self.config.acr_artifact_store_name},
                "nsDesignGroup": {"value": self.config.nsd_name},
                "nsDesignVersion": {"value": self.config.nsd_version},
                "nfviSiteName": {"value": self.config.nfvi_site_name},
            }
        raise TypeError(
            "Unexpected config type. Expected [VNFConfiguration|CNFConfiguration|NSConfiguration],"
            f" received {type(self.config)}"
        )

    def construct_manifest_parameters(self) -> Dict[str, Any]:
        """Create the parmeters dictionary for VNF, CNF or NSD."""
        if self.resource_type == VNF:
            assert isinstance(self.config, VNFConfiguration)
            assert isinstance(self.config.vhd, ArtifactConfig)
            assert isinstance(self.config.arm_template, ArtifactConfig)
            return {
                "location": {"value": self.config.location},
                "publisherName": {"value": self.config.publisher_name},
                "acrArtifactStoreName": {"value": self.config.acr_artifact_store_name},
                "saArtifactStoreName": {"value": self.config.blob_artifact_store_name},
                "acrManifestName": {"value": self.config.acr_manifest_names[0]},
                "saManifestName": {"value": self.config.sa_manifest_name},
                "nfName": {"value": self.config.nf_name},
                "vhdVersion": {"value": self.config.vhd.version},
                "armTemplateVersion": {"value": self.config.arm_template.version},
            }
        if self.resource_type == CNF:
            assert isinstance(self.config, CNFConfiguration)
            return {
                "location": {"value": self.config.location},
                "publisherName": {"value": self.config.publisher_name},
                "acrArtifactStoreName": {"value": self.config.acr_artifact_store_name},
                "acrManifestName": {"value": self.config.acr_manifest_names[0]},
            }
        if self.resource_type == NSD:
            assert isinstance(self.config, NSConfiguration)

            arm_template_names = []

            for nf in self.config.network_functions:
                assert isinstance(nf, NFDRETConfiguration)
                arm_template_names.append(nf.arm_template.artifact_name)

            # Set the artifact version to be the same as the NSD version, so that they
            # don't get over written when a new NSD is published.
            return {
                "location": {"value": self.config.location},
                "publisherName": {"value": self.config.publisher_name},
                "acrArtifactStoreName": {"value": self.config.acr_artifact_store_name},
                "acrManifestNames": {"value": self.config.acr_manifest_names},
                "armTemplateNames": {"value": arm_template_names},
                "armTemplateVersion": {"value": self.config.nsd_version},
            }
        raise ValueError("Unknown configuration type")

    def deploy_nsd_from_bicep(self) -> None:
        """
        Deploy the bicep template defining the VNFD.

        Also ensure that all required predeploy resources are deployed.
        """
        assert isinstance(self.config, NSConfiguration)
        if not self.skip == BICEP_PUBLISH:
            # 1) Deploy Artifact manifest bicep
            if not self.bicep_path:
                # User has not passed in a bicep template, so we are deploying the default
                # one produced from building the NSDV using this CLI
                bicep_path = os.path.join(
                    self.config.output_directory_for_build,
                    NSD_BICEP_FILENAME,
                )

            logger.debug(self.parameters)

            # Create or check required resources
            deploy_manifest_template = not self.nsd_predeploy()

            if deploy_manifest_template:
                self.deploy_manifest_template()
            else:
                logger.debug(
                    "Artifact manifests %s already exist",
                    self.config.acr_manifest_names,
                )
                print("Artifact manifests already exist")

        if self.skip == ARTIFACT_UPLOAD:
            print("Skipping artifact upload")
        else:
            # 2) Upload artifacts - must be done before nsd deployment
            for manifest, nf in zip(
                self.config.acr_manifest_names, self.config.network_functions
            ):
                assert isinstance(nf, NFDRETConfiguration)
                acr_manifest = ArtifactManifestOperator(
                    self.config,
                    self.api_clients,
                    self.config.acr_artifact_store_name,
                    manifest,
                )

                # Convert the NF bicep to ARM
                arm_template_artifact_json = self.convert_bicep_to_arm(
                    os.path.join(
                        self.config.output_directory_for_build, nf.nf_bicep_filename
                    )
                )

                arm_template_artifact = acr_manifest.artifacts[0]

                # appease mypy
                assert (
                    nf.arm_template.file_path
                ), "Config missing ARM template file path"
                with open(nf.arm_template.file_path, "w", encoding="utf-8") as file:
                    file.write(json.dumps(arm_template_artifact_json, indent=4))

                print(f"Uploading ARM template artifact: {nf.arm_template.file_path}")
                arm_template_artifact.upload(nf.arm_template)

        if self.skip == BICEP_PUBLISH:
            print("Skipping bicep nsd publish")
            print("Done")
            return

        # 3) Deploy NSD bicep
        if not self.bicep_path:
            # User has not passed in a bicep template, so we are deploying the default
            # one produced from building the NSDV using this CLI
            bicep_path = os.path.join(
                self.config.output_directory_for_build,
                NSD_BICEP_FILENAME,
            )
        message = (
            f"Deploy bicep template for NSDV {self.config.nsd_version} "
            f"into {self.config.publisher_resource_group_name} under publisher "
            f"{self.config.publisher_name}"
        )
        print(message)
        logger.info(message)
        self.deploy_bicep_template(bicep_path, self.parameters)
        print(
            f"Deployed NSD {self.config.nsd_name} "
            f"version {self.config.nsd_version}."
        )

    def deploy_manifest_template(self) -> None:
        """Deploy the bicep template defining the manifest."""
        print("Deploy bicep template for Artifact manifests")
        logger.debug("Deploy manifest bicep")

        if not self.manifest_bicep_path:
            file_name: str = ""
            if self.resource_type == NSD:
                file_name = NSD_ARTIFACT_MANIFEST_BICEP_FILENAME
            if self.resource_type == VNF:
                file_name = VNF_MANIFEST_BICEP_TEMPLATE_FILENAME
            if self.resource_type == CNF:
                file_name = CNF_MANIFEST_BICEP_TEMPLATE_FILENAME

            manifest_bicep_path = os.path.join(
                str(self.config.output_directory_for_build),
                file_name,
            )
        if not self.manifest_params_file:
            manifest_params = self.construct_manifest_parameters()
        else:
            logger.info("Use provided manifest parameters")
            with open(self.manifest_params_file, "r", encoding="utf-8") as f:
                manifest_json = json.loads(f.read())
                manifest_params = manifest_json["parameters"]
        self.deploy_bicep_template(manifest_bicep_path, manifest_params)

    def nsd_predeploy(self) -> bool:
        """
        All the predeploy steps for a NSD. Check if the RG, publisher, ACR, NSD and
        artifact manifest exist.

        Return True if artifact manifest already exists, False otherwise
        """
        logger.debug("Ensure all required resources exist")
        self.pre_deployer.ensure_config_resource_group_exists()
        self.pre_deployer.ensure_config_publisher_exists()
        self.pre_deployer.ensure_acr_artifact_store_exists()
        self.pre_deployer.ensure_config_nsd_exists()
        return self.pre_deployer.do_config_artifact_manifests_exist()

    def deploy_bicep_template(
        self, bicep_template_path: str, parameters: Dict[Any, Any]
    ) -> Any:
        """
        Deploy a bicep template.

        :param bicep_template_path: Path to the bicep template
        :param parameters: Parameters for the bicep template
        :return Any output that the template produces
        """
        logger.info("Deploy %s", bicep_template_path)
        logger.debug("Parameters: %s", parameters)
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

        :return: Output dictionary from the bicep template.
        :raise RuntimeError if validation or deploy fails
        """
        # Get current time from the time module and remove all digits after the decimal
        # point
        current_time = str(time.time()).split(".", maxsplit=1)[0]

        # Add a timestamp to the deployment name to ensure it is unique
        deployment_name = f"AOSM_CLI_deployment_{current_time}"

        # Validation is automatically re-attempted in live runs, but not in test
        # playback, causing them to fail. This explicitly re-attempts validation to
        # ensure the tests pass
        validation_res = None
        for validation_attempt in range(2):
            try:
                validation = (
                    self.api_clients.resource_client.deployments.begin_validate(
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
                )
                validation_res = LongRunningOperation(
                    self.cli_ctx, "Validating ARM template..."
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
        deployment: DeploymentExtended = LongRunningOperation(
            self.cli_ctx, "Deploying ARM template"
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

    @staticmethod
    def convert_bicep_to_arm(bicep_template_path: str) -> Any:
        """
        Convert a bicep template into an ARM template.

        :param bicep_template_path: The path to the bicep template to be converted
        :return: Output dictionary from the bicep template.
        """
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
            except subprocess.CalledProcessError as err:
                logger.error(
                    (
                        "ARM template compilation failed! See logs for full "
                        "output. The failing command was %s"
                    ),
                    err.cmd,
                )
                logger.debug("bicep build stdout: %s", err.stdout)
                logger.debug("bicep build stderr: %s", err.stderr)
                raise

            with open(
                os.path.join(tmpdir, arm_template_name), "r", encoding="utf-8"
            ) as template_file:
                arm_json = json.loads(template_file.read())

        return arm_json
