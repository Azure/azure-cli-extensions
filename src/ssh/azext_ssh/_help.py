# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

helps['ssh'] = """
    type: group
    short-summary: SSH into Azure VMs
"""

helps['ssh vm'] = """
    type: command
    short-summary: SSH into Azure VMs
    examples:
        - name: Give a resource group and VM to SSH to
          text: |
            az ssh vm --resource-group myResourceGroup --vm-name myVm
        - name: Give the public IP of a VM to SSH to
          text: |
            az ssh vm --ip 1.2.3.4
"""

helps['ssh config'] = """
    type: command
    short-summary: Create an SSH config for Azure VMs which can then be imported to 3rd party SSH clients
    examples:
        - name: Give a resource group and VM for which to create a config, and save in a local file
          text: |
            az ssh config --resource-group myResourceGroup --vm-name myVm --file ./sshconfig
        - name: Give the public IP of a VM for which to create a config
          text: |
            az ssh config --ip 1.2.3.4 --file ./sshconfig
"""
