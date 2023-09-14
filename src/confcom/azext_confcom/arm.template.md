This file is a reference page for the [README](README.md) file.

arm-template.json

```
{
  "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "variables": {
    "container1name": "examplecontainer",
    "containergroupname": "examplecontainergroup"
  },
  "parameters": {
    "share-name": {
      "type": "string",
      "metadata": {
        "description": "Name for the container group"
      }
    },
    "storage-account-name": {
      "type": "string",
      "metadata": {
        "description": "Name for the container"
      }
    },
    "image": {
      "type": "string",
      "metadata": {
        "description": "Image for the container"
      }
    },
    "storage-account-key": {
      "type": "string",
      "metadata": {
        "description": "Name for the gitRepo volume"
      }
    }
  },
  "resources": [
    {
      "name": "[variables('containergroupname')]",
      "type": "Microsoft.ContainerInstance/containerGroups",
      "apiVersion": "2023-05-01",
      "location": "[resourceGroup().location]",
      "properties": {
        "confidentialComputeProperties": {
          "ccePolicy": ""
        },
        "containers": [
          {
            "name": "[variables('container1name')]",
            "properties": {
              "environmentVariables": [
                {
                  "name": "PORT",
                  "value": "80"
                }
              ],
              "image": "[parameters('image')]",
              "resources": {
                "requests": {
                  "cpu": 1,
                  "memoryInGb": 1.5
                }
              },
              "ports": [
                {
                  "port": 80
                }
              ],
              "volumeMounts": [
                {
                  "name": "filesharevolume",
                  "mountPath": "/aci/logs"
                }
              ]
            }
          }
        ],
        "sku": "Confidential",
        "osType": "Linux",
        "ipAddress": {
          "type": "Public",
          "ports": [
            {
              "protocol": "tcp",
              "port": "80"
            }
          ],
          "dnsNameLabel": "dns-label-name"
        },
        "volumes": [
          {
            "name": "filesharevolume",
            "azureFile": {
              "shareName": "[parameters('share-name')]",
              "storageAccountName": "[parameters('storage-account-name')]",
              "storageAccountKey": "[parameters('storage-account-key')]"
            }
          }
        ]
      }
    }
  ],
  "outputs": {
    "containerIPv4Address": {
      "type": "string",
      "value": "[reference(resourceId('Microsoft.ContainerInstance/containerGroups/', variables('containergroupname'))).ipAddress.ip]"
    }
  }
}
```
