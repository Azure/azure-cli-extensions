# Migrating an Azure CLI extension from `setup.py` to `pyproject.toml`

If you own an Azure CLI extension, either here in `src/<name>` or in your own repo, this is how you
move it off `setup.py` and onto a PEP 517 build.

Tracking issue: [Azure/azure-cli-extensions#7740](https://github.com/Azure/azure-cli-extensions/issues/7740)

## Why

- `pip` dropped legacy editable installs (`setup.py develop`), so `pip install -e` now needs a real
  build backend.
- We've been stuck on `wheel==0.30.0` since 2019, because the extension index was built from the
  `metadata.json` that only that version writes. The pin carries CVEs and blocks `setuptools`
  upgrades.
- Extension metadata now comes from `pkginfo` instead of `metadata.json`, so once extensions stop
  depending on `setup.py` the pin can go.

## Status

CI here accepts either `pyproject.toml` or `setup.py`, so there's no rush and nothing breaks while
both formats are in the tree. Don't add a `pyproject.toml` and leave `setup.py` as the actual build
definition though. Pick one.

## Template

Replace `<name>` with your extension name and `azext_<name>` with your package directory.

```toml
[build-system]
requires = ["setuptools>=70"]
build-backend = "setuptools.build_meta"

[project]
name = "<name>"
version = "1.0.0"
description = "Microsoft Azure Command-Line Tools <Name> Extension"
authors = [{ name = "Microsoft Corporation", email = "azpycli@microsoft.com" }]
license = { text = "MIT" }
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
]
dependencies = [
    # contents of the old install_requires / DEPENDENCIES list
]
dynamic = ["readme"]

[project.urls]
# Key must be "Home", not "Homepage". See "Metadata deltas" below.
Home = "https://github.com/Azure/azure-cli-extensions/tree/main/src/<name>"

[tool.setuptools.dynamic]
readme = { file = ["README.md", "HISTORY.rst"], content-type = "text/markdown" }

[tool.setuptools.packages.find]
include = ["azext_<name>*"]

[tool.setuptools.package-data]
azext_<name> = ["azext_metadata.json"]
```

Then delete `setup.py`.

## Field mapping

| `setup.py` | `pyproject.toml` |
| --- | --- |
| `name=` | `[project] name` |
| `VERSION` / `version=` | `[project] version` |
| `description=` | `[project] description` |
| `author=` / `author_email=` | `[project] authors` |
| `url=` | `[project.urls] Home` |
| `long_description=README + HISTORY` | `dynamic = ["readme"]` + `[tool.setuptools.dynamic] readme` |
| `license=` | `[project] license` |
| `classifiers=` | `[project] classifiers` |
| `install_requires=` | `[project] dependencies` |
| `extras_require=` | `[project.optional-dependencies]` |
| `packages=find_packages()` | `[tool.setuptools.packages.find] include` |
| `package_data=` | `[tool.setuptools.package-data]` |
| `cmdclass` from `azure_bdist_wheel` | delete it (see below) |

## Things that will bite you

**`azure_bdist_wheel` / `cmdclass`.** Many extensions carry this block:

```python
try:
    from azure_bdist_wheel import cmdclass
except ImportError:
    from distutils import log as logger
    logger.warn("Wheel is not available, disabling bdist_wheel hook")
```

Delete it. All it did was set a universal (`py2.py3`) wheel tag. Without it your wheel comes out
tagged `py3-none-any`, which is what you want anyway since extensions are Python 3 only.

**`setup.py` that imports its own package.** If your `setup.py` does
`from azext_<name>.something import ...` at module level, that import won't resolve under a default
(isolated) PEP 517 build, because your package isn't installed in the build environment. Inline the
values instead. Watch out for the pattern below in particular. It fails *silently*, so instead of an
error you get a wheel with no dependencies:

```python
DEPENDENCIES = []
try:
    from azext_<name>.manual.dependency import DEPENDENCIES
except ImportError:
    pass
```

**Non-Python files.** Everything you were shipping through `package_data` (`azext_metadata.json`,
bundled binaries, YAML templates, and so on) has to be listed under
`[tool.setuptools.package-data]`. `azext_metadata.json` is not optional; the extension index can't
be built without it.

**Building locally.** Run the build with the source directory as an argument, not by `cd`-ing into
it:

```bash
python -m build --wheel --outdir /tmp/out src/<name>     # correct
cd src/<name> && python -m build --wheel                 # breaks on the second run
```

`setuptools` leaves a `build/` directory behind in the extension folder. The current directory is on
`sys.path`, so that directory ends up shadowing the `build` module itself and every run after the
first one dies with `No module named build.__main__`.

## What changes in the metadata

We built the same extension both ways and diffed the wheels. The file lists came out identical, and
`name`, `version`, `summary`, `license`, `classifiers`, `run_requires` and `metadata_version` were
all unchanged. Two fields do move:

| Field | `setup.py` | `pyproject.toml` |
| --- | --- | --- |
| `description_content_type` | absent | `text/markdown` (or `text/x-rst`) |
| `contacts` | `{name: "Microsoft Corporation", email: "azpycli@microsoft.com"}` | `{email: "Microsoft Corporation <email@microsoft.com>"}` |

Both are expected. PEP 621 folds author name and email into a single field, and a content type is
required for PyPI metadata 2.1+. Anyone reviewing `src/index.json` should know to expect them.

One detail worth copying: use `Home` rather than `Homepage` in `[project.urls]`. `Home` keeps
`project_urls` byte-identical to the old output, whereas `Homepage` changes the key and churns the
index entry for no reason.

## Verifying your migration

Build the wheel before and after, then compare:

```python
import zipfile
z_old = zipfile.ZipFile("old.whl")
z_new = zipfile.ZipFile("new.whl")
print("missing from new:", sorted(set(z_old.namelist()) - set(z_new.namelist())))
```

Anything in the old wheel that's missing from the new one is a regression. It's nearly always a
`package_data` entry you forgot to carry over.

Then check the extension still installs and loads:

```bash
azdev extension build <name>
az extension add --source <path-to-wheel>
az extension show -n <name>
az <your-command-group> --help
```

## Checklist

- [ ] `pyproject.toml` added, `setup.py` deleted
- [ ] `azure_bdist_wheel` / `cmdclass` block removed
- [ ] No build-time imports of your own `azext_*` package
- [ ] `azext_metadata.json` listed in `[tool.setuptools.package-data]`
- [ ] All other non-Python payload listed in `package-data`
- [ ] Old and new wheel file lists compared, nothing missing
- [ ] `az extension add` from the built wheel works and the commands load
- [ ] Extension version left alone (repackaging on its own shouldn't publish a new version)

## Questions

Open an issue on [Azure/azure-cli-extensions](https://github.com/Azure/azure-cli-extensions/issues)
and reference [#7740](https://github.com/Azure/azure-cli-extensions/issues/7740).
