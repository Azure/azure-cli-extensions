# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import unittest

from .recording_processors import RedisEnterpriseKeyReplacer


class RedisEnterpriseKeyReplacerTest(unittest.TestCase):
    def test_key_scenarios_register_processor(self):
        from . import test_demo
        from .test_test_connection import RedisEnterpriseTestConnectionScenarioTest
        from .test_migration import RedisEnterpriseMigrationScenarioTest

        scenarios = [
            getattr(test_demo, 'Redisenterprisescenario{}Test'.format(number))
            for number in range(1, 8)
        ] + [RedisEnterpriseTestConnectionScenarioTest, RedisEnterpriseMigrationScenarioTest]
        for scenario in scenarios:
            with self.subTest(scenario=scenario.__name__):
                test = scenario('runTest')
                self.assertEqual(
                    sum(isinstance(processor, RedisEnterpriseKeyReplacer)
                        for processor in test.recording_processors),
                    1,
                )

    def test_replaces_key_responses(self):
        processor = RedisEnterpriseKeyReplacer()
        for body in (
                {'primaryKey': 'synthetic-primary', 'secondaryKey': 'synthetic-secondary'},
                {'primaryKey': 'synthetic-primary', 'other': 'preserved'}):
            with self.subTest(body=body):
                response = {
                    'headers': {'content-type': ['application/json']},
                    'body': {'string': json.dumps(body)},
                }
                self.assertIs(processor.process_response(response), response)
                result = json.loads(response['body']['string'])
                for key, replacement in (
                        ('primaryKey', 'fake_primary_key'), ('secondaryKey', 'fake_secondary_key')):
                    if key in body:
                        self.assertEqual(result[key], replacement)
                if 'other' in body:
                    self.assertEqual(result['other'], body['other'])
                sanitized = response['body']['string']
                processor.process_response(response)
                self.assertEqual(response['body']['string'], sanitized)

    def test_replaces_oss_source_creation_keys(self):
        response = {
            'headers': {'content-type': ['application/json']},
            'body': {'string': json.dumps({
                'properties': {
                    'hostName': 'source.redis.cache.windows.net',
                    'accessKeys': {'primaryKey': 'synthetic-primary', 'secondaryKey': 'synthetic-secondary'},
                },
            })},
        }
        RedisEnterpriseKeyReplacer().process_response(response)
        properties = json.loads(response['body']['string'])['properties']
        self.assertEqual(properties['hostName'], 'source.redis.cache.windows.net')
        self.assertEqual(properties['accessKeys'], {
            'primaryKey': 'fake_primary_key', 'secondaryKey': 'fake_secondary_key',
        })

    def test_preserves_non_key_responses(self):
        processor = RedisEnterpriseKeyReplacer()
        for body, content_type in (
                ('', 'application/json'),
                ('{"name": "cluster"}', 'application/json'),
                ('[{"primaryKey": "not-a-key-response"}]', 'application/json'),
                ('{"primaryKey": null, "secondaryKey": ""}', 'application/json'),
                ('plain text', 'text/plain')):
            with self.subTest(body=body):
                response = {
                    'headers': {'content-type': [content_type]},
                    'body': {'string': body},
                }
                self.assertIs(processor.process_response(response), response)
                self.assertEqual(response['body']['string'], body)

    def test_rejects_malformed_json(self):
        response = {
            'headers': {'content-type': ['application/json']},
            'body': {'string': '{'},
        }
        with self.assertRaises(json.JSONDecodeError):
            RedisEnterpriseKeyReplacer().process_response(response)
