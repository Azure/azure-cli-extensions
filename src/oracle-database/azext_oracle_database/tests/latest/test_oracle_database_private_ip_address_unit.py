# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from azure.cli.core.aaz._command_ctx import AAZCommandCtx
from azure.cli.core.mock import DummyCli
from azure.core import PipelineClient
from azure.core.pipeline.policies import ContentDecodePolicy

from azext_oracle_database.aaz.latest.oracle_database.cloud_vm_cluster._list_private_ip_address import (
    ListPrivateIpAddress,
)


class PrivateIpAddressPagingTest(unittest.TestCase):
    SUBSCRIPTION = '00000000-0000-0000-0000-000000000000'
    URL = (
        'https://management.azure.com/subscriptions/' + SUBSCRIPTION +
        '/resourceGroups/test-rg/providers/Oracle.Database/cloudVmClusters/test-cluster/'
        'listPrivateIpAddresses?api-version=2026-07-01-preview'
    )

    @staticmethod
    def _address(ip_address):
        return {
            'displayName': 'test-address',
            'hostnameLabel': 'test-host',
            'ipAddress': ip_address,
            'ocid': 'ocid1.privateip.test',
            'subnetId': 'ocid1.subnet.test',
        }

    def _run_command(self, pages):
        cli_ctx = DummyCli()
        client = PipelineClient(base_url='https://management.azure.com')
        sessions = [
            SimpleNamespace(
                http_response=SimpleNamespace(status_code=200),
                context={ContentDecodePolicy.CONTEXT_NAME: page},
            )
            for page in pages
        ]
        command = ListPrivateIpAddress(cli_ctx=cli_ctx)
        with patch.object(AAZCommandCtx, 'get_http_client', return_value=client), \
                patch.object(client, 'send_request', side_effect=sessions) as send_request:
            output = list(command({
                'subscription': self.SUBSCRIPTION,
                'resource_group': 'test-rg',
                'cloudvmclustername': 'test-cluster',
                'subnet_id': 'ocid1.subnet.test',
                'vnic_id': 'ocid1.vnic.test',
            }))
        return output, [call.kwargs['request'] for call in send_request.call_args_list]

    def test_single_page_returns_address_array(self):
        addresses = [self._address('10.0.1.10'), self._address('10.0.1.11')]
        output, requests = self._run_command([{'value': addresses, 'nextLink': None}])

        self.assertEqual(output, addresses)
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0].method, 'POST')
        self.assertEqual(requests[0].url, self.URL)
        self.assertEqual(json.loads(requests[0].body), {
            'subnetId': 'ocid1.subnet.test', 'vnicId': 'ocid1.vnic.test',
        })

    def test_continuation_link_fetches_and_combines_address_pages(self):
        first = self._address('10.0.1.10')
        second = self._address('10.0.1.11')
        next_link = self.URL + '&$skiptoken=next-page'
        output, requests = self._run_command([
            {'value': [first], 'nextLink': next_link},
            {'value': [second], 'nextLink': None},
        ])

        self.assertEqual(output, [first, second])
        self.assertEqual(len(requests), 2)
        self.assertEqual(requests[0].method, 'POST')
        self.assertEqual(requests[1].method, 'GET')
        self.assertEqual(requests[1].url, next_link)
