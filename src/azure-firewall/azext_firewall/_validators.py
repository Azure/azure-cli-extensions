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


def validate_ip_groups(cmd, namespace):
    from msrestazure.tools import is_valid_resource_id, resource_id

    def _validate_name_or_id(ip_group, subscription):
        # determine if public_ip_address is name or ID
        is_id = is_valid_resource_id(ip_group)
        return ip_group if is_id else resource_id(
            subscription=subscription,
            resource_group=namespace.resource_group_name,
            namespace='Microsoft.Network',
            type='ipGroups',
            name=ip_group)

    subscription = get_subscription_id(cmd.cli_ctx)
    if hasattr(namespace, 'destination_ip_groups') and namespace.destination_ip_groups is not None:
        for i, ip_group in enumerate(namespace.destination_ip_groups):
            namespace.destination_ip_groups[i] = _validate_name_or_id(ip_group, subscription)
    if hasattr(namespace, 'source_ip_groups') and namespace.source_ip_groups is not None:
        for i, ip_group in enumerate(namespace.source_ip_groups):
            namespace.source_ip_groups[i] = _validate_name_or_id(ip_group, subscription)


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
        if namespace.virtual_network_name is None:
            namespace.subnet = None
            return

        # determine if subnet is name or ID
        is_id = is_valid_resource_id(namespace.subnet)

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


def get_management_subnet_validator():
    from msrestazure.tools import is_valid_resource_id, resource_id
    from knack.util import CLIError

    def simple_validator(cmd, namespace):
        if any([namespace.management_virtual_network_name,
                namespace.management_item_name,
                namespace.management_public_ip_address]):
            if not all([namespace.management_virtual_network_name,
                        namespace.management_virtual_network_name,
                        namespace.management_public_ip_address]):
                raise CLIError("Usage error: --management-virtual-network-name, --management-ip-config-name "
                               "and --management-public-ip-address")
        else:
            return

        # determine if subnet is name or ID
        is_id = is_valid_resource_id(namespace.management_subnet)

        if not is_id:
            namespace.management_subnet = resource_id(
                subscription=get_subscription_id(cmd.cli_ctx),
                resource_group=namespace.resource_group_name,
                namespace='Microsoft.Network',
                type='virtualNetworks',
                name=namespace.management_virtual_network_name,
                child_type_1='subnets',
                child_name_1=namespace.management_subnet)

    return simple_validator


def get_management_public_ip_validator():
    """ Retrieves a validator for public IP address. Accepting all defaults will perform a check
    for an existing name or ID with no ARM-required -type parameter. """
    from msrestazure.tools import is_valid_resource_id, resource_id

    def simple_validator(cmd, namespace):
        if namespace.management_public_ip_address:
            is_list = isinstance(namespace.management_public_ip_address, list)

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
                for i, public_ip in enumerate(namespace.management_public_ip_address):
                    namespace.management_public_ip_address[i] = _validate_name_or_id(public_ip)
            else:
                namespace.management_public_ip_address = _validate_name_or_id(namespace.management_public_ip_address)

    return simple_validator


def validate_firewall_policy(cmd, namespace):
    from msrestazure.tools import is_valid_resource_id, resource_id

    if hasattr(namespace, 'base_policy') and namespace.base_policy is not None:
        if not is_valid_resource_id(namespace.base_policy):
            namespace.base_policy = resource_id(
                subscription=get_subscription_id(cmd.cli_ctx),
                resource_group=namespace.resource_group_name,
                namespace='Microsoft.Network',
                type='firewallPolicies',
                name=namespace.base_policy)

    if hasattr(namespace, 'firewall_policy') and namespace.firewall_policy is not None:
        if not is_valid_resource_id(namespace.firewall_policy):
            namespace.firewall_policy = resource_id(
                subscription=get_subscription_id(cmd.cli_ctx),
                resource_group=namespace.resource_group_name,
                namespace='Microsoft.Network',
                type='firewallPolicies',
                name=namespace.firewall_policy)


def validate_virtual_hub(cmd, namespace):
    from msrestazure.tools import is_valid_resource_id, resource_id

    if hasattr(namespace, 'virtual_hub') and namespace.virtual_hub is not None:

        if namespace.virtual_hub == '':
            return

        if not is_valid_resource_id(namespace.virtual_hub):
            namespace.virtual_hub = resource_id(
                subscription=get_subscription_id(cmd.cli_ctx),
                resource_group=namespace.resource_group_name,
                namespace='Microsoft.Network',
                type='virtualHubs',
                name=namespace.virtual_hub)


def validate_af_network_rule(cmd, namespace):
    from knack.util import CLIError
    validate_argument_count = 0
    if namespace.destination_addresses is not None:
        validate_argument_count += 1
    if namespace.destination_fqdns is not None:
        validate_argument_count += 1
    if namespace.destination_ip_groups is not None:
        validate_argument_count += 1
    if validate_argument_count != 1:
        raise CLIError('usage error: --destination-addresses | --destination-fqdns | --destination-ip-groups')
    validate_ip_groups(cmd, namespace)


def validate_af_nat_rule(cmd, namespace):
    from knack.util import CLIError
    if namespace.translated_address is None and namespace.translated_fqdn is None:
        raise CLIError('usage error: --translated-address | --translated-fqdn')
    if namespace.translated_address is not None and namespace.translated_fqdn is not None:
        raise CLIError('usage error: --translated-address | --translated-fqdn')
    validate_ip_groups(cmd, namespace)


def validate_af_application_rule(cmd, namespace):
    validate_application_rule_protocols(namespace)
    validate_ip_groups(cmd, namespace)


def validate_rule_group_collection(namespace):
    from knack.util import CLIError
    if namespace.target_fqdns is not None and namespace.fqdn_tags is not None:
        raise CLIError('usage error: --target-fqdns | --fqdn-tags')
    return namespace


def process_private_ranges(namespace):
    if namespace.private_ranges is not None:
        namespace.private_ranges = ', '.join(namespace.private_ranges)


def process_threat_intel_allowlist_ip_addresses(namespace):
    if namespace.ip_addresses is not None:
        namespace.ip_addresses = ', '.join(namespace.ip_addresses)


def process_threat_intel_allowlist_fqdns(namespace):
    if namespace.fqdns is not None:
        namespace.fqdns = ', '.join(namespace.fqdns)
