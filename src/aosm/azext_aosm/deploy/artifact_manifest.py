# Copyright (c) Microsoft Corporation. All rights reserved.
# Highly Confidential Material
"""A module to handle interacting with artifact manifests."""

from knack.log import get_logger
from functools import cached_property
from typing import Any, List, Union

import requests
from azext_aosm.deploy.artifact import Artifact
from azure.storage.blob import BlobClient
from oras.client import OrasClient
from azext_aosm.configuration import Configuration, VNFConfiguration
from azext_aosm.vendored_sdks.models import ArtifactAccessCredential, ArtifactManifest

from azext_aosm.util.management_clients import ApiClients

logger = get_logger(__name__)


class ArtifactManifestOperator:
    """ArtifactManifest class."""

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
        self._manifest_credentials = None

    @cached_property
    def _manifest_credentials(self) -> Any:
        """Gets the details for uploading the artifacts in the manifest."""

        return self.api_clients.aosm_client.artifact_manifests.list_credential(
            resource_group_name=self.config.publisher_resource_group_name,
            publisher_name=self.config.publisher_name,
            artifact_store_name=self.store_name,
            artifact_manifest_name=self.manifest_name,
        ).as_dict()

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
        if manifest.artifacts:
            for artifact in manifest.artifacts:
                assert artifact.artifact_name
                assert artifact.artifact_type
                assert artifact.artifact_version

                artifacts.append(
                    Artifact(
                        artifact_name=artifact.artifact_name,
                        artifact_type=artifact.artifact_type,
                        artifact_version=artifact.artifact_version,
                        artifact_client=self._get_artifact_client(
                            artifact.artifact_name, artifact.artifact_version
                        ),
                    )
                )

        return artifacts

    def _get_artifact_client(
        self, artifact_name: str, artifact_version: str
    ) -> Union[BlobClient, OrasClient]:
        """
        Get the artifact client required for uploading the artifact.

        :param artifact_name: name of the artifact
        :param artifact_version: artifact version
        """
        if self._manifest_credentials["credential_type"] == "AzureStorageAccountToken":
            container_basename = artifact_name.replace("-", "")
            blob_url = self._get_blob_url(f"{container_basename}-{artifact_version}")
            return BlobClient.from_blob_url(blob_url)
        else:
            return self._oras_client(self._manifest_credentials["acr_server_url"])

    def _get_blob_url(self, container_name: str) -> str:
        """
        Get the URL for the blob to be uploaded to the storage account artifact store.

        :param container_name: name of the container
        """
        for container_credential in self._manifest_credentials["container_credentials"]:
            if container_credential["container_name"] == container_name:
                sas_uri = str(container_credential["container_sas_uri"])
                sas_uri_prefix = sas_uri.split("?")[0]
                sas_uri_token = sas_uri.split("?")[1]

                return f"{sas_uri_prefix}/{container_name}?{sas_uri_token}"
        raise KeyError(f"Manifest does not include a credential for {container_name}.")
