# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long,too-many-statements

from azure.cli.core.commands import CliCommandType
from azext_vmware._client_factory import cf_vmware


def load_command_table(self, _):

    vmware_sdk = CliCommandType(
        operations_tmpl='azext_vmware.vendored_sdks.operations#PrivateCloudOperations.{}',
        client_factory=cf_vmware)

    with self.command_group('vmware private-cloud', vmware_sdk, client_factory=cf_vmware) as g:
        g.custom_command('list', 'privatecloud_list')
        g.custom_show_command('show', 'privatecloud_show')
        g.custom_command('create', 'privatecloud_create')
        g.custom_command('update', 'privatecloud_update')
        g.custom_command('delete', 'privatecloud_delete')
        g.custom_command('listadmincredentials', 'privatecloud_listadmincredentials')
        g.custom_command('addidentitysource', 'privatecloud_addidentitysource')
        g.custom_command('deleteidentitysource', 'privatecloud_deleteidentitysource')
        g.custom_command('rotate-vcenter-password', 'privatecloud_rotate_vcenter_password')
        g.custom_command('rotate-nsxt-password', 'privatecloud_rotate_nsxt_password')

    with self.command_group('vmware cluster', vmware_sdk, client_factory=cf_vmware) as g:
        g.custom_command('create', 'cluster_create')
        g.custom_command('update', 'cluster_update')
        g.custom_command('list', 'cluster_list')
        g.custom_command('delete', 'cluster_delete')
        g.custom_show_command('show', 'cluster_show')

    with self.command_group('vmware authorization', vmware_sdk, client_factory=cf_vmware) as g:
        g.custom_command('create', 'authorization_create')
        g.custom_command('list', 'authorization_list')
        g.custom_command('delete', 'authorization_delete')
        g.custom_show_command('show', 'authorization_show')

    with self.command_group('vmware hcx-enterprise-site', vmware_sdk, client_factory=cf_vmware) as g:
        g.custom_command('create', 'hcxenterprisesite_create')
        g.custom_command('list', 'hcxenterprisesite_list')
        g.custom_command('delete', 'hcxenterprisesite_delete')
        g.custom_show_command('show', 'hcxenterprisesite_show')

    with self.command_group('vmware location', vmware_sdk, client_factory=cf_vmware) as g:
        g.custom_command('checkquotaavailability', 'check_quota_availability')
        g.custom_command('checktrialavailability', 'check_trial_availability')

    with self.command_group('vmware datastore', vmware_sdk, client_factory=cf_vmware) as g:
        g.custom_command('create', 'datastore_create', deprecate_info=g.deprecate(redirect='"az vmware datastore netapp-volume create" or "az vmware datastore disk-pool-volume create"', hide=True))
        g.custom_command('list', 'datastore_list')
        g.custom_show_command('show', 'datastore_show')
        g.custom_command('delete', 'datastore_delete')

    with self.command_group('vmware datastore netapp-volume', vmware_sdk, client_factory=cf_vmware) as g:
        g.custom_command('create', 'datastore_netappvolume_create')

    with self.command_group('vmware datastore disk-pool-volume', vmware_sdk, client_factory=cf_vmware) as g:
        g.custom_command('create', 'datastore_diskpoolvolume_create')

    with self.command_group('vmware addon', vmware_sdk, client_factory=cf_vmware) as g:
        g.custom_command('list', 'addon_list')

    with self.command_group('vmware addon vr', vmware_sdk, client_factory=cf_vmware) as g:
        g.custom_command('create', 'addon_vr_create')
        g.custom_show_command('show', 'addon_vr_show')
        g.custom_command('update', 'addon_vr_update')
        g.custom_command('delete', 'addon_vr_delete')

    with self.command_group('vmware addon hcx', vmware_sdk, client_factory=cf_vmware) as g:
        g.custom_command('create', 'addon_hcx_create')
        g.custom_show_command('show', 'addon_hcx_show')
        g.custom_command('update', 'addon_hcx_update')
        g.custom_command('delete', 'addon_hcx_delete')

    with self.command_group('vmware addon srm', vmware_sdk, client_factory=cf_vmware) as g:
        g.custom_command('create', 'addon_srm_create')
        g.custom_show_command('show', 'addon_srm_show')
        g.custom_command('update', 'addon_srm_update')
        g.custom_command('delete', 'addon_srm_delete')

    with self.command_group('vmware global-reach-connection', vmware_sdk, client_factory=cf_vmware) as g:
        g.custom_command('create', 'globalreachconnection_create')
        g.custom_command('list', 'globalreachconnection_list')
        g.custom_command('delete', 'globalreachconnection_delete')
        g.custom_show_command('show', 'globalreachconnection_show')

    with self.command_group('vmware cloud-link', vmware_sdk, client_factory=cf_vmware) as g:
        g.custom_command('create', 'cloud_link_create')
        g.custom_command('list', 'cloud_link_list')
        g.custom_command('delete', 'cloud_link_delete')
        g.custom_show_command('show', 'cloud_link_show')

    with self.command_group('vmware script-cmdlet', vmware_sdk, client_factory=cf_vmware) as g:
        g.custom_command('list', 'script_cmdlet_list')
        g.custom_show_command('show', 'script_cmdlet_show')

    with self.command_group('vmware script-package', vmware_sdk, client_factory=cf_vmware) as g:
        g.custom_command('list', 'script_package_list')
        g.custom_show_command('show', 'script_package_show')

    with self.command_group('vmware script-execution', vmware_sdk, client_factory=cf_vmware) as g:
        g.custom_command('create', 'script_execution_create')
        g.custom_command('list', 'script_execution_list')
        g.custom_command('delete', 'script_execution_delete')
        g.custom_show_command('show', 'script_execution_show')

    with self.command_group('vmware workload-network dhcp', vmware_sdk, client_factory=cf_vmware) as g:
        g.custom_command('list', 'workload_network_dhcp_list')
        g.custom_show_command('show', 'workload_network_dhcp_show')

    with self.command_group('vmware workload-network dhcp server', vmware_sdk, client_factory=cf_vmware) as g:
        g.custom_command('create', 'workload_network_dhcp_server_create')
        g.custom_command('delete', 'workload_network_dhcp_delete')
        g.custom_command('update', 'workload_network_dhcp_server_update')

    with self.command_group('vmware workload-network dhcp relay', vmware_sdk, client_factory=cf_vmware) as g:
        g.custom_command('create', 'workload_network_dhcp_relay_create')
        g.custom_command('delete', 'workload_network_dhcp_delete')
        g.custom_command('update', 'workload_network_dhcp_relay_update')

    with self.command_group('vmware workload-network dns-service', vmware_sdk, client_factory=cf_vmware) as g:
        g.custom_command('list', 'workload_network_dns_services_list')
        g.custom_show_command('show', 'workload_network_dns_services_get')
        g.custom_command('create', 'workload_network_dns_services_create')
        g.custom_command('update', 'workload_network_dns_services_update')
        g.custom_command('delete', 'workload_network_dns_services_delete')

    with self.command_group('vmware workload-network dns-zone', vmware_sdk, client_factory=cf_vmware) as g:
        g.custom_command('list', 'workload_network_dns_zone_list')
        g.custom_show_command('show', 'workload_network_dns_zone_get')
        g.custom_command('create', 'workload_network_dns_zone_create')
        g.custom_command('update', 'workload_network_dns_zone_update')
        g.custom_command('delete', 'workload_network_dns_zone_delete')

    with self.command_group('vmware workload-network port-mirroring', vmware_sdk, client_factory=cf_vmware) as g:
        g.custom_command('list', 'workload_network_port_mirroring_list')
        g.custom_show_command('show', 'workload_network_port_mirroring_get')
        g.custom_command('create', 'workload_network_port_mirroring_create')
        g.custom_command('update', 'workload_network_port_mirroring_update')
        g.custom_command('delete', 'workload_network_port_mirroring_delete')
