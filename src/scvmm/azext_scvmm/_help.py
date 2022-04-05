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
    short-summary: Create vmmserver resource
    examples:
      - name: Connect to a vmmserver
        text: |-
                az scvmm vmmserver connect --subscription "Name or ID of the subscription" \
--resource-group "resource group name" --location "location" --custom-location "custom location name" \
--name "vmmserver name" --fqdn "vmmserver FQDN or IP addess" --port "vmmserver port" \
--username "vmmserver user name" --password "vmmserver password"
"""

helps[
    'scvmm vmmserver delete'
] = """
    type: command
    short-summary: "Delete vmmserver resource"
    examples:
      - name: Delete vmmserver resource
        text: |-
                az scvmm vmmserver delete --ids "resource id" --name "vmmserver name" \
--resource-group "resource group name" --subscription "Name or ID of the subscription"
"""

helps[
    'scvmm vmmserver list'
] = """
    type: command
    short-summary: Retrieve a list of vmmservers
    examples:
      - name: Retrieve a list of vmmservers present in a resource group
        text: |-
               az scvmm vmmserver list --subscription "Name or ID of the subscription" \
--resource-group "resource group name"

      - name: Retrieve a list of vmmservers present in a subscription
        text: |-
               az scvmm vmmserver list --subscription "Name or ID of the subscription"
"""

helps[
    'scvmm vmmserver show'
] = """
    type: command
    short-summary: Get details of a vmmserver
    examples:
      - name: Get details of a vmmserver by ARM ID
        text: |-
                az scvmm vmmserver show --ids "resource id"

      - name: Get details of a vmmserver by name
        text: |-
                az scvmm vmmserver show --subscription "Name or ID of the subscription" \
--resource-group "resource group name" --name "vmmserver name"
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
                az scvmm vmmserver inventory-item list --subscription "Name or ID of the subscription" \
--resource-group "resource group name" --vmmserver "name of the vmmserver"
"""

helps[
    'scvmm vmmserver inventory-item show'
] = """
    type: command
    short-summary: Get details of an inventory item present in a vmmserver.
    examples:
      - name: Get details of a inventory item
        text: |-
                az scvmm vmmserver inventory-item show --subscription "Name or ID of the subscription" \
--resource-group "resource group name" --vmmserver "name of the vmmserver" --inventory-item "Inventory Item Name"
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
    short-summary: Create a cloud resource
    examples:
      - name: Create cloud
        text: |-
                az scvmm cloud create --subscription "Name or ID of the subscription" \
--resource-group "resource group name" --location "location" \
--custom-location "custom location name" --vmmserver "name or id of the vmmserver" \
--inventory-item "inventory item name or uuid of the resource in vmm" --name "cloud name"
"""

helps[
    'scvmm cloud delete'
] = """
    type: command
    short-summary: Delete cloud resource
    examples:
      - name: Delete cloud by ARM ID
        text: |-
                az scvmm cloud delete --ids "resource id"

      - name: Delete cloud by name
        text: |-
                az scvmm cloud delete --subscription "Name or ID of the subscription" \
--resource-group "resource group name" --name "cloud name"
"""

helps[
    'scvmm cloud list'
] = """
    type: command
    short-summary: Retrieve a list of clouds
    examples:
      - name: Retrieve a list of clouds present in a resource group
        text: |-
               az scvmm cloud list --subscription "Name or ID of the subscription" \
--resource-group "resource group name"

      - name: Retrieve a list of clouds present in a subscription
        text: |-
               az scvmm cloud list --subscription "Name or ID of the subscription"
"""

helps[
    'scvmm cloud show'
] = """
    type: command
    short-summary: Get details of a cloud
    examples:
      - name: Get details of a cloud by ARM ID
        text: |-
                az scvmm cloud show --ids "resource id"

      - name: Get details of a cloud by name
        text: |-
                az scvmm cloud show --subscription "Name or ID of the subscription" \
--resource-group "resource group name" --name "cloud name"
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
    short-summary: Create a vm-template resource
    examples:
      - name: Create vm-template
        text: |-
                az scvmm vm-template create --subscription "Name or ID of the subscription" \
--resource-group "resource group name" --location "location" \
--custom-location "custom location name" --vmmserver "name or id of the vmmserver" \
--inventory-item "inventory item name or uuid of the resource in vmm" --name "vm-template name"
"""

helps[
    'scvmm vm-template delete'
] = """
    type: command
    short-summary: Delete vm-template resource
    examples:
      - name: Delete vm-template by ARM ID
        text: |-
                az scvmm vm-template delete --ids "resource id"

      - name: Delete vm-template by name
        text: |-
                az scvmm vm-template delete --subscription "Name or ID of the subscription" \
--resource-group "resource group name" --name "vm-template name"
"""

helps[
    'scvmm vm-template list'
] = """
    type: command
    short-summary: Retrieve a list of vm-templates
    examples:
      - name: Retrieve a list of vm-templates present in a resource group
        text: |-
               az scvmm vm-template list --subscription "Name or ID of the subscription" \
--resource-group "resource group name"

      - name: Retrieve a list of vm-templates present in a subscription
        text: |-
               az scvmm vm-template list --subscription "Name or ID of the subscription"
"""

helps[
    'scvmm vm-template show'
] = """
    type: command
    short-summary: Get details of a vm-template
    examples:
      - name: Get details of a vm-template by ARM ID
        text: |-
                az scvmm vm-template show --ids "resource id"

      - name: Get details of a vm-template by name
        text: |-
                az scvmm vm-template show --subscription "Name or ID of the subscription" \
--resource-group "resource group name" --name "vm-template name"
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
    short-summary: Create a virtual-network resource
    examples:
      - name: Create virtual-network
        text: |-
                az scvmm virtual-network create --subscription "Name or ID of the subscription" \
--resource-group "resource group name" --location "location" \
--custom-location "custom location name" --vmmserver "name or id of the vmmserver" \
--inventory-item "inventory item name or uuid of the resource in vmm" --name "virtual-network name"
"""

helps[
    'scvmm virtual-network delete'
] = """
    type: command
    short-summary: Delete virtual-network resource
    examples:
      - name: Delete virtual-network by ARM ID
        text: |-
                az scvmm virtual-network delete --ids "resource id"

      - name: Delete virtual-network by name
        text: |-
                az scvmm virtual-network delete --subscription "Name or ID of the subscription" \
--resource-group "resource group name" --name "virtual-network name"
"""

helps[
    'scvmm virtual-network list'
] = """
    type: command
    short-summary: Retrieve a list of virtual-networks
    examples:
      - name: Retrieve a list of virtual-networks present in a resource group
        text: |-
               az scvmm virtual-network list --subscription "Name or ID of the subscription" \
--resource-group "resource group name"

      - name: Retrieve a list of virtual-networks present in a subscription
        text: |-
               az scvmm virtual-network list --subscription "Name or ID of the subscription"
"""

helps[
    'scvmm virtual-network show'
] = """
    type: command
    short-summary: Get details of a virtual-network
    examples:
      - name: Get details of a virtual-network by ARM ID
        text: |-
                az scvmm virtual-network show --ids "resource id"

      - name: Get details of a virtual-network by name
        text: |-
                az scvmm virtual-network show --subscription "Name or ID of the subscription" \
--resource-group "resource group name" --name "virtual-network name"
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
    short-summary: Create an availabilty set resource
    examples:
      - name: Create an availabilty set
        text: |-
                az scvmm avset create --subscription "Name or ID of the subscription" \
--resource-group "resource group name" --location "location" \
--custom-location "custom location name" --vmmserver "name or id of the vmmserver" \
--avset-name "name of the availability set in vmm" --name "availabilty set name"
"""

helps[
    'scvmm avset delete'
] = """
    type: command
    short-summary: Delete an availabilty set resource
    examples:
      - name: Delete an availabilty set by ARM ID
        text: |-
                az scvmm avset delete --ids "resource id"

      - name: Delete an availabilty set by name
        text: |-
                az scvmm avset delete --subscription "Name or ID of the subscription" \
--resource-group "resource group name" --name "availabilty set name"
"""

helps[
    'scvmm avset list'
] = """
    type: command
    short-summary: Retrieve a list of availabilty sets
    examples:
      - name: Retrieve a list of availabilty sets present in a resource group
        text: |-
               az scvmm avset list --subscription "Name or ID of the subscription" \
--resource-group "resource group name"

      - name: Retrieve a list of availabilty sets present in a subscription
        text: |-
               az scvmm avset list --subscription "Name or ID of the subscription"
"""

helps[
    'scvmm avset show'
] = """
    type: command
    short-summary: Get details of an availabilty set
    examples:
      - name: Get details of an availabilty set by ARM ID
        text: |-
                az scvmm avset show --ids "resource id"

      - name: Get details of an availabilty set by name
        text: |-
                az scvmm avset show --subscription "Name or ID of the subscription" \
--resource-group "resource group name" --name "availabilty set name"
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
    short-summary: Create a VM resource
    examples:
      - name: Enable an exiting VM to azure.
        text: |-
                az scvmm vm create --subscription "Name or ID of the subscription" \
--resource-group "resource group name" --location "location" --custom-location "custom location name" \
--inventory-item "inventory item name or uuid of the resource in vmm" --name "vm name"

      - name: Create a new VM in vmmserver using a VM Template
        text: |-
                az scvmm vm create --subscription "Name or ID of the subscription" \
--resource-group "resource group name" --location "location" \
--custom-location "custom location name" --vm-template "vm-template name" --cloud "cloud name" \
--name "vm name"

      - name: Create a new VM specifying some template overrides
        text: |-
                az scvmm vm create --subscription "Name or ID of the subscription" \
--resource-group "resource group name" --location "location" \
--custom-location "custom location name" --vm-template "vm-template name" --cloud "cloud name" \
--name "vm name" --cpu-count 2 --memory-size 2048 --dynamic-memory-enabled true \
--disk name=disk_1 disk-size=2 bus=0 --nic name=nic_1 network="network name"
"""

helps[
    'scvmm vm delete'
] = """
    type: command
    short-summary: Delete a VM resource
    examples:
      - name: Delete a VM by ARM ID from both azure and VMM
        text: |-
                az scvmm vm delete --ids "resource id"

      - name: Delete a VM by name from both azure and VMM
        text: |-
                az scvmm vm delete --subscription "Name or ID of the subscription" \
--resource-group "resource group name" --name "availabilty set name"

      - name: Disable a VM from azure retaining the actual VM in the VMM infra
        text: |-
                az scvmm vm delete --subscription "Name or ID of the subscription" \
--resource-group "resource group name" --name "availabilty set name" --retain

      - name: Force delete the VM ARM resource
        text: |-
                az scvmm vm delete --subscription "Name or ID of the subscription" \
--resource-group "resource group name" --name "availabilty set name" --force
"""

helps[
    'scvmm vm list'
] = """
    type: command
    short-summary: Retrieve a list of VMs
    examples:
      - name: Retrieve a list of VMs present in a resource group
        text: |-
               az scvmm vm list --subscription "Name or ID of the subscription" \
--resource-group "resource group name"

      - name: Retrieve a list of VMs present in a subscription
        text: |-
               az scvmm vm list --subscription "Name or ID of the subscription"
"""

helps[
    'scvmm vm show'
] = """
    type: command
    short-summary: Get details of an VM
    examples:
      - name: Get details of an VM by ARM ID
        text: |-
                az scvmm vm show --ids "resource id"

      - name: Get details of an VM by name
        text: |-
                az scvmm vm show --subscription "Name or ID of the subscription" \
--resource-group "resource group name" --name "VM name"
"""

helps[
    'scvmm vm start'
] = """
    type: command
    short-summary: Start a VM
    examples:
      - name: Start a vm
        text: |-
               az scvmm vm start --subscription "Name or ID of the subscription" \
--resource-group "resource group name" --name "VM name"
"""

helps[
    'scvmm vm stop'
] = """
    type: command
    short-summary: Stop a VM
    examples:
      - name: Shut down the VM gracefully
        text: |-
               az scvmm vm stop --subscription "Name or ID of the subscription" \
--resource-group "resource group name" --name "VM name"

      - name: Power off the VM
        text: |-
               az scvmm vm stop --subscription "Name or ID of the subscription" \
--resource-group "resource group name" --name "VM name" --skip-shutdown
"""

helps[
    'scvmm vm restart'
] = """
    type: command
    short-summary: Restart a VM
    examples:
      - name: Restart a vm
        text: |-
               az scvmm vm restart --subscription "Name or ID of the subscription" \
--resource-group "resource group name" --name "VM name"
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
      - name: Update vm
        text: |-
               az scvmm vm --subscription "Name or ID of the subscription" \
--resource-group "resource group name" --name "VM name" --cpu-count "no. of CPUs" \
--memory-size "vm memory size in MB" --tags department=Sales
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
      - name: Add a virtual disk to a virtual machine
        text: |-
                az scvmm vm disk add --subscription "Name or ID of the subscription" \
--resource-group "resource group name" --vm-name "VM name" --name "disk name" \
--bus "bus number" --lun "lun number" --disk-size "the disk size in GB"
"""

helps[
    'scvmm vm disk delete'
] = """
    type: command
    short-summary: Delete disks of a virtual machine
    examples:
      - name: Delete disks of a virtual machine
        text: |-
                az scvmm vm disk delete --subscription "Name or ID of the subscription" \
--resource-group "resource group name" --vm-name "VM name" --disks "disk name 1" "disk name 2"
"""

helps[
    'scvmm vm disk list'
] = """
    type: command
    short-summary: Retrieve the list of disks present in a VM
    examples:
      - name: Retrieve the list of disks present in a VM
        text: |-
                az scvmm vm disk list --subscription "Name or ID of the subscription" \
--resource-group "resource group name" --vm-name "VM name"
"""

helps[
    'scvmm vm disk show'
] = """
    type: command
    short-summary: Get the details of a disk present in a VM
    examples:
      - name: Get details of vm disk
        text: |-
                az scvmm vm disk show --subscription "Name or ID of the subscription" \
--resource-group "resource group name" --vm-name "VM name" --name "disk name"
"""

helps[
    'scvmm vm disk update'
] = """
    type: command
    short-summary: Update a disk of a VM
    examples:
      - name: Update a disk of a VM
        text: |-
                az scvmm vm disk show --subscription "Name or ID of the subscription" \
--resource-group "resource group name" --vm-name "VM name" --name "disk name" \
--bus-type "Bus Type" --disk-size "the disk size in GB" --vhd-type "VHD Type of the disk"
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
                az scvmm vm nic add --subscription "Name or ID of the subscription" \
--resource-group "resource group name" --vm-name "VM name" --name "nic name" \
--network "network name" --ipv4-address-type "IPv4 Address Type" \
--mac-address-type "MAC Address Type"
"""

helps[
    'scvmm vm nic delete'
] = """
    type: command
    short-summary: Delete NICs of a virtual machine
    examples:
      - name: Delete NICs of a virtual machine
        text: |-
                az scvmm vm nic delete --subscription "Name or ID of the subscription" \
--resource-group "resource group name" --vm-name "VM name" --nics "nic name 1" "nic name 2"
"""

helps[
    'scvmm vm nic list'
] = """
    type: command
    short-summary: Retrieve the list of NICs present in a VM
    examples:
      - name: Retrieve the list of NICs present in a VM
        text: |-
                az scvmm vm nic list --subscription "Name or ID of the subscription" \
--resource-group "resource group name" --vm-name "VM name"
"""

helps[
    'scvmm vm nic show'
] = """
    type: command
    short-summary: Get the details of a NIC present in a VM
    examples:
      - name: Get details of vm NIC
        text: |-
                az scvmm vm nic show --subscription "Name or ID of the subscription" \
--resource-group "resource group name" --vm-name "VM name" --name "nic name"
"""

helps[
    'scvmm vm nic update'
] = """
    type: command
    short-summary: Update a NIC of a VM
    examples:
      - name: Update a NIC of a VM
        text: |-
                az scvmm vm nic show --subscription "Name or ID of the subscription" \
--resource-group "resource group name" --vm-name "VM name" --name "nic name" \
--network "network name" --ipv4-address-type "IPv4 Address Type" \
--mac-address-type "MAC Address Type"
"""

# endregion
