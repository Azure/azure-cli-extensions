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
| VM deallocate | Separate `az vm deallocate` | Automatic (skips if already stopped) |
| VM resize + controller change | `az vm update` | Combined in one step |
| VM start | Separate `az vm start` | `--start-vm` |
| Rollback instructions | None | Provided in output |
| Dry-run mode | None | `--dry-run` |

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
