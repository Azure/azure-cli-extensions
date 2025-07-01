# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest.mock import Mock, patch

from azext_networkcloud.operations.common_analyticsoutputsettings import (
    AnalyticsOutputSettings,
)
from azure.cli.core.azclierror import (
    InvalidArgumentValueError,
    RequiredArgumentMissingError,
)


class TestAnalyticsOutputSettings(unittest.TestCase):
    def setUp(self):
        self.args_schema = Mock()
        self.analytics_output_settings = AnalyticsOutputSettings()

    @patch("azext_networkcloud.operations.common_analyticsoutputsettings.has_value")
    def test_pre_operations_analytics_output_settings_system_assigned_only(
        self, mock_has_value
    ):
        mock_has_value.return_value = True
        args = Mock()
        args.analytics_output_settings.identity_type = "SystemAssignedIdentity"

        self.analytics_output_settings.pre_operations_update(args)

        self.assertEqual(
            args.analytics_output_settings.identity_type, "SystemAssignedIdentity"
        )
        self.assertIsNone(args.analytics_output_settings.identity_resource_id)

    @patch("azext_networkcloud.operations.common_analyticsoutputsettings.has_value")
    def test_pre_operations_analytics_output_settings_user_assigned_only(
        self, mock_has_value
    ):
        mock_has_value.return_value = True
        args = Mock()
        args.analytics_output_settings.identity_type = "UserAssignedIdentity"

        # Mock the identity
        mock_identity1 = Mock(return_value="id1")

        args.analytics_output_settings.identity_resource_id = mock_identity1

        self.analytics_output_settings.pre_operations_update(args)

        self.assertEqual(
            args.analytics_output_settings.identity_type, "UserAssignedIdentity"
        )
        self.assertEqual(args.analytics_output_settings.identity_resource_id(), "id1")

    @patch("azext_networkcloud.operations.common_analyticsoutputsettings.has_value")
    def test_pre_operations_analytics_output_settings_both_assigned(
        self, mock_has_value
    ):
        mock_has_value.return_value = True
        args = Mock()
        args.analytics_output_settings.identity_type = "SystemAssignedIdentity"

        # Mock the identity
        mock_identity1 = Mock(return_value="id1")

        args.analytics_output_settings.identity_resource_id = mock_identity1

        self.analytics_output_settings.pre_operations_update(args)

        self.assertEqual(
            args.analytics_output_settings.identity_type, "SystemAssignedIdentity"
        )
        self.assertIsNone(args.analytics_output_settings.identity_resource_id)

    @patch("azext_networkcloud.operations.common_analyticsoutputsettings.has_value")
    def test_pre_operations_analytics_output_settings_user_no_id(self, mock_has_value):
        def has_value_side_effect(arg):
            if arg is None:
                return False
            return True

        # Set the side effect for the mock
        mock_has_value.side_effect = has_value_side_effect

        args = Mock()
        args.analytics_output_settings.identity_type = "UserAssignedIdentity"
        args.analytics_output_settings.identity_resource_id = None

        with self.assertRaises(InvalidArgumentValueError):
            self.analytics_output_settings.pre_operations_update(args)

    @patch("azext_networkcloud.operations.common_analyticsoutputsettings.has_value")
    def test_pre_operations_analytics_output_settings_no_workspace_id(
        self, mock_has_value
    ):
        def has_value_side_effect(arg):
            if arg is None:
                return False
            return True

        # Set the side effect for the mock
        mock_has_value.side_effect = has_value_side_effect

        args = Mock()
        args.analytics_output_settings.analytics_workspace_id = None

        with self.assertRaises(RequiredArgumentMissingError):
            self.analytics_output_settings.pre_operations_update(args)
