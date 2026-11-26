# Readiness correctness rationale

## Linux: module packages are not installed kernels

RHEL 9.8 can contain a module directory for an older kernel release even when
that kernel is not installed. The observed layout contains:

| Item | Value |
| --- | --- |
| Installed/default/running kernel | `5.14.0-687.59.1.el9_8.x86_64` |
| Additional module directory | `5.14.0-687.2.1.el9_8.x86_64` |
| File in that directory | `extra/kmod-kvdo/vdo/kvdo.ko` |
| Owning package | `kmod-kvdo-8.2.7.4-189.el9_8.x86_64` |
| Older kernel package, kernel image, initramfs and BLS entry | Absent |
| Actual installed kernel's NVMe and Hyper-V PCI drivers | Present |

Treating every `/lib/modules` directory as an installed kernel incorrectly
requires an initramfs for the module package's older release. Preparation then
reports a missing boot image even though the actual boot kernel is ready.
Rebooting does not fix this directory-based error.

This is a false readiness failure on a legitimate package layout, not a new
platform feature or evidence that the installed kernel lacks NVMe drivers.
Normal conversion correctly stops before controller/disk changes, but the false
failure blocks supported conversions. Deleting a package-owned module or
bypassing OS checks is not an acceptable workaround.

### Correction and safety invariants

Kernel releases are derived from installed kernel package file lists, actual
kernel images, and GRUB/BLS references. A module-only directory is not a kernel.
Debug/header artifacts and rescue-image aliases are excluded.

Package file lists retain references to missing images, so genuine installed or
boot-referenced kernels are not silently skipped. Missing genuine module
directories, failed package queries, missing required boot images/drivers and
failed repairs still block readiness.

Check remains read-only, fixes remain opt-in, and Linux dry-run continues to
stage instead of applying changes. No command, flag, VM-size policy, SDK/API,
ADE gate, dependency, release version or supported-platform change is required.

### Validation

The Linux correction was validated by the focused readiness/EFI suite:
**42 tests and 51 subtests**. It covers:

- The package-owned module-only directory in check/fix/dry-run modes.
- Multiple genuine installed kernels.
- Missing package-listed and boot-referenced boot images.
- Failed package queries without protected-file mutation.
- Debug/header files and rescue aliases.
- Existing driver rebuild, fstab and standalone EFI behavior.

Changed Python files pass lint, the embedded Bash passes syntax validation, and
the preview wheel builds with the expected source. Full-package lint retains
an unchanged help-registration import warning; that validation limit is recorded
in [TESTING.md](TESTING.md). The fixture tests use disposable chroots, not Azure
VMs or real block-device mounts.

### Release-scope rationale

This is a correction to advertised readiness behavior on an already-supported
OS. It removes a demonstrated false negative while preserving genuine failure
gates. It does not expand the feature or support scope.

The correction can be reviewed as bounded correctness work within the proposed
January 2027 release. It does not itself authorize an earlier release or alter
the release schedule. Historical live results must not be treated as acceptance
of a newly changed CLI payload.

## Windows: complete boot readiness and durable NVMe parameters

The Windows correction follows guest preparation in
[Azure-NVMe-Conversion.ps1](https://github.com/Azure/SAP-on-Azure-Scripts-and-Utilities/blob/main/Azure-NVMe-Utils/Azure-NVMe-Conversion.ps1)
from **Azure/SAP-on-Azure-Scripts-and-Utilities**. Its public source describes
Windows boot failures and NVMe parameters being reset by first-device
installation.

Checking only `stornvme`/`vpci` Start and override values can report readiness
when the driver binary is absent, PCI is not boot-start, or required NVMe
parameters are missing. Pre-shutdown registry readback alone also does not
provide a synchronous persistence guarantee.

### Required state and correction

Every ControlSet is checked for:

| Setting | Required state |
| --- | --- |
| Driver binary | `stornvme.sys` exists |
| `stornvme`, `vpci`, `pci` Start | DWORD `0` |
| `stornvme`/`vpci` StartOverride | Absent |
| `pci` StartOverride | Allowed and preserved |
| `stornvme\Parameters\IoTimeoutValue` | DWORD `240` |
| `stornvme\Parameters\BusType` | DWORD `17` |
| `stornvme\Parameters\StorageSupportedFeatures` | DWORD `3` |
| `stornvme\Parameters\PnpInterface\5` | DWORD `1` |

Fixes wait for and validate `sc.exe`, set the required DWORD values, remove only
the blocking NVMe/virtual-PCI overrides, and flush registry state before reporting
success. If the SYSTEM flush fails, all affected service keys must flush
successfully. Readback and complete confirmations remain mandatory; failures
cannot produce a readiness result.

With a normal Windows NVMe start, the flow waits for running/guest-agent-ready
and verifies that the OS disk is actually enumerated as NVMe. With `--fix-os`,
it reapplies parameters after first boot, flushes them, performs a controlled
restart, and verifies settings again after guest readiness.

Without `--fix-os`, verification is read-only. Deferred and `--no-wait` starts
report pending post-boot work and provide verification guidance rather than
silently claiming guest readiness. Explicit `check --controller-type NVMe` on
an already-converted Windows VM performs the same read-only runtime checks.
Start/verification failures explicitly report that VM conversion may already
have occurred; there is no automatic rollback or peer-VM shutdown.

### Scope and validation

The correction does not replace the SDK VM-update API, change supported Windows
releases, add Windows dry-run, install dependencies or alter a release milestone.
The PowerShell-specific read-only VM-model workaround is not required by the
assessed SDK serializer, which omits the cited output-only disk fields.

The combined suite passes **129 tests and 80 subtests**, with live scenarios
excluded. Native PowerShell executes the actual guest scripts against virtual
registry/disk handles, covering missing binaries, incorrect/missing parameters,
type mismatches, permitted PCI overrides, successful fixes, flush fallback,
flush/readback/SC failures and non-NVMe runtime state. Orchestration regressions
cover restart persistence, read-only validation, bounded agent waits, deferred
and no-wait starts, disabled checks and explicit partial-conversion failures.

No real host registry writes or Azure VM operations are performed by these
tests. They are not live Windows boot certification; real boot/reboot validation
on supported Windows releases and Standard/Trusted Launch remains a release
acceptance requirement.

This is existing boot-safety and persistence correctness work, not a new
conversion command or platform expansion. Its opt-in repair/restart behavior
and explicit deferred state should be reviewed with the proposed January
release scope. The release schedule is not changed by these commits.
