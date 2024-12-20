# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from colorama import Fore
from colorama import Style

WINDOWS_INVALID_FOLDERNAME_CHARS = "\\/*:<>?\"|"
RECOMMENDATION_SSH_CLIENT_NOT_FOUND = (Fore.YELLOW + "Ensure OpenSSH is installed correctly.\nAlternatively, use "
                                       "--ssh-client-folder to provide OpenSSH folder path." + Style.RESET_ALL)