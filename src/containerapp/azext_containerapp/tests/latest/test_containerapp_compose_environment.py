# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import unittest  # pylint: disable=unused-import

from azure.cli.testsdk import (ResourceGroupPreparer)
from azure.cli.testsdk.decorators import serial_test
from azext_containerapp.tests.latest.common import (
    ContainerappComposePreviewScenarioTest,  # pylint: disable=unused-import
    write_test_file,
    clean_up_test_file,
    TEST_DIR, TEST_LOCATION)

from .utils import prepare_containerapp_env_for_app_e2e_tests


class ContainerappComposePreviewEnvironmentSettingsScenarioTest(ContainerappComposePreviewScenarioTest):
    @serial_test()
    @ResourceGroupPreparer(name_prefix='cli_test_containerapp_preview', location='eastus')
    def test_containerapp_compose_create_with_environment(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))
        compose_text = f"""
services:
  foo:
    image: mcr.microsoft.com/azuredocs/aks-helloworld:v1
    environment:
      - RACK_ENV=development
      - SHOW=true
      - BAZ="snafu"
"""
        compose_file_name = f"{self._testMethodName}_compose.yml"
        write_test_file(compose_file_name, compose_text)

        env_id = prepare_containerapp_env_for_app_e2e_tests(self)
        self.kwargs.update({
            'environment': env_id,
            'compose': compose_file_name,
        })

        command_string = 'containerapp compose create'
        command_string += ' --compose-file-path {compose}'
        command_string += ' --resource-group {rg}'
        command_string += ' --environment {environment}'
        self.cmd(command_string, checks=[
            self.check(f'[?name==`foo`].properties.template.containers[0].env[0].name', ["RACK_ENV"]),
            self.check(f'[?name==`foo`].properties.template.containers[0].env[0].value', ["development"]),
            self.check(f'[?name==`foo`].properties.template.containers[0].env[1].name', ["SHOW"]),
            self.check(f'[?name==`foo`].properties.template.containers[0].env[1].value', ["true"]),
            self.check(f'[?name==`foo`].properties.template.containers[0].env[2].name', ["BAZ"]),
            self.check(f'[?name==`foo`].properties.template.containers[0].env[2].value', ['"snafu"'])
        ])

        self.cmd(f'containerapp delete -n foo -g {resource_group} --yes', expect_failure=False)
        clean_up_test_file(compose_file_name)

    @serial_test()
    @ResourceGroupPreparer(name_prefix='cli_test_containerapp_preview', location='eastus')
    def test_containerapp_compose_create_with_unset_env_defaults(self, resource_group):
        """Verify that ${VAR:-default} is expanded to 'default' when VAR is not set in the shell."""
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        # Ensure the test variables are not set in the local shell so we exercise the default branch
        os.environ.pop('COMPOSE_VAR_A', None)
        os.environ.pop('COMPOSE_VAR_B', None)
        os.environ['COMPOSE_VAR_C'] = 'set_value'  # This one IS set; default should be ignored

        compose_text = f"""
services:
  foo:
    image: mcr.microsoft.com/azuredocs/aks-helloworld:v1
    environment:
      COMPOSE_VAR_A: ${{COMPOSE_VAR_A:-default_a}}
      COMPOSE_VAR_B: ${{COMPOSE_VAR_B:-default_b}}
      COMPOSE_VAR_C: ${{COMPOSE_VAR_C:-should_not_appear}}
"""
        compose_file_name = f"{self._testMethodName}_compose.yml"
        write_test_file(compose_file_name, compose_text)

        env_id = prepare_containerapp_env_for_app_e2e_tests(self)
        self.kwargs.update({
            'environment': env_id,
            'compose': compose_file_name,
        })

        command_string = 'containerapp compose create'
        command_string += ' --compose-file-path {compose}'
        command_string += ' --resource-group {rg}'
        command_string += ' --environment {environment}'
        self.cmd(command_string, checks=[
            self.check(f'[?name==`foo`].properties.template.containers[0].env[0].name', ["COMPOSE_VAR_A"]),
            self.check(f'[?name==`foo`].properties.template.containers[0].env[0].value', ["default_a"]),
            self.check(f'[?name==`foo`].properties.template.containers[0].env[1].name', ["COMPOSE_VAR_B"]),
            self.check(f'[?name==`foo`].properties.template.containers[0].env[1].value', ["default_b"]),
            self.check(f'[?name==`foo`].properties.template.containers[0].env[2].name', ["COMPOSE_VAR_C"]),
            self.check(f'[?name==`foo`].properties.template.containers[0].env[2].value', ["set_value"]),
        ])

        os.environ.pop('COMPOSE_VAR_C', None)
        self.cmd(f'containerapp delete -n foo -g {resource_group} --yes', expect_failure=False)
        clean_up_test_file(compose_file_name)


class ContainerappComposePreviewEnvironmentSettingsExpectedExceptionScenarioTest(ContainerappComposePreviewScenarioTest):  # pylint: disable=line-too-long
    @serial_test()
    @ResourceGroupPreparer(name_prefix='cli_test_containerapp_preview', location='eastus')
    def test_containerapp_compose_create_with_environment_prompt(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        compose_text = f"""
services:
  foo:
    image: mcr.microsoft.com/azuredocs/aks-helloworld:v1
    environment:
      - LOREM=
"""
        compose_file_name = f"{self._testMethodName}_compose.yml"
        write_test_file(compose_file_name, compose_text)
        env_id = prepare_containerapp_env_for_app_e2e_tests(self)
        self.kwargs.update({
            'environment': env_id,
            'compose': compose_file_name,
        })
        
        command_string = 'containerapp compose create'
        command_string += ' --compose-file-path {compose}'
        command_string += ' --resource-group {rg}'
        command_string += ' --environment {environment}'

        # This test fails because prompts are not supported in NoTTY environments
        self.cmd(command_string, expect_failure=True)
        self.cmd(f'containerapp delete -n foo -g {resource_group} --yes', expect_failure=False)

        clean_up_test_file(compose_file_name)
