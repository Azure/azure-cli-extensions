# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ResourceGroupPreparer, ScenarioTest
from azure.cli.testsdk.scenario_tests import AllowLargeResponse


class RedisEnterpriseFirewallRulesScenarioTest(ScenarioTest):

    @AllowLargeResponse(size_kb=9999)
    @ResourceGroupPreparer(name_prefix='clitest-redisenterprise-fw-', location='eastus2euap')
    def test_redisenterprise_firewall_rules(self, resource_group):
        self.kwargs.update({
            'cluster': self.create_random_name(prefix='clitest-fw-', length=23),
            'rules_create': '[{"name":"office","source-address-prefix":"203.0.113.0/24"},'
                            '{"name":"azure","source-address-prefix":"AzureCloud"}]',
            'rules_update': '[{"name":"replacement","source-address-prefix":"198.51.100.1"}]',
        })
        cluster = '--cluster-name {cluster} --resource-group {rg}'
        show = 'redisenterprise show ' + cluster
        update = 'redisenterprise update ' + cluster
        self.cmd('redisenterprise create ' + cluster
                 + ' --location eastus2euap --sku Balanced_B1 --no-database '
                   '--public-network-access Enabled --firewall-rules \'{rules_create}\'',
                 checks=[self.check('length(firewallRules)', 2)])
        self.cmd(show, checks=[self.check('sort(firewallRules[].name)', ['azure', 'office']),
                               self.check("firewallRules[?name=='office'].sourceAddressPrefix",
                                          ['203.0.113.0/24'])])
        self.cmd(update + ' --firewall-rules \'{rules_update}\'',
                 checks=[self.check('length(firewallRules)', 1),
                         self.check('firewallRules[0].name', 'replacement')])
        self.cmd(update + ' --firewall-rules "[]"', checks=[self.check('length(firewallRules)', 0)])
        self.cmd(update + ' --firewall-rules \'{rules_update}\'')
        self.cmd(update + ' --public-network-access Disabled --firewall-rules "[]"')
        self.cmd(show, checks=[self.check('publicNetworkAccess', 'Disabled'),
                               self.check('length(firewallRules)', 0)])
        self.cmd(update + ' --public-network-access Enabled --firewall-rules \'{rules_update}\'')
        self.cmd(update + ' --firewall-rules null')
        self.cmd(show, checks=[self.check('length(firewallRules || `[]`)', 0)])
        self.cmd('redisenterprise delete ' + cluster + ' -y')

    @AllowLargeResponse(size_kb=9999)
    @ResourceGroupPreparer(name_prefix='clitest-redisenterprise-fw-put-', location='centraluseuap')
    def test_redisenterprise_firewall_rules_put(self, resource_group):
        self.kwargs.update({
            'cluster': self.create_random_name(prefix='clitest-fw-', length=23),
            'rules_create': '[{"name":"office","source-address-prefix":"203.0.113.0/24"},'
                            '{"name":"azure","source-address-prefix":"AzureCloud"}]',
            'rules_update': '[{"name":"replacement","source-address-prefix":"198.51.100.1"}]',
        })
        cluster = '--cluster-name {cluster} --resource-group {rg}'
        show = 'redisenterprise show ' + cluster
        create = ('redisenterprise create ' + cluster
                  + ' --location centraluseuap --sku Balanced_B1 --public-network-access Enabled')
        self.cmd(create + ' --firewall-rules \'{rules_create}\'',
                 checks=[self.check('name', 'default'), self.check('provisioningState', 'Succeeded')])
        self.cmd(show, checks=[self.check('sort(firewallRules[].name)', ['azure', 'office'])])
        self.cmd('redisenterprise database show ' + cluster,
                 checks=[self.check('name', 'default'), self.check('provisioningState', 'Succeeded')])
        create += ' --no-database'
        self.cmd(create + ' --firewall-rules \'{rules_update}\'')
        self.cmd(show, checks=[self.check('firewallRules[0].name', 'replacement'),
                               self.check('length(firewallRules)', 1)])
        self.cmd(create + ' --firewall-rules "[]"')
        self.cmd(show, checks=[self.check('length(firewallRules)', 0)])
        self.cmd(create + ' --firewall-rules \'{rules_create}\'')
        self.cmd(show, checks=[self.check('sort(firewallRules[].name)', ['azure', 'office'])])
        self.cmd(create)
        self.cmd(show, checks=[self.check('length(firewallRules)', 0)])
        self.cmd('redisenterprise delete ' + cluster + ' -y')
