# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
import json
from unittest.mock import patch, mock_open
from pathlib import Path
from azext_aosm.common.utils import (
    convert_bicep_to_arm, render_bicep_contents_from_j2, get_template_path,
    extract_tarfile, snake_case_to_camel_case, check_tool_installed,
    call_subprocess_raise_output, clean_registry_name, push_image_from_local_registry_to_acr,
    login_to_artifact_store_registry, split_image_path, is_valid_nexus_image_version,
    generate_data_for_given_schema, append_text, InvalidFileTypeError, MissingDependency, CLIError
)

class TestUtils(unittest.TestCase):
    def test_generate_data_with_valid_schema(self):
        """Test generating data with a valid JSON schema."""
        schema = json.dumps({
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name", "age"]
        })
        result = generate_data_for_given_schema(schema)
        self.assertIsInstance(result, dict)
        self.assertIn("name", result)
        self.assertIn("age", result)
           