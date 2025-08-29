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
    short-summary: Run AI assistant to analyze and troubleshoot Kubernetes clusters.
    long-summary: |-
      This command allows you to ask questions about your Azure Kubernetes cluster and get answers using AI models.
      Environment variables must be set to use the AI model, please refer to https://docs.litellm.ai/docs/providers to learn more about supported AI providers and models and required environment variables.
    parameters:
        - name: --name -n
          type: string
          short-summary: Name of the managed cluster.
        - name: --resource-group -g
          type: string
          short-summary: Name of the resource group.
        - name: --model
          type: string
          short-summary: Model to use for the LLM.
        - name: --api-key
          type: string
          short-summary: API key to use for the LLM (if not given, uses environment variables AZURE_API_KEY, OPENAI_API_KEY).
        - name: --config-file
          type: string
          short-summary: Path to configuration file.
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

    examples:
        - name: Ask about pod issues in the cluster with Azure OpenAI
          text: |-
            export AZURE_API_BASE="https://my-azureopenai-service.openai.azure.com/"
            export AZURE_API_VERSION="2025-01-01-preview"
            export AZURE_API_KEY="sk-xxx"
            az aks agent "Why are my pods not starting?" --name MyManagedCluster --resource-group MyResourceGroup --model azure/my-gpt4.1-deployment
        - name: Ask about pod issues in the cluster with OpenAI
          text: |-
            export OPENAI_API_KEY="sk-xxx"
            az aks agent "Why are my pods not starting?" --name MyManagedCluster --resource-group MyResourceGroup --model gpt-4o
        - name: Run in interactive mode without a question
          text: az aks agent "Check the pod status in my cluster" --name MyManagedCluster --resource-group MyResourceGroup --model azure/my-gpt4.1-deployment --api-key "sk-xxx"
        - name: Run in non-interactive batch mode
          text: az aks agent "Diagnose networking issues" --no-interactive --max-steps 15 --model azure/my-gpt4.1-deployment
        - name: Show detailed tool output during analysis
          text: az aks agent "Why is my service workload unavailable in namespace workload-ns?" --show-tool-output --model azure/my-gpt4.1-deployment
        - name: Use custom configuration file
          text: az aks agent "Check kubernetes pod resource usage" --config-file /path/to/custom.yaml --model azure/my-gpt4.1-deployment
        - name: Run agent with no echo of the original question
          text: az aks agent "What is the status of my cluster?" --no-echo-request --model azure/my-gpt4.1-deployment
        - name: Refresh toolsets to get the latest available tools
          text: az aks agent "What is the status of my cluster?" --refresh-toolsets --model azure/my-gpt4.1-deployment
        - name: Run agent with config file
          text: |
            az aks agent "Check kubernetes pod resource usage" --config-file /path/to/custom.yaml
            Here is an example of config file:
            ```json
            model: "gpt-4o"
            api_key: "..."
            # define a list of mcp servers, mcp server can be defined
            mcp_servers:
              aks_mcp:
                description: "The AKS-MCP is a Model Context Protocol (MCP) server that enables AI assistants to interact with Azure Kubernetes Service (AKS) clusters"
                url: "http://localhost:8003/sse"

            # try adding your own tools or toggle the built-in toolsets here
            # e.g. query company-specific data, fetch logs from your existing observability tools, etc
            # To check how to add a customized toolset, please refer to https://docs.robusta.dev/master/configuration/holmesgpt/custom_toolsets.html#custom-toolsets
            # To find all built-in toolsets, please refer to https://docs.robusta.dev/master/configuration/holmesgpt/builtin_toolsets.html
            toolsets:
              # add a new json processor toolset
              json_processor:
                description: "A toolset for processing JSON data using jq"
                prerequisites:
                  - command: "jq --version"  # Ensure jq is installed
                tools:
                  - name: "process_json"
                    description: "A tool that uses jq to process JSON input"
                    command: "echo '{{ json_input }}' | jq '.'"  # Example jq command to format JSON
              # disable a built-in toolsets
              aks/core:
                enabled: false
              ```
"""
