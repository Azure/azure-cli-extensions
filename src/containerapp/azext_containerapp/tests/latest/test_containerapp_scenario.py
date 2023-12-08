# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import platform
from unittest import mock
import time
import unittest

from azure.cli.command_modules.containerapp._utils import format_location
from msrestazure.tools import parse_resource_id

from azure.cli.testsdk.reverse_dependency import get_dummy_cli
from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck, live_only)
from knack.util import CLIError

from azext_containerapp.tests.latest.common import TEST_LOCATION

from .common import STAGE_LOCATION
from .utils import prepare_containerapp_env_for_app_e2e_tests

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class ContainerappScenarioTest(ScenarioTest):
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="eastus2")
    def test_containerapp_e2e(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        env_id = prepare_containerapp_env_for_app_e2e_tests(self)

        containerapp_name = self.create_random_name(prefix='containerapp-e2e', length=24)

        # Create basic Container App with default image
        self.cmd('containerapp create -g {} -n {} --environment {}'.format(resource_group, containerapp_name, env_id), checks=[
            JMESPathCheck('name', containerapp_name)
        ])

        self.cmd('containerapp show -g {} -n {}'.format(resource_group, containerapp_name), checks=[
            JMESPathCheck('name', containerapp_name),
        ])

        self.cmd('containerapp list -g {}'.format(resource_group), checks=[
            JMESPathCheck('length(@)', 1),
            JMESPathCheck('[0].name', containerapp_name),
        ])

        # Create Container App with image, resource and replica limits
        create_string = "containerapp create -g {} -n {} --environment {} --image nginx --cpu 0.5 --memory 1.0Gi --min-replicas 2 --max-replicas 4".format(resource_group, containerapp_name, env_id)
        self.cmd(create_string, checks=[
            JMESPathCheck('name', containerapp_name),
            JMESPathCheck('properties.template.containers[0].image', 'nginx'),
            JMESPathCheck('properties.template.containers[0].resources.cpu', '0.5'),
            JMESPathCheck('properties.template.containers[0].resources.memory', '1Gi'),
            JMESPathCheck('properties.template.scale.minReplicas', '2'),
            JMESPathCheck('properties.template.scale.maxReplicas', '4')
        ])

        self.cmd('containerapp create -g {} -n {} --environment {} --ingress external --target-port 8080'.format(resource_group, containerapp_name, env_id), checks=[
            JMESPathCheck('properties.configuration.ingress.external', True),
            JMESPathCheck('properties.configuration.ingress.targetPort', 8080)
        ])

        # Container App with ingress should fail unless target port is specified
        with self.assertRaises(CLIError):
            self.cmd('containerapp create -g {} -n {} --environment {} --ingress external'.format(resource_group, containerapp_name, env_id))

        # Create Container App with secrets and environment variables
        containerapp_name = self.create_random_name(prefix='containerapp-e2e', length=24)
        create_string = 'containerapp create -g {} -n {} --environment {} --secrets mysecret=secretvalue1 anothersecret="secret value 2" --env-vars GREETING="Hello, world" SECRETENV=secretref:anothersecret'.format(
            resource_group, containerapp_name, env_id)
        self.cmd(create_string, checks=[
            JMESPathCheck('name', containerapp_name),
            JMESPathCheck('length(properties.template.containers[0].env)', 2),
            JMESPathCheck('length(properties.configuration.secrets)', 2)
        ])


    # TODO rename
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="westeurope")
    def test_containerapp_update(self, resource_group):
        #  identity is unavailable for location 'North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use eastus as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))

        env_id = prepare_containerapp_env_for_app_e2e_tests(self, location)

        # Create basic Container App with default image
        containerapp_name = self.create_random_name(prefix='containerapp-update', length=24)

        self.cmd('containerapp create -g {} -n {} --environment {}'.format(resource_group, containerapp_name, env_id), checks=[
            JMESPathCheck('name', containerapp_name),
            JMESPathCheck('length(properties.template.containers)', 1),
            JMESPathCheck('properties.template.containers[0].name', containerapp_name)
        ])

        self.cmd('containerapp show -g {} -n {}'.format(resource_group, containerapp_name), checks=[
            JMESPathCheck('name', containerapp_name),
        ])

        self.cmd('containerapp list -g {}'.format(resource_group), checks=[
            JMESPathCheck('length(@)', 1),
            JMESPathCheck('[0].name', containerapp_name),
        ])

        # Create Container App with image, resource and replica limits
        create_string = "containerapp create -g {} -n {} --environment {} --image nginx --cpu 0.5 --memory 1.0Gi --min-replicas 2 --max-replicas 4".format(resource_group, containerapp_name, env_id)
        self.cmd(create_string, checks=[
            JMESPathCheck('name', containerapp_name),
            JMESPathCheck('properties.template.containers[0].image', 'nginx'),
            JMESPathCheck('properties.template.containers[0].resources.cpu', '0.5'),
            JMESPathCheck('properties.template.containers[0].resources.memory', '1Gi'),
            JMESPathCheck('properties.template.scale.minReplicas', '2'),
            JMESPathCheck('properties.template.scale.maxReplicas', '4')
        ])

        self.cmd('containerapp create -g {} -n {} --environment {} --ingress external --target-port 8080'.format(resource_group, containerapp_name, env_id), checks=[
            JMESPathCheck('properties.configuration.ingress.external', True),
            JMESPathCheck('properties.configuration.ingress.targetPort', 8080)
        ])

        # Container App with ingress should fail unless target port is specified
        with self.assertRaises(CLIError):
            self.cmd('containerapp create -g {} -n {} --environment {} --ingress external'.format(resource_group, containerapp_name, env_id))

        # Create Container App with secrets and environment variables
        containerapp_name = self.create_random_name(prefix='containerapp-e2e', length=24)
        create_string = 'containerapp create -g {} -n {} --environment {} --secrets mysecret=secretvalue1 anothersecret="secret value 2" --env-vars GREETING="Hello, world" SECRETENV=secretref:anothersecret'.format(
            resource_group, containerapp_name, env_id)
        self.cmd(create_string, checks=[
            JMESPathCheck('name', containerapp_name),
            JMESPathCheck('length(properties.template.containers[0].env)', 2),
            JMESPathCheck('length(properties.configuration.secrets)', 2)
        ])


    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="eastus2")
    def test_container_acr(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))
        env_id = prepare_containerapp_env_for_app_e2e_tests(self)

        containerapp_name = self.create_random_name(prefix='containerapp-e2e', length=24)
        registry_name = self.create_random_name(prefix='containerapp', length=24)

        # Create ACR
        acr_location = TEST_LOCATION
        if format_location(acr_location) == format_location(STAGE_LOCATION):
            acr_location = "eastus"
        acr = self.cmd('acr create -g {} -n {} --sku Basic --admin-enabled --location {}'.format(resource_group, registry_name, acr_location)).get_output_in_json()
        registry_server = acr["loginServer"]

        acr_credentials = self.cmd('acr credential show -g {} -n {}'.format(resource_group, registry_name)).get_output_in_json()
        registry_username = acr_credentials["username"]
        registry_password = acr_credentials["passwords"][0]["value"]

        # Create Container App with ACR
        containerapp_name = self.create_random_name(prefix='containerapp-e2e', length=24)
        create_string = 'containerapp create -g {} -n {} --environment {} --registry-username {} --registry-server {} --registry-password {}'.format(
            resource_group, containerapp_name, env_id, registry_username, registry_server, registry_password)
        self.cmd(create_string, checks=[
            JMESPathCheck('name', containerapp_name),
            JMESPathCheck('properties.configuration.registries[0].server', registry_server),
            JMESPathCheck('properties.configuration.registries[0].username', registry_username),
            JMESPathCheck('length(properties.configuration.secrets)', 1),
        ])

        # Update Container App with ACR
        update_string = 'containerapp update -g {} -n {} --min-replicas 0 --max-replicas 1 --set-env-vars testenv=testing'.format(
            resource_group, containerapp_name)
        self.cmd(update_string, checks=[
            JMESPathCheck('name', containerapp_name),
            JMESPathCheck('properties.configuration.registries[0].server', registry_server),
            JMESPathCheck('properties.configuration.registries[0].username', registry_username),
            JMESPathCheck('length(properties.configuration.secrets)', 1),
            JMESPathCheck('properties.template.scale.minReplicas', '0'),
            JMESPathCheck('properties.template.scale.maxReplicas', '1'),
            JMESPathCheck('length(properties.template.containers[0].env)', 1),
            JMESPathCheck('properties.template.containers[0].env[0].name', "testenv"),
            JMESPathCheck('properties.template.containers[0].env[0].value', None),
        ])

        # Add secrets to Container App with ACR
        containerapp_secret = self.cmd('containerapp secret list -g {} -n {}'.format(resource_group, containerapp_name)).get_output_in_json()
        secret_name = containerapp_secret[0]["name"]
        secret_string = 'containerapp secret set -g {} -n {} --secrets newsecret=test'.format(resource_group, containerapp_name)
        self.cmd(secret_string, checks=[
            JMESPathCheck('length(@)', 2),
        ])

        with self.assertRaises(CLIError):
            # Removing ACR password should fail since it is needed for ACR
            self.cmd('containerapp secret remove -g {} -n {} --secret-names {}'.format(resource_group, containerapp_name, secret_name))

    # TODO rename
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northeurope")
    def test_containerapp_update_containers(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        env_id = prepare_containerapp_env_for_app_e2e_tests(self)

        # Create basic Container App with default image
        containerapp_name = self.create_random_name(prefix='containerapp-update', length=24)
        self.cmd('containerapp create -g {} -n {} --environment {}'.format(resource_group, containerapp_name, env_id), checks=[
            JMESPathCheck('name', containerapp_name),
            JMESPathCheck('length(properties.template.containers)', 1),
            JMESPathCheck('properties.template.containers[0].name', containerapp_name)
        ])

        # Update existing Container App that has a single container

        update_string = 'containerapp update -g {} -n {} --image {} --cpu 0.5 --memory 1.0Gi --args mycommand mycommand2 --command "mycommand" --revision-suffix suffix --min-replicas 2 --max-replicas 34'.format(
            resource_group, containerapp_name, 'nginx')
        self.cmd(update_string, checks=[
            JMESPathCheck('name', containerapp_name),
            JMESPathCheck('length(properties.template.containers)', 1),
            JMESPathCheck('properties.template.containers[0].name', containerapp_name),
            JMESPathCheck('properties.template.containers[0].image', 'nginx'),
            JMESPathCheck('properties.template.containers[0].resources.cpu', '0.5'),
            JMESPathCheck('properties.template.containers[0].resources.memory', '1Gi'),
            JMESPathCheck('properties.template.scale.minReplicas', '2'),
            JMESPathCheck('properties.template.scale.maxReplicas', '34'),
            JMESPathCheck('properties.template.containers[0].command[0]', "mycommand"),
            JMESPathCheck('length(properties.template.containers[0].args)', 2)
        ])

        # Add new container to existing Container App
        update_string = 'containerapp update -g {} -n {} --container-name {} --image {}'.format(
            resource_group, containerapp_name, "newcontainer", "nginx")
        self.cmd(update_string, checks=[
            JMESPathCheck('name', containerapp_name),
            JMESPathCheck('length(properties.template.containers)', 2)
        ])

        # Updating container properties in a Container App with multiple containers, without providing container name should error
        update_string = 'containerapp update -g {} -n {} --cpu {} --memory {}'.format(
            resource_group, containerapp_name, '1.0', '2.0Gi')
        with self.assertRaises(CLIError):
            self.cmd(update_string)

        # Updating container properties in a Container App with multiple containers, should work when container name provided
        update_string = 'containerapp update -g {} -n {} --container-name {} --cpu {} --memory {}'.format(
            resource_group, containerapp_name, 'newcontainer', '0.75', '1.5Gi')
        self.cmd(update_string)

        update_string = 'containerapp update -g {} -n {} --container-name {} --cpu {} --memory {}'.format(
            resource_group, containerapp_name, containerapp_name, '0.75', '1.5Gi')
        self.cmd(update_string, checks=[
            JMESPathCheck('properties.template.containers[0].resources.cpu', '0.75'),
            JMESPathCheck('properties.template.containers[0].resources.memory', '1.5Gi'),
            JMESPathCheck('properties.template.containers[1].resources.cpu', '0.75'),
            JMESPathCheck('properties.template.containers[1].resources.memory', '1.5Gi'),
        ])

    @ResourceGroupPreparer(location="northeurope")
    def test_containerapp_logstream(self, resource_group):
        containerapp_name = self.create_random_name(prefix='capp', length=24)
        env_id = prepare_containerapp_env_for_app_e2e_tests(self)

        self.cmd(f'containerapp create -g {resource_group} -n {containerapp_name} --environment {env_id} --min-replicas 1 --ingress external --target-port 80')

        self.cmd(f'containerapp logs show -n {containerapp_name} -g {resource_group}')

    @ResourceGroupPreparer(location="northeurope")
    def test_containerapp_eventstream(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        containerapp_name = self.create_random_name(prefix='capp', length=24)
        env_id = prepare_containerapp_env_for_app_e2e_tests(self)
        env_rg = parse_resource_id(env_id).get('resource_group')
        env_name = parse_resource_id(env_id).get('name')

        self.cmd(f'containerapp create -g {resource_group} -n {containerapp_name} --environment {env_id} --min-replicas 1 --ingress external --target-port 80')

        self.cmd(f'containerapp logs show -n {containerapp_name} -g {resource_group} --type system')
        self.cmd(f'containerapp env logs show -n {env_name} -g {env_rg}')

    @ResourceGroupPreparer(location="northeurope")
    def test_containerapp_registry_msi(self, resource_group):
        #  resource type 'Microsoft.ContainerRegistry/registries' is not available in North Central US(Stage), if the TEST_LOCATION is "northcentralusstage", use eastus as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))

        app = self.create_random_name(prefix='app', length=24)
        acr = self.create_random_name(prefix='acr', length=24)

        env_id = prepare_containerapp_env_for_app_e2e_tests(self, location)

        self.cmd(f'containerapp create -g {resource_group} -n {app} --environment {env_id} --min-replicas 1 --ingress external --target-port 80')
        self.cmd(f'acr create -g {resource_group} -n {acr} --sku basic --admin-enabled')
        # self.cmd(f'acr credential renew -n {acr} ')
        self.cmd(f'containerapp registry set --server {acr}.azurecr.io -g {resource_group} -n {app}')
        app_data = self.cmd(f'containerapp show -g {resource_group} -n {app}').get_output_in_json()
        self.assertEqual(app_data["properties"]["configuration"]["registries"][0].get("server"), f'{acr}.azurecr.io')
        self.assertIsNotNone(app_data["properties"]["configuration"]["registries"][0].get("passwordSecretRef"))
        self.assertIsNotNone(app_data["properties"]["configuration"]["registries"][0].get("username"))
        self.assertEqual(app_data["properties"]["configuration"]["registries"][0].get("identity"), "")

        self.cmd(f'containerapp registry set --server {acr}.azurecr.io -g {resource_group} -n {app} --identity system')
        app_data = self.cmd(f'containerapp show -g {resource_group} -n {app}').get_output_in_json()
        self.assertEqual(app_data["properties"]["configuration"]["registries"][0].get("server"), f'{acr}.azurecr.io')
        self.assertEqual(app_data["properties"]["configuration"]["registries"][0].get("passwordSecretRef"), "")
        self.assertEqual(app_data["properties"]["configuration"]["registries"][0].get("username"), "")
        self.assertEqual(app_data["properties"]["configuration"]["registries"][0].get("identity"), "system")
