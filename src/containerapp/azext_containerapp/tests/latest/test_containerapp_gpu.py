# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import time

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck, live_only)

from azext_containerapp.tests.latest.common import (write_test_file, clean_up_test_file)
from .common import TEST_LOCATION

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

class ContainerAppWorkloadProfilesGPUTest(ScenarioTest):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, random_config_dir=True, **kwargs)

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northeurope")
    def test_containerapp_create_enable_dedicated_gpu(self, resource_group):
        self.cmd('configure --defaults location={}'.format("northeurope"))
        env = self.create_random_name(prefix='gpu-env', length=24)
        gpu_default_name = "gpu"
        gpu_default_type = "NC24-A100"
        self.cmd('containerapp env create -g {} -n {} --logs-destination none --enable-dedicated-gpu'.format(
            resource_group, env), expect_failure=False, checks=[
            JMESPathCheck("name", env),
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("length(properties.workloadProfiles)", 2),
            JMESPathCheck('properties.workloadProfiles[0].name', "Consumption", case_sensitive=False),
            JMESPathCheck('properties.workloadProfiles[0].workloadProfileType', "Consumption", case_sensitive=False),
            JMESPathCheck('properties.workloadProfiles[1].name', gpu_default_name, case_sensitive=False),
            JMESPathCheck('properties.workloadProfiles[1].workloadProfileType', gpu_default_type, case_sensitive=False),
            JMESPathCheck('properties.workloadProfiles[1].maximumCount', 1),
            JMESPathCheck('properties.workloadProfiles[1].minimumCount', 0),
        ])
        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env)).get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env)).get_output_in_json()
        app1 = self.create_random_name(prefix='app1', length=24)
        self.cmd(f'containerapp create -n {app1} -g {resource_group} --image mcr.microsoft.com/azuredocs/samples-tf-mnist-demo:gpu --environment {env} -w {gpu_default_name} --min-replicas 1 --cpu 0.1 --memory 0.1', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("properties.workloadProfileName", gpu_default_name),
            JMESPathCheck('properties.template.containers[0].resources.cpu', '0.1'),
            JMESPathCheck('properties.template.containers[0].resources.memory', '0.1Gi'),
            JMESPathCheck('properties.template.containers[0].resources.gpu', '1'),
            JMESPathCheck('properties.template.scale.minReplicas', '1'),
            JMESPathCheck('properties.template.scale.maxReplicas', '10')
        ])

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="eastus2")
    def test_containerapp_create_enable_consumption_gpu(self, resource_group):
        self.cmd('configure --defaults location={}'.format("northeurope"))
        env = self.create_random_name(prefix='consumption-gpu-env', length=24)
        self.cmd('containerapp env create -g {} -n {} --logs-destination none --enable-workload-profiles'.format(
            resource_group, env), expect_failure=False, checks=[
            JMESPathCheck("name", env),
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("length(properties.workloadProfiles)", 1),
            JMESPathCheck('properties.workloadProfiles[0].name', "Consumption", case_sensitive=False),
            JMESPathCheck('properties.workloadProfiles[0].workloadProfileType', "Consumption", case_sensitive=False),
        ])
        consumption_gpu_wp_name = "Consumption-T4"

        self.cmd("az containerapp env workload-profile set -g {} -n {} --workload-profile-name {consumption_gpu_wp_name} --workload-profile-type Consumption_GPU_NC8as_T4".format(
            resource_group, env), expect_failure=False)

        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env)).get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env)).get_output_in_json()
        app1 = self.create_random_name(prefix='app1', length=24)
        self.cmd(f'containerapp create -n {app1} -g {resource_group} --image mcr.microsoft.com/azuredocs/samples-tf-mnist-demo:gpu --environment {env} -w {consumption_gpu_wp_name} --cpu 0.1 --memory 0.1 --gpu 1', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("properties.workloadProfileName", consumption_gpu_wp_name),
            JMESPathCheck('properties.template.containers[0].resources.cpu', '0.1'),
            JMESPathCheck('properties.template.containers[0].resources.memory', '0.1Gi'),
            JMESPathCheck('properties.template.containers[0].resources.gpu', '1'),
        ])
