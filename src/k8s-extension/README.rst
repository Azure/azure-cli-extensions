Microsoft Azure CLI 'k8s-extension' Extension
=============================================

This package is for the 'k8s-extension' extension.
i.e. 'az k8s-extension'

### How to use ###
Install this extension using the below CLI command
```
az extension add --name k8s-extension
```

### Included Features
#### Kubernetes Extensions:
Kubernetes Extensions: [more info](https://docs.microsoft.com/en-us/azure/kubernetessconfiguration/)\
*Examples:*

##### Create a KubernetesExtension
```
az k8s-extension create \
    --resource-group groupName \
    --cluster-name clusterName \
    --cluster-type clusterType \
    --name extensionName \
    --extension-type extensionType \
    --scope scopeType \
    --release-train releaseTrain \
    --version versionNumber \
    --auto-upgrade-minor-version autoUpgrade \
    --configuration-settings exampleSetting=exampleValue \
```

##### Get a KubernetesExtension
```
az k8s-extension show \
    --resource-group groupName \
    --cluster-name clusterName \
    --cluster-type clusterType \
    --name extensionName
```

##### Delete a KubernetesExtension
```
az k8s-extension delete \
    --resource-group groupName \
    --cluster-name clusterName \
    --cluster-type clusterType \
    --name extensionName
```

##### List all KubernetesExtension of a cluster
```
az k8s-extension list \
    --resource-group groupName \
    --cluster-name clusterName \
    --cluster-type clusterType
```

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.