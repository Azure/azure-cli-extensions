# --------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT
# License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------
"""Contains class for deploying resources required by NFDs/NSDs via the SDK."""

from knack.log import get_logger

from azure.core import exceptions as azure_exceptions
from azure.cli.core.azclierror import AzCLIError
from azure.mgmt.resource.resources.v2022_09_01.models import ResourceGroup

from azure.mgmt.resource import ResourceManagementClient
from azext_aosm.util.management_clients import ApiClientsAndCaches
from azext_aosm.vendored_sdks import HybridNetworkManagementClient
from azext_aosm.vendored_sdks.models import (
    ArtifactStore,
    ArtifactStoreType,
    NetworkFunctionDefinitionGroup,
    NetworkServiceDesignGroup,
    Publisher,
)
from azext_aosm._configuration import Configuration, VNFConfiguration
from azext_aosm._constants import PROV_STATE_SUCCEEDED

logger = get_logger(__name__)


class PreDeployerViaSDK:
    """A class for checking or publishing resources required by NFDs/NSDs."""

    def __init__(
        self,
        apiClientsAndCaches: ApiClientsAndCaches,
        config: Configuration,
    ) -> None:
        """
        Initializes a new instance of the Deployer class.

        :param aosm_client: The client to use for managing AOSM resources.
        :type aosm_client: HybridNetworkManagementClient
        :param resource_client: The client to use for managing Azure resources.
        :type resource_client: ResourceManagementClient
        """

        self.api_clients = apiClientsAndCaches
        self.config = config

    def ensure_resource_group_exists(self, resource_group_name: str) -> None:
        """
        Checks whether a particular resource group exists on the subscription.
        Copied from virtutils.

        :param resource_group_name: The name of the resource group

        Raises a NotFoundError exception if the resource group does not exist.
        Raises a PermissionsError exception if we don't have permissions to check resource group existence.
        """
        rg: ResourceGroup
        if not self.api_clients.resource_client.resource_groups.check_existence(
            resource_group_name
        ):
            logger.info(f"RG {resource_group_name} not found. Create it.")
            print(f"Creating resource group {resource_group_name}.")
            rg_params: ResourceGroup = ResourceGroup(location=self.config.location)
            rg = self.api_clients.resource_client.resource_groups.create_or_update(
                resource_group_name, rg_params
            )
        else:
            print(f"Resource group {resource_group_name} exists.")
            rg = self.api_clients.resource_client.resource_groups.get(
                resource_group_name
            )

    def ensure_config_resource_group_exists(self) -> None:
        """
        Ensures that the publisher exists in the resource group.

        Finds the parameters from self.config
        """
        self.ensure_resource_group_exists(self.config.publisher_resource_group_name)

    def ensure_publisher_exists(
        self, resource_group_name: str, publisher_name: str, location: str
    ) -> None:
        """
        Ensures that the publisher exists in the resource group.

        :param resource_group_name: The name of the resource group.
        :type resource_group_name: str
        :param publisher_name: The name of the publisher.
        :type publisher_name: str
        :param location: The location of the publisher.
        :type location: str
        """
        logger.info("Creating publisher %s if it does not exist", publisher_name)
        try:
            pubby = self.api_clients.aosm_client.publishers.get(
                resource_group_name, publisher_name
            )
            print(
                f"Publisher {pubby.name} exists in resource group {resource_group_name}"
            )
        except azure_exceptions.ResourceNotFoundError:
            # Create the publisher
            print(
                f"Creating publisher {publisher_name} in resource group {resource_group_name}"
            )
            pub = self.api_clients.aosm_client.publishers.begin_create_or_update(
                resource_group_name=resource_group_name,
                publisher_name=publisher_name,
                parameters=Publisher(location=location, scope="Private"),
            )
            pub.result()

    def ensure_config_publisher_exists(self) -> None:
        """
        Ensures that the publisher exists in the resource group.

        Finds the parameters from self.config
        """
        self.ensure_publisher_exists(
            resource_group_name=self.config.publisher_resource_group_name,
            publisher_name=self.config.publisher_name,
            location=self.config.location,
        )

    def ensure_artifact_store_exists(
        self,
        resource_group_name: str,
        publisher_name: str,
        artifact_store_name: str,
        artifact_store_type: ArtifactStoreType,
        location: str,
    ) -> None:
        """
        Ensures that the artifact store exists in the resource group.

        :param resource_group_name: The name of the resource group.
        :type resource_group_name: str
        :param publisher_name: The name of the publisher.
        :type publisher_name: str
        :param artifact_store_name: The name of the artifact store.
        :type artifact_store_name: str
        :param artifact_store_type: The type of the artifact store.
        :type artifact_store_type: ArtifactStoreType
        :param location: The location of the artifact store.
        :type location: str
        """
        logger.info(
            "Creating artifact store %s if it does not exist",
            artifact_store_name,
        )
        try:
            self.api_clients.aosm_client.artifact_stores.get(
                resource_group_name=resource_group_name,
                publisher_name=publisher_name,
                artifact_store_name=artifact_store_name,
            )
            print(
                f"Artifact store {artifact_store_name} exists in resource group {resource_group_name}"
            )
        except azure_exceptions.ResourceNotFoundError:
            print(
                f"Create Artifact Store {artifact_store_name} of type {artifact_store_type}"
            )
            poller = (
                self.api_clients.aosm_client.artifact_stores.begin_create_or_update(
                    resource_group_name=resource_group_name,
                    publisher_name=publisher_name,
                    artifact_store_name=artifact_store_name,
                    parameters=ArtifactStore(
                        location=location,
                        store_type=artifact_store_type,
                    ),
                )
            )
            # Asking for result waits for provisioning state Succeeded before carrying
            # on
            arty: ArtifactStore = poller.result()

            if arty.provisioning_state != PROV_STATE_SUCCEEDED:
                logger.debug(f"Failed to provision artifact store: {arty.name}")
                raise RuntimeError(
                    f"Creation of artifact store proceeded, but the provisioning"
                    f" state returned is {arty.provisioning_state}. "
                    f"\nAborting"
                )
            logger.debug(
                f"Provisioning state of {artifact_store_name}"
                f": {arty.provisioning_state}"
            )

    def ensure_acr_artifact_store_exists(self) -> None:
        """
        Ensures that the ACR Artifact store exists.

        Finds the parameters from self.config
        """
        self.ensure_artifact_store_exists(
            self.config.publisher_resource_group_name,
            self.config.publisher_name,
            self.config.acr_artifact_store_name,
            ArtifactStoreType.AZURE_CONTAINER_REGISTRY,
            self.config.location,
        )

    def ensure_sa_artifact_store_exists(self) -> None:
        """
        Ensures that the Storage Account Artifact store for VNF exists.

        Finds the parameters from self.config
        """
        if not isinstance(self.config, VNFConfiguration):
            raise AzCLIError(
                "Check that storage account artifact store exists failed as requires VNFConfiguration file"
            )

        self.ensure_artifact_store_exists(
            self.config.publisher_resource_group_name,
            self.config.publisher_name,
            self.config.blob_artifact_store_name,
            ArtifactStoreType.AZURE_STORAGE_ACCOUNT,
            self.config.location,
        )

    def ensure_nfdg_exists(
        self,
        resource_group_name: str,
        publisher_name: str,
        nfdg_name: str,
        location: str,
    ):
        """
        Ensures that the network function definition group exists in the resource group.

        :param resource_group_name: The name of the resource group.
        :type resource_group_name: str
        :param publisher_name: The name of the publisher.
        :type publisher_name: str
        :param nfdg_name: The name of the network function definition group.
        :type nfdg_name: str
        :param location: The location of the network function definition group.
        :type location: str
        """

        logger.info(
            "Creating network function definition group %s if it does not exist",
            nfdg_name,
        )
        self.api_clients.aosm_client.network_function_definition_groups.begin_create_or_update(
            resource_group_name=resource_group_name,
            publisher_name=publisher_name,
            network_function_definition_group_name=nfdg_name,
            parameters=NetworkFunctionDefinitionGroup(location=location),
        )

    def ensure_config_nfdg_exists(
        self,
    ):
        """
        Ensures that the Network Function Definition Group exists.

        Finds the parameters from self.config
        """
        self.ensure_nfdg_exists(
            self.config.publisher_resource_group_name,
            self.config.publisher_name,
            self.config.nfdg_name,
            self.config.location,
        )

    def ensure_nsdg_exists(
        self,
        resource_group_name: str,
        publisher_name: str,
        nsdg_name: str,
        location: str,
    ):
        """
        Ensures that the network service design group exists in the resource group.

        :param resource_group_name: The name of the resource group.
        :type resource_group_name: str
        :param publisher_name: The name of the publisher.
        :type publisher_name: str
        :param nsdg_name: The name of the network service design group.
        :type nsdg_name: str
        :param location: The location of the network service design group.
        :type location: str
        """

        logger.info(
            "Creating network service design group %s if it does not exist",
            nsdg_name,
        )
        self.api_clients.aosm_client.network_service_design_groups.begin_create_or_update(
            resource_group_name=resource_group_name,
            publisher_name=publisher_name,
            network_service_design_group_name=nsdg_name,
            parameters=NetworkServiceDesignGroup(location=location),
        )

    def resource_exists_by_name(self, rg_name: str, resource_name: str) -> bool:
        """
        Determine if a resource with the given name exists. No checking is done as
        to the type.

        :param resource_name: The name of the resource to check.
        """
        logger.debug("Check if %s exists", resource_name)
        resources = self.api_clients.resource_client.resources.list_by_resource_group(
            resource_group_name=rg_name
        )

        resource_exists = False

        for resource in resources:
            if resource.name == resource_name:
                resource_exists = True
                break

        return resource_exists
