# Azure Migrate Runbooks CLI — Implementation & Architecture Plan

> Status: **Design only. No implementation code is produced in this phase.**
> Scope boundary: **all new code lives under `src/migrate/azext_migrate/`.**
> `k8s-extension` is studied as a *reference pattern only* — nothing is imported from it.

---

## 0. Agent execution prerequisites (read first)

This section makes the plan runnable by an autonomous agent. Everything below is *execution fact*, not
architecture — do these before Phase 0 (§15).

### 0.1 Environment bootstrap (one-time)

```pwsh
# activate the existing venv (root: C:\virtual\environment)
& C:\virtual\environment\Scripts\Activate.ps1     # or: python -m venv <path> to create a new one
pip install azdev
# from the repo root (azure-cli-extensions):
azdev setup --repo .                                # wires azure-cli + this ext repo
azdev extension add migrate                         # make the migrate ext importable/dev-installed
az extension list                                   # confirm 'migrate' is a dev extension
```

Everything the `Verify` gates run (`azdev style|linter|test migrate`) requires this to be done once. If
`azdev` is unavailable, STOP and escalate — do not hand-roll pytest.

### 0.2 Concrete constants to pin (fill before writing `constants.py`)

The design references these but the **literal values must be read from the spec** (`spec/Runbooks/*`,
`spec/RunbookExecutions/*`) or confirmed with the service owner — do NOT invent them:

| Constant | Where it lives | Source of truth | Status |
| --- | --- | --- | --- |
| `RUNBOOKS_API_VERSION` = `"2020-06-01-preview"` | `shared/constants.py` | `api-version=` in the spec YAMLs | **confirmed** |
| Provider namespace + type-segment casing (`Microsoft.Migrate` / `migrateProjects` / `runbooks` / `executions`) | `shared/constants.py` | resource IDs + returned `type` in the spec YAMLs | **confirmed** — canonical ID `/subscriptions/{s}/resourceGroups/{rg}/providers/Microsoft.Migrate/migrateProjects/{p}/runbooks/{n}/executions/{e}` (camelCase `migrateProjects`). Note: existing `local`/replication code uses lowercase `migrateprojects` (`helpers/_server.py`); ARM path is case-insensitive so both work, but new runbook code pins this canonical casing for stable recordings + `id` parsing |
| `scopeType` value (`"Wave"`) + `waveId` template | `runbook/constants.py`, `models.build_generate_body` | CreateRunbook body in spec | confirmed (§1.3.3) — scope is polymorphic; discriminator `scopeType` is matched **case-sensitively**, so the payload uses camelCase (`scopeType`/`waveId`), verified live against the service |
| `RunbookExecutionAction` codes | `runbook/models.py` | service enum | confirmed (§1.3.2) |
| `stepRef` values per step type | `runbook/models.py` | AddStep body in spec / service | **placeholder for now** — stub in `models.py` with `# TODO(confirm): stepRef per step type`; fill from spec/service before Phase 3 (`step add`) |
| Runbook status terminal states (for `wait`/`--watch`/polling) | `runbook/constants.py` | GetRunbook `properties.status` enum | **confirmed** — `--watch` terminal set (`EXECUTION_TERMINAL_STATES`) derived from two authoritative service enums: `RunbookExecutionStatus` (execution ARM resource `properties.status`: Queued/InProgress/Completed/Failed/Pausing/Paused/Resuming/Cancelling/Cancelled) and `ExecutionState` (status.json node state: adds Succeeded/PartiallySucceeded/Skipped etc.). Terminal = Completed/Failed/Cancelled ∪ Succeeded/PartiallySucceeded/Skipped. Validated live |

Any row marked **CONFIRM** is a Phase-0 blocker for the module that needs it; if unavailable, stub the
constant with a `# TODO(confirm): <source>` and gate the dependent live test with `@live_only()` until known.

### 0.3 Test-harness recipe (migrate has none today)

Phase 1 introduces the first recordings. Create a shared `ScenarioTest` base once so every scenario test
inherits scrubbing (there is no existing base to copy in migrate):

- Put it at `tests/latest/_test_base.py` with a `MigrateScenarioTest(ScenarioTest)` that registers, in
  `__init__`/`setUp`: subscription-id replacer → `00000000-0000-0000-0000-000000000000`, and processors that
  strip `sig=`/`Bearer`/SAS query strings from **both** request and response bodies/URIs (see §14).
- Unit tests use plain `unittest.TestCase` with a mocked `cmd` (copy the `_create_mock_cmd` shape from the
  existing `test_migrate_commands.py`).
- Test method name == recording file name (§14). Keep fixtures in `runbook/data/`.

### 0.4 Per-command parameter contract

The exact `options_list`, enum choices, and required/optional flags per command are **already fully
enumerated in the CLI spec** (`spec/az migrate runbooks cli - spec.md`) — every command has its own
"Arguments" table listing each flag, type, required/optional, and allowed values. This doc deliberately does
**not** duplicate them; the spec's per-command Arguments tables **are** the parameter contract. The agent's
job is to transcribe them 1:1 into `runbook/params.py` (`options_list` = the spec's literal `--flag`
spelling, enums = the spec's allowed-value lists, `required=` per the spec's column), and to encode the
cross-argument constraints (approval / custom-script parameter-sets, mutual exclusions) in
`runbook/validators.py` per §5/§12. Where a name is ambiguous, the spec's literal `--flag` spelling wins.
Keep the finalized arg table in `runbook/params.py` docstrings so it stays the single source in code.

---

## 1. Repository observations

### 1.1 The `migrate` extension today

- **Package:** `src/migrate/azext_migrate/`, extension name `migrate`, version `3.0.0b4`,
  `azext.minCliCoreVersion = 2.75.0`, `azext.isPreview = true`.
- **Command loader:** `MigrateCommandsLoader(AzCommandsLoader)` in
  [azext_migrate/__init__.py](../azext_migrate/__init__.py). It:
  - registers `custom_command_type = azext_migrate.custom#{}`,
  - calls `load_aaz_command_table` (the `aaz/` package is currently empty — just `__init__.py`),
  - then calls `load_command_table` from `commands.py` and `load_arguments` from `_params.py`.
- **Existing command groups** (all `is_preview=True`) in
  [azext_migrate/commands.py](../azext_migrate/commands.py):
  - `migrate get-discovered-server`
  - `migrate local replication {init,new,list,get,remove,get-job}`
  - `migrate local start-migration`
- **REST already uses raw requests.** [azext_migrate/helpers/_utils.py](../azext_migrate/helpers/_utils.py)
  already wraps `azure.cli.core.util.send_raw_request` with:
  - `send_get_request(cmd, uri)`
  - `get_resource_by_id(cmd, resource_id, api_version)` (returns `None` on 404)
  - `create_or_update_resource(cmd, resource_id, api_version, properties)` (handles 202/empty)
  - `delete_resource(cmd, resource_id, api_version)`
  - `validate_arm_id_format(arm_id, template)`
  - centralized `APIVersion` enum, `IdFormats`, `RoleDefinitionIds` constants.
  **This is the precedent the spec's Open Question #1/#2 refers to — we extend it, not replace it.**
- **Logging:** `knack.log.get_logger(__name__)`; **errors:** `knack.util.CLIError`.
- **Helpers layout:** `helpers/_utils.py`, `helpers/_server.py`, `helpers/migration/start/`,
  `helpers/replication/{get,init,job,list,new,remove}/` — i.e. **one folder per verb** with logic split
  out of `custom.py`. Commands in `custom.py` are thin and import their implementation lazily.
- **Tests:** [azext_migrate/tests/latest/test_migrate_commands.py](../azext_migrate/tests/latest/test_migrate_commands.py)
  uses `azure.cli.testsdk.ScenarioTest` but with **`unittest.mock` patched HTTP** — there is currently
  **no `recordings/` folder** in the migrate extension.

### 1.2 The `k8s-extension` reference (patterns to replicate, not import)

- Clean separation: `commands.py`, `_params.py`, `_validators.py`, `custom.py`, `_format.py` (table
  transformers), `_help.py`, `action.py` (custom argparse actions), `consts.py`, `utils.py`.
- `commands.py` uses `command_group` / `custom_command` / `custom_show_command`, with
  `supports_no_wait=True`, `table_transformer=`, `confirmation=`.
- Centralized `consts.py` for API versions, RP namespaces, fault types.
- `utils.py` centralizes logging (`knack.log`), **telemetry** (`azure.cli.core.telemetry.set_exception /
  set_user_fault / add_extension_event`), and reusable error mapping (`HttpResponseError` →
  `azure.cli.core.azclierror.*`).
- Uses typed CLI errors from `azure.cli.core.azclierror` (`InvalidArgumentValueError`,
  `RequiredArgumentMissingError`, `MutuallyExclusiveArgumentError`, `ResourceNotFoundError`, etc.).
- **Recording tests:** `tests/latest/` with `ScenarioTest`, `recordings/<test_method>.yaml` (one YAML per
  test), `data/` for fixtures, `MockClasses.py` for pure unit tests. YAML filename == test method name.
- **Difference from migrate:** k8s-extension uses **vendored SDK clients**. We deliberately **do not**
  copy that; per the spec's Overall Objective we invoke ARM directly via `send_raw_request()`.

### 1.3 Spec observations (source of truth)

Command tree from `spec/az migrate runbooks cli - spec.md` (Appendix A) and REST files under
`spec/Runbooks/` and `spec/RunbookExecutions/`:

| Command group | Verbs | Backing |
| --- | --- | --- |
| `migrate runbook` | `generate`, `show`, `list`, `update`, `delete`, `wait` | ARM resource `.../migrateProjects/{p}/runbooks/{n}` |
| `migrate runbook definition` | `show`, `download`, `visualize` | definition document / files / client-side |
| `migrate runbook definition step` | `add`, `update`, `remove` | sub-objects of definition (read-modify-write) |
| `migrate runbook definition workstream` | `split`, `merge` | sub-objects of definition |
| `migrate runbook parameter` | `download`, `upload` | parameters file (SAS blob) |
| `migrate runbook execution` | `start`, `pause`, `resume`, `cancel`, `show`, `list`, `visualize` | ARM child `.../runbooks/{n}/executions/{id}` |
| `migrate runbook execution step` | `retry`, `approve`, `complete` | action on a step within an execution |
| `migrate wave` | `show`, `list` | supporting reads |
| `migrate project` | `show`, `list` | supporting reads |
| `migrate workload` | `show`, `list`, `update-target-settings` | supporting reads + update |

Confirmed REST endpoints (all `https://management.azure.com{MigrateProjectResourceId}/...`,
`api-version={RunbooksAPIVersion}`, `auth: inherit`):

**Runbook resource & sub-object actions** (`spec/Runbooks/`):

- `PUT    .../runbooks/{n}` — CreateRunbook (`generate`); body `properties.scope = {scopeType:Wave, waveId}`
- `GET    .../runbooks/{n}` — GetRunbook (`show`)
- `GET    .../runbooks` — ListRunbooks (`list`)
- `DELETE .../runbooks/{n}` — DeleteRunbook (`delete`)
- `POST   .../runbooks/{n}/Regenerate` — RegenerateRunbook (re-`generate`; no body)
- `POST   .../runbooks/{n}/AddStep` — body `{stepName, displayName, stepRef, migrationEntityIds, dependsOn[]}`
- `POST   .../runbooks/{n}/UpdateStep` — body `{stepId, displayName, dependsOn[]}`
- `POST   .../runbooks/{n}/DeleteStep` — body `{stepId}`
- `POST   .../runbooks/{n}/SplitWorkstream` — body `{sourceWorkstreamId, stepIds[], newWorkstreamName}` (moves the given steps into the new workstream; no `migrationEntityIds`)
- `POST   .../runbooks/{n}/MergeWorkstreams` — body `{workstreamId[], newWorkstreamName?}` (`newWorkstreamName` optional — service defaults to the first workstream's name)
- `POST   .../runbooks/{n}/GenerateDownloadUrl` — download definition/spec + parameters; returns a **SAS URL to a ZIP**

**Execution resource & actions** (`spec/RunbookExecutions/`):

- `GET    .../runbooks/{n}/executions` — ListRunbookExecutions (`execution list`)
- `GET    .../runbooks/{n}/executions/{e}` — GetRunbookExecution (`execution show`)
- `PUT    .../runbooks/{n}/executions/{e}` — StartRunbookExecution (`execution start`); body `{properties:{}}`
- `PATCH  .../runbooks/{n}/executions/{e}` — PatchRunbookExecution; body `{status}`
- `POST   .../runbooks/{n}/executions/{e}/PerformAction` — body `{action:<int>, targetId, migrationEntityIds[]}` → **pause=1/resume=2/cancel=3/retry=4** (differ only by the integer `RunbookExecutionAction` code)
- `POST   .../runbooks/{n}/executions/{e}/ProvideApproval` — body `{action:"Approve", targetId:<stepId>, migrationEntityIds[]}` (`execution step approve`; `Reject` also available)
- `POST   .../runbooks/{n}/executions/{e}/UpdateStepStatus` — body `{action:"Complete", targetId:<stepId>, migrationEntityIds[]}` (`execution step complete`; `Fail`/`Skip` also available)
- `POST   .../runbooks/{n}/executions/{e}/GenerateDownloadUrl` — download status.json; returns a **SAS URL to a ZIP**

> **Dominant pattern:** ~13 of the ~20 endpoints are **`POST {resourceId}/{ActionName}` with a small JSON
> body**. This is the single most important architectural signal — it validates one generic
> `post_action(resource_id, action_name, body)` client method that every edit/action command reuses
> (see §6).

**Inconsistencies / assumptions (clarified with the spec owner):**

1. **~~Swapped verbs~~ — RESOLVED.** The execution YAMLs now correctly declare `GET` for
   `GetRunbookExecution` and `PUT` for `StartRunbookExecution`.
2. **`action` field — codes now CONFIRMED.** All execution actions come from one service enum
   `RunbookExecutionAction` (0-based ordinal): `Start=0, Pause=1, Resume=2, Cancel=3, Retry=4, Complete=5,
   Fail=6, Skip=7, Approve=8, Reject=9`. `PerformAction` uses the **integer** code (e.g. `"action": 1` for
   pause); `ProvideApproval`/`UpdateStepStatus` send the **string** member name (`"Approve"`/`"Complete"`).
   `models.py` mirrors this one enum + body builders. **Nothing about these codes is open anymore** — a
   value change would be a one-line edit.
3. **Start execution needs no scope.** `StartRunbookExecution` body is `{properties:{}}`; it only needs the
   **runbook ARM id in the URL**. Scope (`{scopeType:"Wave", waveId}`) applies **only to `generate`**
   (CreateRunbook). `waveId` is derived as `{project_resource_id}/waves/{wave_name}` in
   `models.build_generate_body`; the extra leading slash in the YAML example is an artifact, not part of the
   value. No casing/scope concern remains.
4. **`GenerateDownloadUrl` returns a SAS URL to a blob, not the file.** Flow: `POST .../GenerateDownloadUrl`
   → response carries a **pre-signed blob SAS URL** → `files.py` does a plain HTTP GET on that URL
   (**no ARM token** — the SAS is self-authorizing) to fetch a **ZIP** → extract with Python `zipfile`.
   Used by definition download, parameter download, and execution status download.
5. **CLI params → REST body mapping for steps.** The CLI surfaces
   `--step-type/--step-name/--step-description/--depends-on` plus type-specific `--approval-type` (Approval)
   and `--run-mode/--execution-target` (CustomScript). `models.py` maps these onto the `AddStep`/`UpdateStep`
   body (`{stepName, displayName, stepRef, migrationEntityIds, dependsOn, …}`). **The same parameter-set
   treatment applies to `step update` (§2.3), not only `step add`**, and additional approval/custom-script
   properties the service adds later are absorbed by this mapping layer.
6. **`MergeWorkstreams` takes an array of workstreams.** Body key `workstreamId` is a **list**; the CLI
   surfaces it as `--source-workstream-ids` (plural). Mapping handled in `models.py`.
7. **The YAMLs are a Swagger substitute only.** `auth: inherit`, `settings`, `runtime`/`.bru` scripts, and
   `seq` are **Bruno-client artifacts and are ignored** by the implementation — only **method + URL + body**
   are contractually meaningful. (`auth: inherit` just means "use the caller's ARM token", which
   `send_raw_request` supplies automatically.)
8. **Steps/workstreams are not ARM resources** and are edited via dedicated **POST action endpoints**
   (AddStep/UpdateStep/DeleteStep/SplitWorkstream/MergeWorkstreams) — no read-modify-write PATCH;
   `cmds/definition_step.py`/`cmds/definition_workstream.py` call `post_action` directly.

---

## 2. Proposed folder structure

All new code is organized as **self-contained feature packages** inside `azext_migrate` (starting with
`runbook/`), plus a **cross-feature `shared/` access layer** every group reuses. New command paths never
collide with existing `get-discovered-server` / `local` commands and can be reviewed/shipped independently.

```text
src/migrate/
├── azext_migrate/
│   ├── __init__.py                  # (edit) also load runbook command table + args + help
│   ├── commands.py                  # (unchanged existing)
│   ├── custom.py                    # (unchanged) existing local/replication commands
│   ├── _params.py                   # (unchanged)
│   ├── _help.py                     # (unchanged) + import feature _help modules
│   ├── helpers/                     # existing shared helpers (send_raw_request wrappers) — reused
│   │   └── _utils.py
│   ├── shared/                      # NEW cross-feature access layer (used by EVERY migrate feature group)
│   │   ├── __init__.py
│   │   ├── arm_client.py            # ArmClient — generic ARM REST wrapper (send_raw_request)
│   │   ├── arm_ids.py               # generic ID/URL builders, --ids parsing, api-version join
│   │   ├── constants.py             # provider namespace, base ID templates, api-version registry
│   │   ├── errors.py                # ARM error → azclierror mapping
│   │   ├── polling.py               # LRO / --no-wait / wait / --watch helpers
│   │   ├── files.py                 # GenerateDownloadUrl SAS→zip + safe local file IO
│   │   └── telemetry.py             # azure.cli.core.telemetry wrappers
│   └── runbook/                     # FEATURE package: `migrate runbook` (+ its nested subgroups)
│       ├── __init__.py
│       ├── commands.py              # load_runbook_command_table(self) — registers group + all subgroups
│       ├── params.py                # load_runbook_arguments(self)
│       ├── _help.py                 # helps[...] for every runbook command
│       ├── constants.py             # runbook-specific enums, ID templates, fault types
│       ├── validators.py            # runbook argument-constraint validators
│       ├── transformers.py          # runbook `--output table` transformers
│       ├── models.py                # runbook request-body builders + enums
│       ├── cmds/                    # business logic — ONE module per (sub)group; filename = subgroup path
│       │   ├── __init__.py
│       │   ├── runbook.py                 # `migrate runbook`                       generate/show/list/update/delete/wait/regenerate
│       │   ├── definition.py              # `migrate runbook definition`            show/download/visualize
│       │   ├── definition_step.py         # `migrate runbook definition step`       add/update/remove   (nested subgroup)
│       │   ├── definition_workstream.py   # `migrate runbook definition workstream` split/merge         (nested subgroup)
│       │   ├── parameter.py               # `migrate runbook parameter`             download/upload
│       │   ├── execution.py               # `migrate runbook execution`             start/show/list/pause/resume/cancel/visualize
│       │   └── execution_step.py          # `migrate runbook execution step`        retry/approve/complete    (nested subgroup)
│       └── visualize/               # client-side (non-REST) rendering
│           ├── __init__.py
│           ├── graph.py                 # definition/execution JSON -> DAG model
│           ├── renderer.py              # DAG model -> self-contained HTML (HTML-escaped, inline JS/CSS)
│           └── templates/
│               └── runbook.html.tmpl    # inline template (no CDN references)
│   # future peer groups (`migrate wave`/`project`/`workload`) — when implemented, each gets its OWN
│   # feature package (wave/, project/, workload/) beside runbook/, reusing shared/
└── azext_migrate/tests/latest/
    ├── __init__.py
    ├── shared/                      # tests for the cross-feature shared/ layer
    │   ├── test_arm_ids_unit.py         # id/--ids parsing, api-version join
    │   └── test_errors_unit.py          # ARM status → azclierror mapping
    └── runbook/                     # ALL runbook tests live under one per-feature folder
        ├── __init__.py
        ├── test_runbook_scenario.py     # ScenarioTest recording/playback tests
        ├── test_runbook_unit.py         # pure unit tests (models, validators, transformers, graph, renderer)
        ├── recordings/                  # one YAML per test method (filename == method name)
        │   ├── test_runbook_crud.yaml
        │   ├── test_runbook_execution.yaml
        │   └── ...
        └── data/                        # fixtures scoped to runbook tests
            ├── sample_definition.json
            └── sample_parameters.json
    # future peer groups add their OWN test folder here too (tests/latest/wave/, .../project/, …)
```

**Why feature packages + a shared layer:** it guarantees namespace isolation from the existing flat
`custom.py`/`_params.py`, keeps each (sub)group's logic in its own small module, and lets each feature
surface be enabled/disabled by **one loader call** (`load_runbook_command_table(self)`) added to
`__init__.py` (§4). The runbook feature therefore **does not touch the existing `custom.py` at all** — its
`CliCommandType(operations_tmpl='azext_migrate.runbook.cmds.{}')` routes every command into `runbook/cmds/*`
instead, so `cmds/` plays the role `custom.py` plays for the existing commands. Crucially this makes the
pattern **extensible**: future top-level groups (`migrate wave`, `migrate project`, `migrate workload`, and
anything added later) are new **peer packages**, each enabled by its own one-line
`load_<feature>_command_table(self)` hook, that reuse the same `shared/` layer instead of duplicating it.

### 2.1 Avoiding utility duplication across subgroups (the core concern)

**Concern:** if each subgroup gets its own folder with its own `command`/`init`/`util`, common helpers get
copy-pasted into every folder. This is a real anti-pattern — and it is exactly what the existing migrate
`helpers/replication/{get,init,job,list,new,remove}/` **verb-per-folder** layout risks.

**How other multi-subgroup extensions actually organize (reference evidence):**

- **`containerapp`** — the largest multi-subgroup extension in this repo (`containerapp`, `containerapp env`,
  `containerapp job`, `containerapp session`, `containerapp auth`, `containerapp env storage`, …). It does
  **NOT** use folder-per-subgroup. It has **one flat shared layer at the package root**:
  `_utils.py`, `_clients.py`, `_client_factory.py`, `_constants.py`, `_models.py`, `_transformers.py`,
  `_validators.py`, `_help.py`, `_params.py`, a **single** `commands.py`, a **single** `custom.py`.
  Per-subgroup *logic* lives in **one file per subgroup** (`containerapp_env_decorator.py`,
  `containerapp_job_decorator.py`, …) that all consume the shared root layer. Cross-cutting helpers are
  further split **by concern, not by subgroup** (`_ssh_utils.py`, `_dapr_utils.py`, `_archive_utils.py`).
- **`dataprotection`** keeps generated commands in `aaz/` and hand-written logic in a single `manual/`
  package + one `custom.py` — again, shared helpers are centralized, not per-subgroup.

**Conclusion / rule for migrate:** subgroups differ only in **business logic**, never in utilities.
Therefore:

1. **A cross-feature `shared/` access layer** — `arm_client.py`, `arm_ids.py`, `errors.py`, `polling.py`,
   `files.py`, `telemetry.py`, and base `constants.py` are defined **exactly once** under
   `azext_migrate/shared/` and imported by **every feature group** (runbook, wave, project, workload, and
   anything added later). Feature-specific `models.py`/`transformers.py`/`validators.py`/`constants.py` live
   in each feature package and are shared by that feature's subgroups.
2. **`cmds/` contains only per-(sub)group business logic** — each module is a thin orchestrator
   (resolve → validate → build body → `arm_client.post_action/put/get` → transform). **No `arm_client.py`,
   `_utils.py`, or `constants.py` is ever created inside `cmds/`.** A lint/review rule enforces that
   `cmds/*` and feature packages may import from `shared/`, but `shared/` never imports from any feature.
3. Because ~13 endpoints are the same `POST {resourceId}/{action}` shape, the *entire* edit/action surface
   (steps, workstreams, execution actions, approvals, completes, regenerate) is served by **one**
   `arm_client.post_action` + a handful of body builders in `models.py`. There is essentially nothing left
   to duplicate — `cmds/definition_step.py:add()` is ~5 lines: build body, call
   `post_action(runbook_id, 'AddStep', body)`.

This directly resolves the duplication worry: `commands`/`params`/`_help` are split per subgroup for
readability, but **all common code lives in a single shared layer**, mirroring how `containerapp` scales to
dozens of subgroups without duplicating utilities.

### 2.2 Reference patterns for logic placement (why a sub-package, not top-level `custom.py`)

Two in-repo patterns were studied:

- **`migrate` (existing `local`/replication):** a **thin top-level `custom.py`** whose functions **lazily
  import** their implementation from `helpers/replication/<verb>/…`. This works and keeps `custom.py` small,
  but as the surface grows `custom.py` becomes a catch-all and the per-verb folders tempt utility
  duplication.
- **`containerapp` (large extension):** a single large `custom.py` that delegates to **decorator classes**
  (one per feature, e.g. `ContainerAppJobDecorator`) over a **centralized** `_utils.py`/`_clients.py`.

Both centralize utilities and keep the command layer thin. The runbook feature adopts the **self-contained
`runbook/` sub-package** with `cmds/*.py` (plain functions, no decorator state machine — raw REST
doesn't need one) over a single shared access layer. This matches containerapp's centralized-utility
principle while staying isolated inside the `migrate` boundary. **The existing `local` commands are left
as-is** for now (isolation requirement); §2.4 describes how they *can* later adopt this same pattern
without any user-facing change.

### 2.3 Naming, nested subgroups, and peer groups (extensibility rules)

These rules make the layout scale to arbitrary future `migrate` groups/subgroups:

- **Logic folder is `cmds/`** (not `operations/`), and **files are named after the subgroup path** below the
  feature root — no `_ops` suffix. Examples inside `runbook/cmds/`: `runbook.py`, `definition.py`,
  `parameter.py`, `execution.py`.
- **Nested / doubly-nested subgroups** encode their full path with underscores, so depth is unlimited and
  two different `step` subgroups never collide:
  - `migrate runbook definition step` → `cmds/definition_step.py`
  - `migrate runbook execution step` → `cmds/execution_step.py`
  A third level (e.g. a hypothetical `migrate runbook definition step approval`) is simply
  `cmds/definition_step_approval.py`. The registration string `'<module>#<func>'` maps 1:1 to the file.
- **Peer groups are separate feature packages, never nested under `runbook/`.** Future groups like
  `migrate wave`, `migrate project`, and `migrate workload` would each be a **sibling** feature package in
  its **own folder named after the group** (`wave/`, `project/`, `workload/`) — not a shared/generic
  `supporting/` folder, and not nested under `runbook/`. (They are **out of scope for now** — see §15
  Future TODO.)
- **Every feature package reuses `shared/`** for REST/IDs/errors/polling/files/telemetry, so adding a group
  never duplicates the access layer. Enablement is **one loader hook per feature package** in
  `__init__.py` (§4).

### 2.4 Future: migrating the existing `local` commands to the feature-package pattern

The current `local`/replication commands (`migrate get-discovered-server`, `migrate local replication …`,
`migrate local start-migration`) **can** be moved onto this pattern later as a pure refactor — **command
paths stay identical**, so there is no user-facing break. This is **out of scope now** (don't touch working
commands), but nothing in the design blocks it. The mapping:

| Today (`local`, verb-per-folder) | Future (feature-package pattern) |
| --- | --- |
| thin `custom.py` funcs that lazily import helpers | `local/cmds/*` functions bound via `operations_tmpl` |
| `helpers/replication/{get,init,job,list,new,remove}/` (folder per verb) | `local/cmds/replication.py` (one module per subgroup) |
| `helpers/migration/start/` | `local/cmds/start_migration.py` (or a `local start-migration` module) |
| `helpers/_utils.py` `send_raw_request` wrappers | folded into `shared/arm_client.py` / `shared/arm_ids.py` |
| registration in root `commands.py` | `local/commands.py::load_local_command_table(self)` |
| args in root `_params.py` | `local/params.py::load_local_arguments(self)` |

Migration steps (mechanical, incremental):

1. Create a `local/` **peer package** (sibling of `runbook/`); move the replication/migration logic into
   `local/cmds/*`, collapsing the six verb-folders into per-subgroup modules.
2. Point a new `CliCommandType(operations_tmpl='azext_migrate.local.cmds.{}')` at them.
3. Add `load_local_command_table(self)` / `load_local_arguments(self)` hooks in `__init__.py` and **remove**
   the old root `commands.py` / `_params.py` registration for those commands.
4. Retire `helpers/replication/*` once its logic lives in `local/cmds/*` + `shared/`.

Why it's safe / low-risk: paths are unchanged (`migrate local …`); it's the same REST, now routed through
`shared/arm_client` instead of `helpers/_utils`. Best done as its **own phase after** the runbook feature is
stable, so `shared/` is already proven before `local` depends on it. Caveat: the existing
`unittest.mock`-patched HTTP tests would be re-pointed at `shared/arm_client` (and ideally gain recordings,
per §14).

---

## 3. Module responsibilities

| Module | Responsibility | Depends on |
| --- | --- | --- |
| `runbook/commands.py` | Register command groups/subgroups, wire `supports_no_wait`, `confirmation`, `table_transformer`, `custom_show_command`. | knack/azcli, `transformers`, `constants` |
| `runbook/params.py` | Declare arguments, `options_list`, `get_enum_type`, `get_three_state_flag`, attach `validators`. | `constants`, `validators` |
| `runbook/_help.py` | `helps[...]` YAML docstrings + **examples** (release requirement per spec Open Q#4). | — |
| `runbook/constants.py` | Runbook-specific enums, ID templates, fault types (extends the shared api-version registry). | `shared/constants` |
| `runbook/validators.py` | Enforce the spec's **Argument constraints** (Azure CLI has no parameter-sets). | `constants`, azclierror |
| `runbook/transformers.py` | `--output table` transformers (definition, execution status, list). | — |
| `shared/arm_client.py` | **Single, cross-feature** ARM REST surface: `get/list/put/patch/delete/post_action` via `send_raw_request`; header/body serialization; delegates error mapping to `errors`. | `errors`, `arm_ids`, azcli.util |
| `shared/arm_ids.py` | Generic resource-ID/URL builders; join `api-version`; parse `--ids`. | `constants` |
| `shared/polling.py` | Poll GET until terminal status; back `generate`/`execution start` `--no-wait`; power `wait`; `--watch`. | `arm_client`, `constants` |
| `shared/errors.py` | Map ARM error bodies + status codes to `azclierror` types with actionable messages. | azclierror, telemetry |
| `shared/telemetry.py` | `record_exception`, `set_user_fault`, `add_event` wrappers (no-op safe). | azcli.telemetry |
| `shared/files.py` | `POST GenerateDownloadUrl` → SAS blob URL → HTTP GET (no ARM token) → unzip; safe local path handling. | `arm_client` |
| `shared/constants.py` | Provider namespace, base ID templates, api-version registry — shared by all feature groups. | — |
| `runbook/models.py` | Request-body builders (e.g. `build_generate_body(wave_id)`), enum definitions, response projections. | `constants` |
| `runbook/cmds/*` | Business logic per (sub)group; **one module per subgroup path**; orchestrate validate → build request → call client → transform. | shared layer + models/validators/transformers |
| `runbook/visualize/*` | Pure client-side transform of JSON → DAG → **self-contained, HTML-escaped** HTML file. | stdlib only |

**Dependency direction (strictly one-way):**
`commands/params` → `cmds` → (`models`, `transformers`, `validators`, feature `constants`) → `shared/`
(`arm_client`, `arm_ids`, `polling`, `files`, `errors`, `telemetry`, base `constants`). No cycles.
`cmds` never imports `commands`; `shared/` never imports any feature package.

---

## 4. Command registration strategy

Keep existing registration untouched; **append** a single call so new commands are additive and
conflict-free.

- [azext_migrate/__init__.py](../azext_migrate/__init__.py) `load_command_table`: after the existing
  `load_command_table(self, args)`, add `from azext_migrate.runbook.commands import
  load_runbook_command_table; load_runbook_command_table(self)`.
- `load_arguments`: after existing `load_arguments`, add
  `from azext_migrate.runbook.params import load_runbook_arguments; load_runbook_arguments(self)`.
- Help: `azext_migrate/_help.py` adds `from azext_migrate.runbook import _help  # noqa` (import side-effect
  registers `helps`). No changes to existing help entries.

Inside `runbook/commands.py`, register with a **custom command type** scoped to the `cmds` package so
resolution is unambiguous. **This is why the feature needs no `custom.py`:** the existing commands resolve
through `custom_command_type = azext_migrate.custom#{}` (into `custom.py`), whereas the runbook group binds
its own `CliCommandType(operations_tmpl='azext_migrate.runbook.cmds.{}')`, so `'runbook#generate'` loads
`azext_migrate.runbook.cmds.runbook.generate`. The `runbook/cmds/*` modules **are** this feature's command
implementations — `custom.py` is left untouched. Nested subgroups get their own `command_group` block and
their own `cmds` module:

```python
# runbook/commands.py
runbook_cmds = CliCommandType(operations_tmpl='azext_migrate.runbook.cmds.{}')

with self.command_group('migrate runbook', runbook_cmds, is_preview=True) as g:
    g.custom_command('generate', 'runbook#generate', supports_no_wait=True)
    g.custom_show_command('show', 'runbook#show', table_transformer='...')
    g.custom_command('list', 'runbook#list_', table_transformer='...')
    g.custom_command('update', 'runbook#update')
    g.custom_command('delete', 'runbook#delete', confirmation=True)
    g.custom_wait_command('wait', 'show')             # native predicates over custom show (spec §7)

# nested subgroup: `migrate runbook definition`
with self.command_group('migrate runbook definition', runbook_cmds) as g:
    g.custom_show_command('show', 'definition#show', table_transformer='...')
    g.custom_command('download', 'definition#download')

# doubly-nested subgroup: `migrate runbook definition step`
with self.command_group('migrate runbook definition step', runbook_cmds) as g:
    g.custom_command('add', 'definition_step#add')
    g.custom_command('update', 'definition_step#update')
    g.custom_command('remove', 'definition_step#remove', confirmation=True)
```

`operations_tmpl` resolves `'<module>#<func>'` to `azext_migrate.runbook.cmds.<module>.<func>`, so the
module name is exactly the subgroup path (`definition_step`, `execution_step`) — **nesting depth is
unlimited and two different `step` subgroups never collide.**

**Peer groups** (added later) would live in their **own** feature package named after the group and be
registered the same way (they are *siblings* of `migrate runbook`, not children). For example, a future
`migrate wave` group:

```python
# wave/commands.py  (added only when wave/project/workload are implemented — each in its own folder)
wave_cmds = CliCommandType(operations_tmpl='azext_migrate.wave.cmds.{}')
with self.command_group('migrate wave', wave_cmds, is_preview=True) as g:
    g.custom_show_command('show', 'wave#show')
    g.custom_command('list', 'wave#list_')
```

This mirrors the k8s-extension registration style while staying self-contained per feature.

**Isolation guarantees:** new command paths all start with `migrate runbook` (and, when added, future peer
groups like `migrate wave`) — none overlap existing `migrate get-discovered-server` or `migrate local ...`.
No global argument context is modified except adding new contexts.

---

## 5. CLI command organization

- **`commands.py`** — *only* command registration + transformer/confirmation/no-wait wiring. No logic.
- **`params.py`** — *only* argument declarations. Shared arg types defined once:
  `project_name`, `runbook_name` (`--runbook-name`; and `-n/--name` where the runbook is the primary
  resource), `execution_id`, `step_id`, `workstream_id`, `wave_name`, enum types (status, step-type,
  approval-type, run-mode, execution-target). `--ids` is auto-provided by Azure CLI when `id_part` is set
  on the name arguments, satisfying the spec's `--ids` addressing.
- **`cmds/*.py`** — thin command functions (target ~15–40 lines each). Each function:
  1. resolves identity (`arm_ids`), 2. validates (`validators`, already partly enforced declaratively),
  3. builds request (`models`), 4. calls `arm_client`, 5. transforms/returns.
- **`validators.py`** — cross-argument constraints the spec spells out per command (e.g. `--approval-type`
  required when `--step-type Approval`; `--run-mode`/`--execution-target` only for `--step-type CustomScript`;
  `--entities`/`--all-ready` only for `Partial` and mutually exclusive; `--comment` required for `complete`).
  **`step update` reuses the same parameter-set validators as `step add`** (approval / custom-script
  conditionals), inferring the step's type from the target step when `--step-type` is omitted.
- **`shared/arm_client.py` + `shared/arm_ids.py`** — the client/helper modules; the only place
  `send_raw_request` and URL/ID assembly live (reused by every feature group).
- **`transformers.py`** — the "default table view" tables named in the spec (definition table:
  `Id, Step Name, Depends On, Configuration Status, Workloads, Applications`; execution table:
  `Id, Step Name, Step Status, Depends On, Workload Progress`).

---

## 6. REST client architecture

A single `ArmClient` (in `shared/arm_client.py`) centralizes every ARM interaction (spec Objective +
Reusability §8). It wraps
the existing proven `send_raw_request` helpers rather than reinventing them.

```text
cmds/*     ──►  ArmClient (shared/)  ──►  send_raw_request(cli_ctx, method, url, body, headers)
                        │                         (auth, token, cloud endpoint handled by Az CLI)
                        ├─ arm_ids: build resource id + ?api-version=
                        └─ errors: status/body → azclierror
```

Responsibilities of `ArmClient` (all take `cmd`):

- `get(resource_id)` / `get_or_none(resource_id)` — GET; 404→None variant for existence checks.
- `list(collection_id)` — GET with automatic **`nextLink` pagination** aggregation (runbooks, executions).
- `put(resource_id, body)` — create/generate/start; returns body or async handle.
- `patch(resource_id, body)` — `runbook update`, `PatchRunbookExecution` (`{status}`).
- `delete(resource_id)` — delete.
- `post_action(resource_id, action_name, body=None)` — **the workhorse.** Serves every
  `POST {resourceId}/{action_name}` endpoint: `Regenerate`, `AddStep`, `UpdateStep`, `DeleteStep`,
  `SplitWorkstream`, `MergeWorkstreams`, `GenerateDownloadUrl`, `PerformAction`, `ProvideApproval`,
  `UpdateStepStatus`. ~13 commands share this one method.
- All methods send `Content-Type=application/json`, serialize dict→JSON, parse JSON→dict, and route errors
  through `errors.raise_for_arm_error(response)`.

**Action-code abstraction (removes duplication for execution actions):** `PerformAction` handles
`pause/resume/cancel/retry` via an integer `action` code from the confirmed `RunbookExecutionAction` enum
(`Start=0, Pause=1, Resume=2, Cancel=3, Retry=4, Complete=5, Fail=6, Skip=7, Approve=8, Reject=9`).
`models.py` owns an `ExecutionAction` enum (member → int) and a
single `build_perform_action_body(action, target_id=None, entity_ids=None)` builder, so those four commands
are one-liners differing only by enum member. `approve`/`complete` reuse the **same** enum but serialize the
**string member name** for the `ProvideApproval`/`UpdateStepStatus` bodies via
`build_step_action_body(action, target_id, entity_ids)`.

**Download/unzip:** `GenerateDownloadUrl` returns a SAS URL to a **ZIP**; `files.py` downloads then
extracts with Python `zipfile` (definition+docs, parameters, or execution status.json).

**Cloud/endpoint handling:** URLs are always
`cmd.cli_ctx.cloud.endpoints.resource_manager + resource_id + '?api-version=' + RUNBOOKS_API_VERSION`,
so sovereign clouds work automatically (matches existing `_utils.py` pattern).

**Reuse decision:** `arm_client.py` internally calls the existing
`helpers/_utils.py` functions where they already fit (`get_resource_by_id`, `create_or_update_resource`,
`delete_resource`) and adds runbook-specific methods (`list` with paging, `post_action`, `patch`). This
honors "reuse migrate utilities where appropriate" without importing anything from other extensions.

---

## 7. Utility layer design

- **`arm_ids.py`**
  - `project_id(sub, rg, project)`, `runbook_id(project_id, name)`,
    `execution_id(runbook_id, execution_id)` from ID templates in `constants.py`.
  - `resolve_ids(cmd, namespace)` — when `--ids` is supplied, parse it into
    (sub, rg, project, runbook, execution); otherwise assemble from discrete args. Central place for the
    spec's "Execution identity" addressing rules.
  - `with_api_version(resource_id)` — append `?api-version=`.
- **`polling.py`** — `poll_until(cmd, get_fn, predicate, interval, timeout)` used by `--watch`,
  and terminal-status detection for `generate`/`execution start`. The public `wait` command uses the CLI's
  native `custom_wait_command` bound to the custom `show`, so `wait` gets `--created/--updated/--deleted/`
  `--exists/--custom/--interval/--timeout` for free (no hand-written polling for `wait` itself).
- **`files.py`** — `download_sas_zip(sas_url, dest)` (plain HTTP GET on the pre-signed blob URL — **no ARM
  token** — then unzip with Python `zipfile`), `save_json(obj, path)`,
  `generate_and_download(cmd, resource_id, dest)` = `POST GenerateDownloadUrl` → read SAS URL from response
  → `download_sas_zip`. Validates/normalizes destination paths (prevents path traversal), defaults to CWD
  per spec.
- **`errors.py`** — `raise_for_arm_error(response)`; maps `404→ResourceNotFoundError`,
  `400→InvalidArgumentValueError`/`BadRequestError`, `403→ForbiddenError`, `409→ClientRequestError`,
  `5xx→CLIInternalError`; extracts `error.code`/`error.message`; appends remediation hints.
- **`telemetry.py`** — `record_exception(ex, fault_type, summary)`, `set_user_fault()`,
  `add_event(name, props)`; all guarded so telemetry never breaks a command.
- **`transformers.py`** — pure functions `dict → list[OrderedDict]` for the named table views
  (feature-specific; lives in `runbook/`).

The access modules above (`arm_client`, `arm_ids`, `polling`, `files`, `errors`, `telemetry`, base
`constants`) are **cross-feature** and live in `shared/`, so `runbook/` and any future feature group
(e.g. `wave/`, `project/`, `workload/`) reuse them without duplication. Feature-specific
`models`/`transformers`/`validators`/`constants` live in each feature package. Only if a `shared/` helper
proves useful to the existing `local`/`replication` commands would it also be surfaced via `helpers/` (per
spec §11 "introduce new shared utilities only when they provide value across multiple command groups").

### 7.1 Visualize pipeline (`graph.py` → `renderer.py` → `runbook.html.tmpl`)

`migrate runbook definition visualize` and `migrate runbook execution visualize` turn a runbook JSON
document into a **single, self-contained, offline HTML file** (a dependency graph the user can open in a
browser). It is **purely client-side** — the only network call is the one read (`arm_client.get`) that
fetches the JSON; everything after that is local, stdlib-only transformation. The three files split the job
into **parse → render → template** so each stage is independently unit-testable:

1. **`visualize/graph.py` — JSON → DAG model (data only, no HTML).**
   - Input: the definition document (steps + `dependsOn` + workstreams) or an execution document (steps +
     per-step `status`/progress).
   - Output: an in-memory **DAG** — a list of **nodes** (one per step/workstream, carrying id, name,
     type, and for executions the status) and **edges** (one per `dependsOn` link).
   - Also: validates the graph (detects cycles / dangling `dependsOn` references) and computes a stable
     **topological layering** (which nodes sit in which "row") so the renderer can lay them out
     deterministically. This module contains **no HTML and no I/O** — just dict/list → dataclasses, which
     makes it trivial to unit-test the graph shape.

2. **`visualize/renderer.py` — DAG model → HTML string (the security-critical stage).**
   - Takes the DAG model and produces the final HTML by filling the template.
   - **HTML-escapes every user-controlled value** (step names, descriptions, workstream names) with
     `html.escape` **before** substitution — this is the mandatory **XSS guard** (spec §5): a step named
     `<script>alert(1)</script>` must render as inert text, never execute. This is the single most
     important line in the feature and is asserted by a unit test.
   - Emits nodes/edges as data the template's inline script draws (e.g. a small vanilla-JS layout, or
     precomputed SVG/positioned `<div>`s from the layering in step 1). Status colors for execution graphs
     are applied here.

3. **`visualize/templates/runbook.html.tmpl` — the static shell.**
   - A plain HTML skeleton with placeholders plus **inline `<style>` and `<script>`** — **no CDN / no
     external URLs / no network fonts**, so the output is fully **offline and self-contained** (open it
     from disk with no internet, and nothing phones home). Keeping markup out of Python (in a template)
     keeps `renderer.py` focused on escaping + data, and lets the visual design change without touching
     logic.

**Write-out & flags:** the `cmds/*` `visualize` function calls `graph → renderer`, then uses
`shared/files.py` to write the HTML to `--output-path` (default: CWD, path-traversal-normalized). An
optional `--open`/`--launch` flag can open it in the default browser (via `webbrowser`), but the file is the
primary artifact. Nothing about visualize touches ARM beyond the initial read, so it works against any
saved/downloaded definition JSON too.

### 7.2 Learnings from the POC viewer (`spec/poc/` — temporary reference, to be deleted)

A throwaway POC (`spec/poc/fluent web components+static html/`) was reviewed **for layout/visualization
ideas only**. It is an Azure-portal-lookalike static viewer (`viewer.html` + `runbook.data.js` /
`status.data.js`) with a C# generator that projects the spec into a view-model. What we take from it and
what we explicitly reject:

**Adopt (layout / view-model ideas):**

- **The intended visualization is a portal-style, workstream-grouped list — not (only) a node-link SVG
  DAG.** This matches the 4 portal screenshots. The primary view is a grid grouped by workstream with a
  group header `Workstream: <name> (<count>)`, and a **"Step dependency" text-summary column** rather than
  a drawn graph. The SVG DAG (§7.1) becomes secondary/optional; the grouped grid is the default.
- **Two panels sharing one visual style:** a **Planning** view (definition) and an **Execution** view
  (status). Planning columns: **Steps** (icon + display name + `stepRef` badge), **Configuration status**
  (badge), **Step dependency** (summary text), **Workloads** (count of `entities[]`), **Applications**
  (placeholder `—` until the service provides it). Execution: per-workstream group with a roll-up status
  pill, per-step status pill, and per-entity progress bars, plus an overall progress % bar.
- **Summary cards** at the top: Planning → Workstreams / Steps / Workloads(entities); Execution → Total /
  Succeeded / Running / Waiting / Pending / Failed.
- **`dependencySummary` derivation is confirmed:** distinct upstream **step display-names** collected from
  `prerequisite[] + dependsOn[]` (validates the planned `_merged_deps` helper). Each dependency also
  carries a `mode` and resolved entity names for the detail view.
- **Name resolution:** build a `stepId → displayName` map and an entity `id → displayName` map (from
  `entities[]`) up front; resolve dependency `step` ids and step `entities[]` ids through them.
- **Category/icon are derived from `stepRef` substrings** (setup / dataSync / testMigration /
  testMigrationCleanup / approval / migration / cutover). Optional cosmetic nicety for the grid.
- **Per-step detail** (POC uses a slide-in drawer): Category, Step type (`stepRef`), Step ID, Status,
  Workloads/Entities chips, Pre-requisites list, Depends-on list. We can render this as static
  inline/expandable markup — no drawer/JS required.

**Reject (violates our constraints — do NOT copy verbatim):**

- **CDN / external components.** The POC loads `@fluentui/web-components` from `cdn.jsdelivr.net` and uses
  web fonts. Our output **must be fully offline and self-contained** (§7.1): NO CDN, NO external URLs, NO
  network fonts, NO web components. The POC's plain inline CSS (`.grid`, `.group__head`, `.card`, `.pill`,
  `.bar`) is reusable as a starting point once the `<fluent-*>` elements are replaced with plain
  `<div>`/`<span>` styled by inline CSS.
- **Client-side `fetch()` / polling / `file://` script re-injection.** The POC polls `status.json` every
  2.5s and re-injects `status.data.js` on `file://`. Our `--watch` **regenerates the HTML file
  server-side** on each interval; the emitted HTML is a **static snapshot** with minimal/no inline JS and
  **no network calls**.
- **Client-side escaping as the security boundary.** The POC's JS `esc()` confirms the escaping shape, but
  our XSS guard stays in **Python (`html.escape` in `renderer.py`)** on every user-controlled string before
  substitution.

**Reconciliation notes:**

- POC labels the count column **"Entities"**; our table/spec and the portal use **"Workloads"** (= count of
  `entities[]`) and a separate **"Applications"** column (no data in the current `runbook.json` → `—`).
- POC status vocab is Succeeded/Running/WaitingApproval/Pending/Failed; the real `status.json` uses
  Completed/InProgress/Blocked/NotStarted/Failed — the renderer needs a small **status→CSS-class/label map**
  (execution) distinct from the **config-status map** (Configured / Partial (n/m) / NotConfigured) for
  planning.
- POC merges both panels into a single tabbed HTML from two data files. Our CLI keeps **two separate
  commands and two separate output files** (`definition visualize`, `execution visualize`) that **share the
  CSS/visual style**; a combined tabbed document is out of scope unless requested.

---

## 8. Business logic layering

```text
┌───────────────────────────────────────────────────────────┐
│ Command layer          commands.py / params.py             │  registration + arg parsing
├───────────────────────────────────────────────────────────┤
│ Validation layer       validators.py                       │  parameter-set constraints
├───────────────────────────────────────────────────────────┤
│ Orchestration layer    cmds/*.py                           │  thin: resolve→build→call→transform
├───────────────────────────────────────────────────────────┤
│ Request/response       models.py · transformers.py         │  body builders · table projections
├───────────────────────────────────────────────────────────┤
│ Access layer (shared/) arm_client · arm_ids · files ·      │  the ONLY REST/IO surface
│                        polling · errors · telemetry        │
├───────────────────────────────────────────────────────────┤
│ Foundation             constants.py                        │  versions, enums, templates
└───────────────────────────────────────────────────────────┘
```

Commands remain thin and delegate; the access layer is the single choke-point for REST, IDs, polling,
files, errors, and telemetry — eliminating duplication.

---

## 9. Request / response lifecycle

Example: `az migrate runbook generate -g rg --project-name p -n rb --wave-name w1 --no-wait`

1. **Parse** — `params.py` binds args; `id_part` enables `--ids`.
2. **Validate** — `validators.validate_generate` (wave required, name pattern).
3. **Resolve** — `arm_ids.runbook_id(project_id(sub, rg, p), 'rb')`.
4. **Build** — `models.build_generate_body(wave_id)` →
   `{"properties": {"scope": {"scopeType": "Wave", "waveId": ".../waves/w1"}}}`.
5. **Call** — `arm_client.put(runbook_id, body)` → `send_raw_request` (PUT).
6. **LRO / `--no-wait`** — with `--no-wait` the command returns **immediately after the PUT is accepted**,
   emitting the **initial resource** (runbook in `Generating` state, incl. its ARM `id`/`name`) with **no
   polling**. The caller checks progress later via `az migrate runbook show` or blocks with
   `az migrate runbook wait --custom "properties.status=='Succeeded'"`. Without `--no-wait`,
   `polling.poll_until(status in terminal)` blocks until the runbook reaches a terminal state.
   (For `execution start`, `--no-wait` returns the execution `id` + initial object; check via
   `az migrate runbook execution show`.)
7. **Transform** — default JSON; `--output table` uses the runbook table transformer.
8. **Errors** — any `>=400` routed through `errors.raise_for_arm_error`; telemetry fault recorded.

Read example (`execution show --watch`): resolve execution id → `arm_client.get` (status.json projection)
→ `transformers.execution_table` → if `--watch`, a **client-side loop** (`polling.poll_until`) re-issues the
GET and **re-renders the table every `--interval` seconds** (default 5s) until the execution reaches a
terminal state or the user presses `Ctrl+C` (caught and surfaced as `ManualInterrupt`). `--watch` is **not a
native Azure CLI feature** — it is implemented in `cmds/execution.py` (`show`) and renders its own table rather than
using standard output formatting (precedent: `az arc`/connectedk8s watch-style loops).

---

## 10. Logging strategy

- One `logger = get_logger(__name__)` per module (consistent with existing migrate + k8s-extension).
- **Levels:** `debug` for request URL/verb/correlation id and non-sensitive response summaries;
  `info` for user-facing progress (e.g. "Runbook is being generated"); `warning` for recoverable issues;
  `error` only when raising.
- **REST logging** lives in `arm_client` so it is centralized: log method + URL + `x-ms-correlation-request-id`
  / `x-ms-request-id` from response headers. **Never log** request/response bodies that may contain SAS
  URIs, tokens, or parameter file contents; redact query strings containing `sig=`/`token`.
- **Correlation:** surface `x-ms-correlation-request-id` in `--debug` and in error messages to aid support.

---

## 11. Telemetry strategy

- Wrap `azure.cli.core.telemetry` in `runbook/telemetry.py` (never call it directly from operations, so it
  can be no-op/tested).
- On handled failures, `errors.raise_for_arm_error` calls `telemetry.record_exception(ex, fault_type,
  summary)` with **fault types centralized in `constants.py`** (e.g. `RUNBOOK_ARM_ERROR`,
  `RUNBOOK_VALIDATION_ERROR`, `RUNBOOK_FILE_ERROR`, `RUNBOOK_VISUALIZE_ERROR`).
- Distinguish user faults (`set_user_fault()` for 4xx/validation) from service faults (5xx).
- Optional lightweight events for long-running ops (`add_event('runbook.generate', {...})`) with **no PII**
  (no names/descriptions/IDs beyond subscription-safe correlation ids).
- Telemetry must be best-effort: all calls wrapped in try/except so instrumentation never fails a command.

---

## 12. Error handling strategy

- **Typed exceptions** from `azure.cli.core.azclierror` (aligns with modern Az CLI UX and linter):
  `RequiredArgumentMissingError`, `InvalidArgumentValueError`, `MutuallyExclusiveArgumentError`,
  `ResourceNotFoundError`, `ForbiddenError`, `ClientRequestError`, `CLIInternalError`, `FileOperationError`,
  `ManualInterrupt`. (The existing code uses `knack.util.CLIError`; new runbook code standardizes on
  `azclierror` for richer classification, while remaining compatible.)
- **ARM failures:** single mapper `errors.raise_for_arm_error(response)` extracts `error.code` +
  `error.message`; adds actionable hints (e.g. `ResourceGroupNotFound` → "create the resource group or
  check --subscription", `RunbookNotFound` → verify `--project-name`/`-n`). Mirrors the helpful mapping
  already in `helpers/_utils.get_resource_by_id`.
- **Validation errors:** raised pre-flight from `validators.py` with the exact offending parameter names.
- **Retries:** rely on Az CLI's built-in transient-retry in `send_raw_request`; add bounded retry only for
  SAS blob download/upload in `files.py` (network hiccups), never for state-changing ARM calls.
- **Confirmation:** `delete`, `execution cancel`, `definition step remove` use `confirmation=True`
  (bypassed by `--yes`).
- **Consistency:** operations never raise raw `Exception`; everything funnels through `errors`/validators.

---

## 13. Testing strategy

Two complementary layers, organized **per feature** under `tests/latest/` (`shared/`, `runbook/`, and a
sibling folder for each future group) so tests never mix across features:

1. **Unit tests (`runbook/test_runbook_unit.py`, plus `shared/test_arm_ids_unit.py` /
   `shared/test_errors_unit.py`, no network):**
   - `arm_ids` ID/`--ids` parsing round-trips.
   - `validators` accept/reject matrices for every "Argument constraints" block in the spec.
   - `models` body builders (exact JSON shape incl. `scopeType`/`waveId`).
   - `transformers` table projections from sample JSON in `runbook/data/`.
   - `visualize/graph` DAG construction and `renderer` **HTML-escaping** (assert `<script>`/`<`/`&` in a
     malicious step name is encoded — the mandatory XSS guard from spec §5).
   - `errors` status→exception mapping.
   Use `unittest` + mocked `cmd` (like the existing `test_migrate_commands.py` `_create_mock_cmd`).

2. **Scenario / recording tests (`runbook/test_runbook_scenario.py`):**
   - `azure.cli.testsdk.ScenarioTest`; commands driven via `self.cmd(...)` with `self.check(...)`.
   - End-to-end flows: CRUD (`generate→show→list→update→delete`), execution
     (`start→show→pause→resume→cancel`), step actions, parameter upload/download.
   - Assertions use `self.check('name', ...)`, `self.check('properties.status', ...)` and
     `get_output_in_json()` for list membership.

Coverage target: every command has at least one scenario path; every validator branch a unit test.

---

## 14. Recording test strategy

Replicate the k8s-extension recording philosophy inside migrate (which currently has none):

- Each feature keeps recordings **inside its own test folder**: `tests/latest/runbook/recordings/`. One YAML
  per test method; **filename == test method name** (`test_runbook_crud` →
  `runbook/recordings/test_runbook_crud.yaml`).
- Record live once against a real project, then rely on VCR playback in CI (default test mode).
- **Scrubbing:** register replacers so subscription IDs → `00000000-0000-0000-0000-000000000000`, and
  **SAS tokens / `sig=` query params / bearer tokens are removed** from recorded requests and responses
  (extend `ScenarioTest` `setUp` with `self.recording_processors` / `self.replay_processors`).
- Use `ResourceGroupPreparer` where a live RG is needed; use fixed `self.kwargs` names for stable
  playback. Mark inherently live-only flows (LRO that can't be deterministically recorded) with
  `@live_only()`; use `@record_only()` for flows that must not run live in CI.
- Sensitive files (`sample_parameters.json`) contain only synthetic data.
- Recording tests are a **release requirement** (spec Open Q#4) — this is the gating deliverable
  alongside example-bearing help.

---

## 15. Incremental implementation plan

Deliver in vertical slices so the architecture is proven before breadth is added (spec §6). **Each phase
is a loop: keep iterating on that phase until its acceptance criteria are ALL met, then — and only then —
move to the next phase.** Every phase ships with its help entries (with examples), unit tests, and at least
one recording test.

**Agent loop protocol (how to iterate each phase):**

1. Implement/adjust the phase's files.
2. Run the phase's **`Verify`** command(s).
3. If any check fails → read the failure, fix the specific cause, **go back to step 2** (do not advance).
4. When **every** checkbox is `[x]` and `Verify` is clean → mark the phase done and start the next phase.
5. **Stop and escalate** (don't loop forever) if the same check fails after ~3 fix attempts, or if a
   failure is a genuine external blocker (unpublished API, missing service-side contract). Record the
   blocker; skip only that command's live portion (use `@live_only()`/`@record_only()` as noted in §14).

The global `Verify` for every phase is `azdev style migrate && azdev linter migrate && azdev test migrate`
(plus the phase-specific commands below). "Green in playback" means the recorded test passes with no live
credentials.

- **Phase 0 — Skeleton & wiring:** create the `shared/` layer + `runbook/` package; register an empty
  command group; add the loader hooks in `__init__.py`; confirm `az migrate runbook -h` renders with no
  impact on existing commands. Establish `shared/constants`, `arm_client`, `arm_ids`, `errors`,
  `telemetry` and `runbook/transformers` shells.
  - **Acceptance criteria (loop until all `[x]`):**
    - [ ] `az migrate runbook -h` renders the group.
    - [ ] `az migrate -h` still lists every existing `get-discovered-server`/`local` command unchanged.
    - [ ] extension imports with no errors; empty `shared/`+`runbook/` skeletons import cleanly.
    - [ ] `azdev style`/`azdev linter` pass on the new packages.
  - **Verify:** `az migrate runbook -h && az migrate -h && azdev style migrate && azdev linter migrate`
    (no REST is called yet).
- **Phase 1 — First subgroup (`runbook` core):** implement `generate/show/list/delete` + `wait`
  end-to-end, including one recording test and unit tests. **This locks the patterns** (§16).
  - **Acceptance criteria (loop until all `[x]`):**
    - [ ] all five commands work against a **real** project (live run once).
    - [ ] `test_runbook_crud` recording is **green in playback**.
    - [ ] unit tests cover `arm_ids`, `models`, `transformers`, and **every** `validators` branch for these
      commands.
    - [ ] `--output table` renders the runbook view; `--no-wait` and `wait --custom` both behave.
    - [ ] help has an **example** per command; existing commands still load.
  - **Verify:** `azdev test migrate --tests test_runbook_crud && azdev test migrate --tests
    test_runbook_unit && azdev linter migrate && azdev style migrate` (= §16 acceptance).
- **Phase 2 — `runbook update/regenerate` + `definition show/download`** (adds PATCH, `Regenerate`, and
  `GenerateDownloadUrl` SAS→ZIP handling in `shared/files.py`).
  - **Acceptance criteria (loop until all `[x]`):**
    - [ ] `update` (PATCH) and `regenerate` (POST, no body) round-trip against a real runbook.
    - [ ] `definition download` fetches the SAS URL, downloads, and `zipfile`-extracts to the target path
      (path-traversal-safe, defaults to CWD); a unit test extracts a sample ZIP.
    - [ ] `definition show` table view renders.
    - [ ] recording test(s) **green in playback**; **no** SAS/token leaks in recordings.
  - **Verify:** `azdev test migrate --tests test_runbook_definition && grep -RiL "sig=\|Bearer"
    src/migrate/**/recordings/*.yaml && azdev linter migrate && azdev style migrate`.
- **Phase 3 — `definition step` (Add/Update/DeleteStep) + `definition workstream`
  (Split/MergeWorkstreams)** — all via `post_action`; the step CLI-arg → REST-body mapping (§1.3.5) is
  settled here. **Completes the runbook-definition surface before moving to executions.**
  - **Acceptance criteria (loop until all `[x]`):**
    - [ ] `step add/update/remove` and `workstream split/merge` all succeed via the single `post_action`.
    - [ ] `models.py` maps every CLI arg (incl. approval / custom-script parameter-sets, shared by `add`
      **and** `update`) onto the correct body.
    - [ ] `validators` reject **every** invalid parameter-set combo (unit-tested accept/reject matrix).
    - [ ] `MergeWorkstreams` `--source-workstream-ids` serializes as an array; `remove` honors
      `confirmation`.
    - [ ] recording test(s) **green in playback**.
  - **Verify:** `azdev test migrate --tests test_runbook_step test_runbook_workstream && azdev linter
    migrate && azdev style migrate`.
- **Phase 4 — `execution` (start/show/list + pause/resume/cancel via `PerformAction`)** +
  `--no-wait`/`--watch`. Uses the confirmed `RunbookExecutionAction` codes (`Pause=1, Resume=2, Cancel=3`).
  - **Acceptance criteria (loop until all `[x]`):**
    - [ ] `start` (PUT `{properties:{}}`), `show`, `list` (nextLink paging) work against a real runbook.
    - [ ] `pause/resume/cancel` send the correct integer `PerformAction` code and the service transitions
      state accordingly; `cancel` honors `confirmation`.
    - [ ] `--no-wait` returns the initial execution object; `--watch` re-renders the table each `--interval`
      until a terminal state and exits cleanly on `Ctrl+C` (`ManualInterrupt`).
    - [ ] execution table transformer renders; recording test(s) **green in playback**.
  - **Verify:** `azdev test migrate --tests test_runbook_execution && azdev linter migrate && azdev style
    migrate`.
- **Phase 5 — `execution step` (retry via `PerformAction`, approve via `ProvideApproval`, complete via
  `UpdateStepStatus`)** + `parameter upload`.
  - **Acceptance criteria (loop until all `[x]`):**
    - [ ] `step retry` sends `PerformAction action=4`; `approve` sends `ProvideApproval {action:"Approve"}`;
      `complete` sends `UpdateStepStatus {action:"Complete"}` — each against a real paused/awaiting step,
      and the step transitions.
    - [ ] `parameter upload` uploads the file and the service accepts it.
    - [ ] `--comment`/parameter-set validators enforced (unit-tested).
    - [ ] recording test(s) **green in playback**.
  - **Verify:** `azdev test migrate --tests test_runbook_execution_step test_runbook_parameter && azdev
    linter migrate && azdev style migrate`.
- **Phase 6 — `visualize`** (definition + execution) — pure client-side.
  - **Acceptance criteria (loop until all `[x]`):**
    - [ ] `definition visualize` and `execution visualize` each emit a **single self-contained** `.html`
      with **no** external/CDN references (verified by scanning the output for `http`/`src=`).
    - [ ] a unit test asserts a malicious step name (`<script>…`) is **HTML-escaped** (the XSS guard,
      spec §5).
    - [ ] `graph.py` unit tests cover DAG build, cycle detection, and dangling-`dependsOn` handling.
    - [ ] output path is path-traversal-safe and defaults to CWD; optional `--open` launches the browser.
  - **Verify:** `azdev test migrate --tests test_runbook_visualize && azdev linter migrate && azdev style
    migrate`. **No live ARM call beyond the single read** — runs in unit/playback without recordings.

**Future / not-yet-scheduled (TODO):**

- **Peer groups** `migrate wave`, `migrate project`, `migrate workload` (show/list) +
  `workload update-target-settings` — **not implemented now.** When added, **each becomes its own feature
  package named after the group** (`wave/`, `project/`, `workload/`) reusing `shared/`, once their REST
  contracts are confirmed. No generic `supporting/` package.
- **Migrate the existing `local` commands to the feature-package pattern** (§2.4) — a pure refactor into a
  `local/` peer package reusing `shared/`, with unchanged command paths. Out of scope now; best sequenced
  after the runbook feature is stable.
- Any endpoints still unpublished when the phases above complete.

**Why incremental:** it isolates risk to a small surface, gets an early reviewable pattern, lets the
service team validate the raw-REST approach on real endpoints before we scale to ~30 commands, and means
unpublished APIs (steps, actions) don't block the commands whose REST already exists.

---

## 16. First subgroup implementation plan (`migrate runbook` core)

Target commands: `generate`, `show`, `list`, `delete`, `wait` (the ones with confirmed REST).

Files touched/created:

1. `shared/constants.py` + `runbook/constants.py` — provider `Microsoft.Migrate`, api-version registry and
   project/runbook ID templates (shared); `scopeType` value, runbook status enum, fault types (runbook).
2. `shared/arm_ids.py` — `project_id`, `runbook_id`, `resolve_ids` (+`--ids`), `with_api_version`.
3. `shared/arm_client.py` — `get/get_or_none/list(paged)/put/delete` over `send_raw_request` (reusing
   existing `_utils` where it fits), routing through `errors`.
4. `shared/errors.py` — `raise_for_arm_error` + message hints + telemetry hook.
5. `runbook/models.py` — `build_generate_body(wave_id)`.
6. `runbook/transformers.py` — runbook list/show table view.
7. `runbook/validators.py` — `validate_generate` (wave + name), name/id resolution guard.
8. `runbook/cmds/runbook.py` — `generate` (PUT, `supports_no_wait`), `show` (GET), `list_` (GET+filter by
   `--wave-name`/`--status`, AND-combinable per spec §1.3), `delete` (DELETE, `confirmation`).
9. `commands.py` / `params.py` / `_help.py` — register the 5 commands, args, help **with examples**.
10. Tests — `runbook/test_runbook_unit.py` (ids, body, transformer, validators) +
    `runbook/test_runbook_scenario.py::test_runbook_crud` with `runbook/recordings/test_runbook_crud.yaml`.

Acceptance for Phase 1: `az migrate runbook generate/show/list/delete/wait` work against a real project;
recording test green in playback; existing `migrate`/`migrate local` commands unaffected
(`az migrate -h` still lists them); linter/style pass.

---

## 17. Extensibility strategy

- **New endpoint:** add a body builder in `models.py` + one function in the relevant `cmds/*` module +
  one registration line. No client changes (client is verb-generic).
- **New subgroup:** add `cmds/<path>.py` (filename = subgroup path, e.g. `definition_step.py`), a
  `command_group('migrate runbook <path>')` block, args, help. Zero changes elsewhere.
- **New nested subgroup (2+ levels):** same rule — the file name encodes the full path under the feature
  root with underscores; depth is unlimited and same-named leaves (`definition step` vs `execution step`)
  never collide.
- **New top-level peer group / feature area:** add a new feature package **named after the group**
  (e.g. `wave/`, `project/`, `workload/`) with its own `commands/params/_help/cmds/`, reusing the `shared/`
  layer; add one loader hook in `__init__.py`. No changes to `runbook/`. (No generic `supporting/` folder.)
- **New API version:** change one constant (`RUNBOOKS_API_VERSION`); optionally keep a per-resource-type
  version map in `constants.py` (as k8s-extension does) if different resources diverge.
- **New command type (client-side like `visualize`):** drop under `visualize/` or a new sibling package;
  it reuses `arm_client` only for the read, then transforms locally.
- **New action endpoint:** because ~13 endpoints share `POST {resourceId}/{action}`, a new action is just
  a body builder + a one-line `post_action(id, '<ActionName>', body)` call — no client change at all.

---

## 18. Risks and mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| `PerformAction` integer action codes | pause/resume/cancel/retry must send the right code | **Codes confirmed** from service enum `RunbookExecutionAction` (`Pause=1, Resume=2, Cancel=3, Retry=4`); single `ExecutionAction` enum in `models.py`; one-place fix if they ever change |
| Utility duplication across subgroups (the stated concern) | Maintenance drift | **Single cross-feature `shared/` layer**; `cmds/*` hold logic only; lint rule: `shared/` never imports a feature package (§2.1) |
| CLI-spec step params vs `AddStep` body mismatch (§1.3.5) | Wrong step payload | `models.py` mapping layer CLI args → REST body; confirm step-type/approval mapping |
| `action` typed as int (PerformAction) vs string (Approve/Complete) | Serialization bug | Two explicit enums + two body builders in `models.py` |
| WaveId construction wrong (generate only) | 400 from ARM on `generate` | `waveId = {project_id}/waves/{wave}` built + normalized in `models`/`arm_ids`; unit-tested |
| LRO shape unknown (async header vs status polling) | `--no-wait`/`wait` behavior | `polling.py` supports both `Azure-AsyncOperation`/`Location` headers and status-field polling; `wait` bound to `show` per spec §7 |
| `GenerateDownloadUrl` returns a ZIP (not raw JSON) | Download commands break if treated as JSON | `files.py` downloads SAS then `zipfile`-extracts; unit-tested with a sample zip |
| Recording secrets (SAS/tokens) leaking into YAML | Security | Mandatory scrubbers in test setUp; never log bodies in `arm_client` |
| XSS in `visualize` HTML (user-controlled names) | Script injection in emitted file | Mandatory HTML-escaping + fully inline/offline assets (spec §5); unit test asserts encoding |
| Regressing existing `migrate`/`local` commands | Broken GA-ish surface | Additive registration only; no edits to existing modules except two append-only loader hooks; scenario test asserts existing commands still load |
| `knack.CLIError` vs `azclierror` mix | Inconsistent UX | New code standardizes on `azclierror`; existing code left as-is (no forced refactor) |
| Large `custom.py`-style monoliths | Maintainability | Per-verb/per-subgroup modules; module/function size limits (§ code quality) |

---

## 19. Recommended improvements (after reviewing repo + spec)

1. **Adopt `azclierror` typed exceptions** in new code (existing extension uses `knack.CLIError`); improves
   telemetry classification and matches current Az CLI guidance. Do not refactor existing commands now.
2. **Introduce recording tests** for the migrate extension (none exist today) — required for release and
   raises overall quality; start with the runbook subgroup.
3. **Centralize telemetry** (the existing migrate code has none); add the thin `telemetry.py` wrapper so
   faults are measurable in preview.
4. **Add secret scrubbing** to any future recordings globally (shared test base) — protects the SAS URLs
   returned by `GenerateDownloadUrl`.
5. **Document the raw-REST pattern** (this doc + a short `runbook/README` developer note) so future API
   additions follow the same seams; keep command **examples in `_help.py`** (release requirement).
6. **The `PerformAction` integer codes are confirmed** (`RunbookExecutionAction`: `Pause=1, Resume=2,
   Cancel=3, Retry=4`, etc.) — no open contract detail remains; nothing blocks Phase 1.
7. **Pin a single `RUNBOOKS_API_VERSION`** and thread it exclusively through `arm_ids.with_api_version`
   so version bumps are one-line.
8. **Naming conventions to standardize** (see below).

### Naming conventions

- **Shared modules:** lowercase, purpose-named (`arm_client.py`). **Command-logic modules** live in `cmds/`,
  one per (sub)group, filename = the subgroup path below the feature root (`runbook.py`, `definition.py`,
  `definition_step.py`, `execution_step.py`).
- **Command functions:** verb-first, snake_case, matching CLI verb (`generate`, `show`, `list_`,
  `update`, `delete`, `pause_execution`…); trailing underscore only to avoid builtins (`list_`).
- **Request builders:** `build_<thing>_body(...)` in `models.py`.
- **Response transformers:** `<thing>_table(result)` in `transformers.py`.
- **ID builders:** `<scope>_id(...)` in `arm_ids.py`.
- **Constants:** UPPER_SNAKE in `constants.py`; enums as `str`-valued Enums.
- **Validators:** `validate_<command>(namespace)`; **fault types:** `RUNBOOK_<AREA>_ERROR`.

### Documentation, code quality

- **Docs:** command examples in `runbook/_help.py`; architecture in this file
  ([docs/runbook-cli-design.md](runbook-cli-design.md)); a short developer `README` in `runbook/`;
  `HISTORY.rst` bump per release.
- **Module size:** keep operation modules < ~250 lines; split when a subgroup grows.
- **Function size:** command functions ~15–40 lines; helpers single-responsibility.
- **Typing:** type hints on all new helper/model/client signatures.
- **Linting:** honor repo `pylintrc`; register any unavoidable exceptions in
  `src/migrate/linter_exclusions.yml` (as the extension already does) rather than disabling globally.
- **Comments/docstrings:** module + public-function docstrings; comment *why*, not *what*.
- **Dependency direction:** enforce the one-way layering in §3; `cmds` must never import `commands`, and
  `shared/` must never import a feature package.

---

## Appendix — command → REST/behavior mapping (initial)

| CLI command | Method | Endpoint (relative to `{MigrateProjectResourceId}`) | Notes |
| --- | --- | --- | --- |
| `runbook generate` | PUT | `/runbooks/{n}` | body `scope=Wave/waveId`; `--no-wait` |
| `runbook generate` (re-run) | POST | `/runbooks/{n}/Regenerate` | no body |
| `runbook show` | GET | `/runbooks/{n}` | |
| `runbook list` | GET | `/runbooks` | client-side AND filter by wave/status |
| `runbook update` | PATCH | `/runbooks/{n}` | editable metadata |
| `runbook delete` | DELETE | `/runbooks/{n}` | confirmation |
| `runbook wait` | GET | `/runbooks/{n}` | native `custom_wait_command` over custom `show` |
| `definition show` | GET | `/runbooks/{n}` | projected/filtered; table view |
| `definition download` | POST | `/runbooks/{n}/GenerateDownloadUrl` | SAS URL → **ZIP** (spec + docs) |
| `definition visualize` | GET + local | `/runbooks/{n}` | client-side HTML |
| `definition step add` | POST | `/runbooks/{n}/AddStep` | body `{stepName, displayName, stepRef, migrationEntityIds, dependsOn}`; type-specific params (approval-type / run-mode+execution-target) mapped by `models.py` |
| `definition step update` | POST | `/runbooks/{n}/UpdateStep` | body `{stepId, displayName, dependsOn, …}`; **same parameter-sets as `step add`** (approval-type / run-mode+execution-target) |
| `definition step remove` | POST | `/runbooks/{n}/DeleteStep` | body `{stepId}`; confirmation |
| `definition workstream split` | POST | `/runbooks/{n}/SplitWorkstream` | body `{sourceWorkstreamId, stepIds, newWorkstreamName}` (`--step-ids` moves steps into the new workstream) |
| `definition workstream merge` | POST | `/runbooks/{n}/MergeWorkstreams` | body `{workstreamId[], newWorkstreamName?}` (`--new-workstream-name` optional; defaults to first) |
| `parameter download` | POST | `/runbooks/{n}/GenerateDownloadUrl` | SAS URL → ZIP |
| `parameter upload` | POST/PUT | upload API | contract TBD |
| `execution start` | PUT | `/runbooks/{n}/executions/{id}` | body `{properties:{}}`; `--no-wait` |
| `execution show` | GET | `/runbooks/{n}/executions/{id}` | status.json projection; `--watch` |
| `execution list` | GET | `/runbooks/{n}/executions` | `nextLink` paged |
| `execution pause/resume/cancel` | POST | `/runbooks/{n}/executions/{id}/PerformAction` | body `{action:<int>, targetId, migrationEntityIds}` (`pause=1`/`resume=2`/`cancel=3`); `cancel` confirmation |
| `execution step retry` | POST | `/runbooks/{n}/executions/{id}/PerformAction` | body `{action:4, targetId:<stepId>, migrationEntityIds}` (`retry=4`) |
| `execution step approve` | POST | `/runbooks/{n}/executions/{id}/ProvideApproval` | body `{action:"Approve", targetId:<stepId>, migrationEntityIds}` |
| `execution step complete` | POST | `/runbooks/{n}/executions/{id}/UpdateStepStatus` | body `{action:"Complete", targetId:<stepId>, migrationEntityIds}` |
| `execution (patch status)` | PATCH | `/runbooks/{n}/executions/{id}` | body `{status}` (internal/optional) |
| `execution download-status` | POST | `/runbooks/{n}/executions/{id}/GenerateDownloadUrl` | SAS URL → ZIP (status.json) |
| `execution visualize` | GET + local | `/runbooks/{n}/executions/{id}` | client-side HTML |
| `wave/project/workload show/list` | GET | supporting endpoints | contract TBD |
| `workload update-target-settings` | PATCH | supporting endpoint | contract TBD |
