# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import logging
import os
import sys
from unittest import TestCase
from unittest.mock import mock_open, patch

from azext_aosm.inputs.arm_template_input import ArmTemplateInput

code_directory = os.path.dirname(__file__)
parent_directory = os.path.abspath(os.path.join(code_directory, "../.."))
arm_template_path = os.path.join(parent_directory, "mock_arm_templates", "simple-template.json")
no_params_template_path = os.path.join(parent_directory, "mock_arm_templates", "no-params-template.json")


class TestARMTemplateInput(TestCase):
    """Test the ARMTempalteInput class."""

    def setUp(self):
        # Prints out info logs in console if fails
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        self.arm_input = ArmTemplateInput(
            artifact_name="test-artifact-name",
            artifact_version="1.1.1",
            template_path=arm_template_path,
            default_config=None
        )

    def test_get_defaults_is_none(self):
        """Test ARM template input when default config is None"""
        arm_template_input = self.arm_input

        # Test when default_config is None
        arm_template_input.default_config = None
        defaults = arm_template_input.get_defaults()
        self.assertEqual(defaults, {})

    def test_get_defaults_is_empty_dict(self):
        """Test ARM template input when default config is {}"""
        arm_template_input = self.arm_input
        # Test when default_config is an empty dictionary
        arm_template_input.default_config = {}
        defaults = arm_template_input.get_defaults()
        self.assertEqual(defaults, {})

    def test_get_defaults_with_config(self):
        """Test ARM template input when default config provided"""
        arm_template_input = self.arm_input
        # Test when default_config has some values
        arm_template_input.default_config = {
            "param1": "value1",
            "param2": "value2"
        }
        defaults = arm_template_input.get_defaults()
        self.assertEqual(defaults, {
            "param1": "value1",
            "param2": "value2"
        })

    def test_get_schema_with_params(self):
        """Test getting the schema for the ARM template input."""
        schema = self.arm_input.get_schema()
        expected_schema = {
            '$schema': 'https://json-schema.org/draft-07/schema#',
            'properties': {'location': {'type': 'string', 'default': 'uksouth'}},
            'required': [],
            'type': 'object'
        }
        print("SCHEMA", schema)
        self.assertEqual(schema, expected_schema)

    @patch("builtins.open", mock_open(
        read_data='{"$schema": "#", "resources": { } }'))
    def test_get_schema_no_parameters(self):
        """Test getting the schema for the ARM template input when no parameters are found."""

        no_params_arm_input = ArmTemplateInput(
            artifact_name="test-artifact-name",
            artifact_version="1.1.1",
            template_path=no_params_template_path,
            default_config=None
        )
        # Assert logger warning when no parameters in file
        with self.assertLogs(level='WARNING'):
            schema = no_params_arm_input.get_schema()
            expected_schema = {
                '$schema': 'https://json-schema.org/draft-07/schema#',
                'properties': {},
                'required': [],
                'type': 'object'
            }
            # Assert outputted schema is base schema with empty properties
            self.assertEqual(schema, expected_schema)

    def test_generate_schema_from_params_with_default_values(self):
        """ Test _generate_schema_from_arm_params for ARM template input.
            With default values, which mean no required params
        """
        schema = {
            "properties": {},
            "required": []
        }
        data = {
            "test": {
                "type": "string",
                "defaultValue": "test"
            }
        }
        # pylint: disable=protected-access
        self.arm_input._generate_schema_from_arm_params(schema, data)

        expected_schema = {
            'properties':
                {'test': {'type': 'string', 'default': 'test'}},
                'required': []}

        self.assertEqual(schema, expected_schema)

    def test_generate_schema_from_params_with_no_default_values(self):
        """ Test _generate_schema_from_params for ARM template input.
            Without default values, so they should be added to required properties
        """
        schema = {
            "properties": {},
            "required": []
        }
        data = {
            "test": {
                "type": "string"
            }
        }
        # pylint: disable=protected-access
        self.arm_input._generate_schema_from_arm_params(schema, data)
        expected_schema = {'properties': {'test': {'type': 'string'}}, 'required': ['test']}
        self.assertEqual(schema, expected_schema)

    def test_generate_schema_from_params_nested_properties(self):
        """ Test _generate_schema_from_arm_params for ARM template input.
            With an object in the template, so we expect this to be called recursively
        """
        schema = {
            "properties": {},
            "required": []
        }
        data = {
            "test": {
                "type": "string"
            },
            "vmImageRepositoryCredentials": {
                "type": "object",
                "metadata": {
                    "description": "Credentials used to login to the image repository."
                }
            }
        }
        # pylint: disable=protected-access
        self.arm_input._generate_schema_from_arm_params(schema, data)

        # We expect vmImageRepositoryCredentials to be required and to have a nested schema
        expected_schema = {'properties':
                           {'test': {'type': 'string'},
                            'vmImageRepositoryCredentials': {
                                "type": "object",
                                "properties": {},
                                "required": []}
                            },
                           'required': ['test', 'vmImageRepositoryCredentials']}
        self.assertEqual(schema, expected_schema)
