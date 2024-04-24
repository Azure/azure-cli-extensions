# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from ..aaz.latest.vmware.workload_network.dhcp import Create as _DHCPCreate, Update as _DHCPUpdate, Delete as _DHCPDelete
from azure.cli.core.aaz import register_command

# dhcp relay


@register_command(
    "vmware workload-network dhcp relay create",
)
class DHCPRelayCreate(_DHCPCreate):
    """Create DHCP by ID in a private cloud workload network.

    :example: Create DHCP by ID in a workload network.
        az vmware workload-network dhcp relay create --resource-group group1 --private-cloud cloud1 --dhcp dhcp1 --display-name dhcpConfigurations1 --revision 1 --server-addresses 40.1.5.1/24
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZListArg, AAZStrArg, AAZListArgFormat
        args_schema = super()._build_arguments_schema(*args, **kwargs)

        args_schema.server_addresses = AAZListArg(
            options=["--server-addresses"],
            fmt=AAZListArgFormat(max_length=3),
            help="DHCP Relay Addresses. Max 3.",
        )
        server_addresses = args_schema.server_addresses
        server_addresses.Element = AAZStrArg()

        args_schema.relay._registered = False
        args_schema.server._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.relay.server_addresses = args.server_addresses


@register_command(
    "vmware workload-network dhcp relay delete",
    confirmation="This will delete the workload network DHCP. Are you sure?"
)
class DHCPRelayDelete(_DHCPDelete):
    """Delete DHCP by ID in a private cloud workload network.

    :example: Delete DHCP by ID in a workload network.
        az vmware workload-network dhcp relay delete --resource-group group1 --private-cloud cloud1 --dhcp dhcp1
    """


@register_command(
    "vmware workload-network dhcp relay update",
)
class DHCPRelayUpdate(_DHCPUpdate):
    """Create DHCP by ID in a private cloud workload network.

    :example: Update DHCP by ID in a workload network.
        az vmware workload-network dhcp relay update --resource-group group1 --private-cloud cloud1 --dhcp dhcp1 --display-name dhcpConfigurations1 --revision 1 --server-addresses 40.1.5.1/24
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZListArg, AAZStrArg, AAZListArgFormat
        args_schema = super()._build_arguments_schema(*args, **kwargs)

        args_schema.server_addresses = AAZListArg(
            options=["--server-addresses"],
            fmt=AAZListArgFormat(max_length=3),
            help="DHCP Relay Addresses. Max 3.",
            nullable=True,
        )
        server_addresses = args_schema.server_addresses
        server_addresses.Element = AAZStrArg(
            nullable=True,
        )

        args_schema.relay._registered = False
        args_schema.server._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.relay.server_addresses = args.server_addresses


# dhcp server


@register_command(
    "vmware workload-network dhcp server create",
)
class DHCPServerCreate(_DHCPCreate):
    """Create DHCP by ID in a private cloud workload network.

    :example: Create DHCP by ID in a workload network.
        az vmware workload-network dhcp server create --resource-group group1 --private-cloud cloud1 --dhcp dhcp1 --display-name dhcpConfigurations1 --revision 1 --server-address 40.1.5.1/24 --lease-time 86400
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZIntArg, AAZStrArg
        args_schema = super()._build_arguments_schema(*args, **kwargs)

        args_schema.lease_time = AAZIntArg(
            options=["--lease-time"],
            help="DHCP Server Lease Time.",
        )
        args_schema.server_address = AAZStrArg(
            options=["--server-address"],
            help="DHCP Server Address.",
        )

        args_schema.relay._registered = False
        args_schema.server._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.server.lease_time = args.lease_time
        args.server.server_address = args.server_address


@register_command(
    "vmware workload-network dhcp server delete",
    confirmation="This will delete the workload network DHCP. Are you sure?"
)
class DHCPServerDelete(_DHCPDelete):
    """Delete DHCP by ID in a private cloud workload network.

    :example: Delete DHCP by ID in a workload network.
        az vmware workload-network dhcp server delete --resource-group group1 --private-cloud cloud1 --dhcp dhcp1
    """


@register_command(
    "vmware workload-network dhcp server update",
)
class DHCPServerUpdate(_DHCPUpdate):
    """Update DHCP by ID in a private cloud workload network.

    :example: Update DHCP by ID in a workload network.
        az vmware workload-network dhcp server update --resource-group group1 --private-cloud cloud1 --dhcp dhcp1 --display-name dhcpConfigurations1 --revision 1 --server-address 40.1.5.1/24 --lease-time 86400
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZIntArg, AAZStrArg
        args_schema = super()._build_arguments_schema(*args, **kwargs)

        args_schema.lease_time = AAZIntArg(
            options=["--lease-time"],
            help="DHCP Server Lease Time.",
            nullable=True,
        )
        args_schema.server_address = AAZStrArg(
            options=["--server-address"],
            help="DHCP Server Address.",
            nullable=True,
        )

        args_schema.relay._registered = False
        args_schema.server._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.server.lease_time = args.lease_time
        args.server.server_address = args.server_address
