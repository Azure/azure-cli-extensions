# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps


helps['aks use-dev-spaces'] = """
    type: command
    short-summary: (PREVIEW) Use Azure Dev Spaces with a managed Kubernetes cluster.
    long-summary: "If needed, a Dev Spaces resource will be created and connected to the target cluster, and Dev Spaces commands will be installed on this machine."
    parameters:
        - name: --cluster-name -n
          type: string
          short-summary: Name of the target AKS cluster.
        - name: --resource-group -g
          type: string
          short-summary: Name of the target AKS cluster's resource group.
        - name: --space -s
          type: string
          short-summary: The isolated space in the cluster to develop in.
"""

helps['aks remove-dev-spaces'] = """
    type: command
    short-summary: (PREVIEW) Remove Azure Dev Spaces from a managed Kubernetes cluster.
    parameters:
        - name: --cluster-name -n
          type: string
          short-summary: Name of the target AKS cluster.
        - name: --resource-group -g
          type: string
          short-summary: Name of the target AKS cluster's resource group.
        - name: --yes -y
          type: bool
          short-summary: Do not prompt for confirmation.
"""
