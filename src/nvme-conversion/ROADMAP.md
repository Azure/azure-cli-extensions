# Azure NVMe Conversion Extension — Analysis & Roadmap

## 1. Script Analysis

### Source Script
`Azure-NVMe-Conversion.ps1` — 1,323 lines of PowerShell that orchestrates the conversion of Azure VMs between SCSI and NVMe disk controllers.

### What the Script Does (Logical Flow)

```
┌─────────────────────────────────────────────────┐
│ 1. VALIDATION PHASE                             │
│   ├─ Check Azure context / authentication       │
│   ├─ Get VM, verify it exists                   │
│   ├─ Check Azure Disk Encryption (block ADE)    │
│   ├─ Check VM power state (must be running)     │
│   ├─ Detect OS (Windows / Linux)                │
│   ├─ Check Windows version (>= 2019)            │
│   ├─ Check VM generation (must be Gen2)         │
│   └─ Check current controller (SCSI vs NVMe)    │
│                                                 │
│ 2. SKU VALIDATION PHASE                         │
│   ├─ Get compute resource SKUs for region       │
│   ├─ Validate target SKU exists in zone         │
│   ├─ Check resource disk compatibility          │
│   └─ Verify target SKU supports NVMe/SCSI       │
│                                                 │
│ 3. OS PREPARATION PHASE                         │
│   ├─ Windows: Check stornvme driver via         │
│   │   RunCommand, optionally fix                │
│   └─ Linux: Run embedded bash script via        │
│       RunCommand that:                          │
│       ├─ Checks NVMe driver in initrd/initramfs │
│       ├─ Checks nvme_core.io_timeout parameter  │
│       ├─ Checks /etc/fstab for deprecated devs  │
│       ├─ Optionally fixes all issues            │
│       └─ Supports dry-run staging               │
│                                                 │
│ 4. CONVERSION PHASE                             │
│   ├─ Shutdown VM (Stop-AzVM)                    │
│   ├─ Update OS disk capabilities via REST API   │
│   │   (PATCH disk supportedCapabilities)        │
│   ├─ Update VM size + DiskControllerType        │
│   └─ Optionally start VM                        │
│                                                 │
│ 5. POST-CONVERSION                              │
│   └─ Output revert instructions                 │
└─────────────────────────────────────────────────┘
```

### Key Azure SDK Operations Required

| PS Script Operation | Python SDK Equivalent |
|---|---|
| `Get-AzContext` | `azure.cli.core` (handled by CLI framework) |
| `Get-AzVM` | `ComputeManagementClient.virtual_machines.get()` |
| `Get-AzVMExtension` | `ComputeManagementClient.virtual_machine_extensions.get()` |
| `Get-AzVM -Status` | `ComputeManagementClient.virtual_machines.instance_view()` |
| `Get-AzDisk` | `ComputeManagementClient.disks.get()` |
| `Get-AzComputeResourceSku` | `ComputeManagementClient.resource_skus.list()` |
| `Invoke-AzVMRunCommand` | `ComputeManagementClient.virtual_machines.begin_run_command()` |
| `Stop-AzVM` | `ComputeManagementClient.virtual_machines.begin_deallocate()` |
| `Start-AzVM` | `ComputeManagementClient.virtual_machines.begin_start()` |
| `Update-AzVM` | `ComputeManagementClient.virtual_machines.begin_create_or_update()` |
| `Invoke-RestMethod` (disk PATCH) | `ComputeManagementClient.disks.begin_update()` |

---

## 2. Extension Design

### Extension Name
`nvme-conversion`

### Package Name
`azext_nvme_conversion`

### Command Group & Commands

```
az nvme-conversion
├── convert     # Full conversion (SCSI→NVMe or NVMe→SCSI)
├── check       # Pre-flight validation only (no changes)
└── revert      # Convenience: convert back to original controller
```

### Command: `az nvme-conversion convert`

| Parameter | CLI Flag | Type | Required | Description |
|---|---|---|---|---|
| resource_group | `--resource-group -g` | str | Yes | Resource group of the VM |
| vm_name | `--vm-name -n` | str | Yes | VM name |
| new_controller_type | `--controller-type` | str (NVMe/SCSI) | No (default: NVMe) | Target controller type |
| vm_size | `--vm-size` | str | Yes | Target VM size/SKU |
| start_vm | `--start-vm` | bool | No | Start VM after conversion |
| fix_os | `--fix-os` | bool | No | Auto-fix OS settings |
| ignore_sku_check | `--ignore-sku-check` | bool | No | Skip SKU validation |
| ignore_os_check | `--ignore-os-check` | bool | No | Skip OS readiness check |
| ignore_windows_version | `--ignore-windows-version-check` | bool | No | Skip Windows version check |
| dry_run | `--dry-run` | bool | No | Linux only: stage changes without applying |
| sleep_seconds | `--sleep-seconds` | int | No (default: 15) | Delay before starting VM |
| yes | `--yes -y` | bool | No | Skip confirmation prompts |

### Command: `az nvme-conversion check`

Same parameters as `convert` minus `--start-vm`, `--fix-os`, `--sleep-seconds`. Runs all validation steps and OS checks without making changes.

### Command: `az nvme-conversion revert`

| Parameter | CLI Flag | Type | Required | Description |
|---|---|---|---|---|
| resource_group | `--resource-group -g` | str | Yes | Resource group of the VM |
| vm_name | `--vm-name -n` | str | Yes | VM name |
| original_vm_size | `--original-vm-size` | str | Yes | Original VM size to revert to |
| start_vm | `--start-vm` | bool | No | Start VM after revert |

---

## 3. Directory Structure

```
src/nvme-conversion/
├── setup.py
├── setup.cfg
├── README.md
├── HISTORY.rst
└── azext_nvme_conversion/
    ├── __init__.py              # CommandsLoader
    ├── commands.py              # Command registration
    ├── _params.py               # Argument definitions
    ├── _help.py                 # Help text
    ├── _validators.py           # Parameter validators
    ├── custom.py                # Core conversion logic
    ├── _client_factory.py       # SDK client factory
    ├── _vm_operations.py        # VM operations (get, stop, start, update)
    ├── _sku_operations.py       # SKU validation logic
    ├── _os_preparation.py       # OS checks & fixes (Windows + Linux)
    ├── _disk_operations.py      # Disk update operations
    ├── azext_metadata.json      # Extension metadata
    ├── scripts/
    │   └── linux_nvme_check.sh  # Extracted Linux bash script
    └── tests/
        ├── __init__.py
        └── latest/
            ├── __init__.py
            ├── test_nvme_conversion.py         # Scenario tests
            ├── test_validators.py              # Unit tests for validators
            ├── test_os_preparation.py          # Unit tests for OS prep
            └── recordings/                     # VCR test recordings
```

---

## 4. Implementation Roadmap

### Phase 1: Scaffold & Core Infrastructure
**Estimated complexity: Low**

- [x] 1. **Create extension scaffold**
   - [x] `setup.py`, `setup.cfg`, `README.md`, `HISTORY.rst`
   - [x] `azext_metadata.json`
   - [x] `__init__.py` with `CommandsLoader`
   - [x] Empty `commands.py`, `_params.py`, `_help.py`

- [x] 2. **Client factory** (`_client_factory.py`)
   - [x] Create `ComputeManagementClient` from CLI context
   - [x] Handle subscription context

- [x] 3. **Register commands** (`commands.py`)
   - [x] `nvme-conversion convert`
   - [x] `nvme-conversion check`
   - [x] `nvme-conversion revert` — *not needed: `convert --controller-type SCSI` handles this*

- [x] 4. **Define parameters** (`_params.py`)
   - [x] All arguments with types, validators, help text
   - [x] Enum choices for `--controller-type`

- [x] 5. **Define help text** (`_help.py`)
   - [x] Command group help
   - [x] Per-command help with examples

### Phase 2: Validation Logic
**Estimated complexity: Medium**

- [x] 6. **VM validation** (`custom.py`)
   - [x] `_validate_vm()` — fetch VM, raise if not found
   - [x] `_check_vm_power_state()` — check power state
   - [x] `_check_ade_extension()` — block ADE for Linux
   - [x] `_check_vm_generation()` — must be Gen2
   - [x] `_check_current_controller()` — detect SCSI/NVMe
   - [x] `_detect_os_type()` — Windows vs Linux
   - [x] `_check_windows_version()` — >= 2019

- [x] 7. **SKU validation** (`custom.py`)
   - [x] `_validate_sku()` — target SKU exists
   - [x] Zone availability check
   - [x] Controller support check
   - [x] Resource disk compatibility (Windows)

- [x] 8. **Validators** (`_validators.py`)
   - [x] `validate_vm_size` — must match Standard_* pattern
   - [x] `validate_sleep_seconds` — non-negative, max 600

### Phase 3: OS Preparation
**Estimated complexity: High**

- [x] 9. **OS preparation** (`custom.py`)
   - [x] `_prepare_windows()` — run stornvme check/fix via RunCommand
   - [x] `_prepare_linux()` — run bash script via RunCommand
   - [x] `_check_os_readiness()` — check-only wrapper

- [x] 10. **Linux bash script** (`_linux_script.py`)
    - [x] Extract the embedded ~453-line bash script
    - [x] Parameterize it (accept `-fix` and `-dryrun` flags)
    - [x] Wrap in `get_linux_check_script()` function

### Phase 4: Conversion Operations
**Estimated complexity: Medium**

- [x] 11. **Disk operations** (`custom.py`)
    - [x] `_update_disk_capabilities()` — update OS disk supportedCapabilities
    - [x] Use `disks.begin_update()` instead of raw REST

- [x] 12. **VM operations** (`custom.py`)
    - [x] `_stop_vm()` — deallocate
    - [x] `_start_vm()` — start with optional delay
    - [x] `_update_vm()` — resize + set DiskControllerType

### Phase 5: Command Orchestration
**Estimated complexity: Medium**

- [x] 13. **`convert` command** (`custom.py`)
    - [x] Orchestrate: validate → check OS → confirm → shutdown → update disk → update VM → start
    - [x] Progress output via `logger.warning()` for user-visible messages
    - [x] Handle `--yes` for non-interactive mode (via `confirmation=True`)
    - [x] Handle `--dry-run` for Linux

- [x] 14. **`check` command** (`custom.py`)
    - [x] Run validation + OS checks only, output report
    - [x] Return structured JSON with pass/fail per check

- [x] 15. **`revert` command** — *not needed: `convert --controller-type SCSI` handles this*

### Phase 6: Testing
**Estimated complexity: High**

- [x] 16. **Unit tests** (`test_nvme_conversion.py`)
    - [x] Test OS type detection (Windows, Linux, None)
    - [x] Test controller state detection
    - [x] Test Windows version validation
    - [x] Test VM generation check (V1 blocked, V2 passes)
    - [x] Test Linux script content validation

- [x] 17. **Unit tests — OS preparation**
    - [x] Mock RunCommand responses
    - [x] Test Windows check parsing (pass, Start error, StartOverride error)
    - [x] Test Linux script output parsing (pass, error, fix mode, dry-run mode)

- [x] 18. **Scenario tests** (`test_nvme_conversion.py`)
    - [x] Mocked end-to-end convert: SCSI→NVMe, NVMe→SCSI
    - [x] Mocked end-to-end check: pass, gen1 fail, ADE fail, VM not found
    - [x] Convert already-on-target returns no-change
    - [x] Convert with start-vm / without start-vm / no-wait
    - [x] Convert dry-run stops before shutdown
    - [x] Convert includes revert command for NVMe target
    - [x] VM size auto-resolution tests (4 tests)

- [x] 19. **Live tests**
    - [x] Ubuntu, RHEL, SLES, Azure Linux 4, Windows 2022, Windows 2019
    - [x] Full conversion round-trip (SCSI→NVMe→SCSI)

### Phase 7: Polish & Release
**Estimated complexity: Low**

- [x] 20. **Error handling**
    - [x] User-friendly error messages
    - [x] Actionable suggestions on failure
    - [x] Revert instructions on conversion failure
    - [x] `--no-wait` support for long operations

- [x] 21. **Output formatting**
    - [x] Table format for check results
    - [x] JSON output for automation
    - [x] Table format for convert results

- [x] 22. **Documentation**
    - [x] `README.md` with usage examples
    - [x] `HISTORY.rst` with initial version
    - [x] Help text with realistic examples

- [x] 23. **CI integration**
    - [x] Linting (`flake8`) — all files pass
    - [x] Pylint — 9.89/10, all issues fixed
    - [x] `azdev style nvme-conversion` — PASSED
    - [x] All Python files compile without errors
    - [x] `azdev linter` — PASSED (1 issue fixed: added --ignore-win-ver short alias)
    - [ ] Register in `src/index.json` (auto on merge to main)

---

## 5. Key Design Decisions

### Why NOT use AAZ (Auto-generated commands)?
The script orchestrates **multiple Azure operations** (VM get → extension check → SKU check → RunCommand → VM stop → disk PATCH → VM update → VM start). AAZ is designed for single-resource CRUD operations mapping to a single REST endpoint. This extension requires custom orchestration logic.

### SDK vs Raw REST
The original script uses `Invoke-RestMethod` for the OS disk PATCH. The Python SDK's `disks.begin_update()` can achieve the same result without raw REST calls, which is cleaner and benefits from SDK retry/error handling.

### Embedded Bash Script
The ~500-line Linux bash script will be kept as a string constant in `_os_preparation.py` (or loaded from `scripts/linux_nvme_check.sh`). It's sent to the VM via RunCommand — it never executes locally.

### Confirmation Prompts
The original script uses `Read-Host` for confirmation. The CLI extension will use `--yes/-y` for non-interactive mode and `az cli`'s built-in confirmation via `user_confirmation()`.

### Logging
PowerShell's `WriteRunLog` maps to Python's `logger`:
- `INFO` → `logger.info()` (only shown with `--debug`)
- `WARNING` → `logger.warning()` (always shown)
- `ERROR` → `raise CLIError()` or `raise ValidationError()`
- `IMPORTANT` → `logger.warning()` with prominent formatting

---

## 6. Dependencies

```python
DEPENDENCIES = [
    'azure-mgmt-compute>=33.0.0',
]
```

The `azure-mgmt-compute` package provides:
- `ComputeManagementClient` — VM, disk, extension, SKU operations
- `VirtualMachine`, `Disk`, `RunCommandInput` models

---

## 7. Risk Assessment

| Risk | Impact | Mitigation |
|---|---|---|
| Long-running operations (VM stop/start) | User confusion | Progress indicators, `--no-wait` support |
| RunCommand timeout on large VMs | Script appears stuck | Set explicit timeouts, stream output |
| SKU API returns stale data | Wrong validation result | Cache with TTL, warn user |
| Linux bash script fails on unknown distro | Conversion proceeds without OS prep | Fail-safe: block conversion if OS check fails |
| Disk PATCH fails | Disk in inconsistent state | Disk update is safe — no data loss, retry-able |
| VM won't start after conversion | VM stuck deallocated | Provide revert command with original size |

---

## 8. Testing Strategy

### Test Pyramid

```
          ┌──────────────┐
          │  Live Tests  │  ← Optional, CI-gated, real Azure resources
          │   (2-3)      │
         ┌┴──────────────┴┐
         │ Scenario Tests │  ← Recorded HTTP, full command flow
         │    (8-10)      │
        ┌┴────────────────┴┐
        │    Unit Tests    │  ← Mocked, fast, high coverage
        │     (20-30)      │
        └──────────────────┘
```

### Unit Tests
- Validator functions with various inputs
- SKU capability parsing
- OS type detection
- Windows/Linux check output parsing
- Error condition handling

### Scenario Tests (with VCR recordings)
- Happy path: SCSI → NVMe conversion
- Happy path: NVMe → SCSI conversion
- Check command output format
- Revert command
- Error: VM not found
- Error: Gen1 VM blocked
- Error: ADE detected
- Error: SKU doesn't support NVMe
- Error: Windows version too old
- Dry-run mode (Linux)

### Live Tests
- Full round-trip conversion on a test VM
- Verify VM boots correctly after conversion
- Verify disk controller type changed
