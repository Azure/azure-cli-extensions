# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Integration tests for the vnf definition type commands in the aosm extension.
They test the following commands:
    aosm nfd build
    aosm nfd publish
    aosm nsd build
    aosm nsd publish
"""

import os
import logging
import sys
import shutil
from tempfile import TemporaryDirectory

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer, live_only
from knack.log import get_logger
from azext_aosm.tests.latest.integration_tests.scenario_tests.recording_processors import (
    TokenReplacer,
    SasUriReplacer,
    BlobStoreUriReplacer,
    UsernameReplacer,
)
from azext_aosm.tests.latest.integration_tests.utils import (
    update_input_file,
    get_path_to_vnf_mocks,
)

logger = get_logger(__name__)

# We use the TEMPLATE files as a jinja2 templates to populate some input parameters at runtime.
NFD_INPUT_TEMPLATE_NAME = "vnf_input_template.jsonc"
NFD_INPUT_FILE_NAME = "vnf_input.jsonc"
NSD_INPUT_TEMPLATE_NAME = "vnf_nsd_input_template.jsonc"
NSD_INPUT_FILE_NAME = "nsd_input.jsonc"
ARM_TEMPLATE_NAME = "ubuntu_template.json"
VHD_NAME = "ubuntu.vhd"


class VnfNsdTest(ScenarioTest):
    """This class contains the integration tests for the aosm extension for vnf definition type."""

    def __init__(self, method_name):
        """
        This constructor initializes the class
        :param method_name: The name of the test method.
        :param recording_processors: The recording processors to use for the test.
        These recording processors modify the recording of a test before it is saved,
        helping to remove sensitive information from the recording.
        """
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        super().__init__(
            method_name,
            recording_processors=[
                TokenReplacer(),
                SasUriReplacer(),
                BlobStoreUriReplacer(),
                UsernameReplacer(),
            ],
        )

    @ResourceGroupPreparer(name_prefix="cli_test_vnf_nsd_", location="uksouth")
    @live_only()  # to avoid 'CannotOverwriteExistingCassetteException' when run from recording
    def test_vnf_nsd_build_and_publish(self, resource_group):
        """
        This test creates a vnf nfd and nsd, publishes them.
        The resource group is created by the ResourceGroupPreparer decorator
        and is deleted at the end of the live test.

        :param resource_group: The name of the resource group to use for the test.
        This is passed in by the ResourceGroupPreparer decorator.
        """
        starting_directory = os.getcwd()

        vnf_mocks_dir = get_path_to_vnf_mocks()

        arm_template_path = os.path.join(vnf_mocks_dir, ARM_TEMPLATE_NAME)

        vhd_path = os.path.join(vnf_mocks_dir, VHD_NAME)

        with TemporaryDirectory() as test_dir:
            os.chdir(test_dir)

            try:
                # For ORAS push to work, we need the arm template to be in the
                # current working directory.
                arm_template_in_temp_dir = os.path.join(test_dir, ARM_TEMPLATE_NAME)

                shutil.copy(arm_template_path, arm_template_in_temp_dir)

                nfd_input_file_path = os.path.join(test_dir, NFD_INPUT_FILE_NAME)

                update_input_file(
                    NFD_INPUT_TEMPLATE_NAME,
                    nfd_input_file_path,
                    params={
                        "publisher_resource_group_name": resource_group,
                        "arm_template_path": arm_template_in_temp_dir,
                        "vhd_path": vhd_path,
                    },
                )

                self.cmd(
                    f'az aosm nfd build --config-file "{nfd_input_file_path}" --definition-type vnf'
                )

                self.cmd(
                    "az aosm nfd publish --build-output-folder vnf-cli-output --definition-type vnf"
                )

                nsd_input_file_path = os.path.join(test_dir, NSD_INPUT_FILE_NAME)
                update_input_file(
                    NSD_INPUT_TEMPLATE_NAME,
                    nsd_input_file_path,
                    params={"publisher_resource_group_name": resource_group},
                )

                self.cmd(f'az aosm nsd build -f "{nsd_input_file_path}"')

                self.cmd("az aosm nsd publish --build-output-folder nsd-cli-output")
            finally:
                os.chdir(starting_directory)
