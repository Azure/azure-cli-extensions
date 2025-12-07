Azure CLI AKS Agent Extension
===============================

Introduction
============


The AKS Agent extension provides the "az aks agent" command, an AI-powered assistant that helps analyze and troubleshoot Azure Kubernetes Service (AKS) clusters using Large Language Models (LLMs). The agent combines cluster context, configurable toolsets, and LLMs to answer natural-language questions about your cluster (for example, "Why are my pods not starting?") and can investigate issues in both interactive and non-interactive (batch) modes.

New in this version: **az aks agent-init** command for containerized agent deployment!

The `az aks agent-init` command deploys the AKS agent as a Helm chart directly in your AKS cluster with enterprise-grade security:

- **Kubernetes RBAC**: Uses cluster roles to securely access Kubernetes resources with least-privilege principles
- **Workload Identity**: Leverages Azure workload identity for secure, keyless access to Azure resources
- **Interactive LLM Configuration**: Guides you through setting up LLM models with encrypted storage in Kubernetes secrets

When asking questions with `az aks agent`:

- The agent automatically uses the last configured model
- Use `--model` to select a specific model when you have multiple models configured

This architecture provides better security, scalability, and manageability for production AKS troubleshooting workflows.

Key capabilities
----------------


- **Containerized Deployment**: Agent runs as a Helm chart in your AKS cluster with `az aks agent-init`.
- **Secure Access**: Uses Kubernetes RBAC for cluster resources and Azure workload identity for Azure resources.
- **LLM Configuration**: Interactively configure LLM models with credentials stored securely in Kubernetes secrets.
- Support for multiple LLM providers (Azure OpenAI, OpenAI, Anthropic, Gemini, etc.).
- Automatically uses the last configured model by default.
- Optionally use --model to select a specific model when you have multiple models configured.
- Interactive and non-interactive modes (use --no-interactive for batch runs).
- Control echo and tool output visibility with --no-echo-request and --show-tool-output.
- Refresh the available toolsets with --refresh-toolsets.

Prerequisites
-------------
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

This command will configure the LLM configuration and:

1. Guide you through LLM model configuration with credentials stored securely in Kubernetes secrets
2. Deploy the AKS agent Helm chart in your cluster
3. Configure Kubernetes RBAC for secure cluster resource access
4. Optionally configure Azure workload identity for Azure resource access

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

    az aks agent "Diagnose networking issues" --no-interactive --max-steps 15 --model azure/my-gpt4.1-deployment

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
