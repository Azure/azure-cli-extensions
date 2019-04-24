# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

helps['vm repair'] = """
    type: group
    short-summary: VM Repair Group
    long-summary: >
        Self repair faulty VMs.
"""

helps['vm repair swap-disk'] = """
    type: command
    short-summary: Create a new rescue VM, and attach a copy of the OS disk from the target VM to the rescue VM as a data disk. 
    examples:
        - name: Disk Swap a VM
          text: >
            az vm repair swap-disk -g MyResourceGroup -n myVM
"""

helps['vm repair restore-swap'] = """
    type: command
    short-summary: Attach the data disk from the rescue VM to the target VM as an OS disk. Remove the rescue resources.
    examples:
        - name: Restore a Disk Swap a VM
          text: >
            az vm repair restore-swap -g MyResourceGroup -n myVM --rescue-name rescueVM
"""
