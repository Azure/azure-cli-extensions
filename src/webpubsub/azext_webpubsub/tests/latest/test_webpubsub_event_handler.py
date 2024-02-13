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


class WebpubsubEventHandlerTest(ScenarioTest):

    def __init__(self, method_name):
        super(WebpubsubEventHandlerTest, self).__init__(
            method_name, recording_processors=[KeyReplacer()]
        )

    @ResourceGroupPreparer(random_name_length=20)
    def test_webpubsub_event_handler(self, resource_group):
        tags_key = 'key'
        tags_val = 'value'
        updated_tags_val = 'value2'
        curr_dir = os.path.dirname(os.path.realpath(__file__))
        self.kwargs.update({
            'name': self.create_random_name('webpubsub', 16),
            'sku': 'Standard_S1',
            'location': 'westcentralus',
            'tags': '{}={}'.format(tags_key, tags_val),
            'unit_count': 1,
            'updated_tags': '{}={}'.format(tags_key, updated_tags_val),
            'updated_sku': 'Free_F1',
            'hub': 'myHub',
            'urlTemplate1': 'http://host.com',
            'userEventPattern1': 'event1,event2',
            'systemEventPattern1': 'connect',
            'systemEvents1': ['connect'],
            'urlTemplate2': 'http://host2.com',
            'userEventPattern2': 'event3,event4',
            'systemEventPattern2': 'disconnect,connected',
            'systemEvents2': ['disconnect', 'connected'],
            'authResource': 'uri://abc',
            'params': os.path.join(curr_dir, 'parameter.json').replace('\\', '\\\\'),
        })

        # Create
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

        # Test hub creation
        self.cmd('webpubsub hub create -g {rg} -n {name} --hub-name {hub} --event-handler url-template={urlTemplate1} user-event-pattern={userEventPattern1} system-event=connect', checks=[
            self.check('name', '{hub}'),
            self.check('properties.anonymousConnectPolicy', 'deny'),
            self.check('properties.eventHandlers[0].urlTemplate', '{urlTemplate1}'),
            self.check('properties.eventHandlers[0].userEventPattern', '{userEventPattern1}'),
            self.check('properties.eventHandlers[0].systemEvents[0]', 'connect'),
        ])

        # Test hub show
        self.cmd('webpubsub hub show -g {rg} -n {name} --hub-name {hub}', checks=[
            self.check('name', '{hub}'),
            self.check('properties.anonymousConnectPolicy', 'deny'),
            self.check('properties.eventHandlers[0].urlTemplate', '{urlTemplate1}'),
            self.check('properties.eventHandlers[0].userEventPattern', '{userEventPattern1}'),
            self.check('properties.eventHandlers[0].systemEvents[0]', 'connect'),
        ])

        # Test hub list
        self.cmd('webpubsub hub list -g {rg} -n {name}', checks=[
            self.check('[0].name', '{hub}'),
            self.check('[0].properties.anonymousConnectPolicy', 'deny'),
            self.check('[0].properties.eventHandlers[0].urlTemplate', '{urlTemplate1}'),
            self.check('[0].properties.eventHandlers[0].userEventPattern', '{userEventPattern1}'),
            self.check('[0].properties.eventHandlers[0].systemEvents[0]', 'connect'),
        ])

        # Test hub update
        self.cmd('webpubsub hub update -g {rg} -n {name} --hub-name {hub} --allow-anonymous --event-handler url-template={urlTemplate2} user-event-pattern={userEventPattern2} system-event=disconnect system-event=connected auth-type="ManagedIdentity" auth-resource={authResource}', checks=[
            self.check('name', '{hub}'),
            self.check('properties.anonymousConnectPolicy', 'allow'),
            self.check('properties.eventHandlers[0].urlTemplate', '{urlTemplate2}'),
            self.check('properties.eventHandlers[0].userEventPattern', '{userEventPattern2}'),
            self.check('properties.eventHandlers[0].systemEvents[0]', 'disconnect'),
            self.check('properties.eventHandlers[0].systemEvents[1]', 'connected'),
            self.check('properties.eventHandlers[0].auth.type', 'ManagedIdentity'),
            self.check('properties.eventHandlers[0].auth.managedIdentity.resource', '{authResource}'),
        ])

        # Test event handler hub delete
        self.cmd('webpubsub hub delete  -g {rg} -n {name} --hub-name {hub}')
        count = len(self.cmd('webpubsub hub list -g {rg} -n {name}').get_output_in_json())
        self.assertTrue(count == 0)

        # Delete resource
        self.cmd('webpubsub delete -g {rg} -n {name}')
