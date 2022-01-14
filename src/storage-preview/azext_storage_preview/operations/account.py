# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Custom operations for storage account commands"""

import os
from azure.cli.core.util import get_file_json, shell_safe_json_parse
from knack.util import CLIError
from knack.log import get_logger
from .._client_factory import storage_client_factory

logger = get_logger(__name__)


# pylint: disable=too-many-locals, too-many-statements, too-many-branches, unused-argument
def create_storage_account(cmd, resource_group_name, account_name, sku=None, location=None, kind=None,
                           tags=None, custom_domain=None, encryption_services=None, encryption_key_source=None,
                           encryption_key_name=None, encryption_key_vault=None, encryption_key_version=None,
                           access_tier=None, https_only=None, enable_sftp=None, enable_local_user=None,
                           enable_files_aadds=None, bypass=None, default_action=None, assign_identity=False,
                           enable_large_file_share=None, enable_files_adds=None, domain_name=None,
                           net_bios_domain_name=None, forest_name=None, domain_guid=None, domain_sid=None,
                           azure_storage_sid=None, enable_hierarchical_namespace=None,
                           encryption_key_type_for_table=None, encryption_key_type_for_queue=None,
                           routing_choice=None, publish_microsoft_endpoints=None, publish_internet_endpoints=None,
                           require_infrastructure_encryption=None, allow_blob_public_access=None,
                           min_tls_version=None, allow_shared_key_access=None, edge_zone=None,
                           identity_type=None, user_identity_id=None, key_vault_user_identity_id=None,
                           sas_expiration_period=None, key_expiration_period_in_days=None,
                           allow_cross_tenant_replication=None, default_share_permission=None,
                           enable_nfs_v3=None, subnet=None, vnet_name=None, action='Allow', enable_alw=None,
                           immutability_period_since_creation_in_days=None, immutability_policy_state=None,
                           allow_protected_append_writes=None, public_network_access=None):
    StorageAccountCreateParameters, Kind, Sku, CustomDomain, AccessTier, Identity, Encryption, NetworkRuleSet = \
        cmd.get_models('StorageAccountCreateParameters', 'Kind', 'Sku', 'CustomDomain', 'AccessTier', 'Identity',
                       'Encryption', 'NetworkRuleSet')
    scf = storage_client_factory(cmd.cli_ctx)
    if kind is None:
        logger.warning("The default kind for created storage account will change to 'StorageV2' from 'Storage' "
                       "in the future")
    params = StorageAccountCreateParameters(sku=Sku(name=sku), kind=Kind(kind), location=location, tags=tags,
                                            encryption=Encryption())
    # TODO: remove this part when server side remove the constraint
    if encryption_services is None:
        params.encryption.services = {'blob': {}}

    if custom_domain:
        params.custom_domain = CustomDomain(name=custom_domain, use_sub_domain=None)

    # Encryption
    if encryption_services:
        params.encryption = Encryption(services=encryption_services)

    if encryption_key_source is not None:
        params.encryption.key_source = encryption_key_source

    if params.encryption.key_source and params.encryption.key_source == "Microsoft.Keyvault":
        if params.encryption.key_vault_properties is None:
            KeyVaultProperties = cmd.get_models('KeyVaultProperties')
            params.encryption.key_vault_properties = KeyVaultProperties(key_name=encryption_key_name,
                                                                        key_vault_uri=encryption_key_vault,
                                                                        key_version=encryption_key_version)

    if identity_type and 'UserAssigned' in identity_type and user_identity_id:
        params.identity = Identity(type=identity_type, user_assigned_identities={user_identity_id: {}})
    elif identity_type:
        params.identity = Identity(type=identity_type)
    if key_vault_user_identity_id is not None:
        EncryptionIdentity = cmd.get_models('EncryptionIdentity')
        params.encryption.encryption_identity = EncryptionIdentity(
            encryption_user_assigned_identity=key_vault_user_identity_id)

    if access_tier:
        params.access_tier = AccessTier(access_tier)
    if assign_identity:
        params.identity = Identity(type='SystemAssigned')
    if https_only is not None:
        params.enable_https_traffic_only = https_only
    if enable_hierarchical_namespace is not None:
        params.is_hns_enabled = enable_hierarchical_namespace
    if enable_sftp is not None:
        params.is_sftp_enabled = enable_sftp
    if enable_local_user is not None:
        params.is_local_user_enabled = enable_local_user

    AzureFilesIdentityBasedAuthentication = cmd.get_models('AzureFilesIdentityBasedAuthentication')
    if enable_files_aadds is not None:
        params.azure_files_identity_based_authentication = AzureFilesIdentityBasedAuthentication(
            directory_service_options='AADDS' if enable_files_aadds else 'None')
    if enable_files_adds is not None:
        ActiveDirectoryProperties = cmd.get_models('ActiveDirectoryProperties')
        if enable_files_adds:  # enable AD
            if not (domain_name and net_bios_domain_name and forest_name and domain_guid and domain_sid and
                    azure_storage_sid):
                raise CLIError("To enable ActiveDirectoryDomainServicesForFile, user must specify all of: "
                               "--domain-name, --net-bios-domain-name, --forest-name, --domain-guid, --domain-sid and "
                               "--azure_storage_sid arguments in Azure Active Directory Properties Argument group.")

            active_directory_properties = ActiveDirectoryProperties(domain_name=domain_name,
                                                                    net_bios_domain_name=net_bios_domain_name,
                                                                    forest_name=forest_name, domain_guid=domain_guid,
                                                                    domain_sid=domain_sid,
                                                                    azure_storage_sid=azure_storage_sid)
            # TODO: Enabling AD will automatically disable AADDS. Maybe we should throw error message

            params.azure_files_identity_based_authentication = AzureFilesIdentityBasedAuthentication(
                directory_service_options='AD',
                active_directory_properties=active_directory_properties)

        else:  # disable AD
            if domain_name or net_bios_domain_name or forest_name or domain_guid or domain_sid or azure_storage_sid:  # pylint: disable=too-many-boolean-expressions
                raise CLIError("To disable ActiveDirectoryDomainServicesForFile, user can't specify any of: "
                               "--domain-name, --net-bios-domain-name, --forest-name, --domain-guid, --domain-sid and "
                               "--azure_storage_sid arguments in Azure Active Directory Properties Argument group.")

            params.azure_files_identity_based_authentication = AzureFilesIdentityBasedAuthentication(
                directory_service_options='None')

    if default_share_permission is not None:
        if params.azure_files_identity_based_authentication is None:
            params.azure_files_identity_based_authentication = AzureFilesIdentityBasedAuthentication(
                directory_service_options='None')
        params.azure_files_identity_based_authentication.default_share_permission = default_share_permission

    if enable_large_file_share:
        LargeFileSharesState = cmd.get_models('LargeFileSharesState')
        params.large_file_shares_state = LargeFileSharesState("Enabled")

    if NetworkRuleSet and (bypass or default_action or subnet):
        virtual_network_rules = None
        if bypass and not default_action:
            raise CLIError('incorrect usage: --default-action ACTION [--bypass SERVICE ...]')
        if subnet:
            from msrestazure.tools import is_valid_resource_id
            if not is_valid_resource_id(subnet):
                raise CLIError("Expected fully qualified resource ID: got '{}'".format(subnet))
            VirtualNetworkRule = cmd.get_models('VirtualNetworkRule')
            virtual_network_rules = [VirtualNetworkRule(virtual_network_resource_id=subnet,
                                                        action=action)]
        params.network_rule_set = NetworkRuleSet(
            bypass=bypass, default_action=default_action, ip_rules=None,
            virtual_network_rules=virtual_network_rules)

    if encryption_key_type_for_table is not None or encryption_key_type_for_queue is not None:
        EncryptionServices = cmd.get_models('EncryptionServices')
        EncryptionService = cmd.get_models('EncryptionService')
        params.encryption = Encryption()
        params.encryption.services = EncryptionServices()
        if encryption_key_type_for_table is not None:
            table_encryption_service = EncryptionService(enabled=True, key_type=encryption_key_type_for_table)
            params.encryption.services.table = table_encryption_service
        if encryption_key_type_for_queue is not None:
            queue_encryption_service = EncryptionService(enabled=True, key_type=encryption_key_type_for_queue)
            params.encryption.services.queue = queue_encryption_service

    if any([routing_choice, publish_microsoft_endpoints, publish_internet_endpoints]):
        RoutingPreference = cmd.get_models('RoutingPreference')
        params.routing_preference = RoutingPreference(
            routing_choice=routing_choice,
            publish_microsoft_endpoints=publish_microsoft_endpoints,
            publish_internet_endpoints=publish_internet_endpoints
        )
    if allow_blob_public_access is not None:
        params.allow_blob_public_access = allow_blob_public_access

    if require_infrastructure_encryption:
        params.encryption.require_infrastructure_encryption = require_infrastructure_encryption

    if min_tls_version:
        params.minimum_tls_version = min_tls_version

    if allow_shared_key_access is not None:
        params.allow_shared_key_access = allow_shared_key_access

    if edge_zone is not None:
        ExtendedLocation, ExtendedLocationTypes = cmd.get_models('ExtendedLocation', 'ExtendedLocationTypes')
        params.extended_location = ExtendedLocation(name=edge_zone,
                                                    type=ExtendedLocationTypes.EDGE_ZONE)

    if key_expiration_period_in_days is not None:
        KeyPolicy = cmd.get_models('KeyPolicy')
        params.key_policy = KeyPolicy(key_expiration_period_in_days=key_expiration_period_in_days)

    if sas_expiration_period:
        SasPolicy = cmd.get_models('SasPolicy')
        params.sas_policy = SasPolicy(sas_expiration_period=sas_expiration_period)

    if allow_cross_tenant_replication is not None:
        params.allow_cross_tenant_replication = allow_cross_tenant_replication

    if enable_nfs_v3 is not None:
        params.enable_nfs_v3 = enable_nfs_v3

    if enable_alw is not None:
        ImmutableStorageAccount = cmd.get_models('ImmutableStorageAccount')
        AccountImmutabilityPolicyProperties = cmd.get_models('AccountImmutabilityPolicyProperties')
        immutability_policy = None

        if any([immutability_period_since_creation_in_days, immutability_policy_state,
                allow_protected_append_writes is not None]):
            immutability_policy = AccountImmutabilityPolicyProperties(
                immutability_period_since_creation_in_days=immutability_period_since_creation_in_days,
                state=immutability_policy_state,
                allow_protected_append_writes=allow_protected_append_writes
            )

        params.immutable_storage_with_versioning = ImmutableStorageAccount(enabled=enable_alw,
                                                                           immutability_policy=immutability_policy)

    if public_network_access is not None:
        params.public_network_access = public_network_access

    return scf.storage_accounts.begin_create(resource_group_name, account_name, params)


def list_storage_accounts(cmd, resource_group_name=None):
    scf = storage_client_factory(cmd.cli_ctx)
    if resource_group_name:
        accounts = scf.storage_accounts.list_by_resource_group(resource_group_name)
    else:
        accounts = scf.storage_accounts.list()
    return list(accounts)


def show_storage_account_connection_string(cmd, resource_group_name, account_name, protocol='https', blob_endpoint=None,
                                           file_endpoint=None, queue_endpoint=None, table_endpoint=None,
                                           key_name='primary'):
    scf = storage_client_factory(cmd.cli_ctx)
    obj = scf.storage_accounts.list_keys(resource_group_name, account_name)  # pylint: disable=no-member
    try:
        keys = [obj.keys[0].value, obj.keys[1].value]  # pylint: disable=no-member
    except AttributeError:
        # Older API versions have a slightly different structure
        keys = [obj.key1, obj.key2]  # pylint: disable=no-member

    endpoint_suffix = cmd.cli_ctx.cloud.suffixes.storage_endpoint
    connection_string = 'DefaultEndpointsProtocol={};EndpointSuffix={};AccountName={};AccountKey={}'.format(
        protocol,
        endpoint_suffix,
        account_name,
        keys[0] if key_name == 'primary' else keys[1])  # pylint: disable=no-member
    connection_string = '{}{}'.format(connection_string,
                                      ';BlobEndpoint={}'.format(blob_endpoint) if blob_endpoint else '')
    connection_string = '{}{}'.format(connection_string,
                                      ';FileEndpoint={}'.format(file_endpoint) if file_endpoint else '')
    connection_string = '{}{}'.format(connection_string,
                                      ';QueueEndpoint={}'.format(queue_endpoint) if queue_endpoint else '')
    connection_string = '{}{}'.format(connection_string,
                                      ';TableEndpoint={}'.format(table_endpoint) if table_endpoint else '')
    return {'connectionString': connection_string}


def show_storage_account_usage(cmd, location):
    scf = storage_client_factory(cmd.cli_ctx)
    try:
        client = scf.usages
    except NotImplementedError:
        client = scf.usage
    return next((x for x in client.list_by_location(location) if x.name.value == 'StorageAccounts'), None)  # pylint: disable=no-member


def get_storage_account_properties(cli_ctx, account_id):
    scf = storage_client_factory(cli_ctx)
    from msrestazure.tools import parse_resource_id
    result = parse_resource_id(account_id)
    return scf.storage_accounts.get_properties(result['resource_group'], result['name'])


# pylint: disable=too-many-locals, too-many-statements, too-many-branches, too-many-boolean-expressions, line-too-long
def update_storage_account(cmd, instance, sku=None, tags=None, custom_domain=None, use_subdomain=None,
                           encryption_services=None, encryption_key_source=None, encryption_key_version=None,
                           encryption_key_name=None, encryption_key_vault=None,
                           access_tier=None, https_only=None, enable_sftp=None, enable_local_user=None,
                           enable_files_aadds=None, assign_identity=False,
                           bypass=None, default_action=None, enable_large_file_share=None, enable_files_adds=None,
                           domain_name=None, net_bios_domain_name=None, forest_name=None, domain_guid=None,
                           domain_sid=None, azure_storage_sid=None, routing_choice=None,
                           publish_microsoft_endpoints=None, publish_internet_endpoints=None,
                           allow_blob_public_access=None, min_tls_version=None, allow_shared_key_access=None,
                           identity_type=None, user_identity_id=None, key_vault_user_identity_id=None,
                           sas_expiration_period=None, key_expiration_period_in_days=None,
                           allow_cross_tenant_replication=None, default_share_permission=None,
                           immutability_period_since_creation_in_days=None, immutability_policy_state=None,
                           allow_protected_append_writes=None, public_network_access=None):
    StorageAccountUpdateParameters, Sku, CustomDomain, AccessTier, Identity, Encryption, NetworkRuleSet = \
        cmd.get_models('StorageAccountUpdateParameters', 'Sku', 'CustomDomain', 'AccessTier', 'Identity', 'Encryption',
                       'NetworkRuleSet')

    domain = instance.custom_domain
    if custom_domain is not None:
        domain = CustomDomain(name=custom_domain)
        if use_subdomain is not None:
            domain.use_sub_domain_name = use_subdomain == 'true'

    encryption = instance.encryption
    if not encryption and any((encryption_services, encryption_key_source, encryption_key_name,
                               encryption_key_vault, encryption_key_version is not None)):
        encryption = Encryption()
    if encryption_services:
        encryption.services = encryption_services

    if encryption_key_source:
        encryption.key_source = encryption_key_source

    if encryption.key_source and encryption.key_source == "Microsoft.Keyvault":
        if encryption.key_vault_properties is None:
            KeyVaultProperties = cmd.get_models('KeyVaultProperties')
            encryption.key_vault_properties = KeyVaultProperties()
    else:
        if any([encryption_key_name, encryption_key_vault, encryption_key_version]):
            raise ValueError(
                'Specify `--encryption-key-source=Microsoft.Keyvault` to configure key vault properties.')
        if encryption.key_vault_properties is not None:
            encryption.key_vault_properties = None

    if encryption_key_name:
        encryption.key_vault_properties.key_name = encryption_key_name
    if encryption_key_vault:
        encryption.key_vault_properties.key_vault_uri = encryption_key_vault
    if encryption_key_version is not None:
        encryption.key_vault_properties.key_version = encryption_key_version

    params = StorageAccountUpdateParameters(
        sku=Sku(name=sku) if sku is not None else instance.sku,
        tags=tags if tags is not None else instance.tags,
        custom_domain=domain,
        encryption=encryption,
        access_tier=AccessTier(access_tier) if access_tier is not None else instance.access_tier,
        enable_https_traffic_only=https_only if https_only is not None else instance.enable_https_traffic_only
    )

    if identity_type and 'UserAssigned' in identity_type and user_identity_id:
        user_assigned_identities = {user_identity_id: {}}
        if instance.identity.user_assigned_identities:
            for item in instance.identity.user_assigned_identities:
                if item != user_identity_id:
                    user_assigned_identities[item] = None
        params.identity = Identity(type=identity_type, user_assigned_identities=user_assigned_identities)
    elif identity_type:
        params.identity = Identity(type=identity_type)

    if key_vault_user_identity_id is not None:
        EncryptionIdentity = cmd.get_models('EncryptionIdentity')
        params.encryption.encryption_identity = EncryptionIdentity(
            encryption_user_assigned_identity=key_vault_user_identity_id)

    AzureFilesIdentityBasedAuthentication = cmd.get_models('AzureFilesIdentityBasedAuthentication')
    if enable_files_aadds is not None:
        if enable_files_aadds:  # enable AADDS
            origin_storage_account = get_storage_account_properties(cmd.cli_ctx, instance.id)
            if origin_storage_account.azure_files_identity_based_authentication and \
                    origin_storage_account.azure_files_identity_based_authentication.directory_service_options == 'AD':
                raise CLIError("The Storage account already enabled ActiveDirectoryDomainServicesForFile, "
                               "please disable it by running this cmdlets with \"--enable-files-adds false\" "
                               "before enable AzureActiveDirectoryDomainServicesForFile.")
            params.azure_files_identity_based_authentication = AzureFilesIdentityBasedAuthentication(
                directory_service_options='AADDS' if enable_files_aadds else 'None')
        else:  # Only disable AADDS and keep others unchanged
            origin_storage_account = get_storage_account_properties(cmd.cli_ctx, instance.id)
            if not origin_storage_account.azure_files_identity_based_authentication or \
                    origin_storage_account.azure_files_identity_based_authentication.directory_service_options\
                    == 'AADDS':
                params.azure_files_identity_based_authentication = AzureFilesIdentityBasedAuthentication(
                    directory_service_options='None')
            else:
                params.azure_files_identity_based_authentication = \
                    origin_storage_account.azure_files_identity_based_authentication

    if enable_files_adds is not None:
        ActiveDirectoryProperties = cmd.get_models('ActiveDirectoryProperties')
        if enable_files_adds:  # enable AD
            if not(domain_name and net_bios_domain_name and forest_name and domain_guid and domain_sid and
                   azure_storage_sid):
                raise CLIError("To enable ActiveDirectoryDomainServicesForFile, user must specify all of: "
                               "--domain-name, --net-bios-domain-name, --forest-name, --domain-guid, --domain-sid and "
                               "--azure_storage_sid arguments in Azure Active Directory Properties Argument group.")
            origin_storage_account = get_storage_account_properties(cmd.cli_ctx, instance.id)
            if origin_storage_account.azure_files_identity_based_authentication and \
                    origin_storage_account.azure_files_identity_based_authentication.directory_service_options \
                    == 'AADDS':
                raise CLIError("The Storage account already enabled AzureActiveDirectoryDomainServicesForFile, "
                               "please disable it by running this cmdlets with \"--enable-files-aadds false\" "
                               "before enable ActiveDirectoryDomainServicesForFile.")
            active_directory_properties = ActiveDirectoryProperties(domain_name=domain_name,
                                                                    net_bios_domain_name=net_bios_domain_name,
                                                                    forest_name=forest_name, domain_guid=domain_guid,
                                                                    domain_sid=domain_sid,
                                                                    azure_storage_sid=azure_storage_sid)
            # TODO: Enabling AD will automatically disable AADDS. Maybe we should throw error message

            params.azure_files_identity_based_authentication = AzureFilesIdentityBasedAuthentication(
                directory_service_options='AD',
                active_directory_properties=active_directory_properties)

        else:  # disable AD
            if domain_name or net_bios_domain_name or forest_name or domain_guid or domain_sid or azure_storage_sid:
                raise CLIError("To disable ActiveDirectoryDomainServicesForFile, user can't specify any of: "
                               "--domain-name, --net-bios-domain-name, --forest-name, --domain-guid, --domain-sid and "
                               "--azure_storage_sid arguments in Azure Active Directory Properties Argument group.")
            # Only disable AD and keep others unchanged
            origin_storage_account = get_storage_account_properties(cmd.cli_ctx, instance.id)
            if not origin_storage_account.azure_files_identity_based_authentication or \
                    origin_storage_account.azure_files_identity_based_authentication.directory_service_options == 'AD':
                params.azure_files_identity_based_authentication = AzureFilesIdentityBasedAuthentication(
                    directory_service_options='None')
            else:
                params.azure_files_identity_based_authentication = \
                    origin_storage_account.azure_files_identity_based_authentication
    if default_share_permission is not None:
        if params.azure_files_identity_based_authentication is None:
            params.azure_files_identity_based_authentication = AzureFilesIdentityBasedAuthentication(
                directory_service_options='None')
        params.azure_files_identity_based_authentication.default_share_permission = default_share_permission

    if assign_identity:
        params.identity = Identity(type='SystemAssigned')
    if enable_large_file_share:
        LargeFileSharesState = cmd.get_models('LargeFileSharesState')
        params.large_file_shares_state = LargeFileSharesState("Enabled")
    if NetworkRuleSet:
        acl = instance.network_rule_set
        if acl:
            if bypass:
                acl.bypass = bypass
            if default_action:
                acl.default_action = default_action
        elif default_action:
            acl = NetworkRuleSet(bypass=bypass, virtual_network_rules=None, ip_rules=None,
                                 default_action=default_action)
        elif bypass:
            raise CLIError('incorrect usage: --default-action ACTION [--bypass SERVICE ...]')
        params.network_rule_set = acl

    if hasattr(params, 'routing_preference') and any([routing_choice, publish_microsoft_endpoints,
                                                      publish_internet_endpoints]):
        if params.routing_preference is None:
            RoutingPreference = cmd.get_models('RoutingPreference')
            params.routing_preference = RoutingPreference()
        if routing_choice is not None:
            params.routing_preference.routing_choice = routing_choice
        if publish_microsoft_endpoints is not None:
            params.routing_preference.publish_microsoft_endpoints = publish_microsoft_endpoints
        if publish_internet_endpoints is not None:
            params.routing_preference.publish_internet_endpoints = publish_internet_endpoints

    if allow_blob_public_access is not None:
        params.allow_blob_public_access = allow_blob_public_access
    if min_tls_version:
        params.minimum_tls_version = min_tls_version

    if allow_shared_key_access is not None:
        params.allow_shared_key_access = allow_shared_key_access

    if key_expiration_period_in_days is not None:
        KeyPolicy = cmd.get_models('KeyPolicy')
        params.key_policy = KeyPolicy(key_expiration_period_in_days=key_expiration_period_in_days)

    if sas_expiration_period:
        SasPolicy = cmd.get_models('SasPolicy')
        params.sas_policy = SasPolicy(sas_expiration_period=sas_expiration_period)

    if allow_cross_tenant_replication is not None:
        params.allow_cross_tenant_replication = allow_cross_tenant_replication

    if any([immutability_period_since_creation_in_days, immutability_policy_state, allow_protected_append_writes is not None]):
        ImmutableStorageAccount = cmd.get_models('ImmutableStorageAccount')
        AccountImmutabilityPolicyProperties = cmd.get_models('AccountImmutabilityPolicyProperties')
        immutability_policy = None

        immutability_policy = AccountImmutabilityPolicyProperties(
            immutability_period_since_creation_in_days=immutability_period_since_creation_in_days,
            state=immutability_policy_state,
            allow_protected_append_writes=allow_protected_append_writes
        )

        params.immutable_storage_with_versioning = ImmutableStorageAccount(enabled=None,
                                                                           immutability_policy=immutability_policy)

    if public_network_access is not None:
        params.public_network_access = public_network_access

    if enable_sftp is not None:
        params.is_sftp_enabled = enable_sftp
    if enable_local_user is not None:
        params.is_local_user_enabled = enable_local_user

    return params


def create_blob_inventory_policy(cmd, client, resource_group_name, account_name, policy):
    # BlobInventoryPolicy = cmd.get_models('BlobInventoryPolicy')
    # TODO: add again with rule management if bandwidth is allowed
    # BlobInventoryPolicy, BlobInventoryPolicySchema, BlobInventoryPolicyRule, BlobInventoryPolicyDefinition, \
    # BlobInventoryPolicyFilter = cmd.get_models('BlobInventoryPolicy', 'BlobInventoryPolicySchema',
    #                                            'BlobInventoryPolicyRule', 'BlobInventoryPolicyDefinition',
    #                                            'BlobInventoryPolicyFilter')
    # filters = BlobInventoryPolicyFilter(prefix_match=prefix_match, blob_types=blob_types,
    #                                     include_blob_versions=include_blob_versions,
    #                                     include_snapshots=include_snapshots)
    # rule = BlobInventoryPolicyRule(enabled=True, name=rule_name,
    #                                definition=BlobInventoryPolicyDefinition(filters=filters))
    # policy = BlobInventoryPolicySchema(enabled=enabled, destination=destination,
    #                                    type=type, rules=[rule])
    # blob_inventory_policy = BlobInventoryPolicy(policy=policy)
    #
    # return client.create_or_update(resource_group_name=resource_group_name, account_name=account_name,
    #                                blob_inventory_policy_name=blob_inventory_policy_name,
    #                                properties=blob_inventory_policy,
    #                                **kwargs)
    if os.path.exists(policy):
        policy = get_file_json(policy)
    else:
        policy = shell_safe_json_parse(policy)

    BlobInventoryPolicy, InventoryRuleType, BlobInventoryPolicyName = \
        cmd.get_models('BlobInventoryPolicy', 'InventoryRuleType', 'BlobInventoryPolicyName')
    properties = BlobInventoryPolicy()
    if 'type' not in policy:
        policy['type'] = InventoryRuleType.INVENTORY
    properties.policy = policy

    return client.create_or_update(resource_group_name=resource_group_name, account_name=account_name,
                                   blob_inventory_policy_name=BlobInventoryPolicyName.DEFAULT, properties=properties)


def delete_blob_inventory_policy(cmd, client, resource_group_name, account_name):
    BlobInventoryPolicyName = cmd.get_models('BlobInventoryPolicyName')
    return client.delete(resource_group_name=resource_group_name, account_name=account_name,
                         blob_inventory_policy_name=BlobInventoryPolicyName.DEFAULT)


def get_blob_inventory_policy(cmd, client, resource_group_name, account_name):
    BlobInventoryPolicyName = cmd.get_models('BlobInventoryPolicyName')
    return client.get(resource_group_name=resource_group_name, account_name=account_name,
                      blob_inventory_policy_name=BlobInventoryPolicyName.DEFAULT)


def update_blob_inventory_policy(cmd, client, resource_group_name, account_name, parameters=None):
    BlobInventoryPolicyName = cmd.get_models('BlobInventoryPolicyName')
    return client.create_or_update(resource_group_name=resource_group_name, account_name=account_name,
                                   blob_inventory_policy_name=BlobInventoryPolicyName.DEFAULT, properties=parameters)


def list_network_rules(client, resource_group_name, account_name):
    sa = client.get_properties(resource_group_name, account_name)
    rules = sa.network_rule_set
    delattr(rules, 'bypass')
    delattr(rules, 'default_action')
    return rules


def add_network_rule(cmd, client, resource_group_name, account_name, action='Allow', subnet=None,
                     vnet_name=None, ip_address=None, tenant_id=None, resource_id=None):  # pylint: disable=unused-argument
    sa = client.get_properties(resource_group_name, account_name)
    rules = sa.network_rule_set
    if subnet:
        from msrestazure.tools import is_valid_resource_id
        if not is_valid_resource_id(subnet):
            raise CLIError("Expected fully qualified resource ID: got '{}'".format(subnet))
        VirtualNetworkRule = cmd.get_models('VirtualNetworkRule')
        if not rules.virtual_network_rules:
            rules.virtual_network_rules = []
        rules.virtual_network_rules = [r for r in rules.virtual_network_rules
                                       if r.virtual_network_resource_id.lower() != subnet.lower()]
        rules.virtual_network_rules.append(VirtualNetworkRule(virtual_network_resource_id=subnet, action=action))
    if ip_address:
        IpRule = cmd.get_models('IPRule')
        if not rules.ip_rules:
            rules.ip_rules = []
        rules.ip_rules = [r for r in rules.ip_rules if r.ip_address_or_range != ip_address]
        rules.ip_rules.append(IpRule(ip_address_or_range=ip_address, action=action))
    if resource_id:
        ResourceAccessRule = cmd.get_models('ResourceAccessRule')
        if not rules.resource_access_rules:
            rules.resource_access_rules = []
        rules.resource_access_rules = [r for r in rules.resource_access_rules if r.resource_id !=
                                       resource_id or r.tenant_id != tenant_id]
        rules.resource_access_rules.append(ResourceAccessRule(tenant_id=tenant_id, resource_id=resource_id))

    StorageAccountUpdateParameters = cmd.get_models('StorageAccountUpdateParameters')
    params = StorageAccountUpdateParameters(network_rule_set=rules)
    return client.update(resource_group_name, account_name, params)


def remove_network_rule(cmd, client, resource_group_name, account_name, ip_address=None, subnet=None,
                        vnet_name=None, tenant_id=None, resource_id=None):  # pylint: disable=unused-argument
    sa = client.get_properties(resource_group_name, account_name)
    rules = sa.network_rule_set
    if subnet:
        rules.virtual_network_rules = [x for x in rules.virtual_network_rules
                                       if not x.virtual_network_resource_id.endswith(subnet)]
    if ip_address:
        rules.ip_rules = [x for x in rules.ip_rules if x.ip_address_or_range != ip_address]

    if resource_id:
        rules.resource_access_rules = [x for x in rules.resource_access_rules if
                                       not (x.tenant_id == tenant_id and x.resource_id == resource_id)]

    StorageAccountUpdateParameters = cmd.get_models('StorageAccountUpdateParameters')
    params = StorageAccountUpdateParameters(network_rule_set=rules)
    return client.update(resource_group_name, account_name, params)


def create_management_policies(client, resource_group_name, account_name, policy=None):
    if policy:
        if os.path.exists(policy):
            policy = get_file_json(policy)
        else:
            policy = shell_safe_json_parse(policy)
    return client.create_or_update_management_policies(resource_group_name, account_name, policy=policy)


def update_management_policies(client, resource_group_name, account_name, parameters=None):
    if parameters:
        parameters = parameters.policy
    return client.create_or_update_management_policies(resource_group_name, account_name, policy=parameters)


def update_file_service_properties(cmd, instance, enable_delete_retention=None,
                                   delete_retention_days=None, enable_smb_multichannel=None,
                                   versions=None, authentication_methods=None, kerberos_ticket_encryption=None,
                                   channel_encryption=None):
    from azure.cli.core.azclierror import ValidationError
    params = {}
    # set delete retention policy according input
    if enable_delete_retention is not None:
        if enable_delete_retention is False:
            delete_retention_days = None
        instance.share_delete_retention_policy = cmd.get_models('DeleteRetentionPolicy')(
            enabled=enable_delete_retention, days=delete_retention_days)

    # If already enabled, only update days
    if enable_delete_retention is None and delete_retention_days is not None:
        if instance.share_delete_retention_policy is not None and instance.share_delete_retention_policy.enabled:
            instance.share_delete_retention_policy.days = delete_retention_days
        else:
            raise ValidationError(
                "Delete Retention Policy hasn't been enabled, and you cannot set delete retention days. "
                "Please set --enable-delete-retention as true to enable Delete Retention Policy.")

    # Fix the issue in server when delete_retention_policy.enabled=False, the returned days is 0
    # TODO: remove it when server side return null not 0 for days
    if instance.share_delete_retention_policy is not None and instance.share_delete_retention_policy.enabled is False:
        instance.share_delete_retention_policy.days = None
    if instance.share_delete_retention_policy:
        params['share_delete_retention_policy'] = instance.share_delete_retention_policy

    # set protocol settings
    if any([enable_smb_multichannel is not None, versions, authentication_methods, kerberos_ticket_encryption, channel_encryption]):
        params['protocol_settings'] = instance.protocol_settings
    if enable_smb_multichannel is not None:
        params['protocol_settings'].smb.multichannel = cmd.get_models('Multichannel')(enabled=enable_smb_multichannel)
    if versions is not None:
        params['protocol_settings'].smb.versions = versions
    if authentication_methods is not None:
        params['protocol_settings'].smb.authentication_methods = authentication_methods
    if kerberos_ticket_encryption is not None:
        params['protocol_settings'].smb.kerberos_ticket_encryption = kerberos_ticket_encryption
    if channel_encryption is not None:
        params['protocol_settings'].smb.channel_encryption = channel_encryption

    return params


def _generate_local_user(local_user, permission_scope=None, ssh_authorized_key=None,
                         home_directory=None, has_shared_key=None, has_ssh_key=None, has_ssh_password=None):
    if permission_scope is not None:
        local_user.permission_scopes = permission_scope
    if ssh_authorized_key is not None:
        local_user.ssh_authorized_keys = ssh_authorized_key
    if home_directory is not None:
        local_user.home_directory = home_directory
    if has_shared_key is not None:
        local_user.has_shared_key = has_shared_key
    if has_ssh_key is not None:
        local_user.has_ssh_key = has_ssh_key
    if has_ssh_password is not None:
        local_user.has_ssh_password = has_ssh_password


def create_local_user(cmd, client, resource_group_name, account_name, username, permission_scope=None, home_directory=None,
                      has_shared_key=None, has_ssh_key=None, has_ssh_password=None, ssh_authorized_key=None, **kwargs):
    LocalUser = cmd.get_models('LocalUser')
    local_user = LocalUser()

    _generate_local_user(local_user, permission_scope, ssh_authorized_key,
                         home_directory, has_shared_key, has_ssh_key, has_ssh_password)
    return client.create_or_update(resource_group_name=resource_group_name, account_name=account_name,
                                   username=username, properties=local_user)


def update_local_user(cmd, client, resource_group_name, account_name, username, permission_scope=None,
                      home_directory=None, has_shared_key=None, has_ssh_key=None, has_ssh_password=None,
                      ssh_authorized_key=None, **kwargs):
    local_user = client.get(resource_group_name, account_name, username)

    _generate_local_user(local_user, permission_scope, ssh_authorized_key,
                         home_directory, has_shared_key, has_ssh_key, has_ssh_password)
    return client.create_or_update(resource_group_name=resource_group_name, account_name=account_name,
                                   username=username, properties=local_user)
