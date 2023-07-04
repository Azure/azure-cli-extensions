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
from azext_aosm.custom import build_definition, generate_definition_config

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


class TestCNF(unittest.TestCase):
    def test_generate_config(self):
        """
        Test generating a config file for a VNF.
        """
        starting_directory = os.getcwd()
        with TemporaryDirectory() as test_dir:
            os.chdir(test_dir)

            try:
                generate_definition_config("cnf")
                assert os.path.exists("input.json")
            finally:
                os.chdir(starting_directory)

    def test_build(self):
        """
        Test the build command for CNFs.
        """
        starting_directory = os.getcwd()
        with TemporaryDirectory() as test_dir:
            os.chdir(test_dir)

            try:
                build_definition(
                    "cnf",
                    os.path.join(mock_cnf_folder, "input-nfconfigchart.json")
                )
                assert os.path.exists("nfd-bicep-nginx-basic-test")
            finally:
                os.chdir(starting_directory)

    def test_build_no_mapping(self):
        """
        Test the build command for CNFs where no mapping file is supplied.

        Also reorder the parameters.
        """
        starting_directory = os.getcwd()
        with TemporaryDirectory() as test_dir:
            os.chdir(test_dir)

            try:
                build_definition(
                    "cnf",
                    os.path.join(mock_cnf_folder, "input-nf-agent-cnf.json"),
                    order_params=True
                )
                assert os.path.exists("nfd-bicep-nf-agent-cnf")
            finally:
                os.chdir(starting_directory)
