# Azure CLI cli-translator Extension #
This package is for the 'cli-translator' extension, i.e. 'az cli-translator'.

### How to use ###
Install this extension using the below CLI command
```
az extension add --name cli-translator
```

### Included Features
#### ARM template to Azure CLI scripts translator:
*Examples:*

##### Translate an ARM template to Azure CLI scripts

```
az cli-translator arm translate \
    --subscription 00000000-0000-0000-0000-000000000000 \
    --resource-group groupName \
    --template armTemplatePath \
    --parameters armParametersPath
```

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.

