# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import time
from time import sleep
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck, live_only)
from subprocess import run

from .common import (write_test_file, TEST_LOCATION, clean_up_test_file)
from .utils import create_containerapp_env

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class ContainerappPreviewScenarioTest(ScenarioTest):
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

    @ResourceGroupPreparer(location="eastus", random_name_length=15)
    def test_containerapp_preview_environment_type(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))
        aks_name = "my-aks-cluster"
        connected_cluster_name = "my-connected-cluster"
        custom_location_id = None
        try:
            self.cmd(f'aks create --resource-group {resource_group} --name {aks_name} --enable-aad --generate-ssh-keys --enable-cluster-autoscaler --min-count 4 --max-count 10 --node-count 4')
            self.cmd(f'aks get-credentials --resource-group {resource_group} --name {aks_name} --overwrite-existing --admin')

            self.cmd(f'connectedk8s connect --resource-group {resource_group} --name {connected_cluster_name}')
            connected_cluster = self.cmd(f'az connectedk8s show --resource-group {resource_group} --name {connected_cluster_name}').get_output_in_json()

            connected_cluster_id = connected_cluster.get('id')
            extension = self.cmd(f'az k8s-extension create'
                                 f' --resource-group {resource_group}'
                                 f' --name containerapp-ext'
                                 f' --cluster-type connectedClusters'
                                 f' --cluster-name {connected_cluster_name}'
                                 f' --extension-type "Microsoft.App.Environment" '
                                 f' --release-train stable'
                                 f' --auto-upgrade-minor-version true'
                                 f' --scope cluster'
                                 f' --release-namespace appplat-ns'
                                 f' --configuration-settings "Microsoft.CustomLocation.ServiceAccount=default"'
                                 f' --configuration-settings "appsNamespace=appplat-ns"'
                                 f' --configuration-settings "clusterName={connected_cluster_name}"'
                                 f' --configuration-settings "envoy.annotations.service.beta.kubernetes.io/azure-load-balancer-resource-group={resource_group}"').get_output_in_json()
            custom_location_name = "my-custom-location"
            custom_location_id = self.cmd(f'az customlocation create -g {resource_group} -n {custom_location_name} -l {TEST_LOCATION} --host-resource-id {connected_cluster_id} --namespace appplat-ns -c {extension["id"]}').get_output_in_json()['id']
        except Exception as e:
            pass

        # create connected environment with client or create a command for connected?
        sub_id = self.cmd('az account show').get_output_in_json()['id']

        connected_env_name = 'my-connected-env'
        connected_env_resource_id = f"/subscriptions/{sub_id}/resourceGroups/{resource_group}/providers/Microsoft.App/connectedEnvironments/{connected_env_name}"
        file = f"{resource_group}.json"
        env_payload = '{{ "location": "{location}", "extendedLocation": {{ "name": "{custom_location_id}", "type": "CustomLocation" }}, "Properties": {{}}}}' \
            .format(location=TEST_LOCATION, custom_location_id=custom_location_id)
        write_test_file(file, env_payload)
        self.cmd(f'az rest --method put --uri "{connected_env_resource_id}?api-version=2022-06-01-preview" --body "@{file}"')
        containerapp_env = self.cmd(f'az rest --method get --uri "{connected_env_resource_id}?api-version=2022-06-01-preview"').get_output_in_json()
        while containerapp_env["properties"]["provisioningState"].lower() != "succeeded":
            time.sleep(5)
            containerapp_env = self.cmd(
                f'az rest --method get --uri "{connected_env_resource_id}?api-version=2022-06-01-preview"').get_output_in_json()

        ca_name = self.create_random_name(prefix='containerapp', length=24)
        self.cmd(
            f'az containerapp create --name {ca_name} --resource-group {resource_group} --environment {connected_env_name} --image "mcr.microsoft.com/k8se/quickstart:latest" --environment-type connected',
            checks=[
                JMESPathCheck('properties.environmentId', connected_env_resource_id),
                JMESPathCheck('properties.provisioningState', "Succeeded")
            ])
        ca_name2 = self.create_random_name(prefix='containerapp', length=24)
        self.cmd(
            f'az containerapp create --name {ca_name2} --resource-group {resource_group} --environment {connected_env_resource_id} --image "mcr.microsoft.com/k8se/quickstart:latest" --environment-type connected',
            checks=[
                JMESPathCheck('properties.environmentId', connected_env_resource_id),
                JMESPathCheck('properties.provisioningState', "Succeeded")
            ])

        # test show/list/delete
        self.cmd('containerapp list -g {}'.format(resource_group), checks=[
            JMESPathCheck('length(@)', 2)
        ])

        self.cmd('containerapp list -g {} --environment-type {}'.format(resource_group, 'connected'), checks=[
            JMESPathCheck('length(@)', 2)
        ])

        self.cmd('containerapp list -g {} --environment-type {} --environment {}'.format(resource_group, 'connected', connected_env_name), checks=[
            JMESPathCheck('length(@)', 2)
        ])

        self.cmd('containerapp list -g {} --environment-type {}'.format(resource_group, 'managed'), checks=[
            JMESPathCheck('length(@)', 0)
        ])

        app2 = self.cmd('containerapp show -n {} -g {}'.format(ca_name2, resource_group)).get_output_in_json()
        self.cmd('containerapp delete --ids {} --yes'.format(app2['id']))

        self.cmd('containerapp delete -n {} -g {} --yes'.format(ca_name, resource_group))

        self.cmd('containerapp list -g {}'.format(resource_group), checks=[
            JMESPathCheck('length(@)', 0)
        ])
        clean_up_test_file(file)

    @ResourceGroupPreparer(location="eastus")
    def test_containerapp_preview_e2e(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        env_name = self.create_random_name(prefix='containerapp-env', length=24)
        ca_name = self.create_random_name(prefix='containerapp', length=24)

        create_containerapp_env(self, env_name, resource_group)

        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        self.cmd(
            f'az containerapp create --name {ca_name} --resource-group {resource_group} --environment {env_name} --image "mcr.microsoft.com/k8se/quickstart:latest" --environment-type managed',
            checks=[
                JMESPathCheck('properties.environmentId', containerapp_env['id']),
                JMESPathCheck('properties.provisioningState', "Succeeded")
            ])

        app = self.cmd(
            'containerapp show -n {} -g {}'.format(ca_name, resource_group),
            checks=[
                JMESPathCheck('properties.environmentId', containerapp_env['id']),
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('name', ca_name),
            ]
        ).get_output_in_json()

        self.cmd('containerapp list -g {}'.format(resource_group), checks=[
            JMESPathCheck('length(@)', 1)
        ])

        self.cmd('containerapp list -g {} --environment-type {}'.format(resource_group, 'managed'), checks=[
            JMESPathCheck('length(@)', 1)
        ])

        self.cmd('containerapp delete --ids {} --yes'.format(app['id']))

        self.cmd('containerapp list -g {}'.format(resource_group), checks=[
            JMESPathCheck('length(@)', 0)
        ])
