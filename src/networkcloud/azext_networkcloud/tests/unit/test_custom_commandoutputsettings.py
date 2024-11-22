# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest.mock import Mock, patch

from azext_networkcloud.operations.common_commandoutputsettings import (
    CommandOutputSettings,
)
from azure.cli.core.azclierror import InvalidArgumentValueError


class TestCommandOutputSettings(unittest.TestCase):
    def setUp(self):
        self.args_schema = Mock()
        self.command_output_settings = CommandOutputSettings()

    @patch("azext_networkcloud.operations.common_commandoutputsettings.has_value")
    def test_pre_operations_command_output_settings_system_assigned_only(
        self, mock_has_value
    ):
        mock_has_value.return_value = True
        args = Mock()
        args.command_output_settings.identity_type = "SystemAssignedIdentity"

        self.command_output_settings.pre_operations_update(args)

        self.assertEqual(
            args.command_output_settings.identity_type, "SystemAssignedIdentity"
        )
        self.assertIsNone(args.command_output_settings.identity_resource_id)

    @patch("azext_networkcloud.operations.common_commandoutputsettings.has_value")
    def test_pre_operations_command_output_settings_user_assigned_only(
        self, mock_has_value
    ):
        mock_has_value.return_value = True
        args = Mock()
        args.command_output_settings.identity_type = "UserAssignedIdentity"

        # Mock the identity
        mock_identity1 = Mock(return_value="id1")

        args.command_output_settings.identity_resource_id = mock_identity1

        self.command_output_settings.pre_operations_update(args)

        self.assertEqual(
            args.command_output_settings.identity_type, "UserAssignedIdentity"
        )
        self.assertEqual(args.command_output_settings.identity_resource_id(), "id1")

    @patch("azext_networkcloud.operations.common_commandoutputsettings.has_value")
    def test_pre_operations_command_output_settings_both_assigned(self, mock_has_value):
        mock_has_value.return_value = True
        args = Mock()
        args.command_output_settings.identity_type = "SystemAssignedIdentity"

        # Mock the identity
        mock_identity1 = Mock(return_value="id1")

        args.command_output_settings.identity_resource_id = mock_identity1

        self.command_output_settings.pre_operations_update(args)

        self.assertEqual(
            args.command_output_settings.identity_type, "SystemAssignedIdentity"
        )
        self.assertIsNone(args.command_output_settings.identity_resource_id)

    @patch("azext_networkcloud.operations.common_commandoutputsettings.has_value")
    def test_pre_operations_command_output_settings_user_no_id(self, mock_has_value):
        mock_has_value.return_value = (
            False  # UserAssigned identity resource ID is not passed
        )
        args = Mock()
        args.command_output_settings.identity_type = "UserAssignedIdentity"
        args.command_output_settings.identity_resource_id = None

        with self.assertRaises(InvalidArgumentValueError):
            self.command_output_settings.pre_operations_update(args)
