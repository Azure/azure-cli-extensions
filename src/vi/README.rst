Microsoft Azure CLI 'vi' Extension
=============================================

This package is for the 'vi' (Video Indexer) extension.
i.e. 'az vi'

This package includes the 'extension' and 'camera' subgroups.
i.e. 'az vi extension' and 'az vi camera'

### How to use ###
Install this extension using the below CLI command
```
az extension add --name vi
```

### Included Features
#### Video Indexer Extension:
Video Indexer Extension: [more info](https://learn.microsoft.com/en-us/azure/azure-video-indexer/)\
*Examples:*

##### Show Video Indexer Extension details
```
az vi extension show \
    --resource-group groupName \
    --connected-cluster clusterName
```

##### Troubleshoot a Video Indexer Extension
```
az vi extension troubleshoot \
    --resource-group groupName \
    --connected-cluster clusterName
```

##### List all cameras for a Video Indexer Extension
```
az vi camera list \
    --resource-group groupName \
    --connected-cluster clusterName
```
