# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""A module to handle interacting with artifact manifests."""
from functools import cached_property, lru_cache
from typing import Any, List, Union

from azure.cli.core.azclierror import AzCLIError
from knack.log import get_logger
from oras.client import OrasClient

from azext_aosm._configuration import Configuration
from azext_aosm.deploy.artifact import Artifact
from azext_aosm.util.management_clients import ApiClients
from azext_aosm.vendored_sdks.models import (
    ArtifactManifest,
    ArtifactType,
    CredentialType,
    ManifestArtifactFormat,
)
from azext_aosm.vendored_sdks.azure_storagev2.blob.v2022_11_02 import BlobClient

logger = get_logger(__name__)


class ArtifactManifestOperator:
    """ArtifactManifest class."""

    # pylint: disable=too-few-public-methods
    def __init__(
        self,
        config: Configuration,
        api_clients: ApiClients,
        store_name: str,
        manifest_name: str,
    ) -> None:
        """Init."""
        self.manifest_name = manifest_name
        self.api_clients = api_clients
        self.config = config
        self.store_name = store_name
        self.artifacts = self._get_artifact_list()

    @cached_property
    def _manifest_credentials(self) -> Any:
        """Gets the details for uploading the artifacts in the manifest."""

        return self.api_clients.aosm_client.artifact_manifests.list_credential(
            resource_group_name=self.config.publisher_resource_group_name,
            publisher_name=self.config.publisher_name,
            artifact_store_name=self.store_name,
            artifact_manifest_name=self.manifest_name,
        ).as_dict()

    @lru_cache(maxsize=32)  # noqa: B019
    def _oras_client(self, acr_url: str) -> OrasClient:
        """
        Returns an OrasClient object for uploading to the artifact store ACR.

        :param arc_url: URL of the ACR backing the artifact manifest
        """
        client = OrasClient(hostname=acr_url)
        client.login(
            username=self._manifest_credentials["username"],
            password=self._manifest_credentials["acr_token"],
        )
        return client

    def _get_artifact_list(self) -> List[Artifact]:
        """Get the list of Artifacts in the Artifact Manifest."""
        artifacts = []

        manifest: ArtifactManifest = (
            self.api_clients.aosm_client.artifact_manifests.get(
                resource_group_name=self.config.publisher_resource_group_name,
                publisher_name=self.config.publisher_name,
                artifact_store_name=self.store_name,
                artifact_manifest_name=self.manifest_name,
            )
        )

        # Instatiate an Artifact object for each artifact in the manifest.
        if manifest.properties.artifacts:
            for artifact in manifest.properties.artifacts:
                if not (
                    artifact.artifact_name
                    and artifact.artifact_type
                    and artifact.artifact_version
                ):
                    raise AzCLIError(
                        "Cannot upload artifact. Artifact returned from "
                        "manifest query is missing required information."
                        f"{artifact}"
                    )

                artifacts.append(
                    Artifact(
                        artifact_name=artifact.artifact_name,
                        artifact_type=artifact.artifact_type,
                        artifact_version=artifact.artifact_version,
                        artifact_client=self._get_artifact_client(artifact),
                        manifest_credentials=self._manifest_credentials,
                    )
                )

        return artifacts

    def _get_artifact_client(
        self, artifact: ManifestArtifactFormat
    ) -> Union[BlobClient, OrasClient]:
        """
        Get the artifact client required for uploading the artifact.

        :param artifact - a ManifestArtifactFormat with the artifact info.
        """
        # Appease mypy - an error will be raised before this if these are blank
        assert artifact.artifact_name
        assert artifact.artifact_type
        assert artifact.artifact_version
        if (
            self._manifest_credentials["credential_type"]
            == CredentialType.AZURE_STORAGE_ACCOUNT_TOKEN
        ):
            # Check we have the required artifact types for this credential. Indicates
            # a coding error if we hit this but worth checking.
            if not (
                artifact.artifact_type
                in (ArtifactType.IMAGE_FILE, ArtifactType.VHD_IMAGE_FILE)
            ):
                raise AzCLIError(
                    f"Cannot upload artifact {artifact.artifact_name}."
                    " Artifact manifest credentials of type "
                    f"{CredentialType.AZURE_STORAGE_ACCOUNT_TOKEN} are not expected "
                    f"for Artifacts of type {artifact.artifact_type}"
                )

            container_basename = artifact.artifact_name.replace("-", "")
            container_name = f"{container_basename}-{artifact.artifact_version}"

            # For AOSM to work VHD blobs must have the suffix .vhd
            if artifact.artifact_name.endswith("-vhd"):
                blob_name = f"{artifact.artifact_name[:-4].replace('-', '')}-{artifact.artifact_version}.vhd"
            else:
                blob_name = container_name

            logger.debug("container name: %s, blob name: %s", container_name, blob_name)

            blob_url = self._get_blob_url(container_name, blob_name)
            return BlobClient.from_blob_url(blob_url)
        return self._oras_client(self._manifest_credentials["acr_server_url"])

    def _get_blob_url(self, container_name: str, blob_name: str) -> str:
        """
        Get the URL for the blob to be uploaded to the storage account artifact store.

        :param container_name: name of the container
        :param blob_name: the name that the blob will get uploaded with
        """
        for container_credential in self._manifest_credentials["container_credentials"]:
            if container_credential["container_name"] == container_name:
                sas_uri = str(container_credential["container_sas_uri"])
                sas_uri_prefix, sas_uri_token = sas_uri.split("?", maxsplit=1)

                blob_url = f"{sas_uri_prefix}/{blob_name}?{sas_uri_token}"
                logger.debug("Blob URL: %s", blob_url)

                return blob_url
        raise KeyError(f"Manifest does not include a credential for {container_name}.")
