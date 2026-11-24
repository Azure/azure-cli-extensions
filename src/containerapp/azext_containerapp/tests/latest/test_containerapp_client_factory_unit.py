# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest

from azure.cli.core.azclierror import CLIInternalError

from azext_containerapp._client_factory import handle_raw_exception


class TestHandleRawException(unittest.TestCase):
    def test_preserves_non_json_error_with_braces(self):
        error = RuntimeError("<html><style>body {color:red}</style>gateway error</html>")

        with self.assertRaises(RuntimeError) as raised:
            handle_raw_exception(error)

        self.assertIs(raised.exception, error)

    def test_extracts_json_error(self):
        error = RuntimeError('{"error":{"code":"BadRequest","message":"invalid request"}}')

        with self.assertRaises(CLIInternalError) as raised:
            handle_raw_exception(error)

        self.assertIn("(BadRequest) invalid request", str(raised.exception))
