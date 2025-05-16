# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import time
import unittest
from unittest import mock

from azure.cli.command_modules.containerapp._utils import format_location
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, live_only, JMESPathCheck, JMESPathCheckExists)
from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from .common import TEST_LOCATION, STAGE_LOCATION

from .utils import (create_and_verify_containerapp_up,
                    create_and_verify_containerapp_up_with_multiple_environments,
                    create_and_verify_containerapp_up_for_default_registry_image,
                    prepare_containerapp_env_for_app_e2e_tests)

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class ContainerAppUpImageTest(ScenarioTest):

    def test_containerapp_up_create_resource_group(self):
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))
        resource_group = self.create_random_name(prefix='cli.group', length=24)
        image = "mcr.microsoft.com/k8se/quickstart:latest"
        ca_name = self.create_random_name(prefix='containerapp', length=24)

        env = prepare_containerapp_env_for_app_e2e_tests(self, location=location)

        self.cmd(
            'containerapp up -g {} -n {} --image {} --environment {} --ingress external --target-port 80'.format(
                resource_group, ca_name, image, env), expect_failure=False)

        self.cmd(f'containerapp show -g {resource_group} -n {ca_name}', checks=[
            JMESPathCheck("resourceGroup", resource_group),
            JMESPathCheck("properties.provisioningState", "Succeeded"),
        ])
        self.cmd(f'group delete -n {resource_group} --yes --no-wait', expect_failure=False)

    @live_only()
    @ResourceGroupPreparer(location="eastus2")
    def test_containerapp_up_image_e2e(self, resource_group):
        image = "mcr.microsoft.com/k8se/quickstart:latest"
        create_and_verify_containerapp_up(self, resource_group=resource_group, image=image)

    @live_only()
    @ResourceGroupPreparer(location="eastus2")
    def test_containerapp_up_source_with_bullseye_buildpack_e2e(self, resource_group):
        source_path = os.path.join(TEST_DIR, os.path.join("data", "source_built_using_bullseye_buildpack_net7"))
        ingress = 'external'
        target_port = '8080'
        create_and_verify_containerapp_up(self, resource_group=resource_group, source_path=source_path, ingress=ingress, target_port=target_port)

    @live_only()
    @ResourceGroupPreparer(location="eastus2")
    def test_containerapp_up_source_with_bookworm_buildpack_e2e(self, resource_group):
        source_path = os.path.join(TEST_DIR, os.path.join("data", "source_built_using_bookworm_buildpack_net8"))
        ingress = 'external'
        target_port = '8080'
        create_and_verify_containerapp_up(self, resource_group=resource_group, source_path=source_path, ingress=ingress, target_port=target_port)

    @live_only()
    @AllowLargeResponse()
    @ResourceGroupPreparer(location="eastus2")
    def test_containerapp_up_source_with_dockerfile_e2e(self, resource_group):
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))

        source_path = os.path.join(TEST_DIR, os.path.join("data", "source_built_using_dockerfile"))
        ingress = 'external'
        target_port = '80'
        create_and_verify_containerapp_up(self, resource_group=resource_group, source_path=source_path, ingress=ingress, target_port=target_port, location=location, check_registry_identity='system')

        acr_list = self.cmd(f'acr list -g {resource_group}', checks=[
            JMESPathCheck('length(@)', 1),
        ]).get_output_in_json()
        acr = acr_list[0]['name']
        registry_server = f'{acr}.azurecr.io'
        app = self.create_random_name(prefix='aca', length=24)
        create_and_verify_containerapp_up(self, resource_group=resource_group, app_name=app, source_path=source_path, ingress=ingress, target_port=target_port, registry_server=registry_server, location=location, check_registry_identity='system')
        app_json = self.cmd(f'containerapp show -n {app} -g {resource_group}', checks=[
            # JMESPathCheck("properties.template.containers[0].image", image_name),
            JMESPathCheck("properties.configuration.registries[0].identity", 'system'),
            JMESPathCheck("properties.configuration.registries[0].server", f'{acr}.azurecr.io'),
            JMESPathCheck("properties.configuration.registries[0].username", ""),
            JMESPathCheck("properties.configuration.registries[0].passwordSecretRef", ""),
        ]).get_output_in_json()
        image_from_app = app_json["properties"]["template"]["containers"][0]["image"]
        self.assertTrue(image_from_app.startswith(f'{acr}.azurecr.io'))

        # use `az containerapp up --source` to update an existing app
        create_and_verify_containerapp_up(self, resource_group=resource_group, app_name=app, source_path=source_path, ingress=ingress, target_port=target_port, registry_server=registry_server, location=location, check_registry_identity='system')
        app_json = self.cmd(f'containerapp show -n {app} -g {resource_group}', checks=[
            # JMESPathCheck("properties.template.containers[0].image", image_name),
            JMESPathCheck("properties.configuration.registries[0].identity", 'system'),
            JMESPathCheck("properties.configuration.registries[0].server", f'{acr}.azurecr.io'),
            JMESPathCheck("properties.configuration.registries[0].username", ""),
            JMESPathCheck("properties.configuration.registries[0].passwordSecretRef", ""),
        ]).get_output_in_json()
        image_from_app2 = app_json["properties"]["template"]["containers"][0]["image"]
        self.assertTrue(image_from_app2.startswith(f'{acr}.azurecr.io'))
        self.assertNotEqual(image_from_app, image_from_app2)

    @live_only()
    @ResourceGroupPreparer(location="eastus2")
    @unittest.skip("acr_task_run function from acr module uses outdated Storage SDK which does not work with testing.")
    def test_containerapp_up_source_with_acr_task_e2e(self, resource_group):
        source_path = os.path.join(TEST_DIR, os.path.join("data", "source_built_using_acr_task"))
        ingress = 'external'
        target_port = '8080'
        create_and_verify_containerapp_up(self, resource_group=resource_group, source_path=source_path, ingress=ingress, target_port=target_port)

    @live_only()
    @ResourceGroupPreparer(location="eastus2")
    def test_containerapp_up_source_with_multiple_environments_e2e(self, resource_group):
        source_path = os.path.join(TEST_DIR, os.path.join("data", "source_built_using_bullseye_buildpack_net7"))
        ingress = 'external'
        target_port = '8080'
        create_and_verify_containerapp_up_with_multiple_environments(self, resource_group=resource_group, source_path=source_path, ingress=ingress, target_port=target_port, location="eastus2")

    # We have to use @live_only() here as cloud builder and build resource name is generated randomly
    # and no matched request could be found for all builder/build ARM requests
    @live_only()
    @ResourceGroupPreparer(location="eastus2")
    def test_containerapp_up_source_with_default_registry_image(self, resource_group):
        source_path = os.path.join(TEST_DIR, os.path.join("data", "source_built_using_source_to_cloud"))
        ingress = 'external'
        target_port = '80'
        container_name = "test-container-name"
        cpu = 0.5
        memory = "1Gi"
        create_and_verify_containerapp_up_for_default_registry_image(self, resource_group=resource_group, source_path=source_path, ingress=ingress, target_port=target_port, location="eastus2", container_name=container_name, cpu=cpu, memory=memory)

    @live_only()
    @ResourceGroupPreparer(location="westus3")
    def test_containerapp_up_foundry_model_e2e(self, resource_group):
        model_name = "gpt2-medium"
        model_version = "18"
        model_registry = "azureml"
        location = "westus3"
        create_and_verify_containerapp_up(self, resource_group=resource_group, location=location, model_name=model_name, model_version=model_version, model_registry=model_registry)


class ContainerappUpRegistryIdentityWithSourceTests(ScenarioTest):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, random_config_dir=True, **kwargs)

    @live_only()  # Pass lively, But failed in playback mode when execute queue_acr_build
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="westeurope")
    def test_containerapp_up_source_registry_identity_user(self, resource_group):
        # MSI is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use eastus as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))

        source_path = os.path.join(TEST_DIR, os.path.join("data", "source_built_using_dockerfile"))

        app = self.create_random_name(prefix='aca', length=24)
        identity1 = self.create_random_name(prefix='id1', length=24)
        identity2 = self.create_random_name(prefix='id2', length=24)
        acr = self.create_random_name(prefix='acr', length=24)
        image_source = "mcr.microsoft.com/k8se/quickstart:latest"

        env = prepare_containerapp_env_for_app_e2e_tests(self, location=location)

        identity_rid_1 = self.cmd(f'identity create -g {resource_group} -n {identity1}').get_output_in_json()["id"]
        identity_rid_2 = self.cmd(f'identity create -g {resource_group} -n {identity2}').get_output_in_json()["id"]

        # create an ACR without --admin-enabled
        self.cmd(f'acr create --sku basic -n {acr} -g {resource_group}', checks=[
            JMESPathCheck("adminUserEnabled", False),
            JMESPathCheck("anonymousPullEnabled", False),
        ])
        # create a new containerapp with `az containerapp up` only with `--registry-server {acr}.azurecr.io`
        # Use SystemAssigned as default for image pull
        with mock.patch('azure.cli.command_modules.role.custom._gen_guid', side_effect=self.create_guid):
            self.cmd(
                f'containerapp up -g {resource_group} -n {app} --source "{source_path}" --ingress external --target-port 80 --environment {env} --registry-server {acr}.azurecr.io')

        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "SystemAssigned"),
            JMESPathCheck("properties.configuration.secrets", None),
            JMESPathCheck("length(properties.configuration.registries)", 1),
            JMESPathCheck("properties.configuration.registries[0].identity", 'system'),
            JMESPathCheck("properties.configuration.registries[0].server", f'{acr}.azurecr.io'),
            JMESPathCheck("properties.configuration.registries[0].username", ""),
            JMESPathCheck("properties.configuration.registries[0].passwordSecretRef", ""),
        ])
        # update the registry to a user-identity
        with mock.patch('azure.cli.command_modules.role.custom._gen_guid', side_effect=self.create_guid):
            self.cmd(
                f'containerapp up -g {resource_group} -n {app} --registry-identity {identity_rid_1} --source "{source_path}" --ingress external --target-port 80 --environment {env} --registry-server {acr}.azurecr.io')

        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "SystemAssigned, UserAssigned"),
            JMESPathCheckExists(f'identity.userAssignedIdentities."{identity_rid_1}"'),
            JMESPathCheck("length(properties.configuration.registries)", 1),
            JMESPathCheck("properties.configuration.registries[0].identity", identity_rid_1),
            JMESPathCheck("properties.configuration.registries[0].server", f'{acr}.azurecr.io'),
            JMESPathCheck("properties.configuration.registries[0].username", ""),
            JMESPathCheck("properties.configuration.registries[0].passwordSecretRef", ""),
        ])

        # update the containerapp with --system-assigned
        self.cmd(
            f'containerapp up -g {resource_group} -n {app} --registry-identity {identity_rid_1} --source "{source_path}" --ingress external --target-port 80 --environment {env} --registry-server {acr}.azurecr.io --system-assigned')

        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "SystemAssigned, UserAssigned"),
            JMESPathCheckExists(f'identity.userAssignedIdentities."{identity_rid_1}"'),
            JMESPathCheck("length(properties.configuration.registries)", 1),
            JMESPathCheck("properties.configuration.registries[0].identity", identity_rid_1),
            JMESPathCheck("properties.configuration.registries[0].server", f'{acr}.azurecr.io'),
            JMESPathCheck("properties.configuration.registries[0].username", ""),
            JMESPathCheck("properties.configuration.registries[0].passwordSecretRef", ""),
        ])

        # update the containerapp with --system-assigned --user-assigned
        self.cmd(
            f'containerapp up -g {resource_group} -n {app} --user-assigned {identity_rid_1} --system-assigned --source "{source_path}" --ingress external --target-port 80 --environment {env} --registry-server {acr}.azurecr.io')

        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "SystemAssigned, UserAssigned"),
            JMESPathCheckExists(f'identity.userAssignedIdentities."{identity_rid_1}"'),
            JMESPathCheck("length(properties.configuration.registries)", 1),
            JMESPathCheck("properties.configuration.registries[0].identity", identity_rid_1),
            JMESPathCheck("properties.configuration.registries[0].server", f'{acr}.azurecr.io'),
            JMESPathCheck("properties.configuration.registries[0].username", ""),
            JMESPathCheck("properties.configuration.registries[0].passwordSecretRef", ""),
        ])

        self.cmd(f'containerapp identity remove --system-assigned -g {resource_group} -n {app}', checks=[
            JMESPathCheck("type", "UserAssigned"),
        ])

        app_json = self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "UserAssigned"),
            JMESPathCheckExists(f'identity.userAssignedIdentities."{identity_rid_1}"'),
            JMESPathCheck("length(properties.configuration.registries)", 1),
            JMESPathCheck("properties.configuration.registries[0].identity", identity_rid_1),
            JMESPathCheck("properties.configuration.registries[0].server", f'{acr}.azurecr.io'),
            JMESPathCheck("properties.configuration.registries[0].username", ""),
            JMESPathCheck("properties.configuration.registries[0].passwordSecretRef", ""),
        ]).get_output_in_json()
        image_name1 = app_json["properties"]["template"]["containers"][0]["image"]
        self.assertTrue(image_name1.startswith(f'{acr}.azurecr.io'))

        # update the containerapp with --system-assigned --user-assigned
        self.cmd(
            f'containerapp up -g {resource_group} -n {app} --user-assigned {identity_rid_1} {identity_rid_2} --system-assigned --source "{source_path}" --ingress external --target-port 80 --environment {env} --registry-server {acr}.azurecr.io')

        app_json = self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "SystemAssigned, UserAssigned"),
            JMESPathCheckExists(f'identity.userAssignedIdentities."{identity_rid_1}"'),
            JMESPathCheckExists(f'identity.userAssignedIdentities."{identity_rid_2}"'),
            JMESPathCheck("length(properties.configuration.registries)", 1),
            JMESPathCheck("properties.configuration.registries[0].identity", identity_rid_1),
            JMESPathCheck("properties.configuration.registries[0].server", f'{acr}.azurecr.io'),
            JMESPathCheck("properties.configuration.registries[0].username", ""),
            JMESPathCheck("properties.configuration.registries[0].passwordSecretRef", ""),
        ]).get_output_in_json()
        image_name2 = app_json["properties"]["template"]["containers"][0]["image"]
        self.assertTrue(image_name2.startswith(f'{acr}.azurecr.io'))
        self.assertNotEqual(image_name1, image_name2)

    @live_only()  # Pass lively, But failed in playback mode when execute queue_acr_build
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="westeurope")
    def test_containerapp_up_source_registry_identity_system(self, resource_group):
        # MSI is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use eastus as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))
        source_path = os.path.join(TEST_DIR, os.path.join("data", "source_built_using_dockerfile"))

        app = self.create_random_name(prefix='aca', length=24)
        acr = self.create_random_name(prefix='acr', length=24)

        env = prepare_containerapp_env_for_app_e2e_tests(self, location=location)

        self.cmd(f'acr create --sku basic -n {acr} -g {resource_group} --admin-enabled')
        with mock.patch('azure.cli.command_modules.role.custom._gen_guid', side_effect=self.create_guid):
            self.cmd(f'containerapp up -g {resource_group} -n {app} --registry-identity "system" --source "{source_path}" --ingress external --target-port 80 --environment {env} --registry-server {acr}.azurecr.io')

        app_json = self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "SystemAssigned"),
            JMESPathCheck("properties.configuration.secrets", None),
            JMESPathCheck("length(properties.configuration.registries)", 1),
            JMESPathCheck("properties.configuration.registries[0].identity", 'system'),
            JMESPathCheck("properties.configuration.registries[0].server", f'{acr}.azurecr.io'),
            JMESPathCheck("properties.configuration.registries[0].username", ""),
            JMESPathCheck("properties.configuration.registries[0].passwordSecretRef", "")
        ]).get_output_in_json()
        image_name1 = app_json["properties"]["template"]["containers"][0]["image"]
        self.assertTrue(image_name1.startswith(f'{acr}.azurecr.io'))

        with mock.patch('azure.cli.command_modules.role.custom._gen_guid', side_effect=self.create_guid):
            self.cmd(
                f'containerapp up -g {resource_group} -n {app} --registry-identity "system" --source "{source_path}" --ingress internal --target-port 80 --environment {env} --registry-server {acr}.azurecr.io')

        app_json = self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "SystemAssigned"),
            JMESPathCheck("properties.configuration.secrets", None),
            JMESPathCheck("length(properties.configuration.registries)", 1),
            JMESPathCheck("properties.configuration.registries[0].identity", 'system'),
            JMESPathCheck("properties.configuration.registries[0].server", f'{acr}.azurecr.io'),
            JMESPathCheck("properties.configuration.registries[0].username", ""),
            JMESPathCheck("properties.configuration.registries[0].passwordSecretRef", "")
        ]).get_output_in_json()
        image_name2 = app_json["properties"]["template"]["containers"][0]["image"]
        self.assertTrue(image_name2.startswith(f'{acr}.azurecr.io'))
        self.assertNotEqual(image_name1, image_name2)

    @live_only()  # Pass lively, But failed in playback mode when execute queue_acr_build
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="westeurope")
    def test_containerapp_up_source_private_registry_port(self, resource_group):
        # MSI is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use eastus as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))
        source_path = os.path.join(TEST_DIR, os.path.join("data", "source_built_using_dockerfile"))

        app = self.create_random_name(prefix='aca', length=24)
        acr = self.create_random_name(prefix='acr', length=24)
        image_source = "mcr.microsoft.com/k8se/quickstart:latest"

        env = prepare_containerapp_env_for_app_e2e_tests(self, location=location)
        acr_location = TEST_LOCATION
        if format_location(acr_location) == format_location(STAGE_LOCATION):
            acr_location = "eastus"
        self.cmd(f'acr create --sku basic -n {acr} -g {resource_group} --admin-enabled -l {acr_location}')
        self.cmd(f'acr import -n {acr} --source {image_source}')
        password = self.cmd(f'acr credential show -n {acr} --query passwords[0].value').get_output_in_json()

        self.cmd(
            f'containerapp up -g {resource_group} -n {app} --source "{source_path}" --ingress external --target-port 80 --environment {env} --registry-server {acr}.azurecr.io --registry-username {acr} --registry-password {password}')

        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("properties.configuration.registries[0].server", f"{acr}.azurecr.io"),
            JMESPathCheck("properties.configuration.registries[0].identity", ""),
            JMESPathCheck("properties.configuration.registries[0].username", acr),
            JMESPathCheck("properties.configuration.registries[0].passwordSecretRef", f"{acr}azurecrio-{acr}"),
            JMESPathCheck("properties.configuration.secrets[0].name", f"{acr}azurecrio-{acr}"),
        ])

        # update from username/password to system
        with mock.patch('azure.cli.command_modules.role.custom._gen_guid', side_effect=self.create_guid):
            self.cmd(
                f'containerapp up -g {resource_group} -n {app}  --source "{source_path}" --ingress external --target-port 80 --environment {env} --registry-server {acr}.azurecr.io --registry-identity system',
                expect_failure=False)

        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "SystemAssigned"),
            JMESPathCheck("properties.configuration.secrets", None),
            JMESPathCheck("length(properties.configuration.registries)", 1),
            JMESPathCheck("properties.configuration.registries[0].identity", 'system'),
            JMESPathCheck("properties.configuration.registries[0].server", f"{acr}.azurecr.io"),
            JMESPathCheck("properties.configuration.registries[0].username", ""),
            JMESPathCheck("properties.configuration.registries[0].passwordSecretRef", ""),
        ])

    @live_only()  # Pass lively, But failed in playback mode when execute queue_acr_build
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="westeurope")
    def test_containerapp_up_source_registry_acr_look_up_credentical(self, resource_group):
        # MSI is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use eastus as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))
        source_path = os.path.join(TEST_DIR, os.path.join("data", "source_built_using_dockerfile"))

        app = self.create_random_name(prefix='aca', length=24)
        acr = self.create_random_name(prefix='acr', length=24)
        image_source = "mcr.microsoft.com/k8se/quickstart:latest"

        env = prepare_containerapp_env_for_app_e2e_tests(self, location=location)

        acr_location = TEST_LOCATION
        if format_location(acr_location) == format_location(STAGE_LOCATION):
            acr_location = "eastus"
        self.cmd(f'acr create --sku basic -n {acr} -g {resource_group} --admin-enabled --location {acr_location}')
        self.cmd(f'acr import -n {acr} --source {image_source}')

        # `az containberapp create` only with `--registry-server {acr}.azurecr.io`, use SystemAssigned as default for image pull
        with mock.patch('azure.cli.command_modules.role.custom._gen_guid', side_effect=self.create_guid):
            self.cmd(f'containerapp up -g {resource_group} -n {app} --source "{source_path}" --ingress external --target-port 80 --environment {env} --registry-server {acr}.azurecr.io', expect_failure=False)

        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
                JMESPathCheck("properties.provisioningState", "Succeeded"),
                JMESPathCheck("identity.type", "SystemAssigned"),
                JMESPathCheck("properties.configuration.secrets", None),
                JMESPathCheck("length(properties.configuration.registries)", 1),
                JMESPathCheck("properties.configuration.registries[0].identity", 'system'),
                JMESPathCheck("properties.configuration.registries[0].server", f'{acr}.azurecr.io'),
                JMESPathCheck("properties.configuration.registries[0].username", ""),
                JMESPathCheck("properties.configuration.registries[0].passwordSecretRef", ""),
        ])

        # --registry-server {acr}.azurecr.io --registry-username, auto lookup credentical
        self.cmd(
            f'containerapp up -g {resource_group} -n {app} --source "{source_path}" --ingress external --target-port 80 --environment {env} --registry-server {acr}.azurecr.io --registry-username a', expect_failure=False)

        app_json = self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "SystemAssigned"),
            JMESPathCheck("properties.configuration.secrets[0].name", f"{acr}azurecrio-{acr}"),
            JMESPathCheck("properties.configuration.registries[0].server", f"{acr}.azurecr.io"),
            JMESPathCheck("properties.configuration.registries[0].identity", ""),
            JMESPathCheck("properties.configuration.registries[0].username", acr),
        ]).get_output_in_json()
        image_name1 = app_json["properties"]["template"]["containers"][0]["image"]
        self.assertTrue(image_name1.startswith(f'{acr}.azurecr.io'))

        # update existing app, the registry keep consistent
        with mock.patch('azure.cli.command_modules.role.custom._gen_guid', side_effect=self.create_guid):
            self.cmd(f'containerapp up -g {resource_group} -n {app} --source "{source_path}" --environment {env} --registry-server {acr}.azurecr.io', expect_failure=False)
        app_json = self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "SystemAssigned"),
            JMESPathCheck("properties.configuration.secrets[0].name", f"{acr}azurecrio-{acr}"),
            JMESPathCheck("properties.configuration.registries[0].server", f"{acr}.azurecr.io"),
            JMESPathCheck("properties.configuration.registries[0].identity", ""),
            JMESPathCheck("properties.configuration.registries[0].username", acr)
        ]).get_output_in_json()
        image_name2 = app_json["properties"]["template"]["containers"][0]["image"]
        self.assertTrue(image_name2.startswith(f'{acr}.azurecr.io'))
        self.assertNotEqual(image_name1, image_name2)

        # update containerapp registry from username/password to identity
        with mock.patch('azure.cli.command_modules.role.custom._gen_guid', side_effect=self.create_guid):
            self.cmd(f'containerapp up -g {resource_group} -n {app} --source "{source_path}" --ingress external --target-port 80 --environment {env} --registry-server {acr}.azurecr.io --registry-identity system', expect_failure=False)

        app_json = self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "SystemAssigned"),
            JMESPathCheck("properties.configuration.secrets", None),
            JMESPathCheck("length(properties.configuration.registries)", 1),
            JMESPathCheck("properties.configuration.registries[0].identity", 'system'),
            JMESPathCheck("properties.configuration.registries[0].server", f'{acr}.azurecr.io'),
            JMESPathCheck("properties.configuration.registries[0].username", ""),
            JMESPathCheck("properties.configuration.registries[0].passwordSecretRef", ""),
        ]).get_output_in_json()
        image_name2 = app_json["properties"]["template"]["containers"][0]["image"]
        self.assertTrue(image_name2.startswith(f'{acr}.azurecr.io'))
        self.assertNotEqual(image_name1, image_name2)

    @live_only()  # Pass lively, But failed in playback mode when execute queue_acr_build
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="westeurope")
    def test_containerapp_up_source_identity_registry(self, resource_group):
        # MSI is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use eastus as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))
        source_path = os.path.join(TEST_DIR, os.path.join("data", "source_built_using_dockerfile"))

        env_name = self.create_random_name(prefix='containerapp-e2e-env', length=24)
        ca_name = self.create_random_name(prefix='containerapp', length=24)
        acr = self.create_random_name(prefix='acr', length=24)

        # prepare env
        user_identity_name = self.create_random_name(prefix='env-msi', length=24)
        identity_json = self.cmd(
            'identity create -g {} -n {}'.format(resource_group, user_identity_name)).get_output_in_json()
        user_identity_id = identity_json["id"]

        self.cmd(
            'containerapp env create -g {} -n {} --mi-system-assigned --mi-user-assigned {} --logs-destination none'.format(
                resource_group, env_name, user_identity_id))
        containerapp_env = self.cmd(
            'containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()
        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd(
                'containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()
        env = containerapp_env["id"]

        # prepare acr
        acr_id = \
        self.cmd(f'acr create --sku basic -n {acr} -g {resource_group} --location {location}').get_output_in_json()[
            "id"]
        # role assign
        roleAssignmentName1 = self.create_guid()
        roleAssignmentName2 = self.create_guid()
        self.cmd(
            f'role assignment create --role acrpull --assignee {containerapp_env["identity"]["principalId"]} --scope {acr_id} --name {roleAssignmentName1}')
        self.cmd(
            f'role assignment create --role acrpull --assignee {identity_json["principalId"]} --scope {acr_id} --name {roleAssignmentName2}')

        # wait for role assignment take effect
        time.sleep(30)

        # use env system msi to pull image
        self.cmd(
            f'containerapp up -g {resource_group} -n {ca_name} --source "{source_path}" --ingress external --target-port 80 --environment {env} --registry-server {acr}.azurecr.io --registry-identity system-environment')
        self.cmd(f'containerapp show -g {resource_group} -n {ca_name}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "None"),
            JMESPathCheck("properties.configuration.registries[0].server", f"{acr}.azurecr.io"),
            JMESPathCheck("properties.configuration.registries[0].identity", "system-environment",
                          case_sensitive=False),
        ])

        # update use env user assigned identity
        self.cmd(
            f'containerapp registry set -g {resource_group} -n {ca_name} --server {acr}.azurecr.io --identity {user_identity_id}')
        app_json = self.cmd(f'containerapp show -g {resource_group} -n {ca_name}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "None"),
            JMESPathCheck("properties.configuration.registries[0].server", f"{acr}.azurecr.io"),
            JMESPathCheck("properties.configuration.registries[0].identity", user_identity_id, case_sensitive=False),
        ]).get_output_in_json()

        image_name = app_json["properties"]["template"]["containers"][0]["image"]
        self.assertTrue(image_name.startswith(f'{acr}.azurecr.io'))

        # update containerapp to create new revision
        self.cmd(f'containerapp update -g {resource_group} -n {ca_name} --revision-suffix v2')
        self.cmd(f'containerapp show -g {resource_group} -n {ca_name}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "None"),
            JMESPathCheck("properties.configuration.registries[0].server", f"{acr}.azurecr.io"),
            JMESPathCheck("properties.configuration.registries[0].identity", user_identity_id, case_sensitive=False),
            JMESPathCheck("properties.template.containers[0].image", image_name),
            JMESPathCheck("properties.template.revisionSuffix", "v2")
        ])

        # update use env system managed identity
        self.cmd(
            f'containerapp registry set -g {resource_group} -n {ca_name} --server {acr}.azurecr.io --identity system-environment')
        self.cmd(f'containerapp show -g {resource_group} -n {ca_name}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "None"),
            JMESPathCheck("properties.configuration.registries[0].server", f"{acr}.azurecr.io"),
            JMESPathCheck("properties.configuration.registries[0].identity", "system-environment"),
            JMESPathCheck("properties.template.containers[0].image", image_name),
        ])

        # update containerapp to create new revision
        self.cmd(f'containerapp update -g {resource_group} -n {ca_name}  --revision-suffix v3')
        self.cmd(f'containerapp show -g {resource_group} -n {ca_name}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "None"),
            JMESPathCheck("properties.configuration.registries[0].server", f"{acr}.azurecr.io"),
            JMESPathCheck("properties.configuration.registries[0].identity", "system-environment"),
            JMESPathCheck("properties.template.containers[0].image", image_name),
            JMESPathCheck("properties.template.revisionSuffix", "v3")
        ])
