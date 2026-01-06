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
  - name: Create a registry with regional endpoints enabled.
    text: >
        az acr create -n myregistry -g MyResourceGroup --sku Premium --enable-regional-endpoints true
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
        az acr update -n myregistry --enable-regional-endpoints true
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
  - name: Log in to all endpoints of an Azure Container Registry
    text: >
        az acr login -n myregistry --all-endpoints
"""
