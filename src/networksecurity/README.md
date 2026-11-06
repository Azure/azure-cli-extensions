# Azure CLI Network Security extension

This preview extension manages Microsoft.NetworkSecurity NeuroShield resources
using API version `2026-10-01-preview`. Azure CLI 2.75.0 or later is required.

The service is currently in private preview. Subscriptions must be enabled for
the `Microsoft.NetworkSecurity/NeuroShieldPreview` feature.

Command names are provisional pending CLI-team design review.

Inventory assessments and remediation require the `Microsoft.Azure.Networking`
`Neuron` VM extension, installed separately using the service-provided settings.
Its managed identity must be attached to the VM and match the protected-resource
registration. Creating a protected resource does not install the VM extension;
installing the VM extension does not register the protected resource.

## Usage

List NeuroShields in the current subscription:

```azurecli
az networksecurity neuroshield list
```

Get a NeuroShield:

```azurecli
az networksecurity neuroshield show --resource-group myResourceGroup --name myNeuroShield
```

List protected resources and aggregate findings:

```azurecli
az networksecurity neuroshield protected-resource list --resource-group myResourceGroup --neuro-shield-name myNeuroShield
az networksecurity neuroshield finding list --resource-group myResourceGroup --neuro-shield-name myNeuroShield
```

Use `--help` to explore management operations, finding mitigation and rollback,
mitigation execution and rollback, inventory uploads, summaries, operation status,
and provider operation discovery.

## Development

The `aaz` package is generated from the corresponding
[AAZ command models](https://github.com/Azure/aaz/tree/main/Commands/networksecurity).
Update those models and regenerate instead of editing generated commands.
The provider operation catalog is implemented in `custom.py` because AAZ
excludes provider operation discovery endpoints.