# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['acr query'] = """
    type: group
    short-summary: KQL querying against an ACR.
"""

helps['acr query'] = """
    type: command
    short-summary: KQL querying against an ACR.
    examples:
        - name: Query for all digests signed by $Signature in the registry
          text: az acr query -n MyRegistry -q "Manifests | where annotations['org.cncf.notary.signature.subject'] == $Signature | project createdAt, digest, subject, repository"

        - name: Query for all digests signed by $Signature in the repository $RepostioryName
          text: az acr query -n MyRegistry --repository $RepostioryName -q "Manifests | where annotations['org.cncf.notary.signature.subject'] == $Signature | project createdAt, digest, subject"

        - name: Query for all digests in a registry using pagination
          text: az acr query -n MyRegistry -q "Manifests | project digest | order by digest asc" --skip-token eyAibm8iOiAibHVjayIsICJidXQiOiAibmljZSIsICJ0cnkiOiAiISIgfQ==
"""

