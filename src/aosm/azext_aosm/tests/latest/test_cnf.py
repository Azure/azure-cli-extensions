# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# import os
import unittest
import json
import logging
# from unittest.mock import Mock, patch

from azext_aosm.generate_nfd.cnf_nfd_generator import CnfNfdGenerator
from azext_aosm._configuration import CNFConfiguration, HelmPackageConfig

from azure.cli.core.azclierror import (
    BadRequestError,
    InvalidArgumentValueError,
    ResourceNotFoundError,
    InvalidTemplateError
)

# Instantiate CNF with faked config file
with open("azext_aosm/tests/latest/mock_cnf/config_file.json", "r", encoding="utf-8") as f:
    config_as_dict = json.loads(f.read())
config = CNFConfiguration(**config_as_dict)
test_cnf = CnfNfdGenerator(config)
invalid_helm_package = test_cnf.config.helm_packages[0]
invalid_helm_package = HelmPackageConfig(**invalid_helm_package)


# pylint: disable=protected-access
class TestExtractChart(unittest.TestCase):
    # Jordan: can we test whether this has extracted correctly in a unit test?
    def test_invalid_chart(self):
        with self.assertRaises(InvalidTemplateError):
            print("TEST", invalid_helm_package)
            test_cnf._extract_chart(invalid_helm_package.path_to_chart)


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
