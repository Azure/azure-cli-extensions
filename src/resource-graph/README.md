# Azure CLI Resource Graph Extension #

This package is for the 'resource-graph' extension, i.e. 'az graph'.

### How to use ###
Install this extension using the below CLI command
```
az extension add --name resoure-graph
```

### Included Features

#### Resource Graph Query:
*Examples:*

##### Query the resources managed by Azure Resource Manager.

```
az graph query -q "project id, name, type, location, tags"
```

See https://aka.ms/AzureResourceGraph-QueryLanguage to learn more about query language and browse examples

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.