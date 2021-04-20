# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

helps['ssh'] = """
    type: group
    short-summary: SSH into resources (Azure VMs, etc) using AAD issued openssh certificates
"""

helps['ssh vm'] = """
    type: command
    short-summary: SSH into Azure VMs using an ssh certificate
    examples:
        - name: Give a resource group and VM to SSH to
          text: |
            az ssh vm --resource-group myResourceGroup --vm-name myVm
        - name: Give the public IP (or hostname) of a VM to SSH to
          text: |
            az ssh vm --ip 1.2.3.4
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
