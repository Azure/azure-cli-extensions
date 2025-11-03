Azure CLI AKS Agent Extension
===============================

Introduction
============


The AKS Agent extension provides the "az aks agent" command, an AI-powered assistant that helps analyze and troubleshoot Azure Kubernetes Service (AKS) clusters using Large Language Models (LLMs). The agent combines cluster context, configurable toolsets, and LLMs to answer natural-language questions about your cluster (for example, "Why are my pods not starting?") and can investigate issues in both interactive and non-interactive (batch) modes.

New in this version: **az aks agent-init** command for easy LLM model configuration!

You can now use `az aks agent-init` to interactively add and configure LLM models before asking questions. This command guides you through the setup process, allowing you to add multiple models as needed. When asking questions with `az aks agent`, you can:

- Use `--config-file` to specify your own model configuration file
- Use `--model` to select a previously configured model
- If neither is provided, the last configured LLM will be used by default

This makes it much easier to manage and switch between multiple models for your AKS troubleshooting workflows.

Key capabilities
----------------


- Interactive and non-interactive modes (use --no-interactive for batch runs).
- Support for multiple LLM providers (Azure OpenAI, OpenAI, etc.) via interactive configuration.
- **Easy model setup with `az aks agent-init`**: interactively add and configure LLM models, run multiple times to add more models.
- Configurable via a JSON/YAML config file provided with --config-file, or select a model with --model.
- If no config or model is specified, the last configured LLM is used automatically.
- Control echo and tool output visibility with --no-echo-request and --show-tool-output.
- Refresh the available toolsets with --refresh-toolsets.
- Stay in traditional toolset mode by default, or opt in to aks-mcp integration with ``--aks-mcp`` when you need the enhanced capabilities.

Prerequisites
-------------
No need to manually set environment variables! All model and credential information can be configured interactively using `az aks agent-init`.
For more details about supported model providers and required
variables, see: https://docs.litellm.ai/docs/providers


LLM Configuration Explained
---------------------------

The AKS Agent uses YAML configuration files to define LLM connections. Each configuration contains a provider specification and the required environment variables for that provider.

Configuration Structure
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

    llms:
    - provider: azure
      MODEL_NAME: gpt-4.1
      AZURE_API_KEY: *******
      AZURE_API_BASE: https://{azure-openai-service}.openai.azure.com/
      AZURE_API_VERSION: 2025-04-01-preview

Field Explanations
^^^^^^^^^^^^^^^^^^

**provider**
    The LiteLLM provider route that determines which LLM service to use. This follows the LiteLLM provider specification from https://docs.litellm.ai/docs/providers.

    Common values:

    * ``azure`` - Azure OpenAI Service
    * ``openai`` - OpenAI API and OpenAI-compatible APIs (e.g., local models, other services)
    * ``anthropic`` - Anthropic Claude
    * ``gemini`` - Google's Gemini
    * ``openai_compatible`` - OpenAI-compatible APIs (e.g., local models, other services)

**MODEL_NAME**
    The specific model or deployment name to use. This varies by provider:

    * For Azure OpenAI: Your deployment name (e.g., ``gpt-4.1``, ``gpt-35-turbo``)
    * For OpenAI: Model name (e.g., ``gpt-4``, ``gpt-3.5-turbo``)
    * For other providers: Check the specific model names in LiteLLM documentation

**Environment Variables by Provider**

The remaining fields are environment variables required by each provider. These correspond to the authentication and configuration requirements of each LLM service:

**Azure OpenAI (provider: azure)**
    * ``AZURE_API_KEY`` - Your Azure OpenAI API key
    * ``AZURE_API_BASE`` - Your Azure OpenAI endpoint URL (e.g., https://your-resource.openai.azure.com/)
    * ``AZURE_API_VERSION`` - API version (e.g., 2024-02-01, 2025-04-01-preview)

**OpenAI (provider: openai)**
    * ``OPENAI_API_KEY`` - Your OpenAI API key (starts with sk-)

**Gemini (provider: gemini)**
    * ``GOOGLE_API_KEY`` - Your Google Cloud API key
    * ``GOOGLE_API_ENDPOINT`` - Base URL for the Gemini API endpoint

**Anthropic (provider: anthropic)**
    * ``ANTHROPIC_API_KEY`` - Your Anthropic API key

**OpenAI Compatible (provider: openai_compatible)**
    * ``OPENAI_API_BASE`` - Base URL for the API endpoint
    * ``OPENAI_API_KEY`` - API key (if required by the service)

Multiple Model Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can configure multiple models in a single file:

.. code-block:: yaml

    llms:
    - provider: azure
      MODEL_NAME: gpt-4
      AZURE_API_KEY: your-azure-key
      AZURE_API_BASE: https://your-azure-endpoint.openai.azure.com/
      AZURE_API_VERSION: 2024-02-01
    - provider: openai
      MODEL_NAME: gpt-4
      OPENAI_API_KEY: your-openai-key
    - provider: anthropic
      MODEL_NAME: claude-3-sonnet-20240229
      ANTHROPIC_API_KEY: your-anthropic-key

When using ``--model``, specify the provider and model as ``provider/model_name`` (e.g., ``azure/gpt-4``, ``openai/gpt-4``).

Security Note
^^^^^^^^^^^^^

API keys and credentials in configuration files should be kept secure. Consider using:

* Restricted file permissions (``chmod 600 config.yaml``)
* Environment variable substitution where supported
* Separate configuration files for different environments (dev/prod)

Quick start and examples
=========================

Install the extension
---------------------

.. code-block:: bash

    az extension add --name aks-agent

Configure LLM models interactively
----------------------------------

.. code-block:: bash

    az aks agent-init

This command will guide you through adding a new LLM model. You can run it multiple times to add more models or update existing models. All configured models are saved locally and can be selected when asking questions.

Run the agent (Azure OpenAI example) :
-----------------------------------

**1. Use the last configured model (no extra parameters needed):**

.. code-block:: bash

    az aks agent "Why are my pods not starting?" --name MyManagedCluster --resource-group MyResourceGroup

**2. Specify a particular model you have configured:**

.. code-block:: bash

    az aks agent "Why are my pods not starting?" --name MyManagedCluster --resource-group MyResourceGroup --model azure/my-gpt4.1-deployment

**3. Use a custom config file:**

.. code-block:: bash

    az aks agent "Why are my pods not starting?" --config-file /path/to/your/model_config.yaml


Run the agent (OpenAI example)
------------------------------

**1. Use the last configured model (no extra parameters needed):**

.. code-block:: bash

    az aks agent "Why are my pods not starting?" --name MyManagedCluster --resource-group MyResourceGroup

**2. Specify a particular model you have configured:**

.. code-block:: bash
    
    az aks agent "Why are my pods not starting?" --name MyManagedCluster --resource-group MyResourceGroup --model gpt-4o

**3. Use a custom config file:**

.. code-block:: bash

    az aks agent "Why are my pods not starting?" --config-file /path/to/your/model_config.yaml

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
