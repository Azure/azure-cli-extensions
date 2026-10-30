# Edge Action extension development

Contributor guidance for command generation, customizations, and tests.
For installation and usage, see [README.md](README.md).

## Command generation and customizations

The generated commands target API version `2026-10-01`. Maintain command models
in AAZ and regenerate the `aaz` directory; do not patch generated request or response
code by hand. Customizations in `custom.py` and `commands.py` are maintained
separately from the generated `aaz` directory.

Argument customizations isolate both `_args_schema` and `_arguments_schema` from
their generated base classes so added options do not depend on command load order.

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
Azure CLI runtime patch.

## Tests

The test suite uses recorded scenarios as contract snapshots and unit tests for
local behavior:

| Suite | Purpose |
| --- | --- |
| `test_edge_action_custom.py` | Standard `unittest` tests for download aliases and file output, argument-cache isolation, field boundaries, generic-update precedence, client-side pagination limits/resumption, file/ZIP deployment, and registered customization polling, no-wait, and failure paths. Transport calls are mocked; command serialization and polling execute normally. |
| `test_edge_action.py` | Recordable `ScenarioTest` lifecycles using `ResourceGroupPreparer`, covering CRUD, tag replacement/clearing, property preservation, deployment results, retrieved code content, default-version swaps, and independent/combined/generic execution-filter updates. |
| `test_edge_action_recording_processors.py` | Sanitizer regression tests, cassette hygiene, and offline VCR matching of signed polling links. |

The recorded scenarios provide service-contract regression coverage.
Root and version updates check that replacing or clearing tags preserves the
other resource fields. Deployment checks assert the stable version-resource result,
and code retrieval checks the deployed bytes, including service-packaged ZIPs.
The filter scenario checks independent and combined named updates, tag clearing,
generic-update precedence, string preservation, and tag removal, verifying each
result with a subsequent GET. It uses full version resource IDs and deletes the
filter, then the non-default version, then the default version.

Playback retains the test SDK's default request matchers, including the method,
URL, and query string (`api-version`), and additionally uses VCR's JSON-aware body
matcher. Scenario JMESPath checks assert the response fields and outcomes that
matter to the commands. A serialized request-body regression therefore cannot
pass merely because its URL still matches a recorded response, and a recording
for a different API version does not match. There is no separate Swagger snapshot
or schema validator to maintain. Focused mocked-transport unit tests cover customization failure and
polling variants without requiring live service failures or synthetic cassettes.

Playback also skips `AAZBasePolling._delay` through a replay-only patch, in addition
to the test SDK's standard playback hooks. The original method is restored after
each test; live polling and recorded `Retry-After` headers remain unchanged.

The JavaScript upload fixture is pinned to CRLF by `test_files/.gitattributes`
because deployment reads and base64-encodes its raw bytes. This preserves the
recorded payload on both Linux and Windows; an offline check compares the JS/ZIP
fixture bytes with their recorded requests.

From the repository root, in an activated Azure CLI development environment:

```powershell
azdev test azext_edge_action --discover --series
```

Measure command and argument coverage separately:

```powershell
azdev cmdcov edge-action
azdev cmdcov edge-action --level argument
```

The argument report measures scenario-source/recording coverage, not all unit
tests. Download output and the three list commands' `--max-items`/`--next-token`
behavior are covered by local unit tests. The report also includes CLI-wide
`--change-reference` and `--acquire-policy-token` arguments, whose policy-token
workflow is outside this extension's service scenarios. Do not describe the raw
argument percentage as complete live coverage or add unrelated policy resources
just to increase it.

For a direct offline run without installing the extension:

```powershell
$env:PYTHONPATH = (Resolve-Path .\src\edge-action).Path
python -m unittest azext_edge_action.tests.latest.test_edge_action_custom -v
```

Recording loading uses PyYAML,
which is already part of the Azure CLI test environment.

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
Re-record affected scenarios whenever their HTTP interactions change, including
execution-filter named-field updates, generic options, and cleanup. Assertion-only
changes can be checked against fresh recordings of the same interactions.
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

References:
[Azure CLI test guidance](https://github.com/Azure/azure-cli/blob/dev/doc/authoring_tests.md),
[AAZ generation](https://azure.github.io/aaz-dev-tools/pages/usage/cli-generator/),
[EdgeActions Python tests](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/edgeactions/azure-mgmt-edgeactions/tests),
and [EdgeAction PowerShell tests](https://github.com/Azure/azure-powershell/tree/main/src/EdgeAction/EdgeAction.Autorest/test).
