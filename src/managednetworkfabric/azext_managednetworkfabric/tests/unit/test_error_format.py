# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest.mock import Mock

from knack.util import CLIError

from azext_managednetworkfabric.operations.error_format import ErrorFormat


class TestErrorFormatOutput(unittest.TestCase):
    """Tests for ErrorFormat._output() which strips nested error details."""

    def test_output_strips_nested_details(self):
        """Verify nested 'details' inside each error detail entry are removed."""
        mock_cmd = Mock()
        mock_cmd.deserialize_output.return_value = {
            "error": {
                "code": "ResyncPasswordFailed",
                "message": "One or more devices failed.",
                "details": [
                    {
                        "code": "CouldNotConnect",
                        "message": "Device CE1 unreachable.",
                        "target": "CE1",
                        "details": [
                            {
                                "code": "Timeout",
                                "message": "Connection timed out.",
                            }
                        ],
                    },
                    {
                        "code": "CouldNotConnect",
                        "message": "Device CE2 unreachable.",
                        "target": "CE2",
                        "details": [
                            {
                                "code": "Timeout",
                                "message": "Connection timed out.",
                            }
                        ],
                    },
                ],
            }
        }
        mock_cmd.ctx = Mock()
        mock_cmd.ctx.vars.instance = Mock()

        result = ErrorFormat._output(mock_cmd)

        for detail in result["error"]["details"]:
            self.assertNotIn(
                "details",
                detail,
                f"Nested 'details' should be stripped from detail: {detail}",
            )

    def test_output_preserves_top_level_fields(self):
        """Verify top-level error fields are preserved after stripping."""
        mock_cmd = Mock()
        mock_cmd.deserialize_output.return_value = {
            "error": {
                "code": "ResyncPasswordFailed",
                "message": "One or more devices failed.",
                "details": [
                    {
                        "code": "CouldNotConnect",
                        "message": "Device CE1 unreachable.",
                        "target": "CE1",
                        "details": [],
                    }
                ],
            }
        }
        mock_cmd.ctx = Mock()
        mock_cmd.ctx.vars.instance = Mock()

        result = ErrorFormat._output(mock_cmd)

        self.assertEqual(result["error"]["code"], "ResyncPasswordFailed")
        self.assertEqual(result["error"]["message"], "One or more devices failed.")
        self.assertEqual(len(result["error"]["details"]), 1)
        self.assertEqual(result["error"]["details"][0]["code"], "CouldNotConnect")
        self.assertEqual(result["error"]["details"][0]["target"], "CE1")

    def test_output_no_error_key(self):
        """Verify response without 'error' key is returned as-is."""
        mock_cmd = Mock()
        mock_cmd.deserialize_output.return_value = {"status": "Succeeded"}
        mock_cmd.ctx = Mock()
        mock_cmd.ctx.vars.instance = Mock()

        result = ErrorFormat._output(mock_cmd)

        self.assertEqual(result, {"status": "Succeeded"})

    def test_output_none_result(self):
        """Verify None result is returned as-is."""
        mock_cmd = Mock()
        mock_cmd.deserialize_output.return_value = None
        mock_cmd.ctx = Mock()
        mock_cmd.ctx.vars.instance = Mock()

        result = ErrorFormat._output(mock_cmd)

        self.assertIsNone(result)

    def test_output_details_without_nested(self):
        """Verify details without nested 'details' are left unchanged."""
        mock_cmd = Mock()
        mock_cmd.deserialize_output.return_value = {
            "error": {
                "code": "ResyncPasswordFailed",
                "message": "One or more devices failed.",
                "details": [
                    {
                        "code": "CouldNotConnect",
                        "message": "Device CE1 unreachable.",
                        "target": "CE1",
                    }
                ],
            }
        }
        mock_cmd.ctx = Mock()
        mock_cmd.ctx.vars.instance = Mock()

        result = ErrorFormat._output(mock_cmd)

        self.assertEqual(result["error"]["details"][0]["code"], "CouldNotConnect")
        self.assertEqual(
            result["error"]["details"][0]["message"], "Device CE1 unreachable."
        )
        self.assertEqual(result["error"]["details"][0]["target"], "CE1")


class TestErrorFormatMessage(unittest.TestCase):
    """Tests for ErrorFormat.format_error_message()."""

    @staticmethod
    def _make_http_error(code, message, target=None, details=None):
        """Build a mock HttpResponseError with OData-style attributes."""
        error = Mock()
        error.code = code
        error.message = message
        error.target = target
        error.details = details or []
        http_error = Mock()
        http_error.error = error
        return http_error

    @staticmethod
    def _make_detail(code, message, target=None):
        """Build a mock error detail entry."""
        detail = Mock()
        detail.code = code
        detail.message = message
        detail.target = target
        return detail

    def test_basic_error_no_details(self):
        """Verify formatting of error with no detail entries."""
        http_error = self._make_http_error("ResyncPasswordFailed", "Operation failed.")
        http_error.error.details = None

        result = ErrorFormat.format_error_message(http_error)

        self.assertIn("(ResyncPasswordFailed) Operation failed.", result)
        self.assertIn("Code: ResyncPasswordFailed", result)
        self.assertIn("Message: Operation failed.", result)
        self.assertNotIn("Exception Details:", result)

    def test_error_with_target(self):
        """Verify target field is included when present."""
        http_error = self._make_http_error(
            "ResyncPasswordFailed",
            "Operation failed.",
            target="/subscriptions/xxx/resourceGroups/rg/providers/.../fabric1",
        )
        http_error.error.details = None

        result = ErrorFormat.format_error_message(http_error)

        self.assertIn(
            "Target: /subscriptions/xxx/resourceGroups/rg/providers/.../fabric1", result
        )

    def test_single_detail_entry(self):
        """Verify formatting with a single detail entry."""
        detail = self._make_detail(
            "CouldNotConnect", "Device CE1 unreachable.", target="CE1"
        )
        http_error = self._make_http_error(
            "ResyncPasswordFailed", "One or more devices failed.", details=[detail]
        )

        result = ErrorFormat.format_error_message(http_error)

        self.assertIn("Exception Details:", result)
        self.assertIn("\t(CouldNotConnect) Device CE1 unreachable.", result)
        self.assertIn("\tCode: CouldNotConnect", result)
        self.assertIn("\tMessage: Device CE1 unreachable.", result)
        self.assertIn("\tTarget: CE1", result)

    def test_multiple_details_have_blank_line_separator(self):
        """Verify a blank line separates each detail block for readability."""
        detail1 = self._make_detail(
            "CouldNotConnect", "Device CE1 unreachable.", target="CE1"
        )
        detail2 = self._make_detail(
            "CouldNotConnect", "Device CE2 unreachable.", target="CE2"
        )
        http_error = self._make_http_error(
            "ResyncPasswordFailed",
            "One or more devices failed.",
            details=[detail1, detail2],
        )

        result = ErrorFormat.format_error_message(http_error)
        lines = result.split("\n")

        # Find the index of Target: CE1 and the next detail header
        ce1_target_idx = next(
            i for i, line in enumerate(lines) if "Target: CE1" in line
        )
        ce2_header_idx = next(
            i for i, line in enumerate(lines) if "(CouldNotConnect) Device CE2" in line
        )
        # There should be a blank line between CE1 target and CE2 header
        self.assertEqual(
            lines[ce1_target_idx + 1],
            "",
            "Expected blank line between detail blocks",
        )
        self.assertEqual(ce2_header_idx, ce1_target_idx + 2)

    def test_detail_without_target(self):
        """Verify detail entry without target omits the Target line."""
        detail = self._make_detail("AuthFailure", "Auth token expired.")
        http_error = self._make_http_error(
            "ResyncPasswordFailed", "Failed.", details=[detail]
        )

        result = ErrorFormat.format_error_message(http_error)

        self.assertNotIn("Target:", result.split("Exception Details:")[-1])

    def test_no_error_attribute(self):
        """Verify fallback to str(http_error) when error attribute is missing."""
        http_error = Mock(spec=Exception)
        http_error.error = None
        http_error.__str__ = Mock(return_value="Raw error string")

        result = ErrorFormat.format_error_message(http_error)

        self.assertEqual(result, "Raw error string")


class TestHandleLroError(unittest.TestCase):
    """Tests for ErrorFormat.handle_lro_error()."""

    def test_raises_cli_error(self):
        """Verify handle_lro_error raises CLIError with formatted message."""
        error = Mock()
        error.code = "ResyncPasswordFailed"
        error.message = "Operation failed."
        error.target = None
        error.details = None
        http_error = Exception("Operation failed.")
        http_error.error = error

        with self.assertRaises(CLIError) as ctx:
            ErrorFormat.handle_lro_error(http_error)

        self.assertIn("ResyncPasswordFailed", str(ctx.exception))
        self.assertIn("Operation failed.", str(ctx.exception))

    def test_raises_cli_error_with_details(self):
        """Verify handle_lro_error includes detail entries in the CLIError."""
        detail = Mock()
        detail.code = "CouldNotConnect"
        detail.message = "Device CE1 unreachable."
        detail.target = "CE1"
        error = Mock()
        error.code = "ResyncPasswordFailed"
        error.message = "One or more devices failed."
        error.target = None
        error.details = [detail]
        http_error = Exception("One or more devices failed.")
        http_error.error = error

        with self.assertRaises(CLIError) as ctx:
            ErrorFormat.handle_lro_error(http_error)

        error_msg = str(ctx.exception)
        self.assertIn("Exception Details:", error_msg)
        self.assertIn("CouldNotConnect", error_msg)
        self.assertIn("Device CE1 unreachable.", error_msg)
        self.assertIn("Target: CE1", error_msg)


if __name__ == "__main__":
    unittest.main()
