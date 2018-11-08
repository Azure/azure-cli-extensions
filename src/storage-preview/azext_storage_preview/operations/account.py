# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Custom operations for storage account commands"""

import os
from azure.cli.core.util import get_file_json, shell_safe_json_parse
from .._client_factory import storage_client_factory


# pylint: disable=too-many-locals
def create_storage_account(cmd, resource_group_name, account_name, sku=None, location=None, kind=None,
                           tags=None, custom_domain=None, encryption_services=None, access_tier=None, https_only=None,
                           file_aad=None, hierarchical_namespace=None, bypass=None, default_action=None,
                           assign_identity=False):
    StorageAccountCreateParameters, Kind, Sku, CustomDomain, AccessTier, Identity, Encryption, NetworkRuleSet = \
        cmd.get_models('StorageAccountCreateParameters', 'Kind', 'Sku', 'CustomDomain', 'AccessTier', 'Identity',
                       'Encryption', 'NetworkRuleSet')
    scf = storage_client_factory(cmd.cli_ctx)
    params = StorageAccountCreateParameters(sku=Sku(name=sku), kind=Kind(kind), location=location, tags=tags)
    if custom_domain:
        params.custom_domain = CustomDomain(name=custom_domain, use_sub_domain=None)
    if encryption_services:
        params.encryption = Encryption(services=encryption_services)
    if access_tier:
        params.access_tier = AccessTier(access_tier)
    if assign_identity:
        params.identity = Identity()
    if https_only:
        params.enable_https_traffic_only = https_only
    if file_aad:
        params.enable_azure_files_aad_integration = file_aad
    if hierarchical_namespace:
        params.is_hns_enabled = hierarchical_namespace

    if NetworkRuleSet and (bypass or default_action):
        if bypass and not default_action:
            from knack.util import CLIError
            raise CLIError('incorrect usage: --default-action ACTION [--bypass SERVICE ...]')
        params.network_rule_set = NetworkRuleSet(bypass=bypass, default_action=default_action, ip_rules=None,
                                                 virtual_network_rules=None)

    return scf.storage_accounts.create(resource_group_name, account_name, params)


# pylint: disable=too-many-locals
def update_storage_account(cmd, instance, sku=None, tags=None, custom_domain=None, use_subdomain=None,
                           encryption_services=None, encryption_key_source=None, encryption_key_vault_properties=None,
                           access_tier=None, https_only=None, file_aad=None, assign_identity=False, bypass=None,
                           default_action=None):
    StorageAccountUpdateParameters, Sku, CustomDomain, AccessTier, Identity, Encryption, NetworkRuleSet = \
        cmd.get_models('StorageAccountUpdateParameters', 'Sku', 'CustomDomain', 'AccessTier', 'Identity',
                       'Encryption', 'NetworkRuleSet')
    domain = instance.custom_domain
    if custom_domain is not None:
        domain = CustomDomain(name=custom_domain)
        if use_subdomain is not None:
            domain.name = use_subdomain == 'true'

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
        enable_https_traffic_only=https_only if https_only is not None else instance.enable_https_traffic_only,
        enable_azure_files_aad_integration=file_aad if file_aad is not None
        else instance.enable_azure_files_aad_integration
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
            from knack.util import CLIError
            raise CLIError('incorrect usage: --default-action ACTION [--bypass SERVICE ...]')
        params.network_rule_set = acl
    return params


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
