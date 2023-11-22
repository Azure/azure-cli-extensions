# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Contains class for deploying resources required by NFDs/NSDs via the SDK."""

from typing import Optional

from azure.cli.core.azclierror import AzCLIError
from azure.cli.core.commands import LongRunningOperation
from azure.core import exceptions as azure_exceptions
from azure.mgmt.resource.resources.models import ResourceGroup
from knack.log import get_logger

from azext_aosm._configuration import (
    Configuration,
    VNFConfiguration,
)
from azext_aosm.util.management_clients import ApiClients
from azext_aosm.vendored_sdks.models import (
    ArtifactStore,
    ArtifactStorePropertiesFormat,
    ArtifactStoreType,
    NetworkFunctionDefinitionGroup,
    NetworkServiceDesignGroup,
    ProvisioningState,
    Publisher,
    PublisherPropertiesFormat,
    ManagedServiceIdentity
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
        config: Configuration,
        cli_ctx: Optional[object] = None,
    ) -> None:
        """
        Initializes a new instance of the Deployer class.

        :param api_clients: ApiClients object for AOSM and ResourceManagement
        :param config: The configuration for this NF
        :param cli_ctx: The CLI context. Used with all LongRunningOperation calls.
        """

        self.api_clients = api_clients
        self.config = config
        self.cli_ctx = cli_ctx

    def ensure_resource_group_exists(self, resource_group_name: str) -> None:
        """
        Checks whether a particular resource group exists on the subscription, and
        attempts to create it if not.

        :param resource_group_name: The name of the resource group
        """
        if not self.api_clients.resource_client.resource_groups.check_existence(
            resource_group_name
        ):
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
        except azure_exceptions.ResourceNotFoundError:
            # Create the publisher with default SAMI and private scope
            logger.info("Creating publisher %s if it does not exist", publisher_name)
            print(
                f"Creating publisher {publisher_name} in resource group"
                f" {resource_group_name}"
            )
            publisher_properties = PublisherPropertiesFormat(scope="Private")
            publisher_sami = ManagedServiceIdentity(type="SystemAssigned")
            poller = self.api_clients.aosm_client.publishers.begin_create_or_update(
                resource_group_name=resource_group_name,
                publisher_name=publisher_name,
                parameters=Publisher(location=location, properties=publisher_properties, identity=publisher_sami),
            )
            LongRunningOperation(self.cli_ctx, "Creating publisher...")(poller)

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
                f"Artifact store {artifact_store_name} exists in resource group"
                f" {resource_group_name}"
            )
        except azure_exceptions.ResourceNotFoundError as ex:
            print(
                f"Create Artifact Store {artifact_store_name} of type"
                f" {artifact_store_type}"
            )
            artifact_store_properties = ArtifactStorePropertiesFormat(store_type=artifact_store_type)
            poller = (
                self.api_clients.aosm_client.artifact_stores.begin_create_or_update(
                    resource_group_name=resource_group_name,
                    publisher_name=publisher_name,
                    artifact_store_name=artifact_store_name,
                    parameters=ArtifactStore(
                        location=location,
                        properties=artifact_store_properties,
                    ),
                )
            )
            # LongRunningOperation waits for provisioning state Succeeded before
            # carrying on
            artifactStore: ArtifactStore = LongRunningOperation(
                self.cli_ctx, "Creating Artifact Store..."
            )(poller)

            if artifactStore.properties.provisioning_state != ProvisioningState.SUCCEEDED:
                logger.debug("Failed to provision artifact store: %s", artifactStore.name)
                raise RuntimeError(
                    "Creation of artifact store proceeded, but the provisioning"
                    f" state returned is {artifactStore.properties.provisioning_state}. "
                    "\nAborting"
                ) from ex
            logger.debug(
                "Provisioning state of %s: %s",
                artifact_store_name,
                artifactStore.properties.provisioning_state,
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
            ArtifactStoreType.AZURE_CONTAINER_REGISTRY,  # type: ignore
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
            ArtifactStoreType.AZURE_STORAGE_ACCOUNT,  # type: ignore
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
            nfdg: NetworkFunctionDefinitionGroup = LongRunningOperation(
                self.cli_ctx, "Creating Network Function Definition Group..."
            )(poller)

            if nfdg.properties.provisioning_state != ProvisioningState.SUCCEEDED:
                logger.debug(
                    "Failed to provision Network Function Definition Group: %s",
                    nfdg.name,
                )
                raise RuntimeError(
                    "Creation of Network Function Definition Group proceeded, but the"
                    f" provisioning state returned is {nfdg.properties.provisioning_state}."
                    " \nAborting"
                ) from ex
            logger.debug(
                "Provisioning state of %s: %s", nfdg_name, nfdg.properties.provisioning_state
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

    def ensure_config_nsd_exists(
        self,
    ):
        """
        Ensures that the Network Service Design exists.

        Finds the parameters from self.config
        """
        self.ensure_nsd_exists(
            self.config.publisher_resource_group_name,
            self.config.publisher_name,
            self.config.nsd_name,
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
    ) -> bool:
        """Returns True if all required manifests exist, False otherwise."""
        all_acr_mannys_exist = True
        any_acr_mannys_exist: bool = not self.config.acr_manifest_names

        for manifest in self.config.acr_manifest_names:
            acr_manny_exists: bool = self.does_artifact_manifest_exist(
                rg_name=self.config.publisher_resource_group_name,
                publisher_name=self.config.publisher_name,
                store_name=self.config.acr_artifact_store_name,
                manifest_name=manifest,
            )
            all_acr_mannys_exist &= acr_manny_exists
            any_acr_mannys_exist |= acr_manny_exists

        if isinstance(self.config, VNFConfiguration):
            sa_manny_exists: bool = self.does_artifact_manifest_exist(
                rg_name=self.config.publisher_resource_group_name,
                publisher_name=self.config.publisher_name,
                store_name=self.config.blob_artifact_store_name,
                manifest_name=self.config.sa_manifest_name,
            )
            if all_acr_mannys_exist and sa_manny_exists:
                return True
            if any_acr_mannys_exist or sa_manny_exists:
                raise AzCLIError(
                    "Only a subset of artifact manifest exists. Cannot proceed. Please delete"
                    " the NFDV or NSDV as appropriate using the `az aosm nfd delete` or "
                    "`az aosm nsd delete` command."
                )
            return False

        return all_acr_mannys_exist

    def ensure_nsd_exists(
        self,
        resource_group_name: str,
        publisher_name: str,
        nsd_name: str,
        location: str,
    ):
        """
        Ensures that the network service design group exists in the resource group.

        :param resource_group_name: The name of the resource group.
        :type resource_group_name: str
        :param publisher_name: The name of the publisher.
        :type publisher_name: str
        :param nsd_name: The name of the network service design group.
        :type nsd_name: str
        :param location: The location of the network service design group.
        :type location: str
        """
        print(
            f"Creating Network Service Design {nsd_name} if it does not exist",
        )
        logger.info(
            "Creating Network Service Design  %s if it does not exist",
            nsd_name,
        )
        poller = self.api_clients.aosm_client.network_service_design_groups.begin_create_or_update(
            resource_group_name=resource_group_name,
            publisher_name=publisher_name,
            network_service_design_group_name=nsd_name,
            parameters=NetworkServiceDesignGroup(location=location),
        )
        LongRunningOperation(self.cli_ctx, "Creating Network Service Design...")(poller)

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
