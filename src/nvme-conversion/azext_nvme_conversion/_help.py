# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Help text definitions for nvme-conversion commands."""

from knack.help_files import helps  # pylint: disable=unused-import


helps['nvme-conversion'] = """
type: group
short-summary: Convert VM disk controllers between SCSI and NVMe.
long-summary: |
    Validate, prepare, and convert Azure Virtual Machines from SCSI to NVMe disk controllers
    and back. Unlike 'az vm update --disk-controller-type' which only sets the controller
    property, this extension handles the full conversion lifecycle: pre-flight validation
    (Gen2, ADE, SKU capabilities), OS readiness checks and fixes (stornvme on Windows,
    initramfs/grub/fstab on Linux), OS disk capability update, VM deallocate, resize,
    controller change, and optional restart — all in a single command.
    For more information, see https://learn.microsoft.com/azure/virtual-machines/enable-nvme-interface
"""

helps['nvme-conversion convert'] = """
type: command
short-summary: Convert a VM's disk controller between SCSI and NVMe.
long-summary: |
    Performs the full conversion flow in 8 steps:
    [1] Validate VM exists and is Gen2
    [2] Resolve target controller type and VM size
    [3] Check prerequisites (ADE, generation, power state)
    [4] Validate target SKU capabilities
    [5] Check/fix OS readiness via RunCommand
    [6] Shut down (deallocate) the VM
    [7] Update OS disk capabilities and VM size
    [8] Optionally start the VM

    If --controller-type is not specified, the command auto-detects the current type
    and toggles to the opposite. If --vm-size is not specified and the current size
    supports both SCSI and NVMe, the current size is kept.
examples:
  - name: Convert a VM to NVMe (auto-detect, keep current size)
    text: >
        az nvme-conversion convert
        --resource-group MyResourceGroup
        --vm-name MyVM
        --start-vm
        --yes
        --verbose
  - name: Convert a VM to NVMe with a specific target size
    text: >
        az nvme-conversion convert
        --resource-group MyResourceGroup
        --vm-name MyVM
        --vm-size Standard_E4bds_v5
        --start-vm
        --yes
        --verbose
  - name: Convert a VM back to SCSI
    text: >
        az nvme-conversion convert
        --resource-group MyResourceGroup
        --vm-name MyVM
        --controller-type SCSI
        --vm-size Standard_E4s_v5
        --start-vm
        --yes
        --verbose
  - name: Convert with automatic OS fixes (stornvme driver on Windows, initramfs/grub/fstab on Linux)
    text: >
        az nvme-conversion convert
        --resource-group MyResourceGroup
        --vm-name MyVM
        --fix-os
        --start-vm
        --yes
        --verbose
  - name: Dry-run on a Linux VM to assess readiness without making any changes
    text: >
        az nvme-conversion convert
        --resource-group MyResourceGroup
        --vm-name MyLinuxVM
        --dry-run
        --verbose
  - name: Convert without waiting for the VM to fully start
    text: >
        az nvme-conversion convert
        --resource-group MyResourceGroup
        --vm-name MyVM
        --start-vm
        --no-wait
        --yes
        --verbose
  - name: Convert and skip OS readiness check (use when OS is already prepared)
    text: >
        az nvme-conversion convert
        --resource-group MyResourceGroup
        --vm-name MyVM
        --ignore-os-check
        --start-vm
        --yes
        --verbose
"""

helps['nvme-conversion check'] = """
type: command
short-summary: Check VM readiness for disk controller conversion without making changes.
long-summary: |
    Runs all pre-flight validation checks and reports the results as a JSON object
    with pass/fail status per check. Checks include:
    - VM exists and is Generation 2
    - No Azure Disk Encryption for Linux
    - Current disk controller type
    - Target SKU supports the desired controller
    - OS readiness (stornvme driver on Windows, NVMe driver/grub/fstab on Linux)

    If --controller-type is not specified, checks readiness for toggling to the opposite type.
    Use this command to validate VMs before conversion, especially in bulk scenarios.
examples:
  - name: Check if a VM is ready for conversion
    text: >
        az nvme-conversion check
        --resource-group MyResourceGroup
        --vm-name MyVM
        --verbose
  - name: Check readiness targeting a specific VM size
    text: >
        az nvme-conversion check
        --resource-group MyResourceGroup
        --vm-name MyVM
        --vm-size Standard_E4bds_v5
        --verbose
  - name: Check readiness skipping OS checks (faster, no RunCommand)
    text: >
        az nvme-conversion check
        --resource-group MyResourceGroup
        --vm-name MyVM
        --ignore-os-check
        --verbose
  - name: Check if a VM can be converted to SCSI
    text: >
        az nvme-conversion check
        --resource-group MyResourceGroup
        --vm-name MyVM
        --controller-type SCSI
        --verbose
"""
