# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

helps['vm repair'] = """
    type: group
    short-summary: Setup repair VMs with copied source OS Disk to resolve issues.
    long-summary: |
        When your VM is non-bootable, VM Repair enables users to setup new repair VMs and copy over the source VM's OS Disk and attach it as a data disk. Then the user can run their own scripts or use [pre-built](https://github.com/Azure/repair-script-library) ones to fix the disk.
"""

helps['vm repair create'] = """
    type: command
    short-summary: Create a new repair VM and attach the source VM's copied OS disk as a data disk.
    examples:
        - name: Create a repair VM
          text: >
            az vm repair create -g MyResourceGroup -n myVM --verbose
        - name: Create a repair VM and set the VM authentication
          text: >
            az vm repair create -g MyResourceGroup -n myVM --repair-username username --repair-password password!234 --verbose
        - name: Create a repair VM of a specific distro or a specific URN could also be provided
          text: >
            az vm repair create -g MyResourceGroup -n myVM --distro 'rhel7|sles12|ubuntu20|centos6|oracle8|sles15'
        - name: Create a repair VM with a Private IP address without any pop up asking for confirmation.
          text: >
            az vm repair create -g MyResourceGroup -n myVM --yes --repair-username <username> --repair-password <password>
        - name: Create a repair VM with a Public IP address without any user input.
          text: >
            az vm repair create -g MyResourceGroup -n myVM --associate-public-ip --yes --repair-username <username> --repair-password <password>
        - name: Create a repair VM with Standard Security type.
          text: >
            az vm repair create -g MyResourceGroup -n myVM --yes --repair-username <username> --repair-password <password> --disable-trusted-launch
        - name: Create a repair VM from a source VM with an encrypted disk. The repair VM is created with the data disk unencrypted and accessible.
          text: >
            az vm repair create -g MyResourceGroup -n myVM --yes --repair-username <username> --repair-password <password> --unlock-encrypted-vm --encrypt-recovery-key <key>
        - name: Create a repair VM with an OS Disk storage type of StandardSSD_LRS.
          text: >
            az vm repair create -g MyResourceGroup -n myVM --yes --repair-username <username> --repair-password <password> --os-disk-type StandardSSD_LRS
"""

helps['vm repair restore'] = """
    type: command
    short-summary: Replace source VM's OS disk with data disk from repair VM.
    examples:
        - name: Restore from the repair VM, command will auto-search for repair-vm
          text: >
            az vm repair restore -g MyResourceGroup -n MyVM --verbose
        - name: Restore from the repair VM, specify the disk to restore
          text: >
            az vm repair restore -g MyResourceGroup -n MyVM --disk-name MyDiskCopy --verbose
"""

helps['vm repair run'] = """
    type: command
    short-summary: Run verified scripts from GitHub on a VM. 'az vm repair list-scripts' to view available scripts.
    examples:
        - name: Run the script with <run-id> directly on the VM.
          text: >
            az vm repair run -g MyResourceGroup -n MySourceWinVM --run-id win-hello-world --verbose
        - name: Run the script with <run-id> on the linked repair VM.
          text: >
            az vm repair run -g MyResourceGroup -n MySourceWinVM --run-id win-hello-world --run-on-repair --verbose
        - name: Run a script with parameters on the VM.
          text: >
            az vm repair run -g MyResourceGroup -n MySourceWinVM --run-id win-hello-world --parameters hello=hi world=earth --verbose
        - name: Run a verified script with some parameters. In the first parameter named 'key', only the value 'test' is sent to the script. The second parameter named \'initiator\', uses the prefix '++' to send the entire following string 'initiator=selfhelp' to the script. 
          text: >
            az vm repair run -g MyResourceGroup -n MySourceWinVM --run-id linux-alar2 --parameters key=test ++initiator=selfhelp --verbose --debug
        - name: Run a local custom script on the VM.
          text: >
            az vm repair run -g MyResourceGroup -n MySourceWinVM --custom-script-file ./file.ps1 --verbose
        - name: Run unverified script from your fork of https://github.com/Azure/repair-script-library
          text: >
            az vm repair run -g MyResourceGroup -n MySourceWinVM --preview "https://github.com/User/repair-script-library/blob/main/map.json" --run-id test
"""

helps['vm repair list-scripts'] = """
    type: command
    short-summary: List available scripts. Located https://github.com/Azure/repair-script-library
    examples:
        - name: List scripts
          text: >
            az vm repair list-scripts --verbose
        - name: List windows scripts only.
          text: >
            az vm repair list-scripts --query "[?starts_with(id, 'win')]"
        - name: List scripts with test in its description.
          text: >
            az vm repair list-scripts --query "[?contains(description, 'test')]"
        - name: List unverified script from your fork of https://github.com/Azure/repair-script-library
          text: >
            az vm repair list-scripts --preview "https://github.com/User/repair-script-library/blob/main/map.json"
"""

helps['vm repair reset-nic'] = """
    type: command
    short-summary: Reset the network interface stack on the VM guest OS. https://learn.microsoft.com/en-us/troubleshoot/azure/virtual-machines/reset-network-interface
    examples:
        - name: Reset the VM guest NIC. Specify VM resource group and name.
          text: >
            az vm repair reset-nic -g MyResourceGroup -n MyVM --verbose
        - name: Reset the VM guest NIC. Specify subscription id, VM resource group and name.
          text: >
            az vm repair reset-nic -g MyResourceGroup -n MyVM --subscription mySub --verbose
        - name: Reset the VM guest NIC and auto-start the VM if it is not in running state.
          text: >
            az vm repair reset-nic -g MyResourceGroup -n MyVM --yes --verbose
"""

helps['vm repair repair-and-restore'] = """
    type: command
    short-summary: Repair and restore the VM.
    examples:
        - name: Repair and restore a VM.
          text: >
            az vm repair repair-and-restore --name vmrepairtest --resource-group MyResourceGroup --verbose
"""
helps['vm repair repair-button'] = """
    type: command
    short-summary: repair button script.
    examples:
        - name: repair-button.
          text: >
            az vm repair repair-button --name vmrepairtest --resource-group MyResourceGroup --button-command fstab --verbose
"""
