# Azure CLI cli-translator Extension #
This package is for the 'cli-translator' extension, i.e. 'az cli-translator'.

### How to use ###
Install this extension using the below CLI command
```
az extension add --name cli-translator
```

### Included Features
#### ARM template to Azure CLI scripts translator(Currently only support Compute, Network and Storage):
*Examples:*

##### Translate a local ARM template to Azure CLI scripts

> The ARM template can be downloaded in create & validation page or template page from portal.

```
az cli-translator arm translate \
    --target-subscription 00000000-0000-0000-0000-000000000000 \
    --resource-group groupName \
    --template /path/to/local/template.json \
    --parameters /path/to/local/parameters.json
```

##### Translate a remote ARM template(uri) to Azure CLI scripts

> The template.json and parameters.json used here are just samples, you can use your own ones instead.

```
az cli-translator arm translate \
    --target-subscription 00000000-0000-0000-0000-000000000000 \
    --resource-group groupName \
    --template https://raw.githubusercontent.com/Azure/azure-cli-extensions/master/src/cli-translator/samples/template.json \
    --parameters https://raw.githubusercontent.com/Azure/azure-cli-extensions/master/src/cli-translator/samples/parameters.json
```

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.

