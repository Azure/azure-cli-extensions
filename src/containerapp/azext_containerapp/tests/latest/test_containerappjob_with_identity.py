# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.command_modules.containerapp._utils import format_location
from msrestazure.tools import parse_resource_id
from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck, JMESPathCheckExists, JMESPathCheckNotExists)

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

from .common import TEST_LOCATION, STAGE_LOCATION
from .utils import prepare_containerapp_env_for_app_e2e_tests
import time


class ContainerAppJobsCRUDOperationsTest(ScenarioTest):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, random_config_dir=True, **kwargs)

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northcentralus")
    # test for CRUD operations on Container App Job resource with trigger type as manual
    def test_containerapp_manualjob_withidentity_crudoperations_e2e(self, resource_group):
        # MSI is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use eastus as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))

        job = self.create_random_name(prefix='job1', length=24)

        env_id = prepare_containerapp_env_for_app_e2e_tests(self, location)
        env_rg = parse_resource_id(env_id).get('resource_group')
        env_name = parse_resource_id(env_id).get('name')

        # create a container app environment for a Container App Job resource
        self.cmd('containerapp env show -n {} -g {}'.format(env_name, env_rg), checks=[
            JMESPathCheck('name', env_name)
        ])

        ## test for CRUD operations on Container App Job resource with trigger type as manual
        # create a Container App Job resource with trigger type as manual and with a system assigned identity
        self.cmd("az containerapp job create --resource-group {} --name {} --environment {} --secrets 'testsecret=testsecretvalue' --replica-timeout 200 --replica-retry-limit 2 --trigger-type manual --parallelism 1 --replica-completion-count 1 --image mcr.microsoft.com/k8se/quickstart-jobs:latest --cpu '0.25' --memory '0.5Gi' --system-assigned".format(resource_group, job, env_id))

        # verify the container app job resource contains system identity
        self.cmd("az containerapp job show --resource-group {} --name {}".format(resource_group, job), checks=[
            JMESPathCheck('name', job),
            JMESPathCheck('properties.configuration.replicaTimeout', 200),
            JMESPathCheck('properties.configuration.replicaRetryLimit', 2),
            JMESPathCheck('properties.configuration.triggerType', "manual", case_sensitive=False),
            JMESPathCheck('identity.type', "SystemAssigned", case_sensitive=False),
            JMESPathCheckExists('identity.principalId'),
            JMESPathCheckExists('identity.tenantId'),
        ])

        # get list of Container App Jobs secrets
        self.cmd("az containerapp job identity show --resource-group {} --name {}".format(resource_group, job), checks=[
            JMESPathCheck('type', "SystemAssigned", case_sensitive=False),
            JMESPathCheckExists('principalId'),
            JMESPathCheckExists('tenantId'),
        ])

        # create a user assigned identity
        user_identity_name = self.create_random_name(prefix='containerappjob-user', length=24)
        user_identity = self.cmd('identity create -g {} -n {}'.format(resource_group, user_identity_name)).get_output_in_json()
        user_identity_id = user_identity['id']

        # assign user identity to container app job
        self.cmd("az containerapp job identity assign --resource-group {} --name {} --user-assigned '{}'".format(resource_group, job, user_identity_id), checks=[
            JMESPathCheck('type', "SystemAssigned, UserAssigned", case_sensitive=False),
            JMESPathCheckExists('principalId'),
            JMESPathCheckExists('tenantId'),
            JMESPathCheckExists('userAssignedIdentities'),
        ])

        # Remove user assigned identity from container app job
        self.cmd("az containerapp job identity remove --resource-group {} --name {} --user-assigned '{}' --yes".format(resource_group, job, user_identity_id), checks=[
            JMESPathCheck('type', "SystemAssigned", case_sensitive=False),
            JMESPathCheckExists('principalId'),
            JMESPathCheckExists('tenantId'),
            JMESPathCheckNotExists('userAssignedIdentities'),
        ])

        # Remove system assigned identity from container app job
        self.cmd("az containerapp job identity remove --resource-group {} --name {} --system-assigned --yes".format(resource_group, job), checks=[
            JMESPathCheck('type', "None", case_sensitive=False)
        ])

        # confirm no identity is assigned to container app job
        self.cmd("az containerapp job identity show --resource-group {} --name {}".format(resource_group, job), checks=[
            JMESPathCheck('type', "None", case_sensitive=False)
        ])

        # check container app job resource does not have any identity
        self.cmd("az containerapp job show --resource-group {} --name {}".format(resource_group, job), checks=[
            JMESPathCheck('identity.type', "None", case_sensitive=False)
        ])

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northcentralus")
    def test_containerapp_eventjob_identity_keda(self, resource_group):
        # MSI is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use eastus as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))

        env_id = prepare_containerapp_env_for_app_e2e_tests(self, location)

        job_name = self.create_random_name(prefix='job1', length=24)
        user_identity_name = self.create_random_name(prefix='job1-user', length=24)
        user_identity_id = self.cmd('identity create -g {} -n {}'.format(resource_group, user_identity_name)).get_output_in_json()["id"]

        self.cmd(f'containerapp job create -g {resource_group} -n {job_name} --environment {env_id} \
                 --mi-system-assigned --mi-user-assigned {user_identity_name} \
                 --trigger-type Event --replica-timeout 60 --replica-completion-count 1 --parallelism 1 --min-executions 0 --max-executions 10 --polling-interval 60 \
                 --image "mcr.microsoft.com/k8se/quickstart-jobs:latest" --cpu "0.5" --memory "1Gi" \
                 --scale-rule-name azure-queue --scale-rule-type azure-queue --scale-rule-metadata "accountName=account1" "queueName=queue1" "queueLength=1" --scale-rule-identity {user_identity_name}')

        # verify the container app job resource
        self.cmd(f'az containerapp job show -g {resource_group} -n {job_name}'.format(), checks=[
            JMESPathCheck('name', job_name),
            JMESPathCheck('properties.configuration.replicaTimeout', 60),
            JMESPathCheck('properties.configuration.triggerType', "event", case_sensitive=False),
            JMESPathCheck('properties.configuration.eventTriggerConfig.scale.maxExecutions', 10),
            JMESPathCheck('properties.configuration.eventTriggerConfig.scale.rules[0].metadata.accountName', "account1"),
            JMESPathCheck('properties.configuration.eventTriggerConfig.scale.rules[0].metadata.queueName', "queue1"),
            JMESPathCheck('properties.configuration.eventTriggerConfig.scale.rules[0].metadata.queueLength', "1"),
            JMESPathCheck('properties.configuration.eventTriggerConfig.scale.rules[0].identity', user_identity_id, case_sensitive=False),
        ])

        self.cmd(f'containerapp job update -g {resource_group} -n {job_name} --scale-rule-name azure-blob --scale-rule-type azure-blob --scale-rule-metadata "accountName=account2" "blobContainerName=blob2" "blobCount=2" --scale-rule-identity {user_identity_id}')
        self.cmd(f'containerapp job show -g {resource_group} -n {job_name}', checks=[
            JMESPathCheck("properties.configuration.eventTriggerConfig.scale.rules[0].name", "azure-queue"),
            JMESPathCheck("properties.configuration.eventTriggerConfig.scale.rules[0].type", "azure-queue"),
            JMESPathCheck('properties.configuration.eventTriggerConfig.scale.rules[0].metadata.accountName', "account1"),
            JMESPathCheck('properties.configuration.eventTriggerConfig.scale.rules[0].metadata.queueName', "queue1"),
            JMESPathCheck('properties.configuration.eventTriggerConfig.scale.rules[0].metadata.queueLength', "1"),
            JMESPathCheck('properties.configuration.eventTriggerConfig.scale.rules[0].identity', user_identity_id, case_sensitive=False),
            JMESPathCheck("properties.configuration.eventTriggerConfig.scale.rules[1].name", "azure-blob"),
            JMESPathCheck("properties.configuration.eventTriggerConfig.scale.rules[1].type", "azure-blob"),
            JMESPathCheck("properties.configuration.eventTriggerConfig.scale.rules[1].metadata.accountName", "account2"),
            JMESPathCheck("properties.configuration.eventTriggerConfig.scale.rules[1].metadata.blobContainerName", "blob2"),
            JMESPathCheck("properties.configuration.eventTriggerConfig.scale.rules[1].metadata.blobCount", "2"),
            JMESPathCheck("properties.configuration.eventTriggerConfig.scale.rules[1].identity", user_identity_id, case_sensitive=False),
        ])

        self.cmd(f'containerapp job update -g {resource_group} -n {job_name} --scale-rule-name azure-queue --scale-rule-type azure-queue --scale-rule-metadata "accountName=account3" "queueName=queue3" "queueLength=3" --scale-rule-identity system')
        self.cmd(f'containerapp job show -g {resource_group} -n {job_name}', checks=[
            JMESPathCheck("properties.configuration.eventTriggerConfig.scale.rules[0].name", "azure-queue"),
            JMESPathCheck("properties.configuration.eventTriggerConfig.scale.rules[0].type", "azure-queue"),
            JMESPathCheck('properties.configuration.eventTriggerConfig.scale.rules[0].metadata.accountName', "account3"),
            JMESPathCheck('properties.configuration.eventTriggerConfig.scale.rules[0].metadata.queueName', "queue3"),
            JMESPathCheck('properties.configuration.eventTriggerConfig.scale.rules[0].metadata.queueLength', "3"),
            JMESPathCheck('properties.configuration.eventTriggerConfig.scale.rules[0].identity', "system", case_sensitive=False),
            JMESPathCheck("properties.configuration.eventTriggerConfig.scale.rules[1].name", "azure-blob"),
            JMESPathCheck("properties.configuration.eventTriggerConfig.scale.rules[1].type", "azure-blob"),
            JMESPathCheck("properties.configuration.eventTriggerConfig.scale.rules[1].metadata.accountName", "account2"),
            JMESPathCheck("properties.configuration.eventTriggerConfig.scale.rules[1].metadata.blobContainerName", "blob2"),
            JMESPathCheck("properties.configuration.eventTriggerConfig.scale.rules[1].metadata.blobCount", "2"),
            JMESPathCheck("properties.configuration.eventTriggerConfig.scale.rules[1].identity", user_identity_id, case_sensitive=False),
        ])

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northcentralus")
    # test for CRUD operations on Container App Job resource with trigger type as manual
    def test_containerappjob_identity_registry(self, resource_group):
        # MSI is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use eastus as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))

        env_name = self.create_random_name(prefix='containerapp-e2e-env', length=24)
        job = self.create_random_name(prefix='job1', length=24)
        user_identity_name = self.create_random_name(prefix='containerapp', length=24)
        acr = self.create_random_name(prefix='acr', length=24)
        image_source = "mcr.microsoft.com/k8se/quickstart:latest"
        image_name = f"{acr}.azurecr.io/k8se/quickstart:latest"

        # prepare env
        user_identity_name = self.create_random_name(prefix='env-msi', length=24)
        identity_json = self.cmd('identity create -g {} -n {}'.format(resource_group, user_identity_name)).get_output_in_json()
        user_identity_id = identity_json["id"]
        
        self.cmd('containerapp env create -g {} -n {} --mi-system-assigned --mi-user-assigned {} --logs-destination none'.format(resource_group, env_name, user_identity_id))
        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()
        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()
        env = containerapp_env["id"]

        # prepare acr
        acr_id = self.cmd(f'acr create --sku basic -n {acr} -g {resource_group} --location {location}').get_output_in_json()["id"]
        # role assign
        roleAssignmentName1 = self.create_guid()
        roleAssignmentName2 = self.create_guid()
        self.cmd(f'role assignment create --role acrpull --assignee {containerapp_env["identity"]["principalId"]} --scope {acr_id} --name {roleAssignmentName1}')
        self.cmd(f'role assignment create --role acrpull --assignee {identity_json["principalId"]} --scope {acr_id} --name {roleAssignmentName2}')
        # upload image
        self.cmd(f'acr import -n {acr} --source {image_source}')

        # wait for role assignment take effect
        time.sleep(30)

        # use env system msi to pull image
        self.cmd(f'containerapp create -g {resource_group} -n {job}  --image {image_name} --ingress external --target-port 80 --environment {env} --registry-server {acr}.azurecr.io --registry-identity system-environment')
        self.cmd(f'containerapp job create -g {resource_group} -n {job} --environment {env} --trigger-type manual --replica-timeout 5 --replica-retry-limit 2 --replica-completion-count 1 --parallelism 1 --image {image_name} --registry-server {acr}.azurecr.io --registry-identity system-environment')
        self.cmd(f'containerapp job show -g {resource_group} -n {job}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "None"),
            JMESPathCheck("properties.configuration.registries[0].server", f"{acr}.azurecr.io"),
            JMESPathCheck("properties.configuration.registries[0].identity", "system-environment", case_sensitive=False),
            JMESPathCheck("properties.template.containers[0].image", image_name),
        ])

        # update use env user assigned identity
        self.cmd(f'containerapp job registry set -g {resource_group} -n {job} --server {acr}.azurecr.io --identity {user_identity_id}')
        self.cmd(f'containerapp job show -g {resource_group} -n {job}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "None"),
            JMESPathCheck("properties.configuration.registries[0].server", f"{acr}.azurecr.io"),
            JMESPathCheck("properties.configuration.registries[0].identity", user_identity_id, case_sensitive=False),
            JMESPathCheck("properties.template.containers[0].image", image_name),
        ])

        # update containerapp job
        self.cmd(f'containerapp job update -g {resource_group} -n {job}  --replica-timeout 30')
        self.cmd(f'containerapp job show -g {resource_group} -n {job}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "None"),
            JMESPathCheck("properties.configuration.registries[0].server", f"{acr}.azurecr.io"),
            JMESPathCheck("properties.configuration.registries[0].identity", user_identity_id, case_sensitive=False),
            JMESPathCheck("properties.template.containers[0].image", image_name),
            JMESPathCheck("properties.configuration.replicaTimeout", "30")
        ])

        # update use env system managed identity
        self.cmd(f'containerapp job registry set -g {resource_group} -n {job} --server {acr}.azurecr.io --identity system-environment')
        self.cmd(f'containerapp job show -g {resource_group} -n {job}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "None"),
            JMESPathCheck("properties.configuration.registries[0].server", f"{acr}.azurecr.io"),
            JMESPathCheck("properties.configuration.registries[0].identity", "system-environment"),
            JMESPathCheck("properties.template.containers[0].image", image_name),
        ])

        # update containerapp job
        self.cmd(f'containerapp job update -g {resource_group} -n {job}  --replica-timeout 20')
        self.cmd(f'containerapp job show -g {resource_group} -n {job}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "None"),
            JMESPathCheck("properties.configuration.registries[0].server", f"{acr}.azurecr.io"),
            JMESPathCheck("properties.configuration.registries[0].identity", "system-environment"),
            JMESPathCheck("properties.template.containers[0].image", image_name),
            JMESPathCheck("properties.configuration.replicaTimeout", "20")
        ])