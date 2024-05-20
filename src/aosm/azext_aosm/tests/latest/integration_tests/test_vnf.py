# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from azext_aosm.custom import onboard_nfd_build, onboard_nfd_generate_config
from azext_aosm.tests.latest.integration_tests.utils import update_input_file
from azext_aosm.common.constants import VNF_OUTPUT_FOLDER_FILENAME

mock_vnf_folder = ((Path(__file__).parent.parent) / "mock_vnf").resolve()

INPUT_WITH_SAS_VHD_PARAMS = {
    "imageDiskSizeGB": 30,
    "imageHyperVGeneration": "V1",
    "apiVersion": "2023-03-01",
    "imageName": "ubuntu-vmImage",
}

# We use the TEMPLATE files as a jinja2 templates to populate some input parameters at runtime.
NFD_INPUT_TEMPLATE_NAME = "vnf_input_template.jsonc"
NFD_INPUT_FILE_NAME = "vnf_input.jsonc"
VNF_INPUT_WITH_SAS_TOKEN_TEMPLATE_NAME = "vnf_input_with_sas_token_template.jsonc"
ARM_TEMPLATE_NAME = "ubuntu_template.json"
VHD_NAME = "ubuntu.vhd"


def get_path_to_vnf_mocks():
    """Get the path to the vnf mocks directory."""
    code_dir = os.path.dirname(__file__)
    vnf_mocks_dir = os.path.join(code_dir, "integration_test_mocks", "vnf_mocks")

    return vnf_mocks_dir


def validate_vhd_parameters(expected_params, vhd_params_file_path):
    """Validate that the expected parameters are in the actual parameters."""
    assert os.path.exists(vhd_params_file_path)
    with open(vhd_params_file_path) as f:
        actual_params = json.load(f)
    assert expected_params == actual_params


class TestVNF(unittest.TestCase):
    def test_generate_config(self):
        """Test generating a config file for a VNF."""
        starting_directory = os.getcwd()
        with TemporaryDirectory() as test_dir:
            os.chdir(test_dir)
            output_file_path = os.path.join(test_dir, "vnf_input.jsonc")

            try:
                onboard_nfd_generate_config(
                    definition_type="vnf",
                    output_file=os.path.join(test_dir, output_file_path),
                )
                assert os.path.exists(output_file_path)
            finally:
                os.chdir(starting_directory)

    def test_build_with_filepath(self):
        """Test building an NFDV for a VNF using a filepath."""
        starting_directory = os.getcwd()
        with TemporaryDirectory() as test_dir:
            os.chdir(test_dir)

            try:
                vnf_mocks_dir = get_path_to_vnf_mocks()

                arm_template_path = os.path.join(vnf_mocks_dir, ARM_TEMPLATE_NAME)
                vhd_path = os.path.join(vnf_mocks_dir, VHD_NAME)

                nfd_input_file_path = os.path.join(test_dir, NFD_INPUT_FILE_NAME)

                update_input_file(
                    NFD_INPUT_TEMPLATE_NAME,
                    nfd_input_file_path,
                    params={
                        "publisher_resource_group_name": "resource_group",
                        "arm_template_path": arm_template_path,
                        "vhd_path": vhd_path,
                    },
                )

                onboard_nfd_build("vnf", nfd_input_file_path)
                assert os.path.exists(VNF_OUTPUT_FOLDER_FILENAME)
            finally:
                os.chdir(starting_directory)

    def test_build_with_sas_token(self):
        """Test building an NFDV for a VNF using a filepath."""
        starting_directory = os.getcwd()
        with TemporaryDirectory() as test_dir:
            os.chdir(test_dir)

            try:
                vnf_mocks_dir = get_path_to_vnf_mocks()

                arm_template_path = os.path.join(vnf_mocks_dir, ARM_TEMPLATE_NAME)

                nfd_input_file_path = os.path.join(test_dir, NFD_INPUT_FILE_NAME)
                update_input_file(
                    VNF_INPUT_WITH_SAS_TOKEN_TEMPLATE_NAME,
                    nfd_input_file_path,
                    params={
                        "publisher_resource_group_name": "resource_group",
                        "arm_template_path": arm_template_path,
                    },
                )

                onboard_nfd_build("vnf", nfd_input_file_path)
                assert os.path.exists(VNF_OUTPUT_FOLDER_FILENAME)
                validate_vhd_parameters(
                    INPUT_WITH_SAS_VHD_PARAMS,
                    f"{VNF_OUTPUT_FOLDER_FILENAME}/nfDefinition/vhdParameters.json",
                )
            finally:
                os.chdir(starting_directory)
