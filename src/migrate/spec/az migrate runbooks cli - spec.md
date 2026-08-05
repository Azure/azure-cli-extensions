# Azure Migrate runbooks – Az CLI commands

This document describes the Azure CLI commands required for the v1 release of the Azure Migrate runbooks capability. Azure CLI is planned to be the primary interface for the first release.

Azure CLI for Azure Migrate is being built for the first time, so we will create a new extension for `migrate` commands and publish it to the Az CLI extension repository. Az CLI commands are organized as:

```azurecli
az [ group ] [ subgroup ] [ command ] {parameters}
```

For Azure Migrate, the group is `migrate`. For runbook commands the subgroup is `runbook` (singular, per Azure CLI naming conventions).

We need to support the following scenarios via Azure CLI:

1. Generate a runbook from a wave
2. Edit/customize the runbook
3. Download a runbook
4. Execute a runbook
5. Track runbook execution status

## Conventions

These conventions apply to every command in this spec unless stated otherwise.

### Resource identity

- Runbook name: `--name/-n`.
- Project: `--resource-group/-g` + `--project-name`. Full ARM resource IDs are supported via the auto-provided `--ids` parameter, so users may pass a runbook resource ID instead of `-g`/`--project-name`/`-n`.
- Wave: `--wave-name`.

### Execution identity

An execution is an ARM **child resource of a runbook** (`.../runbooks/<runbook>/executions/<execution-id>`) and therefore has its own resource ID. For every command that acts on an **existing** execution (`execution pause | resume | cancel | show`, and `execution step retry | approve | complete`, and `execution visualize`):

- The execution is addressed by `--execution-id` together with its parent (`-g` + `--project-name` + `--runbook-name`); **or**
- A single `--ids <execution-resource-id>` may be supplied instead, which encodes the full parent chain (subscription, resource group, project, runbook, execution) and replaces all four parameters.

`--runbook-name` is only required on these commands when the explicit (non-`--ids`) form is used; with `--ids` it is redundant. `execution start` is the exception — it creates a new execution and so is addressed by the parent runbook (`-g` + `--project-name` + `--runbook-name`), returning the new execution id. `execution list` likewise operates on the runbook.

### Global parameters (inherited, do not redefine)

Every command automatically inherits the Az CLI global parameters: `--output/-o` (`json` | `jsonc` | `table` | `tsv` | `yaml`), `--query` (JMESPath), `--subscription`, `--verbose`, `--debug`, and `--help/-h`. Where a command lists a "default table view", that is the output transformer used when `--output table` is selected; JSON remains the default machine output.

### Enums

All constrained values are fixed enums (no spaces) to enable validation and tab-completion:

- Runbook status: `Generating | New | ReadyToStart | InExecution | Paused | Completed | Failed`
- Step type: `Manual | Approval | CustomScript`
- Approval type: `Partial | Full`
- Run mode: `Once | PerEntity`
- Execution target: `Appliance | SourceVm | TargetVm`

### List inputs

Parameters that accept multiple values (e.g. `--depends-on`, `--entities-to-move`, `--source-workstream-ids`) accept a space-separated list, e.g. `--depends-on step1 step2 step3`.

### Long-running operations

`generate` and `execution start` are long-running. They support `--no-wait` to return immediately. When `--no-wait` is used, callers can block on completion using the standard `az migrate runbook wait` command (see [Section 7](#7-waiting-on-long-running-operations)).

### Argument constraints

Where parameters are required or allowed only in combination with others, each command lists an explicit **Argument constraints** subsection. Azure CLI has no native parameter-set construct, so these are enforced by command validators.

---

## 1. Generate a runbook from a wave

### 1.1 az migrate runbook generate

Generates a runbook for a given wave. In future, to support express migrations, this may also accept a scope (a list of migration entities).

```azurecli
az migrate runbook generate -g <resource-group> --project-name <project-name> -n <runbook-name> --wave-name <wave-name> [--no-wait]
```

Outputs the runbook resource ID and the details of the runbook resource (initially in `Generating` state).

```text
Runbook is being generated.
Runbook id: /subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.Migrate/migrateProjects/<project>/runbooks/<runbook-name>

<runbook object, state = Generating, in json (default) or table>
```

Track generation progress with `az migrate runbook show`, or block with `az migrate runbook wait --custom "properties.status=='New'"`.

### 1.2 az migrate runbook show

Shows the details of a single runbook.

```azurecli
az migrate runbook show -g <resource-group> --project-name <project-name> -n <runbook-name>
```

Outputs the runbook ARM object in the format defined by `--output`.

### 1.3 az migrate runbook list

Lists runbooks in a project.

```azurecli
az migrate runbook list -g <resource-group> --project-name <project-name>
```

Supports combinable (AND) filters by wave and by status:

```azurecli
az migrate runbook list -g <rg> --project-name <project> --wave-name <wave-name>
az migrate runbook list -g <rg> --project-name <project> --status InExecution
az migrate runbook list -g <rg> --project-name <project> --wave-name <wave-name> --status InExecution
```

### 1.4 az migrate runbook update

Updates editable runbook metadata (e.g. description).

```azurecli
az migrate runbook update -g <rg> --project-name <project> -n <runbook-name> [--description <text>]
```

### 1.5 az migrate runbook delete

Deletes a runbook.

```azurecli
az migrate runbook delete -g <rg> --project-name <project> -n <runbook-name> [--yes]
```

Prompts for confirmation unless `--yes` is supplied.

---

## 2. Edit/customize the runbook

The runbook definition is a single document. All read and edit operations are grouped under the `definition` subgroup. Steps and workstreams are sub-objects of the definition (not ARM resources); edits read-modify-write the definition and are addressed by `--runbook-name` plus `--step-id`/`--workstream-id`.

### 2.1 az migrate runbook definition show

Shows the contents (definition) of a single runbook. Reads of individual steps/workstreams are filtered projections of this command (there are no separate `step show`/`step list` commands).

```azurecli
az migrate runbook definition show -g <rg> --project-name <project> -n <runbook-name> \
  [--workstream-id <workstream-id>] [--step-id <step-id>]
```

- `--workstream-id` limits output to a single workstream.
- `--step-id` limits output to a single step.

Outputs the runbook definition. Default table view: one table per workstream.

```text
Id, Step Name, Depends On, Configuration Status, Workloads, Applications
```

### 2.2 az migrate runbook definition step add

Adds a single step to the runbook definition.

```azurecli
az migrate runbook definition step add -g <rg> --project-name <project> --runbook-name <runbook-name> \
  --step-type <Manual|Approval|CustomScript> \
  --step-name <display-name> \
  [--step-description <text>] \
  [--depends-on <step-id> [<step-id> ...]] \
  [--approval-type <Partial|Full>] \
  [--run-mode <Once|PerEntity>] \
  [--execution-target <Appliance|SourceVm|TargetVm>]
```
Parameter set - Manual
```azurecli
az migrate runbook definition step add -g <rg> --project-name <project> --runbook-name <runbook-name> \
  --step-type Manual \
  --step-name <display-name> \
  [--step-description <text>] \
  [--depends-on <step-id> [<step-id> ...]]
  
```
Parameter set - Approval
```azurecli
az migrate runbook definition step add -g <rg> --project-name <project> --runbook-name <runbook-name> \
  --step-type Approval \
  --step-name <display-name> \
  [--step-description <text>] \
  [--depends-on <step-id> [<step-id> ...]] \
  [--approval-type <Partial|Full>]  
  
```
Parameter set - CustomScript
```azurecli
az migrate runbook definition step add -g <rg> --project-name <project> --runbook-name <runbook-name> \
  --step-type CustomScript \
  --step-name <display-name> \
  [--step-description <text>] \
  [--depends-on <step-id> [<step-id> ...]] \  
  [--run-mode <Once|PerEntity>] \
  [--execution-target <Appliance|SourceVm|TargetVm>]  
```

**Argument constraints:**

- Required when `--step-type Approval`: `--approval-type`.
- Allowed only when `--step-type CustomScript`: `--run-mode`, `--execution-target`.

Default table view:

```text
Id, Step Name, Depends On, Configuration Status, Workloads, Applications
```

### 2.3 az migrate runbook definition step update

Updates a single step in the runbook definition.

```azurecli
az migrate runbook definition step update -g <rg> --project-name <project> --runbook-name <runbook-name> \
  --step-id <step-id> \
  [--step-name <display-name>] \
  [--step-description <text>] \
  [--depends-on <step-id> [<step-id> ...]]
```

Default table view:

```text
Id, Step Name, Depends On, Configuration Status, Workloads, Applications
```

### 2.4 az migrate runbook definition step remove

Removes a step from the runbook definition.

```azurecli
az migrate runbook definition step remove -g <rg> --project-name <project> --runbook-name <runbook-name> --step-id <step-id> [--yes]
```

### 2.5 az migrate runbook definition workstream split

Splits a single workstream into two workstreams.

```azurecli
az migrate runbook definition workstream split -g <rg> --project-name <project> --runbook-name <runbook-name> \
  --source-workstream-id <workstream-id> \
  --new-workstream-name <display-name> \
  --entities-to-move <entity> [<entity> ...]
```

Default table view:

```text
Id, Step Name, Depends On, Configuration Status, Workloads, Applications
```

### 2.6 az migrate runbook definition workstream merge

Merges two or more workstreams into a single workstream.

```azurecli
az migrate runbook definition workstream merge -g <rg> --project-name <project> --runbook-name <runbook-name> \
  --source-workstream-ids <workstream-id> [<workstream-id> ...] \
  --new-workstream-name <display-name>
```

Default table view:

```text
Id, Step Name, Depends On, Configuration Status, Workloads, Applications
```

### 2.7 az migrate runbook parameter download

Downloads the current version of the parameters file stored with the service.

```azurecli
az migrate runbook parameter download -g <rg> --project-name <project> --runbook-name <runbook-name> [--file <path>]
```

Downloads the JSON parameters file. If `--file` is omitted, the file is written to the current directory. Outputs the file path.

```text
Parameters file downloaded and saved to <file path>
```

### 2.8 az migrate runbook parameter upload

Uploads a new version of the parameters file from the filesystem, replacing the version stored with the service.

```azurecli
az migrate runbook parameter upload -g <rg> --project-name <project> --runbook-name <runbook-name> --file <params.json>
```

Uploads the JSON parameters file, validates it, and reports validation status and whether the parameters file was successfully updated.

```text
Parameters file uploaded to Azure Migrate.
<validation result, json>
```

---

## 3. Download a runbook

### 3.1 az migrate runbook definition download

Downloads the current version of the definition (spec) file stored with the service, along with the documentation markdown.

```azurecli
az migrate runbook definition download -g <rg> --project-name <project> -n <runbook-name> [--destination <dir>]
```

Downloads the definition JSON file and the documentation markdown file into `--destination` (defaults to the current directory). Outputs both file paths.

```text
Runbook definition file downloaded and saved to <file path>
Runbook documentation file downloaded and saved to <file path>
```

---

## 4. Execute a runbook

> For commands that act on an existing execution, the `-g --project-name --runbook-name --execution-id` parameters shown below may be replaced by a single `--ids <execution-resource-id>` (see [Execution identity](#execution-identity)).

### 4.1 az migrate runbook execution start

Starts the execution of a runbook.

```azurecli
az migrate runbook execution start -g <rg> --project-name <project> --runbook-name <runbook-name> [--no-wait]
```

Outputs the execution ID and the details of the execution.

```text
Runbook execution started. Execution id: <execution-id>
<execution object body>
```

> **Implementation note (v1):** `execution start` is implemented as a POST
> `execute` action on the parent runbook resource. The service creates and
> names the new execution and returns its id; the CLI does **not** PUT a
> client-generated execution id.

### 4.2 az migrate runbook execution pause

Pauses an in-progress execution.

```azurecli
az migrate runbook execution pause -g <rg> --project-name <project> --runbook-name <runbook-name> --execution-id <execution-id>
```

```text
Runbook execution paused. Execution id: <execution-id>
<execution object body>
```

### 4.3 az migrate runbook execution resume

Resumes a paused execution.

```azurecli
az migrate runbook execution resume -g <rg> --project-name <project> --runbook-name <runbook-name> --execution-id <execution-id>
```

```text
Runbook execution resumed. Execution id: <execution-id>
<execution object body>
```

### 4.4 az migrate runbook execution cancel

Cancels an in-progress or paused execution. Cancellation is terminal — a cancelled execution cannot be resumed (start a new execution instead).

```azurecli
az migrate runbook execution cancel -g <rg> --project-name <project> --runbook-name <runbook-name> --execution-id <execution-id> [--yes]
```

Prompts for confirmation unless `--yes` is supplied.

```text
Runbook execution cancelled. Execution id: <execution-id>
<execution object body>
```

### 4.5 az migrate runbook execution step retry

Restarts the execution of a failed step in the runbook.

```azurecli
az migrate runbook execution step retry -g <rg> --project-name <project> --runbook-name <runbook-name> \
  --execution-id <execution-id> --step-id <step-id>
```

Outputs the step status from `status.json`.

```text
Step retry started.
<step json snippet from status.json>
```

### 4.6 az migrate runbook execution step approve

Provides approval for an `Approval`-type step during execution.

```azurecli
az migrate runbook execution step approve -g <rg> --project-name <project> --runbook-name <runbook-name> \
  --execution-id <execution-id> --step-id <step-id> \
  [--entities <entity-id> [<entity-id> ...]] [--all-ready]
```

- For a **Full** approval step, the whole step is approved; `--entities`/`--all-ready` are not required.
- For a **Partial** approval step, approval is granted per entity. Supply the entities to approve via `--entities`, or `--all-ready` to approve every currently ready entity.
- **Ready entities** are those that have completed the step's predecessor(s) and are therefore eligible for approval. Discover them with `az migrate runbook execution show --step-id <step-id>` (their workload/entity progress shows as ready/waiting for approval).

**Argument constraints:**

- The target step must be of type `Approval` (otherwise the command errors).
- Allowed only when the step's approval type is `Partial`: `--entities`, `--all-ready`.
- `--entities` and `--all-ready` are mutually exclusive.

```text
Step approval recorded.
<step json snippet from status.json>
```

### 4.7 az migrate runbook execution step complete

Marks a `Manual`-type step as complete during execution. A comment is required to record who/why the step was completed (captured in `status.json`).

```azurecli
az migrate runbook execution step complete -g <rg> --project-name <project> --runbook-name <runbook-name> \
  --execution-id <execution-id> --step-id <step-id> --comment <text>
```

**Argument constraints:**

- The target step must be of type `Manual` (otherwise the command errors).
- `--comment` is required.

```text
Step marked as complete.
<step json snippet from status.json>
```

### 4.8 az migrate runbook execution show

Shows (tracks) the execution status of a runbook. Replaces the previous `track-execution` command.

```azurecli
az migrate runbook execution show -g <rg> --project-name <project> --runbook-name <runbook-name> --execution-id <execution-id>
```

Outputs the status from `status.json`. Default table view:

```text
Id, Step Name, Step Status, Depends On, Workload Progress
```

Filter to a single step:

```azurecli
az migrate runbook execution show -g <rg> --project-name <project> --runbook-name <runbook-name> \
  --execution-id <execution-id> --step-id <step-id>
```

Optionally auto-refresh the status on an interval with `--watch`:

```azurecli
az migrate runbook execution show -g <rg> --project-name <project> --runbook-name <runbook-name> \
  --execution-id <execution-id> --watch
```

> Note: `--watch` is a custom client-side polling option (Azure CLI has no native watch). It periodically re-renders the status table until interrupted.

### 4.9 az migrate runbook execution list

Lists the executions for a runbook.

```azurecli
az migrate runbook execution list -g <rg> --project-name <project> --runbook-name <runbook-name>
```

---

## 5. Visualize (nice to have)

Because the CLI is the only interface for v1 and runbooks are inherently graph-shaped (a DAG of steps across workstreams), these commands render a self-contained HTML view that the user can open in a browser. They are read-only snapshots of the current state.

### 5.1 az migrate runbook definition visualize

Renders the runbook definition (workstreams, steps, dependency DAG, and per-step configuration status) as an HTML file.

```azurecli
az migrate runbook definition visualize -g <rg> --project-name <project> -n <runbook-name> [--file <path>] [--open]
```

- Writes a self-contained HTML file and prints its path.
- `--file` sets the output path (defaults to the current directory).
- `--open` launches the file in the default browser (mirrors the `az aks browse` / `az webapp browse` pattern).

```text
Runbook definition visualization saved to <file path>
```

### 5.2 az migrate runbook execution visualize

Renders the execution status (the dependency DAG annotated with step status and workload progress) as an HTML file.

```azurecli
az migrate runbook execution visualize -g <rg> --project-name <project> --runbook-name <runbook-name> \
  --execution-id <execution-id> [--file <path>] [--open] [--watch]
```

- `--watch` regenerates the snapshot on an interval (client-side polling; Azure CLI has no native watch). v1 is a static snapshot regenerated on refresh, not a live stream.

```text
Runbook execution visualization saved to <file path>
```

> **Implementation constraints:**
> - **Security (mandatory):** step names, descriptions, and workstream names are user-controlled and embedded in the generated HTML — they MUST be HTML-encoded to prevent HTML/script injection (XSS) in the emitted file.
> - **Offline / self-contained:** the HTML must embed all scripts and styles inline (no CDN or remote references), since Azure Migrate users are often in locked-down or air-gapped environments. This also guarantees no outbound network calls.

---

## 6. Supporting az cli commands

> **Deferred — not taken in the first release (v1).** These are nice-to-have
> commands that improve the experience of using the runbook commands. They are
> tracked as to-do items for a later release (see [Section 9](#9-deferred-items-not-in-v1)).

- `az migrate wave show`
- `az migrate wave list`
- `az migrate project show`
- `az migrate project list`
- `az migrate workload show`
- `az migrate workload list`
- `az migrate workload update-target-settings`

---

## 7. Waiting on long-running operations

`az migrate runbook wait` is the standard Azure CLI long-running-operation helper, auto-generated for the runbook resource (which exposes a `show`/GET). It is paired with `--no-wait` on `generate` and `execution start` so scripts can return immediately and then block on a desired state.

```azurecli
# Block until generation completes (runbook leaves the Generating state)
az migrate runbook wait -g <rg> --project-name <project> -n <runbook-name> --custom "properties.status=='New'"

# Block until the resource exists
az migrate runbook wait -g <rg> --project-name <project> -n <runbook-name> --created
```

Supported wait predicates follow the standard set: `--created`, `--deleted`, `--exists`, `--updated`, and `--custom <JMESPath>`, with `--interval` and `--timeout` to control polling.

> Scoping note: `az migrate runbook wait` **is implemented in v1** and paired with `--no-wait` on `generate` and `execution start`.

---

## 8. Open questions
<markdown>
1.Can we develop cli without taking dependency on swagger & SDK and instead making direct api call from cli? We have not published SDK for an existing swagger. As there are multiple teams involved     in effort; we want to enable SDK publishing as separate effort and not get blocked on the same.

[Update] - There are GA extension already leveraging this pattern.

2.How can az migrate extension retrieve logged in user token to make rest api call. Any current sample references would help. 
[Update] - There are GA extension already leveraging this pattern via `send_raw_request()`.

3.Is there any release check list available to release extensions for both public and private preview? We are targeting to release this extension to customers by Aug end (public preview). We are looking for overall effort needed to release the cli extension.
[Update] - For the public preview, you can use the tooling to develop both the CLI and PowerShell experiences. For the private preview, we don't have any specific requirements.
As long as the implementation is complete, you can submit the code to our repository. I'll review the code, and once the review is completed, it can be released at any time.

4.From other extensions, it seems recording tests are needed along with extension code? Are there any additional requirements before release?

[Update] - Recording test cases is required; nothing else is needed. You can just submit the code directly.  doc: must include the example

5.Can we set output type as “table” for some of the command? 
e.g. Refer az migrate runbook definition show 

6.We are planning to implement “vizualize” command to convert json file to static html for better rendering for users? For this purpose, can we keep static html file in repo and update based on info retrieve from service? Any concern with shippig static html file with basic js as part of extension.
[Update] - There is precedence in GA cli to pull exe and helm charts from cli code. Hence this should be fine.

7.We would be supporting -–watch optional parameter which will be blocking command to refesh status periodically. Any concern .with this pattern?
[Update] - There is precedence of this in arc cli which is GA. 

---

## 9. Deferred items (not in v1)

The following are intentionally **not taken in the first release** and are
tracked as to-do items for a later release:

- **`CustomScript` step type** and its associated `definition step add`
  parameters `--run-mode <Once|PerEntity>` and
  `--execution-target <Appliance|SourceVm|TargetVm>` (documented in
  [Section 2.2](#22-az-migrate-runbook-definition-step-add)). v1 supports only
  the `Manual` and `Approval` step types.
- **Supporting `az migrate` commands** in [Section 6](#6-supporting-az-cli-commands):
  `wave show/list`, `project show/list`, and
  `workload show/list/update-target-settings`.

> Delta note: `az migrate runbook wait` (Section 7) was originally optional but
> **is implemented in v1**.

---

## Appendix A. Command grouping

```text
az migrate
│
├── runbook                                  # runbook (ARM resource)
│   ├── generate            -g --project-name -n --wave-name [--no-wait]
│   ├── show                -g --project-name -n
│   ├── list                -g --project-name [--wave-name] [--status]
│   ├── update              -g --project-name -n [--description]
│   ├── delete              -g --project-name -n [--yes]
│   ├── wait                -g --project-name -n [--created|--custom ...]   (Section 7)
│   │
│   ├── definition                           # the definition document
│   │   ├── show            -g --project-name -n [--workstream-id] [--step-id]
│   │   ├── download        -g --project-name -n [--destination]
│   │   ├── visualize       -g --project-name -n [--file] [--open]          (nice-to-have)
│   │   ├── step                             # sub-object of definition (not ARM)
│   │   │   ├── add         --step-type ... (--approval-type | --run-mode/--execution-target)
│   │   │   ├── update      --step-id ...
│   │   │   └── remove      --step-id [--yes]
│   │   └── workstream                       # sub-object of definition (not ARM)
│   │       ├── split       --source-workstream-id --new-workstream-name --entities-to-move
│   │       └── merge       --source-workstream-ids --new-workstream-name
│   │
│   ├── parameter                            # parameters file
│   │   ├── download        -n [--file]
│   │   └── upload          -n --file
│   │
│   └── execution                            # execution (ARM child resource of runbook)
│       ├── start           -g --project-name --runbook-name [--no-wait]
│       ├── pause           «--ids OR -g --project-name --runbook-name --execution-id»
│       ├── resume          « …same addressing… »
│       ├── cancel          « …same… » [--yes]
│       ├── show            « …same… » [--step-id] [--watch]
│       ├── list            -g --project-name --runbook-name
│       ├── visualize       « …same… » [--file] [--open] [--watch]          (nice-to-have)
│       └── step                             # actions on a step within an execution
│           ├── retry       --step-id
│           ├── approve     --step-id [--entities | --all-ready]   (Approval steps)
│           └── complete    --step-id --comment                    (Manual steps)
│
├── wave                                     # supporting (nice-to-have)
│   ├── show
│   └── list
├── project
│   ├── show
│   └── list
└── workload
    ├── show
    ├── list
    └── update-target-settings
```

### Addressing summary

| Subgroup | Backing model | Identity |
| --- | --- | --- |
| `runbook` | ARM resource | `-g` + `--project-name` + `-n` (or `--ids`) |
| `runbook definition step` / `workstream` | sub-objects of the definition (PATCH-based) | `--runbook-name` + `--step-id`/`--workstream-id` (no `--ids`) |
| `runbook parameter` / `definition` | files stored with the service | `--runbook-name` |
| `runbook execution` | ARM child resource | `--execution-id` (+ parent) or `--ids` |
| `runbook execution step` | actions on a step within an execution | execution identity + `--step-id` |
| `wave` / `project` / `workload` | supporting reads | resource-appropriate |

