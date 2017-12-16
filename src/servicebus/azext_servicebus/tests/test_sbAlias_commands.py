# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# AZURE CLI VM TEST DEFINITIONS
import json
import os
import platform
import tempfile
import time
import unittest
import mock
import uuid

import six

from knack.util import CLIError

from azure.cli.core.profiles import ResourceType
from azure.cli.testsdk import (
    ScenarioTest, ResourceGroupPreparer, LiveScenarioTest, api_version_constraint, StorageAccountPreparer)
from azure.mgmt.servicebus.models import ProvisioningStateDR, SBNamespace

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

# pylint: disable=line-too-long
# pylint: disable=too-many-lines


class SBAliasCURDScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_sb_namespace')
    def test_sb_alias(self, resource_group):

        self.kwargs.update({
            'loc_south': 'SouthCentralUS',
            'loc_north': 'NorthCentralUS',
            'namespacenameprimary': self.create_random_name(prefix='sb-nscli', length=20),
            'namespacenamesecondary': self.create_random_name(prefix='sb-nscli', length=20),
            'tags': {'tag1: value1', 'tag2: value2'},
            'sku': 'Premium',
            'tier': 'Premium',
            'authoname':  self.create_random_name(prefix='cliAutho', length=20),
            'defaultauthorizationrule': 'RootManageSharedAccessKey',
            'accessrights': 'Send, Listen',
            'primary': 'PrimaryKey',
            'secondary': 'SecondaryKey',
            'aliasname': self.create_random_name(prefix='cliAlias', length=20),
            'alternatename': self.create_random_name(prefix='cliAlter', length=20),
            'id': '',
            'test': ''
        })

        checknamespaceresult = self.cmd('sb namespace check_name_availability --name {namespacenameprimary}', checks=[self.check('nameAvailable', True)]).output

        self.kwargs.update({'test': json.loads(checknamespaceresult)['reason']})

        # Create Namespace - Primary
        createnames1paceresult = self.cmd('sb namespace create --resource-group {rg} --name {namespacenameprimary} --location {loc_south} --tags {tags} --sku-name {sku} --skutier {tier}', checks=[self.check('sku.name', self.kwargs['sku'])]).output

        # Get Created Namespace - Primary
        getnamespace1result = self.cmd('sb namespace get --resource-group {rg} --name {namespacenameprimary}', checks=[self.check('sku.name', self.kwargs['sku'])]).output

        # Create Namespace - Secondary
        createnamespace2result = self.cmd('sb namespace create --resource-group {rg} --name {namespacenamesecondary} --location {loc_north} --tags {tags} --sku-name {sku} --skutier {tier}', checks=[self.check('sku.name', self.kwargs['sku'])]).output

        # Get Created Namespace - Secondary
        getnamespace2result = self.cmd('sb namespace get --resource-group {rg} --name {namespacenamesecondary}', checks=[self.check('sku.name', self.kwargs['sku'])]).output

        # Create Authoriazation Rule
        # createauthorizationruleresult = self.cmd('sb namespace authorizationrule create --resource-group {rg} --namespace-name {namespacename} --name {authoname} --access-rights {accessrights}',
        createauthorizationruleresult = self.cmd(
           'sb namespace authorizationrule create --resource-group {rg} --namespace-name {namespacenameprimary} --name {authoname}', checks=[self.check('name', self.kwargs['authoname'])]).output

        partnernamespaceid = json.loads(getnamespace2result)['id']
        self.kwargs.update({'id': partnernamespaceid})
        # Get Create Authorization Rule
        getauthorizationruleresult = self.cmd(
            'sb namespace authorizationrule get --resource-group {rg} --namespace-name {namespacenameprimary} --name {authoname}', checks=[self.check('name', self.kwargs['authoname'])]).output

        # CheckNameAvailability - Alias

        checkaliasresult = self.cmd('sb alias check_name_availability --resource-group {rg} --namespace-name {namespacenameprimary} --alias {aliasname}', checks=[self.check('nameAvailable', True)]).output

        # Create alias
        createalias = self.cmd('sb alias create  --resource-group {rg} --namespace-name {namespacenameprimary} --alias {aliasname} --partner-namespace {id}').output

        # get alias - Primary
        getaliasprimary = self.cmd(
            'sb alias get  --resource-group {rg} --namespace-name {namespacenameprimary} --alias {aliasname}').output

        # get alias - Secondary
        getaliassecondary = self.cmd(
            'sb alias get  --resource-group {rg} --namespace-name {namespacenamesecondary} --alias {aliasname}').output

        getaliasprimarynamespace = self.cmd(
            'sb alias get  --resource-group {rg} --namespace-name {namespacenameprimary} --alias {aliasname}').output

        #check for the Alias Provisioning succeeded
        while json.loads(getaliasprimarynamespace)['provisioningState'] != ProvisioningStateDR.succeeded.value:
            time.sleep(30)
            getaliasprimarynamespace = self.cmd(
                'sb alias get  --resource-group {rg} --namespace-name {namespacenameprimary} --alias {aliasname}').output


        # Break Pairing
        breakpairing = self.cmd(
            'sb alias break_pairing  --resource-group {rg} --namespace-name {namespacenameprimary} --alias {aliasname}').output

        getaliasafterbreak = self.cmd(
            'sb alias get  --resource-group {rg} --namespace-name {namespacenameprimary} --alias {aliasname}').output

        # check for the Alias Provisioning succeeded
        while json.loads(getaliasafterbreak)['provisioningState'] != ProvisioningStateDR.succeeded.value:
            time.sleep(30)
            getaliasafterbreak = self.cmd(
                'sb alias get  --resource-group {rg} --namespace-name {namespacenameprimary} --alias {aliasname}').output


        # Create alias
        createalias = self.cmd(
            'sb alias create  --resource-group {rg} --namespace-name {namespacenameprimary} --alias {aliasname} --partner-namespace {id}').output

        getaliasaftercreate = self.cmd(
            'sb alias get  --resource-group {rg} --namespace-name {namespacenameprimary} --alias {aliasname}').output

        # check for the Alias Provisioning succeeded
        while json.loads(getaliasaftercreate)['provisioningState'] != ProvisioningStateDR.succeeded.value:
            time.sleep(30)
            getaliasaftercreate = self.cmd(
                'sb alias get  --resource-group {rg} --namespace-name {namespacenameprimary} --alias {aliasname}').output

        # FailOver
        failover = self.cmd(
            'sb alias fail_over  --resource-group {rg} --namespace-name {namespacenamesecondary} --alias {aliasname}').output

        getaliasafterfail = self.cmd(
            'sb alias get  --resource-group {rg} --namespace-name {namespacenamesecondary} --alias {aliasname}').output

        # check for the Alias Provisioning succeeded
        while json.loads(getaliasafterfail)['provisioningState'] != ProvisioningStateDR.succeeded.value:
            time.sleep(30)
            getaliasafterfail = self.cmd(
                'sb alias get  --resource-group {rg} --namespace-name {namespacenamesecondary} --alias {aliasname}').output

        # Delete Alias
        deleteailais = self.cmd(
            'sb alias delete  --resource-group {rg} --namespace-name {namespacenamesecondary} --alias {aliasname}').output

        # Delete Namespace - primary
        self.cmd('sb namespace delete --resource-group {rg} --name {namespacenameprimary}')

        # Delete Namespace - secondary
        self.cmd('sb namespace delete --resource-group {rg} --name {namespacenamesecondary}')



