# Azure CLI CommandChange Extension #
This is an extension to Azure CLI to manage CommandChange resources.

## How to use ##
Install this extension using the below CLI command
```
az extension add --name command-change
```

### Included Features ###
#### command-change ####
##### meta-diff #####
```
az command-change meta-diff --base-meta-file fileA --diff-meta-file fileB --only-break
```
##### version-diff #####
```
az command-change version-diff --base-version 2.47.0 --diff-version 2.49.0 --target-module monitor
```