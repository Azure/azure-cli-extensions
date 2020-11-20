# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
import os

from azure.cli.testsdk import (
    ResourceGroupPreparer, RoleBasedServicePrincipalPreparer, ScenarioTest, live_only)
from azure_devtools.scenario_tests import AllowLargeResponse


def _get_test_data_file(filename):
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(curr_dir, 'data', filename)


class AzureKubernetesServiceScenarioTest(ScenarioTest):
    @live_only()  # without live only fails with need az login
    @AllowLargeResponse()
    def test_get_version(self):
        versions_cmd = 'aks get-versions -l westus2'
        self.cmd(versions_cmd, checks=[
            self.check(
                'type', 'Microsoft.ContainerService/locations/orchestrators'),
            self.check('orchestrators[0].orchestratorType', 'Kubernetes')
        ])

    # without live only fails with needs .ssh fails (maybe generate-ssh-keys would fix) and maybe az login.
    @live_only()
    @AllowLargeResponse()
    @ResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_create_and_update_with_managed_aad(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} ' \
                     '--vm-set-type VirtualMachineScaleSets -c 1 ' \
                     '--enable-aad --aad-admin-group-object-ids 00000000-0000-0000-0000-000000000001 -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('aadProfile.managed', True),
            self.check(
                'aadProfile.adminGroupObjectIds[0]', '00000000-0000-0000-0000-000000000001')
        ])

        update_cmd = 'aks update --resource-group={resource_group} --name={name} ' \
                     '--aad-admin-group-object-ids 00000000-0000-0000-0000-000000000002 ' \
                     '--aad-tenant-id 00000000-0000-0000-0000-000000000003 -o json'
        self.cmd(update_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('aadProfile.managed', True),
            self.check(
                'aadProfile.adminGroupObjectIds[0]', '00000000-0000-0000-0000-000000000002'),
            self.check('aadProfile.tenantId',
                       '00000000-0000-0000-0000-000000000003')
        ])

    # without live only fails with needs .ssh fails (maybe generate-ssh-keys would fix) and maybe az login.
    @live_only()
    @AllowLargeResponse()
    @ResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='canadacentral')
    def test_aks_create_aadv1_and_update_with_managed_aad(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} ' \
                     '--vm-set-type VirtualMachineScaleSets -c 1 ' \
                     '--aad-server-app-id 00000000-0000-0000-0000-000000000001 ' \
                     '--aad-server-app-secret fake-secret ' \
                     '--aad-client-app-id 00000000-0000-0000-0000-000000000002 ' \
                     '--aad-tenant-id d5b55040-0c14-48cc-a028-91457fc190d9 ' \
                     '-o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('aadProfile.managed', None),
            self.check('aadProfile.serverAppId',
                       '00000000-0000-0000-0000-000000000001'),
            self.check('aadProfile.clientAppId',
                       '00000000-0000-0000-0000-000000000002'),
            self.check('aadProfile.tenantId',
                       'd5b55040-0c14-48cc-a028-91457fc190d9')
        ])

        update_cmd = 'aks update --resource-group={resource_group} --name={name} ' \
                     '--enable-aad ' \
                     '--aad-admin-group-object-ids 00000000-0000-0000-0000-000000000003 ' \
                     '--aad-tenant-id 00000000-0000-0000-0000-000000000004 -o json'
        self.cmd(update_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('aadProfile.managed', True),
            self.check(
                'aadProfile.adminGroupObjectIds[0]', '00000000-0000-0000-0000-000000000003'),
            self.check('aadProfile.tenantId',
                       '00000000-0000-0000-0000-000000000004')
        ])

    # without live only fails with needs .ssh fails (maybe generate-ssh-keys would fix) and maybe az login.
    @live_only()
    @AllowLargeResponse()
    @ResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='canadacentral')
    def test_aks_create_nonaad_and_update_with_managed_aad(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} ' \
                     '--vm-set-type VirtualMachineScaleSets --node-count=1 ' \
                     '-o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('aadProfile', None)
        ])

        update_cmd = 'aks update --resource-group={resource_group} --name={name} ' \
                     '--enable-aad ' \
                     '--aad-admin-group-object-ids 00000000-0000-0000-0000-000000000001 ' \
                     '--aad-tenant-id 00000000-0000-0000-0000-000000000002 -o json'
        self.cmd(update_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('aadProfile.managed', True),
            self.check(
                'aadProfile.adminGroupObjectIds[0]', '00000000-0000-0000-0000-000000000001'),
            self.check('aadProfile.tenantId',
                       '00000000-0000-0000-0000-000000000002')
        ])

    # without live only fails with needs .ssh fails (maybe generate-ssh-keys would fix) and maybe az login.
    @live_only()
    @AllowLargeResponse()
    @ResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_create_and_update_with_managed_aad_enable_azure_rbac(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} ' \
                     '--vm-set-type VirtualMachineScaleSets  AvailabilitySet -c 1 ' \
                     '--enable-aad --enable-azure-rbac --aad-admin-group-object-ids 00000000-0000-0000-0000-000000000001 -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('aadProfile.managed', True),
            self.check('aadProfile.enableAzureRBAC', True),
            self.check(
                'aadProfile.adminGroupObjectIds[0]', '00000000-0000-0000-0000-000000000001')
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
            self.check('addonProfiles.ingressApplicationGateway.enabled', True),
            self.check(
                'addonProfiles.ingressApplicationGateway.config.subnetPrefix', "10.2.0.0/16")
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
            self.check('addonProfiles.ingressApplicationGateway.enabled', True),
            self.check(
                'addonProfiles.ingressApplicationGateway.config.applicationGatewayName', "gateway"),
            self.check('addonProfiles.ingressApplicationGateway.config.subnetId',
                       vnet_id + '/subnets/appgw-subnet')
        ]).get_output_in_json()

        addon_client_id = aks_cluster["addonProfiles"]["ingressApplicationGateway"]["identity"]["clientId"]

        self.kwargs.update({
            'addon_client_id': addon_client_id,
        })

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
        create_cmd = 'aks create -n {aks_name} -g {resource_group} --enable-managed-identity --generate-ssh-keys ' \
                     '--vnet-subnet-id {vnet_id}/subnets/aks-subnet ' \
                     '-a ingress-appgw --appgw-id {appgw_id} -o json'
        aks_cluster = self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.ingressApplicationGateway.enabled', True),
            self.check(
                'addonProfiles.ingressApplicationGateway.config.applicationGatewayId', appgw_id)
        ]).get_output_in_json()

        addon_client_id = aks_cluster["addonProfiles"]["ingressApplicationGateway"]["identity"]["clientId"]

        self.kwargs.update({
            'addon_client_id': addon_client_id,
        })

    @AllowLargeResponse()
    @ResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_create_with_openservicemesh_addon(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --enable-managed-identity --generate-ssh-keys ' \
                     '-a open-service-mesh -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.openServiceMesh.enabled', True),
        ])

    @AllowLargeResponse()
    @ResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_enable_addon_with_openservicemesh(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --enable-managed-identity --service-principal xxxx --client-secret yyyy --generate-ssh-keys -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.openServiceMesh', None),
        ])

        enable_cmd = 'aks enable-addons --addons open-service-mesh --resource-group={resource_group} --name={name} -o json'
        self.cmd(enable_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.openServiceMesh.enabled', True),
        ])

    @AllowLargeResponse()
    @ResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_disable_addon_openservicemesh(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --enable-managed-identity --service-principal xxxx --client-secret yyyy --generate-ssh-keys ' \
                     '-a open-service-mesh -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.openServiceMesh.enabled', True),
        ])

        disable_cmd = 'aks disable-addons --addons open-service-mesh --resource-group={resource_group} --name={name} -o json'
        self.cmd(disable_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.openServiceMesh.enabled', False),
            self.check('addonProfiles.openServiceMesh.config', None)
        ])

    @AllowLargeResponse()
    @ResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_create_with_confcom_addon(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --enable-managed-identity --generate-ssh-keys ' \
                     '-a confcom -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.ACCSGXDevicePlugin.enabled', True),
            self.check(
                'addonProfiles.ACCSGXDevicePlugin.config.ACCSGXQuoteHelperEnabled', "true")
        ])

    @AllowLargeResponse()
    @ResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_create_with_confcom_addon_helper_disabled(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --enable-managed-identity --generate-ssh-keys ' \
                     '-a confcom --disable-sgxquotehelper -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.ACCSGXDevicePlugin.enabled', True),
            self.check(
                'addonProfiles.ACCSGXDevicePlugin.config.ACCSGXQuoteHelperEnabled', "false")
        ])

    @AllowLargeResponse()
    @ResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_enable_addons_confcom_addon(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --enable-managed-identity --generate-ssh-keys ' \
                     '-o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.ACCSGXDevicePlugin', None)
        ])

        enable_cmd = 'aks enable-addons --addons confcom --resource-group={resource_group} --name={name} -o json'
        self.cmd(enable_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.ACCSGXDevicePlugin.enabled', True),
            self.check(
                'addonProfiles.ACCSGXDevicePlugin.config.ACCSGXQuoteHelperEnabled', "true")
        ])

    @AllowLargeResponse()
    @ResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_disable_addons_confcom_addon(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --enable-managed-identity --generate-ssh-keys ' \
                     '-a confcom -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.ACCSGXDevicePlugin.enabled', True),
            self.check(
                'addonProfiles.ACCSGXDevicePlugin.config.ACCSGXQuoteHelperEnabled', "true")
        ])

        disable_cmd = 'aks disable-addons --addons confcom --resource-group={resource_group} --name={name} -o json'
        self.cmd(disable_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.ACCSGXDevicePlugin.enabled', False),
            self.check('addonProfiles.ACCSGXDevicePlugin.config', None)
        ])

    @live_only()
    @AllowLargeResponse()
    @ResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_stop_and_start(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name}'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
        ])

        stop_cmd = 'aks stop --resource-group={resource_group} --name={name}'
        self.cmd(stop_cmd)

        start_cmd = 'aks start --resource-group={resource_group} --name={name}'
        self.cmd(start_cmd)

    @AllowLargeResponse()
    @ResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_create_with_managed_disk(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name
        })
        create_cmd = 'aks create --resource-group={resource_group} --name={name} ' \
                     '--generate-ssh-keys ' \
                     '--vm-set-type VirtualMachineScaleSets -c 1 ' \
                     '--node-osdisk-type=Managed'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('agentPoolProfiles[0].osDiskType', 'Managed'),
        ])

    @AllowLargeResponse()
    @ResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_create_with_ephemeral_disk(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} ' \
                     '--generate-ssh-keys ' \
                     '--vm-set-type VirtualMachineScaleSets -c 1 ' \
                     '--node-osdisk-type=Ephemeral --node-osdisk-size 60'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('agentPoolProfiles[0].osDiskType', 'Ephemeral'),
        ])

    @AllowLargeResponse()
    @ResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_nodepool_get_upgrades(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        node_pool_name = self.create_random_name('c', 6)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'node_pool_name': node_pool_name
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} ' \
                     '--nodepool-name {node_pool_name} ' \
                     '-c 1'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
        ])

        # nodepool get-upgrades
        self.cmd('aks nodepool get-upgrades '
                 '--resource-group={resource_group} '
                 '--cluster-name={name} '
                 '--nodepool-name={node_pool_name}',
                 checks=[
                     # if rerun the recording, please update latestNodeImageVersion to the latest value
                     self.check('latestNodeImageVersion',
                                'AKSUbuntu-1604-2020.10.28'),
                     self.check(
                         'type', "Microsoft.ContainerService/managedClusters/agentPools/upgradeProfiles")
                 ])

        # delete
        self.cmd(
            'aks delete -g {resource_group} -n {name} --yes --no-wait', checks=[self.is_empty()])

    @AllowLargeResponse()
    @ResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_upgrade_node_image_only_cluster(self, resource_group, resource_group_location):
        # kwargs for string formatting
        aks_name = self.create_random_name('cliakstest', 16)
        node_pool_name = self.create_random_name('c', 6)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'node_pool_name': node_pool_name
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} ' \
                     '--nodepool-name {node_pool_name} ' \
                     '--generate-ssh-keys ' \
                     '--vm-set-type VirtualMachineScaleSets --node-count=1 ' \
                     '-o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded')
        ])

        upgrade_node_image_only_cluster_cmd = 'aks upgrade ' \
                                              '-g {resource_group} ' \
                                              '-n {name} ' \
                                              '--node-image-only ' \
                                              '--yes'
        self.cmd(upgrade_node_image_only_cluster_cmd, checks=[
            self.check(
                'agentPoolProfiles[0].provisioningState', 'UpgradingNodeImageVersion')
        ])

    @AllowLargeResponse()
    @ResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_upgrade_node_image_only_nodepool(self, resource_group, resource_group_location):
        # kwargs for string formatting
        aks_name = self.create_random_name('cliakstest', 16)
        node_pool_name = self.create_random_name('c', 6)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'node_pool_name': node_pool_name
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} ' \
                     '--nodepool-name {node_pool_name} ' \
                     '--generate-ssh-keys ' \
                     '--vm-set-type VirtualMachineScaleSets --node-count=1 ' \
                     '-o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded')
        ])

        upgrade_node_image_only_nodepool_cmd = 'aks nodepool upgrade ' \
                                               '--resource-group {resource_group} ' \
                                               '--cluster-name {name} ' \
                                               '-n {node_pool_name} ' \
                                               '--node-image-only ' \
                                               '--no-wait'
        self.cmd(upgrade_node_image_only_nodepool_cmd)

        get_nodepool_cmd = 'aks nodepool show ' \
                           '--resource-group={resource_group} ' \
                           '--cluster-name={name} ' \
                           '-n {node_pool_name} '
        self.cmd(get_nodepool_cmd, checks=[
            self.check('provisioningState', 'UpgradingNodeImageVersion')
        ])

    @AllowLargeResponse()
    @ResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_create_with_windows(self, resource_group, resource_group_location):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'dns_name_prefix': self.create_random_name('cliaksdns', 16),
            'location': resource_group_location,
            'resource_type': 'Microsoft.ContainerService/ManagedClusters',
            'windows_admin_username': 'azureuser1',
            'windows_admin_password': 'replace-Password1234$',
            'nodepool2_name': 'npwin',
        })

        # create
        create_cmd = 'aks create --resource-group={resource_group} --name={name} --location={location} ' \
                     '--dns-name-prefix={dns_name_prefix} --node-count=1 --generate-ssh-keys ' \
                     '--windows-admin-username={windows_admin_username} --windows-admin-password={windows_admin_password} ' \
                     '--load-balancer-sku=standard --vm-set-type=virtualmachinescalesets --network-plugin=azure'
        self.cmd(create_cmd, checks=[
            self.exists('fqdn'),
            self.exists('nodeResourceGroup'),
            self.check('provisioningState', 'Succeeded'),
            self.check('windowsProfile.adminUsername', 'azureuser1')
        ])

        # nodepool add
        self.cmd('aks nodepool add --resource-group={resource_group} --cluster-name={name} --name={nodepool2_name} --os-type Windows --node-count=1', checks=[
            self.check('provisioningState', 'Succeeded')
        ])

        # update Windows license type
        self.cmd('aks update --resource-group={resource_group} --name={name} --enable-ahub', checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('windowsProfile.licenseType', 'Windows_Server')
        ])

        # #nodepool delete
        self.cmd(
            'aks nodepool delete --resource-group={resource_group} --cluster-name={name} --name={nodepool2_name} --no-wait', checks=[self.is_empty()])

        # delete
        self.cmd(
            'aks delete -g {resource_group} -n {name} --yes --no-wait', checks=[self.is_empty()])

    @AllowLargeResponse()
    @ResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_create_with_ahub(self, resource_group, resource_group_location):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'dns_name_prefix': self.create_random_name('cliaksdns', 16),
            'location': resource_group_location,
            'resource_type': 'Microsoft.ContainerService/ManagedClusters',
            'windows_admin_username': 'azureuser1',
            'windows_admin_password': 'replace-Password1234$',
            'nodepool2_name': 'npwin',
        })

        # create
        create_cmd = 'aks create --resource-group={resource_group} --name={name} --location={location} ' \
                     '--dns-name-prefix={dns_name_prefix} --node-count=1 --generate-ssh-keys ' \
                     '--windows-admin-username={windows_admin_username} --windows-admin-password={windows_admin_password} ' \
                     '--load-balancer-sku=standard --vm-set-type=virtualmachinescalesets --network-plugin=azure --enable-ahub'
        self.cmd(create_cmd, checks=[
            self.exists('fqdn'),
            self.exists('nodeResourceGroup'),
            self.check('provisioningState', 'Succeeded'),
            self.check('windowsProfile.adminUsername', 'azureuser1'),
            self.check('windowsProfile.licenseType', 'Windows_Server')
        ])

        # nodepool add
        self.cmd('aks nodepool add --resource-group={resource_group} --cluster-name={name} --name={nodepool2_name} --os-type Windows --node-count=1', checks=[
            self.check('provisioningState', 'Succeeded')
        ])

        # update Windows license type
        self.cmd('aks update --resource-group={resource_group} --name={name} --disable-ahub', checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('windowsProfile.licenseType', 'None')
        ])

        # #nodepool delete
        self.cmd(
            'aks nodepool delete --resource-group={resource_group} --cluster-name={name} --name={nodepool2_name} --no-wait', checks=[self.is_empty()])

        # delete
        self.cmd(
            'aks delete -g {resource_group} -n {name} --yes --no-wait', checks=[self.is_empty()])

    @live_only()
    @AllowLargeResponse()
    @ResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westeurope')
    def test_aks_update_to_msi_cluster(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --generate-ssh-keys '
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
        ])

        # update to MSI cluster
        self.cmd('aks update --resource-group={resource_group} --name={name} --enable-managed-identity --yes', checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('identity.type', 'SystemAssigned')
        ])

        # delete
        self.cmd(
            'aks delete -g {resource_group} -n {name} --yes --no-wait', checks=[self.is_empty()])

    @live_only()  # without live only fails with need az login
    @AllowLargeResponse()
    @ResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='eastus')
    def test_aks_create_with_gitops_addon(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} -a gitops -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.gitops.enabled', True),
        ])

    @live_only()  # without live only fails with need az login
    @AllowLargeResponse()
    @ResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='eastus')
    def test_aks_enable_addon_with_gitops(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.gitops', None),
        ])

        enable_cmd = 'aks enable-addons --addons gitops --resource-group={resource_group} --name={name} -o json'
        self.cmd(enable_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.gitops.enabled', True),
        ])

    @live_only()  # without live only fails with need az login
    @AllowLargeResponse()
    @ResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='eastus')
    def test_aks_disable_addon_gitops(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} -a gitops -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.gitops.enabled', True),
        ])

        disable_cmd = 'aks disable-addons --addons gitops --resource-group={resource_group} --name={name} -o json'
        self.cmd(disable_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.gitops.enabled', False),
            self.check('addonProfiles.gitops.config', None)
        ])

    @AllowLargeResponse()
    @ResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_create_with_node_config(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'kc_path': _get_test_data_file('kubeletconfig.json'),
            'oc_path': _get_test_data_file('linuxosconfig.json')
        })

        # use custom feature so it does not require subscription to regiter the feature
        create_cmd = 'aks create --resource-group={resource_group} --name={name} --generate-ssh-keys ' \
                     '--kubelet-config={kc_path} --linux-os-config={oc_path} --aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/CustomNodeConfigPreview -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('agentPoolProfiles[0].kubeletConfig.cpuManagerPolicy', 'static'),
            self.check('agentPoolProfiles[0].linuxOsConfig.swapFileSizeMb', 1500),
            self.check('agentPoolProfiles[0].linuxOsConfig.sysctls.netIpv4TcpTwReuse', True)
        ])

        # nodepool add
        nodepool_cmd = 'aks nodepool add --resource-group={resource_group} --cluster-name={name} --name=nodepool2 --node-count=1 ' \
                       '--kubelet-config={kc_path} --linux-os-config={oc_path} --aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/CustomNodeConfigPreview'
        self.cmd(nodepool_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('kubeletConfig.cpuCfsQuotaPeriod', '200ms'),
            self.check('linuxOsConfig.sysctls.netCoreSomaxconn', 163849)
        ])
