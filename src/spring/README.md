Microsoft Azure CLI 'spring-cloud' Extension
==========================================

This package is for the 'spring-cloud' extension.
i.e. 'az spring-cloud'

### How to use ###
Install this extension using the below CLI command
```
az extension add --name spring-cloud
```

### Sample Commands ###
Create a service and not wait
```
az spring-cloud create -n <service name> --no-wait
```
Create a green deployment with default configuration
```
az spring-cloud app deployment  create --app <app name> -n <deployment name> --jar-path <jar path>
```