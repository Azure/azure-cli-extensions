# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import time

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck, live_only, StorageAccountPreparer)

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

from azext_containerapp.tests.latest.common import TEST_LOCATION
from .utils import create_containerapp_env

class ContainerAppJobsExecutionsTest(ScenarioTest):
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northcentralus")
    def test_containerapp_job_executionstest_e2e(self, resource_group):
        import requests
        
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        env = self.create_random_name(prefix='env', length=24)
        job = self.create_random_name(prefix='job2', length=24)

        create_containerapp_env(self, env, resource_group)

        # create a container app environment for a Container App Job resource
        self.cmd('containerapp env show -n {} -g {}'.format(env, resource_group), checks=[
            JMESPathCheck('name', env)            
        ])

        # create a Container App Job resource
        self.cmd("az containerapp job create --resource-group {} --name {} --environment {} --replica-timeout 200 --replica-retry-limit 1 --trigger-type manual --replica-completion-count 1 --parallelism 1 --image mcr.microsoft.com/k8se/quickstart:latest --cpu '0.25' --memory '0.5Gi'".format(resource_group, job, env))

        # wait for 60s for the job to be provisioned
        jobProvisioning = True
        timeout = time.time() + 60*1   # 1 minutes from now
        while(jobProvisioning):
            jobProvisioning = self.cmd("az containerapp job show --resource-group {} --name {}".format(resource_group, job)).get_output_in_json()['properties']['provisioningState'] != "Succeeded"
            if(time.time() > timeout):
                break

        # start the job execution
        execution = self.cmd("az containerapp job start --resource-group {} --name {}".format(resource_group, job)).get_output_in_json()
        if "id" in execution:
            # check if the job execution id is in the response
            self.assertEqual(job in execution['id'], True)
        if "name" in execution:
            # check if the job execution name is in the response
            self.assertEqual(job in execution['name'], True)

        # get list of all executions for the job
        executionList = self.cmd("az containerapp job execution list --resource-group {} --name {}".format(resource_group, job)).get_output_in_json()
        self.assertTrue(len(executionList) == 1)
        
        # get single execution for the job
        singleExecution = self.cmd("az containerapp job execution show --resource-group {} --name {} --job-execution-name {}".format(resource_group, job, execution['name'])).get_output_in_json()
        self.assertEqual(job in singleExecution['name'], True)