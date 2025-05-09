# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck)

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))
from .common import TEST_LOCATION
from .utils import create_containerapp_env


class ContainerAppMountSecretTest(ScenarioTest):
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northcentralus")
    def test_container_app_mount_secret_e2e(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))
        env = self.create_random_name(prefix='env', length=24)
        app = self.create_random_name(prefix='app1', length=24)

        create_containerapp_env(self, env, resource_group)

        self.cmd('containerapp env show -n {} -g {}'.format(env, resource_group), checks=[
            JMESPathCheck('name', env)            
        ])

        secretRef1 = "mysecret"
        secretValue1 = "secretvalue1"
        secretRef2 = "anothersecret"
        secretValue2 = "secretvalue2"

        self.cmd(f'az containerapp create -g {resource_group} --environment {env} -n {app} --secrets {secretRef1}={secretValue1} {secretRef2}={secretValue2} --secret-volume-mount "mnt/secrets"')        
        
        self.cmd('containerapp show -g {} -n {}'.format(resource_group, app), checks=[
            JMESPathCheck('properties.template.volumes[0].storageType', 'Secret'), 
            # --secret-volume-mount mounts all secrets, not specific secrets, therefore no secrets should be returned.
            JMESPathCheck('properties.template.volumes[0].secrets', None),
            JMESPathCheck('properties.template.containers[0].volumeMounts[0].mountPath', 'mnt/secrets'), 
        ])
        # test using update to update the secret volume mount path
        self.cmd(f'az containerapp update -n {app} -g {resource_group} --secret-volume-mount "mnt/newpath"')    
        
        self.cmd('containerapp show -g {} -n {}'.format(resource_group, app), checks=[
            JMESPathCheck('properties.template.containers[0].volumeMounts[0].mountPath', 'mnt/newpath'), 
        ])
    
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northcentralus")
    def test_container_app_mount_secret_update_e2e(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))
        # test creating a container app that does not have a secret volume mount, then uses update to add a secret volume mount
        app = self.create_random_name(prefix='app2', length=24)
        env = self.create_random_name(prefix='env', length=24)
        create_containerapp_env(self, env, resource_group)

        secretRef1 = "mysecret"
        secretValue1 = "secretvalue1"
        secretRef2 = "anothersecret"
        secretValue2 = "secretvalue2"

        self.cmd('containerapp env show -n {} -g {}'.format(env, resource_group), checks=[
            JMESPathCheck('name', env)            
        ])

        self.cmd(f'az containerapp create -g {resource_group} --environment {env} -n {app} --secrets {secretRef1}={secretValue1} {secretRef2}={secretValue2}')
        
        self.cmd('containerapp show -g {} -n {}'.format(resource_group, app), checks=[
            JMESPathCheck('properties.template.volumes', None), 
        ])

        self.cmd(f'az containerapp update -n {app} -g {resource_group} --secret-volume-mount "mnt/secrets"')
        
        self.cmd('containerapp show -g {} -n {}'.format(resource_group, app), checks=[
            JMESPathCheck('properties.template.volumes[0].storageType', 'Secret'), 
            JMESPathCheck('properties.template.volumes[0].secrets', None),
            JMESPathCheck('properties.template.containers[0].volumeMounts[0].mountPath', 'mnt/secrets'), 
        ])





