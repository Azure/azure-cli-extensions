Azure CLI AKS Agent Extension
===============================

Introduction
============

The AKS Agent extension provides the "az aks agent" command, an AI-powered assistant that
helps analyze and troubleshoot Azure Kubernetes Service (AKS) clusters using Large Language
Models (LLMs). The agent combines cluster context, configurable toolsets, and LLMs to answer
natural-language questions about your cluster (for example, "Why are my pods not starting?")
and can investigate issues in both interactive and non-interactive (batch) modes.

Key capabilities
----------------

- Interactive and non-interactive modes (use --no-interactive for batch runs).
- Support for multiple LLM providers (Azure OpenAI, OpenAI, etc.) via environment variables.
- Configurable via a JSON/YAML config file provided with --config-file.
- Control echo and tool output visibility with --no-echo-request and --show-tool-output.
- Refresh the available toolsets with --refresh-toolsets.
- Stay in traditional toolset mode by default, or opt in to aks-mcp integration with ``--aks-mcp`` when you need the enhanced capabilities.

Prerequisites
-------------

Before using the agent, make sure provider-specific environment variables are set. For
example, Azure OpenAI typically requires AZURE_API_BASE, AZURE_API_VERSION, and AZURE_API_KEY,
while OpenAI requires OPENAI_API_KEY. For more details about supported providers and required
variables, see: https://docs.litellm.ai/docs/providers

Quick start and examples
========================

Install the extension
---------------------

.. code-block:: bash

    az extension add --name aks-agent

Run the agent (Azure OpenAI example)
-----------------------------------

.. code-block:: bash

    export AZURE_API_BASE="https://my-azureopenai-service.openai.azure.com/"
    export AZURE_API_VERSION="2025-01-01-preview"
    export AZURE_API_KEY="sk-xxx"

    az aks agent "Why are my pods not starting?" --name MyManagedCluster --resource-group MyResourceGroup --model azure/my-gpt4.1-deployment

Run the agent (OpenAI example)
------------------------------

.. code-block:: bash

    export OPENAI_API_KEY="sk-xxx"
    az aks agent "Why are my pods not starting?" --name MyManagedCluster --resource-group MyResourceGroup --model gpt-4o

Run in non-interactive batch mode
---------------------------------

.. code-block:: bash

    az aks agent "Diagnose networking issues" --no-interactive --max-steps 15 --model azure/my-gpt4.1-deployment

Opt in to MCP mode
------------------

Traditional toolsets remain the default. Enable the aks-mcp integration when you want the enhanced toolsets by passing ``--aks-mcp``. You can return to traditional mode on a subsequent run with ``--no-aks-mcp``.

.. code-block:: bash

    az aks agent --aks-mcp "Check node health with MCP" --name MyManagedCluster --resource-group MyResourceGroup --model azure/my-gpt4.1-deployment

Using a configuration file
--------------------------

Pass a config file with --config-file to predefine model, credentials, and toolsets. See
the example config and more detailed examples in the help definition at
`src/aks-agent/azext_aks_agent/_help.py`.

More help
---------

For a complete list of parameters, detailed examples and help text, run:

.. code-block:: bash

    az aks agent -h
