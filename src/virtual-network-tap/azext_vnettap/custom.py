# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=protected-access

from .aaz.latest.network.vnet.tap import Create as _CreateVnetTap
from .aaz.latest.network.nic.vtap_config import Create as _CreateVtapConfig
from azure.cli.core.util import parse_proxy_resource_id
from azure.cli.core.azclierror import InvalidArgumentValueError


class CreateVnetTap(_CreateVnetTap):

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZStrArg

        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.destination = AAZStrArg(
            options=["--destination"],
            help="Resource ID of the destination resource",
            required=True,
            arg_group="Destination"
        )
        args_schema.lb_id._registered = False
        args_schema.nic_id._registered = False

        return args_schema

    def pre_operations(self):
        args = self.ctx.args

        dest_err = 'Unable to parse --destination resource ID. Supply an IP configuration ID ' \
                   'for one of the following resource types: loadBalancers, networkInterfaces'
        destination = parse_proxy_resource_id(args.destination.to_serialized_data())
        if not destination:
            raise InvalidArgumentValueError(dest_err)

        dest_type = destination.get('type').lower()
        dest_args = {
            'loadbalancers': 'lb_id',
            'networkinterfaces': 'nic_id'
        }
        if dest_type in dest_args:
            setattr(args, dest_args[dest_type], args.destination)
        else:
            raise InvalidArgumentValueError(dest_err)


class CreateVtapConfig(_CreateVtapConfig):

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZStrArg

        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.vnet_tap = AAZStrArg(
            options=["--vnet-tap"],
            help="Name or ID of the virtual network tap.",
            required=True,
        )
        args_schema.vtap_id._required = False
        args_schema.vtap_id._registered = False

        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        template = "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Network/virtualNetworkTaps/{}"
        if not parse_proxy_resource_id(args.vnet_tap.to_serialized_data()):
            args.vtap_id = template.format(self.ctx.subscription_id, args.resource_group, args.vnet_tap)
        else:
            args.vtap_id = args.vnet_tap
