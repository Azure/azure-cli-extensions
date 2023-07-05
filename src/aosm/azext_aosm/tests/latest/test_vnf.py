# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
from tempfile import TemporaryDirectory

from azext_aosm.custom import build_definition, generate_definition_config

mock_vnf_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mock_vnf")


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
                build_definition("vnf", os.path.join(mock_vnf_folder, "input.json"))
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
                    os.path.join(mock_vnf_folder, "input.json"),
                    order_params=True,
                )
                assert os.path.exists("nfd-bicep-ubuntu-template")
            finally:
                os.chdir(starting_directory)
