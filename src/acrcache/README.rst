Microsoft Azure CLI 'acrcache' Extension
==========================================

## Overview
.
The `acrcache` extension adds support for managing Azure Container Registry (ACR) cache rules via the Azure CLI. 

## Features

- Create, update, list, show, and delete cache rules for ACR.
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
    - Azure CLI Extensions Repo : https://github.com/AzureCR/azure-cli-extensions. Note: ACR cache extension is in feature/artifactcache branch.

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

```sh
az acr cache create -r <registry-name> -n <rule-name> -s <source-repo> -t <target-repo> \
  --sync true --platforms linux/amd64,linux/arm64 --sync-referrers enabled \
  --include-artifact-types images,notary-project-signature --exclude-image-types <image-types>
```sh
az acr cache list -r <registry-name>
az acr cache list -r <registry-name>
```

### Create a cache rule

```sh
az acr cache create -r <registry-name> -n <rule-name> -s <source-repo> -t <target-repo> \
  --sync true --platforms linux/amd64,linux/arm64 --sync-referrers enabled \
  --include-artifact-types images,notary-project-signature --exclude-image-types <image-types>
```

### Update a cache rule

```sh
az acr cache update -r <registry-name> -n <rule-name> --platforms linux/amd64 --sync-referrers disabled \
  --include-artifact-types images --exclude-artifact-types <image-types>
```

### Show a cache rule

```sh
az acr cache show -r <registry-name> -n <rule-name>
```

### Delete a cache rule

```sh
az acr cache delete -r <registry-name> -n <rule-name>
```

## Minimum Azure CLI Version

This extension requires Azure CLI version **2.57.0** or higher.

## Documentation

For more details, see the official [Azure CLI documentation](https://learn.microsoft.com/cli/azure/acr).


