Microsoft Azure CLI 'acrabac' Extension
=======================================

The 'acrabac' extension is for private preview of an Azure Container Registry feature "ABAC-based Repository Permission".


Usage
-----

The extension is to support ABAC-based Repository Permission when creating or updating Azure Container Registries.
ABAC-based Repository Permission allows granting role assignment permissions at the repository level through role assignment conditions.

The extension adds an extra parameter `--role-assignment-mode` to `az acr create` and `az acr update`.
Allowed values are `LegacyRegistryPermissions`, `AbacRepositoryPermissions`. Default is `LegacyRegistryPermissions`.

### Examples

Create a registry with ABAC-based Repository Permission enabled:

```bash
az acr create -g $resource_group -n $acr_name --sku Basic --role-assignment-mode AbacRepositoryPermissions --location $location
```

Turn on ABAC-based Repository Permission on an existing registry:

```bash
az acr update -g $resource_group -n $acr_name --role-assignment-mode AbacRepositoryPermissions
```

Check status of ABAC-based Repository Permission on a registry:

```bash
az acr show -g $resource_group -n $acr_name --query roleAssignmentMode
```
