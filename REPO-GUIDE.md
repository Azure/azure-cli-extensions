# `azure-cli-extensions` — How This Repo Works

A practical orientation guide for someone new to the repo. Everything below was verified against
the current checkout; file paths and line references point at real code.

`aks-preview` is used as the worked example throughout, since that is where AKS / Azure Monitor
work lands.

---

## 1. What this repo actually is

Per `README.md`, the repo serves **two independent purposes**:

| Purpose | Location | What it is |
|---|---|---|
| Extension **source code** | `src/<extension-name>/` | 211 extension folders, each an installable Python wheel |
| The **extension index** | `src/index.json` | 6.5 MB catalogue of *published* wheels (220 extensions, 386 `aks-preview` versions) |

These are decoupled. `src/index.json` is what `az extension add --name <x>` reads (synced to
`https://aka.ms/azure-cli-extension-index-v1` every few minutes). A wheel can be indexed without
its source living here, and source can live here without being indexed.

> **Key mental model:** this repo does *not* ship the CLI itself. It ships **add-on command
> modules** that plug into `azure-cli` core at runtime. Core lives in the separate
> [`Azure/azure-cli`](https://github.com/Azure/azure-cli) repo, and you need a clone of it to
> develop here (see §5).

### Top-level layout

```
azure-cli-extensions/
├── src/                      # all extensions + index.json
│   ├── index.json            # published wheel catalogue (hash, version, metadata)
│   ├── service_name.json     # top-level command group → Azure service name + docs URL
│   │                         #   (checked by scripts/ci/service_name.py)
│   └── aks-preview/          # one extension
├── scripts/ci/               # index + release automation (update_index.py, test_index.py, ...)
├── scripts/automation/       # build_package.py, create_release_tag.py
├── .azure-pipelines/         # ADO templates (azdev_setup.yml, variables.yml)
├── azure-pipelines.yml       # the PR CI definition
├── .github/workflows/        # GitHub-side automation (release trigger, linter comments)
├── .github/CODEOWNERS        # per-extension reviewers
└── docs/                     # points at the canonical azure-cli authoring docs
```

---

## 2. Anatomy of a single extension

```
src/aks-preview/
├── setup.py                    # VERSION = "22.0.0b6"  ← the published version
├── setup.cfg                   # bdist_wheel config
├── HISTORY.rst                 # changelog; has a "Pending" section (see §6)
├── README.rst
├── linter_exclusions.yml       # per-extension linter waivers
├── azcli_aks_live_test/        # live-test harness (ADO pipelines + configs)
└── azext_aks_preview/          # ← the actual Python package that gets imported
    ├── azext_metadata.json     # minCliCoreVersion, isPreview flag
    ├── __init__.py             # COMMAND_LOADER_CLS — the entry point
    ├── commands.py             # command name → Python function mapping
    ├── _params.py              # CLI argument definitions
    ├── _help.py                # help text
    ├── _validators.py          # argument validation
    ├── _format.py              # table output transformers
    ├── _client_factory.py      # builds SDK clients  ← request plumbing
    ├── custom.py               # command implementations
    ├── managed_cluster_decorator.py   # builds the ManagedCluster request body
    ├── agentpool_decorator.py         # same, for node pools
    ├── vendored_sdks/          # generated ARM SDK (excluded from static checks)
    ├── aaz/                    # aaz-dev-tools generated commands
    └── tests/latest/           # tests + 289 HTTP recordings
```

The folder naming is a hard convention: directory `src/<name>/` contains package `azext_<name_with_underscores>/`.

---

## 3. The command flow — from `az` to ARM

This is the core thing to understand.

```
  $ az aks create -g rg -n mycluster --enable-addons monitoring
        │
        │  1. azure-cli core discovers installed extensions and calls COMMAND_LOADER_CLS
        ▼
  azext_aks_preview/__init__.py  →  ContainerServiceCommandsLoader
        │      load_command_table():
        │        a) load_aaz_command_table(...)   ← AAZ-generated commands first
        │        b) commands.load_command_table() ← handwritten ones, which OVERRIDE AAZ
        │      load_arguments()  →  _params.py
        ▼
  commands.py    g.custom_command("create", "aks_create", supports_no_wait=True)
        │        (inside a command_group bound to client_factory=cf_managed_clusters)
        ▼
  custom.py::aks_create        (line 1225)
        │      builds a decorator, then:
        │        mc = aks_create_decorator.construct_mc_profile_preview()   (line 1518)
        │        return aks_create_decorator.create_mc(mc)                   (line 1526)
        ▼
  managed_cluster_decorator.py :: AKSPreviewManagedClusterCreateDecorator  (line 4487)
        │      set_up_network_profile(mc), set_up_addon_profiles(mc),
        │      set_up_api_server_access_profile(mc), ...  ← one method per feature
        │      each mutates the ManagedCluster model object
        ▼
  put_mc()  (line 6336)
        │      self.client.begin_create_or_update(...)   (line 6342)
        │      or sdk_no_wait(...) when --no-wait        (line 6355)
        ▼
  vendored_sdks/azure_mgmt_preview_aks  →  ContainerServiceClient
        │      api_version = "2026-06-02-preview"   (_configuration.py:52)
        ▼
  HTTPS PUT to Azure Resource Manager
```

### 3a. Where requests are built — **two** distinct mechanisms

The repo mixes two generations of tooling. Knowing which one a command uses tells you where to edit.

#### Mechanism A — vendored SDK + decorators (handwritten; most of `aks-preview`)

1. **`vendored_sdks/`** holds an AutoRest/TypeSpec-generated ARM SDK. It is checked in
   deliberately, and `README.md` notes it is excluded from CI static checking precisely because
   generated code fails those checks. Two clients are vendored here:
   `azure_mgmt_preview_aks` and `azure_mgmt_preview_aks_pis`.

2. **`_client_factory.py`** registers those SDKs as CLI "custom resource types" and exposes one
   factory per operation group:

   ```python
   CUSTOM_MGMT_AKS_PREVIEW = CustomResourceType(
       'azext_aks_preview.vendored_sdks.azure_mgmt_preview_aks', 'ContainerServiceClient')

   def cf_managed_clusters(cli_ctx, *_):
       return get_container_service_client(cli_ctx).managed_clusters
   ```

   `commands.py` attaches these via `client_factory=cf_managed_clusters`, so the command
   implementation receives an authenticated, subscription-scoped client for free.

3. **Decorators build the request body.** For anything as large as `ManagedCluster`, the payload
   is assembled by an ordered chain of `set_up_*` / `update_*` methods, each owning exactly one
   feature. This is the pattern to follow when adding a flag:
   - add the argument in `_params.py`
   - add a `set_up_<feature>` (create) and `update_<feature>` (update) method in the decorator
   - call it from `construct_mc_profile_preview()` / `update_mc_profile_preview()` (line 9027)
   - the final `put_mc()` sends it

   Constants for feature names/addons live in `_consts.py`.

#### Mechanism B — AAZ (`aaz/`, generated by `aaz-dev-tools`)

Newer commands are **declarative and fully generated from the Swagger/TypeSpec spec** — no
handwritten SDK. Example: `aaz/latest/aks/safeguards/_show.py`.

Here the HTTP request is expressed directly as a class:

```python
class DeploymentSafeguardsGet(AAZHttpOperation):
    @property
    def url(self):            ...   # ARM template URL
    @property
    def method(self):         ...   # "GET"
    @property
    def url_parameters(self): ...   # subscriptionId, resourceGroupName, ...
    @property
    def query_parameters(self):
        return { "api-version", "2025-05-02-preview" }
    @property
    def header_parameters(self): ...
    def on_200(self, session):   ...  # response deserialization schema
```

Note each mechanism pins its **own** api-version (`2026-06-02-preview` for the vendored SDK,
`2025-05-02-preview` for this AAZ command). They are independent.

> ⚠️ Files under `aaz/` are marked `# Code generated by aaz-dev-tools` with `pylint: skip-file`.
> **Do not hand-edit them** — regenerate with `aaz-dev-tools`. To customize behaviour, use the
> `pre_operations()` / `post_operations()` hooks, or override the command in `commands.py`
> (remember the loader applies handwritten commands *after* AAZ, so they win).

---

## 4. Adding new API surface

When the AKS RP ships a new api-version and you need new fields:

1. **Regenerate / re-vendor the SDK** into `vendored_sdks/` (AutoRest or TypeSpec). The api-version
   default lives in `vendored_sdks/azure_mgmt_preview_aks/_configuration.py`.
2. **Expose the flag** in `_params.py` (+ `_validators.py`, `_help.py`, `_consts.py`).
3. **Wire the payload** in the relevant decorator (`managed_cluster_decorator.py` /
   `agentpool_decorator.py`).
4. **Register** the command in `commands.py` if it is new.
5. **Test** (§5) and **changelog** (§6).

`swagger_to_sdk_config.json` at the repo root drives spec→SDK automation.

---

## 5. Development cycle

### Setup (mirrors CI exactly — `.azure-pipelines/templates/azdev_setup.yml`)

```bash
python -m venv env && source env/bin/activate
pip install -U pip
pip install --upgrade azdev==0.2.13      # CI pins this exact version
pip install build wheel

git clone -q --single-branch -b dev https://github.com/Azure/azure-cli.git ../azure-cli
azdev setup -c ../azure-cli -r .          # -c = CLI core repo, -r = this repo
```

`azdev setup -r .` installs every extension in `src/` in editable mode, so edits take effect
immediately with no reinstall.

To work on just one extension:

```bash
azdev extension add aks-preview
az extension list            # confirm it resolves to your working tree
az aks create --help
```

### Inner loop

```bash
# edit code, then run it straight away — no build step needed
az aks create -g rg -n c1 --enable-addons monitoring --debug

# see the exact HTTP request/response ARM receives
az aks create ... --debug        # or --verbose
```

`--debug` is the fastest way to confirm your decorator actually put the field on the wire.

### Test

Tests are `ScenarioTest`-based and replay recorded HTTP traffic (289 recordings under
`src/aks-preview/azext_aks_preview/tests/latest/recordings/`).

```bash
azdev test aks-preview                                   # whole extension (playback)
azdev test aks-preview --live                            # hit real Azure, re-record
azdev test --src aks-preview test_aks_commands           # single module
pytest src/aks-preview/.../tests/latest/test_aks_commands.py -k mytest
```

Recording helpers live alongside the tests: `custom_preparers.py`, `recording_processors.py`
(scrubs secrets), `mocks.py`. Long-running end-to-end validation uses the separate
`azcli_aks_live_test/` ADO pipelines.

`pytest.ini` defines markers: `e2e_packaging`, `smoke`, `slow`.

### Lint / style — run these *before* pushing, they are enforced gates

```bash
azdev linter --include-whl-extensions aks-preview
azdev style aks-preview
azdev scan --include-whl-extensions aks-preview          # credential scan
```

Waivers go in `linter_exclusions.yml` (root and/or per-extension).

### Build a wheel locally

```bash
azdev extension build aks-preview        # emits dist/*.whl
az extension add --source dist/aks_preview-22.0.0b6-py3-none-any.whl --yes
```

---

## 6. Release & publish flow

### What you do in your PR

1. Add your entry to the **`Pending`** section of `HISTORY.rst`.
2. When releasing, promote `Pending` into a new numbered section and bump `VERSION` in `setup.py`
   (semver; `22.0.0b6` style for preview).
3. **Do not edit `src/index.json`** — automation owns it. `README.md` is explicit that the
   precondition for auto-publish is *bump the version but do not touch the index*.

`HISTORY.rst` states this guidance verbatim at the top of the file.

### What automation does

```
PR merged to main
   └─► .github/workflows/TriggerExtensionRelease.yml
          (OIDC login → az pipelines build queue → ADO OneBranch release pipeline)
              └─► builds the .whl, signs, uploads to the CDN/storage
                    └─► opens a follow-up PR updating src/index.json
                          (sha256 + metadata via scripts/ci/update_index.py)
                              └─► index syncs to aka.ms/azure-cli-extension-index-v1
                                    └─► `az extension add/update --name aks-preview` sees it
```

Supporting automation: `.github/workflows/CreateReleaseTag.yml`,
`scripts/automation/build_package.py`, `scripts/ci/idempotent_release.py`,
`scripts/ci/release_version_cal.py`.

Manual fallback (external-hosted wheels): `azdev extension update-index <URL-to-whl>` computes
the sha256 and writes the entry. Hashes must be **lowercase** or CI fails.

---

## 7. CI gates on every PR (`azure-pipelines.yml`)

| Job | What it enforces |
|---|---|
| `CredScan` | no secrets committed |
| `PolicyCheck` | Microsoft policy compliance |
| `CheckLicenseHeader` | MIT header on every source file |
| `CheckInit` | `__init__.py` present where required |
| `IndexVerify` | `src/index.json` well-formed, hashes match published wheels |
| `SourceTests` | integration + build tests across a Python matrix; publishes wheel artifacts |
| `AzdevStyleModifiedExtensions` | `azdev style` on changed extensions only |
| `AzdevLinterModifiedExtensions` | `azdev linter` on changed extensions only |
| `AzdevScanModifiedExtensions{High,Medium}` | credential scanning by confidence tier |
| `CheckExternalUrls` | external links resolve (`external_url_exclusions.json` waives) |

GitHub-side helpers post linter/style results as PR comments (`AddPRComment.yml`,
`AzdevLinter.yml`, `AzdevStyle.yml`) and `BlockPRMerge.yml` gates merges.

Review routing is `.github/CODEOWNERS`; `aks-preview` is owned by `@fumingzhang @elvazhu521`
(line 63), so any change under `src/aks-preview/` requires their approval.

---

## 8. Quick reference — "where do I change X?"

| I want to… | File |
|---|---|
| Add a CLI flag | `_params.py` |
| Validate a flag | `_validators.py` |
| Write help text / examples | `_help.py` |
| Register a new command | `commands.py` |
| Implement command logic | `custom.py` |
| Put a field on the ARM request body | `managed_cluster_decorator.py` / `agentpool_decorator.py` |
| Change which SDK/api-version is called | `_client_factory.py` + `vendored_sdks/.../_configuration.py` |
| Change table output | `_format.py` |
| Add a constant / addon name | `_consts.py` |
| Edit a generated command | ❌ regenerate `aaz/` with `aaz-dev-tools`; don't hand-edit |
| Record a changelog entry | `HISTORY.rst` → `Pending` |
| Bump the shipped version | `setup.py` → `VERSION` |
| Add an index entry | ❌ automation does it; don't hand-edit `src/index.json` |

---

## 9. Canonical upstream docs

`docs/README.md` intentionally defers to `Azure/azure-cli`:

- [Authoring an extension](https://github.com/Azure/azure-cli/blob/dev/doc/extensions/authoring.md)
- [Publishing](https://github.com/Azure/azure-cli/blob/dev/doc/extensions/authoring.md#publish)
- [Command guidelines](https://github.com/Azure/azure-cli/blob/dev/doc/command_guidelines.md)
- [Extension metadata](https://github.com/Azure/azure-cli/blob/dev/doc/extensions/metadata.md)
- [FAQ](https://github.com/Azure/azure-cli/blob/dev/doc/extensions/faq.md)
- [`azdev` tooling](https://github.com/Azure/azure-cli-dev-tools)
- [Migrating to `pyproject.toml`](docs/pyproject-migration.md)
