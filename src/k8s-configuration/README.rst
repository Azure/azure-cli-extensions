Microsoft Azure CLI 'k8s-configuration' Extension
==========================================

This package is for the 'k8s-configuration' extension.
i.e. 'az k8s-configuration'

### How to use ###
Install this extension using the below CLI command
```
az extension add --name k8s-configuration
```

### Included Features

#### Flux Configuration (Flux v2):
Flux Configuration (Flux v1) Configuration: [more info](https://docs.microsoft.com/en-us/azure/kubernetessconfiguration/)\
*Examples:*

##### Create a Flux Configuration (Flux v2)
```
az k8s-configuration create flux \
    --resource-group groupName \
    --cluster-name clusterName \
    --cluster-type clusterType \
    --name configurationName \
    --namespace configurationNamespace \
    --scope cluster
    --kind git \
    --url https://github.com/Azure/arc-k8s-demo \
    --branch main \
    --kustomization name=my-kustomization 
```

##### Get a Flux Configuration (Flux v2)
```
az k8s-configuration flux show \
    --resource-group groupName \
    --cluster-name clusterName \
    --cluster-type clusterType \
    --name configurationName
```

##### Delete a Flux Configuration (Flux v2)
```
az k8s-configuration flux delete \
    --resource-group groupName \
    --cluster-name clusterName \
    --cluster-type clusterType \
    --name configurationName
```

##### List all Flux Configuration (Flux v2) on a cluster
```
az k8s-configuration flux list \
    --resource-group groupName \
    --cluster-name clusterName \
    --cluster-type clusterType
```

#### Source Control Configuration (Flux v1):
Source Control Configuration (Flux v1) Configuration: [more info](https://docs.microsoft.com/en-us/azure/kubernetessconfiguration/)\
*Examples:*

##### Create a Source Control Configuration (Flux v1)
```
az k8s-configuration create \
    --resource-group groupName \
    --cluster-name clusterName \
    --cluster-type clusterType \
    --name configurationName \
    --operator-instance-name operatorInstanceName \
    --operator-namespace operatorNamespace \
    --repository-url githubRepoUrl \
    --operator-params operatorParameters \
    --enable-helm-operator \
    --helm-operator-version chartVersion \
    --helm-operator-params chartParameters
```

##### Get a Source Control Configuration (Flux v1)
```
az k8s-configuration show \
    --resource-group groupName \
    --cluster-name clusterName \
    --cluster-type clusterType \
    --name configurationName
```

##### Delete a Source Control Configuration (Flux v1)
```
az k8s-configuration delete \
    --resource-group groupName \
    --cluster-name clusterName \
    --cluster-type clusterType \
    --name configurationName
```

##### Update a Source Control Configuration (Flux v1)
```
az k8s-configuration create \
    --resource-group groupName \
    --cluster-name clusterName \
    --cluster-type clusterType \
    --name configurationName \
    --repository-url githubRepoUrl \
    --operator-params operatorParameters \
    --enable-helm-operator \
    --helm-operator-version chartVersion \
    --helm-operator-params chartParameters
```

##### List all Source Control Configuration (Flux v1) on a cluster
```
az k8s-configuration list \
    --resource-group groupName \
    --cluster-name clusterName \
    --cluster-type clusterType
```

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.