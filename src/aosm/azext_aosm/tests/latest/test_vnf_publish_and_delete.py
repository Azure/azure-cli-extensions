from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from knack.log import get_logger
import os
from jinja2 import Template
from typing import Any, Dict


logger = get_logger(__name__)

NFD_INPUT_TEMPLATE_NAME = "vnf_input_template.json"
NFD_INPUT_FILE_NAME = "vnf_input.json"
NSD_INPUT_TEMPLATE_NAME = "vnf_nsd_input_template.json"
NSD_INPUT_FILE_NAME = "nsd_input.json"
ARM_TEMPLATE_RELATIVE_PATH = "scenario_test_mocks/vnf_mocks/ubuntu_template.json"


def update_resource_group_in_input_file(
    input_template_name: str, output_file_name: str, resource_group: str
) -> str:
    code_dir = os.path.dirname(__file__)
    templates_dir = os.path.join(
        code_dir, "scenario_test_mocks", "mock_input_templates"
    )
    input_template_path = os.path.join(templates_dir, input_template_name)

    with open(input_template_path, "r", encoding="utf-8") as file:
        contents = file.read()

    jinja_template = Template(contents)

    rendered_template = jinja_template.render(
        publisher_resource_group_name=resource_group
    )

    output_path = os.path.join(templates_dir, output_file_name)

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(rendered_template)

    return output_path


class VnfNsdTest(ScenarioTest):
    @ResourceGroupPreparer()
    def test_vnf_nsd_publish_and_delete(self, resource_group):
        # We are overriding a resource group name here because we need to have some 
        # resources predeployed in order to get around the timeout bug in the testing framework.
        resource_group = "patrykkulik-test"

        nfd_input_file_path = update_resource_group_in_input_file(
            NFD_INPUT_TEMPLATE_NAME, NFD_INPUT_FILE_NAME, resource_group
        )

        self.cmd(
            f'az aosm nfd build -f "{nfd_input_file_path}" --definition-type vnf --force'
        )

        self.cmd(
            f'az aosm nfd publish -f "{nfd_input_file_path}" --definition-type vnf --debug'
        )

        nsd_input_file_path = update_resource_group_in_input_file(
            NSD_INPUT_TEMPLATE_NAME, NSD_INPUT_FILE_NAME, resource_group
        )

        self.cmd(f'az aosm nsd build -f "{nsd_input_file_path}" --debug --force')
        self.cmd(f'az aosm nsd publish -f "{nsd_input_file_path}" --debug')

        self.cmd(
            f'az aosm nfd delete --definition-type vnf -f "{nfd_input_file_path}" --debug --force'
        )
        self.cmd(f'az aosm nsd delete -f "{nsd_input_file_path}" --debug --force')
