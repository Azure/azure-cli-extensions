# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

helps['logicapp test'] = """
type: group
short-summary: Scaffold, inspect and explicitly run local native SDK test projects.
long-summary: >
  create writes source-only native MSTest scaffolding; plan remains read-only.
  run requires explicit SDK terms and project-trust acknowledgements, with
  restore separately opt-in. Native test code and build/restore targets can
  execute arbitrary code and contact services. No sandbox or network isolation
  is provided. Named/active local contexts supply project defaults, never a
  cloud runtime target or login.
"""

helps['logicapp test create'] = """
type: command
short-summary: Scaffold a native SDK test project without restoring packages or running code.
long-summary: >
  Writes a new Tests/WORKFLOW directory with a net8.0 MSTest project, exact
  SDK 1.0.3/engine 1.165.50/MSTest 4.0.2 references, .NET 8 selection,
  reviewed-source NuGet configuration and an empty trigger fixture.
  Existing directories are refused. Relative --output-path uses the selected
  local project. No SDK binaries, credentials or project settings are copied.
  The starter is ignored and guarded as inconclusive until its author reviews
  fixtures, mocks external operations and writes real business assertions.
examples:
  - name: Scaffold tests for a workflow in the active local project.
    text: az logicapp test create --workflow Orders
  - name: Scaffold in a new project-relative directory without restoring packages.
    text: az logicapp test create --path .\\App --workflow Orders --output-path .\\Tests\\Orders
"""

helps['logicapp test run'] = """
type: command
short-summary: Explicitly build and run reviewed native SDK/MSTest tests with a deadline.
long-summary: >
  Requires --accept-sdk-terms and --trust-project every time. Review
  https://www.nuget.org/packages/Microsoft.Azure.Workflows.WebJobs.Tests.Extension/1.0.3/License
  including use, redistribution, data collection and update restrictions.
  CLI telemetry opt-out does not establish that SDK telemetry is disabled.
  Uses a .NET 8 SDK, a reviewed explicit NuGet configuration and project-private
  home/cache/config directories. No global tools or dependencies are installed.
  Restore is allowed only with --restore; an existing lockfile uses locked mode.
  Both build and test otherwise use --no-restore. Imports/targets/test code can
  still perform arbitrary operations: these controls are not a security sandbox.
  Default project is Tests/WORKFLOW/Workflow.Tests.csproj under the selected
  local project. Explicit --test-project and --nuget-config inputs use shell CWD.
  Relative report destinations use the selected local project. Existing reports
  are refused. Raw native stdout/stderr is discarded, and sensitive raw TRX stays
  in the test project's .logicapp-test-state/runs/INVOCATION_ID/native.trx.
  Only bounded, consistent completed TRX counts can produce nativeTestsPassed.
  Empty/entirely skipped suites exit 7, deadline expiry 8, cleanup pending 9.
  Other exits: 1 native test failure, 2 runner/dependency error, 3 local input,
  4 missing acknowledgement, 5 observed input drift, 6 publication, 130 interruption.
  Counts do not attest that arbitrary test code called the SDK or covered the
  selected workflow. Mocking is not denied-egress execution or connector certification.
examples:
  - name: Restore and run an authored, reviewed synthetic test project after reviewing SDK terms.
    text: az logicapp test run --path .\\App --workflow Orders --accept-sdk-terms --trust-project --restore
  - name: Run a previously restored project and save a new sanitized report.
    text: az logicapp test run --workflow Orders --accept-sdk-terms --trust-project --report-path .\\Reports\\native.json
"""

helps['logicapp test plan'] = """
type: command
short-summary: Produce a bounded, versioned local preflight report; never run tests.
long-summary: >
  Inspects Standard workflow bytes, limited top-level structure and literal
  configuration declarations. Explicit test project, or the default test create
  project when present, is XML metadata only.
  Outputs notExecuted markers even for valid authoring. Exit 0 means successful
  planning, never tests passed. --strict exits 4 for blocked execution gates.
  Other exits: 1 authoring, 3 input, 5 changed inputs, 6 publication error.
  --path overrides the project path from a named or active local context;
  otherwise the current directory is used. Cloud contexts cannot supply a
  local project. An explicit --path bypasses the active context; a named cloud
  --context is refused even with --path.
  CLI argument and context resolution errors occur before a report is available.
  Default stdout only; --report-path writes a sanitized report to an existing
  directory. Relative report paths use the selected project, not the shell's
  current directory; absolute report paths are unchanged.
  Global output/query flags work before diagnostic nonzero exits.
examples:
  - name: Inspect one workflow without changing files.
    text: az logicapp test plan --path .\\App --workflow Orders --output json
  - name: Inspect one workflow in the active local context without changing files.
    text: az logicapp test plan --workflow Orders --output json
  - name: Save a report under a named local project's existing Reports directory.
    text: az logicapp test plan --context development --workflow Orders --report-path .\\Reports\\plan.json
  - name: Inspect declared test metadata and save the preflight report.
    text: az logicapp test plan --path .\\App --workflow Orders --test-project .\\Tests\\App.csproj --report-path .\\Reports\\plan.json
  - name: Generate a preflight report and fail the invocation if execution gates remain blocked.
    text: az logicapp test plan --path .\\App --workflow Orders --strict --output json
"""

helps['logicapp test results'] = """
type: group
short-summary: Inspect saved preflight or sanitized native test reports.
"""

helps['logicapp test results show'] = """
type: command
short-summary: Inspect a saved JSON test report without rerunning tests or following embedded paths.
long-summary: >
  Accepts closed version 1.0 and 2.0 foundation preflight documents with
  notExecuted markers, preserving the recorded exit policy and source result.
  Validation is not a signature or provenance
  attestation. Exit 0 means inspection succeeded, never testsPassed; the source
  outcome and exit remain in inspection. Optional --workflow-file compares
  exact bytes and exits 5 on drift. Also accepts closed original execution
  reports from test run (logicapp-sdk-test schema 1.0). Native counts/outcomes are
  historical, retained under sourceOutcome/sourceExitCode, not new execution.
  Raw SDK/TRX files, unexpected fields and unknown producers are refused.
  Accepted JSON remains unauthenticated: schema validation is not proof of authorship.
examples:
  - name: Inspect a saved preflight report (no tests executed) and check the current definition identity.
    text: az logicapp test results show --result-file .\\App\\Reports\\plan.json --workflow-file .\\App\\Orders\\workflow.json
"""

helps['logicapp context'] = """
type: group
short-summary: Manage saved Logic Apps target shortcuts.
long-summary: >
  Contexts store local path/port or deployed resource group/app names only. They
  do not store credentials or bind subscription/tenant; Azure CLI login and
  account selection, including --subscription, remain inherited.
"""

helps['logicapp project'] = """
type: group
short-summary: Manage local Logic Apps Standard projects.
"""

helps['logicapp workflow'] = """
type: group
short-summary: Manage Logic Apps Standard workflows.
"""

helps['logicapp deployment'] = """
type: group
short-summary: Manage logic app deployments.
"""

helps['logicapp dependency'] = """
type: group
short-summary: Inspect and install Logic Apps Standard local dependencies.
"""

helps['logicapp connector'] = """
type: group
short-summary: Inspect Logic Apps Standard connectors.
"""

helps['logicapp connector operation'] = """
type: group
short-summary: Inspect operations exposed by a built-in (service provider) connector.
"""

helps['logicapp connector managed'] = """
type: group
short-summary: Inspect Azure managed connectors from the ARM APIHub catalog.
"""

helps['logicapp connector managed operation'] = """
type: group
short-summary: Inspect operations exposed by an Azure managed connector.
"""

helps['logicapp runtime'] = """
type: group
short-summary: Manage local Logic Apps Standard runtimes.
"""

helps['logicapp run'] = """
type: group
short-summary: Manage Logic Apps Standard workflow runs.
"""

helps['logicapp project create'] = """
type: command
short-summary: Create or adopt a local Logic Apps Standard project.
examples:
  - name: Create a project with an initial workflow.
    text: az logicapp project create --path .\\orders --workflow process-order
"""

helps['logicapp context create'] = """
type: command
short-summary: Create a named Logic Apps CLI context.
examples:
  - name: Create and activate a local context.
    text: az logicapp context create --name orders-local --path .\\orders --use
"""

helps['logicapp context use'] = """
type: command
short-summary: Select the active Logic Apps CLI context.
examples:
  - name: Use a registered context.
    text: az logicapp context use --name orders-local
"""

helps['logicapp connection'] = """
type: group
short-summary: Author local and inspect deployed Logic Apps Standard connections.
"""

helps['logicapp connection managed'] = """
type: group
short-summary: Create Azure managed API connections for local projects or deployed Standard sites.
"""

helps['logicapp connection managed create'] = """
type: command
short-summary: Create an Azure managed API connection and wire a local project or deployed app.
long-summary: >
  --name always names the connection. Choose --path or a local --context for
  local development; --logic-app-name or a cloud --context selects a deployed app.
  With no explicit target the active context is used. Local Azure scope comes
  from local.settings.json Values.WORKFLOWS_SUBSCRIPTION_ID,
  WORKFLOWS_RESOURCE_GROUP_NAME and WORKFLOWS_LOCATION_NAME; explicit
  --subscription, --resource-group and --location override those values without
  changing settings or the default account. Azure login is still required.
  Local projects use a seven-day development connection key stored only in
  local.settings.json and referenced from connections.json. No deployed app,
  managed identity or access-policy write is needed. Local auth-mode
  managed-identity and user-assigned identities are unsupported; raw,
  service-principal and oauth configure the connector's backend authentication,
  independently of the local runtime key. Local settings must be unencrypted
  and not tracked by Git; .gitignore protection is added. Force is required for
  existing Azure resources, local wiring or the key setting. Failures may retain
  Azure resources and partially updated local files; inspect before retrying.
  Deployed targets retain the guarded managed API/OAuth/identity creation of legacy
  connection create --managed-api. That legacy mode is deprecated but retains
  its original --name meaning throughout this preview; removal requires an
  announced breaking change and it remains deployed-only.
  OAuth failures may retain connection/access-policy resources. Inspect the
  reported state before retrying; timeout does not promise resource removal.
examples:
  - name: Create an Azure Blob connection for the site's managed identity.
    text: az logicapp connection managed create -g my-rg --logic-app-name my-app -n blobProd --connector azureblob -l eastus --auth-mode managed-identity
  - name: Create an Office 365 connection with browser consent.
    text: az logicapp connection managed create -g my-rg --logic-app-name my-app -n outlook --connector office365 -l eastus --auth-mode oauth
  - name: Create a connection for a local project using its Azure settings.
    text: az logicapp connection managed create --path .\\orders -n outlook --connector office365 --auth-mode oauth
  - name: Override Azure scope for a saved local project without changing its settings.
    text: az logicapp connection managed create --context orders-local -n outlook --connector office365 --auth-mode oauth --subscription 11111111-1111-1111-1111-111111111111 -g dev-rg -l eastus
"""

helps['logicapp context list'] = """
type: command
short-summary: List saved targets with their active selection.
long-summary: Read-only, name-sorted inventory. Does not create a missing context store.
examples:
  - name: Inspect saved targets in a table.
    text: az logicapp context list --output table
"""

helps['logicapp context show'] = """
type: command
short-summary: Show a named saved target, or the active target.
examples:
  - name: Inspect the active target.
    text: az logicapp context show
  - name: Inspect a saved target without activating it.
    text: az logicapp context show --name orders-local
"""

helps['logicapp context update'] = """
type: command
short-summary: Edit an existing saved target without changing its selection.
long-summary: >
  Omitted fields are retained. Editing an active target prompts unless --yes is
  supplied. Switching kind requires --kind and complete new coordinates: path
  and port for local, resource group and logic-app-name for cloud. Old known
  coordinates are cleared. Does not create a missing context or contact Azure.
examples:
  - name: Edit the port of an existing local shortcut.
    text: az logicapp context update --name orders-local --port 7079
  - name: Deliberately switch an existing shortcut to a deployed target.
    text: az logicapp context update --name dev --kind cloud -g my-rg --logic-app-name my-app --yes
"""

helps['logicapp context delete'] = """
type: command
short-summary: Delete one saved shortcut, never a project or Azure resource.
long-summary: >
  Prompts unless --yes is supplied. Deleting the active shortcut clears the
  active selection without choosing a replacement; runtime commands then require
  an explicit target or a deliberate context use. Other shortcuts are preserved.
examples:
  - name: Remove a saved shortcut only.
    text: az logicapp context delete --name orders-local
"""

helps['logicapp workflow create'] = """
type: command
short-summary: Add a workflow to an existing local Logic Apps Standard project.
long-summary: >
  Authors locally only and makes no network call. Writes just the workflow's
  workflow.json, leaving host.json and local.settings.json untouched, so adding a
  second workflow is non-destructive. Not idempotent: it fails if the workflow
  already exists, so it is safe to retry only with --force.
examples:
  - name: Add a workflow using the starter template.
    text: az logicapp workflow create --path .\\orders --workflow process-order
  - name: Add a workflow from an authored definition.
    text: az logicapp workflow create --path .\\orders --workflow send-message --file .\\send.json
"""

helps['logicapp workflow list'] = """
type: command
short-summary: List workflows in a running local or deployed Logic Apps Standard app.
long-summary: >
  Returns value and nextContinuationToken. Each item has name, kind, state and
  health. Fetches the entire service inventory before client-side paging, sorted
  by name. Tokens are offsets, not snapshots; inventory changes between calls
  can shift page boundaries. Unknown state or health is reported as null.
  Inventory traversal allows at most 100 service pages and 10000 accumulated
  entries, failing explicitly without partial results when either limit is exceeded.
examples:
  - name: Discover workflows in a local runtime.
    text: az logicapp workflow list --local --port 7071 --output table
  - name: Discover workflows in a deployed app.
    text: az logicapp workflow list --resource-group my-rg --name my-app
"""

helps['logicapp workflow show'] = """
type: command
short-summary: Read a workflow's metadata and authored workflow.json.
long-summary: >
  Returns name, kind, state, health, etag, and workflow (the complete workflow.json
  object). Reads the runtime metadata and file plane with the same target and
  authentication. Does not resolve app settings or download connections,
  credentials, or other app files. Authored definitions can themselves contain
  sensitive literals. JSON output contains the definition; table output shows
  only name, kind, state and health.
  The etag can be passed to set/delete --if-match to guard an editing session.
examples:
  - name: Read one local workflow.
    text: az logicapp workflow show --local --workflow hello
  - name: Read a workflow using a saved context.
    text: az logicapp workflow show --context dev --workflow hello
"""

helps['logicapp workflow export'] = """
type: command
short-summary: Export one authored workflow.json without changing the app.
long-summary: >
  Preserves the actual Stateful or Stateless kind and the complete authored
  workflow file, including expressions and runtime configuration. Requires a
  .json destination outside the filesystem root and --force to replace a file.
  Publishes the complete file atomically; directories and symbolic links are
  rejected. No full app download, connections or app credentials are included.
  Definitions can contain authored sensitive literals: protect the output file.
  The result includes the source file etag for a later --if-match guard.
examples:
  - name: Export one local workflow.
    text: az logicapp workflow export --local --workflow hello --output-path .\\download\\hello\\workflow.json
  - name: Export one deployed workflow.
    text: az logicapp workflow export -g my-rg -n my-app --workflow hello --output-path .\\hello.json
"""

helps['logicapp workflow set'] = """
type: command
short-summary: Replace one existing workflow.json with revision checks and runtime preflight.
long-summary: >
  Requires a complete --file with the same Stateful/Stateless kind. Performs
  static checks and target-runtime definition validation before writing. Reads
  the current file revision, confirms the target, rechecks after confirmation,
  writes with an exact If-Match, and verifies the write receipt and file bytes.
  --if-match can also bind the update to the revision from a previous show/export.
  No --force bypass is available. Identical input is validated but not written.


  Requires --allow-non-atomic: VFS is not transactional. ETag checks cannot prevent
  every race or partial upload, and a concurrently deleted file can be recreated.
  Export first and coordinate with other writers. Unexpected creation, ambiguous
  failures and unverified results fail explicitly. A mismatched owned revision
  is conditionally restored only when ownership can be verified; newer or missing
  files are not blindly overwritten. Guaranteed rollback is not available.


  Verification covers the authored file, not execution or completed runtime
  reload. This does not create a new workflow intentionally, convert its kind,
  change shared settings/connections, or cancel runs. Read-only/run-from-package
  targets may reject writes; use documented deployment commands instead.
examples:
  - name: Update a workflow on a running local host after retaining an export.
    text: az logicapp workflow set --local --workflow hello --file .\\edited\\workflow.json --allow-non-atomic --yes
  - name: Guard a deployed update using the ETag obtained during export.
    text: az logicapp workflow set -g my-rg -n my-app --workflow hello --file .\\edited\\workflow.json --if-match saved-etag --allow-non-atomic
"""

helps['logicapp workflow delete'] = """
type: command
short-summary: Remove one workflow.json while retaining shared and sibling files.
long-summary: >
  Requires --allow-non-atomic to acknowledge the runtime's non-transactional VFS
  behavior. Reads and checks the existing supported workflow and exact revision,
  prompts unless --yes is supplied, rechecks after confirmation, and conditionally
  deletes only workflow.json. Verifies absence with a file-plane 404; unknown
  outcomes or a recreated file are errors, never silently retried. --if-match
  optionally binds deletion to an earlier show/export revision.


  Other workflow files and the workflow directory are retained, as are shared app
  settings, connections, artifacts and identities. Runtime removal is asynchronous;
  this does not cancel active runs, purge run history or delete the app resource.
  Export first for recovery. No wildcard/force revision bypass is supported.
examples:
  - name: Delete a workflow on a running local host.
    text: az logicapp workflow delete --local --workflow hello --allow-non-atomic --yes
  - name: Delete one workflow using a saved target and confirmation.
    text: az logicapp workflow delete --context dev --workflow hello --allow-non-atomic
"""

helps['logicapp workflow enable'] = """
type: command
short-summary: Configure one deployed Standard workflow as Enabled and observe runtime state.
long-summary: >
  Supports deployed Stateful/Stateless workflows using -g/-n or a cloud context.
  Local runtime targets are rejected without editing files or restarting hosts.
  Requires --allow-non-atomic because App Service replaces the entire app settings
  map when setting `Workflows.<name>.FlowState`. Other settings are preserved from
  the snapshot, but concurrent unrelated updates can be lost despite preflight
  and readback. Coordinate all settings writers. Requires confirmation unless
  --yes is supplied; enabling may process accumulated trigger backlog.
  Reports verified configuredState separately from runtimeState after one runtime
  observation. Converged means matching metadata, not drained runs or proof that
  all dispatchers are quiescent. Pending/unknown states produce warnings without
  automatic retries or rollback. This does not start/stop the app, edit definitions,
  cancel runs or purge history. App settings and provider error bodies are not
  exposed, including by this operation's REST debug logs.
examples:
  - name: Enable one deployed workflow after coordinating settings writers.
    text: az logicapp workflow enable -g my-rg -n my-app --workflow hello --allow-non-atomic
  - name: Use a saved deployed target without prompting.
    text: az logicapp workflow enable --context production --workflow hello --allow-non-atomic --yes
"""

helps['logicapp workflow disable'] = """
type: command
short-summary: Configure one deployed Standard workflow as Disabled and observe runtime state.
long-summary: >
  Supports deployed Stateful/Stateless workflows using -g/-n or a cloud context.
  Local runtime targets are rejected without requests, file edits or host restarts.
  Disabling stops new ordinary workflow instances/triggers after propagation;
  existing in-progress/pending runs continue. This does not cancel runs, purge
  history, reset triggers or stop the app resource.
  Requires --allow-non-atomic and confirmation unless --yes is supplied.
  App Service replaces the entire settings map; values are retained from a
  snapshot, but unrelated concurrent changes can be lost. There is no settings
  ETag/transaction guarantee. Settings updates can have hosting/reload effects.
  configuredState is verified by settings readback; runtimeState is a separate
  single observation. Pending/unknown results warn instead of claiming trigger
  quiescence. Already configured requests do not write or prompt. No automatic
  retry/rollback is attempted, and uncertain writes/readbacks return errors.
  Neither settings values nor raw provider errors appear in command results or
  this operation's REST debug logs.
examples:
  - name: Disable only hello, without stopping its app or cancelling runs.
    text: az logicapp workflow disable -g my-rg -n my-app --workflow hello --allow-non-atomic
  - name: Disable a workflow through a saved deployed target.
    text: az logicapp workflow disable --context production --workflow hello --allow-non-atomic --yes
"""

helps['logicapp connection create'] = """
type: command
short-summary: Add a service provider connection to a local project, or a managed API connection to a deployed app.
long-summary: >
  Two modes. By default this writes a service provider connection into a local
  project. With --managed-api it instead creates an Azure managed API connection
  for a deployed Logic App, and --name means the Logic App rather than the
  connection; name the connection with --connection-name.


  Local mode:
  Writes the connection into connections.json and any secret value into
  local.settings.json, which deployment package excludes. A secret is never accepted
  on the command line: --secret names the app setting and the value is read from
  standard input. For identity-based connections omit --secret entirely and supply
  --parameter NAME=VALUE instead; dots nest values, so authProvider.Type becomes a
  nested object, which is what the runtime requires. Parameters sourced from app
  configuration need a matching --app-setting. local.settings.json is added to
  .gitignore unless --no-gitignore is given. Not idempotent: it fails if the
  connection or app setting already exists, so it is safe to retry only with --force.


  Managed API mode (--managed-api):
  Creates three coupled things, because the first alone is unusable: the ARM
  Microsoft.Web/connections resource, an access policy naming the app's managed
  identity, and a managedApiConnections entry in the app's connections.json. The
  connection is always created with kind V2, since V1 connections reject access
  policies and the kind cannot be changed afterwards. The app must already have a
  managed identity; without one the command stops before creating anything.
  An existing valid connections.json with a strong VFS ETag is also required
  before ARM mutations. Missing files or unversioned/weak revisions fail closed;
  the CLI does not attempt unqualified create-only file writes. Publication and
  file-entry restoration use the exact fresh reread ETag, never a wildcard.
  Revision conflicts are not retried; file guards are not an ARM transaction.
  --auth-mode oauth opens a browser so you can approve the connection. The CLI
  listens on a loopback port for the redirect, which is how it learns consent
  finished; the consent service redeems the authorization code itself, so the
  callback usually carries no code and nothing further is confirmed. Use
  --no-browser on a headless machine to print the URL instead of launching one.
  If consent, access-policy creation, or connections.json wiring fails, ARM
  resources and access policies are retained for manual inspection. An
  unconditional PUT can update another writer's resource even after preflight
  absence; it does not authorize automatic deletion or policy restoration.
  Properties, credentials or granted access may have changed. Inspect and
  deliberately recover retained state before retrying; --force is not a
  concurrency guarantee. Only guarded file-entry restoration is attempted.
  Existing credentials cannot always be recovered from ARM readback. An unreadable
  or malformed existing connections.json is not replaced with an empty file.


  On Windows PowerShell, an @appsetting('NAME') value has to reach az intact.
  PowerShell forwards the parentheses unquoted to cmd.exe, which ends the
  IF EXIST block inside az.cmd and fails with "--parameter was unexpected at this
  time". Insert the PowerShell stop-parsing token immediately before the first
  --parameter to pass the rest of the line through unparsed.
examples:
  - name: Add a Service Bus connection, value piped in (PowerShell).
    text: $env:SB_CONNECTION | az logicapp connection create --path .\\orders --name serviceBus --connector serviceBus --secret serviceBus_connectionString
  - name: Add a Service Bus connection, value piped in (bash).
    text: printf '%s' "$SB_CONNECTION" | az logicapp connection create --path ./orders --name serviceBus --connector serviceBus --secret serviceBus_connectionString
  - name: Add a Service Bus connection that uses managed identity, with no secret anywhere.
    text: az logicapp connection create --path ./orders --name serviceBus --connector serviceBus --parameter-set ManagedServiceIdentity --parameter "fullyQualifiedNamespace=@appsetting('serviceBus_fullyQualifiedNamespace')" authProvider.Type=ManagedServiceIdentity --app-setting serviceBus_fullyQualifiedNamespace=contoso.servicebus.windows.net
  - name: Create an Azure Blob managed API connection that authenticates as the app's identity.
    text: az logicapp connection create --managed-api -g rg-lacli-ri2bg8 -n la-cli-pilot-ri2bg8 --connection-name blobProd --connector azureblob -l eastus --auth-mode managed-identity
  - name: Create an Office 365 connection and approve it in a browser.
    text: az logicapp connection create --managed-api -g rg-lacli-ri2bg8 -n la-cli-pilot-ri2bg8 --connection-name outlook --connector office365 -l eastus --auth-mode oauth
  - name: Same, on a headless machine - print the consent URL instead of opening a browser.
    text: az logicapp connection create --managed-api -g rg-lacli-ri2bg8 -n la-cli-pilot-ri2bg8 --connection-name outlook --connector office365 -l eastus --auth-mode oauth --no-browser
"""

helps['logicapp connection acl'] = """
type: group
short-summary: Manage access policies on a managed API connection.
long-summary: >
  An access policy names the Entra identity allowed to use a managed API
  connection. A Logic App reaches a managed API connection through its own
  managed identity, so without a matching policy the connection exists but the
  app cannot call it. Only V2 connections accept access policies.
"""

helps['logicapp connection acl list'] = """
type: command
short-summary: List access policies on a managed API connection.
examples:
  - name: List the identities allowed to use a connection.
    text: az logicapp connection acl list -g rg-lacli-ri2bg8 --connection blobProd
"""

helps['logicapp connection acl show'] = """
type: command
short-summary: Show one access policy on a managed API connection.
examples:
  - name: Show a single access policy.
    text: az logicapp connection acl show -g rg-lacli-ri2bg8 --connection blobProd --policy la-cli-pilot-ri2bg8-00000000-0000-0000-0000-000000000000
"""

helps['logicapp connection acl add'] = """
type: command
short-summary: Grant an Entra identity access to a managed API connection.
long-summary: >
  Takes the object id of the principal, normally the principalId reported by
  az logicapp identity show. Refuses on V1 connections, which cannot hold access
  policies and cannot be converted.
examples:
  - name: Grant a Logic App's system-assigned identity access to a connection.
    text: az logicapp connection acl add -g rg-lacli-ri2bg8 --connection blobProd --object-id 00000000-0000-0000-0000-000000000000
"""

helps['logicapp connection acl remove'] = """
type: command
short-summary: Remove an access policy from a managed API connection.
long-summary: >
  The principal named by the policy immediately loses access to the connection,
  so workflows relying on it begin to fail. Prompts unless --yes is given.
examples:
  - name: Remove an access policy without prompting.
    text: az logicapp connection acl remove -g rg-lacli-ri2bg8 --connection blobProd --policy la-cli-pilot-ri2bg8-00000000-0000-0000-0000-000000000000 --yes
"""

helps['logicapp connection list'] = """
type: command
short-summary: List connections wired into a deployed Logic App Standard app.
long-summary: >
  Reads only the app's connections.json file through the ARM VFS proxy. This is
  the file-plane wiring that workflows can use; it does not reconcile against
  ARM Microsoft.Web/connections resources, so ARM-created-but-unwired connections
  and dangling file references are not surfaced. parameterValues and runtime URLs
  are redacted by default.
examples:
  - name: List app-wired connections.
    text: az logicapp connection list --resource-group rg-lacli-ri2bg8 --name la-cli-pilot-ri2bg8
  - name: List app-wired connections including runtime URLs.
    text: az logicapp connection list -g rg-lacli-ri2bg8 -n la-cli-pilot-ri2bg8 --show-runtime-urls
"""

helps['logicapp connection show'] = """
type: command
short-summary: Show one connection wired into a deployed Logic App Standard app.
long-summary: >
  Reads only connections.json through the ARM VFS proxy. This file-plane view can
  differ from ARM Microsoft.Web/connections inventory. parameterValues and runtime
  URLs are redacted by default; use --show-runtime-urls only when you need the
  runtime URL in your current shell.
examples:
  - name: Show one app-wired connection.
    text: az logicapp connection show --resource-group rg-lacli-ri2bg8 --name la-cli-pilot-ri2bg8 --connection cliPilotBlob
  - name: Show one managed API connection from the managed class.
    text: az logicapp connection show -g rg-lacli-ri2bg8 -n la-cli-pilot-ri2bg8 --connection office365-prod --class managedApiConnections
"""

helps['logicapp connection test'] = """
type: command
short-summary: Test a configured Logic Apps Standard connection.
long-summary: >
  Tests an app-wired service-provider connection, an app-wired managed API
  connection, or an ARM Microsoft.Web/connections resource id. A connector with
  no advertised test endpoint is not treated as healthy: the command reports
  outcome noTestAvailable, says the connection was not verified, and exits 3.
  Returned 5xx responses are failures, and 429 responses are couldNotReach with
  retryAfter preserved when supplied.
examples:
  - name: Test an app-wired connection by name.
    text: az logicapp connection test --resource-group rg-lacli-ri2bg8 --name la-cli-pilot-ri2bg8 --connection cliPilotBlob
  - name: Test a managed ARM connection resource by id.
    text: az logicapp connection test -g rg-lacli-ri2bg8 -n la-cli-pilot-ri2bg8 --connection /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-lacli-ri2bg8/providers/Microsoft.Web/connections/office365-prod
"""

helps['logicapp connection delete'] = """
type: command
short-summary: Remove a connection from a deployed Logic App.
long-summary: >
  Removes the connections.json entry. For a managed API connection, only access
  policies matching the entry's exclusively owned system-assigned identity can
  be removed, and the resource is deleted only when exclusive ownership is
  established. User-assigned identities can be shared by multiple apps, so their
  policies and connection resource are retained, with a reason reported.
  Identities merely assigned to this app are not evidence of connection ownership.
  Pass --keep-resource to keep the resource even for an exclusively owned policy;
  this flag does not revoke shared user-assigned identity access.
  App settings referenced by a service provider connection are never deleted,
  only reported, since other connections may still read them.
  Removal requires a strong ETag from the current connections.json reread and
  sends that exact revision. Missing/weak ETags or a revision conflict stop the
  command without ARM cleanup or an unconditional retry. VFS receipt/readback
  checks remain required; these are not a cross-resource transaction.
  The authored managed connection ID must be a canonical relative resource ID
  in the selected subscription and resource group. Absolute, malformed or
  cross-scope IDs refuse before connection-resource ARM access or unlink,
  including with --keep-resource. Manage cross-scope resources explicitly.
examples:
  - name: Remove a connection from an app, without prompting.
    text: az logicapp connection delete -g rg-lacli-ri2bg8 -n la-cli-pilot-ri2bg8 --connection cliPilotBlob --yes
  - name: Remove this app's entry and exclusively owned policies, keeping the resource.
    text: az logicapp connection delete -g rg-lacli-ri2bg8 -n la-cli-pilot-ri2bg8 --connection sharedBlob --keep-resource --yes
  - name: Disambiguate a name that exists in both connection classes.
    text: az logicapp connection delete -g rg-lacli-ri2bg8 -n la-cli-pilot-ri2bg8 --connection blob --class managedApiConnections --yes
"""

helps['logicapp workflow validate'] = """
type: command
short-summary: Validate workflow definitions offline by default.
long-summary: >
  Invalid workflow shapes, including non-object triggers, are returned as
  structured validation findings rather than unexpected exceptions. Static
  validation continues checking actions and references when triggers are invalid.
examples:
  - name: Validate one workflow in a local project.
    text: az logicapp workflow validate --path .\\orders --workflow process-order
"""

helps['logicapp deployment package'] = """
type: command
short-summary: Create a deterministic deployment package for a Logic Apps Standard project.
long-summary: >
  Excludes directories containing the native scaffold Workflow.Tests.csproj or
  .logicapp-test-state, including custom in-project test locations, and raw TRX
  files. Test sources, fixtures, private caches and build outputs under those
  directories are not deployed. A test project/state sharing the deployment
  root or a workflow definition directory is refused, not silently omitted.
  Keep tests in dedicated directories. Ordinary runtime binaries remain eligible.
  Root .funcignore controls additional authored exclusions; .gitignore is not
  deployment policy. Arbitrary test code can write elsewhere, so inspect the
  manifest and exclude other private fixtures/artifacts explicitly.
examples:
  - name: Package a project.
    text: az logicapp deployment package --path .\\orders --output-path .\\orders.zip
"""

helps['logicapp dependency check'] = """
type: command
short-summary: Check local dependencies required by Logic Apps Standard tooling.
examples:
  - name: Check selected dependencies.
    text: az logicapp dependency check --kind core-tools --kind azurite
"""

helps['logicapp dependency install'] = """
type: command
short-summary: Download and install local dependencies required by Logic Apps Standard tooling.
long-summary: >
  Installs Azure Functions Core Tools, Node.js, Azurite, and the Logic Apps extension bundle from
  their publishers into a folder shared with Visual Studio Code's Azure Logic Apps extension
  (~/.azurelogicapps/dependencies by default, or LA_DEPENDENCIES_PATH), so a machine already set
  up for VS Code is not made to download them twice.


  Archives are verified against the publisher's published SHA256 where one exists -- Node.js
  through SHASUMS256.txt and Core Tools through their .sha2 sidecar -- and every install records
  a .logicapps-integrity.json manifest, which is what lets 'az logicapp dependency uninstall'
  remove only what this CLI put there.


  Azurite is published only through npm and needs its dependency tree resolved, so it is installed
  with the npm that ships alongside Node.js, confined to the managed folder. It is fetched from
  the public npm registry rather than whatever registry your npm is configured for; pass
  --source-url to use another. Install Node.js first if you do not already have it.


  Managed tool folders are added only to child-process environments for npm,
  Azurite, and local runtimes. Your global PATH is not modified.


  The .NET SDK is deliberately not installed. Its only vendor-supported route is a remote install
  script, and this command will not run one on your machine. 'az logicapp dependency check' still
  reports it.
examples:
  - name: Install everything this CLI can install.
    text: az logicapp dependency install --yes
  - name: Install just Functions Core Tools.
    text: az logicapp dependency install --kind core-tools --yes
  - name: Install the Azurite storage emulator for local runs.
    text: az logicapp dependency install --kind azurite --yes
  - name: Pin a specific Core Tools version.
    text: az logicapp dependency install --kind core-tools --version 4.0.7030 --yes
  - name: Install into a different directory.
    text: az logicapp dependency install --kind node --target-dir /opt/logicapps-deps --yes
"""

helps['logicapp dependency uninstall'] = """
type: command
short-summary: Remove local dependencies that this CLI installed.
long-summary: >
  Removes only material recorded in a .logicapps-integrity.json manifest written by
  'az logicapp dependency install'. A dependency folder without that manifest is left untouched,
  because the dependency root is shared with Visual Studio Code and may hold tools this CLI
  never installed.
examples:
  - name: Remove everything this CLI installed.
    text: az logicapp dependency uninstall --yes
  - name: Remove only Node.js.
    text: az logicapp dependency uninstall --kind node --yes
"""

helps['logicapp connector list'] = """
type: command
short-summary: List connectors visible to a Logic Apps Standard runtime.
long-summary: >
  The runtime route returns the whole catalog in one response and does not page,
  so --max-items and --next-token are applied by the CLI after the full
  response is received, not by the service.
examples:
  - name: List connectors from a local runtime.
    text: az logicapp connector list --local --port 7071
"""

helps['logicapp connector show'] = """
type: command
short-summary: Show one connector from a Logic Apps Standard runtime.
examples:
  - name: Show a connector from a local runtime.
    text: az logicapp connector show --local --port 7071 --connector /serviceProviders/acasession
"""

helps['logicapp connector operation list'] = """
type: command
short-summary: List operations exposed by a built-in (service provider) connector.
long-summary: >
  Reads the site runtime operationGroups catalog, which is the built-in connector
  catalog, not the ARM managed connector catalog returned by
  az logicapp connector managed operation list. The runtime returns the whole
  operation list in one response and emits no continuation token, so --kind,
  --search, --max-items and --next-token are all applied by the CLI after
  the full response is received. Operations are classified as triggers using the
  runtime's own trigger field rather than inferred.
examples:
  - name: List every operation on a built-in connector.
    text: az logicapp connector operation list --local --port 7071 --connector /serviceProviders/serviceBus
  - name: List only the triggers, accepting the id reported by connector list.
    text: az logicapp connector operation list --local --port 7071 --connector /serviceProviders/serviceBus --kind trigger
  - name: Search operations on a deployed app.
    text: az logicapp connector operation list -g my-rg -n my-app --connector serviceBus --search "send message"
"""

helps['logicapp connector operation show'] = """
type: command
short-summary: Show one operation exposed by a built-in (service provider) connector.
long-summary: >
  --operation accepts either the bare operation name or the full operation id
  reported by az logicapp connector operation list.
examples:
  - name: Show one operation on a local runtime.
    text: az logicapp connector operation show --local --port 7071 --connector /serviceProviders/serviceBus --operation sendMessage
"""

helps['logicapp connector managed list'] = """
type: command
short-summary: List Azure managed connectors from the ARM APIHub catalog.
long-summary: >
  Queries ARM managedApis for one Azure location at api-version 2018-07-01-preview.
  This is the managed connector catalog, not the Logic Apps Standard site-runtime
  operationGroups catalog returned by az logicapp connector list.
examples:
  - name: List managed connectors in East US.
    text: az logicapp connector managed list --location eastus
  - name: Search managed connectors client-side.
    text: az logicapp connector managed list --location eastus --search office
"""

helps['logicapp connector managed show'] = """
type: command
short-summary: Show one Azure managed connector from ARM APIHub.
examples:
  - name: Show the Office 365 managed connector.
    text: az logicapp connector managed show --location eastus --connector office365
"""

helps['logicapp connector managed operation list'] = """
type: command
short-summary: List operations for one Azure managed connector.
long-summary: >
  Queries the ARM managedApis apiOperations route. --search filters operations;
  it does not search for connector names.
examples:
  - name: List Office 365 actions.
    text: az logicapp connector managed operation list --location eastus --connector office365 --kind action
  - name: Search Office 365 operations.
    text: az logicapp connector managed operation list --location eastus --connector office365 --search "send mail"
"""

helps['logicapp connector managed operation show'] = """
type: command
short-summary: Show one operation for an Azure managed connector.
examples:
  - name: Show the Office 365 SendEmailV2 operation.
    text: az logicapp connector managed operation show --location eastus --connector office365 --operation SendEmailV2
"""

helps['logicapp runtime start'] = """
type: command
short-summary: Start a local Logic Apps Standard runtime.
long-summary: >
  When the project's local.settings.json sets AzureWebJobsStorage to
  UseDevelopmentStorage=true, the Azurite storage emulator is started automatically on
  ports 10000-10002 unless one is already serving there, in which case it is reused.
  Only an emulator this CLI started is ever stopped, and only once no CLI-started
  foreground or background runtime is still using it. Process ownership is
  checked using both PID and creation time on Windows, Linux, and macOS; an
  unverified or recycled PID is never stopped. Pass --no-azurite to manage the
  emulator yourself.
examples:
  - name: Start a project runtime in the background.
    text: az logicapp runtime start --path .\\orders --port 7071 --background
  - name: Start a runtime without touching the storage emulator.
    text: az logicapp runtime start --path .\\orders --port 7071 --background --no-azurite
"""

helps['logicapp runtime doctor'] = """
type: command
short-summary: Diagnose a local project's runtime prerequisites without changing them.
long-summary: >
  Reads project files, selected child-environment tool versions, cached bundle
  evidence and literal loopback ports. Never installs, downloads, starts, stops,
  repairs, decrypts settings, changes context, or contacts cloud storage.
  Configuration and upstream values are not printed. A stopped host is an
  optional skipped live probe, not an offline preflight failure. Unknown tool
  and bundle compatibility is not healthy. This is not a workflow business test.
  Exit 0 means no required blockers or unknown checks, 1 means a required failure,
  and 2 means a required unknown (or optional failed/warning/unknown with --strict).
  JSON and table findings are printed before a diagnostic nonzero exit.
  Exact tool/bundle compatibility remains required unknown, so an otherwise
  responsive project normally exits 2; unknown is not failure or healthy certification.
examples:
  - name: Diagnose a local project and preserve JSON findings for CI.
    text: az logicapp runtime doctor --path .\\orders --output json
  - name: Inspect a saved local context in a human-readable table.
    text: az logicapp runtime doctor --context orders-local --output table
"""

helps['logicapp runtime show'] = """
type: command
short-summary: Show local Logic Apps Standard runtime status.
examples:
  - name: Show runtime status.
    text: az logicapp runtime show --port 7071
"""

helps['logicapp runtime stop'] = """
type: command
short-summary: Stop a local runtime started by this CLI.
long-summary: |
  A retry can remove a cleanup-pending receipt once every recorded process and
  launch consumer has exited and the port is idle. It never signals a recycled or
  unverifiable PID. Confirmed exited Windows processes may still have open handles.
  Recovered receipts report result already-exited rather than terminated.
examples:
  - name: Stop one CLI-started runtime.
    text: az logicapp runtime stop --port 7071
"""

helps['logicapp run start'] = """
type: command
short-summary: Start a workflow run by firing a trigger.
examples:
  - name: Start a run against a local runtime.
    text: az logicapp run start --local --port 7071 --workflow process-order --trigger manual --payload-file .\\payload.json
"""

helps['logicapp run show'] = """
type: command
short-summary: Show one workflow run.
examples:
  - name: Show a run from a local runtime.
    text: az logicapp run show --local --port 7071 --workflow process-order --run-id 08584129676611502966413873720CU00
"""

helps['logicapp run wait'] = """
type: command
short-summary: Wait for a Stateful run to reach a terminal status within a deadline.
long-summary: |
  Supports running local and deployed Standard apps and saved targets. Exit 0
  means observed Succeeded; 4 means a different terminal status; 2 means the CLI
  wait deadline expired (not workflow TimedOut); 1 means an observation error.
  Missing runs, authorization failures, malformed responses and unknown statuses
  fail promptly. No missing-run grace period, implicit cancellation or retry.
  JSON/table/query output is preserved before nonzero result exits. Responses
  omit inputs, outputs, provider errors and signed URLs. Each network request is
  bounded; an in-flight read may exceed the polling deadline by its 5-second
  read timeout. OS DNS resolution and CLI token acquisition are not forcibly
  interrupted by that network timeout.
examples:
  - name: Wait up to a minute for a local Stateful run.
    text: az logicapp run wait --local --workflow hello --run-id RUN_ID --timeout 60 --interval 2
"""

helps['logicapp run cancel'] = """
type: command
short-summary: Request cancellation of one Stateful workflow run.
long-summary: |
  Requires confirmation or --yes. A POST acknowledgement is not cancellation:
  without --wait a bounded readback reports cancelled, pending or an observation
  failure. --wait requires observed Cancelled for exit 0; another terminal state
  exits 4 and a wait deadline exits 2. Already-terminal runs are unchanged (exit
  0) without POST. Cancellation does not roll back effects or guarantee in-flight
  actions stop. No uncertain request is retried, and timeout never sends another
  cancellation. Stateless workflows are rejected before mutation.
examples:
  - name: Request cancellation and wait for an observed Cancelled status.
    text: az logicapp run cancel --local --workflow hello --run-id RUN_ID --yes --wait --timeout 60 --interval 2
"""

helps['logicapp run resubmit'] = """
type: command
short-summary: Request a new Stateful execution starting from one eligible action of a completed run.
long-summary: |
  Requires --workflow, --run-id and one --action, plus confirmation or --yes.
  This is the run-resubmit API with actionsToResubmit, not trigger-history replay.
  The runtime must advertise canResubmit=true for that executed action; missing,
  false or malformed eligibility, skipped actions and active source runs refuse
  before POST. The CLI never enables the feature or emulates graph eligibility.
  Run/action identity and stable metadata are rechecked after confirmation.
  The runtime uses the source workflow version and retained prior results.
  Selected/dependent actions can repeat external effects with current connections
  and settings. This is a new execution, not in-place resume or exactly-once recovery.
  HTTP 202 reports accepted, not completed. newRunId comes only from the service;
  a missing identity reports acceptedNewRunIdUnknown. No Location/latest-run fallback,
  trigger-history substitution, configuration restore or automatic POST retry.
  Use run wait separately when a new identity is returned. Preflight/submission
  each use a 60-second deadline excluding interactive confirmation time.
examples:
  - name: Resubmit one eligible action from a retained completed Stateful run.
    text: az logicapp run resubmit --local --workflow hello --run-id RUN_ID --action Send_HTTP --yes
"""

helps['logicapp trigger'] = """
type: group
short-summary: Manage Logic Apps Standard workflow triggers.
"""

helps['logicapp trigger history'] = """
type: group
short-summary: Replay explicitly selected retained trigger histories.
"""

helps['logicapp trigger history resubmit'] = """
type: command
short-summary: Request a new Stateful execution from an explicit retained fired trigger history.
long-summary: |
  Requires confirmation or --yes and may duplicate external side effects. This
  is not resume or exactly-once recovery; no source run is selected or changed.
  Requires --workflow, --trigger and --history-name. Reads the selected trigger
  and fired history directly, rechecking after confirmation. It does not search
  histories or require a readable associated source run.
  Never substitutes a run id for a history id. Missing history, Stateless and
  invalid metadata fail before POST. A 202 reports accepted, not completed, with
  newRunId only if the response identifies it. Otherwise it reports
  acceptedNewRunIdUnknown. No Location/nextLink URL is followed or printed and
  no resubmit request is retried. Preflight and submission each use a 60-second
  deadline; interactive confirmation time is excluded.
examples:
  - name: Replay an explicitly selected retained fired trigger history.
    text: az logicapp trigger history resubmit -g my-rg -n my-app --workflow hello --trigger manual --history-name HISTORY_ID --yes
"""

helps['logicapp run action'] = """
type: group
short-summary: Inspect the individual actions inside a workflow run.
"""

helps['logicapp identity'] = """
type: group
short-summary: Manage the managed identity of a deployed Logic App Standard site.
"""

helps['logicapp run list'] = """
type: command
short-summary: List workflow runs.
long-summary: >
  Pages server-side. Each response carries nextContinuationToken; pass it back as
  --next-token to fetch the next page. Do not derive the token yourself:
  the platform's token is what keeps runs created between pages from being skipped.
examples:
  - name: List the most recent runs from a local runtime.
    text: az logicapp run list --local --port 7071 --workflow process-order --max-items 20
  - name: List only failed runs of a deployed app.
    text: az logicapp run list --resource-group orders-rg --name orders-app --workflow process-order --status Failed
"""

helps['logicapp run action list'] = """
type: command
short-summary: List the actions of a workflow run and their individual status.
long-summary: >
  This is the first step in answering why a run failed. run show reports only that
  an action failed; this names which one. Content links are redacted by default
  because they carry a SAS token.
examples:
  - name: Find the failed action in a run.
    text: az logicapp run action list --local --port 7071 --workflow process-order --run-id 08584129676611502966413873720CU00 --query "value[?status=='Failed']"
"""

helps['logicapp run action show'] = """
type: command
short-summary: Show one action from a workflow run.
examples:
  - name: Show a single action.
    text: az logicapp run action show --local --port 7071 --workflow process-order --run-id 08584129676611502966413873720CU00 --action Send_message
"""

helps['logicapp run action show-content'] = """
type: command
short-summary: Download the recorded inputs or outputs of a run action.
long-summary: >
  The platform stores action payloads out of band and returns only a link. This
  downloads the payload and prints it, so a connector's underlying error detail is
  visible without handling a SAS URI by hand. Defaults to outputs. Not every action
  records both payloads: an action that failed before it produced a response has no
  outputs at all, and its error text is on run action show instead.
examples:
  - name: Read why an action failed.
    text: az logicapp run action show-content --local --port 7071 --workflow process-order --run-id 08584129676611502966413873720CU00 --action Send_message
  - name: Read the inputs an action was given, capped in size.
    text: az logicapp run action show-content --resource-group orders-rg --name orders-app --workflow process-order --run-id 08584129676611502966413873720CU00 --action Send_message --content inputs --max-bytes 4096
"""

helps['logicapp identity assign'] = """
type: command
short-summary: Assign a managed identity to a deployed Logic App.
long-summary: >
  Additive: assigning a user-assigned identity leaves an existing system-assigned
  identity in place. Assigning an identity is only half of enabling an
  identity-based connection; the identity still needs a data-plane role assignment
  on the target resource.
examples:
  - name: Enable the system-assigned identity.
    text: az logicapp identity assign --resource-group orders-rg --name orders-app --system-assigned
  - name: Attach a user-assigned identity.
    text: az logicapp identity assign --resource-group orders-rg --name orders-app --user-assigned /subscriptions/0000/resourceGroups/orders-rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/orders-identity
"""

helps['logicapp identity show'] = """
type: command
short-summary: Show the managed identity of a deployed Logic App.
long-summary: >
  Reports type None when the app has no identity, rather than printing nothing.
examples:
  - name: Show the identity, including the principal id to grant roles to.
    text: az logicapp identity show --resource-group orders-rg --name orders-app
"""

helps['logicapp identity remove'] = """
type: command
short-summary: Remove a managed identity from a deployed Logic App.
long-summary: >
  Removes only what is named, leaving other identities assigned. Workflows using an
  identity-based connection will start failing authentication once their identity is
  removed.
examples:
  - name: Remove the system-assigned identity.
    text: az logicapp identity remove --resource-group orders-rg --name orders-app --system-assigned
"""
