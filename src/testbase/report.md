# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az testbase|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az testbase` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az testbase account|TestBaseAccounts|[commands](#CommandsInTestBaseAccounts)|
|az testbase analysis-result|AnalysisResults|[commands](#CommandsInAnalysisResults)|
|az testbase available-os|AvailableOS|[commands](#CommandsInAvailableOS)|
|az testbase customer-event|CustomerEvents|[commands](#CommandsInCustomerEvents)|
|az testbase email-event|EmailEvents|[commands](#CommandsInEmailEvents)|
|az testbase favorite-process|FavoriteProcesses|[commands](#CommandsInFavoriteProcesses)|
|az testbase flighting-ring|FlightingRings|[commands](#CommandsInFlightingRings)|
|az testbase os-update|OSUpdates|[commands](#CommandsInOSUpdates)|
|az testbase package|Packages|[commands](#CommandsInPackages)|
|az testbase sku|Skus|[commands](#CommandsInSkus)|
|az testbase test-result|TestResults|[commands](#CommandsInTestResults)|
|az testbase test-summary|TestSummaries|[commands](#CommandsInTestSummaries)|
|az testbase test-type|TestTypes|[commands](#CommandsInTestTypes)|
|az testbase usage|Usage|[commands](#CommandsInUsage)|

## COMMANDS
### <a name="CommandsInTestBaseAccounts">Commands in `az testbase account` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az testbase account list](#TestBaseAccountsListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersTestBaseAccountsListByResourceGroup)|[Example](#ExamplesTestBaseAccountsListByResourceGroup)|
|[az testbase account list](#TestBaseAccountsListBySubscription)|ListBySubscription|[Parameters](#ParametersTestBaseAccountsListBySubscription)|[Example](#ExamplesTestBaseAccountsListBySubscription)|
|[az testbase account show](#TestBaseAccountsGet)|Get|[Parameters](#ParametersTestBaseAccountsGet)|[Example](#ExamplesTestBaseAccountsGet)|
|[az testbase account create](#TestBaseAccountsCreate)|Create|[Parameters](#ParametersTestBaseAccountsCreate)|[Example](#ExamplesTestBaseAccountsCreate)|
|[az testbase account update](#TestBaseAccountsUpdate)|Update|[Parameters](#ParametersTestBaseAccountsUpdate)|[Example](#ExamplesTestBaseAccountsUpdate)|
|[az testbase account delete](#TestBaseAccountsOffboard)|Offboard|[Parameters](#ParametersTestBaseAccountsOffboard)|[Example](#ExamplesTestBaseAccountsOffboard)|
|[az testbase account check-package-name](#TestBaseAccountsCheckPackageNameAvailability)|CheckPackageNameAvailability|[Parameters](#ParametersTestBaseAccountsCheckPackageNameAvailability)|[Example](#ExamplesTestBaseAccountsCheckPackageNameAvailability)|
|[az testbase account get-package-blob-path](#TestBaseAccountsGetFileUploadUrl)|GetFileUploadUrl|[Parameters](#ParametersTestBaseAccountsGetFileUploadUrl)|[Example](#ExamplesTestBaseAccountsGetFileUploadUrl)|

### <a name="CommandsInAnalysisResults">Commands in `az testbase analysis-result` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az testbase analysis-result list](#AnalysisResultsList)|List|[Parameters](#ParametersAnalysisResultsList)|[Example](#ExamplesAnalysisResultsList)|
|[az testbase analysis-result show](#AnalysisResultsGet)|Get|[Parameters](#ParametersAnalysisResultsGet)|[Example](#ExamplesAnalysisResultsGet)|

### <a name="CommandsInAvailableOS">Commands in `az testbase available-os` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az testbase available-os list](#AvailableOSList)|List|[Parameters](#ParametersAvailableOSList)|[Example](#ExamplesAvailableOSList)|
|[az testbase available-os show](#AvailableOSGet)|Get|[Parameters](#ParametersAvailableOSGet)|[Example](#ExamplesAvailableOSGet)|

### <a name="CommandsInCustomerEvents">Commands in `az testbase customer-event` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az testbase customer-event list](#CustomerEventsListByTestBaseAccount)|ListByTestBaseAccount|[Parameters](#ParametersCustomerEventsListByTestBaseAccount)|[Example](#ExamplesCustomerEventsListByTestBaseAccount)|
|[az testbase customer-event show](#CustomerEventsGet)|Get|[Parameters](#ParametersCustomerEventsGet)|[Example](#ExamplesCustomerEventsGet)|
|[az testbase customer-event create](#CustomerEventsCreate)|Create|[Parameters](#ParametersCustomerEventsCreate)|[Example](#ExamplesCustomerEventsCreate)|
|[az testbase customer-event delete](#CustomerEventsDelete)|Delete|[Parameters](#ParametersCustomerEventsDelete)|[Example](#ExamplesCustomerEventsDelete)|

### <a name="CommandsInEmailEvents">Commands in `az testbase email-event` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az testbase email-event list](#EmailEventsList)|List|[Parameters](#ParametersEmailEventsList)|[Example](#ExamplesEmailEventsList)|
|[az testbase email-event show](#EmailEventsGet)|Get|[Parameters](#ParametersEmailEventsGet)|[Example](#ExamplesEmailEventsGet)|

### <a name="CommandsInFavoriteProcesses">Commands in `az testbase favorite-process` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az testbase favorite-process list](#FavoriteProcessesList)|List|[Parameters](#ParametersFavoriteProcessesList)|[Example](#ExamplesFavoriteProcessesList)|
|[az testbase favorite-process show](#FavoriteProcessesGet)|Get|[Parameters](#ParametersFavoriteProcessesGet)|[Example](#ExamplesFavoriteProcessesGet)|
|[az testbase favorite-process create](#FavoriteProcessesCreate)|Create|[Parameters](#ParametersFavoriteProcessesCreate)|[Example](#ExamplesFavoriteProcessesCreate)|
|[az testbase favorite-process delete](#FavoriteProcessesDelete)|Delete|[Parameters](#ParametersFavoriteProcessesDelete)|[Example](#ExamplesFavoriteProcessesDelete)|

### <a name="CommandsInFlightingRings">Commands in `az testbase flighting-ring` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az testbase flighting-ring list](#FlightingRingsList)|List|[Parameters](#ParametersFlightingRingsList)|[Example](#ExamplesFlightingRingsList)|
|[az testbase flighting-ring show](#FlightingRingsGet)|Get|[Parameters](#ParametersFlightingRingsGet)|[Example](#ExamplesFlightingRingsGet)|

### <a name="CommandsInOSUpdates">Commands in `az testbase os-update` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az testbase os-update list](#OSUpdatesList)|List|[Parameters](#ParametersOSUpdatesList)|[Example](#ExamplesOSUpdatesList)|
|[az testbase os-update show](#OSUpdatesGet)|Get|[Parameters](#ParametersOSUpdatesGet)|[Example](#ExamplesOSUpdatesGet)|

### <a name="CommandsInPackages">Commands in `az testbase package` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az testbase package list](#PackagesListByTestBaseAccount)|ListByTestBaseAccount|[Parameters](#ParametersPackagesListByTestBaseAccount)|[Example](#ExamplesPackagesListByTestBaseAccount)|
|[az testbase package show](#PackagesGet)|Get|[Parameters](#ParametersPackagesGet)|[Example](#ExamplesPackagesGet)|
|[az testbase package create](#PackagesCreate)|Create|[Parameters](#ParametersPackagesCreate)|[Example](#ExamplesPackagesCreate)|
|[az testbase package update](#PackagesUpdate)|Update|[Parameters](#ParametersPackagesUpdate)|[Example](#ExamplesPackagesUpdate)|
|[az testbase package delete](#PackagesDelete)|Delete|[Parameters](#ParametersPackagesDelete)|[Example](#ExamplesPackagesDelete)|
|[az testbase package get-download-url](#PackagesGetDownloadURL)|GetDownloadURL|[Parameters](#ParametersPackagesGetDownloadURL)|[Example](#ExamplesPackagesGetDownloadURL)|
|[az testbase package hard-delete](#PackagesHardDelete)|HardDelete|[Parameters](#ParametersPackagesHardDelete)|[Example](#ExamplesPackagesHardDelete)|

### <a name="CommandsInSkus">Commands in `az testbase sku` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az testbase sku list](#SkusList)|List|[Parameters](#ParametersSkusList)|[Example](#ExamplesSkusList)|

### <a name="CommandsInTestResults">Commands in `az testbase test-result` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az testbase test-result list](#TestResultsList)|List|[Parameters](#ParametersTestResultsList)|[Example](#ExamplesTestResultsList)|
|[az testbase test-result show](#TestResultsGet)|Get|[Parameters](#ParametersTestResultsGet)|[Example](#ExamplesTestResultsGet)|
|[az testbase test-result get-download-url](#TestResultsGetDownloadURL)|GetDownloadURL|[Parameters](#ParametersTestResultsGetDownloadURL)|[Example](#ExamplesTestResultsGetDownloadURL)|
|[az testbase test-result get-video-download-url](#TestResultsGetVideoDownloadURL)|GetVideoDownloadURL|[Parameters](#ParametersTestResultsGetVideoDownloadURL)|[Example](#ExamplesTestResultsGetVideoDownloadURL)|

### <a name="CommandsInTestSummaries">Commands in `az testbase test-summary` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az testbase test-summary list](#TestSummariesList)|List|[Parameters](#ParametersTestSummariesList)|[Example](#ExamplesTestSummariesList)|
|[az testbase test-summary show](#TestSummariesGet)|Get|[Parameters](#ParametersTestSummariesGet)|[Example](#ExamplesTestSummariesGet)|

### <a name="CommandsInTestTypes">Commands in `az testbase test-type` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az testbase test-type list](#TestTypesList)|List|[Parameters](#ParametersTestTypesList)|[Example](#ExamplesTestTypesList)|
|[az testbase test-type show](#TestTypesGet)|Get|[Parameters](#ParametersTestTypesGet)|[Example](#ExamplesTestTypesGet)|

### <a name="CommandsInUsage">Commands in `az testbase usage` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az testbase usage list](#UsageList)|List|[Parameters](#ParametersUsageList)|[Example](#ExamplesUsageList)|


## COMMAND DETAILS
### group `az testbase account`
#### <a name="TestBaseAccountsListByResourceGroup">Command `az testbase account list`</a>

##### <a name="ExamplesTestBaseAccountsListByResourceGroup">Example</a>
```
az testbase account list --resource-group "contoso-rg1"
```
##### <a name="ParametersTestBaseAccountsListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--get-deleted**|boolean|The flag indicating if we need to include the Test Base Accounts which were soft deleted before.|get_deleted|getDeleted|

#### <a name="TestBaseAccountsListBySubscription">Command `az testbase account list`</a>

##### <a name="ExamplesTestBaseAccountsListBySubscription">Example</a>
```
az testbase account list
```
##### <a name="ParametersTestBaseAccountsListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--get-deleted**|boolean|The flag indicating if we need to include the Test Base Accounts which were soft deleted before.|get_deleted|getDeleted|

#### <a name="TestBaseAccountsGet">Command `az testbase account show`</a>

##### <a name="ExamplesTestBaseAccountsGet">Example</a>
```
az testbase account show --resource-group "contoso-rg1" --name "contoso-testBaseAccount1"
```
##### <a name="ParametersTestBaseAccountsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--name**|string|The resource name of the Test Base Account.|name|testBaseAccountName|

#### <a name="TestBaseAccountsCreate">Command `az testbase account create`</a>

##### <a name="ExamplesTestBaseAccountsCreate">Example</a>
```
az testbase account create --location "westus" --sku-name "S0" --resource-group "contoso-rg1" --name \
"contoso-testBaseAccount1"
```
##### <a name="ParametersTestBaseAccountsCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--name**|string|The resource name of the Test Base Account.|name|testBaseAccountName|
|**--restore**|boolean|The flag indicating if we would like to restore the Test Base Accounts which were soft deleted before.|restore|restore|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--tags**|dictionary|The tags of the resource.|tags|tags|
|**--resource-type**|string|The type of resource the SKU applies to.|resource_type|resourceType|
|**--sku-name**|string|The name of the SKU. This is typically a letter + number code, such as B0 or S0.|sku_name|name|
|**--locations**|array|The locations that the SKU is available.|locations|locations|

#### <a name="TestBaseAccountsUpdate">Command `az testbase account update`</a>

##### <a name="ExamplesTestBaseAccountsUpdate">Example</a>
```
az testbase account update --name "S0" --resource-group "contoso-rg1"
```
##### <a name="ParametersTestBaseAccountsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--name**|string|The resource name of the Test Base Account.|name|testBaseAccountName|
|**--tags**|dictionary|The tags of the Test Base Account.|tags|tags|
|**--resource-type**|string|The type of resource the SKU applies to.|resource_type|resourceType|
|**--name**|string|The name of the SKU. This is typically a letter + number code, such as B0 or S0.|name|name|
|**--locations**|array|The locations that the SKU is available.|locations|locations|

#### <a name="TestBaseAccountsOffboard">Command `az testbase account delete`</a>

##### <a name="ExamplesTestBaseAccountsOffboard">Example</a>
```
az testbase account delete --resource-group "contoso-rg1" --name "contoso-testBaseAccount1"
```
##### <a name="ParametersTestBaseAccountsOffboard">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--name**|string|The resource name of the Test Base Account.|name|testBaseAccountName|

#### <a name="TestBaseAccountsCheckPackageNameAvailability">Command `az testbase account check-package-name`</a>

##### <a name="ExamplesTestBaseAccountsCheckPackageNameAvailability">Example</a>
```
az testbase account check-package-name --name "testApp" --type "Microsoft.TestBase/testBaseAccounts/packages" \
--application-name "testApp" --version "1.0.0" --resource-group "contoso-rg1"
```
##### <a name="ParametersTestBaseAccountsCheckPackageNameAvailability">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--name**|string|The resource name of the Test Base Account.|name|testBaseAccountName|
|**--name**|string|Resource name to verify.|name|name|
|**--application-name**|string|Application name to verify.|application_name|applicationName|
|**--version**|string|Version name to verify.|version|version|
|**--type**|string|fully qualified resource type which includes provider namespace.|type|type|

#### <a name="TestBaseAccountsGetFileUploadUrl">Command `az testbase account get-package-blob-path`</a>

##### <a name="ExamplesTestBaseAccountsGetFileUploadUrl">Example</a>
```
az testbase account get-package-blob-path --file-name "package.zip" --resource-group "contoso-rg1" --name \
"contoso-testBaseAccount1"
```
##### <a name="ParametersTestBaseAccountsGetFileUploadUrl">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--name**|string|The resource name of the Test Base Account.|name|testBaseAccountName|
|**--file-name**|string|The custom file name of the uploaded blob.|file_name|blobName|

### group `az testbase analysis-result`
#### <a name="AnalysisResultsList">Command `az testbase analysis-result list`</a>

##### <a name="ExamplesAnalysisResultsList">Example</a>
```
az testbase analysis-result list --analysis-result-type "CPURegression" --package-name "contoso-package2" \
--resource-group "contoso-rg1" --account-name "contoso-testBaseAccount1" --test-result-name "Windows-10-1909-Test-Id"
az testbase analysis-result list --analysis-result-type "CPUUtilization" --package-name "contoso-package2" \
--resource-group "contoso-rg1" --account-name "contoso-testBaseAccount1" --test-result-name "Windows-10-1909-Test-Id"
az testbase analysis-result list --analysis-result-type "MemoryRegression" --package-name "contoso-package2" \
--resource-group "contoso-rg1" --account-name "contoso-testBaseAccount1" --test-result-name "Windows-10-1909-Test-Id"
az testbase analysis-result list --analysis-result-type "MemoryUtilization" --package-name "contoso-package2" \
--resource-group "contoso-rg1" --account-name "contoso-testBaseAccount1" --test-result-name "Windows-10-1909-Test-Id"
```
##### <a name="ParametersAnalysisResultsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--account-name**|string|The resource name of the Test Base Account.|account_name|testBaseAccountName|
|**--package-name**|string|The resource name of the Test Base Package.|package_name|packageName|
|**--test-result-name**|string|The Test Result Name. It equals to {osName}-{TestResultId} string.|test_result_name|testResultName|
|**--analysis-result-type**|choice|The type of the Analysis Result of a Test Result.|analysis_result_type|analysisResultType|

#### <a name="AnalysisResultsGet">Command `az testbase analysis-result show`</a>

##### <a name="ExamplesAnalysisResultsGet">Example</a>
```
az testbase analysis-result show --name "cpuRegression" --package-name "contoso-package2" --resource-group \
"contoso-rg1" --account-name "contoso-testBaseAccount1" --test-result-name "Windows-10-1909-Test-Id"
az testbase analysis-result show --name "cpuUtilization" --package-name "contoso-package2" --resource-group \
"contoso-rg1" --account-name "contoso-testBaseAccount1" --test-result-name "Windows-10-1909-Test-Id"
az testbase analysis-result show --name "memoryRegression" --package-name "contoso-package2" --resource-group \
"contoso-rg1" --account-name "contoso-testBaseAccount1" --test-result-name "Windows-10-1909-Test-Id"
az testbase analysis-result show --name "memoryUtilization" --package-name "contoso-package2" --resource-group \
"contoso-rg1" --account-name "contoso-testBaseAccount1" --test-result-name "Windows-10-1909-Test-Id"
```
##### <a name="ParametersAnalysisResultsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--account-name**|string|The resource name of the Test Base Account.|account_name|testBaseAccountName|
|**--package-name**|string|The resource name of the Test Base Package.|package_name|packageName|
|**--test-result-name**|string|The Test Result Name. It equals to {osName}-{TestResultId} string.|test_result_name|testResultName|
|**--analysis-result-name**|choice|The name of the Analysis Result of a Test Result.|analysis_result_name|analysisResultName|

### group `az testbase available-os`
#### <a name="AvailableOSList">Command `az testbase available-os list`</a>

##### <a name="ExamplesAvailableOSList">Example</a>
```
az testbase available-os list --os-update-type "SecurityUpdate" --resource-group "contoso-rg" --account-name \
"contoso-testBaseAccount"
```
##### <a name="ParametersAvailableOSList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--account-name**|string|The resource name of the Test Base Account.|account_name|testBaseAccountName|
|**--os-update-type**|choice|The type of the OS Update.|os_update_type|osUpdateType|

#### <a name="AvailableOSGet">Command `az testbase available-os show`</a>

##### <a name="ExamplesAvailableOSGet">Example</a>
```
az testbase available-os show --available-os-resource-name "Windows-10-2004" --resource-group "contoso-rg" \
--account-name "contoso-testBaseAccount"
```
##### <a name="ParametersAvailableOSGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--account-name**|string|The resource name of the Test Base Account.|account_name|testBaseAccountName|
|**--available-os-resource-name**|string|The resource name of an Available OS.|available_os_resource_name|availableOSResourceName|

### group `az testbase customer-event`
#### <a name="CustomerEventsListByTestBaseAccount">Command `az testbase customer-event list`</a>

##### <a name="ExamplesCustomerEventsListByTestBaseAccount">Example</a>
```
az testbase customer-event list --resource-group "contoso-rg1" --account-name "contoso-testBaseAccount1"
```
##### <a name="ParametersCustomerEventsListByTestBaseAccount">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--account-name**|string|The resource name of the Test Base Account.|account_name|testBaseAccountName|

#### <a name="CustomerEventsGet">Command `az testbase customer-event show`</a>

##### <a name="ExamplesCustomerEventsGet">Example</a>
```
az testbase customer-event show --name "WeeklySummary" --resource-group "contoso-rg1" --account-name \
"contoso-testBaseAccount1"
```
##### <a name="ParametersCustomerEventsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--account-name**|string|The resource name of the Test Base Account.|account_name|testBaseAccountName|
|**--customer-event-name**|string|The resource name of the Test Base Customer event.|customer_event_name|customerEventName|

#### <a name="CustomerEventsCreate">Command `az testbase customer-event create`</a>

##### <a name="ExamplesCustomerEventsCreate">Example</a>
```
az testbase customer-event create --name "WeeklySummary" --event-name "WeeklySummary" --receivers \
"[{\\"receiverType\\":\\"UserObjects\\",\\"receiverValue\\":{\\"userObjectReceiverValue\\":{\\"userObjectIds\\":[\\"245\
245245245325\\",\\"365365365363565\\"]}}},{\\"receiverType\\":\\"DistributionGroup\\",\\"receiverValue\\":{\\"distribut\
ionGroupListReceiverValue\\":{\\"distributionGroups\\":[\\"test@microsoft.com\\"]}}}]" --resource-group "contoso-rg1" \
--account-name "contoso-testBaseAccount1"
```
##### <a name="ParametersCustomerEventsCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--account-name**|string|The resource name of the Test Base Account.|account_name|testBaseAccountName|
|**--customer-event-name**|string|The resource name of the Test Base Customer event.|customer_event_name|customerEventName|
|**--event-name**|string|The name of the event subscribed to.|event_name|eventName|
|**--receivers**|array|The notification event receivers.|receivers|receivers|

#### <a name="CustomerEventsDelete">Command `az testbase customer-event delete`</a>

##### <a name="ExamplesCustomerEventsDelete">Example</a>
```
az testbase customer-event delete --name "WeeklySummary" --resource-group "contoso-rg1" --account-name \
"contoso-testBaseAccount1"
```
##### <a name="ParametersCustomerEventsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--account-name**|string|The resource name of the Test Base Account.|account_name|testBaseAccountName|
|**--customer-event-name**|string|The resource name of the Test Base Customer event.|customer_event_name|customerEventName|

### group `az testbase email-event`
#### <a name="EmailEventsList">Command `az testbase email-event list`</a>

##### <a name="ExamplesEmailEventsList">Example</a>
```
az testbase email-event list --resource-group "contoso-rg" --account-name "contoso-testBaseAccount"
```
##### <a name="ParametersEmailEventsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--account-name**|string|The resource name of the Test Base Account.|account_name|testBaseAccountName|

#### <a name="EmailEventsGet">Command `az testbase email-event show`</a>

##### <a name="ExamplesEmailEventsGet">Example</a>
```
az testbase email-event show --email-event-resource-name "weekly-summary" --resource-group "contoso-rg" --account-name \
"contoso-testBaseAccount"
```
##### <a name="ParametersEmailEventsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--account-name**|string|The resource name of the Test Base Account.|account_name|testBaseAccountName|
|**--email-event-resource-name**|string|The resource name of an email event.|email_event_resource_name|emailEventResourceName|

### group `az testbase favorite-process`
#### <a name="FavoriteProcessesList">Command `az testbase favorite-process list`</a>

##### <a name="ExamplesFavoriteProcessesList">Example</a>
```
az testbase favorite-process list --package-name "contoso-package2" --resource-group "contoso-rg1" --account-name \
"contoso-testBaseAccount1"
```
##### <a name="ParametersFavoriteProcessesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--account-name**|string|The resource name of the Test Base Account.|account_name|testBaseAccountName|
|**--package-name**|string|The resource name of the Test Base Package.|package_name|packageName|

#### <a name="FavoriteProcessesGet">Command `az testbase favorite-process show`</a>

##### <a name="ExamplesFavoriteProcessesGet">Example</a>
```
az testbase favorite-process show --name "testAppProcess" --package-name "contoso-package2" --resource-group \
"contoso-rg1" --account-name "contoso-testBaseAccount1"
```
##### <a name="ParametersFavoriteProcessesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--account-name**|string|The resource name of the Test Base Account.|account_name|testBaseAccountName|
|**--package-name**|string|The resource name of the Test Base Package.|package_name|packageName|
|**--name**|string|The resource name of a favorite process in a package. If the process name contains characters that are not allowed in Azure Resource Name, we use 'actualProcessName' in request body to submit the name.|name|favoriteProcessResourceName|

#### <a name="FavoriteProcessesCreate">Command `az testbase favorite-process create`</a>

##### <a name="ExamplesFavoriteProcessesCreate">Example</a>
```
az testbase favorite-process create --name "testAppProcess" --package-name "contoso-package2" --actual-process-name \
"testApp&.exe" --resource-group "contoso-rg1" --account-name "contoso-testBaseAccount1"
```
##### <a name="ParametersFavoriteProcessesCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--account-name**|string|The resource name of the Test Base Account.|account_name|testBaseAccountName|
|**--package-name**|string|The resource name of the Test Base Package.|package_name|packageName|
|**--name**|string|The resource name of a favorite process in a package. If the process name contains characters that are not allowed in Azure Resource Name, we use 'actualProcessName' in request body to submit the name.|name|favoriteProcessResourceName|
|**--actual-process-name**|string|The actual name of the favorite process. It will be equal to resource name except for the scenario that the process name contains characters that are not allowed in the resource name.|actual_process_name|actualProcessName|

#### <a name="FavoriteProcessesDelete">Command `az testbase favorite-process delete`</a>

##### <a name="ExamplesFavoriteProcessesDelete">Example</a>
```
az testbase favorite-process delete --name "testAppProcess" --package-name "contoso-package2" --resource-group \
"contoso-rg1" --account-name "contoso-testBaseAccount1"
```
##### <a name="ParametersFavoriteProcessesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--account-name**|string|The resource name of the Test Base Account.|account_name|testBaseAccountName|
|**--package-name**|string|The resource name of the Test Base Package.|package_name|packageName|
|**--name**|string|The resource name of a favorite process in a package. If the process name contains characters that are not allowed in Azure Resource Name, we use 'actualProcessName' in request body to submit the name.|name|favoriteProcessResourceName|

### group `az testbase flighting-ring`
#### <a name="FlightingRingsList">Command `az testbase flighting-ring list`</a>

##### <a name="ExamplesFlightingRingsList">Example</a>
```
az testbase flighting-ring list --resource-group "contoso-rg" --account-name "contoso-testBaseAccount"
```
##### <a name="ParametersFlightingRingsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--account-name**|string|The resource name of the Test Base Account.|account_name|testBaseAccountName|

#### <a name="FlightingRingsGet">Command `az testbase flighting-ring show`</a>

##### <a name="ExamplesFlightingRingsGet">Example</a>
```
az testbase flighting-ring show --flighting-ring-resource-name "Insider-Beta-Channel" --resource-group "contoso-rg" \
--account-name "contoso-testBaseAccount"
```
##### <a name="ParametersFlightingRingsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--account-name**|string|The resource name of the Test Base Account.|account_name|testBaseAccountName|
|**--flighting-ring-resource-name**|string|The resource name of a flighting ring.|flighting_ring_resource_name|flightingRingResourceName|

### group `az testbase os-update`
#### <a name="OSUpdatesList">Command `az testbase os-update list`</a>

##### <a name="ExamplesOSUpdatesList">Example</a>
```
az testbase os-update list --os-update-type "SecurityUpdate" --package-name "contoso-package2" --resource-group \
"contoso-rg1" --account-name "contoso-testBaseAccount1"
```
##### <a name="ParametersOSUpdatesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--account-name**|string|The resource name of the Test Base Account.|account_name|testBaseAccountName|
|**--package-name**|string|The resource name of the Test Base Package.|package_name|packageName|
|**--os-update-type**|choice|The type of the OS Update.|os_update_type|osUpdateType|

#### <a name="OSUpdatesGet">Command `az testbase os-update show`</a>

##### <a name="ExamplesOSUpdatesGet">Example</a>
```
az testbase os-update show --os-update-resource-name "Windows-10-2004-2020-12-B-505" --package-name "contoso-package2" \
--resource-group "contoso-rg1" --account-name "contoso-testBaseAccount1"
```
##### <a name="ParametersOSUpdatesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--account-name**|string|The resource name of the Test Base Account.|account_name|testBaseAccountName|
|**--package-name**|string|The resource name of the Test Base Package.|package_name|packageName|
|**--os-update-resource-name**|string|The resource name of an OS Update.|os_update_resource_name|osUpdateResourceName|

### group `az testbase package`
#### <a name="PackagesListByTestBaseAccount">Command `az testbase package list`</a>

##### <a name="ExamplesPackagesListByTestBaseAccount">Example</a>
```
az testbase package list --resource-group "contoso-rg1" --account-name "contoso-testBaseAccount1"
```
##### <a name="ParametersPackagesListByTestBaseAccount">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--account-name**|string|The resource name of the Test Base Account.|account_name|testBaseAccountName|

#### <a name="PackagesGet">Command `az testbase package show`</a>

##### <a name="ExamplesPackagesGet">Example</a>
```
az testbase package show --name "contoso-package2" --resource-group "contoso-rg1" --account-name \
"contoso-testBaseAccount1"
```
##### <a name="ParametersPackagesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--account-name**|string|The resource name of the Test Base Account.|account_name|testBaseAccountName|
|**--package-name**|string|The resource name of the Test Base Package.|package_name|packageName|

#### <a name="PackagesCreate">Command `az testbase package create`</a>

##### <a name="ExamplesPackagesCreate">Example</a>
```
az testbase package create --name "contoso-package2" --location "westus" --application-name "contoso-package2" \
--blob-path "storageAccountPath/package.zip" --flighting-ring "Insider Beta Channel" --target-os-list \
os-update-type="Security updates" target-o-ss="Windows 10 2004" target-o-ss="Windows 10 1903" --tests \
"[{\\"isActive\\":true,\\"testType\\":\\"OutOfBoxTest\\",\\"commands\\":[{\\"name\\":\\"Install\\",\\"action\\":\\"Inst\
all\\",\\"alwaysRun\\":true,\\"applyUpdateBefore\\":false,\\"content\\":\\"app/scripts/install/job.ps1\\",\\"contentTyp\
e\\":\\"Path\\",\\"maxRunTime\\":1800,\\"restartAfter\\":true,\\"runAsInteractive\\":true,\\"runElevated\\":true},{\\"n\
ame\\":\\"Launch\\",\\"action\\":\\"Launch\\",\\"alwaysRun\\":false,\\"applyUpdateBefore\\":true,\\"content\\":\\"app/s\
cripts/launch/job.ps1\\",\\"contentType\\":\\"Path\\",\\"maxRunTime\\":1800,\\"restartAfter\\":false,\\"runAsInteractiv\
e\\":true,\\"runElevated\\":true},{\\"name\\":\\"Close\\",\\"action\\":\\"Close\\",\\"alwaysRun\\":false,\\"applyUpdate\
Before\\":false,\\"content\\":\\"app/scripts/close/job.ps1\\",\\"contentType\\":\\"Path\\",\\"maxRunTime\\":1800,\\"res\
tartAfter\\":false,\\"runAsInteractive\\":true,\\"runElevated\\":true},{\\"name\\":\\"Uninstall\\",\\"action\\":\\"Unin\
stall\\",\\"alwaysRun\\":true,\\"applyUpdateBefore\\":false,\\"content\\":\\"app/scripts/uninstall/job.ps1\\",\\"conten\
tType\\":\\"Path\\",\\"maxRunTime\\":1800,\\"restartAfter\\":false,\\"runAsInteractive\\":true,\\"runElevated\\":true}]\
}]" --version "1.0.0" --resource-group "contoso-rg1" --account-name "contoso-testBaseAccount1"
```
##### <a name="ParametersPackagesCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--account-name**|string|The resource name of the Test Base Account.|account_name|testBaseAccountName|
|**--package-name**|string|The resource name of the Test Base Package.|package_name|packageName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--tags**|dictionary|The tags of the resource.|tags|tags|
|**--application-name**|string|Application name|application_name|applicationName|
|**--version**|string|Application version|version|version|
|**--target-os-list**|array|Specifies the target OSs of specific OS Update types.|target_os_list|targetOSList|
|**--flighting-ring**|string|The flighting ring for feature update.|flighting_ring|flightingRing|
|**--blob-path**|string|The file path of the package.|blob_path|blobPath|
|**--tests**|array|The detailed test information.|tests|tests|

#### <a name="PackagesUpdate">Command `az testbase package update`</a>

##### <a name="ExamplesPackagesUpdate">Example</a>
```
az testbase package update --name "contoso-package2" --blob-path "storageAccountPath/package.zip" --flighting-ring \
"Insider Beta Channel" --is-enabled false --target-os-list os-update-type="Security updates" target-o-ss="Windows 10 \
2004" target-o-ss="Windows 10 1903" --tests "[{\\"isActive\\":true,\\"testType\\":\\"OutOfBoxTest\\",\\"commands\\":[{\
\\"name\\":\\"Install\\",\\"action\\":\\"Install\\",\\"alwaysRun\\":true,\\"applyUpdateBefore\\":false,\\"content\\":\\\
"app/scripts/install/job.ps1\\",\\"contentType\\":\\"Path\\",\\"maxRunTime\\":1800,\\"restartAfter\\":true,\\"runAsInte\
ractive\\":true,\\"runElevated\\":true},{\\"name\\":\\"Launch\\",\\"action\\":\\"Launch\\",\\"alwaysRun\\":false,\\"app\
lyUpdateBefore\\":true,\\"content\\":\\"app/scripts/launch/job.ps1\\",\\"contentType\\":\\"Path\\",\\"maxRunTime\\":180\
0,\\"restartAfter\\":false,\\"runAsInteractive\\":true,\\"runElevated\\":true},{\\"name\\":\\"Close\\",\\"action\\":\\"\
Close\\",\\"alwaysRun\\":false,\\"applyUpdateBefore\\":false,\\"content\\":\\"app/scripts/close/job.ps1\\",\\"contentTy\
pe\\":\\"Path\\",\\"maxRunTime\\":1800,\\"restartAfter\\":false,\\"runAsInteractive\\":true,\\"runElevated\\":true},{\\\
"name\\":\\"Uninstall\\",\\"action\\":\\"Uninstall\\",\\"alwaysRun\\":true,\\"applyUpdateBefore\\":false,\\"content\\":\
\\"app/scripts/uninstall/job.ps1\\",\\"contentType\\":\\"Path\\",\\"maxRunTime\\":1800,\\"restartAfter\\":false,\\"runA\
sInteractive\\":true,\\"runElevated\\":true}]}]" --resource-group "contoso-rg1" --account-name \
"contoso-testBaseAccount1"
```
##### <a name="ParametersPackagesUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--account-name**|string|The resource name of the Test Base Account.|account_name|testBaseAccountName|
|**--package-name**|string|The resource name of the Test Base Package.|package_name|packageName|
|**--tags**|dictionary|The tags of the Package.|tags|tags|
|**--target-os-list**|array|Specifies the target OSs of specific OS Update types.|target_os_list|targetOSList|
|**--flighting-ring**|string|The flighting ring for feature update.|flighting_ring|flightingRing|
|**--is-enabled**|boolean|Specifies whether the package is enabled. It doesn't schedule test for package which is not enabled.|is_enabled|isEnabled|
|**--blob-path**|string|The file name of the package.|blob_path|blobPath|
|**--tests**|array|The detailed test information.|tests|tests|

#### <a name="PackagesDelete">Command `az testbase package delete`</a>

##### <a name="ExamplesPackagesDelete">Example</a>
```
az testbase package delete --name "contoso-package2" --resource-group "contoso-rg1" --account-name \
"contoso-testBaseAccount1"
```
##### <a name="ParametersPackagesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--account-name**|string|The resource name of the Test Base Account.|account_name|testBaseAccountName|
|**--package-name**|string|The resource name of the Test Base Package.|package_name|packageName|

#### <a name="PackagesGetDownloadURL">Command `az testbase package get-download-url`</a>

##### <a name="ExamplesPackagesGetDownloadURL">Example</a>
```
az testbase package get-download-url --name "contoso-package2" --resource-group "contoso-rg1" --account-name \
"contoso-testBaseAccount1"
```
##### <a name="ParametersPackagesGetDownloadURL">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--account-name**|string|The resource name of the Test Base Account.|account_name|testBaseAccountName|
|**--package-name**|string|The resource name of the Test Base Package.|package_name|packageName|

#### <a name="PackagesHardDelete">Command `az testbase package hard-delete`</a>

##### <a name="ExamplesPackagesHardDelete">Example</a>
```
az testbase package hard-delete --name "contoso-package2" --resource-group "contoso-rg1" --account-name \
"contoso-testBaseAccount1"
```
##### <a name="ParametersPackagesHardDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--account-name**|string|The resource name of the Test Base Account.|account_name|testBaseAccountName|
|**--package-name**|string|The resource name of the Test Base Package.|package_name|packageName|

### group `az testbase sku`
#### <a name="SkusList">Command `az testbase sku list`</a>

##### <a name="ExamplesSkusList">Example</a>
```
az testbase sku list
```
##### <a name="ParametersSkusList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

### group `az testbase test-result`
#### <a name="TestResultsList">Command `az testbase test-result list`</a>

##### <a name="ExamplesTestResultsList">Example</a>
```
az testbase test-result list --filter "osName eq \'Windows 10 2004\' and releaseName eq \'2020.11B\'" --os-update-type \
"SecurityUpdate" --package-name "contoso-package2" --resource-group "contoso-rg1" --account-name \
"contoso-testBaseAccount1"
```
##### <a name="ParametersTestResultsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--account-name**|string|The resource name of the Test Base Account.|account_name|testBaseAccountName|
|**--package-name**|string|The resource name of the Test Base Package.|package_name|packageName|
|**--os-update-type**|choice|The type of the OS Update.|os_update_type|osUpdateType|
|**--filter**|string|Odata filter|filter|$filter|

#### <a name="TestResultsGet">Command `az testbase test-result show`</a>

##### <a name="ExamplesTestResultsGet">Example</a>
```
az testbase test-result show --package-name "contoso-package2" --resource-group "contoso-rg1" --account-name \
"contoso-testBaseAccount1" --name "Windows-10-1909-99b1f80d-03a9-4148-997f-806ba5bac8e0"
```
##### <a name="ParametersTestResultsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--account-name**|string|The resource name of the Test Base Account.|account_name|testBaseAccountName|
|**--package-name**|string|The resource name of the Test Base Package.|package_name|packageName|
|**--test-result-name**|string|The Test Result Name. It equals to {osName}-{TestResultId} string.|test_result_name|testResultName|

#### <a name="TestResultsGetDownloadURL">Command `az testbase test-result get-download-url`</a>

##### <a name="ExamplesTestResultsGetDownloadURL">Example</a>
```
az testbase test-result get-download-url --package-name "contoso-package2" --resource-group "contoso-rg1" \
--account-name "contoso-testBaseAccount1" --name "Windows-10-1909-99b1f80d-03a9-4148-997f-806ba5bac8e0"
```
##### <a name="ParametersTestResultsGetDownloadURL">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--account-name**|string|The resource name of the Test Base Account.|account_name|testBaseAccountName|
|**--package-name**|string|The resource name of the Test Base Package.|package_name|packageName|
|**--test-result-name**|string|The Test Result Name. It equals to {osName}-{TestResultId} string.|test_result_name|testResultName|

#### <a name="TestResultsGetVideoDownloadURL">Command `az testbase test-result get-video-download-url`</a>

##### <a name="ExamplesTestResultsGetVideoDownloadURL">Example</a>
```
az testbase test-result get-video-download-url --package-name "contoso-package2" --resource-group "contoso-rg1" \
--account-name "contoso-testBaseAccount1" --name "Windows-10-1909-99b1f80d-03a9-4148-997f-806ba5bac8e0"
```
##### <a name="ParametersTestResultsGetVideoDownloadURL">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--account-name**|string|The resource name of the Test Base Account.|account_name|testBaseAccountName|
|**--package-name**|string|The resource name of the Test Base Package.|package_name|packageName|
|**--test-result-name**|string|The Test Result Name. It equals to {osName}-{TestResultId} string.|test_result_name|testResultName|

### group `az testbase test-summary`
#### <a name="TestSummariesList">Command `az testbase test-summary list`</a>

##### <a name="ExamplesTestSummariesList">Example</a>
```
az testbase test-summary list --resource-group "contoso-rg1" --account-name "contoso-testBaseAccount1"
```
##### <a name="ParametersTestSummariesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--account-name**|string|The resource name of the Test Base Account.|account_name|testBaseAccountName|

#### <a name="TestSummariesGet">Command `az testbase test-summary show`</a>

##### <a name="ExamplesTestSummariesGet">Example</a>
```
az testbase test-summary show --resource-group "contoso-rg1" --account-name "contoso-testBaseAccount1" --name \
"contoso-package2-096bffb5-5d3d-4305-a66a-953372ed6e88"
```
##### <a name="ParametersTestSummariesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--account-name**|string|The resource name of the Test Base Account.|account_name|testBaseAccountName|
|**--test-summary-name**|string|The name of the Test Summary.|test_summary_name|testSummaryName|

### group `az testbase test-type`
#### <a name="TestTypesList">Command `az testbase test-type list`</a>

##### <a name="ExamplesTestTypesList">Example</a>
```
az testbase test-type list --resource-group "contoso-rg" --account-name "contoso-testBaseAccount"
```
##### <a name="ParametersTestTypesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--account-name**|string|The resource name of the Test Base Account.|account_name|testBaseAccountName|

#### <a name="TestTypesGet">Command `az testbase test-type show`</a>

##### <a name="ExamplesTestTypesGet">Example</a>
```
az testbase test-type show --resource-group "contoso-rg" --account-name "contoso-testBaseAccount" \
--test-type-resource-name "Functional-Test"
```
##### <a name="ParametersTestTypesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--account-name**|string|The resource name of the Test Base Account.|account_name|testBaseAccountName|
|**--test-type-resource-name**|string|The resource name of a test type.|test_type_resource_name|testTypeResourceName|

### group `az testbase usage`
#### <a name="UsageList">Command `az testbase usage list`</a>

##### <a name="ExamplesUsageList">Example</a>
```
az testbase usage list --resource-group "contoso-rg1" --account-name "contoso-testBaseAccount1"
```
##### <a name="ParametersUsageList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource.|resource_group_name|resourceGroupName|
|**--account-name**|string|The resource name of the Test Base Account.|account_name|testBaseAccountName|
|**--filter**|string|Odata filter|filter|$filter|
