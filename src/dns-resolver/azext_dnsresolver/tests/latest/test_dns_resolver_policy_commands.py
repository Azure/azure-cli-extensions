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


class DnsResolverPolicyClientTest(ScenarioTest):
    @ResourceGroupPreparer(name_prefix='cli_test_dns_resolver_policy_', location='westus2')
    def test_dns_resolver_policy_crud(self):
        self.kwargs.update({
            'dns_resolver_policy_name': self.create_random_name('dnsrp-', 20),
        })

        self.cmd(
            'dns-resolver policy create -n {dns_resolver_policy_name} -g {rg} --tags key=value1',
            checks=[
                self.check('name', '{dns_resolver_policy_name}'),
                self.check('type', 'Microsoft.Network/dnsResolverPolicies')
            ]
        )
        self.cmd(
            'dns-resolver policy list -g {rg}',
            checks=[
                self.check('length(@)', 1),
                self.check('[0].name', '{dns_resolver_policy_name}')
            ]
        )
        self.cmd('dns-resolver policy update -n {dns_resolver_policy_name} -g {rg} --tags key=value2')
        self.cmd(
            'dns-resolver policy show -n {dns_resolver_policy_name} -g {rg}',
            checks=[
                self.check('name', '{dns_resolver_policy_name}'),
                self.check('tags.key', 'value2')
            ]
        )
        self.cmd('dns-resolver policy delete -n {dns_resolver_policy_name} -g {rg} --no-wait --yes')

    @ResourceGroupPreparer(name_prefix='cli_test_dns_resolver_domain_list_', location='westus2')
    def test_dns_resolver_domain_list_crud(self):
        self.kwargs.update({
            'dns_resolver_domain_list_name': self.create_random_name('dnsrdl-', 20),
        })

        self.cmd(
            'dns-resolver domain-list create -n {dns_resolver_domain_list_name} -g {rg} --tags key=value1 --domains "[contoso.com]"',
            checks=[
                self.check('name', '{dns_resolver_domain_list_name}'),
                self.check('type', 'Microsoft.Network/dnsResolverDomainLists')
            ]
        )
        self.cmd(
            'dns-resolver domain-list list -g {rg}',
            checks=[
                self.check('length(@)', 1),
                self.check('[0].name', '{dns_resolver_domain_list_name}')
            ]
        )
        self.cmd('dns-resolver domain-list update -n {dns_resolver_domain_list_name} -g {rg} --tags key=value2')
        self.cmd(
            'dns-resolver domain-list show -n {dns_resolver_domain_list_name} -g {rg}',
            checks=[
                self.check('name', '{dns_resolver_domain_list_name}'),
                self.check('tags.key', 'value2')
            ]
        )
        self.cmd('dns-resolver domain-list delete -n {dns_resolver_domain_list_name} -g {rg} --no-wait --yes')

    @ResourceGroupPreparer(name_prefix='cli_test_dns_security_rule_', location='westus2')
    def test_dns_security_rule_crud(self):
        self.kwargs.update({
            'dns_security_rule_name': self.create_random_name('dnssr-', 16),
            'dns_resolver_policy_name': self.create_random_name('dnsrp-', 20),
            'dns_resolver_domain_list_name': self.create_random_name('dnsdl-', 20),
            'vnet_name': self.create_random_name('vnet-', 12),
            'subnet_name': self.create_random_name('subnet-', 12)
        })

        self.cmd('dns-resolver policy create -n {dns_resolver_policy_name} -g {rg}')
        self.cmd('dns-resolver domain-list create -n {dns_resolver_domain_list_name} -g {rg} --tags key=value1 --domains "[contoso.com]"')
        self.kwargs['domain_list_id'] = self.cmd('dns-resolver domain-list show -n {dns_resolver_domain_list_name} -g {rg}').get_output_in_json()['id']

        self.kwargs['action_arg'] = f'{{action-type:Block,block-response-code:SERVFAIL}}'
        self.kwargs['domain_list_arg'] = f'[{{id:{self.kwargs["domain_list_id"]}}}]'
        self.cmd(
            'dns-resolver policy dns-security-rule create -n {dns_security_rule_name} -g {rg} --policy-name {dns_resolver_policy_name} --priority 100 --action "{action_arg}" --domain-lists "{domain_list_arg}" --rule-state Enabled '
            '--tags key=value1',
            checks=[
                self.check('name', '{dns_security_rule_name}'),
                self.check('type', 'Microsoft.Network/dnsResolverPolicies/dnsSecurityRules')
            ]
        )
        self.cmd(
            'dns-resolver policy dns-security-rule list -g {rg} --policy-name {dns_resolver_policy_name}',
            checks=[
                self.check('length(@)', 1),
                self.check('[0].name', '{dns_security_rule_name}')
            ]
        )
        self.cmd('dns-resolver policy dns-security-rule update -n {dns_security_rule_name} -g {rg} --policy-name {dns_resolver_policy_name} --tags key=value2')
        self.cmd(
            'dns-resolver policy dns-security-rule show -n {dns_security_rule_name} -g {rg} --policy-name {dns_resolver_policy_name}',
            checks=[
                self.check('name', '{dns_security_rule_name}'),
                self.check('tags.key', 'value2')
            ]
        )
        self.cmd('dns-resolver policy dns-security-rule delete -n {dns_security_rule_name} -g {rg} --policy-name {dns_resolver_policy_name} --no-wait --yes')

    @ResourceGroupPreparer(name_prefix='cli_test_dns_resolver_policy_link_', location='westus2')
    def test_dns_resolver_policy_link_crud(self):
        self.kwargs.update({
            'vnet_link_name': self.create_random_name('vl-', 16),
            'dns_resolver_policy_name': self.create_random_name('dnsrp-', 20),
            'vnet_name': self.create_random_name('vnet-', 12),
        })

        self.cmd('network vnet create -n {vnet_name} -g {rg}')
        self.kwargs['vnet_id'] = self.cmd('network vnet show -n {vnet_name} -g {rg}').get_output_in_json()['id']
        self.cmd('dns-resolver policy create -n {dns_resolver_policy_name} -g {rg}')
        self.kwargs['dns_resolver_policy_id'] = self.cmd('dns-resolver policy show -n {dns_resolver_policy_name} -g {rg}').get_output_in_json()['id']

        self.cmd(
            'dns-resolver policy vnet-link create -n {vnet_link_name} -g {rg} --policy-name {dns_resolver_policy_name} '
            '--virtual-network "{{id:{vnet_id}}}" --tags key=value1',
            checks=[
                self.check('name', '{vnet_link_name}'),
                self.check('type', 'Microsoft.Network/dnsResolverPolicies/virtualNetworkLinks')
            ]
        )
        self.cmd(
            'dns-resolver policy vnet-link list -g {rg} --policy-name {dns_resolver_policy_name}',
            checks=[
                self.check('length(@)', 1),
                self.check('[0].name', '{vnet_link_name}')
            ]
        )
        self.cmd('dns-resolver policy vnet-link update -n {vnet_link_name} -g {rg} --policy-name {dns_resolver_policy_name} --tags key=value2')
        self.cmd(
            'dns-resolver policy vnet-link show -n {vnet_link_name} -g {rg} --policy-name {dns_resolver_policy_name}',
            checks=[
                self.check('name', '{vnet_link_name}'),
                self.check('tags.key', 'value2')
            ]
        )
        self.cmd(
            'dns-resolver policy virtual-network list-dns-resolver-policy --virtual-network-name {vnet_name} -g {rg}',
            checks=[
                self.check('length(@)', 1),
                self.check('[0].id', '{dns_resolver_policy_id}')
            ]
        )
        self.cmd('dns-resolver policy vnet-link delete -n {vnet_link_name} -g {rg} --policy-name {dns_resolver_policy_name} --no-wait --yes')
