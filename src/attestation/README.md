Microsoft Azure CLI 'attestation' Extension
==========================================

### Usage ###
#### Install the extension ####
Install this extension using the below CLI command
```
az extension add --name attestation
```
#### Check the version ####
```
az extension show --name attestation --query version
```
#### Connect to Azure subscription ####
```
az login
az account set -s {subs_id}
```
#### Create a resource group (or use an existing one) ####
```
az group create -n testrg -l westus
```
#### Create provider in AAD mode ####
```
az attestation create -n testatt1 -g testrg -l westus
```
#### Get default policy ####
```
az attestation policy show -n testatt1 -g testrg --attestation-type SGX-IntelSDK
```
#### Configure policy in Text format using file path ###
```
# Download the policy file: https://github.com/Azure/azure-cli-extensions/blob/master/src/attestation/azext_attestation/tests/latest/policies/text_sgx_policy.txt

az attestation policy set -n testatt1 -g testrg --attestation-type SGX-IntelSDK -f "{local_path}\text_sgx_policy.txt"
```
#### Get policy ####
```
az attestation policy show -n testatt1 -g testrg --attestation-type SGX-IntelSDK
```
#### Configure policy in unsigned JWT format using file path ####
```
# Download the policy file: https://github.com/Azure/azure-cli-extensions/blob/master/src/attestation/azext_attestation/tests/latest/policies/unsigned_jwt_sgx_policy.txt

az attestation policy set -n testatt1 -g testrg --attestation-type SGX-IntelSDK --policy-format JWT -f "{local_path}\unsigned_jwt_sgx_policy.txt"
```
#### Get policy ####
```
az attestation policy show -n testatt1 -g testrg --attestation-type SGX-IntelSDK
```

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.
