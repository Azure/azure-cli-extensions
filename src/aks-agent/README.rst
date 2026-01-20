Azure CLI AKS Agent Extension
===============================

Introduction
============


The AKS Agent extension provides the "az aks agent" command, an AI-powered assistant that helps analyze and troubleshoot Azure Kubernetes Service (AKS) clusters using Large Language Models (LLMs). The agent combines cluster context, configurable toolsets, and LLMs to answer natural-language questions about your cluster (for example, "Why are my pods not starting?") and can investigate issues in both interactive and non-interactive (batch) modes.

New in this version: **az aks agent-init** command for flexible agent deployment!

The `az aks agent-init` command supports two deployment modes:

- **Cluster mode**: Deploys the AKS agent as a Helm chart directly in your AKS cluster with enterprise-grade security (Kubernetes RBAC, workload identity, encrypted secrets)
- **Local mode**: Runs the AKS agent in a Docker container on your local machine with automatic credential and kubeconfig mounting

During initialization, you'll be prompted to:

- Choose between cluster or local deployment mode
- Configure your LLM provider and model interactively
- For cluster mode: specify namespace and service account for RBAC
- Validate connectivity and save the configuration

When asking questions with `az aks agent`:

- The agent automatically uses the last configured model
- Use `--model` to select a specific model when you have multiple models configured
- For local mode: Ensure Docker is installed and running

This architecture provides flexibility to choose between production-ready cluster deployment or convenient local troubleshooting workflows.

Key capabilities
----------------


- **Flexible Deployment**: Choose between cluster mode (Helm chart) or local mode (Docker container) with `az aks agent-init`.
- **Interactive Configuration**: Guided setup for deployment mode, namespace selection, and service account configuration.
- **Secure Access**: Cluster mode uses Kubernetes RBAC for cluster resources and Azure workload identity for Azure resources.
- **LLM Configuration**: Interactively configure LLM models with credentials stored securely (Kubernetes secrets for cluster mode, local files for local mode).
- Support for multiple LLM providers (Azure OpenAI, OpenAI, Anthropic, Gemini, etc.).
- Automatically uses the last configured model by default.
- Optionally use --model to select a specific model when you have multiple models configured.
- Interactive and non-interactive modes (use --no-interactive for batch runs).
- Control echo and tool output visibility with --no-echo-request and --show-tool-output.
- Refresh the available toolsets with --refresh-toolsets.

Prerequisites
-------------
- **For cluster mode**: Kubernetes cluster access with sufficient permissions to create namespaces, deployments, and RBAC resources
- **For local mode**: Docker installed and running on your local machine

No need to manually set environment variables! All model and credential information can be configured interactively using `az aks agent-init`.
For more details about supported model providers and required
variables, see: https://docs.litellm.ai/docs/providers


Quick start and examples
=========================

Install the extension
---------------------

.. code-block:: bash

    az extension add --name aks-agent

Initialize and configure the AKS agent
---------------------------------------

.. code-block:: bash

    az aks agent-init --resource-group MyResourceGroup --name MyManagedCluster

This command will interactively guide you through the initialization process:

1. **Choose deployment mode**: Select between cluster mode (agent runs as Helm chart in AKS) or local mode (agent runs in Docker container on your machine)
2. **Configure LLM model**: Select and validate LLM provider with credentials stored securely
3. **Cluster mode setup**:
   
   - Specify the namespace for deployment (e.g., aks-agent)
   - Provide service account name for Kubernetes RBAC
   - Deploy the AKS agent Helm chart in your cluster
   - Configure Kubernetes RBAC for secure cluster resource access
   - Optionally configure Azure workload identity for Azure resource access

4. **Local mode setup**:
   
   - Configure Docker-based agent execution
   - Store configuration files locally for cluster-specific access
   - Mount Azure credentials and kubeconfig automatically

You can run it multiple times to update configurations or add more models.

Run the agent (Azure OpenAI example) :
-----------------------------------

**1. Use the last configured model (no extra parameters needed):**

.. code-block:: bash

    az aks agent "Why are my pods not starting?" --name MyManagedCluster --resource-group MyResourceGroup

**2. Specify a particular model you have configured:**

.. code-block:: bash

    az aks agent "Why are my pods not starting?" --name MyManagedCluster --resource-group MyResourceGroup --model azure/my-gpt4.1-deployment


Run the agent (OpenAI example)
------------------------------

**1. Use the last configured model (no extra parameters needed):**

.. code-block:: bash

    az aks agent "Why are my pods not starting?" --name MyManagedCluster --resource-group MyResourceGroup

**2. Specify a particular model you have configured:**

.. code-block:: bash
    
    az aks agent "Why are my pods not starting?" --name MyManagedCluster --resource-group MyResourceGroup --model gpt-4o

Run in non-interactive batch mode
---------------------------------

.. code-block:: bash

    az aks agent "Diagnose networking issues" --no-interactive --name MyManagedCluster --resource-group MyResourceGroup --model azure/my-gpt4.1-deployment

Clean up the AKS agent
-----------------------

To uninstall the AKS agent and clean up all Kubernetes resources:

.. code-block:: bash

    az aks agent-cleanup --resource-group MyResourceGroup --name MyManagedCluster

This command will:

1. Uninstall the AKS agent Helm chart from your cluster
2. Remove all associated Kubernetes resources (deployments, pods, secrets, RBAC configurations)
3. Clean up the LLM configuration secrets

More help
---------

For a complete list of parameters, detailed examples and help text, run:

.. code-block:: bash

    az aks agent -h
