# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest

from azure.cli.testsdk import (
    ResourceGroupPreparer, RoleBasedServicePrincipalPreparer, ScenarioTest, live_only)
from azure_devtools.scenario_tests import AllowLargeResponse


class AzureKubernetesServiceScenarioTest(ScenarioTest):
    @live_only()  # without live only fails with need az login
    @AllowLargeResponse()
    def test_get_version(self):
        versions_cmd = 'aks get-versions -l westus2'
        self.cmd(versions_cmd, checks=[
            self.check('type', 'Microsoft.ContainerService/locations/orchestrators'),
            self.check('orchestrators[0].orchestratorType', 'Kubernetes')
        ])

    @live_only()  # without live only fails with needs .ssh fails (maybe generate-ssh-keys would fix) and maybe az login.
    @AllowLargeResponse()
    @ResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_create_and_update_with_managed_aad(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} ' \
                     '--vm-set-type  AvailabilitySet -c 1 ' \
                     '--enable-aad --aad-admin-group-object-ids 00000000-0000-0000-0000-000000000001'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('aadProfile.managed', True),
            self.check('aadProfile.adminGroupObjectIds[0]', '00000000-0000-0000-0000-000000000001')
        ])

        update_cmd = 'aks update --resource-group={resource_group} --name={name} ' \
                     '--aad-admin-group-object-ids 00000000-0000-0000-0000-000000000002 ' \
                     '--aad-tenant-id 00000000-0000-0000-0000-000000000003'
        self.cmd(update_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('aadProfile.managed', True),
            self.check('aadProfile.adminGroupObjectIds[0]', '00000000-0000-0000-0000-000000000002'),
            self.check('aadProfile.tenantId', '00000000-0000-0000-0000-000000000003')
        ])
