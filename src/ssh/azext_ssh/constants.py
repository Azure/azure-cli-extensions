# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from colorama import Fore
from colorama import Style

CLIENT_PROXY_VERSION = "1.3.017634"
CLIENT_PROXY_RELEASE = "release01-11-21"
CLIENT_PROXY_STORAGE_URL = "https://sshproxysa.blob.core.windows.net"
CLEANUP_TOTAL_TIME_LIMIT_IN_SECONDS = 120
CLEANUP_TIME_INTERVAL_IN_SECONDS = 10
CLEANUP_AWAIT_TERMINATION_IN_SECONDS = 30
RELAY_INFO_MAXIMUM_DURATION_IN_SECONDS = 3600
WINDOWS_INVALID_FOLDERNAME_CHARS = "\\/*:<>?\"|"
RECOMMENDATION_SSH_CLIENT_NOT_FOUND = (Fore.YELLOW + "Ensure OpenSSH is installed correctly.\nAlternatively, use "
                                       "--ssh-client-folder to provide OpenSSH folder path." + Style.RESET_ALL)
RECOMMENDATION_RESOURCE_NOT_FOUND = (Fore.YELLOW + "Please ensure the active subscription is set properly "
                                     "and resource exists." + Style.RESET_ALL)
RDP_TERMINATE_SSH_WAIT_TIME_IN_SECONDS = 30
