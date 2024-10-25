# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest.mock import Mock, patch

from azext_networkcloud.operations.common_managedidentity import ManagedIdentity
from azure.cli.core.aaz import AAZBoolArg, AAZListArg


class TestManagedIdentity(unittest.TestCase):
    def setUp(self):
        self.args_schema = Mock()
        self.managed_identity = ManagedIdentity()

    def test_build_arguments_schema(self):
        self.managed_identity.build_arguments_schema(self.args_schema)

        # Test mi_system_assigned
        self.assertIsInstance(self.args_schema.mi_system_assigned, AAZBoolArg)
        self.assertIsNotNone(self.args_schema.mi_system_assigned)

        # Test mi_user_assigned
        self.assertIsInstance(self.args_schema.mi_user_assigned, AAZListArg)
        self.assertIsNotNone(self.args_schema.mi_user_assigned)

        # validate unregistered parameters
        self.assertFalse(self.args_schema.identity._registered)

    @patch("azext_networkcloud.operations.common_managedidentity.has_value")
    def test_pre_operations_both_assigned(self, mock_has_value):
        mock_has_value.return_value = True
        args = Mock()
        args.mi_system_assigned = True

        # Mock the objects that have a `to_serialized_data` method
        mock_identity1 = Mock()
        mock_identity1.to_serialized_data.return_value = "id1"
        mock_identity2 = Mock()
        mock_identity2.to_serialized_data.return_value = "id2"

        args.mi_user_assigned = [mock_identity1, mock_identity2]
        args.identity = Mock()
        args.identity.type = None

        self.managed_identity.pre_operations_create(args)

        self.assertEqual(args.identity.type, "SystemAssigned,UserAssigned")
        self.assertEqual(
            args.identity.user_assigned_identities,
            {"id1": {}, "id2": {}},
        )

    @patch("azext_networkcloud.operations.common_managedidentity.has_value")
    def test_pre_operations_system_assigned_only(self, mock_has_value):
        mock_has_value.return_value = True
        args = Mock()
        args.mi_system_assigned = True

        # No user-assigned identities
        args.mi_user_assigned = []
        args.identity = Mock()
        args.identity.type = None

        self.managed_identity.pre_operations_create(args)

        self.assertEqual(args.identity.type, "SystemAssigned")

    @patch("azext_networkcloud.operations.common_managedidentity.has_value")
    def test_pre_operations_user_assigned_only(self, mock_has_value):
        mock_has_value.return_value = True
        args = Mock()
        args.mi_system_assigned = False  # No system-assigned identity

        # Mock the objects that have a `to_serialized_data` method
        mock_identity1 = Mock()
        mock_identity1.to_serialized_data.return_value = "id1"
        mock_identity2 = Mock()
        mock_identity2.to_serialized_data.return_value = "id2"

        args.mi_user_assigned = [mock_identity1, mock_identity2]
        args.identity = Mock()
        args.identity.type = None

        self.managed_identity.pre_operations_create(args)

        self.assertEqual(args.identity.type, "UserAssigned")
        self.assertEqual(
            args.identity.user_assigned_identities,
            {"id1": {}, "id2": {}},
        )

    @patch("azext_networkcloud.operations.common_managedidentity.has_value")
    def test_pre_operations_create_nothing_passed(self, mock_has_value):
        mock_has_value.return_value = (
            False  # Neither SystemAssigned nor UserAssigned identities are passed
        )
        args = Mock()
        args.mi_system_assigned = False
        args.mi_user_assigned = []
        args.identity = Mock()
        args.identity.type = None
        args.identity.user_assigned_identities = None

        self.managed_identity.pre_operations_create(args)

        self.assertEqual(
            args.identity.type, "None"
        )  # Expecting None as identity type is passed
        self.assertIsNone(
            args.identity.user_assigned_identities
        )  # Expecting no dictionary as no user-assigned identities are passed

    @patch("azext_networkcloud.operations.common_managedidentity.has_value")
    def test_pre_operations_update_nothing_passed(self, mock_has_value):
        mock_has_value.return_value = (
            False  # Neither SystemAssigned nor UserAssigned identities are passed
        )
        args = Mock()
        args.mi_system_assigned = False
        args.mi_user_assigned = []
        args.identity = None

        self.managed_identity.pre_operations_update(args)

        self.assertIsNone(args.identity)  # Expecting no identity type is passed
