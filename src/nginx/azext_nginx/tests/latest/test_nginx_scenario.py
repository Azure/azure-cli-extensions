# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from azure.cli.testsdk.scenario_tests import AllowLargeResponse


class NginxScenarioTest(ScenarioTest):

    @AllowLargeResponse(size_kb=10240)
    @ResourceGroupPreparer(name_prefix='AZcliDeploymentTestRG_', random_name_length=34, location='eastus2')
    def test_create_deployment(self, resource_group):
        self.kwargs.update({
            'deployment_name': 'azclitest-deployment',
            'location': 'eastus2',
            'rg': resource_group,
            'sku': 'preview_Monthly_gmz7xq9ge3py',
            'public_ip_name': 'azclitest-public-ip',
            'vnet_name': 'azclitest-vnet',
            'subnet_name': 'azclitest-subnet',
            'tags': 'tag1="value1" tag2="value2"'
        })
        
        public_ip = self.cmd('network public-ip create --resource-group {rg} --name {public_ip_name} --version IPv4 --sku Standard --zone 2').get_output_in_json()
        vnet = self.cmd('network vnet create --resource-group {rg} --name {vnet_name} --address-prefixes 10.0.0.0/16 --subnet-name {subnet_name}').get_output_in_json()
        self.cmd('network vnet subnet update --resource-group {rg} --name {subnet_name} --vnet-name {vnet_name} --delegations NGINX.NGINXPLUS/nginxDeployments')

        self.kwargs['public_ip_addresses'] = "{public-ip-addresses:[{id:" + public_ip['publicIp']['id'] + "}]}"
        self.kwargs['subnet_id'] = "{subnet-id:" + vnet['newVNet']['subnets'][0]['id'] + "}"

        self.cmd('nginx deployment create --name {deployment_name} --resource-group {rg} --location {location} --sku name={sku} --enable-diagnostics-support true --network-profile front-end-ip-configuration="{public_ip_addresses}" network-interface-configuration="{subnet_id}"', checks=[
            self.check('properties.provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['deployment_name'])
        ])

        deployment_list = self.cmd('nginx deployment list --resource-group {rg}',).get_output_in_json()
        assert len(deployment_list) > 0
        
        self.cmd('nginx deployment update --name {deployment_name} --resource-group {rg} --location {location} --tags {tags} --enable-diagnostics-support false', checks=[
            self.check('properties.provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['deployment_name'])
        ])

        updated_deployment = self.cmd('nginx deployment show --name {deployment_name} --resource-group {rg}').get_output_in_json()
        assert updated_deployment['tags'] is not None
        assert updated_deployment['properties']['enableDiagnosticsSupport'] is False

        
        
    def test_list_deployments(self):
        deployment_list = self.cmd('nginx deployment list').get_output_in_json()
        assert len(deployment_list) > 0