# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import sys
import unittest

# Ensure src/amg (parent directory containing azext_amg) is in sys.path
amg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if amg_path not in sys.path:
    sys.path.insert(0, amg_path)

from azext_amg.custom import _convert_duration_to_seconds


class AmgUnitTest(unittest.TestCase):
    def test_duration_conversion(self):
        self.assertEqual(_convert_duration_to_seconds("1s"), 1)
        self.assertEqual(_convert_duration_to_seconds("1m"), 60)
        self.assertEqual(_convert_duration_to_seconds("1h"), 3600)
        self.assertEqual(_convert_duration_to_seconds("1d"), 86400)
        self.assertEqual(_convert_duration_to_seconds("1w"), 604800)
        self.assertEqual(_convert_duration_to_seconds("1M"), 2592000)
        self.assertEqual(_convert_duration_to_seconds("1y"), 31536000)
        self.assertEqual(_convert_duration_to_seconds("10y"), 315360000)

    def test_create_role_assignment_with_aaz_types(self):
        from unittest.mock import MagicMock, patch
        from azure.cli.core.aaz._field_value import AAZSimpleValue
        from azext_amg.custom import _create_role_assignment

        mock_cli_ctx = MagicMock()
        mock_assignments_client = MagicMock()

        # Simulate AAZSimpleValue types that previously caused JSON serialization errors
        aaz_principal_id = AAZSimpleValue(None, "2b83823d-1afa-419f-8246-4b5d9df2f7e2")
        aaz_role_id = AAZSimpleValue(None, "monitoring-reader-role-id")
        aaz_scope = AAZSimpleValue(None, "/subscriptions/00000000-0000-0000-0000-000000000000")

        with patch('azext_amg.custom.get_mgmt_service_client') as mock_get_client:
            mock_client = MagicMock()
            mock_client.role_assignments = mock_assignments_client
            mock_get_client.return_value = mock_client

            _create_role_assignment(mock_cli_ctx, aaz_principal_id, aaz_role_id, aaz_scope)

            # Verify client.create was called with string parameters
            self.assertTrue(mock_assignments_client.create.called)
            call_kwargs = mock_assignments_client.create.call_args.kwargs
            self.assertIsInstance(call_kwargs['parameters'].principal_id, str)
            self.assertIsInstance(call_kwargs['parameters'].role_definition_id, str)
            self.assertIsInstance(call_kwargs['scope'], str)
            self.assertEqual(call_kwargs['parameters'].principal_id, "2b83823d-1afa-419f-8246-4b5d9df2f7e2")


