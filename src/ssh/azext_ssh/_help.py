# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

helps['ssh'] = """
    type: group
    short-summary: SSH into resources (Azure VMs, Arc servers, etc) using AAD issued openssh certificates.
"""

helps['ssh vm'] = """
    type: command
    short-summary: SSH into Azure VMs or Arc Servers.
    long-summary: Users can login using AAD issued certificates or using local user credentials. We recommend login using AAD issued certificates. To SSH as a local user in the target machine, you must provide the local user name using the --local-user argument.
    examples:
        - name: Give a resource group and VM to SSH using AAD issued certificates
          text: |
            az ssh vm --resource-group myResourceGroup --vm-name myVM

        - name: Give the public IP (or hostname) of a VM to SSH to SSH using AAD issued certificates
          text: |
            az ssh vm --ip 1.2.3.4
            az ssh vm --hostname example.com

        - name: Using a custom private key file
          text: |
            az ssh vm --ip 1.2.3.4 --private-key-file key --public-key-file key.pub

        - name: Using additional ssh arguments
          text: |
            az ssh vm --ip 1.2.3.4 -- -A -o ForwardX11=yes

        - name: Give the Resource Type of a VM to SSH using AAD issued certificates. Using the resource type is useful when there is an Azure VM and a Arc Server with the same name in the same resource group.
          text: |
            az ssh vm --resource-type Microsoft.Compute --resource-group myResourceGroup --vm-name myVM

        - name: Give a local user name to SSH using local user credentials on the target machine using certificate based authentication.
          text: |
            az ssh vm --local-user username --ip 1.2.3.4 --certificate-file cert.pub --private-key key

        - name: Give a local user name to SSH using local user credentials on the target machine using key based authentication.
          text: |
            az ssh vm --local-user username --resource-group myResourceGroup --vm-name myVM --private-key-file key

        - name: Give a local user name to SSH using local user credentials on the target machine using password based authentication.
          text: |
            az ssh vm --local-user username --resource-group myResourceGroup --vm-name myArcServer
"""

helps['ssh config'] = """
    type: command
    short-summary: Create an SSH config for resources (Azure VMs, etc) which can then be used by clients that support OpenSSH configs and certificates
    long-summary: Other software (git/rsync/etc) that support setting an SSH command can be set to use the config file by setting the command to 'ssh -F /path/to/config' e.g. rsync -e 'ssh -F /path/to/config'
    examples:
        - name: Give a resource group and VM for which to create a config, and save in a local file
          text: |
            az ssh config --resource-group myResourceGroup --vm-name myVm --file ./sshconfig

        - name: Give the public IP (or hostname) of a VM for which to create a config and then ssh
          text: |
            az ssh config --ip 1.2.3.4 --file ./sshconfig
            ssh -F ./sshconfig 1.2.3.4

        - name: Create a generic config for use with any host
          text: |
            #Bash
            az ssh config --ip \\* --file ./sshconfig
            #PowerShell
            az ssh config --ip * --file ./sshconfig

        - name: Examples with other software
          text: |
            #Bash
            az ssh config --ip \\* --file ./sshconfig
            rsync -e 'ssh -F ./sshconfig' -avP directory/ myvm:~/directory
            GIT_SSH_COMMAND="ssh -F ./sshconfig" git clone myvm:~/gitrepo
"""

helps['ssh cert'] = """
    type: command
    short-summary: Create an SSH RSA certificate signed by AAD
    examples:
        - name: Create a short lived ssh certificate signed by AAD
          text: |
            az ssh cert --public-key-file ./id_rsa.pub --file ./id_rsa-aadcert.pub
"""

helps['ssh arc'] = """
    type: command
    short-summary: SSH into Azure Arc Servers
    long-summary: Users can now login using AAD issued certificates or using local user credentials. We recommend login using AAD issued certificates as azure automatically rotate SSH CA keys. To SSH as a local user in the target machine, you must provide the local user name using the --local-user argument.
    examples:
        - name: Give a resource group and Arc Server Name to SSH using AAD issued certificates
          text: |
            az ssh arc --resource-group myResourceGroup --vm-name myArcServer

        - name: Using a custom private key file
          text: |
            az ssh arc --resource-group myResourceGroup --vm-name myArcServer --private-key-file key --public-key-file key.pub

        - name: Give a local user name to SSH to a local user using certificate-based authentication
          text: |
            az ssh arc  --resource-group myResourceGroup --vm-name myArcServer --certificate-file cert.pub --private-key key --local-user name

        - name: Give a local user name to SSH to a local user using key-based authentication
          text: |
            az ssh arc --resource-group myRG --vm-name myVM --local-user name --private-key-file key

        - name: Give a local user name to SSH to a local user using password-based authentication
          text: |
            az ssh arc --resource-group myResourceGroup --vm-name myArcServer --local-user username
"""
