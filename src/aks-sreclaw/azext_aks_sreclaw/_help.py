# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

helps[
    "aks claw"
] = """
    type: group
    short-summary: Commands to manage Openclaw-powered SREClaw in a managed Kubernetes cluster.
"""

helps[
    "aks claw create"
] = """
    type: command
    short-summary: Initialize and deploy SREClaw to an AKS cluster.
    long-summary: |-
      This command deploys the SREClaw helm chart to your AKS cluster and guides you through
      configuring an LLM provider. The command will prompt you to select an LLM provider
      (Azure OpenAI or OpenAI), enter model names and API credentials, validate the connection,
      and configure a Kubernetes service account.
    parameters:
        - name: --name -n
          type: string
          short-summary: Name of the managed cluster.
        - name: --resource-group -g
          type: string
          short-summary: Name of the resource group.
        - name: --namespace
          type: string
          short-summary: The Kubernetes namespace where SREClaw will be deployed.
          long-summary: Required parameter. Specify the namespace for SREClaw deployment.
        - name: --no-wait
          type: bool
          short-summary: Do not wait for the long-running operation to finish.
    examples:
        - name: Deploy SREClaw to kube-system namespace
          text: |-
            az aks claw create --resource-group myResourceGroup --name myAKSCluster --namespace kube-system
        - name: Deploy SREClaw without waiting for completion
          text: |-
            az aks claw create --resource-group myResourceGroup --name myAKSCluster --namespace my-namespace --no-wait
"""

helps[
    "aks claw delete"
] = """
    type: command
    short-summary: Delete and uninstall SREClaw from an AKS cluster.
    long-summary: |-
      This command uninstalls the SREClaw helm chart and deletes all associated resources
      from your AKS cluster, including secrets and configurations.
    parameters:
        - name: --name -n
          type: string
          short-summary: Name of the managed cluster.
        - name: --resource-group -g
          type: string
          short-summary: Name of the resource group.
        - name: --namespace
          type: string
          short-summary: The Kubernetes namespace where SREClaw is deployed.
          long-summary: Required parameter. Specify the namespace where SREClaw is deployed.
        - name: --no-wait
          type: bool
          short-summary: Do not wait for the long-running operation to finish.
    examples:
        - name: Delete SREClaw from kube-system namespace
          text: |-
            az aks claw delete --resource-group myResourceGroup --name myAKSCluster --namespace kube-system
        - name: Delete SREClaw without waiting for completion
          text: |-
            az aks claw delete --resource-group myResourceGroup --name myAKSCluster --namespace my-namespace --no-wait
"""

helps[
    "aks claw connect"
] = """
    type: command
    short-summary: Establish a port-forward connection to the SREClaw service.
    long-summary: |-
      This command creates a port-forward to the aks-sreclaw service, making it accessible
      on localhost. The command displays the gateway token needed for authentication and
      provides instructions to open the service in a browser. Press Ctrl+C to stop.
    parameters:
        - name: --name -n
          type: string
          short-summary: Name of the managed cluster.
        - name: --resource-group -g
          type: string
          short-summary: Name of the resource group.
        - name: --namespace
          type: string
          short-summary: The Kubernetes namespace where the aks-sreclaw service is deployed.
          long-summary: Required parameter. Specify the namespace where SREClaw is deployed.
        - name: --local-port
          type: int
          short-summary: Local port to use for port-forwarding.
          long-summary: Defaults to 18789 if not specified.
    examples:
        - name: Connect to SREClaw service on default port
          text: |-
            az aks claw connect --resource-group myResourceGroup --name myAKSCluster --namespace kube-system
        - name: Connect to SREClaw service on custom port
          text: |-
            az aks claw connect --resource-group myResourceGroup --name myAKSCluster --namespace kube-system --local-port 8080
"""

helps[
    "aks claw status"
] = """
    type: command
    short-summary: Display the status of the SREClaw deployment.
    long-summary: |-
      This command shows the current status of the SREClaw deployment including helm release
      status, deployment replica counts, pod status and readiness, and configured LLM providers
      with their models and API endpoints.
    parameters:
        - name: --name -n
          type: string
          short-summary: Name of the managed cluster.
        - name: --resource-group -g
          type: string
          short-summary: Name of the resource group.
        - name: --namespace
          type: string
          short-summary: The Kubernetes namespace where SREClaw is deployed.
          long-summary: Required parameter. Specify the namespace where SREClaw is deployed.
    examples:
        - name: Check SREClaw deployment status
          text: |-
            az aks claw status --resource-group myResourceGroup --name myAKSCluster --namespace kube-system
"""
