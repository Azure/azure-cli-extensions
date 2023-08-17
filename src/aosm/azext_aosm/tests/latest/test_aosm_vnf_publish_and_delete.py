# Commented out because of a bug in the CLI extension that causes the test to timeout.

# # --------------------------------------------------------------------------------------------
# # Copyright (c) Microsoft Corporation. All rights reserved.
# # Licensed under the MIT License. See License.txt in the project root for license information.
# #
# # This is an integration tests for the aosm extension. It tests the following commands for the
# # vnf definition type:
# #   aosm nfd build
# #   aosm nfd publish
# #   aosm nfd delete
# #   aosm nsd build
# #   aosm nsd publish
# #   aosm nsd delete
# # --------------------------------------------------------------------------------------------

# from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
# from knack.log import get_logger
# import os
# from jinja2 import Template
# from .recording_processors import AcrTokenReplacer, SasUriReplacer


# logger = get_logger(__name__)

# NFD_INPUT_TEMPLATE_NAME = "vnf_input_template.json"
# NFD_INPUT_FILE_NAME = "vnf_input.json"
# NSD_INPUT_TEMPLATE_NAME = "vnf_nsd_input_template.json"
# NSD_INPUT_FILE_NAME = "nsd_input.json"
# ARM_TEMPLATE_RELATIVE_PATH = "scenario_test_mocks/vnf_mocks/ubuntu_template.json"


# def update_resource_group_in_input_file(
#     input_template_name: str, output_file_name: str, resource_group: str
# ) -> str:
#     """
#     This function updates the resource group name in the input template file and returns the
#     path to the updated file.

#     :param input_template_name: The name of the input template file.
#     :param output_file_name: The name of the output file.
#     :param resource_group: The name of the resource group to update the input template with.
#     :return: The path to the updated input template file."""
#     code_dir = os.path.dirname(__file__)
#     templates_dir = os.path.join(
#         code_dir, "scenario_test_mocks", "mock_input_templates"
#     )
#     input_template_path = os.path.join(templates_dir, input_template_name)

#     with open(input_template_path, "r", encoding="utf-8") as file:
#         contents = file.read()

#     jinja_template = Template(contents)

#     rendered_template = jinja_template.render(
#         publisher_resource_group_name=resource_group
#     )

#     output_path = os.path.join(templates_dir, output_file_name)

#     with open(output_path, "w", encoding="utf-8") as file:
#         file.write(rendered_template)

#     return output_path


# class VnfNsdTest(ScenarioTest):
#     """
#     This class contains the integration tests for the aosm extension for vnf definition type.
#     """
#     def __init__(self, method_name):
#         """
#         This constructor initializes the class

#         :param method_name: The name of the test method.
#         :param recording_processors: The recording processors to use for the test.
#         These recording processors modify the recording of a test before it is saved,
#         helping to remove sensitive information from the recording.
#         """
#         super(VnfNsdTest, self).__init__(
#             method_name,
#             recording_processors=[AcrTokenReplacer(), SasUriReplacer()]
#         )

#     @ResourceGroupPreparer(name_prefix="cli_test_vnf_nsd_", location="northeurope")
#     def test_vnf_nsd_publish_and_delete(self, resource_group):
#         """
#         This test creates a vnf nfd and nsd, publishes them, and then deletes them.

#         :param resource_group: The name of the resource group to use for the test.
#         This is passed in by the ResourceGroupPreparer decorator.
#         """
#         nfd_input_file_path = update_resource_group_in_input_file(
#             NFD_INPUT_TEMPLATE_NAME, NFD_INPUT_FILE_NAME, resource_group
#         )

#         self.cmd(
#             f'az aosm nfd build -f "{nfd_input_file_path}" --definition-type vnf --force'
#         )

#         # There is currently a bug in the CLI testing framework that causes the command
#         # to fail on timeout. This is a workaround to retry the command if it fails.
#         retry_attempts = 0
#         while retry_attempts < 2:
#             try:
#                 self.cmd(
#                     f'az aosm nfd publish -f "{nfd_input_file_path}" --definition-type vnf'
#                 )
#                 break
#             except Exception:
#                 retry_attempts += 1

#                 if retry_attempts == 2:
#                     # If the command fails twice, then the test should fail.
#                     # We still need to clean up the resources, so we run the delete command.
#                     self.cmd(
#                         f'az aosm nfd delete --definition-type vnf -f "{nfd_input_file_path}" --clean --force'
#                     )
#                     raise

#         nsd_input_file_path = update_resource_group_in_input_file(
#             NSD_INPUT_TEMPLATE_NAME, NSD_INPUT_FILE_NAME, resource_group
#         )

#         self.cmd(f'az aosm nsd build -f "{nsd_input_file_path}" --force')

#         try:
#             self.cmd(f'az aosm nsd publish -f "{nsd_input_file_path}"')
#         finally:
#             # If the command fails, then the test should fail.
#             # We still need to clean up the resources, so we run the delete command.
#             self.cmd(f'az aosm nsd delete -f "{nsd_input_file_path}" --clean --force')
#             self.cmd(
#                 f'az aosm nfd delete --definition-type vnf -f "{nfd_input_file_path}" --clean --force'
#             )
