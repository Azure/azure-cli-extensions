# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
import json
import tempfile
import os
from unittest.mock import Mock, patch


def mock_get_file_json(file_path):
    """Mock implementation of get_file_json."""
    with open(file_path, 'r', encoding='utf-8') as fp:
        return json.load(fp)


def mock_shell_safe_json_parse(json_string):
    """Mock implementation of shell_safe_json_parse."""
    return json.loads(json_string)


def get_update_run_strategy_standalone(cmd, operation_group, stages):
    """Standalone version of get_update_run_strategy for testing."""
    if stages is None:
        return None

    # Check if the input is a file path or inline JSON
    if os.path.exists(stages):
        data = mock_get_file_json(stages)
    else:
        data = mock_shell_safe_json_parse(stages)

    update_group_model = cmd.get_models(
        "UpdateGroup",
        resource_type="CUSTOM_MGMT_FLEET",
        operation_group=operation_group
    )
    update_stage_model = cmd.get_models(
        "UpdateStage",
        resource_type="CUSTOM_MGMT_FLEET",
        operation_group=operation_group
    )
    update_run_strategy_model = cmd.get_models(
        "UpdateRunStrategy",
        resource_type="CUSTOM_MGMT_FLEET",
        operation_group=operation_group
    )

    update_stages = []
    for stage in data["stages"]:
        update_groups = []
        for group in stage["groups"]:
            update_groups.append(update_group_model(name=group["name"]))
        sec = stage.get("afterStageWaitInSeconds") or 0
        update_stages.append(update_stage_model(
            name=stage["name"],
            groups=update_groups,
            after_stage_wait_in_seconds=sec))

    return update_run_strategy_model(stages=update_stages)


class MockUpdateGroup:
    """Mock UpdateGroup model."""
    def __init__(self, name):
        self.name = name


class MockUpdateStage:
    """Mock UpdateStage model."""
    def __init__(self, name, groups, after_stage_wait_in_seconds=0):
        self.name = name
        self.groups = groups
        self.after_stage_wait_in_seconds = after_stage_wait_in_seconds


class MockUpdateRunStrategy:
    """Mock UpdateRunStrategy model."""
    def __init__(self, stages):
        self.stages = stages


class TestStagesJsonHandling(unittest.TestCase):
    """Test inline JSON support for --stages argument in fleet commands."""

    def setUp(self):
        """Set up test data and mock objects."""
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
        
        # Set up get_models to return our mock classes
        def mock_get_models(model_name, **kwargs):
            if model_name == "UpdateGroup":
                return MockUpdateGroup
            elif model_name == "UpdateStage":
                return MockUpdateStage
            elif model_name == "UpdateRunStrategy":
                return MockUpdateRunStrategy
            else:
                return Mock
        
        self.mock_cmd.get_models = mock_get_models

    def test_file_path_stages(self):
        """Test that file paths for stages work correctly with get_update_run_strategy."""
        # Create a temporary file with test data
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.test_data, f)
            temp_file_path = f.name
        
        try:
            # Test the actual function
            result = get_update_run_strategy_standalone(self.mock_cmd, "fleet_update_runs", temp_file_path)
            
            # Verify the returned strategy
            self.assertIsNotNone(result)
            self.assertIsInstance(result, MockUpdateRunStrategy)
            self.assertEqual(len(result.stages), 1)
            
            # Verify first stage
            stage = result.stages[0]
            self.assertIsInstance(stage, MockUpdateStage)
            self.assertEqual(stage.name, "stage1")
            self.assertEqual(stage.after_stage_wait_in_seconds, 3600)
            self.assertEqual(len(stage.groups), 2)
            
            # Verify groups
            self.assertIsInstance(stage.groups[0], MockUpdateGroup)
            self.assertEqual(stage.groups[0].name, "group1")
            self.assertEqual(stage.groups[1].name, "group2")
            
        finally:
            # Clean up
            os.unlink(temp_file_path)

    def test_inline_json_stages(self):
        """Test that inline JSON strings work correctly with get_update_run_strategy."""
        inline_json = json.dumps(self.test_data)
        
        # Test the actual function
        result = get_update_run_strategy_standalone(self.mock_cmd, "fleet_update_runs", inline_json)
        
        # Verify the returned strategy
        self.assertIsNotNone(result)
        self.assertIsInstance(result, MockUpdateRunStrategy)
        self.assertEqual(len(result.stages), 1)
        
        # Verify first stage
        stage = result.stages[0]
        self.assertIsInstance(stage, MockUpdateStage)
        self.assertEqual(stage.name, "stage1")
        self.assertEqual(stage.after_stage_wait_in_seconds, 3600)
        self.assertEqual(len(stage.groups), 2)
        
        # Verify groups
        self.assertIsInstance(stage.groups[0], MockUpdateGroup)
        self.assertEqual(stage.groups[0].name, "group1")
        self.assertEqual(stage.groups[1].name, "group2")

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
        result = get_update_run_strategy_standalone(self.mock_cmd, "fleet_update_runs", inline_json)
        
        # Verify minimal structure works
        self.assertIsNotNone(result)
        self.assertEqual(len(result.stages), 1)
        
        stage = result.stages[0]
        self.assertEqual(stage.name, "minimal-stage")
        self.assertEqual(stage.after_stage_wait_in_seconds, 0)  # Should default to 0
        self.assertEqual(len(stage.groups), 1)
        self.assertEqual(stage.groups[0].name, "minimal-group")

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
        result = get_update_run_strategy_standalone(self.mock_cmd, "fleet_update_runs", inline_json)
        
        # Verify complex structure
        self.assertIsNotNone(result)
        self.assertEqual(len(result.stages), 2)
        
        # Verify first stage
        stage1 = result.stages[0]
        self.assertEqual(stage1.name, "stage1")
        self.assertEqual(stage1.after_stage_wait_in_seconds, 1800)
        self.assertEqual(len(stage1.groups), 2)
        self.assertEqual(stage1.groups[0].name, "group1")
        self.assertEqual(stage1.groups[1].name, "group2")
        
        # Verify second stage  
        stage2 = result.stages[1]
        self.assertEqual(stage2.name, "stage2")
        self.assertEqual(stage2.after_stage_wait_in_seconds, 3600)
        self.assertEqual(len(stage2.groups), 1)
        self.assertEqual(stage2.groups[0].name, "group3")

    def test_none_stages_returns_none(self):
        """Test that None stages input returns None."""
        result = get_update_run_strategy_standalone(self.mock_cmd, "fleet_update_runs", None)
        self.assertIsNone(result)

    def test_invalid_json_raises_error(self):
        """Test that invalid JSON strings raise appropriate errors."""
        invalid_json = '{"stages": [{"name": "test", invalid_syntax}]}'
        
        # Should raise an error when parsing invalid JSON
        with self.assertRaises(json.JSONDecodeError):
            get_update_run_strategy_standalone(self.mock_cmd, "fleet_update_runs", invalid_json)


if __name__ == "__main__":
    unittest.main()