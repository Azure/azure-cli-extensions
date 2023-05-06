# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Custom operations for storage account commands"""

from knack.util import CLIError
from knack.log import get_logger
from .._client_factory import storage_client_factory

logger = get_logger(__name__)


# pylint: disable=too-many-locals, too-many-statements, too-many-branches, unused-argument
def create_storage_account(cmd, resource_group_name, account_name, sku=None, location=None, kind=None,
                           tags=None, custom_domain=None, encryption_services=None, encryption_key_source=None,
                           encryption_key_name=None, encryption_key_vault=None, encryption_key_version=None,
                           access_tier=None, https_only=None, enable_sftp=None, enable_local_user=None,
                           enable_files_aadkerb=None,
                           enable_files_aadds=None, bypass=None, default_action=None, assign_identity=False,
                           enable_large_file_share=None, enable_files_adds=None, domain_name=None,
                           net_bios_domain_name=None, forest_name=None, domain_guid=None, domain_sid=None,
                           sam_account_name=None, account_type=None,
                           azure_storage_sid=None, enable_hierarchical_namespace=None,
                           encryption_key_type_for_table=None, encryption_key_type_for_queue=None,
                           routing_choice=None, publish_microsoft_endpoints=None, publish_internet_endpoints=None,
                           require_infrastructure_encryption=None, allow_blob_public_access=None,
                           min_tls_version=None, allow_shared_key_access=None, edge_zone=None,
                           identity_type=None, user_identity_id=None,
                           key_vault_user_identity_id=None, federated_identity_client_id=None,
                           sas_expiration_period=None, key_expiration_period_in_days=None,
                           allow_cross_tenant_replication=None, default_share_permission=None,
                           enable_nfs_v3=None, subnet=None, vnet_name=None, action='Allow', enable_alw=None,
                           immutability_period_since_creation_in_days=None, immutability_policy_state=None,
                           allow_protected_append_writes=None, public_network_access=None, allowed_copy_scope=None,
                           dns_endpoint_type=None):
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
    if key_vault_user_identity_id is not None or federated_identity_client_id is not None:
        EncryptionIdentity = cmd.get_models('EncryptionIdentity')
        params.encryption.encryption_identity = EncryptionIdentity(
            encryption_user_assigned_identity=key_vault_user_identity_id,
            encryption_federated_identity_client_id=federated_identity_client_id
        )

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
    if enable_files_aadkerb is not None:
        if enable_files_aadkerb:
            active_directory_properties = None
            if domain_name or domain_guid:
                ActiveDirectoryProperties = cmd.get_models('ActiveDirectoryProperties')
                active_directory_properties = ActiveDirectoryProperties(domain_name=domain_name,
                                                                        domain_guid=domain_guid)
            params.azure_files_identity_based_authentication = AzureFilesIdentityBasedAuthentication(
                directory_service_options='AADKERB',
                active_directory_properties=active_directory_properties)
        else:
            params.azure_files_identity_based_authentication = AzureFilesIdentityBasedAuthentication(
                directory_service_options='None')

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
                                                                    azure_storage_sid=azure_storage_sid,
                                                                    sam_account_name=sam_account_name,
                                                                    account_type=account_type)
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

    if allowed_copy_scope is not None:
        params.allowed_copy_scope = allowed_copy_scope

    if dns_endpoint_type is not None:
        params.dns_endpoint_type = dns_endpoint_type

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


def get_storage_account_properties(cli_ctx, account_id):
    scf = storage_client_factory(cli_ctx)
    from msrestazure.tools import parse_resource_id
    result = parse_resource_id(account_id)
    return scf.storage_accounts.get_properties(result['resource_group'], result['name'])


# pylint: disable=too-many-locals, too-many-statements, too-many-branches, too-many-boolean-expressions, line-too-long
def update_storage_account(cmd, instance, sku=None, tags=None, custom_domain=None, use_subdomain=None,
                           encryption_services=None, encryption_key_source=None, encryption_key_version=None,
                           encryption_key_name=None, encryption_key_vault=None, enable_files_aadkerb=None,
                           access_tier=None, https_only=None, enable_sftp=None, enable_local_user=None,
                           enable_files_aadds=None, assign_identity=False,
                           bypass=None, default_action=None, enable_large_file_share=None, enable_files_adds=None,
                           domain_name=None, net_bios_domain_name=None, forest_name=None, domain_guid=None,
                           domain_sid=None, azure_storage_sid=None, sam_account_name=None, account_type=None,
                           routing_choice=None, publish_microsoft_endpoints=None, publish_internet_endpoints=None,
                           allow_blob_public_access=None, min_tls_version=None, allow_shared_key_access=None,
                           identity_type=None, user_identity_id=None,
                           key_vault_user_identity_id=None, federated_identity_client_id=None,
                           sas_expiration_period=None, key_expiration_period_in_days=None,
                           allow_cross_tenant_replication=None, default_share_permission=None,
                           immutability_period_since_creation_in_days=None, immutability_policy_state=None,
                           allow_protected_append_writes=None, public_network_access=None, allowed_copy_scope=None):
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

    if key_vault_user_identity_id is not None or federated_identity_client_id is not None:
        original_encryption_identity = params.encryption.encryption_identity if params.encryption else None
        EncryptionIdentity = cmd.get_models('EncryptionIdentity')
        if not original_encryption_identity:
            original_encryption_identity = EncryptionIdentity()
        params.encryption.encryption_identity = EncryptionIdentity(
            encryption_user_assigned_identity=key_vault_user_identity_id if key_vault_user_identity_id else original_encryption_identity.encryption_user_assigned_identity,
            encryption_federated_identity_client_id=federated_identity_client_id if federated_identity_client_id else original_encryption_identity.encryption_federated_identity_client_id
        )

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

    if enable_files_aadkerb is not None:
        if enable_files_aadkerb:  # enable AADKERB
            origin_storage_account = get_storage_account_properties(cmd.cli_ctx, instance.id)
            if origin_storage_account.azure_files_identity_based_authentication and \
                    origin_storage_account.azure_files_identity_based_authentication.directory_service_options \
                    == 'AADDS':
                raise CLIError("The Storage account already enabled AzureActiveDirectoryDomainServicesForFile, "
                               "please disable it by running this cmdlets with \"--enable-files-aadds false\" "
                               "before enable AzureActiveDirectoryKerberosForFile.")
            if origin_storage_account.azure_files_identity_based_authentication and \
                    origin_storage_account.azure_files_identity_based_authentication.directory_service_options == 'AD':
                raise CLIError("The Storage account already enabled ActiveDirectoryDomainServicesForFile, "
                               "please disable it by running this cmdlets with \"--enable-files-adds false\" "
                               "before enable AzureActiveDirectoryKerberosForFile.")
            active_directory_properties = None
            if domain_name or domain_guid:
                ActiveDirectoryProperties = cmd.get_models('ActiveDirectoryProperties')
                active_directory_properties = ActiveDirectoryProperties(domain_name=domain_name,
                                                                        domain_guid=domain_guid)
            params.azure_files_identity_based_authentication = AzureFilesIdentityBasedAuthentication(
                directory_service_options='AADKERB',
                active_directory_properties=active_directory_properties)

        else:  # disable AADKERB
            # Only disable AADKERB and keep others unchanged
            origin_storage_account = get_storage_account_properties(cmd.cli_ctx, instance.id)
            if not origin_storage_account.azure_files_identity_based_authentication or \
                    origin_storage_account.azure_files_identity_based_authentication.directory_service_options == 'AADKERB':
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
            if origin_storage_account.azure_files_identity_based_authentication and \
                    origin_storage_account.azure_files_identity_based_authentication.directory_service_options == 'AADKERB':
                raise CLIError("The Storage account already enabled AzureActiveDirectoryKerberosForFile, "
                               "please disable it by running this cmdlets with \"--enable-files-aadkerb false\" "
                               "before enable ActiveDirectoryDomainServicesForFile.")
            active_directory_properties = ActiveDirectoryProperties(domain_name=domain_name,
                                                                    net_bios_domain_name=net_bios_domain_name,
                                                                    forest_name=forest_name, domain_guid=domain_guid,
                                                                    domain_sid=domain_sid,
                                                                    azure_storage_sid=azure_storage_sid,
                                                                    sam_account_name=sam_account_name,
                                                                    account_type=account_type)
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

    if allowed_copy_scope is not None:
        params.allowed_copy_scope = allowed_copy_scope

    if enable_sftp is not None:
        params.is_sftp_enabled = enable_sftp
    if enable_local_user is not None:
        params.is_local_user_enabled = enable_local_user

    return params
