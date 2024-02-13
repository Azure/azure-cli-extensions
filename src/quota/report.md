# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az quota|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az quota` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az quota|Quota|[commands](#CommandsInQuota)|
|az quota quotaoperation|QuotaOperation|[commands](#CommandsInQuotaOperation)|
|az quota quotarequeststatus|QuotaRequestStatus|[commands](#CommandsInQuotaRequestStatus)|
|az quota usage|Usages|[commands](#CommandsInUsages)|

## COMMANDS
### <a name="CommandsInQuota">Commands in `az quota` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az quota list](#QuotaList)|List|[Parameters](#ParametersQuotaList)|[Example](#ExamplesQuotaList)|
|[az quota show](#QuotaGet)|Get|[Parameters](#ParametersQuotaGet)|[Example](#ExamplesQuotaGet)|
|[az quota create](#QuotaCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersQuotaCreateOrUpdate#Create)|[Example](#ExamplesQuotaCreateOrUpdate#Create)|
|[az quota update](#QuotaUpdate)|Update|[Parameters](#ParametersQuotaUpdate)|[Example](#ExamplesQuotaUpdate)|

### <a name="CommandsInQuotaOperation">Commands in `az quota quotaoperation` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az quota quotaoperation list](#QuotaOperationList)|List|[Parameters](#ParametersQuotaOperationList)|[Example](#ExamplesQuotaOperationList)|

### <a name="CommandsInQuotaRequestStatus">Commands in `az quota quotarequeststatus` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az quota quotarequeststatus list](#QuotaRequestStatusList)|List|[Parameters](#ParametersQuotaRequestStatusList)|[Example](#ExamplesQuotaRequestStatusList)|
|[az quota quotarequeststatus show](#QuotaRequestStatusGet)|Get|[Parameters](#ParametersQuotaRequestStatusGet)|[Example](#ExamplesQuotaRequestStatusGet)|

### <a name="CommandsInUsages">Commands in `az quota usage` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az quota usage list](#UsagesList)|List|[Parameters](#ParametersUsagesList)|[Example](#ExamplesUsagesList)|
|[az quota usage show](#UsagesGet)|Get|[Parameters](#ParametersUsagesGet)|[Example](#ExamplesUsagesGet)|


## COMMAND DETAILS
### group `az quota`
#### <a name="QuotaList">Command `az quota list`</a>

##### <a name="ExamplesQuotaList">Example</a>
```
az quota list --scope "subscriptions/00000000-0000-0000-0000-000000000000/providers/Microsoft.Compute/locations/eastus"
az quota list --scope "subscriptions/00000000-0000-0000-0000-000000000000/providers/Microsoft.Network/locations/eastus"
az quota list --scope "subscriptions/00000000-0000-0000-0000-000000000000/providers/Microsoft.MachineLearningServices/l\
ocations/eastus"
```
##### <a name="ParametersQuotaList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The target Azure resource URI. For example, `/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/qms-test/providers/Microsoft.Batch/batchAccounts/testAccount/`. This is the target Azure resource URI for the List GET operation. If a `{resourceName}` is added after `/quotas`, then it's the target Azure resource URI in the GET operation for the specific resource.|scope|scope|

#### <a name="QuotaGet">Command `az quota show`</a>

##### <a name="ExamplesQuotaGet">Example</a>
```
az quota show --resource-name "standardNDSFamily" --scope "subscriptions/00000000-0000-0000-0000-000000000000/providers\
/Microsoft.Compute/locations/eastus"
az quota show --resource-name "MinPublicIpInterNetworkPrefixLength" --scope "subscriptions/00000000-0000-0000-0000-0000\
00000000/providers/Microsoft.Network/locations/eastus"
```
##### <a name="ParametersQuotaGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-name**|string|Resource name for a given resource provider. For example: - SKU name for Microsoft.Compute - SKU or TotalLowPriorityCores for Microsoft.MachineLearningServices  For Microsoft.Network PublicIPAddresses.|resource_name|resourceName|
|**--scope**|string|The target Azure resource URI. For example, `/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/qms-test/providers/Microsoft.Batch/batchAccounts/testAccount/`. This is the target Azure resource URI for the List GET operation. If a `{resourceName}` is added after `/quotas`, then it's the target Azure resource URI in the GET operation for the specific resource.|scope|scope|

#### <a name="QuotaCreateOrUpdate#Create">Command `az quota create`</a>

##### <a name="ExamplesQuotaCreateOrUpdate#Create">Example</a>
```
az quota create --properties "{\\"name\\":{\\"value\\":\\"MinPublicIpInterNetworkPrefixLength\\"},\\"limit\\":{\\"limit\
ObjectType\\":\\"LimitValue\\",\\"value\\":10},\\"resourceType\\":\\"MinPublicIpInterNetworkPrefixLength\\"}" \
--resource-name "MinPublicIpInterNetworkPrefixLength" --scope "subscriptions/D7EC67B3-7657-4966-BFFC-41EFD36BAAB3/provi\
ders/Microsoft.Network/locations/eastus"
az quota create --properties "{\\"name\\":{\\"value\\":\\"StandardSkuPublicIpAddresses\\"},\\"limit\\":{\\"limitObjectT\
ype\\":\\"LimitValue\\",\\"value\\":10},\\"resourceType\\":\\"PublicIpAddresses\\"}" --resource-name \
"StandardSkuPublicIpAddresses" --scope "subscriptions/D7EC67B3-7657-4966-BFFC-41EFD36BAAB3/providers/Microsoft.Network/\
locations/eastus"
az quota create --properties "{\\"name\\":{\\"value\\":\\"standardFSv2Family\\"},\\"limit\\":{\\"limitObjectType\\":\\"\
LimitValue\\",\\"value\\":10}}" --resource-name "standardFSv2Family" --scope "subscriptions/D7EC67B3-7657-4966-BFFC-41E\
FD36BAAB3/providers/Microsoft.Compute/locations/eastus"
az quota create --properties "{\\"name\\":{\\"value\\":\\"TotalLowPriorityCores\\"},\\"limit\\":{\\"limitObjectType\\":\
\\"LimitValue\\",\\"value\\":10},\\"resourceType\\":\\"lowPriority\\"}" --resource-name "TotalLowPriorityCores" \
--scope "subscriptions/D7EC67B3-7657-4966-BFFC-41EFD36BAAB3/providers/Microsoft.MachineLearningServices/locations/eastu\
s"
```
##### <a name="ParametersQuotaCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-name**|string|Resource name for a given resource provider. For example: - SKU name for Microsoft.Compute - SKU or TotalLowPriorityCores for Microsoft.MachineLearningServices  For Microsoft.Network PublicIPAddresses.|resource_name|resourceName|
|**--scope**|string|The target Azure resource URI. For example, `/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/qms-test/providers/Microsoft.Batch/batchAccounts/testAccount/`. This is the target Azure resource URI for the List GET operation. If a `{resourceName}` is added after `/quotas`, then it's the target Azure resource URI in the GET operation for the specific resource.|scope|scope|
|**--limitobject**|object|The resource quota limit value.|limitobject|LimitObject|
|**--resource-type**|string|Resource type name.|resource_type|resourceType|
|**--properties**|any|Additional properties for the specific resource provider.|properties|properties|
|**--value**|string|Resource name.|value|value|

#### <a name="QuotaUpdate">Command `az quota update`</a>

##### <a name="ExamplesQuotaUpdate">Example</a>
```
az quota update --properties "{\\"name\\":{\\"value\\":\\"standardFSv2Family\\"},\\"limit\\":{\\"limitObjectType\\":\\"\
LimitValue\\",\\"value\\":10}}" --resource-name "standardFSv2Family" --scope "subscriptions/D7EC67B3-7657-4966-BFFC-41E\
FD36BAAB3/providers/Microsoft.Compute/locations/eastus"
az quota update --properties "{\\"name\\":{\\"value\\":\\"MinPublicIpInterNetworkPrefixLength\\"},\\"limit\\":{\\"limit\
ObjectType\\":\\"LimitValue\\",\\"value\\":10},\\"resourceType\\":\\"MinPublicIpInterNetworkPrefixLength\\"}" \
--resource-name "MinPublicIpInterNetworkPrefixLength" --scope "subscriptions/D7EC67B3-7657-4966-BFFC-41EFD36BAAB3/provi\
ders/Microsoft.Network/locations/eastus"
```
##### <a name="ParametersQuotaUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-name**|string|Resource name for a given resource provider. For example: - SKU name for Microsoft.Compute - SKU or TotalLowPriorityCores for Microsoft.MachineLearningServices  For Microsoft.Network PublicIPAddresses.|resource_name|resourceName|
|**--scope**|string|The target Azure resource URI. For example, `/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/qms-test/providers/Microsoft.Batch/batchAccounts/testAccount/`. This is the target Azure resource URI for the List GET operation. If a `{resourceName}` is added after `/quotas`, then it's the target Azure resource URI in the GET operation for the specific resource.|scope|scope|
|**--limitobject**|object|The resource quota limit value.|limitobject|LimitObject|
|**--resource-type**|string|Resource type name.|resource_type|resourceType|
|**--properties**|any|Additional properties for the specific resource provider.|properties|properties|
|**--value**|string|Resource name.|value|value|

### group `az quota quotaoperation`
#### <a name="QuotaOperationList">Command `az quota quotaoperation list`</a>

##### <a name="ExamplesQuotaOperationList">Example</a>
```
az quota quotaoperation list
```
##### <a name="ParametersQuotaOperationList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

### group `az quota quotarequeststatus`
#### <a name="QuotaRequestStatusList">Command `az quota quotarequeststatus list`</a>

##### <a name="ExamplesQuotaRequestStatusList">Example</a>
```
az quota quotarequeststatus list --scope "subscriptions/D7EC67B3-7657-4966-BFFC-41EFD36BAAB3/providers/Microsoft.Comput\
e/locations/eastus"
```
##### <a name="ParametersQuotaRequestStatusList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The target Azure resource URI. For example, `/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/qms-test/providers/Microsoft.Batch/batchAccounts/testAccount/`. This is the target Azure resource URI for the List GET operation. If a `{resourceName}` is added after `/quotas`, then it's the target Azure resource URI in the GET operation for the specific resource.|scope|scope|
|**--filter**|string|| Field                    | Supported operators   |---------------------|------------------------  |requestSubmitTime | ge, le, eq, gt, lt  |provisioningState eq {QuotaRequestState}  |resourceName eq {resourceName} |filter|$filter|
|**--top**|integer|Number of records to return.|top|$top|
|**--skiptoken**|string|The **Skiptoken** parameter is used only if a previous operation returned a partial result. If a previous response contains a **nextLink** element, its value includes a **skiptoken** parameter that specifies a starting point to use for subsequent calls.|skiptoken|$skiptoken|

#### <a name="QuotaRequestStatusGet">Command `az quota quotarequeststatus show`</a>

##### <a name="ExamplesQuotaRequestStatusGet">Example</a>
```
az quota quotarequeststatus show --id "2B5C8515-37D8-4B6A-879B-CD641A2CF605" --scope "subscriptions/00000000-0000-0000-\
0000-000000000000/providers/Microsoft.Compute/locations/eastus"
az quota quotarequeststatus show --id "2B5C8515-37D8-4B6A-879B-CD641A2CF605" --scope "subscriptions/00000000-0000-0000-\
0000-000000000000/providers/Microsoft.Compute/locations/eastus"
az quota quotarequeststatus show --id "2B5C8515-37D8-4B6A-879B-CD641A2CF605" --scope "subscriptions/D7EC67B3-7657-4966-\
BFFC-41EFD36BAAB3/providers/Microsoft.Compute/locations/eastus"
```
##### <a name="ParametersQuotaRequestStatusGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--id**|string|Quota request ID.|id|id|
|**--scope**|string|The target Azure resource URI. For example, `/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/qms-test/providers/Microsoft.Batch/batchAccounts/testAccount/`. This is the target Azure resource URI for the List GET operation. If a `{resourceName}` is added after `/quotas`, then it's the target Azure resource URI in the GET operation for the specific resource.|scope|scope|

### group `az quota usage`
#### <a name="UsagesList">Command `az quota usage list`</a>

##### <a name="ExamplesUsagesList">Example</a>
```
az quota usage list --scope "subscriptions/00000000-0000-0000-0000-000000000000/providers/Microsoft.Compute/locations/e\
astus"
az quota usage list --scope "subscriptions/00000000-0000-0000-0000-000000000000/providers/Microsoft.Network/locations/e\
astus"
az quota usage list --scope "subscriptions/00000000-0000-0000-0000-000000000000/providers/Microsoft.MachineLearningServ\
ices/locations/eastus"
```
##### <a name="ParametersUsagesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The target Azure resource URI. For example, `/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/qms-test/providers/Microsoft.Batch/batchAccounts/testAccount/`. This is the target Azure resource URI for the List GET operation. If a `{resourceName}` is added after `/quotas`, then it's the target Azure resource URI in the GET operation for the specific resource.|scope|scope|

#### <a name="UsagesGet">Command `az quota usage show`</a>

##### <a name="ExamplesUsagesGet">Example</a>
```
az quota usage show --resource-name "standardNDSFamily" --scope "subscriptions/00000000-0000-0000-0000-000000000000/pro\
viders/Microsoft.Compute/locations/eastus"
az quota usage show --resource-name "MinPublicIpInterNetworkPrefixLength" --scope "subscriptions/00000000-0000-0000-000\
0-000000000000/providers/Microsoft.Network/locations/eastus"
```
##### <a name="ParametersUsagesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-name**|string|Resource name for a given resource provider. For example: - SKU name for Microsoft.Compute - SKU or TotalLowPriorityCores for Microsoft.MachineLearningServices  For Microsoft.Network PublicIPAddresses.|resource_name|resourceName|
|**--scope**|string|The target Azure resource URI. For example, `/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/qms-test/providers/Microsoft.Batch/batchAccounts/testAccount/`. This is the target Azure resource URI for the List GET operation. If a `{resourceName}` is added after `/quotas`, then it's the target Azure resource URI in the GET operation for the specific resource.|scope|scope|
