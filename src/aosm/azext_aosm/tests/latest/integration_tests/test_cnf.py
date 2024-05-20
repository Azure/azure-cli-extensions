# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest
import json
import os
from tempfile import TemporaryDirectory

from azext_aosm.custom import (
    onboard_nfd_generate_config,
    onboard_nfd_build,
)

from azext_aosm.tests.latest.integration_tests.utils import (
    update_input_file,
    get_path_to_test_chart,
)

# We use the TEMPLATE file as a jinja2 template to populate some input parameters at runtime.
INPUT_TEMPLATE_NAME = "cnf_input_template.jsonc"
INPUT_FILE_NAME = "cnf_input.jsonc"


class TestCNF(unittest.TestCase):
    def test_generate_config(self):
        """Test generating a config file for a VNF."""
        starting_directory = os.getcwd()
        with TemporaryDirectory() as test_dir:
            os.chdir(test_dir)
            output_file_path = os.path.join(test_dir, "cnf_input.jsonc")

            try:
                onboard_nfd_generate_config(
                    definition_type="cnf",
                    output_file=os.path.join(test_dir, output_file_path),
                )
                assert os.path.exists(output_file_path)
            finally:
                os.chdir(starting_directory)

    def test_build(self):
        """Test the build command for CNFs."""
        starting_directory = os.getcwd()

        chart_path = get_path_to_test_chart()

        with TemporaryDirectory() as test_dir:
            os.chdir(test_dir)

            try:
                cnf_input_file_path = os.path.join(test_dir, INPUT_FILE_NAME)

                update_input_file(
                    INPUT_TEMPLATE_NAME,
                    cnf_input_file_path,
                    params={
                        "publisher_resource_group_name": "cli_test_cnf_nfd",
                        "path_to_chart": chart_path,
                    },
                )

                onboard_nfd_build("cnf", cnf_input_file_path)
                assert os.path.exists("cnf-cli-output")

                assert os.path.exists("cnf-cli-output/all_deploy.parameters.json")

                expected_deploy_params = {
                    "location": "uksouth",
                    "publisherName": "automated-cli-test-nginx-publisher",
                    "publisherResourceGroupName": "cli_test_cnf_nfd",
                    "acrArtifactStoreName": "nginx-acr",
                    "acrManifestName": "nginx-acr-manifest-1-0-0",
                    "nfDefinitionGroup": "nginx",
                    "nfDefinitionVersion": "1.0.0",
                }
                with open(
                    "cnf-cli-output/all_deploy.parameters.json"
                ) as allDeployParametersFile:
                    params = json.load(allDeployParametersFile)
                    assert params == expected_deploy_params
            finally:
                os.chdir(starting_directory)
