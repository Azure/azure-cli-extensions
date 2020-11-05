# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Custom operations for storage account commands"""

import os
from azure.cli.core.util import get_file_json, shell_safe_json_parse, find_child_item
from knack.log import get_logger
from knack.util import CLIError
from .._client_factory import storage_client_factory

logger = get_logger(__name__)


def str2bool(v):
    if v is not None:
        return v.lower() == "true"
    return v


# pylint: disable=too-many-locals, too-many-statements, too-many-branches
def create_storage_account(cmd, resource_group_name, account_name, sku=None, location=None, kind=None,
                           tags=None, custom_domain=None, encryption_services=None, access_tier=None, https_only=None,
                           enable_files_aadds=None, bypass=None, default_action=None, assign_identity=False,
                           enable_large_file_share=None, enable_files_adds=None, domain_name=None,
                           net_bios_domain_name=None, forest_name=None, domain_guid=None, domain_sid=None,
                           azure_storage_sid=None, enable_hierarchical_namespace=None,
                           encryption_key_type_for_table=None, encryption_key_type_for_queue=None,
                           routing_choice=None, publish_microsoft_endpoints=None, publish_internet_endpoints=None,
                           require_infrastructure_encryption=None, allow_blob_public_access=None,
                           min_tls_version=None, extended_location_name=None, extended_location_type=None):
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
    if encryption_services:
        params.encryption = Encryption(services=encryption_services)
    if access_tier:
        params.access_tier = AccessTier(access_tier)
    if assign_identity:
        params.identity = Identity()
    if https_only is not None:
        params.enable_https_traffic_only = https_only
    if enable_hierarchical_namespace is not None:
        params.is_hns_enabled = enable_hierarchical_namespace

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

    if enable_large_file_share:
        LargeFileSharesState = cmd.get_models('LargeFileSharesState')
        params.large_file_shares_state = LargeFileSharesState("Enabled")

    if NetworkRuleSet and (bypass or default_action):
        if bypass and not default_action:
            raise CLIError('incorrect usage: --default-action ACTION [--bypass SERVICE ...]')
        params.network_rule_set = NetworkRuleSet(bypass=bypass, default_action=default_action, ip_rules=None,
                                                 virtual_network_rules=None)

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
            publish_microsoft_endpoints=str2bool(publish_microsoft_endpoints),
            publish_internet_endpoints=str2bool(publish_internet_endpoints)
        )
    if allow_blob_public_access is not None:
        params.allow_blob_public_access = allow_blob_public_access

    if require_infrastructure_encryption:
        params.encryption.require_infrastructure_encryption = require_infrastructure_encryption

    if min_tls_version:
        params.minimum_tls_version = min_tls_version

    if extended_location_name is not None:
        ExtendedLocation = cmd.get_models('ExtendedLocation')
        params.extended_location = ExtendedLocation(name=extended_location_name,
                                                    type=extended_location_type)

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


# pylint: disable=too-many-locals
def update_storage_account(cmd, instance, sku=None, tags=None, custom_domain=None, use_subdomain=None,
                           encryption_services=None, encryption_key_source=None, encryption_key_vault_properties=None,
                           access_tier=None, https_only=None, assign_identity=False, bypass=None,
                           default_action=None):
    StorageAccountUpdateParameters, Sku, CustomDomain, AccessTier, Identity, Encryption, NetworkRuleSet = \
        cmd.get_models('StorageAccountUpdateParameters', 'Sku', 'CustomDomain', 'AccessTier', 'Identity',
                       'Encryption', 'NetworkRuleSet')
    domain = instance.custom_domain
    if custom_domain is not None:
        domain = CustomDomain(name=custom_domain)
        if use_subdomain is not None:
            domain.use_sub_domain_name = use_subdomain == 'true'

    encryption = instance.encryption
    if encryption_services:
        if not encryption:
            encryption = Encryption(services=encryption_services)
        else:
            encryption.services = encryption_services

    if encryption_key_source or encryption_key_vault_properties:
        if encryption:
            encryption.key_source = encryption_key_source
            encryption.key_vault_properties = encryption_key_vault_properties
        else:
            raise ValueError('--encryption-services is required when configure encryption key source')

    params = StorageAccountUpdateParameters(
        sku=Sku(name=sku) if sku is not None else instance.sku,
        tags=tags if tags is not None else instance.tags,
        custom_domain=domain,
        encryption=encryption,
        access_tier=AccessTier(access_tier) if access_tier is not None else instance.access_tier,
        enable_https_traffic_only=https_only if https_only is not None else instance.enable_https_traffic_only
    )
    if assign_identity:
        params.identity = Identity()

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
    return params


def create_blob_inventory_policy(cmd, client, resource_group_name, account_name, policy, blob_inventory_policy_name):
    #BlobInventoryPolicy = cmd.get_models('BlobInventoryPolicy')
    # TODO: add again with rule management if bandwidth is allowed
    BlobInventoryPolicy, BlobInventoryPolicySchema, BlobInventoryPolicyRule, BlobInventoryPolicyDefinition, \
    BlobInventoryPolicyFilter = cmd.get_models('BlobInventoryPolicy', 'BlobInventoryPolicySchema',
                                               'BlobInventoryPolicyRule', 'BlobInventoryPolicyDefinition',
                                               'BlobInventoryPolicyFilter')
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

    BlobInventoryPolicy, InventoryRuleType = cmd.get_models('BlobInventoryPolicy', 'InventoryRuleType')
    properties = BlobInventoryPolicy()
    if 'type' not in policy:
        policy['type'] = InventoryRuleType.INVENTORY
    properties.policy = policy

    return client.create_or_update(resource_group_name=resource_group_name, account_name=account_name,
                                   blob_inventory_policy_name=blob_inventory_policy_name, properties=properties)


def update_blob_inventory_policy(cmd, client, resource_group_name, account_name, blob_inventory_policy_name,
                                 parameters=None):
    return client.create_or_update(resource_group_name=resource_group_name, account_name=account_name,
                                   blob_inventory_policy_name=blob_inventory_policy_name, properties=parameters)


def add_blob_inventory_policy_rule(cmd, client, resource_group_name, account_name, policy_id,
                source_container, destination_container, min_creation_time=None, prefix_match=None):

    """
    Add rule for blob inventory policy
    """
    policy_properties = client.get(resource_group_name, account_name, policy_id)

    BlobInventoryPolicyRule, BlobInventoryPolicyFilter = \
        cmd.get_models('BlobInventoryPolicyRule', 'BlobInventoryPolicyFilter')
    new_or_rule = BlobInventoryPolicyRule(
        source_container=source_container,
        destination_container=destination_container,
        filters=BlobInventoryPolicyFilter(prefix_match=prefix_match, min_creation_time=min_creation_time)
    )
    policy_properties.rules.append(new_or_rule)
    return client.create_or_update(resource_group_name, account_name, policy_id, policy_properties)


def remove_blob_inventory_policy_rule(client, resource_group_name, account_name, policy_id, rule_id):

    or_policy = client.get(resource_group_name=resource_group_name,
                           account_name=account_name,
                           object_replication_policy_id=policy_id)

    rule = find_child_item(or_policy, rule_id, path='rules', key_path='rule_id')
    or_policy.rules.remove(rule)

    return client.create_or_update(resource_group_name, account_name, policy_id, or_policy)


def get_blob_inventory_policy_rule(client, resource_group_name, account_name, policy_id, rule_id):
    policy_properties = client.get(resource_group_name, account_name, policy_id)
    for rule in policy_properties.rules:
        if rule.rule_id == rule_id:
            return rule
    raise CLIError("{} does not exist.".format(rule_id))


def list_blob_inventory_policy_rules(client, resource_group_name, account_name, policy_id):
    policy_properties = client.get(resource_group_name, account_name, policy_id)
    return policy_properties.rules


def update_blob_inventory_policy_rule(client, resource_group_name, account_name, policy_id, rule_id, source_container=None,
                   destination_container=None, min_creation_time=None, prefix_match=None):

    policy_properties = client.get(resource_group_name, account_name, policy_id)

    for i, rule in enumerate(policy_properties.rules):
        if rule.rule_id == rule_id:
            if destination_container is not None:
                policy_properties.rules[i].destination_container = destination_container
            if source_container is not None:
                policy_properties.rules[i].source_container = source_container
            if min_creation_time is not None:
                policy_properties.rules[i].filters.min_creation_time = min_creation_time
            if prefix_match is not None:
                policy_properties.rules[i].filters.prefix_match = prefix_match

    client.create_or_update(resource_group_name=resource_group_name, account_name=account_name,
                            object_replication_policy_id=policy_id, properties=policy_properties)

    return get_blob_inventory_policy_rule(client, resource_group_name=resource_group_name, account_name=account_name,
                       policy_id=policy_id, rule_id=rule_id)


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
        rules.resource_access_rules = [r for r in rules.resource_access_rules if r.resource_id.lower() !=
                                       resource_id.lower() or r.tenant_id.lower() != tenant_id.lower()]
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
