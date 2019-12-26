# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, StorageAccountPreparer, JMESPathCheck, NoneCheck,
                               api_version_constraint)


class AzureFirewallScenario(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_azure_firewall')
    def test_azure_firewall(self, resource_group):

        self.kwargs.update({
            'af': 'af1',
            'coll': 'rc1',
            'rule1': 'rule1',
            'rule2': 'rule2'
        })
        self.cmd('network firewall create -g {rg} -n {af}')
        self.cmd('network firewall show -g {rg} -n {af}')
        self.cmd('network firewall list -g {rg}')
        self.cmd('network firewall delete -g {rg} -n {af}')

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
        vnet_instance = self.cmd('network vnet create -g {rg} -n {vnet} --subnet-name "AzureFirewallSubnet" --address-prefixes 10.0.0.0/16 --subnet-prefixes 10.0.0.0/24').get_output_in_json()
        subnet_id_default = vnet_instance['newVNet']['subnets'][0]['id']

        self.cmd('network firewall ip-config create -g {rg} -n {ipconfig} -f {af} --public-ip-address {pubip} --vnet-name {vnet}', checks=[
            self.check('name', '{ipconfig}'),
            self.check('subnet.id', subnet_id_default)
        ])
        self.cmd('network firewall ip-config create -g {rg} -n {ipconfig2} -f {af} --public-ip-address {pubip2}', checks=[
            self.check('name', '{ipconfig2}'),
            self.check('subnet', None)
        ])

        self.cmd('network firewall ip-config delete -g {rg} -n {ipconfig2} -f {af}')
        self.cmd('network firewall ip-config delete -g {rg} -n {ipconfig} -f {af}')

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
            'nat_rule1': 'nat-rule1',
            'app_rule1': 'app-rule1',
            'source_ip_group': 'sourceipgroup',
            'destination_ip_group': 'destinationipgroup'
        })

        self.cmd('extension add -n ip-group')
        self.cmd('network ip-group create -n {source_ip_group} -g {rg} --ip-addresses 10.0.0.0 10.0.0.1')
        self.cmd('network ip-group create -n {destination_ip_group} -g {rg} --ip-addresses 10.0.0.2 10.0.0.3')
        self.cmd('network firewall create -g {rg} -n {af}')
        self.cmd('network firewall network-rule create -g {rg} -n {network_rule1} -c {coll} --priority 10000 --action Allow -f {af} --source-addresses 10.0.0.0 111.1.0.0/24 --protocols UDP TCP ICMP --destination-ip-groups {destination_ip_group} --destination-ports 80')
        self.cmd('network firewall nat-rule create -g {rg} -n {network_rule1} -c {coll2} --priority 10001 --action Dnat -f {af} --source-addresses 10.0.0.0 111.1.0.0/24 --protocols UDP TCP --translated-fqdn server1.internal.com --destination-ports 96 --destination-addresses 12.36.22.14 --translated-port 95 --source-ip-groups {source_ip_group}')
        self.cmd('network firewall application-rule create -f {af} -n {app_rule1} --protocols Http=80 Https=8080 -g {rg} -c {coll3} --priority 10000 --action Allow --source-ip-groups {source_ip_group} --target-fqdns www.bing.com')
        self.cmd('network firewall delete -g {rg} -n {af}')

    @ResourceGroupPreparer(name_prefix='cli_test_azure_firewall_zones', location='eastus')
    def test_azure_firewall_zones(self, resource_group):

        self.kwargs.update({
            'af': 'af1',
            'coll': 'rc1',
        })
        self.cmd('network firewall create -g {rg} -n {af} --zones 1 3')
        self.cmd('network firewall update -g {rg} -n {af} --zones 1')

    @ResourceGroupPreparer(name_prefix='cli_test_azure_firewall_policy', location='westcentralus')
    def test_azure_firewall_policy(self, resource_group, resource_group_location):
        from knack.util import CLIError
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

        self.cmd('network firewall policy show -g {rg} -n {policy}', checks=[
            self.check('type', 'Microsoft.Network/FirewallPolicies'),
            self.check('name', '{policy}')
        ])

        self.cmd('network firewall policy list -g {rg}', checks=[
            self.check('@[0].type', 'Microsoft.Network/FirewallPolicies'),
            self.check('@[0].name', '{policy}')
        ])

        self.cmd('network firewall policy list')

        self.cmd('network firewall policy update -g {rg} -n {policy} --threat-intel-mode Deny', checks=[
            self.check('type', 'Microsoft.Network/FirewallPolicies'),
            self.check('name', '{policy}'),
            self.check('threatIntelMode', 'Deny')
        ])

        self.cmd('network firewall policy rule-collection-group create -g {rg} --priority {collection_group_priority} --policy-name {policy} -n {collectiongroup}', checks=[
            self.check('type', 'Microsoft.Network/RuleGroups'),
            self.check('name', '{collectiongroup}')
        ])

        self.cmd('network firewall policy rule-collection-group show -g {rg} --policy-name {policy} -n {collectiongroup}', checks=[
            self.check('type', 'Microsoft.Network/RuleGroups'),
            self.check('name', '{collectiongroup}'),
            self.check('priority', '{collection_group_priority}')
        ])

        self.cmd('network firewall policy rule-collection-group list -g {rg} --policy-name {policy}', checks=[
            self.check('length(@)', 1),
            self.check('@[0].type', 'Microsoft.Network/RuleGroups'),
            self.check('@[0].name', '{collectiongroup}'),
            self.check('@[0].priority', '{collection_group_priority}')
        ])

        self.cmd('network firewall policy rule-collection-group update -g {rg} --policy-name {policy} -n {collectiongroup} --priority 12000', checks=[
            self.check('type', 'Microsoft.Network/RuleGroups'),
            self.check('name', '{collectiongroup}'),
            self.check('priority', 12000)
        ])

        self.cmd('az network firewall policy rule-collection-group collection add-nat-collection -n nat-collection \
                 --policy-name {policy} --rule-collection-group-name {collectiongroup} -g {rg} --collection-priority 10005 \
                 --action DNAT --rule-name network-rule --description "test" \
                 --destination-addresses "202.120.36.15" --source-addresses "202.120.36.13" "202.120.36.14" \
                 --translated-address 128.1.1.1 --translated-port 1234 \
                 --destination-ports 12000 12001 --ip-protocols TCP UDP', checks=[
            self.check('length(rules)', 1),
            self.check('rules[0].ruleType', "FirewallPolicyNatRule"),
            self.check('rules[0].name', "nat-collection")
        ])

        self.cmd('network firewall policy rule-collection-group collection add-filter-collection -g {rg} --policy-name {policy} \
                 --rule-collection-group-name {collectiongroup} -n filter-collection-1 --collection-priority 13000 \
                 --action Allow --rule-name network-rule --rule-type NetworkRule \
                 --description "test" --destination-addresses "202.120.36.15" --source-addresses "202.120.36.13" "202.120.36.14" \
                 --destination-ports 12003 12004 --ip-protocols Any ICMP', checks=[
            self.check('length(rules)', 2),
            self.check('rules[1].ruleType', "FirewallPolicyFilterRule"),
            self.check('rules[1].name', "filter-collection-1")
        ])

        self.cmd('network firewall policy rule-collection-group collection add-filter-collection -g {rg} --policy-name {policy} \
                 --rule-collection-group-name {collectiongroup} -n filter-collection-2 --collection-priority 14000 \
                 --action Allow --rule-name application-rule --rule-type ApplicationRule \
                 --description "test" --destination-addresses "202.120.36.15" "202.120.36.16" --source-addresses "202.120.36.13" "202.120.36.14" --protocols Http=12800 Https=12801 \
                 --fqdn-tags AzureBackup HDInsight', checks=[
            self.check('length(rules)', 3),
            self.check('rules[2].ruleType', "FirewallPolicyFilterRule"),
            self.check('rules[2].name', "filter-collection-2")
        ])

        self.cmd('network firewall policy rule-collection-group collection list -g {rg} --policy-name {policy} \
                 --rule-collection-group-name {collectiongroup}', checks=[
            self.check('length(@)', 3)
        ])

        self.cmd('network firewall policy rule-collection-group collection rule add -g {rg} --policy-name {policy} \
                 --rule-collection-group-name {collectiongroup} --collection-name filter-collection-2 --name application-rule-2 \
                 --rule-type ApplicationRule --description "test" --source-addresses 202.120.36.13 202.120.36.14 \
                 --destination-addresses 202.120.36.15 202.120.36.16 --protocols Http=12800 Https=12801 --target-fqdns www.bing.com', checks=[
            self.check('length(rules[2].ruleConditions)', 2)
        ])

        self.cmd('network firewall policy rule-collection-group collection rule add -g {rg} --policy-name {policy} \
                 --rule-collection-group-name {collectiongroup} --collection-name filter-collection-1 \
                 --name network-rule-2 --rule-type NetworkRule \
                 --description "test" --destination-addresses "202.120.36.15" --source-addresses "202.120.36.13" "202.120.36.14" \
                 --destination-ports 12003 12004 --ip-protocols Any ICMP', checks=[
            self.check('length(rules[1].ruleConditions)', 2)
        ])

        self.cmd('network firewall policy rule-collection-group collection rule remove -g {rg} --policy-name {policy} \
                 --rule-collection-group-name {collectiongroup} --collection-name filter-collection-1 --name network-rule-2', checks=[
            self.check('length(rules[1].ruleConditions)', 1),
            self.check('rules[1].ruleConditions[0].name', 'network-rule')
        ])

        self.cmd('network firewall policy rule-collection-group collection remove -g {rg} --policy-name {policy} \
                 --rule-collection-group-name {collectiongroup} --name filter-collection-1', checks=[
            self.check('length(rules)', 2)
        ])

        with self.assertRaisesRegexp(CLIError, 'Unable to find status link for polling.'):
            self.cmd('network firewall policy rule-collection-group delete -g {rg} --policy-name {policy} --name {collectiongroup}')

        self.cmd('network firewall policy rule-collection-group list -g {rg} --policy-name {policy}', checks=[
            self.check('length(@)', 0)
        ])

        self.cmd('network firewall policy delete -g {rg} --name {policy}')
