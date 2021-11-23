# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import

helps['k8s-configuration'] = """
    type: group
    short-summary: Commands to manage resources from Microsoft.KubernetesConfiguration.
"""

helps['k8s-configuration create'] = """
    type: command
    short-summary: Create a Flux v1 Kubernetes configuration (This command is for Flux v1, to use the newer Flux v2, run "az k8s-configuration flux create").
    examples:
      - name: Create a Flux v1 Kubernetes configuration
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
    short-summary: List Flux v1 Kubernetes configurations (This command is for Flux v1, to use the newer Flux v2, run "az k8s-configuration flux list").
    examples:
      - name: List Flux v1 Kubernetes configuration
        text: |-
            az k8s-configuration list --resource-group MyResourceGroup --cluster-name MyClusterName \\
            --cluster-type connectedClusters
"""

helps['k8s-configuration delete'] = """
    type: command
    short-summary: Delete a Flux v1 Kubernetes configuration (This command is for Flux v1, to use the newer Flux v2, run "az k8s-configuration flux delete").
    examples:
      - name: Delete a Flux v1 Kubernetes configuration
        text: |-
            az k8s-configuration delete --resource-group MyResourceGroup --cluster-name MyClusterName \\
            --cluster-type connectedClusters --name MyConfigurationName
"""

helps['k8s-configuration show'] = """
    type: command
    short-summary: Show details of a Flux v1 Kubernetes configuration (This command is for Flux v1, to use the newer Flux v2, run "az k8s-configuration flux show").
    examples:
      - name: Show details of a Flux v1 Kubernetes configuration
        text: |-
            az k8s-configuration show --resource-group MyResourceGroup --cluster-name MyClusterName \\
            --cluster-type connectedClusters --name MyConfigurationName
"""

helps['k8s-configuration flux'] = """
    type: group
    short-summary: Commands to manage Flux v2 Kubernetes configurations.
"""

helps['k8s-configuration flux create'] = """
    type: command
    short-summary: Create a Kubernetes Flux v2 Configuration.
    examples:
      - name: Create a Kubernetes v2 Flux Configuration
        text: |-
          az k8s-configuration flux create --resource-group my-resource-group \\
          --cluster-name mycluster --cluster-type connectedClusters \\
          --name myconfig --scope cluster --namespace my-namespace \\
          --kind git --url https://github.com/Azure/arc-k8s-demo \\
          --branch main --kustomization name=my-kustomization
"""

helps['k8s-configuration flux update'] = """
    type: command
    short-summary: Update a Kubernetes Flux v2 Configuration.
    examples:
      - name: Update a Kubernetes v2 Flux Configuration
        text: |-
          az k8s-configuration flux update --resource-group my-resource-group \\
          --cluster-name mycluster --cluster-type connectedClusters --name myconfig \\
          --url https://github.com/Azure/arc-k8s-demo --branch main \\
          --kustomization name=my-kustomization path=./my/new-path
"""

helps['k8s-configuration flux list'] = """
    type: command
    short-summary: List Kubernetes Flux v2 Configurations.
    examples:
      - name: List all Kubernetes Flux v2 Configurations on a cluster
        text: |-
          az k8s-configuration flux list --resource-group my-resource-group \\
          --cluster-name mycluster --cluster-type connectedClusters
"""

helps['k8s-configuration flux show'] = """
    type: command
    short-summary: Show a Kubernetes Flux v2 Configuration.
    examples:
      - name: Show details of a Kubernetes Flux v2 Configuration
        text: |-
          az k8s-configuration flux show --resource-group my-resource-group \\
          --cluster-name mycluster --cluster-type connectedClusters --name myconfig
"""

helps['k8s-configuration flux delete'] = """
    type: command
    short-summary: Delete a Kubernetes Flux v2 Configuration.
    examples:
      - name: Delete an existing Kubernetes Flux v2 Configuration
        text: |-
          az k8s-configuration flux delete --resource-group my-resource-group \\
          --cluster-name mycluster --cluster-type connectedClusters --name myconfig
"""

helps['k8s-configuration flux kustomization'] = """
    type: group
    short-summary: Commands to manage Kustomizations associated with Flux v2 Kubernetes configurations.
"""

helps['k8s-configuration flux kustomization create'] = """
    type: command
    short-summary: Create a Kustomization associated with a Kubernetes Flux v2 Configuration.
    examples:
      - name: Create a Kustomization associated wiht a Kubernetes v2 Flux Configuration
        text: |-
          az k8s-configuration flux kustomization create --resource-group my-resource-group \\
          --cluster-name mycluster --cluster-type connectedClusters --name myconfig \\
          --kustomization-name my-kustomization-2 --path ./my/path --prune --force
"""

helps['k8s-configuration flux kustomization update'] = """
    type: command
    short-summary: Update a Kustomization associated with a Kubernetes Flux v2 Configuration.
    examples:
      - name: Update a Kustomization associated with a Kubernetes v2 Flux Configuration
        text: |-
          az k8s-configuration flux kustomization update --resource-group my-resource-group \\
          --cluster-name mycluster --cluster-type connectedClusters --name myconfig \\
          --kustomization-name my-kustomization --path ./my/new-path --prune --force
"""

helps['k8s-configuration flux kustomization list'] = """
    type: command
    short-summary: List Kustomizations associated with a Kubernetes Flux v2 Configuration.
    examples:
      - name: List all Kustomizations associated with a Kubernetes Flux v2 Configuration on a cluster
        text: |-
          az k8s-configuration flux kustomization list --resource-group my-resource-group \\
          --cluster-name mycluster --name myconfig --cluster-type connectedClusters
"""

helps['k8s-configuration flux kustomization show'] = """
    type: command
    short-summary: Show a Kustomization associated with a Flux v2 Configuration.
    examples:
      - name: Show details of a Kustomization associated with a Kubernetes Flux v2 Configuration
        text: |-
          az k8s-configuration flux kustomization show --resource-group my-resource-group \\
          --cluster-name mycluster --cluster-type connectedClusters --name myconfig \\
          --kustomization-name my-kustomization
"""

helps['k8s-configuration flux kustomization delete'] = """
    type: command
    short-summary: Delete a Kustomization associated with a Kubernetes Flux v2 Configuration.
    examples:
      - name: Delete an existing Kustomization associated with a Kubernetes Flux v2 Configuration
        text: |-
          az k8s-configuration flux kustomization delete --resource-group my-resource-group \\
          --cluster-name mycluster --cluster-type connectedClusters --name myconfig \\
          --kustomization-name my-kustomization
"""
