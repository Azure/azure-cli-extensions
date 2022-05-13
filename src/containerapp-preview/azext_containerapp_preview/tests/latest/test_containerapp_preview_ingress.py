# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest  # pylint: disable=unused-import

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class ContainerappComposePreviewIngressScenarioTest(ScenarioTest):
    @ResourceGroupPreparer(name_prefix='cli_test_containerapp_preview', location='eastus')
    def test_containerapp_compose_create_with_ingress_external(self, resource_group):
        compose_text = """
services:
  foo:
    image: mcr.microsoft.com/azuredocs/aks-helloworld:v1
    ports: 8080:80
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
            self.check('[?name==`foo`].properties.configuration.ingress.targetPort', [80]),
            self.check('[?name==`foo`].properties.configuration.ingress.external', [True]),
        ])

        if os.path.exists(compose_file_name):
            os.remove(compose_file_name)


class ContainerappComposePreviewIngressInternalScenarioTest(ScenarioTest):
    @ResourceGroupPreparer(name_prefix='cli_test_containerapp_preview', location='eastus')
    def test_containerapp_compose_create_with_ingress_internal(self, resource_group):
        compose_text = """
services:
  foo:
    image: mcr.microsoft.com/azuredocs/aks-helloworld:v1
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
            self.check('[?name==`foo`].properties.configuration.ingress.targetPort', [3000]),
            self.check('[?name==`foo`].properties.configuration.ingress.external', [False]),
        ])

        if os.path.exists(compose_file_name):
            os.remove(compose_file_name)


class ContainerappComposePreviewIngressBothScenarioTest(ScenarioTest):
    @ResourceGroupPreparer(name_prefix='cli_test_containerapp_preview', location='eastus')
    def test_containerapp_compose_create_with_ingress_both(self, resource_group):
        compose_text = """
services:
  foo:
    image: mcr.microsoft.com/azuredocs/aks-helloworld:v1
    ports: 4000:3000
    expose:
      - "5000"
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
            self.check('[?name==`foo`].properties.configuration.ingress.targetPort', [3000]),
            self.check('[?name==`foo`].properties.configuration.ingress.external', [True]),
        ])

        if os.path.exists(compose_file_name):
            os.remove(compose_file_name)


class ContainerappComposePreviewIngressPromptScenarioTest(ScenarioTest):
    @ResourceGroupPreparer(name_prefix='cli_test_containerapp_preview', location='eastus')
    def test_containerapp_compose_create_with_ingress_prompt(self, resource_group):
        compose_text = """
services:
  foo:
    image: mcr.microsoft.com/azuredocs/aks-helloworld:v1
    ports:
      - 4000:3000
      - 443:443
      - 80:80
    expose:
      - "5000"
      - "3000"
      - "443"
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

        # This test fails because prompts are not supported in NoTTY environments
        self.cmd(command_string, expect_failure=True)

        if os.path.exists(compose_file_name):
            os.remove(compose_file_name)
