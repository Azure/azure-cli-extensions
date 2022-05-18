# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest  # pylint: disable=unused-import

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class ContainerappComposePreviewSecretsScenarioTest(ScenarioTest):
    @ResourceGroupPreparer(name_prefix='cli_test_containerapp_preview', location='eastus')
    def test_containerapp_compose_create_with_secrets(self, resource_group):
        compose_text = """
services:
  foo:
    image: mcr.microsoft.com/azuredocs/aks-helloworld:v1
    secrets:
      - source: my_secret
        target: redis_secret
        uid: '103'
        gid: '103'
        mode: 0440
secrets:
  my_secret:
    file: ./my_secret.txt
  my_other_secret:
    external: true
"""
        compose_file_name = f"{self._testMethodName}_compose.yml"
        docker_compose_file = open(compose_file_name, "w", encoding='utf-8')
        _ = docker_compose_file.write(compose_text)
        docker_compose_file.close()

        secrets_file_name = "./my_secret.txt"
        docker_secrets_file = open(secrets_file_name, "w", encoding='utf-8')
        _ = docker_secrets_file.write("Lorem Ipsum\n")
        docker_secrets_file.close()

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
            self.check('[?name==`foo`].properties.configuration.secrets[0].name', ["redis-secret"]),
            self.check('[?name==`foo`].properties.template.containers[0].env[0].name', ["redis-secret"]),
            self.check('[?name==`foo`].properties.template.containers[0].env[0].secretRef', ["redis-secret"])  # pylint: disable=C0301
        ])

        if os.path.exists(compose_file_name):
            os.remove(compose_file_name)

        if os.path.exists(secrets_file_name):
            os.remove(secrets_file_name)

    @ResourceGroupPreparer(name_prefix='cli_test_containerapp_preview', location='eastus')
    def test_containerapp_compose_create_with_secrets_and_existing_environment(self, resource_group):
        compose_text = """
services:
  foo:
    image: mcr.microsoft.com/azuredocs/aks-helloworld:v1
    environment:
      database__client: mysql
      database__connection__host: db
      database__connection__user: root
      database__connection__password: example
      database__connection__database: snafu
    secrets:
      - source: my_secret
        target: redis_secret
        uid: '103'
        gid: '103'
        mode: 0440
secrets:
  my_secret:
    file: ./snafu.txt
  my_other_secret:
    external: true
"""
        compose_file_name = f"{self._testMethodName}_compose.yml"
        docker_compose_file = open(compose_file_name, "w", encoding='utf-8')
        _ = docker_compose_file.write(compose_text)
        docker_compose_file.close()

        secrets_file_name = "./snafu.txt"
        docker_secrets_file = open(secrets_file_name, "w", encoding='utf-8')
        _ = docker_secrets_file.write("Lorem Ipsum\n")
        docker_secrets_file.close()

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
            self.check('length([?name==`foo`].properties.template.containers[0].env[].name)', 6),
        ])

        if os.path.exists(compose_file_name):
            os.remove(compose_file_name)

        if os.path.exists(secrets_file_name):
            os.remove(secrets_file_name)

    @ResourceGroupPreparer(name_prefix='cli_test_containerapp_preview', location='eastus')
    def test_containerapp_compose_create_with_secrets_and_existing_environment_conflict(self, resource_group):
        compose_text = """
services:
  foo:
    image: mcr.microsoft.com/azuredocs/aks-helloworld:v1
    environment:
      database--client: mysql
    secrets:
      -  database__client
secrets:
  database__client:
    file: ./database__client.txt
"""
        compose_file_name = f"{self._testMethodName}_compose.yml"
        docker_compose_file = open(compose_file_name, "w", encoding='utf-8')
        _ = docker_compose_file.write(compose_text)
        docker_compose_file.close()

        secrets_file_name = "./database__client.txt"
        docker_secrets_file = open(secrets_file_name, "w", encoding='utf-8')
        _ = docker_secrets_file.write("Lorem Ipsum\n")
        docker_secrets_file.close()

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

        # This test fails with duplicate environment variable names
        self.cmd(command_string, expect_failure=True)

        if os.path.exists(compose_file_name):
            os.remove(compose_file_name)

        if os.path.exists(secrets_file_name):
            os.remove(secrets_file_name)
