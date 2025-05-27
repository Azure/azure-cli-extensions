Microsoft Azure CLI 'vme' Extension
==========================================

This package is for the 'vme' extension.
i.e. 'az vme'

### How to use ###
Install this extension using the below CLI command
```
az extension add --name vme
```

### Included Features
#### Install version managed extensions with default configurations
```
az vme install --resource-group my-rg --name my-cluster --include all
```

#### Uninstall version managed extensions
```
az vme uninstall --resource-group my-rg --name my-cluster --include all
```

#### Check version managed extensions' upgrade status
```
az vme upgrade --resource-group my-rg --name my-cluster --wait
```