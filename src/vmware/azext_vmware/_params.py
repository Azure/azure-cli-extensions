# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long


def load_arguments(self, _):

    from azure.cli.core.commands.parameters import tags_type
    from azure.cli.core.commands.validators import get_default_location_from_resource_group

    with self.argument_context('vmware') as c:
        c.argument('tags', tags_type)
        c.argument('location', validator=get_default_location_from_resource_group)
        c.argument('private_cloud', options_list=['--private-cloud', '-c'], help='Name of the private cloud.')

    with self.argument_context('vmware private-cloud') as c:
        c.argument('circuit_primary_subnet', help='A /30 subnet for the primary circuit in the Express Route to configure routing between your network and Microsoft\'s Enterprise edge (MSEEs) routers.')
        c.argument('circuit_secondary_subnet', help='A /30 subnet for the secondary circuit in the Express Route to configure routing between your network and Microsoft\'s Enterprise edge (MSEEs) routers.')
        c.argument('cluster_size', help='Number of hosts for the default management cluster. Minimum of 3 and maximum of 16.')
        c.argument('network_block', help='A subnet at least of size /22. Make sure the CIDR format is conformed to (A.B.C.D/X) where A,B,C,D are between 0 and 255, and X is between 0 and 22.')

    with self.argument_context('vmware cluster') as c:
        c.argument('name', options_list=['--name', '-n'], help='Name of the cluster.')
        c.argument('sku', help='The product SKU.')
        c.argument('size', help='Number of hosts for the cluster. Minimum of 3 and a maximum of 16.')

    with self.argument_context('vmware private-cloud create') as c:
        c.argument('name', options_list=['--name', '-n'], help='Name of the private cloud.')
        c.argument('sku', help='The product SKU.')
        c.argument('internet', help='Connectivity to internet. Specify "Enabled" or "Disabled".')
        c.argument('vcenter_password', help='vCenter admin password.')
        c.argument('nsxt_password', help='NSX-T Manager password.')

    with self.argument_context('vmware private-cloud show') as c:
        c.argument('name', options_list=['--name', '-n'], help='Name of the private cloud.')

    with self.argument_context('vmware private-cloud update') as c:
        c.argument('name', options_list=['--name', '-n'], help='Name of the private cloud.')

    with self.argument_context('vmware private-cloud delete') as c:
        c.argument('name', options_list=['--name', '-n'], help='Name of the private cloud.')

    with self.argument_context('vmware authorization') as c:
        c.argument('name', options_list=['--name', '-n'], help='Name of the authorization.')

    with self.argument_context('vmware private-cloud addidentitysource') as c:
        c.argument('alias', help='The domain\'s NetBIOS name.')
        c.argument('base_group_dn', help='The base distinguished name for groups.')
        c.argument('base_user_dn', help='The base distinguished name for users.')
        c.argument('domain', help='The domain\'s dns name.')
        c.argument('name', options_list=['--name', '-n'], help='The name of the identity source.')
        c.argument('password', help='The password of the Active Directory user with a minimum of read-only access to Base DN for users and groups.')
        c.argument('primary_server', help='Primary server URL.')
        c.argument('secondary_server', help='Secondary server URL.')
        c.argument('ssl', help='Protect LDAP communication using SSL certificate (LDAPS). Specify "Enabled" or "Disabled".')
        c.argument('username', help='The ID of an Active Directory user with a minimum of read-only access to Base DN for users and group.')

    with self.argument_context('vmware private-cloud deleteidentitysource') as c:
        c.argument('alias', help='The domain\'s NetBIOS name.')
        c.argument('domain', help='The domain\'s dns name.')
        c.argument('name', options_list=['--name', '-n'], help='The name of the identity source.')

    with self.argument_context('vmware private-cloud update') as c:
        c.argument('name', options_list=['--name', '-n'], help='Name of the private cloud.')
        c.argument('internet', help='Connectivity to internet. Specify "Enabled" or "Disabled".')

    with self.argument_context('vmware hcx-enterprise-site') as c:
        c.argument('name', options_list=['--name', '-n'], help='The name of the HCX Enterprise Site.')
