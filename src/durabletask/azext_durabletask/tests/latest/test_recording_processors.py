# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import unittest
from types import SimpleNamespace

from .recording_processors import IdentityRecordingProcessor


class IdentityRecordingProcessorTests(unittest.TestCase):
    def test_identity_fields_are_sanitized_without_changing_resource_properties(self):
        body = json.dumps({
            'identity': {'tenantId': 'test-tenant', 'principalId': 'test-principal'},
            'systemData': {'createdBy': 'test-author', 'lastModifiedBy': 'test-editor', 'updatedBy': 'test-editor'},
            'subscription': 'test-subscription',
            'properties': {'keySource': 'MicrosoftManaged', 'autoRotationEnabled': False},
        })
        processor = IdentityRecordingProcessor()
        request = SimpleNamespace(uri='https://management.example.test', body=body.encode('utf-8'))
        processor.process_request(request)
        response = {
            'body': {'string': body},
            'headers': {'Content-Type': ['application/json'], 'x-ms-client-tenant-id': ['test-tenant']},
        }
        processor.process_response(response)
        sanitized = json.loads(response['body']['string'])
        self.assertEqual(json.loads(request.body), sanitized)
        self.assertEqual(sanitized['identity'], {
            'tenantId': '00000000-0000-0000-0000-000000000000',
            'principalId': '00000000-0000-0000-0000-000000000000',
        })
        self.assertEqual(sanitized['systemData']['createdBy'], '00000000-0000-0000-0000-000000000000')
        self.assertEqual(sanitized['systemData']['updatedBy'], '00000000-0000-0000-0000-000000000000')
        self.assertEqual(sanitized['subscription'], '00000000-0000-0000-0000-000000000000')
        self.assertEqual(sanitized['properties'], {'keySource': 'MicrosoftManaged', 'autoRotationEnabled': False})
        self.assertEqual(response['headers'], {'Content-Type': ['application/json']})

    def test_empty_http_bodies_are_preserved(self):
        processor = IdentityRecordingProcessor()
        request = SimpleNamespace(uri='https://management.example.test', body=None)
        self.assertIs(processor.process_request(request), request)
        response = {'body': {'string': ''}, 'headers': {}}
        self.assertIs(processor.process_response(response), response)

    def test_playback_response_bytes_are_supported(self):
        response = {'body': {'string': b'{"principalId":"test-principal"}'}, 'headers': {}}
        IdentityRecordingProcessor().process_response(response)
        self.assertEqual(
            response['body']['string'], b'{"principalId":"00000000-0000-0000-0000-000000000000"}')

    def test_graph_object_ids_are_sanitized_without_changing_arm_ids(self):
        body = json.dumps({
            'id': '11111111-2222-3333-4444-555555555555',
            'resource': {'id': '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/test'},
        })
        sanitized = json.loads(IdentityRecordingProcessor._sanitize(body))
        self.assertEqual(sanitized['id'], '00000000-0000-0000-0000-000000000000')
        self.assertEqual(sanitized['resource']['id'], json.loads(body)['resource']['id'])

    def test_role_assignment_request_paths_are_repeatable(self):
        request = SimpleNamespace(
            uri='https://management.example.test/roleAssignments/11111111-2222-3333-4444-555555555555',
            body=None)
        IdentityRecordingProcessor().process_request(request)
        self.assertEqual(
            request.uri,
            'https://management.example.test/roleAssignments/00000000-0000-0000-0000-000000000000')

    def test_dashboard_links_do_not_reveal_tenant_or_scheduler_host(self):
        body = json.dumps({'dashboardUrl': (
            'https://dashboard.durabletask.io?endpoint=https%3a%2f%2f'
            'temporary-scheduler.northcentralus.durabletask.io'
            '&tenantId=11111111-2222-3333-4444-555555555555'
        )})
        response = {'body': {'string': body}, 'headers': {}}
        IdentityRecordingProcessor().process_response(response)
        self.assertNotIn('temporary-scheduler', response['body']['string'])
        self.assertNotIn('11111111-2222-3333-4444-555555555555', response['body']['string'])

    def test_signed_operation_links_are_sanitized_in_requests_and_response_headers(self):
        uri = 'https://management.example.test/operationStatuses/test?t=time&c=certificate&s=signature&h=hash'
        processor = IdentityRecordingProcessor()
        request = SimpleNamespace(uri=uri, body=None)
        processor.process_request(request)
        response = {'body': {'string': ''}, 'headers': {'azure-asyncoperation': [uri]}}
        processor.process_response(response)
        expected = (
            'https://management.example.test/operationStatuses/test'
            '?t=redacted&c=redacted&s=redacted&h=redacted'
        )
        self.assertEqual(request.uri, expected)
        self.assertEqual(response['headers']['azure-asyncoperation'], [expected])

    def test_key_vault_authentication_challenges_do_not_reveal_tenant(self):
        response = {'body': {'string': ''}, 'headers': {
            'www-authenticate': [
                'Bearer authorization="https://login.windows.net/11111111-2222-3333-4444-555555555555"'
            ],
        }}
        IdentityRecordingProcessor().process_response(response)
        self.assertEqual(response['headers']['www-authenticate'], [
            'Bearer authorization="https://login.windows.net/00000000-0000-0000-0000-000000000000"',
        ])
