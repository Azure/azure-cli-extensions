Microsoft Azure CLI 'acrcache' Extension
==========================================

## Overview
.
The `acrcache` extension adds support for managing Azure Container Registry (ACR) cache rules via the Azure CLI. 

## Features

- Create, update, list, show, and delete cache rules for ACR.
- **Managed Identity Authentication**: Configure user-assigned managed identities for secure cross-registry authentication.
  - **--assign-identity**: Specify a user-assigned managed identity for authenticating with source registries.
- Configure artifact sync with flexible filters:
  - **--platforms**: Filter which platforms to sync (e.g., `linux/amd64`, `linux/arm64`).
  - **--sync-referrers**: Enable or disable syncing of referrers.
  - **--include-artifact-types**: Specify artifact types to include in sync.
  - **--exclude-artifact-types**: Specify artifact types to exclude from sync.
  - **--include-image-types**: Specify image types to include in sync.
  - **--exclude-image-types**: Specify image types to exclude from sync.

## Installation

### Prerequisites
1. Install Python (minimum supported version is 3.6; Python 3.12 is recommended) from http://python.org.
2. Fork and clone the required repo's
    - Azure CLI Repo : https://github.com/Azure/azure-cli  
    - Azure CLI Extensions Repo : https://github.com/AzureCR/azure-cli-extensions. 

- Note: ACR cache extension is in feature/artifactcache branch.

    After forking `azure-cli`, follow the below commands to setup

    # Clone your forked repository

    git clone https://github.com/<your-github-name>/azure-cli.git

    cd azure-cli

    # Add the Azure/azure-cli repository as upstream

    git remote add upstream https://github.com/Azure/azure-cli.git

    git fetch upstream

    # Reset the default dev branch to track dev branch of Azure/azure-cli so you can use it to track the latest azure-cli code.

    git branch dev --set-upstream-to upstream/dev

    # Develop with a new branch

    git checkout -b <feature_branch>

  Do the same for `azure-cli-extensions` except that the default branch for it is main, run git branch main --set-upstream-to upstream/main instead.
  Note: The ACR cache extension is in the `feature/artifactcache` branch of the `azure-cli-extensions` repository, do NOT merge changes into main.

3. Create a virtual environment in the directory that contains both your CLI and CLI extension clones

    ```sh
    python -m venv .venv
    ```
4. Activate the virtual environment

    Windows CMD.exe:

    `.venv\Scripts\activate.bat`

    Windows Powershell:

    `.venv\Scripts\activate.ps1`

    OSX/Linux (bash):

    `source .venv/bin/activate`

5. Install the required packages
    Install python dependencies
      ```sh
      python -m pip install -U pip
      ```
      Due to a known issue, the Azure CLI currently requires an older version of setuptools (70.0.0) and wheel (0.30.0) because newer versions are incompatible and may cause installation or build failures. For more details, see the related issue: https://github.com/Azure/azure-cli/issues/29467
     
      pip install setuptools==70.0.0 	

      pip install --force-reinstall wheel==0.30.0

    Install azdev
      ```sh
      pip install -U azdev
      ```

    Setup azdev
      azdev setup -c -r azure-cli-extensions/

    Build extension
      azdev extension build acrcache

Developing with the ACR Cache Extension
==========================================  

Please write the description of changes which can be perceived by customers into HISTORY.rst.

If you want to release a new extension version, please update the version in setup.py as well.

If you make changes to the extension, you can test it by running:

azdev extension build "acrcache"

this will build your new changes into the extension package which you will see immediately.

## Usage

### List cache rules

```sh
az acr cache list -r <registry-name>
```

### Create a cache rule

#### Basic cache rule (pull-through cache)
```sh
az acr cache create -r <registry-name> -n <rule-name> -s <source-repo> -t <target-repo>
```

#### Cache rule with credential set
```sh
az acr cache create -r <registry-name> -n <rule-name> -s <source-repo> -t <target-repo> -c <credential-set>
```

#### Cache rule with user-assigned managed identity (ACR-to-ACR authentication)
```sh
az acr cache create -r <registry-name> -n <rule-name> -s <upstream-acr>.azurecr.io/<source-repo> -t <target-repo> \
  --assign-identity /subscriptions/<subscription-id>/resourceGroups/<resource-group>/providers/Microsoft.ManagedIdentity/userAssignedIdentities/<identity-name>
```

#### Advanced cache rule with artifact sync and filtering
```sh
az acr cache create -r <registry-name> -n <rule-name> -s <source-repo> -t <target-repo> \
  --sync activesync --platforms linux/amd64,linux/arm64 --sync-referrers enabled \
  --include-artifact-types images,notary-project-signature
```

### Update a cache rule

#### Update credential set
```sh
az acr cache update -r <registry-name> -n <rule-name> -c <new-credential-set>
```

#### Update with managed identity
```sh
az acr cache update -r <registry-name> -n <rule-name> \
  --assign-identity /subscriptions/<subscription-id>/resourceGroups/<resource-group>/providers/Microsoft.ManagedIdentity/userAssignedIdentities/<identity-name>
```

#### Update sync settings and filters
```sh
az acr cache update -r <registry-name> -n <rule-name> --sync activesync --platforms linux/amd64 \
  --sync-referrers enabled --include-artifact-types images
```

#### Remove credential set
```sh
az acr cache update -r <registry-name> -n <rule-name> --remove-cred-set
```

### Show a cache rule

```sh
az acr cache show -r <registry-name> -n <rule-name>
```

### Sync a specific tag immediately

```sh
az acr cache sync -r <registry-name> -n <rule-name> --image <tag>
```

### Delete a cache rule

```sh
az acr cache delete -r <registry-name> -n <rule-name>
```

## Authentication Methods

### User-Assigned Managed Identity

The `--assign-identity` parameter enables secure authentication between Azure Container Registries using user-assigned managed identities. This is particularly useful for:

- **Cross-subscription ACR caching**: Cache images from ACRs in different subscriptions
- **Cross-tenant scenarios**: Secure authentication across Azure AD tenants
- **Enhanced security**: Eliminates the need for credential sets in many scenarios

#### Requirements
- Both source and target registries must be in the same Azure AD tenant
- The managed identity must have `AcrPull` permissions on the source registry
- The managed identity must be in the same subscription as the target registry

#### Resource ID Format
```
/subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identity-name}
```

#### Example Setup
1. Create a user-assigned managed identity
2. Assign `AcrPull` role to the identity on the source registry
3. Create cache rule with the identity resource ID

```sh
# Create managed identity
az identity create -g <resource-group> -n <identity-name>

# Assign AcrPull permissions to source registry
az role assignment create --assignee <identity-principal-id> --role AcrPull --scope <source-registry-id>

# Create cache rule with managed identity
az acr cache create -r <target-registry> -n <rule-name> -s <source-registry>.azurecr.io/<repo> -t <target-repo> \
  --assign-identity /subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.ManagedIdentity/userAssignedIdentities/<identity-name>
```

## Artifact Sync and Filtering

### Sync Modes
- **PassiveSync** (default): Pull-through cache behavior - images are cached when pulled
- **ActiveSync**: Proactive synchronization - images are automatically pulled and cached

### Important Notes
- **--sync-referrers enabled** requires **--sync activesync**
- Artifact filtering parameters (--platforms, --include-artifact-types, etc.) require **--sync activesync**
- Tag filters (--starts-with, --ends-with, --contains) require **--sync activesync**

## Minimum Azure CLI Version

This extension requires Azure CLI version **2.57.0** or higher.

## Documentation

For more details, see the official [Azure CLI documentation](https://learn.microsoft.com/cli/azure/acr).


