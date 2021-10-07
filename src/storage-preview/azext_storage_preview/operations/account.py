# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Custom operations for storage account commands"""

import os
from azure.cli.core.util import get_file_json, shell_safe_json_parse
from knack.util import CLIError
from .._client_factory import storage_client_factory


# pylint: disable=too-many-locals
def create_storage_account(cmd, resource_group_name, account_name, sku=None, location=None, kind=None,
                           tags=None, custom_domain=None, encryption_services=None, access_tier=None, https_only=None,
                           hierarchical_namespace=None, bypass=None, default_action=None, assign_identity=False):
    StorageAccountCreateParameters, Kind, Sku, CustomDomain, AccessTier, Identity, Encryption, NetworkRuleSet = \
        cmd.get_models('StorageAccountCreateParameters', 'Kind', 'Sku', 'CustomDomain', 'AccessTier', 'Identity',
                       'Encryption', 'NetworkRuleSet')
    scf = storage_client_factory(cmd.cli_ctx)
    params = StorageAccountCreateParameters(sku=Sku(name=sku), kind=Kind(kind), location=location, tags=tags)
    if custom_domain:
        params.custom_domain = CustomDomain(name=custom_domain, use_sub_domain_name=None)
    if encryption_services:
        params.encryption = Encryption(services=encryption_services)
    if access_tier:
        params.access_tier = AccessTier(access_tier)
    if assign_identity:
        params.identity = Identity()
    if https_only:
        params.enable_https_traffic_only = https_only
    if hierarchical_namespace:
        params.is_hns_enabled = hierarchical_namespace

    if NetworkRuleSet and (bypass or default_action):
        if bypass and not default_action:
            raise CLIError('incorrect usage: --default-action ACTION [--bypass SERVICE ...]')
        params.network_rule_set = NetworkRuleSet(bypass=bypass, default_action=default_action, ip_rules=None,
                                                 virtual_network_rules=None)

    return scf.storage_accounts.create(resource_group_name, account_name, params)


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
