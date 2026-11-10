# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

from requests import Response
from urllib3.response import HTTPResponse

from azure.cli.core.mock import DummyCli
from azure.cli.core.util import rmtree_with_retry
from azure.cli.testsdk.base import execute
from azure.cli.testsdk.patches import (
    patch_load_cached_subscriptions,
    patch_main_exception_handler,
    patch_retrieve_token_for_user,
)
from azure.cli.testsdk.scenario_tests.const import MOCKED_SUBSCRIPTION_ID
from vcr.request import Request

from azext_planetarycomputer.tests.latest.test_planetarycomputer import _CatalogRecordingProcessor


def _response(status, body):
    response = Response()
    response.status_code = status
    response.headers['Content-Type'] = 'application/json'
    response._content = json.dumps(body).encode('utf-8')  # pylint: disable=protected-access
    response.raw = HTTPResponse(body=response.content, status=status)
    return response


class PlanetarycomputerStableApiSmoke(unittest.TestCase):

    def setUp(self):
        self.cli_ctx = DummyCli(random_config_dir=True)
        self.addCleanup(self.cli_ctx.env_patch.stop)
        self.addCleanup(rmtree_with_retry, self.cli_ctx.config.config_dir)
        self.cli_ctx.config.set_value('core', 'collect_telemetry', 'false')
        self.cli_ctx.config.set_value('extension', 'use_dynamic_install', 'no')
        patch_load_cached_subscriptions(self)
        patch_retrieve_token_for_user(self)
        patch_main_exception_handler(self)

    def test_stable_api_smoke(self):
        """Catches fail-open unsupported CLI options and lifecycle fields absent from live Basic responses."""
        path = '/subscriptions/{}/resourceGroups/test-rg/providers/Microsoft.Orbital/geoCatalogs/test-catalog'.format(
            MOCKED_SUBSCRIPTION_ID)
        catalog = {
            'id': path,
            'name': 'test-catalog',
            'type': 'Microsoft.Orbital/geoCatalogs',
            'location': 'eastus',
            'properties': {'tier': 'Basic', 'provisioningState': 'Succeeded', 'state': 'Running'},
        }
        stopped = dict(catalog, properties=dict(
            catalog['properties'], state='Stopped', stoppedSinceUtc='2026-10-01T00:00:00Z'))
        create = (
            'planetarycomputer geocatalog create -g test-rg -n test-catalog -l eastus '
            '--tier Basic --scope NoReuse --public-network-access Disabled '
            '--user-assigned /subscriptions/{}/resourceGroups/test-rg/providers/'
            'Microsoft.ManagedIdentity/userAssignedIdentities/test-identity'
        ).format(MOCKED_SUBSCRIPTION_ID)
        unsupported_options = (
            '--premium-configuration managed-storage-capacity=5',
            '--system-assigned',
            '--mi-system-assigned',
        )

        with patch('requests.sessions.Session.send', autospec=True, side_effect=[
            _response(201, catalog), _response(200, stopped), _response(200, {'value': []}),
        ]) as send:
            execute(self.cli_ctx, create)
            shown = execute(
                self.cli_ctx, 'planetarycomputer geocatalog show -g test-rg -n test-catalog'
            ).get_output_in_json()
            links = execute(
                self.cli_ctx,
                'planetarycomputer geocatalog private-link-resource list -g test-rg --catalog-name test-catalog',
            ).get_output_in_json()
            for option in unsupported_options:
                with self.assertRaises(SystemExit) as failure:
                    execute(self.cli_ctx, create + ' ' + option)
                self.assertEqual(failure.exception.code, 2)
            for action in ('assign', 'remove'):
                for option in ('--system-assigned', '--mi-system-assigned'):
                    with self.assertRaises(SystemExit) as failure:
                        execute(
                            self.cli_ctx,
                            'planetarycomputer geocatalog identity {} -g test-rg -n test-catalog {}'.format(
                                action, option),
                        )
                    self.assertEqual(failure.exception.code, 2)

        self.assertEqual(send.call_count, 3, 'Unsupported options must fail before sending an HTTP request')
        for call, method, expected_path in zip(send.call_args_list, ['PUT', 'GET', 'GET'], [
            path, path, path + '/privateLinkResources',
        ]):
            request = call.args[1]
            url = urlparse(request.url)
            self.assertEqual(request.method, method)
            self.assertEqual((url.scheme, url.netloc, url.path), ('https', 'management.azure.com', expected_path))
            self.assertEqual(parse_qs(url.query), {'api-version': ['2026-10-01']})

        body = json.loads(send.call_args_list[0].args[1].body)
        self.assertEqual(body['identity']['type'], 'UserAssigned')
        self.assertEqual(len(body['identity']['userAssignedIdentities']), 1)
        self.assertEqual(body['properties']['tier'], 'Basic')
        self.assertNotIn('premiumConfiguration', body['properties'])
        self.assertEqual(body['properties']['autoGeneratedDomainNameLabelScope'], 'NoReuse')
        self.assertEqual(body['properties']['publicNetworkAccess'], 'Disabled')
        self.assertEqual(shown['properties']['state'], 'Stopped')
        self.assertEqual(shown['properties']['stoppedSinceUtc'], '2026-10-01T00:00:00Z')
        self.assertEqual(links, [])

    def test_recording_privacy(self):
        """Catches fail-open recording leaks that successful live requests cannot detect."""
        fixture_id = '/subscriptions/test-sub/resourceGroups/test-rg/providers/Microsoft.Orbital/geoCatalogs/fixture'
        processor = _CatalogRecordingProcessor(lambda: fixture_id)
        url = (
            'https://eastus2euap.management.azure.com/operations/operation-id'
            '?api-version=2026-10-01&t=deadline&c=certificate%2Bdata&s=signature&h=hash&other=keep'
        )
        expected = (
            'https://eastus2euap.management.azure.com/operations/operation-id'
            '?api-version=2026-10-01&t=sanitized&c=sanitized&s=sanitized&h=sanitized&other=keep'
        )
        self.assertEqual(processor.process_request(Request('GET', url, None, {})).uri, expected)
        request = processor.process_request(Request(
            'PUT', url, b'{"tags": {"owner": "owner@contoso.com"}, "properties": {"tier": "Basic"}}',
            {'Content-Type': 'application/json'},
        ))
        self.assertEqual(json.loads(request.body), {
            'tags': {'owner': 'user@example.com'}, 'properties': {'tier': 'Basic'},
        })
        body = {'value': [
            {'id': fixture_id.upper(), 'name': 'fixture',
             'systemData': {'createdBy': 'owner@contoso.com', 'lastModifiedBy': 'object-id'},
             'identity': {'principalId': 'principal-id', 'tenantId': 'tenant-id'},
             'properties': {
                 'catalogUri': 'https://fixture.real-domain.eastus2euap.geocatalog.spatio.azure.com',
                 'managedStorageResourceIds': [
                     '/resourceGroups/real-managed-group/providers/Microsoft.Storage/storageAccounts/realstorage',
                 ],
                 'managedResourceGroupId': '/resourceGroups/another-managed-group',
             }},
            {'name': 'unrelated-customer-catalog'},
            {'id': fixture_id.replace('test-rg', 'customer-rg'), 'name': 'fixture'},
            {'id': fixture_id.replace('test-sub', 'customer-sub'), 'name': 'fixture'},
        ], 'nextLink': url}
        response = processor.process_response({
            'headers': {'Azure-AsyncOperation': [url], 'Location': [url]},
            'body': {'string': json.dumps(body)},
        })
        self.assertEqual(response['headers'], {'Azure-AsyncOperation': [expected], 'Location': [expected]})
        data = json.loads(response['body']['string'])
        self.assertEqual(data['nextLink'], expected)
        self.assertEqual([item['name'] for item in data['value']], ['fixture'])
        serialized = response['body']['string']
        for secret in ('owner@contoso.com', 'object-id', 'principal-id', 'tenant-id',
                       'real-domain', 'real-managed-group', 'realstorage', 'unrelated-customer-catalog',
                       'another-managed-group', 'customer-rg', 'customer-sub'):
            self.assertNotIn(secret, serialized)
        self.assertEqual(processor.redact_operation_url(expected), expected)
        self.assertEqual(processor.scrub_metadata({'principalId': None, 'tenantId': ''}),
                         {'principalId': None, 'tenantId': ''})
        self.assertEqual(processor.process_response({
            'headers': {}, 'body': {'string': '{"value": []}'},
        })['body']['string'], '{"value": []}')
