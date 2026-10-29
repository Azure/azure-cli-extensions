# Azure CLI Relationship Extension #
This is an extension to Azure CLI to manage Relationship resources.

Relationships are ARM extension resources that create semantic associations
between a source resource and a target resource. Three relationship types are supported:

- **dependencyOf** — creates dependency links between ARM resources
- **serviceGroupMember** — associates Azure resources with Service Groups, with the Service Group as the relationship source
- **contains** — read-only, system-discovered containment relationships at subscription and resource-group scope

## How to use ##
Install this extension using the below CLI command
```
az extension add --name relationship
```

### Included Features

All commands use the stable Microsoft.Relationships API version **2026-08-01**.
The extension itself remains in preview.

| Command group | Commands | Scope selector |
| --- | --- | --- |
| `az relationship dependency-of` | `create`, `show`, `update`, `list`, `delete`, `wait` | `--resource-uri` |
| `az relationship service-group-member` | `create`, `show`, `update`, `list`, `delete`, `wait` | `--resource-uri` |
| `az relationship dependency-of-by-service-group` | `create`, `show`, `update`, `list`, `delete`, `wait` | `--service-group-name` |
| `az relationship contains` | `list` | `--subscription`, optional `--resource-group` |

The `update` commands read the current resource, apply changes, and write it back
with PUT; they do not call a PATCH endpoint. Create, update, and delete support
`--no-wait`. List commands follow pagination and support `--max-items` and
`--next-token`.

#### Create a dependencyOf relationship from a resource group to a service group
```
az relationship dependency-of create \
    --resource-uri "/subscriptions/{sub}/resourceGroups/{rg}" \
    --name myDependency \
    --target-id "/providers/Microsoft.Management/serviceGroups/mySG"
```

#### Create a dependencyOf relationship from a subscription to a service group
```
az relationship dependency-of create \
    --resource-uri "/subscriptions/{sub}" \
    --name subDep \
    --target-id "/providers/Microsoft.Management/serviceGroups/mySG"
```

#### Show a dependencyOf relationship
```
az relationship dependency-of show \
    --resource-uri "/subscriptions/{sub}/resourceGroups/{rg}" \
    --name myDependency
```

#### Delete a dependencyOf relationship
```
az relationship dependency-of delete \
    --resource-uri "/subscriptions/{sub}/resourceGroups/{rg}" \
    --name myDependency --yes
```

#### Create a serviceGroupMember relationship
```
az relationship service-group-member create \
    --resource-uri "/subscriptions/{sub}/resourceGroups/{rg}" \
    --name myMembership \
    --source-id "/providers/Microsoft.Management/serviceGroups/mySG"
```

#### Show a serviceGroupMember relationship
```
az relationship service-group-member show \
    --resource-uri "/subscriptions/{sub}/resourceGroups/{rg}" \
    --name myMembership
```

#### Delete a serviceGroupMember relationship
```
az relationship service-group-member delete \
    --resource-uri "/subscriptions/{sub}/resourceGroups/{rg}" \
    --name myMembership --yes
```

#### List and update relationships at a resource scope
```
az relationship dependency-of list --resource-uri "/subscriptions/{sub}/resourceGroups/{rg}"
az relationship service-group-member list --resource-uri "/subscriptions/{sub}"

az relationship dependency-of update \
    --resource-uri "/subscriptions/{sub}/resourceGroups/{rg}" \
    --name myDependency \
    --target-id "/providers/Microsoft.Management/serviceGroups/mySG"

az relationship service-group-member update \
    --resource-uri "/subscriptions/{sub}/resourceGroups/{rg}" \
    --name myMembership \
    --source-id "/providers/Microsoft.Management/serviceGroups/mySG"
```

#### Manage dependencyOf relationships attached to a Service Group
These commands use explicit tenant-level Service Group routes. Existing
`dependency-of` commands still accept a Service Group ID as `--resource-uri`.
```
az relationship dependency-of-by-service-group create \
    --service-group-name sourceSG --name myDependency \
    --target-id "/providers/Microsoft.Management/serviceGroups/targetSG"

az relationship dependency-of-by-service-group list --service-group-name sourceSG
az relationship dependency-of-by-service-group show --service-group-name sourceSG --name myDependency

az relationship dependency-of-by-service-group update \
    --service-group-name sourceSG --name myDependency \
    --target-id "/providers/Microsoft.Management/serviceGroups/anotherTargetSG"

az relationship dependency-of-by-service-group delete \
    --service-group-name sourceSG --name myDependency --yes --no-wait
az relationship dependency-of-by-service-group wait \
    --service-group-name sourceSG --name myDependency --deleted
```

#### List contains relationships
Omit `--resource-group` to list at subscription scope. Contains relationships are
read-only; no create, update, or delete commands are available.
```
az relationship contains list --subscription "{sub}"

az relationship contains list --subscription "{sub}" --resource-group "{rg}" \
    --filter "properties.metadata.targetType eq 'Microsoft.Compute/virtualMachines'"
```

### Validation

Use the Azure CLI development environment and the current `azure-cli-testsdk`
from the Azure CLI source repository; the older PyPI test SDK can have incompatible
authentication mocks with recent CLI versions.

Run the unit tests and recorded scenarios without Azure credentials:
```
python -m pytest src/relationship/azext_relationship/tests/latest -q
```

PR readiness also requires both linter passes from the repository workflow:

```powershell
azdev linter relationship --min-severity medium
$mergeBase = git merge-base HEAD upstream/main
azdev linter EXT --repo . --src HEAD --tgt $mergeBase --rules missing_command_example
foreach ($file in (git diff --name-only --diff-filter=AM $mergeBase)) {
    $scan = azdev scan --confidence-level MEDIUM -f $file --continue-on-failure | ConvertFrom-Json
    if ($scan.secrets_detected) { throw "Secret scan findings in $file" }
}
```

The second pass uses Git history and is not covered by the first invocation.
Examples for generated commands must be defined in their AAZ models; handwritten
help entries alone do not populate the generated command metadata.

All scenarios support offline playback from the checked-in recordings.

To re-record, explicitly set `AZURE_TEST_RUN_LIVE=true` and configure:

- `AZURE_RELATIONSHIP_TEST_TARGET_SG`: the shared Service Group resource ID for the
  dependency and membership scenarios.
- `AZURE_RELATIONSHIP_TEST_DEPENDENCY_SG`: a **different**, dedicated Service Group
  resource ID used only by the Service Group-scoped dependency lifecycle.
- `AZURE_TENANT_ID`, `AZURE_RELATIONSHIP_TEST_PRINCIPAL_ID`, and
  `AZURE_RELATIONSHIP_TEST_USER`: the test tenant and caller identifiers to sanitize.

Provision fresh child Service Groups directly under the authorized root, await
their provisioning operations, and allow at least five minutes after the dedicated
fixture is ready before starting the suite. Both fixtures require permission to
manage relationships, such as their automatically provisioned Service Group
Administrator assignments. Use a different Service Group for the dependency
lifecycle than for the shared fixture. Remove run-created Service Groups and grants
after recording.

Resource-side
relationship permissions must also be available on the test subscription and its
resources. For a dedicated live-test environment, assign Relationship Administrator
to the test identity once at the test subscription scope before running the suite;
the scenarios do not assign roles individually. Allow new assignments to propagate
before starting the tests. No role changes on the root Service Group are required.
Live scenarios create temporary resource groups and, where needed, managed identities.
Scenarios do not retry commands. Recordings normalize fixture and caller identifiers
through the test framework's name replacer.
