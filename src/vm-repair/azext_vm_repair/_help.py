# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

helps['vm repair'] = """
    type: group
    short-summary: Auto repair commands to fix faulty VMs.
    long-summary: |
        When Azure Virtual Machines are faulty, usually they be can't connected using RDP or SSH. To troubleshoot and correct them, the machine's OS disks will be copied and attached to another repair machine to perform repair. VM repair scripts will enable Azure users to self-repair faulty VMs by running simple commands within the Azure CLI.
"""

helps['vm repair swap-disk'] = """
    type: command
    short-summary: Create a new repair VM and attach the faulty VM's copied OS disk as a data disk.
    examples:
        - name: Disk Swap a VM
          text: >
            az vm repair swap-disk -g MyResourceGroup -n myVM --verbose
        - name: Disk Swap a VM and set the repair VM authentication
          text: >
            az vm repair swap-disk -g MyResourceGroup -n myVM --repair-username username --repair-password password!234 --verbose
"""

helps['vm repair restore-swap'] = """
    type: command
    short-summary: Replace faulty VM's OS disk with data disk from repair VM.
    examples:
        - name: Restore a Disk Swap, command will auto-search for repair-vm
          text: >
            az vm repair restore-swap -g MyResourceGroup -n MyVM --verbose
        - name: Restore a Disk Swap, specify the repair-vm
          text: >
            az vm repair restore-swap -g MyResourceGroup -n MyVM --repair-vm-name repairVM --repair-resource-group repairGroup --verbose
        - name: Restore a Disk Swap, specify the repair-vm and disk to restore
          text: >
            az vm repair restore-swap -g MyResourceGroup -n MyVM --repair-vm-name repairVM --repair-resource-group repairGroup --disk-name MyDiskCopy --verbose
"""
