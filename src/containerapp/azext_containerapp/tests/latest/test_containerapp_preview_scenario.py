# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import time
from time import sleep

from msrestazure.tools import parse_resource_id

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck, live_only)

from .common import (write_test_file, TEST_LOCATION, clean_up_test_file)
from .custom_preparers import ConnectedClusterPreparer
from .utils import prepare_containerapp_env_for_app_e2e_tests, create_extension_and_custom_location

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class ContainerappPreviewScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(location="eastus", random_name_length=15)
    @ConnectedClusterPreparer(location=TEST_LOCATION)
    def test_containerapp_preview_environment_type(self, resource_group, infra_cluster, connected_cluster_name):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))
        custom_location_name = "my-custom-location"
        create_extension_and_custom_location(self, resource_group, connected_cluster_name, custom_location_name)

        # create connected environment with client or create a command for connected?
        sub_id = self.cmd('az account show').get_output_in_json()['id']
        static_ip = '1.1.1.1'
        connected_env_name = 'my-connected-env'
        custom_location_id = f"/subscriptions/{sub_id}/resourceGroups/{resource_group}/providers/Microsoft.ExtendedLocation/customLocations/{custom_location_name}"
        self.cmd(f'containerapp connected-env create -g {resource_group} --name {connected_env_name} --custom-location {custom_location_name} --static-ip {static_ip} -d "InstrumentationKey=TestInstrumentationKey;IngestionEndpoint=https://ingestion.com/;LiveEndpoint=https://abc.com/" -l {TEST_LOCATION}', checks=[
            JMESPathCheck('name', connected_env_name),
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck('extendedLocation.name', custom_location_id),
            JMESPathCheck('properties.staticIp', static_ip)
        ])

        connected_env_resource_id = self.cmd(f'containerapp connected-env show -g {resource_group} --name {connected_env_name}', checks=[
            JMESPathCheck('name', connected_env_name),
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck('extendedLocation.name', custom_location_id),
            JMESPathCheck('properties.staticIp', static_ip)
        ]).get_output_in_json()['id']

        self.cmd(f'containerapp connected-env list -g {resource_group} --custom-location {custom_location_name}', expect_failure=False, checks=[
            JMESPathCheck('length(@)', 1),
            JMESPathCheck('[0].name', connected_env_name),
            JMESPathCheck('[0].properties.provisioningState', "Succeeded"),
            JMESPathCheck('[0].extendedLocation.name', custom_location_id),
            JMESPathCheck('[0].properties.staticIp', static_ip)
        ])
        ca_name1 = self.create_random_name(prefix='containerapp1', length=24)
        self.cmd(
            f'az containerapp create --name {ca_name1} --resource-group {resource_group} --environment {connected_env_name} --image "mcr.microsoft.com/k8se/quickstart:latest" --ingress external --target-port 80 --environment-type connected',
            checks=[
                JMESPathCheck('name', ca_name1),
                JMESPathCheck('properties.environmentId', connected_env_resource_id),
                JMESPathCheck('properties.provisioningState', "Succeeded")
            ])

        ca_name2 = self.create_random_name(prefix='containerapp2', length=24)
        self.cmd(
            f'az containerapp create --name {ca_name2} --resource-group {resource_group} --environment {connected_env_name} --image "mcr.microsoft.com/k8se/quickstart:latest" --environment-type connected',
            checks=[
                JMESPathCheck('name', ca_name2),
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

        self.cmd('containerapp delete -n {} -g {} --yes'.format(ca_name1, resource_group))

        self.cmd('containerapp list -g {}'.format(resource_group), checks=[
            JMESPathCheck('length(@)', 0)
        ])
        self.cmd(f'containerapp connected-env delete -g {resource_group} --name {connected_env_name} --yes', expect_failure=False)
        self.cmd(f'containerapp connected-env delete -g {resource_group} --name {connected_env_name} --yes', expect_failure=False)

        self.cmd(f'containerapp connected-env list -g {resource_group} --custom-location {custom_location_name}', expect_failure=False, checks=[
                JMESPathCheck('length(@)', 0),
        ])

    @ResourceGroupPreparer(location="eastus")
    def test_containerapp_preview_e2e(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        ca_name = self.create_random_name(prefix='containerapp', length=24)

        env_id = prepare_containerapp_env_for_app_e2e_tests(self)
        env_rg = parse_resource_id(env_id).get('resource_group')
        env_name = parse_resource_id(env_id).get('name')

        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(env_rg, env_name)).get_output_in_json()

        self.cmd(
            f'az containerapp create --name {ca_name} --resource-group {resource_group} --environment {env_id} --image "mcr.microsoft.com/k8se/quickstart:latest" --environment-type managed',
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
