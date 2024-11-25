# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import time
from azure.cli.command_modules.containerapp._utils import format_location

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck, JMESPathCheckExists)

from .common import (TEST_LOCATION, STAGE_LOCATION, write_test_file,
                     clean_up_test_file,
                     )
from .utils import create_containerapp_env


class ContainerappSessionPoolTests(ScenarioTest):
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer()
    def test_containerapp_sessionpool(self, resource_group):
        location = TEST_LOCATION
        self.cmd('configure --defaults location={}'.format(location))

        env_name = self.create_random_name(prefix='aca-sp-env', length=24)
        self.cmd('containerapp env create -g {} -n {} -l {} --logs-destination none'.format(resource_group, env_name, location), expect_failure=False)
        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()
        while containerapp_env["properties"]["provisioningState"].lower() in ["waiting", "inprogress"]:
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        # List Session Pools
        sessionpool_list = self.cmd("containerapp sessionpool list -g {}".format(resource_group)).get_output_in_json()
        self.assertTrue(len(sessionpool_list) == 0)

        # Create JupyterPython SessionPool
        sessionpool_name_python = self.create_random_name(prefix='spjupyterpython', length=24)
        self.cmd('containerapp sessionpool create -g {} -n {} --cooldown-period {}'.format(
            resource_group, sessionpool_name_python, 300), checks=[
            JMESPathCheck('name', sessionpool_name_python),
            JMESPathCheck('properties.containerType', "PythonLTS"),
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck('properties.dynamicPoolConfiguration.cooldownPeriodInSeconds', 300)
        ])

        # Create CustomContainer SessionPool
        sessionpool_name_custom = self.create_random_name(prefix='spcustomcontainer', length=24)
        ready_instances = 2
        image = "mcr.microsoft.com/k8se/quickstart:latest"
        secret_name = "testsecret"
        secret_value = "testsecretvalue"
        cpu = "0.5"
        memory = "1Gi"
        self.cmd(
            'containerapp sessionpool create -g {} -n {} --container-type CustomContainer --environment {} --secrets {}={} --ready-sessions {} --image {} --cpu {} --memory {} --target-port {}'.format(
                resource_group, sessionpool_name_custom, env_name, secret_name, secret_value, ready_instances, image, cpu, memory, 80),
            checks=[
                JMESPathCheck('name', sessionpool_name_custom),
                JMESPathCheck('properties.containerType', "CustomContainer"),
                JMESPathCheck('properties.scaleConfiguration.maxConcurrentSessions', 10),
                JMESPathCheck('properties.scaleConfiguration.readySessionInstances', ready_instances),
                JMESPathCheck('properties.secrets[0].name', secret_name),
                JMESPathCheck('properties.customContainerTemplate.containers[0].image', image),
                JMESPathCheck('properties.customContainerTemplate.containers[0].resources.cpu', cpu),
                JMESPathCheck('properties.customContainerTemplate.containers[0].resources.memory', memory),
                JMESPathCheck('properties.customContainerTemplate.ingress.targetPort', 80),
            ])

        sessionpool = self.cmd('containerapp sessionpool show -g {} -n {}'.format(resource_group, sessionpool_name_custom)).get_output_in_json()
        while sessionpool["properties"]["provisioningState"].lower() in ["waiting", "inprogress"]:
            time.sleep(5)
            sessionpool = self.cmd('containerapp sessionpool show -g {} -n {}'.format(resource_group, sessionpool_name_custom)).get_output_in_json()

        self.cmd(
            'containerapp sessionpool show -g {} -n {}'.format(resource_group, sessionpool_name_custom),
            checks=[JMESPathCheck('properties.provisioningState', "Succeeded")]
        )

        # List Session Pools
        sessionpool_list = self.cmd("containerapp sessionpool list -g {}".format(resource_group)).get_output_in_json()
        self.assertTrue(len(sessionpool_list) == 2)

        # Update Session Pool
        max_concurrent_session = 12
        cpu = "2.0"
        memory = "4Gi"
        egress = "EgressDisabled"
        cooldown = 400
        secret_name = "testsecret1"
        secret_value = "testsecretvalue1"
        self.cmd(
            'containerapp sessionpool update -g {} -n {} --max-sessions {} --cpu {} --memory {} --network-status {} --cooldown-period {} --secrets {}={}'.format(
                resource_group, sessionpool_name_custom, max_concurrent_session, cpu, memory, egress, cooldown, secret_name, secret_value),
            checks=[
                JMESPathCheck('name', sessionpool_name_custom),
                JMESPathCheck('properties.containerType', "CustomContainer"),
                JMESPathCheck('properties.scaleConfiguration.maxConcurrentSessions', max_concurrent_session),
                JMESPathCheck('properties.scaleConfiguration.readySessionInstances', ready_instances),
                JMESPathCheck('properties.secrets[0].name', secret_name),
                JMESPathCheck('properties.customContainerTemplate.containers[0].image', image),
                JMESPathCheck('properties.customContainerTemplate.containers[0].resources.cpu', cpu),
                JMESPathCheck('properties.customContainerTemplate.containers[0].resources.memory', memory),
                JMESPathCheck('properties.customContainerTemplate.ingress.targetPort', 80),
                JMESPathCheck('properties.sessionNetworkConfiguration.status', egress),
                JMESPathCheck('properties.dynamicPoolConfiguration.cooldownPeriodInSeconds', cooldown),
            ])

        sessionpool = self.cmd('containerapp sessionpool show -g {} -n {}'.format(resource_group, sessionpool_name_custom)).get_output_in_json()
        while sessionpool["properties"]["provisioningState"].lower() in ["waiting", "inprogress"]:
            time.sleep(5)
            sessionpool = self.cmd('containerapp sessionpool show -g {} -n {}'.format(resource_group, sessionpool_name_custom)).get_output_in_json()

        self.cmd(
            'containerapp sessionpool show -g {} -n {}'.format(resource_group, sessionpool_name_custom),
            checks=[JMESPathCheck('properties.provisioningState', "Succeeded")]
        )

        # Show a Session Pool
        self.cmd(
            'containerapp sessionpool show -g {} -n {}'.format(resource_group, sessionpool_name_custom),
            checks=[
                JMESPathCheck('name', sessionpool_name_custom),
                JMESPathCheck('properties.containerType', "CustomContainer")
            ])

        self.cmd('containerapp sessionpool delete -g {} -n {} --yes'.format(resource_group, sessionpool_name_python))
        self.cmd('containerapp sessionpool delete -g {} -n {} --yes'.format(resource_group, sessionpool_name_custom))

        # List Session Pools
        sessionpool_list = self.cmd("containerapp sessionpool list -g {}".format(resource_group)).get_output_in_json()
        self.assertTrue(len(sessionpool_list) == 0)

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer()
    def test_containerapp_sessionpool_registry(self, resource_group):
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastasia"
        self.cmd('configure --defaults location={}'.format(location))

        env_name = self.create_random_name(prefix='aca-sp-env-registry', length=24)
        self.cmd('containerapp env create -g {} -n {} -l {} --logs-destination none'.format(resource_group, env_name, location), expect_failure=False)
        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()
        while containerapp_env["properties"]["provisioningState"].lower() in ["waiting", "inprogress"]:
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        acr = self.create_random_name(prefix='acr', length=24)
        image_source = "mcr.microsoft.com/k8se/quickstart:latest"
        image_name = f"{acr}.azurecr.io/k8se/quickstart:latest"

        self.cmd(f'acr create --sku basic -n {acr} -g {resource_group} --admin-enabled')
        self.cmd(f'acr import -n {acr} --source {image_source}')
        password = self.cmd(f'acr credential show -n {acr} --query passwords[0].value').get_output_in_json()

        # Create CustomContainer SessionPool
        sessionpool_name_custom = self.create_random_name(prefix='spcc', length=24)
        ready_instances = 2
        cpu = "0.5"
        memory = "1Gi"
        self.cmd(
            f'containerapp sessionpool create -g {resource_group} -n {sessionpool_name_custom} --container-type CustomContainer --environment {env_name} --ready-sessions {ready_instances} --image {image_name} --cpu {cpu} --memory {memory} --target-port 80 --registry-server {acr}.azurecr.io --registry-username {acr} --registry-password {password}',
            checks=[
                JMESPathCheck('name', sessionpool_name_custom),
                JMESPathCheck('properties.containerType', "CustomContainer"),
                JMESPathCheck('properties.customContainerTemplate.containers[0].image', image_name),
                JMESPathCheck('properties.customContainerTemplate.containers[0].resources.cpu', cpu),
                JMESPathCheck('properties.customContainerTemplate.containers[0].resources.memory', memory),
                JMESPathCheck('properties.customContainerTemplate.registryCredentials.server', f"{acr}.azurecr.io"),
                JMESPathCheck('properties.customContainerTemplate.registryCredentials.username', acr),
                JMESPathCheck('properties.customContainerTemplate.containers[0].resources.memory', memory),
                JMESPathCheck('properties.secrets[0].name', f"{acr}azurecrio-{acr}"),
                JMESPathCheck('properties.customContainerTemplate.ingress.targetPort', 80),
            ])

        sessionpool = self.cmd('containerapp sessionpool show -g {} -n {}'.format(resource_group, sessionpool_name_custom)).get_output_in_json()
        while sessionpool["properties"]["provisioningState"].lower() in ["waiting", "inprogress"]:
            time.sleep(5)
            sessionpool = self.cmd('containerapp sessionpool show -g {} -n {}'.format(resource_group, sessionpool_name_custom)).get_output_in_json()

        self.cmd('containerapp sessionpool show -g {} -n {}'.format(resource_group, sessionpool_name_custom),
                 checks=[JMESPathCheck('properties.provisioningState', "Succeeded")])

        # List Session Pools
        sessionpool_list = self.cmd("containerapp sessionpool list -g {}".format(resource_group)).get_output_in_json()
        self.assertTrue(len(sessionpool_list) == 1)

        self.cmd('containerapp sessionpool delete -g {} -n {} --yes'.format(resource_group, sessionpool_name_custom))

        # List Session Pools
        sessionpool_list = self.cmd("containerapp sessionpool list -g {}".format(resource_group)).get_output_in_json()
        self.assertTrue(len(sessionpool_list) == 0)

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer()
    def test_containerapp_sessionpool_registry_identity(self, resource_group):
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastasia"
        self.cmd('configure --defaults location={}'.format(location))

        user_identity_name = self.create_random_name(prefix='sp-msi1', length=24)
        identity_json = self.cmd('identity create -g {} -n {} -l {}'.format(resource_group, user_identity_name, location)).get_output_in_json()
        user_identity_id = identity_json["id"]
        principal_id = identity_json["principalId"]
        
        env_name = self.create_random_name(prefix='aca-sp-env-registry', length=24)
        self.cmd('containerapp env create -g {} -n {} -l {} --logs-destination none'.format(resource_group, env_name, location), expect_failure=False)
        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()
        while containerapp_env["properties"]["provisioningState"].lower() in ["waiting", "inprogress"]:
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        acr = self.create_random_name(prefix='acr', length=24)
        image_source = "mcr.microsoft.com/k8se/quickstart:latest"
        image_name = f"{acr}.azurecr.io/k8se/quickstart:latest"

        acr_resource_id = self.cmd(f'acr create --sku basic -n {acr} -g {resource_group} -l {location}').get_output_in_json()["id"]
        self.cmd(f'acr import -n {acr} --source {image_source}')
        roleAssignmentName = self.create_guid()
        self.cmd(f'role assignment create --role acrpull --assignee {principal_id} --scope {acr_resource_id} --name {roleAssignmentName}')
       
        # wait for role assignment take effect
        time.sleep(30)
        
        # Create CustomContainer SessionPool
        sessionpool_name_custom = self.create_random_name(prefix='spcc', length=24)
        ready_instances = 2
        cpu = "0.5"
        memory = "1Gi"
        self.cmd(
            f'containerapp sessionpool create -g {resource_group} -n {sessionpool_name_custom} -l {location} --container-type CustomContainer --environment {env_name} --ready-sessions {ready_instances} --image {image_name} --cpu {cpu} --memory {memory} --target-port 80 --registry-server {acr}.azurecr.io --registry-identity {user_identity_id} --mi-system-assigned',
            checks=[
                JMESPathCheck('name', sessionpool_name_custom),
                JMESPathCheck('properties.containerType', "CustomContainer"),
                JMESPathCheck('properties.customContainerTemplate.containers[0].image', image_name),
                JMESPathCheck('properties.customContainerTemplate.ingress.targetPort', 80),
                JMESPathCheck("properties.provisioningState", "Succeeded"),
                JMESPathCheck("identity.type", "SystemAssigned, UserAssigned"),
                JMESPathCheckExists(f'identity.userAssignedIdentities."{user_identity_id}"'),
                JMESPathCheck("properties.customContainerTemplate.registryCredentials.identity", user_identity_id),
                JMESPathCheck("properties.customContainerTemplate.registryCredentials.server", f'{acr}.azurecr.io'),
                JMESPathCheck("properties.customContainerTemplate.registryCredentials.username", None),
                JMESPathCheck("properties.customContainerTemplate.registryCredentials.passwordSecretRef", None)
            ])

        sessionpool = self.cmd('containerapp sessionpool show -g {} -n {}'.format(resource_group, sessionpool_name_custom)).get_output_in_json()
        while sessionpool["properties"]["provisioningState"].lower() in ["waiting", "inprogress"]:
            time.sleep(5)
            sessionpool = self.cmd('containerapp sessionpool show -g {} -n {}'.format(resource_group, sessionpool_name_custom)).get_output_in_json()

        self.cmd('containerapp sessionpool show -g {} -n {}'.format(resource_group, sessionpool_name_custom),
                 checks=[JMESPathCheck('properties.provisioningState', "Succeeded")])

        # Update session pool to remove SystemAssigned
        self.cmd(
            f'containerapp sessionpool create -g {resource_group} -n {sessionpool_name_custom} -l {location} --container-type CustomContainer --environment {env_name} --ready-sessions {ready_instances} --image {image_name} --cpu {cpu} --memory {memory} --target-port 80 --registry-server {acr}.azurecr.io --registry-identity {user_identity_id}',
            checks=[
                JMESPathCheck('name', sessionpool_name_custom),
                JMESPathCheck("properties.provisioningState", "Succeeded"),
                JMESPathCheck("identity.type", "UserAssigned"),
                JMESPathCheck("properties.managedIdentitySettings[0].identity", user_identity_id),
                JMESPathCheck("properties.managedIdentitySettings[0].lifecycle", "None"),
            ])
        
        self.cmd('containerapp sessionpool delete -g {} -n {} --yes'.format(resource_group, sessionpool_name_custom))

        # List Session Pools
        sessionpool_list = self.cmd("containerapp sessionpool list -g {}".format(resource_group)).get_output_in_json()
        self.assertTrue(len(sessionpool_list) == 0)
