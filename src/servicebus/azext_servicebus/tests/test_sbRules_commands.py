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


class SBRulesCURDScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_sb_namespace')
    def test_sb_rules(self, resource_group):

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
            'topicauthoname': self.create_random_name(prefix='cliTopicAutho', length=25),
            'subscriptionname': self.create_random_name(prefix='sb-subscli', length=25),
            'rulename': self.create_random_name(prefix='sb-rulecli', length=25),
            'sqlexpression': 'test=test'
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

        # Create Topic
        createtopicresult = self.cmd(
            'sb topic create --resource-group {rg} --namespace-name {namespacename} --name {topicname} ',
                                     checks=[self.check('name', self.kwargs['topicname'])]).output

        # Get Topic
        gettopicresult = self.cmd(
            'sb topic get --resource-group {rg} --namespace-name {namespacename} --name {topicname} ',
            checks=[self.check('name', self.kwargs['topicname'])]).output

        # Create Subscription
        createsubscriptionresult = self.cmd(
            'sb subscription create --resource-group {rg} --namespace-name {namespacename} --topic-name {topicname} --name {subscriptionname}',
            checks=[self.check('name', self.kwargs['subscriptionname'])]).output

        # Get Create Subscription
        getsubscriptionresult = self.cmd(
            'sb subscription get --resource-group {rg} --namespace-name {namespacename} --topic-name {topicname} --name {subscriptionname}',
            checks=[self.check('name', self.kwargs['subscriptionname'])]).output

        # Create Rules
        createrulesresult = self.cmd(
            'sb rule create --resource-group {rg} --namespace-name {namespacename} --topic-name {topicname} --subscription-name {subscriptionname} --name {rulename} --filter-sql-expression {sqlexpression}',
            checks=[self.check('name', self.kwargs['rulename'])]).output

        # Get Created Rules
        getrulesnresult = self.cmd(
            'sb rule get --resource-group {rg} --namespace-name {namespacename} --topic-name {topicname} --subscription-name {subscriptionname} --name {rulename}',
            checks=[self.check('name', self.kwargs['rulename'])]).output

        # Get Rules List By Subscription
        listrulesnresult = self.cmd(
            'sb rule list --resource-group {rg} --namespace-name {namespacename} --topic-name {topicname} --subscription-name {subscriptionname}').output
        self.assertGreater(len(listrulesnresult), 0)

        # Delete create Subscription
        self.cmd(
            'sb rule delete --resource-group {rg} --namespace-name {namespacename} --topic-name {topicname} --subscription-name {subscriptionname} --name {rulename}')

        # Delete create Subscription
        self.cmd('sb subscription delete --resource-group {rg} --namespace-name {namespacename} --topic-name {topicname} --name {subscriptionname}')

        # Delete Topic
        self.cmd('sb topic delete --resource-group {rg} --namespace-name {namespacename} --name {topicname}')

        # Delete Namespace
        self.cmd('sb namespace delete --resource-group {rg} --name {namespacename}')
