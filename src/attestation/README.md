Microsoft Azure CLI 'attestation' Extension
==========================================

This package is for the 'attestation' extension, i.e. `az attestation`.
More info on [Microsoft Azure cloud security attestation](https://azure.microsoft.com/en-us/blog/microsoft-azure-updates-cloud-security-attestation/).

### How to use ###
Install this extension using the below CLI command
```
az extension add --name attestation
```
To see command arguments details, should run the command with `-h`.
Example:
```
az attestation create -h
```
```
az attestation list -h
```
```
az attestation show -h
```
```
az attestation delete -h
```

### Included features ###
#### Create an attestation ####
The parameter `certs_input_path` is a path to your certificates pem file, it conforms to x5c in [RFC7517](https://tools.ietf.org/html/rfc7517#section-4.7).

Example:
```
az attestation create \
--location "eastus2" \
--provider-name "myattestationprovider" \
--resource-group "MyResourceGroup"
```
Notice:
May not all the values from `az account list-locations` are supported to create an attetation right now, more regions will be added in the future.

#### List all attestations ####
Example:
List all attestations in a subscription
```
az attestation list
```
List all attestations in a resource group
```
az attestation list \
--resource-group "MyResourceGroup"
```

#### Show the status of one attestation ####
Example:
```
az attestation show \
--provider-name "myattestationprovider" \
--resource-group "MyResourceGroup"
```

#### Delete an attestation ####
Example:
```
az attestation delete \
--name "myattestationprovider" \
--resource-group "MyResourceGroup"
```

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.
