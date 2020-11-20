# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

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
