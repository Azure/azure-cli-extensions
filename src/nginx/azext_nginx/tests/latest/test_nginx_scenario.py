# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from unittest import mock
import json
import time

class NginxScenarioTest(ScenarioTest):
    @AllowLargeResponse(size_kb=10240)
    @ResourceGroupPreparer(name_prefix='AZCLITestRG_', random_name_length=34, location='eastus2')
    def test_nginx(self, resource_group):
        self.kwargs.update({
            'deployment_name': 'azcli-deployment',
            'location': 'eastus2',
            'rg': resource_group,
            'sku': 'standardv2_Monthly_gmz7xq9ge3py',
            'public_ip_name': 'azclitest-public-ip',
            'vnet_name': 'azclitest-vnet',
            'subnet_name': 'azclitest-subnet',
            'subnet_name2_migrated': 'azclitest-subnet2',
            'tags': 'tag1="value1" tag2="value2"',
            'kv_name': self.create_random_name(prefix='cli', length=20),
            'cert_name': 'azclitestcert',
            'managed_identity': 'azclitestmi',
            'autoscale_settings': '[{name:default,capacity:{min:10,max:30}}]',
            'web_application_firewall_settings': '{activation-state:Enabled}',
            'create_config_file': "[{content:aHR0cCB7CiAgICB1cHN0cmVhbSBhcHAgewogICAgICAgIHpvbmUgYXBwIDY0azsKICAgICAgICBsZWFzdF9jb25uOwogICAgICAgIHNlcnZlciAxMC4wLjEuNDo4MDAwOwogICAgfQoKICAgIHNlcnZlciB7CiAgICAgICAgbGlzdGVuIDgwOwogICAgICAgIHNlcnZlcl9uYW1lICouZXhhbXBsZS5jb207CgogICAgICAgIGxvY2F0aW9uIC8gewogICAgICAgICAgICBwcm94eV9zZXRfaGVhZGVyIEhvc3QgJGhvc3Q7CiAgICAgICAgICAgIHByb3h5X3NldF9oZWFkZXIgWC1SZWFsLUlQICRyZW1vdGVfYWRkcjsKICAgICAgICAgICAgcHJveHlfc2V0X2hlYWRlciBYLVByb3h5LUFwcCBhcHA7CiAgICAgICAgICAgIHByb3h5X3NldF9oZWFkZXIgR2l0aHViLVJ1bi1JZCAwMDAwMDA7CiAgICAgICAgICAgIHByb3h5X2J1ZmZlcmluZyBvbjsKICAgICAgICAgICAgcHJveHlfYnVmZmVyX3NpemUgNGs7CiAgICAgICAgICAgIHByb3h5X2J1ZmZlcnMgOCA4azsKICAgICAgICAgICAgcHJveHlfcmVhZF90aW1lb3V0IDYwczsKICAgICAgICAgICAgcHJveHlfcGFzcyBodHRwOi8vYXBwOwogICAgICAgICAgICBoZWFsdGhfY2hlY2s7CiAgICAgICAgfQogICAgICAgIAogICAgfQp9,virtual-path:/etc/nginx/nginx.conf}]",
            'config_files': '[{"content":"aHR0cCB7DQogICAgdXBzdHJlYW0gYXBwIHsNCiAgICAgICAgc2VydmVyIDE3Mi4yNy4wLjQ6ODA7DQogICAgfQ0KICAgIHNlcnZlciB7DQogICAgICAgIGxpc3RlbiA4MDsNCiAgICAgICAgbG9jYXRpb24gLyB7DQogICAgICAgICAgICBkZWZhdWx0X3R5cGUgdGV4dC9odG1sOw0KICAgICAgICAgICAgcmV0dXJuIDIwMCAnPCFET0NUWVBFIGh0bWw+PGgxIHN0eWxlPSJmb250LXNpemU6MzBweDsiPkhlbGxvIGZyb20gTmdpbnggV2ViIFNlcnZlciE8L2gxPlxuJzsNCiAgICAgICAgfQ0KICAgICAgICBsb2NhdGlvbiAvYXBwLyB7DQogICAgICAgICAgICBwcm94eV9wYXNzIGh0dHA6Ly9hcHAuYmxvYi5jb3JlLndpbmRvd3MubmV0LzsNCiAgICAgICAgICAgIHByb3h5X2h0dHBfdmVyc2lvbiAxLjE7DQogICAgICAgICAgICBwcm94eV9yZWFkX3RpbWVvdXQgNjAwOw0KCSAgICAgICAgcHJveHlfY29ubmVjdF90aW1lb3V0IDYwMDsNCgkgICAgICAgIHByb3h5X3NlbmRfdGltZW91dCA2MDA7DQogICAgICAgIH0NCiAgICB9DQp9","virtual-path":"/etc/nginx/nginx.conf"}]',
            'protected_files': "[{'content':'aHR0cCB7DQogICAgc2VydmVyIHsNCiAgICAgICAgbGlzdGVuIDgwOw0KICAgICAgICByZXR1cm4gMjAwICdIZWxsbyBmcm9tIFByb3RlY3RlZCBGaWxlJzsNCiAgICB9DQp9','virtual-path':'/etc/nginx/protected.conf'}]",
            'compressed_file': '{data:H4sIAAAAAAAAA+3VbWvbMBAHcL/Op7hCoTCIbckPCU0olG3QvVoog21QMCK+1qGyJGRlpBv57pPXbsla1wkdZS3c70UMdxfxP2wn6mqhVuFcq8vg2cTeKMt+Xb37V56zLGBpwvOYpVkyCmLGspwHED9fpI1l44QFCKzWrm9uV/+Vqpwz8GMA3tI0zqKoQRgzZHfF1net8K6Yp9eTP3WJonGFf3bUptag/YYWWBzGIQvT47G/wb1d1tvlt931w4C8KyB/UsCkt5v2drNHAyZdAZMnBcx7u6Pe7vh3wMHWwCaZXDQOFYwf3KRCiRrhTYgrURuJ/iei3sqt58IttIJo66hWiZdiKV3hbgyCw5WLKlfLyV8zFt3SKuBxDEfTg3cf3376OnsP7dzJtOInZyilhs/ayvJgGvnChTraHLDuyHD/eW0Zq1c3RYOuqFCUfuUz3Tg4rPznpH/wy/AchRx+mMGhxVo7LERZ2p1fmrWl4akxt29K17wRTQPtC3ccRR1D/ijpqmJe4fx698L8ZS3M91mY/8vCyctaONln4WT/hdeD9eB//xkQQgghhBBCCCGEEEIIIYQQQggh5FX6CfCArk8AKAAA}',
            'create_waf2_file': 'ew0KICAgICJwb2xpY3kiOiB7DQogICAgICAgICJuYW1lIjogInRlc3Rwb2xpY3kyIiwNCiAgICAgICAgInRlbXBsYXRlIjogeyAibmFtZSI6ICJQT0xJQ1lfVEVNUExBVEVfTkdJTlhfQkFTRSIgfSwNCiAgICAgICAgImFwcGxpY2F0aW9uTGFuZ3VhZ2UiOiAidXRmLTgiLA0KICAgICAgICAiZW5mb3JjZW1lbnRNb2RlIjogImJsb2NraW5nIiwNCiAgICAgICAgImJsb2NraW5nLXNldHRpbmdzIjogew0KICAgICAgICAgICAgInZpb2xhdGlvbnMiOiBbDQogICAgICAgICAgICAgICAgew0KICAgICAgICAgICAgICAgICAgICAibmFtZSI6ICJWSU9MX0pTT05fRk9STUFUIiwNCiAgICAgICAgICAgICAgICAgICAgImFsYXJtIjogdHJ1ZSwNCiAgICAgICAgICAgICAgICAgICAgImJsb2NrIjogdHJ1ZQ0KICAgICAgICAgICAgICAgIH0sDQogICAgICAgICAgICAgICAgew0KICAgICAgICAgICAgICAgICAgICAibmFtZSI6ICJWSU9MX1BBUkFNRVRFUl9WQUxVRV9NRVRBQ0hBUiIsDQogICAgICAgICAgICAgICAgICAgICJhbGFybSI6IGZhbHNlLA0KICAgICAgICAgICAgICAgICAgICAiYmxvY2siOiBmYWxzZQ0KICAgICAgICAgICAgICAgIH0NCiAgICAgICAgICAgIF0NCiAgICAgICAgfQ0KICAgIH0NCn0=',
        })

        # Nginx for Azure Deployment
        public_ip = self.cmd('network public-ip create --resource-group {rg} --location {location} --name {public_ip_name} --version IPv4 --sku Standard --zone 2').get_output_in_json()
        # creating first vnet and first subnet
        self.cmd('network vnet create --resource-group {rg} --location {location} --name {vnet_name} --address-prefixes 10.0.0.0/16 --subnet-name {subnet_name}').get_output_in_json()
        self.cmd('network vnet subnet update --resource-group {rg} --name {subnet_name} --vnet-name {vnet_name} --delegations NGINX.NGINXPLUS/nginxDeployments')

        # creating second subnet
        self.cmd('network vnet subnet create --resource-group {rg} --name {subnet_name2_migrated} --vnet-name {vnet_name} --address-prefixes 10.0.1.0/24').get_output_in_json()
        self.cmd('network vnet subnet update --resource-group {rg} --name {subnet_name2_migrated} --vnet-name {vnet_name} --delegations NGINX.NGINXPLUS/nginxDeployments')

        self.kwargs['public_ip_addresses'] = "{public-ip-addresses:[{id:" + public_ip['publicIp']['id'] + "}]}"

        subnet1 = self.cmd('network vnet subnet show --name {subnet_name} --vnet-name {vnet_name} --resource-group {rg}').get_output_in_json()
        subnet2 = self.cmd('network vnet subnet show --name {subnet_name2_migrated} --vnet-name {vnet_name} --resource-group {rg}').get_output_in_json()
        self.kwargs['subnet_id'] = "{subnet-id:" + subnet1['id'] + "}"
        self.kwargs['subnet_id_migrated'] = "{subnet-id:" + subnet2['id'] + "}"

        managed_identity = self.cmd('identity create --name {managed_identity} --resource-group {rg}').get_output_in_json()
        identity_object_id = managed_identity['principalId']
        self.kwargs.update({
            'identity_object_id': identity_object_id,
        })
        self.kwargs['identities'] = "{\"type\":\"UserAssigned\",\"userAssignedIdentities\":{\"" + managed_identity['id'] + "\":{}}}"
        self.cmd('nginx deployment create --name {deployment_name} --resource-group {rg} --location {location} --sku name={sku} --enable-diagnostics true --network-profile front-end-ip-configuration="{public_ip_addresses}" network-interface-configuration="{subnet_id}" --identity {identities} --scaling-properties capacity=10 --auto-upgrade-profile upgrade-channel=preview', checks=[
            self.check('properties.provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['deployment_name'])
        ])

        deployment_list = self.cmd('nginx deployment list --resource-group {rg}',).get_output_in_json()
        assert len(deployment_list) > 0
        self.cmd('nginx deployment update --name {deployment_name} --resource-group {rg} --tags {tags} --enable-diagnostics false --scaling-properties profiles={autoscale_settings}  --nginx-app-protect  web-application-firewall-settings={web_application_firewall_settings}', checks=[
            self.check('properties.provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['deployment_name'])
        ])
        self.cmd('nginx deployment wait --updated --name {deployment_name} --resource-group {rg}')
        updated_deployment = self.cmd('nginx deployment show --name {deployment_name} --resource-group {rg}').get_output_in_json()
        assert updated_deployment['tags'] is not None
        assert updated_deployment['properties']['enableDiagnosticsSupport'] is False

        # migrating to subnet 2
        self.cmd('nginx deployment update --name {deployment_name} --resource-group {rg} --network-profile front-end-ip-configuration="{public_ip_addresses}" network-interface-configuration="{subnet_id_migrated}"', checks=[
            self.check('properties.provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['deployment_name'])
        ])
        self.cmd('nginx deployment wait --updated --name {deployment_name} --resource-group {rg}')
        updated_deployment = self.cmd('nginx deployment show --name {deployment_name} --resource-group {rg}').get_output_in_json()
        assert updated_deployment['properties']['networkProfile']['networkInterfaceConfiguration']['subnetId'] == subnet2['id']

        # Nginx for Azure API key
        create_api_key = 'nginx deployment api-key create -n "test-key" --deployment-name {deployment_name} --resource-group {rg} --end-date-time "2025-11-20T17:59:39.123Z" --secret-text "s5V/9~o^4TYCVwmNc2Y>Y1^64&T`0sXg-j9!Xy|8"'
        self.cmd(create_api_key)
        # Nginx for Azure certificates
        create_keyvault = 'keyvault create --name {kv_name} --resource-group {rg}'
        kv = self.cmd(create_keyvault, checks=[
        self.check('properties.provisioningState', 'Succeeded')
        ]).get_output_in_json()
        kv_resource_id = kv['id']
        assert kv_resource_id is not None
        self.kwargs.update({
            'kv_resource_id': kv_resource_id,
        })
        policy = self.cmd('keyvault certificate get-default-policy').get_output_in_json()
        self.kwargs['policy'] = policy
        with open('policy.json', 'w') as json_file:
            json.dump(policy, json_file)
        
        current_user = self.cmd('ad signed-in-user show').get_output_in_json()
        current_user_object_id = current_user['id']
        self.kwargs.update({
            'current_user_object_id': current_user_object_id,
        })

        # Grant the current user Key Vault Administrator permissions
        with mock.patch('azure.cli.command_modules.role.custom._gen_guid', side_effect=self.create_guid):
            self.cmd("role assignment create --role 'Key Vault Administrator' --assignee-object-id {current_user_object_id} --scope {kv_resource_id} --assignee-principal-type 'User'")
        
        with mock.patch('azure.cli.command_modules.role.custom._gen_guid', side_effect=self.create_guid):
            self.cmd("role assignment create --role 'Key Vault Administrator' --assignee-object-id {identity_object_id} --scope {kv_resource_id} --assignee-principal-type 'ServicePrincipal'")
        
        time.sleep(60) # wait for the role assignment to propagate
        self.cmd('keyvault certificate create --vault-name {kv_name} -n {cert_name} -p @policy.json')
        certificate = self.cmd('keyvault certificate show --name {cert_name} --vault-name {kv_name}').get_output_in_json()
        self.kwargs['kv_secret_id'] = certificate['sid']
        self.kwargs['mi_principal_id'] = self.cmd('identity show --name {managed_identity} --resource-group {rg}').get_output_in_json()['principalId']

        if self.is_live:
            print('=-=-=-=-=-=-=-=-= into the is live')
        print('-=-=-=-=-=-=-=-= Sleeping for 30 seconds to wait for the role assignment to propagate')
        self.cmd('nginx deployment certificate create --certificate-name {cert_name} --deployment-name {deployment_name} --resource-group {rg} --certificate-path /etc/nginx/test.cert --key-path /etc/nginx/test.key --key-vault-secret-id {kv_secret_id}', checks=[
            self.check('properties.provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['cert_name']),
            self.check('properties.keyVaultSecretId', self.kwargs['kv_secret_id'])
        ])
        cert_list = self.cmd('nginx deployment certificate list --deployment-name {deployment_name} --resource-group {rg}').get_output_in_json()
        assert len(cert_list) > 0
        self.cmd('nginx deployment certificate update --certificate-name {cert_name} --deployment-name {deployment_name} --resource-group {rg} --certificate-path /etc/nginx/testupdated.cert --key-path /etc/nginx/testupdated.key', checks=[
            self.check('properties.provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['cert_name']),
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
        self.cmd("nginx deployment configuration create --name default --deployment-name {deployment_name} --resource-group {rg}  --root-file /etc/nginx/nginx.conf --files {create_config_file}", checks=[
            self.check('properties.provisioningState', 'Succeeded'),
            self.check('name', 'default'),
        ])
        config_list = self.cmd('nginx deployment configuration list --deployment-name {deployment_name} --resource-group {rg}').get_output_in_json()
        assert len(config_list) > 0
        update_config = 'nginx deployment configuration update --name default --deployment-name {deployment_name} --resource-group {rg}  --root-file nginx.conf --package data=H4sIAAAAAAAAA+3VbWvbMBAHcL/Op7hCoTCIbckPCU0olG3QvVoog21QMCK+1qGyJGRlpBv57pPXbsla1wkdZS3c70UMdxfxP2wn6mqhVuFcq8vg2cTeKMt+Xb37V56zLGBpwvOYpVkyCmLGspwHED9fpI1l44QFCKzWrm9uV/+Vqpwz8GMA3tI0zqKoQRgzZHfF1net8K6Yp9eTP3WJonGFf3bUptag/YYWWBzGIQvT47G/wb1d1tvlt931w4C8KyB/UsCkt5v2drNHAyZdAZMnBcx7u6Pe7vh3wMHWwCaZXDQOFYwf3KRCiRrhTYgrURuJ/iei3sqt58IttIJo66hWiZdiKV3hbgyCw5WLKlfLyV8zFt3SKuBxDEfTg3cf3376OnsP7dzJtOInZyilhs/ayvJgGvnChTraHLDuyHD/eW0Zq1c3RYOuqFCUfuUz3Tg4rPznpH/wy/AchRx+mMGhxVo7LERZ2p1fmrWl4akxt29K17wRTQPtC3ccRR1D/ijpqmJe4fx698L8ZS3M91mY/8vCyctaONln4WT/hdeD9eB//xkQQgghhBBCCCGEEEIIIYQQQggh5FX6CfCArk8AKAAA'
        self.cmd(update_config, checks=[
            self.check('name', 'default'),
        ])
        update_config = 'nginx deployment configuration update --name default --deployment-name {deployment_name} --resource-group {rg}  --root-file /etc/nginx/nginx.conf --files {create_config_file} --protected-files {protected_files}'
        self.cmd(update_config, checks=[
            self.check('name', 'default'),
        ])
        self.cmd('nginx deployment configuration delete --name default --deployment-name {deployment_name} --resource-group {rg} --yes')
        self.cmd('nginx deployment configuration analyze --name default --deployment-name {deployment_name}  --resource-group {rg} --root-file nginx.conf --package {compressed_file}', checks=[
            self.check('status', 'SUCCEEDED'),
        ])

        # Nginx for Azure Waf v2
        self.cmd("nginx deployment waf-policy create --name default --deployment-name {deployment_name} --resource-group {rg}  --filepath /etc/app_protect/conf/policy.json --content {create_waf2_file}", checks=[
            self.check('properties.provisioningState', 'Succeeded'),
            self.check('name', 'default'),
        ])

        self.cmd("nginx deployment waf-policy show --name default --deployment-name {deployment_name} --resource-group {rg} ", checks=[
            self.check('name', 'default'),
        ])

        waf_policy_list = self.cmd("nginx deployment waf-policy list --deployment-name {deployment_name} --resource-group {rg} ").get_output_in_json()
        assert len(waf_policy_list) > 0

        self.cmd("nginx deployment waf-policy update --name default --deployment-name {deployment_name} --resource-group {rg}  --filepath /etc/app_protect/conf/policy2.json --content {create_waf2_file}", checks=[
            self.check('name', 'default'),
        ])

        self.cmd('nginx deployment waf-policy delete --name default --deployment-name {deployment_name} --resource-group {rg} --yes')
        waf_policy_list = self.cmd("nginx deployment waf-policy list --deployment-name {deployment_name} --resource-group {rg} ").get_output_in_json()
        assert len(waf_policy_list) == 0

        self.cmd('nginx deployment delete --name {deployment_name} --resource-group {rg} --yes')
        deployment_list = self.cmd('nginx deployment list --resource-group {rg}').get_output_in_json()
        assert len(deployment_list) == 0
