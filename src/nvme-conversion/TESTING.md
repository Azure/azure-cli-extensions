# NVMe Conversion Extension — Live Test Tracker

## Windows readiness and persistence regressions

The Windows guest script now verifies the driver binary, all required boot-driver
and NVMe DWORD settings, registry flush/readback and the actual NVMe OS disk.
PCI overrides remain allowed. Boot orchestration covers guest-agent readiness,
opt-in post-first-boot remediation/restart, persistence after restart and
explicit pending/partial-failure results.

From `src/nvme-conversion`, run:

```bash
python3 -B -m pytest \
  azext_nvme_conversion/tests/latest/test_nvme_conversion.py \
  azext_nvme_conversion/tests/latest/test_readiness_failures.py \
  azext_nvme_conversion/tests/latest/test_linux_efi_timeout.py \
  azext_nvme_conversion/tests/latest/test_windows_readiness.py \
  -k "not NvmeConversionCheckTest and not NvmeConversionConvertTest" \
  -q -p no:cacheprovider
```

Result: **129 passed, 80 subtests passed, 2 live scenarios deselected**.
Native guest-script tests use PowerShell when available; `NVME_TEST_PWSH` can
select an existing executable. They mock registry/CIM/disk/SC operations and
never modify the host registry. Without PowerShell those native cases explicitly
skip rather than claiming acceptance.

Covered cases include missing driver/parameter/PCI settings, incorrect value
types, preserved PCI overrides, failed SC/flush/readback, root-flush fallback,
non-NVMe boot disks, agent timeout, deferred/no-wait/skipped checks, post-reboot
drift and already-current Windows NVMe checks without conversion.
These are functional synthetic regressions, not live Windows boot validation.
See [READINESS-CHANGE-RATIONALE.md](READINESS-CHANGE-RATIONALE.md) for the public
source attribution, safety contract and release-scope explanation.

## Linux kernel-inventory regression coverage

The prepared Linux script derives kernel releases from installed package files
and boot-image/GRUB/BLS references. The package-owned RHEL `kmod-kvdo` directory
is not another installed kernel. Genuine missing images, missing module
inventories, or failed package queries still block readiness. Existing check,
fix, dry-run, driver-rebuild, fstab, and EFI behavior remains covered.

From `src/nvme-conversion`, run on Linux as root for the disposable chroot tests:

```bash
python3 -B -m pytest \
  azext_nvme_conversion/tests/latest/test_readiness_failures.py \
  azext_nvme_conversion/tests/latest/test_linux_efi_timeout.py \
  -q -p no:cacheprovider
```

Result for the prepared patch: **42 passed, 51 subtests passed**.
The regressions cover the extra module directory in check/fix/dry-run, multiple
real kernels, package-listed/boot-referenced missing images, package-query
failures, debug/header files and rescue aliases. The fixtures do not make Azure
calls, mount real disks, or install packages.

### Style and package verification

Completed validation:

```bash
python3 -B -m flake8 --max-line-length=120 \
  --ignore=E501,W503,W504,C901 \
  azext_nvme_conversion/_linux_script.py \
  azext_nvme_conversion/tests/latest/test_readiness_failures.py
python3 -B setup.py bdist_wheel
git diff --check
```

Results: **changed-file flake8 passed; preview wheel build passed; whitespace
check passed**. The exact embedded Bash also passed `bash -n`, and changed
documentation relative links were validated. A fixture continuation indentation
was normalized without changing its command text.

Validation limits are explicit: repository discovery in `azdev style` stalled
and was stopped, so that attempt is not counted as passed. The broader documented
full-package flake8 command reports `F401` for the unchanged side-effect help
registration import in `__init__.py`; its content was verified against the PR
baseline and was not changed as part of this fix. No lint rules, registered
repositories, installed tools, or release metadata were modified.

The older live records below are historical and are not acceptance evidence for
this newly changed payload.

## VM-wide ADE exclusion regression update (2026-11-24)

The control-plane preflight now rejects ADE on OS or data disks, custom-named
Linux/Windows ADE handlers, unknown or residual encryption settings, incomplete
inventory and API failures. Guest commands and controller/disk writes must not
run after rejection. SSE/encryption at host and returning to SCSI remain separate
from the NVMe ADE exclusion.

Run the existing workflow tests and unchanged EFI regressions with:

```bash
python3 -B -m pytest \
  azext_nvme_conversion/tests/latest/test_nvme_conversion.py \
  azext_nvme_conversion/tests/latest/test_linux_efi_timeout.py \
  -k "not NvmeConversionCheckTest and not NvmeConversionConvertTest" -v
```

The new tests use mocked Azure responses, not encrypted live VMs. The versioned
`nvmeEligibility` output is diagnostic metadata; ALAR no longer consumes or
requires it. Its local BEK/encryption guard is validated separately. These are ADE-refusal tests, not
successful ADE conversion or decryption certification. No new VMs are deployed.

## RHEL 7 standalone EFI regression update (2026-11-23)

The embedded Linux script now repairs the resolved RHEL 7 standalone EFI
configuration even when defaults or another generated file already contain
`nvme_core.io_timeout=240`. It checks every kernel entry, rejects incorrect,
duplicate, or conflicting timeout arguments, and preserves dry-run and repeat
behavior. Modern redirect stubs are not overwritten.

Run the 13 isolated regressions from the repository root on Linux as root:

```bash
python3 -B -m unittest discover \
  -s src/nvme-conversion/azext_nvme_conversion/tests/latest \
  -p test_linux_efi_timeout.py -v
```

Result: **13 passed**. The tests execute the actual embedded timeout functions
in temporary chroots with existing Bash/coreutils/awk tools and stubbed GRUB
generation. They make no Azure calls, mounts, or package installations, and
require no ALAR checkout. Other hosts explicitly skip them.

The existing documented extension unit command also passed: **58 tests passed,
2 live scenario tests deselected**. Separately, ALAR/shared-script validation
passed **37 unit tests and 191 differential fixtures**.

Live validation used the exact image `RedHat:RHEL:79-gen2:7.9.2023030110`.
A rebuilt ALAR candidate embedding the corrected script completed actual
check/dry-run/apply/repeat, SCSI/NVMe/second-NVMe/SCSI rollback, runtime timeout
240 on both NVMe boots, repeat identity, and a native missing-timeout fault
repair. This is shared-script/ALAR validation, not a new end-to-end execution
of `az nvme-conversion convert`. Both existing VMs were deallocated afterward;
no new VMs were created. Stable public SSH acceptance remains separate.

The historical live tracker below is retained unchanged.

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
