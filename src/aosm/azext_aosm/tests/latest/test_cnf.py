# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory

from azext_aosm.custom import build_definition, generate_definition_config


mock_cnf_folder = ((Path(__file__).parent) / "mock_cnf").resolve()


class TestCNF(unittest.TestCase):
    def test_generate_config(self):
        """Test generating a config file for a VNF."""
        starting_directory = os.getcwd()
        with TemporaryDirectory() as test_dir:
            os.chdir(test_dir)

            try:
                generate_definition_config("cnf")
                assert os.path.exists("input.json")
            finally:
                os.chdir(starting_directory)

    def test_build(self):
        """Test the build command for CNFs."""
        starting_directory = os.getcwd()
        with TemporaryDirectory() as test_dir:
            os.chdir(test_dir)

            try:
                build_definition(
                    "cnf", str(mock_cnf_folder / "input-nfconfigchart.json")
                )
                assert os.path.exists("nfd-bicep-nginx-basic-test")
                # Confirm that the generated schema file correctly handles array deployment params.
                assert os.path.exists("nfd-bicep-nginx-basic-test/schemas/deploymentParameters.json")
                with open("nfd-bicep-nginx-basic-test/schemas/deploymentParameters.json") as f:
                    schema = json.load(f)
                    assert schema["properties"]["imagePullSecrets_0"]["type"] == "string"
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
                    str(mock_cnf_folder / "input-nf-agent-cnf.json"),
                    order_params=True,
                )
                assert os.path.exists("nfd-bicep-nf-agent-cnf")
            finally:
                os.chdir(starting_directory)
