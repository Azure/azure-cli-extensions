# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from azure.cli.testsdk.scenario_tests import AllowLargeResponse
import json

class NginxScenarioTest(ScenarioTest):

    @AllowLargeResponse(size_kb=10240)
    @ResourceGroupPreparer(name_prefix='AZCLIDeploymentTestRG_', random_name_length=34, location='eastus2euap')
    def test_deployment_cert_config(self, resource_group):
        self.kwargs.update({
            'deployment_name': 'azclitest-deployment',
            'location': 'eastus2euap',
            'rg': resource_group,
            'sku': 'standard_Monthly',
            'public_ip_name': 'azclitest-public-ip',
            'vnet_name': 'azclitest-vnet',
            'subnet_name': 'azclitest-subnet',
            'tags': 'tag1="value1" tag2="value2"',
            'kv_name': self.create_random_name(prefix='cli', length=20),
            'cert_name': 'azclitestcert',
            'config_files': '[{"content":"aHR0cCB7DQogICAgdXBzdHJlYW0gYXBwIHsNCiAgICAgICAgc2VydmVyIDE3Mi4yNy4wLjQ6ODA7DQogICAgfQ0KICAgIHNlcnZlciB7DQogICAgICAgIGxpc3RlbiA4MDsNCiAgICAgICAgbG9jYXRpb24gLyB7DQogICAgICAgICAgICBkZWZhdWx0X3R5cGUgdGV4dC9odG1sOw0KICAgICAgICAgICAgcmV0dXJuIDIwMCAnPCFET0NUWVBFIGh0bWw+PGgxIHN0eWxlPSJmb250LXNpemU6MzBweDsiPkhlbGxvIGZyb20gTmdpbnggV2ViIFNlcnZlciE8L2gxPlxuJzsNCiAgICAgICAgfQ0KICAgICAgICBsb2NhdGlvbiAvYXBwLyB7DQogICAgICAgICAgICBwcm94eV9wYXNzIGh0dHA6Ly9hcHAuYmxvYi5jb3JlLndpbmRvd3MubmV0LzsNCiAgICAgICAgICAgIHByb3h5X2h0dHBfdmVyc2lvbiAxLjE7DQogICAgICAgICAgICBwcm94eV9yZWFkX3RpbWVvdXQgNjAwOw0KCSAgICAgICAgcHJveHlfY29ubmVjdF90aW1lb3V0IDYwMDsNCgkgICAgICAgIHByb3h5X3NlbmRfdGltZW91dCA2MDA7DQogICAgICAgIH0NCiAgICB9DQp9","virtual-path":"/etc/nginx/nginx.conf"}]'
        })
        # Nginx for Azure Deployment
        public_ip = self.cmd('network public-ip create --resource-group {rg} --name {public_ip_name} --version IPv4 --sku Standard --zone 2').get_output_in_json()
        vnet = self.cmd('network vnet create --resource-group {rg} --name {vnet_name} --address-prefixes 10.0.0.0/16 --subnet-name {subnet_name}').get_output_in_json()
        self.cmd('network vnet subnet update --resource-group {rg} --name {subnet_name} --vnet-name {vnet_name} --delegations NGINX.NGINXPLUS/nginxDeployments')

        self.kwargs['public_ip_addresses'] = "{public-ip-addresses:[{id:" + public_ip['publicIp']['id'] + "}]}"
        self.kwargs['subnet_id'] = "{subnet-id:" + vnet['newVNet']['subnets'][0]['id'] + "}"

        self.cmd('nginx deployment create --name {deployment_name} --resource-group {rg} --location {location} --sku name={sku} --enable-diagnostics true --network-profile front-end-ip-configuration="{public_ip_addresses}" network-interface-configuration="{subnet_id}"', checks=[
            self.check('properties.provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['deployment_name'])
        ])

        deployment_list = self.cmd('nginx deployment list --resource-group {rg}',).get_output_in_json()
        assert len(deployment_list) > 0
        
        self.cmd('nginx deployment update --name {deployment_name} --resource-group {rg} --location {location} --tags {tags} --enable-diagnostics false', checks=[
            self.check('properties.provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['deployment_name'])
        ])
        self.cmd('nginx deployment wait --updated --name {deployment_name} --resource-group {rg}')
        updated_deployment = self.cmd('nginx deployment show --name {deployment_name} --resource-group {rg}').get_output_in_json()
        assert updated_deployment['tags'] is not None
        assert updated_deployment['properties']['enableDiagnosticsSupport'] is False

        # Nginx for Azure certificates
        self.cmd('keyvault create --name {kv_name} --resource-group {rg} --location {location}')
        policy = self.cmd('keyvault certificate get-default-policy').get_output_in_json()
        self.kwargs['policy'] = policy
        with open('policy.json', 'w') as json_file:
            json.dump(policy, json_file)
        
        self.cmd('keyvault certificate create --vault-name {kv_name} -n {cert_name} -p @policy.json')
        certificate = self.cmd('keyvault certificate show --name {cert_name} --vault-name {kv_name}').get_output_in_json()
        self.kwargs['kv_secret_id'] = certificate['sid']
        self.cmd('nginx deployment certificate create --certificate-name {cert_name} --deployment-name {deployment_name} --resource-group {rg} --certificate-path /etc/nginx/test.cert --key-path /etc/nginx/test.key --key-vault-secret-id {kv_secret_id}', checks=[
            self.check('properties.provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['cert_name']),
            self.check('location', self.kwargs['location']),
            self.check('properties.keyVaultSecretId', self.kwargs['kv_secret_id'])
        ])
        
        cert_list = self.cmd('nginx deployment certificate list --deployment-name {deployment_name} --resource-group {rg}').get_output_in_json()
        assert len(cert_list) > 0

        self.cmd('nginx deployment certificate update --certificate-name {cert_name} --deployment-name {deployment_name} --resource-group {rg} --certificate-path /etc/nginx/testupdated.cert --key-path /etc/nginx/testupdated.key', checks=[
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

        # Nginx for Azure configuration
        self.cmd('nginx deployment configuration create --name default --deployment-name {deployment_name} --resource-group {rg} --root-file /etc/nginx/nginx.conf --files {config_files}', checks=[
            self.check('properties.provisioningState', 'Succeeded'),
            self.check('name', 'default'),
            self.check('properties.files[0].virtualPath', '/etc/nginx/nginx.conf'),
            self.check('properties.rootFile', '/etc/nginx/nginx.conf')
        ])
        config_list = self.cmd('nginx deployment configuration list --deployment-name {deployment_name} --resource-group {rg}').get_output_in_json()
        assert len(config_list) > 0

        new_root_config_file_path = '/etc/nginx/nginxupdate.conf'
        updated_config_files = self.kwargs['config_files'].replace('/etc/nginx/nginx.conf', new_root_config_file_path)
        self.kwargs['config_files'] = updated_config_files
        self.cmd('nginx deployment configuration update --name default --deployment-name {deployment_name} --resource-group {rg} --root-file /etc/nginx/nginxupdate.conf --files {config_files}', checks=[
            self.check('properties.provisioningState', 'Succeeded'),
            self.check('name', 'default')
        ])
        self.cmd('nginx deployment configuration wait --updated --name default --deployment-name {deployment_name} --resource-group {rg}')
        self.cmd('nginx deployment configuration show --name default --deployment-name {deployment_name} --resource-group {rg}', checks=[
            self.check('name', 'default'),
            self.check('properties.files[0].virtualPath', new_root_config_file_path),
            self.check('properties.rootFile', new_root_config_file_path),
            self.check('type', 'NGINX.NGINXPLUS/nginxDeployments/configurations')
        ])

        self.cmd('nginx deployment configuration delete --name default --deployment-name {deployment_name} --resource-group {rg} --yes')
        #config_list = self.cmd('nginx deployment configuration list --deployment-name {deployment_name} --resource-group {rg}').get_output_in_json()
        #assert len(config_list) == 0

        self.cmd('nginx deployment delete --name {deployment_name} --resource-group {rg} --yes')
        deployment_list = self.cmd('nginx deployment list --resource-group {rg}').get_output_in_json()
        assert len(deployment_list) == 0
