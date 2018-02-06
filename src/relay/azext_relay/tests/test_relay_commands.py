# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# AZURE CLI Relay - NAMESPACE TEST DEFINITIONS

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


# pylint: disable=line-too-long
# pylint: disable=too-many-lines


class RelayScenarioTest(ScenarioTest):
    @ResourceGroupPreparer(name_prefix='cli_test_eh_namespace')
    def test_relay_namespace(self, resource_group):
        self.kwargs.update({
            'loc': 'westus2',
            'rg': resource_group,
            'namespacename': self.create_random_name(prefix='relay-nscli', length=20),
            'tags': {'tag1: value1'},
            'sku': 'Standard',
            'tier': 'Standard',
            'authoname': self.create_random_name(prefix='cliAutho', length=20),
            'defaultauthorizationrule': 'RootManageSharedAccessKey',
            'accessrights': 'Send',
            'primary': 'PrimaryKey',
            'secondary': 'SecondaryKey'
        })

        # Check for the NameSpace name Availability

        self.cmd('relay namespace exists --name {namespacename}',
                 checks=[self.check('nameAvailable', True)])

        # Create Namespace
        self.cmd(
            'relay namespace create --resource-group {rg} --name {namespacename} --location {loc} --tags {tags} --sku-tier {tier}',
            checks=[self.check('sku.tier', self.kwargs['tier'])])

        # Get Created Namespace
        self.cmd('relay namespace show --resource-group {rg} --name {namespacename}',
                 checks=[self.check('sku.tier', self.kwargs['tier'])])

        # Get Created Namespace list by subscription
        listnamespaceresult = self.cmd('relay namespace list').output
        self.assertGreater(len(listnamespaceresult), 0)

        # Get Created Namespace list by ResourceGroup
        listnamespacebyresourcegroupresult = self.cmd('relay namespace list --resource-group {rg}').output
        self.assertGreater(len(listnamespacebyresourcegroupresult), 0)

        # Create Authoriazation Rule
        self.cmd(
            'relay namespace authorizationrule create --resource-group {rg} --namespace-name {namespacename} --name {authoname} --access-rights {accessrights}',
            checks=[self.check('name', self.kwargs['authoname'])])

        # Get Authorization Rule
        self.cmd(
            'relay namespace authorizationrule show --resource-group {rg} --namespace-name {namespacename} --name {authoname}',
            checks=[self.check('name', self.kwargs['authoname'])])

        # Get Default Authorization Rule
        self.cmd(
            'relay namespace authorizationrule show --resource-group {rg} --namespace-name {namespacename} --name {defaultauthorizationrule}',
            checks=[self.check('name', self.kwargs['defaultauthorizationrule'])])

        # Get Authorization Rule Listkeys
        self.cmd(
            'relay namespace authorizationrule keys list --resource-group {rg} --namespace-name {namespacename} --name {authoname}')

        # Regeneratekeys - Primary
        self.cmd(
            'relay namespace authorizationrule keys renew --resource-group {rg} --namespace-name {namespacename} --name {authoname} --key-name {primary}')

        # Regeneratekeys - Secondary
        self.cmd(
            'relay namespace authorizationrule keys renew --resource-group {rg} --namespace-name {namespacename} --name {authoname} --key-name {secondary}')

        # Delete AuthorizationRule
        self.cmd(
            'relay namespace authorizationrule delete --resource-group {rg} --namespace-name {namespacename} --name {authoname}')

        # Delete Namespace list by ResourceGroup
        self.cmd('relay namespace delete --resource-group {rg} --name {namespacename}')

    @ResourceGroupPreparer(name_prefix='cli_test_relay_wcfrelay')
    def test_relay_wcfrelay(self, resource_group):
        self.kwargs.update({
            'loc': 'westus2',
            'rg': resource_group,
            'namespacename': self.create_random_name(prefix='relay-nscli', length=20),
            'tags': {'tag1: value1', 'tag2: value2'},
            'sku': 'Standard',
            'tier': 'Standard',
            'authoname': self.create_random_name(prefix='cliAutho', length=20),
            'defaultauthorizationrule': 'RootManageSharedAccessKey',
            'accessrights': 'Listen',
            'primary': 'PrimaryKey',
            'secondary': 'SecondaryKey',
            'wcfrelayname': self.create_random_name(prefix='relay-wcfrelaycli', length=25),
            'wcfrelayauthoname': self.create_random_name(prefix='cliwcfrelayAutho', length=25),
            'requiresclientauthorization': 'True',
            'requirestransportsecurity': 'True',
            'usermetadata': 'UserMetadata',
            'relaytype': 'NetTcp'
        })

        # Create Namespace
        self.cmd(
            'relay namespace create --resource-group {rg} --name {namespacename} --location {loc} --tags {tags} --sku-tier {tier}',
            checks=[self.check('sku.tier', self.kwargs['tier'])])

        # Get Created Namespace
        self.cmd('relay namespace show --resource-group {rg} --name {namespacename}',
                 checks=[self.check('sku.tier', self.kwargs['tier'])])

        # Create WCFRelay
        self.cmd(
            'relay wcfrelay create --resource-group {rg} --namespace-name {namespacename} --name {wcfrelayname} --relay-type {relaytype} --requires-client-authorization {requiresclientauthorization} --requires-transport-security {requirestransportsecurity} --user-metadata {usermetadata}',
            checks=[self.check('name', self.kwargs['wcfrelayname'])])

        # Get WCFRelay
        self.cmd('relay wcfrelay show --resource-group {rg} --namespace-name {namespacename} --name {wcfrelayname}',
                 checks=[self.check('name', self.kwargs['wcfrelayname'])])

        # WCFRelay List
        listwcfrelay = self.cmd('relay wcfrelay list --resource-group {rg} --namespace-name {namespacename}').output
        self.assertGreater(len(listwcfrelay), 0)

        # Create Authoriazation Rule
        self.cmd(
            'relay wcfrelay authorizationrule create --resource-group {rg} --namespace-name {namespacename} --wcfrelay-name {wcfrelayname} --name {wcfrelayauthoname} --access-rights {accessrights}',
            checks=[self.check('name', self.kwargs['wcfrelayauthoname'])])

        # Get Create Authorization Rule
        self.cmd(
            'relay wcfrelay authorizationrule show --resource-group {rg} --namespace-name {namespacename} --wcfrelay-name {wcfrelayname} --name {wcfrelayauthoname}',
            checks=[self.check('name', self.kwargs['wcfrelayauthoname'])])

        # Get Authorization Rule Listkeys
        self.cmd(
            'relay wcfrelay authorizationrule keys list --resource-group {rg} --namespace-name {namespacename} --wcfrelay-name {wcfrelayname} --name {wcfrelayauthoname}')

        # Regeneratekeys - Primary
        regenrateprimarykeyresult = self.cmd(
            'relay wcfrelay authorizationrule keys renew --resource-group {rg} --namespace-name {namespacename} --wcfrelay-name {wcfrelayname} --name {wcfrelayauthoname} --key-name {primary}')
        self.assertIsNotNone(regenrateprimarykeyresult)

        # Regeneratekeys - Secondary
        regenratesecondarykeyresult = self.cmd(
            'relay wcfrelay authorizationrule keys renew --resource-group {rg} --namespace-name {namespacename} --wcfrelay-name {wcfrelayname} --name {wcfrelayauthoname} --key-name {secondary}')
        self.assertIsNotNone(regenratesecondarykeyresult)

        # Delete WCFRelay AuthorizationRule
        self.cmd(
            'relay wcfrelay authorizationrule delete --resource-group {rg} --namespace-name {namespacename} --wcfrelay-name {wcfrelayname} --name {wcfrelayauthoname}')

        # Delete WCFRelay
        self.cmd('relay wcfrelay delete --resource-group {rg} --namespace-name {namespacename} --name {wcfrelayname}')

        # Delete Namespace
        self.cmd('relay namespace delete --resource-group {rg} --name {namespacename}')

    @ResourceGroupPreparer(name_prefix='cli_test_relay_hybridconnection')
    def test_relay_hybridconnection(self, resource_group):
        self.kwargs.update({
            'loc': 'westus2',
            'rg': resource_group,
            'namespacename': self.create_random_name(prefix='relay-nscli', length=20),
            'tags': {'tag1: value1', 'tag2: value2'},
            'sku': 'Standard',
            'tier': 'Standard',
            'authoname': self.create_random_name(prefix='cliAutho', length=20),
            'defaultauthorizationrule': 'RootManageSharedAccessKey',
            'accessrights': 'Listen',
            'primary': 'PrimaryKey',
            'secondary': 'SecondaryKey',
            'hybridconnectionname': self.create_random_name(prefix='relay-hybridcli', length=25),
            'hybridconnectionauthoname': self.create_random_name(prefix='clihybridAutho', length=25),
            'requiresclientauthorization': 'True',
            'usermetadata': 'UserMetadata'
        })

        # Create Namespace
        self.cmd('relay namespace create --resource-group {rg} --name {namespacename} --location {loc} --tags {tags} --sku-tier {tier}',
                 checks=[self.check('sku.tier', self.kwargs['tier'])])

        # Get Created Namespace
        self.cmd('relay namespace show --resource-group {rg} --name {namespacename}',
                 checks=[self.check('sku.tier', self.kwargs['tier'])])

        # Create Hybrid Connections
        self.cmd('relay hybrid-connections create --resource-group {rg} --namespace-name {namespacename} --name {hybridconnectionname} --requires-client-authorization {requiresclientauthorization} --user-metadata {usermetadata}', checks=[self.check('name', self.kwargs['hybridconnectionname'])])

        # Get Hybrid Connections
        self.cmd('relay hybrid-connections show --resource-group {rg} --namespace-name {namespacename} --name {hybridconnectionname}', checks=[self.check('name', self.kwargs['hybridconnectionname'])])

        # Hybrid Connections List
        listhybirdconnection = self.cmd('relay hybrid-connections list --resource-group {rg} --namespace-name {namespacename}').output
        self.assertGreater(len(listhybirdconnection), 0)

        # Create Authoriazation Rule
        self.cmd('relay hybrid-connections authorizationrule create --resource-group {rg} --namespace-name {namespacename} --hybrid-connection-name {hybridconnectionname} --name {hybridconnectionauthoname} --access-rights {accessrights}', checks=[self.check('name', self.kwargs['hybridconnectionauthoname'])])

        # Get Create Authorization Rule
        self.cmd('relay hybrid-connections authorizationrule show --resource-group {rg} --namespace-name {namespacename} --hybrid-connection-name {hybridconnectionname} --name {hybridconnectionauthoname}', checks=[self.check('name', self.kwargs['hybridconnectionauthoname'])])

        # Get Authorization Rule Listkeys
        self.cmd('relay hybrid-connections authorizationrule keys list --resource-group {rg} --namespace-name {namespacename} --hybrid-connection-name {hybridconnectionname} --name {hybridconnectionauthoname}')

        # Regeneratekeys - Primary
        regenrateprimarykeyresult = self.cmd('relay hybrid-connections authorizationrule keys renew --resource-group {rg} --namespace-name {namespacename} --hybrid-connection-name {hybridconnectionname} --name {hybridconnectionauthoname} --key-name {primary}')
        self.assertIsNotNone(regenrateprimarykeyresult)

        # Regeneratekeys - Secondary
        regenratesecondarykeyresult = self.cmd('relay hybrid-connections authorizationrule keys renew --resource-group {rg} --namespace-name {namespacename} --hybrid-connection-name {hybridconnectionname} --name {hybridconnectionauthoname} --key-name {secondary}')
        self.assertIsNotNone(regenratesecondarykeyresult)

        # Delete Hybrid Connections AuthorizationRule
        self.cmd('relay hybrid-connections authorizationrule delete --resource-group {rg} --namespace-name {namespacename} --hybrid-connection-name {hybridconnectionname} --name {hybridconnectionauthoname}')

        # Delete Hybrid Connections
        self.cmd('relay hybrid-connections delete --resource-group {rg} --namespace-name {namespacename} --name {hybridconnectionname}')

        # Delete Namespace
        self.cmd('relay namespace delete --resource-group {rg} --name {namespacename}')
