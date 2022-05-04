# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import time
import unittest

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck, live_only)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

@live_only()
class ContainerappIdentityTests(ScenarioTest):
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="eastus2")
    def test_containerapp_identity_e2e(self, resource_group):
        env_name = self.create_random_name(prefix='containerapp-env', length=24)
        ca_name = self.create_random_name(prefix='containerapp', length=24)
        user_identity_name = self.create_random_name(prefix='containerapp', length=24)

        self.cmd('containerapp env create -g {} -n {}'.format(resource_group, env_name))

        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        self.cmd('containerapp create -g {} -n {} --environment {}'.format(resource_group, ca_name, env_name))

        self.cmd('containerapp identity assign --system-assigned -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('type', 'SystemAssigned'),
        ])

        self.cmd('identity create -g {} -n {}'.format(resource_group, user_identity_name))

        self.cmd('containerapp identity assign --user-assigned {} -g {} -n {}'.format(user_identity_name, resource_group, ca_name), checks=[
            JMESPathCheck('type', 'SystemAssigned, UserAssigned'),
        ])

        self.cmd('containerapp identity show -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('type', 'SystemAssigned, UserAssigned'),
        ])

        self.cmd('containerapp identity remove --user-assigned {} -g {} -n {}'.format(user_identity_name, resource_group, ca_name), checks=[
            JMESPathCheck('type', 'SystemAssigned'),
        ])

        self.cmd('containerapp identity show -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('type', 'SystemAssigned'),
        ])

        self.cmd('containerapp identity remove --system-assigned -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('type', 'None'),
        ])

        self.cmd('containerapp identity show -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('type', 'None'),
        ])

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="eastus")
    def test_containerapp_identity_system(self, resource_group):
        env_name = self.create_random_name(prefix='containerapp-env', length=24)
        ca_name = self.create_random_name(prefix='containerapp', length=24)

        self.cmd('containerapp env create -g {} -n {}'.format(resource_group, env_name))

        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        self.cmd('containerapp create -g {} -n {} --environment {} --system-assigned'.format(resource_group, ca_name, env_name))

        self.cmd('containerapp identity show -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('type', 'SystemAssigned'),
        ])

        self.cmd('containerapp identity remove --system-assigned -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('type', 'None'),
        ])

        self.cmd('containerapp identity assign --system-assigned -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('type', 'SystemAssigned'),
        ])

        self.cmd('containerapp identity remove --system-assigned -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('type', 'None'),
        ])

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="eastus2")
    def test_containerapp_identity_user(self, resource_group):
        env_name = self.create_random_name(prefix='containerapp-env', length=24)
        ca_name = self.create_random_name(prefix='containerapp', length=24)
        user_identity_name1 = self.create_random_name(prefix='containerapp-user1', length=24)
        user_identity_name2 = self.create_random_name(prefix='containerapp-user2', length=24)

        self.cmd('containerapp env create -g {} -n {}'.format(resource_group, env_name))

        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        self.cmd('containerapp create -g {} -n {} --environment {}'.format(resource_group, ca_name, env_name))

        self.cmd('identity create -g {} -n {}'.format(resource_group, user_identity_name1))

        self.cmd('identity create -g {} -n {}'.format(resource_group, user_identity_name2))

        self.cmd('containerapp identity assign --system-assigned -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('type', 'SystemAssigned'),
        ])

        self.cmd('containerapp identity assign --user-assigned {} {} -g {} -n {}'.format(user_identity_name1, user_identity_name2, resource_group, ca_name), checks=[
            JMESPathCheck('type', 'SystemAssigned, UserAssigned'),
        ])

        self.cmd('containerapp identity show -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('type', 'SystemAssigned, UserAssigned'),
        ])

        self.cmd('containerapp identity remove --user-assigned {} -g {} -n {}'.format(user_identity_name1, resource_group, ca_name), checks=[
            JMESPathCheck('type', 'SystemAssigned, UserAssigned'),
        ])

        self.cmd('containerapp identity remove --user-assigned {} -g {} -n {}'.format(user_identity_name2, resource_group, ca_name), checks=[
            JMESPathCheck('type', 'SystemAssigned'),
        ])

        self.cmd('containerapp identity show -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('type', 'SystemAssigned'),
        ])

        self.cmd('containerapp identity remove --system-assigned -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('type', 'None'),
        ])

        self.cmd('containerapp identity show -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('type', 'None'),
        ])


@live_only()
class ContainerappEnvStorageTests(ScenarioTest):
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="eastus2")
    def test_containerapp_env_storage(self, resource_group):
        env_name = self.create_random_name(prefix='containerapp-env', length=24)
        storage_name = self.create_random_name(prefix='storage', length=24)
        shares_name = self.create_random_name(prefix='share', length=24)

        self.cmd('containerapp env create -g {} -n {}'.format(resource_group, env_name))

        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        self.cmd('storage account create -g {} -n {} --kind StorageV2 --sku Standard_ZRS --enable-large-file-share'.format(resource_group, storage_name))
        self.cmd('storage share-rm create -g {} -n {} --storage-account {} --access-tier "TransactionOptimized" --quota 1024'.format(resource_group, shares_name, storage_name))

        storage_keys = self.cmd('az storage account keys list -g {} -n {}'.format(resource_group, storage_name)).get_output_in_json()[0]

        self.cmd('containerapp env storage set -g {} -n {} --storage-name {} --azure-file-account-name {} --azure-file-account-key {} --access-mode ReadOnly --azure-file-share-name {}'.format(resource_group, env_name, storage_name, storage_name, storage_keys["value"], shares_name), checks=[
            JMESPathCheck('name', storage_name),
        ])

        self.cmd('containerapp env storage show -g {} -n {} --storage-name {}'.format(resource_group, env_name, storage_name), checks=[
            JMESPathCheck('name', storage_name),
        ])

        self.cmd('containerapp env storage list -g {} -n {}'.format(resource_group, env_name), checks=[
            JMESPathCheck('[0].name', storage_name),
        ])

        self.cmd('containerapp env storage remove -g {} -n {} --storage-name {} --yes'.format(resource_group, env_name, storage_name))

        self.cmd('containerapp env storage list -g {} -n {}'.format(resource_group, env_name), checks=[
            JMESPathCheck('length(@)', 0),
        ])


@live_only()
class ContainerappIngressTests(ScenarioTest):
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="eastus2")
    def test_containerapp_ingress_e2e(self, resource_group):
        env_name = self.create_random_name(prefix='containerapp-env', length=24)
        ca_name = self.create_random_name(prefix='containerapp', length=24)

        self.cmd('containerapp env create -g {} -n {}'.format(resource_group, env_name))

        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        self.cmd('containerapp create -g {} -n {} --environment {} --ingress external --target-port 80'.format(resource_group, ca_name, env_name))

        self.cmd('containerapp ingress show -g {} -n {}'.format(resource_group, ca_name, env_name), checks=[
            JMESPathCheck('external', True),
            JMESPathCheck('targetPort', 80),
        ])

        self.cmd('containerapp ingress disable -g {} -n {}'.format(resource_group, ca_name, env_name))

        containerapp_def = self.cmd('containerapp show -g {} -n {}'.format(resource_group, ca_name)).get_output_in_json()

        self.assertEqual("fqdn" in containerapp_def["properties"]["configuration"], False)

        self.cmd('containerapp ingress enable -g {} -n {} --type internal --target-port 81 --allow-insecure --transport http2'.format(resource_group, ca_name, env_name))

        self.cmd('containerapp ingress show -g {} -n {}'.format(resource_group, ca_name, env_name), checks=[
            JMESPathCheck('external', False),
            JMESPathCheck('targetPort', 81),
            JMESPathCheck('allowInsecure', True),
            JMESPathCheck('transport', "Http2"),
        ])

        self.cmd('containerapp ingress show -g {} -n {}'.format(resource_group, ca_name, env_name), checks=[
            JMESPathCheck('external', False),
            JMESPathCheck('targetPort', 81),
            JMESPathCheck('allowInsecure', True),
            JMESPathCheck('transport', "Http2"),
        ])

    def test_containerapp_ingress_traffic_e2e(self, resource_group):
        env_name = self.create_random_name(prefix='containerapp-env', length=24)
        ca_name = self.create_random_name(prefix='containerapp', length=24)

        self.cmd('containerapp env create -g {} -n {}'.format(resource_group, env_name))

        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        self.cmd('containerapp create -g {} -n {} --environment {} --ingress external --target-port 80'.format(resource_group, ca_name, env_name))

        self.cmd('containerapp ingress show -g {} -n {}'.format(resource_group, ca_name, env_name), checks=[
            JMESPathCheck('external', True),
            JMESPathCheck('targetPort', 80),
        ])

        self.cmd('containerapp ingress traffic set -g {} -n {} --traffic-weight latest=100'.format(resource_group, ca_name), checks=[
            JMESPathCheck('[0].latestRevision', True),
            JMESPathCheck('[0].weight', 100),
        ])

        containerapp_def = self.cmd('containerapp show -g {} -n {}'.format(resource_group, ca_name)).get_output_in_json()

        self.assertEqual("fqdn" in containerapp_def["properties"]["configuration"], False)

        self.cmd('containerapp ingress enable -g {} -n {} --type internal --target-port 81 --allow-insecure --transport http2'.format(resource_group, ca_name, env_name))

        self.cmd('containerapp ingress show -g {} -n {}'.format(resource_group, ca_name, env_name), checks=[
            JMESPathCheck('external', False),
            JMESPathCheck('targetPort', 81),
            JMESPathCheck('allowInsecure', True),
            JMESPathCheck('transport', "Http2"),
        ])

        self.cmd('containerapp ingress show -g {} -n {}'.format(resource_group, ca_name, env_name), checks=[
            JMESPathCheck('external', False),
            JMESPathCheck('targetPort', 81),
            JMESPathCheck('allowInsecure', True),
            JMESPathCheck('transport', "Http2"),
        ])
