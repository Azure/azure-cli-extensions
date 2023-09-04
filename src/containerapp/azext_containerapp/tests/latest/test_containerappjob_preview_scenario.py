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
from .custom_preparers import ConnectedClusterPreparer
from .utils import create_containerapp_env

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class ContainerappJobPreviewScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(location=TEST_LOCATION, random_name_length=15)
    @ConnectedClusterPreparer(location=TEST_LOCATION)
    def test_containerappjob_preview_environment_type(self, resource_group, infra_cluster, connected_cluster_name):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))
        custom_location_name = "my-custom-location"
        try:
            connected_cluster = self.cmd(f'az connectedk8s show --resource-group {resource_group} --name {connected_cluster_name}').get_output_in_json()
            while connected_cluster["connectivityStatus"] == "Connecting":
                time.sleep(5)
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

            self.cmd(f'az customlocation create -g {resource_group} -n {custom_location_name} -l {TEST_LOCATION} --host-resource-id {connected_cluster_id} --namespace appplat-ns -c {extension["id"]}')
        except:
            pass

        # create connected environment with client or create a command for connected?
        sub_id = self.cmd('az account show').get_output_in_json()['id']

        connected_env_name = 'my-connected-env'
        connected_env_resource_id = f"/subscriptions/{sub_id}/resourceGroups/{resource_group}/providers/Microsoft.App/connectedEnvironments/{connected_env_name}"
        custom_location_id = f"/subscriptions/{sub_id}/resourceGroups/{resource_group}/providers/Microsoft.ExtendedLocation/customLocations/{custom_location_name}"
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
            f"az containerapp job create --name {ca_name} --resource-group {resource_group} --environment {connected_env_name} --environment-type connected --replica-timeout 200 --replica-retry-limit 2 --trigger-type manual --parallelism 1 --replica-completion-count 1 --image mcr.microsoft.com/k8se/quickstart-jobs:latest --cpu '0.25' --memory '0.5Gi'",
            checks=[
                JMESPathCheck('properties.environmentId', connected_env_resource_id),
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('properties.configuration.replicaTimeout', 200),
                JMESPathCheck('properties.configuration.replicaRetryLimit', 2),
                JMESPathCheck('properties.configuration.triggerType', "manual", case_sensitive=False),
            ])
        ca_name2 = self.create_random_name(prefix='containerapp', length=24)
        self.cmd(
            f"az containerapp job create --name {ca_name2} --resource-group {resource_group} --environment {connected_env_resource_id} --replica-timeout 200 --replica-retry-limit 2 --trigger-type manual --parallelism 1 --replica-completion-count 1 --image mcr.microsoft.com/k8se/quickstart-jobs:latest --cpu '0.25' --memory '0.5Gi'",
            checks=[
                JMESPathCheck('properties.environmentId', connected_env_resource_id),
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('properties.configuration.replicaTimeout', 200),
                JMESPathCheck('properties.configuration.replicaRetryLimit', 2),
                JMESPathCheck('properties.configuration.triggerType', "manual", case_sensitive=False),
            ])

        # test show/list/delete
        self.cmd('containerapp job list -g {}'.format(resource_group), checks=[
            JMESPathCheck('length(@)', 2)
        ])

        self.cmd('containerapp list -g {} --environment-type {}'.format(resource_group, 'managed'), checks=[
            JMESPathCheck('length(@)', 0)
        ])

        app2 = self.cmd('containerapp job show -n {} -g {}'.format(ca_name2, resource_group)).get_output_in_json()
        self.cmd('containerapp job delete --ids {} --yes'.format(app2['id']))

        self.cmd('containerapp job delete -n {} -g {} --yes'.format(ca_name, resource_group))

        self.cmd('containerapp job list -g {}'.format(resource_group), checks=[
            JMESPathCheck('length(@)', 0)
        ])
        clean_up_test_file(file)

    @ResourceGroupPreparer(location="eastus")
    def test_containerappjob_preview_e2e(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        env_name = self.create_random_name(prefix='containerapp-env', length=24)
        ca_name = self.create_random_name(prefix='containerapp', length=24)

        create_containerapp_env(self, env_name, resource_group)

        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        self.cmd(
            f"az containerapp job create --name {ca_name} --resource-group {resource_group} --environment {env_name} --replica-timeout 200 --replica-retry-limit 2 --trigger-type manual --parallelism 1 --replica-completion-count 1 --image mcr.microsoft.com/k8se/quickstart-jobs:latest --cpu '0.25' --memory '0.5Gi' --environment-type managed",
            checks=[
                JMESPathCheck('properties.environmentId', containerapp_env['id']),
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('properties.configuration.replicaTimeout', 200),
                JMESPathCheck('properties.configuration.replicaRetryLimit', 2),
                JMESPathCheck('properties.configuration.triggerType', "manual", case_sensitive=False),
            ])

        app = self.cmd(
            'containerapp job show -n {} -g {}'.format(ca_name, resource_group),
            checks=[
                JMESPathCheck('properties.environmentId', containerapp_env['id']),
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('name', ca_name),
            ]
        ).get_output_in_json()

        self.cmd('containerapp job list -g {}'.format(resource_group), checks=[
            JMESPathCheck('length(@)', 1)
        ])

        self.cmd('containerapp job delete --ids {} --yes'.format(app['id']))

        self.cmd('containerapp job list -g {}'.format(resource_group), checks=[
            JMESPathCheck('length(@)', 0)
        ])
