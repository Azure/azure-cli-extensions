# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from subprocess import run
from time import sleep

from azure.cli.command_modules.containerapp._utils import format_location

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, live_only, JMESPathCheck,
                               LogAnalyticsWorkspacePreparer)

from .common import TEST_LOCATION, STAGE_LOCATION
from .utils import create_extension_and_custom_location

from .custom_preparers import ConnectedClusterPreparer


class ContainerAppUpConnectedEnvImageTest(ScenarioTest):
    def __init__(self, method_name, config_file=None, recording_name=None, recording_processors=None,
                 replay_processors=None, recording_patches=None, replay_patches=None, random_config_dir=False):

        super().__init__(method_name, config_file, recording_name, recording_processors, replay_processors,
                         recording_patches, replay_patches, random_config_dir)
        cmd = ['azdev', 'extension', 'add', 'connectedk8s']
        run(cmd, check=True)
        cmd = ['azdev', 'extension', 'add', 'k8s-extension']
        run(cmd, check=True)
        # Wait for extensions to be installed
        # We mock time.sleep in azure-sdk-tools, that's why we need to use sleep here.
        sleep(120)

    # If the process contains create_extension, it contains _generate_log_analytics_if_not_provided, which cause playback failed.
    # If the process contains create custom location, it will use a random name, which will cause playback failed too.
    # So prepare extension and custom location before execute the `up` command
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="eastus", random_name_length=15)
    @ConnectedClusterPreparer(location=TEST_LOCATION)
    def test_containerapp_up_on_arc_e2e(self, resource_group, connected_cluster_name):
        connected_cluster = self.cmd(
            f'az connectedk8s show --resource-group {resource_group} --name {connected_cluster_name}').get_output_in_json()
        custom_location_name = self.create_random_name(prefix="my-custom-location", length=24)
        create_extension_and_custom_location(self, resource_group, connected_cluster_name, custom_location_name)
        sub_id = self.cmd('az account show').get_output_in_json()['id']
        custom_location_id = f"/subscriptions/{sub_id}/resourceGroups/{resource_group}/providers/Microsoft.ExtendedLocation/customLocations/{custom_location_name}"
        connected_cluster_id = connected_cluster['id']
        app_name = self.create_random_name(prefix='app1', length=24)
        image = 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'

        # -n {appname} --connected-cluster-id
        self.cmd(f'containerapp up -n {app_name} -g {resource_group} --connected-cluster-id {connected_cluster_id} --image {image}')
        env_list = self.cmd(f'containerapp connected-env list -g {resource_group}').get_output_in_json()
        self.assertEqual(env_list[0]["extendedLocation"]["name"].lower(), custom_location_id.lower())
        if format_location(connected_cluster["location"]) == format_location('eastus2euap'):
            self.assertEqual(format_location(env_list[0]["location"]), format_location(TEST_LOCATION))
        else:
            self.assertEqual(format_location(env_list[0]["location"]), format_location(connected_cluster["location"]))
        env_id = env_list[0]["id"]
        env_name = env_list[0]["name"]
        self._validate_app(resource_group, app_name, custom_location_id, env_id)

        # -n {appname}
        self.cmd(f'containerapp up -n {app_name} -g {resource_group} --image {image}', expect_failure=False)
        self._validate_app(resource_group, app_name, custom_location_id, env_id)

        # -n {appname} --environment {env_name}
        app_name = 'mycontainerapp2'
        self.cmd(f'containerapp up -n {app_name} -g {resource_group} --environment {env_id} --image {image}',
                 expect_failure=False)
        self._validate_app(resource_group, app_name, custom_location_id, env_id)

        # -n {appname} --environment {env_id}
        self.cmd(f'containerapp up -n {app_name} -g {resource_group} --environment {env_name} --image {image}',
                 expect_failure=False)
        self._validate_app(resource_group, app_name, custom_location_id, env_id)

        # -n {appname} --connected-cluster-id --environment {env_name}
        self.cmd(
            f'containerapp up -n {app_name} -g {resource_group} --connected-cluster-id {connected_cluster_id} --environment {env_id} --image {image}',
            expect_failure=False)
        self._validate_app(resource_group, app_name, custom_location_id, env_id)

        # -n {appname} --connected-cluster-id --environment {env_id}
        self.cmd(
            f'containerapp up -n {app_name} -g {resource_group} --connected-cluster-id {connected_cluster_id} --environment {env_name} --image {image}',
            expect_failure=False)
        self._validate_app(resource_group, app_name, custom_location_id, env_id)

        # -n {appname} --custom-location
        app_name = 'mycontainerapp3'
        self.cmd(
            f'containerapp up -n {app_name} -g {resource_group} --custom-location {custom_location_id} --image {image}',
            expect_failure=False)
        self._validate_app(resource_group, app_name, custom_location_id, env_id)

        # -n {appname} --custom-location --environment {env_id}
        self.cmd(
            f'containerapp up -n {app_name} -g {resource_group} --custom-location {custom_location_id} --environment {env_id} --image {image}',
            expect_failure=False)
        self._validate_app(resource_group, app_name, custom_location_id, env_id)

        # -n {appname} --custom-location --environment {env_name}
        self.cmd(
            f'containerapp up -n {app_name} -g {resource_group} --custom-location {custom_location_id} --environment {env_name} --image {image}',
            expect_failure=False)
        self._validate_app(resource_group, app_name, custom_location_id, env_id)

    @live_only()
    @ResourceGroupPreparer(location="eastus", random_name_length=15)
    @ConnectedClusterPreparer(location=TEST_LOCATION)
    def test_containerapp_up_on_arc_auto_install_extension_e2e(self, resource_group, connected_cluster_name):
        connected_cluster = self.cmd(f'az connectedk8s show --resource-group {resource_group} --name {connected_cluster_name}').get_output_in_json()
        connected_cluster_id = connected_cluster['id']
        app_name = 'mycontainerapp'
        image = 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'

        # -n {appname} --connected-cluster-id
        self.cmd(f'containerapp up -n {app_name} -g {resource_group} --connected-cluster-id {connected_cluster_id} --image {image}', expect_failure=False)

        extension_type = 'microsoft.app.environment'
        installed_exts = self.cmd(f'k8s-extension list -c {connected_cluster_name} -g {resource_group} --cluster-type connectedClusters').get_output_in_json()
        found_extension = False
        for item in installed_exts:
            if item['extensionType'] == extension_type:
                self.assertEqual(item["provisioningState"], "Succeeded")
                found_extension = True
                break
        self.assertTrue(found_extension)
        custom_location_list = self.cmd('customlocation list').get_output_in_json()
        custom_location_id = None
        for custom_location in custom_location_list:
            if custom_location["hostResourceId"] == connected_cluster_id:
                self.assertEqual(custom_location["provisioningState"], "Succeeded")
                custom_location_id = custom_location["id"]
                break
        self.assertIsNotNone(custom_location_id)
        env_list = self.cmd(f'containerapp connected-env list -g {resource_group}').get_output_in_json()
        self.assertEqual(env_list[0]["extendedLocation"]["name"].lower(), custom_location_id.lower())
        if format_location(connected_cluster["location"]) == format_location('eastus2euap'):
            self.assertEqual(format_location(env_list[0]["location"]), format_location(TEST_LOCATION))
        else:
            self.assertEqual(format_location(env_list[0]["location"]), format_location(connected_cluster["location"]))
        env_id = env_list[0]["id"]
        env_name = env_list[0]["name"]

        self._validate_app(resource_group, app_name, custom_location_id, env_id)

        # -n {appname}
        self.cmd(f'containerapp up -n {app_name} -g {resource_group} --image {image}', expect_failure=False)
        self._validate_app(resource_group, app_name, custom_location_id, env_id)

        # -n {appname} --environment {env_name}
        app_name = 'mycontainerapp2'
        self.cmd(f'containerapp up -n {app_name} -g {resource_group} --environment {env_id} --image {image}', expect_failure=False)
        self._validate_app(resource_group, app_name, custom_location_id, env_id)

        # -n {appname} --environment {env_id}
        self.cmd(f'containerapp up -n {app_name} -g {resource_group} --environment {env_name} --image {image}', expect_failure=False)
        self._validate_app(resource_group, app_name, custom_location_id, env_id)

        # -n {appname} --connected-cluster-id --environment {env_name}
        self.cmd(f'containerapp up -n {app_name} -g {resource_group} --connected-cluster-id {connected_cluster_id} --environment {env_id} --image {image}', expect_failure=False)
        self._validate_app(resource_group, app_name, custom_location_id, env_id)

        # -n {appname} --connected-cluster-id --environment {env_id}
        self.cmd(f'containerapp up -n {app_name} -g {resource_group} --connected-cluster-id {connected_cluster_id} --environment {env_name} --image {image}', expect_failure=False)
        self._validate_app(resource_group, app_name, custom_location_id, env_id)

        # -n {appname} --custom-location
        app_name = 'mycontainerapp3'
        self.cmd(f'containerapp up -n {app_name} -g {resource_group} --custom-location {custom_location_id} --image {image}', expect_failure=False)
        self._validate_app(resource_group, app_name, custom_location_id, env_id)

        # -n {appname} --custom-location --environment {env_id}
        self.cmd(f'containerapp up -n {app_name} -g {resource_group} --custom-location {custom_location_id} --environment {env_id} --image {image}', expect_failure=False)
        self._validate_app(resource_group, app_name, custom_location_id, env_id)

        # -n {appname} --custom-location --environment {env_name}
        self.cmd(f'containerapp up -n {app_name} -g {resource_group} --custom-location {custom_location_id} --environment {env_name} --image {image}', expect_failure=False)
        self._validate_app(resource_group, app_name, custom_location_id, env_id)

    def _validate_app(self, resource_group, app_name, custom_location_id, environment_id):
        app = self.cmd(f"containerapp show -g {resource_group} -n {app_name}").get_output_in_json()
        self.assertEqual(app["extendedLocation"]["name"].lower(), custom_location_id.lower())
        self.assertEqual(app["properties"]["environmentId"].lower(), environment_id.lower())
        self.assertEqual(app["properties"]["provisioningState"], "Succeeded")
