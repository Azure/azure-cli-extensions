# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long,too-many-statements


def load_command_table(self, _):

    with self.command_group('vmware private-cloud') as g:
        from .operations.private_cloud import PrivateCloudCreate, PrivateCloudUpdate
        self.command_table['vmware private-cloud create'] = PrivateCloudCreate(loader=self)
        self.command_table['vmware private-cloud update'] = PrivateCloudUpdate(loader=self)

        g.custom_command('listadmincredentials', 'privatecloud_listadmincredentials', deprecate_info=g.deprecate(redirect='az vmware private-cloud list-admin-credentials', hide=True))
        g.custom_command('addidentitysource', 'privatecloud_addidentitysource', deprecate_info=g.deprecate(redirect='az vmware private-cloud identity-source create', hide=True))
        g.custom_command('add-identity-source', 'privatecloud_addidentitysource', deprecate_info=g.deprecate(redirect='az vmware private-cloud identity-source create', hide=True))
        g.custom_command('deleteidentitysource', 'privatecloud_deleteidentitysource', deprecate_info=g.deprecate(redirect='az vmware private-cloud identity-source delete', hide=True))
        g.custom_command('delete-identity-source', 'privatecloud_deleteidentitysource', deprecate_info=g.deprecate(redirect='az vmware private-cloud identity-source delete', hide=True))
        g.custom_command('add-cmk-encryption', 'privatecloud_addcmkencryption', deprecate_info=g.deprecate(redirect='az vmware private-cloud enable-cmk-encryption', hide=True))
        g.custom_command('delete-cmk-encryption', 'privatecloud_deletecmkenryption', deprecate_info=g.deprecate(redirect='az vmware private-cloud disable-cmk-encryption', hide=True))
        g.custom_command('enable-cmk-encryption', 'privatecloud_addcmkencryption')
        g.custom_command('disable-cmk-encryption', 'privatecloud_deletecmkenryption')
        g.custom_command('rotate-nsxt-password', 'privatecloud_rotate_nsxt_password')

    with self.command_group('vmware private-cloud identity') as g:
        g.custom_command('assign', 'privatecloud_identity_assign')
        g.custom_command('remove', 'privatecloud_identity_remove')
        g.custom_show_command('show', 'privatecloud_identity_get')

    with self.command_group('vmware location') as g:
        g.custom_command('checkquotaavailability', 'check_quota_availability', deprecate_info=g.deprecate(redirect='az vmware location check-quota-availability', hide=True))
        g.custom_command('checktrialavailability', 'check_trial_availability', deprecate_info=g.deprecate(redirect='az vmware location check-trial-availability', hide=True))

    with self.command_group('vmware datastore') as g:
        g.custom_command('create', 'datastore_create', deprecate_info=g.deprecate(redirect='"az vmware datastore netapp-volume create" or "az vmware datastore disk-pool-volume create"', hide=True))

    with self.command_group('vmware script-execution') as g:
        g.custom_command('create', 'script_execution_create')

    with self.command_group('vmware datastore netapp-volume'):
        from .operations.datastore import DatastoreNetappVolumeCreate
        self.command_table['vmware datastore netapp-volume create'] = DatastoreNetappVolumeCreate(loader=self)

    with self.command_group('vmware datastore disk-pool-volume'):
        from .operations.datastore import DatastoreDiskPoolVolumeCreate
        self.command_table['vmware datastore disk-pool-volume create'] = DatastoreDiskPoolVolumeCreate(loader=self)

    with self.command_group('vmware addon vr'):
        from .operations.addon import AddonVrCreate, AddonVrUpdate, AddonVrShow, AddonVrDelete
        self.command_table['vmware addon vr create'] = AddonVrCreate(loader=self)
        self.command_table['vmware addon vr update'] = AddonVrUpdate(loader=self)
        self.command_table['vmware addon vr show'] = AddonVrShow(loader=self)
        self.command_table['vmware addon vr delete'] = AddonVrDelete(loader=self)

    with self.command_group('vmware addon hcx'):
        from .operations.addon import AddonHcxCreate, AddonHcxUpdate, AddonHcxShow, AddonHcxDelete
        self.command_table['vmware addon hcx create'] = AddonHcxCreate(loader=self)
        self.command_table['vmware addon hcx update'] = AddonHcxUpdate(loader=self)
        self.command_table['vmware addon hcx show'] = AddonHcxShow(loader=self)
        self.command_table['vmware addon hcx delete'] = AddonHcxDelete(loader=self)

    with self.command_group('vmware addon srm'):
        from .operations.addon import AddonSrmCreate, AddonSrmUpdate, AddonSrmShow, AddonSrmDelete
        self.command_table['vmware addon srm create'] = AddonSrmCreate(loader=self)
        self.command_table['vmware addon srm update'] = AddonSrmUpdate(loader=self)
        self.command_table['vmware addon srm show'] = AddonSrmShow(loader=self)
        self.command_table['vmware addon srm delete'] = AddonSrmDelete(loader=self)

    with self.command_group('vmware addon arc'):
        from .operations.addon import AddonArcCreate, AddonArcUpdate, AddonArcShow, AddonArcDelete
        self.command_table['vmware addon arc create'] = AddonArcCreate(loader=self)
        self.command_table['vmware addon arc update'] = AddonArcUpdate(loader=self)
        self.command_table['vmware addon arc show'] = AddonArcShow(loader=self)
        self.command_table['vmware addon arc delete'] = AddonArcDelete(loader=self)

    with self.command_group('vmware workload-network dhcp relay'):
        from .operations.workload_network import DHCPRelayCreate, DHCPRelayUpdate, DHCPRelayDelete
        self.command_table['vmware workload-network dhcp relay create'] = DHCPRelayCreate(loader=self)
        self.command_table['vmware workload-network dhcp relay update'] = DHCPRelayUpdate(loader=self)
        self.command_table['vmware workload-network dhcp relay delete'] = DHCPRelayDelete(loader=self)

    with self.command_group('vmware workload-network dhcp server'):
        from .operations.workload_network import DHCPServerCreate, DHCPServerUpdate, DHCPServerDelete
        self.command_table['vmware workload-network dhcp server create'] = DHCPServerCreate(loader=self)
        self.command_table['vmware workload-network dhcp server update'] = DHCPServerUpdate(loader=self)
        self.command_table['vmware workload-network dhcp server delete'] = DHCPServerDelete(loader=self)

    with self.command_group('vmware placement-policy vm'):
        from .operations.placement_policy import PlacementPolicyVMCreate, PlacementPolicyVMUpdate, PlacementPolicyVMDelete
        self.command_table['vmware placement-policy vm create'] = PlacementPolicyVMCreate(loader=self)
        self.command_table['vmware placement-policy vm update'] = PlacementPolicyVMUpdate(loader=self)
        self.command_table['vmware placement-policy vm delete'] = PlacementPolicyVMDelete(loader=self)

    with self.command_group('vmware placement-policy vm-host'):
        from .operations.placement_policy import PlacementPolicyVMHostCreate, PlacementPolicyVMHostUpdate, \
            PlacementPolicyVMHostDelete
        self.command_table['vmware placement-policy vm-host create'] = PlacementPolicyVMHostCreate(loader=self)
        self.command_table['vmware placement-policy vm-host update'] = PlacementPolicyVMHostUpdate(loader=self)
        self.command_table['vmware placement-policy vm-host delete'] = PlacementPolicyVMHostDelete(loader=self)
