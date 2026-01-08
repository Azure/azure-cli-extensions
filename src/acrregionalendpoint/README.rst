Microsoft Azure CLI 'acrregionalendpoint' Extension
==========================================

The 'acrregionalendpoint' extension is for private preview of an Azure Container Registry feature "Regional Endpoint".

Installation
------------

Install the extension using the Azure CLI:

.. code-block:: bash

    az extension add --source <path-to-acrregionalendpoint-extension> --allow-preview true

Usage
-----

This extension enhances Azure Container Registry commands with regional endpoint support:

**az acr create**

Create a registry with regional endpoints enabled:

.. code-block:: bash

    az acr create --resource-group myResourceGroup --name myRegistry --sku Premium --location westus --enable-regional-endpoints true

**az acr update**

Enable or disable regional endpoints on an existing registry:

.. code-block:: bash

    # Enable regional endpoints
    az acr update --name myRegistry --enable-regional-endpoints true

    # Disable regional endpoints
    az acr update --name myRegistry --enable-regional-endpoints false

**az acr login**

Log in to an Azure Container Registry through the Docker CLI:

.. code-block:: bash

    # Login to main endpoint (default)
    az acr login --name myRegistry

    # Login to all endpoints (main + regional endpoints)
    az acr login --name myRegistry --all-endpoints

**az acr import**

Import images using regional endpoint URIs:

.. code-block:: bash

    # Import from regional endpoint
    az acr import --name myTargetRegistry --source mySourceRegistry.eastus.geo.azurecr.io/myimage:latest

    # Import using registry parameter with regional endpoint
    az acr import --name myTargetRegistry --source myimage:latest --registry mySourceRegistry.eastus.geo.azurecr.io

**az acr show-endpoints**

Display available endpoints for a registry:

.. code-block:: bash

    az acr show-endpoints --name myRegistry

Example output when regional endpoints are enabled:

.. code-block:: json

    {
      "dataEndpoints": [
        {
          "endpoint": "myregistry.eastus.data.azurecr.io",
          "region": "eastus"
        }
      ],
      "loginServer": "myregistry.azurecr.io",
      "regionalEndpoints": [
        {
          "endpoint": "myregistry.eastus.geo.azurecr.io",
          "region": "eastus"
        }
      ]
    }

Requirements
------------

* Regional endpoints require **Premium SKU**
* Regional endpoints cannot be used with Docker Content Trust (DCT)
* Subscription must be registered for the Regional Endpoint feature flag

Notes
-----

* When enabling regional endpoints, it's recommended to also enable data endpoints (``--data-endpoint-enabled``) for optimal performance
* Regional endpoint URIs follow the format: ``registryname.region.geo.azurecr.io``
