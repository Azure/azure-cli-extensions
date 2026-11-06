# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from types import SimpleNamespace
import unittest
from unittest.mock import Mock, call, patch

from knack.util import CLIError
from azext_networksecurity.custom import list_operations


class OperationListTest(unittest.TestCase):

    def setUp(self):
        endpoint = SimpleNamespace(resource_manager='https://management.usgovcloudapi.net/')
        self.cli_ctx = SimpleNamespace(cloud=SimpleNamespace(endpoints=endpoint))
        self.cmd = SimpleNamespace(cli_ctx=self.cli_ctx)
        self.url = (
            'https://management.usgovcloudapi.net/providers/Microsoft.NetworkSecurity/'
            'operations?api-version=2026-10-01-preview'
        )

    @patch('azext_networksecurity.custom.send_raw_request')
    def test_lists_all_pages_using_active_cloud_endpoint(self, send):
        next_link = self.url + '&$skiptoken=next'
        response = Mock()
        response.json.side_effect = [
            {'value': [{'name': 'first/read'}], 'nextLink': next_link},
            {'value': [{'name': 'second/read'}]}
        ]
        send.return_value = response

        self.assertEqual(
            list_operations(self.cmd),
            [{'name': 'first/read'}, {'name': 'second/read'}]
        )
        self.assertEqual(send.call_args_list, [
            call(self.cli_ctx, 'GET', self.url),
            call(self.cli_ctx, 'GET', next_link)
        ])

    @patch('azext_networksecurity.custom.send_raw_request')
    def test_empty_catalog(self, send):
        send.return_value.json.return_value = {'value': []}

        self.assertEqual(list_operations(self.cmd), [])
        send.assert_called_once_with(self.cli_ctx, 'GET', self.url)

    @patch('azext_networksecurity.custom.send_raw_request')
    def test_surfaces_request_failure(self, send):
        send.side_effect = CLIError('Authorization denied')

        with self.assertRaisesRegex(CLIError, 'Authorization denied'):
            list_operations(self.cmd)
