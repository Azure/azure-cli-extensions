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
|az quota quota-request-status|QuotaRequestStatus|[commands](#CommandsInQuotaRequestStatus)|
|az quota quota-resource-provider|QuotaResourceProviders|[commands](#CommandsInQuotaResourceProviders)|
|az quota operation|Operation|[commands](#CommandsInOperation)|

## COMMANDS
### <a name="CommandsInQuota">Commands in `az quota` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az quota list](#QuotaList)|List|[Parameters](#ParametersQuotaList)|[Example](#ExamplesQuotaList)|
|[az quota show](#QuotaGet)|Get|[Parameters](#ParametersQuotaGet)|[Example](#ExamplesQuotaGet)|
|[az quota create](#QuotaCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersQuotaCreateOrUpdate#Create)|[Example](#ExamplesQuotaCreateOrUpdate#Create)|
|[az quota update](#QuotaUpdate)|Update|[Parameters](#ParametersQuotaUpdate)|[Example](#ExamplesQuotaUpdate)|

### <a name="CommandsInOperation">Commands in `az quota operation` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az quota operation list](#OperationList)|List|[Parameters](#ParametersOperationList)|[Example](#ExamplesOperationList)|

### <a name="CommandsInQuotaRequestStatus">Commands in `az quota quota-request-status` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az quota quota-request-status list](#QuotaRequestStatusList)|List|[Parameters](#ParametersQuotaRequestStatusList)|[Example](#ExamplesQuotaRequestStatusList)|
|[az quota quota-request-status show](#QuotaRequestStatusGet)|Get|[Parameters](#ParametersQuotaRequestStatusGet)|[Example](#ExamplesQuotaRequestStatusGet)|

### <a name="CommandsInQuotaResourceProviders">Commands in `az quota quota-resource-provider` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az quota quota-resource-provider list](#QuotaResourceProvidersList)|List|[Parameters](#ParametersQuotaResourceProvidersList)|[Example](#ExamplesQuotaResourceProvidersList)|


## COMMAND DETAILS

### group `az quota`
#### <a name="QuotaList">Command `az quota list`</a>

##### <a name="ExamplesQuotaList">Example</a>
```
az quota list --scope "subscriptions/00000000-0000-0000-0000-000000000000/providers/Microsoft.Compute/locations/eastus"
```
##### <a name="ExamplesQuotaList">Example</a>
```
az quota list --scope "subscriptions/00000000-0000-0000-0000-000000000000/providers/Microsoft.MachineLearningServices/l\
ocations/eastus"
```
##### <a name="ParametersQuotaList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The target Azure resource URI. For example, `/subscriptions/9f6cce51-6baf-4de5-a3c4-6f58b85315b9/resourceGroups/qms-test/providers/Microsoft.Batch/batchAccounts/testAccount/`. This is the target Azure resource URI for the List GET operation. If a `{resourceName}` is added after `/quotaLimits`, then it's the target Azure resource URI in the GET operation for the specific resource.|scope|scope|

#### <a name="QuotaGet">Command `az quota show`</a>

##### <a name="ExamplesQuotaGet">Example</a>
```
az quota show --resource-name "standardNDSFamily" --scope "subscriptions/00000000-0000-0000-0000-000000000000/providers\
/Microsoft.Compute/locations/eastus"
```
##### <a name="ParametersQuotaGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-name**|string|Resource name for a given resource provider. For example: - SKU name for Microsoft.Compute - Sku or TotalLowPriorityCores for Microsoft.MachineLearningServices|resource_name|resourceName|
|**--scope**|string|The target Azure resource URI. For example, `/subscriptions/9f6cce51-6baf-4de5-a3c4-6f58b85315b9/resourceGroups/qms-test/providers/Microsoft.Batch/batchAccounts/testAccount/`. This is the target Azure resource URI for the List GET operation. If a `{resourceName}` is added after `/quotaLimits`, then it's the target Azure resource URI in the GET operation for the specific resource.|scope|scope|

#### <a name="QuotaCreateOrUpdate#Create">Command `az quota create`</a>

##### <a name="ExamplesQuotaCreateOrUpdate#Create">Example</a>
```
az quota create --properties "{\\"name\\":{\\"value\\":\\"standardFSv2Family\\"},\\"limit\\":200}" --resource-name \
"standardFSv2Family" --scope "subscriptions/D7EC67B3-7657-4966-BFFC-41EFD36BAAB3/providers/Microsoft.Compute/locations/\
eastus"
```
##### <a name="ExamplesQuotaCreateOrUpdate#Create">Example</a>
```
az quota create --properties "{\\"name\\":{\\"value\\":\\"standardFSv2Family\\"},\\"limit\\":200}" --resource-name \
"standardFSv2Family" --scope "subscriptions/D7EC67B3-7657-4966-BFFC-41EFD36BAAB3/providers/Microsoft.Compute/locations/\
eastus"
```
##### <a name="ExamplesQuotaCreateOrUpdate#Create">Example</a>
```
az quota create --properties "{\\"name\\":{\\"value\\":\\"TotalLowPriorityCores\\"},\\"limit\\":200,\\"resourceType\\":\
\\"lowPriority\\"}" --resource-name "TotalLowPriorityCores" --scope "subscriptions/D7EC67B3-7657-4966-BFFC-41EFD36BAAB3\
/providers/Microsoft.MachineLearningServices/locations/eastus"
```
##### <a name="ParametersQuotaCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-name**|string|Resource name for a given resource provider. For example: - SKU name for Microsoft.Compute - Sku or TotalLowPriorityCores for Microsoft.MachineLearningServices|resource_name|resourceName|
|**--scope**|string|The target Azure resource URI. For example, `/subscriptions/9f6cce51-6baf-4de5-a3c4-6f58b85315b9/resourceGroups/qms-test/providers/Microsoft.Batch/batchAccounts/testAccount/`. This is the target Azure resource URI for the List GET operation. If a `{resourceName}` is added after `/quotaLimits`, then it's the target Azure resource URI in the GET operation for the specific resource.|scope|scope|
|**--limit**|integer|Quota limit.|limit|limit|
|**--resource-type**|choice|Resource type name.|resource_type|resourceType|
|**--properties**|any|Additional properties for the specific resource provider.|properties|properties|
|**--value**|string|Resource name.|value|value|

#### <a name="QuotaUpdate">Command `az quota update`</a>

##### <a name="ExamplesQuotaUpdate">Example</a>
```
az quota update --properties "{\\"name\\":{\\"value\\":\\"standardFSv2Family\\"},\\"limit\\":200}" --resource-name \
"standardFSv2Family" --scope "subscriptions/D7EC67B3-7657-4966-BFFC-41EFD36BAAB3/providers/Microsoft.Compute/locations/\
eastus"
```
##### <a name="ParametersQuotaUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-name**|string|Resource name for a given resource provider. For example: - SKU name for Microsoft.Compute - Sku or TotalLowPriorityCores for Microsoft.MachineLearningServices|resource_name|resourceName|
|**--scope**|string|The target Azure resource URI. For example, `/subscriptions/9f6cce51-6baf-4de5-a3c4-6f58b85315b9/resourceGroups/qms-test/providers/Microsoft.Batch/batchAccounts/testAccount/`. This is the target Azure resource URI for the List GET operation. If a `{resourceName}` is added after `/quotaLimits`, then it's the target Azure resource URI in the GET operation for the specific resource.|scope|scope|
|**--limit**|integer|Quota limit.|limit|limit|
|**--resource-type**|choice|Resource type name.|resource_type|resourceType|
|**--properties**|any|Additional properties for the specific resource provider.|properties|properties|
|**--value**|string|Resource name.|value|value|

### group `az quota operation`
#### <a name="OperationList">Command `az quota operation list`</a>

##### <a name="ExamplesOperationList">Example</a>
```
az quota operation list
```
##### <a name="ParametersOperationList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
### group `az quota quota-request-status`
#### <a name="QuotaRequestStatusList">Command `az quota quota-request-status list`</a>

##### <a name="ExamplesQuotaRequestStatusList">Example</a>
```
az quota quota-request-status list --scope "subscriptions/D7EC67B3-7657-4966-BFFC-41EFD36BAAB3/providers/Microsoft.Comp\
ute/locations/eastus"
```
##### <a name="ParametersQuotaRequestStatusList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The target Azure resource URI. For example, `/subscriptions/9f6cce51-6baf-4de5-a3c4-6f58b85315b9/resourceGroups/qms-test/providers/Microsoft.Batch/batchAccounts/testAccount/`. This is the target Azure resource URI for the List GET operation. If a `{resourceName}` is added after `/quotaLimits`, then it's the target Azure resource URI in the GET operation for the specific resource.|scope|scope|
|**--filter**|string|| Field                    | Supported operators   |---------------------|------------------------  |requestSubmitTime | ge, le, eq, gt, lt  |provisioningState eq {QuotaRequestState}  |resourceName eq {resourceName} |filter|$filter|
|**--top**|integer|Number of records to return.|top|$top|
|**--skiptoken**|string|The **Skiptoken** parameter is used only if a previous operation returned a partial result. If a previous response contains a **nextLink** element, the value of the **nextLink** element includes a **skiptoken** parameter that specifies a starting point to use for subsequent calls.|skiptoken|$skiptoken|

#### <a name="QuotaRequestStatusGet">Command `az quota quota-request-status show`</a>

##### <a name="ExamplesQuotaRequestStatusGet">Example</a>
```
az quota quota-request-status show --id "2B5C8515-37D8-4B6A-879B-CD641A2CF605" --scope "subscriptions/00000000-0000-000\
0-0000-000000000000/providers/Microsoft.Compute/locations/eastus"
```
##### <a name="ExamplesQuotaRequestStatusGet">Example</a>
```
az quota quota-request-status show --id "2B5C8515-37D8-4B6A-879B-CD641A2CF605" --scope "subscriptions/00000000-0000-000\
0-0000-000000000000/providers/Microsoft.Compute/locations/eastus"
```
##### <a name="ExamplesQuotaRequestStatusGet">Example</a>
```
az quota quota-request-status show --id "2B5C8515-37D8-4B6A-879B-CD641A2CF605" --scope "subscriptions/D7EC67B3-7657-496\
6-BFFC-41EFD36BAAB3/providers/Microsoft.Compute/locations/eastus"
```
##### <a name="ParametersQuotaRequestStatusGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--id**|string|Quota request ID.|id|id|
|**--scope**|string|The target Azure resource URI. For example, `/subscriptions/9f6cce51-6baf-4de5-a3c4-6f58b85315b9/resourceGroups/qms-test/providers/Microsoft.Batch/batchAccounts/testAccount/`. This is the target Azure resource URI for the List GET operation. If a `{resourceName}` is added after `/quotaLimits`, then it's the target Azure resource URI in the GET operation for the specific resource.|scope|scope|

### group `az quota quota-resource-provider`
#### <a name="QuotaResourceProvidersList">Command `az quota quota-resource-provider list`</a>

##### <a name="ExamplesQuotaResourceProvidersList">Example</a>
```
az quota quota-resource-provider list
```
##### <a name="ParametersQuotaResourceProvidersList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|