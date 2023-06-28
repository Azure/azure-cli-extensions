# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
from unittest.mock import Mock, patch
from tempfile import TemporaryDirectory

from azext_aosm.custom import build_definition

mock_vnf_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mock_vnf")

class TestVNF():
    def test_build(self):
        starting_directory = os.getcwd()
        with TemporaryDirectory() as test_dir:
            os.chdir(test_dir)
            
            try:
                build_definition("vnf", os.path.join(mock_vnf_folder, "input.json"))
                assert os.path.exists("nfd-bicep-ubuntu-template")
            except:
                os.chdir(starting_directory)
