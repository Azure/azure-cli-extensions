# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import time
import yaml

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck, live_only, StorageAccountPreparer)

from .common import TEST_LOCATION

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

from .utils import create_containerapp_env

class ContainerAppWorkloadProfilesTest(ScenarioTest):
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="eastus")
    @live_only()  # encounters 'CannotOverwriteExistingCassetteException' only when run from recording (passes when run live)
    def test_containerapp_env_workload_profiles_e2e(self, resource_group):
        import requests

        env = self.create_random_name(prefix='env', length=24)
        vnet = self.create_random_name(prefix='name', length=24)
        app1 = self.create_random_name(prefix='app1', length=24)
        app2 = self.create_random_name(prefix='app2', length=24)

        location = "northcentralus"

        self.cmd(f"az network vnet create -l {location} --address-prefixes '14.0.0.0/16' -g {resource_group} -n {vnet}")
        sub_id = self.cmd(f"az network vnet subnet create --address-prefixes '14.0.0.0/22' --delegations Microsoft.App/environments -n sub -g {resource_group} --vnet-name {vnet}").get_output_in_json()["id"]

        self.cmd(f'containerapp env create -g {resource_group} -n {env} -s {sub_id} --location {location} --enableWorkloadProfiles')

        containerapp_env = self.cmd(f'containerapp env show -g {resource_group} -n {env}').get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() in ["waiting", "inprogress"]:
            time.sleep(5)
            containerapp_env = self.cmd(f'containerapp env show -g {resource_group} -n {env}').get_output_in_json()
        time.sleep(30)

        self.cmd(f'containerapp env show -n {env} -g {resource_group}', checks=[
            JMESPathCheck('name', env),
            JMESPathCheck('properties.workloadProfiles[0].name', "Consumption", case_sensitive=False),
            JMESPathCheck('properties.workloadProfiles[0].workloadProfileType', "Consumption", case_sensitive=False),
        ])

        self.cmd(f"az containerapp env workload-profile list-supported -l {location}")

        profiles = self.cmd(f"az containerapp env workload-profile list -g {resource_group} -n {env}").get_output_in_json()
        self.assertEqual(len(profiles), 1)
        self.assertEqual(profiles[0]["properties"]["name"].lower(), "consumption")
        self.assertEqual(profiles[0]["properties"]["workloadProfileType"].lower(), "consumption")

        self.cmd(f"az containerapp env workload-profile set -g {resource_group} -n {env} --workload-profile-name my-d4 --workload-profile-type D4 --min-nodes 2 --max-nodes 3")

        while containerapp_env["properties"]["provisioningState"].lower() in ["waiting", "inprogress"]:
            time.sleep(5)
            containerapp_env = self.cmd(f'containerapp env show -g {resource_group} -n {env}').get_output_in_json()
        time.sleep(30)

        self.cmd(f"az containerapp env workload-profile show -g {resource_group} -n {env} --workload-profile-name my-d4 ", checks=[
            JMESPathCheck("properties.name", "my-d4"),
            JMESPathCheck("properties.maximumCount", 3),
            JMESPathCheck("properties.minimumCount", 2),
            JMESPathCheck("properties.workloadProfileType", "D4"),
        ])

        self.cmd(f"az containerapp env workload-profile set -g {resource_group} -n {env} --workload-profile-name my-d4 --min-nodes 1 --max-nodes 2")

        while containerapp_env["properties"]["provisioningState"].lower() in ["waiting", "inprogress"]:
            time.sleep(5)
            containerapp_env = self.cmd(f'containerapp env show -g {resource_group} -n {env}').get_output_in_json()
        time.sleep(30)

        self.cmd(f"az containerapp env workload-profile show -g {resource_group} -n {env} --workload-profile-name my-d4 ", checks=[
            JMESPathCheck("properties.name", "my-d4"),
            JMESPathCheck("properties.maximumCount", 2),
            JMESPathCheck("properties.minimumCount", 1),
            JMESPathCheck("properties.workloadProfileType", "D4"),
        ])

        self.cmd(f"az containerapp create -g {resource_group} --target-port 80 --ingress external --image mcr.microsoft.com/azuredocs/containerapps-helloworld:latest --environment {env} -n {app1} --workload-profile-name consumption")
        self.cmd(f"az containerapp create -g {resource_group} --target-port 80 --ingress external --image mcr.microsoft.com/azuredocs/containerapps-helloworld:latest --environment {env} -n {app2} --workload-profile-name my-d4")

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="eastus")
    @live_only()  # encounters 'CannotOverwriteExistingCassetteException' only when run from recording (passes when run live)
    def test_containerapp_env_workload_profiles_delete(self, resource_group):
        import requests

        env = self.create_random_name(prefix='env', length=24)
        vnet = self.create_random_name(prefix='name', length=24)

        location = "northcentralus"

        self.cmd(f"az network vnet create -l {location} --address-prefixes '14.0.0.0/16' -g {resource_group} -n {vnet}")
        sub_id = self.cmd(f"az network vnet subnet create --address-prefixes '14.0.0.0/22' --delegations Microsoft.App/environments -n sub -g {resource_group} --vnet-name {vnet}").get_output_in_json()["id"]

        self.cmd(f'containerapp env create -g {resource_group} -n {env} -s {sub_id} --location {location} --enableWorkloadProfiles')

        containerapp_env = self.cmd(f'containerapp env show -g {resource_group} -n {env}').get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() in ["waiting", "inprogress"]:
            time.sleep(5)
            containerapp_env = self.cmd(f'containerapp env show -g {resource_group} -n {env}').get_output_in_json()
        time.sleep(30)

        self.cmd(f"az containerapp env workload-profile set -g {resource_group} -n {env} --workload-profile-name my-d8 --workload-profile-type D8 --min-nodes 1 --max-nodes 1")

        while containerapp_env["properties"]["provisioningState"].lower() in ["waiting", "inprogress"]:
            time.sleep(5)
            containerapp_env = self.cmd(f'containerapp env show -g {resource_group} -n {env}').get_output_in_json()
        time.sleep(30)

        self.cmd(f"az containerapp env workload-profile show -g {resource_group} -n {env} --workload-profile-name my-d8 ", checks=[
            JMESPathCheck("properties.name", "my-d8"),
            JMESPathCheck("properties.maximumCount", 1),
            JMESPathCheck("properties.minimumCount", 1),
            JMESPathCheck("properties.workloadProfileType", "D8"),
        ])

        profiles = self.cmd(f"az containerapp env workload-profile list -g {resource_group} -n {env}").get_output_in_json()
        self.assertEqual(len(profiles), 2)

        self.cmd(f"az containerapp env workload-profile delete -g {resource_group} -n {env} --workload-profile-name my-d8 ")

        profiles = self.cmd(f"az containerapp env workload-profile list -g {resource_group} -n {env}").get_output_in_json()
        self.assertEqual(len(profiles), 1)