# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['k8sconfiguration'] = """
    type: group
    short-summary: Commands to manage K8sconfigurations.
"""

helps['k8sconfiguration create'] = """
    type: command
    short-summary: Create a K8sconfiguration.
    examples:
      - name: Create a k8sconfiguration
        text: |-
            az k8sconfiguration create --resource-group MyResourceGroup --cluster-name MyClusterName \\
            --cluster-type 'connectedClusters' --name MyConfigurationName --operator-instance-name OperatorInst01 \\
            --operator-namespace OperatorNamespace01 --repository-url git://github.com/fluxHowTo/flux-get-started \\
            --operator-params "'--git-readonly'" --enable-helm-operator --helm-operator-version 0.6.0 \\
            --helm-operator-params '--set helm.versions=v3'
"""

helps['k8sconfiguration list'] = """
    type: command
    short-summary: List K8sconfigurations.
    examples:
      - name: List all k8sconfigurations of a cluster
        text: |-
            az k8sconfiguration list --resource-group MyResourceGroup --cluster-name MyClusterName \\
            --cluster-type 'connectedClusters'
"""

helps['k8sconfiguration delete'] = """
    type: command
    short-summary: Delete a K8sconfiguration.
    examples:
      - name: Delete a k8sconfiguration
        text: |-
            az k8sconfiguration delete --resource-group MyResourceGroup --cluster-name MyClusterName \\
            --cluster-type 'connectedClusters' --name MyConfigurationName
"""

helps['k8sconfiguration show'] = """
    type: command
    short-summary: Show details of a K8sconfiguration.
    examples:
      - name: Show a k8sconfiguration
        text: |-
            az k8sconfiguration show --resource-group MyResourceGroup --cluster-name MyClusterName \\
            --cluster-type 'connectedClusters' --name MyConfigurationName
"""

helps['k8sconfiguration update'] = """
    type: command
    short-summary: Update a K8sconfiguration.
    examples:
      - name: Update an existing k8sconfiguration
        text: |-
            az k8sconfiguration update --resource-group MyResourceGroup --cluster-name MyClusterName \\
            --cluster-type 'connectedClusters' --name MyConfigurationName --enable-helm-operator \\
            --repository-url git://github.com/fluxHowTo/flux-get-started --operator-params "'--git-readonly'" \\
            --helm-operator-version 0.6.0 --helm-operator-params '--set helm.versions=v3'
"""
