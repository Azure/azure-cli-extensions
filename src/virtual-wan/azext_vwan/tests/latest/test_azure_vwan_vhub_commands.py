# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, StorageAccountPreparer,
                               JMESPathCheck, NoneCheck, api_version_constraint)

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

class AzureVWanVHubScenario(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_azure_vwan_route_table')
    def test_azure_vwan_vhub_basic_scenario(self, resource_group):
        self.kwargs.update({
            'vwan': 'clitestvwan',
            'vhub': 'clitestvhub',
            'rg': resource_group
        })

        self.cmd('network vwan create -n {vwan} -g {rg} --type Standard')
        self.cmd('network vhub create -g {rg} -n {vhub} --vwan {vwan}  --address-prefix 10.0.0.0/24 -l SouthCentralUS --sku Standard')

        self.cmd('network vhub update -g {rg} -n {vhub} --sku Basic')
        self.cmd('network vwan update -g {rg} -n {vwan} --type Basic')

    @ResourceGroupPreparer(name_prefix='cli_test_azure_vhub_connection')
    def test_azure_vhub_connection_basic_scenario(self, resource_group):
        self.kwargs.update({
            'vnet': 'clitestvnet',
            'vwan': 'clitestvwan',
            'vhub': 'clitestvhub',
            'connection': 'clitestvhubconnection',
            'rg': resource_group
        })

        self.cmd('network vnet create -g {rg} -n {vnet}')
        self.cmd('network vwan create -n {vwan} -g {rg} --type Standard')
        self.cmd('network vhub create -g {rg} -n {vhub} --vwan {vwan}  --address-prefix 10.5.0.0/16 -l westus --sku Standard')
        self.cmd('network vhub connection create --resource-group {rg} --vhub-name {vhub} --name {connection} --remote-vnet {vnet}', checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('name', self.kwargs.get('connection'))
        ])

    @ResourceGroupPreparer(name_prefix='cli_test_azure_vpn_server_config')
    def test_azure_vpn_server_config_basic_scenario(self, resource_group):
        self.kwargs.update({
            'vserverconfig': 'clitestserverconfig',
            'cert_file': os.path.join(TEST_DIR, 'ApplicationGatewayAuthCert.cer'),
            'pem_file': os.path.join(TEST_DIR, 'ApplicationGatewayAuthCert.pem'),
            'rg': resource_group
        })

        self.cmd('network vpn-server-config create -n {vserverconfig} -g {rg} '
                 '--vpn-client-root-certs "{cert_file}" '
                 '--vpn-client-revoked-certs "{pem_file}"')

        self.cmd('network vpn-server-config set -n {vserverconfig} -g {rg} --auth-types Radius '
                 '--radius-client-root-certs "{cert_file}" '
                 '--radius-server-root-certs "{pem_file}" '
                 '--radius-servers address=test1 secret=clitest score=10 '
                 '--radius-servers address=test2 secret=clitest score=10')

        self.cmd('network vpn-server-config wait -n {vserverconfig} -g {rg} --created')

        self.cmd('network vpn-server-config set -n {vserverconfig} -g {rg} --auth-types AAD '
                 '--aad-audience 222 '
                 '--aad-issuer 222 '
                 '--aad-tenant 222 '
                 '--no-wait')

        self.cmd('network vpn-server-config wait -n {vserverconfig} -g {rg} --created')

        self.cmd('network vpn-server-config show -n {vserverconfig} -g {rg}')

        self.cmd('network vpn-server-config list -g {rg}')

        self.cmd('network vpn-server-config list')

        self.cmd('network vpn-server-config ipsec-policy add -n {vserverconfig} -g {rg} '
                 '--ipsec-encryption AES256 --ipsec-integrity SHA256 '
                 '--sa-lifetime 86471 --sa-data-size 429496 --ike-encryption AES256 '
                 '--ike-integrity SHA384 --dh-group DHGroup14 --pfs-group PFS14')

        self.cmd('network vpn-server-config ipsec-policy list -n {vserverconfig} -g {rg}')

        self.cmd('network vpn-server-config ipsec-policy remove -n {vserverconfig} -g {rg} --index 0')

        self.cmd('network vpn-server-config ipsec-policy add -n {vserverconfig} -g {rg} '
                 '--ipsec-encryption AES256 --ipsec-integrity SHA256 '
                 '--sa-lifetime 86471 --sa-data-size 429496 --ike-encryption AES256 '
                 '--ike-integrity SHA384 --dh-group DHGroup14 --pfs-group PFS14')

        self.cmd('network vpn-server-config ipsec-policy list -n {vserverconfig} -g {rg}')

        self.cmd('network vpn-server-config delete -n {vserverconfig} -g {rg}')

    @ResourceGroupPreparer(name_prefix='cli_test_azure_vhub_connection')
    def test_azure_p2s_vpn_gateway_basic_scenario(self, resource_group):
        self.kwargs.update({
            'vnet': 'clitestvnet',
            'vwan': 'clitestvwan',
            'vhub': 'clitestvhub',
            'vserverconfig': 'clitestserverconfig',
            'vp2sgateway': 'clitestvp2sgateway',
            'rg': resource_group
        })

        self.cmd('network vnet create -g {rg} -n {vnet}')
        self.cmd('network vwan create -n {vwan} -g {rg} --type Standard')
        self.cmd('network vhub create -g {rg} -n {vhub} --vwan {vwan}  --address-prefix 10.5.0.0/16 -l westus --sku Standard')
        self.cmd('network vpn-server-config create -n {vserverconfig} -g {rg} '
                 '--vpn-client-root-certs ".\\ApplicationGatewayAuthCert.cer" '
                 '--vpn-client-revoked-certs ".\\ApplicationGatewayAuthCert.pem"')
        self.cmd('az network p2s-vpn-gateway create -g {rg} -n {vp2sgateway} --scale-unit 2 '
                 '--vhub {vhub} --vpn-server-config {vserverconfig} --address-space 10.0.0.0/24 11.0.0.0/24')
