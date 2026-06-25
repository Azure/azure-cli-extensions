# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az codesigning|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az codesigning` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az codesigning|CodeSigningAccount|[commands](#CommandsInCodeSigningAccount)|
|az codesigning certificate-profile|CertificateProfile|[commands](#CommandsInCertificateProfile)|

## COMMANDS
### <a name="CommandsInCodeSigningAccount">Commands in `az codesigning` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az codesigning list](#CodeSigningAccountListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersCodeSigningAccountListByResourceGroup)|[Example](#ExamplesCodeSigningAccountListByResourceGroup)|
|[az codesigning list](#CodeSigningAccountListBySubscription)|ListBySubscription|[Parameters](#ParametersCodeSigningAccountListBySubscription)|[Example](#ExamplesCodeSigningAccountListBySubscription)|
|[az codesigning show](#CodeSigningAccountGet)|Get|[Parameters](#ParametersCodeSigningAccountGet)|[Example](#ExamplesCodeSigningAccountGet)|
|[az codesigning create](#CodeSigningAccountCreate)|Create|[Parameters](#ParametersCodeSigningAccountCreate)|[Example](#ExamplesCodeSigningAccountCreate)|
|[az codesigning update](#CodeSigningAccountUpdate)|Update|[Parameters](#ParametersCodeSigningAccountUpdate)|[Example](#ExamplesCodeSigningAccountUpdate)|
|[az codesigning delete](#CodeSigningAccountDelete)|Delete|[Parameters](#ParametersCodeSigningAccountDelete)|[Example](#ExamplesCodeSigningAccountDelete)|

### <a name="CommandsInCertificateProfile">Commands in `az codesigning certificate-profile` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az codesigning certificate-profile list](#CertificateProfileListByCodeSigningAccount)|ListByCodeSigningAccount|[Parameters](#ParametersCertificateProfileListByCodeSigningAccount)|[Example](#ExamplesCertificateProfileListByCodeSigningAccount)|
|[az codesigning certificate-profile show](#CertificateProfileGet)|Get|[Parameters](#ParametersCertificateProfileGet)|[Example](#ExamplesCertificateProfileGet)|
|[az codesigning certificate-profile create](#CertificateProfileCreate)|Create|[Parameters](#ParametersCertificateProfileCreate)|[Example](#ExamplesCertificateProfileCreate)|
|[az codesigning certificate-profile delete](#CertificateProfileDelete)|Delete|[Parameters](#ParametersCertificateProfileDelete)|[Example](#ExamplesCertificateProfileDelete)|


## COMMAND DETAILS

### group `az codesigning`
#### <a name="CodeSigningAccountListByResourceGroup">Command `az codesigning list`</a>

##### <a name="ExamplesCodeSigningAccountListByResourceGroup">Example</a>
```
az codesigning list --resource-group "MyResourceGroup"
```
##### <a name="ParametersCodeSigningAccountListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="CodeSigningAccountListBySubscription">Command `az codesigning list`</a>

##### <a name="ExamplesCodeSigningAccountListBySubscription">Example</a>
```
az codesigning list
```
##### <a name="ParametersCodeSigningAccountListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="CodeSigningAccountGet">Command `az codesigning show`</a>

##### <a name="ExamplesCodeSigningAccountGet">Example</a>
```
az codesigning show --name "MyAccount" --resource-group "MyResourceGroup"
```
##### <a name="ParametersCodeSigningAccountGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--name**|string|Code Signing account name|name|accountName|

#### <a name="CodeSigningAccountCreate">Command `az codesigning create`</a>

##### <a name="ExamplesCodeSigningAccountCreate">Example</a>
```
az codesigning create --name "MyAccount" --location "eastus" --resource-group "MyResourceGroup"
```
##### <a name="ParametersCodeSigningAccountCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--name**|string|Code Signing account name|name|accountName|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--location**|string|The geo-location where the resource lives|location|location|

#### <a name="CodeSigningAccountUpdate">Command `az codesigning update`</a>

##### <a name="ExamplesCodeSigningAccountUpdate">Example</a>
```
az codesigning update --name "MyAccount" --tags key1="value1" --resource-group "MyResourceGroup"
```
##### <a name="ParametersCodeSigningAccountUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--name**|string|Code Signing account name|name|accountName|
|**--tags**|dictionary|Resource tags.|tags|tags|

#### <a name="CodeSigningAccountDelete">Command `az codesigning delete`</a>

##### <a name="ExamplesCodeSigningAccountDelete">Example</a>
```
az codesigning delete --name "MyAccount" --resource-group "MyResourceGroup"
```
##### <a name="ParametersCodeSigningAccountDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--name**|string|Code Signing account name|name|accountName|

### group `az codesigning certificate-profile`
#### <a name="CertificateProfileListByCodeSigningAccount">Command `az codesigning certificate-profile list`</a>

##### <a name="ExamplesCertificateProfileListByCodeSigningAccount">Example</a>
```
az codesigning certificate-profile list --account-name "MyAccount" --resource-group "MyResourceGroup"
```
##### <a name="ParametersCertificateProfileListByCodeSigningAccount">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|Code Signing account name|account_name|accountName|

#### <a name="CertificateProfileGet">Command `az codesigning certificate-profile show`</a>

##### <a name="ExamplesCertificateProfileGet">Example</a>
```
az codesigning certificate-profile show --account-name "MyAccount" --name "profileA" --resource-group \
"MyResourceGroup"
```
##### <a name="ParametersCertificateProfileGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|Code Signing account name|account_name|accountName|
|**--name**|string|Certificate profile name|name|profileName|

#### <a name="CertificateProfileCreate">Command `az codesigning certificate-profile create`</a>

##### <a name="ExamplesCertificateProfileCreate">Example</a>
```
az codesigning certificate-profile create --account-name "MyAccount" --common-name "Contoso Inc" --organization \
"Contoso Inc" --name "profileA" --resource-group "MyResourceGroup"
```
##### <a name="ParametersCertificateProfileCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|Code Signing account name|account_name|accountName|
|**--name**|string|Certificate profile name|name|profileName|
|**--common-name**|string|Used as CN in the subject name of the certificate|common_name|commonName|
|**--organization**|string|Used as O in the subject name of the certificate|organization|organization|

#### <a name="CertificateProfileDelete">Command `az codesigning certificate-profile delete`</a>

##### <a name="ExamplesCertificateProfileDelete">Example</a>
```
az codesigning certificate-profile delete --account-name "MyAccount" --name "profileA" --resource-group \
"MyResourceGroup"
```
##### <a name="ParametersCertificateProfileDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|Code Signing account name|account_name|accountName|
|**--name**|string|Certificate profile name|name|profileName|
