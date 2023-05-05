# Copyright (c) Microsoft Corporation. All rights reserved.
# Highly Confidential Material
"""A module to handle interacting with artifacts."""

from knack.log import get_logger
from dataclasses import dataclass
from typing import Union

from azure.storage.blob import BlobClient
from azext_aosm.configuration import ArtifactConfig, DESCRIPTION_MAP
from oras.client import OrasClient

logger = get_logger(__name__)


@dataclass
class Artifact:
    """Artifact class."""

    artifact_name: str
    artifact_type: str
    artifact_version: str
    artifact_client: Union[BlobClient, OrasClient]

    def upload(self, artifact_config: ArtifactConfig) -> None:
        """
        Upload aritfact.

        :param artifact_config: configuration for the artifact being uploaded
        """
        if self.artifact_type == "OCIArtifact" or self.artifact_type == "ArmTemplate":
            self._upload_to_acr(artifact_config)
        else:
            self._upload_to_storage_account(artifact_config)

    def _upload_to_acr(self, artifact_config: ArtifactConfig) -> None:
        """
        Upload artifact to ACR.

        :param artifact_config: configuration for the artifact being uploaded
        """
        assert type(self.artifact_client) == OrasClient

        # If not included in config, the file path value will be the description of
        # the field.
        if (
            artifact_config.file_path
            and not artifact_config.file_path == DESCRIPTION_MAP["file_path"]
        ):
            target = f"{self.artifact_client.remote.hostname.replace('https://', '')}/{self.artifact_name}:{self.artifact_version}"
            logger.debug(f"Uploading {artifact_config.file_path} to {target}")
            self.artifact_client.push(
                file=artifact_config.file_path,
                target=target,
            )
        else:
            raise NotImplementedError(
                "Copying artifacts is not implemented for ACR artifacts stores."
            )

    def _upload_to_storage_account(self, artifact_config: ArtifactConfig) -> None:
        """
        Upload artifact to storage account.

        :param artifact_config: configuration for the artifact being uploaded
        """
        assert type(self.artifact_client) == BlobClient

        # If the file path is given, upload the artifact, else, copy it from an existing blob.
        if (
            artifact_config.file_path
            and not artifact_config.file_path == DESCRIPTION_MAP["file_path"]
        ):
            logger.info("Upload to blob store")
            with open(artifact_config.file_path, "rb") as artifact:
                self.artifact_client.upload_blob(artifact, overwrite=True)
            logger.info(
                f"Successfully uploaded {artifact_config.file_path} to {self.artifact_client.account_name}"
            )
        else:
            logger.info("Copy from SAS URL to blob store")
            source_blob = BlobClient.from_blob_url(artifact_config.blob_sas_url)

            if source_blob.exists():
                logger.debug(source_blob.url)
                self.artifact_client.start_copy_from_url(source_blob.url)
                logger.info(
                    f"Successfully copied {source_blob.blob_name} from {source_blob.account_name} to {self.artifact_client.account_name}"
                )
            else:
                raise RuntimeError(
                    f"{source_blob.blob_name} does not exist in {source_blob.account_name}."
                )
