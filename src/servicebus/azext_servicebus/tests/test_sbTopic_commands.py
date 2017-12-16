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


class SBTopicsCURDScenarioTest(ScenarioTest):

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
            'topicname': self.create_random_name(prefix='sb-topiccli', length=25),
            'topicauthoname': self.create_random_name(prefix='cliTopicAutho', length=25)
        })

        # Create Namespace
        createnamespaceresult = self.cmd(
            'servicebus namespace create --resource-group {rg} --name {namespacename} '
                          '--location {loc} --tags {tags} --sku-name {sku} --skutier {tier}',
                          checks=[self.check('sku.name', self.kwargs['sku'])]).output

        # Get Created Namespace
        getnamespaceresult = self.cmd(
            'servicebus namespace get --resource-group {rg} --name {namespacename}',
                          checks=[self.check('sku.name', self.kwargs['sku'])]).output

        # Create Topic
        createtopicresult = self.cmd(
            'servicebus topic create --resource-group {rg} --namespace-name {namespacename} --name {topicname} ',
                                     checks=[self.check('name', self.kwargs['topicname'])]).output

        # Get Topic
        gettopicresult = self.cmd(
            'servicebus topic get --resource-group {rg} --namespace-name {namespacename} --name {topicname} ',
            checks=[self.check('name', self.kwargs['topicname'])]).output

        # Topic List
        listtopicresult = self.cmd(
            'servicebus topic list --resource-group {rg} --namespace-name {namespacename}').output

        # Create Authoriazation Rule
        # createauthorizationruleresult = self.cmd('servicebus namespace authorizationrule create --resource-group {rg} --namespace-name {namespacename} --name {authoname} --access-rights {accessrights}',
        createauthorizationruleresult = self.cmd(
            'servicebus topic authorizationrule create --resource-group {rg} --namespace-name {namespacename} --topic-name {topicname} --name {authoname}',
                          checks=[self.check('name', self.kwargs['authoname'])]).output

        # Get Create Authorization Rule
        getauthorizationruleresult = self.cmd(
            'servicebus topic authorizationrule get --resource-group {rg} --namespace-name {namespacename} --topic-name {topicname} --name {authoname}',
            checks=[self.check('name', self.kwargs['authoname'])]).output

        # Get Authorization Rule Listkeys
        authorizationrulelistkeysresult = self.cmd(
            'servicebus topic authorizationrule listkeys --resource-group {rg} --namespace-name {namespacename} --topic-name {topicname} --name {authoname}').output

        # Regeneratekeys - Primary
        regenrateprimarykeyresult = self.cmd(
            'servicebus topic authorizationrule regeneratekeys --resource-group {rg} --namespace-name {namespacename} --topic-name {topicname} --name {authoname} --regeneratekey {primary}').output
        self.assertIsNotNone(regenrateprimarykeyresult)

        # Regeneratekeys - Secondary
        regenratesecondarykeyresult = self.cmd(
            'servicebus topic authorizationrule regeneratekeys --resource-group {rg} --namespace-name {namespacename} --topic-name {topicname} --name {authoname} --regeneratekey {secondary}').output
        self.assertIsNotNone(regenratesecondarykeyresult)

        # Delete Topic AuthorizationRule
        deleteauthorizationruleresult = self.cmd(
            'servicebus topic authorizationrule delete --resource-group {rg} --namespace-name {namespacename} --topic-name {topicname} --name {authoname}').output

        # Delete Topic
        self.cmd('servicebus topic delete --resource-group {rg} --namespace-name {namespacename} --name {topicname}')

        # Delete Namespace
        self.cmd('servicebus namespace delete --resource-group {rg} --name {namespacename}')
