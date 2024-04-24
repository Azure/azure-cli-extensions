This file is a reference page for the [README](README.md) file. 

template.parameters.json 

```
{
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "share-name": {
            "value": "<share-account>"
        },
        "storage-account-name": {
            "value": "<storage-account-name>"
        },
        "storage-account-key": {
            "value": "<storage-acount-key>"
        },
        "image": {
            "value": "acicc.azurecr.io/aci/cc-hello-world:latest"
        }
    }
}
```