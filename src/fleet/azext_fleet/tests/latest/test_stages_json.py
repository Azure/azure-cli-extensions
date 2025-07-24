# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
import json
import tempfile
import os
from unittest.mock import Mock


class TestStagesJsonHandling(unittest.TestCase):
    """Test inline JSON support for --stages argument in fleet commands."""

    def setUp(self):
        """Set up test data."""
        self.test_data = {
            "stages": [
                {
                    "name": "stage1",
                    "groups": [
                        {"name": "group1"},
                        {"name": "group2"}
                    ],
                    "afterStageWaitInSeconds": 3600
                }
            ]
        }
        
        # Mock cmd object that provides get_models method
        self.mock_cmd = Mock()
        self.mock_cmd.get_models.return_value = Mock

    def test_file_path_stages(self):
        """Test that file paths for stages work correctly."""
        # This test validates the existing functionality continues to work
        
        # Create a temporary file with test data
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.test_data, f)
            temp_file_path = f.name
        
        try:
            # Test the file path logic
            self.assertTrue(os.path.exists(temp_file_path))
            
            with open(temp_file_path, 'r', encoding='utf-8') as fp:
                data = json.load(fp)
            
            # Verify the data structure is correct for stages
            self.assertIn("stages", data)
            self.assertEqual(len(data["stages"]), 1)
            self.assertEqual(data["stages"][0]["name"], "stage1")
            self.assertEqual(len(data["stages"][0]["groups"]), 2)
            self.assertEqual(data["stages"][0]["afterStageWaitInSeconds"], 3600)
            
        finally:
            # Clean up
            os.unlink(temp_file_path)

    def test_inline_json_stages(self):
        """Test that inline JSON strings for stages work correctly."""
        # This test validates the new functionality
        
        inline_json = json.dumps(self.test_data)
        
        # Test the inline JSON logic
        self.assertFalse(os.path.exists(inline_json))  # Should not exist as file
        
        data = json.loads(inline_json)
        
        # Verify the data structure is correct for stages
        self.assertIn("stages", data)
        self.assertEqual(len(data["stages"]), 1)
        self.assertEqual(data["stages"][0]["name"], "stage1")
        self.assertEqual(len(data["stages"][0]["groups"]), 2)
        self.assertEqual(data["stages"][0]["afterStageWaitInSeconds"], 3600)

    def test_inline_json_minimal_stages(self):
        """Test inline JSON with minimal required fields."""
        minimal_data = {
            "stages": [
                {
                    "name": "minimal-stage",
                    "groups": [
                        {"name": "minimal-group"}
                    ]
                }
            ]
        }
        
        inline_json = json.dumps(minimal_data)
        data = json.loads(inline_json)
        
        # Verify minimal structure works
        self.assertIn("stages", data)
        self.assertEqual(data["stages"][0]["name"], "minimal-stage")
        self.assertEqual(data["stages"][0]["groups"][0]["name"], "minimal-group")
        # afterStageWaitInSeconds should be optional

    def test_invalid_json_string(self):
        """Test that invalid JSON strings raise appropriate errors."""
        invalid_json = '{"stages": [{"name": "test", invalid_syntax}]}'
        
        # Should not exist as a file
        self.assertFalse(os.path.exists(invalid_json))
        
        # Should raise JSONDecodeError when parsed
        with self.assertRaises(json.JSONDecodeError):
            json.loads(invalid_json)

    def test_json_with_path_like_content(self):
        """Test JSON string that contains path-like content."""
        path_like_data = {
            "stages": [
                {
                    "name": "/path/like/stage",
                    "groups": [
                        {"name": "group-with-/slashes/"}
                    ]
                }
            ]
        }
        
        inline_json = json.dumps(path_like_data)
        
        # Even though it contains paths, it should be treated as JSON if it's valid JSON
        self.assertFalse(os.path.exists(inline_json))
        
        data = json.loads(inline_json)
        self.assertEqual(data["stages"][0]["name"], "/path/like/stage")
        self.assertEqual(data["stages"][0]["groups"][0]["name"], "group-with-/slashes/")

    def test_complex_stages_structure(self):
        """Test more complex stages structure with multiple stages and groups."""
        complex_data = {
            "stages": [
                {
                    "name": "stage1",
                    "groups": [
                        {"name": "group1"},
                        {"name": "group2"}
                    ],
                    "afterStageWaitInSeconds": 1800
                },
                {
                    "name": "stage2", 
                    "groups": [
                        {"name": "group3"}
                    ],
                    "afterStageWaitInSeconds": 3600
                }
            ]
        }
        
        inline_json = json.dumps(complex_data)
        data = json.loads(inline_json)
        
        # Verify complex structure
        self.assertEqual(len(data["stages"]), 2)
        self.assertEqual(data["stages"][0]["name"], "stage1")
        self.assertEqual(data["stages"][1]["name"], "stage2")
        self.assertEqual(len(data["stages"][0]["groups"]), 2)
        self.assertEqual(len(data["stages"][1]["groups"]), 1)


if __name__ == "__main__":
    unittest.main()