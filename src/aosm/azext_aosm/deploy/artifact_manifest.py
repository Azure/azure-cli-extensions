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
from azext_aosm._configuration import Configuration, VNFConfiguration
from azext_aosm.vendored_sdks.models import ArtifactAccessCredential

from azext_aosm.util.management_clients import ApiClientsAndCaches

logger = get_logger(__name__)


class ArtifactManifest:
    """ArtifactManifest class."""

    def __init__(self, config: Configuration, api_clients: ApiClientsAndCaches, store_name: str, manifest_name: str) -> None:
        """Init."""
        self.manifest_name = manifest_name
        self.api_clients = api_clients
        self.config = config
        self.artifacts = self._get_artifact_list()
        self.store_name = store_name
        self._manifest_credentials = None

    @cached_property
    def _manifest_credentials(self) -> ArtifactAccessCredential:
        """Gets the details for uploading the artifacts in the manifest."""
        
        return self.api_clients.aosm_client.artifact_manifests.list_credential(
            resource_group_name=self.config.publisher_resource_group_name,
            publisher_name=self.config.publisher_name,
            artifact_store_name=self.store_name,
            artifact_manifest_name=self.manifest_name
        )


    def _oras_client(self, acr_url: str) -> OrasClient:
        """
        Returns an OrasClient object for uploading to the artifact str        Returns an OrasClient object for uploading to the artifact store ACR.oe ACR.

        :param arc_url: URL of the ACR backing the artifact manifest
        """
        client = OrasClient(hostname=acr_url)
        client.login(
            username=self._manifest_credentials.as_dict()["username"],
            password=self._manifest_credentials["acrToken"],
        )

        return client

    def _get_artifact_list(self) -> List[Artifact]:
        """Get the list of Artifacts in the Artifact Manifest."""
        url = f"https://management.azure.com/{self.resource_id.lstrip('/')}?api-version=2022-09-01-preview"
        response = requests.get(
            url=url,
            headers={
                "Authorization": f"Bearer {self._access_token}",
            },
            allow_redirects=True,
            timeout=30,
        )

        artifacts = []

        # Instatiate an Artifact object for each artifact in the manifest.
        for artifact in response.json()["properties"]["artifacts"]:
            artifact_name = artifact["artifactName"]
            artifact_version = artifact["artifactVersion"]

            artifacts.append(
                Artifact(
                    artifact_name=artifact_name,
                    artifact_type=artifact["artifactType"],
                    artifact_version=artifact_version,
                    artifact_client=self._get_artifact_client(
                        artifact_name, artifact_version
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
        if self._manifest_credentials["credentialType"] == "AzureStorageAccountToken":
            container_basename = artifact_name.replace("-", "")
            blob_url = self._get_blob_url(f"{container_basename}-{artifact_version}")
            return BlobClient.from_blob_url(blob_url)
        else:
            return self._oras_client(self._manifest_credentials["acrServerUrl"])

    def _get_blob_url(self, container_name: str) -> str:
        """
        Get the URL for the blob to be uploaded to the storage account artifact store.

        :param container_name: name of the container 
        """
        for container_credential in self._manifest_credentials["containerCredentials"]:
            if container_credential["containerName"] == container_name:
                sas_uri = str(container_credential["containerSasUri"])
                sas_uri_prefix = sas_uri.split("?")[0]
                sas_uri_token = sas_uri.split("?")[1]

                return f"{sas_uri_prefix}/{container_name}?{sas_uri_token}"
        raise KeyError(f"Manifest does not include a credential for {container_name}.")
