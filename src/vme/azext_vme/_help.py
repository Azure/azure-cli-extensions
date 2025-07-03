# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

# pylint: disable=line-too-long
helps['vme'] = """
    type: group
    short-summary: Commands to manage version managed extensions on connected kubernetes clusters.
"""

helps['vme install'] = """
    type: command
    short-summary: Install version managed extensions.
    examples:
      - name: Install all version managed extensions
        text: |-
          az vme install --resource-group my-resource-group --cluster-name my-cluster --include all
      - name: Install specific version managed extension
        text: |-
          az vme install --resource-group my-resource-group --cluster-name my-cluster --include microsoft.azure.secretstore
      - name: Enable feature flag and then install specific version managed extension
        text: |-
          az vme install --resource-group my-resource-group --cluster-name my-cluster --include microsoft.arc.containerstorage --kube-config /path/to/kubeconfig.yaml --kube-context my-context
"""

helps['vme uninstall'] = """
    type: command
    short-summary: Uninstall version managed extensions.
    examples:
      - name: Uninstall all version managed extensions
        text: |-
          az vme uninstall --resource-group my-resource-group --cluster-name my-cluster --include all
      - name: Uninstall specific version managed extension
        text: |-
          az vme uninstall --resource-group my-resource-group --cluster-name my-cluster --include microsoft.azure.secretstore
"""

helps['vme upgrade'] = """
    type: command
    short-summary: Check version managed extensions' upgrade status.
    examples:
      - name: Check version managed extensions' upgrade status
        text: |-
          az vme upgrade --resource-group my-resource-group --cluster-name my-cluster --wait
"""

helps['vme list'] = """
    type: command
    short-summary: List version managed extensions.
    examples:
      - name: List version managed extensions
        text: |-
          az vme list --resource-group my-resource-group --cluster-name my-cluster
      - name: List version managed extensions with table format
        text: |-
          az vme list --resource-group my-resource-group --cluster-name my-cluster --output table
"""
