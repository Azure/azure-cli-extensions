# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import json
from unittest import TestCase
from pathlib import Path
from azext_aosm.build_processors.helm_chart_processor import HelmChartProcessor
from ruamel.yaml import CommentedMap, CommentedSeq
from azext_aosm.common.constants import EXPOSE, HARDCODE
from azext_aosm.inputs.helm_chart_input import HelmChartInput
code_directory = os.path.dirname(__file__)
parent_directory = os.path.abspath(os.path.join(code_directory, "../.."))
mock_cnf_directory = os.path.join(parent_directory, "mock_cnf")
parameter_exposure_directory = os.path.join(mock_cnf_directory, "finetune_parameter_exposure")

EXPOSE_TRUE_OVERRIDE_FILE = os.path.join(parameter_exposure_directory, "expose-all-true-override-values.yaml")
EXPOSE_FALSE_OVERRIDE_FILE = os.path.join(parameter_exposure_directory, "expose-all-false-override-values.yaml")
EXPOSE_TRUE_EXPECTED_MAPPINGS = os.path.join(parameter_exposure_directory, "expose-all-true-expected-mappings.json")
EXPOSE_FALSE_EXPECTED_MAPPINGS = os.path.join(parameter_exposure_directory, "expose-all-false-expected-mappings.json")

MOCK_NF_AGENT_HELM_CHART = os.path.join(mock_cnf_directory, "helm-charts", "nf-agent-cnf-0.1.0.tgz")


class BaseExposeAllTrue(TestCase):
    def setUp(self):
        input_artifact = HelmChartInput(
            artifact_name='test-helm-chart',
            artifact_version='1.0.0',
            chart_path=Path(MOCK_NF_AGENT_HELM_CHART),
            default_config_path=Path(EXPOSE_TRUE_OVERRIDE_FILE)
        )
        self.helm_chart_processor = HelmChartProcessor(
            name="test-generate-mappings-cnf",
            input_artifact=input_artifact,
            registry_handler=None,
            expose_all_params=True
        )


class BaseExposeAllFalse(TestCase):
    def setUp(self):
        input_artifact = HelmChartInput(
            artifact_name='test-helm-chart',
            artifact_version='1.0.0',
            chart_path=Path(MOCK_NF_AGENT_HELM_CHART),
            default_config_path=Path(EXPOSE_FALSE_OVERRIDE_FILE)
        )
        self.helm_chart_processor = HelmChartProcessor(
            name="test-generate-mappings-cnf",
            input_artifact=input_artifact,
            registry_handler=None,
            expose_all_params=False
        )


class TestGenerateMappingsExposeAllMock(BaseExposeAllTrue):
    def test_catch_all_yaml(self):
        schema = self.helm_chart_processor.input_artifact.get_schema()
        defaults = self.helm_chart_processor.input_artifact.get_defaults()
        output_mappings = self.helm_chart_processor.generate_values_mappings(schema, defaults)
        with open(EXPOSE_TRUE_EXPECTED_MAPPINGS, "r", encoding="utf-8") as _file:
            expected_mappings = json.load(_file)
        self.assertEqual(output_mappings, expected_mappings)


class TestGeneratemappingsExposeNoneMock(BaseExposeAllFalse):
    def test_catch_all_yaml(self):
        schema = self.helm_chart_processor.input_artifact.get_schema()
        defaults = self.helm_chart_processor.input_artifact.get_defaults()
        output_mappings = self.helm_chart_processor.generate_values_mappings(schema, defaults)
        with open(EXPOSE_FALSE_EXPECTED_MAPPINGS, "r", encoding="utf-8") as _file:
            expected_mappings = json.load(_file)
        self.assertEqual(output_mappings, expected_mappings)


class TestGenerateMappingsExposeAllTrueInteger(BaseExposeAllTrue):
    def setUp(self):
        super().setUp()
        self.mocked_yaml = CommentedMap()
        self.mocked_yaml['testParameter'] = 1

    def test_integer_no_comment(self):
        self.helm_chart_processor.input_artifact.default_config = self.mocked_yaml
        schema = self.helm_chart_processor.input_artifact.get_schema()
        defaults = self.helm_chart_processor.input_artifact.get_defaults()

        output_mappings = self.helm_chart_processor.generate_values_mappings(schema, defaults)
        expected_mappings = {"testParameter": "{deployParameters.test-generate-mappings-cnf.testParameter}"}
        self.assertEqual(output_mappings, expected_mappings)

    def test_integer_hardcode_nfdv(self):
        # If expose all is true, and hardcode-nfdv, hardcode the parameter
        self.mocked_yaml.yaml_add_eol_comment(HARDCODE, 'testParameter')
        self.helm_chart_processor.input_artifact.default_config = self.mocked_yaml
        schema = self.helm_chart_processor.input_artifact.get_schema()
        defaults = self.helm_chart_processor.input_artifact.get_defaults()

        output_mappings = self.helm_chart_processor.generate_values_mappings(schema, defaults)
        expected_mappings = {"testParameter": 1}
        self.assertEqual(output_mappings, expected_mappings)

    def test_integer_expose_cgs(self):
        # This should do nothing different here, because expose all will already expose this
        self.mocked_yaml.yaml_add_eol_comment(EXPOSE, 'testParameter')

        self.helm_chart_processor.input_artifact.default_config = self.mocked_yaml
        schema = self.helm_chart_processor.input_artifact.get_schema()
        defaults = self.helm_chart_processor.input_artifact.get_defaults()

        output_mappings = self.helm_chart_processor.generate_values_mappings(schema, defaults)
        expected_mappings = {"testParameter": "{deployParameters.test-generate-mappings-cnf.testParameter}"}
        self.assertEqual(output_mappings, expected_mappings)

    def test_integer_both_comments(self):
        # We expect comments to be ignored if they have both options, so should expose all
        self.mocked_yaml.yaml_add_eol_comment(f"# {EXPOSE} {HARDCODE}", 'testParameter')

        self.helm_chart_processor.input_artifact.default_config = self.mocked_yaml
        schema = self.helm_chart_processor.input_artifact.get_schema()
        defaults = self.helm_chart_processor.input_artifact.get_defaults()

        output_mappings = self.helm_chart_processor.generate_values_mappings(schema, defaults)
        expected_mappings = {"testParameter": "{deployParameters.test-generate-mappings-cnf.testParameter}"}
        self.assertEqual(output_mappings, expected_mappings)


class TestGenerateMappingsExposeAllTrueObject(BaseExposeAllTrue):
    def setUp(self):
        """
        This mock looks like:
        testParameter:
            object1: "object1"
            object2: "object2
        """
        super().setUp()
        self.mocked_yaml = CommentedMap()
        self.mocked_yaml_object = CommentedMap()
        self.mocked_yaml_object['object1'] = "object1"
        self.mocked_yaml_object['object2'] = "object2"

    def test_object_no_comment(self):

        self.mocked_yaml['testParameter'] = self.mocked_yaml_object
        self.helm_chart_processor.input_artifact.default_config = self.mocked_yaml

        schema = self.helm_chart_processor.input_artifact.get_schema()
        defaults = self.helm_chart_processor.input_artifact.get_defaults()

        output_mappings = self.helm_chart_processor.generate_values_mappings(schema, defaults)
        expected_mappings = {
            "testParameter": {
                "object1": "{deployParameters.test-generate-mappings-cnf.testParameter_object1}",
                "object2": "{deployParameters.test-generate-mappings-cnf.testParameter_object2}",
            }
        }
        self.assertEqual(output_mappings, expected_mappings)

    def test_object_expose_cgs(self):
        """
        This mock looks like:
        testParameter:
            object1: "object1" # expose-cgs
            object2: "object2
        """
        self.mocked_yaml_object.yaml_add_eol_comment(EXPOSE, 'object1')
        self.mocked_yaml['testParameter'] = self.mocked_yaml_object

        self.helm_chart_processor.input_artifact.default_config = self.mocked_yaml
        schema = self.helm_chart_processor.input_artifact.get_schema()
        defaults = self.helm_chart_processor.input_artifact.get_defaults()

        output_mappings = self.helm_chart_processor.generate_values_mappings(schema, defaults)
        expected_mappings = {
            "testParameter": {
                "object1": "{deployParameters.test-generate-mappings-cnf.testParameter_object1}",
                "object2": "{deployParameters.test-generate-mappings-cnf.testParameter_object2}",
            }
        }
        self.assertEqual(output_mappings, expected_mappings)

    def test_object_hardcode_nfdv(self):
        """
        This mock looks like:
        testParameter:
            object1: "object1" # hardcode-nfdv
            object2: "object2
        """
        self.mocked_yaml_object.yaml_add_eol_comment(HARDCODE, 'object1')
        self.mocked_yaml['testParameter'] = self.mocked_yaml_object

        self.helm_chart_processor.input_artifact.default_config = self.mocked_yaml
        schema = self.helm_chart_processor.input_artifact.get_schema()
        defaults = self.helm_chart_processor.input_artifact.get_defaults()

        output_mappings = self.helm_chart_processor.generate_values_mappings(schema, defaults)
        expected_mappings = {
            "testParameter": {
                "object1": "object1",
                "object2": "{deployParameters.test-generate-mappings-cnf.testParameter_object2}",
            }
        }
        self.assertEqual(output_mappings, expected_mappings)


class TestGenerateMappingsExposeAllTrueArray(BaseExposeAllTrue):
    def setUp(self):
        """
        This mock looks like:
        testParameter:
        - item1object1: 1
          item1object2: "test1"
        - item2object1: 2
          item2object2: "test2"
        """
        super().setUp()

        # Create two CommentedMaps (objects) and add them to the CommentedSeq (list)
        self.mocked_seq = CommentedSeq()
        self.mocked_map1 = CommentedMap()
        self.mocked_map1['item1object1'] = 1
        self.mocked_map1['item1object2'] = "test1"
        self.mocked_seq.append(self.mocked_map1)

        self.mocked_map2 = CommentedMap()
        self.mocked_map2['item2object1'] = 2
        self.mocked_map2['item2object2'] = "test2"
        self.mocked_seq.append(self.mocked_map2)
        # Add the CommentedSeq (list) to a CommentedMap (object)
        self.mocked_map = CommentedMap()
        self.mocked_map['testParameter'] = self.mocked_seq

    def test_array_no_comment(self):
        self.helm_chart_processor.input_artifact.default_config = self.mocked_map

        schema = self.helm_chart_processor.input_artifact.get_schema()
        defaults = self.helm_chart_processor.input_artifact.get_defaults()

        output_mappings = self.helm_chart_processor.generate_values_mappings(schema, defaults)
        expected_mappings = {
            "testParameter": "{deployParameters.test-generate-mappings-cnf.testParameter}"
        }
        self.assertEqual(output_mappings, expected_mappings)

    def test_array_hardcode_nfdv(self):
        self.mocked_map.yaml_add_eol_comment(HARDCODE, 'testParameter')
        self.helm_chart_processor.input_artifact.default_config = self.mocked_map

        schema = self.helm_chart_processor.input_artifact.get_schema()
        defaults = self.helm_chart_processor.input_artifact.get_defaults()

        output_mappings = self.helm_chart_processor.generate_values_mappings(schema, defaults)
        expected_mappings = {
            "testParameter": [
                {
                    "item1object1": 1,
                    "item1object2": "test1"
                },
                {
                    "item2object1": 2,
                    "item2object2": "test2"
                },
            ],
        }
        self.assertEqual(output_mappings, expected_mappings)

    def test_array_expose_cgs(self):
        self.mocked_map.yaml_add_eol_comment(EXPOSE, 'testParameter')
        self.helm_chart_processor.input_artifact.default_config = self.mocked_map

        schema = self.helm_chart_processor.input_artifact.get_schema()
        defaults = self.helm_chart_processor.input_artifact.get_defaults()

        output_mappings = self.helm_chart_processor.generate_values_mappings(schema, defaults)
        expected_mappings = {
            "testParameter": "{deployParameters.test-generate-mappings-cnf.testParameter}"
        }
        self.assertEqual(output_mappings, expected_mappings)

    def test_item_comment_ignored(self):
        self.mocked_map['testParameter'][0].yaml_add_eol_comment(HARDCODE, 'item2object1')

        self.helm_chart_processor.input_artifact.default_config = self.mocked_map

        schema = self.helm_chart_processor.input_artifact.get_schema()
        defaults = self.helm_chart_processor.input_artifact.get_defaults()

        output_mappings = self.helm_chart_processor.generate_values_mappings(schema, defaults)
        expected_mappings = {
            "testParameter": "{deployParameters.test-generate-mappings-cnf.testParameter}"
        }
        self.assertEqual(output_mappings, expected_mappings)


class TestGenerateMappingsExposeAllTrueEmptyArray(BaseExposeAllTrue):
    def setUp(self):
        super().setUp()
        self.mocked_yaml = CommentedSeq()
        self.mocked_map = CommentedMap()
        self.mocked_map['testParameter'] = self.mocked_yaml

    def test_empty_array(self):
        self.helm_chart_processor.input_artifact.default_config = self.mocked_map

        schema = self.helm_chart_processor.input_artifact.get_schema()
        defaults = self.helm_chart_processor.input_artifact.get_defaults()

        output_mappings = self.helm_chart_processor.generate_values_mappings(schema, defaults)
        expected_mappings = {"testParameter": "{deployParameters.test-generate-mappings-cnf.testParameter}"}
        self.assertEqual(output_mappings, expected_mappings)

    def test_empty_array_expose_cgs(self):
        self.mocked_map.yaml_add_eol_comment(EXPOSE, 'testParameter')
        self.helm_chart_processor.input_artifact.default_config = self.mocked_map

        schema = self.helm_chart_processor.input_artifact.get_schema()
        defaults = self.helm_chart_processor.input_artifact.get_defaults()

        output_mappings = self.helm_chart_processor.generate_values_mappings(schema, defaults)
        expected_mappings = {"testParameter": "{deployParameters.test-generate-mappings-cnf.testParameter}"}
        self.assertEqual(output_mappings, expected_mappings)

    def test_empty_array_hardcode_nfdv(self):
        self.mocked_map.yaml_add_eol_comment(HARDCODE, 'testParameter')
        self.helm_chart_processor.input_artifact.default_config = self.mocked_map

        schema = self.helm_chart_processor.input_artifact.get_schema()
        defaults = self.helm_chart_processor.input_artifact.get_defaults()

        output_mappings = self.helm_chart_processor.generate_values_mappings(schema, defaults)
        expected_mappings = {"testParameter": []}
        self.assertEqual(output_mappings, expected_mappings)


class TestGenerateMappingsExposeAllTrueNestedArray(BaseExposeAllTrue):
    def setUp(self):
        """
        This mock looks like:
        testParameter:
        - item1object1: 1
          item1object2:
          - nestedObject: 2
        """
        super().setUp()
        # Create two CommentedMaps (objects) and add them to the CommentedSeq (list)
        self.mocked_seq = CommentedSeq()
        self.mocked_map1 = CommentedMap()
        self.mocked_map1['item1object1'] = 1

        self.mocked_nested_seq = CommentedSeq()
        self.mocked_map2 = CommentedMap()
        self.mocked_map2['nestedobject'] = 2
        self.mocked_nested_seq.append(self.mocked_map2)

        self.mocked_map1['item1object2'] = self.mocked_nested_seq
        self.mocked_seq.append(self.mocked_map1)

        # Add the CommentedSeq to a CommentedMap
        self.mocked_map = CommentedMap()
        self.mocked_map['testParameter'] = self.mocked_seq

    def test_array_hardcode_nfdv(self):
        self.mocked_map.yaml_add_eol_comment(HARDCODE, 'testParameter')
        self.helm_chart_processor.input_artifact.default_config = self.mocked_map

        schema = self.helm_chart_processor.input_artifact.get_schema()
        defaults = self.helm_chart_processor.input_artifact.get_defaults()

        output_mappings = self.helm_chart_processor.generate_values_mappings(schema, defaults)
        expected_mappings = {
            "testParameter": [
                {
                    "item1object1": 1,
                    "item1object2": [
                        {
                            "nestedobject": 2
                        }
                    ]
                }
            ],
        }
        self.assertEqual(output_mappings, expected_mappings)

    def test_array_no_comment(self):
        self.helm_chart_processor.input_artifact.default_config = self.mocked_map

        schema = self.helm_chart_processor.input_artifact.get_schema()
        defaults = self.helm_chart_processor.input_artifact.get_defaults()

        output_mappings = self.helm_chart_processor.generate_values_mappings(schema, defaults)
        expected_mappings = {
            "testParameter": "{deployParameters.test-generate-mappings-cnf.testParameter}"
        }
        self.assertEqual(output_mappings, expected_mappings)

    def test_array_expose_cgs(self):
        self.mocked_map.yaml_add_eol_comment(EXPOSE, 'testParameter')
        self.helm_chart_processor.input_artifact.default_config = self.mocked_map
        schema = self.helm_chart_processor.input_artifact.get_schema()
        defaults = self.helm_chart_processor.input_artifact.get_defaults()

        output_mappings = self.helm_chart_processor.generate_values_mappings(schema, defaults)
        expected_mappings = {
            "testParameter": "{deployParameters.test-generate-mappings-cnf.testParameter}"
        }
        self.assertEqual(output_mappings, expected_mappings)


class TestGenerateMappingsExposeAllFalseInteger(BaseExposeAllFalse):
    def setUp(self):
        super().setUp()
        self.mocked_yaml = CommentedMap()
        self.mocked_yaml['testParameter'] = 1

    def test_integer_no_comment(self):
        self.helm_chart_processor.input_artifact.default_config = self.mocked_yaml
        schema = self.helm_chart_processor.input_artifact.get_schema()
        defaults = self.helm_chart_processor.input_artifact.get_defaults()

        output_mappings = self.helm_chart_processor.generate_values_mappings(schema, defaults)
        expected_mappings = {"testParameter": 1}

        self.assertEqual(output_mappings, expected_mappings)

    def test_integer_hardcode_nfdv(self):
        self.mocked_yaml.yaml_add_eol_comment(HARDCODE, 'testParameter')
        self.helm_chart_processor.input_artifact.default_config = self.mocked_yaml

        schema = self.helm_chart_processor.input_artifact.get_schema()
        defaults = self.helm_chart_processor.input_artifact.get_defaults()

        output_mappings = self.helm_chart_processor.generate_values_mappings(schema, defaults)
        expected_mappings = {"testParameter": 1}
        self.assertEqual(output_mappings, expected_mappings)

    def test_integer_expose_cgs(self):
        self.mocked_yaml.yaml_add_eol_comment(EXPOSE, 'testParameter')
        self.helm_chart_processor.input_artifact.default_config = self.mocked_yaml

        schema = self.helm_chart_processor.input_artifact.get_schema()
        defaults = self.helm_chart_processor.input_artifact.get_defaults()

        output_mappings = self.helm_chart_processor.generate_values_mappings(schema, defaults)
        expected_mappings = {"testParameter": "{deployParameters.test-generate-mappings-cnf.testParameter}"}
        self.assertEqual(output_mappings, expected_mappings)

    def test_integer_both_comments(self):
        # We expect comments to be ignored if they have both options, so should expose nothing
        self.mocked_yaml.yaml_add_eol_comment(f"# {EXPOSE} {HARDCODE}", 'testParameter')
        self.helm_chart_processor.input_artifact.default_config = self.mocked_yaml

        schema = self.helm_chart_processor.input_artifact.get_schema()
        defaults = self.helm_chart_processor.input_artifact.get_defaults()

        output_mappings = self.helm_chart_processor.generate_values_mappings(schema, defaults)
        expected_mappings = {"testParameter": 1}

        self.assertEqual(output_mappings, expected_mappings)


class TestGenerateMappingsExposeAllFalseObject(BaseExposeAllFalse):
    def setUp(self):
        """
        This mock looks like:
        testParameter:
            object1: "object1"
            object2: "object2"
        """
        super().setUp()
        self.mocked_yaml = CommentedMap()
        self.mocked_yaml_object = CommentedMap()
        self.mocked_yaml_object['object1'] = "object1"
        self.mocked_yaml_object['object2'] = "object2"

    def test_object_no_comment(self):
        self.mocked_yaml['testParameter'] = self.mocked_yaml_object
        self.helm_chart_processor.input_artifact.default_config = self.mocked_yaml

        schema = self.helm_chart_processor.input_artifact.get_schema()
        defaults = self.helm_chart_processor.input_artifact.get_defaults()

        output_mappings = self.helm_chart_processor.generate_values_mappings(schema, defaults)
        expected_mappings = {
            "testParameter": {
                "object1": "object1",
                "object2": "object2",
            }
        }
        self.assertEqual(output_mappings, expected_mappings)

    def test_object_expose_cgs(self):
        """
        This mock looks like:
        testParameter:
            object1: "object1" # expose-cgs
            object2: "object2
        """
        self.mocked_yaml_object.yaml_add_eol_comment(EXPOSE, 'object1')
        self.mocked_yaml['testParameter'] = self.mocked_yaml_object

        self.helm_chart_processor.input_artifact.default_config = self.mocked_yaml

        schema = self.helm_chart_processor.input_artifact.get_schema()
        defaults = self.helm_chart_processor.input_artifact.get_defaults()

        output_mappings = self.helm_chart_processor.generate_values_mappings(schema, defaults)
        expected_mappings = {
            "testParameter": {
                "object1": "{deployParameters.test-generate-mappings-cnf.testParameter_object1}",
                "object2": "object2",
            }
        }
        self.assertEqual(output_mappings, expected_mappings)

    def test_object_hardcode_nfdv(self):
        """
        This mock looks like:
        testParameter:
            object1: "object1" # hardcode-nfdv
            object2: "object2
        """
        self.mocked_yaml_object.yaml_add_eol_comment(HARDCODE, 'object1')
        self.mocked_yaml['testParameter'] = self.mocked_yaml_object

        self.helm_chart_processor.input_artifact.default_config = self.mocked_yaml

        schema = self.helm_chart_processor.input_artifact.get_schema()
        defaults = self.helm_chart_processor.input_artifact.get_defaults()

        output_mappings = self.helm_chart_processor.generate_values_mappings(schema, defaults)
        expected_mappings = {
            "testParameter": {
                "object1": "object1",
                "object2": "object2",
            }
        }
        self.assertEqual(output_mappings, expected_mappings)


class TestGenerateMappingsExposeAllFalseArray(BaseExposeAllFalse):
    def setUp(self):
        """
        This mock looks like:
        testParameter:
        - item1object1: 1
          item1object2: "test1"
        - item2object1: 2
          item2object2: "test2"
        """
        super().setUp()

        # Create two CommentedMaps (objects) and add them to the CommentedSeq (list)
        self.mocked_seq = CommentedSeq()
        self.mocked_map1 = CommentedMap()
        self.mocked_map1['item1object1'] = 1
        self.mocked_map1['item1object2'] = "test1"
        self.mocked_seq.append(self.mocked_map1)

        self.mocked_map2 = CommentedMap()
        self.mocked_map2['item2object1'] = 2
        self.mocked_map2['item2object2'] = "test2"
        self.mocked_seq.append(self.mocked_map2)
        # Add the CommentedSeq (list) to a CommentedMap (object)
        self.mocked_map = CommentedMap()
        self.mocked_map['testParameter'] = self.mocked_seq

    def test_array_no_comment(self):
        self.helm_chart_processor.input_artifact.default_config = self.mocked_map
        schema = self.helm_chart_processor.input_artifact.get_schema()
        defaults = self.helm_chart_processor.input_artifact.get_defaults()

        output_mappings = self.helm_chart_processor.generate_values_mappings(schema, defaults)
        expected_mappings = {
            "testParameter": [
                {
                    "item1object1": 1,
                    "item1object2": "test1"
                },
                {
                    "item2object1": 2,
                    "item2object2": "test2"
                },
            ],
        }
        self.assertEqual(output_mappings, expected_mappings)

    def test_array_hardcode_nfdv(self):
        self.mocked_map.yaml_add_eol_comment(HARDCODE, 'testParameter')
        self.helm_chart_processor.input_artifact.default_config = self.mocked_map

        schema = self.helm_chart_processor.input_artifact.get_schema()
        defaults = self.helm_chart_processor.input_artifact.get_defaults()

        output_mappings = self.helm_chart_processor.generate_values_mappings(schema, defaults)
        expected_mappings = {
            "testParameter": [
                {
                    "item1object1": 1,
                    "item1object2": "test1"
                },
                {
                    "item2object1": 2,
                    "item2object2": "test2"
                },
            ],
        }
        self.assertEqual(output_mappings, expected_mappings)

    def test_array_expose_cgs(self):
        self.mocked_map.yaml_add_eol_comment(EXPOSE, 'testParameter')
        self.helm_chart_processor.input_artifact.default_config = self.mocked_map
        schema = self.helm_chart_processor.input_artifact.get_schema()
        defaults = self.helm_chart_processor.input_artifact.get_defaults()

        output_mappings = self.helm_chart_processor.generate_values_mappings(schema, defaults)
        expected_mappings = {
            "testParameter": "{deployParameters.test-generate-mappings-cnf.testParameter}"
        }
        self.assertEqual(output_mappings, expected_mappings)

    def test_item_comment_ignored(self):
        self.mocked_map['testParameter'][0].yaml_add_eol_comment(EXPOSE, 'item2object1')

        self.helm_chart_processor.input_artifact.default_config = self.mocked_map
        self.helm_chart_processor.input_artifact.default_config = self.mocked_map

        schema = self.helm_chart_processor.input_artifact.get_schema()
        defaults = self.helm_chart_processor.input_artifact.get_defaults()
        output_mappings = self.helm_chart_processor.generate_values_mappings(schema, defaults)

        expected_mappings = {
            "testParameter": [
                {
                    "item1object1": 1,
                    "item1object2": "test1"
                },
                {
                    "item2object1": 2,
                    "item2object2": "test2"
                },
            ],
        }
        self.assertEqual(output_mappings, expected_mappings)


class TestGenerateMappingsExposeAllFalseEmptyArray(BaseExposeAllFalse):
    def setUp(self):
        super().setUp()
        self.mocked_yaml = CommentedSeq()
        self.mocked_map = CommentedMap()
        self.mocked_map['testParameter'] = self.mocked_yaml

    def test_empty_array(self):
        self.helm_chart_processor.input_artifact.default_config = self.mocked_map

        schema = self.helm_chart_processor.input_artifact.get_schema()
        defaults = self.helm_chart_processor.input_artifact.get_defaults()

        output_mappings = self.helm_chart_processor.generate_values_mappings(schema, defaults)
        expected_mappings = {"testParameter": []}
        self.assertEqual(output_mappings, expected_mappings)

    def test_empty_array_expose_cgs(self):
        self.mocked_map.yaml_add_eol_comment(EXPOSE, 'testParameter')
        self.helm_chart_processor.input_artifact.default_config = self.mocked_map

        schema = self.helm_chart_processor.input_artifact.get_schema()
        defaults = self.helm_chart_processor.input_artifact.get_defaults()

        output_mappings = self.helm_chart_processor.generate_values_mappings(schema, defaults)
        expected_mappings = {"testParameter": "{deployParameters.test-generate-mappings-cnf.testParameter}"}
        self.assertEqual(output_mappings, expected_mappings)

    def test_empty_array_hardcode_nfdv(self):
        self.mocked_map.yaml_add_eol_comment(HARDCODE, 'testParameter')
        self.helm_chart_processor.input_artifact.default_config = self.mocked_map
        schema = self.helm_chart_processor.input_artifact.get_schema()
        defaults = self.helm_chart_processor.input_artifact.get_defaults()

        output_mappings = self.helm_chart_processor.generate_values_mappings(schema, defaults)
        expected_mappings = {"testParameter": []}
        self.assertEqual(output_mappings, expected_mappings)


class TestGenerateMappingsExposeAllFalseNestedArray(BaseExposeAllFalse):
    def setUp(self):
        """
        This mock looks like:
        testParameter:
        - item1object1: 1
          item1object2:
          - nestedObject: 2
        """
        super().setUp()
        # Create two CommentedMaps (objects) and add them to the CommentedSeq (list)
        self.mocked_seq = CommentedSeq()
        self.mocked_map1 = CommentedMap()
        self.mocked_map1['item1object1'] = 1

        self.mocked_nested_seq = CommentedSeq()
        self.mocked_map2 = CommentedMap()
        self.mocked_map2['nestedobject'] = 2
        self.mocked_nested_seq.append(self.mocked_map2)

        self.mocked_map1['item1object2'] = self.mocked_nested_seq
        self.mocked_seq.append(self.mocked_map1)

        # Add the CommentedSeq to a CommentedMap
        self.mocked_map = CommentedMap()
        self.mocked_map['testParameter'] = self.mocked_seq

    def test_array_hardcode_nfdv(self):
        self.mocked_map.yaml_add_eol_comment(HARDCODE, 'testParameter')
        self.helm_chart_processor.input_artifact.default_config = self.mocked_map

        schema = self.helm_chart_processor.input_artifact.get_schema()
        defaults = self.helm_chart_processor.input_artifact.get_defaults()

        output_mappings = self.helm_chart_processor.generate_values_mappings(schema, defaults)
        expected_mappings = {
            "testParameter": [
                {
                    "item1object1": 1,
                    "item1object2": [
                        {
                            "nestedobject": 2
                        }
                    ]
                }
            ],
        }
        self.assertEqual(output_mappings, expected_mappings)

    def test_array_no_comment(self):
        self.helm_chart_processor.input_artifact.default_config = self.mocked_map
        schema = self.helm_chart_processor.input_artifact.get_schema()
        defaults = self.helm_chart_processor.input_artifact.get_defaults()

        output_mappings = self.helm_chart_processor.generate_values_mappings(schema, defaults)
        expected_mappings = {
            "testParameter": [
                {
                    "item1object1": 1,
                    "item1object2": [
                        {
                            "nestedobject": 2
                        }
                    ]
                }
            ],
        }
        self.assertEqual(output_mappings, expected_mappings)

    def test_array_expose_cgs(self):
        self.mocked_map.yaml_add_eol_comment(EXPOSE, 'testParameter')
        self.helm_chart_processor.input_artifact.default_config = self.mocked_map

        schema = self.helm_chart_processor.input_artifact.get_schema()
        defaults = self.helm_chart_processor.input_artifact.get_defaults()

        output_mappings = self.helm_chart_processor.generate_values_mappings(schema, defaults)
        expected_mappings = {
            "testParameter": "{deployParameters.test-generate-mappings-cnf.testParameter}",
        }
        self.assertEqual(output_mappings, expected_mappings)
