# NVMe Conversion Extension — Development Guide

## Origin & Context

This extension is a modernized Azure CLI port of the PowerShell script
[Azure-NVMe-Conversion.ps1](https://github.com/Azure/SAP-on-Azure-Scripts-and-Utilities/tree/main/Azure-NVMe-Utils)
from the SAP-on-Azure-Scripts-and-Utilities repository. The original script (1,323 lines of PowerShell)
was converted to a Python-based Azure CLI extension following the
[Azure CLI extension authoring guidelines](https://github.com/Azure/azure-cli/blob/dev/doc/extensions/authoring.md).

## Reference Documentation

### Azure CLI Extension Development

| Resource | URL |
|---|---|
| Extension authoring guide | https://github.com/Azure/azure-cli/blob/dev/doc/extensions/authoring.md |
| Extension metadata spec | https://github.com/Azure/azure-cli/blob/dev/doc/extensions/metadata.md |
| Extension versioning guidelines | https://github.com/Azure/azure-cli/blob/dev/doc/extensions/versioning_guidelines.md |
| Extension summary guidelines | https://github.com/Azure/azure-cli/blob/dev/doc/extensions/extension_summary_guidelines.md |
| Extension FAQ | https://github.com/Azure/azure-cli/blob/dev/doc/extensions/faq.md |
| Authoring commands guide | https://github.com/Azure/azure-cli/blob/main/doc/authoring_command_modules/authoring_commands.md |
| azdev CLI dev tools | https://github.com/Azure/azure-cli-dev-tools |
| azure-cli-extensions repo | https://github.com/Azure/azure-cli-extensions |

### Azure NVMe & Disk Controller

| Resource | URL |
|---|---|
| Original PowerShell script | https://github.com/Azure/SAP-on-Azure-Scripts-and-Utilities/tree/main/Azure-NVMe-Utils |
| Azure NVMe overview | https://learn.microsoft.com/azure/virtual-machines/enable-nvme-interface |
| VM sizes with NVMe support | https://learn.microsoft.com/azure/virtual-machines/sizes/overview |
| Disk controller types API | `DiskControllerTypes` capability in `resource_skus.list()` |
| az vm update --disk-controller-type | https://learn.microsoft.com/cli/azure/vm#az-vm-update (Preview) |
| azure-vm-utils (udev rules) | https://github.com/Azure/azure-vm-utils |

### Python SDK

| Package | Used for |
|---|---|
| `azure-mgmt-compute` (bundled in CLI core) | VM, disk, extension, SKU, RunCommand operations |
| `azure.cli.core.azclierror` | Semantic error types (ValidationError, ResourceNotFoundError, InvalidArgumentValueError) |
| `azure.cli.core.commands.parameters` | `get_enum_type` for --controller-type |
| `azure.cli.testsdk` | ScenarioTest base class for live tests |

## Architecture

```
azext_nvme_conversion/
├── __init__.py              # CommandsLoader — entry point
├── commands.py              # Command registration + table formatters
├── _params.py               # Argument definitions + validators
├── _help.py                 # Help text (YAML-like format)
├── _validators.py           # Parameter validators (vm_size, sleep_seconds)
├── _format.py               # Table output formatters for -o table
├── _client_factory.py       # ComputeManagementClient factory
├── custom.py                # Core orchestration logic (convert + check)
├── _windows_checks.py       # Windows: version check + stornvme driver
├── _linux_checks.py         # Linux: RunCommand wrapper
├── _linux_script.py         # Embedded 500-line bash script
├── azext_metadata.json      # Extension metadata (preview, min CLI version)
└── tests/latest/
    └── test_nvme_conversion.py  # 56 unit + integration tests
```

### Data Flow

```
User runs: az nvme-conversion convert -g myRG -n myVM --start-vm

  ┌─ custom.py ────────────────────────────────────────────────────────────────────────────┐
  │ [1/8] _validate_vm()         → ComputeClient.virtual_machines.get()                    │
  │ [2/8] _resolve_vm_size()     → ComputeClient.resource_skus.list()                      │
  │ [3/8] _check_ade_extension() → ComputeClient.virtual_machine_extensions.get()          │
  │       _check_vm_generation() → ComputeClient.disks.get()                               │
  │       _check_vm_power_state()→ ComputeClient.virtual_machines.instance_view()          │
  │ [4/8] _validate_sku()        → ComputeClient.resource_skus.list()                      │
  │ [5/8] _prepare_os()          → _windows_checks.py or _linux_checks.py                  │
  │       └─ RunCommand           → ComputeClient.virtual_machines.begin_run_command()     │
  │ [6/8] _stop_vm()             → ComputeClient.virtual_machines.begin_deallocate()       │
  │ [7/8] _update_disk_capabilities() → ComputeClient.disks.begin_update()                 │
  │       _update_vm()           → ComputeClient.virtual_machines.begin_create_or_update() │
  │ [8/8] _start_vm()            → ComputeClient.virtual_machines.begin_start()            │
  └────────────────────────────────────────────────────────────────────────────────────────┘
```

## Development Setup

### Prerequisites

- Python 3.10+ (CLI supports 3.10–3.13)
- Azure CLI installed (`az --version`)
- WSL (for Linux testing) or native Linux

### Quick Start (without azdev)

```bash
cd src/nvme-conversion

# Build wheel
python3 setup.py bdist_wheel

# Install extension
az extension remove -n nvme-conversion 2>/dev/null
az extension add --source dist/nvme_conversion-1.0.0b1-py3-none-any.whl --yes

# Run tests
python3 -m pytest azext_nvme_conversion/tests/latest/test_nvme_conversion.py -v \
    -k "not NvmeConversionCheckTest and not NvmeConversionConvertTest"

# Lint
python3 -m flake8 --max-line-length=120 --ignore=E501,W503,W504,C901 \
    --exclude=_linux_script.py azext_nvme_conversion/*.py
```

### Full Setup (with azdev)

```bash
# Create virtual environment
python3 -m venv .venv-azdev
source .venv-azdev/bin/activate

# Install azdev
pip install azdev

# Setup with extension repo
azdev setup -r <path-to-azure-cli-extensions> -e nvme-conversion

# Validate (run before every PR)
azdev style nvme-conversion
azdev test nvme-conversion
azdev linter nvme-conversion
```

## Key Design Decisions

### Why custom commands (not AAZ)?

The extension orchestrates **8 sequential Azure API calls** (VM get → extension check → SKU check →
RunCommand → VM stop → disk PATCH → VM update → VM start). AAZ is designed for single-resource
CRUD operations. Custom orchestration with `custom.py` is required.

### SDK vs Raw REST

The original PowerShell script uses `Invoke-RestMethod` with a bearer token for the disk PATCH.
We use `ComputeManagementClient.disks.begin_update()` which provides automatic auth, retry,
and error handling.

### Error types

| Error type | When used |
|---|---|
| `ResourceNotFoundError` | VM not found |
| `ValidationError` | Gen1, ADE installed, OS not ready, VM not deallocated |
| `InvalidArgumentValueError` | Bad SKU, SKU doesn't support target controller, invalid --vm-size |

### SKU DiskControllerTypes behavior

| `DiskControllerTypes` value | Meaning | NVMe target | SCSI target |
|---|---|---|---|
| `"SCSI, NVMe"` | Both supported | OK | OK |
| `"NVMe"` | NVMe only (v6+) | OK | BLOCKED |
| `"SCSI"` | SCSI only | BLOCKED | OK |
| absent | SCSI only (old SKUs) | BLOCKED | OK |

### Udev rules strategy

When `azure-vm-utils` is not installed and `--fix-os` is used, the extension deploys a fallback
udev rule (`99-azure-nvme-fallback.rules`) that provides:
- `io_timeout=240s` for NVMe remote disks
- `/dev/disk/azure/root` and `/dev/disk/azure/data/by-lun/N` symlinks

It does NOT provide `by-name`, `by-serial`, `by-index` (those require the `azure-nvme-id` binary
from `azure-vm-utils`). The fallback rule is numbered 99 so `80-azure-disk.rules` takes precedence
when `azure-vm-utils` is later installed.

## Testing

### Unit tests (56 tests)

```bash
python3 -m pytest azext_nvme_conversion/tests/latest/test_nvme_conversion.py -v \
    -k "not NvmeConversionCheckTest and not NvmeConversionConvertTest"
```

Test categories:
- **NvmeConversionUnitTests** (16): OS detection, controller resolution, Windows version, VM generation
- **WindowsChecksUnitTests** (5): RunCommand result parsing, fix mode
- **LinuxChecksUnitTests** (5): RunCommand result parsing, fix/dry-run modes
- **ValidatorUnitTests** (6): vm_size format, sleep_seconds range
- **ResolveVmSizeTests** (8): Auto-size resolution, SKU capability handling
- **ConvertEndToEndTests** (11): Full mocked convert flow
- **CheckEndToEndTests** (6): Full mocked check flow

### Live tests

See `TESTING.md` for the full test tracker. Live tests were run against:
- Ubuntu 24.04, RHEL 9 LVM, SLES 15 SP6, Azure Linux 4, Windows Server 2022, Windows Server 2019
- Both WSL and Windows Command Prompt CLIs
- SCSI→NVMe and NVMe→SCSI conversions
- Edge cases: already-on-target, dry-run, --no-wait, --ignore-os-check
- Batch conversion: 13 RHEL Gen2 VMs across 2 resource groups

### azdev validation

```bash
source ~/azdev-env/bin/activate
azdev style nvme-conversion    # Pylint PASSED, Flake8 PASSED
azdev test nvme-conversion     # 56 passed, 2 skipped
azdev linter nvme-conversion   # Requires ssh extension fix (unrelated)
```

## Versioning

Following [Azure CLI extension versioning guidelines](https://github.com/Azure/azure-cli/blob/dev/doc/extensions/versioning_guidelines.md):

- Current version: `1.0.0b1` (initial preview)
- Preview versions use `X.Y.ZbN` format
- `azext_metadata.json` sets `azext.isPreview: true`

## Publishing

For extensions hosted in `Azure/azure-cli-extensions`, publishing is automatic:
1. Merge code to `main` branch
2. The CI detects the version via `python setup.py --version`
3. If version is new, CI builds the wheel, uploads it, and updates `src/index.json`
4. A PR is auto-created for the index update
5. After merge, the extension is available via `az extension add -n nvme-conversion`

Manual `index.json` updates are NOT required.

## Files Reference

| File | Purpose | Lines |
|---|---|---|
| `setup.py` | Package metadata, version, dependencies | ~55 |
| `setup.cfg` | Empty (convention) | 1 |
| `README.md` | User-facing documentation | ~45 |
| `HISTORY.rst` | Release history (reStructuredText, repo convention) | ~12 |
| `ROADMAP.md` | Development roadmap with checkboxes | ~300 |
| `TESTING.md` | Live test tracker with results | ~100 |
| `DEVELOPMENT.md` | This file | ~200 |
| `azext_metadata.json` | Extension metadata (preview, min CLI version) | 4 |
| `__init__.py` | CommandsLoader entry point | ~30 |
| `commands.py` | Command registration + formatters | ~15 |
| `_params.py` | Argument definitions | ~50 |
| `_help.py` | Help text with examples | ~80 |
| `_validators.py` | Parameter validators | ~30 |
| `_format.py` | Table output formatters | ~40 |
| `_client_factory.py` | SDK client factory | ~10 |
| `custom.py` | Core orchestration logic | ~560 |
| `_windows_checks.py` | Windows OS checks/fixes | ~95 |
| `_linux_checks.py` | Linux OS checks/fixes | ~80 |
| `_linux_script.py` | Embedded bash script (~500 lines) | ~520 |
| `tests/.../test_nvme_conversion.py` | 56 unit + integration tests | ~670 |
