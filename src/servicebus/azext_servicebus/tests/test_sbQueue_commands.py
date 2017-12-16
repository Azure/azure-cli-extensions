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

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

# pylint: disable=line-too-long
# pylint: disable=too-many-lines


class SBQueueCURDScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_sb_namespace')
    def test_sb_namespace(self, resource_group):

        self.kwargs.update({
            'loc': 'westus2',
            'namespacename': self.create_random_name(prefix='sb-nscli', length=20),
            'tags': {'tag1: value1', 'tag2: value2'},
            'sku': 'Standard',
            'tier': 'Standard',
            'authoname': self.create_random_name(prefix='cliAutho', length=20),
            'defaultauthorizationrule': 'RootManageSharedAccessKey',
            'accessrights': 'Send, Listen',
            'primary': 'PrimaryKey',
            'secondary': 'SecondaryKey',
            'queuename': self.create_random_name(prefix='sb-queuecli', length=25),
            'queueauthoname': self.create_random_name(prefix='cliQueueAutho', length=25),
            'lock_duration': 'PT10M'

        })

        # Create Namespace
        createnamespaceresult = self.cmd(
            'sb namespace create --resource-group {rg} --name {namespacename} '
                          '--location {loc} --tags {tags} --sku-name {sku} --skutier {tier}',
                          checks=[self.check('sku.name', self.kwargs['sku'])]).output

        # Get Created Namespace
        getnamespaceresult = self.cmd(
            'sb namespace get --resource-group {rg} --name {namespacename}',
                          checks=[self.check('sku.name', self.kwargs['sku'])]).output

        # Create Queue
        createqueueresult = self.cmd(
            'sb queue create --resource-group {rg} --namespace-name {namespacename} --name {queuename} --auto-delete-on-idle {lock_duration} ',
                                     checks=[self.check('name', self.kwargs['queuename'])]).output

        # Get Queue
        getqueueresult = self.cmd(
            'sb queue get --resource-group {rg} --namespace-name {namespacename} --name {queuename}',
            checks=[self.check('name', self.kwargs['queuename'])]).output

        # Queue List
        listqueueresult = self.cmd(
            'sb queue list --resource-group {rg} --namespace-name {namespacename}').output

        # Create Authoriazation Rule
        # createauthorizationruleresult = self.cmd('sb namespace authorizationrule create --resource-group {rg} --namespace-name {namespacename} --name {authoname} --access-rights {accessrights}',
        createauthorizationruleresult = self.cmd(
            'sb queue authorizationrule create --resource-group {rg} --namespace-name {namespacename} --queue-name {queuename} --name {authoname}',
                          checks=[self.check('name', self.kwargs['authoname'])]).output

        # Get Create Authorization Rule
        getauthorizationruleresult = self.cmd(
            'sb queue authorizationrule get --resource-group {rg} --namespace-name {namespacename} --queue-name {queuename} --name {authoname}',
            checks=[self.check('name', self.kwargs['authoname'])]).output

        # Get Authorization Rule Listkeys
        authorizationrulelistkeysresult = self.cmd(
            'sb queue authorizationrule listkeys --resource-group {rg} --namespace-name {namespacename} --queue-name {queuename} --name {authoname}').output

        # Regeneratekeys - Primary
        regenrateprimarykeyresult = self.cmd(
            'sb queue authorizationrule regeneratekeys --resource-group {rg} --namespace-name {namespacename} --queue-name {queuename} --name {authoname} --regeneratekey {primary}').output
        self.assertIsNotNone(regenrateprimarykeyresult)

        # Regeneratekeys - Secondary
        regenratesecondarykeyresult = self.cmd(
            'sb queue authorizationrule regeneratekeys --resource-group {rg} --namespace-name {namespacename} --queue-name {queuename} --name {authoname} --regeneratekey {secondary}').output
        self.assertIsNotNone(regenratesecondarykeyresult)

        # Delete Queue AuthorizationRule
        deleteauthorizationruleresult = self.cmd(
            'sb queue authorizationrule delete --resource-group {rg} --namespace-name {namespacename} --queue-name {queuename} --name {authoname}').output

        # Delete Queue
        self.cmd('sb queue delete --resource-group {rg} --namespace-name {namespacename} --name {queuename}')

        # Delete Namespace
        self.cmd('sb namespace delete --resource-group {rg} --name {namespacename}')



