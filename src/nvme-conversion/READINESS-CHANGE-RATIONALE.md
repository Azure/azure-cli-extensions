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

The focused readiness/EFI suite passes **42 tests and 51 subtests**. It covers:

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
