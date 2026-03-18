# # --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Integration tests for the cnf definition type commands in the aosm extension.
They test the following commands:
    aosm nfd build
    aosm nfd publish
"""
# We are only testing the nfd and not the nsd commands here. This is because the nsd commands
# are tested in the vnf tests and the nsd code path is the same for both vnf and cnf.

import os
import logging
import sys
import shutil
import unittest.mock as mock
from tempfile import TemporaryDirectory

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer, live_only
from knack.log import get_logger
from azext_aosm.tests.latest.integration_tests.utils import (
    mock_in_unit_test,
    update_input_file,
    get_path_to_test_chart,
    get_cgv_path
)
from azext_aosm.tests.latest.integration_tests.scenario_tests.recording_processors import (
    TokenReplacer,
    SasUriReplacer,
    BlobStoreUriReplacer,
    UsernameReplacer,
)

logger = get_logger(__name__)

# We use the TEMPLATE file as a jinja2 template to populate some input parameters at runtime.
NFD_INPUT_TEMPLATE_NAME = "cnf_input_template.jsonc"
NFD_INPUT_FILE_NAME = "cnf_input.jsonc"
NSD_INPUT_TEMPLATE_NAME = "cnf_nsd_input_template.jsonc"
NSD_INPUT_FILE_NAME = "cnf_nsd_input.jsonc"
SNS_INPUT_TEMPLATE_NAME = "cnf_sns_input_template.jsonc"
SNS_INPUT_FILE_NAME = "cnf_sns_input.jsonc"

def patch_call_subprocess_raise_output(unit_test):
    """Patch the call_subprocess_raise_output function to return a valid mocked output."""

    # call_subprocess_raise_output uses subprocess.run to call a command and return the output.
    # Subprocess is not recorded by the python vcr which means that in the playback we are
    # actually trying to run commands like logging into ACRs, which will fail. To avoid this
    # we mock the call_subprocess_raise_output function to return a valid mocked output.
    def _mock_call_subprocess_raise_output(
        *args, **kwargs
    ):  # pylint: disable=unused-argument
        mocked_output = "Valid mocked output"
        mocked_call_subprocess_raise_output = mock.Mock(return_value=mocked_output)
        return mocked_call_subprocess_raise_output

    # Mock this function in all relevant files
    mock_in_unit_test(
        unit_test,
        "azext_aosm.common.artifact.call_subprocess_raise_output",
        _mock_call_subprocess_raise_output,
    )

    mock_in_unit_test(
        unit_test,
        "azext_aosm.common.registry.call_subprocess_raise_output",
        _mock_call_subprocess_raise_output,
    )

    mock_in_unit_test(
        unit_test,
        "azext_aosm.common.utils.call_subprocess_raise_output",
        _mock_call_subprocess_raise_output,
    )


class CnfNfdTest(ScenarioTest):
    """
    Integration tests for the aosm extension for cnf definition type.

    This test uses Live Scenario Test because it depends on using the `az login` command
    which does not work when playing back from the recording.
    """

    def __init__(self, method_name):
        """
        This constructor initializes the class
        :param method_name: The name of the test method.
        :param recording_processors: The recording processors to use for the test.
        These recording processors modify the recording of a test before it is saved,
        helping to remove sensitive information from the recording.
        :param replay_patches: The patches to apply when replaying the test.
        These patches modify the test to use mocked functions instead of making live calls.
        They will not be applied in live tests.
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
            replay_patches=[patch_call_subprocess_raise_output],
        )

    @ResourceGroupPreparer(name_prefix="cli_test_cnf_nfd_", location="uksouth")
    @live_only()  # to avoid 'CannotOverwriteExistingCassetteException' when run from recording
    def test_cnf_nfd_build_and_publish(self, resource_group):
        """
        This test builds a cnf nfd output folder and publishes it.
        The resource group used is created by the ResourceGroupPreparer decorator
        and is deleted at the end of the live test.

        :param resource_group: The name of the resource group to use for the test.
        This is passed in by the ResourceGroupPreparer decorator.
        """
        starting_directory = os.getcwd()

        with TemporaryDirectory() as test_dir:
            os.chdir(test_dir)

            try:
                chart_path = get_path_to_test_chart()

                nfd_input_file_path = os.path.join(test_dir, NFD_INPUT_FILE_NAME)

                update_input_file(
                    NFD_INPUT_TEMPLATE_NAME,
                    nfd_input_file_path,
                    params={
                        "publisher_resource_group_name": resource_group,
                        "path_to_chart": chart_path,
                    },
                )

                self.cmd(
                    f'az aosm nfd build -f "{nfd_input_file_path}" --definition-type cnf'
                )

                self.cmd("az aosm nfd publish -b cnf-cli-output --definition-type cnf")

                nsd_input_file_path = os.path.join(test_dir, NSD_INPUT_FILE_NAME)
                update_input_file(
                    NSD_INPUT_TEMPLATE_NAME,
                    nsd_input_file_path,
                    params={"publisher_resource_group_name": resource_group},
                )

                self.cmd(f'az aosm nsd build -f "{nsd_input_file_path}"')

                self.cmd("az aosm nsd publish --build-output-folder nsd-cli-output")                
                
                sns_input_file_path = os.path.join(test_dir, SNS_INPUT_FILE_NAME)
                update_input_file(
                    SNS_INPUT_TEMPLATE_NAME,
                    sns_input_file_path,
                    params={"publisher_resource_group_name": resource_group},
                )

                self.cmd(f'az aosm sns build -f "{sns_input_file_path}"')
                cgv_file = get_cgv_path()               
                shutil.copy(cgv_file, "sns-cli-output")
                self.cmd("az aosm sns deploy --build-output-folder sns-cli-output")                                
            finally:
                os.chdir(starting_directory)
