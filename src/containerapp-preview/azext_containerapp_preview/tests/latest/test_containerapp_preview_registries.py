# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest  # pylint: disable=unused-import

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class ContainerappComposePreviewRegistryAllArgsScenarioTest(ScenarioTest):
    @ResourceGroupPreparer(name_prefix='cli_test_containerapp_preview', location='eastus')
    def test_containerapp_compose_create_with_registry_all_args(self, resource_group):
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
            'registry_server': "foobar.azurecr.io",
            'registry_user': "foobar",
            'registry_pass': "snafu",
        })

        command_string = 'containerapp compose create'
        command_string += ' --compose-file-path {compose}'
        command_string += ' --resource-group {rg}'
        command_string += ' --environment {environment}'
        command_string += ' --logs-workspace {workspace}'
        command_string += ' --registry-server {registry_server}'
        command_string += ' --registry-username {registry_user}'
        command_string += ' --registry-password {registry_pass}'

        self.cmd(command_string, checks=[
            self.check('[?name==`foo`].properties.configuration.registries[0].server', ["foobar.azurecr.io"]),
            self.check('[?name==`foo`].properties.configuration.registries[0].username', ["foobar"]),
            self.check('[?name==`foo`].properties.configuration.registries[0].passwordSecretRef', ["foobarazurecrio-foobar"]),  # pylint: disable=C0301
        ])

        if os.path.exists(compose_file_name):
            os.remove(compose_file_name)


class ContainerappComposePreviewRegistryServerArgOnlyScenarioTest(ScenarioTest):
    @ResourceGroupPreparer(name_prefix='cli_test_containerapp_preview', location='eastus')
    def test_containerapp_compose_create_with_registry_server_arg_only(self, resource_group):
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
            'registry_server': "foobar.azurecr.io",
        })

        command_string = 'containerapp compose create'
        command_string += ' --compose-file-path {compose}'
        command_string += ' --resource-group {rg}'
        command_string += ' --environment {environment}'
        command_string += ' --logs-workspace {workspace}'
        command_string += ' --registry-server {registry_server}'

        # This test fails because prompts are not supported in NoTTY environments
        self.cmd(command_string, expect_failure=True)

        if os.path.exists(compose_file_name):
            os.remove(compose_file_name)
