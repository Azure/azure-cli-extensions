# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

helps['hello world'] = """
    type: command
    short-summary: Say hello world.
"""


helps['vm repair'] = """
    type: group
    short-summary: VM Repair Group
    long-summary: >
        Self repair faulty VMs.
"""

helps['vm repair swap-disk'] = """
    type: command
    short-summary: Disk Swap
    examples:
        - name: Disk Swap a VM
          text: >
            az vm repair swap-disk -g MyResourceGroup -n myVM
"""

helps['vm repair restore-swap'] = """
    type: command
    short-summary: Restore Disk Swap
    examples:
        - name: Restore a Disk Swap a VM
          text: >
            az vm repair restore-swap -g MyResourceGroup -n myVM
"""
