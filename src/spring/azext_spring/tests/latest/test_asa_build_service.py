# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import tempfile
import unittest
from pathlib import Path

from azure.cli.core.azclierror import ClientRequestError

from ..._build_service import _update_builder


class TestBuilderInput(unittest.TestCase):
    def test_missing_builder_input_raises_cli_error(self):
        with self.assertRaisesRegex(ClientRequestError, "--builder-json or --builder-file is required"):
            _update_builder(None, None)

    def test_parses_builder_file_and_inline_json(self):
        with tempfile.TemporaryDirectory() as directory:
            builder_file = Path(directory) / "builder.json"
            builder_file.write_text('{"stack": {"id": "file-stack"}}', encoding="utf-8")

            self.assertEqual({"stack": {"id": "file-stack"}}, _update_builder(builder_file, None))
        self.assertEqual({"stack": {"id": "inline-stack"}}, _update_builder(None, '{"stack": {"id": "inline-stack"}}'))
