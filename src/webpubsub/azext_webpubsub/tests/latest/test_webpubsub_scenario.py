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
    def test_webpubsub(self, resource_group):
        tags_key = 'key'
        tags_val = 'value'
        updated_tags_val = 'value2'

        self.kwargs.update({
            'name': self.create_random_name('webpubsub', 16),
            'sku': 'Standard_S1',
            'location': 'eastus',
            'tags': '{}={}'.format(tags_key, tags_val),
            'unit_count': 1,
            'updated_tags': '{}={}'.format(tags_key, updated_tags_val),
            'updated_sku': 'Free_F1'
        })

        # Test create
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

        # Test show
        self.cmd('webpubsub show -g {rg} -n {name}', checks=[
            self.check('name', '{name}'),
            self.check('location', '{location}'),
            self.check('provisioningState', 'Succeeded'),
            self.check('sku.name', '{sku}'),
            self.check('sku.capacity', '{unit_count}'),
            self.exists('hostName'),
            self.exists('publicPort'),
            self.exists('serverPort'),
            self.exists('externalIp'),
        ])

        # Test list
        self.cmd('webpubsub list -g {rg}', checks=[
            self.check('[0].name', '{name}'),
            self.check('[0].location', '{location}'),
            self.check('[0].provisioningState', 'Succeeded'),
            self.check('[0].sku.name', '{sku}'),
            self.check('[0].sku.capacity', '{unit_count}'),
            self.exists('[0].hostName'),
            self.exists('[0].publicPort'),
            self.exists('[0].serverPort'),
            self.exists('[0].externalIp'),
        ])

        # Test update
        self.cmd('webpubsub update -g {rg} -n {name} --tags {updated_tags} --sku {updated_sku}', checks=[
            self.check('name', '{name}'),
            self.check('location', '{location}'),
            self.check('provisioningState', 'Succeeded'),
            self.check('sku.name', '{updated_sku}'),
            self.check('tags.{}'.format(tags_key), updated_tags_val),
            self.exists('hostName'),
            self.exists('publicPort'),
            self.exists('serverPort'),
            self.exists('externalIp'),
        ])

        # Test key show
        self.cmd('webpubsub key show -n {name} -g {rg}', checks=[
            self.exists('primaryKey'),
            self.exists('secondaryKey')
        ])

        # Test list skus
        self.cmd('webpubsub list-skus -n {name} -g {rg}', checks=[
            self.check('[0].sku.name', 'Free_F1'),
            self.check('[1].sku.name', 'Standard_S1')
        ])

        # Test list usage
        self.cmd('webpubsub list-usage -l {location}', checks=[
            self.check('[0].name.value', 'FreeTierInstances'),
            self.check('[1].name.value', 'SignalRTotalUnits')
        ])

        # Test key regenerate
        self.cmd('webpubsub key regenerate -n {name} -g {rg} --key-type secondary', checks=[
            self.exists('primaryKey'),
            self.exists('secondaryKey')
        ])

        # Test key regenerate salt
        self.cmd('webpubsub key regenerate -n {name} -g {rg} --key-type salt', checks=[
            self.exists('primaryKey'),
            self.exists('secondaryKey')
        ])

        # Test delete
        count = len(self.cmd('webpubsub list').get_output_in_json())
        self.cmd('webpubsub delete -g {rg} -n {name}')
        final_count = len(self.cmd('webpubsub list').get_output_in_json())
        self.assertTrue(final_count == count - 1)
