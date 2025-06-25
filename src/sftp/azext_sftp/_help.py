# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['sftp'] = """
    type: group
    short-summary: Commands to connect to Azure Storage Accounts via SFTP
    long-summary: |
        These commands allow you to generate certificates and connect to Azure Storage Accounts using SFTP.
        
        The SFTP extension provides two main capabilities:
        1. Certificate generation using Azure AD authentication (similar to 'az ssh cert')
        2. Fully managed SFTP connections to Azure Storage with automatic credential handling
        
        This extension closely follows the patterns established by the SSH extension, providing
        a familiar experience for users already using 'az ssh' commands.
"""

helps['sftp cert'] = """
    type: command
    short-summary: Generate SSH certificate for SFTP authentication
    long-summary: |
        Generate an SSH certificate that can be used for authenticating to Azure Storage SFTP endpoints.
        This uses Azure AD authentication to generate a certificate similar to 'az ssh cert'.
        The certificate can be used with the 'az sftp connect' command or with standard SFTP clients.
    examples:
        - name: Generate a certificate using an existing public key
          text: az sftp cert --public-key-file ~/.ssh/id_rsa.pub --file ~/my_cert.pub
        - name: Generate a certificate and create a new key pair
          text: az sftp cert --file ~/my_cert.pub
        - name: Generate a certificate with custom SSH client folder
          text: az sftp cert --file ~/my_cert.pub --ssh-client-folder "C:\\Program Files\\OpenSSH"
"""

helps['sftp connect'] = """
    type: command
    short-summary: Connect to Azure Storage Account via SFTP
    long-summary: |
        Establish an SFTP connection to an Azure Storage Account. This command provides two modes:
        1. Fully managed: Run without any credentials and the command will automatically generate
           an SSH certificate and establish the connection.
        2. User-provided credentials: Use your own SSH keys or certificates for authentication.
        
        The command automatically handles Azure Storage SFTP endpoint resolution and authentication.
    examples:
        - name: Connect with automatic certificate generation (fully managed)
          text: az sftp connect --storage-account mystorageaccount
        - name: Connect to storage account with existing certificate
          text: az sftp connect --storage-account mystorageaccount --certificate-file ~/my_cert.pub        - name: Connect with existing SSH key pair
          text: az sftp connect --storage-account mystorageaccount --public-key-file ~/.ssh/id_rsa.pub --private-key-file ~/.ssh/id_rsa
        - name: Connect with custom port
          text: az sftp connect --storage-account mystorageaccount --port 2222
        - name: Connect with additional SFTP arguments
          text: az sftp connect --storage-account mystorageaccount --sftp-args "-v"
        - name: Connect with custom SSH client folder (Windows)
          text: az sftp connect --storage-account mystorageaccount --ssh-client-folder "C:\\Program Files\\OpenSSH"
        - name: Connect in different Azure clouds (automatic hostname resolution)
          text: |
            # The extension automatically resolves hostnames based on Azure cloud:
            # Azure Public: mystorageaccount.blob.core.windows.net
            # Azure China: mystorageaccount.blob.core.chinacloudapi.cn  
            # Azure Government: mystorageaccount.blob.core.usgovcloudapi.net
            az sftp connect --storage-account mystorageaccount
"""
