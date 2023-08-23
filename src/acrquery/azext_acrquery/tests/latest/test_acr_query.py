# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest import mock
import json

from azext_acrquery.query import (
    create_query
)

from azure.cli.command_modules.acr._docker_utils import (
    EMPTY_GUID,
    get_authorization_header,
)

from azure.cli.core.mock import DummyCli


class AcrQueryCommandsTests(unittest.TestCase):

    @mock.patch('azext_acrquery.query.get_access_credentials', autospec=True)
    @mock.patch('requests.request', autospec=True)
    def test_acrquery(self, mock_requests_get, mock_get_access_credentials):
        cmd = self._setup_cmd()

        response = mock.MagicMock()
        response.headers = {}
        response.status_code = 200
        response.content = json.dumps({'repositories': ['testrepo1', 'testrepo2']}).encode()
        mock_requests_get.return_value = response

        # Basic auth
        mock_get_access_credentials.return_value = 'testregistry.azurecr.io', 'username', 'password'
        create_query(cmd, 'testregistry', 'get')
        mock_requests_get.assert_called_with(
            method='post',
            url='https://testregistry.azurecr.io/acr/v1/_metadata/_query',
            headers=get_authorization_header('username', 'password'),
            params=None,
            json={
                'query': 'get'
            },
            timeout=300,
            verify=mock.ANY)

        # Bearer auth
        mock_get_access_credentials.return_value = 'testregistry.azurecr.io', EMPTY_GUID, 'password'
        create_query(cmd, 'testregistry', 'get')
        mock_requests_get.assert_called_with(
            method='post',
            url='https://testregistry.azurecr.io/acr/v1/_metadata/_query',
            headers=get_authorization_header(EMPTY_GUID, 'password'),
            params=None,
            json={
                'query': 'get'
            },
            timeout=300,
            verify=mock.ANY)

        # Filter by repository
        mock_get_access_credentials.return_value = 'testregistry.azurecr.io', EMPTY_GUID, 'password'
        create_query(cmd, 'testregistry', 'get', repository='repository')
        mock_requests_get.assert_called_with(
            method='post',
            url='https://testregistry.azurecr.io/acr/v1/repository/_metadata/_query',
            headers=get_authorization_header(EMPTY_GUID, 'password'),
            params=None,
            json={
                'query': 'get'
            },
            timeout=300,
            verify=mock.ANY)

        # Request with skip token
        mock_get_access_credentials.return_value = 'testregistry.azurecr.io', EMPTY_GUID, 'password'
        create_query(cmd, 'testregistry', 'get', repository='repository', skip_token='12345678')
        mock_requests_get.assert_called_with(
            method='post',
            url='https://testregistry.azurecr.io/acr/v1/repository/_metadata/_query',
            headers=get_authorization_header(EMPTY_GUID, 'password'),
            params=None,
            json={
                'query': 'get',
                'options': {
                    '$skipToken': '12345678'
                }
            },
            timeout=300,
            verify=mock.ANY)

    def _setup_cmd(self):
        cmd = mock.MagicMock()
        cmd.cli_ctx = DummyCli()
        mock_sku = mock.MagicMock()
        mock_sku.classic.value = 'Classic'
        mock_sku.basic.value = 'Basic'
        cmd.get_models.return_value = mock_sku
        return cmd