# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest import mock
import json

from ...cssc import (
    create_acrcssc,
    _validate_task_type
    # update_acrcssc,
    # list_acrcssc,
    # delete_acrcssc
)

from azure.cli.command_modules.acr._docker_utils import (
    EMPTY_GUID,
    get_authorization_header,
)

from azure.cli.core.mock import DummyCli


class AcrCsscCommandsTests(unittest.TestCase):

    def test_create_acrcssc(self, ):
        cmd = self._setup_cmd()

        # Basic auth
        #mock_get_access_credentials.return_value = 'testregistry.azurecr.io', 'username', 'password'
        validation_result = _validate_task_type("dummny")
        self.assertFalse(validation_result)
        # create_acrcssc(cmd, 'testregistry', 'get')
        # mock_requests_get.assert_called_with(
        #     method='post',
        #     url='https://testregistry.azurecr.io/acr/v1/_metadata/_query',
        #     headers=get_authorization_header('username', 'password'),
        #     params=None,
        #     json={
        #         'query': 'get'
        #     },
        #     timeout=300,
        #     verify=mock.ANY)

    def _setup_cmd(self):
        cmd = mock.MagicMock()
        cmd.cli_ctx = DummyCli()
        mock_sku = mock.MagicMock()
        mock_sku.classic.value = 'Classic'
        mock_sku.basic.value = 'Basic'
        #cmd.get_models.return_value = mock_sku
        return cmd