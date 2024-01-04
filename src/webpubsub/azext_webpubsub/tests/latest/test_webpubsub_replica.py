# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-import, line-too-long, unused-argument
import os
import unittest

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from .recording_processors import KeyReplacer


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class WebpubsubScenarioTest(ScenarioTest):

    def __init__(self, method_name):
        super(WebpubsubScenarioTest, self).__init__(
            method_name, recording_processors=[KeyReplacer()]
        )

    @ResourceGroupPreparer(random_name_length=20)
    def test_webpubsub_replica(self, resource_group):
        tags_key = 'key'
        tags_val = 'value'
        updated_tags_val = 'value2'
        replica_name = 'clitestReplica'
        replica_location = 'westus'

        self.kwargs.update({
            'name': self.create_random_name('webpubsub', 16),
            'sku': 'Premium_P1',
            'location': 'eastus',
            'tags': '{}={}'.format(tags_key, tags_val),
            'unit_count': 1,
            'updated_tags': '{}={}'.format(tags_key, updated_tags_val),
            'replica_name': replica_name,
            'replica_location': replica_location
        })

        # Test create primary
        self.cmd('webpubsub create -g {rg} -n {name} --tags {tags} -l {location} --sku {sku} --unit-count {unit_count}', checks=[
            self.check('name', '{name}'),
            self.check('location', '{location}'),
            self.check('provisioningState', 'Succeeded'),
            self.check('sku.name', '{sku}'),
            self.check('sku.capacity', '{unit_count}'),
            self.check('tags.{}'.format(tags_key), tags_val),
            self.exists('hostName'),
            self.exists('publicPort'),
            self.exists('serverPort'),
            self.exists('externalIp'),
        ])

          # test create replica
        self.cmd('az webpubsub replica create -n {name} --replica-name {replica_name} -g {rg} --sku {sku} --unit-count {unit_count} -l {replica_location} --tags {tags}', checks=[
            self.check('name', '{replica_name}'),
            self.check('location', '{replica_location}'),
            self.check('provisioningState', 'Succeeded'),
            self.check('sku.name', '{sku}'),
            self.check('tags.{}'.format(tags_key), tags_val),
        ])

       # test show replica
        self.cmd('az webpubsub replica show -n {name} --replica-name {replica_name} -g {rg}', checks=[
            self.check('name', '{replica_name}'),
            self.check('location', '{replica_location}'),
            self.check('provisioningState', 'Succeeded'),
            self.check('sku.name', '{sku}'),
            self.check('tags.{}'.format(tags_key), tags_val),
        ])

        # test list replica
        self.cmd('az webpubsub replica list -n {name} -g {rg}', checks=[
            self.check('[0].name', '{replica_name}'),
            self.check('[0].location', '{replica_location}'),
            self.check('[0].provisioningState', 'Succeeded'),
            self.check('[0].sku.name', '{sku}'),
            self.check('[0].tags.{}'.format(tags_key), tags_val),
        ])

        # test remove replica
        self.cmd('az webpubsub replica delete -n {name} --replica-name {replica_name} -g {rg}')
