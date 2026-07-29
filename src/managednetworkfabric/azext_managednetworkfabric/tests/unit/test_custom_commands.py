# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from abc import ABC
from unittest.mock import Mock, patch

from azure.core.exceptions import HttpResponseError
from knack.util import CLIError

from azext_managednetworkfabric.operations.error_format import ErrorFormat


class CustomCommandTestClass(ABC):
    """
    This class provides methods that test the _handler and _output
    functions of commands inheriting the ErrorFormat pattern.
    """

    def test_handler_returns_result_on_success(self):
        """Verify _handler returns poller result on success."""
        mock_poller = Mock()
        mock_poller.result.return_value = {"status": "Succeeded"}

        self.cmd.ctx = Mock()
        self.cmd.ctx.args.no_wait = False

        with patch.object(self.base_class, "_handler", return_value=mock_poller):
            result = self.cmd._handler(Mock())

        self.assertEqual(result, {"status": "Succeeded"})

    def test_handler_returns_none_when_poller_is_none(self):
        """Verify _handler returns None when parent returns None."""
        with patch.object(self.base_class, "_handler", return_value=None):
            result = self.cmd._handler(Mock())

        self.assertIsNone(result)

    def test_handler_raises_cli_error_on_http_error(self):
        """Verify _handler catches HttpResponseError and raises CLIError."""
        error_obj = Mock()
        error_obj.code = "OperationFailed"
        error_obj.message = "Something went wrong."
        error_obj.target = None
        error_obj.details = None

        http_error = HttpResponseError(message="Something went wrong.")
        http_error.error = error_obj

        mock_poller = Mock()
        mock_poller.result.side_effect = http_error

        self.cmd.ctx = Mock()
        self.cmd.ctx.args.no_wait = False

        with patch.object(self.base_class, "_handler", return_value=mock_poller):
            with self.assertRaises(CLIError) as ctx:
                self.cmd._handler(Mock())

        self.assertIn("OperationFailed", str(ctx.exception))
        self.assertIn("Something went wrong.", str(ctx.exception))

    def test_handler_raises_cli_error_with_details(self):
        """Verify _handler formats multiple error details with blank line separators."""
        detail1 = Mock()
        detail1.code = "CouldNotConnect"
        detail1.message = "Device CE1 unreachable."
        detail1.target = "CE1"

        detail2 = Mock()
        detail2.code = "CouldNotConnect"
        detail2.message = "Device CE2 unreachable."
        detail2.target = "CE2"

        error_obj = Mock()
        error_obj.code = "OperationFailed"
        error_obj.message = "One or more devices failed."
        error_obj.target = None
        error_obj.details = [detail1, detail2]

        http_error = HttpResponseError(message="One or more devices failed.")
        http_error.error = error_obj

        mock_poller = Mock()
        mock_poller.result.side_effect = http_error

        self.cmd.ctx = Mock()
        self.cmd.ctx.args.no_wait = False

        with patch.object(self.base_class, "_handler", return_value=mock_poller):
            with self.assertRaises(CLIError) as ctx:
                self.cmd._handler(Mock())

        error_msg = str(ctx.exception)
        self.assertIn("Target: CE1", error_msg)
        self.assertIn("Target: CE2", error_msg)

        # Verify blank line between detail blocks
        lines = error_msg.split("\n")
        ce1_target_idx = next(
            i for i, line in enumerate(lines) if "Target: CE1" in line
        )
        self.assertEqual(
            lines[ce1_target_idx + 1],
            "",
            "Expected blank line between detail blocks",
        )

    def test_handler_returns_poller_on_no_wait(self):
        """Verify _handler returns the poller directly when --no-wait is set."""
        mock_poller = Mock()

        self.cmd.ctx = Mock()
        self.cmd.ctx.args.no_wait = True

        with patch.object(self.base_class, "_handler", return_value=mock_poller):
            result = self.cmd._handler(Mock())

        self.assertIs(result, mock_poller)
        mock_poller.result.assert_not_called()

    def test_output_delegates_to_error_format(self):
        """Verify _output calls ErrorFormat._output with self as parent_cmd."""
        with patch.object(
            ErrorFormat, "_output", return_value={"status": "Succeeded"}
        ) as mock_output:
            result = self.cmd._output()

        mock_output.assert_called_once_with(self.cmd)
        self.assertEqual(result, {"status": "Succeeded"})

    def test_output_strips_nested_details(self):
        """Verify _output removes nested details from error response."""
        mock_result = {
            "error": {
                "code": "OperationFailed",
                "message": "Failed.",
                "details": [
                    {
                        "code": "CouldNotConnect",
                        "message": "Device unreachable.",
                        "details": [
                            {"code": "Nested", "message": "Should be removed."}
                        ],
                    }
                ],
            }
        }
        self.cmd.deserialize_output = Mock(return_value=mock_result)
        self.cmd.ctx = Mock()
        self.cmd.ctx.vars.instance = Mock()

        result = self.cmd._output()

        for detail in result["error"]["details"]:
            self.assertNotIn("details", detail)


class TestFabricRotateCertificateCommand(CustomCommandTestClass, unittest.TestCase):
    """Tests for fabric rotate-certificate custom command."""

    def setUp(self):
        from azext_managednetworkfabric.aaz.latest.networkfabric.fabric import (
            RotateCertificate as _RotateCertificateCommand,
        )
        from azext_managednetworkfabric.custom.fabric_rotate_certificate import (
            RotateCertificateCommand,
        )

        self.base_class = _RotateCertificateCommand
        self.cmd = RotateCertificateCommand.__new__(RotateCertificateCommand)


class TestDeviceResyncPasswordCommand(CustomCommandTestClass, unittest.TestCase):
    """Tests for device resync-password custom command."""

    def setUp(self):
        from azext_managednetworkfabric.aaz.latest.networkfabric.device import (
            ResyncPassword as _ResyncPasswordCommand,
        )
        from azext_managednetworkfabric.custom.device_resync_password import (
            ResyncPasswordCommand,
        )

        self.base_class = _ResyncPasswordCommand
        self.cmd = ResyncPasswordCommand.__new__(ResyncPasswordCommand)


class TestFabricResyncPasswordCommand(CustomCommandTestClass, unittest.TestCase):
    """Tests for fabric resync-password custom command."""

    def setUp(self):
        from azext_managednetworkfabric.aaz.latest.networkfabric.fabric import (
            ResyncPassword as _ResyncPasswordCommand,
        )
        from azext_managednetworkfabric.custom.fabric_resync_password import (
            ResyncPasswordCommand,
        )

        self.base_class = _ResyncPasswordCommand
        self.cmd = ResyncPasswordCommand.__new__(ResyncPasswordCommand)


if __name__ == "__main__":
    unittest.main()
