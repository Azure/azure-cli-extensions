Microsoft Azure CLI 'spring' Extension
==========================================

This package is for the 'spring' extension.
i.e. 'az spring'

### How to use ###
Install this extension using the below CLI command
```
az extension add --name spring
```

### Sample Commands ###
Create a service and not wait
```
az spring create -n <service name> --no-wait
```
Create a green deployment with default configuration
```
az spring app deployment  create --app <app name> -n <deployment name> --jar-path <jar path>
```