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
#### Kubernetes Configuration:
Kubernetes SourceControl Configuration: [more info](https://docs.microsoft.com/en-us/azure/kubernetessconfiguration/)\
*Examples:*

##### Create a KubernetesConfiguration
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

##### Get a KubernetesConfiguration
```
az k8s-configuration show \
    --resource-group groupName \
    --cluster-name clusterName \
    --cluster-type clusterType \
    --name configurationName
```

##### Delete a KubernetesConfiguration
```
az k8s-configuration delete \
    --resource-group groupName \
    --cluster-name clusterName \
    --cluster-type clusterType \
    --name configurationName
```

##### Update a KubernetesConfiguration
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

##### List all KubernetesConfigurations of a cluster
```
az k8s-configuration list \
    --resource-group groupName \
    --cluster-name clusterName \
    --cluster-type clusterType
```

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.