# Copyright (c) Microsoft Corporation. All rights reserved.
# Highly Confidential Material

# pylint: disable=unidiomatic-typecheck
"""A module to handle interacting with artifacts."""
import os
import subprocess
from dataclasses import dataclass
from typing import List, Union

from azure.cli.core.commands import LongRunningOperation
from azure.mgmt.containerregistry import ContainerRegistryManagementClient
from azure.mgmt.containerregistry.models import ImportImageParameters, ImportSource
from azure.storage.blob import BlobClient, BlobType
from knack.log import get_logger
from knack.util import CLIError
from oras.client import OrasClient
from azure.cli.core.commands import LongRunningOperation
from azure.mgmt.containerregistry import ContainerRegistryManagementClient

from azext_aosm._configuration import ArtifactConfig, HelmPackageConfig

logger = get_logger(__name__)


@dataclass
class Artifact:
    """Artifact class."""

    artifact_name: str
    artifact_type: str
    artifact_version: str
    artifact_client: Union[BlobClient, OrasClient]

    def upload(self, artifact_config: Union[ArtifactConfig, HelmPackageConfig]) -> None:
        """
        Upload aritfact.

        :param artifact_config: configuration for the artifact being uploaded
        """
        if type(self.artifact_client) == OrasClient:
            if type(artifact_config) == HelmPackageConfig:
                self._upload_helm_to_acr(artifact_config)
            elif type(artifact_config) == ArtifactConfig:
                self._upload_arm_to_acr(artifact_config)
            else:
                raise ValueError(f"Unsupported artifact type: {type(artifact_config)}.")
        else:
            assert isinstance(artifact_config, ArtifactConfig)
            self._upload_to_storage_account(artifact_config)

    def _upload_arm_to_acr(self, artifact_config: ArtifactConfig) -> None:
        """
        Upload ARM artifact to ACR.

        :param artifact_config: configuration for the artifact being uploaded
        """
        assert type(self.artifact_client) == OrasClient

        if artifact_config.file_path:
            try:
                # OrasClient 0.1.17 has a bug
                # https://github.com/oras-project/oras-py/issues/90 which means on
                # Windows we need a real blank file on disk, without a colon in the
                # filepath (so tempfile can't be used and we just put it in the working
                # directory), that can act as the manifest config file. So create one
                # and then delete it after the upload.
                with open("dummyManifestConfig.json", "w", encoding="utf-8") as f:
                    target = (
                        f"{self.artifact_client.remote.hostname.replace('https://', '')}"
                        f"/{self.artifact_name}:{self.artifact_version}"
                    )
                    logger.debug(
                        "Uploading %s to %s", artifact_config.file_path, target
                    )
                    self.artifact_client.push(
                        files=[artifact_config.file_path],
                        target=target,
                        manifest_config=f.name,
                    )
            finally:
                # Delete the dummy file
                try:
                    os.remove("dummyManifestConfig.json")
                except FileNotFoundError:
                    pass
        else:
            raise NotImplementedError(
                "Copying artifacts is not implemented for ACR artifacts stores."
            )

    def _upload_helm_to_acr(self, artifact_config: HelmPackageConfig) -> None:
        """
        Upload artifact to ACR.

        :param artifact_config: configuration for the artifact being uploaded
        """
        assert isinstance(self.artifact_client, OrasClient)
        chart_path = artifact_config.path_to_chart
        if not self.artifact_client.remote.hostname:
            raise ValueError(
                "Cannot upload artifact. Oras client has no remote hostname."
            )
        registry = self.artifact_client.remote.hostname.replace("https://", "")
        target_registry = f"oci://{registry}"
        registry_name = registry.replace(".azurecr.io", "")

        # az acr login --name "registry_name"
        login_command = ["az", "acr", "login", "--name", registry_name]
        subprocess.run(login_command, check=True)

        try:
            logger.debug("Uploading %s to %s", chart_path, target_registry)

            # helm push "$chart_path" "$target_registry"
            push_command = ["helm", "push", chart_path, target_registry]
            subprocess.run(push_command, check=True)
        finally:
            # If we don't logout from the registry, future Artifact uploads to this ACR
            # will fail with an UNAUTHORIZED error. There is no az acr logout command,
            # but it is a wrapper around docker, so a call to docker logout will work.
            logout_command = ["docker", "logout", registry]
            subprocess.run(logout_command, check=True)

    def _upload_to_storage_account(self, artifact_config: ArtifactConfig) -> None:
        """
        Upload artifact to storage account.

        :param artifact_config: configuration for the artifact being uploaded
        """
        assert type(self.artifact_client) == BlobClient
        assert type(artifact_config) == ArtifactConfig

        # If the file path is given, upload the artifact, else, copy it from an existing blob.
        if artifact_config.file_path:
            logger.info("Upload to blob store")
            with open(artifact_config.file_path, "rb") as artifact:
                self.artifact_client.upload_blob(
                    artifact, overwrite=True, blob_type=BlobType.PAGEBLOB
                )
            logger.info(
                "Successfully uploaded %s to %s",
                artifact_config.file_path,
                self.artifact_client.account_name,
            )
        else:
            # Config Validation will raise error if not true
            assert artifact_config.blob_sas_url
            logger.info("Copy from SAS URL to blob store")
            source_blob = BlobClient.from_blob_url(artifact_config.blob_sas_url)

            if source_blob.exists():
                logger.debug(source_blob.url)
                self.artifact_client.start_copy_from_url(source_blob.url)
                logger.info(
                    "Successfully copied %s from %s to %s",
                    source_blob.blob_name,
                    source_blob.account_name,
                    self.artifact_client.account_name,
                )
            else:
                raise RuntimeError(
                    f"{source_blob.blob_name} does not exist in"
                    f" {source_blob.account_name}."
                )

    @staticmethod
    def copy_image(
        cli_ctx,
        container_registry_client: ContainerRegistryManagementClient,
        source_registry_id: str,
        source_image: str,
        target_registry_resource_group_name: str,
        target_registry_name: str,
        target_tags: List[str],
        mode: str = "NoForce",
    ):
        """
        Copy image from one ACR to another.

        :param cli_ctx: CLI context
        :param container_registry_client: container registry client
        :param source_registry_id: source registry ID
        :param source_image: source image
        :param target_registry_resource_group_name: target registry resource group name
        :param target_registry_name: target registry name
        :param target_tags: the list of tags to be applied to the imported image
                            should be of form: namepace/name:tag or name:tag
        :param mode: mode for import
        """

        source = ImportSource(resource_id=source_registry_id, source_image=source_image)

        import_parameters = ImportImageParameters(
            source=source,
            target_tags=target_tags,
            untagged_target_repositories=[],
            mode=mode,
        )
        try:
            result_poller = container_registry_client.begin_import_image(
                resource_group_name=target_registry_resource_group_name,
                registry_name=target_registry_name,
                parameters=import_parameters,
            )

            LongRunningOperation(cli_ctx, "Importing image...")(result_poller)

            logger.info(
                "Successfully imported %s to %s", source_image, target_registry_name
            )
        except CLIError as error:
            logger.error(
                (
                    "Failed to import %s to %s. Check if this image exists in the"
                    " source registry or is already present in the target registry."
                ),
                source_image,
                target_registry_name,
            )
            logger.debug(error, exc_info=True)
