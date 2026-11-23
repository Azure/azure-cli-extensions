# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
from unittest.mock import patch

from azext_managedcleanroom.custom import CollaborationCreate, CollaborationUpdate


class _Client:

    @staticmethod
    def format_url(url, **parameters):
        return url.format(**parameters)


class TestCollaborationCommands(unittest.TestCase):

    _PARAMETERS = {
        "subscriptionId": "subscription",
        "resourceGroupName": "resource-group",
        "collaborationName": "collaboration",
    }

    @staticmethod
    def _operation_url(operation_type):
        class TestOperation(operation_type):

            @property
            def client(self):
                return _Client()

            @property
            def url_parameters(self):
                return TestCollaborationCommands._PARAMETERS

        return object.__new__(TestOperation).url

    def test_operations_use_public_namespace_by_default(self):
        with patch.dict(os.environ, {}, clear=True):
            for operation_type in (
                    CollaborationCreate.CollaborationsCreate,
                    CollaborationUpdate.CollaborationsUpdate):
                with self.subTest(operation_type=operation_type):
                    self.assertIn(
                        "/providers/Microsoft.CleanRoom/collaborations/",
                        self._operation_url(operation_type),
                    )

    def test_operations_use_private_namespace_when_configured(self):
        with patch.dict(os.environ, {"UsePrivateCleanRoomNamespace": "true"}, clear=True):
            for operation_type in (
                    CollaborationCreate.CollaborationsCreate,
                    CollaborationUpdate.CollaborationsUpdate):
                with self.subTest(operation_type=operation_type):
                    self.assertIn(
                        "/providers/Private.CleanRoom/collaborations/",
                        self._operation_url(operation_type),
                    )


if __name__ == "__main__":
    unittest.main()
