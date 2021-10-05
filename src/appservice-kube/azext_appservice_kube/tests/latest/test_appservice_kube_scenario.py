# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
import base64

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, RoleBasedServicePrincipalPreparer, live_only)

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

# TODO
class AppserviceKubernetesScenarioTest(ScenarioTest):
    @live_only()
    @AllowLargeResponse()
    @ResourceGroupPreparer(random_name_length=24, name_prefix='clitest', location="eastus", parameter_name="aks_rg")
    @ResourceGroupPreparer(random_name_length=24, name_prefix='clitest', location="eastus", parameter_name="arc_rg")
    def test_basic(self, aks_rg, arc_rg):
        print("starting test")
        # create aks
        aks_name = "{}-aks".format(aks_rg)

        self._create_connected_cluster(aks_name, aks_rg, arc_rg)

        # TODO change this to wait + poll
        self.assertEqual(self.cmd("connectedk8s show --resource-group {} --name {}".format(arc_rg, self.cluster_name)).get_output_in_json().get("provisioningState"), "Succeeded")

        self._create_log_analytics(arc_rg)
        self._install_appservice_extension(arc_rg, aks_rg)
        self._create_custom_location()
        self._create_kube_env()

    def _create_connected_cluster(self, aks_name, aks_rg, arc_rg):
        aks_create_result = self.cmd('aks create --resource-group {} --name {} --enable-aad --generate-ssh-keys'.format(aks_rg, aks_name)).get_output_in_json()

        self.infra_rg = self.cmd('aks show --resource-group {} --name {} --output tsv --query nodeResourceGroup'.format(aks_rg, aks_name)).output

        self.cmd("network public-ip create --resource-group {} --name MyPublicIP --sku STANDARD".format(self.infra_rg))
        self.static_ip = self.cmd("network public-ip show --resource-group {} --name MyPublicIP --output tsv --query ipAddress".format(self.infra_rg)).output


        print(self.cmd("aks get-credentials --resource-group {} --name {} --admin".format(aks_rg, aks_name)).output)
        # kubectl get ns

        self.cluster_name="{}-cluster".format(arc_rg) # Name of the connected cluster resource

        connectedk8s_result = self.cmd("connectedk8s connect --resource-group {} --name {}".format(arc_rg, self.cluster_name)).get_output_in_json()

        return self.cmd("connectedk8s show --resource-group {} --name {}".format(arc_rg, self.cluster_name)).get_output_in_json()
        # TODO may need to poll to wait for this to finish ^

    def _create_log_analytics(self, arc_rg):
        workspace_name="{}-workspace".format(arc_rg)
        self.cmd("monitor log-analytics workspace create --resource-group {} --workspace-name {}".format(arc_rg, workspace_name))
        log_analytics_workspace_id = self.cmd("az monitor log-analytics workspace show --resource-group {} --workspace-name {} --query customerId --output tsv".format(arc_rg, workspace_name)).output
        self.log_analytics_workspace_id_enc = base64.b64encode(bytes(log_analytics_workspace_id, "ascii"))
        log_analytics_key = self.cmd("monitor log-analytics workspace get-shared-keys --resource-group {} --workspace-name {} --query primarySharedKey --output tsv".format(arc_rg, workspace_name)).output
        self.log_analytics_key_enc = base64.b64encode(bytes(log_analytics_key, "ascii"))


    def _install_appservice_extension(self, arc_rg, aks_rg):
        extension_name = "appservice-ext" # Name of the App Service extension
        namespace = "appservice-ns" # Namespace in your cluster to install the extension and provision resources
        kube_environment_name = self.create_random_name("kube-env", 24)  # Name of the App Service Kubernetes environment resource
        self.cmd("k8s-extension create --debug \
            --resource-group {} \
            --name {} \
            --cluster-type connectedClusters \
            --cluster-name {} \
            --extension-type 'Microsoft.Web.Appservice' \
            --release-train stable \
            --auto-upgrade-minor-version true \
            --scope cluster \
            --release-namespace $namespace \
            --configuration-settings \"Microsoft.CustomLocation.ServiceAccount=default\" \
            --configuration-settings \"appsNamespace={}\" \
            --configuration-settings \"clusterName={}\" \
            --configuration-settings \"loadBalancerIp={}\" \
            --configuration-settings \"keda.enabled=true\" \
            --configuration-settings \"buildService.storageClassName=default\" \
            --configuration-settings \"buildService.storageAccessMode=ReadWriteOnce\" \
            --configuration-settings \"customConfigMap={}/kube-environment-config\" \
            --configuration-settings \"envoy.annotations.service.beta.kubernetes.io/azure-load-balancer-resource-group={}\" \
            --configuration-settings \"logProcessor.appLogs.destination=log-analytics\" \
            --configuration-protected-settings \"logProcessor.appLogs.logAnalyticsConfig.customerId={}\" \
            --configuration-protected-settings \"logProcessor.appLogs.logAnalyticsConfig.sharedKey={}\"".format(arc_rg, extension_name, self.cluster_name, namespace, kube_environment_name, self.static_ip, namespace, aks_rg, self.log_analytics_workspace_id_enc, self.log_analytics_key_enc))
        self.extension_id = self.cmd("k8s-extension show \
            --cluster-type connectedClusters \
            --cluster-name {} \
            --resource-group {} \
            --name {} \
            --query id \
            --output tsv".format(self.cluster_name, arc_rg, extension_name)).output
        self.cmd("resource wait --ids {} --custom \"properties.installState!='Pending'\" --api-version \"2020-07-01-preview\"".format(self.extension_id))

    def _create_custom_location(self):
        pass

    def _create_kube_env(self):
        pass