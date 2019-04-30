# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

helps['vm repair'] = """
    type: group
    short-summary: Auto repair commands to fix faulty VMs. Recommended to use all commands with the --verbose flag.
    long-summary: >
        VM repair commands will create a new rescue VM to fix the OS disk of the faulty VM. This is called the 'disk-swap' process. The OS disk of the faulty VM will be copied then attached on the rescue VM's data disk. From the rescue VM, one can diagnose and fix the attached data disk.
"""

helps['vm repair swap-disk'] = """
    type: command
    short-summary: Create a new rescue VM, and attach a copy of the OS disk from the target VM to the rescue VM as a data disk. Recommended to use with the --verbose flag.
    examples:
        - name: Disk Swap a VM
          text: >
            az vm repair swap-disk -g MyResourceGroup -n myVM --verbose
        - name: Disk Swap a VM and set the rescue VM auths
          text: >
            az vm repair swap-disk -g MyResourceGroup -n myVM --rescue-username username --rescue-password password!234 --verbose
"""

helps['vm repair restore-swap'] = """
    type: command
    short-summary: Restore the disk swap by attaching the disk from the rescue VM onto the OS disk of the target VM. All rescue resources will be removed. Recommended to use with the --verbose flag.
    examples:
        - name: Restore a Disk Swap, command will auto-search for rescue-vm
          text: >
            az vm repair restore-swap -g MyResourceGroup -n MyVM --verbose
        - name: Restore a Disk Swap, specify the rescue-vm
          text: >
            az vm repair restore-swap -g MyResourceGroup -n MyVM --rescue-vm-name RescueVM --rescue-resource-group RescueGroup --verbose
        - name: Restore a Disk Swap, specify the rescue-vm and disk to restore
          text: >
            az vm repair restore-swap -g MyResourceGroup -n MyVM --rescue-vm-name RescueVM --rescue-resource-group RescueGroup --disk-name MyDiskCopy --verbose
"""
