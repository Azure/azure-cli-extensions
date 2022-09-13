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
            'tags': 'tag1="value1" tag2="value2"',
            'kv_name': self.create_random_name(prefix='cli', length=20),
            'cert_name': 'azclitestcert'
        })
        # Nginx on Azure Deployment
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
        self.cmd('nginx deployment wait --updated --name {deployment_name} --resource-group {rg}')
        updated_deployment = self.cmd('nginx deployment show --name {deployment_name} --resource-group {rg}').get_output_in_json()
        assert updated_deployment['tags'] is not None
        assert updated_deployment['properties']['enableDiagnosticsSupport'] is False

        # Nginx on Azure certificates
        self.cmd('keyvault create --name {kv_name} --resource-group {rg} --location {location}')
        policy = self.cmd('keyvault certificate get-default-policy').get_output_in_json()
        self.kwargs['policy'] = policy
        self.cmd('keyvault certificate create --vault-name {kv_name} -n {cert_name} -p {policy}')
        certificate = self.cmd('keyvault certificate show --name {cert_name} --vault-name {kv_name}')
        self.kwargs['kv_secret_id'] = certificate['id']
        self.cmd('nginx deployment certificate create --certificate-name {cert_name} --deployment-name {deployment_name} --resource-group {rg} --certificate-virtual-path /etc/nginx/test.cert --key-virtual-path /etc/nginx/test.key --key-vault-secret-id {kv_secret_id}', checks=[
            self.check('properties.provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['cert_name']),
            self.check('location', self.kwargs['location']),
            self.check('properties.keyVaultSecretId', self.kwargs['kv_secret_id'])
        ])
        
        cert_list = self.cmd('nginx deployment certificate list --deployment-name {deployment_name} --resource-group {rg}').get_output_in_json()
        assert len(cert_list) > 0

        self.cmd('nginx deployment certificate update --certificate-name {cert_name} --deployment-name {deployment_name} --resource-group {rg} --certificate-virtual-path /etc/nginx/testupdated.cert --key-virtual-path /etc/nginx/testupdated.key', checks=[
            self.check('properties.provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['cert_name']),
            self.check('location', self.kwargs['location']),
            self.check('properties.keyVaultSecretId', self.kwargs['kv_secret_id'])
        ])
        self.cmd('nginx deployment certificate wait --updated --name {cert_name} --deployment-name {deployment_name} --resource-group {rg}')
        self.cmd('nginx deployment certificate show --certificate-name {cert_name} --deployment-name {deployment_name} --resource-group {rg}', checks=[
            self.check('name', self.kwargs['cert_name']),
            self.check('properties.certificateVirtualPath', '/etc/nginx/testupdated.cert'),
            self.check('properties.keyVirtualPath', '/etc/nginx/testupdated.key')
        ])

        self.cmd('nginx deployment certificate delete --name {cert_name} --deployment-name {deployment_name} --resource-group {rg} --yes')
        cert_list = self.cmd('nginx deployment certificate list --deployment-name {deployment_name} --resource-group {rg}').get_output_in_json()
        assert len(cert_list) == 0