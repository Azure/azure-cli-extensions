# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest  # pylint: disable=unused-import

from azure.cli.testsdk import (ResourceGroupPreparer)
from azure.cli.testsdk.decorators import serial_test
from azext_containerapp_compose.tests.latest.common import (ContainerappComposePreviewScenarioTest,  # pylint: disable=unused-import
                                                            write_test_file,
                                                            clean_up_test_file,
                                                            TEST_DIR)


class ContainerappComposePreviewResourceSettingsScenarioTest(ContainerappComposePreviewScenarioTest):
    @serial_test()
    @ResourceGroupPreparer(name_prefix='cli_test_containerapp_preview', location='eastus')
    def test_containerapp_compose_create_with_resources_from_service_cpus(self, resource_group):
        compose_text = """
services:
  foo:
    image: mcr.microsoft.com/azuredocs/aks-helloworld:v1
    cpus: 1.25
    expose:
      - "3000"
"""
        compose_file_name = f"{self._testMethodName}_compose.yml"
        write_test_file(compose_file_name, compose_text)

        self.kwargs.update({
            'environment': self.create_random_name(prefix='containerapp-compose', length=24),
            'workspace': self.create_random_name(prefix='containerapp-compose', length=24),
            'compose': compose_file_name,
        })

        command_string = 'containerapp compose create'
        command_string += ' --compose-file-path {compose}'
        command_string += ' --resource-group {rg}'
        command_string += ' --environment {environment}'
        command_string += ' --logs-workspace {workspace}'
        self.cmd(command_string, checks=[
            self.check('[?name==`foo`].properties.template.containers[0].resources.cpu', [1.25]),
        ])

        clean_up_test_file(compose_file_name)

    @serial_test()
    @ResourceGroupPreparer(name_prefix='cli_test_containerapp_preview', location='eastus')
    def test_containerapp_compose_create_with_resources_from_deploy_cpu(self, resource_group):
        compose_text = """
services:
  foo:
    image: mcr.microsoft.com/azuredocs/aks-helloworld:v1
    deploy:
      resources:
        reservations:
          cpus: 1.25
    expose:
      - "3000"
"""
        compose_file_name = f"{self._testMethodName}_compose.yml"
        write_test_file(compose_file_name, compose_text)

        self.kwargs.update({
            'environment': self.create_random_name(prefix='containerapp-compose', length=24),
            'workspace': self.create_random_name(prefix='containerapp-compose', length=24),
            'compose': compose_file_name,
        })

        command_string = 'containerapp compose create'
        command_string += ' --compose-file-path {compose}'
        command_string += ' --resource-group {rg}'
        command_string += ' --environment {environment}'
        command_string += ' --logs-workspace {workspace}'
        self.cmd(command_string, checks=[
            self.check('[?name==`foo`].properties.template.containers[0].resources.cpu', [1.25]),
        ])

        clean_up_test_file(compose_file_name)

    @serial_test()
    @ResourceGroupPreparer(name_prefix='cli_test_containerapp_preview', location='eastus')
    def test_containerapp_compose_create_with_resources_from_both_cpus_and_deploy_cpu(self, resource_group):
        compose_text = """
services:
  foo:
    image: mcr.microsoft.com/azuredocs/aks-helloworld:v1
    cpus: 0.75
    deploy:
      resources:
        reservations:
          cpus: 1.25
    expose:
      - "3000"
"""
        compose_file_name = f"{self._testMethodName}_compose.yml"
        write_test_file(compose_file_name, compose_text)

        self.kwargs.update({
            'environment': self.create_random_name(prefix='containerapp-compose', length=24),
            'workspace': self.create_random_name(prefix='containerapp-compose', length=24),
            'compose': compose_file_name,
        })

        command_string = 'containerapp compose create'
        command_string += ' --compose-file-path {compose}'
        command_string += ' --resource-group {rg}'
        command_string += ' --environment {environment}'
        command_string += ' --logs-workspace {workspace}'
        self.cmd(command_string, checks=[
            self.check('[?name==`foo`].properties.template.containers[0].resources.cpu', [1.25]),
        ])

        clean_up_test_file(compose_file_name)
