# Azure NVMe Conversion Extension

Convert Azure Virtual Machines between SCSI and NVMe disk controllers.

For architecture, design decisions, and development setup, see [DEVELOPMENT.md](DEVELOPMENT.md).

## Why use this extension?

The built-in `az vm update --disk-controller-type` only sets the controller property on the VM — one step out of eight required for a safe conversion. This extension orchestrates the full lifecycle:

| Step | `az vm update` | `az nvme-conversion convert` |
|---|---|---|
| Pre-flight validation (Gen2, ADE, SKU) | Manual | Automatic |
| OS readiness check & fix (drivers, grub, fstab) | Manual RunCommand per distro | `--fix-os` |
| OS disk `supportedCapabilities` update | Separate `az disk update` | Automatic |
| VM deallocate | Separate `az vm deallocate` | Automatic (skips only if confirmed deallocated) |
| VM resize + controller change | `az vm update` | Combined in one step |
| VM start | Separate `az vm start` | `--start-vm` |
| Rollback instructions | None | Provided in output |
| Dry-run mode | None | `--dry-run` (Linux only) |

## Usage

```bash
# Convert a VM (auto-detects controller type, keeps current size if it supports both)
az nvme-conversion convert --resource-group myRG --vm-name myVM --start-vm

# Convert and change VM size
az nvme-conversion convert --resource-group myRG --vm-name myVM --vm-size Standard_E4bds_v5 --start-vm

# Check VM readiness without making changes
az nvme-conversion check --resource-group myRG --vm-name myVM

# Explicitly convert to SCSI with a different size
az nvme-conversion convert --resource-group myRG --vm-name myVM --controller-type SCSI --vm-size Standard_E4s_v5 --start-vm

# Dry-run for Linux VMs (stage changes without applying)
az nvme-conversion convert --resource-group myRG --vm-name myVM --dry-run

# Auto-fix OS settings during conversion
az nvme-conversion convert --resource-group myRG --vm-name myVM --fix-os --start-vm --yes
```

## Preparation safety

Linux preparation verifies the actual NVMe PCI and Hyper-V PCI modules for each
installed kernel, using its distribution-specific boot images. Empty inventories,
failed inspections/rebuilds and remaining errors block conversion, including with
`--fix-os`. Multi-letter SCSI names are supported; UUID queries do not depend on
`blkid` field order. Unresolved legacy fstab entries fail without replacing fstab.

Windows preparation verifies `stornvme` and `vpci` in every installed ControlSet.
Fixes wait for `sc.exe`, check its exit code and recheck registry values. Both
platforms require explicit, complete RunCommand confirmations. Windows rejects
`--dry-run` before guest preparation, even when `--fix-os` is supplied.

Disk and controller updates require confirmed deallocation. A stopped,
transitional or unknown power state is not treated as deallocated.

## ADE exclusion

NVMe is refused when ADE is present on the OS disk or any attached data disk,
or when the VM extension/disk inventory cannot be verified. The preflight checks
Linux and Windows ADE handler identities, VM disk encryption settings and every
managed disk's ADE metadata. Extension names need not be the default, and API
errors are not treated as "not installed". Unlocking a disk or removing the
extension does not prove that the disks are decrypted.

This gate cannot be bypassed with OS/SKU skip flags or dry-run. A return to SCSI
is not blocked by the NVMe ADE exclusion. SSE, customer-managed server-side keys
and encryption at host are not ADE.

Successful checks include `vmResourceId` and a versioned `nvmeEligibility` object
with source VM identity, UTC check time, OS/data disk IDs and explicit ADE-free
states. Failed/unknown ADE checks return no eligibility object and stop before
guest RunCommand. Consumers must require `overallStatus: passed`, not just a
zero process exit. This is diagnostic control-plane metadata, not signed Azure
attestation or an ALAR prerequisite. ALAR does not require this extension or its
JSON output; its separate local guard checks recovery-key/encryption evidence.

## Parameters

| Parameter | Description | Required |
|---|---|---|
| `--resource-group -g` | Resource group of the VM | Yes |
| `--vm-name -n` | VM name | Yes |
| `--controller-type` | Target controller type (NVMe or SCSI). Auto-detected if omitted | No |
| `--vm-size` | Target VM size/SKU. If omitted, keeps current size when it supports the target controller | No |
| `--start-vm` | Start VM after conversion | No |
| `--fix-os` | Auto-fix OS settings for NVMe readiness | No |
| `--ignore-sku-check` | Skip SKU validation | No |
| `--ignore-os-check` | Skip OS readiness check | No |
| `--ignore-windows-version-check` | Skip Windows version check | No |
| `--dry-run` | Linux only: stage changes without applying | No |
| `--sleep-seconds` | Delay before starting VM (default: 15) | No |
| `--yes -y` | Skip confirmation prompts | No |
| `--no-wait` | Do not wait for VM start to complete | No |


## RHEL 7 standalone EFI timeout handling

For RHEL/redhat/CentOS 7 guests with `/etc/grub2-efi.cfg`, Linux readiness checks
the resolved standalone EFI kernel entries rather than accepting a timeout argument
from `/etc/default/grub` or an unrelated generated configuration. `--fix-os`
regenerates the verified standalone target and requires exact timeout 240 on every
kernel entry. Dry-run does not rebuild or modify boot files. Broken links, modern
redirect stubs in this old-layout branch, and failed/ineffective generation are
reported explicitly rather than overwritten or treated as ready. Other release
and BIOS branches retain their existing behavior. This GRUB correction does not
alter encryption; the separate ADE eligibility gate described above still applies.
