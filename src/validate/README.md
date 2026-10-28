# Azure CLI `validate` extension

`az validate` checks Azure CLI commands without running them: command names, parameter names, required
parameters, and the values the parser can check (choices, numbers, `--query` expressions and similar).
It is meant for commands written by people, scripts or AI assistants, before anyone runs them.

It never runs the checked commands, never installs extensions, never signs in and never reads files named in
the checked commands.

## Install

```bash
az extension add --name validate
```

## Usage

```bash
# One or more commands, each as a single argument
az validate --command 'az group create -n MyResourceGroup -l westus' 'az group show -n MyResourceGroup'

# Every az command in a script file (.ps1 and .psm1 files are read as PowerShell, others as Bash)
az validate --file deploy.sh
az validate --file deploy.ps1

# Script text, and an explicit shell
az validate --script 'RG=MyResourceGroup; az group create -n $RG -l westus' --shell bash

# Also write the JSON result to a file
az validate --file deploy.sh --output-file result.json
```

| Parameter | Meaning |
| --- | --- |
| `--command -c` | One or more commands to check. |
| `--script -s` | Script text; every `az` command in it is checked. |
| `--file` | Path of a script file; every `az` command in it is checked. |
| `--shell` | `bash` or `powershell`. Default: `bash`, or `powershell` for a `--file` ending in `.ps1` or `.psm1`. |
| `--output-file` | Also write the result as JSON (UTF-8) to this file. The normal output is unchanged. |
| `--offline` | Never download published command metadata; use cached metadata only. |

Use exactly one of `--command`, `--script` and `--file`. The exit code is 0 whether or not the checked
commands are valid; read `status` in the result.

### Quoting

Pass each command as one argument, quoted for the shell you run `az validate` from. Inside a checked
command, write file arguments with a space (`--parameters @params.json`), not with `=`
(`--parameters=@params.json`). The Azure CLI expands `=@<existing file>` in `az validate`'s own arguments
before `az validate` runs, so the file's content would be checked instead of the reference.

## What is checked

- **Core commands** are parsed with the installed Azure CLI's own parser, so the result matches the
  installed version.
- **Commands from installed extensions** are parsed the same way; the extension's command table is loaded as
  `az <command> --help` would load it. If an installed extension needs access that `az validate` doesn't
  allow while it loads (for example, reading files outside the Azure CLI and Python directories), its
  commands come back `unchecked` (`InternalError`).
- **Commands from extensions that aren't installed** are checked against published command metadata,
  downloaded from the Azure CLI metadata stores and cached for 12 hours. This needs network access; with
  `--offline` or no network, such commands come back `unchecked`. Published metadata records parameter
  names, required parameters, choices and number types, but not whether a parameter without a type takes
  a value.
- **Core commands that an extension changes** (for example, a preview extension that adds parameters) are
  checked against both: an error that the extension resolves is reported as a `RequiresExtension` warning
  instead.
- **Placeholders** such as `<resource-group>`, `$RG`, `${RG}`, `"$(az ...)"` and `@file` count as valid
  values, and are listed in `placeholders`. Real values are checked normally.
- Configured defaults (`az config set defaults.group=...`) are ignored, so results don't depend on the
  machine.

It doesn't check whether resources exist, whether you have access, or rules that a command only applies when
it runs.

## Result

`-o json` returns one document:

```json
{
  "schemaVersion": "1.0",
  "status": "invalid",
  "isValid": false,
  "summary": {"commands": 1, "valid": 0, "invalid": 1, "unchecked": 0},
  "results": [
    {
      "index": 0, "line": 1, "column": 1, "status": "invalid",
      "commandName": "vm create", "source": "core",
      "parameters": ["--resource-group", "--name", "--image"],
      "errors": [
        {"code": "UnrecognizedArgument", "message": "Unrecognized arguments: --sizee.",
         "parameters": ["--sizee"], "suggestions": ["--size"]}
      ],
      "warnings": []
    }
  ],
  "versions": {"azureCli": "2.91.0", "validate": "1.0.0b1"}
}
```

- `status` is `valid`, `invalid` or `unchecked` (could not be checked; see `reason`). For the whole
  document, `invalid` wins, then `unchecked`.
- Each result has the input `index` and the 1-based `line` and `column` of the command in that input.
- `source` is `core` or `extension:<name>`; `requiresExtension` names an extension that isn't installed.
- `placeholders` lists `{parameter, placeholder}` for placeholder values.
- `notes` holds input-level findings (ignored non-`az` lines, unsupported shell syntax).
- Messages name parameters but never repeat the values from the checked command.

### Codes

| What to do | Codes |
| --- | --- |
| Find the right command | `UnknownCommand`, `MissingSubcommand`, `NotAzCommand` |
| Fix a parameter | `UnrecognizedArgument`, `AmbiguousArgument`, `MissingRequiredArgument`, `MissingValue`, `UnexpectedValue`, `MutuallyExclusiveArguments`, `InvalidValue`, `InvalidChoice`, `InvalidQuery`, `InvalidArgumentUsage` |
| Fix the shell syntax | `ShellSyntax`; warnings `UnquotedPlaceholder`, `UnquotedOperator` |
| Could not check (`unchecked`) | `ExtensionNotPublished`, `MetadataUnavailable`, `ExtensionIndexUnavailable`, `UnsupportedShellSyntax`, `PlaceholderCommandName`, `InternalError` |
| For information | `RequiresExtension`, `PromptsForConfirmation`, `DeprecatedArgument`, `DeprecatedCommand`, `Preview`, `PreviewArgument`, `Experimental`, `UpcomingBreakingChange`, `ExtensionOverridesCommand`, `ValueNotChecked`, `MetadataLimits`, `ExtensionNotInstalled`, `ExtensionGroup` |

## Shell support

Bash and PowerShell scripts are read, never run: variables, `$(...)` and other expansions are treated as
placeholders. `az` commands inside `$(...)`, backticks, assignments, pipelines, `if` and `case` blocks, and
loops are found and checked. Heredocs and here-strings, Bash process substitution (`<(...)`), and PowerShell
`@(...)` and `@{...}` literals, splatting and `--%` are not supported: a command that uses them comes back
`unchecked`, and other unsupported text is reported in `notes`.

## Limitations

- Only syntax and parameters are checked, not intent or Azure state.
- Extensions published outside this repository have no published metadata. Their commands come back
  `unchecked` unless the extension is installed.
- The `az validate` command itself may be installed automatically the first time it is used, like other
  extensions, if dynamic install is enabled.
