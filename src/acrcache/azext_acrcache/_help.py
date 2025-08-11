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
long-summary: |
  NOTE: The parameters --platforms, --sync-referrers, --include-artifact-types, and --exclude-artifact-types are not yet implemented. Using any of these parameters will return a 'not implemented' error message.

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
    text: az acr cache create -r myregistry -n MyRule -s docker.io/library/ubuntu -t ubuntu --sync enable --starts-with v1 --ends-with beta
  - name: Create a cache rule with artifact sync enabled, set a tag filter, and specify platforms and sync referrers.
    text: az acr cache create -r myregistry -n MyRule -s docker.io/library/ubuntu -t ubuntu --sync enable --starts-with v1 --ends-with beta --platforms linux/amd64,linux/arm64 --sync-referrers enable
  - name: Create a cache rule with artifact sync enabled, set a tag filter, and specify  platforms, sync referrers and artifact types to include.
    text: az acr cache create -r myregistry -n MyRule -s docker.io/library/ubuntu -t ubuntu --sync enable --starts-with v1 --ends-with beta --platforms linux/amd64,linux/arm64 --sync-referrers enable --include-artifact-types application/vnd.cncf.notary.signature
  - name: Create a cache rule with artifact sync enabled, set a tag filter, and specify platforms, sync referrers and artifact types to exclude.
    text: az acr cache create -r myregistry -n MyRule -s docker.io/library/ubuntu -t ubuntu --sync enable --starts-with v1 --ends-with beta --platforms linux/amd64,linux/arm64 --sync-referrers enable --exclude-artifact-types application/vnd.cncf.helm.chart.v1.tar+gzip,application/vnd.aquasec.trivy.report+json
  - name: Create a cache rule with artifact sync enabled, set a tag filter, and specify platforms, sync referrers, artifact types to include and image types to include.
    text: az acr cache create -r myregistry -n MyRule -s docker.io/library/ubuntu -t ubuntu --sync enable --starts-with v1 --ends-with beta --platforms linux/amd64,linux/arm64 --sync-referrers enable --include-artifact-types application/vnd.aquasec.trivy.report+json,application/vnd.cncf.helm.chart.v1.tar+gzip --include-image-types docker.manifest.v2+json
  - name: Create a cache rule with artifact sync enabled, set a tag filter, and specify platforms, sync referrers, artifact types to exclude and image types to exclude.
    text: az acr cache create -r myregistry -n MyRule -s docker.io/library/ubuntu -t ubuntu --sync enable --starts-with v1 --ends-with beta --platforms linux/amd64,linux/arm64 --sync-referrers enable --exclude-artifact-types application/vnd.aquasec.trivy.vulnerability.report,application/vnd.aquasec.trivy.report+json --exclude-image-types application/vnd.oci.image.manifest.v1+json,application/vnd.oci.image.index.v1+json
"""

helps['acr cache update'] = """
type: command
short-summary: Update the credential set on a cache rule.
long-summary: |
  NOTE: The parameters --platforms, --sync-referrers, --include-artifact-types, and --exclude-artifact-types are not yet implemented. Using any of these parameters will return a 'not implemented' error message.

examples:
  - name: Change or add a credential set to an existing cache rule.
    text: az acr cache update -r myregistry -n MyRule -c NewCredSet
  - name: Remove a credential set from an existing cache rule.
    text: az acr cache update -r myregistry -n MyRule --remove-cred-set
  - name: Enable artifact sync and set a tag filter.
    text: az acr cache update -r myregistry -n MyRule --sync enable --starts-with v1 --ends-with beta
  - name: Enable artifact sync, set a tag filter, and specify platforms and sync referrers.
    text: az acr cache update -r myregistry -n MyRule --sync enable --starts-with v1 --ends-with beta --platforms linux/amd64,linux/arm64 --sync-referrers enable
  - name: Enable artifact sync, set a tag filter, and specify platforms, sync referrers and artifact types to include.
    text: az acr cache update -r myregistry -n MyRule --sync enable --starts-with v1 --ends-with beta --platforms linux/amd64,linux/arm64 --sync-referrers enable --include-artifact-types images,notary-project-signature
  - name: Enable artifact sync, set a tag filter, and specify platforms, sync referrers and artifact types to exclude.
    text: az acr cache update -r myregistry -n MyRule --sync enable --starts-with v1 --ends-with beta --platforms linux/amd64,linux/arm64 --sync-referrers enable --exclude-artifact-types application/vnd.aquasec.trivy.vulnerability.report
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
