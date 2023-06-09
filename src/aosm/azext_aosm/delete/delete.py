# --------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT
# License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------
"""Contains class for deploying generated definitions using the Python SDK."""
from knack.log import get_logger

from azext_aosm._configuration import NFConfiguration, NSConfiguration, VNFConfiguration
from azext_aosm.util.management_clients import ApiClients
from azext_aosm.util.utils import input_ack

logger = get_logger(__name__)


class ResourceDeleter:
    def __init__(
        self,
        api_clients: ApiClients,
        config: NFConfiguration or NSConfiguration,
    ) -> None:
        """
        Initializes a new instance of the Deployer class.

        :param aosm_client: The client to use for managing AOSM resources.
        :type aosm_client: HybridNetworkManagementClient
        :param resource_client: The client to use for managing Azure resources.
        :type resource_client: ResourceManagementClient
        """
        logger.debug("Create ARM/Bicep Deployer")
        self.api_clients = api_clients
        self.config = config

    def delete_vnf(self, clean: bool = False):
        """
        Delete the NFDV and manifests.  If they don't exist it still reports them as
        deleted.

        :param clean: Delete the NFDG, artifact stores and publisher too.     defaults
                to False     Use with care.
        """
        assert isinstance(self.config, VNFConfiguration)
        if clean:
            print(
                f"Are you sure you want to delete all resources associated with NFD {self.config.nf_name} including the artifact stores and publisher {self.config.publisher_name}?"
            )
            logger.warning(
                "This command will fail if other NFD versions exist in the NFD group."
            )
            logger.warning(
                "Only do this if you are SURE you are not sharing the publisher and artifact stores with other NFDs"
            )
            print("There is no undo.  Type the publisher name to confirm.")
            if not input_ack(self.config.publisher_name.lower(), "Confirm delete:"):
                print("Not proceeding with delete")
                return
        else:
            print(
                f"Are you sure you want to delete the NFD Version {self.config.version} and associated manifests from group {self.config.nfdg_name} and publisher {self.config.publisher_name}?"
            )
            print("There is no undo. Type 'delete' to confirm")
            if not input_ack("delete", "Confirm delete:"):
                print("Not proceeding with delete")
                return

        self.delete_nfdv()
        self.delete_artifact_manifest("sa")
        self.delete_artifact_manifest("acr")

        if clean:
            logger.info("Delete called for all resources.")
            self.delete_nfdg()
            self.delete_artifact_store("acr")
            self.delete_artifact_store("sa")
            self.delete_publisher()

    def delete_nsd(self):
        """
        Delete the NSDV and manifests.

        If they don't exist it still reports them as deleted.
        """
        assert isinstance(self.config, NSConfiguration)

        print(
            f"Are you sure you want to delete the NSD Version {self.config.nsd_version}, the associated manifest {self.config.acr_manifest_name} and configuration group schema {self.config.cg_schema_name}?"
        )
        print("There is no undo. Type 'delete' to confirm")
        if not input_ack("delete", "Confirm delete:"):
            print("Not proceeding with delete")
            return

        self.delete_nsdv()
        self.delete_artifact_manifest("acr")
        self.delete_config_group_schema()

    def delete_nfdv(self):
        message = f"Delete NFDV {self.config.version} from group {self.config.nfdg_name} and publisher {self.config.publisher_name}"
        logger.debug(message)
        print(message)
        try:
            poller = self.api_clients.aosm_client.network_function_definition_versions.begin_delete(
                resource_group_name=self.config.publisher_resource_group_name,
                publisher_name=self.config.publisher_name,
                network_function_definition_group_name=self.config.nfdg_name,
                network_function_definition_version_name=self.config.version,
            )
            poller.result()
            print("Deleted NFDV.")
        except Exception:
            logger.error(
                f"Failed to delete NFDV {self.config.version} from group {self.config.nfdg_name}"
            )
            raise

    def delete_nsdv(self):
        assert isinstance(self.config, NSConfiguration)
        message = f"Delete NSDV {self.config.nsd_version} from group {self.config.nsdg_name} and publisher {self.config.publisher_name}"
        logger.debug(message)
        print(message)
        try:
            poller = self.api_clients.aosm_client.network_service_design_versions.begin_delete(
                resource_group_name=self.config.publisher_resource_group_name,
                publisher_name=self.config.publisher_name,
                network_service_design_group_name=self.config.nsdg_name,
                network_service_design_version_name=self.config.nsd_version,
            )
            poller.result()
            print("Deleted NSDV.")
        except Exception:
            logger.error(
                f"Failed to delete NSDV {self.config.nsd_version} from group {self.config.nsdg_name}"
            )
            raise

    def delete_artifact_manifest(self, store_type: str) -> None:
        """
        _summary_

        :param store_type: "sa" or "acr"
        :raises CLIInternalError: If called with any other store type         :raises
                Exception if delete throws an exception
        """
        if store_type == "sa":
            assert isinstance(self.config, VNFConfiguration)
            store_name = self.config.blob_artifact_store_name
            manifest_name = self.config.sa_manifest_name
        elif store_type == "acr":
            store_name = self.config.acr_artifact_store_name
            manifest_name = self.config.acr_manifest_name
        else:
            from azure.cli.core.azclierror import CLIInternalError

            raise CLIInternalError(
                "Delete artifact manifest called for invalid store type. Valid types are sa and acr."
            )
        message = (
            f"Delete Artifact manifest {manifest_name} from artifact store {store_name}"
        )
        logger.debug(message)
        print(message)
        try:
            poller = self.api_clients.aosm_client.artifact_manifests.begin_delete(
                resource_group_name=self.config.publisher_resource_group_name,
                publisher_name=self.config.publisher_name,
                artifact_store_name=store_name,
                artifact_manifest_name=manifest_name,
            )
            poller.result()
            print("Deleted Artifact Manifest")
        except Exception:
            logger.error(
                f"Failed to delete Artifact manifest {manifest_name} from artifact store {store_name}"
            )
            raise

    def delete_nsdg(self) -> None:
        """Delete the NSDG."""
        message = f"Delete NSD Group {self.config.nsdg_name}"
        logger.debug(message)
        print(message)
        try:
            poller = (
                self.api_clients.aosm_client.network_service_design_groups.begin_delete(
                    resource_group_name=self.config.publisher_resource_group_name,
                    publisher_name=self.config.publisher_name,
                    network_service_design_group_name=self.config.nsdg_name,
                )
            )
            poller.result()
            print("Deleted NSD Group")
        except Exception:
            logger.error("Failed to delete NFDG.")
            raise

    def delete_nfdg(self) -> None:
        """Delete the NFDG."""
        message = f"Delete NFD Group {self.config.nfdg_name}"
        logger.debug(message)
        print(message)
        try:
            poller = self.api_clients.aosm_client.network_function_definition_groups.begin_delete(
                resource_group_name=self.config.publisher_resource_group_name,
                publisher_name=self.config.publisher_name,
                network_function_definition_group_name=self.config.nfdg_name,
            )
            poller.result()
            print("Deleted NFD Group")
        except Exception:
            logger.error("Failed to delete NFDG.")
            raise

    def delete_artifact_store(self, store_type: str) -> None:
        """Delete an artifact store
        :param store_type: "sa" or "acr"
        :raises CLIInternalError: If called with any other store type
        :raises Exception if delete throws an exception."""
        if store_type == "sa":
            assert isinstance(self.config, VNFConfiguration)
            store_name = self.config.blob_artifact_store_name
        elif store_type == "acr":
            store_name = self.config.acr_artifact_store_name
        else:
            from azure.cli.core.azclierror import CLIInternalError

            raise CLIInternalError(
                "Delete artifact store called for invalid store type. Valid types are sa and acr."
            )
        message = f"Delete Artifact store {store_name}"
        logger.debug(message)
        print(message)
        try:
            poller = self.api_clients.aosm_client.artifact_stores.begin_delete(
                resource_group_name=self.config.publisher_resource_group_name,
                publisher_name=self.config.publisher_name,
                artifact_store_name=store_name,
            )
            poller.result()
            print("Deleted Artifact Store")
        except Exception:
            logger.error(f"Failed to delete Artifact store {store_name}")
            raise

    def delete_publisher(self) -> None:
        """
        Delete the publisher.

        Warning - dangerous
        """
        message = f"Delete Publisher {self.config.publisher_name}"
        logger.debug(message)
        print(message)
        try:
            poller = self.api_clients.aosm_client.publishers.begin_delete(
                resource_group_name=self.config.publisher_resource_group_name,
                publisher_name=self.config.publisher_name,
            )
            poller.result()
            print("Deleted Publisher")
        except Exception:
            logger.error("Failed to delete publisher")
            raise

    def delete_config_group_schema(self) -> None:
        """Delete the Configuration Group Schema."""
        message = f"Delete Configuration Group Schema {self.config.cg_schema_name}"
        logger.debug(message)
        print(message)
        try:
            poller = (
                self.api_clients.aosm_client.configuration_group_schemas.begin_delete(
                    resource_group_name=self.config.publisher_resource_group_name,
                    publisher_name=self.config.publisher_name,
                    configuration_group_schema_name=self.config.cg_schema_name,
                )
            )
            poller.result()
            print("Deleted Configuration Group Schema")
        except Exception:
            logger.error("Failed to delete the Configuration Group Schema")
            raise
