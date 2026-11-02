# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk.scenario_tests.const import MOCKED_SUBSCRIPTION_ID


class PlanetarycomputerPrivateLinkScenario(ScenarioTest):

    def setUp(self):
        if self.in_recording and not self.is_live:
            raise RuntimeError('Use AZURE_TEST_RUN_LIVE=true to record the private-link scenario explicitly.')
        self.vcr.match_on = (*self.vcr.match_on, 'body')
        super().setUp()
        endpoint = patch.object(
            self.cli_ctx.cloud.endpoints, 'resource_manager', 'https://eastus2euap.management.azure.com/')
        endpoint.start()
        self.addCleanup(endpoint.stop)
        if self.in_recording:
            catalog_id = os.environ['PLANETARYCOMPUTER_TEST_CATALOG_ID']
            subnet_id = os.environ['PLANETARYCOMPUTER_TEST_SUBNET_ID']
        else:
            catalog_id = (
                '/subscriptions/{}/resourceGroups/canary-test/providers/Microsoft.Orbital/geoCatalogs/broken'
            ).format(MOCKED_SUBSCRIPTION_ID)
            subnet_id = (
                '/subscriptions/{}/resourceGroups/internal-testing/providers/Microsoft.Network/'
                'virtualNetworks/vnet-devasingh-dns-final-e2euap/subnets/snet-private-endpoint'
            ).format(MOCKED_SUBSCRIPTION_ID)
        catalog_parts = catalog_id.split('/')
        subnet_parts = subnet_id.split('/')
        self.kwargs.update({
            'catalog_id': catalog_id,
            'catalog_subscription': catalog_parts[2],
            'catalog_rg': catalog_parts[4],
            'catalog': catalog_parts[-1],
            'network_subscription': subnet_parts[2],
            'network_rg': subnet_parts[4],
            'subnet_id': subnet_id,
            'endpoint': self.create_random_name('cli-private-link-', 30),
        })

    def test_geocatalog_private_link_lifecycle(self):
        """Covers missing private-link scenarios, matching request bodies as well as recorded URLs."""
        catalog_args = '--subscription {catalog_subscription} -g {catalog_rg} --catalog-name {catalog}'
        connection = 'planetarycomputer geocatalog private-endpoint-connection '
        catalog = self.cmd(
            'planetarycomputer geocatalog show --subscription {catalog_subscription} '
            '-g {catalog_rg} -n {catalog}'
        ).get_output_in_json()
        self.assertEqual(catalog['properties']['provisioningState'], 'Succeeded')
        self.assertEqual(catalog['location'].replace(' ', '').lower(), 'eastus2euap')
        links = self.cmd(
            'planetarycomputer geocatalog private-link-resource list ' + catalog_args
        ).get_output_in_json()
        link = next(item for item in links if item['groupId'] == 'geocatalog')
        self.assertIn('api', link['requiredMembers'])
        self.assertIn('privatelink.geocatalog.spatio.azure.com', link['requiredZoneNames'])

        self.addCleanup(
            self.cmd,
            'network private-endpoint delete --subscription {network_subscription} '
            '-g {network_rg} -n {endpoint}',
        )
        endpoint = self.cmd(
            'network private-endpoint create --subscription {network_subscription} '
            '-g {network_rg} -n {endpoint} -l eastus2euap --subnet {subnet_id} '
            '--private-connection-resource-id {catalog_id} --group-id geocatalog '
            '--connection-name {endpoint} --manual-request true --request-message cli-private-link-test'
        ).get_output_in_json()
        connections = self.cmd(connection + 'list ' + catalog_args).get_output_in_json()
        matches = [
            item for item in connections
            if item['privateEndpoint']['id'].lower() == endpoint['id'].lower()
        ]
        self.assertEqual(len(matches), 1)
        self.kwargs['connection'] = matches[0]['name']
        self.assertEqual(matches[0]['privateLinkServiceConnectionState']['status'], 'Pending')

        connection_args = catalog_args + ' -n {connection}'
        approved = self.cmd(
            connection + 'create ' + connection_args +
            ' --private-link-service-connection-state status=Approved description=cli-approved actions-required=None'
        ).get_output_in_json()
        self.assertEqual(approved['privateLinkServiceConnectionState']['status'], 'Approved')
        shown = self.cmd(connection + 'show ' + connection_args).get_output_in_json()
        self.assertEqual(shown['privateLinkServiceConnectionState']['status'], 'Approved')
        self.assertEqual(shown['privateEndpoint']['id'].lower(), endpoint['id'].lower())
        updated = self.cmd(
            connection + 'update ' + connection_args +
            ' --private-link-service-connection-state description=cli-updated'
        ).get_output_in_json()
        self.assertEqual(updated['privateLinkServiceConnectionState']['status'], 'Approved')
        self.assertEqual(updated['privateLinkServiceConnectionState']['description'], 'cli-updated')
        self.cmd(connection + 'wait ' + connection_args + ' --created --interval 5 --timeout 120')
        self.cmd(connection + 'delete ' + connection_args + ' --yes')
        self.cmd(connection + 'wait ' + connection_args + ' --deleted --interval 5 --timeout 120')
        remaining = self.cmd(connection + 'list ' + catalog_args).get_output_in_json()
        self.assertFalse(any(item['name'] == self.kwargs['connection'] for item in remaining))

        requests = [
            request for request in self.cassette.requests
            if '/providers/microsoft.orbital/geocatalogs/' in request.uri.lower()
        ]
        self.assertTrue(requests)
        for request in requests:
            self.assertEqual(parse_qs(urlparse(request.uri).query)['api-version'], ['2026-10-01'])
