# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, import-outside-toplevel


def load_command_table(self, _):
    from azext_cloudservice.operations.cloud_service import CloudServiceList, CloudServiceListAll
    from azext_cloudservice.operations.role_instance import RoleInstanceShowRemoteDesktopFile
    from azext_cloudservice.operations.update_domain import UpdateDomainWalkUpdateDomain

    self.command_table['cloud-service list'] = CloudServiceList(loader=self)
    self.command_table['cloud-service list-all'] = CloudServiceListAll(loader=self)
    self.command_table['cloud-service role-instance show-remote-desktop-file'] = \
        RoleInstanceShowRemoteDesktopFile(loader=self)
    self.command_table['cloud-service update-domain walk-update-domain'] = UpdateDomainWalkUpdateDomain(loader=self)

    with self.command_group('cloud-service', is_experimental=True) as g:
        g.custom_command('create', 'cloud_service_create', supports_no_wait=True)
