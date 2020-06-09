# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def network_client_factory(cli_ctx, aux_subscriptions=None, **_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from .profiles import CUSTOM_FIREWALL
    return get_mgmt_service_client(cli_ctx, CUSTOM_FIREWALL, aux_subscriptions=aux_subscriptions,
                                   api_version='2019-11-01')


def network_client_policy_factory(cli_ctx, aux_subscriptions=None, **_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from .profiles import CUSTOM_FIREWALL_POLICY
    return get_mgmt_service_client(cli_ctx, CUSTOM_FIREWALL_POLICY, aux_subscriptions=aux_subscriptions,
                                   api_version='2020-05-01')


def cf_firewalls(cli_ctx, _):
    return network_client_factory(cli_ctx).azure_firewalls


def cf_firewall_fqdn_tags(cli_ctx, _):
    return network_client_factory(cli_ctx).azure_firewall_fqdn_tags


def cf_firewall_policies(cli_ctx, _):
    return network_client_policy_factory(cli_ctx).firewall_policies


def cf_firewall_policy_rule_collection_groups(cli_ctx, _):
    return network_client_policy_factory(cli_ctx).firewall_policy_rule_collection_groups
