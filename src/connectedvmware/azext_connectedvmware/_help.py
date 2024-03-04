# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable= too-many-lines, unused-import

from knack.help_files import helps


helps[
    'connectedvmware'
] = """
    type: group
    short-summary: Commands to manage Connected VMware.
"""

helps[
    'connectedvmware resource-pool'
] = """
    type: group
    short-summary: resource pool resource
"""

helps[
    'connectedvmware resource-pool create'
] = """
    type: command
    short-summary: "Create a resource pool resource"
    examples:
      - name: Create resource pool
        text: |-
               az connectedvmware resource-pool create --custom-location "custom location name" \
               --location "location name" --inventory-item "name or id the inventory item" \
               --name "resource pool name" --resource-group "resource group name" \
               --vcenter "name or id of the vcenter"
"""

helps[
    'connectedvmware resource-pool delete'
] = """
    type: command
    short-summary: "Delete resource pool resource"
    examples:
      - name: Delete resource pool
        text: |-
               az connectedvmware resource-pool delete --ids "resource id" --name "resource pool name" \
               --resource-group "resource group name" --subscription "Name or ID of subscription"
"""

helps[
    'connectedvmware resource-pool list'
] = """
    type: command
    short-summary: "Retrieve a list of resource pool of given resource group"
    examples:
      - name: Retrieve a list of resource pool
        text: |-
               az connectedvmware resource-pool list --resource-group "resource group name"
"""

helps[
    'connectedvmware resource-pool show'
] = """
    type: command
    short-summary: "Get details of a resource pool by id, resource-group, resource pool name, or subscription"
    examples:
      - name: Get details of a resource pool
        text: |-
               az connectedvmware resource-pool show --ids "resource id" --name "resource pool name" \
               --resource-group "resource group name" --subscription "Name or ID of subscription"
"""

helps[
    'connectedvmware cluster'
] = """
    type: group
    short-summary: cluster resource
"""

helps[
    'connectedvmware cluster create'
] = """
    type: command
    short-summary: "Create a cluster resource"
    examples:
      - name: Create cluster
        text: |-
               az connectedvmware cluster create --custom-location "custom location name" \
               --location "location name" --inventory-item "name or id the inventory item" \
               --name "cluster name" --resource-group "resource group name" \
               --vcenter "name or id of the vcenter"
"""

helps[
    'connectedvmware cluster delete'
] = """
    type: command
    short-summary: "Delete cluster resource"
    examples:
      - name: Delete cluster
        text: |-
               az connectedvmware cluster delete --ids "resource id" --name "cluster name" \
               --resource-group "resource group name" --subscription "Name or ID of subscription"
"""

helps[
    'connectedvmware cluster list'
] = """
    type: command
    short-summary: "Retrieve a list of cluster of given resource group"
    examples:
      - name: Retrieve a list of cluster
        text: |-
               az connectedvmware cluster list --resource-group "resource group name"
"""

helps[
    'connectedvmware cluster show'
] = """
    type: command
    short-summary: "Get details of a cluster by id, resource-group, cluster name, or subscription"
    examples:
      - name: Get details of a cluster
        text: |-
               az connectedvmware cluster show --ids "resource id" --name "cluster name" \
               --resource-group "resource group name" --subscription "Name or ID of subscription"
"""

helps[
    'connectedvmware datastore'
] = """
    type: group
    short-summary: datastore resource
"""

helps[
    'connectedvmware datastore create'
] = """
    type: command
    short-summary: "Create a datastore resource"
    examples:
      - name: Create datastore
        text: |-
               az connectedvmware datastore create --custom-location "custom location name" \
               --location "location name" --inventory-item "name or id the inventory item" \
               --name "datastore name" --resource-group "resource group name" \
               --vcenter "name or id of the vcenter"
"""

helps[
    'connectedvmware datastore delete'
] = """
    type: command
    short-summary: "Delete datastore resource"
    examples:
      - name: Delete datastore
        text: |-
               az connectedvmware datastore delete --ids "resource id" --name "datastore name" \
               --resource-group "resource group name" --subscription "Name or ID of subscription"
"""

helps[
    'connectedvmware datastore list'
] = """
    type: command
    short-summary: "Retrieve a list of datastore of given resource group"
    examples:
      - name: Retrieve a list of datastore
        text: |-
               az connectedvmware datastore list --resource-group "resource group name"
"""

helps[
    'connectedvmware datastore show'
] = """
    type: command
    short-summary: "Get details of a datastore by id, resource-group, datastore name, or subscription"
    examples:
      - name: Get details of a datastore
        text: |-
               az connectedvmware datastore show --ids "resource id" --name "datastore name" \
               --resource-group "resource group name" --subscription "Name or ID of subscription"
"""

helps[
    'connectedvmware host'
] = """
    type: group
    short-summary: host resource
"""

helps[
    'connectedvmware host create'
] = """
    type: command
    short-summary: "Create a host resource"
    examples:
      - name: Create host
        text: |-
               az connectedvmware host create --custom-location "custom location name" \
               --location "location name" --inventory-item "name or id the inventory item" \
               --name "host name" --resource-group "resource group name" \
               --vcenter "name or id of the vcenter"
"""

helps[
    'connectedvmware host delete'
] = """
    type: command
    short-summary: "Delete host resource"
    examples:
      - name: Delete host
        text: |-
               az connectedvmware host delete --ids "resource id" --name "host name" \
               --resource-group "resource group name" --subscription "Name or ID of subscription"
"""

helps[
    'connectedvmware host list'
] = """
    type: command
    short-summary: "Retrieve a list of host of given resource group"
    examples:
      - name: Retrieve a list of host
        text: |-
               az connectedvmware host list --resource-group "resource group name"
"""

helps[
    'connectedvmware host show'
] = """
    type: command
    short-summary: "Get details of a host by id, resource-group, host name, or subscription"
    examples:
      - name: Get details of a host
        text: |-
               az connectedvmware host show --ids "resource id" --name "host name" \
               --resource-group "resource group name" --subscription "Name or ID of subscription"
"""

helps[
    'connectedvmware vcenter'
] = """
    type: group
    short-summary: Vcenter resource.
"""

helps[
    'connectedvmware vcenter connect'
] = """
    type: command
    short-summary: "Create vcenter resource"
    examples:
      - name: Connect to vcenter
        text: |-
               az connectedvmware vcenter connect --custom-location "custom location name" \
               --fqdn "vcenter fqdn/ip" --username "vcenter user name" --password "vcenter password" \
               --resource-group "resource group name" --location "location name" --name "vcenter name"
"""

helps[
    'connectedvmware vcenter delete'
] = """
    type: command
    short-summary: "Delete vcenter resource"
    examples:
      - name: Delete vcenter resource
        text: |-
               az connectedvmware vcenter delete --ids "resource id" --name "vcenter name" \
               --resource-group "resource group name" --subscription "Name or ID of subscription"
"""

helps[
    'connectedvmware vcenter list'
] = """
    type: command
    short-summary: "Retrieve a list of vcenter resource of given resource group"
    examples:
      - name: Retrieve a list of vcenter resource
        text: |-
               az connectedvmware vcenter list --resource-group "resource group name"
"""

helps[
    'connectedvmware vcenter show'
] = """
    type: command
    short-summary: "Get details of a vcenter resource by id, resource-group, vcenter name or subscription"
    examples:
      - name: Get details of a vcenter resource
        text: |-
               az connectedvmware vcenter show --ids "resource id" --name "vcenter name" \
                   --resource-group "resource group name" --subscription "Name or ID of subscription"
"""

helps[
    'connectedvmware vcenter inventory-item'
] = """
    type: group
    short-summary: inventory item resource.
"""

helps[
    'connectedvmware vcenter inventory-item list'
] = """
    type: command
    short-summary: "Retrieve a list of inventory item given by resource group and vcenter name."
    examples:
      - name: Retrieve a list of inventory item
        text: |-
               az connectedvmware vcenter inventory-item list --resource-group "resource group name" \
               --vcenter "name of the vcenter"
"""

helps[
    'connectedvmware vcenter inventory-item show'
] = """
    type: command
    short-summary: "Get details of a inventory item by inventory item name or id, resource-group and vcenter name."
    examples:
      - name: Get details of a inventory item
        text: |-
               az connectedvmware vcenter inventory-item show --inventory-item "inventory item name" \
               --resource-group "resource group name" --vcenter "name of the vcenter"
"""

helps[
    'connectedvmware virtual-network'
] = """
    type: group
    short-summary: virtual network resource
"""

helps[
    'connectedvmware virtual-network create'
] = """
    type: command
    short-summary: "Create virtual network resource"
    examples:
      - name: Create virtual network
        text: |-
               az connectedvmware virtual-network create --custom-location "custom location name" \
               --location "location name" --inventory-item "name or id the inventory item" \
               --name "virtual network name" --resource-group "resource group name" \
               --vcenter "name or id of the vcenter"
"""

helps[
    'connectedvmware virtual-network delete'
] = """
    type: command
    short-summary: "Delete virtual network resource"
    examples:
      - name: Delete virtual network
        text: |-
               az connectedvmware virtual-network delete --ids "resource id" --name "virtual network name" \
               --resource-group "resource group name" --subscription "Name or ID of subscription"
"""

helps[
    'connectedvmware virtual-network list'
] = """
    type: command
    short-summary: "Retrieve a list of virtual network of given resource group"
    examples:
      - name: Retrieve a list of virtual network resource
        text: |-
               az connectedvmware virtual-network list --resource-group "resource group name"
"""

helps[
    'connectedvmware virtual-network show'
] = """
    type: command
    short-summary: "Get details of a virtual network by id, resource-group, reource pool name or subscription"
    examples:
      - name: Get details of a virtual-network
        text: |-
               az connectedvmware virtual-network show --ids "resource id" --name "virtual network name" \
               --resource-group "resource group name" --subscription "Name or ID of subscription"
"""

helps[
    'connectedvmware vm'
] = """
    type: group
    short-summary: vm resource
"""

helps[
    'connectedvmware vm create'
] = """
    type: command
    short-summary: "Create VMInstance resource"
    examples:
      - name: Create vm
        text: |-
               az connectedvmware vm create --custom-location "custom location name" \
               --location "location name" --inventory-item "name or id of the inventory item" \
               --name "virtual machine name" --resource-group "resource group name" \
               --vcenter "name or id of the vcenter"

      - name: Enable an exiting VM to azure.
        text: |-
               az connectedvmware vm create --subscription contoso-sub \
               --resource-group contoso-rg --location eastus --custom-location contoso-cl \
               --inventory-item 01234567-0123-0123-0123-0123456789ab --name contoso-vm

      - name: Link an HCRP Machine to a vCenter in another subscription using the machine id.
        text: |-
               az connectedvmware vm create \
               --machine-id /subscriptions/01234567-0123-0123-0123-0123456789ab/resourceGroups/contoso-rg/providers/Microsoft.HybridCompute/machines/contoso-vm \
               --vcenter /subscriptions/fedcba98-7654-3210-0123-456789abcdef/resourceGroups/contoso-rg/providers/Microsoft.HybridCompute/vcenters/contoso-vcenter

      - name: Link an HCRP Machine to a vCenter in another subscription using the machine name.
        text: |-
                az connectedvmware vm create \
                --resource-group contoso-rg --location eastus --name hcrp-contoso-machine \
                --vcenter /subscriptions/fedcba98-7654-3210-0123-456789abcdef/resourceGroups/contoso-rg/providers/Microsoft.HybridCompute/vcenters/contoso-vcenter

      - name: Link an HCRP Machine to a vCenter in the same subscription and resource group.
        text: |-
                az connectedvmware vm create \
                --resource-group contoso-rg --location eastus --name hcrp-contoso-machine \
                --vcenter contoso-vcenter
"""

helps[
    'connectedvmware vm create-from-machines'
] = """
    type: command
    short-summary: "Create VMInstance resource(s) from existing Microsoft.HybridCompute machines."
    examples:
      - name: Create VMware resources from the specified Arc for Servers machine in the vCenter
        text: |-
                az connectedvmware vm create-from-machines \
--resource-group contoso-rg --name contoso-vm \
--vcenter-id /subscriptions/fedcba98-7654-3210-0123-456789abcdef/resourceGroups/contoso-rg-2/providers/Microsoft.HybridCompute/vcenters/contoso-vcenter

      - name: Creates VMware resources from all Arc for Servers machines in the specified resource group belonging to that vCenter
        text: |-
                az connectedvmware vm create-from-machines \
--resource-group contoso-rg \
--vcenter-id /subscriptions/fedcba98-7654-3210-0123-456789abcdef/resourceGroups/contoso-rg-2/providers/Microsoft.HybridCompute/vcenters/contoso-vcenter

      - name: Create VMware resources from all Arc for Servers machines in the specified subscription belonging to that vCenter
        text: |-
                az connectedvmware vm create-from-machines \
--subscription contoso-sub \
--vcenter-id /subscriptions/fedcba98-7654-3210-0123-456789abcdef/resourceGroups/contoso-rg-2/providers/Microsoft.HybridCompute/vcenters/contoso-vcenter
"""

helps[
    'connectedvmware vm delete'
] = """
    type: command
    short-summary: "Delete vm resource"
    examples:
      - name: Delete vm
        text: |-
               az connectedvmware vm delete --ids "resource id" --name "virtual machine name" \
               --resource-group "resource group name" --subscription "Name or ID of subscription"
"""

helps[
    'connectedvmware vm list'
] = """
    type: command
    short-summary: "Retrieve a list of vm of given resource group"
    examples:
      - name: Retrieve a list of vm resource
        text: |-
               az connectedvmware vm list --resource-group "resource group name"
"""

helps[
    'connectedvmware vm restart'
] = """
    type: command
    short-summary: "Restart vm resource"
    examples:
      - name: Restart vm
        text: |-
               az connectedvmware vm restart --ids "resource id" --name "virtual machine name" \
               --resource-group "resource group name" --subscription "Name or ID of subscription"
"""

helps[
    'connectedvmware vm show'
] = """
    type: command
    short-summary: "Get details of a vm by id, resource-group, reource pool name or subscription"
    examples:
      - name: Get details of a vm resource
        text: |-
               az connectedvmware vm show --ids "resource id" --name "vm template name" \
               --resource-group "resource group name" --subscription "Name or ID of subscription"
"""

helps[
    'connectedvmware vm start'
] = """
    type: command
    short-summary: "Start vm resource"
    examples:
      - name: Start vm
        text: |-
               az connectedvmware vm start --ids "resource id" --name "virtual machine name" \
               --resource-group "resource group name" --subscription "Name or ID of subscription"
"""

helps[
    'connectedvmware vm stop'
] = """
    type: command
    short-summary: "Stop vm resource"
    examples:
      - name: Stop vm
        text: |-
               az connectedvmware vm stop --ids "resource id" --name "virtual machine name" \
               --resource-group "resource group name" --subscription "Name or ID of subscription"
"""

helps[
    'connectedvmware vm update'
] = """
    type: command
    short-summary: "Update vm resource"
    examples:
      - name: Update vm
        text: |-
               az connectedvmware vm update --ids "resource id" --name "virtual machine name" \
               --resource-group "resource group name" --subscription "Name or ID of subscription" \
               --memory-size "vm memory size in MB" --num-CPUs "no. of CPUs"
"""

helps[
    'connectedvmware vm disk'
] = """
    type: group
    short-summary: vm disk
"""

helps[
    'connectedvmware vm disk add'
] = """
    type: command
    short-summary: "Add virtual disk to a virtual machine"
    examples:
      - name: Add virtual disk to a virtual machine
        text: |-
               az connectedvmware vm disk add --controller-key "The controller key of the disk" \
               --disk-size "The disk size in GBs" --name "Name of the Disk" --resource-group \
               "resource group name" --vm-name "Name of the virtual machine"
"""

helps[
    'connectedvmware vm disk delete'
] = """
    type: command
    short-summary: "Delete virtual disks to a virtual machine"
    examples:
      - name: Delete virtual disks to a virtual machine
        text: |-
               az connectedvmware vm disk delete --disk "Names of the Disks" --resource-group \
               "resource group name" --vm-name "Name of the virtual machine"
"""

helps[
    'connectedvmware vm disk list'
] = """
    type: command
    short-summary: "Retrieve a list of vm disk from given resource group name and vm name"
    examples:
      - name: Retrieve a list of vm disk
        text: |-
               az connectedvmware vm disk list --resource-group "resource group name" --vm-name \
               "Name of the virtual machine"
"""

helps[
    'connectedvmware vm disk show'
] = """
    type: command
    short-summary: "Get details of a vm disk by it's name, resource-group and vm name"
    examples:
      - name: Get details of vm disk
        text: |-
               az connectedvmware vm disk show --name "Name of the Disk" --resource-group \
               "resource group name" --vm-name "Name of the virtual machine"
"""
helps[
    'connectedvmware vm disk update'
] = """
    type: command
    short-summary: "Update virtual disk to a virtual machine"
    examples:
      - name: Update virtual disk to a virtual machine
        text: |-
               az connectedvmware vm disk update --controller-key "The controller key of the disk" \
               --disk-size "The disk size in GBs" --name "Name of the Disk" --resource-group \
               "resource group name" --vm-name "Name of the virtual machine"
"""

helps[
    'connectedvmware vm nic'
] = """
    type: group
    short-summary: vm nic
"""

helps[
    'connectedvmware vm nic add'
] = """
    type: command
    short-summary: "Add virtual nic to a virtual machine"
    examples:
      - name: Add virtual nic to a virtual machine
        text: |-
               az connectedvmware vm nic add --name "Name of the NIC" --network "Network Name or Id" \
               --resource-group "resource group name" --vm-name "Name of the virtual machine"
"""

helps[
    'connectedvmware vm nic delete'
] = """
    type: command
    short-summary: "Delete virtual nic to a virtual machine"
    examples:
      - name: Delete virtual nic to a virtual machine
        text: |-
               az connectedvmware vm nic delete --nics "Names of the NICs" --resource-group \
               "resource group name" --vm-name "Name of the virtual machine"
"""

helps[
    'connectedvmware vm nic list'
] = """
    type: command
    short-summary: "Retrieve a list of vm nic from given resource group name and vm name"
    examples:
      - name: Retrieve a list of vm nic
        text: |-
               az connectedvmware vm nic list --resource-group "resource group name" --vm-name \
               "Name of the virtual machine"
"""

helps[
    'connectedvmware vm nic show'
] = """
    type: command
    short-summary: "Get details of a vm nic by it's name, resource-group and vm name"
    examples:
      - name: Get details of vm nic
        text: |-
               az connectedvmware vm nic show --name "Name of the NIC" --resource-group \
               "resource group name" --vm-name "Name of the virtual machine"
"""

helps[
    'connectedvmware vm guest-agent'
] = """
    type: group
    short-summary: vm guest agent.
"""

helps[
    'connectedvmware vm guest-agent enable'
] = """
    type: command
    short-summary: "Enable guest agent on the vm"
    examples:
      - name: Enable guest agent on the vm
        text: |-
               az connectedvmware vm guest-agent enable --username "vm user name" --password "vm password" \
               --resource-group "resource group name" --subscription "Name or ID of subscription" \
               --vm-name "vm name"
"""

helps[
    'connectedvmware vm guest-agent show'
] = """
    type: command
    short-summary: "Get details of a guest agent by guest agent name, resource-group and vm name."
    examples:
      - name: Get details of a guest agent
        text: |-
               az connectedvmware vm guest-agent show --resource-group "resource group name" \
               --vm-name "name of the vm"
"""

helps['connectedvmware vm extension'] = """
    type: group
    short-summary: Manage vm extension with connectedvmware
"""

helps['connectedvmware vm extension list'] = """
    type: command
    short-summary: "The operation to get all extensions of a non-Azure vm."
    examples:
      - name: Get all VM Extensions
        text: |-
               az connectedvmware vm extension list --vm-name "vm name" --resource-group "myResourceGroup"
"""

helps['connectedvmware vm extension show'] = """
    type: command
    short-summary: "The operation to get the extension."
    examples:
      - name: Get VM Extension
        text: |-
               az connectedvmware vm extension show --name "CustomScriptExtension" --vm-name "vm name" \
--resource-group "myResourceGroup"
"""

helps['connectedvmware vm extension create'] = """
    type: command
    short-summary: "The operation to create the extension."
    examples:
      - name: Create a VM Extension
        text: |-
               az connectedvmware vm extension create --name "CustomScriptExtension" --location "eastus2euap" --type \
"CustomScriptExtension" --publisher "Microsoft.Compute" --settings "{\\"commandToExecute\\":\\"powershell.exe -c \
\\\\\\"Get-Process | Where-Object { $_.CPU -gt 10000 }\\\\\\"\\"}" --type-handler-version "1.10" --vm-name \
"vm name" --resource-group "myResourceGroup"
"""

helps['connectedvmware vm extension update'] = """
    type: command
    short-summary: "The operation to update the extension."
    examples:
      - name: Update a VM Extension
        text: |-
               az connectedvmware vm extension update --name "CustomScriptExtension" --type "CustomScriptExtension" \
--publisher "Microsoft.Compute" --settings "{\\"commandToExecute\\":\\"powershell.exe -c \\\\\\"Get-Process | \
Where-Object { $_.CPU -lt 100 }\\\\\\"\\"}" --type-handler-version "1.10" --vm-name "vm name" --resource-group \
"myResourceGroup"
"""

helps['connectedvmware vm extension delete'] = """
    type: command
    short-summary: "The operation to delete the extension."
    examples:
      - name: Delete a VM Extension
        text: |-
               az connectedvmware vm extension delete --name "vm extension name" --vm-name "vm name" --resource-group \
"myResourceGroup"
"""

helps[
    'connectedvmware vm-template'
] = """
    type: group
    short-summary: vm template resource
"""

helps[
    'connectedvmware vm-template create'
] = """
    type: command
    short-summary: "Create vm template resource"
    examples:
      - name: Create vm template
        text: |-
               az connectedvmware vm-template create --custom-location "custom location name" \
               --location "location name" --inventory-item "name or id the inventory item" \
               --name "vm template name" --resource-group "resource group name" \
               --vcenter "name or id of the vcenter"
"""

helps[
    'connectedvmware vm-template delete'
] = """
    type: command
    short-summary: "Delete vm template resource"
    examples:
      - name: Delete virtual template
        text: |-
               az connectedvmware vm-template delete --ids "resource id" --name "vm template name" \
               --resource-group "resource group name" --subscription "Name or ID of subscription"
"""

helps[
    'connectedvmware vm-template list'
] = """
    type: command
    short-summary: "Retrieve a list of vm template of given resource group"
    examples:
      - name: Retrieve a list of vm template resource
        text: |-
               az connectedvmware vm-template list --resource-group "resource group name"
"""

helps[
    'connectedvmware vm-template show'
] = """
    type: command
    short-summary: "Get details of a vm template by id, resource-group, reource pool name or subscription"
    examples:
      - name: Get details of a vm template
        text: |-
               az connectedvmware vm-template show --ids "resource id" --name "vm template name" \
               --resource-group "resource group name" --subscription "Name or ID of subscription"
"""
