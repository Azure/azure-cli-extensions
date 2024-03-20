# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.command_modules.containerapp._utils import format_location
from msrestazure.tools import parse_resource_id

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck)

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

from .common import TEST_LOCATION, STAGE_LOCATION
from .utils import prepare_containerapp_env_for_app_e2e_tests


class ContainerAppJobsCRUDOperationsTest(ScenarioTest):
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northcentralus")
    # test for CRUD operations on Container App Job resource with trigger type as manual
    def test_containerapp_manualjob_crudoperations_e2e(self, resource_group):
        
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        job = self.create_random_name(prefix='job1', length=24)

        env_id = prepare_containerapp_env_for_app_e2e_tests(self)
        env_rg = parse_resource_id(env_id).get('resource_group')
        env_name = parse_resource_id(env_id).get('name')

        # create a container app environment for a Container App Job resource
        self.cmd('containerapp env show -n {} -g {}'.format(env_name, env_rg), checks=[
            JMESPathCheck('name', env_name)
        ])

        ## test for CRUD operations on Container App Job resource with trigger type as manual
        # create a Container App Job resource with trigger type as manual
        self.cmd("az containerapp job create --resource-group {} --name {} --environment {} --replica-timeout 200 --replica-retry-limit 2 --trigger-type manual --parallelism 1 --replica-completion-count 1 --image mcr.microsoft.com/k8se/quickstart-jobs:latest --cpu '0.25' --memory '0.5Gi'".format(resource_group, job, env_id))

        # verify the container app job resource
        self.cmd("az containerapp job show --resource-group {} --name {}".format(resource_group, job), checks=[
            JMESPathCheck('name', job),
            JMESPathCheck('properties.configuration.replicaTimeout', 200),
            JMESPathCheck('properties.configuration.replicaRetryLimit', 2),
            JMESPathCheck('properties.configuration.triggerType', "manual", case_sensitive=False),
        ])

        # get list of Container App Jobs
        jobs_list = self.cmd("az containerapp job list --resource-group {}".format(resource_group)).get_output_in_json()
        self.assertTrue(len(jobs_list) == 1)

        # update the Container App Job resource
        self.cmd("az containerapp job update --resource-group {} --name {} --replica-timeout 300 --replica-retry-limit 1 --image mcr.microsoft.com/k8se/quickstart-jobs:latest --cpu '0.5' --memory '1.0Gi'".format(resource_group, job), checks=[
            JMESPathCheck('name', job),
            JMESPathCheck('properties.configuration.replicaTimeout', 300),
            JMESPathCheck('properties.configuration.replicaRetryLimit', 1),
            JMESPathCheck('properties.configuration.triggerType', "manual", case_sensitive=False),
            JMESPathCheck('properties.template.containers[0].image', "mcr.microsoft.com/k8se/quickstart-jobs:latest"),
            JMESPathCheck('properties.template.containers[0].resources.cpu', "0.5"),
            JMESPathCheck('properties.template.containers[0].resources.memory', "1Gi"),
        ])

        # verify the updated Container App Job resource
        self.cmd("az containerapp job show --resource-group {} --name {}".format(resource_group, job), checks=[
            JMESPathCheck('name', job),
            JMESPathCheck('properties.configuration.replicaTimeout', 300),
            JMESPathCheck('properties.configuration.replicaRetryLimit', 1),
            JMESPathCheck('properties.configuration.triggerType', "manual", case_sensitive=False),
            JMESPathCheck('properties.template.containers[0].image', "mcr.microsoft.com/k8se/quickstart-jobs:latest"),
            JMESPathCheck('properties.template.containers[0].resources.cpu', "0.5"),
            JMESPathCheck('properties.template.containers[0].resources.memory', "1Gi"),
        ])

        # delete the Container App Job resource
        self.cmd("az containerapp job delete --resource-group {} --name {} --yes".format(resource_group, job))

        # verify the Container App Job resource is deleted
        jobs_list = self.cmd("az containerapp job list --resource-group {}".format(resource_group)).get_output_in_json()
        self.assertTrue(len(jobs_list) == 0)
        
        ## test for CRUD operations on Container App Job resource with trigger type as schedule
        job2 = self.create_random_name(prefix='job2', length=24)

        # create a Container App Job resource with trigger type as schedule
        self.cmd("az containerapp job create --resource-group {} --name {} --environment {} --replica-timeout 200 --replica-retry-limit 2 --trigger-type schedule --parallelism 1 --replica-completion-count 1 --cron-expression '*/5 * * * *' --image mcr.microsoft.com/k8se/quickstart-jobs:latest --cpu '0.25' --memory '0.5Gi'".format(resource_group, job2, env_id))

        # verify the container app job resource
        self.cmd("az containerapp job show --resource-group {} --name {}".format(resource_group, job2), checks=[
            JMESPathCheck('name', job2),
            JMESPathCheck('properties.configuration.replicaTimeout', 200),
            JMESPathCheck('properties.configuration.replicaRetryLimit', 2),
            JMESPathCheck('properties.configuration.triggerType', "schedule", case_sensitive=False),
            JMESPathCheck('properties.configuration.scheduleTriggerConfig.cronExpression', "*/5 * * * *"),
        ])

        # get list of Container App Jobs
        jobs_list = self.cmd("az containerapp job list --resource-group {}".format(resource_group)).get_output_in_json()
        self.assertTrue(len(jobs_list) == 1)

        # update the Container App Job resource
        self.cmd("az containerapp job update --resource-group {} --name {} --replica-timeout 300 --replica-retry-limit 1 --cron-expression '*/10 * * * *' --image mcr.microsoft.com/k8se/quickstart-jobs:latest --cpu '0.5' --memory '1.0Gi'".format(resource_group, job2))

        # verify the updated Container App Job resource
        self.cmd("az containerapp job show --resource-group {} --name {}".format(resource_group, job2), checks=[
            JMESPathCheck('name', job2),
            JMESPathCheck('properties.configuration.replicaTimeout', 300),
            JMESPathCheck('properties.configuration.replicaRetryLimit', 1),
            JMESPathCheck('properties.configuration.triggerType', "schedule", case_sensitive=False),
            JMESPathCheck('properties.configuration.scheduleTriggerConfig.cronExpression', "*/10 * * * *"),
            JMESPathCheck('properties.template.containers[0].image', "mcr.microsoft.com/k8se/quickstart-jobs:latest"),
            JMESPathCheck('properties.template.containers[0].resources.cpu', "0.5"),
            JMESPathCheck('properties.template.containers[0].resources.memory', "1Gi"),
        ])

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="westeurope")
    def test_containerapp_manualjob_private_registry_port(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))
        acr = self.create_random_name(prefix='acr', length=24)
        image_source = "mcr.microsoft.com/k8se/quickstart:latest"

        env_id = prepare_containerapp_env_for_app_e2e_tests(self)
        acr_location = TEST_LOCATION
        if format_location(acr_location) == format_location(STAGE_LOCATION):
            acr_location = "eastus"
        self.cmd(f'acr create --sku basic -n {acr} -g {resource_group} --admin-enabled -l {acr_location}')
        self.cmd(f'acr import -n {acr} --source {image_source}')
        password = self.cmd(f'acr credential show -n {acr} --query passwords[0].value').get_output_in_json()

        app = self.create_random_name(prefix='aca1', length=24)
        image_name = f"{acr}.azurecr.io:443/k8se/quickstart:latest"

        self.cmd(f"containerapp job create -g {resource_group} -n {app} --image {image_name} --environment {env_id} --registry-server {acr}.azurecr.io:443 --registry-username {acr} --registry-password {password} --replica-timeout 200 --replica-retry-limit 2 --trigger-type schedule --parallelism 1 --replica-completion-count 1 --cron-expression '*/10 * * * *' ")

        self.cmd(f'containerapp job show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("properties.configuration.registries[0].server", f"{acr}.azurecr.io:443"),
            JMESPathCheck("properties.template.containers[0].image", image_name),
            JMESPathCheck("properties.configuration.secrets[0].name", f"{acr}azurecrio-443-{acr}")
        ])

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="westeurope")
    def test_containerapp_manualjob_registry_acr_look_up_credentical(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))
        app = self.create_random_name(prefix='aca', length=24)
        acr = self.create_random_name(prefix='acr', length=24)
        image_source = "mcr.microsoft.com/k8se/quickstart:latest"
        image_name = f"{acr}.azurecr.io:443/k8se/quickstart:latest"

        env_id = prepare_containerapp_env_for_app_e2e_tests(self)
        acr_location = TEST_LOCATION
        if format_location(acr_location) == format_location(STAGE_LOCATION):
            acr_location = "eastus"
        self.cmd(f'acr create --sku basic -n {acr} -g {resource_group} --admin-enabled -l {acr_location}')
        self.cmd(f'acr import -n {acr} --source {image_source}')
        password = self.cmd(f'acr credential show -n {acr} --query passwords[0].value').get_output_in_json()

        app = self.create_random_name(prefix='aca1', length=24)
        image_name = f"{acr}.azurecr.io/k8se/quickstart:latest"

        self.cmd(
            f"containerapp job create -g {resource_group} -n {app} --image {image_name} --environment {env_id} --registry-server {acr}.azurecr.io --replica-timeout 200 --replica-retry-limit 2 --trigger-type schedule --parallelism 1 --replica-completion-count 1 --cron-expression '*/10 * * * *' ")

        self.cmd(f'containerapp job show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("properties.configuration.registries[0].server", f"{acr}.azurecr.io"),
            JMESPathCheck("properties.template.containers[0].image", image_name),
            JMESPathCheck("properties.configuration.secrets[0].name", f"{acr}azurecrio-{acr}")
        ])

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northcentralus")
    # test for CRUD operations on Container App Job resource with trigger type as manual
    def test_containerapp_eventjob_defaults_e2e(self, resource_group): 
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        job = self.create_random_name(prefix='job3', length=24)

        env_id = prepare_containerapp_env_for_app_e2e_tests(self)

        ## test for CRUD operations on Container App Job resource with trigger type as manual
        # create a Container App Job resource with trigger type as manual
        self.cmd("az containerapp job create --resource-group {} --name {} --environment {} --trigger-type event --scale-rule-name 'queue' --scale-rule-type 'azure-queue' --scale-rule-metadata 'accountName=containerappextension' 'queueName=testeventdrivenjobs' 'queueLength=1' 'connectionFromEnv=AZURE_STORAGE_CONNECTION_STRING' --scale-rule-auth 'connection=connection-string-secret' --secrets 'connection-string-secret=testConnString' --env-vars 'AZURE_STORAGE_QUEUE_NAME=testeventdrivenjobs' 'AZURE_STORAGE_CONNECTION_STRING=secretref:connection-string-secret'".format(resource_group, job, env_id))

        # verify the container app job resource
        self.cmd("az containerapp job show --resource-group {} --name {}".format(resource_group, job), checks=[
            JMESPathCheck('name', job),
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck('properties.configuration.replicaTimeout', 1800),
            JMESPathCheck('properties.configuration.replicaRetryLimit', 0),
            JMESPathCheck('properties.configuration.eventTriggerConfig.parallelism', 1),
            JMESPathCheck('properties.configuration.eventTriggerConfig.replicaCompletionCount', 1),
            JMESPathCheck('properties.configuration.eventTriggerConfig.scale.minExecutions', 0),
            JMESPathCheck('properties.configuration.eventTriggerConfig.scale.maxExecutions', 100),
            JMESPathCheck('properties.configuration.eventTriggerConfig.scale.pollingInterval', 30),
            JMESPathCheck('properties.configuration.triggerType', "event", case_sensitive=False),
        ])

        # delete the Container App Job resource
        self.cmd("az containerapp job delete --resource-group {} --name {} --yes".format(resource_group, job))

        # verify the Container App Job resource is deleted
        jobs_list = self.cmd("az containerapp job list --resource-group {}".format(resource_group)).get_output_in_json()
        self.assertTrue(len(jobs_list) == 0)

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northcentralus")
    # test for CRUD operations on Container App Job resource with trigger type as manual
    def test_containerapp_manualjob_defaults_e2e(self, resource_group): 
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        job = self.create_random_name(prefix='job4', length=24)

        env_id = prepare_containerapp_env_for_app_e2e_tests(self)

        ## test for CRUD operations on Container App Job resource with trigger type as manual
        # create a Container App Job resource with trigger type as manual
        self.cmd("az containerapp job create --resource-group {} --name {} --environment {} --trigger-type manual".format(resource_group, job, env_id))

        # verify the container app job resource
        self.cmd("az containerapp job show --resource-group {} --name {}".format(resource_group, job), checks=[
            JMESPathCheck('name', job),
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck('properties.configuration.replicaTimeout', 1800),
            JMESPathCheck('properties.configuration.replicaRetryLimit', 0),
            JMESPathCheck('properties.configuration.manualTriggerConfig.parallelism', 1),
            JMESPathCheck('properties.configuration.manualTriggerConfig.replicaCompletionCount', 1),
            JMESPathCheck('properties.configuration.triggerType', "manual", case_sensitive=False),
        ])

        # delete the Container App Job resource
        self.cmd("az containerapp job delete --resource-group {} --name {} --yes".format(resource_group, job))

        # verify the Container App Job resource is deleted
        jobs_list = self.cmd("az containerapp job list --resource-group {}".format(resource_group)).get_output_in_json()
        self.assertTrue(len(jobs_list) == 0)

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northcentralus")
    # test for CRUD operations on Container App Job resource with trigger type as manual
    def test_containerapp_cronjob_defaults_e2e(self, resource_group): 
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        job = self.create_random_name(prefix='job5', length=24)

        env_id = prepare_containerapp_env_for_app_e2e_tests(self)

        ## test for CRUD operations on Container App Job resource with trigger type as manual
        # create a Container App Job resource with trigger type as manual
        self.cmd("az containerapp job create --resource-group {} --name {} --environment {} --trigger-type schedule --cron-expression \"*/1 * * * *\" ".format(resource_group, job, env_id))

        # verify the container app job resource
        self.cmd("az containerapp job show --resource-group {} --name {}".format(resource_group, job), checks=[
            JMESPathCheck('name', job),
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck('properties.configuration.replicaTimeout', 1800),
            JMESPathCheck('properties.configuration.replicaRetryLimit', 0),
            JMESPathCheck('properties.configuration.scheduleTriggerConfig.parallelism', 1),
            JMESPathCheck('properties.configuration.scheduleTriggerConfig.replicaCompletionCount', 1),
            JMESPathCheck('properties.configuration.triggerType', "schedule", case_sensitive=False),
        ])

        # delete the Container App Job resource
        self.cmd("az containerapp job delete --resource-group {} --name {} --yes".format(resource_group, job))

        # verify the Container App Job resource is deleted
        jobs_list = self.cmd("az containerapp job list --resource-group {}".format(resource_group)).get_output_in_json()
        self.assertTrue(len(jobs_list) == 0)
        
        

