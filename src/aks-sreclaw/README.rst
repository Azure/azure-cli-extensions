Azure CLI AKS SREClaw Extension
================================

This extension provides commands to manage AKS SREClaw, an autonomous AI-powered troubleshooting assistant for Azure Kubernetes Service clusters.

Installation
------------

To install the extension:

.. code-block:: bash

    az extension add --name aks-sreclaw

Usage
-----

Deploy SREClaw to your AKS cluster
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Initialize and deploy SREClaw with interactive LLM configuration:

.. code-block:: bash

    az aks claw create --resource-group MyResourceGroup --name MyAKSCluster --namespace kube-system

This command will:

1. Prompt you to select an LLM provider (Azure OpenAI or OpenAI)
2. Guide you through entering model names and API credentials
3. Validate the connection to your LLM provider
4. Prompt for a Kubernetes service account name
5. Deploy the SREClaw helm chart to your cluster
6. Wait for pods to be ready (up to 5 minutes)

Deploy without waiting for completion
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    az aks claw create --resource-group MyResourceGroup --name MyAKSCluster --namespace kube-system --no-wait

Check deployment status
~~~~~~~~~~~~~~~~~~~~~~~

View the current status of your SREClaw deployment:

.. code-block:: bash

    az aks claw status --resource-group MyResourceGroup --name MyAKSCluster --namespace kube-system

This displays:

- Helm release status
- Deployment replica counts
- Pod status and readiness
- Configured LLM providers with models and API endpoints

Connect to SREClaw service
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Establish a port-forward connection to access the SREClaw web interface:

.. code-block:: bash

    az aks claw connect --resource-group MyResourceGroup --name MyAKSCluster --namespace kube-system

The command will:

- Display the gateway authentication token
- Create a port-forward to localhost:18789
- Provide instructions to open the service in your browser

To use a different local port:

.. code-block:: bash

    az aks claw connect --resource-group MyResourceGroup --name MyAKSCluster --namespace kube-system --local-port 8080

Press Ctrl+C to stop the port-forwarding.

Delete SREClaw
~~~~~~~~~~~~~~

Uninstall SREClaw and clean up all resources:

.. code-block:: bash

    az aks claw delete --resource-group MyResourceGroup --name MyAKSCluster --namespace kube-system

This command will:

1. Prompt for confirmation
2. Uninstall the SREClaw helm chart
3. Delete all associated secrets and configurations
4. Wait for pods to be removed

To delete without waiting:

.. code-block:: bash

    az aks claw delete --resource-group MyResourceGroup --name MyAKSCluster --namespace kube-system --no-wait

LLM Provider Configuration
---------------------------

Azure OpenAI
~~~~~~~~~~~~

When prompted during deployment, select Azure OpenAI and provide:

- **Models**: Comma-separated model names (e.g., ``gpt-5.4,gpt-5.1``)
- **API Key**: Your Azure OpenAI API key
- **API Base**: Your Azure OpenAI endpoint (e.g., ``https://YOUR-RESOURCE-NAME.openai.azure.com/openai/v1/``)

OpenAI
~~~~~~

When prompted during deployment, select OpenAI and provide:

- **Models**: Comma-separated model names (e.g., ``gpt-5.4,gpt-5.1``)
- **API Key**: Your OpenAI API key

Prerequisites
-------------

- Azure CLI installed
- An AKS cluster
- kubectl configured to access your cluster
- Appropriate permissions to deploy resources to your AKS cluster
- An LLM provider account (Azure OpenAI or OpenAI) with API access

Service Account Requirements
-----------------------------

SREClaw requires a Kubernetes service account with:

- Appropriate Role and RoleBinding in the target namespace
- For Azure resource access: annotation with ``azure.workload.identity/client-id: <managed-identity-client-id>``

Ensure you create these before running ``az aks claw create``.

Troubleshooting
---------------

Check deployment status
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    az aks claw status --resource-group MyResourceGroup --name MyAKSCluster --namespace kube-system

View pod logs
~~~~~~~~~~~~~

.. code-block:: bash

    kubectl logs -n kube-system -l app.kubernetes.io/name=aks-sreclaw

Verify helm release
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    helm list -n kube-system

Uninstall and reinstall
~~~~~~~~~~~~~~~~~~~~~~~~

If you encounter issues:

.. code-block:: bash

    az aks claw delete --resource-group MyResourceGroup --name MyAKSCluster --namespace kube-system
    az aks claw create --resource-group MyResourceGroup --name MyAKSCluster --namespace kube-system

Support
-------

For issues and feature requests, please visit:
https://github.com/Azure/azure-cli-extensions

License
-------

This extension is licensed under the MIT License. See LICENSE.txt for details.
