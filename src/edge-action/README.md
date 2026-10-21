# Azure CLI Edge Action Extension

Azure CLI extension for managing Azure Front Door (AFD) Edge Actions.

## Overview

Edge Actions allow you to customize how Azure Front Door handles requests and responses at the edge. This extension provides commands to create, manage, and deploy Edge Actions for Azure Front Door.

## Installation

```bash
az extension add --name edge-action
```

## Commands

### Edge Action Management

```bash
# Create an edge action
az edge-action create --resource-group myResourceGroup --name myEdgeAction --location global --sku name=Standard tier=Standard

# List edge actions
az edge-action list --resource-group myResourceGroup

# Show edge action details
az edge-action show --resource-group myResourceGroup --name myEdgeAction

# Update edge action
az edge-action update --resource-group myResourceGroup --name myEdgeAction --tags env=prod

# Delete edge action
az edge-action delete --resource-group myResourceGroup --name myEdgeAction
```

### Version Management

```bash
# Create a version
az edge-action version create --resource-group myResourceGroup --edge-action-name myEdgeAction --name v1 --location global --deployment-type file --is-default-version True

# Deploy code to a version
az edge-action version deploy-from-file --resource-group myResourceGroup --edge-action-name myEdgeAction --version v1 --file-path ./mycode.js

# List versions
az edge-action version list --resource-group myResourceGroup --edge-action-name myEdgeAction

# Download version code as a ZIP file
az edge-action version get-version-code --resource-group myResourceGroup --edge-action-name myEdgeAction --version v1 --output-directory ./downloads

# Delete a version
az edge-action version delete --resource-group myResourceGroup --edge-action-name myEdgeAction --name v1
```

`get-version-code --output-directory` (alias `-d`) creates the output directory
when needed and saves the decoded bytes as `<response-name>.zip`, overwriting an
existing file with that name. It returns `file` and `message` fields identifying
the saved file. Without this option, the command returns the original `name` and
base64-encoded `content`. With `--no-wait`, it does not wait for or save the download.
Invalid content, unsafe response filenames, and file-write errors are reported
instead of returning a successful download result.

### Execution Filters

```bash
# Create an execution filter
az edge-action execution-filter create --resource-group myResourceGroup --edge-action-name myEdgeAction --name myFilter --location global --version-id /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Cdn/edgeActions/{name}/versions/{version} --execution-filter-identifier-header-name x-edge-action --execution-filter-identifier-header-value enabled

# List execution filters
az edge-action execution-filter list --resource-group myResourceGroup --edge-action-name myEdgeAction

# Update one execution-filter field; omitted fields are preserved
az edge-action execution-filter update --resource-group myResourceGroup --edge-action-name myEdgeAction --name myFilter --execution-filter-identifier-header-value updated

# Point the filter to another version under the same Edge Action
az edge-action execution-filter update --resource-group myResourceGroup --edge-action-name myEdgeAction --name myFilter --version-id /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Cdn/edgeActions/{name}/versions/v2

# Delete an execution filter
az edge-action execution-filter delete --resource-group myResourceGroup --edge-action-name myEdgeAction --name myFilter
```

Execution-filter `update` uses GET followed by PUT and supports `--tags`, `--version-id`,
`--execution-filter-identifier-header-name`, and
`--execution-filter-identifier-header-value`, independently or together.
Omitted fields are preserved from the fetched resource. Tags replace the tag collection;
use `--tags "{}"` to clear it. The header name/value pair must be unique among
other filters under the same Edge Action; multiple filters can reference the same
version. Existing generic `--set`, `--add`, `--remove`, and `--force-string`
options remain available. Named arguments are applied first, followed by generic
operations in their specified order; a generic operation on the same property
therefore takes precedence. Generic options remain subject to the resource schema
and service validation; for example, `--add` requires a list property, and this
resource has no writable list properties. Generic property paths use the AAZ
flattened field names, for example `--set execution_filter_identifier_header_value=enabled`
or `--remove tags.purpose`, rather than `properties.executionFilterIdentifierHeaderValue`.

## Features

- Full lifecycle management of Azure Front Door Edge Actions
- Version control for Edge Action code
- JavaScript and zip file deployment support
- Execution filter management for selective Edge Action execution
- Azure Front Door route attachment support

## Development and tests

The generated commands target API version `2026-10-01`. Maintain command models
in AAZ and regenerate the `aaz` directory; do not patch generated request or response
code by hand. Customizations in `custom.py` and `commands.py` are maintained
separately from the generated `aaz` directory.

The registered `GetVersionCode` subclass owns the download arguments and file-output
handling. It retains the generated request, response deserialization, polling, and
`--no-wait` behavior without modifying generated code.

CLI help examples are maintained in the AAZ Workspace Editor's command examples.
Export those examples to the AAZ repository before regenerating the extension;
regeneration does not preserve examples added only to generated Python files.
Scenario recording and playback use the test commands, not the help examples.
The saved execution-filter update model uses AAZ's `GenericOnly` generation mode.
Keep that mode when reloading/regenerating from the unchanged Swagger. The PUT
model's parent `properties` annotation excludes update mutability, so the generated
command does not expose the writable version/header arguments. The extension-owned
`ExecutionFilterUpdate` subclass adds those optional arguments and applies supplied
values in `pre_instance_update`. Its registration in `commands.py` retains the
generated GET/PUT operations, generic update options, polling, and error handling.
The customization is outside generated files and does not modify the spec.

The registered `swap-default` customization uses an operation-specific AAZ client
that supplies a no-op deserializer only when the generated operation supplies none.
Successful polling response bodies are discarded for this no-result action;
204/no-content results, existing deserializers, `--no-wait`, and polling failures
retain their normal behavior. This compatibility fix ships with the extension and
survives regeneration of the generated command files. It does not require a local
Azure CLI runtime patch or a spec change; the planned RP response remains
204/no-content.

The test suite separates offline contracts from recorded service evidence:

| Suite | Purpose |
| --- | --- |
| `test_edge_action_contract.py` | Offline tests through registered commands and the AAZ HTTP pipeline: API version, request serialization, flattened resource output, pagination, named/generic execution-filter updates and polling, help argument parsing, no-content responses, errors, and `no_wait`. Responses are synthetic, not recordings. |
| `test_edge_action_custom.py` | Offline tests for file/ZIP encoding, automatic ZIP creation, validation, and forwarding to the generated deployment command. |
| `test_edge_action.py` | Recordable `ScenarioTest` lifecycles using `ResourceGroupPreparer`, covering CRUD, tag updates, file/ZIP deployment, code retrieval, default-version swaps, and every execution-filter update field. |
| `test_edge_action_spec.py` | Offline pinned-Swagger validation: positive/negative request and response schema tests, polling and pagination contracts, API-version checks, and strict validation of every checked-in cassette. |
| `test_edge_action_recording_processors.py` | Sanitizer regression tests, cassette hygiene, and offline VCR matching of signed polling links. |

Every synthetic request and response in `test_edge_action_contract.py` also passes
through the pinned specification validator. Coverage includes create HTTP 200/201
polling followed by GET, asynchronous deletion, and both immediate and asynchronous
action results. These tests exercise generated behavior, but do not replace
successful playback of real stable-API recordings.

The lifecycle assertions follow the EdgeActions Python and PowerShell scenarios:
verify the result as well as the subsequent GET, preserve deployment/default-version
properties during tag updates, use full version resource IDs in execution filters,
and delete filters before versions, with non-default versions deleted before the
default version. All three resource update commands retain
GET/PUT generic update. The execution-filter live scenario deploys two versions
and independently changes tags, header
name, header value, and version ID; it also updates all four together and clears
tags. It also exercises `--set` with `--force-string` and `--remove`.
Every step checks both the update result and a subsequent GET, including all
unchanged fields. Header pairs are derived from the randomized filter name.

From the repository root, in an activated Azure CLI development environment:

```powershell
python -m pip install -r src\edge-action\azext_edge_action\tests\requirements.txt
azdev extension add edge-action
azdev test test_edge_action_contract test_edge_action_custom --discover --series
```

For a direct offline run without installing the extension:

```powershell
$env:PYTHONPATH = (Resolve-Path .\src\edge-action).Path
python -m pytest src\edge-action\azext_edge_action\tests\latest\test_edge_action_contract.py src\edge-action\azext_edge_action\tests\latest\test_edge_action_custom.py -q
```

The integration-test runner in `scripts/ci/test_source.py` installs each selected
extension's `<package>/tests/requirements.txt` before `azdev test --discover`.
This installs `jsonschema` for these tests without adding it to the extension's
runtime dependencies. Local test runs must install the test requirements explicitly
as shown above; `azdev extension add` alone does not install them.

### Pinned specification and offline audit

`tests/latest/spec_snapshot.json` bundles the stable Swagger and its common-type
references from `Azure/azure-rest-api-specs` commit
`9d29928794867148db0aed101144d14b2876e3a1`, with SHA-256 hashes of both source
documents. At verification, the stable Swagger's latest upstream change was
`2e2b290fd446b03bbddcdc31098ff97e7218f0cf` (LRO headers and deployment results).
Both bundled source hashes matched the local specs checkout.

A commit hash is not required to generate from a local checkout, but a full SHA
is required to refresh this reproducible test snapshot. Refresh downloads from
that immutable commit; ordinary tests and cassette audits never fetch schemas:

```powershell
python src\edge-action\azext_edge_action\tests\latest\spec_validation.py --refresh 9d29928794867148db0aed101144d14b2876e3a1
python -m pytest src\edge-action\azext_edge_action\tests\latest\test_edge_action_spec.py src\edge-action\azext_edge_action\tests\latest\test_edge_action_recording_processors.py -q
python src\edge-action\azext_edge_action\tests\latest\spec_validation.py --recordings src\edge-action\azext_edge_action\tests\latest\recordings
```

The audit reports the cassette and interaction number and exits nonzero on any
mismatch. Preview recordings fail the stable API check; they must not be skipped
or relabeled to claim stable coverage. To exercise validator/sanitizer unit tests
separately, append `-k "not test_recording_matches_pinned_spec"` to the pytest
command. Do not interpret that selected run as a passing stable recording audit.

Validation checks HTTP requests and responses rather than inspecting generated
Python source. An actual PUT 202 is rejected because this Swagger declares only
PUT 200/201. Resource responses,
required fields, types, no-content responses, polling headers, status documents,
Location results and pagination bodies are checked against their own contracts.
The validator has two explicit, test-only exceptions: version response
`validationStatus` may be null, and swapDefault's Location response need not be
HTTP 204 with an empty body. A swapDefault Location HTTP 200 response and
Azure-AsyncOperation status responses validate only the JSON `status` field
(a nonempty string), not other body fields. A swapDefault Location HTTP 204
response is accepted without inspecting its body. HTTP success and API-version
checks remain enforced. Other operations' response contracts and swapDefault's
initial POST response remain unchanged; the pinned Swagger is not modified.
When swapDefault's Location points to the affected version resource itself, a
HTTP 200 response is validated against the version GET schema, not the status
document schema. Subsequent GETs to that resource keep the same resource
validation; opaque Location endpoints still require a status document.
The swapDefault behavioral tests accept either a successful polling status body
or an empty Location result, without requiring the RP to return a body. They invoke
the registered customization against the unmodified Azure CLI runtime, including
Azure-AsyncOperation-only, Location-only, and combined polling flows. Schema
allowances alone do not fix the missing-deserializer error; the customization
described above supplies that runtime compatibility.

### Recording sanitization

`EdgeActionRecordingProcessor` extends, rather than replaces, `ScenarioTest`'s
default subscription, random-name and authentication processors. It runs on
recording and replay copies; it does not rewrite live HTTP requests.
It removes authentication/cookie and tracing headers, redacts `systemData`
identities and known token fields, and hashes signed polling-query values
(`t`, `c`, `s`, `h`, `sig`, `token`, `access_token`) into stable placeholders.
Distinct tokens remain distinct for replay matching. Header names, polling URLs,
retry delays, API versions, status codes, JSON types and deployment/code content
are preserved; existing Content-Length headers are recalculated.

New recordings are sanitized by the scenario hooks. To apply the same processor
to existing recordings without re-recording their traffic, offline:

```powershell
python src\edge-action\azext_edge_action\tests\latest\recording_processors.py src\edge-action\azext_edge_action\tests\latest\recordings
```

Review new recording diffs for additional service-specific sensitive fields before
committing; these targeted rules are not a general-purpose secret scanner.

### Recording service scenarios

Live execution must be explicitly authorized against a suitable test environment.
Re-record affected scenarios whenever their command sequence or assertions change,
including execution-filter named-field updates, generic options, and cleanup.
Do not change API-version strings or synthesize interactions to make playback pass.

Select an authorized disposable test subscription with access to the stable API.
Live tests create resources and may incur charges; use the repository's configured
Azure CLI development environment, log in, and verify the selected subscription
before running:

```powershell
azdev test EdgeActionScenarioTest --discover --series --live
azdev test EdgeActionScenarioTest --series
azdev cmdcov edge-action
```

The first command records real traffic, and the second replays it. Missing recording
files also trigger live execution, so retain recordings when running offline.
Review and sanitize recording diffs before committing. Resource-group cleanup is
registered by `ResourceGroupPreparer`, including when assertions fail.

To re-record only the changed execution-filter scenario and then replay it:

```powershell
azdev test test_edge_action_execution_filter_crud --discover --series --live
azdev test test_edge_action_execution_filter_crud --series
```

Subscription-level listing is defined in the stable Swagger, but the current
exported AAZ models place it under `cdn edge-action list`. This extension's
`edge-action list` still requires `--resource-group`; merging both list resources
under the intended command is an AAZ-model change, not something the tests should
silently emulate.

References:
[Azure CLI test guidance](https://github.com/Azure/azure-cli/blob/dev/doc/authoring_tests.md),
[AAZ generation](https://azure.github.io/aaz-dev-tools/pages/usage/cli-generator/),
[EdgeActions Python tests](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/edgeactions/azure-mgmt-edgeactions/tests),
and [EdgeAction PowerShell tests](https://github.com/Azure/azure-powershell/tree/main/src/EdgeAction/EdgeAction.Autorest/test).
