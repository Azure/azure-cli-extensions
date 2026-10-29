# Saved Logic Apps targets

Contexts were already part of the original extension's `context create/use`
flow. They are local shortcuts, not general Azure CLI contexts: a local target
stores an absolute project path and runtime port; a deployed target stores a
resource group and Logic App Standard site name. No credentials, subscription,
tenant, slot, environment variables or app settings are stored. `az login`,
`az account set` and inherited `--subscription` determine Azure authentication
and subscription on each deployed operation.

Local managed-connection creation can also create Azure resources without a
deployed app. It reads Azure scope from the selected project's
`local.settings.json` (`WORKFLOWS_SUBSCRIPTION_ID`,
`WORKFLOWS_RESOURCE_GROUP_NAME`, `WORKFLOWS_LOCATION_NAME`), with per-command
`--subscription`, `--resource-group`, and `--location` overrides. This does not
extend the context schema, switch the default account, or save cloud coordinates
in a local context. See the [local managed-connection guide](../README.md#managed-connections-for-local-projects)
for required settings, development-key handling and retained-resource limits.

Local `context create` defaults to port 7071 when `--port` is omitted; explicit
ports must be integers from 1 through 65535. This works through the CLI parser,
not only direct command calls. Stored-context validation remains strict:
boolean, floating-point and string port values are invalid.

```powershell
az logicapp context create --name orders-local --path .\orders --port 7071 --use
az logicapp context create --name orders-cloud -g my-rg --logic-app-name my-app
az logicapp context list --output table
az logicapp context list --query "[?active].name" --output json
az logicapp context show
az logicapp context show --name orders-cloud
az logicapp context update --name orders-local --port 7079 --yes
az logicapp context use --name orders-cloud
az logicapp context delete --name orders-local --yes
```

**Inspection never selects a target or creates storage.** Missing storage is an
empty list; `show` without `--name` requires an active context. List is a
name-sorted JSON array. List/show entries retain the original create/use shape:
`name`, `active`, `store`, and `target` with `kind`, `path`, `port`,
`resourceGroup`, `logicAppName`. Inapplicable coordinates are null. Table
output includes the active marker and target coordinates. Unknown saved
metadata is preserved, but not returned, so it is not inadvertently exposed.

**Update is a partial edit, not an upsert.** `--name` always identifies the
existing shortcut; `--logic-app-name` identifies the deployed site. Omitted
coordinates and unrelated metadata survive. At least one target field is
required. Editing an inactive shortcut does not affect selection. Changing an
active shortcut confirms the exact new target unless `--yes` is supplied; it
retains that same context name as active and redirects subsequent commands.
Identical input returns `action: unchanged` without prompting or replacing
the JSON file. A changed input returns `action: updated`.

Changing target kind requires explicit `--kind` and complete new coordinates.
There is no implicit local/cloud conversion or inherited port during conversion:

```powershell
az logicapp context update --name dev --kind cloud -g my-rg --logic-app-name my-app --yes
az logicapp context update --name dev --kind local --path .\orders --port 7071 --yes
```

The old kind's known coordinates are cleared to null. Unknown metadata remains
untouched even during conversion. As with original create, a local project path
need not exist yet; it is expanded and stored as absolute, without inspecting or
changing the project. Paths must be nonempty and ports integers in 1..65535.
Cloud coordinates must be names, not resource IDs or URLs. Empty/invalid
values, credentials-shaped values, missing records and conflicting flags fail
before replacing saved state. CLI argument errors exit nonzero, as do unreadable
stores, unsupported versions, invalid records and concurrent-change conflicts.

**Delete removes one shortcut only.** It prompts unless `--yes` is supplied.
Deleting an inactive shortcut leaves active selection unchanged. Deleting the
active shortcut atomically removes it and clears selection; **no replacement is
chosen**. The result reports `action: deleted`, `active: false`, `wasActive` and
`activeContext` (the remaining selection or null). Project files, Azure
resources, credentials, runtimes and workflow history are never deleted.
Missing names fail rather than report success.

Runtime/cloud commands without an active context then require explicit target
coordinates or a deliberate `context use`. Offline local-authoring commands
use the current directory when no context is selected, but refuse an explicitly
selected cloud context even with `--path`. An active cloud context without an
explicit path is also refused instead of becoming a local destination.
Cloud runtime validation is a separate dual-plane operation:
`workflow validate --context orders-cloud --path .\orders --workflow hello --with-runtime`
validates the explicit local authored file against the deployed runtime.
An invalid/unreadable active store is not silently treated as no
context; supply an explicit project path or repair the saved store deliberately.

## Storage and concurrency boundaries

The location is `<Azure CLI configuration directory>\logicapp\contexts.json`,
using Azure CLI's configuration-root resolver. Without `AZURE_CONFIG_DIR`, this
is the existing `~\.azure\logicapp\contexts.json` location. A custom config root
has an independent store and active selection, with no global-store fallback,
automatic import, cross-profile merge or write-on-read migration. To reuse
shortcuts in another profile, deliberately recreate them there with `context
create`; the original store remains untouched. Cooperating writers use the lock
beside the selected profile's store.
Original unversioned stores are accepted. An explicit `version`, if present,
must be integer `1`; unsupported versions are refused without rewriting them.
All known records and active references are checked on read, including duplicate
JSON keys, non-finite numbers, conflicting target coordinates and wrong types.
Numeric overflow (for example `1e9999`) and nesting deeper than 128 levels are
refused with sanitized errors; invalid bytes are not rewritten and parser errors
do not silently select the current directory.
Cloud resource-group/app coordinates must be literal printable single-segment
names, not dot segments or percent-escaped values. Creation, update and saved-store
loading reject unsafe coordinates without rewriting the store. The same check
guards runtime/identity ARM site-ID construction, including explicit coordinates;
malformed or child-resource site targets cannot substitute another ARM route.
Absent optional inapplicable coordinates are accepted for old valid records.
Unknown top-level, record and target fields are retained through writes.
Context list/show never create a context directory, JSON file or lock file;
Azure CLI itself may initialize its configuration directory during startup.

Create/use/update/delete share a bounded native advisory file lock on
`contexts.json.lock` (Windows byte-range lock, POSIX `flock`). After a prompt
they acquire that lock and re-read the complete snapshot; any changed saved
record or selection causes an explicit conflict, not a blind overwrite or
automatic retry. Comparisons preserve JSON scalar types, including unknown
nested metadata: `true`, `1` and `1.0` are distinct changes. Identical values with
reordered object members remain no-ops without replacing the file.
Publication failure preserves the prior store. If temporary-file cleanup also
fails, the sanitized error identifies retained temporary state for inspection;
an already-removed temporary is tolerated without masking the publication error.
A busy lock fails after five seconds. The lock file remains
in place so its identity is not replaced while another process waits.

Writes publish a flushed, `fsync`-ed temporary file from the same directory via
atomic replacement. Readers see a complete old or new JSON file, not a
partially truncated store. A failed publication preserves the old file.
This is **not a transaction with Azure or the project filesystem**, and does
not promise crash-proof directory durability. Cooperating writers in this
release are serialized; older extension versions, manual editors, tools that
ignore the lock and unsupported/network filesystem semantics are outside that
guarantee. Coordinate those writers rather than deleting the lock file or
treating the snapshot check as a universal compare-and-swap.

Validation uses private, session-only stores and fake target clients. No live
Azure resource calls or user-global context edits are needed to exercise CRUD.
Independent-process regressions also use the real resolver with a shared fake
home and separate config roots, so isolation is not inferred from a mocked path.

## Local runtime lifecycle

Bare `runtime start`, `runtime show`, and `runtime stop` use the active local
context's saved port, matching runtime API consumers and doctor. Explicit
`--port` wins, including an explicit 7071; 7071 is the fallback without a saved
or explicit port. Start with an explicit port still uses the active local path.
An explicit `runtime start --path` selects an independent project and uses
7071 unless a port is supplied, as doctor does. Bare lifecycle commands refuse
an active cloud context. Explicit show/stop ports do not require a project
context. `runtime stop --all` still selects all CLI-owned runtime records,
independent of active context, and never broadens process ownership.

Stop verifies the saved PID and process-creation identity before signalling.
On Windows, an exited process can remain in the PID table while a handle is
open; a native exit timestamp distinguishes that case from a running or
unverifiable process.
Windows process-tree snapshots can also retain an old parent PID. A process
whose verified current birth predates the selected parent's birth cannot be its
child: it and that unrelated subtree are excluded, never signalled. If that
earlier identity cannot still be verified, cleanup remains conservative.

If a failed stop leaves a `cleanupPending` receipt, retry the same
`az logicapp runtime stop --port <port>` command. The retry removes that exact
unchanged receipt only after every recorded process and launch consumer is
confirmed exited/absent and the port is idle. It reports `result: already-exited`,
not a new termination. A live, recycled or unverifiable PID, occupied port,
malformed receipt, or concurrent receipt replacement retains the record and
returns an error. An ordinary stale receipt without `cleanupPending` still
refuses identity-mismatched stop. Shared Azurite is released only when no other
runtime or launch consumer needs it.
