# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from .recording_processors import KeyReplacer


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class WebpubsubNetworkTest(ScenarioTest):

    def __init__(self, method_name):
        super(WebpubsubNetworkTest, self).__init__(
            method_name, recording_processors=[KeyReplacer()]
        )

    @ResourceGroupPreparer(random_name_length=20)
    def test_webpubsub_network(self, resource_group):
        tags_key = 'key'
        tags_val = 'value'
        self.kwargs.update({
            'name': self.create_random_name('webpubsub', 16),
            'sku': 'Standard_S1',
            'location': 'eastus',
            'tags': '{}={}'.format(tags_key, tags_val),
            'unit_count': 1,
        })

        # Test create primary
        self.cmd('webpubsub create -g {rg} -n {name} --tags {tags} -l {location} --sku {sku} --unit-count {unit_count}', checks=[
            self.check('name', '{name}'),
            self.check('location', '{location}'),
            self.check('provisioningState', 'Succeeded'),
            self.check('sku.name', '{sku}'),
            self.check('sku.capacity', '{unit_count}'),
            self.check('tags.key', 'value'),
            self.exists('hostName'),
            self.exists('publicPort'),
            self.exists('serverPort'),
            self.exists('externalIp'),
        ])

        # Test update public network rules
        self.cmd('webpubsub network-rule update -g {rg} -n {name} --public-network --allow ServerConnection ClientConnection --deny RESTAPI Trace', checks=[
            self.check('networkAcLs.publicNetwork.allow[0]', 'ServerConnection'),
            self.check('networkAcLs.publicNetwork.allow[1]', 'ClientConnection'),
            self.check('networkAcLs.publicNetwork.deny[0]', 'RESTAPI'),
            self.check('networkAcLs.publicNetwork.deny[1]', 'Trace'),
        ])

        # Test add IP rule
        self.cmd('webpubsub network-rule ip-rule add -g {rg} -n {name} --ip-rule value="10.0.0.0/24" action="Allow" --ip-rule value="192.168.0.0/24" action="Deny"', checks=[
            self.check('networkAcLs.ipRules[0].value', '0.0.0.0/0'),  # default allow
            self.check('networkAcLs.ipRules[0].action', 'Allow'),
            self.check('networkAcLs.ipRules[1].value', '::/0'),  # default allow
            self.check('networkAcLs.ipRules[1].action', 'Allow'),
            self.check('networkAcLs.ipRules[2].value', '10.0.0.0/24'),
            self.check('networkAcLs.ipRules[2].action', 'Allow'),
            self.check('networkAcLs.ipRules[3].value', '192.168.0.0/24'),
            self.check('networkAcLs.ipRules[3].action', 'Deny'),
        ])

        # Test show network rules
        self.cmd('webpubsub network-rule show -g {rg} -n {name}', checks=[
            self.check('publicNetwork.allow[0]', 'ServerConnection'),
            self.check('publicNetwork.allow[1]', 'ClientConnection'),
            self.check('publicNetwork.deny[0]', 'RESTAPI'),
            self.check('publicNetwork.deny[1]', 'Trace'),
            self.check('ipRules[0].value', '0.0.0.0/0'),  # default allow
            self.check('ipRules[0].action', 'Allow'),
            self.check('ipRules[1].value', '::/0'),  # default allow
            self.check('ipRules[1].action', 'Allow'),
            self.check('ipRules[2].value', '10.0.0.0/24'),
            self.check('ipRules[2].action', 'Allow'),
            self.check('ipRules[3].value', '192.168.0.0/24'),
            self.check('ipRules[3].action', 'Deny'),
        ])

        # Test remove IP rule
        self.cmd('webpubsub network-rule ip-rule remove -g {rg} -n {name} --ip-rule value="10.0.0.0/24" action="Allow" --ip-rule value="192.168.0.0/24" action="Deny"', checks=[
            self.check('networkAcLs.ipRules[0].value', '0.0.0.0/0'),  # default allow
            self.check('networkAcLs.ipRules[0].action', 'Allow'),
            self.check('networkAcLs.ipRules[1].value', '::/0'),  # default allow
            self.check('networkAcLs.ipRules[1].action', 'Allow'),
        ])
