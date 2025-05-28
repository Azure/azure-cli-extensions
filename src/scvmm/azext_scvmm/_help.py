# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable= too-many-lines, unused-import

from knack.help_files import helps


helps[
    'scvmm'
] = """
    type: group
    short-summary: Commands for managing Arc for SCVMM resources
"""

# region scvmm vmmserver

helps[
    'scvmm vmmserver'
] = """
    type: group
    short-summary: Manage Arc for SCVMM VMMServer resources
"""

helps[
    'scvmm vmmserver connect'
] = """
    type: command
    short-summary: Create a vmmserver resource
    examples:
      - name: Connect to a vmmserver
        text: |-
                az scvmm vmmserver connect --subscription contoso-sub \
--resource-group contoso-rg --location eastus --custom-location contoso-cl \
--name contoso-vmmserver --fqdn vmm.contoso.com --port 8100 \
--username contoso-user --password contoso-password
"""

helps[
    'scvmm vmmserver update'
] = """
    type: command
    short-summary: Update vmmserver resource
    examples:
      - name: Update a vmmserver by ARM ID
        text: |-
                az scvmm vmmserver update --ids \
/subscriptions/01234567-0123-0123-0123-0123456789ab/resourceGroups/contoso-rg/providers/Microsoft.ScVmm/vmmservers/contoso-vmmserver \
--tags department=Sales

      - name: Update a vmmserver by name
        text: |-
                az scvmm vmmserver update --subscription contoso-sub \
--resource-group contoso-rg --name contoso-vmmserver --tags department=Sales
"""

helps[
    'scvmm vmmserver delete'
] = """
    type: command
    short-summary: Delete a vmmserver resource
    examples:
      - name: Delete a vmmserver resource by Name
        text: |-
                az scvmm vmmserver delete --name contoso-vmmserver \
--resource-group contoso-rg --subscription contoso-sub
      - name: Delete a vmmserver resource by ARM ID
        text: |-
                az scvmm vmmserver delete --ids \
/subscriptions/01234567-0123-0123-0123-0123456789ab/resourceGroups/contoso-rg/providers/Microsoft.ScVmm/vmmServers/contoso-vmmserver
"""

helps[
    'scvmm vmmserver list'
] = """
    type: command
    short-summary: Retrieve a list of vmmservers
    examples:
      - name: Retrieve a list of vmmservers present in a resource group
        text: |-
               az scvmm vmmserver list --subscription contoso-sub \
--resource-group contoso-rg

      - name: Retrieve a list of vmmservers present in a subscription
        text: |-
               az scvmm vmmserver list --subscription contoso-sub
"""

helps[
    'scvmm vmmserver show'
] = """
    type: command
    short-summary: Get details of a vmmserver
    examples:
      - name: Get details of a vmmserver by ARM ID
        text: |-
                az scvmm vmmserver show --ids \
/subscriptions/01234567-0123-0123-0123-0123456789ab/resourceGroups/contoso-rg/providers/Microsoft.ScVmm/vmmServers/contoso-vmmserver

      - name: Get details of a vmmserver by name
        text: |-
                az scvmm vmmserver show --subscription contoso-sub \
--resource-group contoso-rg --name contoso-vmmserver
"""

helps[
    'scvmm vmmserver wait'
] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the vmmserver is met.
"""

helps[
    'scvmm vmmserver inventory-item'
] = """
    type: group
    short-summary: inventory item resource.
"""

helps[
    'scvmm vmmserver inventory-item list'
] = """
    type: command
    short-summary: Retrieve a list of inventory items present in a vmmserver.
    examples:
      - name: Retrieve a list of inventory items
        text: |-
                az scvmm vmmserver inventory-item list --subscription contoso-sub \
--resource-group contoso-rg --vmmserver contoso-vmmserver
"""

helps[
    'scvmm vmmserver inventory-item show'
] = """
    type: command
    short-summary: Get details of an inventory item present in a vmmserver.
    examples:
      - name: Get details of a inventory item
        text: |-
                az scvmm vmmserver inventory-item show --subscription contoso-sub \
--resource-group contoso-rg --vmmserver contoso-vmmserver --inventory-item 01234567-0123-0123-0123-0123456789ab
"""

# endregion

# region scvmm cloud

helps[
    'scvmm cloud'
] = """
    type: group
    short-summary: Manage Arc for SCVMM Cloud resources
"""

helps[
    'scvmm cloud create'
] = """
    type: command
    short-summary: Create cloud resource
    examples:
      - name: Create a cloud
        text: |-
                az scvmm cloud create --subscription contoso-sub \
--resource-group contoso-rg --location eastus \
--custom-location contoso-cl --vmmserver contoso-vmmserver \
--inventory-item 01234567-0123-0123-0123-0123456789ab --name contoso-cloud
"""

helps[
    'scvmm cloud update'
] = """
    type: command
    short-summary: Update cloud resource
    examples:
      - name: Update a cloud by ARM ID
        text: |-
                az scvmm cloud update --ids \
/subscriptions/01234567-0123-0123-0123-0123456789ab/resourceGroups/contoso-rg/providers/Microsoft.ScVmm/clouds/contoso-cloud \
--tags department=Sales

      - name: Update a cloud by name
        text: |-
                az scvmm cloud update --subscription contoso-sub \
--resource-group contoso-rg --name contoso-cloud --tags department=Sales
"""

helps[
    'scvmm cloud delete'
] = """
    type: command
    short-summary: Delete cloud resource
    examples:
      - name: Delete a cloud by ARM ID
        text: |-
                az scvmm cloud delete --ids \
/subscriptions/01234567-0123-0123-0123-0123456789ab/resourceGroups/contoso-rg/providers/Microsoft.ScVmm/clouds/contoso-cloud

      - name: Delete a cloud by name
        text: |-
                az scvmm cloud delete --subscription contoso-sub \
--resource-group contoso-rg --name contoso-cloud
"""

helps[
    'scvmm cloud list'
] = """
    type: command
    short-summary: Retrieve a list of clouds
    examples:
      - name: Retrieve a list of clouds present in a resource group
        text: |-
               az scvmm cloud list --subscription contoso-sub \
--resource-group contoso-rg

      - name: Retrieve a list of clouds present in a subscription
        text: |-
               az scvmm cloud list --subscription contoso-sub
"""

helps[
    'scvmm cloud show'
] = """
    type: command
    short-summary: Get details of a cloud
    examples:
      - name: Get details of a cloud by ARM ID
        text: |-
                az scvmm cloud show --ids \
/subscriptions/01234567-0123-0123-0123-0123456789ab/resourceGroups/contoso-rg/providers/Microsoft.ScVmm/clouds/contoso-cloud

      - name: Get details of a cloud by name
        text: |-
                az scvmm cloud show --subscription contoso-sub \
--resource-group contoso-rg --name contoso-cloud
"""

helps[
    'scvmm cloud wait'
] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the cloud is met.
"""

# endregion

# region scvmm vm-template

helps[
    'scvmm vm-template'
] = """
    type: group
    short-summary: Manage Arc for SCVMM Virtual Machine Template resources
"""

helps[
    'scvmm vm-template create'
] = """
    type: command
    short-summary: Create vm-template resource
    examples:
      - name: Create a vm-template
        text: |-
                az scvmm vm-template create --subscription contoso-sub \
--resource-group contoso-rg --location eastus \
--custom-location contoso-cl --vmmserver contoso-vmmserver \
--inventory-item 01234567-0123-0123-0123-0123456789ab --name contoso-vmtemplate
"""

helps[
    'scvmm vm-template update'
] = """
    type: command
    short-summary: Update vm-template resource
    examples:
      - name: Update a vm-template by ARM ID
        text: |-
                az scvmm vm-template update --ids \
/subscriptions/01234567-0123-0123-0123-0123456789ab/resourceGroups/contoso-rg/providers/Microsoft.ScVmm/virtualMachineTemplates/contoso-vmtemplate \
--tags department=Sales

      - name: Update a vm-template by name
        text: |-
                az scvmm vm-template update --subscription contoso-sub \
--resource-group contoso-rg --name contoso-vmtemplate --tags department=Sales
"""

helps[
    'scvmm vm-template delete'
] = """
    type: command
    short-summary: Delete vm-template resource
    examples:
      - name: Delete a vm-template by ARM ID
        text: |-
                az scvmm vm-template delete --ids \
/subscriptions/01234567-0123-0123-0123-0123456789ab/resourceGroups/contoso-rg/providers/Microsoft.ScVmm/virtualMachineTemplates/contoso-vmtemplate

      - name: Delete a vm-template by name
        text: |-
                az scvmm vm-template delete --subscription contoso-sub \
--resource-group contoso-rg --name contoso-vmtemplate
"""

helps[
    'scvmm vm-template list'
] = """
    type: command
    short-summary: Retrieve a list of vm-templates
    examples:
      - name: Retrieve a list of vm-templates present in a resource group
        text: |-
               az scvmm vm-template list --subscription contoso-sub \
--resource-group contoso-rg

      - name: Retrieve a list of vm-templates present in a subscription
        text: |-
               az scvmm vm-template list --subscription contoso-sub
"""

helps[
    'scvmm vm-template show'
] = """
    type: command
    short-summary: Get details of a vm-template
    examples:
      - name: Get details of a vm-template by ARM ID
        text: |-
                az scvmm vm-template show --ids \
/subscriptions/01234567-0123-0123-0123-0123456789ab/resourceGroups/contoso-rg/providers/Microsoft.ScVmm/virtualMachineTemplates/contoso-vmtemplate

      - name: Get details of a vm-template by name
        text: |-
                az scvmm vm-template show --subscription contoso-sub \
--resource-group contoso-rg --name contoso-vmtemplate
"""

helps[
    'scvmm vm-template wait'
] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the vm-template is met.
"""

# endregion

# region scvmm virtual-network

helps[
    'scvmm virtual-network'
] = """
    type: group
    short-summary: Manage Arc for SCVMM Virtual Network resources
"""

helps[
    'scvmm virtual-network create'
] = """
    type: command
    short-summary: Create virtual-network resource
    examples:
      - name: Create a virtual-network
        text: |-
                az scvmm virtual-network create --subscription contoso-sub \
--resource-group contoso-rg --location eastus \
--custom-location contoso-cl --vmmserver contoso-vmmserver \
--inventory-item 01234567-0123-0123-0123-0123456789ab --name contoso-vnet
"""

helps[
    'scvmm virtual-network update'
] = """
    type: command
    short-summary: Update virtual-network resource
    examples:
      - name: Update a virtual-network by ARM ID
        text: |-
                az scvmm virtual-network update --ids \
/subscriptions/01234567-0123-0123-0123-0123456789ab/resourceGroups/contoso-rg/providers/Microsoft.ScVmm/virtualNetworks/contoso-vnet \
--tags department=Sales

      - name: Update a virtual-network by name
        text: |-
                az scvmm virtual-network update --subscription contoso-sub \
--resource-group contoso-rg --name contoso-vnet --tags department=Sales
"""

helps[
    'scvmm virtual-network delete'
] = """
    type: command
    short-summary: Delete virtual-network resource
    examples:
      - name: Delete a virtual-network by ARM ID
        text: |-
                az scvmm virtual-network delete --ids \
/subscriptions/01234567-0123-0123-0123-0123456789ab/resourceGroups/contoso-rg/providers/Microsoft.ScVmm/virtualNetworks/contoso-vnet

      - name: Delete a virtual-network by name
        text: |-
                az scvmm virtual-network delete --subscription contoso-sub \
--resource-group contoso-rg --name contoso-vnet
"""

helps[
    'scvmm virtual-network list'
] = """
    type: command
    short-summary: Retrieve a list of virtual-networks
    examples:
      - name: Retrieve a list of virtual-networks present in a resource group
        text: |-
               az scvmm virtual-network list --subscription contoso-sub \
--resource-group contoso-rg

      - name: Retrieve a list of virtual-networks present in a subscription
        text: |-
               az scvmm virtual-network list --subscription contoso-sub
"""

helps[
    'scvmm virtual-network show'
] = """
    type: command
    short-summary: Get details of a virtual-network
    examples:
      - name: Get details of a virtual-network by ARM ID
        text: |-
                az scvmm virtual-network show --ids \
/subscriptions/01234567-0123-0123-0123-0123456789ab/resourceGroups/contoso-rg/providers/Microsoft.ScVmm/virtualNetworks/contoso-vnet

      - name: Get details of a virtual-network by name
        text: |-
                az scvmm virtual-network show --subscription contoso-sub \
--resource-group contoso-rg --name contoso-vnet
"""

helps[
    'scvmm virtual-network wait'
] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the virtual-network is met.
"""

# endregion

# region scvmm availabilty set

helps[
    'scvmm avset'
] = """
    type: group
    short-summary: Manage Arc for SCVMM Availability Set resources
"""

helps[
    'scvmm avset create'
] = """
    type: command
    short-summary: Create availabilty set resource
    examples:
      - name: Create an availabilty set
        text: |-
                az scvmm avset create --subscription contoso-sub \
--resource-group contoso-rg --location eastus \
--custom-location contoso-cl --vmmserver contoso-vmmserver \
--avset-name "name of the availability set in vmm" --name contoso-avset
"""

helps[
    'scvmm avset update'
] = """
    type: command
    short-summary: Update availabilty set resource
    examples:
      - name: Update an availabilty set by ARM ID
        text: |-
                az scvmm avset update --ids \
/subscriptions/01234567-0123-0123-0123-0123456789ab/resourceGroups/contoso-rg/providers/Microsoft.ScVmm/availabiltySets/contoso-avset \
--tags department=Sales

      - name: Update an availabilty set by name
        text: |-
                az scvmm avset update --subscription contoso-sub \
--resource-group contoso-rg --name contoso-avset --tags department=Sales
"""


helps[
    'scvmm avset delete'
] = """
    type: command
    short-summary: Delete availabilty set resource
    examples:
      - name: Delete an availabilty set by ARM ID
        text: |-
                az scvmm avset delete --ids \
/subscriptions/01234567-0123-0123-0123-0123456789ab/resourceGroups/contoso-rg/providers/Microsoft.ScVmm/availabiltySets/contoso-avset

      - name: Delete an availabilty set by name
        text: |-
                az scvmm avset delete --subscription contoso-sub \
--resource-group contoso-rg --name contoso-avset
"""

helps[
    'scvmm avset list'
] = """
    type: command
    short-summary: Retrieve a list of availabilty sets
    examples:
      - name: Retrieve a list of availabilty sets present in a resource group
        text: |-
               az scvmm avset list --subscription contoso-sub \
--resource-group contoso-rg

      - name: Retrieve a list of availabilty sets present in a subscription
        text: |-
               az scvmm avset list --subscription contoso-sub
"""

helps[
    'scvmm avset show'
] = """
    type: command
    short-summary: Get details of an availabilty set
    examples:
      - name: Get details of an availabilty set by ARM ID
        text: |-
                az scvmm avset show --ids \
/subscriptions/01234567-0123-0123-0123-0123456789ab/resourceGroups/contoso-rg/providers/Microsoft.ScVmm/availabiltySets/contoso-avset

      - name: Get details of an availabilty set by name
        text: |-
                az scvmm avset show --subscription contoso-sub \
--resource-group contoso-rg --name contoso-avset
"""

helps[
    'scvmm avset wait'
] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the availability set is met.
"""

# endregion

# region virtual machine

helps[
    'scvmm vm'
] = """
    type: group
    short-summary: Manage Arc for SCVMM Virtual Machine resources
"""

helps[
    'scvmm vm create'
] = """
    type: command
    short-summary: Create VM resource
    examples:
      - name: Enable an exiting VM to azure.
        text: |-
                az scvmm vm create --subscription contoso-sub \
--resource-group contoso-rg --location eastus --custom-location contoso-cl \
--inventory-item 01234567-0123-0123-0123-0123456789ab --name contoso-vm

      - name: Create a new VM in vmmserver using a VM Template
        text: |-
                az scvmm vm create --subscription contoso-sub \
--resource-group contoso-rg --location eastus \
--custom-location contoso-cl --vm-template contoso-vmtemplate --cloud contoso-cloud \
--name contoso-vm

      - name: Create a new VM specifying some template overrides
        text: |-
                az scvmm vm create --subscription contoso-sub \
--resource-group contoso-rg --location eastus \
--custom-location contoso-cl --vm-template contoso-vmtemplate --cloud contoso-cloud \
--name contoso-vm --cpu-count 2 --memory-size 2048 --dynamic-memory-enabled true \
--disk name=disk_1 disk-size=2 bus=0 --nic name=nic_1 network=contoso-vnet
"""

helps[
    'scvmm vm delete'
] = """
    type: command
    short-summary: Delete VM resource
    examples:
      - name: Delete a VM by ARM ID from both azure and VMM
        text: |-
                az scvmm vm delete --ids \
/subscriptions/01234567-0123-0123-0123-0123456789ab/resourceGroups/contoso-rg/providers/Microsoft.ScVmm/virtualMachines/contoso-vm

      - name: Delete a VM by name from both azure and VMM
        text: |-
                az scvmm vm delete --subscription contoso-sub \
--resource-group contoso-rg --name contoso-avset

      - name: Disable a VM from azure retaining the actual VM in the VMM infra
        text: |-
                az scvmm vm delete --subscription contoso-sub \
--resource-group contoso-rg --name contoso-avset --retain

      - name: Force delete the VM ARM resource
        text: |-
                az scvmm vm delete --subscription contoso-sub \
--resource-group contoso-rg --name contoso-avset --force

      - name: Delete the VM from SCVMM
        text: |-
                az scvmm vm delete --subscription contoso-sub \
--resource-group contoso-rg --name contoso-avset --deleteFromHost
"""

helps[
    'scvmm vm list'
] = """
    type: command
    short-summary: Retrieve a list of VMs
    examples:
      - name: Retrieve a list of VMs present in a resource group
        text: |-
               az scvmm vm list --subscription contoso-sub \
--resource-group contoso-rg

      - name: Retrieve a list of VMs present in a subscription
        text: |-
               az scvmm vm list --subscription contoso-sub
"""

helps[
    'scvmm vm show'
] = """
    type: command
    short-summary: Get details of an VM
    examples:
      - name: Get details of an VM by ARM ID
        text: |-
                az scvmm vm show --ids \
/subscriptions/01234567-0123-0123-0123-0123456789ab/resourceGroups/contoso-rg/providers/Microsoft.ScVmm/virtualMachines/contoso-vm

      - name: Get details of an VM by name
        text: |-
                az scvmm vm show --subscription contoso-sub \
--resource-group contoso-rg --name contoso-vm
"""

helps[
    'scvmm vm start'
] = """
    type: command
    short-summary: Start a VM
    examples:
      - name: Start a vm
        text: |-
               az scvmm vm start --subscription contoso-sub \
--resource-group contoso-rg --name contoso-vm
"""

helps[
    'scvmm vm stop'
] = """
    type: command
    short-summary: Stop a VM
    examples:
      - name: Shut down the VM gracefully
        text: |-
               az scvmm vm stop --subscription contoso-sub \
--resource-group contoso-rg --name contoso-vm

      - name: Power off the VM
        text: |-
               az scvmm vm stop --subscription contoso-sub \
--resource-group contoso-rg --name contoso-vm --skip-shutdown
"""

helps[
    'scvmm vm restart'
] = """
    type: command
    short-summary: Restart a VM
    examples:
      - name: Restart a vm
        text: |-
               az scvmm vm restart --subscription contoso-sub \
--resource-group contoso-rg --name contoso-vm
"""

helps[
    'scvmm vm create-checkpoint'
] = """
    type: command
    short-summary: Create a VM checkpoint
    examples:
      - name: Create VM checkpoint
        text: |-
               az scvmm vm create-checkpoint --subscription contoso-sub \
--resource-group contoso-rg --name contoso-vm --checkpoint-name contoso-chkpt-name \
--checkpoint-description contoso-chkpt-description
"""

helps[
    'scvmm vm delete-checkpoint'
] = """
    type: command
    short-summary: Delete the specified VM checkpoint
    examples:
      - name: Delete VM checkpoint
        text: |-
               az scvmm vm delete-checkpoint --subscription contoso-sub \
--resource-group contoso-rg --name contoso-vm --checkpoint-id checkpoint-guid
"""

helps[
    'scvmm vm restore-checkpoint'
] = """
    type: command
    short-summary: Restore VM checkpoint
    examples:
      - name: Restore VM checkpoint
        text: |-
               az scvmm vm restore-checkpoint --subscription contoso-sub \
--resource-group contoso-rg --name contoso-vm --checkpoint-id checkpoint-guid
"""

helps[
    'scvmm vm update'
] = """
    type: command
    short-summary: |-
                      Update a VM. \
Management of VM disks and NICs are not using this subcommand. \
There are separate subcommands for the same.
    examples:
      - name: Update a VM to have 2 vCPUs and 4GB Memory.
        text: |-
               az scvmm vm update --subscription contoso-sub \
--resource-group contoso-rg --name contoso-vm --cpu-count 2 \
--memory-size 4096 --tags department=Sales
"""

helps[
    'scvmm vm wait'
] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the vm is met.
"""

# endregion

# region vm disk

helps[
    'scvmm vm disk'
] = """
    type: group
    short-summary: Managing the Disks of Arc for SCVMM Virtual Machine
"""

helps[
    'scvmm vm disk add'
] = """
    type: command
    short-summary: Add a virtual disk to a virtual machine
    examples:
      - name: |-
                Create a virtual disk with size 100 GB to a virtual machine \
and attach it to Bus 1 Lun 10 SCSI controller.
        text: |-
                az scvmm vm disk add --subscription contoso-sub \
--resource-group contoso-rg --vm-name contoso-vm --name disk_2 \
--bus 1 --lun 10 --bus-type SCSI --disk-size 100
"""

helps[
    'scvmm vm disk delete'
] = """
    type: command
    short-summary: Delete disks of a virtual machine
    examples:
      - name: Delete disks of a virtual machine
        text: |-
                az scvmm vm disk delete --subscription contoso-sub \
--resource-group contoso-rg --vm-name contoso-vm --disks disk_1 disk_2
"""

helps[
    'scvmm vm disk list'
] = """
    type: command
    short-summary: Retrieve the list of disks present in a VM
    examples:
      - name: Retrieve the list of disks present in a VM
        text: |-
                az scvmm vm disk list --subscription contoso-sub \
--resource-group contoso-rg --vm-name contoso-vm
"""

helps[
    'scvmm vm disk show'
] = """
    type: command
    short-summary: Get the details of a disk present in a VM
    examples:
      - name: Get details of vm disk
        text: |-
                az scvmm vm disk show --subscription contoso-sub \
--resource-group contoso-rg --vm-name contoso-vm --name disk_1
"""

helps[
    'scvmm vm disk update'
] = """
    type: command
    short-summary: Update a disk of a VM
    examples:
      - name: Update a disk of a VM
        text: |-
                az scvmm vm disk update --subscription contoso-sub \
--resource-group contoso-rg --vm-name contoso-vm --name disk_1 \
--bus-type IDE --bus 0 --disk-size 40 --vhd-type Dynamic
"""

helps[
    'scvmm vm disk wait'
] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the vm disk is met.
"""

# endregion

# region vm nic

helps[
    'scvmm vm nic'
] = """
    type: group
    short-summary: Managing the NICs of Arc for SCVMM Virtual Machine
"""

helps[
    'scvmm vm nic add'
] = """
    type: command
    short-summary: Add a network interface card to a virtual machine
    examples:
      - name: Add a NIC to a virtual machine
        text: |-
                az scvmm vm nic add --subscription contoso-sub \
--resource-group contoso-rg --vm-name contoso-vm --name nic_1 \
--network contoso-vnet --ipv4-address-type Dynamic \
--mac-address-type Dynamic
"""

helps[
    'scvmm vm nic delete'
] = """
    type: command
    short-summary: Delete NICs of a virtual machine
    examples:
      - name: Delete NICs of a virtual machine
        text: |-
                az scvmm vm nic delete --subscription contoso-sub \
--resource-group contoso-rg --vm-name contoso-vm --nics nic_1 nic_2
"""

helps[
    'scvmm vm nic list'
] = """
    type: command
    short-summary: Retrieve the list of NICs present in a VM
    examples:
      - name: Retrieve the list of NICs present in a VM
        text: |-
                az scvmm vm nic list --subscription contoso-sub \
--resource-group contoso-rg --vm-name contoso-vm
"""

helps[
    'scvmm vm nic show'
] = """
    type: command
    short-summary: Get the details of a NIC present in a VM
    examples:
      - name: Get details of vm NIC
        text: |-
                az scvmm vm nic show --subscription contoso-sub \
--resource-group contoso-rg --vm-name contoso-vm --name nic_1
"""

helps[
    'scvmm vm nic update'
] = """
    type: command
    short-summary: Update a NIC of a VM
    examples:
      - name: Update a NIC of a VM
        text: |-
                az scvmm vm nic update --subscription contoso-sub \
--resource-group contoso-rg --vm-name contoso-vm --name nic_1 \
--network contoso-vnet --ipv4-address-type Dynamic \
--mac-address-type Dynamic
"""

helps[
    'scvmm vm nic wait'
] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the vm nic is met.
"""

# endregion

# region vm guest-agent

helps[
    'scvmm vm guest-agent'
] = """
    type: group
    short-summary: vm guest agent.
"""

helps[
    'scvmm vm guest-agent enable'
] = """
    type: command
    short-summary: "Enable guest agent on the vm"
    examples:
      - name: Enable guest agent on the vm
        text: |-
               az scvmm vm guest-agent enable --username contoso-user --password contoso-pass \
               --resource-group contoso-rg --subscription contoso-sub \
               --vm-name contoso-vm
"""

helps[
    'scvmm vm guest-agent show'
] = """
    type: command
    short-summary: "Get details of a guest agent by guest agent name, resource-group and vm name."
    examples:
      - name: Get details of a guest agent
        text: |-
               az scvmm vm guest-agent show --resource-group contoso-rg \
               --vm-name contoso-vm
"""

# endregion

# region vm extension

helps['scvmm vm extension'] = """
    type: group
    short-summary: Manage vm extension with scvmm
"""

helps['scvmm vm extension list'] = """
    type: command
    short-summary: "The operation to get all extensions of a non-Azure vm."
    examples:
      - name: Get all VM Extensions
        text: |-
               az scvmm vm extension list --vm-name contoso-vm --resource-group contoso-rg
"""

helps['scvmm vm extension show'] = """
    type: command
    short-summary: "The operation to get the extension."
    examples:
      - name: Get VM Extension
        text: |-
               az scvmm vm extension show --name contoso-extension --vm-name contoso-vm \
--resource-group contoso-rg
"""

helps['scvmm vm extension create'] = """
    type: command
    short-summary: "The operation to create the extension."
    examples:
      - name: Create a VM Extension
        text: |-
               az scvmm vm extension create --name contoso-extension --location eastus2euap --type \
CustomScriptExtension --publisher Microsoft.Compute --settings "{\\"commandToExecute\\":\\"powershell.exe -c \
\\\\\\"Get-Process | Where-Object { $_.CPU -gt 10000 }\\\\\\"\\"}" --type-handler-version 1.10 --vm-name \
contoso-vm --resource-group contoso-rg
"""

helps['scvmm vm extension update'] = """
    type: command
    short-summary: "The operation to update the extension."
    examples:
      - name: Update a VM Extension
        text: |-
               az scvmm vm extension update --name contoso-extension --type CustomScriptExtension \
--publisher Microsoft.Compute --settings "{\\"commandToExecute\\":\\"powershell.exe -c \\\\\\"Get-Process | \
Where-Object { $_.CPU -lt 100 }\\\\\\"\\"}" --type-handler-version 1.10 --vm-name contoso-vm --resource-group \
contoso-rg
"""

helps['scvmm vm extension delete'] = """
    type: command
    short-summary: "The operation to delete the extension."
    examples:
      - name: Delete a VM Extension
        text: |-
               az scvmm vm extension delete --name contoso-extension --vm-name contoso-vm --resource-group \
contoso-rg
"""

# endregion
