# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import time
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck, live_only)

from .common import (write_test_file, TEST_LOCATION)

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class ContainerappScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(location="eastus", random_name_length=15)
    def test_containerapp_preview_environment_type(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))
        aks_name = "my-aks-cluster"
        connected_cluster_name = "my-connected-cluster"
        self.cmd(
            f'aks create --resource-group {resource_group} --name {aks_name} --enable-aad --generate-ssh-keys --enable-cluster-autoscaler --min-count 4 --max-count 10 --node-count 4')
        self.cmd(
            f'aks get-credentials --resource-group {resource_group} --name {aks_name} --overwrite-existing --admin')
        try:
            self.cmd(f'connectedk8s connect --resource-group {resource_group} --name {connected_cluster_name}')
        except:
            pass
        connected_cluster = self.cmd(
            f'az connectedk8s show --resource-group {resource_group} --name {connected_cluster_name}').get_output_in_json()
        connected_cluster_id = connected_cluster['id']
        extension = self.cmd(f'az k8s-extension create'
                             f' --resource-group {resource_group}'
                             f' --name containerapp-ext'
                             f' --cluster-type connectedClusters'
                             f' --cluster-name {connected_cluster["name"]}'
                             f' --extension-type "Microsoft.App.Environment" '
                             f' --release-train stable'
                             f' --auto-upgrade-minor-version true'
                             f' --scope cluster'
                             f' --release-namespace appplat-ns'
                             f' --configuration-settings "Microsoft.CustomLocation.ServiceAccount=default"'
                             f' --configuration-settings "appsNamespace=appplat-ns"'
                             f' --configuration-settings "clusterName={connected_cluster["name"]}"'
                             f' --configuration-settings "envoy.annotations.service.beta.kubernetes.io/azure-load-balancer-resource-group={resource_group}"').get_output_in_json()
        custom_location_name = "my-custom-location"
        custom_location_id = self.cmd(
            f'az customlocation create -g {resource_group} -n {custom_location_name} -l {TEST_LOCATION} --host-resource-id {connected_cluster_id} --namespace appplat-ns -c {extension["id"]}') \
            .get_output_in_json()['id']
        # create connected environment with client or create a command for connected?
        sub_id = self.cmd('az account show').get_output_in_json()['id']

        connected_env_name = 'my-connected-env'
        connected_env_resource_id = f"/subscriptions/{sub_id}/resourceGroups/{resource_group}/providers/Microsoft.App/connectedEnvironments/{connected_env_name}"
        file = f"{resource_group}.json"
        env_payload = '{{ "location": "{location}", "extendedLocation": {{ "name": "{custom_location_id}", "type": "CustomLocation" }}, "Properties": {{}}}}' \
            .format(location=TEST_LOCATION, custom_location_id=custom_location_id)
        write_test_file(file, env_payload)
        self.cmd(
            f'az rest --method put --uri "{connected_env_resource_id}?api-version=2022-06-01-preview" --body "@{file}"')
        containerapp_env = self.cmd(
            f'az rest --method get --uri "{connected_env_resource_id}?api-version=2022-06-01-preview"').get_output_in_json()
        while containerapp_env["properties"]["provisioningState"].lower() != "succeeded":
            time.sleep(5)
            containerapp_env = self.cmd(
                f'az rest --method get --uri "{connected_env_resource_id}?api-version=2022-06-01-preview"').get_output_in_json()

        ca_name = self.create_random_name(prefix='containerapp', length=24)
        self.cmd(
            f'az containerapp create --name {ca_name} --resource-group {resource_group} --environment {connected_env_name} --image "mcr.microsoft.com/k8se/quickstart:latest" --environment-type connected',
            checks=[
                JMESPathCheck('properties.environmentId', connected_env_resource_id),
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('extendedLocation.name', custom_location_id)
            ])
        ca_name2 = self.create_random_name(prefix='containerapp', length=24)
        self.cmd(
            f'az containerapp create --name {ca_name2} --resource-group {resource_group} --environment {connected_env_resource_id} --image "mcr.microsoft.com/k8se/quickstart:latest" --environment-type connected',
            checks=[
                JMESPathCheck('properties.environmentId', connected_env_resource_id),
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('extendedLocation.name', custom_location_id)
            ])
