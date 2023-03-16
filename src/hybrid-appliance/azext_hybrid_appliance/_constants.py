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
