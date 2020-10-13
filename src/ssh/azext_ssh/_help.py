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
    short-summary: Create an SSH config for resources (Azure VMs, etc) which can then be imported to 3rd party SSH clients
    examples:
        - name: Give a resource group and VM for which to create a config, and save in a local file
          text: |
            az ssh config --resource-group myResourceGroup --vm-name myVm --file ./sshconfig
        - name: Give the public IP (or hostname) of a VM for which to create a config
          text: |
            az ssh config --ip 1.2.3.4 --file ./sshconfig
        - name: Create a generic config for use with any host
          text: |
            #Bash
            az ssh config --ip \\* --file ./sshconfig
            #PowerShell
            az ssh config --ip * --file ./sshconfig
"""

helps['ssh cert'] = """
    type: command
    short-summary: Create an SSH RSA certifcate signed by AAD
    examples:
        - name: Create a short lived ssh certificate signed by AAD
          text: |
            az ssh cert --public-key-file ./id_rsa.pub --file ./id_rsa-aadcert.pub
"""
