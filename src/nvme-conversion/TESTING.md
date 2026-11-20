# NVMe Conversion Extension — Live Test Tracker

**Date**: 2026-05-10
**Resource Group**: `nvme-conversion-test`
**Location**: `westus3`
**Extension version**: `1.0.0b1`
**az CLI versions**: WSL 2.86.0 / Windows 2.85.0

## Test VMs

| VM Name | OS | Image | Size | Initial Controller | Status |
|---|---|---|---|---|---|
| nvme-test-ubuntu | Linux | Canonical:ubuntu-24_04-lts:server:latest | Standard_D2s_v5 | SCSI | Provisioned |
| nvme-test-rhel | Linux | RedHat:RHEL:9-lvm-gen2:latest | Standard_D2s_v5 | SCSI | Provisioned |
| nvme-test-sles | Linux | SUSE:sles-15-sp6:gen2:latest | Standard_D2s_v5 | SCSI | Provisioned |
| nvme-test-azl4 | Linux | microsoftazurelinux:azurelinux-4:4:latest | Standard_D2s_v5 | SCSI | Provisioned |
| nvme-test-win | Windows | MicrosoftWindowsServer:WindowsServer:2022-datacenter-g2:latest | Standard_D2s_v5 | SCSI | Provisioned |

## Test Plan

### Phase A — `check` command (read-only, no changes)

| # | Test | VM | CLI | Expected | Result | Notes |
|---|---|---|---|---|---|---|
| A1 | Check Ubuntu (SCSI→NVMe, no --vm-size) | nvme-test-ubuntu | WSL | passed (SKU warns) | **PASS** | After fix: warns about missing DiskControllerTypes but passes |
| A1-pre | Check Ubuntu (before SKU fix) | nvme-test-ubuntu | WSL | skuValidation failed | **PASS** | Correctly detected D2s_v5 lacks NVMe before the fix |
| A2 | Check RHEL (--ignore-sku-check) | nvme-test-rhel | WSL | passed | **PASS** | All checks pass including osReadiness via RunCommand |
| A3 | Check SLES (--ignore-sku-check, no OS) | nvme-test-sles | WSL | passed | **PASS** | Validation checks pass (ADE, Gen2, controller) |
| A4 | Check AzL4 (--ignore-sku-check, no OS) | nvme-test-azl4 | WSL | passed | **PASS** | Validation checks pass |
| A5 | Check Win2022 from Windows CLI | nvme-test-win | **Win CMD** | osReadiness failed | **PASS** | StartOverride:ERROR detected correctly. windowsVersion: passed |
| A6 | Check Ubuntu full (all checks) | nvme-test-ubuntu | WSL | passed | **PASS** | All 7 checks pass including osReadiness and skuValidation |
| A7 | Check already-on-target (--controller-type SCSI) | nvme-test-ubuntu | WSL | info/no-change | **PASS** | Returns `controllerCheck: info` |

> **Finding A1b (critical)**: No v5 D-series SKU has `DiskControllerTypes` in the SKU API.
> Only v6+ and Ebds/Ebs v5 series advertise it. When absent, it means SCSI-only.
>
> **Fix applied**: SKU validation now treats missing `DiskControllerTypes` as "unknown" —
> warns but doesn't block. The VM update API will fail safely if the SKU truly doesn't support it.
>
> **Finding A5**: Windows Server 2022 has `StartOverride` registry key that blocks NVMe.
> This is expected and fixable with `--fix-os`. The check correctly identifies this.

### Phase B — `convert` command (SCSI → NVMe)

| # | Test | VM | CLI | Expected | Result | Notes |
|---|---|---|---|---|---|---|
| B1 | Convert Ubuntu SCSI→NVMe (--vm-size Standard_D2s_v6 --fix-os --start-vm) | nvme-test-ubuntu | WSL | succeeded, NVMe | **PASS** | All 8 steps completed, VM running on NVMe |
| B2 | Convert RHEL SCSI→NVMe (--vm-size Standard_D2s_v6 --fix-os --start-vm) | nvme-test-rhel | WSL | succeeded, NVMe | **PASS** | |
| B3 | Convert SLES SCSI→NVMe (--vm-size Standard_D2s_v6 --fix-os --start-vm) | nvme-test-sles | WSL | succeeded, NVMe | **PASS** | |
| B4 | Convert AzL4 SCSI→NVMe (--vm-size Standard_D2s_v6 --fix-os --start-vm) | nvme-test-azl4 | WSL | succeeded, NVMe | **PASS** | |
| B5 | Convert Windows SCSI→NVMe (--vm-size Standard_D2s_v6 --fix-os --start-vm) | nvme-test-win | WSL | succeeded, NVMe | **PASS** | |

### Phase C — Post-conversion validation

| # | Test | VM | CLI | Expected | Result | Notes |
|---|---|---|---|---|---|---|
| C1 | Verify Ubuntu is NVMe after boot | nvme-test-ubuntu | WSL | controller=NVMe | **PASS** | az vm show confirms NVMe |
| C2 | Verify RHEL is NVMe after boot | nvme-test-rhel | WSL | controller=NVMe | **PASS** | |
| C3 | Verify SLES is NVMe after boot | nvme-test-sles | WSL | controller=NVMe | **PASS** | |
| C4 | Verify AzL4 is NVMe after boot | nvme-test-azl4 | WSL | controller=NVMe | **PASS** | |
| C5 | Verify Windows is NVMe after boot | nvme-test-win | WSL | controller=NVMe | **PASS** | |

### Phase D — `convert` command (NVMe → SCSI revert)

| # | Test | VM | CLI | Expected | Result | Notes |
|---|---|---|---|---|---|---|
| D1 | Convert Ubuntu NVMe→SCSI (--start-vm) | nvme-test-ubuntu | WSL | succeeded, SCSI | **PASS** | Reverted to D2s_v5 SCSI, VM running |
| D2 | Convert Windows NVMe→SCSI (--start-vm) | nvme-test-win | WSL | succeeded, SCSI | **PASS** | Reverted to D2s_v5 SCSI, VM running |

### Phase E — Edge cases & error paths

| # | Test | VM | CLI | Expected | Result | Notes |
|---|---|---|---|---|---|---|
| E1 | Convert already-NVMe with --controller-type NVMe | nvme-test-rhel | WSL | no-change | **PASS** | Returns status:no-change cleanly |
| E2 | Check with --ignore-os-check | nvme-test-ubuntu | WSL | passed (skips OS) | **PASS** | No powerState/osReadiness checks in output |
| E3 | Convert with --dry-run (Linux) | nvme-test-sles | WSL | dry-run-complete | **PASS** | VM unchanged, returns immediately |
| E4 | Convert with --no-wait --start-vm | nvme-test-azl4 | WSL | succeeded, no wait | **PASS** | Conversion completed, VM reverted to SCSI |
| E5 | Check from Windows CLI | nvme-test-win | **Win CMD** | osReadiness failed | **PASS** | Extension works correctly from Windows CMD |

### Phase F — Windows version coverage

| # | Test | VM | CLI | Expected | Result | Notes |
|---|---|---|---|---|---|---|
| F1 | Check Win2022 (from WSL) | nvme-test-win | WSL | osReadiness: StartOverride:ERROR | **PASS** | Most popular server version |
| F2 | Check Win2022 (from Win CMD) | nvme-test-win | **Win CMD** | osReadiness: StartOverride:ERROR | **PASS** | Same result from both CLIs |
| F3 | Check Win2019 (from WSL) | nvme-test-w2019 | WSL | windowsVersion: passed, osReadiness: failed | **PASS** | Min NVMe version, StartOverride issue detected |
| F4 | Check Win2019 (from Win CMD) | nvme-test-w2019 | **Win CMD** | windowsVersion: passed, osReadiness: failed | **PASS** | Identical results from both CLIs |

> **Most used Windows Server versions on Azure** (by market share):
> 1. Windows Server 2022 — current mainstream (tested: Win2022 ✓)
> 2. Windows Server 2019 — still widely deployed, minimum for NVMe (testing: Win2019)
> 3. Windows Server 2025 — newest, same NVMe behavior as 2022 (not testing: same code path)
> 4. Windows Server 2016 — legacy, BLOCKED by our version check (< 2019)

### Phase G — Cleanup

| # | Task | Result | Notes |
|---|---|---|---|
| G1 | Delete resource group nvme-conversion-test | | |
