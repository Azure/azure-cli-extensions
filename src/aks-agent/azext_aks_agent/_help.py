# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
from knack.help_files import helps

helps[
    "aks agent"
] = """
    type: command
    short-summary: Run AI assistant to analyze and troubleshoot Azure Kubernetes Service (AKS) clusters.
    long-summary: |-
      This command allows you to ask questions about your Azure Kubernetes cluster and get answers using AI models.

      Prerequisites:
      - Run 'az aks agent-init' first to configure the LLM provider and deployment mode
      - For client mode: Docker must be installed and running
    parameters:
        - name: --name -n
          type: string
          short-summary: Name of the managed cluster.
        - name: --resource-group -g
          type: string
          short-summary: Name of the resource group.
        - name: --model
          type: string
          short-summary: Specify the LLM provider and model or deployment to use for the AI assistant.
          long-summary: |-
            The --model parameter determines which large language model (LLM) and provider will be used to analyze your cluster.
            For OpenAI, use the model name directly (e.g., gpt-4o).
            For Azure OpenAI, use `azure/<deployment name>` (e.g., azure/gpt-4.1).
            Each provider may require different environment variables and model naming conventions.
            For a full list of supported providers, model patterns, and required environment variables, see https://docs.litellm.ai/docs/providers.
            Note: For Azure OpenAI, it is recommended to set the deployment name as the model name until https://github.com/BerriAI/litellm/issues/13950 is resolved.
        - name: --max-steps
          type: int
          short-summary: Maximum number of steps the LLM can take to investigate the issue.
        - name: --no-interactive
          type: bool
          short-summary: Disable interactive mode. When set, the agent will not prompt for input and will run in batch mode.
        - name: --no-echo-request
          type: bool
          short-summary: Disable echoing back the question provided to AKS Agent in the output.
        - name: --show-tool-output
          type: bool
          short-summary: Show the output of each tool that was called during the analysis.
        - name: --refresh-toolsets
          type: bool
          short-summary: Refresh the toolsets status.
        - name: --status
          type: bool
          short-summary: Show AKS agent deployment status including helm release, deployments, and pod information.
        - name: --namespace
          type: string
          short-summary: The Kubernetes namespace where the AKS Agent is deployed. Required for cluster mode.
        - name: --mode
          type: string
          short-summary: The mode decides how the agent is deployed.
          long-summary: |-
            The agent can be deployed in two modes:
            - cluster mode: Deploys AKS agent as a Helm release on the cluster with managed aks-mcp instance
            - client mode: Configures agent to run locally in a Docker container
            Default is 'cluster' mode.
    examples:
        - name: Ask about pod issues in the cluster with OpenAI
          text: |-
            az aks agent "Why are my pods not starting?" --model gpt-4o --resource-group myResourceGroup --name myAKSCluster
        - name: Ask about pod issues in the cluster with last configured model
          text: |-
            az aks agent "Why are my pods not starting?" --resource-group myResourceGroup --name myAKSCluster
        - name: Check AKS agent deployment status
          text: |-
            az aks agent --status --resource-group myResourceGroup --name myAKSCluster
        - name: Ask about pod issues in the cluster with Azure OpenAI
          text: |-
            az aks agent "Why are my pods not starting?" --model azure/gpt-4.1 --resource-group myResourceGroup --name myAKSCluster
        - name: Run in interactive mode without a question
          text: |-
            az aks agent "Check the pod status in my cluster" --model azure/gpt-4.1 --resource-group myResourceGroup --name myAKSCluster
        - name: Run in non-interactive batch mode
          text: |-
            az aks agent "Diagnose networking issues" --no-interactive --max-steps 15 --model azure/gpt-4.1 --resource-group myResourceGroup --name myAKSCluster
        - name: Show detailed tool output during analysis
          text: |-
            az aks agent "Why is my service workload unavailable in namespace workload-ns?" --show-tool-output --model azure/gpt-4.1 --resource-group myResourceGroup --name myAKSCluster
        - name: Run agent with no echo of the original question
          text: |-
            az aks agent "What is the status of my cluster?" --no-echo-request --model azure/gpt-4.1 --resource-group myResourceGroup --name myAKSCluster
        - name: Refresh toolsets to get the latest available tools
          text: |-
            az aks agent "What is the status of my cluster?" --refresh-toolsets --model azure/gpt-4.1 --resource-group myResourceGroup --name myAKSCluster
"""

helps[
    "aks agent-init"
] = """
    type: command
    short-summary: Initialize and validate LLM provider/model configuration for AKS agent.
    long-summary: |-
      This command interactively guides you to select an LLM provider and model, validates the connection, and saves the configuration for later use.
      You can run this command multiple times to add or update different model configurations.

      The command supports two deployment modes:
      - cluster mode: Deploys AKS agent as a Helm release on the cluster with managed aks-mcp instance
      - client mode: Configures agent to run locally in a Docker container

      Note: Configuration is required before running 'az aks agent'. The agent will validate that all necessary
      configuration files (model_list.yaml, custom_toolset.yaml) exist before execution.
    parameters:
        - name: --name -n
          type: string
          short-summary: Name of the managed cluster.
        - name: --resource-group -g
          type: string
          short-summary: Name of the resource group.
    examples:
        - name: Initialize and deploy AKS agent to a cluster
          text: |-
            az aks agent-init --resource-group myResourceGroup --name myAKSCluster
"""

helps[
    "aks agent-cleanup"
] = """
    type: command
    short-summary: Cleanup and uninstall AKS agent from the cluster.
    long-summary: |-
      This command removes the AKS agent and deletes all associated resources from the cluster.
    parameters:
        - name: --name -n
          type: string
          short-summary: Name of the managed cluster.
        - name: --resource-group -g
          type: string
          short-summary: Name of the resource group.
        - name: --namespace
          type: string
          short-summary: The Kubernetes namespace where the AKS Agent is deployed. Required for cluster mode.
        - name: --mode
          type: string
          short-summary: The mode decides how the agent is deployed.
          long-summary: |-
            The agent can be deployed in two modes:
            - cluster mode: Deploys AKS agent as a Helm release on the cluster with managed aks-mcp instance
            - client mode: Configures agent to run locally in a Docker container
            Default is 'cluster' mode.
    examples:
        - name: Cleanup and uninstall AKS agent from the cluster
          text: az aks agent-cleanup --resource-group myResourceGroup --name myAKSCluster
"""
