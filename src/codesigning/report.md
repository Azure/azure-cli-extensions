# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az codesigning|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az codesigning` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az codesigning|CodeSignAccount|[commands](#CommandsInCodeSignAccount)|
|az codesigning certificate-profile|CertificateProfile|[commands](#CommandsInCertificateProfile)|
|az codesigning operation|Operations|[commands](#CommandsInOperations)|

## COMMANDS
### <a name="CommandsInCodeSignAccount">Commands in `az codesigning` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az codesigning list](#CodeSignAccountListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersCodeSignAccountListByResourceGroup)|[Example](#ExamplesCodeSignAccountListByResourceGroup)|
|[az codesigning list](#CodeSignAccountListBySubscription)|ListBySubscription|[Parameters](#ParametersCodeSignAccountListBySubscription)|[Example](#ExamplesCodeSignAccountListBySubscription)|
|[az codesigning show](#CodeSignAccountGet)|Get|[Parameters](#ParametersCodeSignAccountGet)|[Example](#ExamplesCodeSignAccountGet)|
|[az codesigning create](#CodeSignAccountCreate)|Create|[Parameters](#ParametersCodeSignAccountCreate)|[Example](#ExamplesCodeSignAccountCreate)|
|[az codesigning update](#CodeSignAccountUpdate)|Update|[Parameters](#ParametersCodeSignAccountUpdate)|[Example](#ExamplesCodeSignAccountUpdate)|
|[az codesigning delete](#CodeSignAccountDelete)|Delete|[Parameters](#ParametersCodeSignAccountDelete)|[Example](#ExamplesCodeSignAccountDelete)|

### <a name="CommandsInCertificateProfile">Commands in `az codesigning certificate-profile` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az codesigning certificate-profile list](#CertificateProfileListByCodeSignAccount)|ListByCodeSignAccount|[Parameters](#ParametersCertificateProfileListByCodeSignAccount)|[Example](#ExamplesCertificateProfileListByCodeSignAccount)|
|[az codesigning certificate-profile show](#CertificateProfileGet)|Get|[Parameters](#ParametersCertificateProfileGet)|[Example](#ExamplesCertificateProfileGet)|
|[az codesigning certificate-profile create](#CertificateProfileCreate)|Create|[Parameters](#ParametersCertificateProfileCreate)|[Example](#ExamplesCertificateProfileCreate)|
|[az codesigning certificate-profile update](#CertificateProfileUpdate)|Update|[Parameters](#ParametersCertificateProfileUpdate)|Not Found|
|[az codesigning certificate-profile delete](#CertificateProfileDelete)|Delete|[Parameters](#ParametersCertificateProfileDelete)|[Example](#ExamplesCertificateProfileDelete)|

### <a name="CommandsInOperations">Commands in `az codesigning operation` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az codesigning operation show](#OperationsGet)|Get|[Parameters](#ParametersOperationsGet)|Not Found|


## COMMAND DETAILS

### group `az codesigning`
#### <a name="CodeSignAccountListByResourceGroup">Command `az codesigning list`</a>

##### <a name="ExamplesCodeSignAccountListByResourceGroup">Example</a>
```
az codesigning list --resource-group "MyResourceGroup"
```
##### <a name="ParametersCodeSignAccountListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group under which Code Sign Account is registered|resource_group_name|resourceGroupName|

#### <a name="CodeSignAccountListBySubscription">Command `az codesigning list`</a>

##### <a name="ExamplesCodeSignAccountListBySubscription">Example</a>
```
az codesigning list
```
##### <a name="ParametersCodeSignAccountListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="CodeSignAccountGet">Command `az codesigning show`</a>

##### <a name="ExamplesCodeSignAccountGet">Example</a>
```
az codesigning show --account-name "MyAccount" --resource-group "MyResourceGroup"
```
##### <a name="ParametersCodeSignAccountGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group under which Code Sign Account is registered|resource_group_name|resourceGroupName|
|**--account-name**|string|Code Sign account name|account_name|accountName|

#### <a name="CodeSignAccountCreate">Command `az codesigning create`</a>

##### <a name="ExamplesCodeSignAccountCreate">Example</a>
```
az codesigning create --account-name "MyAccount" --location "eastus" --tags key1="value1" --resource-group \
"MyResourceGroup"
```
##### <a name="ParametersCodeSignAccountCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group under which Code Sign Account is registered|resource_group_name|resourceGroupName|
|**--account-name**|string|Code Sign account name|account_name|accountName|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--code-sign-account-properties-account-name**|string||code_sign_account_properties_account_name|accountName|
|**--account-url**|string||account_url|accountUrl|
|**--verification-status**|choice|The vetting status of the code sign account|verification_status|verificationStatus|
|**--provisioning-state**|choice|The current provisioning state|provisioning_state|provisioningState|

#### <a name="CodeSignAccountUpdate">Command `az codesigning update`</a>

##### <a name="ExamplesCodeSignAccountUpdate">Example</a>
```
az codesigning update --account-name "MyAccount" --tags key1="value1" --resource-group "MyResourceGroup"
```
##### <a name="ParametersCodeSignAccountUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group under which Code Sign Account is registered|resource_group_name|resourceGroupName|
|**--account-name**|string|Code Sign account name|account_name|accountName|
|**--tags**|dictionary|Resource tags.|tags|tags|

#### <a name="CodeSignAccountDelete">Command `az codesigning delete`</a>

##### <a name="ExamplesCodeSignAccountDelete">Example</a>
```
az codesigning delete --account-name "MyAccount" --resource-group "MyResourceGroup"
```
##### <a name="ParametersCodeSignAccountDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group under which Code Sign Account is registered|resource_group_name|resourceGroupName|
|**--account-name**|string|Code Sign account name|account_name|accountName|

### group `az codesigning certificate-profile`
#### <a name="CertificateProfileListByCodeSignAccount">Command `az codesigning certificate-profile list`</a>

##### <a name="ExamplesCertificateProfileListByCodeSignAccount">Example</a>
```
az codesigning certificate-profile list --account-name "MyAccount" --resource-group "MyResourceGroup"
```
##### <a name="ParametersCertificateProfileListByCodeSignAccount">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group under which Code Sign Account is registered|resource_group_name|resourceGroupName|
|**--account-name**|string|Code Sign account name|account_name|accountName|

#### <a name="CertificateProfileGet">Command `az codesigning certificate-profile show`</a>

##### <a name="ExamplesCertificateProfileGet">Example</a>
```
az codesigning certificate-profile show --account-name "MyAccount" --profile-name "profileA" --resource-group \
"MyResourceGroup"
```
##### <a name="ParametersCertificateProfileGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group under which Code Sign Account is registered|resource_group_name|resourceGroupName|
|**--account-name**|string|Code Sign account name|account_name|accountName|
|**--profile-name**|string|Certificate profile name|profile_name|profileName|

#### <a name="CertificateProfileCreate">Command `az codesigning certificate-profile create`</a>

##### <a name="ExamplesCertificateProfileCreate">Example</a>
```
az codesigning certificate-profile create --account-name "MyAccount" --profile-name "profileA" --resource-group \
"MyResourceGroup"
```
##### <a name="ParametersCertificateProfileCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group under which Code Sign Account is registered|resource_group_name|resourceGroupName|
|**--account-name**|string|Code Sign account name|account_name|accountName|
|**--profile-name**|string|Certificate profile name|profile_name|profileName|
|**--certificate-profile-properties-profile-name**|string||certificate_profile_properties_profile_name|profileName|
|**--profile-type**|choice||profile_type|profileType|
|**--common-name**|string||common_name|commonName|
|**--subject-alternative-name**|string||subject_alternative_name|subjectAlternativeName|
|**--provisioning-state**|choice|The current provisioning state|provisioning_state|provisioningState|

#### <a name="CertificateProfileUpdate">Command `az codesigning certificate-profile update`</a>

##### <a name="ParametersCertificateProfileUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group under which Code Sign Account is registered|resource_group_name|resourceGroupName|
|**--account-name**|string|Code Sign account name|account_name|accountName|
|**--profile-name**|string|Certificate profile name|profile_name|profileName|
|**--certificate-profile-properties-profile-name**|string||certificate_profile_properties_profile_name|profileName|
|**--profile-type**|choice||profile_type|profileType|
|**--common-name**|string||common_name|commonName|
|**--subject-alternative-name**|string||subject_alternative_name|subjectAlternativeName|
|**--provisioning-state**|choice|The current provisioning state|provisioning_state|provisioningState|

#### <a name="CertificateProfileDelete">Command `az codesigning certificate-profile delete`</a>

##### <a name="ExamplesCertificateProfileDelete">Example</a>
```
az codesigning certificate-profile delete --account-name "MyAccount" --profile-name "profileA" --resource-group \
"MyResourceGroup"
```
##### <a name="ParametersCertificateProfileDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group under which Code Sign Account is registered|resource_group_name|resourceGroupName|
|**--account-name**|string|Code Sign account name|account_name|accountName|
|**--profile-name**|string|Certificate profile name|profile_name|profileName|

### group `az codesigning operation`
#### <a name="OperationsGet">Command `az codesigning operation show`</a>

##### <a name="ParametersOperationsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|