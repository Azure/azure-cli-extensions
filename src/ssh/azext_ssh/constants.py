# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from colorama import Fore
from colorama import Style

AGENT_MINIMUM_VERSION_MAJOR = 1
AGENT_MINIMUM_VERSION_MINOR = 31
CLIENT_PROXY_VERSION = "1.3.026031"
CLIENT_PROXY_RELEASE = "release17-02-24"
CLIENT_PROXY_STORAGE_URL = "https://sshproxysa.blob.core.windows.net"
CLEANUP_TOTAL_TIME_LIMIT_IN_SECONDS = 120
CLEANUP_TIME_INTERVAL_IN_SECONDS = 10
CLEANUP_AWAIT_TERMINATION_IN_SECONDS = 30
RELAY_INFO_MAXIMUM_DURATION_IN_SECONDS = 3600
RETRY_DELAY_IN_SECONDS = 10
SERVICE_CONNECTION_DELAY_IN_SECONDS = 15
WINDOWS_INVALID_FOLDERNAME_CHARS = "\\/*:<>?\"|"
RECOMMENDATION_SSH_CLIENT_NOT_FOUND = (Fore.YELLOW + "Ensure OpenSSH is installed correctly.\nAlternatively, use "
                                       "--ssh-client-folder to provide OpenSSH folder path." + Style.RESET_ALL)
RECOMMENDATION_RESOURCE_NOT_FOUND = (Fore.YELLOW + "Please ensure the active subscription is set properly "
                                     "and resource exists." + Style.RESET_ALL)
RDP_TERMINATE_SSH_WAIT_TIME_IN_SECONDS = 30

ARC_RESOURCE_TYPE_PLACEHOLDER = "arc_resource_type_placeholder"

SUPPORTED_RESOURCE_TYPES = ["microsoft.hybridcompute/machines",
                            "microsoft.compute/virtualmachines",
                            "microsoft.connectedvmwarevsphere/virtualmachines",
                            "microsoft.scvmm/virtualmachines",
                            "microsoft.azurestackhci/virtualmachines"]

# Old version incorrectly used resource providers instead of resource type.
# Will continue to support to avoid breaking backwards compatibility.
LEGACY_SUPPORTED_RESOURCE_TYPES = ["microsoft.hybridcompute",
                                   "microsoft.compute",
                                   "microsoft.connectedvmwarevsphere",
                                   "microsoft.scvmm",
                                   "microsoft.azurestackhci"]

RESOURCE_PROVIDER_TO_RESOURCE_TYPE = {
    "microsoft.hybridcompute": "Microsoft.HybridCompute/machines",
    "microsoft.compute": "Microsoft.Compute/virtualMachines",
    "microsoft.connectedvmwarevsphere": "Microsoft.ConnectedVMwarevSphere/virtualMachines",
    "microsoft.azurestackhci": "Microsoft.AzureStackHCI/virtualMachines",
    "microsoft.scvmm": "Microsoft.ScVmm/virtualMachines"
}

RESOURCE_TYPE_LOWER_CASE_TO_CORRECT_CASE = {
    "microsoft.hybridcompute/machines": "Microsoft.HybridCompute/machines",
    "microsoft.compute/virtualmachines": "Microsoft.Compute/virtualMachines",
    "microsoft.connectedvmwarevsphere/virtualmachines": "Microsoft.ConnectedVMwarevSphere/virtualMachines",
    "microsoft.scvmm/virtualmachines": "Microsoft.ScVmm/virtualMachines",
    "microsoft.azurestackhci/virtualmachines": "Microsoft.AzureStackHCI/virtualMachines"
}
