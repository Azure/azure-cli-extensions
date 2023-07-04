# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


# pylint: disable=line-too-long
# common constants
Snap_Config_Storage_End_Point = "https://k8connecthelm.azureedge.net"
Snap_Config_Container_Name = "snapconfig"
Snap_Config_File_Name = "snap-configuration.json"
Snap_Pull_Public_Api_Endpoint = "api.snapcraft.io"
Snap_Pull_Public_Storage_Endpoint = "https://storage.snapcraftcontent.com"
App_Insights_Endpoint = "https://dc.services.visualstudio.com/v2/track"
MCR_Endpoint = "https://mcr.microsoft.com"
Memory_Threshold = 4
Disk_Threshold = 20
CPU_Threshold = 4
diagnostics_folder_name = "diagnostics_logs"
onboarding_logs_folder_name = "onboarding_logs"
# Fault types
Download_And_Install_Kubectl_Fault_Type = "Failed to download and install kubectl"
Non_Linux_Machine = "User's machine is not a Linux machine"
DiskSpace_Validation_Failed = "DiskSpace threshold not met"
Memory_Validation_Failed = "Memory threshold not met"
CPU_CoreCount_None = "Unable to identify cpu core count"
CPU_Validation_Failed = "CPU core count threshold not met"
Validations_Failed = "Pre-requisite validations failed"
MicroK8s_Setup_Failed = "MicroK8s cluster setup failed"
Microk8s_Inspect_Failed = "Microk8s Inspect failed"
MicroK8s_Cluster_Not_Running = "MicroK8s cluster not running"
Arc_Onboarding_Failed = "Arc onboarding of k8s cluster failed"
Endpoints_Reachability_Validation_Failed = "Endpoints reachability validation failed"
Upgrade_RG_Cluster_Name_Conflict = 'The provided cluster name and rg correspond to different cluster'
MicroK8s_Upgrade_Failed = "MicroK8s cluster upgrade failed"
ConfigMap_Not_Found = "Arc config map not found on the cluster"
Entries_Not_Found_In_ConfigMap = "Name and RG entries not found in configmap"
Unsupported_K8s_Version = "K8s version greater than latest supported"
Failed_To_Change_Telemetry_Push_Interval = "Failed_To_Change_Telemetry_Push_Interval"
Read_ConfigMap_Fault_Type = 'configmap-read-error'
MicroK8s_Unhealthy_Post_Upgrade = "Microk8s unhealthy after upgrade"
Resource_Already_Exists_Fault_Type = "There already exists a resource with the given resource ID."
Connectedk8s_Troubleshoot_Failed = "Failed to run connectedk8s troubleshoot"
No_Storage_Space_Available_Fault_Type = "No storage available on the host machine"
Diagnostics_Folder_Creation_Failed_Fault_Type = "Failed to create diagnostics folder"
Log_file_path_env_variable_name = "LOG_FILE_PATH"
Log_file_name_env_variable_name = "LOG_FILE_NAME"