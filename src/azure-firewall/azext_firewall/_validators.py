# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.client_factory import get_subscription_id


def validate_application_rule_protocols(namespace):
    if not hasattr(namespace, 'protocols'):
        return

    protocol_list = []
    for item in namespace.protocols or []:
        from knack.util import CLIError
        usage_error = CLIError('usage error: --protocols PROTOCOL=PORT [PROTOCOL=PORT ...]')
        item_comps = item.split('=')
        if len(item_comps) != 2:
            raise usage_error
        protocol_list.append({'protocol_type': item_comps[0].lower().capitalize(), 'port': item_comps[1]})
    namespace.protocols = protocol_list


def get_public_ip_validator():
    """ Retrieves a validator for public IP address. Accepting all defaults will perform a check
    for an existing name or ID with no ARM-required -type parameter. """
    from msrestazure.tools import is_valid_resource_id, resource_id

    def simple_validator(cmd, namespace):
        if namespace.public_ip_address:
            is_list = isinstance(namespace.public_ip_address, list)

            def _validate_name_or_id(public_ip):
                # determine if public_ip_address is name or ID
                is_id = is_valid_resource_id(public_ip)
                return public_ip if is_id else resource_id(
                    subscription=get_subscription_id(cmd.cli_ctx),
                    resource_group=namespace.resource_group_name,
                    namespace='Microsoft.Network',
                    type='publicIPAddresses',
                    name=public_ip)

            if is_list:
                for i, public_ip in enumerate(namespace.public_ip_address):
                    namespace.public_ip_address[i] = _validate_name_or_id(public_ip)
            else:
                namespace.public_ip_address = _validate_name_or_id(namespace.public_ip_address)

    return simple_validator


def get_subnet_validator():
    from msrestazure.tools import is_valid_resource_id, resource_id

    def simple_validator(cmd, namespace):
        if namespace.virtual_network_name is None and namespace.subnet is None:
            return
        if namespace.subnet == '':
            return
        usage_error = ValueError('incorrect usage: ( --subnet ID | --subnet NAME --vnet-name NAME)')
        # error if vnet-name is provided without subnet
        if namespace.virtual_network_name and not namespace.subnet:
            raise usage_error

        # determine if subnet is name or ID
        is_id = is_valid_resource_id(namespace.subnet)

        # error if vnet-name is provided along with a subnet ID
        if is_id and namespace.virtual_network_name:
            raise usage_error
        if not is_id and not namespace.virtual_network_name:
            raise usage_error

        if not is_id:
            namespace.subnet = resource_id(
                subscription=get_subscription_id(cmd.cli_ctx),
                resource_group=namespace.resource_group_name,
                namespace='Microsoft.Network',
                type='virtualNetworks',
                name=namespace.virtual_network_name,
                child_type_1='subnets',
                child_name_1=namespace.subnet)

    return simple_validator


def validate_firewall_policy(cmd, namespace):
    from msrestazure.tools import is_valid_resource_id, resource_id

    if namespace.base_policy is None:
        return

    if not is_valid_resource_id(namespace.base_policy):
        namespace.base_policy = resource_id(
            subscription=get_subscription_id(cmd.cli_ctx),
            resource_group=namespace.resource_group_name,
            namespace='Microsoft.Network',
            type='firewallPolicies',
            name=namespace.base_policy)


def validate_af_network_rule(namespace):
    from knack.util import CLIError
    if namespace.destination_addresses is None and namespace.destination_fqdns is None:
        raise CLIError('usage error: --destination-addresses | --destination-fqdns')
    if namespace.destination_addresses is not None and namespace.destination_fqdns is not None:
        raise CLIError('usage error: --destination-addresses | --destination-fqdns')
    return namespace


def validate_af_nat_rule(namespace):
    from knack.util import CLIError
    if namespace.translated_address is None and namespace.translated_fqdn is None:
        raise CLIError('usage error: --translated-address | --translated-fqdn')
    if namespace.translated_address is not None and namespace.translated_fqdn is not None:
        raise CLIError('usage error: --translated-address | --translated-fqdn')
    return namespace


def validate_af_application_rule(namespace):
    return namespace


def validate_rule_group_collection(namespace):
    from knack.util import CLIError
    if namespace.target_fqdns is not None and namespace.fqdn_tags is not None:
        raise CLIError('usage error: --target-fqdns | --fqdn-tags')
    return namespace
