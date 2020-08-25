# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


# pylint: disable=line-too-long

Dogfood_RMEndpoint = 'https://api-dogfood.resources.windows-int.net/'
Invalid_Location_Fault_Type = 'location-validation-error'
Load_Kubeconfig_Fault_Type = 'kubeconfig-load-error'
Read_ConfigMap_Fault_Type = 'configmap-read-error'
Get_ResourceProvider_Fault_Type = 'resource-provider-fetch-error'
Get_ConnectedCluster_Fault_Type = 'connected-cluster-fetch-error'
Create_ConnectedCluster_Fault_Type = 'connected-cluster-create-error'
Delete_ConnectedCluster_Fault_Type = 'connected-cluster-delete-error'
Bad_DeleteRequest_Fault_Type = 'bad-delete-request-error'
Cluster_Already_Onboarded_Fault_Type = 'cluster-already-onboarded-error'
Resource_Already_Exists_Fault_Type = 'resource-already-exists-error'
Resource_Does_Not_Exist_Fault_Type = 'resource-does-not-exist-error'
Create_ResourceGroup_Fault_Type = 'resource-group-creation-error'
Add_HelmRepo_Fault_Type = 'helm-repo-add-error'
List_HelmRelease_Fault_Type = 'helm-list-release-error'
KeyPair_Generate_Fault_Type = 'keypair-generation-error'
PublicKey_Export_Fault_Type = 'publickey-export-error'
PrivateKey_Export_Fault_Type = 'privatekey-export-error'
Install_HelmRelease_Fault_Type = 'helm-release-install-error'
Delete_HelmRelease_Fault_Type = 'helm-release-delete-error'
Check_PodStatus_Fault_Type = 'check-pod-status-error'
Kubernetes_Connectivity_FaultType = 'kubernetes-cluster-connection-error'
Helm_Version_Fault_Type = 'helm-not-updated-error'
Check_HelmVersion_Fault_Type = 'helm-version-check-error'
Helm_Installation_Fault_Type = 'helm-not-installed-error'
Check_HelmInstallation_Fault_Type = 'check-helm-installed-error'
Get_HelmRegistery_Path_Fault_Type = 'helm-registry-path-fetch-error'
Pull_HelmChart_Fault_Type = 'helm-chart-pull-error'
Export_HelmChart_Fault_Type = 'helm-chart-export-error'
Get_Kubernetes_Version_Fault_Type = 'kubernetes-get-version-error'
Get_Kubernetes_Distro_Fault_Type = 'kubernetes-get-distribution-error'
Get_Kubernetes_Namespace_Fault_Type = 'kubernetes-get-namespace-error'
Update_Agent_Success = 'Agents for Connected Cluster {} have been updated successfully'
Update_Agent_Failure = 'Error while updating agents. Please run \"kubectl get pods -n azure-arc\" to check the pods in case of timeout error. Error: {}'
