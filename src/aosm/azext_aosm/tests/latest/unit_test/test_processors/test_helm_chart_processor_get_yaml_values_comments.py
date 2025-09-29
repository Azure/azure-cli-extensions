
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
from pathlib import Path
from unittest import TestCase
from ruamel.yaml import CommentedMap, CommentedSeq
from azext_aosm.common.constants import EXPOSE, HARDCODE
from azext_aosm.build_processors.helm_chart_processor import HelmChartProcessor
from azext_aosm.inputs.helm_chart_input import HelmChartInput

code_directory = os.path.dirname(__file__)
parent_directory = os.path.abspath(os.path.join(code_directory, "../.."))
helm_charts_directory = os.path.join(parent_directory, "mock_cnf", "helm-charts")
MOCK_NF_AGENT_HELM_CHART = os.path.join(helm_charts_directory, "nf-agent-cnf-0.1.0.tgz")

VALID_CHART_NAME = "nf-agent-cnf"
INVALID_VALUES_CHART_NAME = "nf-agent-cnf-invalid-values"
INVALID_NO_VALUES_CHART_NAME = "nf-agent-cnf-no-values"


class TestGetYamlValuesAndCommentsInteger(TestCase):
    def setUp(self):
        input_artifact = HelmChartInput(
            artifact_name='test-helm-chart',
            artifact_version='1.0.0',
            chart_path=Path(MOCK_NF_AGENT_HELM_CHART),
        )
        self.helm_chart_processor = HelmChartProcessor(
            name="test-generate-schema-cnf",
            input_artifact=input_artifact,
            registry_handler=None,
            expose_all_params=False
        )
        self.mocked_yaml = CommentedMap()
        self.mocked_yaml['testParameter'] = 1

    def test_integer_no_comment(self):
        output_object = self.helm_chart_processor._get_yaml_values_and_comments(self.mocked_yaml)
        expected_object = {'testParameter': {'value': 1, 'comment': None}}
        self.assertEqual(output_object, expected_object)

    def test_integer_expose_cgs(self):
        self.mocked_yaml.yaml_add_eol_comment(EXPOSE, 'testParameter')

        output_object = self.helm_chart_processor._get_yaml_values_and_comments(self.mocked_yaml)
        expected_object = {'testParameter': {'value': 1, 'comment': 'expose-cgs'}}
        self.assertEqual(output_object, expected_object)

    def test_integer_hardcode_nfdv(self):
        self.mocked_yaml.yaml_add_eol_comment(HARDCODE, 'testParameter')

        output_object = self.helm_chart_processor._get_yaml_values_and_comments(self.mocked_yaml)
        expected_object = {'testParameter': {'value': 1, 'comment': 'hardcode-nfdv'}}
        self.assertEqual(output_object, expected_object)

    def test_integer_both_comments(self):
        self.mocked_yaml.yaml_add_eol_comment(f"{HARDCODE} {EXPOSE}", 'testParameter')

        output_object = self.helm_chart_processor._get_yaml_values_and_comments(self.mocked_yaml)
        # We expect None, if you have both comments, we ignore them
        expected_object = {'testParameter': {'value': 1, 'comment': None}}
        self.assertEqual(output_object, expected_object)


class TestGetYamlValuesAndCommentsObject(TestCase):
    def setUp(self):
        input_artifact = HelmChartInput(
            artifact_name='test-helm-chart',
            artifact_version='1.0.0',
            chart_path=Path(MOCK_NF_AGENT_HELM_CHART),
        )
        self.helm_chart_processor = HelmChartProcessor(
            name="test-generate-schema-cnf",
            input_artifact=input_artifact,
            registry_handler=None,
            expose_all_params=False
        )
        self.mocked_yaml = CommentedMap()
        self.mocked_yaml_object = CommentedMap()
        self.mocked_yaml_object['object1'] = "object1"
        self.mocked_yaml_object['object2'] = "object2"
        self.mocked_yaml['testParameter'] = self.mocked_yaml_object

    def test_object_no_comment(self):
        output_object = self.helm_chart_processor._get_yaml_values_and_comments(self.mocked_yaml)
        expected_object = {
            'testParameter': {
                'comment': None,
                'value': {
                    'object1': {'comment': None, 'value': 'object1'},
                    'object2': {'comment': None, 'value': 'object2'}
                }
            }
        }
        self.assertEqual(output_object, expected_object)

    def test_object_expose_cgs(self):
        self.mocked_yaml.yaml_add_eol_comment(EXPOSE, 'testParameter')
        output_object = self.helm_chart_processor._get_yaml_values_and_comments(self.mocked_yaml)
        expected_object = {
            'testParameter': {
                'comment': 'expose-cgs',
                'value': {
                    'object1': {'comment': None, 'value': 'object1'},
                    'object2': {'comment': None, 'value': 'object2'}
                }
            }
        }
        self.assertEqual(output_object, expected_object)

    def test_object_hardcode_nfdv(self):
        self.mocked_yaml.yaml_add_eol_comment(HARDCODE, 'testParameter')
        output_object = self.helm_chart_processor._get_yaml_values_and_comments(self.mocked_yaml)
        expected_object = {
            'testParameter': {
                'comment': 'hardcode-nfdv',
                'value': {
                    'object1': {'comment': None, 'value': 'object1'},
                    'object2': {'comment': None, 'value': 'object2'}
                }
            }
        }
        self.assertEqual(output_object, expected_object)

    def test_object_both_comments(self):
        self.mocked_yaml.yaml_add_eol_comment(f"{HARDCODE} {EXPOSE}", 'testParameter')
        output_object = self.helm_chart_processor._get_yaml_values_and_comments(self.mocked_yaml)
        # We expect None, if you have both comments, we ignore them
        expected_object = {
            'testParameter': {
                'comment': None,
                'value': {
                    'object1': {'comment': None, 'value': 'object1'},
                    'object2': {'comment': None, 'value': 'object2'}
                }
            }
        }
        self.assertEqual(output_object, expected_object)

    def test_object_item_expose_cgs(self):
        self.mocked_yaml_object.yaml_add_eol_comment(EXPOSE, 'object1')
        self.mocked_yaml['testParameter'] = self.mocked_yaml_object
        output_object = self.helm_chart_processor._get_yaml_values_and_comments(self.mocked_yaml)
        expected_object = {
            'testParameter': {
                'comment': None,
                'value': {
                    'object1': {'comment': 'expose-cgs', 'value': 'object1'},
                    'object2': {'comment': None, 'value': 'object2'}
                }
            }
        }
        self.assertEqual(output_object, expected_object)

    def test_object_item_hardcode_nfdv(self):
        self.mocked_yaml_object.yaml_add_eol_comment(HARDCODE, 'object2')
        self.mocked_yaml['testParameter'] = self.mocked_yaml_object
        output_object = self.helm_chart_processor._get_yaml_values_and_comments(self.mocked_yaml)
        expected_object = {
            'testParameter': {
                'comment': None,
                'value': {
                    'object1': {'comment': None, 'value': 'object1'},
                    'object2': {'comment': 'hardcode-nfdv', 'value': 'object2'}
                }
            }
        }
        self.assertEqual(output_object, expected_object)

    def test_object_item_both_comments(self):
        self.mocked_yaml_object.yaml_add_eol_comment(f"{HARDCODE} {EXPOSE}", 'object2')
        self.mocked_yaml['testParameter'] = self.mocked_yaml_object
        output_object = self.helm_chart_processor._get_yaml_values_and_comments(self.mocked_yaml)
        # We expect None, if you have both comments, we ignore them
        expected_object = {
            'testParameter': {
                'comment': None,
                'value': {
                    'object1': {'comment': None, 'value': 'object1'},
                    'object2': {'comment': None, 'value': 'object2'}
                }
            }
        }
        self.assertEqual(output_object, expected_object)


class TestGetYamlValuesAndCommentsArray(TestCase):
    def setUp(self):
        """
        This mock looks like:
        testParameter:
        - item1object1: 1
          item1object2: "test1"
        - item2object1: 2
          item2object2: "test2"
        """
        input_artifact = HelmChartInput(
            artifact_name='test-helm-chart',
            artifact_version='1.0.0',
            chart_path=Path(MOCK_NF_AGENT_HELM_CHART),
        )
        self.helm_chart_processor = HelmChartProcessor(
            name="test-generate-schema-cnf",
            input_artifact=input_artifact,
            registry_handler=None,
            expose_all_params=False
        )
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
        output_object = self.helm_chart_processor._get_yaml_values_and_comments(self.mocked_map)
        expected_object = {
            "testParameter": {
                "value": [
                    {
                        "value": {
                            "item1object1": {
                                "value": 1,
                                "comment": None
                            },
                            "item1object2": {
                                "value": "test1",
                                "comment": None
                            }
                        },
                        "comment": None
                    },
                    {
                        "value": {
                            "item2object1": {
                                "value": 2,
                                "comment": None
                            },
                            "item2object2": {
                                "value": "test2",
                                "comment": None
                            }
                        },
                        "comment": None
                    }
                ],
                "comment": None
            }
        }
        self.assertEqual(output_object, expected_object)

    def test_array_expose_cgs(self):
        self.mocked_map.yaml_add_eol_comment(EXPOSE, 'testParameter')
        output_object = self.helm_chart_processor._get_yaml_values_and_comments(self.mocked_map)
        expected_object = {
            "testParameter": {
                "value": [
                    {
                        "value": {
                            "item1object1": {
                                "value": 1,
                                "comment": None
                            },
                            "item1object2": {
                                "value": "test1",
                                "comment": None
                            }
                        },
                        "comment": None
                    },
                    {
                        "value": {
                            "item2object1": {
                                "value": 2,
                                "comment": None
                            },
                            "item2object2": {
                                "value": "test2",
                                "comment": None
                            }
                        },
                        "comment": None
                    }
                ],
                "comment": 'expose-cgs'
            }
        }
        self.assertEqual(output_object, expected_object)

    def test_array_hardcode_nfdv(self):
        self.mocked_map.yaml_add_eol_comment(HARDCODE, 'testParameter')
        output_object = self.helm_chart_processor._get_yaml_values_and_comments(self.mocked_map)
        expected_object = {
            "testParameter": {
                "value": [
                    {
                        "value": {
                            "item1object1": {
                                "value": 1,
                                "comment": None
                            },
                            "item1object2": {
                                "value": "test1",
                                "comment": None
                            }
                        },
                        "comment": None
                    },
                    {
                        "value": {
                            "item2object1": {
                                "value": 2,
                                "comment": None
                            },
                            "item2object2": {
                                "value": "test2",
                                "comment": None
                            }
                        },
                        "comment": None
                    }
                ],
                "comment": 'hardcode-nfdv'
            }
        }
        self.assertEqual(output_object, expected_object)

    def test_array_both_comments(self):
        self.mocked_map.yaml_add_eol_comment(f"{HARDCODE} {EXPOSE}", 'testParameter')
        output_object = self.helm_chart_processor._get_yaml_values_and_comments(self.mocked_map)
        # We expect None, if you have both comments, we ignore them
        expected_object = {
            "testParameter": {
                "value": [
                    {
                        "value": {
                            "item1object1": {
                                "value": 1,
                                "comment": None
                            },
                            "item1object2": {
                                "value": "test1",
                                "comment": None
                            }
                        },
                        "comment": None
                    },
                    {
                        "value": {
                            "item2object1": {
                                "value": 2,
                                "comment": None
                            },
                            "item2object2": {
                                "value": "test2",
                                "comment": None
                            }
                        },
                        "comment": None
                    }
                ],
                "comment": None
            }
        }
        self.assertEqual(output_object, expected_object)

    def test_array_item_expose_cgs(self):
        self.mocked_map['testParameter'][0].yaml_add_eol_comment(EXPOSE, 'item1object1')
        output_object = self.helm_chart_processor._get_yaml_values_and_comments(self.mocked_map)
        expected_object = {
            "testParameter": {
                "value": [
                    {
                        "value": {
                            "item1object1": {
                                "value": 1,
                                "comment": "expose-cgs"
                            },
                            "item1object2": {
                                "value": "test1",
                                "comment": None
                            }
                        },
                        "comment": None
                    },
                    {
                        "value": {
                            "item2object1": {
                                "value": 2,
                                "comment": None
                            },
                            "item2object2": {
                                "value": "test2",
                                "comment": None
                            }
                        },
                        "comment": None
                    }
                ],
                "comment": None
            }
        }
        self.assertEqual(output_object, expected_object)

    def test_array_item_hardcode_nfdv(self):
        self.mocked_map['testParameter'][1].yaml_add_eol_comment(HARDCODE, 'item2object1')
        output_object = self.helm_chart_processor._get_yaml_values_and_comments(self.mocked_map)
        expected_object = {
            "testParameter": {
                "value": [
                    {
                        "value": {
                            "item1object1": {
                                "value": 1,
                                "comment": None
                            },
                            "item1object2": {
                                "value": "test1",
                                "comment": None
                            }
                        },
                        "comment": None
                    },
                    {
                        "value": {
                            "item2object1": {
                                "value": 2,
                                "comment": 'hardcode-nfdv'
                            },
                            "item2object2": {
                                "value": "test2",
                                "comment": None
                            }
                        },
                        "comment": None
                    }
                ],
                "comment": None
            }
        }
        self.assertEqual(output_object, expected_object)

    def test_array_item_both_comments(self):
        self.mocked_map['testParameter'][1].yaml_add_eol_comment(f'{EXPOSE} {HARDCODE}', 'item2object1')
        output_object = self.helm_chart_processor._get_yaml_values_and_comments(self.mocked_map)
        expected_object = {
            "testParameter": {
                "value": [
                    {
                        "value": {
                            "item1object1": {
                                "value": 1,
                                "comment": None
                            },
                            "item1object2": {
                                "value": "test1",
                                "comment": None
                            }
                        },
                        "comment": None
                    },
                    {
                        "value": {
                            "item2object1": {
                                "value": 2,
                                "comment": None
                            },
                            "item2object2": {
                                "value": "test2",
                                "comment": None
                            }
                        },
                        "comment": None
                    }
                ],
                "comment": None
            }
        }
        self.assertEqual(output_object, expected_object)


class TestGetYamlValuesAndCommentsEmptyArray(TestCase):
    def setUp(self):
        input_artifact = HelmChartInput(
            artifact_name='test-helm-chart',
            artifact_version='1.0.0',
            chart_path=Path(MOCK_NF_AGENT_HELM_CHART),
        )
        self.helm_chart_processor = HelmChartProcessor(
            name="test-generate-schema-cnf",
            input_artifact=input_artifact,
            registry_handler=None,
            expose_all_params=False
        )
        self.mocked_yaml = CommentedSeq()
        self.mocked_map = CommentedMap()
        self.mocked_map['testParameter'] = self.mocked_yaml

    def test_array_no_comment(self):
        output_object = self.helm_chart_processor._get_yaml_values_and_comments(self.mocked_map)
        expected_object = {
            "testParameter": {
                "value": [],
                "comment": None
            }
        }
        self.assertEqual(output_object, expected_object)

    def test_array_expose_cgs(self):
        self.mocked_map.yaml_add_eol_comment(EXPOSE, 'testParameter')
        output_object = self.helm_chart_processor._get_yaml_values_and_comments(self.mocked_map)
        expected_object = {
            "testParameter": {
                "value": [],
                "comment": 'expose-cgs'
            }
        }
        self.assertEqual(output_object, expected_object)

    def test_array_hardcode_nfdv(self):
        self.mocked_map.yaml_add_eol_comment(HARDCODE, 'testParameter')
        output_object = self.helm_chart_processor._get_yaml_values_and_comments(self.mocked_map)
        expected_object = {
            "testParameter": {
                "value": [],
                "comment": 'hardcode-nfdv'
            }
        }
        self.assertEqual(output_object, expected_object)

    def test_array_both_comments(self):
        self.mocked_map.yaml_add_eol_comment(f"{HARDCODE} {EXPOSE}", 'testParameter')
        output_object = self.helm_chart_processor._get_yaml_values_and_comments(self.mocked_map)
        # We expect None, if you have both comments, we ignore them
        expected_object = {
            "testParameter": {
                "value": [],
                "comment": None
            }
        }
        self.assertEqual(output_object, expected_object)


class TestGetYamlValuesAndCommentsNestedEmptyArray(TestCase):
    def setUp(self):
        """
        This mock looks like:
        testParameter:
        - item1object1: 1
          item1object2: []
        """
        input_artifact = HelmChartInput(
            artifact_name='test-helm-chart',
            artifact_version='1.0.0',
            chart_path=Path(MOCK_NF_AGENT_HELM_CHART),
        )
        self.helm_chart_processor = HelmChartProcessor(
            name="test-generate-schema-cnf",
            input_artifact=input_artifact,
            registry_handler=None,
            expose_all_params=False
        )
        # Create two CommentedMaps (objects) and add them to the CommentedSeq (list)
        self.mocked_seq = CommentedSeq()
        self.mocked_map1 = CommentedMap()
        self.mocked_map1['item1object1'] = 1
        self.mocked_map1['item1object2'] = CommentedSeq()

        self.mocked_seq.append(self.mocked_map1)

        # Add the CommentedSeq (list) to a CommentedMap (object)
        self.mocked_map = CommentedMap()
        self.mocked_map['testParameter'] = self.mocked_seq

    def test_array_no_comment(self):
        output_object = self.helm_chart_processor._get_yaml_values_and_comments(self.mocked_map)
        expected_object = {
            "testParameter": {
                "value": [
                    {
                        "value": {
                            "item1object1": {
                                "value": 1,
                                "comment": None
                            },
                            "item1object2": {
                                "value": [],
                                "comment": None
                            }
                        },
                        "comment": None
                    }
                ],
                "comment": None
            }
        }
        self.assertEqual(output_object, expected_object)


class TestGetYamlValuesAndCommentsNestedArray(TestCase):
    def setUp(self):
        """
        This mock looks like:
        testParameter:
        - item1object1: 1
          item1object2:
          - nestedObject: 1
        """
        input_artifact = HelmChartInput(
            artifact_name='test-helm-chart',
            artifact_version='1.0.0',
            chart_path=Path(MOCK_NF_AGENT_HELM_CHART),
        )
        self.helm_chart_processor = HelmChartProcessor(
            name="test-generate-schema-cnf",
            input_artifact=input_artifact,
            registry_handler=None,
            expose_all_params=False
        )
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

        # Add the CommentedSeq (list) to a CommentedMap (object)
        self.mocked_map = CommentedMap()
        self.mocked_map['testParameter'] = self.mocked_seq

    def test_nested_array_no_comment(self):
        output_object = self.helm_chart_processor._get_yaml_values_and_comments(self.mocked_map)
        expected_object = {
            "testParameter": {
                "value": [
                    {
                        "value": {
                            "item1object1": {
                                "value": 1,
                                "comment": None
                            },
                            "item1object2": {
                                "value": [
                                    {
                                        "value": {
                                            "nestedobject": {
                                                "value": 2,
                                                "comment": None
                                            }
                                        },
                                        "comment": None
                                    }
                                ],
                                "comment": None
                            }
                        },
                        "comment": None
                    }
                ],
                "comment": None
            }
        }
        self.assertEqual(output_object, expected_object)

    def test_nested_array_hardcode_nfdv(self):
        self.mocked_map['testParameter'][0]["item1object2"][0].yaml_add_eol_comment(HARDCODE, 'nestedobject')
        output_object = self.helm_chart_processor._get_yaml_values_and_comments(self.mocked_map)
        expected_object = {
            "testParameter": {
                "value": [
                    {
                        "value": {
                            "item1object1": {
                                "value": 1,
                                "comment": None
                            },
                            "item1object2": {
                                "value": [
                                    {
                                        "value": {
                                            "nestedobject": {
                                                "value": 2,
                                                "comment": 'hardcode-nfdv'
                                            }
                                        },
                                        "comment": None
                                    }
                                ],
                                "comment": None
                            }
                        },
                        "comment": None
                    }
                ],
                "comment": None
            }
        }
        self.assertEqual(output_object, expected_object)

    def test_nested_array_expose_cgs(self):
        self.mocked_map['testParameter'][0]["item1object2"][0].yaml_add_eol_comment(EXPOSE, 'nestedobject')
        output_object = self.helm_chart_processor._get_yaml_values_and_comments(self.mocked_map)
        expected_object = {
            "testParameter": {
                "value": [
                    {
                        "value": {
                            "item1object1": {
                                "value": 1,
                                "comment": None
                            },
                            "item1object2": {
                                "value": [
                                    {
                                        "value": {
                                            "nestedobject": {
                                                "value": 2,
                                                "comment": 'expose-cgs'
                                            }
                                        },
                                        "comment": None
                                    }
                                ],
                                "comment": None
                            }
                        },
                        "comment": None
                    }
                ],
                "comment": None
            }
        }
        self.assertEqual(output_object, expected_object)
