# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from azext_aosm.custom import build_definition, generate_definition_config

mock_vnf_folder = ((Path(__file__).parent) / "mock_vnf").resolve()


class TestVNF(unittest.TestCase):
    def test_generate_config(self):
        """
        Test generating a config file for a VNF.
        """
        starting_directory = os.getcwd()
        with TemporaryDirectory() as test_dir:
            os.chdir(test_dir)

            try:
                generate_definition_config("vnf")
                assert os.path.exists("input.json")
            finally:
                os.chdir(starting_directory)

    def test_build(self):
        """
        Test building an NFDV for a VNF.
        """
        starting_directory = os.getcwd()
        with TemporaryDirectory() as test_dir:
            os.chdir(test_dir)

            try:
                build_definition("vnf", str(mock_vnf_folder / "input_with_fp.json"))
                assert os.path.exists("nfd-bicep-ubuntu-template")
            finally:
                os.chdir(starting_directory)
                
        with TemporaryDirectory() as test_dir:
            os.chdir(test_dir)

            try:
                build_definition("vnf", str(mock_vnf_folder / "input_with_sas.json"))
                assert os.path.exists("nfd-bicep-ubuntu-template")
            finally:
                os.chdir(starting_directory)

    def test_build_with_ordered_params(self):
        """
        Test building an NFDV for a VNF.
        """
        starting_directory = os.getcwd()
        with TemporaryDirectory() as test_dir:
            os.chdir(test_dir)

            try:
                build_definition(
                    "vnf",
                    str(mock_vnf_folder / "input_with_fp.json"),
                    order_params=True,
                )
                assert os.path.exists("nfd-bicep-ubuntu-template")
            finally:
                os.chdir(starting_directory)
