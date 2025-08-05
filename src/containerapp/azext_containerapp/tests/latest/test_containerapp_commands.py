# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import time
import unittest

from azure.cli.command_modules.containerapp._utils import format_location
from unittest import mock
from azure.cli.core.azclierror import ValidationError

from azure.cli.testsdk.scenario_tests import AllowLargeResponse, live_only
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck, JMESPathCheckNotExists, JMESPathCheckExists)
from azure.mgmt.core.tools import parse_resource_id

from azext_containerapp.tests.latest.common import (write_test_file, clean_up_test_file)
from .common import TEST_LOCATION, STAGE_LOCATION
from .custom_preparers import SubnetPreparer
from .utils import create_containerapp_env, prepare_containerapp_env_for_app_e2e_tests

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class ContainerappIdentityTests(ScenarioTest):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, random_config_dir=True, **kwargs)

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="eastus2")
    def test_containerapp_identity_e2e(self, resource_group):
        # MSI is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use eastus as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))

        ca_name = self.create_random_name(prefix='containerapp', length=24)
        user_identity_name = self.create_random_name(prefix='containerapp', length=24)

        env = prepare_containerapp_env_for_app_e2e_tests(self, location=location)

        self.cmd('containerapp create -g {} -n {} --environment {}'.format(resource_group, ca_name, env))

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
        self.cmd('containerapp delete  -g {} -n {} --yes'.format(resource_group, ca_name), expect_failure=False)

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="canadacentral")
    def test_containerapp_identity_system(self, resource_group):
        # MSI is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use eastus as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))

        env_name = self.create_random_name(prefix='containerapp-env', length=24)
        ca_name = self.create_random_name(prefix='containerapp', length=24)
        logs_workspace_name = self.create_random_name(prefix='containerapp-env', length=24)

        logs_workspace_id = self.cmd('monitor log-analytics workspace create -g {} -n {} -l eastus'.format(resource_group, logs_workspace_name)).get_output_in_json()["customerId"]
        logs_workspace_key = self.cmd('monitor log-analytics workspace get-shared-keys -g {} -n {}'.format(resource_group, logs_workspace_name)).get_output_in_json()["primarySharedKey"]

        self.cmd('containerapp env create -g {} -n {} --logs-workspace-id {} --logs-workspace-key {}'.format(resource_group, env_name, logs_workspace_id, logs_workspace_key))

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
    @ResourceGroupPreparer(location="westeurope")
    def test_containerapp_identity_user(self, resource_group):
        # MSI is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use eastus as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))

        ca_name = self.create_random_name(prefix='containerapp', length=24)
        user_identity_name1 = self.create_random_name(prefix='containerapp-user1', length=24)
        user_identity_name2 = self.create_random_name(prefix='containerapp-user2', length=24)

        env = prepare_containerapp_env_for_app_e2e_tests(self, location=location)

        self.cmd('containerapp create -g {} -n {} --environment {}'.format(resource_group, ca_name, env))

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

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="westeurope")
    def test_containerapp_identity_keda(self, resource_group):
        # MSI is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use eastus as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))

        ca_name = self.create_random_name(prefix='containerapp', length=24)
        user_identity_name1 = self.create_random_name(prefix='containerapp-user1', length=24)

        env = prepare_containerapp_env_for_app_e2e_tests(self, location=location)

        user_identity_id = self.cmd('identity create -g {} -n {}'.format(resource_group, user_identity_name1)).get_output_in_json()["id"]

        self.cmd(f'containerapp create -g {resource_group} -n {ca_name} --environment {env} --system-assigned --user-assigned {user_identity_name1} --scale-rule-name azure-queue --scale-rule-type azure-queue --scale-rule-metadata "accountName=account1" "queueName=queue1" "queueLength=1" --scale-rule-identity {user_identity_name1}')
        self.cmd(f'containerapp show -g {resource_group} -n {ca_name}', checks=[
            JMESPathCheck("properties.template.scale.rules[0].name", "azure-queue"),
            JMESPathCheck("properties.template.scale.rules[0].azureQueue.accountName", "account1"),
            JMESPathCheck("properties.template.scale.rules[0].azureQueue.queueName", "queue1"),
            JMESPathCheck("properties.template.scale.rules[0].azureQueue.queueLength", "1"),
            JMESPathCheck("properties.template.scale.rules[0].azureQueue.identity", user_identity_id, case_sensitive=False),
        ])

        self.cmd(f'containerapp update -g {resource_group} -n {ca_name} --scale-rule-name azure-blob --scale-rule-type azure-blob --scale-rule-metadata "accountName=account2" "blobContainerName=blob2" "blobCount=2" --scale-rule-identity {user_identity_id}')
        self.cmd(f'containerapp show -g {resource_group} -n {ca_name}', checks=[
            JMESPathCheck("properties.template.scale.rules[0].name", "azure-blob"),
            JMESPathCheck("properties.template.scale.rules[0].custom.metadata.accountName", "account2"),
            JMESPathCheck("properties.template.scale.rules[0].custom.metadata.blobContainerName", "blob2"),
            JMESPathCheck("properties.template.scale.rules[0].custom.metadata.blobCount", "2"),
            JMESPathCheck("properties.template.scale.rules[0].custom.identity", user_identity_id, case_sensitive=False),
            JMESPathCheck("properties.template.scale.rules[0].custom.type", "azure-blob"),
        ])


class ContainerappIngressTests(ScenarioTest):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, random_config_dir=True, **kwargs)

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="eastus2")
    def test_containerapp_ingress_e2e(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        ca_name = self.create_random_name(prefix='containerapp', length=24)

        env = prepare_containerapp_env_for_app_e2e_tests(self)

        self.cmd('containerapp create -g {} -n {} --environment {} --ingress external --target-port 80 --allow-insecure'.format(resource_group, ca_name, env))

        self.cmd('containerapp ingress show -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('external', True),
            JMESPathCheck('targetPort', 80),
            JMESPathCheck('allowInsecure', True),
        ])

        self.cmd('containerapp ingress disable -g {} -n {}'.format(resource_group, ca_name))

        containerapp_def = self.cmd('containerapp show -g {} -n {}'.format(resource_group, ca_name)).get_output_in_json()

        self.assertEqual("fqdn" in containerapp_def["properties"]["configuration"], False)

        self.cmd('containerapp ingress enable -g {} -n {} --type internal --target-port 81 --allow-insecure --transport http2'.format(resource_group, ca_name))

        self.cmd('containerapp ingress show -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('external', False),
            JMESPathCheck('targetPort', 81),
            JMESPathCheck('allowInsecure', True),
            JMESPathCheck('transport', "Http2"),
        ])

        self.cmd('containerapp ingress update -g {} -n {} --type external --allow-insecure=False'.format(resource_group, ca_name))

        self.cmd('containerapp ingress show -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('external', True),
            JMESPathCheck('targetPort', 81),
            JMESPathCheck('allowInsecure', False),
            JMESPathCheck('transport', "Http2"),
        ])

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="eastus2")
    def test_containerapp_ingress_traffic_e2e(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        ca_name = self.create_random_name(prefix='containerapp', length=24)

        env = prepare_containerapp_env_for_app_e2e_tests(self)

        self.cmd('containerapp create -g {} -n {} --environment {} --ingress external --target-port 80 --revisions-mode multiple'.format(resource_group, ca_name, env))

        self.cmd('containerapp ingress show -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('external', True),
            JMESPathCheck('targetPort', 80),
        ])

        self.cmd('containerapp ingress traffic set -g {} -n {} --revision-weight latest=100'.format(resource_group, ca_name), checks=[
            JMESPathCheck('[0].latestRevision', True),
            JMESPathCheck('[0].weight', 100),
        ])

        self.cmd('containerapp update -g {} -n {} --cpu 1.0 --memory 2Gi'.format(resource_group, ca_name))

        revisions_list = self.cmd('containerapp revision list -g {} -n {}'.format(resource_group, ca_name)).get_output_in_json()

        self.cmd('containerapp ingress traffic set -g {} -n {} --revision-weight latest=50 {}=50'.format(resource_group, ca_name, revisions_list[0]["name"]), checks=[
            JMESPathCheck('[0].latestRevision', True),
            JMESPathCheck('[0].weight', 50),
            JMESPathCheck('[1].revisionName', revisions_list[0]["name"]),
            JMESPathCheck('[1].weight', 50),
        ])

        self.cmd('containerapp ingress traffic show -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('[0].latestRevision', True),
            JMESPathCheck('[0].weight', 50),
            JMESPathCheck('[1].revisionName', revisions_list[0]["name"]),
            JMESPathCheck('[1].weight', 50),
        ])

        revisions_list = self.cmd('containerapp revision list -g {} -n {}'.format(resource_group, ca_name)).get_output_in_json()

        for revision in revisions_list:
            self.assertEqual(revision["properties"]["trafficWeight"], 50)

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="eastus2")
    def test_containerapp_ingress_traffic_labels_e2e(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        ca_name = self.create_random_name(prefix='containerapp', length=24)

        env = prepare_containerapp_env_for_app_e2e_tests(self)

        self.cmd('containerapp create -g {} -n {} --environment {} --ingress external --target-port 0 --revisions-mode labels --target-label label1'.format(resource_group, ca_name, env))

        # wait for the first revision to come up and populate in traffic.
        ingress = self.cmd('containerapp ingress show -g {} -n {}'.format(resource_group, ca_name)).get_output_in_json()
        for _ in range(100):
            if ingress["traffic"] != None:
                break
            time.sleep(5)
            traffic = self.cmd('containerapp ingress show -g {} -n {}'.format(resource_group, ca_name)).get_output_in_json()

        self.cmd('containerapp ingress show -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('external', True),
            JMESPathCheck('targetPort', 0),
            JMESPathCheck('traffic[0].weight', 100),
            JMESPathCheck('traffic[0].label', "label1"),
        ])

        # Create a new revision with a different label
        self.cmd('containerapp update -g {} -n {} --cpu 1.0 --memory 2Gi --target-label label2'.format(resource_group, ca_name))

        # it may take a minute for the new revision to be created and added to traffic.
        traffic = self.cmd('containerapp ingress traffic show -g {} -n {}'.format(resource_group, ca_name)).get_output_in_json()    
        for _ in range(100):
            if len(traffic) >= 2:
                break
            time.sleep(5)
            traffic = self.cmd('containerapp ingress traffic show -g {} -n {}'.format(resource_group, ca_name)).get_output_in_json()
        
        self.assertEqual(len(traffic), 2)

        revisions_list = self.cmd('containerapp revision list -g {} -n {}'.format(resource_group, ca_name)).get_output_in_json()

        # TODO: The revision list call isn't handled by extensions, this will only work once the core CLI updates to at least 2024-10-02-preview
        # self.assertEqual(revisions_list[0]["properties"]["labels"], "label1")
        # self.assertEqual(revisions_list[2]["properties"]["labels"], "label2")
        self.cmd('containerapp ingress traffic show -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('[0].weight', 100),
            JMESPathCheck('[0].label', "label1"),
            JMESPathCheck('[0].revisionName', revisions_list[0]["name"]),
            JMESPathCheck('[1].weight', 0),
            JMESPathCheck('[1].label', "label2"),
            JMESPathCheck('[1].revisionName', revisions_list[1]["name"]),
        ])

        self.cmd('containerapp ingress traffic set -g {} -n {} --label-weight label1=80 label2=20'.format(resource_group, ca_name), checks=[
            JMESPathCheck('[0].weight', 80),
            JMESPathCheck('[0].label', "label1"),
            JMESPathCheck('[0].revisionName', revisions_list[0]["name"]),
            JMESPathCheck('[1].weight', 20),
            JMESPathCheck('[1].label', "label2"),
            JMESPathCheck('[1].revisionName', revisions_list[1]["name"]),
        ])

        self.cmd('containerapp ingress traffic show -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('[0].weight', 80),
            JMESPathCheck('[0].label', "label1"),
            JMESPathCheck('[0].revisionName', revisions_list[0]["name"]),
            JMESPathCheck('[1].weight', 20),
            JMESPathCheck('[1].label', "label2"),
            JMESPathCheck('[1].revisionName', revisions_list[1]["name"]),
        ])

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northeurope")
    @live_only()  # encounters 'CannotOverwriteExistingCassetteException' only when run from recording (passes when run live) and vnet command error in cli pipeline
    def test_containerapp_tcp_ingress(self, resource_group):
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))

        env_name = self.create_random_name(prefix='env', length=24)
        logs = self.create_random_name(prefix='logs', length=24)
        vnet = self.create_random_name(prefix='name', length=24)
        ca_name = self.create_random_name(prefix='containerapp', length=24)

        self.cmd(f"az network vnet create --address-prefixes '14.0.0.0/23' -g {resource_group} -n {vnet}")
        sub_id = self.cmd(f"az network vnet subnet create --address-prefixes '14.0.0.0/23' --delegations Microsoft.App/environments -n sub -g {resource_group} --vnet-name {vnet}").get_output_in_json()["id"]

        logs_id = self.cmd(f"monitor log-analytics workspace create -g {resource_group} -n {logs} -l eastus").get_output_in_json()["customerId"]
        logs_key = self.cmd(f'monitor log-analytics workspace get-shared-keys -g {resource_group} -n {logs}').get_output_in_json()["primarySharedKey"]

        self.cmd(f'containerapp env create -g {resource_group} -n {env_name} --logs-workspace-id {logs_id} --logs-workspace-key {logs_key} --internal-only -s {sub_id}')

        containerapp_env = self.cmd(f'containerapp env show -g {resource_group} -n {env_name}').get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd(f'containerapp env show -g {resource_group} -n {env_name}').get_output_in_json()

        self.cmd(f'containerapp env show -n {env_name} -g {resource_group}', checks=[
            JMESPathCheck('name', env_name),
            JMESPathCheck('properties.vnetConfiguration.internal', True),
        ])

        self.cmd('containerapp create -g {} -n {} --environment {} --ingress external --transport tcp --target-port 80 --exposed-port 3000'.format(resource_group, ca_name, env_name))

        self.cmd('containerapp ingress show -g {} -n {}'.format(resource_group, ca_name, env_name), checks=[
            JMESPathCheck('external', True),
            JMESPathCheck('targetPort', 80),
            JMESPathCheck('exposedPort', 3000),
            JMESPathCheck('transport', "Tcp"),
        ])

        self.cmd('containerapp ingress enable -g {} -n {} --type internal --target-port 81 --allow-insecure --transport http2'.format(resource_group, ca_name, env_name))

        self.cmd('containerapp ingress show -g {} -n {}'.format(resource_group, ca_name, env_name), checks=[
            JMESPathCheck('external', False),
            JMESPathCheck('targetPort', 81),
            JMESPathCheck('allowInsecure', True),
            JMESPathCheck('transport', "Http2"),
        ])

        self.cmd('containerapp ingress enable -g {} -n {} --type internal --target-port 81 --transport tcp --exposed-port 3020'.format(resource_group, ca_name, env_name))

        self.cmd('containerapp ingress show -g {} -n {}'.format(resource_group, ca_name, env_name), checks=[
            JMESPathCheck('external', False),
            JMESPathCheck('targetPort', 81),
            JMESPathCheck('transport', "Tcp"),
            JMESPathCheck('exposedPort', 3020),
        ])

        app = self.create_random_name(prefix='containerapp', length=24)

        self.cmd(
            f'containerapp create -g {resource_group} -n {app} --image redis --ingress external --target-port 6379 --environment {env_name} --transport tcp --scale-rule-type tcp --scale-rule-name tcp-scale-rule --scale-rule-tcp-concurrency 50 --scale-rule-auth trigger=secretref --scale-rule-metadata key=value',
            checks=[
                JMESPathCheck("properties.configuration.ingress.transport", "Tcp"),
                JMESPathCheck("properties.provisioningState", "Succeeded"),
                JMESPathCheck("properties.template.scale.rules[0].name", "tcp-scale-rule"),
                JMESPathCheck("properties.template.scale.rules[0].tcp.auth[0].triggerParameter", "trigger"),
                JMESPathCheck("properties.template.scale.rules[0].tcp.auth[0].secretRef", "secretref"),
            ])
        # the metadata is not returned in create/update command, we should use show command to check
        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.template.scale.rules[0].name", "tcp-scale-rule"),
            JMESPathCheck("properties.template.scale.rules[0].tcp.metadata.concurrentConnections", "50"),
            JMESPathCheck("properties.template.scale.rules[0].tcp.metadata.key", "value")
        ])
        self.cmd(
            f'containerapp update -g {resource_group} -n {app} --scale-rule-name tcp-scale-rule --scale-rule-type tcp  --scale-rule-tcp-concurrency 2 --scale-rule-auth "apiKey=api-key" "appKey=app-key"',
            checks=[
                JMESPathCheck("properties.configuration.ingress.transport", "Tcp"),
                JMESPathCheck("properties.provisioningState", "Succeeded"),
                JMESPathCheck("properties.template.scale.rules[0].name", "tcp-scale-rule"),
                JMESPathCheck("properties.template.scale.rules[0].tcp.auth[0].triggerParameter", "apiKey"),
                JMESPathCheck("properties.template.scale.rules[0].tcp.auth[0].secretRef", "api-key"),
                JMESPathCheck("properties.template.scale.rules[0].tcp.auth[1].triggerParameter", "appKey"),
                JMESPathCheck("properties.template.scale.rules[0].tcp.auth[1].secretRef", "app-key"),
            ])
        # the metadata is not returned in create/update command, we should use show command to check
        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.template.scale.rules[0].name", "tcp-scale-rule"),
            JMESPathCheck("properties.template.scale.rules[0].tcp.metadata.concurrentConnections", "2"),
        ])

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northeurope")
    def test_containerapp_ip_restrictions(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        ca_name = self.create_random_name(prefix='containerapp', length=24)

        env = prepare_containerapp_env_for_app_e2e_tests(self)

        # self.cmd('containerapp create -g {} -n {} --environment {}'.format(resource_group, ca_name, env_name))
        self.cmd('containerapp create -g {} -n {} --environment {} --ingress external --target-port 80'.format(resource_group, ca_name, env))

        self.cmd('containerapp ingress access-restriction set -g {} -n {} --rule-name name --ip-address 192.168.1.1/32 --description "Description here." --action Allow'.format(resource_group, ca_name), checks=[
            JMESPathCheck('[0].name', "name"),
            JMESPathCheck('[0].ipAddressRange', "192.168.1.1/32"),
            JMESPathCheck('[0].description', "Description here."),
            JMESPathCheck('[0].action', "Allow"),
        ])

        self.cmd('containerapp ingress access-restriction list -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('[0].name', "name"),
            JMESPathCheck('[0].ipAddressRange', "192.168.1.1/32"),
            JMESPathCheck('[0].description', "Description here."),
            JMESPathCheck('[0].action', "Allow"),
        ])

        self.cmd('containerapp ingress access-restriction set -g {} -n {} --rule-name name2 --ip-address 192.168.1.1/8 --description "Description here 2." --action Allow'.format(resource_group, ca_name), checks=[
            JMESPathCheck('[0].name', "name"),
            JMESPathCheck('[0].ipAddressRange', "192.168.1.1/32"),
            JMESPathCheck('[0].description', "Description here."),
            JMESPathCheck('[0].action', "Allow"),
            JMESPathCheck('[1].name', "name2"),
            JMESPathCheck('[1].ipAddressRange', "192.168.1.1/8"),
            JMESPathCheck('[1].description', "Description here 2."),
            JMESPathCheck('[1].action', "Allow"),
        ])

        self.cmd('containerapp ingress access-restriction list -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('[0].name', "name"),
            JMESPathCheck('[0].ipAddressRange', "192.168.1.1/32"),
            JMESPathCheck('[0].description', "Description here."),
            JMESPathCheck('[0].action', "Allow"),
            JMESPathCheck('[1].name', "name2"),
            JMESPathCheck('[1].ipAddressRange', "192.168.1.1/8"),
            JMESPathCheck('[1].description', "Description here 2."),
            JMESPathCheck('[1].action', "Allow"),
        ])

        self.cmd('containerapp ingress access-restriction remove -g {} -n {} --rule-name name'.format(resource_group, ca_name), checks=[
            JMESPathCheck('[0].name', "name2"),
            JMESPathCheck('[0].ipAddressRange', "192.168.1.1/8"),
            JMESPathCheck('[0].description', "Description here 2."),
            JMESPathCheck('[0].action', "Allow"),
        ])

        self.cmd('containerapp ingress access-restriction list -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('[0].name', "name2"),
            JMESPathCheck('[0].ipAddressRange', "192.168.1.1/8"),
            JMESPathCheck('[0].description', "Description here 2."),
            JMESPathCheck('[0].action', "Allow"),
        ])

        self.cmd('containerapp ingress access-restriction remove -g {} -n {} --rule-name name2'.format(resource_group, ca_name), checks=[
            JMESPathCheck('length(@)', 0),
        ])

        self.cmd('containerapp ingress access-restriction list -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('length(@)', 0),
        ])

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northeurope")
    def test_containerapp_ip_restrictions_deny(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        env_name = self.create_random_name(prefix='containerapp-env', length=24)
        ca_name = self.create_random_name(prefix='containerapp', length=24)

        env = prepare_containerapp_env_for_app_e2e_tests(self)

        # self.cmd('containerapp create -g {} -n {} --environment {}'.format(resource_group, ca_name, env_name))
        self.cmd('containerapp create -g {} -n {} --environment {} --ingress external --target-port 80'.format(resource_group, ca_name, env))

        self.cmd('containerapp ingress access-restriction set -g {} -n {} --rule-name name --ip-address 192.168.1.1/32 --description "Description here." --action Deny'.format(resource_group, ca_name), checks=[
            JMESPathCheck('[0].name', "name"),
            JMESPathCheck('[0].ipAddressRange', "192.168.1.1/32"),
            JMESPathCheck('[0].description', "Description here."),
            JMESPathCheck('[0].action', "Deny"),
        ])

        self.cmd('containerapp ingress access-restriction list -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('[0].name', "name"),
            JMESPathCheck('[0].ipAddressRange', "192.168.1.1/32"),
            JMESPathCheck('[0].description', "Description here."),
            JMESPathCheck('[0].action', "Deny"),
        ])

        self.cmd('containerapp ingress access-restriction set -g {} -n {} --rule-name name2 --ip-address 192.168.1.1/8 --description "Description here 2." --action Deny'.format(resource_group, ca_name), checks=[
            JMESPathCheck('[0].name', "name"),
            JMESPathCheck('[0].ipAddressRange', "192.168.1.1/32"),
            JMESPathCheck('[0].description', "Description here."),
            JMESPathCheck('[0].action', "Deny"),
            JMESPathCheck('[1].name', "name2"),
            JMESPathCheck('[1].ipAddressRange', "192.168.1.1/8"),
            JMESPathCheck('[1].description', "Description here 2."),
            JMESPathCheck('[1].action', "Deny"),
        ])

        self.cmd('containerapp ingress access-restriction list -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('[0].name', "name"),
            JMESPathCheck('[0].ipAddressRange', "192.168.1.1/32"),
            JMESPathCheck('[0].description', "Description here."),
            JMESPathCheck('[0].action', "Deny"),
            JMESPathCheck('[1].name', "name2"),
            JMESPathCheck('[1].ipAddressRange', "192.168.1.1/8"),
            JMESPathCheck('[1].description', "Description here 2."),
            JMESPathCheck('[1].action', "Deny"),
        ])

        self.cmd('containerapp ingress access-restriction remove -g {} -n {} --rule-name name'.format(resource_group, ca_name), checks=[
            JMESPathCheck('[0].name', "name2"),
            JMESPathCheck('[0].ipAddressRange', "192.168.1.1/8"),
            JMESPathCheck('[0].description', "Description here 2."),
            JMESPathCheck('[0].action', "Deny"),
        ])

        self.cmd('containerapp ingress access-restriction list -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('[0].name', "name2"),
            JMESPathCheck('[0].ipAddressRange', "192.168.1.1/8"),
            JMESPathCheck('[0].description', "Description here 2."),
            JMESPathCheck('[0].action', "Deny"),
        ])

        self.cmd('containerapp ingress access-restriction remove -g {} -n {} --rule-name name2'.format(resource_group, ca_name), checks=[
            JMESPathCheck('length(@)', 0),
        ])

        self.cmd('containerapp ingress access-restriction list -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('length(@)', 0),
        ])

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northeurope")
    def test_containerapp_cors_policy(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        ca_name = self.create_random_name(prefix='containerapp', length=24)

        env = prepare_containerapp_env_for_app_e2e_tests(self)

        self.cmd('containerapp create -g {} -n {} --environment {} --ingress external --target-port 80'.format(resource_group, ca_name, env))

        self.cmd('containerapp ingress cors enable -g {} -n {} --allowed-origins "http://www.contoso.com" "https://www.contoso.com" --allowed-methods "GET" "POST" --allowed-headers "header1" "header2" --expose-headers "header3" "header4" --allow-credentials true --max-age 100'.format(resource_group, ca_name), checks=[
            JMESPathCheck('length(allowedOrigins)', 2),
            JMESPathCheck('allowedOrigins[0]', "http://www.contoso.com"),
            JMESPathCheck('allowedOrigins[1]', "https://www.contoso.com"),
            JMESPathCheck('length(allowedMethods)', 2),
            JMESPathCheck('allowedMethods[0]', "GET"),
            JMESPathCheck('allowedMethods[1]', "POST"),
            JMESPathCheck('length(allowedHeaders)', 2),
            JMESPathCheck('allowedHeaders[0]', "header1"),
            JMESPathCheck('allowedHeaders[1]', "header2"),
            JMESPathCheck('length(exposeHeaders)', 2),
            JMESPathCheck('exposeHeaders[0]', "header3"),
            JMESPathCheck('exposeHeaders[1]', "header4"),
            JMESPathCheck('allowCredentials', True),
            JMESPathCheck('maxAge', 100),
        ])

        self.cmd('containerapp ingress cors update -g {} -n {} --allowed-origins "*" --allowed-methods "GET" --allowed-headers "header1" --expose-headers --allow-credentials false --max-age 0'.format(resource_group, ca_name), checks=[
            JMESPathCheck('length(allowedOrigins)', 1),
            JMESPathCheck('allowedOrigins[0]', "*"),
            JMESPathCheck('length(allowedMethods)', 1),
            JMESPathCheck('allowedMethods[0]', "GET"),
            JMESPathCheck('length(allowedHeaders)', 1),
            JMESPathCheck('allowedHeaders[0]', "header1"),
            JMESPathCheck('exposeHeaders', None),
            JMESPathCheck('allowCredentials', False),
            JMESPathCheck('maxAge', 0),
        ])

        self.cmd('containerapp ingress cors show -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('length(allowedOrigins)', 1),
            JMESPathCheck('allowedOrigins[0]', "*"),
            JMESPathCheck('length(allowedMethods)', 1),
            JMESPathCheck('allowedMethods[0]', "GET"),
            JMESPathCheck('length(allowedHeaders)', 1),
            JMESPathCheck('allowedHeaders[0]', "header1"),
            JMESPathCheck('exposeHeaders', None),
            JMESPathCheck('allowCredentials', False),
            JMESPathCheck('maxAge', 0),
        ])

        self.cmd('containerapp ingress cors disable -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('corsPolicy', None),
        ])

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="westeurope")
    def test_containerapp_env_premium_ingress_commands(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        env_name = self.create_random_name(prefix='containerapp-env', length=24)
        self.cmd(f'containerapp env create -g {resource_group} -n {env_name} --logs-destination none')

        containerapp_env = self.cmd(f'containerapp env show -g {resource_group} -n {env_name}').get_output_in_json()

        self.cmd(f'az containerapp env workload-profile add -g {resource_group} -n {env_name} -w wp-ingress --min-nodes 2 --max-nodes 5 --workload-profile-type D4'.format(env_name, resource_group))

        self.cmd(f'containerapp env premium-ingress show -g {resource_group} -n {env_name}', checks=[
            JMESPathCheck('message', 'No premium ingress configuration found for this environment, using default values.'),
        ])

        self.cmd(f'containerapp env premium-ingress add -g {resource_group} -n {env_name} -w wp-ingress --min-replicas 3 --max-replicas 5', checks=[
            JMESPathCheck('workloadProfileName', 'wp-ingress'),
            JMESPathCheck('scale.minReplicas', 3),
            JMESPathCheck('scale.maxReplicas', 5),
            JMESPathCheck('terminationGracePeriodSeconds', None),
            JMESPathCheck('requestIdleTimeout', None),
            JMESPathCheck('headerCountLimit', None),
        ])
        
        self.cmd(f'containerapp env premium-ingress show -g {resource_group} -n {env_name}', checks=[
            JMESPathCheck('workloadProfileName', 'wp-ingress'),
            JMESPathCheck('scale.minReplicas', 3),
            JMESPathCheck('scale.maxReplicas', 5),
            JMESPathCheck('terminationGracePeriodSeconds', None),
            JMESPathCheck('requestIdleTimeout', None),
            JMESPathCheck('headerCountLimit', None),
        ])
        
        self.cmd(f'containerapp env premium-ingress update -g {resource_group} -n {env_name} --min-replicas 4 --max-replicas 20 --termination-grace-period 45 --request-idle-timeout 180 --header-count-limit 40', checks=[
            JMESPathCheck('workloadProfileName', 'wp-ingress'),
            JMESPathCheck('scale.minReplicas', 4),
            JMESPathCheck('scale.maxReplicas', 20),
            JMESPathCheck('terminationGracePeriodSeconds', 45),
            JMESPathCheck('requestIdleTimeout', 180),
            JMESPathCheck('headerCountLimit', 40),
        ])

        # set removes unspecified optional parameters
        self.cmd(f'containerapp env premium-ingress add -g {resource_group} -n {env_name} -w wp-ingress --min-replicas 2 --max-replicas 3 --request-idle-timeout 90', checks=[
            JMESPathCheck('workloadProfileName', 'wp-ingress'),
            JMESPathCheck('scale.minReplicas', 2),
            JMESPathCheck('scale.maxReplicas', 3),
            JMESPathCheck('requestIdleTimeout', 90),
            JMESPathCheck('terminationGracePeriodSeconds', None),
            JMESPathCheck('headerCountLimit', None),
        ])

        self.cmd(f'containerapp env premium-ingress remove -g {resource_group} -n {env_name} -y')
    
        self.cmd(f'containerapp env premium-ingress show -g {resource_group} -n {env_name}', checks=[
            JMESPathCheck('message', 'No premium ingress configuration found for this environment, using default values.'),
        ])

        # Clean up
        self.cmd(f'containerapp env delete -g {resource_group} -n {env_name} --yes --no-wait')


class ContainerappCustomDomainTests(ScenarioTest):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, random_config_dir=True, **kwargs)

    @AllowLargeResponse(8192)
    @live_only()  # encounters 'CannotOverwriteExistingCassetteException' only when run from recording (passes when run live)
    @ResourceGroupPreparer(location="westeurope")
    def test_containerapp_custom_domains_e2e(self, resource_group):
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))

        env_name = self.create_random_name(prefix='containerapp-env', length=24)
        ca_name = self.create_random_name(prefix='containerapp', length=24)

        create_containerapp_env(self, env_name, resource_group)

        app = self.cmd('containerapp create -g {} -n {} --environment {} --ingress external --target-port 80'.format(resource_group, ca_name, env_name)).get_output_in_json()

        self.cmd('containerapp hostname list -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('length(@)', 0),
        ])

        # list hostnames with a wrong location
        self.cmd('containerapp hostname list -g {} -n {} -l "{}"'.format(resource_group, ca_name, "eastus2"), checks={
            JMESPathCheck('length(@)', 0),
        }, expect_failure=True)

        # create an App service domain and update its txt records
        contacts = os.path.join(TEST_DIR, 'domain-contact.json')
        zone_name = "{}.com".format(ca_name)
        subdomain_1 = "devtest"
        subdomain_2 = "clitest"
        txt_name_1 = "asuid.{}".format(subdomain_1)
        txt_name_2 = "asuid.{}".format(subdomain_2)
        hostname_1 = "{}.{}".format(subdomain_1, zone_name)
        hostname_2 = "{}.{}".format(subdomain_2, zone_name)
        verification_id = app["properties"]["customDomainVerificationId"]
        self.cmd("appservice domain create -g {} --hostname {} --contact-info=@'{}' --accept-terms".format(resource_group, zone_name, contacts)).get_output_in_json()
        self.cmd('network dns record-set txt add-record -g {} -z {} -n {} -v {}'.format(resource_group, zone_name, txt_name_1, verification_id)).get_output_in_json()
        self.cmd('network dns record-set txt add-record -g {} -z {} -n {} -v {}'.format(resource_group, zone_name, txt_name_2, verification_id)).get_output_in_json()

        # upload cert, add hostname & binding
        pfx_file = os.path.join(TEST_DIR, 'cert.pfx')
        pfx_password = 'test12'
        cert_id = self.cmd('containerapp ssl upload -n {} -g {} --environment {} --hostname {} --certificate-file "{}" --password {}'.format(ca_name, resource_group, env_name, hostname_1, pfx_file, pfx_password), checks=[
            JMESPathCheck('[0].name', hostname_1),
        ]).get_output_in_json()[0]["certificateId"]

        self.cmd('containerapp hostname list -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('length(@)', 1),
            JMESPathCheck('[0].name', hostname_1),
            JMESPathCheck('[0].bindingType', "SniEnabled"),
            JMESPathCheck('[0].certificateId', cert_id),
        ])

        # get cert thumbprint
        cert_thumbprint = self.cmd('containerapp env certificate list -n {} -g {} -c {}'.format(env_name, resource_group, cert_id), checks=[
            JMESPathCheck('length(@)', 1),
            JMESPathCheck('[0].id', cert_id),
        ]).get_output_in_json()[0]["properties"]["thumbprint"]

        # add binding by cert thumbprint
        self.cmd('containerapp hostname bind -g {} -n {} --hostname {} --thumbprint {}'.format(resource_group, ca_name, hostname_2, cert_thumbprint), expect_failure=True)

        self.cmd('containerapp hostname bind -g {} -n {} --hostname {} --thumbprint {} -e {}'.format(resource_group, ca_name, hostname_2, cert_thumbprint, env_name), checks=[
            JMESPathCheck('length(@)', 2),
        ])

        self.cmd('containerapp hostname list -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('length(@)', 2),
            JMESPathCheck('[0].bindingType', "SniEnabled"),
            JMESPathCheck('[0].certificateId', cert_id),
            JMESPathCheck('[1].bindingType', "SniEnabled"),
            JMESPathCheck('[1].certificateId', cert_id),
        ])

        # delete hostname with a wrong location
        self.cmd('containerapp hostname delete -g {} -n {} --hostname {} -l "{}" --yes'.format(resource_group, ca_name, hostname_1, "eastus2"), expect_failure=True)

        self.cmd('containerapp hostname delete -g {} -n {} --hostname {} -l "{}" --yes'.format(resource_group, ca_name, hostname_1, app["location"]), checks=[
            JMESPathCheck('length(@)', 1),
            JMESPathCheck('[0].name', hostname_2),
            JMESPathCheck('[0].bindingType', "SniEnabled"),
            JMESPathCheck('[0].certificateId', cert_id),
        ]).get_output_in_json()

        self.cmd('containerapp hostname list -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('length(@)', 1),
            JMESPathCheck('[0].name', hostname_2),
            JMESPathCheck('[0].bindingType', "SniEnabled"),
            JMESPathCheck('[0].certificateId', cert_id),
        ])

        self.cmd('containerapp hostname delete -g {} -n {} --hostname {} --yes'.format(resource_group, ca_name, hostname_2), checks=[
            JMESPathCheck('length(@)', 0),
        ]).get_output_in_json()

        # add binding by cert id
        self.cmd('containerapp hostname bind -g {} -n {} --hostname {} --certificate {}'.format(resource_group, ca_name, hostname_2, cert_id), checks=[
            JMESPathCheck('length(@)', 1),
            JMESPathCheck('[0].bindingType', "SniEnabled"),
            JMESPathCheck('[0].certificateId', cert_id),
            JMESPathCheck('[0].name', hostname_2),
        ]).get_output_in_json()

        self.cmd('containerapp hostname delete -g {} -n {} --hostname {} --yes'.format(resource_group, ca_name, hostname_2), checks=[
            JMESPathCheck('length(@)', 0),
        ]).get_output_in_json()

        # add binding by cert name, with and without environment
        cert_name = parse_resource_id(cert_id)["resource_name"]

        self.cmd('containerapp hostname bind -g {} -n {} --hostname {} --certificate {}'.format(resource_group, ca_name, hostname_1, cert_name), expect_failure=True)

        self.cmd('containerapp hostname bind -g {} -n {} --hostname {} --certificate {} -e {}'.format(resource_group, ca_name, hostname_1, cert_name, env_name), checks=[
            JMESPathCheck('length(@)', 1),
            JMESPathCheck('[0].bindingType', "SniEnabled"),
            JMESPathCheck('[0].certificateId', cert_id),
            JMESPathCheck('[0].name', hostname_1),
        ]).get_output_in_json()

        self.cmd('containerapp hostname delete -g {} -n {} --hostname {} --yes'.format(resource_group, ca_name, hostname_1), checks=[
            JMESPathCheck('length(@)', 0),
        ]).get_output_in_json()


class ContainerappDaprTests(ScenarioTest):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, random_config_dir=True, **kwargs)

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="eastus2")
    def test_containerapp_dapr_e2e(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        ca_name = self.create_random_name(prefix='containerapp', length=24)

        env = prepare_containerapp_env_for_app_e2e_tests(self)

        self.cmd('containerapp create -g {} -n {} --environment {} --dapr-app-id containerapp --dapr-app-port 800 --dapr-app-protocol grpc --dhmrs 4 --dhrbs 50 --dapr-log-level debug --enable-dapr'.format(resource_group, ca_name, env), checks=[
            JMESPathCheck('properties.configuration.dapr.appId', "containerapp"),
            JMESPathCheck('properties.configuration.dapr.appPort', 800),
            JMESPathCheck('properties.configuration.dapr.appProtocol', "grpc"),
            JMESPathCheck('properties.configuration.dapr.enabled', True),
            JMESPathCheck('properties.configuration.dapr.httpReadBufferSize', 50),
            JMESPathCheck('properties.configuration.dapr.httpMaxRequestSize', 4),
            JMESPathCheck('properties.configuration.dapr.logLevel', "debug"),
            JMESPathCheck('properties.configuration.dapr.enableApiLogging', False),
        ])

        self.cmd('containerapp dapr enable -g {} -n {} --dapr-app-id containerapp1 --dapr-app-port 80 --dapr-app-protocol http --dal --dhmrs 6 --dhrbs 60 --dapr-log-level warn'.format(resource_group, ca_name, env), checks=[
            JMESPathCheck('appId', "containerapp1"),
            JMESPathCheck('appPort', 80),
            JMESPathCheck('appProtocol', "http"),
            JMESPathCheck('enabled', True),
            JMESPathCheck('httpReadBufferSize', 60),
            JMESPathCheck('httpMaxRequestSize', 6),
            JMESPathCheck('logLevel', "warn"),
            JMESPathCheck('enableApiLogging', True),
        ])

        self.cmd('containerapp show -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('properties.configuration.dapr.appId', "containerapp1"),
            JMESPathCheck('properties.configuration.dapr.appPort', 80),
            JMESPathCheck('properties.configuration.dapr.appProtocol', "http"),
            JMESPathCheck('properties.configuration.dapr.enabled', True),
            JMESPathCheck('properties.configuration.dapr.httpReadBufferSize', 60),
            JMESPathCheck('properties.configuration.dapr.httpMaxRequestSize', 6),
            JMESPathCheck('properties.configuration.dapr.logLevel', "warn"),
            JMESPathCheck('properties.configuration.dapr.enableApiLogging', True),
        ])

        self.cmd('containerapp dapr disable -g {} -n {}'.format(resource_group, ca_name, env), checks=[
            JMESPathCheck('appId', "containerapp1"),
            JMESPathCheck('appPort', 80),
            JMESPathCheck('appProtocol', "http"),
            JMESPathCheck('enabled', False),
            JMESPathCheck('httpReadBufferSize', 60),
            JMESPathCheck('httpMaxRequestSize', 6),
            JMESPathCheck('logLevel', "warn"),
            JMESPathCheck('enableApiLogging', True),
        ])

        self.cmd('containerapp show -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('properties.configuration.dapr.appId', "containerapp1"),
            JMESPathCheck('properties.configuration.dapr.appPort', 80),
            JMESPathCheck('properties.configuration.dapr.appProtocol', "http"),
            JMESPathCheck('properties.configuration.dapr.enabled', False),
            JMESPathCheck('properties.configuration.dapr.httpReadBufferSize', 60),
            JMESPathCheck('properties.configuration.dapr.httpMaxRequestSize', 6),
            JMESPathCheck('properties.configuration.dapr.logLevel', "warn"),
            JMESPathCheck('properties.configuration.dapr.enableApiLogging', True),
        ])

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="eastus2")
    def test_containerapp_up_dapr_e2e(self, resource_group):
        """ Ensure that dapr can be enabled if the app has been created using containerapp up """
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        image = 'mcr.microsoft.com/azuredocs/aks-helloworld:v1'
        ca_name = self.create_random_name(prefix='containerapp', length=24)

        env = prepare_containerapp_env_for_app_e2e_tests(self)

        self.cmd(
            'containerapp up -g {} -n {} --environment {} --image {}'.format(
                resource_group, ca_name, env, image))

        self.cmd(
            'containerapp dapr enable -g {} -n {} --dapr-app-id containerapp1 --dapr-app-port 80 '
            '--dapr-app-protocol http --dal --dhmrs 6 --dhrbs 60 --dapr-log-level warn'.format(
                resource_group, ca_name), checks=[
                JMESPathCheck('appId', "containerapp1"),
                JMESPathCheck('enabled', True)
            ])


class ContainerappServiceBindingTests(ScenarioTest):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, random_config_dir=True, **kwargs)

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="eastus2")
    def test_containerapp_dev_add_on_binding_none_client_type(self, resource_group):
        # type "linkers" is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use eastus as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))
        ca_name = self.create_random_name(prefix='containerapp1', length=24)
        redis_ca_name = 'redis'
        postgres_ca_name = 'postgres'
        kafka_ca_name = 'kafka'

        env_id = prepare_containerapp_env_for_app_e2e_tests(self, location)
        env_rg = parse_resource_id(env_id).get('resource_group')
        env_name = parse_resource_id(env_id).get('name')

        self.cmd('containerapp add-on redis create -g {} -n {} --environment {}'.format(env_rg, redis_ca_name, env_name), checks=[
            JMESPathCheck('properties.provisioningState', "Succeeded")
        ])

        self.cmd('containerapp add-on postgres create -g {} -n {} --environment {}'.format(env_rg, postgres_ca_name, env_name), checks=[
            JMESPathCheck('properties.provisioningState', "Succeeded")
        ])
        self.cmd('containerapp add-on kafka create -g {} -n {} --environment {}'.format(env_rg, kafka_ca_name, env_name), checks=[
            JMESPathCheck('properties.provisioningState', "Succeeded")
        ])

        self.cmd(
            'containerapp create -n {} -g {} --environment {} --bind {},clientType=dotnet,resourcegroup={} {},clientType=none,resourcegroup={}'.format(
                ca_name, resource_group, env_id, redis_ca_name, env_rg, postgres_ca_name, env_rg), expect_failure=False, checks=[
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('length(properties.template.serviceBinds)', 2),
                JMESPathCheck('properties.template.serviceBinds[0].name', redis_ca_name),
                JMESPathCheck('properties.template.serviceBinds[0].clientType', "dotnet"),
                JMESPathCheck('properties.template.serviceBinds[1].name', postgres_ca_name),
                JMESPathCheck('properties.template.serviceBinds[1].clientType', "none"),
            ])

        # test clean clientType
        self.cmd(
            'containerapp update -n {} -g {} --bind {},clientType=none,resourcegroup={}'.format(
                ca_name, resource_group, redis_ca_name, env_rg), expect_failure=False, checks=[
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('length(properties.template.serviceBinds)', 2),
                JMESPathCheck('properties.template.serviceBinds[0].name', redis_ca_name),
                JMESPathCheck('properties.template.serviceBinds[0].clientType', "none"),
                JMESPathCheck('properties.template.serviceBinds[1].name', postgres_ca_name),
                JMESPathCheck('properties.template.serviceBinds[1].clientType', "none"),
            ])

        self.cmd(
            'containerapp create -n {} -g {} --environment {} --bind {},resourcegroup={}'.format(
                ca_name, resource_group, env_id, kafka_ca_name, env_rg), expect_failure=False,
            checks=[
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('length(properties.template.serviceBinds)', 1),
                JMESPathCheck('properties.template.serviceBinds[0].name', kafka_ca_name),
                JMESPathCheck('properties.template.serviceBinds[0].clientType', "none"),
            ])

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="eastus2")
    def test_containerapp_dev_add_on_binding_customized_keys_yaml_e2e(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))
        ca_name = self.create_random_name(prefix='containerapp1', length=24)
        redis_ca_name = 'redis-yaml2'
        postgres_ca_name = 'postgres-yaml'

        env_id = prepare_containerapp_env_for_app_e2e_tests(self)
        env_rg = parse_resource_id(env_id).get('resource_group')
        env_name = parse_resource_id(env_id).get('name')

        redis_resource_id = self.cmd('containerapp add-on redis create -g {} -n {} --environment {}'.format(env_rg, redis_ca_name, env_name), checks=[
            JMESPathCheck('properties.provisioningState', "Succeeded")
        ]).get_output_in_json()["id"]

        postgres_resource_id = self.cmd('containerapp add-on postgres create -g {} -n {} --environment {}'.format(env_rg, postgres_ca_name, env_name)).get_output_in_json()["id"]
        # test create
        containerapp_yaml_text = f"""
                                location: {TEST_LOCATION}
                                type: Microsoft.App/containerApps
                                properties:
                                  managedEnvironmentId: {env_id}
                                  configuration:
                                    activeRevisionsMode: single
                                  template:
                                    containers:
                                      - image: mcr.microsoft.com/k8se/quickstart:latest
                                        name: {ca_name}
                                    serviceBinds:
                                      - serviceId: {redis_resource_id}
                                        name: redis
                                        clientType: dotnet
                                        customizedKeys:
                                         CACHE_1_ENDPOINT: REDIS_HOST
                                         CACHE_1_PASSWORD: REDIS_PASSWORD
                                      - serviceId: {postgres_resource_id}
                                        name: postgres
                                        clientType: none
                                        customizedKeys:
                                          DB_ENDPOINT: POSTGRES_HOST
                                          DB_PASSWORD: POSTGRES_PASSWORD
                                """
        containerapp_file_name = f"{self._testMethodName}_containerapp.yml"

        write_test_file(containerapp_file_name, containerapp_yaml_text)
        self.cmd(
            f'containerapp create -n {ca_name} -g {resource_group} --environment {env_id} --yaml {containerapp_file_name}', checks=[
                JMESPathCheck("properties.provisioningState", "Succeeded"),
                JMESPathCheck('length(properties.template.serviceBinds)', 2),
                JMESPathCheck('properties.template.serviceBinds[0].name', "redis"),
                JMESPathCheck('properties.template.serviceBinds[0].clientType', "dotnet"),
                JMESPathCheck('properties.template.serviceBinds[0].customizedKeys.CACHE_1_ENDPOINT', "REDIS_HOST"),
                JMESPathCheck('properties.template.serviceBinds[0].customizedKeys.CACHE_1_PASSWORD', "REDIS_PASSWORD"),
                JMESPathCheck('properties.template.serviceBinds[1].name', "postgres"),
                JMESPathCheck('properties.template.serviceBinds[1].clientType', "none"),
                JMESPathCheck('properties.template.serviceBinds[1].customizedKeys.DB_ENDPOINT', "POSTGRES_HOST"),
                JMESPathCheck('properties.template.serviceBinds[1].customizedKeys.DB_PASSWORD', "POSTGRES_PASSWORD")
            ])
        # test update customizedKeys without clientType
        self.cmd(
            'containerapp update -n {} -g  {} --bind {}:redis,resourcegroup={} --customized-keys CACHE_2_ENDPOINT=REDIS_HOST CACHE_2_PASSWORD=REDIS_PASSWORD'.format(
                ca_name, resource_group, redis_ca_name, env_rg), expect_failure=False, checks=[
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('length(properties.template.serviceBinds)', 2),
                JMESPathCheck('properties.template.serviceBinds[0].name', "redis"),
                JMESPathCheck('properties.template.serviceBinds[0].clientType', "dotnet"),
                JMESPathCheck('properties.template.serviceBinds[0].customizedKeys.CACHE_2_ENDPOINT', "REDIS_HOST"),
                JMESPathCheck('properties.template.serviceBinds[0].customizedKeys.CACHE_2_PASSWORD', "REDIS_PASSWORD"),
                JMESPathCheck('properties.template.serviceBinds[1].name', "postgres"),
                JMESPathCheck('properties.template.serviceBinds[1].clientType', "none"),
                JMESPathCheck('properties.template.serviceBinds[1].customizedKeys.DB_ENDPOINT', "POSTGRES_HOST"),
                JMESPathCheck('properties.template.serviceBinds[1].customizedKeys.DB_PASSWORD', "POSTGRES_PASSWORD")
            ])

        # test update customizedKeys with yaml
        containerapp_yaml_text = f"""
                                        properties:
                                          template:
                                            serviceBinds:
                                              - serviceId: {redis_resource_id}
                                                name: redis
                                                customizedKeys:
                                                 CACHE_3_ENDPOINT: REDIS_HOST
                                                 CACHE_3_PASSWORD: REDIS_PASSWORD
                                              - serviceId: {postgres_resource_id}
                                                name: postgres
                                                customizedKeys:
                                                  DB_2_ENDPOINT: POSTGRES_HOST
                                                  DB_2_PASSWORD: POSTGRES_PASSWORD
                                        """
        containerapp_file_name = f"{self._testMethodName}_containerapp.yml"
        write_test_file(containerapp_file_name, containerapp_yaml_text)
        self.cmd(
            f'containerapp update -n {ca_name} -g {resource_group} --yaml {containerapp_file_name}',
            checks=[
                JMESPathCheck("properties.provisioningState", "Succeeded"),
                JMESPathCheck('length(properties.template.serviceBinds)', 2),
                JMESPathCheck('properties.template.serviceBinds[0].name', "redis"),
                JMESPathCheck('properties.template.serviceBinds[0].clientType', "none"),
                JMESPathCheck('properties.template.serviceBinds[0].customizedKeys.CACHE_3_ENDPOINT', "REDIS_HOST"),
                JMESPathCheck('properties.template.serviceBinds[0].customizedKeys.CACHE_3_PASSWORD', "REDIS_PASSWORD"),
                JMESPathCheck('properties.template.serviceBinds[1].name', "postgres"),
                JMESPathCheck('properties.template.serviceBinds[1].clientType', "none"),
                JMESPathCheck('properties.template.serviceBinds[1].customizedKeys.DB_2_ENDPOINT', "POSTGRES_HOST"),
                JMESPathCheck('properties.template.serviceBinds[1].customizedKeys.DB_2_PASSWORD', "POSTGRES_PASSWORD")
            ])

        # test update with yaml to clean customizedKeys
        containerapp_yaml_text = f"""
                                                properties:
                                                  template:
                                                    serviceBinds:
                                                      - serviceId: {redis_resource_id}
                                                        name: redis
                                                      - serviceId: {postgres_resource_id}
                                                        name: postgres
                                                """
        containerapp_file_name = f"{self._testMethodName}_containerapp.yml"
        write_test_file(containerapp_file_name, containerapp_yaml_text)
        self.cmd(
            f'containerapp update -n {ca_name} -g {resource_group} --yaml {containerapp_file_name}',
            checks=[
                JMESPathCheck("properties.provisioningState", "Succeeded"),
                JMESPathCheck('length(properties.template.serviceBinds)', 2),
                JMESPathCheck('properties.template.serviceBinds[0].name', "redis"),
                JMESPathCheck('properties.template.serviceBinds[0].clientType', "none"),
                JMESPathCheck('properties.template.serviceBinds[0].customizedKeys', None),
                JMESPathCheck('properties.template.serviceBinds[1].name', "postgres"),
                JMESPathCheck('properties.template.serviceBinds[1].clientType', "none"),
                JMESPathCheck('properties.template.serviceBinds[1].customizedKeys', None),
            ])

        self.cmd('containerapp add-on redis delete -g {} -n {} --yes'.format(env_rg, redis_ca_name), expect_failure=False)
        self.cmd('containerapp add-on postgres delete -g {} -n {} --yes'.format(env_rg, postgres_ca_name), expect_failure=False)
        self.cmd('containerapp delete -n {} -g {} --yes'.format(ca_name, resource_group), expect_failure=False)
        clean_up_test_file(containerapp_file_name)

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="eastus2")
    def test_containerapp_dev_add_on_binding_customized_keys_e2e(self, resource_group):
        # type "linkers" is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use eastus as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))
        ca_name = self.create_random_name(prefix='containerapp1', length=24)
        redis_ca_name = 'redis'
        postgres_ca_name = 'postgres'

        env_id = prepare_containerapp_env_for_app_e2e_tests(self, location=location)
        env_rg = parse_resource_id(env_id).get('resource_group')
        env_name = parse_resource_id(env_id).get('name')

        redis_resource_id = self.cmd('containerapp add-on redis create -g {} -n {} --environment {}'.format(env_rg, redis_ca_name, env_name), checks=[
            JMESPathCheck('properties.provisioningState', "Succeeded")
        ]).get_output_in_json()["id"]

        self.cmd('containerapp add-on postgres create -g {} -n {} --environment {}'.format(env_rg, postgres_ca_name, env_name))
        self.cmd(
            'containerapp create -n {} -g  {} --environment {} --bind {},clientType=dotnet,resourcegroup={} {},clientType=none,resourcegroup={}'.format(
                ca_name, resource_group, env_id, redis_ca_name, env_rg, postgres_ca_name, env_rg), expect_failure=False, checks=[
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('length(properties.template.serviceBinds)', 2),
                JMESPathCheck('properties.template.serviceBinds[0].name', redis_ca_name),
                JMESPathCheck('properties.template.serviceBinds[0].clientType', "dotnet"),
                JMESPathCheck('properties.template.serviceBinds[1].name', postgres_ca_name),
                JMESPathCheck('properties.template.serviceBinds[1].clientType', "none"),
            ])
        # For multi-bind with --customized-keys throw error out
        ca_name2 = self.create_random_name(prefix='containerapp2', length=24)
        err_msg = None
        try:
            self.cmd(
                'containerapp create -n {} -g  {} --environment {} --bind {},clientType=dotnet {} --customized-keys CACHE_1_ENDPOINT=REDIS_HOST CACHE_1_PASSWORD=REDIS_PASSWORD'.format(
                    ca_name2, resource_group, env_id, redis_ca_name, postgres_ca_name))
        except Exception as e:
            err_msg = e.error_msg
        self.assertIsNotNone(err_msg)
        self.assertTrue(err_msg.__contains__(
            '--bind have multiple values, but --customized-keys only can be set when --bind is single'))
        err_msg = None
        try:
            self.cmd(
            'containerapp update -n {} -g  {} --bind {},clientType=dotnet {} --customized-keys CACHE_1_ENDPOINT=REDIS_HOST CACHE_1_PASSWORD=REDIS_PASSWORD'.format(
                ca_name, resource_group, redis_ca_name, postgres_ca_name))
        except Exception as e:
            err_msg = e.error_msg
        self.assertIsNotNone(err_msg)
        self.assertTrue(err_msg.__contains__(
            '--bind have multiple values, but --customized-keys only can be set when --bind is single'))

        # For single-bind with --customized-keys
        self.cmd(
            'containerapp update -n {} -g  {} --bind {},clientType=dotnet,resourcegroup={} --customized-keys CACHE_1_ENDPOINT=REDIS_HOST CACHE_1_PASSWORD=REDIS_PASSWORD'.format(
                ca_name, resource_group, redis_ca_name, env_rg), expect_failure=False, checks=[
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('length(properties.template.serviceBinds)', 2),
                JMESPathCheck('properties.template.serviceBinds[0].name', redis_ca_name),
                JMESPathCheck('properties.template.serviceBinds[0].clientType', "dotnet"),
                JMESPathCheck('properties.template.serviceBinds[0].customizedKeys.CACHE_1_ENDPOINT', "REDIS_HOST"),
                JMESPathCheck('properties.template.serviceBinds[0].customizedKeys.CACHE_1_PASSWORD', "REDIS_PASSWORD"),
                JMESPathCheck('properties.template.serviceBinds[1].name', postgres_ca_name),
                JMESPathCheck('properties.template.serviceBinds[1].clientType', "none"),
                JMESPathCheck('properties.template.serviceBinds[1].customizedKeys', None),
            ])
        self.cmd('containerapp delete -n {} -g {} --yes'.format(ca_name, resource_group), expect_failure=False)

        self.cmd(
            'containerapp create -n {} -g  {} --environment {} --bind {},clientType=dotnet,resourcegroup={} --customized-keys CACHE_2_ENDPOINT=REDIS_HOST CACHE_2_PASSWORD=REDIS_PASSWORD'.format(
                ca_name2, resource_group, env_id, redis_ca_name, env_rg), expect_failure=False, checks=[
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('length(properties.template.serviceBinds)', 1),
                JMESPathCheck('properties.template.serviceBinds[0].name', redis_ca_name),
                JMESPathCheck('properties.template.serviceBinds[0].clientType', "dotnet"),
                JMESPathCheck('properties.template.serviceBinds[0].customizedKeys.CACHE_2_ENDPOINT', "REDIS_HOST"),
                JMESPathCheck('properties.template.serviceBinds[0].customizedKeys.CACHE_2_PASSWORD', "REDIS_PASSWORD")
            ])
        self.cmd('containerapp update -n {} -g {} --unbind {}'.format(
            ca_name2, resource_group, redis_ca_name), checks=[
            JMESPathCheck('properties.template.serviceBinds', None),
        ])
        self.cmd('containerapp add-on redis delete -g {} -n {} --yes'.format(env_rg, redis_ca_name))
        self.cmd('containerapp add-on postgres delete -g {} -n {} --yes'.format(env_rg, postgres_ca_name))
        self.cmd('containerapp delete -n {} -g {} --yes'.format(ca_name2, resource_group), expect_failure=False)

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="eastus2")
    @SubnetPreparer(location="eastus", delegations='Microsoft.App/environments', service_endpoints="Microsoft.Storage.Global")
    def test_containerapp_dev_add_on_binding_e2e(self, resource_group, subnet_id):
        # type "linkers" is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use eastus as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))

        env_name = self.create_random_name(prefix='containerapp-env', length=24)
        ca_name = self.create_random_name(prefix='containerapp', length=24)
        image = "mcr.microsoft.com/azuredocs/containerapps-helloworld:latest"
        redis_ca_name = 'redis'
        postgres_ca_name = 'postgres'
        kafka_ca_name = 'kafka'
        mariadb_ca_name = 'mariadb'
        qdrant_ca_name = "qdrant"

        create_containerapp_env(self, env_name, resource_group, subnetId=subnet_id)

        self.cmd('containerapp add-on redis create -g {} -n {} --environment {}'.format(
            resource_group, redis_ca_name, env_name))

        self.cmd('containerapp add-on postgres create -g {} -n {} --environment {}'.format(
            resource_group, postgres_ca_name, env_name))

        self.cmd('containerapp add-on kafka create -g {} -n {} --environment {}'.format(
            resource_group, kafka_ca_name, env_name))

        self.cmd('containerapp add-on mariadb create -g {} -n {} --environment {}'.format(
            resource_group, mariadb_ca_name, env_name))

        self.cmd('containerapp add-on qdrant create -g {} -n {} --environment {}'.format(
            resource_group, qdrant_ca_name, env_name))

        self.cmd('containerapp create -g {} -n {} --environment {} --image {} --bind postgres:postgres_binding redis'.format(
            resource_group, ca_name, env_name, image), checks=[
            JMESPathCheck('properties.template.serviceBinds[0].name', "postgres_binding"),
            JMESPathCheck('properties.template.serviceBinds[1].name', "redis")
        ])

        self.cmd('containerapp update -g {} -n {} --unbind postgres_binding'.format(
            resource_group, ca_name, image), checks=[
            JMESPathCheck('properties.template.serviceBinds[0].name', "redis"),
        ])

        self.cmd('containerapp update -g {} -n {} --bind postgres:postgres_binding kafka mariadb qdrant'.format(
            resource_group, ca_name, image), checks=[
            JMESPathCheck('properties.template.serviceBinds[0].name', "redis"),
            JMESPathCheck('properties.template.serviceBinds[1].name', "postgres_binding"),
            JMESPathCheck('properties.template.serviceBinds[2].name', "kafka"),
            JMESPathCheck('properties.template.serviceBinds[3].name', "mariadb"),
            JMESPathCheck('properties.template.serviceBinds[4].name', "qdrant")
        ])

        self.cmd('containerapp add-on postgres delete -g {} -n {} --yes'.format(
            resource_group, postgres_ca_name, env_name))

        self.cmd('containerapp add-on redis delete -g {} -n {} --yes'.format(
            resource_group, redis_ca_name, env_name))

        self.cmd('containerapp add-on kafka delete -g {} -n {} --yes'.format(
            resource_group, kafka_ca_name, env_name))

        self.cmd('containerapp add-on mariadb delete -g {} -n {} --yes'.format(
            resource_group, mariadb_ca_name, env_name))

        self.cmd('containerapp add-on qdrant delete -g {} -n {} --yes'.format(
            resource_group, qdrant_ca_name, env_name))

        self.cmd(f'containerapp delete -g {resource_group} -n {ca_name} --yes')

        self.cmd('containerapp add-on list -g {} --environment {}'.format(resource_group, env_name), checks=[
            JMESPathCheck('length(@)', 0),
        ])

        self.cmd('containerapp list -g {} --environment {}'.format(resource_group, env_name), checks=[
            JMESPathCheck('length(@)', 0),
        ])

        self.cmd(f'containerapp env delete -g {resource_group} -n {env_name} --yes')

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="eastus2")
    def test_containerapp_addon_binding_e2e(self, resource_group):
        # type "linkers" is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use francecentral as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "francecentral"
        self.cmd('configure --defaults location={}'.format(location))

        ca_name = self.create_random_name(prefix='containerapp', length=24)
        image = "mcr.microsoft.com/azuredocs/containerapps-helloworld:latest"
        redis_ca_name = 'redis'
        postgres_ca_name = 'postgres'
        kafka_ca_name = 'kafka'
        mariadb_ca_name = 'mariadb'
        qdrant_ca_name = "qdrant"
        weaviate_ca_name = "weaviate"
        milvus_ca_name = "milvus"
        ADDON_LIST = ["redis", "postgres", "kafka", "mariadb", "qdrant", "weaviate", "milvus"]

        env_id = prepare_containerapp_env_for_app_e2e_tests(self, location=location)
        env_rg = parse_resource_id(env_id).get('resource_group')
        env_name = parse_resource_id(env_id).get('name')

        self.cmd('containerapp add-on redis create -g {} -n {} --environment {}'.format(
            env_rg, redis_ca_name, env_name))

        self.cmd('containerapp add-on postgres create -g {} -n {} --environment {}'.format(
            env_rg, postgres_ca_name, env_name))

        self.cmd('containerapp add-on kafka create -g {} -n {} --environment {}'.format(
            env_rg, kafka_ca_name, env_name))

        self.cmd('containerapp add-on mariadb create -g {} -n {} --environment {}'.format(
            env_rg, mariadb_ca_name, env_name))

        self.cmd('containerapp add-on qdrant create -g {} -n {} --environment {}'.format(
            env_rg, qdrant_ca_name, env_name))

        self.cmd('containerapp add-on weaviate create -g {} -n {} --environment {}'.format(
            env_rg, weaviate_ca_name, env_name))

        self.cmd('containerapp add-on milvus create -g {} -n {} --environment {}'.format(
            env_rg, milvus_ca_name, env_name))

        for addon in ADDON_LIST:
            self.cmd(f'containerapp show -g {env_rg} -n {addon}', checks=[
                JMESPathCheck("properties.provisioningState", "Succeeded")])

        self.cmd('containerapp create -g {} -n {} --environment {} --image {} --bind postgres:postgres_binding redis'.format(
            env_rg, ca_name, env_name, image), checks=[
            JMESPathCheck('properties.template.serviceBinds[0].name', "postgres_binding"),
            JMESPathCheck('properties.template.serviceBinds[1].name', "redis")
        ])

        self.cmd('containerapp update -g {} -n {} --unbind postgres_binding'.format(
            env_rg, ca_name, image), checks=[
            JMESPathCheck('properties.template.serviceBinds[0].name', "redis"),
        ])

        self.cmd('containerapp update -g {} -n {} --bind postgres:postgres_binding kafka mariadb qdrant weaviate milvus'.format(
            env_rg, ca_name, image), checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck('properties.template.serviceBinds[0].name', "redis"),
            JMESPathCheck('properties.template.serviceBinds[1].name', "postgres_binding"),
            JMESPathCheck('properties.template.serviceBinds[2].name', "kafka"),
            JMESPathCheck('properties.template.serviceBinds[3].name', "mariadb"),
            JMESPathCheck('properties.template.serviceBinds[4].name', "qdrant"),
            JMESPathCheck('properties.template.serviceBinds[5].name', "weaviate"),
            JMESPathCheck('properties.template.serviceBinds[6].name', "milvus")
        ])

        self.cmd('containerapp add-on postgres delete -g {} -n {} --yes'.format(
            env_rg, postgres_ca_name, env_name))

        self.cmd('containerapp add-on redis delete -g {} -n {} --yes'.format(
            env_rg, redis_ca_name, env_name))

        self.cmd('containerapp add-on kafka delete -g {} -n {} --yes'.format(
            env_rg, kafka_ca_name, env_name))

        self.cmd('containerapp add-on mariadb delete -g {} -n {} --yes'.format(
            env_rg, mariadb_ca_name, env_name))

        self.cmd('containerapp add-on qdrant delete -g {} -n {} --yes'.format(
            env_rg, qdrant_ca_name, env_name))

        self.cmd('containerapp add-on weaviate delete -g {} -n {} --yes'.format(
            env_rg, weaviate_ca_name, env_name))

        self.cmd('containerapp add-on milvus delete -g {} -n {} --yes'.format(
            env_rg, milvus_ca_name, env_name))

        self.cmd(f'containerapp delete -g {env_rg} -n {ca_name} --yes')

        self.cmd('containerapp add-on list -g {} --environment {}'.format(env_rg, env_name), checks=[
            JMESPathCheck('length(@)', 0),
        ])

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="eastus2")
    @live_only()
    def test_containerapp_managed_service_binding_e2e(self, resource_group):
        # `mysql flexible-server create`: type 'locations/checkNameAvailability' is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use eastus as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus2"
        self.cmd('configure --defaults location={}'.format(location))

        env_name = self.create_random_name(prefix='containerapp-env', length=24)
        ca_name = self.create_random_name(prefix='containerapp', length=24)
        mysqlserver = "mysqlflexsb"
        postgresqlserver = "postgresqlflexsb"
        postgresqldb = 'flexibleserverdb'
        mysqlflex_dict = {
            "username": "username",
            "password": "password",
            "databaseName": "databaseName"
        }
        postgresqlflex_dict = {
            "username": "username",
            "password": "password"
        }
        # In this case, we need to create mysql and postgres.
        # Their api-version is updated very frequently and we don't want this recording file fail due to the api-version update
        try:
            mysqlflex_json = self.cmd('mysql flexible-server create --resource-group {} --name {} --public-access {} -y'.format(resource_group, mysqlserver, "None"), expect_failure=False).output
            postgresqlflex_json = self.cmd('postgres flexible-server create --resource-group {} --name {} --public-access {} -d {} -y'.format(resource_group, postgresqlserver, "None", postgresqldb), expect_failure=False).output
            mysqlflex_dict = json.loads(mysqlflex_json)
            postgresqlflex_dict = json.loads(postgresqlflex_json)
        except AssertionError as e:
            if str(e).__contains__("Can't overwrite existing cassette"):
                pass
            else:
                raise e

        mysqlusername = mysqlflex_dict['username']
        mysqlpassword = mysqlflex_dict['password']

        mysqldb = mysqlflex_dict['databaseName']
        flex_binding ="mysqlflex_binding"
        postgresqlusername = postgresqlflex_dict['username']
        postgresqlpassword = postgresqlflex_dict['password']
        create_containerapp_env(self, env_name, resource_group, location=location)

        self.cmd('containerapp create -g {} -n {} --environment {} --bind {}:{},database={},username={},password={}'.format(
            resource_group, ca_name, env_name, mysqlserver, flex_binding, mysqldb , mysqlusername, mysqlpassword))
        self.cmd('containerapp show -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('length(properties.template.containers[0].env[?name==`AZURE_MYSQL_HOST`])', 1)
        ])

        self.cmd('containerapp update -g {} -n {} --bind {},database={},username={},password={}'.format(
            resource_group, ca_name, postgresqlserver, postgresqldb , postgresqlusername, postgresqlpassword))
        self.cmd('containerapp show -g {} -n {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('length(properties.template.containers[0].env[?name==`AZURE_MYSQL_HOST`])', 1),
            JMESPathCheck('length(properties.template.containers[0].env[?name==`AZURE_POSTGRESQL_HOST`])', 1)
        ])


class ContainerappEnvStorageTests(ScenarioTest):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, random_config_dir=True, **kwargs)

    @AllowLargeResponse(8192)
    @live_only()  # Passes locally but fails in CI
    @ResourceGroupPreparer(location="eastus")
    def test_containerapp_env_storage(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        env_name = self.create_random_name(prefix='containerapp-env', length=24)
        storage_name = self.create_random_name(prefix='storage', length=24)
        shares_name = self.create_random_name(prefix='share', length=24)

        create_containerapp_env(self, env_name, resource_group)
        storage_account_location = TEST_LOCATION
        if storage_account_location == STAGE_LOCATION:
            storage_account_location = "eastus"
        self.cmd('storage account create -g {} -n {} --kind StorageV2 --sku Standard_LRS --enable-large-file-share --location {}'.format(resource_group, storage_name, storage_account_location))
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


class ContainerappRevisionTests(ScenarioTest):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, random_config_dir=True, **kwargs)

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northeurope")
    def test_containerapp_revision_label_e2e(self, resource_group):
        self.cmd(f"configure --defaults location={TEST_LOCATION}")

        ca_name = self.create_random_name(prefix='containerapp', length=24)

        env = prepare_containerapp_env_for_app_e2e_tests(self)

        self.cmd(f"containerapp create -g {resource_group} -n {ca_name} --environment {env} --image mcr.microsoft.com/k8se/quickstart:latest --ingress external --target-port 80")

        self.cmd(f"containerapp ingress show -g {resource_group} -n {ca_name}", checks=[
            JMESPathCheck('external', True),
            JMESPathCheck('targetPort', 80),
        ])

        self.cmd(f"containerapp create -g {resource_group} -n {ca_name} --environment {env} --ingress external --target-port 80 --image nginx")

        self.cmd(f"containerapp revision set-mode -g {resource_group} -n {ca_name} --mode multiple")

        revision_names = self.cmd(f"containerapp revision list -g {resource_group} -n {ca_name} --all --query '[].name'").get_output_in_json()

        self.assertEqual(len(revision_names), 2)

        labels = []
        for revision in revision_names:
            label = self.create_random_name(prefix='label', length=12)
            labels.append(label)
            self.cmd(f"containerapp revision label add -g {resource_group} -n {ca_name} --revision {revision} --label {label}")

        traffic_weight = self.cmd(f"containerapp ingress traffic show -g {resource_group} -n {ca_name} --query '[].name'").get_output_in_json()

        for traffic in traffic_weight:
            if "label" in traffic:
                self.assertEqual(traffic["label"] in labels, True)

        self.cmd(f"containerapp ingress traffic set -g {resource_group} -n {ca_name} --revision-weight latest=50 --label-weight {labels[0]}=25 {labels[1]}=25")

        traffic_weight = self.cmd(f"containerapp ingress traffic show -g {resource_group} -n {ca_name} --query '[].name'").get_output_in_json()

        for traffic in traffic_weight:
            if "label" in traffic:
                self.assertEqual(traffic["weight"], 25)
            else:
                self.assertEqual(traffic["weight"], 50)

        traffic_weight = self.cmd(f"containerapp revision label swap -g {resource_group} -n {ca_name} --source {labels[0]} --target {labels[1]}").get_output_in_json()

        for revision in revision_names:
            traffic = [w for w in traffic_weight if "revisionName" in w and w["revisionName"] == revision][0]
            self.assertEqual(traffic["label"], labels[(revision_names.index(revision) + 1) % 2])

        self.cmd(f"containerapp revision label remove -g {resource_group} -n {ca_name} --label {labels[0]}", checks=[
            JMESPathCheck('length(@)', 3),
        ])

        self.cmd(f"containerapp revision label remove -g {resource_group} -n {ca_name} --label {labels[1]}", checks=[
            JMESPathCheck('length(@)', 3),
        ])

        traffic_weight = self.cmd(f"containerapp ingress traffic show -g {resource_group} -n {ca_name}").get_output_in_json()

        self.assertEqual(len([w for w in traffic_weight if "label" in w]), 0)

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northeurope")
    @live_only()
    def test_containerapp_revision_labels_mode_e2e(self, resource_group):
        self.cmd(f"configure --defaults location={TEST_LOCATION}")

        ca_name = self.create_random_name(prefix='containerapp', length=24)

        env = prepare_containerapp_env_for_app_e2e_tests(self)

        self.cmd(f"containerapp create -g {resource_group} -n {ca_name} --environment {env} --image mcr.microsoft.com/k8se/quickstart:latest --ingress external --target-port 80")

        self.cmd(f"containerapp ingress show -g {resource_group} -n {ca_name}", checks=[
            JMESPathCheck('external', True),
            JMESPathCheck('targetPort', 80),
        ])

        label0 = 'label0'
        self.cmd(f"containerapp revision set-mode -g {resource_group} -n {ca_name} --mode labels --target-label {label0}")

        label1 = 'label1'
        self.cmd(f"containerapp update -g {resource_group} -n {ca_name} --image mcr.microsoft.com/azuredocs/containerapps-helloworld:latest --target-label {label1}")
        time.sleep(20)
        # --all show revisions include inactive
        revision_names = self.cmd(f"containerapp revision list -g {resource_group} -n {ca_name} --all --query '[].name'").get_output_in_json()
        self.assertEqual(len(revision_names), 3)
        revision_names = self.cmd(
            f"containerapp revision list -g {resource_group} -n {ca_name} --query '[].name'").get_output_in_json()
        self.assertEqual(len(revision_names), 2)
        # Traffic may not be updated immidately
        traffic_weight = self.cmd(f"containerapp ingress traffic show -g {resource_group} -n {ca_name}").get_output_in_json()
        for retry in range(100):
            if len(traffic_weight) >= 2:
                break
            time.sleep(5)
            traffic_weight = self.cmd(f"containerapp ingress traffic show -g {resource_group} -n {ca_name}").get_output_in_json()
        self.assertEqual(len(traffic_weight), 2)
        # self.assertEqual(traffic_weight[0]["label"], label0)
        # self.assertEqual(traffic_weight[0]["revisionName"], revision_names[0])
        # self.assertEqual(traffic_weight[0]["weight"], 100)
        # self.assertEqual(traffic_weight[1]["label"], label1)
        # self.assertEqual(traffic_weight[1]["revisionName"], revision_names[1])
        # self.assertEqual(traffic_weight[1]["weight"], 0)

        self.cmd(f"containerapp ingress traffic set -g {resource_group} -n {ca_name} --label-weight {label0}=75 {label1}=25")

        traffic_weight = self.cmd(f"containerapp ingress traffic show -g {resource_group} -n {ca_name}").get_output_in_json()
        self.assertEqual(traffic_weight[0]["label"], label0)
        self.assertEqual(traffic_weight[0]["revisionName"], revision_names[0])
        self.assertEqual(traffic_weight[0]["weight"], 75)
        self.assertEqual(traffic_weight[1]["label"], label1)
        self.assertEqual(traffic_weight[1]["revisionName"], revision_names[1])
        self.assertEqual(traffic_weight[1]["weight"], 25)
        self.assertEqual(len(traffic_weight), 2)

        traffic_weight = self.cmd(f"containerapp revision label swap -g {resource_group} -n {ca_name} --source {label0} --target {label1}").get_output_in_json()
        self.assertEqual(traffic_weight[0]["label"], label1)
        self.assertEqual(traffic_weight[0]["revisionName"], revision_names[0])
        self.assertEqual(traffic_weight[0]["weight"], 75)
        self.assertEqual(traffic_weight[1]["label"], label0)
        self.assertEqual(traffic_weight[1]["revisionName"], revision_names[1])
        self.assertEqual(traffic_weight[1]["weight"], 25)
        self.assertEqual(len(traffic_weight), 2)

        # make both labels point at the same revision
        self.cmd(f"containerapp revision label add -g {resource_group} -n {ca_name} --label {label0} --revision {revision_names[0]} --yes")

        traffic_weight = self.cmd(f"containerapp ingress traffic show -g {resource_group} -n {ca_name}").get_output_in_json()
        self.assertEqual(traffic_weight[0]["label"], label1)
        self.assertEqual(traffic_weight[0]["revisionName"], revision_names[0])
        self.assertEqual(traffic_weight[0]["weight"], 75)
        self.assertEqual(traffic_weight[1]["label"], label0)
        self.assertEqual(traffic_weight[1]["revisionName"], revision_names[0])
        self.assertEqual(traffic_weight[1]["weight"], 25)
        self.assertEqual(len(traffic_weight), 2)

        # Make them different again. There's a bug in `containerapp ingress traffic set` that can't handle updating weights in multiple sections with the same revision
        traffic_weight = self.cmd(f"containerapp revision label add -g {resource_group} -n {ca_name} --label {label1} --revision {revision_names[1]} --yes").get_output_in_json()
        self.assertEqual(traffic_weight[0]["label"], label1)
        self.assertEqual(traffic_weight[0]["revisionName"], revision_names[1])
        self.assertEqual(traffic_weight[0]["weight"], 75)
        self.assertEqual(traffic_weight[1]["label"], label0)
        self.assertEqual(traffic_weight[1]["revisionName"], revision_names[0])
        self.assertEqual(traffic_weight[1]["weight"], 25)
        self.assertEqual(len(traffic_weight), 2)

        self.cmd(f"containerapp ingress traffic set -g {resource_group} -n {ca_name} --label-weight {label0}=100 {label1}=0")
        traffic_weight = self.cmd(f"containerapp ingress traffic show -g {resource_group} -n {ca_name}").get_output_in_json()
        self.assertEqual(traffic_weight[0]["label"], label1)
        self.assertEqual(traffic_weight[0]["revisionName"], revision_names[1])
        self.assertEqual(traffic_weight[0]["weight"], 0)
        self.assertEqual(traffic_weight[1]["label"], label0)
        self.assertEqual(traffic_weight[1]["revisionName"], revision_names[0])
        self.assertEqual(traffic_weight[1]["weight"], 100)
        self.assertEqual(len(traffic_weight), 2)

        traffic_weight = self.cmd(f"containerapp revision label remove -g {resource_group} -n {ca_name} --label {label1}").get_output_in_json()

        self.assertEqual(traffic_weight[0]["label"], label0)
        self.assertEqual(traffic_weight[0]["revisionName"], revision_names[0])
        self.assertEqual(traffic_weight[0]["weight"], 100)
        self.assertEqual(len(traffic_weight), 1)

class ContainerappAnonymousRegistryTests(ScenarioTest):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, random_config_dir=True, **kwargs)

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northeurope")
    def test_containerapp_anonymous_registry(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        app = self.create_random_name(prefix='aca', length=24)
        image = "mcr.microsoft.com/k8se/quickstart:latest"

        env = prepare_containerapp_env_for_app_e2e_tests(self)

        self.cmd(f'containerapp create -g {resource_group} -n {app} --image {image} --ingress external --target-port 80 --environment {env}')

        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[JMESPathCheck("properties.provisioningState", "Succeeded")])


class ContainerappRegistryIdentityTests(ScenarioTest):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, random_config_dir=True, **kwargs)

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="westeurope")
    def test_containerapp_registry_identity_user(self, resource_group):
        # MSI is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use eastus as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))

        app = self.create_random_name(prefix='aca', length=24)
        identity = self.create_random_name(prefix='id', length=24)
        acr = self.create_random_name(prefix='acr', length=24)
        image_source = "mcr.microsoft.com/k8se/quickstart:latest"
        image_name = f"{acr}.azurecr.io/k8se/quickstart:latest"

        env = prepare_containerapp_env_for_app_e2e_tests(self, location=location)

        identity_rid = self.cmd(f'identity create -g {resource_group} -n {identity}').get_output_in_json()["id"]

        self.cmd(f'acr create --sku basic -n {acr} -g {resource_group} --admin-enabled')
        self.cmd(f'acr import -n {acr} --source {image_source}')
        with mock.patch('azure.cli.command_modules.role.custom._gen_guid', side_effect=self.create_guid):
            self.cmd(f'containerapp create -g {resource_group} -n {app} --registry-identity {identity_rid} --image {image_name} --ingress external --target-port 80 --environment {env} --registry-server {acr}.azurecr.io')

        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("properties.configuration.registries[0].identity", identity_rid),
            JMESPathCheck("properties.configuration.registries[0].server", f'{acr}.azurecr.io'),
            JMESPathCheck("properties.configuration.registries[0].username", ""),
            JMESPathCheck("properties.configuration.registries[0].passwordSecretRef", ""),
            JMESPathCheck("properties.template.containers[0].image", image_name),
        ])

        app2 = self.create_random_name(prefix='aca', length=24)
        with mock.patch('azure.cli.command_modules.role.custom._gen_guid', side_effect=self.create_guid):
            self.cmd(f'containerapp create -g {resource_group} -n {app2} --registry-identity {identity_rid} --image {image_name} --ingress external --target-port 80 --environment {env} --registry-server {acr}.azurecr.io --revision-suffix test1')

        self.cmd(f'containerapp show -g {resource_group} -n {app2}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("properties.template.revisionSuffix", "test1"),
            JMESPathCheck("properties.configuration.registries[0].identity", identity_rid),
            JMESPathCheck("properties.template.containers[0].image", image_name),
        ])

    @live_only()  # Pass lively, But failed in playback mode when execute queue_acr_build
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="westeurope")
    def test_containerapp_create_source_registry_identity_user(self, resource_group):
        # MSI is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use eastus as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))
        source_path = os.path.join(TEST_DIR, os.path.join("data", "source_built_using_dockerfile"))

        app = self.create_random_name(prefix='aca', length=24)
        identity = self.create_random_name(prefix='id', length=24)
        acr = self.create_random_name(prefix='acr', length=24)

        env = prepare_containerapp_env_for_app_e2e_tests(self, location=location)

        identity_rid = self.cmd(f'identity create -g {resource_group} -n {identity}').get_output_in_json()["id"]

        self.cmd(f'acr create --sku basic -n {acr} -g {resource_group} --admin-enabled')
        with mock.patch('azure.cli.command_modules.role.custom._gen_guid', side_effect=self.create_guid):
            self.cmd(
                f'containerapp create -g {resource_group} -n {app} --registry-identity {identity_rid} --source "{source_path}" --ingress external --target-port 80 --environment {env} --registry-server {acr}.azurecr.io')

        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("properties.configuration.registries[0].identity", identity_rid),
            JMESPathCheck("properties.configuration.registries[0].server", f'{acr}.azurecr.io'),
            JMESPathCheck("properties.configuration.registries[0].username", ""),
            JMESPathCheck("properties.configuration.registries[0].passwordSecretRef", ""),
        ])

        app2 = self.create_random_name(prefix='aca', length=24)
        with mock.patch('azure.cli.command_modules.role.custom._gen_guid', side_effect=self.create_guid):
            self.cmd(
                f'containerapp create -g {resource_group} -n {app2} --registry-identity {identity_rid} --source "{source_path}" --ingress external --target-port 80 --environment {env} --registry-server {acr}.azurecr.io --revision-suffix test1')

        app_json = self.cmd(f'containerapp show -g {resource_group} -n {app2}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("properties.template.revisionSuffix", "test1"),
            JMESPathCheck("properties.configuration.registries[0].identity", identity_rid),
            JMESPathCheck("properties.configuration.registries[0].server", f'{acr}.azurecr.io'),
            JMESPathCheck("properties.configuration.registries[0].username", ""),
            JMESPathCheck("properties.configuration.registries[0].passwordSecretRef", ""),
        ]).get_output_in_json()
        image_name1 = app_json["properties"]["template"]["containers"][0]["image"]
        self.assertTrue(image_name1.startswith(f'{acr}.azurecr.io'))

        with mock.patch('azure.cli.command_modules.role.custom._gen_guid', side_effect=self.create_guid):
            self.cmd(
                f'containerapp update -g {resource_group} -n {app2} --source "{source_path}"')

        app_json = self.cmd(f'containerapp show -g {resource_group} -n {app2}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("properties.configuration.registries[0].identity", identity_rid),
            JMESPathCheck("properties.configuration.registries[0].server", f'{acr}.azurecr.io'),
            JMESPathCheck("properties.configuration.registries[0].username", ""),
            JMESPathCheck("properties.configuration.registries[0].passwordSecretRef", ""),
        ]).get_output_in_json()
        image_name2 = app_json["properties"]["template"]["containers"][0]["image"]
        self.assertTrue(image_name2.startswith(f'{acr}.azurecr.io'))
        self.assertNotEqual(image_name1, image_name2)

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="westeurope")
    def test_containerapp_registry_identity_system(self, resource_group):
        # MSI is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use eastus as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))

        app = self.create_random_name(prefix='aca', length=24)
        acr = self.create_random_name(prefix='acr', length=24)
        image_source = "mcr.microsoft.com/k8se/quickstart:latest"
        image_name = f"{acr}.azurecr.io/k8se/quickstart:latest"

        env = prepare_containerapp_env_for_app_e2e_tests(self, location=location)

        self.cmd(f'acr create --sku basic -n {acr} -g {resource_group} --admin-enabled')
        self.cmd(f'acr import -n {acr} --source {image_source}')
        with mock.patch('azure.cli.command_modules.role.custom._gen_guid', side_effect=self.create_guid):
            self.cmd(f'containerapp create -g {resource_group} -n {app} --registry-identity "system" --image {image_name} --ingress external --target-port 80 --environment {env} --registry-server {acr}.azurecr.io')

        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("properties.template.containers[0].image", image_name),
            JMESPathCheck("properties.configuration.registries[0].identity", 'system'),
            JMESPathCheck("properties.configuration.registries[0].server", f'{acr}.azurecr.io'),
            JMESPathCheck("properties.configuration.registries[0].username", ""),
            JMESPathCheck("properties.configuration.registries[0].passwordSecretRef", ""),
        ])
        # Default use system-assign registry identity
        app2 = self.create_random_name(prefix='aca', length=24)
        with mock.patch('azure.cli.command_modules.role.custom._gen_guid', side_effect=self.create_guid):
            self.cmd(f'containerapp create -g {resource_group} -n {app2} --image {image_name} --ingress external --target-port 80 --environment {env} --registry-server {acr}.azurecr.io --revision-suffix test1 --no-wait')

        self.cmd(f'containerapp show -g {resource_group} -n {app2}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("properties.template.revisionSuffix", "test1"),
            JMESPathCheck("properties.template.containers[0].image", image_name),
            JMESPathCheck("properties.configuration.registries[0].identity", 'system'),
            JMESPathCheck("properties.configuration.registries[0].server", f'{acr}.azurecr.io'),
            JMESPathCheck("properties.configuration.registries[0].username", ""),
            JMESPathCheck("properties.configuration.registries[0].passwordSecretRef", ""),
        ])

    @live_only()  # Pass lively, But failed in playback mode when execute queue_acr_build
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="westeurope")
    def test_containerapp_create_source_registry_identity_system(self, resource_group):
        # MSI is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use eastus as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))
        source_path = os.path.join(TEST_DIR, os.path.join("data", "source_built_using_dockerfile"))

        app = self.create_random_name(prefix='aca', length=24)
        acr = self.create_random_name(prefix='acr', length=24)

        env = prepare_containerapp_env_for_app_e2e_tests(self, location=location)

        self.cmd(f'acr create --sku basic -n {acr} -g {resource_group} --admin-enabled')
        with mock.patch('azure.cli.command_modules.role.custom._gen_guid', side_effect=self.create_guid):
            self.cmd(f'containerapp create -g {resource_group} -n {app} --registry-identity "system" --source "{source_path}" --ingress external --target-port 80 --environment {env} --registry-server {acr}.azurecr.io')

        app_json = self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("properties.configuration.registries[0].identity", 'system'),
            JMESPathCheck("properties.configuration.registries[0].server", f'{acr}.azurecr.io'),
            JMESPathCheck("properties.configuration.registries[0].username", ""),
            JMESPathCheck("properties.configuration.registries[0].passwordSecretRef", ""),
        ]).get_output_in_json()
        image_name1 = app_json["properties"]["template"]["containers"][0]["image"]
        self.assertTrue(image_name1.startswith(f'{acr}.azurecr.io'))

        # Default use system-assign registry identity
        app2 = self.create_random_name(prefix='aca', length=24)
        with mock.patch('azure.cli.command_modules.role.custom._gen_guid', side_effect=self.create_guid):
            self.cmd(f'containerapp create -g {resource_group} -n {app2} --source "{source_path}" --ingress external --target-port 80 --environment {env} --registry-server {acr}.azurecr.io --revision-suffix test1 --no-wait')

        app_json = self.cmd(f'containerapp show -g {resource_group} -n {app2}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("properties.template.revisionSuffix", "test1"),
            JMESPathCheck("properties.configuration.registries[0].identity", 'system'),
            JMESPathCheck("properties.configuration.registries[0].server", f'{acr}.azurecr.io'),
            JMESPathCheck("properties.configuration.registries[0].username", ""),
            JMESPathCheck("properties.configuration.registries[0].passwordSecretRef", ""),
        ]).get_output_in_json()
        image_name2 = app_json["properties"]["template"]["containers"][0]["image"]
        self.assertTrue(image_name2.startswith(f'{acr}.azurecr.io'))
        self.assertNotEqual(image_name1, image_name2)

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="westeurope")
    def test_containerapp_private_registry_port(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))
        app = self.create_random_name(prefix='aca', length=24)
        acr = self.create_random_name(prefix='acr', length=24)
        image_source = "mcr.microsoft.com/k8se/quickstart:latest"
        image_name = f"{acr}.azurecr.io:443/k8se/quickstart:latest"

        env = prepare_containerapp_env_for_app_e2e_tests(self)
        acr_location = TEST_LOCATION
        if format_location(acr_location) == format_location(STAGE_LOCATION):
            acr_location = "eastus"
        self.cmd(f'acr create --sku basic -n {acr} -g {resource_group} --admin-enabled -l {acr_location}')
        self.cmd(f'acr import -n {acr} --source {image_source}')
        password = self.cmd(f'acr credential show -n {acr} --query passwords[0].value').get_output_in_json()

        self.cmd(f'containerapp create -g {resource_group} -n {app}  --image {image_name} --ingress external --target-port 80 --environment {env} --registry-server {acr}.azurecr.io:443 --registry-username {acr} --registry-password {password}')

        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("properties.configuration.registries[0].server", f"{acr}.azurecr.io:443"),
            JMESPathCheck("properties.template.containers[0].image", image_name),
            JMESPathCheck("properties.configuration.secrets[0].name", f"{acr}azurecrio-443-{acr}")
        ])

        app2 = self.create_random_name(prefix='aca', length=24)
        image_name = f"{acr}.azurecr.io/k8se/quickstart:latest"
        self.cmd(
            f'containerapp create -g {resource_group} -n {app2}  --image {image_name} --ingress external --target-port 80 --environment {env} --registry-server {acr}.azurecr.io --registry-username {acr} --registry-password {password}')

        self.cmd(f'containerapp show -g {resource_group} -n {app2}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("properties.configuration.registries[0].server", f"{acr}.azurecr.io"),
            JMESPathCheck("properties.template.containers[0].image", image_name),
            JMESPathCheck("properties.configuration.secrets[0].name", f"{acr}azurecrio-{acr}")
        ])

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="westeurope")
    def test_containerapp_registry_acr_look_up_credentical(self, resource_group):
        # MSI is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use eastus as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))
        app = self.create_random_name(prefix='aca', length=24)
        acr = self.create_random_name(prefix='acr', length=24)
        image_source = "mcr.microsoft.com/k8se/quickstart:latest"
        image_name = f"{acr}.azurecr.io/k8se/quickstart:latest"

        env = prepare_containerapp_env_for_app_e2e_tests(self, location=location)

        acr_location = TEST_LOCATION
        if format_location(acr_location) == format_location(STAGE_LOCATION):
            acr_location = "eastus"
        self.cmd(f'acr create --sku basic -n {acr} -g {resource_group} --admin-enabled --location {acr_location}')
        self.cmd(f'acr import -n {acr} --source {image_source}')

        # `az containberapp create` only with `--registry-server {acr}.azurecr.io`, use SystemAssigned as default for image pull
        with mock.patch('azure.cli.command_modules.role.custom._gen_guid', side_effect=self.create_guid):
            self.cmd(f'containerapp create -g {resource_group} -n {app}  --image {image_name} --ingress external --target-port 80 --environment {env} --registry-server {acr}.azurecr.io', checks=[
                JMESPathCheck("identity.type", "SystemAssigned"),
                JMESPathCheck("properties.configuration.secrets", None),
                JMESPathCheck("length(properties.configuration.registries)", 1),
                JMESPathCheck("properties.configuration.registries[0].identity", 'system'),
                JMESPathCheck("properties.configuration.registries[0].server", f'{acr}.azurecr.io'),
                JMESPathCheck("properties.configuration.registries[0].username", ""),
                JMESPathCheck("properties.configuration.registries[0].passwordSecretRef", ""),
            ])

        # --registry-server {acr}.azurecr.io --registry-username, auto lookup credentical
        self.cmd(f'containerapp create -g {resource_group} -n {app}  --image {image_name} --ingress external --target-port 80 --environment {env} --registry-server {acr}.azurecr.io --registry-username a')

        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "None"),
            JMESPathCheck("properties.configuration.registries[0].server", f"{acr}.azurecr.io"),
            JMESPathCheck("properties.template.containers[0].image", image_name),
            JMESPathCheck("properties.configuration.secrets[0].name", f"{acr}azurecrio-{acr}")
        ])

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="westeurope")
    def test_containerapp_identity_registry(self, resource_group):
        # MSI is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use eastus as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))

        env_name = self.create_random_name(prefix='containerapp-e2e-env', length=24)
        ca_name = self.create_random_name(prefix='containerapp', length=24)
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
        self.cmd(f'containerapp create -g {resource_group} -n {ca_name}  --image {image_name} --ingress external --target-port 80 --environment {env} --registry-server {acr}.azurecr.io --registry-identity system-environment')
        self.cmd(f'containerapp show -g {resource_group} -n {ca_name}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "None"),
            JMESPathCheck("properties.configuration.registries[0].server", f"{acr}.azurecr.io"),
            JMESPathCheck("properties.configuration.registries[0].identity", "system-environment", case_sensitive=False),
            JMESPathCheck("properties.template.containers[0].image", image_name),
        ])

        # update use env user assigned identity
        self.cmd(f'containerapp registry set -g {resource_group} -n {ca_name} --server {acr}.azurecr.io --identity {user_identity_id}')
        self.cmd(f'containerapp show -g {resource_group} -n {ca_name}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "None"),
            JMESPathCheck("properties.configuration.registries[0].server", f"{acr}.azurecr.io"),
            JMESPathCheck("properties.configuration.registries[0].identity", user_identity_id, case_sensitive=False),
            JMESPathCheck("properties.template.containers[0].image", image_name),
        ])

        # update containerapp to create new revision
        self.cmd(f'containerapp update -g {resource_group} -n {ca_name}  --revision-suffix v2')
        self.cmd(f'containerapp show -g {resource_group} -n {ca_name}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "None"),
            JMESPathCheck("properties.configuration.registries[0].server", f"{acr}.azurecr.io"),
            JMESPathCheck("properties.configuration.registries[0].identity", user_identity_id, case_sensitive=False),
            JMESPathCheck("properties.template.containers[0].image", image_name),
            JMESPathCheck("properties.template.revisionSuffix", "v2")
        ])

        # update use env system managed identity
        self.cmd(f'containerapp registry set -g {resource_group} -n {ca_name} --server {acr}.azurecr.io --identity system-environment')
        self.cmd(f'containerapp show -g {resource_group} -n {ca_name}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "None"),
            JMESPathCheck("properties.configuration.registries[0].server", f"{acr}.azurecr.io"),
            JMESPathCheck("properties.configuration.registries[0].identity", "system-environment"),
            JMESPathCheck("properties.template.containers[0].image", image_name),
        ])

        # update containerapp to create new revision
        self.cmd(f'containerapp update -g {resource_group} -n {ca_name}  --revision-suffix v3')
        self.cmd(f'containerapp show -g {resource_group} -n {ca_name}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "None"),
            JMESPathCheck("properties.configuration.registries[0].server", f"{acr}.azurecr.io"),
            JMESPathCheck("properties.configuration.registries[0].identity", "system-environment"),
            JMESPathCheck("properties.template.containers[0].image", image_name),
            JMESPathCheck("properties.template.revisionSuffix", "v3")
        ])


class ContainerappUpRegistryIdentityTests(ScenarioTest):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, random_config_dir=True, **kwargs)

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="westeurope")
    def test_containerapp_up_registry_identity_user(self, resource_group):
        # MSI is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use eastus as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))

        app = self.create_random_name(prefix='aca', length=24)
        identity1 = self.create_random_name(prefix='id1', length=24)
        identity2 = self.create_random_name(prefix='id2', length=24)
        acr = self.create_random_name(prefix='acr', length=24)
        image_source = "mcr.microsoft.com/k8se/quickstart:latest"
        image_name = f"{acr}.azurecr.io/k8se/quickstart:latest"

        env = prepare_containerapp_env_for_app_e2e_tests(self, location=location)

        identity_rid_1 = self.cmd(f'identity create -g {resource_group} -n {identity1}').get_output_in_json()["id"]
        identity_rid_2 = self.cmd(f'identity create -g {resource_group} -n {identity2}').get_output_in_json()["id"]

        # create an ACR without --admin-enabled
        self.cmd(f'acr create --sku basic -n {acr} -g {resource_group}', checks=[
            JMESPathCheck("adminUserEnabled", False),
            JMESPathCheck("anonymousPullEnabled", False),
        ])
        self.cmd(f'acr import -n {acr} --source {image_source}')
        # create a new containerapp with `az containerapp up` only with `--registry-server {acr}.azurecr.io`
        # Use SystemAssigned as default for image pull
        with mock.patch('azure.cli.command_modules.role.custom._gen_guid', side_effect=self.create_guid):
            self.cmd(
                f'containerapp up -g {resource_group} -n {app} --image {image_name} --ingress external --target-port 80 --environment {env} --registry-server {acr}.azurecr.io')

        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "SystemAssigned"),
            JMESPathCheck("properties.configuration.secrets", None),
            JMESPathCheck("length(properties.configuration.registries)", 1),
            JMESPathCheck("properties.configuration.registries[0].identity", 'system'),
            JMESPathCheck("properties.configuration.registries[0].server", f'{acr}.azurecr.io'),
            JMESPathCheck("properties.configuration.registries[0].username", ""),
            JMESPathCheck("properties.configuration.registries[0].passwordSecretRef", ""),
        ])
        # update the registry to a user-identity
        with mock.patch('azure.cli.command_modules.role.custom._gen_guid', side_effect=self.create_guid):
            self.cmd(
                f'containerapp up -g {resource_group} -n {app} --registry-identity {identity_rid_1} --image {image_name} --ingress external --target-port 80 --environment {env} --registry-server {acr}.azurecr.io')

        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "SystemAssigned, UserAssigned"),
            JMESPathCheckExists(f'identity.userAssignedIdentities."{identity_rid_1}"'),
            JMESPathCheck("length(properties.configuration.registries)", 1),
            JMESPathCheck("properties.configuration.registries[0].identity", identity_rid_1),
            JMESPathCheck("properties.configuration.registries[0].server", f'{acr}.azurecr.io'),
            JMESPathCheck("properties.configuration.registries[0].username", ""),
            JMESPathCheck("properties.configuration.registries[0].passwordSecretRef", ""),
        ])

        # update the containerapp with --system-assigned
        self.cmd(
            f'containerapp up -g {resource_group} -n {app} --registry-identity {identity_rid_1} --image {image_name} --ingress external --target-port 80 --environment {env} --registry-server {acr}.azurecr.io --system-assigned')

        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "SystemAssigned, UserAssigned"),
            JMESPathCheckExists(f'identity.userAssignedIdentities."{identity_rid_1}"'),
            JMESPathCheck("length(properties.configuration.registries)", 1),
            JMESPathCheck("properties.configuration.registries[0].identity", identity_rid_1),
            JMESPathCheck("properties.configuration.registries[0].server", f'{acr}.azurecr.io'),
            JMESPathCheck("properties.configuration.registries[0].username", ""),
            JMESPathCheck("properties.configuration.registries[0].passwordSecretRef", ""),
        ])

        # update the containerapp with --system-assigned --user-assigned
        self.cmd(
            f'containerapp up -g {resource_group} -n {app} --user-assigned {identity_rid_1} --system-assigned --image {image_name} --ingress external --target-port 80 --environment {env} --registry-server {acr}.azurecr.io')

        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "SystemAssigned, UserAssigned"),
            JMESPathCheckExists(f'identity.userAssignedIdentities."{identity_rid_1}"'),
            JMESPathCheck("length(properties.configuration.registries)", 1),
            JMESPathCheck("properties.configuration.registries[0].identity", identity_rid_1),
            JMESPathCheck("properties.configuration.registries[0].server", f'{acr}.azurecr.io'),
            JMESPathCheck("properties.configuration.registries[0].username", ""),
            JMESPathCheck("properties.configuration.registries[0].passwordSecretRef", ""),
        ])

        self.cmd(f'containerapp identity remove --system-assigned -g {resource_group} -n {app}', checks=[
            JMESPathCheck("type", "UserAssigned"),
        ])

        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "UserAssigned"),
            JMESPathCheckExists(f'identity.userAssignedIdentities."{identity_rid_1}"'),
            JMESPathCheck("length(properties.configuration.registries)", 1),
            JMESPathCheck("properties.configuration.registries[0].identity", identity_rid_1),
            JMESPathCheck("properties.configuration.registries[0].server", f'{acr}.azurecr.io'),
            JMESPathCheck("properties.configuration.registries[0].username", ""),
            JMESPathCheck("properties.configuration.registries[0].passwordSecretRef", ""),
        ])

        # update the containerapp with --system-assigned --user-assigned
        self.cmd(
            f'containerapp up -g {resource_group} -n {app} --user-assigned {identity_rid_1} {identity_rid_2} --system-assigned --image {image_name} --ingress external --target-port 80 --environment {env} --registry-server {acr}.azurecr.io')

        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "SystemAssigned, UserAssigned"),
            JMESPathCheckExists(f'identity.userAssignedIdentities."{identity_rid_1}"'),
            JMESPathCheckExists(f'identity.userAssignedIdentities."{identity_rid_2}"'),
            JMESPathCheck("length(properties.configuration.registries)", 1),
            JMESPathCheck("properties.configuration.registries[0].identity", identity_rid_1),
            JMESPathCheck("properties.configuration.registries[0].server", f'{acr}.azurecr.io'),
            JMESPathCheck("properties.configuration.registries[0].username", ""),
            JMESPathCheck("properties.configuration.registries[0].passwordSecretRef", ""),
        ])

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="westeurope")
    def test_containerapp_up_registry_identity_system(self, resource_group):
        # MSI is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use eastus as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))

        app = self.create_random_name(prefix='aca', length=24)
        acr = self.create_random_name(prefix='acr', length=24)
        image_source = "mcr.microsoft.com/k8se/quickstart:latest"
        image_name = f"{acr}.azurecr.io/k8se/quickstart:latest"

        env = prepare_containerapp_env_for_app_e2e_tests(self, location=location)

        self.cmd(f'acr create --sku basic -n {acr} -g {resource_group} --admin-enabled')
        self.cmd(f'acr import -n {acr} --source {image_source}')
        with mock.patch('azure.cli.command_modules.role.custom._gen_guid', side_effect=self.create_guid):
            self.cmd(f'containerapp up -g {resource_group} -n {app} --registry-identity "system" --image {image_name} --ingress external --target-port 80 --environment {env} --registry-server {acr}.azurecr.io')

        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "SystemAssigned"),
            JMESPathCheck("properties.configuration.secrets", None),
            JMESPathCheck("length(properties.configuration.registries)", 1),
            JMESPathCheck("properties.configuration.registries[0].identity", 'system'),
            JMESPathCheck("properties.configuration.registries[0].server", f'{acr}.azurecr.io'),
            JMESPathCheck("properties.configuration.registries[0].username", ""),
            JMESPathCheck("properties.configuration.registries[0].passwordSecretRef", "")
        ])

        with mock.patch('azure.cli.command_modules.role.custom._gen_guid', side_effect=self.create_guid):
            self.cmd(
                f'containerapp up -g {resource_group} -n {app} --registry-identity "system" --image {image_name} --ingress internal --target-port 80 --environment {env} --registry-server {acr}.azurecr.io')

        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "SystemAssigned"),
            JMESPathCheck("properties.configuration.secrets", None),
            JMESPathCheck("length(properties.configuration.registries)", 1),
            JMESPathCheck("properties.configuration.registries[0].identity", 'system'),
            JMESPathCheck("properties.configuration.registries[0].server", f'{acr}.azurecr.io'),
            JMESPathCheck("properties.configuration.registries[0].username", ""),
            JMESPathCheck("properties.configuration.registries[0].passwordSecretRef", "")
        ])

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="westeurope")
    def test_containerapp_up_private_registry_port(self, resource_group):
        # MSI is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use eastus as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))

        app = self.create_random_name(prefix='aca', length=24)
        acr = self.create_random_name(prefix='acr', length=24)
        image_source = "mcr.microsoft.com/k8se/quickstart:latest"
        image_name = f"{acr}.azurecr.io:443/k8se/quickstart:latest"

        env = prepare_containerapp_env_for_app_e2e_tests(self, location=location)
        acr_location = TEST_LOCATION
        if format_location(acr_location) == format_location(STAGE_LOCATION):
            acr_location = "eastus"
        self.cmd(f'acr create --sku basic -n {acr} -g {resource_group} --admin-enabled -l {acr_location}')
        self.cmd(f'acr import -n {acr} --source {image_source}')
        password = self.cmd(f'acr credential show -n {acr} --query passwords[0].value').get_output_in_json()

        self.cmd(
            f'containerapp up -g {resource_group} -n {app}  --image {image_name} --ingress external --target-port 80 --environment {env} --registry-server {acr}.azurecr.io:443 --registry-username {acr} --registry-password {password}')

        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("properties.configuration.registries[0].server", f"{acr}.azurecr.io:443"),
            JMESPathCheck("properties.configuration.registries[0].identity", ""),
            JMESPathCheck("properties.configuration.registries[0].username", acr),
            JMESPathCheck("properties.configuration.registries[0].passwordSecretRef", f"{acr}azurecrio-443-{acr}"),
            JMESPathCheck("properties.template.containers[0].image", image_name),
            JMESPathCheck("properties.configuration.secrets[0].name", f"{acr}azurecrio-443-{acr}"),
        ])

        app2 = self.create_random_name(prefix='aca', length=24)
        image_name = f"{acr}.azurecr.io/k8se/quickstart:latest"
        self.cmd(
            f'containerapp up -g {resource_group} -n {app2}  --image {image_name} --ingress external --target-port 80 --environment {env} --registry-server {acr}.azurecr.io --registry-username {acr} --registry-password {password}')

        self.cmd(f'containerapp show -g {resource_group} -n {app2}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "None"),
            JMESPathCheck("properties.configuration.registries[0].server", f"{acr}.azurecr.io"),
            JMESPathCheck("properties.configuration.registries[0].identity", ""),
            JMESPathCheck("properties.configuration.registries[0].username", acr),
            JMESPathCheck("properties.template.containers[0].image", image_name),
            JMESPathCheck("properties.configuration.secrets[0].name", f"{acr}azurecrio-{acr}")
        ])

        # update from username/password to system
        with mock.patch('azure.cli.command_modules.role.custom._gen_guid', side_effect=self.create_guid):
            self.cmd(
                f'containerapp up -g {resource_group} -n {app2}  --image {image_name} --ingress external --target-port 80 --environment {env} --registry-server {acr}.azurecr.io --registry-identity system',
                expect_failure=False)

        self.cmd(f'containerapp show -g {resource_group} -n {app2}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "SystemAssigned"),
            JMESPathCheck("properties.configuration.secrets", None),
            JMESPathCheck("length(properties.configuration.registries)", 1),
            JMESPathCheck("properties.configuration.registries[0].identity", 'system'),
            JMESPathCheck("properties.configuration.registries[0].server", f"{acr}.azurecr.io"),
            JMESPathCheck("properties.configuration.registries[0].username", ""),
            JMESPathCheck("properties.configuration.registries[0].passwordSecretRef", ""),
            JMESPathCheck("properties.template.containers[0].image", image_name),
        ])

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="westeurope")
    def test_containerapp_up_registry_acr_look_up_credentical(self, resource_group):
        # MSI is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use eastus as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))
        app = self.create_random_name(prefix='aca', length=24)
        acr = self.create_random_name(prefix='acr', length=24)
        image_source = "mcr.microsoft.com/k8se/quickstart:latest"
        image_name = f"{acr}.azurecr.io/k8se/quickstart:latest"

        env = prepare_containerapp_env_for_app_e2e_tests(self, location=location)

        acr_location = TEST_LOCATION
        if format_location(acr_location) == format_location(STAGE_LOCATION):
            acr_location = "eastus"
        self.cmd(f'acr create --sku basic -n {acr} -g {resource_group} --admin-enabled --location {acr_location}')
        self.cmd(f'acr import -n {acr} --source {image_source}')

        # `az containberapp create` only with `--registry-server {acr}.azurecr.io`, use SystemAssigned as default for image pull
        with mock.patch('azure.cli.command_modules.role.custom._gen_guid', side_effect=self.create_guid):
            self.cmd(f'containerapp up -g {resource_group} -n {app}  --image {image_name} --ingress external --target-port 80 --environment {env} --registry-server {acr}.azurecr.io', expect_failure=False)

        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
                JMESPathCheck("properties.provisioningState", "Succeeded"),
                JMESPathCheck("identity.type", "SystemAssigned"),
                JMESPathCheck("properties.configuration.secrets", None),
                JMESPathCheck("length(properties.configuration.registries)", 1),
                JMESPathCheck("properties.configuration.registries[0].identity", 'system'),
                JMESPathCheck("properties.configuration.registries[0].server", f'{acr}.azurecr.io'),
                JMESPathCheck("properties.configuration.registries[0].username", ""),
                JMESPathCheck("properties.configuration.registries[0].passwordSecretRef", ""),
        ])

        # --registry-server {acr}.azurecr.io --registry-username, auto lookup credentical
        self.cmd(
            f'containerapp up -g {resource_group} -n {app}  --image {image_name} --ingress external --target-port 80 --environment {env} --registry-server {acr}.azurecr.io --registry-username a', expect_failure=False)

        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "SystemAssigned"),
            JMESPathCheck("properties.template.containers[0].image", image_name),
            JMESPathCheck("properties.configuration.secrets[0].name", f"{acr}azurecrio-{acr}"),
            JMESPathCheck("properties.configuration.registries[0].server", f"{acr}.azurecr.io"),
            JMESPathCheck("properties.configuration.registries[0].identity", ""),
            JMESPathCheck("properties.configuration.registries[0].username", acr),
        ])
        # update existing app, the registry keep consistent
        with mock.patch('azure.cli.command_modules.role.custom._gen_guid', side_effect=self.create_guid):
            self.cmd(f'containerapp up -g {resource_group} -n {app}  --image {image_name} --environment {env} --registry-server {acr}.azurecr.io', expect_failure=False)
        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "SystemAssigned"),
            JMESPathCheck("properties.template.containers[0].image", image_name),
            JMESPathCheck("properties.configuration.secrets[0].name", f"{acr}azurecrio-{acr}"),
            JMESPathCheck("properties.configuration.registries[0].server", f"{acr}.azurecr.io"),
            JMESPathCheck("properties.configuration.registries[0].identity", ""),
            JMESPathCheck("properties.configuration.registries[0].username", acr)
        ])
        # update containerapp registry from username/password to identity
        with mock.patch('azure.cli.command_modules.role.custom._gen_guid', side_effect=self.create_guid):
            self.cmd(f'containerapp up -g {resource_group} -n {app}  --image {image_name} --ingress external --target-port 80 --environment {env} --registry-server {acr}.azurecr.io --registry-identity system', expect_failure=False)

        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "SystemAssigned"),
            JMESPathCheck("properties.configuration.secrets", None),
            JMESPathCheck("length(properties.configuration.registries)", 1),
            JMESPathCheck("properties.configuration.registries[0].identity", 'system'),
            JMESPathCheck("properties.configuration.registries[0].server", f'{acr}.azurecr.io'),
            JMESPathCheck("properties.configuration.registries[0].username", ""),
            JMESPathCheck("properties.configuration.registries[0].passwordSecretRef", ""),
        ])

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="westeurope")
    @SubnetPreparer(location="eastus", delegations='Microsoft.App/environments', service_endpoints="Microsoft.Storage.Global")
    def test_containerapp_up_identity_registry(self, resource_group, subnet_id, vnet_name, subnet_name):
        # MSI is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use eastus as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))

        env_name = self.create_random_name(prefix='containerapp-e2e-env', length=24)
        ca_name = self.create_random_name(prefix='containerapp', length=24)
        user_identity_name = self.create_random_name(prefix='containerapp', length=24)
        acr = self.create_random_name(prefix='acr', length=24)
        image_source = "mcr.microsoft.com/k8se/quickstart:latest"
        image_name = f"{acr}.azurecr.io/k8se/quickstart:latest"

        # prepare env
        user_identity_name = self.create_random_name(prefix='env-msi', length=24)
        identity_json = self.cmd(
            'identity create -g {} -n {}'.format(resource_group, user_identity_name)).get_output_in_json()
        user_identity_id = identity_json["id"]

        self.cmd(
            'containerapp env create -g {} -n {} --mi-system-assigned --mi-user-assigned {} --logs-destination none -s {}'.format(
                resource_group, env_name, user_identity_id, subnet_id))
        containerapp_env = self.cmd(
            'containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()
        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd(
                'containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()
        env = containerapp_env["id"]

        # prepare acr
        acr_id = \
        self.cmd(f'acr create --sku basic -n {acr} -g {resource_group} --location {location}').get_output_in_json()[
            "id"]
        # role assign
        roleAssignmentName1 = self.create_guid()
        roleAssignmentName2 = self.create_guid()
        self.cmd(
            f'role assignment create --role acrpull --assignee {containerapp_env["identity"]["principalId"]} --scope {acr_id} --name {roleAssignmentName1}')
        self.cmd(
            f'role assignment create --role acrpull --assignee {identity_json["principalId"]} --scope {acr_id} --name {roleAssignmentName2}')
        # upload image
        self.cmd(f'acr import -n {acr} --source {image_source}')

        # wait for role assignment take effect
        time.sleep(30)

        # use env system msi to pull image
        self.cmd(
            f'containerapp up -g {resource_group} -n {ca_name}  --image {image_name} --ingress external --target-port 80 --environment {env} --registry-server {acr}.azurecr.io --registry-identity system-environment')
        self.cmd(f'containerapp show -g {resource_group} -n {ca_name}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "None"),
            JMESPathCheck("properties.configuration.registries[0].server", f"{acr}.azurecr.io"),
            JMESPathCheck("properties.configuration.registries[0].identity", "system-environment",
                          case_sensitive=False),
            JMESPathCheck("properties.template.containers[0].image", image_name),
        ])

        # update use env user assigned identity
        self.cmd(
            f'containerapp registry set -g {resource_group} -n {ca_name} --server {acr}.azurecr.io --identity {user_identity_id}')
        self.cmd(f'containerapp show -g {resource_group} -n {ca_name}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "None"),
            JMESPathCheck("properties.configuration.registries[0].server", f"{acr}.azurecr.io"),
            JMESPathCheck("properties.configuration.registries[0].identity", user_identity_id, case_sensitive=False),
            JMESPathCheck("properties.template.containers[0].image", image_name),
        ])

        # update containerapp to create new revision
        self.cmd(f'containerapp update -g {resource_group} -n {ca_name}  --revision-suffix v2')
        self.cmd(f'containerapp show -g {resource_group} -n {ca_name}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "None"),
            JMESPathCheck("properties.configuration.registries[0].server", f"{acr}.azurecr.io"),
            JMESPathCheck("properties.configuration.registries[0].identity", user_identity_id, case_sensitive=False),
            JMESPathCheck("properties.template.containers[0].image", image_name),
            JMESPathCheck("properties.template.revisionSuffix", "v2")
        ])

        # update use env system managed identity
        self.cmd(
            f'containerapp registry set -g {resource_group} -n {ca_name} --server {acr}.azurecr.io --identity system-environment')
        self.cmd(f'containerapp show -g {resource_group} -n {ca_name}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "None"),
            JMESPathCheck("properties.configuration.registries[0].server", f"{acr}.azurecr.io"),
            JMESPathCheck("properties.configuration.registries[0].identity", "system-environment"),
            JMESPathCheck("properties.template.containers[0].image", image_name),
        ])

        # update containerapp to create new revision
        self.cmd(f'containerapp update -g {resource_group} -n {ca_name}  --revision-suffix v3')
        self.cmd(f'containerapp show -g {resource_group} -n {ca_name}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("identity.type", "None"),
            JMESPathCheck("properties.configuration.registries[0].server", f"{acr}.azurecr.io"),
            JMESPathCheck("properties.configuration.registries[0].identity", "system-environment"),
            JMESPathCheck("properties.template.containers[0].image", image_name),
            JMESPathCheck("properties.template.revisionSuffix", "v3")
        ])


class ContainerappScaleTests(ScenarioTest):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, random_config_dir=True, **kwargs)

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="westeurope")
    def test_containerapp_scale_create(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        app = self.create_random_name(prefix='aca', length=24)

        env = prepare_containerapp_env_for_app_e2e_tests(self)

        self.cmd(f'containerapp create -g {resource_group} -n {app} --image nginx --ingress external --target-port 80 --environment {env} --scale-rule-name http-scale-rule --scale-rule-http-concurrency 50 --scale-rule-auth trigger=secretref --scale-rule-metadata key=value', checks=[JMESPathCheck("properties.template.scale.rules[0].http.metadata.key", "")])

        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.template.scale.rules[0].name", "http-scale-rule"),
            JMESPathCheck("properties.template.scale.rules[0].http.metadata.concurrentRequests", "50"),
            JMESPathCheck("properties.template.scale.rules[0].http.metadata.key", "value"),
            JMESPathCheck("properties.template.scale.rules[0].http.auth[0].triggerParameter", "trigger"),
            JMESPathCheck("properties.template.scale.rules[0].http.auth[0].secretRef", "secretref"),
            JMESPathCheck("properties.template.scale.rules[0].http.metadata.key", "value"),
        ])

        self.cmd(f'containerapp create -g {resource_group} -n {app}2 --image nginx --environment {env} --scale-rule-name my-datadog-rule --scale-rule-type datadog --scale-rule-metadata "queryValue=7" "age=120" "metricUnavailableValue=0" --scale-rule-auth "apiKey=api-key" "appKey=app-key"', checks=[JMESPathCheck("properties.template.scale.rules[0].custom.metadata.queryValue", "")])

        self.cmd(f'containerapp show -g {resource_group} -n {app}2', checks=[
            JMESPathCheck("properties.template.scale.rules[0].name", "my-datadog-rule"),
            JMESPathCheck("properties.template.scale.rules[0].custom.type", "datadog"),
            JMESPathCheck("properties.template.scale.rules[0].custom.metadata.queryValue", "7"),
            JMESPathCheck("properties.template.scale.rules[0].custom.metadata.age", "120"),
            JMESPathCheck("properties.template.scale.rules[0].custom.metadata.metricUnavailableValue", "0"),
            JMESPathCheck("properties.template.scale.rules[0].custom.auth[0].triggerParameter", "apiKey"),
            JMESPathCheck("properties.template.scale.rules[0].custom.auth[0].secretRef", "api-key"),
            JMESPathCheck("properties.template.scale.rules[0].custom.auth[1].triggerParameter", "appKey"),
            JMESPathCheck("properties.template.scale.rules[0].custom.auth[1].secretRef", "app-key"),
            JMESPathCheck("properties.template.scale.rules[0].custom.metadata.queryValue", "7"),

        ])

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="westeurope")
    def test_containerapp_scale_update(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        app = self.create_random_name(prefix='aca', length=24)

        env = prepare_containerapp_env_for_app_e2e_tests(self)

        self.cmd(f'containerapp create -g {resource_group} -n {app} --image nginx --ingress external --target-port 80 --environment {env} --scale-rule-name http-scale-rule --scale-rule-http-concurrency 50 --scale-rule-auth trigger=secretref --scale-rule-metadata key=value')

        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.template.scale.rules[0].name", "http-scale-rule"),
            JMESPathCheck("properties.template.scale.rules[0].http.metadata.concurrentRequests", "50"),
            JMESPathCheck("properties.template.scale.rules[0].http.metadata.key", "value"),
            JMESPathCheck("properties.template.scale.rules[0].http.auth[0].triggerParameter", "trigger"),
            JMESPathCheck("properties.template.scale.rules[0].http.auth[0].secretRef", "secretref"),
        ])

        self.cmd(f'containerapp update -g {resource_group} -n {app} --image nginx --scale-rule-name my-datadog-rule --scale-rule-type datadog --scale-rule-metadata "queryValue=7" "age=120" "metricUnavailableValue=0"  --scale-rule-auth "apiKey=api-key" "appKey=app-key"')

        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.template.scale.rules[0].name", "my-datadog-rule"),
            JMESPathCheck("properties.template.scale.rules[0].custom.type", "datadog"),
            JMESPathCheck("properties.template.scale.rules[0].custom.metadata.queryValue", "7"),
            JMESPathCheck("properties.template.scale.rules[0].custom.metadata.age", "120"),
            JMESPathCheck("properties.template.scale.rules[0].custom.metadata.metricUnavailableValue", "0"),
            JMESPathCheck("properties.template.scale.rules[0].custom.auth[0].triggerParameter", "apiKey"),
            JMESPathCheck("properties.template.scale.rules[0].custom.auth[0].secretRef", "api-key"),
            JMESPathCheck("properties.template.scale.rules[0].custom.auth[1].triggerParameter", "appKey"),
            JMESPathCheck("properties.template.scale.rules[0].custom.auth[1].secretRef", "app-key"),

        ])

        self.cmd(f'containerapp update -g {resource_group} -n {app} --cpu 0.5 --no-wait')
        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.template.containers[0].resources.cpu", "0.5"),
            JMESPathCheck("properties.template.scale.rules[0].name", "my-datadog-rule"),
            JMESPathCheck("properties.template.scale.rules[0].custom.type", "datadog"),
            JMESPathCheck("properties.template.scale.rules[0].custom.metadata.queryValue", "7"),
            JMESPathCheck("properties.template.scale.rules[0].custom.metadata.age", "120"),
            JMESPathCheck("properties.template.scale.rules[0].custom.metadata.metricUnavailableValue", "0"),
            JMESPathCheck("properties.template.scale.rules[0].custom.auth[0].triggerParameter", "apiKey"),
            JMESPathCheck("properties.template.scale.rules[0].custom.auth[0].secretRef", "api-key"),
            JMESPathCheck("properties.template.scale.rules[0].custom.auth[1].triggerParameter", "appKey"),
            JMESPathCheck("properties.template.scale.rules[0].custom.auth[1].secretRef", "app-key"),
        ])

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="westeurope")
    def test_containerapp_scale_type_tcp(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        app = self.create_random_name(prefix='aca', length=24)

        env = prepare_containerapp_env_for_app_e2e_tests(self)

        self.cmd(
            f'containerapp create -g {resource_group} -n {app} --image redis --transport tcp --ingress internal --target-port 6379 --environment {env}',
            checks=[
                JMESPathCheck("properties.provisioningState", "Succeeded"),
                JMESPathCheck("properties.configuration.ingress.transport", "Tcp"),
            ])

        self.cmd(
            f'containerapp update -g {resource_group} -n {app} --scale-rule-name tcp-scale-rule --scale-rule-type tcp --scale-rule-tcp-concurrency 2 --scale-rule-auth "apiKey=api-key" "appKey=app-key"',
            checks=[
                JMESPathCheck("properties.provisioningState", "Succeeded"),
                JMESPathCheck("properties.configuration.ingress.transport", "Tcp"),
                JMESPathCheck("properties.template.scale.rules[0].name", "tcp-scale-rule"),
                JMESPathCheck("properties.template.scale.rules[0].tcp.auth[0].triggerParameter", "apiKey"),
                JMESPathCheck("properties.template.scale.rules[0].tcp.auth[0].secretRef", "api-key"),
                JMESPathCheck("properties.template.scale.rules[0].tcp.auth[1].triggerParameter", "appKey"),
                JMESPathCheck("properties.template.scale.rules[0].tcp.auth[1].secretRef", "app-key"),
            ])
        # the metadata is not returned in create/update command, we should use show command to check
        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.template.scale.rules[0].name", "tcp-scale-rule"),
            JMESPathCheck("properties.template.scale.rules[0].tcp.metadata.concurrentConnections", "2"),
        ])

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="westeurope")
    def test_containerapp_scale_update_azure_queue(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        app = self.create_random_name(prefix='aca', length=24)
        env = prepare_containerapp_env_for_app_e2e_tests(self)

        self.cmd(f'containerapp create -g {resource_group} -n {app} --image nginx --ingress external --target-port 80 --environment {env} --scale-rule-name http-scale-rule --scale-rule-http-concurrency 50 --scale-rule-auth trigger=secretref --scale-rule-metadata key=value', checks=[JMESPathCheck("properties.template.scale.rules[0].http.metadata.key", "")])

        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.template.scale.rules[0].name", "http-scale-rule"),
            JMESPathCheck("properties.template.scale.rules[0].http.metadata.concurrentRequests", "50"),
            JMESPathCheck("properties.template.scale.rules[0].http.metadata.key", "value"),
            JMESPathCheck("properties.template.scale.rules[0].http.auth[0].triggerParameter", "trigger"),
            JMESPathCheck("properties.template.scale.rules[0].http.auth[0].secretRef", "secretref"),
            JMESPathCheck("properties.template.scale.rules[0].http.metadata.key", "value"),
        ])
        queue_name = self.create_random_name(prefix='queue', length=24)
        containerapp_yaml_text = f"""
properties:
    template:
        containers:
        -   image: nginx
            name: azure-equeue-container
            resources:
              cpu: 0.5
              memory: 1Gi
              ephemeralStorage: 2Gi
        scale:
            minReplicas: 0
            maxReplicas: 1
            rules:
            - name: azure-queue-scale-rule
              azureQueue:
                queueName: {queue_name}
                queueLength: 1
                auth:
                - secretRef: azure-storage
                  triggerParameter: connection
"""
        containerapp_file_name = f"{self._testMethodName}_containerapp.yml"

        write_test_file(containerapp_file_name, containerapp_yaml_text)
        self.cmd(f'containerapp update -n {app} -g {resource_group} --yaml {containerapp_file_name}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("properties.template.scale.rules[0].name", "azure-queue-scale-rule"),
            JMESPathCheck("properties.template.scale.rules[0].azureQueue.queueName", queue_name),
            JMESPathCheck("properties.template.scale.rules[0].azureQueue.queueLength", 1),
            JMESPathCheck("properties.template.scale.rules[0].custom.metadata", None),
        ])
        clean_up_test_file(containerapp_file_name)

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="westeurope")
    def test_containerapp_scale_revision_copy(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        app = self.create_random_name(prefix='aca', length=24)

        env = prepare_containerapp_env_for_app_e2e_tests(self)

        self.cmd(f'containerapp create -g {resource_group} -n {app} --image nginx --ingress external --target-port 80 --environment {env} --scale-rule-name http-scale-rule --scale-rule-http-concurrency 50 --scale-rule-auth trigger=secretref --scale-rule-metadata key=value')

        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.template.scale.rules[0].name", "http-scale-rule"),
            JMESPathCheck("properties.template.scale.rules[0].http.metadata.concurrentRequests", "50"),
            JMESPathCheck("properties.template.scale.rules[0].http.metadata.key", "value"),
            JMESPathCheck("properties.template.scale.rules[0].http.auth[0].triggerParameter", "trigger"),
            JMESPathCheck("properties.template.scale.rules[0].http.auth[0].secretRef", "secretref"),
        ])

        self.cmd(f'containerapp revision copy -g {resource_group} -n {app} --image nginx --scale-rule-name my-datadog-rule --scale-rule-type datadog --scale-rule-metadata "queryValue=7" "age=120" "metricUnavailableValue=0"  --scale-rule-auth "apiKey=api-key" "appKey=app-key"')

        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.template.scale.rules[0].name", "my-datadog-rule"),
            JMESPathCheck("properties.template.scale.rules[0].custom.type", "datadog"),
            JMESPathCheck("properties.template.scale.rules[0].custom.metadata.queryValue", "7"),
            JMESPathCheck("properties.template.scale.rules[0].custom.metadata.age", "120"),
            JMESPathCheck("properties.template.scale.rules[0].custom.metadata.metricUnavailableValue", "0"),
            JMESPathCheck("properties.template.scale.rules[0].custom.auth[0].triggerParameter", "apiKey"),
            JMESPathCheck("properties.template.scale.rules[0].custom.auth[0].secretRef", "api-key"),
            JMESPathCheck("properties.template.scale.rules[0].custom.auth[1].triggerParameter", "appKey"),
            JMESPathCheck("properties.template.scale.rules[0].custom.auth[1].secretRef", "app-key"),

        ])

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="westeurope")
    def test_containerapp_replica_commands(self, resource_group):
        self.cmd(f'configure --defaults location={TEST_LOCATION}')

        app_name = self.create_random_name(prefix='aca', length=24)
        replica_count = 3

        env = prepare_containerapp_env_for_app_e2e_tests(self)

        self.cmd(f'containerapp create -g {resource_group} -n {app_name} --environment {env} --ingress external --target-port 80 --min-replicas {replica_count}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("properties.template.scale.minReplicas", 3)
        ]).get_output_in_json()

        count = self.cmd(f"containerapp replica count -g {resource_group} -n {app_name}").output
        self.assertEqual(int(count), replica_count)

        self.cmd(f'containerapp replica list -g {resource_group} -n {app_name}', checks=[
            JMESPathCheck('length(@)', replica_count),
        ])
        self.cmd(f'containerapp update -g {resource_group} -n {app_name} --min-replicas 0', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("properties.template.scale.minReplicas", 0)
        ])

        self.cmd(f'containerapp delete -g {resource_group} -n {app_name} --yes')

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="westeurope")
    def test_containerapp_preview_create_with_yaml(self, resource_group):
        # MSI is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use eastus as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))

        app = self.create_random_name(prefix='yaml', length=24)

        env_id = prepare_containerapp_env_for_app_e2e_tests(self, location=location)
        env_rg = parse_resource_id(env_id).get('resource_group')
        env_name = parse_resource_id(env_id).get('name')
        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(env_rg, env_name)).get_output_in_json()

        user_identity_name = self.create_random_name(prefix='containerapp-user', length=24)
        user_identity = self.cmd(
            'identity create -g {} -n {}'.format(resource_group, user_identity_name)).get_output_in_json()
        user_identity_id = user_identity['id']

        # test managedEnvironmentId
        containerapp_yaml_text = f"""
                                location: {location}
                                type: Microsoft.App/containerApps
                                tags:
                                    tagname: value
                                properties:
                                  managedEnvironmentId: {containerapp_env["id"]}
                                  configuration:
                                    activeRevisionsMode: Multiple
                                    ingress:
                                      external: false
                                      additionalPortMappings:
                                      - external: false
                                        targetPort: 12345
                                      - external: false
                                        targetPort: 9090
                                        exposedPort: 23456
                                      allowInsecure: false
                                      targetPort: 80
                                      traffic:
                                        - latestRevision: true
                                          weight: 100
                                      transport: Auto
                                      ipSecurityRestrictions:
                                        - name: name
                                          ipAddressRange: "1.1.1.1/10"
                                          action: "Allow"
                                  template:
                                    revisionSuffix: myrevision
                                    terminationGracePeriodSeconds: 90
                                    containers:
                                      - image: nginx
                                        name: nginx
                                        env:
                                          - name: HTTP_PORT
                                            value: 80
                                        command:
                                          - npm
                                          - start
                                        resources:
                                          cpu: 0.5
                                          memory: 1Gi
                                    scale:
                                      minReplicas: 1
                                      maxReplicas: 3
                                      rules:
                                      - http:
                                          auth:
                                          - secretRef: secretref
                                            triggerParameter: trigger
                                          metadata:
                                            concurrentRequests: '50'
                                            key: value
                                        name: http-scale-rule
                                      - name: asb-rule
                                        custom:
                                         type: azure-servicebus
                                         metadata:
                                          topicName: testtopic
                                          subscriptionName: testsubname
                                          namespace: test-namespace
                                          messageCount: 5
                                         identity: {user_identity_id}
                                identity:
                                  type: UserAssigned
                                  userAssignedIdentities:
                                    {user_identity_id}: {{}}
                                """
        containerapp_file_name = f"{self._testMethodName}_containerapp.yml"

        write_test_file(containerapp_file_name, containerapp_yaml_text)
        self.cmd(
            f'containerapp create -n {app} -g {resource_group} --environment {env_id} --yaml {containerapp_file_name}')

        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("properties.configuration.ingress.external", False),
            JMESPathCheck("properties.configuration.ingress.additionalPortMappings[0].external", False),
            JMESPathCheck("properties.configuration.ingress.additionalPortMappings[0].targetPort", 12345),
            JMESPathCheck("properties.configuration.ingress.additionalPortMappings[1].external", False),
            JMESPathCheck("properties.configuration.ingress.additionalPortMappings[1].targetPort", 9090),
            JMESPathCheck("properties.configuration.ingress.additionalPortMappings[1].exposedPort", 23456),
            JMESPathCheck("properties.configuration.ingress.ipSecurityRestrictions[0].name", "name"),
            JMESPathCheck("properties.configuration.ingress.ipSecurityRestrictions[0].ipAddressRange",
                          "1.1.1.1/10"),
            JMESPathCheck("properties.configuration.ingress.ipSecurityRestrictions[0].action", "Allow"),
            JMESPathCheck("properties.environmentId", containerapp_env["id"]),
            JMESPathCheck("properties.template.revisionSuffix", "myrevision"),
            JMESPathCheck("properties.template.terminationGracePeriodSeconds", 90),
            JMESPathCheck("properties.template.containers[0].name", "nginx"),
            JMESPathCheck("properties.template.scale.minReplicas", 1),
            JMESPathCheck("properties.template.scale.maxReplicas", 3),
            JMESPathCheck("properties.template.scale.cooldownPeriod", 300),  # default value from RP
            JMESPathCheck("properties.template.scale.pollingInterval", 30),  # default value from RP
            JMESPathCheck("properties.template.scale.rules[0].name", "http-scale-rule"),
            JMESPathCheck("properties.template.scale.rules[0].http.metadata.concurrentRequests", "50"),
            JMESPathCheck("properties.template.scale.rules[0].http.metadata.key", "value"),
            JMESPathCheck("properties.template.scale.rules[0].http.auth[0].triggerParameter", "trigger"),
            JMESPathCheck("properties.template.scale.rules[0].http.auth[0].secretRef", "secretref"),
            JMESPathCheck("properties.template.scale.rules[1].name", "asb-rule"),
            JMESPathCheck("properties.template.scale.rules[1].custom.type", "azure-servicebus"),
            JMESPathCheck("properties.template.scale.rules[1].custom.metadata.topicName", "testtopic"),
            JMESPathCheck("properties.template.scale.rules[1].custom.metadata.subscriptionName", "testsubname"),
            JMESPathCheck("properties.template.scale.rules[1].custom.metadata.namespace", "test-namespace"),
            JMESPathCheck("properties.template.scale.rules[1].custom.metadata.messageCount", "5"),
            JMESPathCheck("properties.template.scale.rules[1].custom.identity", user_identity_id),
        ])

        # test managedEnvironmentId
        containerapp_yaml_text = f"""
                                        properties:
                                          configuration:
                                            activeRevisionsMode: Multiple
                                            ingress:
                                              external: false
                                              additionalPortMappings:
                                              - external: false
                                                targetPort: 321
                                              - external: false
                                                targetPort: 8080
                                                exposedPort: 1234
                                          template:
                                            scale:
                                              cooldownPeriod: 60
                                              pollingInterval: 301
                                        """

        write_test_file(containerapp_file_name, containerapp_yaml_text)

        self.cmd(f'containerapp update -n {app} -g {resource_group} --yaml {containerapp_file_name}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("properties.configuration.ingress.external", False),
            JMESPathCheck("properties.configuration.ingress.additionalPortMappings[0].external", False),
            JMESPathCheck("properties.configuration.ingress.additionalPortMappings[0].targetPort", 321),
            JMESPathCheck("properties.configuration.ingress.additionalPortMappings[1].external", False),
            JMESPathCheck("properties.configuration.ingress.additionalPortMappings[1].targetPort", 8080),
            JMESPathCheck("properties.configuration.ingress.additionalPortMappings[1].exposedPort", 1234),
            JMESPathCheck("properties.configuration.ingress.ipSecurityRestrictions[0].name", "name"),
            JMESPathCheck("properties.configuration.ingress.ipSecurityRestrictions[0].ipAddressRange",
                          "1.1.1.1/10"),
            JMESPathCheck("properties.configuration.ingress.ipSecurityRestrictions[0].action", "Allow"),
            JMESPathCheck("properties.environmentId", containerapp_env["id"]),
            JMESPathCheck("properties.template.terminationGracePeriodSeconds", 90),
            JMESPathCheck("properties.template.containers[0].name", "nginx"),
            JMESPathCheck("properties.template.scale.minReplicas", 1),
            JMESPathCheck("properties.template.scale.maxReplicas", 3),
            JMESPathCheck("properties.template.scale.cooldownPeriod", 60),
            JMESPathCheck("properties.template.scale.pollingInterval", 301),
            JMESPathCheck("properties.template.scale.rules[0].name", "http-scale-rule"),
            JMESPathCheck("properties.template.scale.rules[0].http.auth[0].triggerParameter", "trigger"),
            JMESPathCheck("properties.template.scale.rules[0].http.auth[0].secretRef", "secretref"),
            JMESPathCheck("properties.template.scale.rules[1].name", "asb-rule"),
            JMESPathCheck("properties.template.scale.rules[1].custom.type", "azure-servicebus"),
            JMESPathCheck("properties.template.scale.rules[1].custom.identity", user_identity_id),
        ])
        clean_up_test_file(containerapp_file_name)

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="westeurope")
    def test_containerapp_create_with_yaml(self, resource_group):
        # MSI is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use eastus as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))

        app = self.create_random_name(prefix='yaml', length=24)

        env_id = prepare_containerapp_env_for_app_e2e_tests(self, location=location)
        env_rg = parse_resource_id(env_id).get('resource_group')
        env_name = parse_resource_id(env_id).get('name')
        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(env_rg, env_name)).get_output_in_json()

        user_identity_name = self.create_random_name(prefix='containerapp-user', length=24)
        user_identity = self.cmd('identity create -g {} -n {}'.format(resource_group, user_identity_name)).get_output_in_json()
        user_identity_id = user_identity['id']

        # test managedEnvironmentId
        containerapp_yaml_text = f"""
            location: {location}
            type: Microsoft.App/containerApps
            tags:
                tagname: value
            properties:
              managedEnvironmentId: {containerapp_env["id"]}
              configuration:
                secrets:
                - name: secret1
                  value: 1
                activeRevisionsMode: labels
                targetLabel: label1
                maxInactiveRevisions: 10
                ingress:
                  external: true
                  allowInsecure: false
                  targetPort: 80
                  transport: Auto
                  ipSecurityRestrictions:
                    - name: name
                      ipAddressRange: "1.1.1.1/10"
                      action: "Allow"
              template:
                revisionSuffix: myrevision
                terminationGracePeriodSeconds: 90
                containers:
                  - image: nginx
                    name: nginx
                    env:
                      - name: HTTP_PORT
                        value: 80
                    command:
                      - npm
                      - start
                    resources:
                      cpu: 0.5
                      memory: 1Gi
                scale:
                  minReplicas: 1
                  maxReplicas: 3
                  rules:
                  - http:
                      auth:
                      - secretRef: secretref
                        triggerParameter: trigger
                      metadata:
                        concurrentRequests: '50'
                        key: value
                    name: http-scale-rule
            identity:
              type: UserAssigned
              userAssignedIdentities:
                {user_identity_id}: {{}}
            """
        containerapp_file_name = f"{self._testMethodName}_containerapp.yml"

        write_test_file(containerapp_file_name, containerapp_yaml_text)
        self.cmd(f'containerapp create -n {app} -g {resource_group} --environment {env_id} --yaml {containerapp_file_name}')

        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("properties.configuration.activeRevisionsMode", "Labels"),
            JMESPathCheck("properties.configuration.ingress.external", True),
            JMESPathCheck("properties.configuration.ingress.traffic[0].label", "label1"),
            JMESPathCheck("properties.configuration.ingress.ipSecurityRestrictions[0].name", "name"),
            JMESPathCheck("properties.configuration.ingress.ipSecurityRestrictions[0].ipAddressRange", "1.1.1.1/10"),
            JMESPathCheck("properties.configuration.ingress.ipSecurityRestrictions[0].action", "Allow"),
            JMESPathCheck("properties.configuration.maxInactiveRevisions", "10"),
            JMESPathCheck("length(properties.configuration.secrets)", 1),
            JMESPathCheck("properties.environmentId", containerapp_env["id"]),
            JMESPathCheck("properties.template.revisionSuffix", "myrevision"),
            JMESPathCheck("properties.template.terminationGracePeriodSeconds", 90),
            JMESPathCheck("properties.template.containers[0].name", "nginx"),
            JMESPathCheck("properties.template.scale.minReplicas", 1),
            JMESPathCheck("properties.template.scale.maxReplicas", 3),
            JMESPathCheck("properties.template.scale.rules[0].name", "http-scale-rule"),
            JMESPathCheck("properties.template.scale.rules[0].http.metadata.concurrentRequests", "50"),
            JMESPathCheck("properties.template.scale.rules[0].http.metadata.key", "value"),
            JMESPathCheck("properties.template.scale.rules[0].http.auth[0].triggerParameter", "trigger"),
            JMESPathCheck("properties.template.scale.rules[0].http.auth[0].secretRef", "secretref"),
        ])

        # test environmentId
        containerapp_yaml_text = f"""
                    location: {location}
                    type: Microsoft.App/containerApps
                    tags:
                        tagname: value
                    properties:
                      environmentId: {containerapp_env["id"]}
                      configuration:
                        secrets:
                        - name: secret1
                        - name: secret2
                          value: 123
                        activeRevisionsMode: labels
                        targetLabel: label1
                        ingress:
                          external: true
                          allowInsecure: false
                          targetPort: 80
                          transport: Auto
                      template:
                        revisionSuffix: myrevision2
                        containers:
                          - image: nginx
                            name: nginx
                            env:
                              - name: HTTP_PORT
                                value: 80
                            command:
                              - npm
                              - start
                            resources:
                              cpu: 0.5
                              memory: 1Gi
                        scale:
                          minReplicas: 1
                          maxReplicas: 3
                          rules: []
                    """
        write_test_file(containerapp_file_name, containerapp_yaml_text)

        self.cmd(f'containerapp update -n {app} -g {resource_group} --yaml {containerapp_file_name}')

        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("properties.configuration.activeRevisionsMode", "Labels"),
            JMESPathCheck("properties.configuration.ingress.external", True),
            JMESPathCheck("properties.configuration.ingress.traffic[0].label", "label1"),
            JMESPathCheck("properties.configuration.ingress.ipSecurityRestrictions[0].name", "name"),
            JMESPathCheck("properties.configuration.ingress.ipSecurityRestrictions[0].ipAddressRange", "1.1.1.1/10"),
            JMESPathCheck("properties.configuration.ingress.ipSecurityRestrictions[0].action", "Allow"),
            JMESPathCheck("length(properties.configuration.secrets)", 2),
            JMESPathCheck("properties.environmentId", containerapp_env["id"]),
            JMESPathCheck("properties.template.revisionSuffix", "myrevision2"),
            JMESPathCheck("properties.template.containers[0].name", "nginx"),
            JMESPathCheck("properties.template.scale.minReplicas", 1),
            JMESPathCheck("properties.template.scale.maxReplicas", 3),
            JMESPathCheck("properties.template.scale.rules", None)
        ])

        self.cmd(f'containerapp secret show -g {resource_group} -n {app} --secret-name secret1', checks=[
            JMESPathCheck("name", 'secret1'),
            JMESPathCheck("value", '1'),
        ])

        self.cmd(f'containerapp secret show -g {resource_group} -n {app} --secret-name secret2', checks=[
            JMESPathCheck("name", 'secret2'),
            JMESPathCheck("value", '123'),
        ])

        # test update without environmentId
        containerapp_yaml_text = f"""
                            properties:
                              template:
                                revisionSuffix: myrevision3
                            """
        write_test_file(containerapp_file_name, containerapp_yaml_text)

        self.cmd(f'containerapp update -n {app} -g {resource_group} --yaml {containerapp_file_name}')

        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("properties.environmentId", containerapp_env["id"]),
            JMESPathCheck("properties.template.revisionSuffix", "myrevision3")
        ])

        # test invalid yaml
        containerapp_yaml_text = f"""
                                            """
        containerapp_file_name = f"{self._testMethodName}_containerapp.yml"
        write_test_file(containerapp_file_name, containerapp_yaml_text)
        try:
            self.cmd(f'containerapp create -n {app} -g {resource_group} --yaml {containerapp_file_name}')
        except Exception as ex:
            print(ex)
            self.assertTrue(isinstance(ex, ValidationError))
            self.assertEqual(ex.error_msg,
                             'Invalid YAML provided. Please see https://aka.ms/azure-container-apps-yaml for a valid containerapps YAML spec.')
            pass

        clean_up_test_file(containerapp_file_name)

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="westeurope")
    @live_only()  # encounters 'CannotOverwriteExistingCassetteException' only when run from recording (passes when run live)
    def test_containerapp_create_with_vnet_yaml(self, resource_group):
        # MSI is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use eastus as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))

        env = self.create_random_name(prefix='env', length=24)
        vnet = self.create_random_name(prefix='name', length=24)

        self.cmd(f"network vnet create --address-prefixes '14.0.0.0/23' -g {resource_group} -n {vnet}")
        sub_id = self.cmd(f"network vnet subnet create --address-prefixes '14.0.0.0/23' --delegations Microsoft.App/environments -n sub -g {resource_group} --vnet-name {vnet}").get_output_in_json()["id"]

        self.cmd(f'containerapp env create -g {resource_group} -n {env} --internal-only -s {sub_id}')
        containerapp_env = self.cmd(f'containerapp env show -g {resource_group} -n {env}').get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd(f'containerapp env show -g {resource_group} -n {env}').get_output_in_json()

        app = self.create_random_name(prefix='yaml', length=24)

        user_identity_name = self.create_random_name(prefix='containerapp-user', length=24)
        user_identity = self.cmd('identity create -g {} -n {}'.format(resource_group, user_identity_name)).get_output_in_json()
        user_identity_id = user_identity['id']

        # test create containerapp transport: Tcp, with exposedPort
        containerapp_yaml_text = f"""
        location: {location}
        type: Microsoft.App/containerApps
        tags:
            tagname: value
        properties:
          managedEnvironmentId: {containerapp_env["id"]}
          configuration:
            activeRevisionsMode: Multiple
            ingress:
              external: true
              exposedPort: 3000
              allowInsecure: false
              targetPort: 80
              traffic:
                - latestRevision: true
                  weight: 100
              transport: Tcp
          template:
            revisionSuffix: myrevision
            containers:
              - image: nginx
                name: nginx
                env:
                  - name: HTTP_PORT
                    value: 80
                command:
                  - npm
                  - start
                resources:
                  cpu: 0.5
                  memory: 1Gi
            scale:
              minReplicas: 1
              maxReplicas: 3
        identity:
          type: UserAssigned
          userAssignedIdentities:
            {user_identity_id}: {{}}
        """
        containerapp_file_name = f"{self._testMethodName}_containerapp.yml"

        write_test_file(containerapp_file_name, containerapp_yaml_text)
        self.cmd(f'containerapp create -n {app} -g {resource_group} --environment {env} --yaml {containerapp_file_name}')

        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("properties.configuration.ingress.external", True),
            JMESPathCheck("properties.configuration.ingress.exposedPort", 3000),
            JMESPathCheck("properties.environmentId", containerapp_env["id"]),
            JMESPathCheck("properties.template.revisionSuffix", "myrevision"),
            JMESPathCheck("properties.template.containers[0].name", "nginx"),
            JMESPathCheck("properties.template.scale.minReplicas", 1),
            JMESPathCheck("properties.template.scale.maxReplicas", 3)
        ])

        # test update containerapp transport: Tcp, with exposedPort
        containerapp_yaml_text = f"""
                location: {location}
                type: Microsoft.App/containerApps
                tags:
                    tagname: value
                properties:
                  environmentId: {containerapp_env["id"]}
                  configuration:
                    activeRevisionsMode: Multiple
                    ingress:
                      external: true
                      exposedPort: 9551
                      allowInsecure: false
                      targetPort: 80
                      traffic:
                        - latestRevision: true
                          weight: 100
                      transport: Tcp
                  template:
                    revisionSuffix: myrevision
                    containers:
                      - image: nginx
                        name: nginx
                        env:
                          - name: HTTP_PORT
                            value: 80
                        command:
                          - npm
                          - start
                        resources:
                          cpu: 0.5
                          memory: 1Gi
                    scale:
                      minReplicas: 1
                      maxReplicas: 3
                """
        write_test_file(containerapp_file_name, containerapp_yaml_text)

        self.cmd(f'containerapp update -n {app} -g {resource_group} --yaml {containerapp_file_name}')

        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("properties.configuration.ingress.external", True),
            JMESPathCheck("properties.configuration.ingress.exposedPort", 9551),
            JMESPathCheck("properties.environmentId", containerapp_env["id"]),
            JMESPathCheck("properties.template.revisionSuffix", "myrevision"),
            JMESPathCheck("properties.template.containers[0].name", "nginx"),
            JMESPathCheck("properties.template.scale.minReplicas", 1),
            JMESPathCheck("properties.template.scale.maxReplicas", 3)
        ])

        # test create containerapp transport: http, with CORS policy
        containerapp_yaml_text = f"""
                        location: {location}
                        type: Microsoft.App/containerApps
                        tags:
                            tagname: value
                        properties:
                          environmentId: {containerapp_env["id"]}
                          configuration:
                            activeRevisionsMode: Multiple
                            ingress:
                              external: true
                              allowInsecure: false
                              clientCertificateMode: Require
                              corsPolicy:
                                allowedOrigins: [a, b]
                                allowedMethods: [c, d]
                                allowedHeaders: [e, f]
                                exposeHeaders: [g, h]
                                maxAge: 7200
                                allowCredentials: true
                              targetPort: 80
                              ipSecurityRestrictions:
                                - name: name
                                  ipAddressRange: "1.1.1.1/10"
                                  action: "Allow"
                              traffic:
                                - latestRevision: true
                                  weight: 100
                              transport: http
                          template:
                            revisionSuffix: myrevision
                            containers:
                              - image: nginx
                                name: nginx
                                env:
                                  - name: HTTP_PORT
                                    value: 80
                                command:
                                  - npm
                                  - start
                                resources:
                                  cpu: 0.5
                                  memory: 1Gi
                            scale:
                              minReplicas: 1
                              maxReplicas: 3
                        """
        write_test_file(containerapp_file_name, containerapp_yaml_text)
        app2 = self.create_random_name(prefix='yaml', length=24)
        self.cmd(f'containerapp create -n {app2} -g {resource_group} --environment {env} --yaml {containerapp_file_name}')

        self.cmd(f'containerapp show -g {resource_group} -n {app2}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("properties.configuration.ingress.external", True),
            JMESPathCheck("properties.configuration.ingress.clientCertificateMode", "Require"),
            JMESPathCheck("properties.configuration.ingress.corsPolicy.allowCredentials", True),
            JMESPathCheck("properties.configuration.ingress.corsPolicy.maxAge", 7200),
            JMESPathCheck("properties.configuration.ingress.corsPolicy.allowedHeaders[0]", "e"),
            JMESPathCheck("properties.configuration.ingress.corsPolicy.allowedMethods[0]", "c"),
            JMESPathCheck("properties.configuration.ingress.corsPolicy.allowedOrigins[0]", "a"),
            JMESPathCheck("properties.configuration.ingress.corsPolicy.exposeHeaders[0]", "g"),
            JMESPathCheck("properties.configuration.ingress.ipSecurityRestrictions[0].name", "name"),
            JMESPathCheck("properties.configuration.ingress.ipSecurityRestrictions[0].ipAddressRange", "1.1.1.1/10"),
            JMESPathCheck("properties.configuration.ingress.ipSecurityRestrictions[0].action", "Allow"),
            JMESPathCheck("properties.environmentId", containerapp_env["id"]),
            JMESPathCheck("properties.template.revisionSuffix", "myrevision"),
            JMESPathCheck("properties.template.containers[0].name", "nginx"),
            JMESPathCheck("properties.template.scale.minReplicas", 1),
            JMESPathCheck("properties.template.scale.maxReplicas", 3)
        ])
        clean_up_test_file(containerapp_file_name)


class ContainerappOtherPropertyTests(ScenarioTest):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, random_config_dir=True, **kwargs)

    @live_only() # Pass lively, failed in playback mode because in the playback mode the cloud is AzureCloud, not AzureChinaCloud
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="chinaeast3")
    def test_containerapp_up_mooncake(self, resource_group):
        ca_name = self.create_random_name(prefix='containerapp', length=24)
        image_name = "mcr.microsoft.com/k8se/quickstart:latest"
        self.cmd('az containerapp up -n {} -g {} --image {} -l chinaeast3'.format(ca_name, resource_group, image_name))
        self.cmd('az containerapp show -n {} -g {}'.format(ca_name, resource_group), checks=[
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck("properties.template.containers[0].image", image_name),
        ])

        self.cmd('az containerapp env list -g {}'.format(resource_group), checks=[
            JMESPathCheck('length(@)', 1),
        ])

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="westus")
    @SubnetPreparer(location="centralus", delegations='Microsoft.App/environments', service_endpoints="Microsoft.Storage.Global")
    def test_containerapp_get_customdomainverificationid_e2e(self, resource_group, subnet_id, vnet_name, subnet_name):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        env_name = self.create_random_name(prefix='containerapp-env', length=24)
        logs_workspace_name = self.create_random_name(prefix='containerapp-env', length=24)

        logs_workspace_id = self.cmd(
            'monitor log-analytics workspace create -g {} -n {} -l eastus'
            .format(resource_group, logs_workspace_name)
        ).get_output_in_json()["customerId"]
        logs_workspace_key = self.cmd(
            'monitor log-analytics workspace get-shared-keys -g {} -n {}'
            .format(resource_group, logs_workspace_name)
        ).get_output_in_json()["primarySharedKey"]

        verification_id = self.cmd(f'containerapp show-custom-domain-verification-id').get_output_in_json()
        self.assertEqual(len(verification_id), 64)

        # create an App service domain and update its txt records
        contacts = os.path.join(TEST_DIR, 'domain-contact.json')
        zone_name = "{}.com".format(env_name)
        subdomain_1 = "devtest"
        txt_name_1 = "asuid.{}".format(subdomain_1)
        hostname_1 = "{}.{}".format(subdomain_1, zone_name)

        self.cmd(
            "appservice domain create -g {} --hostname {} --contact-info=@'{}' --accept-terms"
            .format(resource_group, zone_name, contacts)
        ).get_output_in_json()
        self.cmd(
            'network dns record-set txt add-record -g {} -z {} -n {} -v {}'
            .format(resource_group, zone_name, txt_name_1, verification_id)
        ).get_output_in_json()

        # upload cert, add hostname & binding
        pfx_file = os.path.join(TEST_DIR, 'cert.pfx')
        pfx_password = 'test12'

        self.cmd(
            'containerapp env create -g {} -n {} --logs-workspace-id {} --logs-workspace-key {} '
            '--dns-suffix {} --certificate-file "{}" --certificate-password {} -s {}'
            .format(resource_group, env_name, logs_workspace_id, logs_workspace_key,
                    hostname_1, pfx_file, pfx_password, subnet_id))

        self.cmd(f'containerapp env show -n {env_name} -g {resource_group}', checks=[
            JMESPathCheck('name', env_name),
            JMESPathCheck('properties.customDomainConfiguration.dnsSuffix', hostname_1),
        ])

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northeurope")
    def test_containerapp_termination_grace_period_seconds(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        app = self.create_random_name(prefix='aca', length=24)
        image = "mcr.microsoft.com/k8se/quickstart:latest"
        terminationGracePeriodSeconds = 90
        env = prepare_containerapp_env_for_app_e2e_tests(self)

        self.cmd(f'containerapp create -g {resource_group} -n {app} --image {image} --ingress external --target-port 80 --environment {env} --termination-grace-period {terminationGracePeriodSeconds}')

        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[JMESPathCheck("properties.template.terminationGracePeriodSeconds", terminationGracePeriodSeconds)])

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northeurope")
    def test_containerapp_max_inactive_revisions(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        app = self.create_random_name(prefix='aca', length=24)
        image = "mcr.microsoft.com/k8se/quickstart:latest"

        env = prepare_containerapp_env_for_app_e2e_tests(self)

        self.cmd(f'containerapp create -g {resource_group} -n {app} --image {image} --ingress external --target-port 80 --environment {env} --cpu 0.5 --memory 1Gi')
        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[JMESPathCheck("properties.configuration.maxInactiveRevisions", 100)])

        maxInactiveRevisions = 99
        self.cmd(f'containerapp create -g {resource_group} -n {app} --image {image} --ingress external --target-port 80 --environment {env} --max-inactive-revisions {maxInactiveRevisions}')
        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[JMESPathCheck("properties.configuration.maxInactiveRevisions", maxInactiveRevisions)])

        maxInactiveRevisions = 50
        self.cmd(f'containerapp update -g {resource_group} -n {app} --cpu 0.5 --memory 1Gi --max-inactive-revisions {maxInactiveRevisions}')
        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[JMESPathCheck("properties.configuration.maxInactiveRevisions", maxInactiveRevisions)])

        self.cmd(f'containerapp update -g {resource_group} -n {app} --cpu 0.25 --memory 0.5Gi')
        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[JMESPathCheck("properties.configuration.maxInactiveRevisions", maxInactiveRevisions)])

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="centraluseuap")
    def test_containerapp_kind_functionapp(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        app = self.create_random_name(prefix='aca', length=24)
        image = "mcr.microsoft.com/k8se/quickstart:latest"

        env = prepare_containerapp_env_for_app_e2e_tests(self)

        self.cmd(f'containerapp create -g {resource_group} -n {app} --image {image} --ingress external --target-port 80 --environment {env} --cpu 0.5 --memory 1Gi', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("kind", None)
        ])

        self.cmd(f'containerapp create -g {resource_group} -n {app} --image {image} --ingress external --target-port 80 --environment {env} --kind functionapp', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("kind", "functionapp")
        ])

        self.cmd(f'containerapp update -g {resource_group} -n {app} --cpu 0.25 --memory 0.5Gi', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("kind", "functionapp")
        ])

class ContainerappRuntimeTests(ScenarioTest):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, random_config_dir=True, **kwargs)

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northcentralus")
    def test_containerapp_runtime_java_metrics_create(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        app = self.create_random_name(prefix='aca', length=24)
        image = "mcr.microsoft.com/azurespringapps/samples/hello-world:0.0.1"

        env = prepare_containerapp_env_for_app_e2e_tests(self)

        def create_containerapp_with_runtime_java_metrics_args_and_check(args, expect_failure=False, checks=[]):
            self.cmd(f'containerapp create -g {resource_group} -n {app} --image {image} --environment {env} {args}', expect_failure=expect_failure)
            if not expect_failure:
                self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=checks)

                # Delete container app
                self.cmd(f'containerapp delete  -g {resource_group} -n {app} --yes')

        # Create container app without runtime settings
        create_containerapp_with_runtime_java_metrics_args_and_check('', checks=[
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck("properties.configuration.runtime", None)
            ])

        # Create container app with runtime=generic, it should not have runtime settings
        create_containerapp_with_runtime_java_metrics_args_and_check('--runtime=generic', checks=[
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck("properties.configuration.runtime", None)
            ])

        # Create container app with runtime=java, it should have default java runtime settings
        create_containerapp_with_runtime_java_metrics_args_and_check('--runtime=java', checks=[
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck("properties.configuration.runtime.java.enableMetrics", True)
            ])

        # Create container app with runtime=java and disable java metrics
        create_containerapp_with_runtime_java_metrics_args_and_check('--runtime=java --enable-java-metrics=false', checks=[
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck("properties.configuration.runtime.java.enableMetrics", False)
            ])

        # Create container app with runtime=java and enable java metrics
        create_containerapp_with_runtime_java_metrics_args_and_check('--runtime=java --enable-java-metrics', checks=[
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck("properties.configuration.runtime.java.enableMetrics", True)
            ])

        # Create container app with enable java metrics without setting runtime explicitly
        create_containerapp_with_runtime_java_metrics_args_and_check('--runtime=java --enable-java-metrics', checks=[
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck("properties.configuration.runtime.java.enableMetrics", True)
            ])

        # Unmatched runtime, runtime should be java when enable-java-metrics is set
        create_containerapp_with_runtime_java_metrics_args_and_check('--runtime=generic --enable-java-metrics', expect_failure=True)

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northcentralus")
    def test_containerapp_runtime_java_metrics_update(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        app = self.create_random_name(prefix='aca', length=24)
        image = "mcr.microsoft.com/azurespringapps/samples/hello-world:0.0.1"

        env = prepare_containerapp_env_for_app_e2e_tests(self)

        # Create container app without enabling java metrics
        self.cmd(f'containerapp create -g {resource_group} -n {app} --image {image} --environment {env}')
        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck("properties.configuration.runtime", None)
            ])

        # Update contaier app without runtime settings, it should keep the same runtime settings
        self.cmd(f'containerapp update -g {resource_group} -n {app} --cpu 0.5 --memory 1Gi', checks=[
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck("properties.configuration.runtime", None)
            ])

        self.cmd(f'containerapp update -g {resource_group} -n {app} --enable-java-metrics', checks=[
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck("properties.configuration.runtime.java.enableMetrics", True)
            ])

        self.cmd(f'containerapp update -g {resource_group} -n {app} --cpu 0.25 --memory 0.5Gi', checks=[
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck("properties.configuration.runtime.java.enableMetrics", True)
            ])

        # Update container app with runtime=generic, it should erase runtime settings
        self.cmd(f'containerapp update -g {resource_group} -n {app} --runtime=generic', checks=[
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck("properties.configuration.runtime", None)
            ])

        # Update container app with runtime=java, it should setup default java runtime settings if not set before
        self.cmd(f'containerapp update -g {resource_group} -n {app} --runtime=java', checks=[
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck("properties.configuration.runtime.java.enableMetrics", True)
            ])

        # Update container app with only runtime=java will keep the previous settings if set before
        self.cmd(f'containerapp update -g {resource_group} -n {app} --runtime=java', checks=[
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck("properties.configuration.runtime.java.enableMetrics", True)
            ])

        self.cmd(f'containerapp update -g {resource_group} -n {app} --runtime=java --enable-java-metrics', checks=[
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck("properties.configuration.runtime.java.enableMetrics", True)
            ])

        # Update container app with runtime=java, it should keep the same runtime settings
        self.cmd(f'containerapp update -g {resource_group} -n {app} --runtime=java', checks=[
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck("properties.configuration.runtime.java.enableMetrics", True)
            ])

        self.cmd(f'containerapp update -g {resource_group} -n {app} --runtime=java --enable-java-metrics=false', checks=[
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck("properties.configuration.runtime.java.enableMetrics", False)
            ])

        # Update container app with only runtime=java will keep the previous settings if set before
        self.cmd(f'containerapp update -g {resource_group} -n {app} --runtime=java', checks=[
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck("properties.configuration.runtime.java.enableMetrics", False)
            ])

        # It will imply runtime=java when enable-java-metrics is set
        self.cmd(f'containerapp update -g {resource_group} -n {app} --enable-java-metrics', checks=[
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck("properties.configuration.runtime.java.enableMetrics", True)
            ])

        self.cmd(f'containerapp update -g {resource_group} -n {app} --enable-java-metrics=false', checks=[
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck("properties.configuration.runtime.java.enableMetrics", False)
            ])

        # Update container app failed with wrong runtime
        self.cmd(f'containerapp update -g {resource_group} -n {app} --runtime=generic --enable-java-metrics',
                 expect_failure=True)

        # Delete container app
        self.cmd(f'containerapp delete  -g {resource_group} -n {app} --yes')

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northcentralus")
    def test_containerapp_runtime_java_create(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        app = self.create_random_name(prefix='aca', length=24)
        image = "mcr.microsoft.com/azurespringapps/samples/hello-world:0.0.1"

        env = prepare_containerapp_env_for_app_e2e_tests(self)

        def create_containerapp_with_runtime_java_agent_args_and_check(args, expect_failure=False, checks=[]):
            self.cmd(f'containerapp create -g {resource_group} -n {app} --image {image} --environment {env} {args}',
                     expect_failure=expect_failure)
            if not expect_failure:
                self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=checks)

                # Delete container app
                self.cmd(f'containerapp delete  -g {resource_group} -n {app} --yes')

        create_containerapp_with_runtime_java_agent_args_and_check('', checks=[
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck("properties.configuration.runtime", None)
        ])

        # Create container app with runtime=java, it should have default java runtime settings
        create_containerapp_with_runtime_java_agent_args_and_check('--runtime=java', checks=[
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck("properties.configuration.runtime.java.enableMetrics", True),
        ])

        # Create container app with runtime=java and enable java agent
        create_containerapp_with_runtime_java_agent_args_and_check('--runtime=java --enable-java-agent', checks=[
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck("properties.configuration.runtime.java.enableMetrics", True),
            JMESPathCheck("properties.configuration.runtime.java.javaAgent.enabled", True)
        ])

        # Create container app with runtime=java and enable java metrics
        create_containerapp_with_runtime_java_agent_args_and_check('--runtime=java --enable-java-metrics', checks=[
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck("properties.configuration.runtime.java.enableMetrics", True),
            JMESPathCheck("properties.configuration.runtime.java.javaAgent.enabled", True)
        ])

        # Create container app with runtime=java and disable java agent
        create_containerapp_with_runtime_java_agent_args_and_check('--runtime=java --enable-java-agent=false',checks=[
           JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck("properties.configuration.runtime.java.enableMetrics", True),
            JMESPathCheck("properties.configuration.runtime.java.javaAgent.enabled", False)
        ])

        # Create container app with runtime=java and disable java metrics
        create_containerapp_with_runtime_java_agent_args_and_check('--runtime=java --enable-java-metrics=false', checks=[
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck("properties.configuration.runtime.java.enableMetrics", False),
            JMESPathCheck("properties.configuration.runtime.java.javaAgent.enabled", False)
        ])

        # Create container app with runtime=java and enable java metrics and disable java agent
        create_containerapp_with_runtime_java_agent_args_and_check('--runtime=java --enable-java-metrics=true --enable-java-agent=false',checks=[
             JMESPathCheck('properties.provisioningState', "Succeeded"),
             JMESPathCheck("properties.configuration.runtime.java.enableMetrics", True),
             JMESPathCheck("properties.configuration.runtime.java.javaAgent.enabled", False)
         ])

        # Create container app with runtime=java and disable java metrics and enable java agent
        create_containerapp_with_runtime_java_agent_args_and_check('--runtime=java --enable-java-metrics=false --enable-java-agent=true', checks=[
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck("properties.configuration.runtime.java.enableMetrics", False),
            JMESPathCheck("properties.configuration.runtime.java.javaAgent.enabled", True)
        ])

        # Create container app with runtime=java and enable java metrics and enable java agent
        create_containerapp_with_runtime_java_agent_args_and_check('--runtime=java --enable-java-metrics=true --enable-java-agent=true', checks=[
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck("properties.configuration.runtime.java.enableMetrics", True),
            JMESPathCheck("properties.configuration.runtime.java.javaAgent.enabled", True)
        ])

        # Create container app with runtime=java and disable java metrics and disable java agent
        create_containerapp_with_runtime_java_agent_args_and_check('--runtime=java --enable-java-metrics=false --enable-java-agent=false', checks=[
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck("properties.configuration.runtime.java.enableMetrics", False),
            JMESPathCheck("properties.configuration.runtime.java.javaAgent.enabled", False)
        ])

        # Unmatched runtime, runtime should be java when enable-java-agent is set
        create_containerapp_with_runtime_java_agent_args_and_check('--runtime=generic --enable-java-agent',
                                                                     expect_failure=True)

        # Unmatched runtime, runtime should be java when enable-java-metrics is set
        create_containerapp_with_runtime_java_agent_args_and_check('--runtime=generic --enable-java-metrics',
                                                                   expect_failure=True)

        # Unmatched runtime, runtime should be java when enable-java-metrics and enable-java-agent are set
        create_containerapp_with_runtime_java_agent_args_and_check('--runtime=generic --enable-java-metrics --enable-java-agent',
                                                                   expect_failure=True)

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northcentralus")
    def test_containerapp_runtime_java_update(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        app = self.create_random_name(prefix='aca', length=24)
        image = "mcr.microsoft.com/azurespringapps/samples/hello-world:0.0.1"

        env = prepare_containerapp_env_for_app_e2e_tests(self)

        # Create container app without enabling java metrics
        self.cmd(f'containerapp create -g {resource_group} -n {app} --image {image} --environment {env}')
        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck("properties.configuration.runtime", None)
        ])

        # Update contaier app without runtime settings, it should keep the same runtime settings
        self.cmd(f'containerapp update -g {resource_group} -n {app} --cpu 0.5 --memory 1Gi', checks=[
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck("properties.configuration.runtime", None)
        ])

        self.cmd(f'containerapp update -g {resource_group} -n {app} --enable-java-metrics --enable-java-agent', checks=[
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck("properties.configuration.runtime.java.enableMetrics", True),
            JMESPathCheck("properties.configuration.runtime.java.javaAgent.enabled", True)
        ])

        self.cmd(f'containerapp update -g {resource_group} -n {app} --cpu 0.25 --memory 0.5Gi', checks=[
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck("properties.configuration.runtime.java.enableMetrics", True),
            JMESPathCheck("properties.configuration.runtime.java.javaAgent.enabled", True)
        ])

        self.cmd(f'containerapp update -g {resource_group} -n {app} --enable-java-agent=false', checks=[
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck("properties.configuration.runtime.java.enableMetrics", True),
            JMESPathCheck("properties.configuration.runtime.java.javaAgent.enabled", False)
        ])

        self.cmd(f'containerapp update -g {resource_group} -n {app} --enable-java-metrics=false', checks=[
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck("properties.configuration.runtime.java.enableMetrics", False),
            JMESPathCheck("properties.configuration.runtime.java.javaAgent.enabled", False)
        ])

        # Update container app with runtime=generic, it should erase runtime settings
        self.cmd(f'containerapp update -g {resource_group} -n {app} --runtime=generic', checks=[
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck("properties.configuration.runtime", None)
        ])

        # Update container app with runtime=java, it should setup default java runtime settings if not set before
        self.cmd(f'containerapp update -g {resource_group} -n {app} --runtime=java', checks=[
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck("properties.configuration.runtime.java.enableMetrics", True),
            JMESPathCheckNotExists("properties.configuration.runtime.java.javaAgent")
        ])

        self.cmd(f'containerapp update -g {resource_group} -n {app} --runtime=java --enable-java-metrics', checks=[
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck("properties.configuration.runtime.java.enableMetrics", True),
            JMESPathCheckNotExists("properties.configuration.runtime.java.javaAgent")
        ])

        self.cmd(f'containerapp update -g {resource_group} -n {app} --runtime=java --enable-java-agent', checks=[
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck("properties.configuration.runtime.java.enableMetrics", True),
            JMESPathCheck("properties.configuration.runtime.java.javaAgent.enabled", True)
        ])

        # Update container app with runtime=java, it should keep the same runtime settings
        self.cmd(f'containerapp update -g {resource_group} -n {app} --runtime=java', checks=[
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck("properties.configuration.runtime.java.enableMetrics", True),
            JMESPathCheck("properties.configuration.runtime.java.javaAgent.enabled", True)
        ])

        self.cmd(f'containerapp update -g {resource_group} -n {app} --runtime=java --enable-java-metrics=false',
                 checks=[
                     JMESPathCheck('properties.provisioningState', "Succeeded"),
                     JMESPathCheck("properties.configuration.runtime.java.enableMetrics", False),
                     JMESPathCheck("properties.configuration.runtime.java.javaAgent.enabled", True)
                 ])

        self.cmd(f'containerapp update -g {resource_group} -n {app} --runtime=java', checks=[
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck("properties.configuration.runtime.java.enableMetrics", False),
            JMESPathCheck("properties.configuration.runtime.java.javaAgent.enabled", True)
        ])

        # It will imply runtime=java when enable-java-metrics is set
        self.cmd(f'containerapp update -g {resource_group} -n {app} --enable-java-metrics', checks=[
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck("properties.configuration.runtime.java.enableMetrics", True),
            JMESPathCheck("properties.configuration.runtime.java.javaAgent.enabled", True)
        ])

        # Update container app failed with wrong runtime
        self.cmd(f'containerapp update -g {resource_group} -n {app} --runtime=generic --enable-java-metrics',
                 expect_failure=True)

        # Delete container app
        self.cmd(f'containerapp delete  -g {resource_group} -n {app} --yes')