# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json
import math
import shutil
from abc import ABC, abstractmethod
from functools import lru_cache
from pathlib import Path
import tempfile
from time import sleep
from typing import Any, MutableMapping, Optional

from azext_aosm.common.command_context import CommandContext
from azext_aosm.common.utils import (
    convert_bicep_to_arm,
    clean_registry_name,
    push_image_from_local_registry_to_acr,
    call_subprocess_raise_output,
    check_tool_installed,
)
from azext_aosm.configuration_models.common_parameters_config import (
    BaseCommonParametersConfig,
    NFDCommonParametersConfig,
    CoreVNFCommonParametersConfig,
)
from azext_aosm.vendored_sdks.azure_storagev2.blob import (
    BlobClient,
    BlobType,
)
from azext_aosm.common.registry import ContainerRegistry, AzureContainerRegistry
from azext_aosm.vendored_sdks.models import ArtifactType
from azext_aosm.vendored_sdks import HybridNetworkManagementClient
from azure.core.exceptions import ServiceResponseError
from azure.cli.core.commands import LongRunningOperation
from knack.log import get_logger
from oras.client import OrasClient

logger = get_logger(__name__)


# TODO: Split these out into separate files, probably in a new artifacts module
class BaseArtifact(ABC):
    """Abstract base class for artifacts."""

    def __init__(self, artifact_name: str, artifact_type: str, artifact_version: str):
        self.artifact_name = artifact_name
        self.artifact_type = artifact_type
        self.artifact_version = artifact_version

    def to_dict(self) -> dict:
        """Convert an instance to a dict."""
        output_dict = {"type": ARTIFACT_CLASS_TO_TYPE[type(self)]}
        output_dict.update({k: vars(self)[k] for k in vars(self)})
        return output_dict

    @classmethod
    @abstractmethod
    def from_dict(cls, artifact_dict):
        """Create an instance from a dict."""
        raise NotImplementedError

    @abstractmethod
    def upload(
        self, config: BaseCommonParametersConfig, command_context: CommandContext
    ):
        """Upload the artifact."""


class BaseACRArtifact(BaseArtifact):
    """Abstract base class for ACR artifacts."""

    @abstractmethod
    def upload(
        self, config: BaseCommonParametersConfig, command_context: CommandContext
    ):
        """Upload the artifact."""

    @staticmethod
    @lru_cache(maxsize=32)
    def _manifest_credentials(
        publisherResourceGroupName: str,
        publisherName: str,
        acrArtifactStoreName: str,
        acrManifestName: str,
        aosm_client: HybridNetworkManagementClient,
    ) -> MutableMapping[str, Any]:
        """Gets the details for uploading the artifacts in the manifest."""
        retries = 0
        # This retry logic is to handle the ServiceResponseError that is hit in the integration tests.
        # This error is not hit when running the cli normally because the CLI framework automatically retries,
        # the testing framework does not support automatic retries.
        while retries < 2:
            try:
                credential_dict = aosm_client.artifact_manifests.list_credential(
                    resource_group_name=publisherResourceGroupName,
                    publisher_name=publisherName,
                    artifact_store_name=acrArtifactStoreName,
                    artifact_manifest_name=acrManifestName,
                ).as_dict()
                break
            except ServiceResponseError as error:
                retries += 1
                if retries == 2:
                    logger.debug(error, exc_info=True)
                    raise ServiceResponseError("Failed to get manifest credentials.")

        return credential_dict

    @staticmethod
    def _get_oras_client(manifest_credentials: MutableMapping[str, Any]) -> OrasClient:
        client = OrasClient(hostname=manifest_credentials["acr_server_url"])
        client.login(
            username=manifest_credentials["username"],
            password=manifest_credentials["acr_token"],
        )
        return client

    @staticmethod
    def _get_acr(upload_client: OrasClient) -> str:
        """
        Get the name of the ACR.

        :return: The name of the ACR
        """
        assert hasattr(upload_client, "remote")
        if not upload_client.remote.hostname:
            raise ValueError(
                "Cannot upload artifact. Oras client has no remote hostname."
            )
        return clean_registry_name(upload_client.remote.hostname)


class LocalFileACRArtifact(BaseACRArtifact):
    """Class for ACR artifacts from a local file."""

    def __init__(self, artifact_name, artifact_type, artifact_version, file_path: Path):
        super().__init__(artifact_name, artifact_type, artifact_version)
        self.file_path = file_path

    def to_dict(self) -> dict:
        """Convert an instance to a dict."""
        # Take the output_dict from the parent class
        output_dict = super().to_dict()
        # Add the file_path to the output_dict
        output_dict["file_path"] = str(self.file_path)
        return output_dict

    @classmethod
    def from_dict(cls, artifact_dict):
        try:
            artifact_name = artifact_dict["artifact_name"]
            artifact_type = artifact_dict["artifact_type"]
            artifact_version = artifact_dict["artifact_version"]
            file_path = Path(artifact_dict["file_path"])
            return LocalFileACRArtifact(
                artifact_name=artifact_name,
                artifact_type=artifact_type,
                artifact_version=artifact_version,
                file_path=file_path,
            )
        except KeyError as error:
            raise ValueError(
                f"Artifact is missing required field {error}.\n"
                f"Artifact is: {artifact_dict}.\n"
                "This is unexpected and most likely comes from manual editing "
                "of the definition folder."
            )

    def upload(
        self, config: BaseCommonParametersConfig, command_context: CommandContext
    ):  # pylint: disable=too-many-locals
        """Upload the artifact."""
        logger.debug("LocalFileACRArtifact config: %s", config)

        # TODO: remove, this is temporary until we fix in artifact reader
        self.file_path = Path(self.file_path)
        # For NSDs, we provide paths relative to the artifacts folder, resolve them to absolute paths
        if not self.file_path.is_absolute():
            output_folder_path = command_context.cli_options["definition_folder"]
            resolved_path = output_folder_path.resolve()
            absolute_file_path = resolved_path / self.file_path
            self.file_path = absolute_file_path

        if self.file_path.suffix == ".bicep":
            # Uploading the nf_template as part of the NSD will use this code path
            # This does mean we can never have a bicep file as an artifact, but that should be OK
            logger.debug("Converting self.file_path to ARM")
            arm_template = convert_bicep_to_arm(self.file_path)
            self.file_path = self.file_path.with_suffix(".json")
            json.dump(arm_template, self.file_path.open("w"))
            logger.debug("Converted bicep file to ARM as: %s", self.file_path)

        manifest_credentials = self._manifest_credentials(
            publisherResourceGroupName=config.publisherResourceGroupName,
            publisherName=config.publisherName,
            acrArtifactStoreName=config.acrArtifactStoreName,
            acrManifestName=config.acrManifestName,
            aosm_client=command_context.aosm_client
        )
        if config.disablePublicNetworkAccess:
            if config.vnetPrivateEndPoints:
                parameters = {
                    "manualPrivateEndPointConnections": [
                        {"id": end_point} for end_point in config.vnetPrivateEndPoints
                    ]
                }
                poller = command_context.aosm_client.artifact_stores.begin_approve_private_end_points(
                    config.publisherResourceGroupName,
                    config.publisherName,
                    config.acrArtifactStoreName,
                    parameters
                )
                LongRunningOperation(command_context.cli_ctx)(poller)
            if config.networkFabricControllerIds:
                parameters_nfc = {
                    "networkFabricControllerIds": [
                        {"id": end_point} for end_point in config.networkFabricControllerIds
                    ]
                }
                nnf_poller = command_context.aosm_client.artifact_stores.begin_add_network_fabric_controller_end_points(
                    config.publisherResourceGroupName,
                    config.publisherName,
                    config.acrArtifactStoreName,
                    parameters_nfc
                )
                LongRunningOperation(command_context.cli_ctx)(nnf_poller)
        oras_client = self._get_oras_client(manifest_credentials=manifest_credentials)
        target_acr = self._get_acr(oras_client)
        target = f"{target_acr}/{self.artifact_name}:{self.artifact_version}"
        logger.debug("Uploading %s to %s", self.file_path, target)

        if self.artifact_type == ArtifactType.ARM_TEMPLATE.value:
            retries = 0
            while True:
                try:
                    oras_client.push(files=[self.file_path], target=target)
                    break
                except ValueError as error:
                    if retries < 20:
                        logger.info(
                            "Retrying pushing local artifact to ACR. Retries so far: %s",
                            retries,
                        )
                        retries += 1
                        sleep(3)
                        continue

                    logger.error("Failed to upload %s to %s.", self.file_path, target)
                    logger.debug(error, exc_info=True)
                    raise error

            logger.info(
                "LocalFileACRArtifact uploaded %s to %s using oras push",
                self.file_path,
                target,
            )

        elif self.artifact_type == ArtifactType.OCI_ARTIFACT.value:
            target_acr_name = target_acr.replace(".azurecr.io", "")
            target_acr_with_protocol = f"oci://{target_acr}"
            username = manifest_credentials["username"]
            password = manifest_credentials["acr_token"]

            check_tool_installed("docker")
            check_tool_installed("helm")

            # tmpdir is only used if file_path is dir, but `with` context manager is cleaner to use, so we always
            # set up the tmpdir, even if it doesn't end up being used.
            with tempfile.TemporaryDirectory() as tmpdir:
                if self.file_path.is_dir():
                    helm_package_cmd = [
                        str(shutil.which("helm")),
                        "package",
                        self.file_path,
                        "--destination",
                        tmpdir,
                    ]
                    call_subprocess_raise_output(helm_package_cmd)
                    self.file_path = Path(
                        tmpdir, f"{self.artifact_name}-{self.artifact_version}.tgz"
                    )

                # This seems to prevent occasional helm login failures
                acr_login_cmd = [
                    str(shutil.which("az")),
                    "acr",
                    "login",
                    "--name",
                    target_acr_name,
                    "--username",
                    username,
                    "--password",
                    password,
                ]
                call_subprocess_raise_output(acr_login_cmd)

                try:
                    helm_login_cmd = [
                        str(shutil.which("helm")),
                        "registry",
                        "login",
                        target_acr,
                        "--username",
                        username,
                        "--password",
                        password,
                    ]
                    call_subprocess_raise_output(helm_login_cmd)

                    push_command = [
                        str(shutil.which("helm")),
                        "push",
                        self.file_path,
                        target_acr_with_protocol,
                    ]
                    call_subprocess_raise_output(push_command)
                finally:
                    helm_logout_cmd = [
                        str(shutil.which("helm")),
                        "registry",
                        "logout",
                        target_acr,
                    ]
                    call_subprocess_raise_output(helm_logout_cmd)

            logger.info(
                "LocalFileACRArtifact uploaded %s to %s using helm push",
                self.file_path,
                target,
            )

        else:  # TODO: Make this one of the allowed Azure CLI exceptions
            raise ValueError(
                f"Unexpected artifact type. Got {self.artifact_type}. "
                "Expected {ArtifactType.ARM_TEMPLATE.value} or {ArtifactType.OCI_ARTIFACT.value}"
            )


class RemoteACRArtifact(BaseACRArtifact):
    """Class for ACR artifacts from a remote ACR image."""

    def __init__(  # pylint: disable=too-many-positional-arguments
        self,
        artifact_name,
        artifact_type,
        artifact_version,
        source_registry: ContainerRegistry,
        registry_namespace: str = "",
    ):
        super().__init__(artifact_name, artifact_type, artifact_version)
        self.source_registry = source_registry
        self.registry_namespace = registry_namespace

    def to_dict(self) -> dict:
        """Convert an instance to a dict."""
        # Take the output_dict from the parent class
        output_dict = super().to_dict()
        # Add the source_registry to the output_dict
        if self.source_registry:
            output_dict["source_registry"] = self.source_registry.to_dict()
        if self.registry_namespace:
            output_dict["registry_namespace"] = self.registry_namespace
        return output_dict

    @classmethod
    def from_dict(cls, artifact_dict):
        try:
            artifact_name = artifact_dict["artifact_name"]
            artifact_type = artifact_dict["artifact_type"]
            artifact_version = artifact_dict["artifact_version"]
            source_registry = ContainerRegistry.from_dict(
                registry_dict=artifact_dict["source_registry"]
            )
            registry_namespace = artifact_dict["registry_namespace"]
            return RemoteACRArtifact(
                artifact_name=artifact_name,
                artifact_type=artifact_type,
                artifact_version=artifact_version,
                source_registry=source_registry,
                registry_namespace=registry_namespace,
            )
        except KeyError as error:
            raise ValueError(
                f"Artifact is missing required field {error}.\n"
                f"Artifact is: {artifact_dict}.\n"
                "This is unexpected and most likely comes from manual editing "
                "of the definition folder."
            ) from error

    def upload(
        self, config: BaseCommonParametersConfig, command_context: CommandContext
    ):
        """Upload the artifact."""

        logger.debug("RemoteACRArtifact config: %s", config)

        manifest_credentials = self._manifest_credentials(
            publisherResourceGroupName=config.publisherResourceGroupName,
            publisherName=config.publisherName,
            acrArtifactStoreName=config.acrArtifactStoreName,
            acrManifestName=config.acrManifestName,
            aosm_client=command_context.aosm_client
        )

        target_acr = clean_registry_name(manifest_credentials["acr_server_url"])
        target_username = manifest_credentials["username"]
        target_password = manifest_credentials["acr_token"]

        source_image = (
            f"{self.source_registry.registry_name}/"
            f"{self.registry_namespace}"
            f"{self.artifact_name}"
            f":{self.artifact_version}"
        )

        if command_context.cli_options["no_subscription_permissions"] or not isinstance(
            self.source_registry, AzureContainerRegistry
        ):
            logger.info(
                "Using docker pull and push to copy image artifact: %s",
                self.artifact_name,
            )
            check_tool_installed("docker")
            self.source_registry.pull_image_to_local_registry(source_image=source_image)

            # We do not want the namespace to be included in the target image
            push_image_from_local_registry_to_acr(
                target_acr=target_acr,
                target_image=f"{self.artifact_name}:{self.artifact_version}",
                target_username=target_username,
                target_password=target_password,
                local_docker_image=source_image,
            )
        else:
            logger.info(
                "Using az acr import to copy image artifact: %s", self.artifact_name
            )

            self.source_registry.copy_image_to_target_acr(
                source_image=source_image,
                target_acr=target_acr,
                image_name=self.artifact_name,
                image_version=self.artifact_version,
            )


class BaseStorageAccountArtifact(BaseArtifact):
    """Abstract base class for storage account artifacts."""

    @abstractmethod
    def upload(
        self, config: BaseCommonParametersConfig, command_context: CommandContext
    ):
        """Upload the artifact."""

    def _get_blob_client(
        self, config: BaseCommonParametersConfig, command_context: CommandContext
    ) -> BlobClient:
        container_basename = self.artifact_name.replace("-", "")
        container_name = f"{container_basename}-{self.artifact_version}"
        # For AOSM to work VHD blobs must have the suffix .vhd
        if self.artifact_name.endswith("-vhd"):
            blob_name = f"{self.artifact_name[:-4].replace('-', '')}-{self.artifact_version}.vhd"
        else:
            blob_name = container_name

        logger.debug("container name: %s, blob name: %s", container_name, blob_name)
        # Liskov substitution dictates we must accept BaseCommonParametersConfig, but we should
        # never be calling upload on this class unless we've got CoreVNFCommonParametersConfig
        assert isinstance(config, CoreVNFCommonParametersConfig)
        manifest_credentials = (
            command_context.aosm_client.artifact_manifests.list_credential(
                resource_group_name=config.publisherResourceGroupName,
                publisher_name=config.publisherName,
                artifact_store_name=config.saArtifactStoreName,
                artifact_manifest_name=config.saManifestName,
            ).as_dict()
        )

        for container_credential in manifest_credentials["container_credentials"]:
            if container_credential["container_name"] == container_name:
                sas_uri = str(container_credential["container_sas_uri"])
                sas_uri_prefix, sas_uri_token = sas_uri.split("?", maxsplit=1)

                blob_url = f"{sas_uri_prefix}/{blob_name}?{sas_uri_token}"
                logger.debug("Blob URL: %s", blob_url)

        return BlobClient.from_blob_url(blob_url)


class LocalFileStorageAccountArtifact(BaseStorageAccountArtifact):
    """Class for storage account artifacts from a local file."""

    def __init__(self, artifact_name, artifact_type, artifact_version, file_path: Path):
        super().__init__(artifact_name, artifact_type, artifact_version)
        self.file_path = str(file_path)

    def to_dict(self) -> dict:
        """Convert an instance to a dict."""
        # Take the output_dict from the parent class
        output_dict = super().to_dict()
        # Add the file_path to the output_dict
        output_dict["file_path"] = str(self.file_path)
        return output_dict

    @classmethod
    def from_dict(cls, artifact_dict):
        try:
            artifact_name = artifact_dict["artifact_name"]
            artifact_type = artifact_dict["artifact_type"]
            artifact_version = artifact_dict["artifact_version"]
            file_path = Path(artifact_dict["file_path"])
            return LocalFileStorageAccountArtifact(
                artifact_name=artifact_name,
                artifact_type=artifact_type,
                artifact_version=artifact_version,
                file_path=file_path,
            )
        except KeyError as error:
            raise ValueError(
                f"Artifact is missing required field {error}.\n"
                f"Artifact is: {artifact_dict}.\n"
                "This is unexpected and most likely comes from manual editing "
                "of the definition folder."
            )

    def upload(
        self, config: BaseCommonParametersConfig, command_context: CommandContext
    ):
        """Upload the artifact."""
        # Liskov substitution dictates we must accept BaseCommonParametersConfig, but we should
        # never be calling upload on this class unless we've got NFDCommonParametersConfig
        assert isinstance(config, NFDCommonParametersConfig)
        logger.debug("LocalFileStorageAccountArtifact config: %s", config)
        blob_client = self._get_blob_client(
            config=config, command_context=command_context
        )
        logger.info("Uploading local file '%s' to blob store", self.file_path)
        with open(self.file_path, "rb") as artifact:
            blob_client.upload_blob(
                data=artifact,
                overwrite=True,
                blob_type=BlobType.PAGEBLOB,
                progress_hook=self._vhd_upload_progress_callback,
            )

        logger.info(
            "Successfully uploaded %s to %s", self.file_path, blob_client.container_name
        )

    def _vhd_upload_progress_callback(
        self, current_bytes: int, total_bytes: Optional[int]
    ) -> None:
        """Callback function for VHD upload progress."""
        current_readable = self._convert_to_readable_size(current_bytes)
        total_readable = self._convert_to_readable_size(total_bytes)
        message = f"Uploaded {current_readable} of {total_readable} bytes"
        # We use print here to allow the terminal to easily update the line rather than
        # create a new line for each chunk.
        print(message)

    @staticmethod
    def _convert_to_readable_size(size_in_bytes: Optional[int]) -> str:
        """Converts a size in bytes to a human readable size."""
        if size_in_bytes is None:
            return "Unknown bytes"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        index = int(math.floor(math.log(size_in_bytes, 1024)))
        power = math.pow(1024, index)
        readable_size = round(size_in_bytes / power, 2)
        return f"{readable_size} {size_name[index]}"


class BlobStorageAccountArtifact(BaseStorageAccountArtifact):
    # TODO (Rename): Rename class, e.g. RemoteBlobStorageAccountArtifact
    """Class for storage account artifacts from a remote blob."""

    def __init__(
        self, artifact_name, artifact_type, artifact_version, blob_sas_uri: str
    ):
        super().__init__(artifact_name, artifact_type, artifact_version)
        self.blob_sas_uri = blob_sas_uri

    @classmethod
    def from_dict(cls, artifact_dict):
        try:
            artifact_name = artifact_dict["artifact_name"]
            artifact_type = artifact_dict["artifact_type"]
            artifact_version = artifact_dict["artifact_version"]
            blob_sas_uri = artifact_dict["blob_sas_uri"]
            return BlobStorageAccountArtifact(
                artifact_name=artifact_name,
                artifact_type=artifact_type,
                artifact_version=artifact_version,
                blob_sas_uri=blob_sas_uri,
            )
        except KeyError as error:
            raise ValueError(
                f"Artifact is missing required field {error}.\n"
                f"Artifact is: {artifact_dict}.\n"
                "This is unexpected and most likely comes from manual editing "
                "of the definition folder."
            )

    def upload(
        self, config: BaseCommonParametersConfig, command_context: CommandContext
    ):
        """Upload the artifact."""
        # Liskov substitution dictates we must accept BaseCommonParametersConfig, but we should
        # never be calling upload on this class unless we've got NFDCommonParametersConfig
        assert isinstance(config, NFDCommonParametersConfig)
        logger.info("Copy from SAS URL to blob store")
        source_blob = BlobClient.from_blob_url(self.blob_sas_uri)

        if source_blob.exists():
            target_blob = self._get_blob_client(
                config=config, command_context=command_context
            )
            logger.debug(source_blob.url)
            target_blob.start_copy_from_url(source_blob.url)
            logger.info(
                "Successfully copied %s from %s to %s",
                source_blob.blob_name,
                source_blob.account_name,
                target_blob.account_name,
            )
        else:
            raise RuntimeError(
                f"{source_blob.blob_name} does not exist in"
                f" {source_blob.account_name}."
            )


# Mapping of artifact type names to their classes.
ARTIFACT_TYPE_TO_CLASS = {
    "ACRFromLocalFile": LocalFileACRArtifact,
    "ACRFromRemote": RemoteACRArtifact,
    "StorageAccountFromLocalFile": LocalFileStorageAccountArtifact,
    "StorageAccountFromBlob": BlobStorageAccountArtifact,
}

# Generated mapping of artifact classes to type names.
ARTIFACT_CLASS_TO_TYPE = {v: k for k, v in ARTIFACT_TYPE_TO_CLASS.items()}
