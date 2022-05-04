# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import time
import yaml

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck, live_only)

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

@live_only()
class ContainerappEnvScenarioTest(ScenarioTest):
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="centraluseuap")
    def test_containerapp_env_e2e(self, resource_group):
        env_name = self.create_random_name(prefix='containerapp-e2e-env', length=24)

        self.cmd('containerapp env create -g {} -n {}'.format(resource_group, env_name))

        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        self.cmd('containerapp env list -g {}'.format(resource_group), checks=[
            JMESPathCheck('length(@)', 1),
            JMESPathCheck('[0].name', env_name),
        ])

        self.cmd('containerapp env show -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('name', env_name),
        ])

        # Sleep in case containerapp create takes a while
        self.cmd('containerapp env delete -g {} -n {} --yes'.format(resource_group, env_name))

        # Sleep in case env delete takes a while
        time.sleep(60)
        self.cmd('containerapp env list -g {}'.format(resource_group), checks=[
            JMESPathCheck('length(@)', 0),
        ])

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="centraluseuap")
    def test_containerapp_env_dapr_components(self, resource_group):
        env_name = self.create_random_name(prefix='containerapp-e2e-env', length=24)
        dapr_comp_name = self.create_random_name(prefix='dapr-component', length=24)
        import tempfile

        file_ref, dapr_file = tempfile.mkstemp(suffix=".yml")

        dapr_yaml = """
        name: statestore
        componentType: state.azure.blobstorage
        version: v1
        metadata:
        - name: accountName
          secretRef: storage-account-name
        - name: accountKey
          secretRef: storage-account-key
        - name: containerName
          value: mycontainer
        secrets:
        - name: storage-account-name
          value: storage-account-name
        - name: storage-account-key
          value: mycontainer
        """
        daprloaded = yaml.safe_load(dapr_yaml)
        
        with open(dapr_file, 'w') as outfile:
            yaml.dump(daprloaded, outfile, default_flow_style=False)

        self.cmd('containerapp env create -g {} -n {}'.format(resource_group, env_name))

        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        self.cmd('containerapp env dapr-component set -n {} -g {} --dapr-component-name {} --yaml {}'.format(env_name, resource_group, dapr_comp_name, dapr_file.replace(os.sep, os.sep + os.sep)), checks=[
            JMESPathCheck('name', dapr_comp_name),
        ])

        os.close(file_ref)

        self.cmd('containerapp env dapr-component list -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('length(@)', 1),
            JMESPathCheck('[0].name', dapr_comp_name),
        ])

        self.cmd('containerapp env dapr-component show -n {} -g {} --dapr-component-name {}'.format(env_name, resource_group, dapr_comp_name), checks=[
            JMESPathCheck('name', dapr_comp_name),
        ])
