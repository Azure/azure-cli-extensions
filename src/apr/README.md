# Azure Package Registry CLI extension

This preview extension manages Azure Package Registry resources and their
repository content.

## Command groups

- `az apr registry`
- `az apr repository`
- `az apr repository release`
- `az apr repository package`
- `az apr package`
- `az apr distro`
- `az apr remote`
- `az apr publication`
- `az apr task`

Registry commands use the ARM control plane. Repository and package commands
use the registry data-plane endpoint returned by ARM.

## Installation

After publication:

```bash
az extension add --name apr
az apr --help
```
