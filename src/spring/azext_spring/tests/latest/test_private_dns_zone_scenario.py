# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os

from azure.cli.testsdk import (ScenarioTest)
from azure.cli.testsdk.reverse_dependency import (
    get_dummy_cli,
)

from .custom_dev_setting_constant import SpringTestEnvironmentEnum
from .custom_preparers import (SpringPreparer, SpringResourceGroupPreparer, SpringSubResourceWrapper)


class PrivateDnsZoneTests(ScenarioTest):

    @SpringResourceGroupPreparer(
        dev_setting_name=SpringTestEnvironmentEnum.STANDARD_VNet['resource_group_name'])
    @SpringPreparer(**SpringTestEnvironmentEnum.STANDARD_VNet['spring'])
    def test_private_dns_zone(self, resource_group, spring):

        self.kwargs.update({
            'serviceName': spring,
            'rg': resource_group,
            'zoneid': '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/cli/providers/Microsoft.Network/privateDnsZones/private.azuremicroservices.io'
        })

        self.cmd('spring private-dns-zone add -g {rg} -s {serviceName} --zone-id {zoneid}',
                 checks=[
                     self.check('properties.provisioningState', 'Succeeded'),
                 ])

        self.cmd('spring private-dns-zone clean -g {rg} -s {serviceName}',
            checks=[
                self.check('properties.provisioningState', 'Succeeded'),
                self.check('properties.vnet_addons.private_dns_zone_id', None),
            ])