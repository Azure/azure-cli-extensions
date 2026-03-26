# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

helps['ssh'] = """
    type: group
    short-summary: SSH into resources (Azure VMs, Arc servers, etc) using AAD issued openssh certificates.
    long-summary: SSH into Arc-enabled servers without requiring a public IP address or SSH into Azure Virtual Machines. AAD issued openssh certificates for authentication currently only supported for Linux.
"""

helps['ssh vm'] = """
    type: command
    short-summary: SSH into Azure VMs or Arc Servers.
    long-summary: Users can login using AAD issued certificates or using local user credentials. We recommend login using AAD issued certificates. To SSH using local user credentials, you must provide the local user name using the --local-user parameter.
    examples:
        - name: Give a resource group name and machine name to SSH using AAD issued certificates
          text: |
            az ssh vm --resource-group myResourceGroup --name myVM

        - name: Give the public IP (or hostname) of a VM to SSH using AAD issued certificates
          text: |
            az ssh vm --ip 1.2.3.4
            az ssh vm --hostname example.com

        - name: Using a custom private key file
          text: |
            az ssh vm --ip 1.2.3.4 --private-key-file key --public-key-file key.pub

        - name: Using additional ssh arguments
          text: |
            az ssh vm --ip 1.2.3.4 -- -A -o ForwardX11=yes

        - name: Give the Resource Type of the target. Useful when there is an Azure VM and an Arc Server with the same name in the same resource group. Resource type can be either "Microsoft.HybridCompute" for Arc Servers or "Microsoft.Compute" for Azure Virtual Machines.
          text: |
            az ssh vm --resource-type [Microsoft.Compute/virtualMachines|Microsoft.HybridCompute/machines] --resource-group myResourceGroup --name myVM

        - name: Give a local user name to SSH with local user credentials using certificate based authentication.
          text: |
            az ssh vm --local-user username --ip 1.2.3.4 --certificate-file cert.pub --private-key-file key

        - name: Give a local user name to SSH with local user credentials using key based authentication.
          text: |
            az ssh vm --local-user username --resource-group myResourceGroup --name myVM --private-key-file key

        - name: Give a local user name to SSH with local user credentials using password based authentication.
          text: |
            az ssh vm --local-user username --resource-group myResourceGroup --name myArcServer

        - name: Give a SSH Client Folder to use the ssh executables in that folder, like ssh-keygen.exe and ssh.exe. If not provided, the extension attempts to use pre-installed OpenSSH client (on Windows, extension looks for pre-installed executables under C:\\Windows\\System32\\OpenSSH).
          text: |
            az ssh vm --resource-group myResourceGroup --name myVM --ssh-client-folder "C:\\Program Files\\OpenSSH"

        - name: Open RDP connection over SSH. Useful for connecting via RDP to Arc Servers with no public IP address. Currently only supported for Windows clients.
          text: |
            az ssh vm --resource-group myResourceGroup --name myVM --local-user username --rdp
"""

helps['ssh config'] = """
    type: command
    short-summary: Create an SSH config for resources (Azure VMs, Arc Servers, etc) which can then be used by clients that support OpenSSH configs and certificates
    long-summary: Other software (git/rsync/etc) that support setting an SSH command can be set to use the config file by setting the command to 'ssh -F /path/to/config' e.g. rsync -e 'ssh -F /path/to/config'.  Users can create ssh config files that use AAD issued certificates or local user credentials.
    examples:
        - name: Give the resource group and machine name for which to create a config using AAD issued certificates, save in a local file, and then ssh into that resource
          text: |
            az ssh config --resource-group myResourceGroup --name myVm --file ./sshconfig
            ssh -F ./sshconfig myResourceGroup-myVM

        - name: Give the public IP (or hostname) of an Azure VM for which to create a config and then ssh into that VM
          text: |
            az ssh config --ip 1.2.3.4 --file ./sshconfig
            ssh -F ./sshconfig 1.2.3.4

        - name: Give a local user to create a config using local user credentials, save in local file, and then ssh into that resource
          text: |
            az ssh config --resource-group myResourceGroup --name myMachine --local-user username --certificate-file cert --private-key-file key --file ./sshconfig
            ssh -F ./sshconfig MyResourceGroup-myMachine-username

        - name: Give Keys Destination Folder to store the generated keys and certificates. If not provided, SSH keys are stored in new folder "az_ssh_config" next to the config file.
          text: |
            az ssh config --ip 1.2.3.4 --file ./sshconfig --keys-destination-folder /home/user/mykeys

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

        - name: Give a SSH Client Folder to use the ssh executables in that folder, like ssh-keygen.exe. If not provided, the extension attempts to use pre-installed OpenSSH client (on Windows, extension looks for pre-installed executables under C:\\Windows\\System32\\OpenSSH).
          text: |
            az ssh config --file ./myconfig --resource-group myResourceGroup --name myVM --ssh-client-folder "C:\\Program Files\\OpenSSH"

        - name: Give the Resource Type of the target. Useful when there is an Azure VM and an Arc Server with the same name in the same resource group. Resource type can be either "Microsoft.HybridCompute" for Arc Servers or "Microsoft.Compute" for Azure Virtual Machines.
          text: |
            az ssh config --resource-type [Microsoft.Compute/virtualMachines|Microsoft.HybridCompute/machines] --resource-group myResourceGroup --name myVM --file ./myconfig
"""

helps['ssh cert'] = """
    type: command
    short-summary: Create an SSH RSA certificate signed by AAD
    examples:
        - name: Create a short lived ssh certificate signed by AAD
          text: |
            az ssh cert --public-key-file ./id_rsa.pub --file ./id_rsa-aadcert.pub
        - name: Give a SSH Client Folder to use the ssh executables in that folder, like ssh-keygen.exe. If not provided, the extension attempts to use pre-installed OpenSSH client (on Windows, extension looks for pre-installed executables under C:\\Windows\\System32\\OpenSSH).
          text: |
            az ssh cert --file ./id_rsa-aadcert.pub --ssh-client-folder "C:\\Program Files\\OpenSSH"
"""

helps['ssh arc'] = """
    type: command
    short-summary: SSH into Azure Arc Servers
    long-summary: Users can login using AAD issued certificates or using local user credentials. We recommend login using AAD issued certificates. To SSH using local user credentials you must provide the local user name using the --local-user parameter.
    examples:
        - name: Give a resource group name and machine name to SSH using AAD issued certificates
          text: |
            az ssh arc --resource-group myResourceGroup --name myMachine

        - name: Using a custom private key file
          text: |
            az ssh arc --resource-group myResourceGroup --name myMachine --private-key-file key --public-key-file key.pub

        - name: Using additional ssh arguments
          text: |
            az ssh arc --resource-group myResourceGroup --name myMachine -- -A -o ForwardX11=yes

        - name: Give a local user name to SSH with local user credentials using certificate based authentication.
          text: |
            az ssh arc --local-user username --resource-group myResourceGroup --name myMachine --certificate-file cert.pub --private-key-file key

        - name: Give a local user name to SSH with local user credentials using key based authentication.
          text: |
            az ssh arc --local-user username --resource-group myResourceGroup --name myMachine --private-key-file key

        - name: Give a local user name to SSH with local user credentials using password based authentication.
          text: |
            az ssh arc --local-user username --resource-group myResourceGroup --name myMachine

        - name: Give a SSH Client Folder to use the ssh executables in that folder, like ssh-keygen.exe and ssh.exe. If not provided, the extension attempts to use pre-installed OpenSSH client (on Windows, extension looks for pre-installed executables under C:\\Windows\\System32\\OpenSSH).
          text: |
            az ssh arc --resource-group myResourceGroup --name myMachine --ssh-client-folder "C:\\Program Files\\OpenSSH"

        - name: Open RDP connection over SSH. Useful for connecting via RDP to Arc Servers with no public IP address. Currently only supported for Windows clients.
          text: |
            az ssh arc --resource-group myResourceGroup --name myVM --local-user username --rdp
"""
