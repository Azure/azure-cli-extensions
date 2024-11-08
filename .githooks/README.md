# Git Hooks for Azure CLI Extension Development

## Setup

Please run the following command to enable the hooks.

```bash
git config --local core.hooksPath .githooks

azdev setup -c {azure_cli_repo_path} -r {azure_cli_extension_repo_path}
```

## Usage

Every time you git commit or git push, please make sure you have activated the python environment and completed the azdev setup.

If you want to skip the verification, you can add `--no-verify` to the git command.
