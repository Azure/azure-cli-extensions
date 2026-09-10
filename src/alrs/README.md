# Azure Package Registry CLI extension

This preview extension manages Azure Package Registry resources and their
repository content.

Product and command naming are provisional while the service completes its
onboarding reviews.

## Command groups

- `az alrs registry`
- `az alrs repository`
- `az alrs repository release`
- `az alrs repository package`
- `az alrs package`
- `az alrs distro`
- `az alrs remote`
- `az alrs publication`
- `az alrs task`

Registry commands use the ARM control plane. Repository and package commands
use the registry data-plane endpoint returned by ARM.

## Installation

After publication:

```bash
az extension add --name alrs
az alrs --help
```
