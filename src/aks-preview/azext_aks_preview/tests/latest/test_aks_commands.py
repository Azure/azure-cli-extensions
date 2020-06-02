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
                     '--enable-aad --aad-admin-group-object-ids 00000000-0000-0000-0000-000000000001 -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('aadProfile.managed', True),
            self.check('aadProfile.adminGroupObjectIds[0]', '00000000-0000-0000-0000-000000000001')
        ])

        update_cmd = 'aks update --resource-group={resource_group} --name={name} ' \
                     '--aad-admin-group-object-ids 00000000-0000-0000-0000-000000000002 ' \
                     '--aad-tenant-id 00000000-0000-0000-0000-000000000003 -o json'
        self.cmd(update_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('aadProfile.managed', True),
            self.check('aadProfile.adminGroupObjectIds[0]', '00000000-0000-0000-0000-000000000002'),
            self.check('aadProfile.tenantId', '00000000-0000-0000-0000-000000000003')
        ])

    @AllowLargeResponse()
    @ResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_create_with_ingress_appgw_addon(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --enable-managed-identity --service-principal xxxx --client-secret yyyy --generate-ssh-keys ' \
                     '-a ingress-appgw --appgw-subnet-prefix 10.2.0.0/16 -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.IngressApplicationGateway.enabled', True),
            self.check('addonProfiles.IngressApplicationGateway.config.subnetPrefix', "10.2.0.0/16")
        ])

    @AllowLargeResponse()
    @ResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_byo_subnet_with_ingress_appgw_addon(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        vnet_name = self.create_random_name('cliakstest', 16)
        appgw_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'aks_name': aks_name,
            'vnet_name': vnet_name,
            'appgw_name': appgw_name
        })

        # create virtual network
        create_vnet = 'network vnet create --resource-group={resource_group} --name={vnet_name} ' \
                      '--address-prefix 11.0.0.0/16 --subnet-name aks-subnet --subnet-prefix 11.0.0.0/24  -o json'
        vnet = self.cmd(create_vnet, checks=[
            self.check('newVNet.provisioningState', 'Succeeded')
        ]).get_output_in_json()

        create_subnet = 'network vnet subnet create -n appgw-subnet --resource-group={resource_group} --vnet-name {vnet_name} ' \
                        '--address-prefixes 11.0.1.0/24  -o json'
        self.cmd(create_subnet, checks=[
            self.check('provisioningState', 'Succeeded')
        ])

        vnet_id = vnet['newVNet']["id"]
        assert vnet_id is not None
        self.kwargs.update({
            'vnet_id': vnet_id,
        })

        # create aks cluster
        create_cmd = 'aks create --resource-group={resource_group} --name={aks_name} --enable-managed-identity --generate-ssh-keys ' \
                     '--vnet-subnet-id {vnet_id}/subnets/aks-subnet ' \
                     '-a ingress-appgw --appgw-name gateway --appgw-subnet-id {vnet_id}/subnets/appgw-subnet  -o json'
        aks_cluster = self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.IngressApplicationGateway.enabled', True),
            self.check('addonProfiles.IngressApplicationGateway.config.applicationGatewayName', "gateway"),
            self.check('addonProfiles.IngressApplicationGateway.config.subnetId', vnet_id + '/subnets/appgw-subnet')
        ]).get_output_in_json()

        addon_client_id = aks_cluster["addonProfiles"]["IngressApplicationGateway"]["identity"]["clientId"]

        self.kwargs.update({
            'addon_client_id': addon_client_id,
        })

        check_role_assignment = 'role assignment list --assignee {addon_client_id} --scope {vnet_id}/subnets/appgw-subnet --role "4d97b98b-1d4f-4787-a291-c67834d212e7" -o json'
        self.cmd(check_role_assignment, checks=[
            self.check('[0].roleDefinitionName', 'Network Contributor')
        ])

    @AllowLargeResponse()
    @ResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_byo_appgw_with_ingress_appgw_addon(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        vnet_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'aks_name': aks_name,
            'vnet_name': vnet_name
        })

        # create virtual network
        create_vnet = 'network vnet create --resource-group={resource_group} --name={vnet_name} ' \
                      '--address-prefix 11.0.0.0/16 --subnet-name aks-subnet --subnet-prefix 11.0.0.0/24  -o json'
        vnet = self.cmd(create_vnet, checks=[
            self.check('newVNet.provisioningState', 'Succeeded')
        ]).get_output_in_json()

        create_subnet = 'network vnet subnet create -n appgw-subnet --resource-group={resource_group} --vnet-name {vnet_name} ' \
                        '--address-prefixes 11.0.1.0/24  -o json'
        self.cmd(create_subnet, checks=[
            self.check('provisioningState', 'Succeeded')
        ])

        vnet_id = vnet['newVNet']["id"]
        assert vnet_id is not None
        self.kwargs.update({
            'vnet_id': vnet_id,
        })

        # create public ip for app gateway
        create_pip = 'network public-ip create -n appgw-ip -g {resource_group} ' \
                     '--allocation-method Static --sku Standard  -o json'
        self.cmd(create_pip, checks=[
            self.check('publicIp.provisioningState', 'Succeeded')
        ])

        # create app gateway
        create_appgw = 'network application-gateway create -n appgw -g {resource_group} ' \
                       '--sku Standard_v2 --public-ip-address appgw-ip --subnet {vnet_id}/subnets/appgw-subnet'
        self.cmd(create_appgw)

        # construct group id
        from msrestazure.tools import parse_resource_id, resource_id
        parsed_vnet_id = parse_resource_id(vnet_id)
        group_id = resource_id(subscription=parsed_vnet_id["subscription"],
                               resource_group=parsed_vnet_id["resource_group"])
        appgw_id = group_id + "/providers/Microsoft.Network/applicationGateways/appgw"

        self.kwargs.update({
            'appgw_id': appgw_id,
            'appgw_group_id': group_id
        })

        # create aks cluster
        create_cmd = 'aks create -n {aks_name} -g {resource_group} --enable-managed-identity --service-principal xxxx --client-secret yyyy --generate-ssh-keys ' \
                     '--vnet-subnet-id {vnet_id}/subnets/aks-subnet ' \
                     '-a ingress-appgw --appgw-id {appgw_id} -o json'
        aks_cluster = self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.IngressApplicationGateway.enabled', True),
            self.check('addonProfiles.IngressApplicationGateway.config.applicationGatewayId', appgw_id)
        ]).get_output_in_json()

        addon_client_id = aks_cluster["addonProfiles"]["IngressApplicationGateway"]["identity"]["clientId"]

        self.kwargs.update({
            'addon_client_id': addon_client_id,
        })

        # check role assignment
        check_role_assignment = 'role assignment list --assignee {addon_client_id} --scope {appgw_group_id} --role "b24988ac-6180-42a0-ab88-20f7382dd24c" -o json'
        self.cmd(check_role_assignment, checks=[
            self.check('[0].roleDefinitionName', 'Contributor')
        ])
