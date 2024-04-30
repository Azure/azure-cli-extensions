Microsoft Azure CLI 'acrabac' Extension
=======================================

The 'acrabac' extension is for private preview of an Azure Container Registry feature ABAC-based Repository Permission.


Usage
-----

The extension is to support ABAC-based Repository Permission when creating or updating Azure Container Registries.
ABAC-based Repository Permission allows granting role assignment permissions at the repository level through role assignment conditions.

The extension adds an extra parameter `--abac-permissions-enabled` to `az acr create` and `az acr update`.
Allowed values are `false`, `true`. Default is `false`.

### Examples

Create a registry with ABAC-based Repository Permission enabled:

```bash
az acr create -g $resource_group -n $acr_name --sku Basic --abac-permissions-enabled true --location $location
```

Turn on ABAC-based Repository Permission on an existing registry:

```bash
az acr update -g $resource_group -n $acr_name --abac-permissions-enabled true
```

Check status of ABAC-based Repository Permission on a registry:

```bash
az acr show -n $acr_name --query abacRepoPermission
```
