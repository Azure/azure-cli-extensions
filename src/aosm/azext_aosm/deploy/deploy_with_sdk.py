# --------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT
# License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------
"""Contains class for deploying generated definitions using the Python SDK."""

from knack.log import get_logger
from azure.mgmt.resource import ResourceManagementClient
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


class DeployerViaSDK:
    """A class to deploy Artifact Manifests, NFDs and NSDs using the python SDK."""
    # @@@TODO - not sure this class is required as we can't publish complex objects
    # using the SDK
    
    def __init__(
        self,
        aosm_client: HybridNetworkManagementClient,
        resource_client: ResourceManagementClient,
    ) -> None:
        """
        Initializes a new instance of the Deployer class.

        :param aosm_client: The client to use for managing AOSM resources.
        :type aosm_client: HybridNetworkManagementClient
        :param resource_client: The client to use for managing Azure resources.
        :type resource_client: ResourceManagementClient
        """

        self.aosm_client = aosm_client
        self.resource_client = resource_client
        self.pre_deployer = PreDeployerViaSDK(aosm_client, resource_client)
            
    def publish_artifact_manifest(
        self,
        resource_group_name: str,
        location: str,
        publisher_name: str,
        artifact_store_name: str,
        artifact_manifest: ArtifactManifest,
    ) -> None:
        """
        Publishes an artifact manifest.

        :param resource_group_name: The name of the resource group.
        :type resource_group_name: str
        :param location: The location of the artifact manifest.
        :type location: str
        :param publisher_name: The name of the publisher.
        :type publisher_name: str
        :param artifact_store_name: The name of the artifact store.
        :type artifact_store_name: str
        :param artifact_manifest: The artifact manifest.
        :type artifact_manifest: ArtifactManifest
        """

        self.pre_deployer.ensure_publisher_exists(
            resource_group_name=resource_group_name,
            publisher_name=publisher_name,
            location=location,
        )

        artifact_types = [a.artifact_type for a in artifact_manifest.artifacts]

        if (
            ArtifactType.VHD_IMAGE_FILE
            or ArtifactType.IMAGE_FILE in artifact_types
        ):
            artifact_store_type = ArtifactStoreType.AZURE_STORAGE_ACCOUNT
        else:
            artifact_store_type = ArtifactStoreType.AZURE_CONTAINER_REGISTRY

        self.pre_deployer.ensure_artifact_store_exists(
            resource_group_name=resource_group_name,
            publisher_name=publisher_name,
            artifact_store_name=artifact_store_name,
            artifact_store_type=artifact_store_type,
            location=location,
        )

        logger.info("Creating artifact manifest %s", artifact_manifest.name)
        self.aosm_client.artifact_manifests.begin_create_or_update(
            resource_group_name=resource_group_name,
            publisher_name=publisher_name,
            artifact_store_name=artifact_store_name,
            artifact_manifest_name=artifact_manifest.name,
            parameters=artifact_manifest,
        )
        
    def publish_network_function_definition_version(
        self,
        resource_group_name: str,
        publisher_name: str,
        location: str,
        network_function_definition_group_name: str,
        network_function_definition_version: NetworkFunctionDefinitionVersion,
    ) -> None:
        """
        Publishes a network function definition version.

        :param resource_group_name: The name of the resource group.
        :type resource_group_name: str
        :param publisher_name: The name of the publisher.
        :type publisher_name: str
        :param location: The location of the network function definition version.
        :type location: str
        :param network_function_definition_group_name: The name of the network function definition group.
        :type network_function_definition_group_name: str
        :param network_function_definition_version: The network function definition version.
        :type network_function_definition_version: NetworkFunctionDefinitionVersion
        """

        self.pre_deployer.ensure_publisher_exists(
            resource_group_name=resource_group_name,
            publisher_name=publisher_name,
            location=location,
        )

        self.pre_deployer.ensure_nfdg_exists(
            resource_group_name=resource_group_name,
            publisher_name=publisher_name,
            nfdg_name=network_function_definition_group_name,
            location=location,
        )

        logger.info("Publishing network function definition version")
        self.aosm_client.network_function_definition_versions.begin_create_or_update(
            resource_group_name=resource_group_name,
            publisher_name=publisher_name,
            network_function_definition_group_name=network_function_definition_group_name,
            network_function_definition_version_name=network_function_definition_version.name,
            parameters=network_function_definition_version,
        )

    def publish_network_service_design_version(
        self,
        resource_group_name: str,
        publisher_name: str,
        location: str,
        network_service_design_group_name: str,
        network_service_design_version: NetworkServiceDesignVersion,
    ) -> None:
        """
        Publishes a network service design version.

        :param resource_group_name: The name of the resource group.
        :type resource_group_name: str
        :param publisher_name: The name of the publisher.
        :type publisher_name: str
        :param location: The location of the network service design version.
        :type location: str
        :param network_service_design_group_name: The name of the network service design group.
        :type network_service_design_group_name: str
        :param network_service_design_version: The network service design version.
        :type network_service_design_version: NetworkServiceDesignVersion
        """

        self.pre_deployer.ensure_publisher_exists(
            resource_group_name=resource_group_name,
            publisher_name=publisher_name,
            location=location,
        )

        self.pre_deployer.ensure_nsdg_exists(
            resource_group_name=resource_group_name,
            publisher_name=publisher_name,
            nsdg_name=network_service_design_group_name,
            location=location,
        )

        logger.info("Publishing network service design version")
        self.aosm_client.network_service_design_versions.begin_create_or_update(
            resource_group_name=resource_group_name,
            publisher_name=publisher_name,
            network_service_design_group_name=network_service_design_group_name,
            network_service_design_version_name=network_service_design_version.name,
            parameters=network_service_design_version,
        )
