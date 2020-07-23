# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, record_only)

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

    @ResourceGroupPreparer(name_prefix='cli_test_azure_vwan_route')
    def test_azure_vwan_vhub_route_scenario(self, resource_group):
        self.kwargs.update({
            'vwan': 'clitestvwan',
            'vhub': 'clitestvhub',
            'rg': resource_group
        })

        self.cmd('network vwan create -n {vwan} -g {rg} --type Standard')
        self.cmd('network vhub create -g {rg} -n {vhub} --vwan {vwan}  --address-prefix 10.0.0.0/24 -l SouthCentralUS --sku Standard')

        self.cmd('network vhub route add -g {rg} --vhub-name {vhub} --next-hop 10.0.0.7 --address-prefixes 10.3.3.0/28')
        self.cmd('network vhub route reset -g {rg} --vhub-name {vhub}', checks=[
            self.check('@[0].addressPrefixes[0]', '10.3.3.0/28'),
            self.check('@[0].nextHopIpAddress', '10.0.0.7')
        ])

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

    @ResourceGroupPreparer(name_prefix='cli_test_azure_vpn_server_config', location='westcentralus')
    def test_azure_vpn_server_config_basic_scenario(self, resource_group):
        self.kwargs.update({
            'vserverconfig': 'clitestserverconfig',
            'cert_file': os.path.join(TEST_DIR, 'data', 'ApplicationGatewayAuthCert.cer'),
            'pem_file': os.path.join(TEST_DIR, 'data', 'ApplicationGatewayAuthCert.pem'),
            'rg': resource_group,
            'aad_tenant': 'https://login.microsoftonline.com/0ab2c4f4-81e6-44cc-a0b2-b3a47a1443f4',
            'aad_issuer': 'https://sts.windows.net/0ab2c4f4-81e6-44cc-a0b2-b3a47a1443f4/',
            'aad_audience': 'a21fce82-76af-45e6-8583-a08cb3b956f9'
        })

        self.cmd('network vpn-server-config create -n {vserverconfig} -g {rg} '
                 '--vpn-client-root-certs "{cert_file}" '
                 '--vpn-client-revoked-certs "{pem_file}"',
                 checks=[
                     self.check('name', '{vserverconfig}'),
                     self.exists('vpnClientRootCertificates[0].publicCertData'),
                     self.exists('vpnClientRevokedCertificates[0].thumbprint'),
                     self.check('vpnAuthenticationTypes[0]', 'Certificate')
                 ])

        self.cmd('network vpn-server-config set -n {vserverconfig} -g {rg} --auth-types Radius '
                 '--radius-client-root-certs "{cert_file}" '
                 '--radius-server-root-certs "{pem_file}" '
                 '--radius-servers address=test1 secret=clitest score=10 '
                 '--radius-servers address=test2 secret=clitest score=10')

        self.cmd('network vpn-server-config wait -n {vserverconfig} -g {rg} --created')
        self.cmd('network vpn-server-config set -n {vserverconfig} -g {rg} --auth-types AAD '
                 '--aad-audience {aad_audience} '
                 '--aad-issuer {aad_issuer} '
                 '--aad-tenant {aad_tenant} '
                 '--no-wait')

        self.cmd('network vpn-server-config wait -n {vserverconfig} -g {rg} --created')

        self.cmd('network vpn-server-config show -n {vserverconfig} -g {rg}', checks=[
            self.check('vpnAuthenticationTypes[0]', 'AAD'),
            self.check('aadAuthenticationParameters.aadTenant', '{aad_tenant}'),
            self.check('aadAuthenticationParameters.aadAudience', '{aad_audience}'),
            self.check('aadAuthenticationParameters.aadIssuer', '{aad_issuer}')
        ])

        self.cmd('network vpn-server-config list -g {rg}', checks=[
            self.check('length(@)', 1)
        ])

        self.cmd('network vpn-server-config ipsec-policy add -n {vserverconfig} -g {rg} '
                 '--ipsec-encryption AES256 --ipsec-integrity SHA256 '
                 '--sa-lifetime 86471 --sa-data-size 429496 --ike-encryption AES256 '
                 '--ike-integrity SHA384 --dh-group DHGroup14 --pfs-group PFS14',
                 checks=[
                     self.check('@[0].saLifeTimeSeconds', 86471),
                     self.check('@[0].saDataSizeKilobytes', 429496),
                     self.check('@[0].ipsecEncryption', 'AES256'),
                     self.check('@[0].ipsecIntegrity', 'SHA256'),
                     self.check('@[0].ikeEncryption', 'AES256'),
                     self.check('@[0].ikeIntegrity', 'SHA384'),
                     self.check('@[0].dhGroup', 'DHGroup14'),
                     self.check('@[0].pfsGroup', 'PFS14')
                 ])

        self.cmd('network vpn-server-config ipsec-policy list -n {vserverconfig} -g {rg}', checks=[
            self.check('length(@)', 1)
        ])

        self.cmd('network vpn-server-config ipsec-policy remove -n {vserverconfig} -g {rg} --index 0')

        self.cmd('network vpn-server-config ipsec-policy add -n {vserverconfig} -g {rg} '
                 '--ipsec-encryption AES256 --ipsec-integrity SHA256 '
                 '--sa-lifetime 86471 --sa-data-size 429496 --ike-encryption AES256 '
                 '--ike-integrity SHA384 --dh-group DHGroup14 --pfs-group PFS14',
                 checks=[
                     self.check('@[0].saLifeTimeSeconds', 86471),
                     self.check('@[0].saDataSizeKilobytes', 429496),
                     self.check('@[0].ipsecEncryption', 'AES256'),
                     self.check('@[0].ipsecIntegrity', 'SHA256'),
                     self.check('@[0].ikeEncryption', 'AES256'),
                     self.check('@[0].ikeIntegrity', 'SHA384'),
                     self.check('@[0].dhGroup', 'DHGroup14'),
                     self.check('@[0].pfsGroup', 'PFS14')
                 ])

        self.cmd('network vpn-server-config ipsec-policy list -n {vserverconfig} -g {rg}', checks=[
            self.check('length(@)', 1)
        ])

        self.cmd('network vpn-server-config delete -n {vserverconfig} -g {rg} -y')
        with self.assertRaisesRegexp(SystemExit, '3'):
            self.cmd('network vpn-server-config show -n {vserverconfig} -g {rg}')

    @ResourceGroupPreparer(name_prefix='cli_test_azure_p2s_vpn_gateway', location='westcentralus')
    def test_azure_p2s_vpn_gateway_basic_scenario(self, resource_group):
        self.kwargs.update({
            'vwan': 'clitestvwan',
            'vwan2': 'clitestvwan2',
            'vhub': 'clitestvhub',
            'vhub2': 'clitestvhub2',
            'cert_file': os.path.join(TEST_DIR, 'data', 'ApplicationGatewayAuthCert.cer'),
            'pem_file': os.path.join(TEST_DIR, 'data', 'ApplicationGatewayAuthCert.pem'),
            'vserverconfig': 'clitestserverconfig',
            'vserverconfig2': 'clitestserverconfig2',
            'vp2sgateway': 'clitestvp2sgateway',
            'rg': resource_group
        })

        self.cmd('network vwan create -n {vwan} -g {rg} --type Standard')
        self.cmd('network vhub create -g {rg} -n {vhub} --vwan {vwan}  --address-prefix 10.5.0.0/16 -l westcentralus --sku Standard')
        self.cmd('network vpn-server-config create -n {vserverconfig} -g {rg} '
                 '--vpn-client-root-certs "{cert_file}" '
                 '--vpn-client-revoked-certs "{pem_file}"')
        self.cmd('network vpn-server-config create -n {vserverconfig2} -g {rg} '
                 '--vpn-client-root-certs "{cert_file}" '
                 '--vpn-client-revoked-certs "{pem_file}"')
        self.cmd('az network p2s-vpn-gateway create -g {rg} -n {vp2sgateway} --scale-unit 2 '
                 '--vhub {vhub} --vpn-server-config {vserverconfig} --address-space 10.0.0.0/24 11.0.0.0/24 --no-wait')
        self.cmd('az network p2s-vpn-gateway wait -g {rg} -n {vp2sgateway} --created')
        self.cmd('az network p2s-vpn-gateway update -g {rg} -n {vp2sgateway} --scale-unit 3 '
                 '--vpn-server-config {vserverconfig2} --address-space 13.0.0.0/24 12.0.0.0/24')
        self.cmd('az network p2s-vpn-gateway list -g {rg}', checks=[
            self.check('length(@)', 1)
        ])
        self.cmd('az network p2s-vpn-gateway show -g {rg} -n {vp2sgateway}', checks=[
            self.check('length(p2SconnectionConfigurations[0].vpnClientAddressPool.addressPrefixes)', 2),
            self.check('vpnGatewayScaleUnit', 3)
        ])
        self.cmd('az network p2s-vpn-gateway delete -g {rg} -n {vp2sgateway} -y')
        with self.assertRaisesRegexp(SystemExit, '3'):
            self.cmd('az network p2s-vpn-gateway show -g {rg} -n {vp2sgateway}')

    @ResourceGroupPreparer(name_prefix='cli_test_azure_vwan_vpn_gateway', location='westus')
    def test_azure_vwan_vpn_gateway(self, resource_group):
        from knack.util import CLIError
        self.kwargs.update({
            'vwan': 'testvwan',
            'vhub': 'myclitestvhub',
            'vpngateway': 'mycligateway',
            'routetable': 'testroutetable',
            'rg': resource_group
        })

        # workaround due to service limitation. It should be fixed in the future.
        self.cmd('network vwan create -n {vwan} -g {rg}')
        self.cmd('network vhub create -g {rg} -n {vhub} --vwan {vwan}  --address-prefix 10.0.0.0/24 -l westus')
        self.cmd('network vpn-gateway create -n {vpngateway} -g {rg} --vhub {vhub} -l westus')
        with self.assertRaisesRegexp(CLIError, 'VPN gateway already exist'):
            self.cmd('network vpn-gateway create -n {vpngateway} -g {rg} --vhub {vhub} -l westus')
        self.cmd('network vpn-gateway show -n {vpngateway} -g {rg}')
        self.cmd('network vpn-gateway list -g {rg}')
        self.cmd('network vpn-gateway list')
        self.cmd('network vpn-gateway delete -n {vpngateway} -g {rg}')

    @record_only()
    @ResourceGroupPreparer(name_prefix='cli_test_azure_vwan_vpn_gateway_connection', location='westus')
    def test_azure_vwan_vpn_gateway_connection(self):
        self.kwargs.update({
            'vpngateway': 'yu-vpn-gateway-eastus',
            'connection': 'yu-vpn-connection-westus',
            'vpn_site': '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/azure-cli-test-rg/providers/Microsoft.Network/vpnSites/yu-vpn-site-westus',
            'route_table1': '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/azure-cli-test-rg/providers/Microsoft.Network/virtualHubs/yu-vhub/hubRouteTables/yu-routetable-no-route',
            'route_table2': '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/azure-cli-test-rg/providers/Microsoft.Network/virtualHubs/yu-vhub/hubRouteTables/yu-routetable-no-route1',
            'rg': 'azure-cli-test-rg'
        })

        self.cmd('network vpn-gateway connection create '
                 '-g {rg} '
                 '-n {connection} '
                 '--gateway-name {vpngateway} '
                 '--remote-vpn-site {vpn_site} '
                 '--associated-route-table {route_table1} '
                 '--propagated-route-tables {route_table1} {route_table2} '
                 '--labels label1 label2',
                 checks=[
                     self.check('provisioningState', 'Succeeded'),
                     self.check('name', self.kwargs['vpngateway']),
                     self.check('connections[0].name', self.kwargs['connection']),
                     self.check('connections[0].routingConfiguration.associatedRouteTable.id', self.kwargs['route_table1']),
                     self.check('length(connections[0].routingConfiguration.propagatedRouteTables.ids)', 2),
                     self.check('connections[0].routingConfiguration.propagatedRouteTables.ids[0].id', self.kwargs['route_table1']),
                     self.check('connections[0].routingConfiguration.propagatedRouteTables.ids[1].id', self.kwargs['route_table2']),
                     self.check('length(connections[0].routingConfiguration.propagatedRouteTables.labels)', 2),
                     self.check('connections[0].routingConfiguration.propagatedRouteTables.labels[0]', 'label1'),
                     self.check('connections[0].routingConfiguration.propagatedRouteTables.labels[1]', 'label2')
                 ])

        self.cmd('network vpn-gateway connection show '
                 '-g {rg} '
                 '-n {connection} '
                 '--gateway-name {vpngateway}',
                 checks=[
                     self.check('provisioningState', 'Succeeded'),
                     self.check('name', self.kwargs['connection']),
                     self.check('routingConfiguration.associatedRouteTable.id', self.kwargs['route_table1']),
                     self.check('length(routingConfiguration.propagatedRouteTables.ids)', 2),
                     self.check('routingConfiguration.propagatedRouteTables.ids[0].id', self.kwargs['route_table1']),
                     self.check('routingConfiguration.propagatedRouteTables.ids[1].id', self.kwargs['route_table2']),
                     self.check('length(routingConfiguration.propagatedRouteTables.labels)', 2),
                     self.check('routingConfiguration.propagatedRouteTables.labels[0]', 'label1'),
                     self.check('routingConfiguration.propagatedRouteTables.labels[1]', 'label2')
                 ])

        self.cmd('network vpn-gateway connection list '
                 '-g {rg} '
                 '--gateway-name {vpngateway}',
                 checks=[
                     self.check('length(@)', 1)
                 ])

        self.cmd('network vpn-gateway connection delete '
                 '-g {rg} '
                 '-n {connection} '
                 '--gateway-name {vpngateway}',
                 checks=[])

        from knack.util import CLIError
        with self.assertRaisesRegexp(CLIError, 'does not exist on vpn_gateways'):
            self.cmd('network vpn-gateway connection show '
                     '-g {rg} '
                     '-n {connection} '
                     '--gateway-name {vpngateway}')

    @record_only()
    @ResourceGroupPreparer(name_prefix='cli_test_azure_vwan_p2s_gateway_routing_configuration', location='westus')
    def test_azure_vwan_p2s_gateway_routing_configuration(self):
        self.kwargs.update({
            'vhub': 'yu-vhub1',
            'gateway': 'p2svpngateway',
            'scale_unit': 2,
            'location': 'eastus',
            'address_space': '10.40.0.0/24 10.42.0.0/24',
            'connection_config': 'myconnectionconfig',
            'vpn_server_config': 'vsc1',
            'route_table1': '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/azure-cli-test-rg/providers/Microsoft.Network/virtualHubs/yu-vhub/hubRouteTables/yu-routetable-no-route',
            'route_table2': '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/azure-cli-test-rg/providers/Microsoft.Network/virtualHubs/yu-vhub/hubRouteTables/yu-routetable-no-route1',
            'rg': 'azure-cli-test-rg'
        })

        self.cmd('network p2s-vpn-gateway create '
                 '-g {rg} '
                 '-n {gateway} '
                 '--vhub {vhub} '
                 '--config-name {connection_config} '
                 '--scale-unit 2 '
                 '-l {location} '
                 '--address-space {address_space} '
                 '--vpn-server-config {vpn_server_config} '
                 '--associated-route-table {route_table1} '
                 '--propagated-route-tables {route_table1} {route_table2} '
                 '--labels label1 label2',
                 checks=[
                     self.check('provisioningState', 'Succeeded'),
                     self.check('name', self.kwargs['gateway']),
                     self.check('p2SconnectionConfigurations[0].name', self.kwargs['connection_config']),
                     self.check('p2SconnectionConfigurations[0].routingConfiguration.associatedRouteTable.id', self.kwargs['route_table1']),
                     self.check('length(p2SconnectionConfigurations[0].routingConfiguration.propagatedRouteTables.ids)', 2),
                     self.check('p2SconnectionConfigurations[0].routingConfiguration.propagatedRouteTables.ids[0].id', self.kwargs['route_table1']),
                     self.check('p2SconnectionConfigurations[0].routingConfiguration.propagatedRouteTables.ids[1].id', self.kwargs['route_table2']),
                     self.check('length(p2SconnectionConfigurations[0].routingConfiguration.propagatedRouteTables.labels)', 2),
                     self.check('p2SconnectionConfigurations[0].routingConfiguration.propagatedRouteTables.labels[0]', 'label1'),
                     self.check('p2SconnectionConfigurations[0].routingConfiguration.propagatedRouteTables.labels[1]', 'label2')
                 ])

        self.cmd('network p2s-vpn-gateway connection show '
                 '-g {rg} '
                 '-n {connection_config} '
                 '--gateway-name {gateway}',
                 checks=[
                     self.check('provisioningState', 'Succeeded'),
                     self.check('name', self.kwargs['connection_config']),
                     self.check('routingConfiguration.associatedRouteTable.id', self.kwargs['route_table1']),
                     self.check('length(routingConfiguration.propagatedRouteTables.ids)', 2),
                     self.check('routingConfiguration.propagatedRouteTables.ids[0].id', self.kwargs['route_table1']),
                     self.check('routingConfiguration.propagatedRouteTables.ids[1].id', self.kwargs['route_table2']),
                     self.check('length(routingConfiguration.propagatedRouteTables.labels)', 2),
                     self.check('routingConfiguration.propagatedRouteTables.labels[0]', 'label1'),
                     self.check('routingConfiguration.propagatedRouteTables.labels[1]', 'label2')
                 ])

        self.cmd('network p2s-vpn-gateway connection list '
                 '-g {rg} '
                 '--gateway-name {gateway}',
                 checks=[
                     self.check('length(@)', 1)
                 ])
