# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.client_factory import get_subscription_id

from knack.util import CLIError
from knack.log import get_logger

logger = get_logger(__name__)


def validate_express_route_peering(cmd, namespace):
    from msrestazure.tools import is_valid_resource_id, resource_id
    circuit = namespace.circuit_name
    peering = namespace.peering

    if not circuit and not peering:
        return

    usage_error = CLIError('usage error: --peering ID | --peering NAME --circuit-name CIRCUIT')
    if not is_valid_resource_id(peering):
        namespace.peering = resource_id(
            subscription=get_subscription_id(cmd.cli_ctx),
            resource_group=namespace.resource_group_name,
            namespace='Microsoft.Network',
            type='expressRouteCircuits',
            name=circuit,
            child_type_1='peerings',
            child_name_1=peering
        )
    elif circuit:
        raise usage_error


def validate_express_route_port(cmd, namespace):
    from msrestazure.tools import is_valid_resource_id, resource_id
    if namespace.express_route_port and not is_valid_resource_id(namespace.express_route_port):
        namespace.express_route_port = resource_id(
            subscription=get_subscription_id(cmd.cli_ctx),
            resource_group=namespace.resource_group_name,
            namespace='Microsoft.Network',
            type='expressRoutePorts',
            name=namespace.express_route_port
        )


def validate_virtual_hub(cmd, namespace):
    from msrestazure.tools import is_valid_resource_id, resource_id
    if namespace.virtual_hub and not is_valid_resource_id(namespace.virtual_hub):
        namespace.virtual_hub = resource_id(
            subscription=get_subscription_id(cmd.cli_ctx),
            resource_group=namespace.resource_group_name,
            namespace='Microsoft.Network',
            type='virtualHubs',
            name=namespace.virtual_hub
        )


def bandwidth_validator_factory(mbps=True):
    def validator(namespace):
        return validate_circuit_bandwidth(namespace, mbps=mbps)
    return validator


def validate_circuit_bandwidth(namespace, mbps=True):
    # use gbps if mbps is False
    unit = 'mbps' if mbps else 'gbps'
    try:
        bandwidth = getattr(namespace, 'bandwidth_in_{}'.format(unit))
    except AttributeError:
        return

    if len(bandwidth) == 1:
        bandwidth_comps = bandwidth[0].split(' ')
    else:
        bandwidth_comps = bandwidth

    usage_error = CLIError('usage error: --bandwidth INT {Mbps,Gbps}')
    if len(bandwidth_comps) == 1:
        logger.warning('interpretting --bandwidth as %s. Consider being explicit: Mbps, Gbps', unit)
        setattr(namespace, 'bandwidth_in_{}'.format(unit), float(bandwidth_comps[0]))
        return
    elif len(bandwidth_comps) > 2:
        raise usage_error

    if float(bandwidth_comps[0]) and bandwidth_comps[1].lower() in ['mbps', 'gbps']:
        input_unit = bandwidth_comps[1].lower()
        if input_unit == unit:
            converted_bandwidth = float(bandwidth_comps[0])
        elif input_unit == 'gbps':
            converted_bandwidth = float(bandwidth_comps[0]) * 1000
        else:
            converted_bandwidth = float(bandwidth_comps[0]) / 1000
        setattr(namespace, 'bandwidth_in_{}'.format(unit), converted_bandwidth)
    else:
        raise usage_error
