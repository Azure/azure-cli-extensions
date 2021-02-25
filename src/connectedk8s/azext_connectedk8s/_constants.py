# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


# pylint: disable=line-too-long

Distribution_Enum_Values = ["auto", "generic", "openshift", "rancher_rke", "kind", "k3s", "minikube", "gke", "eks", "aks", "aks_management", "aks_workload", "capz", "aks_engine", "tkg"]
Infrastructure_Enum_Values = ["auto", "generic", "azure", "aws", "gcp", "azure_stack_hci", "azure_stack_hub", "azure_stack_edge", "vsphere", "windows_server"]
Feature_Values = ["cluster-connect", "cluster-extensions", "aad-rbac", "custom-locations"]

Azure_PublicCloudName = 'AZUREPUBLICCLOUD'
Azure_USGovCloudName = 'AZUREUSGOVERNMENTCLOUD'
Azure_DogfoodCloudName = 'AZUREDOGFOOD'
PublicCloud_OriginalName = 'AZURECLOUD'
USGovCloud_OriginalName = 'AZUREUSGOVERNMENT'
Dogfood_RMEndpoint = 'https://api-dogfood.resources.windows-int.net/'
Helm_Environment_File_Fault_Type = 'helm-environment-file-error'
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
User_Not_Found_Type = 'aad-user-not-found-error'
Invalid_AAD_Profile_Details_Type = 'aad-profile-invalid-error'
Get_Credentials_Failed_Fault_Type = 'failed-to-get-list-cluster-user-credentials'
Get_User_AAD_Details_Failed_Fault_Type = "failed-to-get-user-aad-details"
Failed_To_Merge_Credentials_Fault_Type = "failed-to-merge-credentials"
Kubeconfig_Failed_To_Load_Fault_Type = "failed-to-load-kubeconfig-file"
Failed_To_Load_K8s_Configuration_Fault_Type = "failed-to-load-kubernetes-configuration"
Failed_To_Merge_Kubeconfig_File = "failed-to-merge-kubeconfig-file"
Different_Object_With_Same_Name_Fault_Type = "Kubeconfig has an object with same name"
Invalid_Auth_Method_Fault = "Invalid authentication method passed"
Get_Connected_Cluster_Details_Failed_Fault_Type = "Failed to get connected cluster details"
Get_Credentials_Invoked_Without_Token_For_NON_AAD_Fault_Type = "Get Credentials Invoked without client token for Non-AAD connected cluster"
Cluster_Info_Not_Found_Type = 'Error while finding current cluster server details'
Deleting_Arc_Agents_With_Proxy_Kubeconfig_Fault_Type = "The arc agents shouldn't be deleted with proxy kubeconfig"
Incomplete_AAD_Profile_Details_Fault_Type = "AAD client app id or server app id is not provided."
UserProfile_Fault_Type = "USERPROFILE environment variable is not set on windows"
Download_Exe_Fault_Type = "Error while downloading client proxy executable from storage account"
Create_Directory_Fault_Type = "Error while creating directory for placing the executable"
Remove_File_Fault_Type = "Error while removing older client proxy executables."
Open_File_Fault_Type = "Error while opening file in read mode"
Run_Clientproxy_Fault_Type = "Error while starting client proxy process."
Post_Hybridconn_Fault_Type = "Error while posting hybrid connection details to proxy process"
Post_RefreshToken_Fault_Type = "Error while posting refresh token details to proxy process"
Merge_Kubeconfig_Fault_Type = "Error while merging kubeconfig."
Create_CSPExe_Fault_Type = "Error while creating csp executable"
Remove_Config_Fault_Type = "Error while removing old csp config"
Load_Creds_Fault_Type = "Error while loading accessToken.json"
Creds_NotFound_Fault_Type = "Credentials of user not found"
Create_Config_Fault_Type = "Error while creating config file for proxy"
Run_RefreshThread_Fault_Type = "Error while starting refresh thread"
Load_Kubeconfig_Fault_Type = "Error while loading kubeconfig"

Unsupported_Fault_Type = "Error while checking operating system.Unsupported OS detected."

Cluster_Info_Not_Found_Type = 'Error while finding current cluster server details'
Kubeconfig_Failed_To_Load_Fault_Type = "failed-to-load-kubeconfig-file"
Proxy_Cert_Path_Does_Not_Exist_Fault_Type = 'proxy-cert-path-does-not-exist-error'
Proxy_Cert_Path_Does_Not_Exist_Error = 'Proxy cert path {} does not exist. Please check the path provided'
Get_Kubernetes_Infra_Fault_Type = 'kubernetes-get-infrastructure-error'
No_Param_Error = 'No parmeters were specified with update command. Please run az connectedk8s update --help to check parameters available for update'
EnableProxy_Conflict_Error = 'Conflict detected: --disable-proxy can not be set with --https-proxy, --http-proxy, --proxy-skip-range and --proxy-cert at the same time. Please run az connectedk8s update --help for more information about the parameters'
Manual_Upgrade_Called_In_Auto_Update_Enabled = 'Manual Upgrade was called while in auto_Update enabled mode'
Upgrade_Agent_Success = 'Agents for Connected Cluster {} have been upgraded successfully'
Upgrade_Agent_Failure = 'Error while upgrading agents. Please run \"kubectl get pods -n azure-arc\" to check the pods in case of timeout error. Error: {}'
Release_Namespace_Not_Found = 'Error while getting azure-arc releasenamespace'
Get_Helm_Values_Failed = 'Error while doing helm get values azure-arc'
Helm_Existing_User_Supplied_Value_Get_Fault = 'Error while loading the user supplied helm values'
Error_Flattening_User_Supplied_Value_Dict = 'Error while flattening the user supplied helm values dict'
Upgrade_RG_Cluster_Name_Conflict = 'The provided cluster name and rg correspond to different cluster'
Corresponding_CC_Resource_Deleted_Fault = 'CC resource corresponding to this cluster has been deleted by the customer'
