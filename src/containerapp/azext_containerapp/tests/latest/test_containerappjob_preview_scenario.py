# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from msrestazure.tools import parse_resource_id

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck)

from azure.cli.testsdk.decorators import serial_test
from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from .common import TEST_LOCATION
from .custom_preparers import ConnectedClusterPreparer
from .utils import create_extension_and_custom_location, prepare_containerapp_env_for_app_e2e_tests

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class ContainerappJobPreviewScenarioTest(ScenarioTest):
    @serial_test()
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="eastus", random_name_length=15)
    @ConnectedClusterPreparer(location=TEST_LOCATION)
    def test_containerappjob_preview_environment_type(self, resource_group, infra_cluster, connected_cluster_name):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))
        custom_location_name = "my-custom-location"
        create_extension_and_custom_location(self, resource_group, connected_cluster_name, custom_location_name)

        # create connected environment with client or create a command for connected?
        sub_id = self.cmd('az account show').get_output_in_json()['id']

        connected_env_name = 'my-connected-env'
        connected_env_resource_id = f"/subscriptions/{sub_id}/resourceGroups/{resource_group}/providers/Microsoft.App/connectedEnvironments/{connected_env_name}"
        custom_location_id = f"/subscriptions/{sub_id}/resourceGroups/{resource_group}/providers/Microsoft.ExtendedLocation/customLocations/{custom_location_name}"
        self.cmd(f'containerapp connected-env create -g {resource_group} --name {connected_env_name} --custom-location {custom_location_name} -l {TEST_LOCATION}', checks=[
               JMESPathCheck('name', connected_env_name),
               JMESPathCheck('properties.provisioningState', "Succeeded"),
               JMESPathCheck('extendedLocation.name', custom_location_id)
        ])

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

    @ResourceGroupPreparer(location="eastus")
    def test_containerappjob_preview_e2e(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        ca_name = self.create_random_name(prefix='containerapp', length=24)

        env_id = prepare_containerapp_env_for_app_e2e_tests(self)
        env_rg = parse_resource_id(env_id).get('resource_group')
        env_name = parse_resource_id(env_id).get('name')

        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(env_rg, env_name)).get_output_in_json()

        self.cmd(
            f"az containerapp job create --name {ca_name} --resource-group {resource_group} --environment {env_id} --replica-timeout 200 --replica-retry-limit 2 --trigger-type manual --parallelism 1 --replica-completion-count 1 --image mcr.microsoft.com/k8se/quickstart-jobs:latest --cpu '0.25' --memory '0.5Gi' --environment-type managed",
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
