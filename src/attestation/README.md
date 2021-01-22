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
Download the policy file: https://github.com/Azure/azure-cli-extensions/blob/master/src/attestation/azext_attestation/tests/latest/policies/text_sgx_policy.txt

Content:
```
version= 1.0;
authorizationrules {
[ type=="$is-debuggable", value==false ]
&& [ type=="$product-id", value==4639 ]
&& [ type=="$min-svn", value>= 0 ]
&& [ type=="$sgx-mrsigner", value=="E31C9E505F37A58DE09335075FC8591254313EB20BB1A27E5443CC450B6E33E5"]
=> permit();
};
 issuancerules {
c:[ type=="$sgx-mrsigner" ] => issue(type="sgx-mrsigner",
value=c.value);
 c1:[type=="maa-ehd"] => issue(type="aas-ehd", value=c1.value);
 };
```
Run the command:
```
az attestation policy set -n testatt1 -g testrg --attestation-type SGX-IntelSDK -f "{local_path}\text_sgx_policy.txt"
```
#### Get policy ####
```
az attestation policy show -n testatt1 -g testrg --attestation-type SGX-IntelSDK
```
#### Configure policy in unsigned JWT format using file path ####
Download the policy file: https://github.com/Azure/azure-cli-extensions/blob/master/src/attestation/azext_attestation/tests/latest/policies/unsigned_jwt_sgx_policy.txt

Content:
```
eyJhbGciOiJub25lIn0.eyJBdHRlc3RhdGlvblBvbGljeSI6ICJkbVZ5YzJsdmJqMGdNUzR3TzJGMWRHaHZjbWw2WVhScGIyNXlkV3hsYzN0ak9sdDBlWEJsUFQwaUpHbHpMV1JsWW5WbloyRmliR1VpWFNBOVBpQndaWEp0YVhRb0tUdDlPMmx6YzNWaGJtTmxjblZzWlhON1l6cGJkSGx3WlQwOUlpUnBjeTFrWldKMVoyZGhZbXhsSWwwZ1BUNGdhWE56ZFdVb2RIbHdaVDBpYVhNdFpHVmlkV2RuWVdKc1pTSXNJSFpoYkhWbFBXTXVkbUZzZFdVcE8yTTZXM1I1Y0dVOVBTSWtjMmQ0TFcxeWMybG5ibVZ5SWwwZ1BUNGdhWE56ZFdVb2RIbHdaVDBpYzJkNExXMXljMmxuYm1WeUlpd2dkbUZzZFdVOVl5NTJZV3gxWlNrN1l6cGJkSGx3WlQwOUlpUnpaM2d0YlhKbGJtTnNZWFpsSWwwZ1BUNGdhWE56ZFdVb2RIbHdaVDBpYzJkNExXMXlaVzVqYkdGMlpTSXNJSFpoYkhWbFBXTXVkbUZzZFdVcE8yTTZXM1I1Y0dVOVBTSWtjSEp2WkhWamRDMXBaQ0pkSUQwLUlHbHpjM1ZsS0hSNWNHVTlJbkJ5YjJSMVkzUXRhV1FpTENCMllXeDFaVDFqTG5aaGJIVmxLVHRqT2x0MGVYQmxQVDBpSkhOMmJpSmRJRDAtSUdsemMzVmxLSFI1Y0dVOUluTjJiaUlzSUhaaGJIVmxQV011ZG1Gc2RXVXBPMk02VzNSNWNHVTlQU0lrZEdWbElsMGdQVDRnYVhOemRXVW9kSGx3WlQwaWRHVmxJaXdnZG1Gc2RXVTlZeTUyWVd4MVpTazdmVHMifQ.
```
Run the command:
```
az attestation policy set -n testatt1 -g testrg --attestation-type SGX-IntelSDK --policy-format JWT -f "{local_path}\unsigned_jwt_sgx_policy.txt"
```
#### Get policy ####
```
az attestation policy show -n testatt1 -g testrg --attestation-type SGX-IntelSDK
```

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.
