# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import

helps[
    "k8s-configuration"
] = """
    type: group
    short-summary: Commands to manage resources from Microsoft.KubernetesConfiguration.
"""

helps[
    "k8s-configuration list"
] = """
    type: command
    short-summary: List Flux v1 Kubernetes configurations (This command is for Flux v1, to use the newer Flux v2, run "az k8s-configuration flux list").
    examples:
      - name: List Flux v1 Kubernetes configuration
        text: |-
            az k8s-configuration list --resource-group MyResourceGroup --cluster-name MyClusterName \\
            --cluster-type connectedClusters
"""

helps[
    "k8s-configuration delete"
] = """
    type: command
    short-summary: Delete a Flux v1 Kubernetes configuration (This command is for Flux v1, to use the newer Flux v2, run "az k8s-configuration flux delete").
    examples:
      - name: Delete a Flux v1 Kubernetes configuration
        text: |-
            az k8s-configuration delete --resource-group MyResourceGroup --cluster-name MyClusterName \\
            --cluster-type connectedClusters --name MyConfigurationName
"""

helps[
    "k8s-configuration show"
] = """
    type: command
    short-summary: Show details of a Flux v1 Kubernetes configuration (This command is for Flux v1, to use the newer Flux v2, run "az k8s-configuration flux show").
    examples:
      - name: Show details of a Flux v1 Kubernetes configuration
        text: |-
            az k8s-configuration show --resource-group MyResourceGroup --cluster-name MyClusterName \\
            --cluster-type connectedClusters --name MyConfigurationName
"""

helps[
    "k8s-configuration flux"
] = """
    type: group
    short-summary: Commands to manage Flux v2 Kubernetes configurations.
"""

helps[
    "k8s-configuration flux create"
] = """
    type: command
    short-summary: Create a Flux v2 Kubernetes configuration.
    examples:
      - name: Create a Flux v2 Kubernetes configuration
        text: |-
          az k8s-configuration flux create --resource-group my-resource-group \\
          --cluster-name mycluster --cluster-type connectedClusters \\
          --name myconfig --scope cluster --namespace my-namespace \\
          --kind git --url https://github.com/Azure/arc-k8s-demo \\
          --branch main --kustomization name=my-kustomization
      - name: Create a Kubernetes v2 Flux Configuration with Bucket Source Kind
        text: |-
          az k8s-configuration flux create --resource-group my-resource-group \\
          --cluster-name mycluster --cluster-type connectedClusters \\
          --name myconfig --scope cluster --namespace my-namespace \\
          --kind bucket --url https://bucket-provider.minio.io \\
          --bucket-name my-bucket --kustomization name=my-kustomization \\
          --bucket-access-key my-access-key --bucket-secret-key my-secret-key
      - name: Create a Kubernetes v2 Flux Configuration with Azure Blob Source Kind
        text: |-
          az k8s-configuration flux create --resource-group my-resource-group \\
          --cluster-name mycluster --cluster-type connectedClusters \\
          --name myconfig --scope cluster --namespace my-namespace \\
          --kind azblob --url https://mystorageaccount.blob.core.windows.net \\
          --container-name my-container --kustomization name=my-kustomization \\
          --account-key my-account-key
"""

helps[
    "k8s-configuration flux update"
] = """
    type: command
    short-summary: Update a Flux v2 Kubernetes configuration.
    examples:
      - name: Update a Flux v2 Kubernetes configuration
        text: |-
          az k8s-configuration flux update --resource-group my-resource-group \\
          --cluster-name mycluster --cluster-type connectedClusters --name myconfig \\
          --url https://github.com/Azure/arc-k8s-demo --branch main \\
          --kustomization name=my-kustomization path=./my/new-path
      - name: Update a Flux v2 Kubernetes configuration with Bucket Source Kind to connect insecurely
        text: |-
          az k8s-configuration flux update --resource-group my-resource-group \\
          --cluster-name mycluster --cluster-type connectedClusters --name myconfig \\
          --bucket-insecure
      - name: Update a Flux v2 Kubernetes configuration with Azure Blob Source Kind with another container name
        text: |-
          az k8s-configuration flux update --resource-group my-resource-group \\
          --cluster-name mycluster --cluster-type connectedClusters --name myconfig \\
          --container-name other-container
"""

helps[
    "k8s-configuration flux list"
] = """
    type: command
    short-summary: List all Flux v2 Kubernetes configurations.
    examples:
      - name: List Flux v2 Kubernetes configurations on a cluster
        text: |-
          az k8s-configuration flux list --resource-group my-resource-group \\
          --cluster-name mycluster --cluster-type connectedClusters
"""

helps[
    "k8s-configuration flux show"
] = """
    type: command
    short-summary: Show a Flux v2 Kubernetes configuration.
    examples:
      - name: Show details of a Flux v2 Kubernetes configuration
        text: |-
          az k8s-configuration flux show --resource-group my-resource-group \\
          --cluster-name mycluster --cluster-type connectedClusters --name myconfig
"""

helps[
    "k8s-configuration flux delete"
] = """
    type: command
    short-summary: Delete a Flux v2 Kubernetes configuration.
    examples:
      - name: Delete an existing Flux v2 Kubernetes configuration
        text: |-
          az k8s-configuration flux delete --resource-group my-resource-group \\
          --cluster-name mycluster --cluster-type connectedClusters --name myconfig
"""

helps[
    "k8s-configuration flux kustomization"
] = """
    type: group
    short-summary: Commands to manage Kustomizations associated with Flux v2 Kubernetes configurations.
"""

helps[
    "k8s-configuration flux kustomization create"
] = """
    type: command
    short-summary: Create a Kustomization associated with a Flux v2 Kubernetes configuration.
    examples:
      - name: Create a Kustomization associated with a Flux v2 Kubernetes configuration
        text: |-
          az k8s-configuration flux kustomization create --resource-group my-resource-group \\
          --cluster-name mycluster --cluster-type connectedClusters --name myconfig \\
          --kustomization-name my-kustomization-2 --path ./my/path --prune --force
"""

helps[
    "k8s-configuration flux kustomization update"
] = """
    type: command
    short-summary: Update a Kustomization associated with a Flux v2 Kubernetes configuration.
    examples:
      - name: Update a Kustomization associated with a Flux v2 Kubernetes configuration
        text: |-
          az k8s-configuration flux kustomization update --resource-group my-resource-group \\
          --cluster-name mycluster --cluster-type connectedClusters --name myconfig \\
          --kustomization-name my-kustomization --path ./my/new-path --prune --force --disable-health-check
"""

helps[
    "k8s-configuration flux kustomization list"
] = """
    type: command
    short-summary: List Kustomizations associated with a Flux v2 Kubernetes configuration.
    examples:
      - name: List all Kustomizations associated with a Flux v2 Kubernetes configuration
        text: |-
          az k8s-configuration flux kustomization list --resource-group my-resource-group \\
          --cluster-name mycluster --name myconfig --cluster-type connectedClusters
"""

helps[
    "k8s-configuration flux kustomization show"
] = """
    type: command
    short-summary: Show a Kustomization associated with a Flux v2 Kubernetes configuration.
    examples:
      - name: Show details of a Kustomization associated with a Flux v2 Kubernetes configuration
        text: |-
          az k8s-configuration flux kustomization show --resource-group my-resource-group \\
          --cluster-name mycluster --cluster-type connectedClusters --name myconfig \\
          --kustomization-name my-kustomization
"""

helps[
    "k8s-configuration flux kustomization delete"
] = """
    type: command
    short-summary: Delete a Kustomization associated with a Flux v2 Kubernetes configuration.
    examples:
      - name: Delete an existing Kustomization associated with a Flux v2 Kubernetes configuration
        text: |-
          az k8s-configuration flux kustomization delete --resource-group my-resource-group \\
          --cluster-name mycluster --cluster-type connectedClusters --name myconfig \\
          --kustomization-name my-kustomization
"""

helps[
    "k8s-configuration flux deployed-object"
] = """
    type: group
    short-summary: Commands to see deployed objects associated with Flux v2 Kubernetes configurations.
"""

helps[
    "k8s-configuration flux deployed-object list"
] = """
    type: command
    short-summary: List deployed objects associated with a Flux v2 Kubernetes configuration.
    examples:
      - name: List all deployed objects associated with a Flux v2 Kubernetes configuration
        text: |-
          az k8s-configuration flux deployed-object list --resource-group my-resource-group \\
          --cluster-name mycluster --name myconfig --cluster-type connectedClusters
"""

helps[
    "k8s-configuration flux deployed-object show"
] = """
    type: command
    short-summary: Show a deployed object associated with a Flux v2 Kubernetes configuration.
    examples:
      - name: Show details of a deployed object associated with a Flux v2 Kubernetes configuration
        text: |-
          az k8s-configuration flux deployed-object show --resource-group my-resource-group \\
          --cluster-name mycluster --cluster-type connectedClusters --name myconfig \\
          --object-name my-object --object-namespace my-namespace --object-kind GitRepository
"""
