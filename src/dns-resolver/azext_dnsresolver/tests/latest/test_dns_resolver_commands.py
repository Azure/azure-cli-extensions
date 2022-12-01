# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines

from azure.cli.testsdk import (
    ResourceGroupPreparer,
    ScenarioTest
)


class DnsResolverClientTest(ScenarioTest):
    @ResourceGroupPreparer(name_prefix='cli_test_dns_resolver_', location='eastus')
    def test_dns_resolver_crud(self):
        self.kwargs.update({
            'dns_resolver_name': self.create_random_name('dns-resolver-', 20),
            'vnet_name': self.create_random_name('vnet-', 12),
        })

        self.cmd('network vnet create -n {vnet_name} -g {rg}')
        self.kwargs['vnet_id'] = self.cmd('network vnet show -n {vnet_name} -g {rg}').get_output_in_json()['id']

        self.cmd(
            'dns-resolver create -n {dns_resolver_name} -g {rg} --id {vnet_id} --tags key=value1',
            checks=[
                self.check('name', '{dns_resolver_name}'),
                self.check('type', 'Microsoft.Network/dnsResolvers')
            ]
        )
        self.cmd(
            'dns-resolver list -g {rg}',
            checks=[
                self.check('length(@)', 1),
                self.check('[0].name', '{dns_resolver_name}')
            ]
        )
        self.cmd('dns-resolver update -n {dns_resolver_name} -g {rg} --tags key=value2')
        self.cmd(
            'dns-resolver show -n {dns_resolver_name} -g {rg}',
            checks=[
                self.check('name', '{dns_resolver_name}'),
                self.check('tags.key', 'value2')
            ]
        )
        self.cmd('dns-resolver delete -n {dns_resolver_name} -g {rg} --no-wait --yes')

    @ResourceGroupPreparer(name_prefix='cli_test_dns_resolver_', location='eastus')
    def test_dns_resolver_inbound_crud(self):
        self.kwargs.update({
            'endpoint_name': self.create_random_name('endpoint-', 16),
            'dns_resolver_name': self.create_random_name('dns-resolver-', 20),
            'vnet_name': self.create_random_name('vnet-', 12),
            'subnet_name': self.create_random_name('subnet-', 12)
        })

        self.cmd('network vnet create -n {vnet_name} -g {rg}')
        self.cmd('network vnet subnet create -n {subnet_name} -g {rg} --vnet-name {vnet_name} --address-prefixes 10.0.0.0/24')
        self.kwargs['vnet_id'] = self.cmd('network vnet show -n {vnet_name} -g {rg}').get_output_in_json()['id']
        self.kwargs['subnet_id'] = self.cmd('network vnet subnet show -n {subnet_name} -g {rg} --vnet-name {vnet_name}').get_output_in_json()['id']
        self.cmd('dns-resolver create -n {dns_resolver_name} -g {rg} --id {vnet_id}')

        self.cmd(
            'dns-resolver inbound-endpoint create -n {endpoint_name} -g {rg} --dns-resolver-name {dns_resolver_name} '
            '--ip-configurations \"[{{private-ip-address:\'\',private-ip-allocation-method:Dynamic,id:{subnet_id}}}]\" '
            '--tags key=value1',
            checks=[
                self.check('name', '{endpoint_name}'),
                self.check('type', 'Microsoft.Network/dnsResolvers/inboundEndpoints')
            ]
        )
        self.cmd(
            'dns-resolver inbound-endpoint list -g {rg} --dns-resolver-name {dns_resolver_name}',
            checks=[
                self.check('length(@)', 1),
                self.check('[0].name', '{endpoint_name}')
            ]
        )
        self.cmd('dns-resolver inbound-endpoint update -n {endpoint_name} -g {rg} --dns-resolver-name {dns_resolver_name} --tags key=value2')
        self.cmd(
            'dns-resolver inbound-endpoint show -n {endpoint_name} -g {rg} --dns-resolver-name {dns_resolver_name}',
            checks=[
                self.check('name', '{endpoint_name}'),
                self.check('tags.key', 'value2')
            ]
        )
        self.cmd('dns-resolver inbound-endpoint delete -n {endpoint_name} -g {rg} --dns-resolver-name {dns_resolver_name} --no-wait --yes')

    @ResourceGroupPreparer(name_prefix='cli_test_dns_resolver_', location='eastus')
    def test_dns_resolver_outbound_crud(self):
        self.kwargs.update({
            'endpoint_name': self.create_random_name('endpoint-', 16),
            'dns_resolver_name': self.create_random_name('dns-resolver-', 20),
            'vnet_name': self.create_random_name('vnet-', 12),
            'subnet_name': self.create_random_name('subnet-', 12)
        })

        self.cmd('network vnet create -n {vnet_name} -g {rg}')
        self.cmd('network vnet subnet create -n {subnet_name} -g {rg} --vnet-name {vnet_name} --address-prefixes 10.0.0.0/24')
        self.kwargs['vnet_id'] = self.cmd('network vnet show -n {vnet_name} -g {rg}').get_output_in_json()['id']
        self.kwargs['subnet_id'] = self.cmd('network vnet subnet show -n {subnet_name} -g {rg} --vnet-name {vnet_name}').get_output_in_json()['id']
        self.cmd('dns-resolver create -n {dns_resolver_name} -g {rg} --id {vnet_id}')

        self.cmd(
            'dns-resolver outbound-endpoint create -n {endpoint_name} -g {rg} --dns-resolver-name {dns_resolver_name} '
            '--id={subnet_id} --tags key=value1',
            checks=[
                self.check('name', '{endpoint_name}'),
                self.check('type', 'Microsoft.Network/dnsResolvers/outboundEndpoints')
            ]
        )
        self.cmd(
            'dns-resolver outbound-endpoint list -g {rg} --dns-resolver-name {dns_resolver_name}',
            checks=[
                self.check('length(@)', 1),
                self.check('[0].name', '{endpoint_name}')
            ]
        )
        self.cmd('dns-resolver outbound-endpoint update -n {endpoint_name} -g {rg} --dns-resolver-name {dns_resolver_name} --tags key=value2')
        self.cmd(
            'dns-resolver outbound-endpoint show -n {endpoint_name} -g {rg} --dns-resolver-name {dns_resolver_name}',
            checks=[
                self.check('name', '{endpoint_name}'),
                self.check('tags.key', 'value2')
            ]
        )
        self.cmd('dns-resolver outbound-endpoint delete -n {endpoint_name} -g {rg} --dns-resolver-name {dns_resolver_name} --no-wait --yes')

    @ResourceGroupPreparer(name_prefix='cli_test_dns_resolver_', location='eastus')
    def test_dns_resolver_ruleset_crud(self):
        self.kwargs.update({
            'ruleset_name': self.create_random_name('ruleset-', 12),
            'endpoint_name': self.create_random_name('endpoint-', 16),
            'dns_resolver_name': self.create_random_name('dns-resolver-', 20),
            'vnet_name': self.create_random_name('vnet-', 12),
            'subnet_name': self.create_random_name('subnet-', 12)
        })

        self.cmd('network vnet create -n {vnet_name} -g {rg}')
        self.cmd('network vnet subnet create -n {subnet_name} -g {rg} --vnet-name {vnet_name} --address-prefixes 10.0.0.0/24')
        self.kwargs['vnet_id'] = self.cmd('network vnet show -n {vnet_name} -g {rg}').get_output_in_json()['id']
        self.kwargs['subnet_id'] = self.cmd('network vnet subnet show -n {subnet_name} -g {rg} --vnet-name {vnet_name}').get_output_in_json()['id']
        self.cmd('dns-resolver create -n {dns_resolver_name} -g {rg} --id {vnet_id}')
        self.kwargs['outbound_id'] = self.cmd('dns-resolver outbound-endpoint create -n {endpoint_name} -g {rg} --dns-resolver-name {dns_resolver_name} --id={subnet_id}').get_output_in_json()['id']

        self.cmd(
            'dns-resolver forwarding-ruleset create -n {ruleset_name} -g {rg} '
            '--outbound-endpoints [{{id:{outbound_id}}}] --tags key=value1',
            checks=[
                self.check('name', '{ruleset_name}'),
                self.check('type', 'Microsoft.Network/dnsForwardingRulesets')
            ]
        )
        self.cmd(
            'dns-resolver forwarding-ruleset list -g {rg}',
            checks=[
                self.check('length(@)', 1),
                self.check('[0].name', '{ruleset_name}')
            ]
        )
        self.cmd('dns-resolver forwarding-ruleset update -n {ruleset_name} -g {rg} --tags key=value2')
        self.cmd(
            'dns-resolver forwarding-ruleset show -n {ruleset_name} -g {rg}',
            checks=[
                self.check('name', '{ruleset_name}'),
                self.check('tags.key', 'value2')
            ]
        )
        self.cmd('dns-resolver forwarding-ruleset delete -n {ruleset_name} -g {rg} --no-wait --yes')

    @ResourceGroupPreparer(name_prefix='cli_test_dns_resolver_', location='eastus')
    def test_dns_resolver_rule_crud(self):
        self.kwargs.update({
            'rule_name': self.create_random_name('rule-', 12),
            'ruleset_name': self.create_random_name('ruleset-', 12),
            'endpoint_name': self.create_random_name('endpoint-', 16),
            'dns_resolver_name': self.create_random_name('dns-resolver-', 20),
            'vnet_name': self.create_random_name('vnet-', 12),
            'subnet_name': self.create_random_name('subnet-', 12)
        })

        self.cmd('network vnet create -n {vnet_name} -g {rg}')
        self.cmd('network vnet subnet create -n {subnet_name} -g {rg} --vnet-name {vnet_name} --address-prefixes 10.0.0.0/24')
        self.kwargs['vnet_id'] = self.cmd('network vnet show -n {vnet_name} -g {rg}').get_output_in_json()['id']
        self.kwargs['subnet_id'] = self.cmd('network vnet subnet show -n {subnet_name} -g {rg} --vnet-name {vnet_name}').get_output_in_json()['id']
        self.cmd('dns-resolver create -n {dns_resolver_name} -g {rg} --id {vnet_id}')
        self.kwargs['outbound_id'] = self.cmd('dns-resolver outbound-endpoint create -n {endpoint_name} -g {rg} --dns-resolver-name {dns_resolver_name} --id={subnet_id}').get_output_in_json()['id']
        self.cmd('dns-resolver forwarding-ruleset create -n {ruleset_name} -g {rg} --outbound-endpoints [{{id:{outbound_id}}}]')

        self.cmd(
            'dns-resolver forwarding-rule create -n {rule_name} -g {rg} --ruleset-name {ruleset_name} '
            '--domain-name contoso.com. --forwarding-rule-state Enabled --metadata additionalProp=value1 '
            '--target-dns-servers [{{ip-address:10.0.0.1,port:53}}]',
            checks=[
                self.check('name', '{rule_name}'),
                self.check('type', 'Microsoft.Network/dnsForwardingRulesets/forwardingRules')
            ]
        )
        self.cmd(
            'dns-resolver forwarding-rule list -g {rg} --ruleset-name {ruleset_name}',
            checks=[
                self.check('length(@)', 1),
                self.check('[0].name', '{rule_name}')
            ]
        )
        self.cmd('dns-resolver forwarding-rule update -n {rule_name} -g {rg} --ruleset-name {ruleset_name} --forwarding-rule-state Disabled --metadata additionalProp=value2')
        self.cmd(
            'dns-resolver forwarding-rule show -n {rule_name} -g {rg} --ruleset-name {ruleset_name}',
            checks=[
                self.check('forwardingRuleState', 'Disabled'),
                self.check('metadata.additionalProp', 'value2')
            ]
        )
        self.cmd('dns-resolver forwarding-rule delete -n {rule_name} -g {rg} --ruleset-name {ruleset_name} --yes')

    @ResourceGroupPreparer(name_prefix='cli_test_dns_resolver_', location='eastus')
    def test_dns_resolver_vnet_crud(self):
        self.kwargs.update({
            'link_name': self.create_random_name('link-', 12),
            'ruleset_name': self.create_random_name('ruleset-', 12),
            'endpoint_name': self.create_random_name('endpoint-', 16),
            'dns_resolver_name': self.create_random_name('dns-resolver-', 20),
            'vnet_name': self.create_random_name('vnet-', 12),
            'subnet_name': self.create_random_name('subnet-', 12)
        })

        self.cmd('network vnet create -n {vnet_name} -g {rg}')
        self.cmd('network vnet subnet create -n {subnet_name} -g {rg} --vnet-name {vnet_name} --address-prefixes 10.0.0.0/24')
        self.kwargs['vnet_id'] = self.cmd('network vnet show -n {vnet_name} -g {rg}').get_output_in_json()['id']
        self.kwargs['subnet_id'] = self.cmd('network vnet subnet show -n {subnet_name} -g {rg} --vnet-name {vnet_name}').get_output_in_json()['id']
        self.cmd('dns-resolver create -n {dns_resolver_name} -g {rg} --id {vnet_id}')
        self.kwargs['outbound_id'] = self.cmd('dns-resolver outbound-endpoint create -n {endpoint_name} -g {rg} --dns-resolver-name {dns_resolver_name} --id={subnet_id}').get_output_in_json()['id']
        self.cmd('dns-resolver forwarding-ruleset create -n {ruleset_name} -g {rg} --outbound-endpoints [{{id:{outbound_id}}}]')

        self.cmd(
            'dns-resolver vnet-link create -n {link_name} -g {rg} --ruleset-name {ruleset_name} '
            '--id {vnet_id} --metadata additionalProp=value1',
            checks=[
                self.check('name', '{link_name}'),
                self.check('type', 'Microsoft.Network/dnsForwardingRulesets/virtualNetworkLinks')
            ]
        )
        self.cmd(
            'dns-resolver vnet-link list -g {rg} --ruleset-name {ruleset_name}',
            checks=[
                self.check('length(@)', 1),
                self.check('[0].name', '{link_name}')
            ]
        )
        self.cmd('dns-resolver vnet-link update -n {link_name} -g {rg} --ruleset-name {ruleset_name} --metadata additionalProp=value2')
        self.cmd(
            'dns-resolver vnet-link show -n {link_name} -g {rg} --ruleset-name {ruleset_name}',
            checks=[
                self.check('name', '{link_name}'),
                self.check('metadata.additionalProp', 'value2')
            ]
        )
        self.cmd('dns-resolver vnet-link delete -n {link_name} -g {rg} --ruleset-name {ruleset_name} --no-wait --yes')
