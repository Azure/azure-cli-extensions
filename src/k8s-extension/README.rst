Microsoft Azure CLI 'k8s-extension' Extension
=============================================

This package is for the 'k8s-extension' extension.
i.e. 'az k8s-extension'

This package includes the 'extension-types' subgroup.
i.e. 'az k8s-extension extension-types'

### How to use ###
Install this extension using the below CLI command
```
az extension add --name k8s-extension
```

### Included Features
#### Kubernetes Extensions:
Kubernetes Extensions: [more info](https://docs.microsoft.com/en-us/azure/azure-arc/kubernetes/extensions)\
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
    --plan-name examplePlanName \
    --plan-publisher examplePublisher \
    --plan-product exampleOfferId \

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

##### Update an existing KubernetesExtension of a cluster
```
az k8s-extension update \
    --resource-group groupName \
    --cluster-name clusterName \
    --cluster-type clusterType \
    --name extensionName \
    --auto-upgrade true/false \
    --version extensionVersion \
    --release-train releaseTrain \
    --configuration-settings settingsKey=settingsValue \
    --configuration-protected-settings protectedSettingsKey=protectedValue \
    --configuration-settings-file configSettingsFile \
    --configuration-protected-settings-file protectedSettingsFile
```

##### List available extension types of a cluster
```
az k8s-extension extension-types list \
    --resource-group groupName \
    --cluster-name clusterName \
    --cluster-type clusterType 
```

##### List available extension types by location 
```
az k8s-extension extension-types list-by-location \
    --location location 
```

##### Show an extension types of a cluster
```
az k8s-extension extension-types show \
    --resource-group groupName \
    --cluster-name clusterName \
    --cluster-type clusterType \
    --name extensionName 
```

##### List all versions of an extension type by release train
```
az k8s-extension extension-types list-versions \
    --location location \
    --name extensionName
```
