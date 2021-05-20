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
                --location "" --mo-ref-id "mo-ref id of the resource in vc" --name "resource pool name" \
                --resource-group "resource group name" --vcenter "name or id of the vcenter"
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
               --resource-group "resource group name" --subscription "Name or ID of subscription" \
               --location "region name" --name "vcenter name"
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
               --location "region name" --mo-ref-id "mo-ref id of the resource in vc" --name \
               "virtual network name" --resource-group "resource group name" --vcenter "name or id of \
               the vcenter" --inventory-item "inventory item name or id"
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
    short-summary: "Create vm in vcenter from existing vm template"
    examples:
      - name: Create vm
        text: |-
               az connectedvmware vm create --custom-location "custom location name" --location \
               "Region name" --name "virtual network name" --resource-group "resource group name" \
               --vcenter "name or id of the vcenter" --inventory-item "inventory item name or id"
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
               --location "region name" --mo-ref-id "mo-ref id of the resource in vc" --name \
               "vm template name" --resource-group "resource group name" --vcenter "name or id of \
               the vcenter" --inventory-item "inventory item name or id"
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

helps[
    'connectedvmware inventory-item'
] = """
    type: group
    short-summary: inventory item resource.
"""

helps[
    'connectedvmware inventory-item list'
] = """
    type: command
    short-summary: "Retrieve a list of inventory item given by resource group and vcenter name."
    examples:
      - name: Retrieve a list of inventory item
        text: |-
               az connectedvmware inventory-item list --resource-group "resource group name" \
               --vcenter-name "name of the vcenter"
"""

helps[
    'connectedvmware inventory-item show'
] = """
    type: command
    short-summary: "Get details of a inventory item by inventory item name or id, resource-group and vcenter name."
    examples:
      - name: Get details of a vm template
        text: |-
               az connectedvmware inventory-item show --inventory-item-name "inventory item name" \
               --resource-group "resource group name" --vcenter-name "name of the vcenter"
"""
