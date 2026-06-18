# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


# ── Groups ───────────────────────────────────────────────────────────────

helps['chaos'] = """
type: group
short-summary: Manage Azure Chaos Studio resources.
long-summary: |
    Commands for Azure Chaos Studio v2 Workspaces — create and manage workspaces,
    scenarios, scenario configurations, and runs for chaos engineering experiments.
"""

helps['chaos workspace'] = """
type: group
short-summary: Manage Chaos Studio workspaces.
long-summary: |
    Workspaces are the top-level resource for Chaos Studio v2. They define
    the scope of resources that can be targeted by chaos scenarios and the
    managed identity used for fault injection.
"""

helps['chaos scenario'] = """
type: group
short-summary: Manage Chaos Studio scenarios within a workspace.
long-summary: |
    Scenarios define the fault-injection actions available in a workspace.
    Catalog scenarios are populated by workspace evaluation (see
    'az chaos workspace refresh-recommendation'); custom scenarios can be
    created directly.
"""

helps['chaos scenario config'] = """
type: group
short-summary: Manage scenario configurations for a Chaos Studio scenario.
long-summary: |
    Scenario configurations define the steps, branches, and fault parameters
    for a chaos experiment run. Use 'validate' to check a configuration before
    execution and 'fix-permissions' to grant required RBAC roles.
"""

helps['chaos scenario run'] = """
type: group
short-summary: Manage scenario runs for a Chaos Studio scenario.
long-summary: |
    Scenario runs represent individual executions of a scenario configuration.
    Use 'start' to begin a new run, 'show' to inspect its status, and
    'cancel' to stop a running execution.
"""

helps['chaos discovered-resource'] = """
type: group
short-summary: Browse discovered resources in a Chaos Studio workspace.
long-summary: |
    Discovered resources are populated by workspace discovery scans
    (triggered via 'az chaos workspace refresh-recommendation').
    Use 'list' to see all discovered resources and 'show' to inspect
    a specific one.
"""

# ── setup (composite / porcelain) ────────────────────────────────────────

helps['chaos setup'] = """
type: command
short-summary: Stand up a ready-to-use Chaos Studio environment in one step.
long-summary: |
    First-day-experience command that orchestrates the full bootstrap workflow
    so you do not have to run the individual commands yourself:

      1. Creates the resource group if it does not already exist. If the group
         already exists it is reused, and '--location' is optional (it defaults
         to the group's location). If the group does not exist, '--location' is
         required because setup creates the group and has no region to default
         to.
      2. Creates the workspace with a managed identity (user-assigned if
         '--user-assigned' is supplied, otherwise a system-assigned identity).
      3. Grants that identity the built-in 'Reader' role on each '--scopes'
         target (skip with '--skip-permissions') — discovery and evaluation run
         under the workspace identity and cannot enumerate resources without it.
         Re-assigning an existing role is a no-op.
      4. Evaluates scenarios for the workspace (resource discovery + scenario
         recommendations). When a NEW Reader assignment was just made, the
         evaluation is retried for a few minutes to absorb Azure Resource Graph
         propagation lag; pass '--skip-evaluation-wait' to run a single attempt
         (e.g. in CI) and get a rerun hint instead of waiting.
      5. Prints the discovered scenarios and the commands to run next.

    This is a composite "porcelain" command: it wraps the granular 'workspace
    create', 'workspace refresh-recommendation', and role-assignment operations
    behind a single workflow verb. For fine-grained control, run those commands
    directly.

    WHY '--scopes' IS REQUIRED:
    A workspace must declare which resources Chaos Studio is allowed to target —
    there is no safe default. You are expected to already have a resource group
    or service group (or a subscription) you plan to run experiments against.
    Pass one or more ARM resource IDs as the scope. The Azure portal's Create
    Workspace blade requires the same explicit choice.

    ARM RESOURCE ID FORMATS (for '--scopes'):
      Resource group (most common scope):
        `/subscriptions/<sub-id>/resourceGroups/<rg-name>`
      Subscription:
        `/subscriptions/<sub-id>`
      Service group:
        `/providers/Microsoft.Management/serviceGroups/<service-group-name>`

    ARM RESOURCE ID FORMAT (for '--user-assigned'):
      User-assigned managed identity:
        `/subscriptions/<sub-id>/resourceGroups/<rg-name>/providers/Microsoft.ManagedIdentity/userAssignedIdentities/<identity-name>`

    Tip: copy a resource group's ID with
    `az group show -n <rg> --query id -o tsv`.
examples:
    - name: Bootstrap a workspace scoped to a resource group, using a system-assigned identity
      text: >
        az chaos setup --name MyWorkspace --resource-group MyRG --location westus2
        --scopes "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/MyRG"
    - name: Bootstrap with a user-assigned identity as the workspace identity
      text: >
        az chaos setup --name MyWorkspace --resource-group MyRG --location westus2
        --scopes "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/MyRG"
        --user-assigned "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/MyRG/providers/Microsoft.ManagedIdentity/userAssignedIdentities/MyIdentity"
    - name: Bootstrap a workspace scoped to a service group
      text: >
        az chaos setup --name MyWorkspace --resource-group MyRG --location westus2
        --scopes "/providers/Microsoft.Management/serviceGroups/my-critical-services"
    - name: Bootstrap scoped to multiple resource groups and manage RBAC yourself
      text: >
        az chaos setup --name MyWorkspace --resource-group MyRG --location westus2
        --scopes "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/AppRG"
        "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/DataRG"
        --skip-permissions
"""

# ── workspace commands ───────────────────────────────────────────────────

helps['chaos workspace create'] = """
type: command
short-summary: Create a Chaos Studio workspace.
long-summary: |
    Creates a new workspace with the specified scope and managed identity
    configuration. The workspace is the top-level container for scenarios,
    configurations, and runs. This is an LRO that is polled to completion
    by default.

    Identity is configured via the standard Azure CLI flags:
      --system-assigned ""                          (enables a system-assigned identity)
      --user-assigned <resource-id> [<resource-id> ...]  (assigns one or more user-assigned identities)
    Either, both, or neither may be supplied.
examples:
    - name: Create a workspace with a system-assigned identity
      text: >
        az chaos workspace create --name MyWorkspace --resource-group MyRG
        --location westus2
        --scopes "/subscriptions/{sub}/resourceGroups/MyRG"
        --system-assigned ""
    - name: Create a workspace with a user-assigned identity
      text: >
        az chaos workspace create --name MyWorkspace --resource-group MyRG
        --location westus2
        --scopes "/subscriptions/{sub}/resourceGroups/MyRG"
        --user-assigned "/subscriptions/{sub}/resourceGroups/MyRG/providers/Microsoft.ManagedIdentity/userAssignedIdentities/myId"
"""

helps['chaos workspace show'] = """
type: command
short-summary: Get a Chaos Studio workspace.
examples:
    - name: Show a workspace
      text: >
        az chaos workspace show --name MyWorkspace --resource-group MyRG
    - name: Show a workspace with JSON output
      text: >
        az chaos workspace show --name MyWorkspace --resource-group MyRG --output json
"""

helps['chaos workspace list'] = """
type: command
short-summary: List Chaos Studio workspaces.
long-summary: |
    Without --resource-group, lists all workspaces in the subscription.
    With --resource-group, lists only workspaces in that resource group.
examples:
    - name: List all workspaces in the subscription
      text: >
        az chaos workspace list
    - name: List workspaces in a specific resource group
      text: >
        az chaos workspace list --resource-group MyRG
"""

helps['chaos workspace delete'] = """
type: command
short-summary: Delete a Chaos Studio workspace.
examples:
    - name: Delete a workspace
      text: >
        az chaos workspace delete --name MyWorkspace --resource-group MyRG --yes
    - name: Delete a workspace without waiting for completion
      text: >
        az chaos workspace delete --name MyWorkspace --resource-group MyRG --yes --no-wait
"""

helps['chaos workspace update'] = """
type: command
short-summary: Update a Chaos Studio workspace.
long-summary: |
    Update workspace properties such as tags and identity configuration.
    This is an LRO that is polled to completion by default.
examples:
    - name: Update workspace tags
      text: >
        az chaos workspace update --name MyWorkspace --resource-group MyRG
        --tags env=dev team=chaos
    - name: Update the workspace scopes
      text: >
        az chaos workspace update --name MyWorkspace --resource-group MyRG
        --scopes /subscriptions/SUB/resourceGroups/MyRG/providers/Microsoft.Compute/virtualMachines/MyVM
"""

helps['chaos workspace refresh-recommendation'] = """
type: command
short-summary: Refresh scenario recommendations and trigger resource discovery for a workspace.
long-summary: |
    Triggers workspace evaluation, which refreshes scenario recommendations and
    runs resource discovery across all in-scope resources. For non-custom (catalog)
    scenarios, this operation satisfies the evaluation gate required by
    'az chaos scenario config validate' and 'az chaos scenario run start'.
examples:
    - name: Refresh recommendations for a workspace
      text: >
        az chaos workspace refresh-recommendation --name MyWorkspace --resource-group MyRG
    - name: Refresh recommendations without waiting for completion
      text: >
        az chaos workspace refresh-recommendation --name MyWorkspace --resource-group MyRG --no-wait
"""

helps['chaos workspace evaluate-scenarios'] = """
type: command
short-summary: >-
    Alias of `az chaos workspace refresh-recommendation`.
    Refresh scenario recommendations and trigger resource discovery for a workspace.
long-summary: |
    This command is a CLI-side alias for 'az chaos workspace refresh-recommendation'.
    Both commands invoke the same API operation (Workspaces_RefreshRecommendations)
    with identical arguments and behavior. The canonical command name is
    'az chaos workspace refresh-recommendation'.
examples:
    - name: Evaluate scenarios for a workspace
      text: >
        az chaos workspace evaluate-scenarios --name MyWorkspace --resource-group MyRG
    - name: Evaluate scenarios without waiting for completion
      text: >
        az chaos workspace evaluate-scenarios --name MyWorkspace --resource-group MyRG --no-wait
"""

helps['chaos workspace show-discovery'] = """
type: command
short-summary: Get the latest resource-discovery result for a workspace.
long-summary: |
    Retrieves the latest workspace-scope resource-discovery operation result.
    Returns the discovery operation's state (in-progress, succeeded, failed)
    and any failure details. This is a read-only GET — it does NOT trigger
    a new discovery. Use 'az chaos workspace refresh-recommendation' to
    trigger a new discovery scan.
examples:
    - name: Show the latest discovery result
      text: >
        az chaos workspace show-discovery --name MyWorkspace --resource-group MyRG
    - name: Show discovery result with JSON output
      text: >
        az chaos workspace show-discovery --name MyWorkspace --resource-group MyRG --output json
"""

helps['chaos workspace show-evaluation'] = """
type: command
short-summary: Get the latest scenario-evaluation result for a workspace.
long-summary: |
    Retrieves the latest workspace scenario-evaluation operation result.
    Returns the evaluation state — useful for checking whether the workspace
    has been evaluated (a prerequisite for 'scenario config validate' and
    'scenario run start' on catalog scenarios). This is a read-only GET — it
    does NOT trigger a new evaluation. Use
    'az chaos workspace refresh-recommendation' to trigger evaluation.
examples:
    - name: Show the latest evaluation result
      text: >
        az chaos workspace show-evaluation --name MyWorkspace --resource-group MyRG
    - name: Show evaluation result with JSON output
      text: >
        az chaos workspace show-evaluation --name MyWorkspace --resource-group MyRG --output json
"""

# ── scenario commands ────────────────────────────────────────────────────

helps['chaos scenario create'] = """
type: command
short-summary: Create or replace a scenario in a workspace.
long-summary: |
    Creates a custom scenario. Custom scenarios are authored directly via this
    command and define their own actions and parameters. Catalog scenarios
    (populated by 'az chaos workspace refresh-recommendation') are not
    created this way.

    Use --actions, --parameters, and --description to populate the scenario
    body. Each --actions element uses the shorthand-syntax form
    'action-id=<id> name=<step> duration=<ISO8601>' — see
    https://learn.microsoft.com/en-us/cli/azure/use-azure-cli-successfully-tips#use-shorthand-syntax
    for the full syntax reference.
examples:
    - name: Create a minimal custom scenario (no actions yet — add via update)
      text: >
        az chaos scenario create --workspace-name MyWorkspace --resource-group MyRG
        --name MyScenario --description "My custom scenario"
    - name: Create a custom scenario with one action
      text: >
        az chaos scenario create --workspace-name MyWorkspace --resource-group MyRG
        --name MyScenario --description "VM shutdown experiment"
        --actions "[{action-id:'microsoft-compute-shutdown/1.0',name:'step1',duration:'PT5M'}]"
"""

helps['chaos scenario show'] = """
type: command
short-summary: Get a scenario by name.
examples:
    - name: Show a scenario
      text: >
        az chaos scenario show --workspace-name MyWorkspace --resource-group MyRG
        --name ZoneDown-1.0
    - name: Show a scenario with JSON output
      text: >
        az chaos scenario show --workspace-name MyWorkspace --resource-group MyRG
        --name ZoneDown-1.0 --output json
"""

helps['chaos scenario list'] = """
type: command
short-summary: List scenarios in a workspace.
examples:
    - name: List all scenarios
      text: >
        az chaos scenario list --workspace-name MyWorkspace --resource-group MyRG
    - name: List scenarios with table output
      text: >
        az chaos scenario list --workspace-name MyWorkspace --resource-group MyRG --output table
"""

helps['chaos scenario delete'] = """
type: command
short-summary: Delete a scenario.
examples:
    - name: Delete a scenario
      text: >
        az chaos scenario delete --workspace-name MyWorkspace --resource-group MyRG
        --name MyScenario --yes
    - name: Delete a scenario with confirmation prompt
      text: >
        az chaos scenario delete --workspace-name MyWorkspace --resource-group MyRG
        --name MyScenario
"""

# ── scenario config commands ─────────────────────────────────────────────

helps['chaos scenario config create'] = """
type: command
short-summary: Create a scenario configuration with parameters and filters.
long-summary: |
    Creates a scenario configuration that defines the fault parameters and
    resource targeting filters for a chaos experiment run.

    --parameters accepts either inline JSON or a file reference using the
    standard '@filename.json' syntax (e.g., --parameters @params.json).

    Supported --filters keys (shorthand syntax shown; all keys are optional):

      locations=[...]       Azure region strings (e.g. 'westus2'). Only
                            resources in these regions are included. Omit
                            for all regions.
      zones=[...]           Logical availability zone IDs ('1', '2', '3',
                            'zone-redundant'). Only resources whose zones
                            intersect this list are included. The `zones`
                            and `physical-zones` keys are mutually exclusive.
      physical-zones=[...]  Physical zone IDs in `{region}-az{N}` form
                            (e.g. 'westus2-az1'). Resolved per-subscription
                            to logical zones at execution time. Only ONE
                            physical zone is supported in preview. As noted
                            above, this is mutually exclusive with `zones`.

    Supported --exclusions keys (shorthand syntax shown; all keys are optional):

      resources=[...]       ARM resource IDs to exclude verbatim.
      tags=[{key,value},..] Resources with any matching tag are excluded.
      types=[...]           Resource types (e.g. 'Microsoft.Compute/...').
                            All resources of these types are excluded.

    Setting both `zones` and `physical-zones` is rejected by the server with a
    400. No CLI-side validation is performed for this mutual exclusion — the
    server is authoritative.
examples:
    - name: Create a configuration with logical zone targeting
      text: >
        az chaos scenario config create --workspace-name MyWorkspace --resource-group MyRG
        --scenario-name ZoneDown-1.0 --name zone1
        --parameters "[{key:duration,value:PT10M}]"
        --filters "{locations:[westus2],zones:[1]}"
    - name: Create a configuration with physical zone targeting
      text: >
        az chaos scenario config create --workspace-name MyWorkspace --resource-group MyRG
        --scenario-name ZoneDown-1.0 --name zone-physical
        --parameters "[{key:duration,value:PT10M}]"
        --filters "{locations:[westus2],physical-zones:[westus2-az1]}"
    - name: Create a configuration with exclusions by resource ID, tag, and type
      text: >
        az chaos scenario config create --workspace-name MyWorkspace --resource-group MyRG
        --scenario-name ZoneDown-1.0 --name with-exclusions
        --parameters "[{key:duration,value:PT10M}]"
        --filters "{locations:[eastus],zones:[1]}"
        --exclusions "{resources:[/subscriptions/.../virtualMachines/protectedVM],tags:[{key:env,value:prod}],types:[Microsoft.Compute/virtualMachineScaleSets]}"
"""

helps['chaos scenario config show'] = """
type: command
short-summary: Get a scenario configuration.
examples:
    - name: Show a scenario configuration
      text: >
        az chaos scenario config show --workspace-name MyWorkspace --resource-group MyRG
        --scenario-name ZoneDown-1.0 --name zone1
    - name: Show a configuration with JSON output
      text: >
        az chaos scenario config show --workspace-name MyWorkspace --resource-group MyRG
        --scenario-name ZoneDown-1.0 --name zone1 --output json
"""

helps['chaos scenario config list'] = """
type: command
short-summary: List scenario configurations for a scenario.
examples:
    - name: List all configurations for a scenario
      text: >
        az chaos scenario config list --workspace-name MyWorkspace --resource-group MyRG
        --scenario-name ZoneDown-1.0
    - name: List configurations with table output
      text: >
        az chaos scenario config list --workspace-name MyWorkspace --resource-group MyRG
        --scenario-name ZoneDown-1.0 --output table
"""

helps['chaos scenario config delete'] = """
type: command
short-summary: Delete a scenario configuration.
examples:
    - name: Delete a scenario configuration
      text: >
        az chaos scenario config delete --workspace-name MyWorkspace --resource-group MyRG
        --scenario-name ZoneDown-1.0 --name zone1 --yes
    - name: Delete without waiting for completion
      text: >
        az chaos scenario config delete --workspace-name MyWorkspace --resource-group MyRG
        --scenario-name ZoneDown-1.0 --name zone1 --yes --no-wait
"""

helps['chaos scenario config validate'] = """
type: command
short-summary: Validate a scenario configuration.
long-summary: |
    Submits a validation request for a scenario configuration and, by default,
    waits for the validation to complete and auto-fetches the validation result.

    With --no-wait, the command submits the validation and returns immediately.
    Use 'az chaos scenario config show-validation' to retrieve the result
    once the operation completes.

    For non-custom (catalog) scenarios, the workspace must be evaluated before
    validation can succeed. If the workspace has not been evaluated, the command
    will fail with a hint to run 'az chaos workspace refresh-recommendation'.
examples:
    - name: Validate a scenario configuration and display results
      text: >
        az chaos scenario config validate --workspace-name MyWorkspace --resource-group MyRG
        --scenario-name ZoneDown-1.0 --name zone1
    - name: Submit validation without waiting (use 'show-validation' to fetch the result later)
      text: >
        az chaos scenario config validate --workspace-name MyWorkspace --resource-group MyRG
        --scenario-name ZoneDown-1.0 --name zone1 --no-wait
"""

helps['chaos scenario config show-validation'] = """
type: command
short-summary: Get the latest validation result for a scenario configuration.
long-summary: |
    Retrieves the most recent validation result for a scenario configuration.
    This is a read-only GET — it does NOT trigger a new validation. Use
    'az chaos scenario config validate' to submit a new validation request.
examples:
    - name: Show the latest validation result
      text: >
        az chaos scenario config show-validation --workspace-name MyWorkspace
        --resource-group MyRG --scenario-name ZoneDown-1.0 --name zone1
    - name: Show validation result with JSON output
      text: >
        az chaos scenario config show-validation --workspace-name MyWorkspace
        --resource-group MyRG --scenario-name ZoneDown-1.0 --name zone1
        --output json
"""

helps['chaos scenario config fix-permissions'] = """
type: command
short-summary: Fix RBAC permissions for a scenario configuration.
long-summary: |
    Assigns the RBAC roles required for the configuration's targeted resources.
    The operation runs its own internal validation before fixing permissions,
    so a prior 'az chaos scenario config validate' call is NOT required.
    However, the workspace, scenario, and configuration must all exist;
    a 404 NotFound typically means one of these resources is missing or
    the workspace has not finished provisioning.
    Use --what-if for a server-side dry-run that returns the role assignments
    that would be made without actually creating them. Note that --what-if is
    server-evaluated (not client-only like PowerShell's -WhatIf) and the
    response shape is the same PermissionsFix resource regardless of mode.
examples:
    - name: Fix permissions for a configuration
      text: >
        az chaos scenario config fix-permissions --workspace-name MyWorkspace
        --resource-group MyRG --scenario-name ZoneDown-1.0 --name zone1
    - name: Preview what permissions would be assigned (what-if mode)
      text: >
        az chaos scenario config fix-permissions --workspace-name MyWorkspace
        --resource-group MyRG --scenario-name ZoneDown-1.0 --name zone1
        --what-if
"""

helps['chaos scenario config show-permission-fix'] = """
type: command
short-summary: Get the latest permission-fix result for a scenario configuration.
long-summary: |
    Retrieves the most recent permission-fix result. This is a read-only GET —
    it does NOT trigger a new fix. The response body carries
    'properties.whatIfMode' indicating whether the latest fix was a what-if
    dry run or an actual fix; the singleton returns whichever was most recently
    submitted. Use 'az chaos scenario config fix-permissions' to trigger a new
    fix (with optional --what-if for a server-side dry run).
examples:
    - name: Show the latest permission-fix result
      text: >
        az chaos scenario config show-permission-fix --workspace-name MyWorkspace
        --resource-group MyRG --scenario-name ZoneDown-1.0 --name zone1
    - name: Show the latest permission-fix result with JSON output
      text: >
        az chaos scenario config show-permission-fix --workspace-name MyWorkspace
        --resource-group MyRG --scenario-name ZoneDown-1.0 --name zone1
        --output json
"""

# ── scenario run commands ────────────────────────────────────────────────

helps['chaos scenario run start'] = """
type: command
short-summary: Start a scenario run from a scenario configuration.
long-summary: |
    By default, runs a pre-flight validation before executing the scenario
    configuration. If validation fails, the run is not started and the command
    exits non-zero with the validation errors.

    --skip-validation bypasses pre-flight validation and proceeds directly to
    execute. Use for CI re-runs of an already-validated configuration or when
    driving the validate→execute sequence manually.

    --no-wait applies only to the execute phase. Pre-flight validation (if not
    skipped) is always awaited to completion. With --no-wait, the command returns
    immediately after kicking off execute, with the run ID parsed from the
    Location header.

    The fastest fire-and-forget invocation is --skip-validation --no-wait.
examples:
    - name: Start a scenario run (default — validates first, then executes)
      text: >
        az chaos scenario run start --workspace-name MyWorkspace --resource-group MyRG
        --scenario-name ZoneDown-1.0 --config-name zone1
    - name: Start a run skipping pre-flight validation
      text: >
        az chaos scenario run start --workspace-name MyWorkspace --resource-group MyRG
        --scenario-name ZoneDown-1.0 --config-name zone1 --skip-validation
    - name: Start a run without waiting for execute to complete
      text: >
        az chaos scenario run start --workspace-name MyWorkspace --resource-group MyRG
        --scenario-name ZoneDown-1.0 --config-name zone1 --no-wait
    - name: Fire-and-forget (skip validation and don't wait for execute)
      text: >
        az chaos scenario run start --workspace-name MyWorkspace --resource-group MyRG
        --scenario-name ZoneDown-1.0 --config-name zone1 --skip-validation --no-wait
"""

helps['chaos scenario run list'] = """
type: command
short-summary: List scenario runs for a scenario.
long-summary: |
    Lists execution-mode runs for a scenario. To filter runs to a specific
    configuration, post-filter the output by the run's configurationName
    property (visible in --output json/yaml and in table output).
examples:
    - name: List all runs for a scenario
      text: >
        az chaos scenario run list --workspace-name MyWorkspace --resource-group MyRG
        --scenario-name ZoneDown-1.0
    - name: List runs with table output
      text: >
        az chaos scenario run list --workspace-name MyWorkspace --resource-group MyRG
        --scenario-name ZoneDown-1.0 --output table
"""

helps['chaos scenario run show'] = """
type: command
short-summary: Get a specific scenario run.
examples:
    - name: Show a scenario run by ID
      text: >
        az chaos scenario run show --workspace-name MyWorkspace --resource-group MyRG
        --scenario-name ZoneDown-1.0 --run-id 12345678-1234-1234-1234-123456789012
    - name: Show a scenario run with JSON output
      text: >
        az chaos scenario run show --workspace-name MyWorkspace --resource-group MyRG
        --scenario-name ZoneDown-1.0 --run-id 12345678-1234-1234-1234-123456789012
        --output json
"""

helps['chaos scenario run cancel'] = """
type: command
short-summary: Cancel a running scenario run.
long-summary: |
    Sends a cancellation request for a running scenario run. The cancellation
    is an LRO that is polled to completion by default.
examples:
    - name: Cancel a scenario run
      text: >
        az chaos scenario run cancel --workspace-name MyWorkspace --resource-group MyRG
        --scenario-name ZoneDown-1.0 --run-id 12345678-1234-1234-1234-123456789012
    - name: Cancel without waiting for confirmation
      text: >
        az chaos scenario run cancel --workspace-name MyWorkspace --resource-group MyRG
        --scenario-name ZoneDown-1.0 --run-id 12345678-1234-1234-1234-123456789012 --no-wait
"""

# ── discovered-resource commands ─────────────────────────────────────────

helps['chaos discovered-resource list'] = """
type: command
short-summary: List discovered resources in a workspace.
long-summary: |
    Lists all resources discovered by workspace discovery scans. Use
    'az chaos workspace refresh-recommendation' to trigger a new discovery
    scan if the list appears stale.
examples:
    - name: List all discovered resources
      text: >
        az chaos discovered-resource list --workspace-name MyWorkspace --resource-group MyRG
    - name: List discovered resources with table output
      text: >
        az chaos discovered-resource list --workspace-name MyWorkspace --resource-group MyRG
        --output table
"""

helps['chaos discovered-resource show'] = """
type: command
short-summary: Get a discovered resource by name.
examples:
    - name: Show a discovered resource
      text: >
        az chaos discovered-resource show --workspace-name MyWorkspace --resource-group MyRG
        --name myvm
    - name: Show a discovered resource with JSON output
      text: >
        az chaos discovered-resource show --workspace-name MyWorkspace --resource-group MyRG
        --name myvm --output json
"""
