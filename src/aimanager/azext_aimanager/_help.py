# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['aimanager'] = """
    type: group
    short-summary: Manage AI Manager resources for inference on AKS.
"""

helps['aimanager create'] = """
    type: command
    short-summary: Create an AI Manager resource.
    examples:
        - name: Create an AI Manager
          text: az aimanager create --name my-ai-manager -g myrg -l eastus2
        - name: Create an AI Manager with the Keep delete policy
          text: az aimanager create --name my-ai-manager -g myrg -l eastus2 --delete-policy Keep
"""

helps['aimanager update'] = """
    type: command
    short-summary: Update an AI Manager resource.
    examples:
        - name: Update the tags of an AI Manager
          text: az aimanager update --name my-ai-manager -g myrg --tags env=prod team=alpha
        - name: Update the delete policy of an AI Manager
          text: az aimanager update --name my-ai-manager -g myrg --delete-policy Keep
"""

helps['aimanager show'] = """
    type: command
    short-summary: Show the details of an AI Manager resource.
    examples:
        - name: Show an AI Manager
          text: az aimanager show --name my-ai-manager -g myrg
"""

helps['aimanager delete'] = """
    type: command
    short-summary: Delete an AI Manager resource.
    examples:
        - name: Delete an AI Manager
          text: az aimanager delete --name my-ai-manager -g myrg
"""

helps['aimanager list'] = """
    type: command
    short-summary: List AI Manager resources.
    examples:
        - name: List AI Managers in a resource group
          text: az aimanager list -g myrg
        - name: List all AI Managers in the subscription
          text: az aimanager list
"""

helps['aimanager wait'] = """
    type: command
    short-summary: Wait for an AI Manager resource to reach a desired state.
"""

helps['aimanager get-credentials'] = """
    type: command
    short-summary: Get access credentials for an AI Manager.
    long-summary: |-
        Retrieves the Kubernetes configuration for an AI Manager and merges it into the local
        kubeconfig file (default ~/.kube/config), similar to 'az aks get-credentials'.
    examples:
        - name: Get the credentials for an AI Manager and merge into the default kubeconfig
          text: az aimanager get-credentials --name my-ai-manager -g myrg
        - name: Print the credentials to stdout
          text: az aimanager get-credentials --name my-ai-manager -g myrg -f -
"""

helps['aimanager modelsource'] = """
    type: group
    short-summary: Manage model sources within an AI Manager.
    long-summary: |-
        A model source tells the platform where to pull model artifacts from and, for gated or
        private sources, which credential to authenticate with. Model sources are referenced by
        'az aimanager namespace modeldeployment add --model-source-resource-id'.
"""

helps['aimanager modelsource add'] = """
    type: command
    short-summary: Add a model source to an AI Manager.
    examples:
        - name: Add a public Hugging Face model source
          text: az aimanager modelsource add -g myrg --aimanager-name my-ai-manager -n hf --source-type HuggingFace
        - name: Add a Hugging Face model source with an access token for gated models
          text: az aimanager modelsource add -g myrg --aimanager-name my-ai-manager -n hf -s HuggingFace --token hf_xxx --description "Gated models"
"""

helps['aimanager modelsource update'] = """
    type: command
    short-summary: Update a model source within an AI Manager.
    long-summary: |-
        The source type is immutable after creation and is always preserved. Omitted properties
        keep their current values.
    examples:
        - name: Rotate the access token of a model source
          text: az aimanager modelsource update -g myrg --aimanager-name my-ai-manager -n hf --token hf_yyy
        - name: Update the description of a model source
          text: az aimanager modelsource update -g myrg --aimanager-name my-ai-manager -n hf --description "Internal mirror"
"""

helps['aimanager modelsource show'] = """
    type: command
    short-summary: Show the details of a model source within an AI Manager.
    examples:
        - name: Show a model source
          text: az aimanager modelsource show -g myrg --aimanager-name my-ai-manager -n hf
"""

helps['aimanager modelsource list'] = """
    type: command
    short-summary: List the model sources within an AI Manager.
    examples:
        - name: List model sources
          text: az aimanager modelsource list -g myrg --aimanager-name my-ai-manager
"""

helps['aimanager modelsource delete'] = """
    type: command
    short-summary: Delete a model source from an AI Manager.
    examples:
        - name: Delete a model source
          text: az aimanager modelsource delete -g myrg --aimanager-name my-ai-manager -n hf
"""

helps['aimanager modelsource wait'] = """
    type: command
    short-summary: Wait for an AI Manager model source to reach a desired state.
"""

helps['aimanager namespace'] = """
    type: group
    short-summary: Manage namespaces within an AI Manager.
"""

helps['aimanager namespace add'] = """
    type: command
    short-summary: Add a namespace to an AI Manager.
    examples:
        - name: Add a namespace
          text: az aimanager namespace add -m my-ai-manager -g myrg --name team-alpha
        - name: Add a namespace with labels and annotations
          text: az aimanager namespace add -m my-ai-manager -g myrg --name team-alpha --labels team=alpha --annotations owner=alice
"""

helps['aimanager namespace update'] = """
    type: command
    short-summary: Update a namespace within an AI Manager.
    examples:
        - name: Update the labels of a namespace
          text: az aimanager namespace update -m my-ai-manager -g myrg --name team-alpha --labels team=beta
"""

helps['aimanager namespace show'] = """
    type: command
    short-summary: Show the details of a namespace within an AI Manager.
    examples:
        - name: Show a namespace
          text: az aimanager namespace show -m my-ai-manager -g myrg --name team-alpha
"""

helps['aimanager namespace delete'] = """
    type: command
    short-summary: Delete a namespace within an AI Manager.
    examples:
        - name: Delete a namespace
          text: az aimanager namespace delete -m my-ai-manager -g myrg --name team-alpha
"""

helps['aimanager namespace list'] = """
    type: command
    short-summary: List the namespaces within an AI Manager.
    examples:
        - name: List namespaces in an AI Manager
          text: az aimanager namespace list -m my-ai-manager -g myrg
"""

helps['aimanager namespace wait'] = """
    type: command
    short-summary: Wait for an AI Manager namespace to reach a desired state.
"""

helps['aimanager namespace get-credentials'] = """
    type: command
    short-summary: Get access credentials for an AI Manager namespace.
    long-summary: |-
        Retrieves the Kubernetes configuration for an AI Manager namespace and merges it into the
        local kubeconfig file (default ~/.kube/config), similar to 'az aks namespace get-credentials'.
    examples:
        - name: Get the credentials for a namespace and merge into the default kubeconfig
          text: az aimanager namespace get-credentials -m my-ai-manager -g myrg --name team-alpha
        - name: Print the credentials to stdout
          text: az aimanager namespace get-credentials -m my-ai-manager -g myrg --name team-alpha -f -
"""

helps['aimanager namespace list-accesskeys'] = """
    type: command
    short-summary: List the LLM gateway endpoint and API keys of an AI Manager namespace.
    long-summary: |-
        Returns the namespace-scoped, OpenAI-compatible inference gateway endpoint together with the
        current primary and secondary API keys. Treat the keys as secrets: do not log them or persist
        them in plaintext.
    examples:
        - name: List the access keys of a namespace
          text: az aimanager namespace list-accesskeys -g myrg --aimanager-name my-ai-manager --name team-alpha
        - name: Show only the gateway endpoint
          text: az aimanager namespace list-accesskeys -g myrg --aimanager-name my-ai-manager --name team-alpha --query endpoint -o tsv
"""

helps['aimanager namespace rotate-accesskeys'] = """
    type: command
    short-summary: Rotate the LLM gateway API keys of an AI Manager namespace.
    long-summary: |-
        A new key is generated and installed as the primary key, and the previous primary key
        overwrites the secondary key so clients can roll over without downtime. Returns the updated
        access info. Any client still using the previous secondary key will stop being able to
        authenticate.
    examples:
        - name: Rotate the access keys of a namespace
          text: az aimanager namespace rotate-accesskeys -g myrg --aimanager-name my-ai-manager --name team-alpha
"""

helps['aimanager namespace modeldeployment'] = """
    type: group
    short-summary: Manage model deployments within an AI Manager namespace.
"""

helps['aimanager namespace modeldeployment add'] = """
    type: command
    short-summary: Add a model deployment to an AI Manager namespace.
    examples:
        - name: Add a manually scaled model deployment
          text: az aimanager namespace modeldeployment add -g myrg --aimanager-name my-ai-manager --namespace-name team-alpha -n phi --model-resource-id /subscriptions/00000000-0000-0000-0000-000000000000/providers/Microsoft.ContainerService/locations/eastus2/aiModels/phi --vm-size Standard_NC24ads_A100_v4 --replicas 1
        - name: Add an autoscaled model deployment
          text: az aimanager namespace modeldeployment add -g myrg --aimanager-name my-ai-manager --namespace-name team-alpha -n phi --model-resource-id /subscriptions/00000000-0000-0000-0000-000000000000/providers/Microsoft.ContainerService/locations/eastus2/aiModels/phi --vm-size Standard_NC24ads_A100_v4 --min-replicas 1 --max-replicas 3
"""

helps['aimanager namespace modeldeployment update'] = """
    type: command
    short-summary: Update a model deployment within an AI Manager namespace.
    examples:
        - name: Change the fixed replica count
          text: az aimanager namespace modeldeployment update -g myrg --aimanager-name my-ai-manager --namespace-name team-alpha -n phi --replicas 2
        - name: Change the performance mode
          text: az aimanager namespace modeldeployment update -g myrg --aimanager-name my-ai-manager --namespace-name team-alpha -n phi --performance-mode Throughput
"""

helps['aimanager namespace modeldeployment show'] = """
    type: command
    short-summary: Show a model deployment within an AI Manager namespace.
    examples:
        - name: Show a model deployment
          text: az aimanager namespace modeldeployment show -g myrg --aimanager-name my-ai-manager --namespace-name team-alpha -n phi
"""

helps['aimanager namespace modeldeployment list'] = """
    type: command
    short-summary: List model deployments within an AI Manager namespace.
    examples:
        - name: List model deployments
          text: az aimanager namespace modeldeployment list -g myrg --aimanager-name my-ai-manager --namespace-name team-alpha
"""

helps['aimanager namespace modeldeployment delete'] = """
    type: command
    short-summary: Delete a model deployment from an AI Manager namespace.
    examples:
        - name: Delete a model deployment
          text: az aimanager namespace modeldeployment delete -g myrg --aimanager-name my-ai-manager --namespace-name team-alpha -n phi
"""

helps['aimanager namespace modeldeployment wait'] = """
    type: command
    short-summary: Wait for an AI Manager model deployment to reach a desired state.
"""

helps['aimanager model'] = """
    type: group
    short-summary: Browse the AI model catalog and estimate deployment cost.
    long-summary: |-
        AI models are read-only, platform-maintained catalog entries scoped to an Azure region.
        Use 'az aimanager model list' to discover the models available in a region and their
        resource names, which can then be passed to
        'az aimanager namespace modeldeployment add --model-resource-id'.
"""

helps['aimanager model show'] = """
    type: command
    short-summary: Show the details of an AI model in the catalog.
    examples:
        - name: Show an AI model
          text: az aimanager model show -l eastus2 -n 9806f0c862fdd920
"""

helps['aimanager model list'] = """
    type: command
    short-summary: List the AI models available in a region.
    examples:
        - name: List the AI models in a region
          text: az aimanager model list -l eastus2
        - name: List the AI models in a region as a table
          text: az aimanager model list -l eastus2 -o table
"""

helps['aimanager model calculate-cost'] = """
    type: command
    short-summary: Calculate the estimated cost of deploying an AI model in a region.
    long-summary: |-
        Returns a ranked list of GPU SKU pricing plans for deploying the model in the target
        region, each annotated with feasibility, per-replica hourly cost, and estimated relative
        performance. Feasible plans are returned first, ordered by total hourly price ascending.
        No Azure or Kubernetes resources are provisioned by this command. Prices describe a single
        replica; multiply by the desired replica count, bounded by maxAvailableReplicas.
    examples:
        - name: Calculate the cost of deploying a model
          text: az aimanager model calculate-cost -l eastus2 -n 9806f0c862fdd920
        - name: Show the pricing plans as a table
          text: az aimanager model calculate-cost -l eastus2 -n 9806f0c862fdd920 -o table
"""
