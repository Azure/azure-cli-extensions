# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['acr cache'] = """
type: group
short-summary: Manage cache rules in Azure Container Registries.
"""

helps['acr cache show'] = """
type: command
short-summary: Show a cache rule.
examples:
  - name: Show a cache rule.
    text: az acr cache show -r myregistry -n MyRule
"""

helps['acr cache list'] = """
type: command
short-summary: List the cache rules in an Azure Container Registry.
examples:
  - name: List the cache rules in an Azure Container Registry.
    text: az acr cache list -r myregistry
"""

helps['acr cache create'] = """
type: command
short-summary: Create a cache rule.
examples:
  - name: Create a cache rule without a credential set.
    text: az acr cache create -r myregistry -n MyRule -s docker.io/library/ubuntu -t ubuntu
  - name: Create a cache rule with a credential set.
    text: az acr cache create -r myregistry -n MyRule -s docker.io/library/ubuntu -t ubuntu -c MyCredSet
  - name: Create a cache rule with artifact sync enabled and set a tag filter.
    text: az acr cache create -r myregistry -n MyRule -s docker.io/library/ubuntu -t ubuntu --sync true --starts-with v1 --ends-with beta
"""

helps['acr cache update'] = """
type: command
short-summary: Update the credential set on a cache rule.
examples:
  - name: Change or add a credential set to an existing cache rule.
    text: az acr cache update -r myregistry -n MyRule -c NewCredSet
  - name: Remove a credential set from an existing cache rule.
    text: az acr cache update -r myregistry -n MyRule --remove-cred-set
  - name: Enable artifact sync and set a tag filter.
    text: az acr cache update -r myregistry -n MyRule --sync true --starts-with v1 --ends-with beta
"""

helps['acr cache delete'] = """
type: command
short-summary: Delete a cache rule.
examples:
  - name: Delete a cache rule.
    text: az acr cache delete -r myregistry -n MyRule
"""

helps['acr cache sync'] = """
type: command
short-summary: Sync a tag immediately. Artifact sync must be enabled on the cache rule and the tag must be within any specified tag filter.
examples:
  - name: Sync the 'latest' tag.
    text: az acr cache sync -r myregistry -n MyRule --image latest
"""
