# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['k8s-configuration'] = """
    type: group
    short-summary: Commands to manage Kubernetes configuration.
"""

helps['k8s-configuration create'] = """
    type: command
    short-summary: Create a Kubernetes configuration.
    examples:
      - name: Create a Kubernetes configuration
        text: |-
            az k8s-configuration create --resource-group MyResourceGroup --cluster-name MyClusterName \\
            --cluster-type connectedClusters --name MyGitConfig --operator-instance-name OperatorInst01 \\
            --operator-namespace OperatorNamespace01 --operator-type flux --operator-params "'--git-readonly'" \\
            --repository-url git://github.com/fluxHowTo/flux-get-started --enable-helm-operator  \\
            --helm-operator-chart-version 1.4.0 --scope namespace --helm-operator-params '--set helm.versions=v3' \\
            --ssh-private-key '' --ssh-private-key-file '' --https-user '' --https-key '' \\
            --ssh-known-hosts '' --ssh-known-hosts-file ''
"""

helps['k8s-configuration list'] = """
    type: command
    short-summary: List Kubernetes configurations.
    examples:
      - name: List all Kubernetes configurations of a cluster
        text: |-
            az k8s-configuration list --resource-group MyResourceGroup --cluster-name MyClusterName \\
            --cluster-type connectedClusters
"""

helps['k8s-configuration delete'] = """
    type: command
    short-summary: Delete a Kubernetes configuration.
    examples:
      - name: Delete a Kubernetes configuration
        text: |-
            az k8s-configuration delete --resource-group MyResourceGroup --cluster-name MyClusterName \\
            --cluster-type connectedClusters --name MyConfigurationName
"""

helps['k8s-configuration show'] = """
    type: command
    short-summary: Show details of a Kubernetes configuration.
    examples:
      - name: Show a Kubernetes configuration
        text: |-
            az k8s-configuration show --resource-group MyResourceGroup --cluster-name MyClusterName \\
            --cluster-type connectedClusters --name MyConfigurationName
"""

helps['k8s-configuration update'] = """
    type: command
    short-summary: Update a Kubernetes configuration.
    examples:
      - name: Update an existing Kubernetes configuration
        text: |-
            az k8s-configuration update --resource-group MyResourceGroup --cluster-name MyClusterName \\
            --cluster-type connectedClusters --name MyConfigurationName --enable-helm-operator \\
            --repository-url git://github.com/fluxHowTo/flux-get-started --operator-params "'--git-readonly'" \\
            --helm-operator-chart-version 1.4.0 --helm-operator-params '--set helm.versions=v3'
"""
