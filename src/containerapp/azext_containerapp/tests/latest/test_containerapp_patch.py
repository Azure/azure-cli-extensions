# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

import docker

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, live_only)

from azext_containerapp import _utils
from azext_containerapp.tests.latest.utils import create_and_verify_containerapp_up
TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

class ContainerAppPatchTest(ScenarioTest):
    @live_only()
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location = "eastus2")
    def test_containerapp_patch_list_and_apply_with_resource_group_e2e(self, resource_group):
        old_version = "7.0.9-debian-bullseye"
        old_run_image = f"mcr.microsoft.com/oryx/dotnetcore:{old_version}"
        image_to_deploy = f"sourcetocloudtestacr.azurecr.io/sample/dotnet:{old_version}"
        ingress = 'external'
        target_port = '8080'

        # Generate a name for the Container App
        app_name = self.create_random_name(prefix='containerapp', length=24)

        # Create a Container App using a .NET 7.0 image with an outdated run image that is eligible for patching
        create_and_verify_containerapp_up(self, resource_group, image=image_to_deploy, ingress=ingress, target_port=target_port, app_name=app_name)

        # Execute and verify patch list command
        patchable_images = self.cmd(f'containerapp patch list -g {resource_group}').get_output_in_json()
        self.assertTrue(len(patchable_images) == 1)
        self.assertEquals(patchable_images[0]["oldRunImage"], old_run_image)

        # Execute and verify patch apply command
        self.cmd(f'containerapp patch apply -g {resource_group}')
        patchable_images = self.cmd(f'containerapp patch list -g {resource_group}').get_output_in_json()
        self.assertTrue(len(patchable_images) == 0)

    @live_only()
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location = "eastus2")
    def test_containerapp_patch_list_and_apply_with_environment_e2e(self, resource_group):
        old_version = "7.0.9-debian-bullseye"
        old_run_image = f"mcr.microsoft.com/oryx/dotnetcore:{old_version}"
        image_to_deploy = f"sourcetocloudtestacr.azurecr.io/sample/dotnet:{old_version}"
        ingress = 'external'
        target_port = '8080'

        # Generate a name for the Container App
        app_name = self.create_random_name(prefix='containerapp', length=24)

        # Create managed environment
        env_name = self.create_random_name(prefix='env', length=24)
        self.cmd(f'containerapp env create -g {resource_group} -n {env_name}')

        # Create a Container App using a .NET 7.0 image with an outdated run image that is eligible for patching
        create_and_verify_containerapp_up(self, resource_group, env_name=env_name, image=image_to_deploy, ingress=ingress, target_port=target_port, app_name=app_name)

        # Execute and verify patch list command
        patchable_images = self.cmd(f'containerapp patch list -g {resource_group} --environment {env_name}').get_output_in_json()
        self.assertTrue(len(patchable_images) == 1)
        self.assertEquals(patchable_images[0]["oldRunImage"], old_run_image)

        # Execute and verify patch apply command
        self.cmd(f'containerapp patch apply -g {resource_group} --environment {env_name}')
        patchable_images = self.cmd(f'containerapp patch list -g {resource_group} --environment {env_name}').get_output_in_json()
        self.assertTrue(len(patchable_images) == 0)

    @live_only()
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location = "eastus2")
    def test_containerapp_patch_list_and_apply_with_show_all_e2e(self, resource_group):
        image = "mcr.microsoft.com/k8se/quickstart:latest"

        # Generate a name for the Container App
        app_name = self.create_random_name(prefix='containerapp', length=24)

        # Create managed environment
        env_name = self.create_random_name(prefix='env', length=24)
        self.cmd(f'containerapp env create -g {resource_group} -n {env_name}')

        create_and_verify_containerapp_up(self, resource_group, env_name=env_name, image=image, app_name=app_name)

        # Execute and verify patch list command
        patch_cmd = f'containerapp patch list -g {resource_group} --environment {env_name} --show-all'
        output = self.cmd(patch_cmd).get_output_in_json()
        self.assertEquals(output[0]["targetImageName"], "mcr.microsoft.com/k8se/quickstart:latest")

        # Execute and verify patch apply command
        self.cmd(f'containerapp patch apply -g {resource_group} --environment {env_name} --show-all')
        app = self.cmd(f"containerapp show -g {resource_group} -n {app_name}").get_output_in_json()
        image = app["properties"]["template"]["containers"][0]["image"]
        self.assertEquals(image, "mcr.microsoft.com/k8se/quickstart:latest")


    @live_only()
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location = "eastus2")
    def test_containerapp_patch_list_and_apply_without_arguments_e2e(self, resource_group):
        old_version = "7.0.9-debian-bullseye"
        old_run_image = f"mcr.microsoft.com/oryx/dotnetcore:{old_version}"
        image_to_deploy = f"sourcetocloudtestacr.azurecr.io/sample/dotnet:{old_version}"
        ingress = 'external'
        target_port = '8080'

        # Generate a name for the Container App
        app_name = self.create_random_name(prefix='containerapp', length=24)

        # Create a Container App using a .NET 7.0 image with an outdated run image that is eligible for patching
        create_and_verify_containerapp_up(self, resource_group, image=image_to_deploy, ingress=ingress, target_port=target_port, app_name=app_name)

        # Execute and verify patch list command
        self.cmd(f'configure --defaults group={resource_group}')
        patchable_images = self.cmd(f'containerapp patch list').get_output_in_json()
        self.assertTrue(len(patchable_images) == 1)
        self.assertEquals(patchable_images[0]["oldRunImage"], old_run_image)

        # Execute and verify patch apply command
        self.cmd(f'containerapp patch apply')
        patchable_images = self.cmd(f'containerapp patch list').get_output_in_json()
        self.assertTrue(len(patchable_images) == 0)

    @live_only()
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location = "eastus2")
    def test_containerapp_patch_list_and_apply_with_node18_e2e(self, resource_group):
        old_version = "18.16.1-debian-bullseye"
        old_run_image = f"mcr.microsoft.com/oryx/node:{old_version}"
        image_to_deploy = f"sourcetocloudtestacr.azurecr.io/sample/node:{old_version}"
        ingress = 'external'
        target_port = '8080'

        # Generate a name for the Container App
        app_name = self.create_random_name(prefix='containerapp', length=24)

        # Create a Container App using a Node 18 image with an outdated run image that is eligible for patching
        create_and_verify_containerapp_up(self, resource_group, image=image_to_deploy, ingress=ingress, target_port=target_port, app_name=app_name)

        # Execute and verify patch list command
        self.cmd(f'configure --defaults group={resource_group}')
        patchable_images = self.cmd(f'containerapp patch list').get_output_in_json()
        self.assertTrue(len(patchable_images) == 1)
        self.assertEquals(patchable_images[0]["oldRunImage"], old_run_image)

        # Execute and verify patch apply command
        self.cmd(f'containerapp patch apply')
        patchable_images = self.cmd(f'containerapp patch list').get_output_in_json()
        self.assertTrue(len(patchable_images) == 0)

    @live_only()
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location = "eastus2")
    def test_containerapp_patch_list_and_apply_with_python310_e2e(self, resource_group):
        old_version = "3.10.4-debian-bullseye"
        old_run_image = f"mcr.microsoft.com/oryx/python:{old_version}"
        image_to_deploy = f"sourcetocloudtestacr.azurecr.io/sample/python:{old_version}"
        ingress = 'external'
        target_port = '8080'

        # Generate a name for the Container App
        app_name = self.create_random_name(prefix='containerapp', length=24)

        # Create a Container App using a Python 3.9 image with an outdated run image that is eligible for patching
        create_and_verify_containerapp_up(self, resource_group, image=image_to_deploy, ingress=ingress, target_port=target_port, app_name=app_name)

        # Execute and verify patch list command
        self.cmd(f'configure --defaults group={resource_group}')
        patchable_images = self.cmd(f'containerapp patch list').get_output_in_json()
        self.assertTrue(len(patchable_images) == 1)
        self.assertEquals(patchable_images[0]["oldRunImage"], old_run_image)

        # Execute and verify patch apply command
        self.cmd(f'containerapp patch apply')
        patchable_images = self.cmd(f'containerapp patch list').get_output_in_json()
        self.assertTrue(len(patchable_images) == 0)
