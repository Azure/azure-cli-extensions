# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['sftp'] = """
    type: group
    short-summary: Generate SSH certificates and access Azure Storage blob data via SFTP
    long-summary: |
        These commands allow you to generate certificates and connect to Azure Storage Accounts using SFTP.

        PREREQUISITES:
        - Azure Storage Account with SFTP enabled
        - Appropriate RBAC permissions (Storage Blob Data Contributor or similar)
        - Azure CLI authentication (az login)
        - Network connectivity to Azure Storage endpoints

        The SFTP extension provides two main capabilities:
        1. Certificate generation using Azure AD authentication (similar to 'az ssh cert')
        2. Fully managed SFTP connections to Azure Storage with automatic credential handling

        AUTHENTICATION MODES:
        - Fully managed: No credentials needed - automatically generates SSH certificate
        - Certificate-based: Use existing SSH certificate file
        - Key-based: Use SSH public/private key pair (generates certificate automatically)

        This extension closely follows the patterns established by the SSH extension.
"""

helps['sftp cert'] = """
    type: command
    short-summary: Generate SSH certificate for SFTP authentication
    long-summary: |
        Generate an SSH certificate that can be used for authenticating to Azure Storage SFTP endpoints.
        This uses Azure AD authentication to generate a certificate similar to 'az ssh cert'.

        CERTIFICATE NAMING:
        - Generated certificates have '-aadcert.pub' suffix (e.g., id_rsa-aadcert.pub)
        - Certificates are valid for a limited time (typically 1 hour)
        - Private keys are generated with 'id_rsa' name when key pair is created

        The certificate can be used with 'az sftp connect' or with standard SFTP clients.
    examples:
        - name: Generate a certificate using an existing public key
          text: az sftp cert --public-key-file ~/.ssh/id_rsa.pub --file ~/my_cert.pub
        - name: Generate a certificate and create a new key pair in the same directory
          text: az sftp cert --file ~/my_cert.pub
        - name: Generate a certificate with custom SSH client folder
          text: az sftp cert --file ~/my_cert.pub --ssh-client-folder "C:\\Program Files\\OpenSSH"
"""

helps['sftp connect'] = """
    type: command
    short-summary: Access Azure Storage blob data via SFTP
    long-summary: |
        Establish an SFTP connection to an Azure Storage Account.

        AUTHENTICATION MODES:
        1. Fully managed (RECOMMENDED): Run without credentials - automatically generates SSH certificate
           and establishes connection. Credentials are cleaned up after use.

        2. Certificate-based: Use existing SSH certificate file. Certificate must be generated with
           'az sftp cert' or compatible with Azure AD authentication.

        3. Key-based: Provide SSH keys - command will generate certificate automatically from your keys.

        CONNECTION DETAILS:
        - Username format: {storage-account}.{azure-username}
        - Port: Uses SSH default (typically 22) unless specified with --port
        - Endpoints resolved automatically based on Azure cloud environment:
          * Azure Public: {storage-account}.blob.core.windows.net
          * Azure China: {storage-account}.blob.core.chinacloudapi.cn
          * Azure Government: {storage-account}.blob.core.usgovcloudapi.net

        SECURITY:
        - Generated credentials are automatically cleaned up after connection
        - Temporary files stored in secure temporary directories
        - OpenSSH handles certificate validation during connection
    examples:
        - name: Connect with automatic certificate generation (fully managed - RECOMMENDED)
          text: az sftp connect --storage-account mystorageaccount
        - name: Connect to storage account with existing certificate
          text: az sftp connect --storage-account mystorageaccount --certificate-file ~/my_cert.pub
        - name: Connect with existing SSH key pair
          text: az sftp connect --storage-account mystorageaccount --public-key-file ~/.ssh/id_rsa.pub --private-key-file ~/.ssh/id_rsa
        - name: Connect with custom port
          text: az sftp connect --storage-account mystorageaccount --port 2222
        - name: Connect with additional SFTP arguments for debugging
          text: az sftp connect --storage-account mystorageaccount --sftp-args="-v"
        - name: Connect with custom SSH client folder (Windows)
          text: az sftp connect --storage-account mystorageaccount --ssh-client-folder "C:\\Program Files\\OpenSSH"
        - name: Connect with custom connection timeout
          text: az sftp connect --storage-account mystorageaccount --sftp-args="-o ConnectTimeout=30"
"""
