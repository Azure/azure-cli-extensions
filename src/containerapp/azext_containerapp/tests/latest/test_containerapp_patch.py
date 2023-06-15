#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from unittest import mock
import time
import requests
import docker

from azure.cli.testsdk.reverse_dependency import get_dummy_cli
from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck, live_only)
from knack.util import CLIError

from azext_containerapp.tests.latest.common import TEST_LOCATION
from azext_containerapp import _utils
TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

class ContainerAppPatchTest(ScenarioTest):
    @live_only()
    @ResourceGroupPreparer(location = "eastus2")
    def test_containerapp_patch_list_and_apply_with_resource_group_e2e(self, resource_group):
        source_path = os.path.join(TEST_DIR, os.path.join("data", "source_built_using_buildpack"))
        ingress = 'external'
        target_port = '8080'

        # Generate a name for the Container App
        app_name = self.create_random_name(prefix='containerapp', length=24)

        self._create_and_verify_containerapp_up(resource_group,source_path=source_path,ingress=ingress,target_port=target_port,app_name=app_name)
        self._retag_image_to_older_version_and_push(resource_group=resource_group,app_name=app_name)

        # Execute and verify patch list command
        patchable_images = self.cmd(f'containerapp patch list -g {resource_group}').get_output_in_json()
        newRunImageTag = patchable_images[0]["newRunImage"].split(':')[1]
        self.assertEquals(newRunImageTag,_utils.get_latest_buildpack_run_tag("aspnet", "7.0"))
        self.assertEquals(patchable_images[0]["oldRunImage"], "run-dotnet-aspnet-7.0.1-cbl-mariner2.0")

        # Execute and verify patch apply command
        self.cmd(f'containerapp patch apply -g {resource_group}')
        app = self.cmd(f"containerapp show -g {resource_group} -n {app_name}").get_output_in_json()
        patched_image = app["properties"]["template"]["containers"][0]["image"]
        patched_image_tag = patched_image.split(':')[1]
        self.assertEquals(patched_image_tag,_utils.get_latest_buildpack_run_tag("aspnet", "7.0"))

    @live_only()
    @ResourceGroupPreparer(location = "eastus2")
    def test_containerapp_patch_list_and_apply_with_environment_e2e(self, resource_group):
        source_path = os.path.join(TEST_DIR, os.path.join("data", "source_built_using_buildpack"))
        ingress = 'external'
        target_port = '80'

        # Generate a name for the Container App
        app_name = self.create_random_name(prefix='containerapp', length=24)

        # Create managed environment
        env_name = self.create_random_name(prefix='env', length=24)
        self.cmd(f'containerapp env create -g {resource_group} -n {env_name}')

        self._create_and_verify_containerapp_up(resource_group,env_name=env_name,source_path=source_path,ingress=ingress,target_port=target_port,app_name=app_name)
        self._retag_image_to_older_version_and_push(resource_group=resource_group,app_name=app_name)

        # Execute and verify patch list command
        patchable_images = self.cmd(f'containerapp patch list -g {resource_group} --environment {env_name}').get_output_in_json()
        newRunImageTag = patchable_images[0]["newRunImage"].split(':')[1]
        self.assertEquals(newRunImageTag,_utils.get_latest_buildpack_run_tag("aspnet", "7.0"))
        self.assertEquals(patchable_images[0]["oldRunImage"], "run-dotnet-aspnet-7.0.1-cbl-mariner2.0")

        # Execute and verify patch apply command
        self.cmd(f'containerapp patch apply -g {resource_group} --environment {env_name}')
        app = self.cmd(f"containerapp show -g {resource_group} -n {app_name}").get_output_in_json()
        patched_image = app["properties"]["template"]["containers"][0]["image"]
        patched_image_tag = patched_image.split(':')[1]
        self.assertEquals(patched_image_tag,_utils.get_latest_buildpack_run_tag("aspnet", "7.0"))

    @live_only()
    @ResourceGroupPreparer(location = "eastus2")
    def test_containerapp_patch_list_and_apply_with_show_all_e2e(self, resource_group):
        image = "mcr.microsoft.com/k8se/quickstart:latest"

        # Generate a name for the Container App
        app_name = self.create_random_name(prefix='containerapp', length=24)

        # Create managed environment
        env_name = self.create_random_name(prefix='env', length=24)
        self.cmd(f'containerapp env create -g {resource_group} -n {env_name}')

        self._create_and_verify_containerapp_up(resource_group,env_name=env_name,image=image,app_name=app_name)

        # Execute and verify patch list command
        patch_cmd = f'containerapp patch list -g {resource_group} --environment {env_name} --show-all'
        output = self.cmd(patch_cmd).get_output_in_json()
        self.assertEquals(output[0]["targetImageName"],"mcr.microsoft.com/k8se/quickstart:latest")

        # Execute and verify patch apply command
        self.cmd(f'containerapp patch apply -g {resource_group} --environment {env_name} --show-all')
        app = self.cmd(f"containerapp show -g {resource_group} -n {app_name}").get_output_in_json()
        image = app["properties"]["template"]["containers"][0]["image"]
        self.assertEquals(image,"mcr.microsoft.com/k8se/quickstart:latest")


    @live_only()
    @ResourceGroupPreparer(location = "eastus2")
    def test_containerapp_patch_list_and_apply_without_arguments_e2e(self, resource_group):
        source_path = os.path.join(TEST_DIR, os.path.join("data", "source_built_using_buildpack"))
        ingress = 'external'
        target_port = '80'

         # Generate a name for the Container App
        app_name = self.create_random_name(prefix='containerapp', length=24)

        self._create_and_verify_containerapp_up(resource_group,source_path=source_path,ingress=ingress,target_port=target_port,app_name=app_name)
        self._retag_image_to_older_version_and_push(resource_group=resource_group,app_name=app_name)

        # Execute and verify patch list command
        self.cmd(f'configure --defaults group={resource_group}')
        patch_cmd = f'containerapp patch list'
        patchable_images = self.cmd(patch_cmd).get_output_in_json()
        newRunImageTag = patchable_images[0]["newRunImage"].split(':')[1]
        self.assertEquals(newRunImageTag,_utils.get_latest_buildpack_run_tag("aspnet", "7.0"))
        self.assertEquals(patchable_images[0]["oldRunImage"], "run-dotnet-aspnet-7.0.1-cbl-mariner2.0")

        # Execute and verify patch apply command
        self.cmd(f'containerapp patch apply')
        app = self.cmd(f"containerapp show -g {resource_group} -n {app_name}").get_output_in_json()
        patched_image = app["properties"]["template"]["containers"][0]["image"]
        patched_image_tag = patched_image.split(':')[1]
        self.assertEquals(patched_image_tag,_utils.get_latest_buildpack_run_tag("aspnet", "7.0"))

    def _retag_image_to_older_version_and_push(self,resource_group,app_name):
        client = docker.from_env()
        app = self.cmd(f"containerapp show -g {resource_group} -n {app_name}").get_output_in_json()
        image_name = app["properties"]["template"]["containers"][0]["image"]
        current_image = client.images.get(image_name)
        registry = app["properties"]["configuration"]["registries"][0]["server"]
        repo = app["properties"]["template"]["containers"][0]["name"]

        # Re-tag image to an older version to simulate patch list
        old_tag = "run-dotnet-aspnet-7.0.1-cbl-mariner2.0"
        old_image_name = registry + "/" + repo + ":" + old_tag
        current_image.tag(registry + "/" + repo, tag = old_tag)

         # Re-tag and push
        client.images.push(registry + "/" + repo, tag = old_tag)
        self.cmd('az containerapp update -n {} -g {} --image {}'.format(app_name, resource_group, old_image_name))
        app = self.cmd(f"containerapp show -g {resource_group} -n {app_name}").get_output_in_json()
        retagged_image = app["properties"]["template"]["containers"][0]["image"]
        retagged_image_tag = retagged_image.split(':')[1]

        # Verify if image was updated
        self.assertEquals(retagged_image_tag,old_tag)

    def _create_and_verify_containerapp_up(
            self,
            resource_group,
            env_name = None,
            source_path = None,
            image = None,
            location = None,
            ingress = None,
            target_port = None,
            app_name = None):
        # Configure the default location
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        # Ensure that the Container App environment is created
        if env_name is None:
           env_name = self.create_random_name(prefix='env', length=24)
           self.cmd(f'containerapp env create -g {resource_group} -n {env_name}')

        if app_name is None:
            # Generate a name for the Container App
            app_name = self.create_random_name(prefix='containerapp', length=24)

        # Construct the 'az containerapp up' command
        up_cmd = f"containerapp up -g {resource_group} -n {app_name} --environment {env_name}"
        if source_path:
            up_cmd += f" --source \"{source_path}\""
        if image:
            up_cmd += f" --image {image}"
        if ingress:
            up_cmd += f" --ingress {ingress}"
        if target_port:
            up_cmd += f" --target-port {target_port}"

        # Execute the 'az containerapp up' command
        self.cmd(up_cmd)

        # Verify that the Container App is running
        app = self.cmd(f"containerapp show -g {resource_group} -n {app_name}").get_output_in_json()
        url = app["properties"]["configuration"]["ingress"]["fqdn"]
        url = url if url.startswith("http") else f"http://{url}"
        resp = requests.get(url)
        self.assertTrue(resp.ok)

        # Re-run the 'az containerapp up' command with the location parameter if provided
        if location:
            up_cmd += f" -l {location.upper()}"
            self.cmd(up_cmd)

