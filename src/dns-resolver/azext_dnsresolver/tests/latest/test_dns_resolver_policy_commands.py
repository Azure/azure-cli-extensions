# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
from datetime import datetime
from datetime import timedelta
import os
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
        current_time = datetime.utcnow()
        future_time = current_time + timedelta(hours=12)

        self.kwargs.update({
            'dns_resolver_domain_list_name': self.create_random_name('dnsrdl-', 20),
            'storage_account_name': self.create_random_name('stacc', 10),
            'container_name': self.create_random_name('ctn-', 10),

            # Time string for expiry of SAS tokens, calculate it using current time + 1 hour
            'expiry_time': future_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        })

        # Create a storage account for the domain list bulk usage
        self.cmd('storage account create -n {storage_account_name} -g {rg} --sku Standard_LRS')
        self.cmd('storage container create -n {container_name} --account-name {storage_account_name}')

        current_directory = os.path.dirname(os.path.abspath(__file__))
        upload_blob_path = os.path.join(current_directory, 'upload_blob.txt')
        download_blob_path = os.path.join(current_directory, 'download_blob.txt')
        self.kwargs['upload_blob_path'] = upload_blob_path
        self.kwargs['download_blob_path'] = download_blob_path

        self.cmd('storage blob upload --account-name {storage_account_name} --container-name {container_name} --name download_blob.txt --file "{download_blob_path}"')
        self.cmd('storage blob upload --account-name {storage_account_name} --container-name {container_name} --name upload_blob.txt --file "{upload_blob_path}"')

        self.kwargs['sas_upload_url'] = self.cmd(
            'storage blob generate-sas --account-name {storage_account_name} --container-name {container_name} --name upload_blob.txt --permissions r --expiry {expiry_time} --full-uri'
        ).get_output_in_json()

        self.kwargs['sas_download_token'] = self.cmd(
            'storage blob generate-sas --account-name {storage_account_name} --container-name {container_name} --name download_blob.txt --permissions w --expiry {expiry_time} --full-uri'
        ).get_output_in_json()

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

        # Test bulk domain APIs
        self.cmd('dns-resolver domain-list bulk --name {dns_resolver_domain_list_name} -g {rg} --action Upload --storage-url {sas_upload_url}')
        self.cmd('dns-resolver domain-list bulk --name {dns_resolver_domain_list_name} -g {rg} --action Download --storage-url {sas_download_token}')

        self.cmd('dns-resolver domain-list delete -n {dns_resolver_domain_list_name} -g {rg} --no-wait --yes')

        self.cmd('storage blob delete --account-name {storage_account_name} --container-name {container_name} --name upload_blob.txt')
        self.cmd('storage blob delete --account-name {storage_account_name} --container-name {container_name} --name download_blob.txt')
        self.cmd('storage container delete --account-name {storage_account_name} --name {container_name}')
        self.cmd('storage account delete -n {storage_account_name} -g {rg} --yes')

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

        self.kwargs['action_arg'] = f'{{action-type:Block}}'
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
