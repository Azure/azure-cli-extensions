# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, StorageAccountPreparer, JMESPathCheck, NoneCheck,
                               api_version_constraint)
from azure.cli.testsdk.scenario_tests.decorators import AllowLargeResponse
from azure.cli.core.azclierror import ValidationError


class AzureFirewallScenario(ScenarioTest):

    def __init__(self, method_name, config_file=None, recording_dir=None, recording_name=None,
                 recording_processors=None,
                 replay_processors=None, recording_patches=None, replay_patches=None):
        super(AzureFirewallScenario, self).__init__(
            method_name
        )
        self.cmd('extension add -n ip-group')
        self.cmd('extension add -n virtual-wan')

    @ResourceGroupPreparer(name_prefix='cli_test_azure_firewall')
    def test_azure_firewall(self, resource_group):
        self.kwargs.update({
            'af': 'af1',
            'coll': 'rc1',
            'rule1': 'rule1',
            'rule2': 'rule2'
        })
        self.cmd('network firewall create -g {rg} -n {af} --threat-intel-mode Alert --allow-active-ftp', checks=[
            self.check('threatIntelMode', 'Alert'),
            self.check('additionalProperties."Network.FTP.AllowActiveFTP"', 'true')
        ])
        self.cmd('network firewall update -g {rg} -n {af} --threat-intel-mode Deny --allow-active-ftp false', checks=[
            self.check('threatIntelMode', 'Deny'),
            self.not_exists('additionalProperties."Network.FTP.AllowActiveFTP"')
        ])
        self.cmd('network firewall show -g {rg} -n {af}')
        self.cmd('network firewall list -g {rg}')
        self.cmd('network firewall delete -g {rg} -n {af}')

    @ResourceGroupPreparer(name_prefix="cli_test_firewall_with_additional_log_", location="westus")
    def test_firewall_with_additional_log(self):
        self.kwargs.update({
            "firewall_name": self.create_random_name("firewall-", 16)
        })

        self.cmd(
            "network firewall create -n {firewall_name} -g {rg} "
            "--enable-fat-flow-logging --enable-udp-log-optimization",
            checks=[
                self.check('additionalProperties."Network.AdditionalLogs.EnableFatFlowLogging"', "true"),
                self.check('additionalProperties."Network.AdditionalLogs.EnableUdpLogOptimization"', "true")
            ]
        )
        self.cmd(
            "network firewall update -n {firewall_name} -g {rg} "
            "--enable-fat-flow-logging false --enable-udp-log-optimization false",
            checks=[
                self.not_exists('additionalProperties."Network.AdditionalLogs.EnableFatFlowLogging"'),
                self.not_exists('additionalProperties."Network.AdditionalLogs.EnableUdpLogOptimization"')
            ]
        )

        self.cmd("network firewall delete -n {firewall_name} -g {rg}")

    @ResourceGroupPreparer(name_prefix='cli_test_azure_firewall_ip_config')
    def test_azure_firewall_ip_config(self, resource_group):

        self.kwargs.update({
            'af': 'af1',
            'pubip': 'pubip',
            'pubip2': 'pubip2',
            'vnet': 'myvnet',
            'subnet': 'mysubnet',
            'ipconfig': 'myipconfig1',
            'ipconfig2': 'myipconfig2'
        })
        self.cmd('network firewall create -g {rg} -n {af}')
        self.cmd('network public-ip create -g {rg} -n {pubip} --sku standard')
        self.cmd('network public-ip create -g {rg} -n {pubip2} --sku standard')
        self.cmd('network vnet create -g {rg} -n {vnet} --subnet-name "AzureFirewallSubnet" --address-prefixes 10.0.0.0/16 --subnet-prefixes 10.0.0.0/24')
        # vnet_instance = self.cmd('network vnet create -g {rg} -n {vnet} --subnet-name "AzureFirewallSubnet" --address-prefixes 10.0.0.0/16 --subnet-prefixes 10.0.0.0/24').get_output_in_json()
        # subnet_id_default = vnet_instance['newVNet']['subnets'][0]['id']
        # Disable it due to service limitation.
        # self.cmd('network firewall ip-config create -g {rg} -n {ipconfig} -f {af} --public-ip-address {pubip} --vnet-name {vnet}', checks=[
        #     self.check('name', '{ipconfig}'),
        #     self.check('subnet.id', subnet_id_default)
        # ])
        # self.cmd('network firewall ip-config create -g {rg} -n {ipconfig2} -f {af} --public-ip-address {pubip2} --vnet-name {vnet}', checks=[
        #     self.check('name', '{ipconfig2}'),
        #     self.check('subnet', None)
        # ])

        self.cmd('network firewall ip-config delete -g {rg} -n {ipconfig2} -f {af}')
        self.cmd('network firewall ip-config delete -g {rg} -n {ipconfig} -f {af}')

    @ResourceGroupPreparer(name_prefix='test_azure_firewall_management_ip_config')
    def test_azure_firewall_management_ip_config(self, resource_group):
        self.kwargs.update({
            'af': 'af1',
            'pubip': 'pubip',
            'pubip3': 'pubip3',
            'pubip4': 'pubip4',
            'management_pubip': 'pubip2',
            'vnet': 'myvnet',
            'vnet3': 'myvnet3',
            'management_vnet': 'myvnet2',
            'management_vnet2': 'myvnet4',
            'ipconfig': 'myipconfig1',
            'ipconfig3': 'myipconfig3',
            'management_ipconfig': 'myipconfig2'
        })
        self.cmd('network firewall create -g {rg} -n {af}')
        self.cmd('network public-ip create -g {rg} -n {pubip} --sku standard')
        self.cmd('network public-ip create -g {rg} -n {management_pubip} --sku standard')
        self.cmd('network public-ip create -g {rg} -n {pubip3} --sku standard')
        self.cmd('network public-ip create -g {rg} -n {pubip4} --sku standard')
        # maybe need to fix in the future
        # vnet_instance = self.cmd(
        #     'network vnet create -g {rg} -n {vnet} --subnet-name "AzureFirewallSubnet" --address-prefixes 10.0.0.0/16 --subnet-prefixes 10.0.0.0/24').get_output_in_json()
        # subnet_id_ip_config = vnet_instance['newVNet']['subnets'][0]['id']

        # vnet_instance = self.cmd(
        #     'network vnet create -g {rg} -n {management_vnet} --subnet-name "AzureFirewallManagementSubnet" --address-prefixes 10.0.0.0/16 --subnet-prefixes 10.0.0.0/24').get_output_in_json()
        # subnet_id_management_ip_config = vnet_instance['newVNet']['subnets'][0]['id']

        # vnet_instance = self.cmd(
        #     'network vnet create -g {rg} -n {management_vnet2} --subnet-name "AzureFirewallManagementSubnet" --address-prefixes 10.0.0.0/16 --subnet-prefixes 10.0.0.0/24').get_output_in_json()
        # subnet_id_management_ip_config_2 = vnet_instance['newVNet']['subnets'][0]['id']

        # self.cmd('network firewall ip-config create -g {rg} -n {ipconfig} -f {af} --public-ip-address {pubip} --vnet-name {vnet} '
        #          '--m-name {management_ipconfig} --m-public-ip-address {management_pubip} --m-vnet-name {management_vnet}',
        #          checks=[
        #              self.check('name', '{ipconfig}'),
        #              self.check('subnet.id', subnet_id_ip_config)
        #          ])

        # self.cmd('network vnet create -g {rg} -n {vnet} --subnet-name "AzureFirewallSubnet" --address-prefixes 10.0.0.0/16 --subnet-prefixes 10.0.0.0/24')
        # self.cmd('network firewall ip-config create -g {rg} -n {ipconfig3} -f {af} --public-ip-address {pubip3} --vnet-name {vnet}', checks=[
        #     self.check('name', '{ipconfig3}'),
        #     # self.check('subnet', None)
        # ])

        # Disable it due to service limitation.
        # self.cmd(
        #    'network firewall management-ip-config create -g {rg} -n {management_ipconfig} -f {af} --public-ip-address {management_pubip} --vnet-name {management_vnet}',
        #    checks=[
        #        self.check('name', '{management_ipconfig}'),
        #        self.check('subnet.id', subnet_id_management_ip_config)
        #    ])

        # maybe need to fix in the future
        # self.cmd(
        #     'network firewall management-ip-config show -g {rg} -f {af}',
        #     checks=[
        #         self.check('name', '{management_ipconfig}'),
        #         self.check('subnet.id', subnet_id_management_ip_config)
        #     ])

        # self.cmd(
        #     'network firewall management-ip-config update -g {rg} -f {af} --public-ip-address {pubip4} --vnet-name {management_vnet2}',
        #     checks=[
        #         self.check('name', '{management_ipconfig}'),
        #         self.check('subnet.id', subnet_id_management_ip_config_2)
        #     ])

        self.cmd('network firewall ip-config delete -g {rg} -f {af} -n {ipconfig3}')
        self.cmd('network firewall ip-config delete -g {rg} -f {af} -n {ipconfig}')

        self.cmd(
            'network firewall management-ip-config show -g {rg} -f {af}',
            checks=[
                self.is_empty()
            ])

    @ResourceGroupPreparer(name_prefix='cli_test_azure_firewall_threat_intel_allowlist')
    def test_azure_firewall_threat_intel_allowlist(self, resource_group):

        self.kwargs.update({
            'af': 'af1',
        })
        self.cmd('network firewall create -g {rg} -n {af} --private-ranges 10.0.0.0 10.0.0.0/24 IANAPrivateRanges', checks=[
            self.check('additionalProperties."Network.SNAT.PrivateRanges"', '10.0.0.0, 10.0.0.0/24, IANAPrivateRanges')
        ])
        self.cmd('network firewall threat-intel-allowlist create -g {rg} -n {af} --ip-addresses 10.0.0.0 10.0.0.1 --fqdns www.bing.com *.microsoft.com *google.com', checks=[
            self.check('"ThreatIntel.Whitelist.FQDNs"', 'www.bing.com, *.microsoft.com, *google.com'),
            self.check('"ThreatIntel.Whitelist.IpAddresses"', '10.0.0.0, 10.0.0.1')
        ])
        self.cmd('network firewall threat-intel-allowlist show -g {rg} -n {af}', checks=[
            self.check('"ThreatIntel.Whitelist.FQDNs"', 'www.bing.com, *.microsoft.com, *google.com'),
            self.check('"ThreatIntel.Whitelist.IpAddresses"', '10.0.0.0, 10.0.0.1')
        ])
        self.cmd('network firewall threat-intel-allowlist update -g {rg} -n {af} --ip-addresses 10.0.0.1 10.0.0.0 --fqdns *google.com www.bing.com *.microsoft.com', checks=[
            self.check('"ThreatIntel.Whitelist.FQDNs"', '*google.com, www.bing.com, *.microsoft.com'),
            self.check('"ThreatIntel.Whitelist.IpAddresses"', '10.0.0.1, 10.0.0.0')
        ])
        self.cmd('network firewall update -g {rg} -n {af} --private-ranges IANAPrivateRanges 10.0.0.1 10.0.0.0/16', checks=[
            self.check('additionalProperties."Network.SNAT.PrivateRanges"', 'IANAPrivateRanges, 10.0.0.1, 10.0.0.0/16')
        ])
        self.cmd('network firewall threat-intel-allowlist delete -g {rg} -n {af}')

    @ResourceGroupPreparer(name_prefix='cli_test_azure_firewall_rules')
    def test_azure_firewall_rules(self, resource_group):

        self.kwargs.update({
            'af': 'af1',
            'coll': 'rc1',
            'coll2': 'rc2',
            'network_rule1': 'network-rule1',
            'nat_rule1': 'nat-rule1'
        })
        self.cmd('network firewall create -g {rg} -n {af}')
        self.cmd('network firewall network-rule create -g {rg} -n {network_rule1} -c {coll} --priority 10000 --action Allow -f {af} --source-addresses 10.0.0.0 111.1.0.0/24 --protocols UDP TCP ICMP --destination-fqdns www.bing.com --destination-ports 80')
        self.cmd('network firewall nat-rule create -g {rg} -n {network_rule1} -c {coll2} --priority 10001 --action Dnat -f {af} --source-addresses 10.0.0.0 111.1.0.0/24 --protocols UDP TCP --translated-fqdn server1.internal.com --destination-ports 96 --destination-addresses 12.36.22.14 --translated-port 95')
        self.cmd('network firewall delete -g {rg} -n {af}')

    @ResourceGroupPreparer(name_prefix='cli_test_azure_firewall_rules_with_ipgroups')
    def test_azure_firewall_rules_with_ipgroups(self, resource_group):

        self.kwargs.update({
            'af': 'af1',
            'coll': 'rc1',
            'coll2': 'rc2',
            'coll3': 'rc3',
            'network_rule1': 'network-rule1',
            'network_rule2': 'network-rule2',
            'nat_rule1': 'nat-rule1',
            'nat_rule2': 'nat-rule2',
            'app_rule1': 'app-rule1',
            'app_rule2': 'app-rule2',
            'source_ip_group': 'sourceipgroup',
            'destination_ip_group': 'destinationipgroup'
        })

        # self.cmd('extension add -n ip-group')
        self.cmd('network ip-group create -n {source_ip_group} -g {rg} --ip-addresses 10.0.0.0 10.0.0.1')
        self.cmd('network ip-group create -n {destination_ip_group} -g {rg} --ip-addresses 10.0.0.2 10.0.0.3')
        self.cmd('network firewall create -g {rg} -n {af}')
        self.cmd('network firewall network-rule create -g {rg} -n {network_rule1} -c {coll} --priority 10000 --action Allow -f {af} --source-ip-group {source_ip_group} --protocols UDP TCP ICMP --destination-ip-groups {destination_ip_group} --destination-ports 80')
        self.cmd('network firewall network-rule create -g {rg} -n {network_rule2} -c {coll} -f {af} --source-addresses 10.0.0.1 111.2.0.0/24 --protocols UDP TCP --destination-ip-groups {destination_ip_group} --destination-ports 81')
        self.cmd('network firewall nat-rule create -g {rg} -n {network_rule1} -c {coll2} --priority 10001 --action Dnat -f {af} --source-ip-group {source_ip_group} --protocols UDP TCP --translated-fqdn server1.internal.com --destination-ports 96 --destination-addresses 12.36.22.14 --translated-port 95 --source-ip-groups {source_ip_group}')
        self.cmd('network firewall nat-rule create -g {rg} -n {network_rule2} -c {coll2} -f {af} --source-addresses 10.0.0.1 111.2.0.0/24 --protocols UDP TCP --translated-fqdn server2.internal.com --destination-ports 97 --destination-addresses 12.36.22.15 --translated-port 96 --source-ip-groups {source_ip_group}')
        self.cmd('network firewall application-rule create -f {af} -n {app_rule1} --protocols Http=80 Https=8080 -g {rg} -c {coll3} --priority 10000 --action Allow --source-ip-groups {source_ip_group} --target-fqdns www.bing.com')
        self.cmd('network firewall application-rule create -f {af} -n {app_rule2} --protocols Http=80 Https=8080 -g {rg} -c {coll3} --source-ip-groups {source_ip_group} --target-fqdns www.microsoft.com')
        self.cmd('network firewall delete -g {rg} -n {af}')

    @ResourceGroupPreparer(name_prefix='cli_test_azure_firewall_zones', location='eastus')
    def test_azure_firewall_zones(self, resource_group):

        self.kwargs.update({
            'af': 'af1',
            'coll': 'rc1',
        })
        self.cmd('network firewall create -g {rg} -n {af} --zones 1 3')
        self.cmd('network firewall update -g {rg} -n {af} --zones 1')

    @ResourceGroupPreparer(name_prefix='cli_test_azure_firewall_virtual_hub', location='eastus2')
    def test_azure_firewall_virtual_hub(self, resource_group):
        from knack.util import CLIError
        self.kwargs.update({
            'af': 'af1',
            'coll': 'rc1',
            'vwan': 'clitestvwan',
            'vhub': 'clitestvhub',
            'vwan2': 'clitestvwan2',
            'vhub2': 'clitestvhub2',
            'rg': resource_group
        })
        # self.cmd('extension add -n virtual-wan')
        self.cmd('network vwan create -n {vwan} -g {rg} --type Standard')
        # self.cmd('network vhub create -g {rg} -n {vhub} --vwan {vwan}  --address-prefix 10.0.0.0/24 -l eastus2 --sku Standard')
        # self.cmd('network firewall create -g {rg} -n {af} --sku AZFW_Hub --count 1 --vhub {vhub}')
        # self.cmd('network firewall update -g {rg} -n {af} --vhub ""')

        # with self.assertRaisesRegex(CLIError, "allow active ftp is not allowed for azure firewall on virtual hub."):
        #     self.cmd('network firewall create -g {rg} -n {af} --sku AZFW_Hub --count 1 --vhub {vhub} --allow-active-ftp')

        self.cmd('network vwan create -n {vwan2} -g {rg} --type Standard')
        # self.cmd('network vhub create -g {rg} -n {vhub2} --vwan {vwan2}  --address-prefix 10.0.0.0/24 -l eastus2 --sku Standard')
        # self.cmd('network firewall update -g {rg} -n {af} --vhub {vhub2}')

    @ResourceGroupPreparer(name_prefix='cli_test_azure_firewall_virtual_hub', location='eastus2')
    def test_azure_firewall_virtual_hub_with_public_ips(self, resource_group):

        self.kwargs.update({
            'af': 'af1',
            'af2': 'af2',
            'coll': 'rc1',
            'vwan': 'clitestvwan1',
            'vhub': 'clitestvhub1',
            'vwan2': 'clitestvwan2',
            'vhub2': 'clitestvhub2',
            'rg': resource_group
        })
        # self.cmd('extension add -n virtual-wan')
        self.cmd('network vwan create -n {vwan} -g {rg} --type Standard')
        # self.cmd('network vhub create -g {rg} -n {vhub} --vwan {vwan}  --address-prefix 10.0.0.0/24 -l eastus2 --sku Standard')
        # self.cmd('network firewall create -g {rg} -n {af} --sku AZFW_Hub --count 4 --vhub {vhub}', checks=[
        #     self.check('length(hubIpAddresses.publicIPs.addresses)', 4)
        # ])
        # result = self.cmd('network firewall update -g {rg} -n {af} --count 5', checks=[
        #     self.check('length(hubIpAddresses.publicIPs.addresses)', 5)
        # ]).get_output_in_json()
        # self.kwargs.update({
        #     'ip1': result['hubIpAddresses']['publicIPs']['addresses'][0]['address'],
        #     'ip2': result['hubIpAddresses']['publicIPs']['addresses'][1]['address'],
        #     'ip3': result['hubIpAddresses']['publicIPs']['addresses'][2]['address']
        # })
        # self.cmd('network firewall update -g {rg} -n {af} --public-ips {ip1} {ip2} {ip3}', checks=[
        #     self.check('length(hubIpAddresses.publicIPs.addresses)', 3)
        # ])
        # self.cmd('network firewall show -g {rg} -n {af}')

    @AllowLargeResponse(size_kb=10240)
    @ResourceGroupPreparer(name_prefix='cli_test_azure_firewall_with_firewall_policy', location='westus2')
    def test_azure_firewall_with_firewall_policy(self, resource_group, resource_group_location):
        self.kwargs.update({
            'af': 'af1',
            'af2': 'af2',
            'policy': 'myclipolicy',
            'policy2': 'myclipolicy2',
            'coll': 'rc1',
            'vwan': 'clitestvwan',
            'vhub': 'clitestvhub',
            'rg': resource_group,
            'pubip': 'pubip',
            'vnet': 'myvnet',
            'ipconfig': 'myipconfig1',
            'location': resource_group_location,
        })
        # test firewall policy with vhub firewall
        self.cmd('extension add -n virtual-wan')
        self.cmd('network vwan create -n {vwan} -g {rg} --type Standard')
        # self.cmd('network vhub create -g {rg} -n {vhub} --vwan {vwan}  --address-prefix 10.0.0.0/24 -l {location} --sku Standard')

        self.cmd('network firewall policy create -g {rg} -n {policy} -l {location}', checks=[
            self.check('type', 'Microsoft.Network/FirewallPolicies'),
            self.check('name', '{policy}')
        ])
        # self.cmd('network firewall create -g {rg} -n {af} --count 1 --sku AZFW_Hub --vhub clitestvhub --firewall-policy {policy}')

        self.kwargs.update({'location': 'westus2'})

        # test firewall policy with vnet firewall
        self.cmd('network firewall create -g {rg} -n {af2} -l {location} --firewall-policy {policy}')
        self.cmd('network public-ip create -g {rg} -n {pubip} -l {location} --sku standard')
        self.cmd('network vnet create -g {rg} -n {vnet} --subnet-name "AzureFirewallSubnet" -l {location} --address-prefixes 10.0.0.0/16 --subnet-prefixes 10.0.0.0/24')
        # vnet_instance = self.cmd(
        #     'network vnet create -g {rg} -n {vnet} --subnet-name "AzureFirewallSubnet" -l {location} --address-prefixes 10.0.0.0/16 --subnet-prefixes 10.0.0.0/24').get_output_in_json()
        # subnet_id_default = vnet_instance['newVNet']['subnets'][0]['id']

        # Disable it due to service limitation.
        # self.cmd(
        #     'network firewall ip-config create -g {rg} -n {ipconfig} -f {af2} --public-ip-address {pubip} --vnet-name {vnet}',
        #     checks=[
        #         self.check('name', '{ipconfig}'),
        #         self.check('subnet.id', subnet_id_default)
        #     ])
        self.cmd('network firewall policy create -g {rg} -n {policy2} -l {location} --sku Premium', checks=[
            self.check('type', 'Microsoft.Network/FirewallPolicies'),
            self.check('name', '{policy2}')
        ])

    @ResourceGroupPreparer(name_prefix='test_azure_firewall_with_firewall_policy_premium', location='westus2')
    def test_azure_firewall_with_firewall_policy_premium(self, resource_group, resource_group_location):
        self.kwargs.update({
            'policy2': 'myclipolicy2',
            'rg': resource_group,
            'location': resource_group_location,
        })

        self.cmd('network firewall policy create -g {rg} -n {policy2} -l {location} --sku Premium', checks=[
            self.check('type', 'Microsoft.Network/FirewallPolicies'),
            self.check('name', '{policy2}')
        ])

        # test firewall policy identity
        identity = self.cmd('identity create -g {rg} -n identitytest',).get_output_in_json()
        self.kwargs.update({'id': identity['id']})
        # needs a check in the future
        # self.cmd('network firewall policy update -g {rg} -n {policy2} --identity {id}',
        #          checks=[self.exists('identity')])
        # self.cmd('network firewall policy update -g {rg} -n {policy2} --remove {id}',
        #          checks=[self.not_exists('identity')])

    @ResourceGroupPreparer(name_prefix='cli_test_azure_firewall_policy_with_threat_intel_allowlist', location='westus2')
    def test_azure_firewall_policy_with_threat_intel_allowlist(self, resource_group, resource_group_location):
        self.kwargs.update({
            'collectiongroup': 'myclirulecollectiongroup',
            'policy': 'myclipolicy',
            'rg': resource_group,
            'location': resource_group_location,
            'collection_group_priority': 10000
        })
        self.cmd('network firewall policy create -g {rg} -n {policy} -l {location}', checks=[
            self.check('type', 'Microsoft.Network/FirewallPolicies'),
            self.check('name', '{policy}')
        ])

        self.cmd('network firewall policy update -g {rg} -n {policy} --threat-intel-mode Deny '
                 '--ip-addresses 102.0.0.0 102.0.0.1 --fqdns *.google.com',
                 checks=[
                     self.check('type', 'Microsoft.Network/FirewallPolicies'),
                     self.check('name', '{policy}'),
                     self.check('threatIntelMode', 'Deny'),
                     self.check('threatIntelWhitelist.fqdns[0]', '*.google.com'),
                     self.check('threatIntelWhitelist.ipAddresses[0]', '102.0.0.0'),
                     self.check('threatIntelWhitelist.ipAddresses[1]', '102.0.0.1')
                 ])

    @ResourceGroupPreparer(name_prefix='test_azure_firewall_policy_intrusion_detection')
    @AllowLargeResponse()
    def test_azure_firewall_policy_intrusion_detection(self, resource_group):
        self.kwargs.update({
            'policy': 'myFirewallPolicy',
            'rg': resource_group,
        })

        self.cmd('network firewall policy create -g {rg} -n {policy} --sku Premium --idps-mode Off',
                 checks=[
                     self.check('sku.tier', 'Premium'),
                     self.check('intrusionDetection.mode', 'Off')
                 ])

        self.cmd('network firewall policy update -g {rg} -n {policy} --idps-mode Alert',
                 checks=[
                     self.check('intrusionDetection.mode', 'Alert')
                 ])

        self.cmd('network firewall policy intrusion-detection add -g {rg} --policy-name {policy} --mode Deny --signature-id 10001 --private-ranges 167.220.204.0/24 167.221.205.101/32',
                 checks=[
                     self.check('bypassTrafficSettings', []),
                     self.check('length(signatureOverrides)', 1),
                     self.check('signatureOverrides[0]', {'id': '10001', 'mode': 'Deny'}),
                     self.check('privateRanges[0]', "167.220.204.0/24"),
                     self.check('privateRanges[1]', "167.221.205.101/32")
                 ])

        self.cmd('network firewall policy intrusion-detection add -g {rg} --policy-name {policy} --mode Alert --signature-id 20001 --private-ranges 167.220.208.0/24 167.221.205.102/32',
                 checks=[
                     self.check('bypassTrafficSettings', []),
                     self.check('length(signatureOverrides)', 2),
                     self.check('signatureOverrides[0]', {'id': '10001', 'mode': 'Deny'}),
                     self.check('signatureOverrides[1]', {'id': '20001', 'mode': 'Alert'}),
                     self.check('privateRanges[0]', "167.220.208.0/24"),
                     self.check('privateRanges[1]', "167.221.205.102/32")
                 ])

        self.cmd('network firewall policy intrusion-detection add -g {rg} --policy-name {policy} '
                 '--rule-name bypass-rule-1 '
                 '--rule-protocol TCP '
                 '--rule-src-addresses 10.0.0.12 10.0.0.15 '
                 '--rule-dest-addresses 192.168.0.103 192.168.0.104 '
                 '--rule-dest-ports 8080 9090 5432',
                 checks=[
                     self.check('length(bypassTrafficSettings)', 1),
                     self.check('bypassTrafficSettings[0].description', None),
                     self.check('bypassTrafficSettings[0].destinationAddresses', ['192.168.0.103', '192.168.0.104']),
                     self.check('bypassTrafficSettings[0].destinationIpGroups', None),
                     self.check('bypassTrafficSettings[0].protocol', 'TCP'),
                     self.check('bypassTrafficSettings[0].destinationPorts', ['8080', '9090', '5432']),
                     self.check('length(signatureOverrides)', 2),
                     self.check('signatureOverrides[0]', {'id': '10001', 'mode': 'Deny'}),
                     self.check('signatureOverrides[1]', {'id': '20001', 'mode': 'Alert'}),
                 ])

        self.cmd('network firewall policy intrusion-detection list -g {rg} --policy-name {policy}',
                 checks=[
                     self.check('length(bypassTrafficSettings)', 1),
                     self.check('length(signatureOverrides)', 2),
                     self.check('length(privateRanges)', 2)
                 ])

        self.cmd('network firewall policy intrusion-detection remove -g {rg} --policy-name {policy} '
                 '--rule-name bypass-rule-1 '
                 '--signature-id 10001')

        self.cmd('network firewall policy intrusion-detection list -g {rg} --policy-name {policy}',
                 checks=[
                     self.check('length(bypassTrafficSettings)', 0),
                     self.check('length(signatureOverrides)', 1),
                     self.check('length(privateRanges)', 2)
                 ])

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_azure_firewall_policy', location='centralus')
    def test_azure_firewall_policy(self, resource_group, resource_group_location):
        self.kwargs.update({
            'collectiongroup': 'myclirulecollectiongroup',
            'policy': 'myclipolicy',
            'rg': resource_group,
            'location': resource_group_location,
            'collection_group_priority': 10000
        })
        self.cmd('network firewall policy create -g {rg} -n {policy} -l {location} '
                 '--ip-addresses 101.0.0.0 101.0.0.1 --fqdns *.microsoft.com '
                 '--sku Premium '
                 '--idps-mode Deny',
                 checks=[
                     self.check('type', 'Microsoft.Network/FirewallPolicies'),
                     self.check('name', '{policy}'),
                     self.check('threatIntelWhitelist.fqdns[0]', '*.microsoft.com'),
                     self.check('threatIntelWhitelist.ipAddresses[0]', '101.0.0.0'),
                     self.check('threatIntelWhitelist.ipAddresses[1]', '101.0.0.1'),
                     self.check('sku.tier', 'Premium'),
                     self.check('intrusionDetection.mode', 'Deny'),
                 ])

        self.cmd('network firewall policy show -g {rg} -n {policy}', checks=[
            self.check('type', 'Microsoft.Network/FirewallPolicies'),
            self.check('name', '{policy}')
        ])

        self.cmd('network firewall policy list -g {rg}', checks=[
            self.check('@[0].type', 'Microsoft.Network/FirewallPolicies'),
            self.check('@[0].name', '{policy}')
        ])

        self.cmd('network firewall policy list')

        self.cmd('network firewall policy update -g {rg} -n {policy} --threat-intel-mode Deny '
                 '--ip-addresses 102.0.0.0 102.0.0.1 --fqdns *.google.com '
                 '--idps-mode Off',
                 checks=[
                     self.check('type', 'Microsoft.Network/FirewallPolicies'),
                     self.check('name', '{policy}'),
                     self.check('threatIntelMode', 'Deny'),
                     self.check('threatIntelWhitelist.fqdns[0]', '*.google.com'),
                     self.check('threatIntelWhitelist.ipAddresses[0]', '102.0.0.0'),
                     self.check('threatIntelWhitelist.ipAddresses[1]', '102.0.0.1'),
                     self.check('intrusionDetection.mode', 'Off'),
                 ])

        self.cmd('network firewall policy rule-collection-group create -g {rg} --priority {collection_group_priority} --policy-name {policy} -n {collectiongroup}', checks=[
            self.check('type', 'Microsoft.Network/FirewallPolicies/RuleCollectionGroups'),
            self.check('name', '{collectiongroup}')
        ])

        self.cmd('network firewall policy rule-collection-group show -g {rg} --policy-name {policy} -n {collectiongroup}', checks=[
            self.check('type', 'Microsoft.Network/FirewallPolicies/RuleCollectionGroups'),
            self.check('name', '{collectiongroup}'),
            self.check('priority', '{collection_group_priority}')
        ])

        self.cmd('network firewall policy rule-collection-group list -g {rg} --policy-name {policy}', checks=[
            self.check('length(@)', 1),
            self.check('@[0].type', 'Microsoft.Network/FirewallPolicies/RuleCollectionGroups'),
            self.check('@[0].name', '{collectiongroup}'),
            self.check('@[0].priority', '{collection_group_priority}')
        ])

        self.cmd('network firewall policy rule-collection-group update -g {rg} --policy-name {policy} -n {collectiongroup} --priority 12000', checks=[
            self.check('type', 'Microsoft.Network/FirewallPolicies/RuleCollectionGroups'),
            self.check('name', '{collectiongroup}'),
            self.check('priority', 12000)
        ])

        self.cmd('az network firewall policy rule-collection-group collection add-nat-collection -n nat-collection \
                 --policy-name {policy} --rule-collection-group-name {collectiongroup} -g {rg} --collection-priority 10005 \
                 --action DNAT --rule-name network-rule --description "test" \
                 --destination-addresses "202.120.36.15" --source-addresses "202.120.36.13" "202.120.36.14" \
                 --translated-address 128.1.1.1 --translated-port 1234 \
                 --destination-ports 12000 --ip-protocols TCP UDP', checks=[
            self.check('length(ruleCollections)', 1),
            self.check('ruleCollections[0].ruleCollectionType', "FirewallPolicyNatRuleCollection"),
            self.check('ruleCollections[0].name', "nat-collection")
        ])

        self.cmd('network firewall policy rule-collection-group collection add-filter-collection -g {rg} --policy-name {policy} \
                 --rule-collection-group-name {collectiongroup} -n filter-collection-1 --collection-priority 13000 \
                 --action Allow --rule-name network-rule --rule-type NetworkRule \
                 --description "test" --destination-addresses "202.120.36.15" --source-addresses "202.120.36.13" "202.120.36.14" \
                 --destination-ports 12003 12004 --ip-protocols Any ICMP', checks=[
            self.check('length(ruleCollections)', 2),
            self.check('ruleCollections[1].ruleCollectionType', "FirewallPolicyFilterRuleCollection"),
            self.check('ruleCollections[1].name', "filter-collection-1")
        ])

        self.cmd('network firewall policy rule-collection-group collection add-filter-collection -g {rg} --policy-name {policy} \
                 --rule-collection-group-name {collectiongroup} -n filter-collection-2 --collection-priority 14000 \
                 --action Allow --rule-name application-rule --rule-type ApplicationRule \
                 --description "test" --destination-addresses "202.120.36.15" "202.120.36.16" --source-addresses "202.120.36.13" "202.120.36.14" --protocols Http=12800 Https=12801 \
                 --fqdn-tags AzureBackup HDInsight '
                 '--target-urls www.google.com www.bing.com '
                 '--enable-tls-inspection true',
                 checks=[
                     self.check('length(ruleCollections)', 3),
                     self.check('ruleCollections[2].ruleCollectionType', "FirewallPolicyFilterRuleCollection"),
                     self.check('ruleCollections[2].name', "filter-collection-2"),
                     self.check('ruleCollections[2].rules[0].ruleType', 'ApplicationRule'),
                     self.check('ruleCollections[2].rules[0].terminateTLS', True),
                     self.check('ruleCollections[2].rules[0].targetUrls', ['www.google.com', 'www.bing.com'])
                 ])

        self.cmd('az network firewall policy rule-collection-group collection add-nat-collection -n nat-collection-2 \
                                 --policy-name {policy} --rule-collection-group-name {collectiongroup} -g {rg} --collection-priority 1000 \
                                 --action DNAT --rule-name network-rule --description "test" \
                                 --destination-addresses "202.120.36.15" --source-addresses "202.120.36.13" "202.120.36.14" \
                                 --translated-fqdn www.google.com --translated-port 1234 \
                                 --destination-ports 12000 --ip-protocols TCP UDP', checks=[
            self.check('length(ruleCollections)', 4),
            self.check('ruleCollections[3].ruleCollectionType', "FirewallPolicyNatRuleCollection"),
            self.check('ruleCollections[3].name', "nat-collection-2")
        ])

        self.cmd('network firewall policy rule-collection-group collection list -g {rg} --policy-name {policy} \
                 --rule-collection-group-name {collectiongroup}', checks=[
            self.check('length(@)', 4)
        ])

        self.cmd('network firewall policy rule-collection-group collection rule add -g {rg} --policy-name {policy} '
                 '--rule-collection-group-name {collectiongroup} --collection-name filter-collection-2 --name application-rule-2 '
                 '--rule-type ApplicationRule --description "test" --source-addresses 202.120.36.13 202.120.36.14 '
                 '--destination-addresses 202.120.36.15 202.120.36.16 --protocols Http=12800 Https=12801 --target-fqdns www.bing.com',
                 checks=[
                     self.check('length(ruleCollections[2].rules)', 2),
                 ])

        self.cmd('network firewall policy rule-collection-group collection rule add -g {rg} --policy-name {policy} '
                 '--rule-collection-group-name {collectiongroup} --collection-name filter-collection-2 --name application-rule-3 '
                 '--rule-type ApplicationRule --description "test" --source-addresses 202.120.36.13 202.120.36.14 '
                 '--destination-addresses 10.120.36.15 10.120.36.16 --target-urls microsoft.com  ',
                 checks=[
                     self.check('length(ruleCollections[2].rules)', 3),
                     self.check('ruleCollections[2].rules[2].name', 'application-rule-3'),
                     self.check('ruleCollections[2].rules[2].terminateTLS', False),
                     self.check('ruleCollections[2].rules[2].targetUrls', "['microsoft.com']")
                 ])

        self.cmd('network firewall policy rule-collection-group collection rule add -g {rg} --policy-name {policy} \
                 --rule-collection-group-name {collectiongroup} --collection-name filter-collection-1 \
                 --name network-rule-2 --rule-type NetworkRule \
                 --description "test" --destination-addresses "202.120.36.15" --source-addresses "202.120.36.13" "202.120.36.14" \
                 --destination-ports 12003 12004 --ip-protocols Any ICMP', checks=[
            self.check('length(ruleCollections[1].rules)', 2)
        ])

        self.cmd('network firewall policy rule-collection-group collection rule remove -g {rg} --policy-name {policy} \
                 --rule-collection-group-name {collectiongroup} --collection-name filter-collection-1 --name network-rule-2', checks=[
            self.check('length(ruleCollections[1].rules)', 1),
            self.check('ruleCollections[1].rules[0].name', 'network-rule')
        ])

        self.cmd('network firewall policy rule-collection-group collection remove -g {rg} --policy-name {policy} \
                 --rule-collection-group-name {collectiongroup} --name filter-collection-1', checks=[
            self.check('length(ruleCollections)', 3)
        ])

        self.cmd('network firewall policy rule-collection-group delete -g {rg} --policy-name {policy} --name {collectiongroup} -y')

        self.cmd('network firewall policy rule-collection-group list -g {rg} --policy-name {policy}', checks=[
            self.check('length(@)', 0)
        ])

        self.cmd('network firewall policy delete -g {rg} --name {policy}')

    @ResourceGroupPreparer(name_prefix='test_firewall_policy_with_dns_settings')
    def test_firewall_policy_with_dns_settings(self, resource_group):
        self.kwargs.update({
            'rg': resource_group,
            'location': 'eastus',   # available only in this location for now
            'policy': 'fwp01',
            'dns_servers': '10.0.0.1 10.0.0.2 10.0.0.3',
        })

        creation_data = self.cmd('network firewall policy create '
                                 '--resource-group {rg} '
                                 '--location {location} '
                                 '--name {policy} '
                                 '--dns-servers {dns_servers} ').get_output_in_json()
        self.assertEqual(creation_data['name'], self.kwargs['policy'])
        self.assertEqual(creation_data['dnsSettings']['servers'], self.kwargs['dns_servers'].split())

        show_data = self.cmd('network firewall policy show --resource-group {rg} --name {policy}').get_output_in_json()
        self.assertEqual(show_data['name'], self.kwargs['policy'])
        self.assertEqual(show_data['dnsSettings']['servers'], self.kwargs['dns_servers'].split())

        self.cmd('network firewall policy update '
                 '--resource {rg} '
                 '--name {policy} '
                 '--dns-servers 10.0.1.0 '
                 '--enable-dns-proxy true ').get_output_in_json()
        show_data = self.cmd('network firewall policy show --resource-group {rg} --name {policy}').get_output_in_json()
        self.assertEqual(show_data['name'], self.kwargs['policy'])
        self.assertEqual(show_data['dnsSettings']['servers'], ['10.0.1.0'])  # update successfully
        self.assertEqual(show_data['dnsSettings']['enableProxy'], True)     # update succesefully

        self.cmd('network firewall policy update '
                 '--resource {rg} '
                 '--name {policy} ').get_output_in_json()
        show_data = self.cmd('network firewall policy show --resource-group {rg} --name {policy}').get_output_in_json()
        self.assertEqual(show_data['name'], self.kwargs['policy'])
        self.assertEqual(show_data['dnsSettings']['servers'], ['10.0.1.0'])
        self.assertEqual(show_data['dnsSettings']['enableProxy'], True)

        self.cmd('network firewall policy delete --resource-group {rg} --name {policy} ')

    @ResourceGroupPreparer(name_prefix='cli_test_azure_firewall_policy', location='westus2')
    def test_azure_firewall_policy_rules_with_fqdns(self, resource_group, resource_group_location):
        self.kwargs.update({
            'collectiongroup': 'myclirulecollectiongroup',
            'policy': 'myclipolicy',
            'rg': resource_group,
            'location': resource_group_location,
            'collection_group_priority': 10000,
            'source_ip_group': 'sourceipgroup',
            'destination_ip_group': 'destinationipgroup',
            'fw': 'fw1',
            'dns_servers': '10.0.0.2 10.0.0.3'
        })

        self.cmd('network ip-group create -n {source_ip_group} -g {rg} --ip-addresses 10.0.0.0 10.0.0.1')
        self.cmd('network firewall policy create '
                 '--resource-group {rg} '
                 '--location {location} '
                 '--name {policy} '
                 '--dns-servers {dns_servers} '
                 '--enable-dns-proxy',
                 checks=[
                     self.check('type', 'Microsoft.Network/FirewallPolicies'),
                     self.check('name', '{policy}')
                 ])

        self.cmd(
            'network firewall policy rule-collection-group create -g {rg} --priority {collection_group_priority} --policy-name {policy} -n {collectiongroup}',
            checks=[
                self.check('type', 'Microsoft.Network/FirewallPolicies/RuleCollectionGroups'),
                self.check('name', '{collectiongroup}')
            ])

        self.cmd('network firewall policy rule-collection-group collection add-filter-collection -g {rg} --policy-name {policy} '
                 '--rule-collection-group-name {collectiongroup} -n filter-collection-1 --collection-priority 15000 '
                 '--action Allow --rule-name network-rule --rule-type NetworkRule '
                 '--description "test" --destination-fqdns www.bing.com --source-ip-groups {source_ip_group} '
                 '--destination-ports 12003 12004 --ip-protocols Any ICMP',
                 checks=[
                     self.check('length(ruleCollections)', 1),
                     self.check('ruleCollections[0].ruleCollectionType', "FirewallPolicyFilterRuleCollection"),
                     self.check('ruleCollections[0].name', "filter-collection-1")
                 ])

        self.cmd('network firewall policy rule-collection-group collection rule add -g {rg} --policy-name {policy} '
                 '--rule-collection-group-name {collectiongroup} --collection-name filter-collection-1 '
                 '--name network-rule-2 --rule-type NetworkRule '
                 '--description "test" --destination-fqdns www.google.com --source-ip-groups {source_ip_group} '
                 '--destination-ports 12003 12004 --ip-protocols Any ICMP',
                 checks=[
                     self.check('length(ruleCollections[0].rules)', 2)
                 ])

        self.cmd('az network firewall policy rule-collection-group collection add-nat-collection -n nat-collection '
                 '--policy-name {policy} --rule-collection-group-name {collectiongroup} -g {rg} --collection-priority 10005 '
                 '--action DNAT --rule-name nat-rule --description "test" '
                 '--destination-addresses "202.120.36.15" --source-ip-groups {source_ip_group} '
                 '--translated-address 128.1.1.1 --translated-port 1234 '
                 '--destination-ports 12001 --ip-protocols TCP UDP',
                 checks=[
                     self.check('length(ruleCollections)', 2),
                     self.check('ruleCollections[1].ruleCollectionType', "FirewallPolicyNatRuleCollection"),
                     self.check('ruleCollections[1].name', "nat-collection"),
                     self.check('length(ruleCollections[1].rules)', 1)
                 ])

        self.cmd('network firewall policy rule-collection-group collection rule add -g {rg} --policy-name {policy} '
                 '--rule-collection-group-name {collectiongroup} --collection-name nat-collection '
                 '--name nat-rule-2 --rule-type NatRule --description "test" '
                 '--destination-addresses "202.120.36.16" --source-ip-groups {source_ip_group} '
                 '--translated-fqdn www.bing2.com --translated-port 1234 '
                 '--destination-ports 12000 --ip-protocols TCP UDP',
                 checks=[
                     self.check('length(ruleCollections[1].rules)', 2)
                 ])

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_azure_firewall_policy', location='westus2')
    def test_azure_firewall_policy_rules_with_ip_groups(self, resource_group, resource_group_location):
        self.kwargs.update({
            'collectiongroup': 'myclirulecollectiongroup',
            'policy': 'myclipolicy',
            'rg': resource_group,
            'location': resource_group_location,
            'collection_group_priority': 10000,
            'source_ip_group': 'sourceipgroup',
            'destination_ip_group': 'destinationipgroup'
        })

        self.cmd('network ip-group create -n {source_ip_group} -g {rg} --ip-addresses 10.0.0.0 10.0.0.1')
        self.cmd('network ip-group create -n {destination_ip_group} -g {rg} --ip-addresses 10.0.0.2 10.0.0.3')
        self.cmd('network firewall policy create -g {rg} -n {policy} -l {location}', checks=[
            self.check('type', 'Microsoft.Network/FirewallPolicies'),
            self.check('name', '{policy}')
        ])

        self.cmd(
            'network firewall policy rule-collection-group create -g {rg} --priority {collection_group_priority} --policy-name {policy} -n {collectiongroup}',
            checks=[
                self.check('type', 'Microsoft.Network/FirewallPolicies/RuleCollectionGroups'),
                self.check('name', '{collectiongroup}')
            ])

        self.cmd('az network firewall policy rule-collection-group collection add-nat-collection -n nat-collection '
                 '--policy-name {policy} --rule-collection-group-name {collectiongroup} -g {rg} --collection-priority 10005 '
                 '--action DNAT --rule-name nat-rule --description "test" '
                 '--destination-addresses "202.120.36.15" --source-ip-groups {source_ip_group} '
                 '--translated-address 128.1.1.1 --translated-port 1234 '
                 '--destination-ports 12000 --ip-protocols TCP UDP',
                 checks=[
                     self.check('length(ruleCollections)', 1),
                     self.check('ruleCollections[0].ruleCollectionType', "FirewallPolicyNatRuleCollection"),
                     self.check('ruleCollections[0].name', "nat-collection"),
                     self.check('length(ruleCollections[0].rules)', 1)
                 ])

        self.cmd('network firewall policy rule-collection-group collection add-filter-collection -g {rg} --policy-name {policy} '
                 '--rule-collection-group-name {collectiongroup} -n filter-collection-1 --collection-priority 13000 '
                 '--action Allow --rule-name network-rule --rule-type NetworkRule '
                 '--description "test" --destination-ip-groups {destination_ip_group} --source-ip-groups {source_ip_group} '
                 '--destination-ports 12003 --ip-protocols Any ICMP',
                 checks=[
                     self.check('length(ruleCollections)', 2),
                     self.check('ruleCollections[1].ruleCollectionType', "FirewallPolicyFilterRuleCollection"),
                     self.check('ruleCollections[1].name', "filter-collection-1")
                 ])

        self.cmd('network firewall policy rule-collection-group collection add-filter-collection -g {rg} --policy-name {policy} '
                 '--rule-collection-group-name {collectiongroup} -n filter-collection-2 --collection-priority 14000 '
                 '--action Allow --rule-name application-rule --rule-type ApplicationRule '
                 '--description "test" --destination-addresses "202.120.36.15" "202.120.36.16" '
                 '--source-ip-groups {source_ip_group} --protocols Http=12800 Https=12801 '
                 '--fqdn-tags AzureBackup HDInsight --web-categories Hacking',
                 checks=[
                     self.check('length(ruleCollections)', 3),
                     self.check('ruleCollections[2].ruleCollectionType', "FirewallPolicyFilterRuleCollection"),
                     self.check('ruleCollections[2].name', "filter-collection-2"),
                     self.check('length(ruleCollections[2].rules[0].webCategories)', 1)
                 ])

        self.cmd('network firewall policy rule-collection-group collection list -g {rg} --policy-name {policy} '
                 '--rule-collection-group-name {collectiongroup}',
                 checks=[
                     self.check('length(@)', 3)
                 ])

        self.cmd('network firewall policy rule-collection-group collection rule add -g {rg} --policy-name {policy} '
                 '--rule-collection-group-name {collectiongroup} --collection-name filter-collection-2 --name application-rule-2 '
                 '--rule-type ApplicationRule --description "test" --source-ip-groups {source_ip_group} '
                 '--destination-addresses 202.120.36.15 202.120.36.16 --protocols Http=12800 Https=12801 --target-fqdns www.bing.com',
                 checks=[
                     self.check('length(ruleCollections[2].rules)', 2)
                 ])

        self.cmd('network firewall policy rule-collection-group collection rule update -g {rg} --policy-name {policy} '
                 '--rule-collection-group-name {collectiongroup} --collection-name filter-collection-2 --name application-rule-2 '
                 '--target-fqdns www.google0.com www.google1.com www.google2.com --web-categories Hacking Hacking',
                 checks=[
                     self.check('length(ruleCollections[2].rules)', 2),
                     self.check('length(ruleCollections[2].rules[1].targetFqdns)', 3),
                     self.check('length(ruleCollections[2].rules[1].webCategories)', 2),
                 ])

        self.cmd('network firewall policy rule-collection-group collection rule add -g {rg} --policy-name {policy} '
                 '--rule-collection-group-name {collectiongroup} --collection-name filter-collection-1 '
                 '--name network-rule-2 --rule-type NetworkRule '
                 '--description "test" --destination-ip-groups {destination_ip_group} --source-ip-groups {source_ip_group} '
                 '--destination-ports 12003 12004 --ip-protocols Any ICMP',
                 checks=[
                     self.check('length(ruleCollections[1].rules)', 2)
                 ])

        self.cmd('network firewall policy rule-collection-group collection rule add -g {rg} --policy-name {policy} '
                 '--rule-collection-group-name {collectiongroup} --collection-name nat-collection '
                 '--name nat-rule-2 --rule-type NatRule --description "test" '
                 '--destination-addresses "202.120.36.16" --source-ip-groups {source_ip_group} '
                 '--translated-address 128.1.1.1 --translated-port 1234 '
                 '--destination-ports 12000 --ip-protocols TCP UDP',
                 checks=[
                     self.check('length(ruleCollections[0].rules)', 2)
                 ])

        self.cmd('network firewall policy rule-collection-group collection rule remove -g {rg} --policy-name {policy} '
                 '--rule-collection-group-name {collectiongroup} --collection-name filter-collection-1 --name network-rule-2',
                 checks=[
                     self.check('length(ruleCollections[1].rules)', 1),
                     self.check('ruleCollections[1].rules[0].name', 'network-rule')
                 ])

        self.cmd('network firewall policy rule-collection-group collection rule remove -g {rg} --policy-name {policy} '
                 '--rule-collection-group-name {collectiongroup} --collection-name nat-collection --name nat-rule-2',
                 checks=[
                     self.check('length(ruleCollections[0].rules)', 1),
                     self.check('ruleCollections[0].rules[0].name', 'nat-rule')
                 ])

        self.cmd('network firewall policy rule-collection-group collection remove -g {rg} --policy-name {policy} '
                 '--rule-collection-group-name {collectiongroup} --name filter-collection-1',
                 checks=[
                     self.check('length(ruleCollections)', 2)
                 ])

        self.cmd('network firewall policy rule-collection-group delete -g {rg} --policy-name {policy} --name {collectiongroup} -y')

        self.cmd('network firewall policy rule-collection-group list -g {rg} --policy-name {policy}', checks=[
            self.check('length(@)', 0)
        ])

        self.cmd('network firewall policy delete -g {rg} --name {policy}')

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='test_azure_firewall_policy_explicit_proxy', location='westus2')
    def test_azure_firewall_policy_explicit_proxy(self, resource_group):
        self.kwargs.update({
            'policy_name': 'testFirewallPolicy',
            'sas_url': "https://clitestatorageaccount.blob.core.windows.net/explicitproxycontainer/pacfile.pac?sp=r&st=2024-01-09T08:48:06Z&se=2024-01-09T16:48:06Z&spr=https&sv=2022-11-02&sr=b&sig=5B0q%2B90BH0fkPZK6G6LHKRIGMY%2FljNOfsSQ8xaQB6mw%3D"
        })
        self.cmd('network firewall policy create -g {rg} -n {policy_name} --sku Premium --explicit-proxy enable-explicit-proxy=true http-port=85 https-port=121 enable-pac-file=true pac-file-port=122 pac-file="{sas_url}"',
                 checks=[
                     self.check('name', '{policy_name}'),
                     self.check('explicitProxy.enableExplicitProxy', True),
                     self.check('explicitProxy.enablePacFile', True),
                     self.check('explicitProxy.httpPort', 85),
                     self.check('explicitProxy.httpsPort', 121),
                     self.check('explicitProxy.pacFile', '{sas_url}'),
                     self.check('explicitProxy.pacFilePort', 122),
                 ])

        self.cmd(
            'network firewall policy update -g {rg} -n {policy_name} --explicit-proxy enable-explicit-proxy=true http-port=86 https-port=123 enable-pac-file=true pac-file-port=124 pac-file="{sas_url}"',
            checks=[
                self.check('name', '{policy_name}'),
                self.check('explicitProxy.enableExplicitProxy', True),
                self.check('explicitProxy.enablePacFile', True),
                self.check('explicitProxy.httpPort', 86),
                self.check('explicitProxy.httpsPort', 123),
                self.check('explicitProxy.pacFile', '{sas_url}'),
                self.check('explicitProxy.pacFilePort', 124),
            ])

    @ResourceGroupPreparer(name_prefix='test_firewall_with_dns_proxy_')
    def test_firewall_with_dns_proxy(self, resource_group):
        self.kwargs.update({
            'rg': resource_group,
            'fw': 'fw01',
            'dns_servers': '10.0.0.2 10.0.0.3'
        })

        self.cmd('network firewall create -g {rg} -n {fw} '
                 '--dns-servers {dns_servers} '
                 '--enable-dns-proxy false',
                 checks=[
                     self.check('name', '{fw}'),
                     self.check('additionalProperties."Network.DNS.Servers"', "10.0.0.2,10.0.0.3"),
                     self.check('additionalProperties."Network.DNS.EnableProxy"', 'false'),
                 ])

        self.cmd('network firewall show -g {rg} -n {fw}',
                 checks=[
                     self.check('name', '{fw}'),
                     self.check('additionalProperties."Network.DNS.Servers"', "10.0.0.2,10.0.0.3"),
                     self.check('additionalProperties."Network.DNS.EnableProxy"', 'false'),
                 ])

        self.cmd('network firewall update -g {rg} -n {fw} '
                 '--enable-dns-proxy true').get_output_in_json()

        self.cmd('network firewall show -g {rg} -n {fw}',
                 checks=[
                     self.check('name', '{fw}'),
                     self.check('additionalProperties."Network.DNS.Servers"', "10.0.0.2,10.0.0.3"),
                     self.check('additionalProperties."Network.DNS.EnableProxy"', 'true'),
                 ])

        self.cmd('network firewall delete -g {rg} --name {fw}')

    @ResourceGroupPreparer(name_prefix='test_azure_firewall_tier', location='eastus2euap')
    def test_azure_firewall_tier(self, resource_group):
        self.kwargs.update({
            'rg': resource_group
        })
        self.cmd('network firewall create -g {rg} -n af --sku AZFW_VNet --tier Premium',
                 checks=self.check('sku.tier', 'Premium'))

    # BUG ISSUE: https://github.com/Azure/azure-cli-extensions/issues/4096
    @ResourceGroupPreparer(name_prefix='test_azure_firewall_policy_update_premiumonlyproperty_issue', location='westus2')
    def test_azure_firewall_policy_update_premiumonlyproperty_issue(self, resource_group):
        self.kwargs.update({
            'policy': 'testpolicy'
        })

        self.cmd('network firewall policy create -g {rg} -n {policy} --sku Standard --threat-intel-mode Alert')

        self.cmd('network firewall policy update -g {rg} -n {policy} --threat-intel-mode Deny')

    @ResourceGroupPreparer(name_prefix='test_azure_firewall_policy_with_sql', location='eastus2euap')
    def test_azure_firewall_policy_with_sql(self, resource_group):
        self.kwargs.update({
            'policy': 'testpolicy'
        })

        self.cmd('network firewall policy create -g {rg} -n {policy} --sql true',
                 checks=self.check('sql.allowSqlRedirect', True))

        self.cmd('network firewall policy update -g {rg} -n {policy} --sql False',
                 checks=self.check('sql.allowSqlRedirect', False))

    @AllowLargeResponse(size_kb=10240)
    @ResourceGroupPreparer(name_prefix="cli_test_firewall_basic_sku_", location="westus")
    def test_firewall_basic_sku(self):
        self.kwargs.update({
            "firewall_name": self.create_random_name("firewall-", 16),
            "vnet_name": self.create_random_name("vnet-", 12),
            "conf_name": self.create_random_name("ipconfig-", 16),
            "m_conf_name": self.create_random_name("ipconfig-", 16),
            "m_public_ip_name": self.create_random_name("public-ip-", 16),
            "vwan": self.create_random_name("vwan-", 12),
            "vhub": self.create_random_name("vhub-", 12),
        })

        with self.assertRaisesRegex(ValidationError, "When creating Basic SKU firewall, both --m-conf-name and --m-public-ip-address should be provided."):
            self.cmd("network firewall create -n {firewall_name} -g {rg} --sku AZFW_VNet --tier Basic")

        self.cmd("network vnet create -n {vnet_name} -g {rg} --address-prefixes 10.0.0.0/16 --subnet-name AzureFirewallSubnet --subnet-prefixes 10.0.0.0/24")
        self.cmd("network vnet subnet create -n AzureFirewallManagementSubnet -g {rg} --vnet-name {vnet_name} --address-prefixes 10.0.1.0/24")
        self.cmd("network public-ip create -n {m_public_ip_name} -g {rg} --sku Standard")

        self.cmd(
            "network firewall create -n {firewall_name} -g {rg} --sku AZFW_VNet --tier Basic --vnet-name {vnet_name} "
            "--conf-name {conf_name} --m-conf-name {m_conf_name} --m-public-ip {m_public_ip_name}",
            checks=[
                self.check("name", "{firewall_name}"),
                self.check("sku.tier", "Basic")
            ]
        )
        self.cmd("network firewall delete -n {firewall_name} -g {rg}")

        self.cmd("extension add -n virtual-wan")
        self.cmd("network vwan create -n {vwan} -g {rg} --type Standard")
        self.cmd('network vhub create -n {vhub} -g {rg} --vwan {vwan}  --address-prefix 10.0.0.0/24 -l westus --sku Standard')
        self.cmd(
            "network firewall create -n {firewall_name} -g {rg} --vhub {vhub} --public-ip-count 2 --sku AZFW_Hub --tier Basic",
            checks=[
                self.check("name", "{firewall_name}"),
                self.check("sku.name", "AZFW_Hub")
            ]
        )

    @AllowLargeResponse(size_kb=10240)
    @ResourceGroupPreparer(name_prefix="cli_test_firewall_with_route_server_", location="eastus2euap")
    def test_firewall_with_route_server(self):
        self.kwargs.update({
            "firewall_name": self.create_random_name("firewall-", 16),
            "vwan": self.create_random_name("vwan-", 12),
            "vhub": self.create_random_name("vhub-", 12),
        })

        self.cmd("extension add -n virtual-wan")
        self.cmd("network vwan create -n {vwan} -g {rg} --type Standard")
        vhub = self.cmd('network vhub create -n {vhub} -g {rg} --vwan {vwan} --address-prefix 10.0.0.0/24 -l westus --sku Standard').get_output_in_json()
        self.kwargs['route_server_id'] = vhub['id']

        self.cmd("network firewall create -n {firewall_name} -g {rg} -l eastus2euap --route-server-id {route_server_id}",
                 self.check("additionalProperties.\"Network.RouteServerInfo.RouteServerID\"", "{route_server_id}"))
        self.cmd("network firewall update -n {firewall_name} -g {rg} --route-server-id ''",
                 self.check("additionalProperties.\"Network.RouteServerInfo.RouteServerID\"", ""))
        self.cmd("network firewall delete -n {firewall_name} -g {rg}")

    @AllowLargeResponse(size_kb=10240)
    @ResourceGroupPreparer(name_prefix="cli_test_azure_firewall_policy_with_snat_", location="westus")
    def test_azure_firewall_policy_with_snat(self, resource_group):
        self.kwargs.update({
            'af': 'af1',
            'af2': 'af2',
            'policy': 'myclipolicy',
            'policy2': 'myclipolicy2',
            'coll': 'rc1',
            'rg': resource_group,
            'ipconfig': 'myipconfig1',
            'location': "westus",
        })

        self.cmd('network firewall policy create -g {rg} -n {policy} -l {location} --private-ranges IANAPrivateRanges --learn-ranges Enabled', checks=[
            self.check('type', 'Microsoft.Network/FirewallPolicies'),
            self.check('length(snat.privateRanges)', 4),
            self.check('snat.autoLearnPrivateRanges', 'Enabled')
        ])

        self.cmd(
            'network firewall policy update -g {rg} -n {policy} --private-ranges "0.0.0.0/0" --learn-ranges Disabled',
            checks=[
                self.check('type', 'Microsoft.Network/FirewallPolicies'),
                self.check('length(snat.privateRanges)', 1),
            ])

        self.cmd("network firewall policy delete -n {policy} -g {rg}")


    @ResourceGroupPreparer(name_prefix='cli_test_azure_firewall_policy_app_rules_with_custom_headers_', location="westus2")
    def test_azure_firewall_policy_app_rules_with_custom_headers(self, resource_group):
        self.kwargs.update({
            'location': "westus2",
            'rg': resource_group,
            'policy_name': 'policy1',
            'rule_collection_group_name': 'RCG1',
            'rule_collection_name': 'RC1',
            'app_rule_name_1': 'app-rule1',
            'header_name_1': 'MyHeaderName',
            'header_value_1': 'MyHeaderValue',
            'app_rule_name_2': 'app-rule2',
            'header_name_2': 'MyHeaderName2',
            'header_value_2': 'MyHeaderValue2',
            'header_name_3': 'MyHeaderName3',
            'header_value_3': 'MyHeaderValue3'
        })
        
        # Create policy
        self.cmd('network firewall policy create -g {rg} -n {policy_name} -l {location} --sku Premium --idps-mode Off', 
            checks=[
                    self.check('type', 'Microsoft.Network/FirewallPolicies'),
                    self.check('name', '{policy_name}')
        ])

        # Create RCG
        self.cmd('network firewall policy rule-collection-group create -g {rg} --priority 400 --policy-name {policy_name} -n {rule_collection_group_name}', 
                checks=[
                    self.check('type', 'Microsoft.Network/FirewallPolicies/RuleCollectionGroups'),
                    self.check('name', '{rule_collection_group_name}')
        ])

        # Add a new RC with app rule with custom headers to RCG
        self.cmd('network firewall policy rule-collection-group collection add-filter-collection -g {rg} --policy-name {policy_name} \
                 --rule-collection-group-name {rule_collection_group_name} -n {rule_collection_name} --collection-priority 13000 \
                 --action Allow --rule-name {app_rule_name_1} --rule-type ApplicationRule \
                 --source-addresses 202.120.36.13 202.120.36.14 --destination-addresses 10.120.36.15 10.120.36.16 --target-urls microsoft.com \
                 --http-headers-to-insert {header_name_1}={header_value_1} ',
                 checks=[
                    self.check('length(ruleCollections)', 1),
                    self.check('ruleCollections[0].ruleCollectionType', "FirewallPolicyFilterRuleCollection"),
                    self.check('ruleCollections[0].name', "{rule_collection_name}"),
                    self.check('length(ruleCollections[0].rules)', 1),
                    self.check('ruleCollections[0].rules[0].name', '{app_rule_name_1}'),
                    self.check('ruleCollections[0].rules[0].httpHeadersToInsert[0].headerName', "{header_name_1}"),
                    self.check('ruleCollections[0].rules[0].httpHeadersToInsert[0].headerValue', "{header_value_1}")
                ])

        self.cmd('network firewall policy rule-collection-group collection rule add -g {rg} --policy-name {policy_name} \
                --rule-collection-group-name {rule_collection_group_name} --collection-name {rule_collection_name} --name {app_rule_name_2} \
                --rule-type ApplicationRule --description "test" --source-addresses 202.120.22.11 202.120.11.11 \
                --destination-addresses 10.120.36.11 --protocols Http=12800 --target-fqdns microsoft.com \
                --http-headers-to-insert {header_name_2}={header_value_2} {header_name_3}={header_value_3}',
                checks=[
                    self.check('length(ruleCollections[0].rules)',2),
                    self.check('ruleCollections[0].rules[1].name', '{app_rule_name_2}'),
                    self.check('ruleCollections[0].rules[1].httpHeadersToInsert[0].headerName', "{header_name_2}"),
                    self.check('ruleCollections[0].rules[1].httpHeadersToInsert[0].headerValue', "{header_value_2}"),
                    self.check('ruleCollections[0].rules[1].httpHeadersToInsert[1].headerName', "{header_name_3}"),
                    self.check('ruleCollections[0].rules[1].httpHeadersToInsert[1].headerValue', "{header_value_3}")
            ])      

        # delete Rule
        self.cmd('network firewall policy rule-collection-group collection rule remove -g {rg} --policy-name {policy_name} \
                --rule-collection-group-name {rule_collection_group_name} --collection-name {rule_collection_name} --name {app_rule_name_2}',
                checks=[
                    self.check('length(ruleCollections[0].rules)', 1),
                    self.check('ruleCollections[0].rules[0].name', '{app_rule_name_1}')
                ])

        # delete RC
        self.cmd('network firewall policy rule-collection-group collection remove -g {rg} --policy-name {policy_name} \
                 --rule-collection-group-name {rule_collection_group_name} --name {rule_collection_name}', 
                 checks=[
            self.check('length(ruleCollections)', 0)
        ])

        # delete RCG
        self.cmd('network firewall policy rule-collection-group delete -g {rg} --policy-name {policy_name} --name {rule_collection_group_name} -y')
        self.cmd('network firewall policy rule-collection-group list -g {rg} --policy-name {policy_name}', 
        checks=[
            self.check('length(@)', 0)
        ])

    @AllowLargeResponse(size_kb=10240)
    @ResourceGroupPreparer(name_prefix='cli_test_azure_firewall_policy_draft', location='westus2')
    def test_azure_policy_draft(self, resource_group, resource_group_location):
        self.kwargs.update({
            'policy': 'myclipolicy',
            'rg': resource_group,
            'ipconfig': 'myipconfig1',
            'location': resource_group_location,
            'collectiongroup': 'myclirulecollectiongroup',
            'collection_group_priority': 10000
        })        
        self.cmd('network firewall policy create -g {rg} -n {policy} -l {location} --sku Premium --idps-mode Off', checks=[
            self.check('type', 'Microsoft.Network/FirewallPolicies'),
            self.check('name', '{policy}')
        ])

        self.kwargs.update({'location': 'westus2'})
        self.cmd('network firewall policy draft create -g {rg} --policy-name {policy}', checks=[
            self.check('type', 'Microsoft.Network/FirewallPolicies/FirewallPolicyDrafts'),
            self.check('name', '{policy}')
        ])

        self.cmd(
            'network firewall policy draft update -g {rg} --policy-name {policy} --threat-intel-mode Deny --idps-mode Alert',
            checks=[
                self.check('type', 'Microsoft.Network/FirewallPolicies/FirewallPolicyDrafts'),
                self.check('threatIntelMode', 'Deny'),
                self.check('name', '{policy}'),
                self.check('intrusionDetection.mode', 'Alert')
                 ])

        self.cmd('network firewall policy draft intrusion-detection add -g {rg} --policy-name {policy} --mode Deny --signature-id 10001 --private-ranges 167.220.204.0/24 167.221.205.101/32',
                 checks=[
                     self.check('bypassTrafficSettings', []),
                     self.check('length(signatureOverrides)', 1),
                     self.check('signatureOverrides[0]', {'id': '10001', 'mode': 'Deny'}),
                     self.check('privateRanges[0]', "167.220.204.0/24"),
                     self.check('privateRanges[1]', "167.221.205.101/32")
                 ])

        self.cmd('network firewall policy draft intrusion-detection add -g {rg} --policy-name {policy} --mode Alert --signature-id 20001 --private-ranges 167.220.208.0/24 167.221.205.102/32',
                 checks=[
                     self.check('bypassTrafficSettings', []),
                     self.check('length(signatureOverrides)', 2),
                     self.check('signatureOverrides[0]', {'id': '10001', 'mode': 'Deny'}),
                     self.check('signatureOverrides[1]', {'id': '20001', 'mode': 'Alert'}),
                     self.check('privateRanges[0]', "167.220.208.0/24"),
                     self.check('privateRanges[1]', "167.221.205.102/32")
                 ])

        self.cmd('network firewall policy draft intrusion-detection add -g {rg} --policy-name {policy} '
                 '--rule-name bypass-rule-1 '
                 '--rule-protocol TCP '
                 '--rule-src-addresses 10.0.0.12 10.0.0.15 '
                 '--rule-dest-addresses 192.168.0.103 192.168.0.104 '
                 '--rule-dest-ports 8080 9090 5432',
                 checks=[
                     self.check('length(bypassTrafficSettings)', 1),
                     self.check('bypassTrafficSettings[0].description', None),
                     self.check('bypassTrafficSettings[0].destinationAddresses', ['192.168.0.103', '192.168.0.104']),
                     self.check('bypassTrafficSettings[0].destinationIpGroups', None),
                     self.check('bypassTrafficSettings[0].protocol', 'TCP'),
                     self.check('bypassTrafficSettings[0].destinationPorts', ['8080', '9090', '5432']),
                     self.check('length(signatureOverrides)', 2),
                     self.check('signatureOverrides[0]', {'id': '10001', 'mode': 'Deny'}),
                     self.check('signatureOverrides[1]', {'id': '20001', 'mode': 'Alert'}),
                 ])

        self.cmd('network firewall policy draft intrusion-detection list -g {rg} --policy-name {policy}',
                 checks=[
                     self.check('length(bypassTrafficSettings)', 1),
                     self.check('length(signatureOverrides)', 2),
                     self.check('length(privateRanges)', 2)
                 ])

        self.cmd('network firewall policy draft intrusion-detection remove -g {rg} --policy-name {policy} '
                 '--rule-name bypass-rule-1 '
                 '--signature-id 10001')

        self.cmd('network firewall policy draft intrusion-detection list -g {rg} --policy-name {policy}',
                 checks=[
                     self.check('length(bypassTrafficSettings)', 0),
                     self.check('length(signatureOverrides)', 1),
                     self.check('length(privateRanges)', 2)
                 ])

        self.cmd('network firewall policy show -g {rg} -n {policy}',
                 checks=[
                     self.check('threatIntelMode', 'Alert')
                 ])

        self.cmd('network firewall policy deploy -g {rg} --name {policy}')

        self.cmd('network firewall policy show -g {rg} -n {policy}',
                 checks=[
                     self.check('threatIntelMode', 'Deny')
                 ])

        self.cmd('network firewall policy intrusion-detection list -g {rg} --policy-name {policy}',
                 checks=[
                     self.check('length(bypassTrafficSettings)', 0),
                     self.check('length(signatureOverrides)', 1),
                     self.check('length(privateRanges)', 2)
                 ])

        self.cmd('network firewall policy delete -g {rg} --name {policy}')


    @AllowLargeResponse(size_kb=10240)
    @ResourceGroupPreparer(name_prefix='cli_test_azure_firewall_policy_draft', location='westus2')
    def test_azure_policy_rcg_draft(self, resource_group, resource_group_location):
        self.kwargs.update({
            'policy': 'myclipolicy',
            'rg': resource_group,
            'ipconfig': 'myipconfig1',
            'location': resource_group_location,
            'collectiongroup': 'myclirulecollectiongroup',
            'collection_group_priority': 10000
        })        
        self.cmd('network firewall policy create -g {rg} -n {policy} -l {location}', checks=[
            self.check('type', 'Microsoft.Network/FirewallPolicies'),
            self.check('name', '{policy}')
        ])

        self.kwargs.update({'location': 'westus2'})
        self.cmd('network firewall policy draft create -g {rg} --policy-name {policy}', checks=[
            self.check('type', 'Microsoft.Network/FirewallPolicies/FirewallPolicyDrafts'),
            self.check('name', '{policy}')
        ])

        self.cmd('network firewall policy rule-collection-group create -g {rg} --priority {collection_group_priority} --policy-name {policy} --name {collectiongroup}', checks=[
            self.check('type', 'Microsoft.Network/FirewallPolicies/RuleCollectionGroups'),
            self.check('name', '{collectiongroup}')
            ])

        self.cmd('network firewall policy rule-collection-group draft create -g {rg} --rule-collection-group-name {collectiongroup} --priority 150 --policy-name {policy}', checks=[
            self.check('type', 'Microsoft.Network/FirewallPolicies/RuleCollectionGroups/RuleCollectionGroupDrafts'),
            self.check('name', '{collectiongroup}'),
            self.check('priority', 150)
        ])

        self.cmd('network firewall policy rule-collection-group draft update -g {rg} --policy-name {policy}  --rule-collection-group-name {collectiongroup} --priority 12000', checks=[
            self.check('priority', 12000)
        ])

        self.cmd('network firewall policy rule-collection-group draft show -g {rg} --policy-name {policy} --rule-collection-group-name {collectiongroup}', checks=[
            self.check('priority', 12000)
        ])

        self.cmd('az network firewall policy rule-collection-group draft collection add-nat-collection -n nat-collection \
                 --policy-name {policy} --rule-collection-group-name {collectiongroup} -g {rg} --collection-priority 10005 \
                 --action DNAT --rule-name network-rule --description "test" \
                 --destination-addresses "202.120.36.15" --source-addresses "202.120.36.13" "202.120.36.14" \
                 --translated-address 128.1.1.1 --translated-port 1234 \
                 --destination-ports 12000 --ip-protocols TCP UDP', checks=[
            self.check('length(ruleCollections)', 1),
            self.check('ruleCollections[0].ruleCollectionType', "FirewallPolicyNatRuleCollection"),
            self.check('ruleCollections[0].name', "nat-collection")
        ])

        self.cmd('network firewall policy rule-collection-group draft collection add-filter-collection -g {rg} --policy-name {policy} \
                 --rule-collection-group-name {collectiongroup} -n filter-collection-1 --collection-priority 13000 \
                 --action Allow --rule-name network-rule --rule-type NetworkRule \
                 --description "test" --destination-addresses "202.120.36.15" --source-addresses "202.120.36.13" "202.120.36.14" \
                 --destination-ports 12003 12004 --ip-protocols Any ICMP', checks=[
            self.check('length(ruleCollections)', 2),
            self.check('ruleCollections[1].ruleCollectionType', "FirewallPolicyFilterRuleCollection"),
            self.check('ruleCollections[1].name', "filter-collection-1")
        ])

        self.cmd('network firewall policy rule-collection-group draft collection add-filter-collection -g {rg} --policy-name {policy} \
                 --rule-collection-group-name {collectiongroup} -n filter-collection-2 --collection-priority 14000 \
                 --action Allow --rule-name application-rule --rule-type ApplicationRule \
                 --description "test" --destination-addresses "202.120.36.15" "202.120.36.16" --source-addresses "202.120.36.13" "202.120.36.14" --protocols Http=12800 Https=12801 \
                 --fqdn-tags AzureBackup HDInsight '
                 '--target-urls www.google.com www.bing.com '
                 '--enable-tls-inspection true',
                 checks=[
                     self.check('length(ruleCollections)', 3),
                     self.check('ruleCollections[2].ruleCollectionType', "FirewallPolicyFilterRuleCollection"),
                     self.check('ruleCollections[2].name', "filter-collection-2"),
                     self.check('ruleCollections[2].rules[0].ruleType', 'ApplicationRule'),
                     self.check('ruleCollections[2].rules[0].terminateTLS', True),
                     self.check('ruleCollections[2].rules[0].targetUrls', ['www.google.com', 'www.bing.com'])
                 ])

        self.cmd('az network firewall policy rule-collection-group draft collection add-nat-collection -n nat-collection-2 \
                                 --policy-name {policy} --rule-collection-group-name {collectiongroup} -g {rg} --collection-priority 1000 \
                                 --action DNAT --rule-name network-rule --description "test" \
                                 --destination-addresses "202.120.36.15" --source-addresses "202.120.36.13" "202.120.36.14" \
                                 --translated-fqdn www.google.com --translated-port 1234 \
                                 --destination-ports 12000 --ip-protocols TCP UDP', checks=[
            self.check('length(ruleCollections)', 4),
            self.check('ruleCollections[3].ruleCollectionType', "FirewallPolicyNatRuleCollection"),
            self.check('ruleCollections[3].name', "nat-collection-2")
        ])

        self.cmd('network firewall policy rule-collection-group draft collection rule add -g {rg} --policy-name {policy} '
                 '--rule-collection-group-name {collectiongroup} --collection-name filter-collection-2 --name application-rule-2 '
                 '--rule-type ApplicationRule --description "test" --source-addresses 202.120.36.13 202.120.36.14 '
                 '--destination-addresses 202.120.36.15 202.120.36.16 --protocols Http=12800 Https=12801 --target-fqdns www.bing.com',
                 checks=[
                     self.check('length(ruleCollections[2].rules)', 2),
                 ])
        
        self.cmd('network firewall policy rule-collection-group draft collection rule update -g {rg} --policy-name {policy} '
                 '--rule-collection-group-name {collectiongroup} --collection-name filter-collection-2 --name application-rule-2 '
                 '--description "test" --source-addresses 202.120.36.13 202.120.36.14 '
                 '--destination-addresses 202.120.36.15 202.120.36.16 --protocols Http=12800 Https=12801 --target-fqdns www.bing.com',
                 checks=[
                     self.check('length(ruleCollections[2].rules)', 2),
                 ])

        self.cmd('network firewall policy rule-collection-group draft collection list -g {rg} --policy-name {policy} \
                 --rule-collection-group-name {collectiongroup}', checks=[
            self.check('length(@)', 4)
        ])

        self.cmd('network firewall policy rule-collection-group draft collection rule remove -g {rg} --policy-name {policy} \
                 --rule-collection-group-name {collectiongroup} --collection-name filter-collection-1 --name network-rule-2', checks=[
            self.check('length(ruleCollections[1].rules)', 1),
            self.check('ruleCollections[1].rules[0].name', 'network-rule')
        ])

        self.cmd('network firewall policy rule-collection-group draft collection remove -g {rg} --policy-name {policy} \
                 --rule-collection-group-name {collectiongroup} --name filter-collection-1', checks=[
            self.check('length(ruleCollections)', 3)
        ])

        self.cmd('network firewall policy rule-collection-group draft show -g {rg} --policy-name {policy} --rule-collection-group-name {collectiongroup}',
                  checks=[
            self.check('length(ruleCollections[1].rules)', 2),
            self.check('ruleCollections[1].rules[0].name', 'application-rule'),
            self.check('length(ruleCollections)', 3)
        ])

        self.cmd('network firewall policy deploy -g {rg} --name {policy}')

        self.cmd('network firewall policy rule-collection-group show -g {rg} --policy-name {policy} --name {collectiongroup}',
                  checks=[
            self.check('length(ruleCollections[1].rules)', 2),
            self.check('ruleCollections[1].rules[0].name', 'application-rule'),
            self.check('length(ruleCollections)', 3)
        ])

        self.cmd('network firewall policy delete -g {rg} --name {policy}')


    @AllowLargeResponse(size_kb=10240)
    @ResourceGroupPreparer(name_prefix='cli_test_azure_firewall_policy_idps_profiles', location='westus2')
    def test_azure_policy_idps_profiles(self, resource_group, resource_group_location):
        self.kwargs.update({
            'location': "westus2",
            'rg': resource_group,
            'policy_name_1': 'policy1',
            'policy_name_2': 'policy2',
        })

        # create policy without idps profile        
        self.cmd('network firewall policy create -g {rg} -n {policy_name_1} -l {location} --sku Premium', 
                 checks=[
                    self.check('type', 'Microsoft.Network/FirewallPolicies'),
                    self.check('name', '{policy_name_1}')
        ])

        # add idps mode and profile to policy        
        self.cmd('network firewall policy update -g {rg} -n {policy_name_1} --idps-mode Alert --idps-profile Advanced',
                 checks=[
                     self.check('intrusionDetection.mode', 'Alert'),
                     self.check('intrusionDetection.profile', 'Advanced')
                 ])
        
        # delete policy 1
        self.cmd('network firewall policy delete -g {rg} --name {policy_name_1}')

        # create policy 2 with idps profile        
        self.cmd('network firewall policy create -g {rg} -n {policy_name_2} -l {location} --sku Premium --idps-mode Deny --idps-profile Standard',
                 checks=[
                     self.check('type', 'Microsoft.Network/FirewallPolicies'),
                     self.check('name', '{policy_name_2}'),
                     self.check('intrusionDetection.mode', 'Deny'),
                     self.check('intrusionDetection.profile', 'Standard')
        ])

        # change idps profile in policy 2
        self.cmd('network firewall policy update -g {rg} -n {policy_name_2} --idps-mode Deny --idps-profile Basic',
                 checks=[
                     self.check('intrusionDetection.mode', 'Deny'),
                     self.check('intrusionDetection.profile', 'Basic')
        ])  

        # delete policy 2
        self.cmd('network firewall policy delete -g {rg} --name {policy_name_2}')
