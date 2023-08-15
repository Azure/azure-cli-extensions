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

    from .operations.private_cloud import PrivateCloudCreate, PrivateCloudUpdate
    self.command_table['vmware private-cloud create'] = PrivateCloudCreate(loader=self)
    self.command_table['vmware private-cloud update'] = PrivateCloudUpdate(loader=self)

    from .operations.datastore import DatastoreNetappVolumeCreate, DatastoreDiskPoolVolumeCreate
    self.command_table['vmware datastore netapp-volume create'] = DatastoreNetappVolumeCreate(loader=self)
    self.command_table['vmware datastore disk-pool-volume create'] = DatastoreDiskPoolVolumeCreate(loader=self)

    from .operations.addon import AddonVrCreate, AddonVrUpdate, AddonVrShow, AddonVrDelete
    self.command_table['vmware addon vr create'] = AddonVrCreate(loader=self)
    self.command_table['vmware addon vr update'] = AddonVrUpdate(loader=self)
    self.command_table['vmware addon vr show'] = AddonVrShow(loader=self)
    self.command_table['vmware addon vr delete'] = AddonVrDelete(loader=self)

    from .operations.addon import AddonHcxCreate, AddonHcxUpdate, AddonHcxShow, AddonHcxDelete
    self.command_table['vmware addon hcx create'] = AddonHcxCreate(loader=self)
    self.command_table['vmware addon hcx update'] = AddonHcxUpdate(loader=self)
    self.command_table['vmware addon hcx show'] = AddonHcxShow(loader=self)
    self.command_table['vmware addon hcx delete'] = AddonHcxDelete(loader=self)

    from .operations.addon import AddonSrmCreate, AddonSrmUpdate, AddonSrmShow, AddonSrmDelete
    self.command_table['vmware addon srm create'] = AddonSrmCreate(loader=self)
    self.command_table['vmware addon srm update'] = AddonSrmUpdate(loader=self)
    self.command_table['vmware addon srm show'] = AddonSrmShow(loader=self)
    self.command_table['vmware addon srm delete'] = AddonSrmDelete(loader=self)

    from .operations.addon import AddonArcCreate, AddonArcUpdate, AddonArcShow, AddonArcDelete
    self.command_table['vmware addon arc create'] = AddonArcCreate(loader=self)
    self.command_table['vmware addon arc update'] = AddonArcUpdate(loader=self)
    self.command_table['vmware addon arc show'] = AddonArcShow(loader=self)
    self.command_table['vmware addon arc delete'] = AddonArcDelete(loader=self)

    from .operations.workload_network import DHCPRelayCreate, DHCPRelayUpdate, DHCPRelayDelete
    self.command_table['vmware workload-network dhcp relay create'] = DHCPRelayCreate(loader=self)
    self.command_table['vmware workload-network dhcp relay update'] = DHCPRelayUpdate(loader=self)
    self.command_table['vmware workload-network dhcp relay delete'] = DHCPRelayDelete(loader=self)

    from .operations.workload_network import DHCPServerCreate, DHCPServerUpdate, DHCPServerDelete
    self.command_table['vmware workload-network dhcp server create'] = DHCPServerCreate(loader=self)
    self.command_table['vmware workload-network dhcp server update'] = DHCPServerUpdate(loader=self)
    self.command_table['vmware workload-network dhcp server delete'] = DHCPServerDelete(loader=self)

    with self.command_group('vmware private-cloud', vmware_sdk, client_factory=cf_vmware) as g:
        g.custom_command('listadmincredentials', 'privatecloud_listadmincredentials', deprecate_info=g.deprecate(redirect='az vmware private-cloud list-admin-credentials', hide=True))
        g.custom_command('addidentitysource', 'privatecloud_addidentitysource', deprecate_info=g.deprecate(redirect='az vmware private-cloud add-identity-source', hide=True))
        g.custom_command('add-identity-source', 'privatecloud_addidentitysource')
        g.custom_command('deleteidentitysource', 'privatecloud_deleteidentitysource', deprecate_info=g.deprecate(redirect='az vmware private-cloud delete-identity-source', hide=True))
        g.custom_command('delete-identity-source', 'privatecloud_deleteidentitysource')
        g.custom_command('add-cmk-encryption', 'privatecloud_addcmkencryption', deprecate_info=g.deprecate(redirect='az vmware private-cloud enable-cmk-encryption', hide=True))
        g.custom_command('delete-cmk-encryption', 'privatecloud_deletecmkenryption', deprecate_info=g.deprecate(redirect='az vmware private-cloud disable-cmk-encryption', hide=True))
        g.custom_command('enable-cmk-encryption', 'privatecloud_addcmkencryption')
        g.custom_command('disable-cmk-encryption', 'privatecloud_deletecmkenryption')
        g.custom_command('rotate-nsxt-password', 'privatecloud_rotate_nsxt_password')

    with self.command_group('vmware private-cloud identity', vmware_sdk, client_factory=cf_vmware) as g:
        g.custom_command('assign', 'privatecloud_identity_assign')
        g.custom_command('remove', 'privatecloud_identity_remove')
        g.custom_show_command('show', 'privatecloud_identity_get')

    with self.command_group('vmware location', vmware_sdk, client_factory=cf_vmware) as g:
        g.custom_command('checkquotaavailability', 'check_quota_availability', deprecate_info=g.deprecate(redirect='az vmware location check-quota-availability', hide=True))
        g.custom_command('checktrialavailability', 'check_trial_availability', deprecate_info=g.deprecate(redirect='az vmware location check-trial-availability', hide=True))

    with self.command_group('vmware datastore', vmware_sdk, client_factory=cf_vmware) as g:
        g.custom_command('create', 'datastore_create', deprecate_info=g.deprecate(redirect='"az vmware datastore netapp-volume create" or "az vmware datastore disk-pool-volume create"', hide=True))

    # TODO:
    with self.command_group('vmware script-execution', vmware_sdk, client_factory=cf_vmware) as g:
        g.custom_command('create', 'script_execution_create')
        g.custom_command('list', 'script_execution_list')
        g.custom_command('delete', 'script_execution_delete')
        g.custom_show_command('show', 'script_execution_show')

    with self.command_group('vmware workload-network port-mirroring', vmware_sdk, client_factory=cf_vmware) as g:
        g.custom_command('list', 'workload_network_port_mirroring_list')
        g.custom_show_command('show', 'workload_network_port_mirroring_get')
        g.custom_command('create', 'workload_network_port_mirroring_create')
        g.custom_command('update', 'workload_network_port_mirroring_update')
        g.custom_command('delete', 'workload_network_port_mirroring_delete')

    with self.command_group('vmware workload-network segment', vmware_sdk, client_factory=cf_vmware) as g:
        g.custom_command('list', 'workload_network_segment_list')
        g.custom_show_command('show', 'workload_network_segment_get')
        g.custom_command('create', 'workload_network_segment_create')
        g.custom_command('update', 'workload_network_segment_update')
        g.custom_command('delete', 'workload_network_segment_delete')

    with self.command_group('vmware workload-network public-ip', vmware_sdk, client_factory=cf_vmware) as g:
        g.custom_command('list', 'workload_network_public_ip_list')
        g.custom_show_command('show', 'workload_network_public_ip_get')
        g.custom_command('create', 'workload_network_public_ip_create')
        g.custom_command('delete', 'workload_network_public_ip_delete')

    with self.command_group('vmware workload-network vm-group', vmware_sdk, client_factory=cf_vmware) as g:
        g.custom_command('list', 'workload_network_vm_group_list')
        g.custom_show_command('show', 'workload_network_vm_group_get')
        g.custom_command('create', 'workload_network_vm_group_create')
        g.custom_command('update', 'workload_network_vm_group_update')
        g.custom_command('delete', 'workload_network_vm_group_delete')

    with self.command_group('vmware workload-network vm', vmware_sdk, client_factory=cf_vmware) as g:
        g.custom_command('list', 'workload_network_vm_list')
        g.custom_show_command('show', 'workload_network_vm_get')

    with self.command_group('vmware workload-network gateway', vmware_sdk, client_factory=cf_vmware) as g:
        g.custom_command('list', 'workload_network_gateway_list')
        g.custom_show_command('show', 'workload_network_gateway_get')

    with self.command_group('vmware placement-policy', vmware_sdk, client_factory=cf_vmware) as g:
        g.custom_command('list', 'placement_policy_list')
        g.custom_show_command('show', 'placement_policy_get')

    with self.command_group('vmware placement-policy vm', vmware_sdk, client_factory=cf_vmware) as g:
        g.custom_command('create', 'placement_policy_vm_create')
        g.custom_command('update', 'placement_policy_update')
        g.custom_command('delete', 'placement_policy_delete')

    with self.command_group('vmware placement-policy vm-host', vmware_sdk, client_factory=cf_vmware) as g:
        g.custom_command('create', 'placement_policy_vm_host_create')
        g.custom_command('update', 'placement_policy_update')
        g.custom_command('delete', 'placement_policy_delete')

    with self.command_group('vmware vm', vmware_sdk, client_factory=cf_vmware) as g:
        g.custom_command('list', 'virtual_machine_list')
        g.custom_show_command('show', 'virtual_machine_get')
        g.custom_command('restrict-movement', 'virtual_machine_restrict')
