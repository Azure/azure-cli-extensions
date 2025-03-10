# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest.mock import Mock, patch

from azext_networkcloud.operations.common_commandoutputsettings import (
    CommandOutputSettings,
)
from azure.cli.core.azclierror import (
    InvalidArgumentValueError,
    RequiredArgumentMissingError,
)


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
        args.command_output_settings.container_url = (
            "https://myaccount.blob.core.windows.net/mycontainer?restype=container"
        )

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
        args.command_output_settings.container_url = (
            "https://myaccount.blob.core.windows.net/mycontainer?restype=container"
        )

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
        args.command_output_settings.container_url = (
            "https://myaccount.blob.core.windows.net/mycontainer?restype=container"
        )

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
        mock_has_value.side_effect = (
            True,  # CommandOutputSettings does exist
            True,  # ContainerURL is passed. has a value, and is checked first
            False,  # UserAssigned identity resource ID is not passed, and is checked second
        )
        args = Mock()
        args.command_output_settings.identity_type = "UserAssignedIdentity"
        args.command_output_settings.identity_resource_id = None
        args.command_output_settings.container_url = "the url to container"

        with self.assertRaises(InvalidArgumentValueError):
            self.command_output_settings.pre_operations_update(args)

    @patch("azext_networkcloud.operations.common_commandoutputsettings.has_value")
    def test_pre_operations_command_output_settings_no_container_url(
        self, mock_has_value
    ):
        mock_has_value.side_effect = (
            True,  # CommandOutputSettings does exist
            False,  # ContainerURL is not passed
        )
        args = Mock()
        args.command_output_settings.container_url = None

        with self.assertRaises(RequiredArgumentMissingError):
            self.command_output_settings.pre_operations_update(args)
