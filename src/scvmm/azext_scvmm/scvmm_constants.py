# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from enum import Enum

SCVMM_NAMESPACE = "Microsoft.ScVmm"
VMMSERVER_RESOURCE_TYPE = "vmmservers"
CLOUD_RESOURCE_TYPE = "clouds"
VMMSERVER_RESOURCE_TYPE = "vmmservers"
VMTEMPLATE_RESOURCE_TYPE = "virtualmachinetemplates"
VIRTUALNETWORK_RESOURCE_TYPE = "virtualnetworks"
AVAILABILITYSET_RESOURCE_TYPE = "availabilitysets"
EXTENSIONS_RESOURCE_TYPE = "extensions"

MACHINE_KIND_SCVMM = "scvmm"

DEFAULT_VMMSERVER_PORT = 8100

EXTENDED_LOCATION_NAMESPACE = "Microsoft.ExtendedLocation"
CUSTOM_LOCATION_RESOURCE_TYPE = "customLocations"
EXTENDED_LOCATION_TYPE = "customLocation"

INVENTORY_ITEM_TYPE = "InventoryItems"

NAME_PARAMETER = "name"

HCRP_NAMESPACE = "Microsoft.HybridCompute"
MACHINES_RESOURCE_TYPE = "machines"
VM_SYSTEM_ASSIGNED_INDENTITY_TYPE = "SystemAssigned"
GUEST_AGENT_PROVISIONING_ACTION_INSTALL = "install"

# NIC parameters.
NETWORK = "network"
IPV4_ADDRESS_TYPE = "ipv4-address-type"
IPV6_ADDRESS_TYPE = "ipv6-address-type"
MAC_ADDRESS_TYPE = "mac-address-type"
MAC_ADDRESS = "mac-address"


# Disk parameters
TEMPLATE_DISK_ID = "template-disk-id"
DISK_SIZE = "disk-size"
BUS_TYPE = "bus-type"
BUS = "bus"
LUN = "lun"
VHD_TYPE = "vhd-type"
QOS_NAME = "qos-name"
QOS_ID = "qos-id"


class BusType(str, Enum):
    scsi = "SCSI"
    ide = "IDE"


class VHDType(str, Enum):
    static = "Static"
    dynamic = "Dynamic"
