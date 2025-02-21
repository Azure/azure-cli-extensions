# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

import docker

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, live_only)
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

from azext_containerapp import _utils
from azext_containerapp.tests.latest.utils import create_and_verify_containerapp_up
TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class ContainerAppPatchTest(ScenarioTest):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, random_config_dir=True, **kwargs)

    @live_only()
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location = "eastus2")
    def test_containerapp_patch_list_and_apply_with_resource_group_e2e(self, resource_group):
        builder_platform_name = "dotnet"
        builder_platform_version = "7.0.9"
        builder_runtime_image = f"mcr.microsoft.com/oryx/dotnetcore:{builder_platform_version}-debian-bullseye"

        source_path = os.path.join(TEST_DIR, os.path.join("data", "source_built_using_bullseye_buildpack_net7"))
        ingress = 'external'
        target_port = '8080'

        # Generate oryx.env file for the app to snap to an older version of .NET 7.0
        oryx_env_file_path = os.path.join(source_path, "oryx.env")
        with open(oryx_env_file_path, "w+") as f:
            f.write(f"ORYX_PLATFORM_NAME={builder_platform_name}\n")
            f.write(f"ORYX_PLATFORM_VERSION={builder_platform_version}\n")
            f.write(f"ORYX_RUNTIME_IMAGE={builder_runtime_image}\n")

        try:
            # Generate a name for the Container App
            app_name = self.create_random_name(prefix='containerapp', length=24)

            # Create a Container App using a .NET 7.0 image with an outdated run image that is eligible for patching
            create_and_verify_containerapp_up(self, resource_group, source_path=source_path, ingress=ingress, target_port=target_port, app_name=app_name, requires_acr_prerequisite=True)

            # Execute and verify patch list command
            patchable_images = self.cmd(f'containerapp patch list -g {resource_group}').get_output_in_json()
            self.assertTrue(len(patchable_images) == 1)
            self.assertEqual(patchable_images[0]["oldRunImage"], builder_runtime_image)

            # Execute and verify patch apply command
            self.cmd(f'containerapp patch apply -g {resource_group}')
            patchable_images = self.cmd(f'containerapp patch list -g {resource_group}').get_output_in_json()
            self.assertTrue(len(patchable_images) == 0)
        finally:
            # Delete the oryx.env file so it may not conflict with other tests
            os.remove(oryx_env_file_path)

    @live_only()
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location = "eastus2")
    def test_containerapp_patch_list_and_apply_with_environment_e2e(self, resource_group):
        builder_platform_name = "dotnet"
        builder_platform_version = "7.0.9"
        builder_runtime_image = f"mcr.microsoft.com/oryx/dotnetcore:{builder_platform_version}-debian-bullseye"

        source_path = os.path.join(TEST_DIR, os.path.join("data", "source_built_using_bullseye_buildpack_net7"))
        ingress = 'external'
        target_port = '8080'

        # Generate oryx.env file for the app to snap to an older version of .NET 7.0
        oryx_env_file_path = os.path.join(source_path, "oryx.env")
        with open(oryx_env_file_path, "w+") as f:
            f.write(f"ORYX_PLATFORM_NAME={builder_platform_name}\n")
            f.write(f"ORYX_PLATFORM_VERSION={builder_platform_version}\n")
            f.write(f"ORYX_RUNTIME_IMAGE={builder_runtime_image}\n")

        try:
            # Generate a name for the Container App
            app_name = self.create_random_name(prefix='containerapp', length=24)

            # Create managed environment
            env_name = self.create_random_name(prefix='env', length=24)
            self.cmd(f'containerapp env create -g {resource_group} -n {env_name}')

            # Create a Container App using a .NET 7.0 image with an outdated run image that is eligible for patching
            create_and_verify_containerapp_up(self, resource_group, env_name=env_name, source_path=source_path, ingress=ingress, target_port=target_port, app_name=app_name, requires_acr_prerequisite=True)

            # Execute and verify patch list command
            patchable_images = self.cmd(f'containerapp patch list -g {resource_group} --environment {env_name}').get_output_in_json()
            self.assertTrue(len(patchable_images) == 1)
            self.assertEqual(patchable_images[0]["oldRunImage"], builder_runtime_image)

            # Execute and verify patch apply command
            self.cmd(f'containerapp patch apply -g {resource_group} --environment {env_name}')
            patchable_images = self.cmd(f'containerapp patch list -g {resource_group} --environment {env_name}').get_output_in_json()
            self.assertTrue(len(patchable_images) == 0)
        finally:
            # Delete the oryx.env file so it may not conflict with other tests
            os.remove(oryx_env_file_path)

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

        create_and_verify_containerapp_up(self, resource_group, env_name=env_name, image=image, app_name=app_name, requires_acr_prerequisite=True)

        # Execute and verify patch list command
        patch_cmd = f'containerapp patch list -g {resource_group} --environment {env_name} --show-all'
        output = self.cmd(patch_cmd).get_output_in_json()
        self.assertEqual(output[0]["targetImageName"], "mcr.microsoft.com/k8se/quickstart:latest")

        # Execute and verify patch apply command
        self.cmd(f'containerapp patch apply -g {resource_group} --environment {env_name} --show-all')
        app = self.cmd(f"containerapp show -g {resource_group} -n {app_name}").get_output_in_json()
        image = app["properties"]["template"]["containers"][0]["image"]
        self.assertEqual(image, "mcr.microsoft.com/k8se/quickstart:latest")


    @live_only()
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location = "eastus2")
    def test_containerapp_patch_list_and_apply_without_arguments_e2e(self, resource_group):
        builder_platform_name = "dotnet"
        builder_platform_version = "7.0.9"
        builder_runtime_image = f"mcr.microsoft.com/oryx/dotnetcore:{builder_platform_version}-debian-bullseye"

        source_path = os.path.join(TEST_DIR, os.path.join("data", "source_built_using_bullseye_buildpack_net7"))
        ingress = 'external'
        target_port = '8080'

        # Generate oryx.env file for the app to snap to an older version of .NET 7.0
        oryx_env_file_path = os.path.join(source_path, "oryx.env")
        with open(oryx_env_file_path, "w+") as f:
            f.write(f"ORYX_PLATFORM_NAME={builder_platform_name}\n")
            f.write(f"ORYX_PLATFORM_VERSION={builder_platform_version}\n")
            f.write(f"ORYX_RUNTIME_IMAGE={builder_runtime_image}\n")

        try:
            # Generate a name for the Container App
            app_name = self.create_random_name(prefix='containerapp', length=24)

            # Create a Container App using a .NET 7.0 image with an outdated run image that is eligible for patching
            create_and_verify_containerapp_up(self, resource_group, source_path=source_path, ingress=ingress, target_port=target_port, app_name=app_name, requires_acr_prerequisite=True)

            # Execute and verify patch list command
            self.cmd(f'configure --defaults group={resource_group}')
            patchable_images = self.cmd(f'containerapp patch list').get_output_in_json()
            self.assertTrue(len(patchable_images) == 1)
            self.assertEqual(patchable_images[0]["oldRunImage"], builder_runtime_image)

            # Execute and verify patch apply command
            self.cmd(f'containerapp patch apply')
            patchable_images = self.cmd(f'containerapp patch list').get_output_in_json()
            self.assertTrue(len(patchable_images) == 0)
        finally:
            # Delete the oryx.env file so it may not conflict with other tests
            os.remove(oryx_env_file_path)

    @live_only()
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location = "eastus2")
    def test_containerapp_patch_list_and_apply_with_node18_e2e(self, resource_group):
        builder_platform_name = "node"
        builder_platform_version = "18.16.1"
        builder_runtime_image = f"mcr.microsoft.com/oryx/node:{builder_platform_version}-debian-bullseye"

        source_path = os.path.join(TEST_DIR, os.path.join("data", "source_built_using_bullseye_buildpack_node18"))
        ingress = 'external'
        target_port = '8080'

        # Generate oryx.env file for the app to snap to an older version of Node 18
        oryx_env_file_path = os.path.join(source_path, "oryx.env")
        with open(oryx_env_file_path, "w+") as f:
            f.write(f"ORYX_PLATFORM_NAME={builder_platform_name}\n")
            f.write(f"ORYX_PLATFORM_VERSION={builder_platform_version}\n")
            f.write(f"ORYX_RUNTIME_IMAGE={builder_runtime_image}\n")

        try:
            # Generate a name for the Container App
            app_name = self.create_random_name(prefix='containerapp', length=24)

            # Create a Container App using a Node 18 image with an outdated run image that is eligible for patching
            create_and_verify_containerapp_up(self, resource_group, source_path=source_path, ingress=ingress, target_port=target_port, app_name=app_name, requires_acr_prerequisite=True)

            # Execute and verify patch list command
            self.cmd(f'configure --defaults group={resource_group}')
            patchable_images = self.cmd(f'containerapp patch list').get_output_in_json()
            self.assertTrue(len(patchable_images) == 1)
            self.assertEqual(patchable_images[0]["oldRunImage"], builder_runtime_image)

            # Execute and verify patch apply command
            self.cmd(f'containerapp patch apply')
            patchable_images = self.cmd(f'containerapp patch list').get_output_in_json()
            self.assertTrue(len(patchable_images) == 0)
        finally:
            # Delete the oryx.env file so it may not conflict with other tests
            os.remove(oryx_env_file_path)


    @live_only()
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location = "eastus2")
    def test_containerapp_patch_list_and_apply_with_python310_e2e(self, resource_group):
        builder_platform_name = "python"
        builder_platform_version = "3.10.4"
        builder_runtime_image = f"mcr.microsoft.com/oryx/python:{builder_platform_version}-debian-bullseye"

        source_path = os.path.join(TEST_DIR, os.path.join("data", "source_built_using_bullseye_buildpack_python310"))
        ingress = 'external'
        target_port = '80'

        # Generate oryx.env file for the app to snap to an older version of Python 3.10
        oryx_env_file_path = os.path.join(source_path, "oryx.env")
        with open(oryx_env_file_path, "w+") as f:
            f.write(f"ORYX_PLATFORM_NAME={builder_platform_name}\n")
            f.write(f"ORYX_PLATFORM_VERSION={builder_platform_version}\n")
            f.write(f"ORYX_RUNTIME_IMAGE={builder_runtime_image}\n")

        try:
            # Generate a name for the Container App
            app_name = self.create_random_name(prefix='containerapp', length=24)

            # Create a Container App using a Python 3.10 image with an outdated run image that is eligible for patching
            create_and_verify_containerapp_up(self, resource_group, source_path=source_path, ingress=ingress, target_port=target_port, app_name=app_name, requires_acr_prerequisite=True)

            # Execute and verify patch list command
            self.cmd(f'configure --defaults group={resource_group}')
            patchable_images = self.cmd(f'containerapp patch list').get_output_in_json()
            self.assertTrue(len(patchable_images) == 1)
            self.assertEqual(patchable_images[0]["oldRunImage"], builder_runtime_image)

            # Execute and verify patch apply command
            self.cmd(f'containerapp patch apply')
            patchable_images = self.cmd(f'containerapp patch list').get_output_in_json()
            self.assertTrue(len(patchable_images) == 0)
        finally:
            # Delete the oryx.env file so it may not conflict with other tests
            os.remove(oryx_env_file_path)
