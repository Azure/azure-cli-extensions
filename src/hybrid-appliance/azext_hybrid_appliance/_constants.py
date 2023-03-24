# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


# pylint: disable=line-too-long
# common constants
Snap_Config_Storage_End_Point = "https://kkanukollubatch.blob.core.windows.net"
Snap_Config_Container_Name = "pipelinetest"
Snap_Config_File_Name = "snap-configuration.json"
Snap_Pull_Public_Api_Endpoint = "api.snapcraft.io"
Snap_Pull_Public_Storage_Endpoint = "https://storage.snapcraftcontent.com"
App_Insights_Endpoint = "https://mcr.microsoft.com" # Putting a place holder here to stop the command from failing. We need to figure out the correct endpoint to check here.
MCR_Endpoint = "https://mcr.microsoft.com"
Memory_Threshold = 4
Disk_Threshold = 20
Supported_Locations = "southeastasia"
# Fault types
Download_And_Install_Kubectl_Fault_Type = "Failed to download and install kubectl"
Non_Linux_Machine = "User's machine is not a Linux machine"
DiskSpace_Validation_Failed = "DiskSpace threshold not met"
Memory_Validation_Failed = "Memory threshold not met"
Validations_Failed = "Pre-requisite validations failed"
MicroK8s_Setup_Failed = "MicroK8s cluster setup failed"
MicroK8s_Cluster_Not_Running = "MicroK8s cluster not running"
Arc_Onboarding_Failed = "Arc onboarding of k8s cluster failed"
Endpoints_Reachability_Validation_Failed = "Endpoints reachability validation failed"
Upgrade_RG_Cluster_Name_Conflict = 'The provided cluster name and rg correspond to different cluster'
MicroK8s_Upgrade_Failed = "MicroK8s cluster upgrade failed"
Entries_Not_Found_In_ConfigMap = "Name and RG entries not found in configmap"
Unsupported_K8s_Version = "K8s version greater than latest supported"
Read_ConfigMap_Fault_Type = 'configmap-read-error'
MicroK8s_Unhealthy_Post_Upgrade = "Microk8s unhealthy after upgrade"
