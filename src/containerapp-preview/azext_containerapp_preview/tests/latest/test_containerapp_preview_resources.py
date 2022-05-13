# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest  # pylint: disable=unused-import

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class ContainerappComposePreviewResourceSettingsScenarioTest(ScenarioTest):
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
        docker_compose_file = open(compose_file_name, "w", encoding='utf-8')
        _ = docker_compose_file.write(compose_text)
        docker_compose_file.close()

        self.kwargs.update({
            'environment': self.create_random_name(prefix='containerapp-preview', length=24),
            'workspace': self.create_random_name(prefix='containerapp-preview', length=24),
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

        if os.path.exists(compose_file_name):
            os.remove(compose_file_name)

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
        docker_compose_file = open(compose_file_name, "w", encoding='utf-8')
        _ = docker_compose_file.write(compose_text)
        docker_compose_file.close()

        self.kwargs.update({
            'environment': self.create_random_name(prefix='containerapp-preview', length=24),
            'workspace': self.create_random_name(prefix='containerapp-preview', length=24),
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

        if os.path.exists(compose_file_name):
            os.remove(compose_file_name)

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
        docker_compose_file = open(compose_file_name, "w", encoding='utf-8')
        _ = docker_compose_file.write(compose_text)
        docker_compose_file.close()

        self.kwargs.update({
            'environment': self.create_random_name(prefix='containerapp-preview', length=24),
            'workspace': self.create_random_name(prefix='containerapp-preview', length=24),
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

        if os.path.exists(compose_file_name):
            os.remove(compose_file_name)
