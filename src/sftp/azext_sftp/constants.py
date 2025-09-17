# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from colorama import Fore, Style

# File system constants
WINDOWS_INVALID_FOLDERNAME_CHARS = "\\/*:<>?\"|"

# Default ports
DEFAULT_SSH_PORT = DEFAULT_SFTP_PORT = AZURE_STORAGE_SFTP_PORT = 22

# SSH/SFTP client configuration
SSH_CONNECT_TIMEOUT = 30
SSH_SERVER_ALIVE_INTERVAL = 60
SSH_SERVER_ALIVE_COUNT_MAX = 3

# Certificate and key file naming
SSH_PRIVATE_KEY_NAME = "id_rsa"
SSH_PUBLIC_KEY_NAME = "id_rsa.pub"
SSH_CERT_SUFFIX = "-aadcert.pub"

# Error messages and recommendations
RECOMMENDATION_SSH_CLIENT_NOT_FOUND = (
    Fore.YELLOW +
    "Ensure OpenSSH is installed correctly.\n"
    "Alternatively, use --ssh-client-folder to provide OpenSSH folder path." +
    Style.RESET_ALL
)

RECOMMENDATION_STORAGE_ACCOUNT_SFTP = (
    Fore.YELLOW +
    "Ensure your Azure Storage Account has SFTP enabled.\n"
    "Verify your account permissions include Storage Blob Data Contributor or similar." +
    Style.RESET_ALL
)
