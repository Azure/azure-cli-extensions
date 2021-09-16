# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long,too-many-statements


from azext_vmware.action import ScriptExecutionNamedOutputAction, ScriptExecutionParameterAction
from azure.cli.core.commands.parameters import get_enum_type
from ._validators import server_addresses_length


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
        c.argument('accept_eula', help='Accept the end-user license agreement without prompting.')

    with self.argument_context('vmware private-cloud show') as c:
        c.argument('name', options_list=['--name', '-n'], help='Name of the private cloud.')

    with self.argument_context('vmware private-cloud update') as c:
        c.argument('name', options_list=['--name', '-n'], help='Name of the private cloud.')

    with self.argument_context('vmware private-cloud delete') as c:
        c.argument('name', options_list=['--name', '-n'], help='Name of the private cloud.')
        c.argument('yes', help='Deletes without confirmation.')

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

    with self.argument_context('vmware datastore') as c:
        c.argument('name', options_list=['--name', '-n'], help='The name of the datastore.')
        c.argument('cluster', help='The name of the cluster.')
        c.argument('lun_name', help='Name of the LUN to be used.')

    with self.argument_context('vmware datastore create') as c:
        c.argument('nfs_provider_ip', help='IP address of the NFS provider.')
        c.argument('nfs_file_path', help='File path through which the NFS volume is exposed by the provider.')
        c.argument('endpoints', nargs='*', help='iSCSI provider target IP address list.')

    with self.argument_context('vmware datastore netapp-volume create') as c:
        c.argument('volume_id', help='Azure resource ID of the NetApp volume.')

    with self.argument_context('vmware datastore disk-pool-volume create') as c:
        c.argument('target_id', help='Azure resource ID of the iSCSI target.')
        c.argument('mount_option', nargs='*', help='Mode that describes whether the LUN has to be mounted as a datastore or attached as a LUN.')
        c.argument('path', help='Device path.')

    with self.argument_context('vmware addon') as c:
        c.argument('name', options_list=['--name', '-n'], help='Name of the addon.')

    with self.argument_context('vmware addon vr') as c:
        c.argument('vrs_count', help='The vSphere Replication Server (VRS) count.')

    with self.argument_context('vmware addon hcx') as c:
        c.argument('offer', help='The HCX offer, example "VMware MaaS Cloud Provider (Enterprise)".')

    with self.argument_context('vmware addon srm') as c:
        c.argument('license_key', help='The Site Recovery Manager (SRM) license.')

    with self.argument_context('vmware global-reach-connection') as c:
        c.argument('name', options_list=['--name', '-n'], help='Name of the global reach connection.')

    with self.argument_context('vmware global-reach-connection create') as c:
        c.argument('peer_express_route_circuit', help='Identifier of the ExpressRoute Circuit to peer with.')
        c.argument('authorization_key', help='Authorization key from the peer express route.')

    with self.argument_context('vmware cloud-link') as c:
        c.argument('name', options_list=['--name', '-n'], help='The name of the cloud link.')
        c.argument('linked_cloud', help='Identifier of the other private cloud participating in the link.')

    with self.argument_context('vmware script-package') as c:
        c.argument('name', options_list=['--name', '-n'], help='Name of the script package.')

    with self.argument_context('vmware script-cmdlet') as c:
        c.argument('script_package', options_list=['--script-package', '-p'], help='Name of the script package.')
        c.argument('name', options_list=['--name', '-n'], help='Name of the script cmdlet.')

    with self.argument_context('vmware script-execution') as c:
        c.argument('name', options_list=['--name', '-n'], help='Name of the script execution.')

    with self.argument_context('vmware script-execution create') as c:
        c.argument('timeout', help='Time limit for execution.')
        c.argument('parameters', options_list=['--parameter', '-p'], action=ScriptExecutionParameterAction, nargs='*', help='Parameters the script will accept.')
        c.argument('hidden_parameters', options_list=['--hidden-parameter'], action=ScriptExecutionParameterAction, nargs='*', help='Parameters that will be hidden/not visible to ARM, such as passwords and credentials.')
        c.argument('failure_reason', help='Error message if the script was able to run, but if the script itself had errors or powershell threw an exception.')
        c.argument('retention', help='Time to live for the resource. If not provided, will be available for 60 days.')
        c.argument('out', help='Standard output stream from the powershell execution.')
        c.argument('named_outputs', action=ScriptExecutionNamedOutputAction, nargs='*', help='User-defined dictionary.')
        c.argument('script_cmdlet_id', help='A reference to the script cmdlet resource if user is running a AVS script.')

    with self.argument_context('vmware workload-network dhcp') as c:
        c.argument('dhcp_id', help='NSX DHCP identifier. Generally the same as the DHCP display name.')
        c.argument('display_name', help='Display name of the DHCP entity.')
        c.argument('revision', help='NSX revision number.')

    with self.argument_context('vmware workload-network dhcp server') as c:
        c.argument('server_address', help='DHCP Server Address.')
        c.argument('lease_time', help='DHCP Server Lease Time.')

    with self.argument_context('vmware workload-network dhcp relay') as c:
        c.argument('server_addresses', nargs='+', validator=server_addresses_length, help='DHCP Relay Addresses. Max 3.')

    with self.argument_context('vmware workload-network dns-service') as c:
        c.argument('dns_service_id', help="NSX DNS service identifier. Generally the same as the DNS service's display name.")
        c.argument('display_name', help='Display name of the DNS service.')
        c.argument('dns_service_ip', help='DNS service IP of the DNS service.')
        c.argument('default_dns_zone', help='Default DNS zone of the DNS service.')
        c.argument('fqdn_zones', nargs='+', help='FQDN zones of the DNS service.')
        c.argument('log_level', arg_type=get_enum_type(["DEBUG", "INFO", "WARNING", "ERROR", "FATAL"]), help='DNS service log level. Possible values include: "DEBUG", "INFO", "WARNING", "ERROR", "FATAL".')
        c.argument('revision', help='NSX revision number.')

    with self.argument_context('vmware workload-network dns-zone') as c:
        c.argument('dns_zone_id', help="NSX DNS zone identifier. Generally the same as the DNS zone's display name.")
        c.argument('display_name', help='Display name of the DNS zone.')
        c.argument('domain', nargs='+', help='Domain names of the DNS zone.')
        c.argument('dns_server_ips', nargs='+', help='DNS Server IP array of the DNS zone.')
        c.argument('source_ip', help='Source IP of the DNS zone.')
        c.argument('dns_services', help='Number of DNS services using the DNS zone.')
        c.argument('revision', help='NSX revision number.')

    with self.argument_context('vmware workload-network port-mirroring') as c:
        c.argument('port_mirroring_id', help="NSX Port Mirroring identifier. Generally the same as the Port Mirroring display name.")
        c.argument('display_name', help='Display name of the port mirroring profile.')
        c.argument('direction', help='Direction of port mirroring profile. Possible values include: "INGRESS, EGRESS, BIDIRECTIONAL".')
        c.argument('source', help='Source VM Group.')
        c.argument('destination', help='Destination VM Group.')
        c.argument('revision', help='NSX revision number.')
