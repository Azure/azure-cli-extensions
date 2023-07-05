# --------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT
# License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------
"""Contains class for deploying resources required by NFDs/NSDs via the SDK."""

import re
from azure.cli.core.azclierror import AzCLIError
from azure.core import exceptions as azure_exceptions
from azure.mgmt.resource.resources.models import ResourceGroup
from knack.log import get_logger
from typing import Union

from azext_aosm._configuration import (
    NFConfiguration,
    NSConfiguration,
    VNFConfiguration,
    CNFConfiguration,
)
from azext_aosm.util.constants import SOURCE_ACR_REGEX
from azext_aosm.util.management_clients import ApiClients
from azext_aosm.vendored_sdks.models import (
    ArtifactStore,
    ArtifactStoreType,
    NetworkFunctionDefinitionGroup,
    NetworkServiceDesignGroup,
    ProvisioningState,
    Publisher,
)

logger = get_logger(__name__)


class PreDeployerViaSDK:
    """
    A class for checking or publishing resources required by NFDs/NSDs.

    Uses the SDK to deploy rather than ARM, as the objects it deploys are not complex.
    """

    def __init__(
        self,
        api_clients: ApiClients,
        config: Union[NFConfiguration, NSConfiguration],
    ) -> None:
        """
        Initializes a new instance of the Deployer class.

        :param api_clients: ApiClients object for AOSM and ResourceManagement
        :param config: The configuration for this NF
        """

        self.api_clients = api_clients
        self.config = config

    def ensure_resource_group_exists(self, resource_group_name: str) -> None:
        """
        Checks whether a particular resource group exists on the subscription.
        Copied from virtutils.

        :param resource_group_name: The name of the resource group          Raises a
                NotFoundError exception if the resource group does not exist. Raises a
                PermissionsError exception if we don't have permissions to check
                resource group existence.
        """
        if not self.api_clients.resource_client.resource_groups.check_existence(
            resource_group_name
        ):
            if isinstance(self.config, NSConfiguration):
                raise AzCLIError(
                    f"Resource Group {resource_group_name} does not exist. Please"
                    " create it before running this command."
                )
            logger.info("RG %s not found. Create it.", resource_group_name)
            print(f"Creating resource group {resource_group_name}.")
            rg_params: ResourceGroup = ResourceGroup(location=self.config.location)
            self.api_clients.resource_client.resource_groups.create_or_update(
                resource_group_name, rg_params
            )
        else:
            print(f"Resource group {resource_group_name} exists.")
            self.api_clients.resource_client.resource_groups.get(resource_group_name)

    def ensure_config_resource_group_exists(self) -> None:
        """
        Ensures that the resource group exists.

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

        try:
            publisher = self.api_clients.aosm_client.publishers.get(
                resource_group_name, publisher_name
            )
            print(
                f"Publisher {publisher.name} exists in resource group"
                f" {resource_group_name}"
            )
        except azure_exceptions.ResourceNotFoundError as ex:
            if isinstance(self.config, NSConfiguration):
                raise AzCLIError(
                    f"Publisher {publisher_name} does not exist. Please create it"
                    " before running this command."
                ) from ex
            # Create the publisher
            logger.info("Creating publisher %s if it does not exist", publisher_name)
            print(
                f"Creating publisher {publisher_name} in resource group"
                f" {resource_group_name}"
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

    def ensure_config_source_registry_exists(self) -> None:
        """
        Ensures that the source registry exists

        Finds the parameters from self.config
        """
        assert isinstance(self.config, CNFConfiguration)
        logger.info(
            "Check if the source registry %s exists",
            self.config.source_registry_id,
        )

        # Match the source registry format
        source_registry_match = re.search(
            SOURCE_ACR_REGEX, self.config.source_registry_id
        )
        # Config validation has already checked and raised an error if the regex doesn't
        # match
        if source_registry_match and len(source_registry_match.groups()) > 1:
            source_registry_resource_group_name = source_registry_match.group(
                "resource_group"
            )
            source_registry_name = source_registry_match.group("registry_name")

            # This will raise an error if the registry does not exist
            assert self.api_clients.container_registry_client
            self.api_clients.container_registry_client.get(
                resource_group_name=source_registry_resource_group_name,
                registry_name=source_registry_name,
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
                f"Artifact store {artifact_store_name} exists in resource group"
                f" {resource_group_name}"
            )
        except azure_exceptions.ResourceNotFoundError as ex:
            print(
                f"Create Artifact Store {artifact_store_name} of type"
                f" {artifact_store_type}"
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

            if arty.provisioning_state != ProvisioningState.SUCCEEDED:
                logger.debug("Failed to provision artifact store: %s", arty.name)
                raise RuntimeError(
                    "Creation of artifact store proceeded, but the provisioning"
                    f" state returned is {arty.provisioning_state}. "
                    "\nAborting"
                ) from ex
            logger.debug(
                "Provisioning state of %s: %s",
                artifact_store_name,
                arty.provisioning_state,
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
            # This is a coding error but worth checking.
            raise AzCLIError(
                "Cannot check that the storage account artifact store exists as "
                "the configuration file doesn't map to VNFConfiguration"
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

        try:
            self.api_clients.aosm_client.network_function_definition_groups.get(
                resource_group_name=resource_group_name,
                publisher_name=publisher_name,
                network_function_definition_group_name=nfdg_name,
            )
            print(
                f"Network function definition group {nfdg_name} exists in resource"
                f" group {resource_group_name}"
            )
        except azure_exceptions.ResourceNotFoundError as ex:
            print(f"Create Network Function Definition Group {nfdg_name}")
            poller = self.api_clients.aosm_client.network_function_definition_groups.begin_create_or_update(
                resource_group_name=resource_group_name,
                publisher_name=publisher_name,
                network_function_definition_group_name=nfdg_name,
                parameters=NetworkFunctionDefinitionGroup(location=location),
            )

            # Asking for result waits for provisioning state Succeeded before carrying
            # on
            nfdg: NetworkFunctionDefinitionGroup = poller.result()

            if nfdg.provisioning_state != ProvisioningState.SUCCEEDED:
                logger.debug(
                    "Failed to provision Network Function Definition Group: %s",
                    nfdg.name,
                )
                raise RuntimeError(
                    "Creation of Network Function Definition Group proceeded, but the"
                    f" provisioning state returned is {nfdg.provisioning_state}."
                    " \nAborting"
                ) from ex
            logger.debug(
                "Provisioning state of %s: %s", nfdg_name, nfdg.provisioning_state
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

    def ensure_config_nsdg_exists(
        self,
    ):
        """
        Ensures that the Network Function Definition Group exists.

        Finds the parameters from self.config
        """
        self.ensure_nsdg_exists(
            self.config.publisher_resource_group_name,
            self.config.publisher_name,
            self.config.nsdg_name,
            self.config.location,
        )

    def does_artifact_manifest_exist(
        self, rg_name: str, publisher_name: str, store_name: str, manifest_name: str
    ) -> bool:
        try:
            self.api_clients.aosm_client.artifact_manifests.get(
                resource_group_name=rg_name,
                publisher_name=publisher_name,
                artifact_store_name=store_name,
                artifact_manifest_name=manifest_name,
            )
            logger.debug("Artifact manifest %s exists", manifest_name)
            return True
        except azure_exceptions.ResourceNotFoundError:
            logger.debug("Artifact manifest %s does not exist", manifest_name)
            return False

    def do_config_artifact_manifests_exist(
        self,
    ):
        """Returns True if all required manifests exist, False otherwise."""
        acr_manny_exists: bool = self.does_artifact_manifest_exist(
            rg_name=self.config.publisher_resource_group_name,
            publisher_name=self.config.publisher_name,
            store_name=self.config.acr_artifact_store_name,
            manifest_name=self.config.acr_manifest_name,
        )

        if isinstance(self.config, VNFConfiguration):
            sa_manny_exists: bool = self.does_artifact_manifest_exist(
                rg_name=self.config.publisher_resource_group_name,
                publisher_name=self.config.publisher_name,
                store_name=self.config.blob_artifact_store_name,
                manifest_name=self.config.sa_manifest_name,
            )
            if acr_manny_exists and sa_manny_exists:
                return True
            if acr_manny_exists or sa_manny_exists:
                raise AzCLIError(
                    "Only one artifact manifest exists. Cannot proceed. Please delete"
                    " the NFDV using `az aosm nfd delete` and start the publish again"
                    " from scratch."
                )
            return False

        return acr_manny_exists

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
