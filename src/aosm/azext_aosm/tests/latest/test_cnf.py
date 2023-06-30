# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# import os
import unittest
import json
import logging
import os
from tempfile import TemporaryDirectory
# from unittest.mock import Mock, patch

from azext_aosm.generate_nfd.cnf_nfd_generator import CnfNfdGenerator
from azext_aosm._configuration import CNFConfiguration, HelmPackageConfig
from azext_aosm.custom import build_definition

from azure.cli.core.azclierror import (
    BadRequestError,
    InvalidArgumentValueError,
    ResourceNotFoundError,
    InvalidTemplateError
)

mock_cnf_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mock_cnf")
cnf_config_file = os.path.join(mock_cnf_folder, "invalid_config_file.json")

# Instantiate CNF with faked config file
with open(cnf_config_file, "r", encoding="utf-8") as f:
    config_as_dict = json.loads(f.read())
config = CNFConfiguration(config_file=cnf_config_file, **config_as_dict)
test_cnf = CnfNfdGenerator(config)
invalid_helm_package = test_cnf.config.helm_packages[0]


# pylint: disable=protected-access
class TestExtractChart(unittest.TestCase):
    # Jordan: can we test whether this has extracted correctly in a unit test?
    def test_invalid_chart(self):
        with self.assertRaises(InvalidTemplateError):
            print("TEST", invalid_helm_package)
            test_cnf._extract_chart(invalid_helm_package.path_to_chart)


class TestCNF(unittest.TestCase):
    def test_build(self):
        starting_directory = os.getcwd()
        with TemporaryDirectory() as test_dir:
            os.chdir(test_dir)

            try:
                build_definition(
                    "cnf", 
                    os.path.join(mock_cnf_folder, "input-nfconfigchart.json")
                )
                assert os.path.exists("nfd-bicep-ubuntu-template")
            finally:
                os.chdir(starting_directory)


class TestGenerateChartValueMappings(unittest.TestCase):
    # Test for _read_top_level_values_yaml
    # Test for _replace_values_with_deploy_params
    def test_write_mappings_to_file(self):
        pass

    def test_update_path_to_mappings(self):
        pass


class TestGetChartMappingSchema(unittest.TestCase):
    # Test for traverse_dict
    # Test for search_schema
    pass


class TestFindPatternMatchesInChart(unittest.TestCase):
    pass


class TestGenerateNFApplicationConfig(unittest.TestCase):
    pass


class TestGetArtifactList(unittest.TestCase):
    pass


class TestWriteFilesToOutput(unittest.TestCase):
    pass
