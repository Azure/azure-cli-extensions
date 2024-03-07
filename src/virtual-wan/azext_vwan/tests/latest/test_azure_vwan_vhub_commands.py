# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import time

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, VirtualNetworkPreparer, record_only)
from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from .credential_replacer import VpnClientGeneratedURLReplacer

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
        self.cmd(
            'network vhub create -g {rg} -n {vhub} --vwan {vwan} --address-prefix 10.0.0.0/24 -l SouthCentralUS '
            '--sku Standard --hub-routing-preference ExpressRoute --asn 65515',
            checks=[
                self.check('sku', 'Standard'),
                self.check('hubRoutingPreference', 'ExpressRoute'),
                self.check('virtualRouterAsn', 65515)
            ]
        )
        self.cmd(
            'network vhub update -g {rg} -n {vhub} --sku Basic --hub-routing-preference VpnGateway --asn 65515',
            checks=[
                self.check('sku', 'Basic'),
                self.check('hubRoutingPreference', 'VpnGateway'),
                self.check('virtualRouterAsn', 65515)
            ]
        )
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
        # self.cmd('network vhub route reset -g {rg} --vhub-name {vhub}', checks=[
        #     self.check('@[0].addressPrefixes[0]', '10.3.3.0/28'),
        #     self.check('@[0].nextHopIpAddress', '10.0.0.7')
        # ])

    @ResourceGroupPreparer(name_prefix='cli_test_azure_vhub_connection')
    @VirtualNetworkPreparer()
    def test_azure_vhub_connection_basic_scenario(self, virtual_network, resource_group):
        self.kwargs.update({
            'vnet': virtual_network,
            'vwan': 'clitestvwan2',
            'vhub': 'clitestvhub2',
            'connection': 'clitestvhubconnection2',
            'rg': resource_group
        })

        self.cmd('network vwan create -n {vwan} -g {rg} --type Standard')
        self.cmd('network vhub create -g {rg} -n {vhub} --vwan {vwan}  --address-prefix 10.5.0.0/16 -l westus --sku Standard')
        self.cmd('network vhub connection create -g {rg} --vhub-name {vhub} --name {connection} --remote-vnet {vnet}', checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('name', self.kwargs.get('connection'))
        ])
        self.cmd('network vhub connection list -g {rg} --vhub-name {vhub}', checks=self.check('length(@)', 1))
        self.cmd('network vhub connection show -g {rg} --vhub-name {vhub} --name {connection}')
        self.cmd('network vhub connection update -g {rg} --vhub-name {vhub} --name {connection} --labels x1 x2',
                 checks=self.check('length(routingConfiguration.propagatedRouteTables.labels)', 2))
        self.cmd('network vhub connection delete -g {rg} --vhub-name {vhub} --name {connection} -y')
        self.cmd('network vhub connection list -g {rg} --vhub-name {vhub}', checks=self.check('length(@)', 0))

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

        self.cmd('network vpn-server-config list', checks=[])

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

    @ResourceGroupPreparer(name_prefix='test_azure_vpn_server_config_multi_auth', location='westcentralus')
    def test_azure_vpn_server_config_multi_auth(self, resource_group):
        self.kwargs.update({
            'vserverconfig': 'clitestserverconfig',
            'vserverconfig1': 'clitestserverconfig1',
            'cert_file': os.path.join(TEST_DIR, 'data', 'ApplicationGatewayAuthCert.cer'),
            'pem_file': os.path.join(TEST_DIR, 'data', 'ApplicationGatewayAuthCert.pem'),
            'rg': resource_group,
            'aad_tenant': 'https://login.microsoftonline.com/0ab2c4f4-81e6-44cc-a0b2-b3a47a1443f4',
            'aad_issuer': 'https://sts.windows.net/0ab2c4f4-81e6-44cc-a0b2-b3a47a1443f4/',
            'aad_audience': 'a21fce82-76af-45e6-8583-a08cb3b956f9'
        })

        self.cmd('network vpn-server-config create -n {vserverconfig} -g {rg} '
                 '--vpn-client-root-certs "{cert_file}" --vpn-client-revoked-certs "{pem_file}" '
                 '--radius-servers address=test1 secret=clitest score=10 '
                 '--radius-servers address=test2 secret=clitest score=10 '
                 '--aad-audience {aad_audience} '
                 '--aad-issuer {aad_issuer} '
                 '--aad-tenant {aad_tenant} '
                 '--auth-types Radius AAD Certificate --protocols OpenVPN',
                 checks=[
                     self.check('name', '{vserverconfig}'),
                     self.exists('vpnClientRootCertificates[0].publicCertData'),
                     self.exists('vpnClientRevokedCertificates[0].thumbprint'),
                     self.check('length(vpnAuthenticationTypes)', 3),
                     self.check('length(radiusServers)', 2),
                     self.check('aadAuthenticationParameters.aadAudience', '{aad_audience}')
                 ])

        self.cmd('network vpn-server-config create -n {vserverconfig1} -g {rg} '
                 '--vpn-client-root-certs "{cert_file}" --vpn-client-revoked-certs "{pem_file}" ')

        self.cmd('network vpn-server-config set -n {vserverconfig1} -g {rg} '
                 '--vpn-client-root-certs "{cert_file}" --vpn-client-revoked-certs "{pem_file}" '
                 '--radius-servers address=test1 secret=clitest score=10 '
                 '--radius-servers address=test2 secret=clitest score=10 '
                 '--aad-audience {aad_audience} '
                 '--aad-issuer {aad_issuer} '
                 '--aad-tenant {aad_tenant} '
                 '--auth-types Radius AAD Certificate --protocols OpenVPN',
                 checks=[
                     self.check('name', '{vserverconfig1}'),
                     self.check('length(vpnClientRootCertificates)', 1),
                     self.check('length(vpnClientRevokedCertificates)', 1),
                     self.check('length(vpnAuthenticationTypes)', 3),
                     self.check('length(radiusServers)', 2),
                     self.check('aadAuthenticationParameters.aadAudience', '{aad_audience}')
                 ])

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
                 '--vpn-server-config {vserverconfig2} --address-space 13.0.0.0/24 12.0.0.0/24 --labels x1 x2 x3',
                 checks=self.check(
                     'length(p2SConnectionConfigurations[0].routingConfiguration.propagatedRouteTables.labels)', 3))
        self.cmd('az network p2s-vpn-gateway list -g {rg}', checks=[
            self.check('length(@)', 1)
        ])
        self.cmd('az network p2s-vpn-gateway list', checks=[])
        self.cmd('az network p2s-vpn-gateway show -g {rg} -n {vp2sgateway}', checks=[
            self.check('length(p2SConnectionConfigurations[0].vpnClientAddressPool.addressPrefixes)', 2),
            self.check('vpnGatewayScaleUnit', 3)
        ])
        # test disconnect P2S vpn connections
        vpn_id = self.cmd('az network p2s-vpn-gateway connection list -g {rg} --gateway-name {vp2sgateway}').get_output_in_json()
        self.kwargs.update({'vpn_connection': vpn_id[0]['id']})
        self.cmd('az network p2s-vpn-gateway disconnect -g {rg} -n {vp2sgateway} --vpn-connection-ids {vpn_connection}')
        # test resets the primary of the p2s vpn gateway
        self.cmd('az network p2s-vpn-gateway reset -g {rg} -n {vp2sgateway}')
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
        self.cmd('network vpn-gateway show -n {vpngateway} -g {rg}')
        self.cmd('network vpn-gateway list -g {rg}')
        self.cmd('network vpn-gateway list')
        self.cmd('network vpn-gateway delete -n {vpngateway} -g {rg}')

    @ResourceGroupPreparer(name_prefix='cli_test_azure_vwan_vpn_gateway_connection', location='westus')
    def test_azure_vwan_vpn_gateway_connection(self):
        self.kwargs.update({
            'vwan': 'test_vwan',
            'vhub': 'test_vhub',
            'vpngateway': 'test_s2s_vpn_gateway',
            'connection': 'test_s2s_vpn_gateway_connection',
            'vpn_site': 'remote_vpn_site_1',
        })

        self.cmd('network vwan create -g {rg} -n {vwan}')

        self.cmd('network vhub create -g {rg} -n {vhub} --vwan {vwan} --address-prefix 10.0.1.0/24')

        self.cmd('network vpn-gateway create -g {rg} --vhub {vhub} --name {vpngateway}')

        self.cmd('network vpn-site create -g {rg} -n {vpn_site} --ip-address 10.0.2.110 --address-prefixes 10.0.2.0/24')

        self.cmd('network vpn-gateway connection create '
                 '-g {rg} '
                 '-n {connection} '
                 '--gateway-name {vpngateway} '
                 '--remote-vpn-site {vpn_site} ',
                 checks=[
                     self.check('provisioningState', 'Succeeded'),
                     self.check('name', self.kwargs['connection']),
                 ])

        self.cmd('network vpn-gateway connection show '
                 '-g {rg} '
                 '-n {connection} '
                 '--gateway-name {vpngateway}',
                 checks=[
                     self.check('provisioningState', 'Succeeded'),
                     self.check('name', self.kwargs['connection'])
                 ])

        self.cmd('network vpn-gateway connection list -g {rg} --gateway-name {vpngateway}',
                 checks=[
                     self.check('length(@)', 1)
                 ])

        self.cmd('network vpn-gateway connection update -g {rg} --gateway-name {vpngateway} -n {connection} --labels x1 x2')

        self.cmd('network vpn-gateway connection packet-capture start -g {rg} --gateway-name {vpngateway} --connection-name {connection} --link-connection-names {connection}')

        self.cmd('network vpn-gateway connection delete '
                 '-g {rg} '
                 '-n {connection} '
                 '--gateway-name {vpngateway}')

        with self.assertRaisesRegexp(SystemExit, '3'):
            self.cmd('network vpn-gateway connection show '
                     '-g {rg} '
                     '-n {connection} '
                     '--gateway-name {vpngateway}')

    @ResourceGroupPreparer(name_prefix='cli_test_azure_vwan_vpn_gateway_connection_vpn_site_link', location='westus')
    def test_azure_vwan_vpn_gateway_connection_vpn_site_link(self):
        self.kwargs.update({
            'vwan': 'test_vwan',
            'vhub': 'test_vhub',
            'vpngateway': 'test_s2s_vpn_gateway',
            'connection': 'test_s2s_vpn_gateway_connection',
            'vpn_site': 'remote_vpn_site_1',
            'vpn_site_link_conn': 'Connection-Link1',
            'vpn_site_link_name': 'VPN-Site-Link1',
            'vpn_site_link_2_name': 'VPN-Site-Link2',
            'sub': '/subscriptions/{}'.format(self.get_subscription_id())
        })

        self.cmd('network vwan create -g {rg} -n {vwan}')

        self.cmd('network vhub create -g {rg} -n {vhub} --vwan {vwan} --address-prefix 10.0.1.0/24')

        self.cmd('network vpn-gateway create -g {rg} --vhub {vhub} --name {vpngateway}')

        # Test vpn site with links
        self.cmd('network vpn-site create -g {rg} -n {vpn_site} --ip-address 10.0.2.110 --address-prefixes 10.0.2.0/24')
        with self.assertRaisesRegexp(HttpResponseError, 'MissingDefaultLinkForVpnSiteDuringMigrationToLinkFormat'):
            self.cmd('network vpn-site link add -g {rg} --site-name {vpn_site} -n {vpn_site_link_name} --ip-address 10.0.1.111 --asn 1234 --bgp-peering-address 192.168.0.0')
        # Test ipsec policy
        self.cmd('network vpn-gateway connection create '
                 '-g {rg} '
                 '-n {connection} '
                 '--gateway-name {vpngateway} '
                 '--remote-vpn-site {sub}/resourceGroups/{rg}/providers/Microsoft.Network/vpnSites/{vpn_site}')
        self.cmd('network vpn-gateway connection ipsec-policy add -g {rg} --gateway-name {vpngateway} --connection-name {connection} --ipsec-encryption AES256 --ipsec-integrity SHA256 --sa-lifetime 86471 --sa-data-size 429496 --ike-encryption AES256 --ike-integrity SHA384 --dh-group DHGroup14 --pfs-group PFS14')
        self.cmd('network vpn-gateway connection ipsec-policy list -g {rg} --gateway-name {vpngateway} --connection-name {connection}')
        self.cmd('network vpn-gateway connection ipsec-policy remove -g {rg} --gateway-name {vpngateway} --connection-name {connection} --index 1')
        self.cmd('network vpn-gateway connection delete -g {rg} -n {connection} --gateway-name {vpngateway}')
        self.cmd('network vpn-site delete -g {rg} -n {vpn_site}')

        self.cmd('network vpn-site create -g {rg} -n {vpn_site} --ip-address 10.0.4.110 --with-link --address-prefixes 10.0.4.0/24')
        self.cmd('network vpn-site link add -g {rg} --site-name {vpn_site} -n {vpn_site_link_name} --ip-address 10.0.4.111 --asn 1234 --bgp-peering-address 192.168.1.0')
        self.cmd('network vpn-site link add -g {rg} --site-name {vpn_site} -n {vpn_site_link_2_name} --ip-address 10.0.4.112 --asn 1234 --bgp-peering-address 192.168.2.0')
        self.cmd('network vpn-site link list -g {rg} --site-name {vpn_site}')
        self.cmd('network vpn-site link remove -g {rg} --site-name {vpn_site} --index 2')

    @ResourceGroupPreparer(name_prefix='cli_test_azure_vwan_vpn_gateway_connection_vpn_site_link_conn', location='westus')
    def test_azure_vwan_vpn_gateway_connection_vpn_site_link_conn(self):
        self.kwargs.update({
            'vwan': 'test_vwan',
            'vhub': 'test_vhub',
            'vpngateway': 'test_s2s_vpn_gateway',
            'connection': 'test_s2s_vpn_gateway_connection',
            'vpn_site': 'remote_vpn_site_1',
            'vpn_site_link_conn': 'Connection-Link1',
            'vpn_site_link_name': 'VPN-Site-Link1',
            'vpn_site_link_2_name': 'VPN-Site-Link2',
            'sub': '/subscriptions/{}'.format(self.get_subscription_id())
        })

        self.cmd('network vwan create -g {rg} -n {vwan}')

        self.cmd('network vhub create -g {rg} -n {vhub} --vwan {vwan} --address-prefix 10.0.1.0/24')

        self.cmd('network vpn-gateway create -g {rg} --vhub {vhub} --name {vpngateway}')

        self.cmd('network vpn-site create -g {rg} -n {vpn_site} --ip-address 10.0.2.110 --with-link --address-prefixes 10.0.2.0/24')
        self.cmd('network vpn-site link add -g {rg} --site-name {vpn_site} -n {vpn_site_link_name} --ip-address 10.0.2.111 --asn 1234 --bgp-peering-address 192.168.1.0')

        # Test vpn gateway connection with links
        self.cmd('network vpn-gateway connection create '
                 '-g {rg} '
                 '-n {connection} '
                 '--gateway-name {vpngateway} '
                 '--remote-vpn-site {sub}/resourceGroups/{rg}/providers/Microsoft.Network/vpnSites/{vpn_site} '
                 '--vpn-site-link "{sub}/resourceGroups/{rg}/providers/Microsoft.Network/vpnSites/{vpn_site}/vpnSiteLinks/{vpn_site}" '
                 '--with-link')

        self.cmd('network vpn-gateway connection vpn-site-link-conn add '
                 '-g {rg} '
                 '--connection-name {connection} '
                 '--gateway-name {vpngateway} '
                 '-n {vpn_site_link_conn} '
                 '--vpn-site-link "{sub}/resourceGroups/{rg}/providers/Microsoft.Network/vpnSites/{vpn_site}/vpnSiteLinks/{vpn_site_link_name}" '
                 '--vpn-connection-protocol-type IKEv2')

        self.cmd('network vpn-gateway connection vpn-site-link-conn list '
                 '-g {rg} '
                 '--connection-name {connection} '
                 '--gateway-name {vpngateway}')

        self.cmd('network vpn-gateway connection vpn-site-link-conn remove '
                 '-g {rg} '
                 '--connection-name {connection} '
                 '--gateway-name {vpngateway} '
                 '--index 2')

    @ResourceGroupPreparer(name_prefix='cli_test_azure_vwan_vpn_site_link_conn_ipsec_policy', location='westus')
    def test_azure_vwan_vpn_site_link_conn_ipsec_policy(self):
        self.kwargs.update({
            'vwan': 'test_vwan',
            'vhub': 'test_vhub',
            'vpngateway': 'test_s2s_vpn_gateway',
            'connection': 'test_s2s_vpn_gateway_connection',
            'vpn_site': 'remote_vpn_site_1',
            'vpn_site_link_conn': 'Connection-Link1',
            'vpn_site_link_name': 'VPN-Site-Link1',
            'vpn_site_link_2_name': 'VPN-Site-Link2',
            'sub': '/subscriptions/{}'.format(self.get_subscription_id())
        })

        self.cmd('network vwan create -g {rg} -n {vwan}')

        self.cmd('network vhub create -g {rg} -n {vhub} --vwan {vwan} --address-prefix 10.0.1.0/24')

        self.cmd('network vpn-gateway create -g {rg} --vhub {vhub} --name {vpngateway}',
                 checks=[])

        self.cmd('network vpn-site create -g {rg} -n {vpn_site} --ip-address 10.0.2.110 --with-link --address-prefixes 10.0.2.0/24')
        self.cmd('network vpn-site link add -g {rg} --site-name {vpn_site} -n {vpn_site_link_name} --ip-address 10.0.2.111 --asn 1234 --bgp-peering-address 192.168.1.0')

        # Test vpn gateway connection with links
        self.cmd('network vpn-gateway connection create '
                 '-g {rg} '
                 '-n {connection} '
                 '--gateway-name {vpngateway} '
                 '--remote-vpn-site {sub}/resourceGroups/{rg}/providers/Microsoft.Network/vpnSites/{vpn_site} '
                 '--vpn-site-link "{sub}/resourceGroups/{rg}/providers/Microsoft.Network/vpnSites/{vpn_site}/vpnSiteLinks/{vpn_site}" '
                 '--with-link')

        # Test issue:
        # Ipsec policy setted on conneciton will fail due to multi-links on connection
        with self.assertRaisesRegexp(HttpResponseError, 'VpnConnectionPropertyIsDeprecated'):
            self.cmd('network vpn-gateway connection ipsec-policy add -g {rg} --gateway-name {vpngateway} --connection-name {connection} '
                     '--ipsec-encryption AES256 --ipsec-integrity SHA256 --sa-lifetime 86471 --sa-data-size 429496 --ike-encryption AES256 '
                     '--ike-integrity SHA384 --dh-group DHGroup14 --pfs-group PFS14')

        # Test link-conn ipsec policy
        self.cmd('network vpn-gateway connection vpn-site-link-conn ipsec-policy add -g {rg} --gateway-name {vpngateway} --connection-name {connection} '
                 '-n {connection} --ipsec-encryption AES256 --ipsec-integrity SHA256 --sa-lifetime 86471 '
                 '--sa-data-size 429496 --ike-encryption AES256 --ike-integrity SHA384 --dh-group DHGroup14 --pfs-group PFS14')
        self.cmd('network vpn-gateway connection vpn-site-link-conn ipsec-policy list -g {rg} --gateway-name {vpngateway} --connection-name {connection} -n {connection}')
        self.cmd('network vpn-gateway connection vpn-site-link-conn ipsec-policy remove -g {rg} --gateway-name {vpngateway} --connection-name {connection} -n {connection} --index 1')

    @ResourceGroupPreparer(name_prefix='cli_test_azure_vwan_vhub_bgpconnection', location='westus')
    @VirtualNetworkPreparer()
    def test_azure_vwan_vhub_bgpconnection(self, virtual_network, resource_group):
        self.kwargs.update({
            'vnet': virtual_network,
            'vwan': 'testvwan',
            'vhub': 'myclitestvhub',
            'conn': 'myconnection',
            'vhub_conn': 'clitestvhubconnection2',
            'rg': resource_group,
            'sub': '/subscriptions/{}'.format(self.get_subscription_id())
        })

        self.cmd('network vwan create -n {vwan} -g {rg} --type Standard')
        self.cmd('network vhub create -g {rg} -n {vhub} --vwan {vwan}  --address-prefix 10.5.0.0/16 -l westus --sku Standard')
        self.cmd('network vhub connection create -g {rg} --vhub-name {vhub} --name {vhub_conn} --remote-vnet {vnet}', checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('name', self.kwargs.get('vhub_conn'))
        ])

        vhub = self.cmd('network vhub show -g {rg} -n {vhub}').get_output_in_json()
        while (vhub['routingState'] != 'Provisioned'):
            time.sleep(300)
            vhub = self.cmd('network vhub show -g {rg} -n {vhub}').get_output_in_json()

        self.cmd('network vhub bgpconnection create -n {conn} -g {rg} --vhub-name {vhub} --peer-asn 20000  --peer-ip "10.0.0.3" '
                 '--vhub-conn {sub}/resourceGroups/{rg}/providers/Microsoft.Network/virtualHubs/{vhub}/hubVirtualNetworkConnections/{vhub_conn}')
        self.cmd('network vhub bgpconnection list -g {rg} --vhub-name {vhub}')

        # HubBgpConnectionPeerIpCannotBeUpdated and HubBgpConnectionPeerASNCannotBeUpdated
        # self.cmd('network vhub bgpconnection update -n {conn} -g {rg} --vhub-name {vhub} --peer-ip "10.5.0.4"')

        self.cmd('network vhub bgpconnection show -n {conn} -g {rg} --vhub-name {vhub}')
        self.cmd('network vhub bgpconnection delete -n {conn} -g {rg} --vhub-name {vhub} -y')

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
                     self.check('p2SConnectionConfigurations[0].name', self.kwargs['connection_config']),
                     self.check('p2SConnectionConfigurations[0].routingConfiguration.associatedRouteTable.id', self.kwargs['route_table1']),
                     self.check('length(p2SConnectionConfigurations[0].routingConfiguration.propagatedRouteTables.ids)', 2),
                     self.check('p2SConnectionConfigurations[0].routingConfiguration.propagatedRouteTables.ids[0].id', self.kwargs['route_table1']),
                     self.check('p2SConnectionConfigurations[0].routingConfiguration.propagatedRouteTables.ids[1].id', self.kwargs['route_table2']),
                     self.check('length(p2SConnectionConfigurations[0].routingConfiguration.propagatedRouteTables.labels)', 2),
                     self.check('p2SConnectionConfigurations[0].routingConfiguration.propagatedRouteTables.labels[0]', 'label1'),
                     self.check('p2SConnectionConfigurations[0].routingConfiguration.propagatedRouteTables.labels[1]', 'label2')
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

    @record_only()
    @ResourceGroupPreparer(name_prefix='cli_test_azure_vwan_vhub_connection_routing_configuration', location='westus')
    def test_azure_vwan_vhub_connection_routing_configuration(self):
        self.kwargs.update({
            'rg': 'azure-cli-test-rg',
            'connection': 'my-connection',
            'vhub': 'yu-vhub',
            'vnet': 'test-vnet',
            'route_table1': '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/azure-cli-test-rg/providers/Microsoft.Network/virtualHubs/yu-vhub/hubRouteTables/yu-routetable-no-route',
            'route_table2': '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/azure-cli-test-rg/providers/Microsoft.Network/virtualHubs/yu-vhub/hubRouteTables/yu-routetable-no-route1',
            'route': 'route1',
            'next_hop': '70.0.0.2',
            'address_prefixes': '10.80.0.0/16 10.90.0.0/16'
        })

        # You need to create a virtual hub and a vnet before running the following commands.
        self.cmd('network vhub connection create '
                 '-g {rg} '
                 '-n {connection} '
                 '--vhub-name {vhub} '
                 '--remote-vnet {vnet} '
                 '--associated-route-table {route_table1} '
                 '--propagated-route-tables {route_table1} {route_table2} '
                 '--labels label1 label2 '
                 '--route-name {route} '
                 '--next-hop {next_hop} '
                 '--address-prefixes {address_prefixes}',
                 checks=[
                     self.check('provisioningState', 'Succeeded'),
                     self.check('name', self.kwargs['connection']),
                     self.check('routingConfiguration.associatedRouteTable.id', self.kwargs['route_table1']),
                     self.check('length(routingConfiguration.propagatedRouteTables.ids)', 2),
                     self.check('routingConfiguration.propagatedRouteTables.ids[0].id', self.kwargs['route_table1']),
                     self.check('routingConfiguration.propagatedRouteTables.ids[1].id', self.kwargs['route_table2']),
                     self.check('length(routingConfiguration.propagatedRouteTables.labels)', 2),
                     self.check('routingConfiguration.propagatedRouteTables.labels[0]', 'label1'),
                     self.check('routingConfiguration.propagatedRouteTables.labels[1]', 'label2'),
                     self.check('routingConfiguration.vnetRoutes.staticRoutes[0].name', self.kwargs['route']),
                     self.check('routingConfiguration.vnetRoutes.staticRoutes[0].nextHopIpAddress', self.kwargs['next_hop'])
                 ])

        self.cmd('network vhub connection show '
                 '-g {rg} '
                 '-n {connection} '
                 '--vhub-name {vhub}',
                 checks=[
                     self.check('provisioningState', 'Succeeded'),
                     self.check('name', self.kwargs['connection']),
                     self.check('routingConfiguration.associatedRouteTable.id', self.kwargs['route_table1']),
                     self.check('length(routingConfiguration.propagatedRouteTables.ids)', 2),
                     self.check('routingConfiguration.propagatedRouteTables.ids[0].id', self.kwargs['route_table1']),
                     self.check('routingConfiguration.propagatedRouteTables.ids[1].id', self.kwargs['route_table2']),
                     self.check('length(routingConfiguration.propagatedRouteTables.labels)', 2),
                     self.check('routingConfiguration.propagatedRouteTables.labels[0]', 'label1'),
                     self.check('routingConfiguration.propagatedRouteTables.labels[1]', 'label2'),
                     self.check('routingConfiguration.vnetRoutes.staticRoutes[0].name', self.kwargs['route']),
                     self.check('routingConfiguration.vnetRoutes.staticRoutes[0].nextHopIpAddress', self.kwargs['next_hop'])
                 ])

        self.cmd('network vhub connection list '
                 '-g {rg} '
                 '--vhub-name {vhub}',
                 checks=[
                     self.check('length(@)', 1)
                 ])

        self.cmd('network vhub connection delete '
                 '-g {rg} '
                 '-n {connection} '
                 '--vhub-name {vhub} '
                 '-y',
                 checks=[])

        with self.assertRaises(ResourceNotFoundError):
            self.cmd('network vhub connection show '
                     '-g {rg} '
                     '-n {connection} '
                     '--vhub-name {vhub}')

    @record_only()
    @ResourceGroupPreparer(name_prefix='cli_test_azure_vwan_vhub_get_effective_routes')
    def test_azure_vwan_vhub_get_effective_routes(self):
        self.kwargs.update({
            'rg': 'azure-cli-test-rg',
            'vhub': 'yu-vhub1',
            'resource_type': 'P2SConnection',
            'resource_id': '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/azure-cli-test-rg/providers/Microsoft.Network/p2sVpnGateways/p2svpngateway/p2sConnectionConfigurations/myconnectionconfig'
        })

        # You need to create a virtual hub and a P2S VPN gateway with connection, then connect them together before running the following command.
        result = self.cmd('network vhub get-effective-routes '
                          '-g {rg} '
                          '-n {vhub} '
                          '--resource-type {resource_type} '
                          '--resource-id {resource_id} '
                          '-o table')
        lines = result.output.strip().split('\n')
        self.assertTrue(len(lines) == 7)


class P2SVpnGatewayVpnClientTestScenario(ScenarioTest):
    def __init__(self, method_name):
        super().__init__(method_name, recording_processors=[
            VpnClientGeneratedURLReplacer()
        ])

    @ResourceGroupPreparer(name_prefix='test_p2s_vpn_client_generate')
    def test_p2s_vpn_client_generate(self, resource_group):
        self.kwargs.update({
            'vwan': 'test-p2s-vwan',
            'vhub': 'test-p2s-vhub',
            'vpn_server_config': 'test-p2s-vpn-server-config',
            'vpn_server_cert': os.path.join(TEST_DIR, 'data', 'ApplicationGatewayAuthCert.cer'),
            'vpn_server_pem': os.path.join(TEST_DIR, 'data', 'ApplicationGatewayAuthCert.pem'),
            'p2s_gateway': 'test-p2s-gateway',
        })

        self.cmd('network vwan create -g {rg} -n {vwan}')
        self.cmd('network vhub create -g {rg} -n {vhub} --vwan {vwan} --address-prefix 10.0.1.0/24')

        # when live test, run in Linux environment or annotate "self.escape = '\\'" in shlex.py in Powershell before run
        self.cmd('network vpn-server-config create -g {rg} -n {vpn_server_config} '
                 '--vpn-client-root-certs "{vpn_server_cert}" '
                 '--vpn-client-revoked-certs "{vpn_server_pem}"')

        self.cmd('az network p2s-vpn-gateway create -g {rg} --vhub {vhub} -n {p2s_gateway} '
                 '--scale-unit 2 '
                 '--address-space 10.0.2.0/24 11.0.1.0/24 '
                 '--vpn-server-config {vpn_server_config}')

        out = self.cmd('network p2s-vpn-gateway vpn-client generate -g {rg} -n {p2s_gateway}').get_output_in_json()
        self.assertIsNotNone(out['profileUrl'])
        self.assertTrue(out['profileUrl'].endswith('.zip'))


class RoutingIntentClientTest(ScenarioTest):
    @AllowLargeResponse(size_kb=10240)
    @ResourceGroupPreparer(name_prefix="cli_test_routing_intent_", location="westus")
    def test_routing_intent_crud(self):
        self.kwargs.update({
            "routing_intent_name": self.create_random_name("routing-intent-", 20),
            "vwan_name": self.create_random_name("vwan-", 12),
            "vhub_name": self.create_random_name("vhub-", 12),
            "firewall_name": self.create_random_name("firewall-", 16)
        })

        self.cmd("network vwan create -n {vwan_name} -g {rg}")
        self.cmd("network vhub create -n {vhub_name} -g {rg} --vwan {vwan_name} --address-prefix 10.0.1.0/24")

        self.cmd("extension add -n azure-firewall")
        self.kwargs["firewall_id"] = self.cmd(
            "network firewall create -n {firewall_name} -g {rg} --vhub {vhub_name} --sku AZFW_Hub --count 1"
        ).get_output_in_json()["id"]

        self.cmd(
            "network vhub routing-intent create -n {routing_intent_name} -g {rg} --vhub {vhub_name} "
            "--routing-policies \"[{{name:InternetTraffic,destinations:[Internet],next-hop:{firewall_id}}},"
            "{{name:PrivateTrafficPolicy,destinations:[PrivateTraffic],next-hop:{firewall_id}}}]\"",
            checks=[
                self.check("name", "{routing_intent_name}"),
                self.check("length(routingPolicies)", 2)
            ]
        )
        self.cmd(
            "network vhub routing-intent list -g {rg} --vhub {vhub_name}",
            checks=[
                self.check("length(@)", 1),
                self.check("[0].type", "Microsoft.Network/virtualHubs/routingIntent")
            ]
        )
        self.cmd(
            "network vhub routing-intent update -n {routing_intent_name} -g {rg} --vhub {vhub_name} "
            "--routing-policies \"[{{name:InternetTraffic,destinations:[Internet],next-hop:{firewall_id}}}]\""
        )
        self.cmd(
            "network vhub routing-intent show -n {routing_intent_name} -g {rg} --vhub {vhub_name}",
            checks=[
                self.check("name", "{routing_intent_name}"),
                self.check("length(routingPolicies)", 1)
            ]
        )
        self.cmd("network vhub routing-intent delete -n {routing_intent_name} -g {rg} --vhub {vhub_name} --yes")

        self.cmd("extension remove -n azure-firewall")


class RouteMapScenario(ScenarioTest):
    @ResourceGroupPreparer(name_prefix="cli_test_route_map", location="westus")
    def test_vhub_route_map(self):
        self.kwargs.update({
            "vwan_name": self.create_random_name("vwan-", 12),
            "vhub_name": self.create_random_name("vhub-", 12),
            "route_map_name": self.create_random_name("routemap-", 16)
        })

        self.cmd("network vwan create -n {vwan_name} -g {rg}")
        self.cmd("network vhub create -n {vhub_name} -g {rg} --vwan {vwan_name} --address-prefix 10.0.1.0/24")

        self.cmd("network vhub route-map create -n {route_map_name} -g {rg} --vhub-name {vhub_name}", checks=[
            self.check('name', '{route_map_name}')
        ])
        self.cmd("network vhub route-map update -n {route_map_name} -g {rg} --vhub-name {vhub_name} --rules [{{name:rule1,matchCriteria:[{{matchCondition:Contains,routePrefix:[10.0.0.0/8]}}],actions:[{{type:Add,parameters:[{{asPath:[22334]}}]}}]}}]", checks=[
            self.check('name', '{route_map_name}'),
            self.check('rules[0].actions[0].parameters[0].asPath[0]', '22334'),
            self.check('rules[0].actions[0].type', 'Add'),
            self.check('rules[0].matchCriteria[0].matchCondition', 'Contains'),
            self.check('rules[0].matchCriteria[0].routePrefix[0]', '10.0.0.0/8'),
            self.check('rules[0].name', 'rule1')
        ])
        self.cmd("network vhub route-map list -g {rg} --vhub-name {vhub_name}", checks=[
            self.check('[0].name', '{route_map_name}'),
            self.check('[0].rules[0].actions[0].parameters[0].asPath[0]', '22334'),
            self.check('[0].rules[0].actions[0].type', 'Add'),
            self.check('[0].rules[0].matchCriteria[0].matchCondition', 'Contains'),
            self.check('[0].rules[0].matchCriteria[0].routePrefix[0]', '10.0.0.0/8'),
            self.check('[0].rules[0].name', 'rule1')
        ])
        self.cmd('network vhub route-map rule add --name rule2 -g {rg} --route-map-name {route_map_name} --vhub-name {vhub_name} --match-criteria "[{{matchCondition:Contains,routePrefix:[10.0.0.1/8]}}]" --actions "[{{type:Add,parameters:[{{asPath:[22335]}}]}}]" --next-step Continue', checks=[
            self.check('actions[0].parameters[0].asPath[0]', '22335'),
            self.check('actions[0].type', 'Add'),
            self.check('matchCriteria[0].matchCondition', 'Contains'),
            self.check('matchCriteria[0].routePrefix[0]', '10.0.0.1/8'),
            self.check('name', 'rule2'),
            self.check('nextStepIfMatched', 'Continue')
        ])
        self.cmd('network vhub route-map rule show -g {rg} --route-map-name {route_map_name} --vhub-name {vhub_name} --rule-index 0', checks=[
            self.check('actions[0].parameters[0].asPath[0]', '22334'),
            self.check('actions[0].type', 'Add'),
            self.check('matchCriteria[0].matchCondition', 'Contains'),
            self.check('matchCriteria[0].routePrefix[0]', '10.0.0.0/8'),
            self.check('name', 'rule1')
        ])
        self.cmd('network vhub route-map rule list -g {rg} --route-map-name {route_map_name} --vhub-name {vhub_name}', checks=[
            self.check('[0].actions[0].parameters[0].asPath[0]', '22334'),
            self.check('[0].actions[0].type', 'Add'),
            self.check('[0].matchCriteria[0].matchCondition', 'Contains'),
            self.check('[0].matchCriteria[0].routePrefix[0]', '10.0.0.0/8'),
            self.check('[0].name', 'rule1'),
            self.check('[1].actions[0].parameters[0].asPath[0]', '22335'),
            self.check('[1].actions[0].type', 'Add'),
            self.check('[1].matchCriteria[0].matchCondition', 'Contains'),
            self.check('[1].matchCriteria[0].routePrefix[0]', '10.0.0.1/8'),
            self.check('[1].name', 'rule2'),
            self.check('[1].nextStepIfMatched', 'Continue')
        ])
        self.cmd("network vhub route-map show -n {route_map_name} -g {rg} --vhub-name {vhub_name}", checks=[
            self.check('name', '{route_map_name}'),
            self.check('rules[0].actions[0].parameters[0].asPath[0]', '22334'),
            self.check('rules[0].actions[0].type', 'Add'),
            self.check('rules[0].matchCriteria[0].matchCondition', 'Contains'),
            self.check('rules[0].matchCriteria[0].routePrefix[0]', '10.0.0.0/8'),
            self.check('rules[0].name', 'rule1'),
            self.check('rules[1].actions[0].parameters[0].asPath[0]', '22335'),
            self.check('rules[1].actions[0].type', 'Add'),
            self.check('rules[1].matchCriteria[0].matchCondition', 'Contains'),
            self.check('rules[1].matchCriteria[0].routePrefix[0]', '10.0.0.1/8'),
            self.check('rules[1].name', 'rule2'),
            self.check('rules[1].nextStepIfMatched', 'Continue')
        ])
        self.cmd('network vhub route-map rule delete -g {rg} --route-map-name {route_map_name} --vhub-name {vhub_name} --rule-index 1 -y')
        self.cmd("network vhub route-map show -n {route_map_name} -g {rg} --vhub-name {vhub_name}", checks=[
            self.check('name', '{route_map_name}'),
            self.check('length(rules)', 1)
        ])
        self.cmd("network vhub route-map delete -n {route_map_name} -g {rg} --vhub-name {vhub_name} -y")

    @ResourceGroupPreparer(name_prefix='cli_test_vhub_connection_inbound_outbound_routemap')
    @VirtualNetworkPreparer()
    def test_vhub_connection_inbound_outbound_routemap(self, virtual_network, resource_group):
        self.kwargs.update({
            'vnet': virtual_network,
            'vwan': self.create_random_name('vwan', 10),
            'vhub': self.create_random_name('vhub', 10),
            'connection': self.create_random_name('conn', 10),
            "route_map_name": self.create_random_name("routemap-", 16),
            "route_map_name_2": self.create_random_name("routemap-", 16),
            "route_map_name_3": self.create_random_name("routemap-", 16),
            "route_map_name_4": self.create_random_name("routemap-", 16)
        })

        self.cmd('network vwan create -n {vwan} -g {rg} --type Standard')
        self.cmd('network vhub create -g {rg} -n {vhub} --vwan {vwan}  --address-prefix 10.5.0.0/16 -l westus --sku Standard')
        route_map_id = self.cmd("network vhub route-map create -n {route_map_name} -g {rg} --vhub-name {vhub}").get_output_in_json()['id']
        route_map_id_2 = self.cmd("network vhub route-map create -n {route_map_name_2} -g {rg} --vhub-name {vhub}").get_output_in_json()['id']
        route_map_id_3 = self.cmd("network vhub route-map create -n {route_map_name_3} -g {rg} --vhub-name {vhub}").get_output_in_json()['id']
        route_map_id_4 = self.cmd("network vhub route-map create -n {route_map_name_4} -g {rg} --vhub-name {vhub}").get_output_in_json()['id']
        self.kwargs.update({
            'route_map_id': route_map_id,
            'route_map_id_2': route_map_id_2,
            'route_map_id_3': route_map_id_3,
            'route_map_id_4': route_map_id_4
        })
        self.cmd('network vhub connection create -g {rg} --vhub-name {vhub} --name {connection} --remote-vnet {vnet} --associated-inbound-routemap {route_map_id} --associated-outbound-routemap {route_map_id_2}', checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('name', '{connection}'),
            self.check('routingConfiguration.inboundRouteMap.id', '{route_map_id}'),
            self.check('routingConfiguration.outboundRouteMap.id', '{route_map_id_2}')
        ])
        self.cmd('network vhub connection update -g {rg} --vhub-name {vhub} --name {connection} --associated-inbound-routemap {route_map_id_3} --associated-outbound-routemap {route_map_id_4}', checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('name', '{connection}'),
            self.check('routingConfiguration.inboundRouteMap.id', '{route_map_id_3}'),
            self.check('routingConfiguration.outboundRouteMap.id', '{route_map_id_4}')
        ])

    @ResourceGroupPreparer(name_prefix='cli_test_vpn_gateway_connection_inbound_outbound_routemap')
    def test_vpn_gateway_connection_inbound_outbound_routemap(self):
        self.kwargs.update({
            'vwan': self.create_random_name('vwan', 10),
            'vhub': self.create_random_name('vhub', 10),
            'vpn_site': self.create_random_name('site', 10),
            'vpn_gateway': self.create_random_name('gateway', 15),
            'connection': self.create_random_name('conn', 10),
            "route_map_name": self.create_random_name("routemap-", 16),
            "route_map_name_2": self.create_random_name("routemap-", 16),
            "route_map_name_3": self.create_random_name("routemap-", 16),
            "route_map_name_4": self.create_random_name("routemap-", 16)
        })

        self.cmd('network vwan create -g {rg} -n {vwan}')
        self.cmd('network vhub create -g {rg} -n {vhub} --vwan {vwan} --address-prefix 10.0.1.0/24')

        route_map_id = self.cmd("network vhub route-map create -n {route_map_name} -g {rg} --vhub-name {vhub}").get_output_in_json()['id']
        route_map_id_2 = self.cmd("network vhub route-map create -n {route_map_name_2} -g {rg} --vhub-name {vhub}").get_output_in_json()['id']
        route_map_id_3 = self.cmd("network vhub route-map create -n {route_map_name_3} -g {rg} --vhub-name {vhub}").get_output_in_json()['id']
        route_map_id_4 = self.cmd("network vhub route-map create -n {route_map_name_4} -g {rg} --vhub-name {vhub}").get_output_in_json()['id']
        self.kwargs.update({
            'route_map_id': route_map_id,
            'route_map_id_2': route_map_id_2,
            'route_map_id_3': route_map_id_3,
            'route_map_id_4': route_map_id_4
        })
        self.cmd('network vpn-gateway create -g {rg} --vhub {vhub} --name {vpn_gateway}')
        self.cmd('network vpn-site create -g {rg} -n {vpn_site} --ip-address 10.0.2.110 --address-prefixes 10.0.2.0/24')
        self.cmd('network vpn-gateway connection create -g {rg} -n {connection} --gateway-name {vpn_gateway} --remote-vpn-site {vpn_site} --associated-inbound-routemap {route_map_id} --associated-outbound-routemap {route_map_id_2}', checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('name', '{connection}'),
            self.check('routingConfiguration.inboundRouteMap.id', '{route_map_id}'),
            self.check('routingConfiguration.outboundRouteMap.id', '{route_map_id_2}')
        ])
        self.cmd('network vpn-gateway connection update -g {rg} -n {connection} --gateway-name {vpn_gateway} --associated-inbound-routemap {route_map_id_3} --associated-outbound-routemap {route_map_id_4}', checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('name', '{connection}'),
            self.check('routingConfiguration.inboundRouteMap.id', '{route_map_id_3}'),
            self.check('routingConfiguration.outboundRouteMap.id', '{route_map_id_4}')
        ])

    @ResourceGroupPreparer(name_prefix='cli_test_vpn_gateway_nat_rule')
    def test_vpn_gateway_nat_rule(self):
        self.kwargs.update({
            'vwan': self.create_random_name('vwan', 10),
            'vhub': self.create_random_name('vhub', 10),
            'vpn_gateway': self.create_random_name('gateway', 15),
            'nat_rule': self.create_random_name('nat-rule', 15),
        })
        self.cmd('network vwan create -g {rg} -n {vwan}')
        self.cmd('network vhub create -g {rg} -n {vhub} --vwan {vwan} --address-prefix 10.0.1.0/24')
        self.cmd('network vpn-gateway create -g {rg} --vhub {vhub} --name {vpn_gateway}')
        self.cmd('network vpn-gateway nat-rule create -g {rg} --gateway-name {vpn_gateway} --name {nat_rule} '
                 '--internal-mappings [{{"address-space":10.4.0.0/24}}] '
                 '--external-mappings [{{"address-space":192.168.21.0/24}}] '
                 '--type Static --mode EgressSnat',
                 checks=[self.check('name', '{nat_rule}'),
                         self.check('type', 'Static'),
                         self.check('mode', 'EgressSnat'),
                         self.check('internalMappings[0].addressSpace', '10.4.0.0/24'),
                         self.check('externalMappings[0].addressSpace', '192.168.21.0/24')])
        self.cmd('network vpn-gateway nat-rule update -g {rg} --gateway-name {vpn_gateway} --name {nat_rule} '
                 '--internal-mappings [{{"address-space":10.3.0.0/24}}]',
                 checks=[self.check('name', '{nat_rule}'),
                         self.check('type', 'Static'),
                         self.check('mode', 'EgressSnat'),
                         self.check('internalMappings[0].addressSpace', '10.3.0.0/24'),
                         self.check('externalMappings[0].addressSpace', '192.168.21.0/24')])
        self.cmd('network vpn-gateway nat-rule list -g {rg} --gateway-name {vpn_gateway}', self.check('type(@)', 'array'))
        self.cmd('network vpn-gateway nat-rule show -g {rg} --gateway-name {vpn_gateway} --name {nat_rule}', self.check('name', '{nat_rule}'))
        self.cmd('network vpn-gateway nat-rule delete -g {rg} --gateway-name {vpn_gateway} --name {nat_rule} -y')

    @ResourceGroupPreparer(name_prefix='cli_test_p2s_vpn_gateway_inbound_outbound_routemap', location='westcentralus')
    def test_p2s_vpn_gateway_inbound_outbound_routemap(self, resource_group):
        self.kwargs.update({
            'vwan': self.create_random_name('vwan', 10),
            'vhub': self.create_random_name('vhub', 10),
            'cert_file': os.path.join(TEST_DIR, 'data', 'ApplicationGatewayAuthCert.cer'),
            'pem_file': os.path.join(TEST_DIR, 'data', 'ApplicationGatewayAuthCert.pem'),
            'vserverconfig': self.create_random_name("config-", 16),
            'vp2sgateway': self.create_random_name("vp2s-", 16),
            "route_map_name": self.create_random_name("routemap-", 16),
            "route_map_name_2": self.create_random_name("routemap-", 16),
            "route_map_name_3": self.create_random_name("routemap-", 16),
            "route_map_name_4": self.create_random_name("routemap-", 16)
        })

        self.cmd('network vwan create -n {vwan} -g {rg} --type Standard')
        self.cmd('network vhub create -g {rg} -n {vhub} --vwan {vwan}  --address-prefix 10.5.0.0/16 --sku Standard')
        route_map_id = self.cmd("network vhub route-map create -n {route_map_name} -g {rg} --vhub-name {vhub}").get_output_in_json()['id']
        route_map_id_2 = self.cmd("network vhub route-map create -n {route_map_name_2} -g {rg} --vhub-name {vhub}").get_output_in_json()['id']
        route_map_id_3 = self.cmd("network vhub route-map create -n {route_map_name_3} -g {rg} --vhub-name {vhub}").get_output_in_json()['id']
        route_map_id_4 = self.cmd("network vhub route-map create -n {route_map_name_4} -g {rg} --vhub-name {vhub}").get_output_in_json()['id']
        self.kwargs.update({
            'route_map_id': route_map_id,
            'route_map_id_2': route_map_id_2,
            'route_map_id_3': route_map_id_3,
            'route_map_id_4': route_map_id_4
        })
        self.cmd('network vpn-server-config create -n {vserverconfig} -g {rg} --vpn-client-root-certs "{cert_file}" --vpn-client-revoked-certs "{pem_file}"')

        self.cmd('az network p2s-vpn-gateway create -g {rg} -n {vp2sgateway} --scale-unit 2 --vhub {vhub} --vpn-server-config {vserverconfig} --address-space 10.0.0.0/24 11.0.0.0/24 --associated-inbound-routemap {route_map_id} --associated-outbound-routemap {route_map_id_2}', checks=[
            self.check('p2SConnectionConfigurations[0].routingConfiguration.inboundRouteMap.id', '{route_map_id}'),
            self.check('p2SConnectionConfigurations[0].routingConfiguration.outboundRouteMap.id', '{route_map_id_2}')
        ])
        self.cmd('az network p2s-vpn-gateway update -g {rg} -n {vp2sgateway} --associated-inbound-routemap {route_map_id_3} --associated-outbound-routemap {route_map_id_4}', checks=[
            self.check('p2SConnectionConfigurations[0].routingConfiguration.inboundRouteMap.id', '{route_map_id_3}'),
            self.check('p2SConnectionConfigurations[0].routingConfiguration.outboundRouteMap.id', '{route_map_id_4}')
        ])
