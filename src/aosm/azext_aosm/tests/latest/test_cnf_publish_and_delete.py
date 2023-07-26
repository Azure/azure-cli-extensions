from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from knack.log import get_logger
import os
from jinja2 import Template
from typing import Dict


logger = get_logger(__name__)

NFD_INPUT_TEMPLATE_NAME = "cnf_input_template.json"
NFD_INPUT_FILE_NAME = "cnf_input.json"
NSD_INPUT_TEMPLATE_NAME = "nsd_cnf_input_template.json"
NSD_INPUT_FILE_NAME = "input_nsd_cnf.json"
CHART_NAME = "nginxdemo-0.1.0.tgz"

def get_path_to_chart():
    code_dir = os.path.dirname(__file__)
    templates_dir = os.path.join(code_dir, "scenario_test_mocks", "cnf_mocks")
    chart_path = os.path.join(templates_dir, CHART_NAME)
    return chart_path

def update_input_file(input_template_name, output_file_name, params: Dict[str, str]):
    code_dir = os.path.dirname(__file__)
    templates_dir = os.path.join(code_dir, "scenario_test_mocks", "mock_input_templates")
    input_template_path = os.path.join(templates_dir, input_template_name)

    with open(input_template_path, "r", encoding="utf-8") as file:
        contents = file.read()
    
    jinja_template = Template(contents)

    rendered_template = jinja_template.render(**params)

    output_path = os.path.join(templates_dir, output_file_name)

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(rendered_template)

    return output_path


class CnfNsdTest(ScenarioTest):
    @ResourceGroupPreparer()
    def test_cnf_nsd_publish_and_delete(self, resource_group):
        # TODO: should be using a temporary resource group
        resource_group = "patrykkulik-test"

        chart_path = get_path_to_chart()

        nfd_input_file_path = update_input_file(NFD_INPUT_TEMPLATE_NAME, NFD_INPUT_FILE_NAME, params={"publisher_resource_group_name": resource_group, "path_to_chart": chart_path})

        self.cmd(f'az aosm nfd build -f "{nfd_input_file_path}" --definition-type cnf --force')
                
        self.cmd(f'az aosm nfd publish -f "{nfd_input_file_path}" --definition-type cnf --debug')

        # TODO: should I run gets on things to make sure they exist?
    
        nsd_input_file_path = update_input_file(NSD_INPUT_TEMPLATE_NAME, NSD_INPUT_FILE_NAME, params={"publisher_resource_group_name": resource_group})

        self.cmd(f'az aosm nsd build -f "{nsd_input_file_path}" --debug --force')
        self.cmd(f'az aosm nsd publish -f "{nsd_input_file_path}" --debug')
    

        self.cmd(f'az aosm nfd delete --definition-type cnf -f "{nfd_input_file_path}" --debug --force')
        self.cmd(f'az aosm nsd delete -f "{nsd_input_file_path}" --debug --force')

