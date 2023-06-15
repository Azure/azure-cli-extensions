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

class ContainerAppPatchListTest(ScenarioTest):
    @live_only()
    @ResourceGroupPreparer(location = "eastus2")
    def test_containerapp_patch_list_with_resource_group_e2e(self, resource_group):
        source_path = os.path.join(TEST_DIR, os.path.join("data", "source_built_using_buildpack"))
        ingress = 'external'
        target_port = '8080'

        # Configure the default location
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        # Ensure that the Container App environment is created
        env_name = self.create_random_name(prefix='env', length=24)
        self.cmd(f'containerapp env create -g {resource_group} -n {env_name}')

        # Generate a name for the Container App
        app_name = self.create_random_name(prefix='containerapp', length=24)

        # Execute the 'az containerapp up' command
        self.cmd(f"containerapp up -g {resource_group} -n {app_name} --environment {env_name} --source \"{source_path}\" --ingress {ingress} --target-port {target_port}")

        # Verify that the Container App is running
        app = self.cmd(f"containerapp show -g {resource_group} -n {app_name}").get_output_in_json()
        url = app["properties"]["configuration"]["ingress"]["fqdn"]
        url = url if url.startswith("http") else f"http://{url}"
        resp = requests.get(url)
        self.assertTrue(resp.ok)

        # Verify patch list command
        client = docker.from_env()
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

        # Execute patch list command
        patchable_images = self.cmd(f'containerapp patch list -g {resource_group}').get_output_in_json()
        newRunImageTag = patchable_images[0]["newRunImage"].split(':')[1]
        self.assertEquals(newRunImageTag,_utils.get_latest_buildpack_run_tag("aspnet", "7.0"))
        self.assertEquals(patchable_images[0]["oldRunImage"], old_tag)

    @live_only()
    @ResourceGroupPreparer(location = "eastus2")
    def test_containerapp_patch_list_with_environment_e2e(self, resource_group):
        source_path = os.path.join(TEST_DIR, os.path.join("data", "source_built_using_buildpack"))
        ingress = 'external'
        target_port = '80'

         # Configure the default location
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        # Ensure that the Container App environment is created
        env_name = self.create_random_name(prefix='env', length=24)
        self.cmd(f'containerapp env create -g {resource_group} -n {env_name}')

        # Generate a name for the Container App
        app_name = self.create_random_name(prefix='containerapp', length=24)

        # Execute the 'az containerapp up' command
        self.cmd(f"containerapp up -g {resource_group} -n {app_name} --environment {env_name} --source \"{source_path}\" --ingress {ingress} --target-port {target_port}")

        # Verify that the Container App is running
        app = self.cmd(f"containerapp show -g {resource_group} -n {app_name}").get_output_in_json()
        url = app["properties"]["configuration"]["ingress"]["fqdn"]
        url = url if url.startswith("http") else f"http://{url}"
        resp = requests.get(url)
        self.assertTrue(resp.ok)

        # Verify patch list command
        client = docker.from_env()
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

        # Execute patch list command
        patchable_images = self.cmd(f'containerapp patch list -g {resource_group} --environment {env_name}').get_output_in_json()
        newRunImageTag = patchable_images[0]["newRunImage"].split(':')[1]
        self.assertEquals(newRunImageTag,_utils.get_latest_buildpack_run_tag("aspnet", "7.0"))
        self.assertEquals(patchable_images[0]["oldRunImage"], old_tag)

    @live_only()
    @ResourceGroupPreparer(location = "eastus2")
    def test_containerapp_patch_list_with_show_all_e2e(self, resource_group):
        image = "mcr.microsoft.com/k8se/quickstart:latest"
         # Configure the default location
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        # Ensure that the Container App environment is created
        env_name = self.create_random_name(prefix='env', length=24)
        self.cmd(f'containerapp env create -g {resource_group} -n {env_name}')

        # Generate a name for the Container App
        app_name = self.create_random_name(prefix='containerapp', length=24)

        # Construct the 'az containerapp up' command
        up_cmd = f"containerapp up -g {resource_group} -n {app_name} --environment {env_name} --image {image}"

        # Execute the 'az containerapp up' command
        self.cmd(up_cmd)

        # Verify that the Container App is running
        app = self.cmd(f"containerapp show -g {resource_group} -n {app_name}").get_output_in_json()
        url = app["properties"]["configuration"]["ingress"]["fqdn"]
        url = url if url.startswith("http") else f"http://{url}"
        resp = requests.get(url)
        self.assertTrue(resp.ok)

        # Execute and verify patch list command
        patch_cmd = f'containerapp patch list -g {resource_group} --environment {env_name} --show-all'
        output = self.cmd(patch_cmd).get_output_in_json()
        self.assertEquals(output[0]["targetImageName"],"mcr.microsoft.com/k8se/quickstart:latest")

    @live_only()
    @ResourceGroupPreparer(location = "eastus2")
    def test_containerapp_patch_list_without_arguments_e2e(self, resource_group):
        source_path = os.path.join(TEST_DIR, os.path.join("data", "source_built_using_buildpack"))
        ingress = 'external'
        target_port = '80'
        # Configure the default location
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        # Ensure that the Container App environment is created
        env_name = self.create_random_name(prefix='env', length=24)
        self.cmd(f'containerapp env create -g {resource_group} -n {env_name}')

        # Generate a name for the Container App
        app_name = self.create_random_name(prefix='containerapp', length=24)

        # Execute the 'az containerapp up' command
        self.cmd(f"containerapp up -g {resource_group} -n {app_name} --environment {env_name} --source \"{source_path}\" --ingress {ingress} --target-port {target_port}")

        # Verify that the Container App is running
        app = self.cmd(f"containerapp show -g {resource_group} -n {app_name}").get_output_in_json()
        url = app["properties"]["configuration"]["ingress"]["fqdn"]
        url = url if url.startswith("http") else f"http://{url}"
        resp = requests.get(url)
        self.assertTrue(resp.ok)

        # Verify patch list command
        client = docker.from_env()
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

        # Execute and verify patch list command
        self.cmd(f'configure --defaults group={resource_group}')
        patch_cmd = f'containerapp patch list'
        patchable_images = self.cmd(patch_cmd).get_output_in_json()
        newRunImageTag = patchable_images[0]["newRunImage"].split(':')[1]
        self.assertEquals(newRunImageTag,_utils.get_latest_buildpack_run_tag("aspnet", "7.0"))
        self.assertEquals(patchable_images[0]["oldRunImage"], old_tag)