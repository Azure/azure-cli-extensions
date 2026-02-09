# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import

helps['acr create'] = """
type: command
short-summary: Create an Azure Container Registry.
examples:
  - name: Create a managed container registry with the Standard SKU.
    text: >
        az acr create -n myregistry -g MyResourceGroup --sku Standard
  - name: Create a registry with ABAC-based Repository Permission enabled.
    text: >
        az acr create -n myregistry -g MyResourceGroup --sku Standard --role-assignment-mode rbac-abac
  - name: Create a managed container registry with the Premium SKU and regional endpoints enabled.
    text: >
        az acr create -n myregistry -g MyResourceGroup --sku Premium --regional-endpoints enabled
"""

helps['acr update'] = """
type: command
short-summary: Update an Azure Container Registry.
examples:
  - name: Update tags for an Azure Container Registry.
    text: >
        az acr update -n myregistry --tags key1=value1 key2=value2
  - name: Enable the administrator user account for an Azure Container Registry.
    text: >
        az acr update -n myregistry --admin-enabled true
  - name: Turn on ABAC-based Repository Permission on an existing registry.
    text: >
        az acr update -n myregistry --role-assignment-mode rbac-abac
  - name: Enable regional endpoints on an existing registry.
    text: >
        az acr update -n myregistry --regional-endpoints enabled
"""

helps['acr login'] = """
type: command
short-summary: Log in to an Azure Container Registry through the Docker CLI.
long-summary: Docker must be installed on your machine. Once done, use `docker logout <registry url>` to log out. (If you only need a refresh token and do not want to install Docker, specify '--expose-token')
examples:
  - name: Log in to an Azure Container Registry
    text: >
        az acr login -n myregistry
  - name: Get an Azure Container Registry access token
    text: >
        az acr login -n myregistry --expose-token
  - name: Log in to a specific regional endpoint of an Azure Container Registry
    text: >
        az acr login -n myregistry --endpoint eastus
"""

helps['acr show-endpoints'] = """
type: command
short-summary: Display registry endpoints including data endpoints and regional endpoints if configured.
examples:
  - name: Show the endpoints for a registry.
    text: >
        az acr show-endpoints -n myregistry
"""

helps['acr import'] = """
type: command
short-summary: Imports an image to an Azure Container Registry from another Container Registry. Import removes the need to docker pull, docker tag, docker push. For larger images consider using `--no-wait`.
examples:
  - name: Import an image from 'sourceregistry' to 'myregistry'. The image inherits its source repository and tag names.
    text: >
        az acr import -n myregistry --source sourceregistry.azurecr.io/sourcerepository:sourcetag
  - name: Import an image from a public repository on Docker Hub. The image uses the specified repository and tag names.
    text: >
        az acr import -n myregistry --source docker.io/library/hello-world:latest -t targetrepository:targettag
  - name: Import an image from a private repository using its username and password. This also applies to registries outside Azure.
    text: >
        az acr import -n myregistry --source myprivateregistry.azurecr.io/hello-world:latest -u username -p password
  - name: Import an image from an Azure container registry in a different subscription.
    text: |
        az acr import -n myregistry --source sourcerepository:sourcetag -t targetrepository:targettag \\
            -r /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/sourceResourceGroup/providers/Microsoft.ContainerRegistry/registries/sourceRegistry
  - name: Import an image without waiting for successful completion. Failures during import will not be reflected. Run `az acr repository show-tags` to confirm that import succeeded.
    text: >
        az acr import -n myregistry --source sourceregistry.azurecr.io/sourcerepository:sourcetag --no-wait
  - name: Import an image using a regional endpoint URI as the source.
    text: >
        az acr import -n myregistry --source sourceregistry.eastus.geo.azurecr.io/sourcerepository:sourcetag
"""
