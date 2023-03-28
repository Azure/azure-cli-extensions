# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from .custom_preparers import SpringSingleValueReplacer
try:
    import unittest.mock as mock
except ImportError:
    from unittest import mock


class TestStringReplacer(unittest.TestCase):
    def _mock_request(self, uri, body=None):
        request = mock.MagicMock()
        request.uri = uri
        request.method = 'POST'
        request.headers = {'Content-Type': 'application/json'}
        request.body = body
        return request

    def test_process_request(self):
        for parameter, expected in {
            '/resourceGroups/cli/Spring/cli': '/resourceGroups/moniker/Spring/moniker',
            '/resourceGroups/cli/Spring/cli-unittest?api-version=2022-11-01': '/resourceGroups/moniker/Spring/cli-unittest?api-version=2022-11-01',
            '/resourceGroups/cli-unittest/Spring/cli?api-version=2022-11-01': '/resourceGroups/cli-unittest/Spring/moniker?api-version=2022-11-01',
            '/resourceGroups/cli-unittest/Spring/cli': '/resourceGroups/cli-unittest/Spring/moniker',
            '{"resourceGroup": "cli", "id": "/resourceGroups/cli/Spring/cli-unittest", "name": "cli-unittest"}': '{"resourceGroup": "moniker", "id": "/resourceGroups/moniker/Spring/cli-unittest", "name": "cli-unittest"}',
            '"fqdn":"cli.azuremicroservices.io"': '"fqdn":"moniker.azuremicroservices.io"',
            'X1jIN@cli.test.azuremicroservices.io': 'X1jIN@moniker.test.azuremicroservices.io'
        }.items():
            processor = SpringSingleValueReplacer('cli', 'moniker')
            request = processor.process_request(self._mock_request(parameter))
            self.assertEqual(expected, request.uri)
