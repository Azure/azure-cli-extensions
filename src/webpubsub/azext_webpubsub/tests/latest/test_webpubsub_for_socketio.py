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


class WebpubsubForSocketIOTest(ScenarioTest):

    def __init__(self, method_name):
        super(WebpubsubForSocketIOTest, self).__init__(
            method_name, recording_processors=[KeyReplacer()]
        )

    @ResourceGroupPreparer(random_name_length=20)
    def test_webpubsub_for_socketio(self, resource_group):
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
            'updated_sku': 'Free_F1',
            'kind': 'SocketIO',
        })

        # Test Web PubSub for Socket.IO
        self.cmd('webpubsub create -g {rg} -n {name} --tags {tags} -l {location} --sku {sku} --unit-count {unit_count} --kind {kind}', checks=[
            self.check('name', '{name}'),
            self.check('location', '{location}'),
            self.check('provisioningState', 'Succeeded'),
            self.check('sku.name', '{sku}'),
            self.check('sku.capacity', '{unit_count}'),
            self.check('tags.{}'.format(tags_key), tags_val),
            self.check('kind', '{kind}'),
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
            self.check('kind', '{kind}'),
            self.exists('hostName'),
            self.exists('publicPort'),
            self.exists('serverPort'),
            self.exists('externalIp'),
        ])

        # Test Web PubSub for Socket.IO
        self.cmd('webpubsub create -g {rg} -n {name} --tags {tags} -l {location} --sku {sku} --unit-count {unit_count} --kind SocketIO', checks=[
            self.check('name', '{name}'),
            self.check('location', '{location}'),
            self.check('provisioningState', 'Succeeded'),
            self.check('sku.name', '{sku}'),
            self.check('sku.capacity', '{unit_count}'),
            self.check('tags.{}'.format(tags_key), tags_val),
            self.check('kind', "SocketIO"),
            self.exists('hostName'),
            self.exists('publicPort'),
            self.exists('serverPort'),
            self.exists('externalIp'),
        ])
