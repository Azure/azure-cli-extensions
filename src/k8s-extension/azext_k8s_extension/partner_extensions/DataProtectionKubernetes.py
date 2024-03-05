# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument
from knack.log import get_logger
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.azclierror import RequiredArgumentMissingError, InvalidArgumentValueError

from .DefaultExtension import DefaultExtension
from .._client_factory import cf_storage, cf_managed_clusters
from ..vendored_sdks.models import (Extension, PatchExtension, Scope, ScopeCluster)

logger = get_logger(__name__)


class DataProtectionKubernetes(DefaultExtension):
    def __init__(self):
        """Constants for configuration settings
           - Tenant Id (required)
           - Backup storage location (required)
           - Resource Limits (optional)
        """
        self.TENANT_ID = "credentials.tenantId"
        self.BACKUP_STORAGE_ACCOUNT_CONTAINER = "configuration.backupStorageLocation.bucket"
        self.BACKUP_STORAGE_ACCOUNT_NAME = "configuration.backupStorageLocation.config.storageAccount"
        self.BACKUP_STORAGE_ACCOUNT_RESOURCE_GROUP = "configuration.backupStorageLocation.config.resourceGroup"
        self.BACKUP_STORAGE_ACCOUNT_SUBSCRIPTION = "configuration.backupStorageLocation.config.subscriptionId"
        self.RESOURCE_LIMIT_CPU = "resources.limits.cpu"
        self.RESOURCE_LIMIT_MEMORY = "resources.limits.memory"
        self.BACKUP_STORAGE_ACCOUNT_USE_AAD = "configuration.backupStorageLocation.config.useAAD"
        self.BACKUP_STORAGE_ACCOUNT_STORAGE_ACCOUNT_URI = "configuration.backupStorageLocation.config.storageAccountURI"

        self.blob_container = "blobContainer"
        self.storage_account = "storageAccount"
        self.storage_account_resource_group = "storageAccountResourceGroup"
        self.storage_account_subscription = "storageAccountSubscriptionId"
        self.cpu_limit = "cpuLimit"
        self.memory_limit = "memoryLimit"
        self.use_aad = "useAAD"
        self.storage_account_uri = "storageAccountURI"

        self.configuration_mapping = {
            self.blob_container.lower(): self.BACKUP_STORAGE_ACCOUNT_CONTAINER,
            self.storage_account.lower(): self.BACKUP_STORAGE_ACCOUNT_NAME,
            self.storage_account_resource_group.lower(): self.BACKUP_STORAGE_ACCOUNT_RESOURCE_GROUP,
            self.storage_account_subscription.lower(): self.BACKUP_STORAGE_ACCOUNT_SUBSCRIPTION,
            self.cpu_limit.lower(): self.RESOURCE_LIMIT_CPU,
            self.memory_limit.lower(): self.RESOURCE_LIMIT_MEMORY,
            self.use_aad.lower(): self.BACKUP_STORAGE_ACCOUNT_USE_AAD,
            self.storage_account_uri.lower(): self.BACKUP_STORAGE_ACCOUNT_STORAGE_ACCOUNT_URI
        }

        self.bsl_configuration_settings = [
            self.blob_container,
            self.storage_account,
            self.storage_account_resource_group,
            self.storage_account_subscription
        ]

    def Create(
        self,
        cmd,
        client,
        resource_group_name,
        cluster_name,
        name,
        cluster_type,
        cluster_rp,
        extension_type,
        scope,
        auto_upgrade_minor_version,
        release_train,
        version,
        target_namespace,
        release_namespace,
        configuration_settings,
        configuration_protected_settings,
        configuration_settings_file,
        configuration_protected_settings_file,
        plan_name,
        plan_publisher,
        plan_product,
    ):
        # Current scope of DataProtection Kubernetes Backup extension is 'cluster' #TODO: add TSGs when they are in place
        if scope == 'namespace':
            raise InvalidArgumentValueError(f"Invalid scope '{scope}'. This extension can only be installed at 'cluster' scope.")

        scope_cluster = ScopeCluster(release_namespace=release_namespace)
        ext_scope = Scope(cluster=scope_cluster, namespace=None)

        if cluster_type.lower() != 'managedclusters':
            raise InvalidArgumentValueError(f"Invalid cluster type '{cluster_type}'. This extension can only be installed for managed clusters.")

        if release_namespace is not None:
            logger.warning(f"Ignoring 'release-namespace': {release_namespace}")

        tenant_id = self.__get_tenant_id(cmd.cli_ctx)
        if not tenant_id:
            raise SystemExit(logger.error("Unable to fetch TenantId. Please check your subscription or run 'az login' to login to Azure."))

        self.__validate_and_map_config(configuration_settings)
        self.__validate_backup_storage_account(cmd.cli_ctx, resource_group_name, cluster_name, configuration_settings)

        configuration_settings[self.TENANT_ID] = tenant_id

        if configuration_settings.get(self.BACKUP_STORAGE_ACCOUNT_USE_AAD) is None:
            logger.warning("useAAD flag is not specified. Setting it to 'true'. Please provide extension MSI Storage Blob Data Contributor role to the storage account.")
            configuration_settings[self.BACKUP_STORAGE_ACCOUNT_USE_AAD] = "true"

        if configuration_settings.get(self.BACKUP_STORAGE_ACCOUNT_STORAGE_ACCOUNT_URI) is None:
            logger.warning("storageAccountURI is not populated. Setting it to the storage account URI of provided storage account")
            configuration_settings[self.BACKUP_STORAGE_ACCOUNT_STORAGE_ACCOUNT_URI] = self.__get_storage_account_uri(cmd.cli_ctx, configuration_settings)
            logger.warning(f"storageAccountURI: {configuration_settings[self.BACKUP_STORAGE_ACCOUNT_STORAGE_ACCOUNT_URI]}")

        if release_train is None:
            release_train = 'stable'

        create_identity = True
        extension = Extension(
            extension_type=extension_type,
            auto_upgrade_minor_version=True,
            release_train=release_train,
            scope=ext_scope,
            configuration_settings=configuration_settings
        )
        return extension, name, create_identity

    def Update(
        self,
        cmd,
        resource_group_name,
        cluster_name,
        auto_upgrade_minor_version,
        release_train,
        version,
        configuration_settings,
        configuration_protected_settings,
        original_extension,
        yes=False,
    ):
        if configuration_settings is None:
            configuration_settings = {}

        bsl_specified = False
        if len(configuration_settings) > 0:
            bsl_specified = self.__is_bsl_specified(configuration_settings)
            self.__validate_and_map_config(configuration_settings, validate_bsl=bsl_specified)
            if bsl_specified:
                self.__validate_backup_storage_account(cmd.cli_ctx, resource_group_name, cluster_name, configuration_settings)
        # this step is for brownfield migrating to AAD
        if configuration_settings.get(self.BACKUP_STORAGE_ACCOUNT_USE_AAD) is not None and configuration_settings.get(self.BACKUP_STORAGE_ACCOUNT_USE_AAD).lower() == "true":
            logger.warning("useAAD flag is set to true. Please provide extension MSI Storage Blob Data Contributor role to the storage account.")

        if configuration_settings.get(self.BACKUP_STORAGE_ACCOUNT_STORAGE_ACCOUNT_URI) is None:
            # SA details provided in user inputs, but did not provide SA URI.
            logger.warning("storageAccountURI is not populated. Setting it to the storage account URI of provided storage account")
            if bsl_specified:
                configuration_settings[self.BACKUP_STORAGE_ACCOUNT_STORAGE_ACCOUNT_URI] = self.__get_storage_account_uri(cmd.cli_ctx, configuration_settings)
                logger.warning(f"storageAccountURI: {configuration_settings[self.BACKUP_STORAGE_ACCOUNT_STORAGE_ACCOUNT_URI]}")
            # SA details not provided in user input, SA Uri not provided in user input, and also not populated in the original extension, we populate it.
            elif not bsl_specified and original_extension.configuration_settings.get(self.BACKUP_STORAGE_ACCOUNT_STORAGE_ACCOUNT_URI) is None:
                configuration_settings[self.BACKUP_STORAGE_ACCOUNT_STORAGE_ACCOUNT_URI] = self.__get_storage_account_uri(cmd.cli_ctx, original_extension.configuration_settings)
                logger.warning(f"storageAccountURI: {configuration_settings[self.BACKUP_STORAGE_ACCOUNT_STORAGE_ACCOUNT_URI]}")

        return PatchExtension(
            auto_upgrade_minor_version=True,
            release_train=release_train,
            configuration_settings=configuration_settings,
        )

    def __get_tenant_id(self, cli_ctx):
        from azure.cli.core._profile import Profile
        if not cli_ctx.data.get('tenant_id'):
            cli_ctx.data['tenant_id'] = Profile(cli_ctx=cli_ctx).get_subscription()['tenantId']
        return cli_ctx.data['tenant_id']

    def __validate_and_map_config(self, configuration_settings, validate_bsl=True):
        """Validate and set configuration settings for Data Protection K8sBackup extension"""
        input_configuration_settings = dict(configuration_settings.items())
        input_configuration_keys = [key.lower() for key in configuration_settings]

        if validate_bsl:
            for key in self.bsl_configuration_settings:
                if key.lower() not in input_configuration_keys:
                    raise RequiredArgumentMissingError(f"Missing required configuration setting: {key}")

        for key in input_configuration_settings:
            _key = key.lower()
            if _key in self.configuration_mapping:
                configuration_settings[self.configuration_mapping[_key]] = configuration_settings.pop(key)
            else:
                configuration_settings.pop(key)
                logger.warning(f"Ignoring unrecognized configuration setting: {key}")

    def __validate_backup_storage_account(self, cli_ctx, resource_group_name, cluster_name, configuration_settings):
        """Validations performed on the backup storage account
           - Existance of the storage account
           - Cluster and storage account are in the same location
        """
        storage_account = self.__get_storage_account(cli_ctx, configuration_settings)

        cluster_subscription_id = get_subscription_id(cli_ctx)
        managed_clusters_client = cf_managed_clusters(cli_ctx, cluster_subscription_id)
        managed_cluster = managed_clusters_client.get(
            resource_group_name,
            cluster_name)

        if managed_cluster.location != storage_account.location:
            error_message = f"The Kubernetes managed cluster '{cluster_name} ({managed_cluster.location})' and the backup storage account '{configuration_settings[self.BACKUP_STORAGE_ACCOUNT_NAME]} ({storage_account.location})' are not in the same location. Please make sure that the cluster and the storage account are in the same location."
            raise SystemExit(logger.error(error_message))

    def __get_storage_account(self, cli_ctx, configuration_settings):
        """Get the storage account properties"""
        from azure.cli.core.commands.client_factory import get_mgmt_service_client
        from azure.mgmt.storage import StorageManagementClient

        sa_subscription_id = configuration_settings[self.BACKUP_STORAGE_ACCOUNT_SUBSCRIPTION]
        storage_account_client = get_mgmt_service_client(cli_ctx, StorageManagementClient, subscription_id=sa_subscription_id)

        return storage_account_client.storage_accounts.get_properties(
            configuration_settings[self.BACKUP_STORAGE_ACCOUNT_RESOURCE_GROUP],
            configuration_settings[self.BACKUP_STORAGE_ACCOUNT_NAME])

    def __get_storage_account_uri(self, cli_ctx, configuration_settings):
        """Get the storage account blob endpoint"""
        storage_account = self.__get_storage_account(cli_ctx, configuration_settings)
        return storage_account.primary_endpoints.blob

    def __is_bsl_specified(self, configuration_settings):
        """Check if the backup storage account is specified in the input"""
        input_configuration_keys = [key.lower() for key in configuration_settings]
        for key in self.bsl_configuration_settings:
            if key.lower() in input_configuration_keys:
                return True
        return False
