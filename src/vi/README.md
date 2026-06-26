Microsoft Azure CLI 'vi' Extension
=============================================

This package is for the Video Indexer ('vi') i.e. 'az vi'
Azure AI Video Indexer is an AI-powered solution that helps you extract insights from video and audio content.
It is available both as an Azure Arc extension for edge deployments and as a cloud-based application.
Video Indexer: [more info](https://learn.microsoft.com/en-us/azure/azure-video-indexer/)

#### Video Indexer:
This package includes the 'extension' and 'camera' subgroups.
i.e. 'az vi extension' and 'az vi camera'

### Included Features
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

##### Add a camera to a Video Indexer Extension
```
az vi camera add \
    --resource-group groupName \
    --connected-cluster clusterName \
    --camera-name mycamera \
    --rtsp-url rtsp://mycamera
```

##### List all cameras for a Video Indexer Extension
```
az vi camera list \
    --resource-group groupName \
    --connected-cluster clusterName
```
