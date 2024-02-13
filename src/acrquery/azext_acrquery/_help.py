# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps


helps['acr'] = """
    type: group
    short-summary: KQL querying against ACR content.
"""

helps['acr query'] = """
    type: command
    short-summary: Query the content in an ACR using Kusto Query Language.
    long-summary: Query for artifacts and images in an Azure Container Registry using the Kusto Query Language. OCI manifest properties such as digest, subject, annotations, etc. can be used to query, filter, and order search results.
    examples:
        - name: Fetch a single manifest
          text: az acr query -n $MyRegistry -q "Manifests | limit 1"

        - name: Count all manifests in repository $RepositoryName
          text: az acr query -n $MyRegistry -q "Manifests" -o table

        - name: List all manifests in repository $RepositoryName in order of creation date
          text: az acr query -n $MyRegistry --repository $RepositoryName -q "Manifests | order by createdAt desc"

        - name: Query for all digests signed by $Signature in the repository $RepositoryName
          text: az acr query -n $MyRegistry --repository $RepositoryName -q "Manifests | where annotations['org.cncf.notary.signature.subject'] == $Signature | project createdAt, digest, subject"

        - name: Query for the digests in a registry using a skip token and sort by digest (for results with pagination)
          text: az acr query -n $MyRegistry -q "Manifests | project digest | order by digest asc" --skip-token eyAibm8iOiAibHVjayIsICJidXQiOiAibmljZSIsICJ0cnkiOiAiISIgfQ==
"""
