# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az databox|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az databox` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az databox job|Jobs|[commands](#CommandsInJobs)|
|az databox||[commands](#CommandsIn)|
|az databox service|Service|[commands](#CommandsInService)|

## COMMANDS
### <a name="CommandsIn">Commands in `az databox` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az databox mitigate](#Mitigate)|Mitigate|[Parameters](#ParametersMitigate)|[Example](#ExamplesMitigate)|

### <a name="CommandsInJobs">Commands in `az databox job` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az databox job list](#JobsListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersJobsListByResourceGroup)|[Example](#ExamplesJobsListByResourceGroup)|
|[az databox job list](#JobsList)|List|[Parameters](#ParametersJobsList)|[Example](#ExamplesJobsList)|
|[az databox job show](#JobsGet)|Get|[Parameters](#ParametersJobsGet)|[Example](#ExamplesJobsGet)|
|[az databox job create](#JobsCreate)|Create|[Parameters](#ParametersJobsCreate)|[Example](#ExamplesJobsCreate)|
|[az databox job update](#JobsUpdate)|Update|[Parameters](#ParametersJobsUpdate)|[Example](#ExamplesJobsUpdate)|
|[az databox job delete](#JobsDelete)|Delete|[Parameters](#ParametersJobsDelete)|[Example](#ExamplesJobsDelete)|
|[az databox job book-shipment-pick-up](#JobsBookShipmentPickUp)|BookShipmentPickUp|[Parameters](#ParametersJobsBookShipmentPickUp)|[Example](#ExamplesJobsBookShipmentPickUp)|
|[az databox job cancel](#JobsCancel)|Cancel|[Parameters](#ParametersJobsCancel)|[Example](#ExamplesJobsCancel)|
|[az databox job list-credentials](#JobsListCredentials)|ListCredentials|[Parameters](#ParametersJobsListCredentials)|[Example](#ExamplesJobsListCredentials)|

### <a name="CommandsInService">Commands in `az databox service` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az databox service list-available-sku-by-resource-group](#ServiceListAvailableSkusByResourceGroup)|ListAvailableSkusByResourceGroup|[Parameters](#ParametersServiceListAvailableSkusByResourceGroup)|[Example](#ExamplesServiceListAvailableSkusByResourceGroup)|
|[az databox service region-configuration](#ServiceRegionConfiguration)|RegionConfiguration|[Parameters](#ParametersServiceRegionConfiguration)|[Example](#ExamplesServiceRegionConfiguration)|
|[az databox service region-configuration-by-resource-group](#ServiceRegionConfigurationByResourceGroup)|RegionConfigurationByResourceGroup|[Parameters](#ParametersServiceRegionConfigurationByResourceGroup)|[Example](#ExamplesServiceRegionConfigurationByResourceGroup)|
|[az databox service validate-address](#ServiceValidateAddress)|ValidateAddress|[Parameters](#ParametersServiceValidateAddress)|[Example](#ExamplesServiceValidateAddress)|
|[az databox service validate-input](#ServiceValidateInputs)|ValidateInputs|[Parameters](#ParametersServiceValidateInputs)|[Example](#ExamplesServiceValidateInputs)|
|[az databox service validate-input-by-resource-group](#ServiceValidateInputsByResourceGroup)|ValidateInputsByResourceGroup|[Parameters](#ParametersServiceValidateInputsByResourceGroup)|[Example](#ExamplesServiceValidateInputsByResourceGroup)|


## COMMAND DETAILS

### group `az databox`
#### <a name="Mitigate">Command `az databox mitigate`</a>

##### <a name="ExamplesMitigate">Example</a>
```
az databox mitigate --job-name "SdkJob8367" --customer-resolution-code "MoveToCleanUpDevice" --resource-group \
"SdkRg9836"
```
##### <a name="ParametersMitigate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--job-name**|string|The name of the job Resource within the specified resource group. job names must be between 3 and 24 characters in length and use any alphanumeric and underscore only|job_name|jobName|
|**--resource-group-name**|string|The Resource Group Name|resource_group_name|resourceGroupName|
|**--customer-resolution-code**|sealed-choice|Resolution code for the job|customer_resolution_code|customerResolutionCode|

### group `az databox job`
#### <a name="JobsListByResourceGroup">Command `az databox job list`</a>

##### <a name="ExamplesJobsListByResourceGroup">Example</a>
```
az databox job list --resource-group "SdkRg5154"
```
##### <a name="ParametersJobsListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name|resource_group_name|resourceGroupName|
|**--skip-token**|string|$skipToken is supported on Get list of jobs, which provides the next page in the list of jobs.|skip_token|$skipToken|

#### <a name="JobsList">Command `az databox job list`</a>

##### <a name="ExamplesJobsList">Example</a>
```
az databox job list
```
##### <a name="ParametersJobsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="JobsGet">Command `az databox job show`</a>

##### <a name="ExamplesJobsGet">Example</a>
```
az databox job show --expand "details" --name "SdkJob952" --resource-group "SdkRg5154"
```
##### <a name="ExamplesJobsGet">Example</a>
```
az databox job show --expand "details" --name "SdkJob1735" --resource-group "SdkRg7937"
```
##### <a name="ExamplesJobsGet">Example</a>
```
az databox job show --expand "details" --name "TJx-637505258985313014" --resource-group "dmstestresource"
```
##### <a name="ExamplesJobsGet">Example</a>
```
az databox job show --expand "details" --name "SdkJob6429" --resource-group "SdkRg8091"
```
##### <a name="ParametersJobsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name|resource_group_name|resourceGroupName|
|**--job-name**|string|The name of the job Resource within the specified resource group. job names must be between 3 and 24 characters in length and use any alphanumeric and underscore only|job_name|jobName|
|**--expand**|string|$expand is supported on details parameter for job, which provides details on the job stages.|expand|$expand|

#### <a name="JobsCreate">Command `az databox job create`</a>

##### <a name="ExamplesJobsCreate">Example</a>
```
az databox job create --name "SdkJob952" --location "westus" --transfer-type "ImportToAzure" --details \
"{\\"contactDetails\\":{\\"contactName\\":\\"Public SDK Test\\",\\"emailList\\":[\\"testing@microsoft.com\\"],\\"phone\
\\":\\"1234567890\\",\\"phoneExtension\\":\\"1234\\"},\\"dataImportDetails\\":[{\\"accountDetails\\":{\\"dataAccountTyp\
e\\":\\"StorageAccount\\",\\"storageAccountId\\":\\"/subscriptions/fa68082f-8ff7-4a25-95c7-ce9da541242f/resourcegroups/\
databoxbvt/providers/Microsoft.Storage/storageAccounts/databoxbvttestaccount\\"}}],\\"jobDetailsType\\":\\"DataBox\\",\
\\"shippingAddress\\":{\\"addressType\\":\\"Commercial\\",\\"city\\":\\"San Francisco\\",\\"companyName\\":\\"Microsoft\
\\",\\"country\\":\\"US\\",\\"postalCode\\":\\"94107\\",\\"stateOrProvince\\":\\"CA\\",\\"streetAddress1\\":\\"16 \
TOWNSEND ST\\",\\"streetAddress2\\":\\"Unit 1\\"}}" --sku name="DataBox" --resource-group "SdkRg5154"
```
##### <a name="ExamplesJobsCreate">Example</a>
```
az databox job create --name "SdkJob9640" --location "westus" --transfer-type "ImportToAzure" --details \
"{\\"contactDetails\\":{\\"contactName\\":\\"Public SDK Test\\",\\"emailList\\":[\\"testing@microsoft.com\\"],\\"phone\
\\":\\"1234567890\\",\\"phoneExtension\\":\\"1234\\"},\\"dataImportDetails\\":[{\\"accountDetails\\":{\\"dataAccountTyp\
e\\":\\"StorageAccount\\",\\"sharePassword\\":\\"<sharePassword>\\",\\"storageAccountId\\":\\"/subscriptions/fa68082f-8\
ff7-4a25-95c7-ce9da541242f/resourceGroups/databoxbvt1/providers/Microsoft.Storage/storageAccounts/databoxbvttestaccount\
2\\"}}],\\"devicePassword\\":\\"<devicePassword>\\",\\"jobDetailsType\\":\\"DataBox\\",\\"shippingAddress\\":{\\"addres\
sType\\":\\"Commercial\\",\\"city\\":\\"San Francisco\\",\\"companyName\\":\\"Microsoft\\",\\"country\\":\\"US\\",\\"po\
stalCode\\":\\"94107\\",\\"stateOrProvince\\":\\"CA\\",\\"streetAddress1\\":\\"16 TOWNSEND \
ST\\",\\"streetAddress2\\":\\"Unit 1\\"}}" --sku name="DataBox" --resource-group "SdkRg7478"
```
##### <a name="ExamplesJobsCreate">Example</a>
```
az databox job create --name "SdkJob6599" --location "westus" --transfer-type "ImportToAzure" --details \
"{\\"contactDetails\\":{\\"contactName\\":\\"Public SDK Test\\",\\"emailList\\":[\\"testing@microsoft.com\\"],\\"phone\
\\":\\"1234567890\\",\\"phoneExtension\\":\\"1234\\"},\\"dataImportDetails\\":[{\\"accountDetails\\":{\\"dataAccountTyp\
e\\":\\"StorageAccount\\",\\"storageAccountId\\":\\"/subscriptions/fa68082f-8ff7-4a25-95c7-ce9da541242f/resourcegroups/\
databoxbvt/providers/Microsoft.Storage/storageAccounts/databoxbvttestaccount\\"}}],\\"jobDetailsType\\":\\"DataBox\\",\
\\"preferences\\":{\\"encryptionPreferences\\":{\\"doubleEncryption\\":\\"Enabled\\"}},\\"shippingAddress\\":{\\"addres\
sType\\":\\"Commercial\\",\\"city\\":\\"San Francisco\\",\\"companyName\\":\\"Microsoft\\",\\"country\\":\\"US\\",\\"po\
stalCode\\":\\"94107\\",\\"stateOrProvince\\":\\"CA\\",\\"streetAddress1\\":\\"16 TOWNSEND \
ST\\",\\"streetAddress2\\":\\"Unit 1\\"}}" --sku name="DataBox" --resource-group "SdkRg608"
```
##### <a name="ExamplesJobsCreate">Example</a>
```
az databox job create --name "SdkJob6429" --location "westus" --transfer-type "ExportFromAzure" --details \
"{\\"contactDetails\\":{\\"contactName\\":\\"Public SDK Test\\",\\"emailList\\":[\\"testing@microsoft.com\\"],\\"phone\
\\":\\"1234567890\\",\\"phoneExtension\\":\\"1234\\"},\\"dataExportDetails\\":[{\\"accountDetails\\":{\\"dataAccountTyp\
e\\":\\"StorageAccount\\",\\"storageAccountId\\":\\"/subscriptions/fa68082f-8ff7-4a25-95c7-ce9da541242f/resourceGroups/\
akvenkat/providers/Microsoft.Storage/storageAccounts/aaaaaa2\\"},\\"transferConfiguration\\":{\\"transferAllDetails\\":\
{\\"include\\":{\\"dataAccountType\\":\\"StorageAccount\\",\\"transferAllBlobs\\":true,\\"transferAllFiles\\":true}},\\\
"transferConfigurationType\\":\\"TransferAll\\"}}],\\"jobDetailsType\\":\\"DataBox\\",\\"shippingAddress\\":{\\"address\
Type\\":\\"Commercial\\",\\"city\\":\\"San Francisco\\",\\"companyName\\":\\"Microsoft\\",\\"country\\":\\"US\\",\\"pos\
talCode\\":\\"94107\\",\\"stateOrProvince\\":\\"CA\\",\\"streetAddress1\\":\\"16 TOWNSEND \
ST\\",\\"streetAddress2\\":\\"Unit 1\\"}}" --sku name="DataBox" --resource-group "SdkRg8091"
```
##### <a name="ExamplesJobsCreate">Example</a>
```
az databox job create --name "SdkJob5337" --type "UserAssigned" --user-assigned-identities \
"{\\"/subscriptions/fa68082f-8ff7-4a25-95c7-ce9da541242f/resourceGroups/akvenkat/providers/Microsoft.ManagedIdentity/us\
erAssignedIdentities/sdkIdentity\\":{}}" --location "westus" --transfer-type "ImportToAzure" --details \
"{\\"contactDetails\\":{\\"contactName\\":\\"Public SDK Test\\",\\"emailList\\":[\\"testing@microsoft.com\\"],\\"phone\
\\":\\"1234567890\\",\\"phoneExtension\\":\\"1234\\"},\\"dataImportDetails\\":[{\\"accountDetails\\":{\\"dataAccountTyp\
e\\":\\"StorageAccount\\",\\"storageAccountId\\":\\"/subscriptions/fa68082f-8ff7-4a25-95c7-ce9da541242f/resourceGroups/\
databoxbvt1/providers/Microsoft.Storage/storageAccounts/databoxbvttestaccount2\\"}}],\\"jobDetailsType\\":\\"DataBox\\"\
,\\"shippingAddress\\":{\\"addressType\\":\\"Commercial\\",\\"city\\":\\"San Francisco\\",\\"companyName\\":\\"Microsof\
t\\",\\"country\\":\\"US\\",\\"postalCode\\":\\"94107\\",\\"stateOrProvince\\":\\"CA\\",\\"streetAddress1\\":\\"16 \
TOWNSEND ST\\",\\"streetAddress2\\":\\"Unit 1\\"}}" --sku name="DataBox" --resource-group "SdkRg7552"
```
##### <a name="ParametersJobsCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name|resource_group_name|resourceGroupName|
|**--job-name**|string|The name of the job Resource within the specified resource group. job names must be between 3 and 24 characters in length and use any alphanumeric and underscore only|job_name|jobName|
|**--location**|string|The location of the resource. This will be one of the supported and registered Azure Regions (e.g. West US, East US, Southeast Asia, etc.). The region of a resource cannot be changed once it is created, but if an identical region is specified on update the request will succeed.|location|location|
|**--sku**|object|The sku type.|sku|sku|
|**--transfer-type**|sealed-choice|Type of the data transfer.|transfer_type|transferType|
|**--tags**|dictionary|The list of key value pairs that describe the resource. These tags can be used in viewing and grouping this resource (across resource groups).|tags|tags|
|**--type**|string|Identity type|type|type|
|**--user-assigned-identities**|dictionary|User Assigned Identities|user_assigned_identities|userAssignedIdentities|
|**--details**|object|Details of a job run. This field will only be sent for expand details filter.|details|details|
|**--delivery-type**|sealed-choice|Delivery type of Job.|delivery_type|deliveryType|
|**--scheduled-date-time**|date-time|Scheduled date time.|scheduled_date_time|scheduledDateTime|

#### <a name="JobsUpdate">Command `az databox job update`</a>

##### <a name="ExamplesJobsUpdate">Example</a>
```
az databox job update --name "SdkJob952" --contact-name "Update Job" --email-list "testing@microsoft.com" --phone \
"1234567890" --phone-extension "1234" --shipping-address address-type="Commercial" city="San Francisco" \
company-name="Microsoft" country="US" postal-code="94107" state-or-province="CA" street-address1="16 TOWNSEND ST" \
street-address2="Unit 1" --resource-group "SdkRg5154"
```
##### <a name="ExamplesJobsUpdate">Example</a>
```
az databox job update --name "SdkJob1735" --kek-type "CustomerManaged" --kek-url "https://sdkkeyvault.vault.azure.net/k\
eys/SSDKEY/" --kek-vault-resource-id "/subscriptions/fa68082f-8ff7-4a25-95c7-ce9da541242f/resourceGroups/akvenkat/provi\
ders/Microsoft.KeyVault/vaults/SDKKeyVault" --resource-group "SdkRg7937"
```
##### <a name="ExamplesJobsUpdate">Example</a>
```
az databox job update --name "SdkJob2965" --resource-identity-type "SystemAssigned,UserAssigned" \
--user-assigned-identities "{\\"/subscriptions/fa68082f-8ff7-4a25-95c7-ce9da541242f/resourceGroups/akvenkat/providers/M\
icrosoft.ManagedIdentity/userAssignedIdentities/sdkIdentity\\":{}}" --type "UserAssigned" --user-assigned \
resource-id="/subscriptions/fa68082f-8ff7-4a25-95c7-ce9da541242f/resourceGroups/akvenkat/providers/Microsoft.ManagedIde\
ntity/userAssignedIdentities/sdkIdentity" --kek-type "CustomerManaged" --kek-url "https://sdkkeyvault.vault.azure.net/k\
eys/SSDKEY/" --kek-vault-resource-id "/subscriptions/fa68082f-8ff7-4a25-95c7-ce9da541242f/resourceGroups/akvenkat/provi\
ders/Microsoft.KeyVault/vaults/SDKKeyVault" --resource-group "SdkRg9765"
```
##### <a name="ParametersJobsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name|resource_group_name|resourceGroupName|
|**--job-name**|string|The name of the job Resource within the specified resource group. job names must be between 3 and 24 characters in length and use any alphanumeric and underscore only|job_name|jobName|
|**--if-match**|string|Defines the If-Match condition. The patch will be performed only if the ETag of the job on the server matches this value.|if_match|If-Match|
|**--tags**|dictionary|The list of key value pairs that describe the resource. These tags can be used in viewing and grouping this resource (across resource groups).|tags|tags|
|**--shipping-address**|object|Shipping address of the customer.|shipping_address|shippingAddress|
|**--kek-type**|sealed-choice|Type of encryption key used for key encryption.|kek_type|kekType|
|**--kek-url**|string|Key encryption key. It is required in case of Customer managed KekType.|kek_url|kekUrl|
|**--kek-vault-resource-id**|string|Kek vault resource id. It is required in case of Customer managed KekType.|kek_vault_resource_id|kekVaultResourceID|
|**--type**|string|Managed service identity type.|type|type|
|**--user-assigned**|object|User assigned identity properties.|user_assigned|userAssigned|
|**--contact-name**|string|Contact name of the person.|contact_name|contactName|
|**--phone**|string|Phone number of the contact person.|phone|phone|
|**--phone-extension**|string|Phone extension number of the contact person.|phone_extension|phoneExtension|
|**--mobile**|string|Mobile number of the contact person.|mobile|mobile|
|**--email-list**|array|List of Email-ids to be notified about job progress.|email_list|emailList|
|**--notification-preference**|array|Notification preference for a job stage.|notification_preference|notificationPreference|
|**--resource-identity-type**|string|Identity type|resource_identity_type|type|
|**--user-assigned-identities**|dictionary|User Assigned Identities|user_assigned_identities|userAssignedIdentities|

#### <a name="JobsDelete">Command `az databox job delete`</a>

##### <a name="ExamplesJobsDelete">Example</a>
```
az databox job delete --name "SdkJob952" --resource-group "SdkRg5154"
```
##### <a name="ParametersJobsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name|resource_group_name|resourceGroupName|
|**--job-name**|string|The name of the job Resource within the specified resource group. job names must be between 3 and 24 characters in length and use any alphanumeric and underscore only|job_name|jobName|

#### <a name="JobsBookShipmentPickUp">Command `az databox job book-shipment-pick-up`</a>

##### <a name="ExamplesJobsBookShipmentPickUp">Example</a>
```
az databox job book-shipment-pick-up --name "TJ-636646322037905056" --resource-group "bvttoolrg6" --end-time \
"2019-09-22T18:30:00Z" --shipment-location "Front desk" --start-time "2019-09-20T18:30:00Z"
```
##### <a name="ParametersJobsBookShipmentPickUp">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name|resource_group_name|resourceGroupName|
|**--job-name**|string|The name of the job Resource within the specified resource group. job names must be between 3 and 24 characters in length and use any alphanumeric and underscore only|job_name|jobName|
|**--start-time**|date-time|Minimum date after which the pick up should commence, this must be in local time of pick up area.|start_time|startTime|
|**--end-time**|date-time|Maximum date before which the pick up should commence, this must be in local time of pick up area.|end_time|endTime|
|**--shipment-location**|string|Shipment Location in the pickup place. Eg.front desk|shipment_location|shipmentLocation|

#### <a name="JobsCancel">Command `az databox job cancel`</a>

##### <a name="ExamplesJobsCancel">Example</a>
```
az databox job cancel --reason "CancelTest" --name "SdkJob952" --resource-group "SdkRg5154"
```
##### <a name="ParametersJobsCancel">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name|resource_group_name|resourceGroupName|
|**--job-name**|string|The name of the job Resource within the specified resource group. job names must be between 3 and 24 characters in length and use any alphanumeric and underscore only|job_name|jobName|
|**--reason**|string|Reason for cancellation.|reason|reason|

#### <a name="JobsListCredentials">Command `az databox job list-credentials`</a>

##### <a name="ExamplesJobsListCredentials">Example</a>
```
az databox job list-credentials --name "TJ-636646322037905056" --resource-group "bvttoolrg6"
```
##### <a name="ParametersJobsListCredentials">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name|resource_group_name|resourceGroupName|
|**--job-name**|string|The name of the job Resource within the specified resource group. job names must be between 3 and 24 characters in length and use any alphanumeric and underscore only|job_name|jobName|

### group `az databox service`
#### <a name="ServiceListAvailableSkusByResourceGroup">Command `az databox service list-available-sku-by-resource-group`</a>

##### <a name="ExamplesServiceListAvailableSkusByResourceGroup">Example</a>
```
az databox service list-available-sku-by-resource-group --country "US" --available-sku-request-location "westus" \
--transfer-type "ImportToAzure" --location "westus" --resource-group "bvttoolrg6"
```
##### <a name="ParametersServiceListAvailableSkusByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name|resource_group_name|resourceGroupName|
|**--location**|string|The location of the resource|location|location|
|**--transfer-type**|sealed-choice|Type of the transfer.|transfer_type|transferType|
|**--country**|string|ISO country code. Country for hardware shipment. For codes check: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2#Officially_assigned_code_elements|country|country|
|**--available-sku-request-location**|string|Location for data transfer. For locations check: https://management.azure.com/subscriptions/SUBSCRIPTIONID/locations?api-version=2018-01-01|available_sku_request_location|location|
|**--sku-names**|array|Sku Names to filter for available skus|sku_names|skuNames|

#### <a name="ServiceRegionConfiguration">Command `az databox service region-configuration`</a>

##### <a name="ExamplesServiceRegionConfiguration">Example</a>
```
az databox service region-configuration --location "westus" --schedule-availability-request \
"{\\"skuName\\":\\"DataBox\\",\\"storageLocation\\":\\"westus\\"}"
```
##### <a name="ParametersServiceRegionConfiguration">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location**|string|The location of the resource|location|location|
|**--data-box-schedule-availability-request**|object|Request body to get the availability for scheduling data box orders orders.|data_box_schedule_availability_request|DataBoxScheduleAvailabilityRequest|
|**--disk-schedule-availability-request**|object|Request body to get the availability for scheduling disk orders.|disk_schedule_availability_request|DiskScheduleAvailabilityRequest|
|**--heavy-schedule-availability-request**|object|Request body to get the availability for scheduling heavy orders.|heavy_schedule_availability_request|HeavyScheduleAvailabilityRequest|
|**--sku-name**|sealed-choice|Type of the device.|sku_name|skuName|

#### <a name="ServiceRegionConfigurationByResourceGroup">Command `az databox service region-configuration-by-resource-group`</a>

##### <a name="ExamplesServiceRegionConfigurationByResourceGroup">Example</a>
```
az databox service region-configuration-by-resource-group --location "westus" --schedule-availability-request \
"{\\"skuName\\":\\"DataBox\\",\\"storageLocation\\":\\"westus\\"}" --resource-group "SdkRg4981"
```
##### <a name="ParametersServiceRegionConfigurationByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name|resource_group_name|resourceGroupName|
|**--location**|string|The location of the resource|location|location|
|**--data-box-schedule-availability-request**|object|Request body to get the availability for scheduling data box orders orders.|data_box_schedule_availability_request|DataBoxScheduleAvailabilityRequest|
|**--disk-schedule-availability-request**|object|Request body to get the availability for scheduling disk orders.|disk_schedule_availability_request|DiskScheduleAvailabilityRequest|
|**--heavy-schedule-availability-request**|object|Request body to get the availability for scheduling heavy orders.|heavy_schedule_availability_request|HeavyScheduleAvailabilityRequest|
|**--sku-name**|sealed-choice|Type of the device.|sku_name|skuName|

#### <a name="ServiceValidateAddress">Command `az databox service validate-address`</a>

##### <a name="ExamplesServiceValidateAddress">Example</a>
```
az databox service validate-address --location "westus" --device-type "DataBox" --shipping-address \
address-type="Commercial" city="San Francisco" company-name="Microsoft" country="US" postal-code="94107" \
state-or-province="CA" street-address1="16 TOWNSEND ST" street-address2="Unit 1" --validation-type "ValidateAddress"
```
##### <a name="ParametersServiceValidateAddress">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location**|string|The location of the resource|location|location|
|**--validation-type**|sealed-choice|Identifies the type of validation request.|validation_type|validationType|
|**--shipping-address**|object|Shipping address of the customer.|shipping_address|shippingAddress|
|**--device-type**|sealed-choice|Device type to be used for the job.|device_type|deviceType|
|**--preferred-shipment-type**|sealed-choice|Indicates Shipment Logistics type that the customer preferred.|preferred_shipment_type|preferredShipmentType|

#### <a name="ServiceValidateInputs">Command `az databox service validate-input`</a>

##### <a name="ExamplesServiceValidateInputs">Example</a>
```
az databox service validate-input --location "westus" --validation-request "{\\"individualRequestDetails\\":[{\\"dataIm\
portDetails\\":[{\\"accountDetails\\":{\\"dataAccountType\\":\\"StorageAccount\\",\\"storageAccountId\\":\\"/subscripti\
ons/fa68082f-8ff7-4a25-95c7-ce9da541242f/resourcegroups/databoxbvt/providers/Microsoft.Storage/storageAccounts/databoxb\
vttestaccount\\"}}],\\"deviceType\\":\\"DataBox\\",\\"transferType\\":\\"ImportToAzure\\",\\"validationType\\":\\"Valid\
ateDataTransferDetails\\"},{\\"deviceType\\":\\"DataBox\\",\\"shippingAddress\\":{\\"addressType\\":\\"Commercial\\",\\\
"city\\":\\"San Francisco\\",\\"companyName\\":\\"Microsoft\\",\\"country\\":\\"US\\",\\"postalCode\\":\\"94107\\",\\"s\
tateOrProvince\\":\\"CA\\",\\"streetAddress1\\":\\"16 TOWNSEND ST\\",\\"streetAddress2\\":\\"Unit \
1\\"},\\"transportPreferences\\":{\\"preferredShipmentType\\":\\"MicrosoftManaged\\"},\\"validationType\\":\\"ValidateA\
ddress\\"},{\\"validationType\\":\\"ValidateSubscriptionIsAllowedToCreateJob\\"},{\\"country\\":\\"US\\",\\"deviceType\
\\":\\"DataBox\\",\\"location\\":\\"westus\\",\\"transferType\\":\\"ImportToAzure\\",\\"validationType\\":\\"ValidateSk\
uAvailability\\"},{\\"deviceType\\":\\"DataBox\\",\\"validationType\\":\\"ValidateCreateOrderLimit\\"},{\\"deviceType\\\
":\\"DataBox\\",\\"preference\\":{\\"transportPreferences\\":{\\"preferredShipmentType\\":\\"MicrosoftManaged\\"}},\\"v\
alidationType\\":\\"ValidatePreferences\\"}],\\"validationCategory\\":\\"JobCreationValidation\\"}"
```
##### <a name="ParametersServiceValidateInputs">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location**|string|The location of the resource|location|location|
|**--create-job-validations**|object|It does all pre-job creation validations.|create_job_validations|CreateJobValidations|

#### <a name="ServiceValidateInputsByResourceGroup">Command `az databox service validate-input-by-resource-group`</a>

##### <a name="ExamplesServiceValidateInputsByResourceGroup">Example</a>
```
az databox service validate-input-by-resource-group --location "westus" --resource-group "SdkRg6861" \
--validation-request "{\\"individualRequestDetails\\":[{\\"dataImportDetails\\":[{\\"accountDetails\\":{\\"dataAccountT\
ype\\":\\"StorageAccount\\",\\"storageAccountId\\":\\"/subscriptions/fa68082f-8ff7-4a25-95c7-ce9da541242f/resourcegroup\
s/databoxbvt/providers/Microsoft.Storage/storageAccounts/databoxbvttestaccount\\"}}],\\"deviceType\\":\\"DataBox\\",\\"\
transferType\\":\\"ImportToAzure\\",\\"validationType\\":\\"ValidateDataTransferDetails\\"},{\\"deviceType\\":\\"DataBo\
x\\",\\"shippingAddress\\":{\\"addressType\\":\\"Commercial\\",\\"city\\":\\"San Francisco\\",\\"companyName\\":\\"Micr\
osoft\\",\\"country\\":\\"US\\",\\"postalCode\\":\\"94107\\",\\"stateOrProvince\\":\\"CA\\",\\"streetAddress1\\":\\"16 \
TOWNSEND ST\\",\\"streetAddress2\\":\\"Unit 1\\"},\\"transportPreferences\\":{\\"preferredShipmentType\\":\\"MicrosoftM\
anaged\\"},\\"validationType\\":\\"ValidateAddress\\"},{\\"validationType\\":\\"ValidateSubscriptionIsAllowedToCreateJo\
b\\"},{\\"country\\":\\"US\\",\\"deviceType\\":\\"DataBox\\",\\"location\\":\\"westus\\",\\"transferType\\":\\"ImportTo\
Azure\\",\\"validationType\\":\\"ValidateSkuAvailability\\"},{\\"deviceType\\":\\"DataBox\\",\\"validationType\\":\\"Va\
lidateCreateOrderLimit\\"},{\\"deviceType\\":\\"DataBox\\",\\"preference\\":{\\"transportPreferences\\":{\\"preferredSh\
ipmentType\\":\\"MicrosoftManaged\\"}},\\"validationType\\":\\"ValidatePreferences\\"}],\\"validationCategory\\":\\"Job\
CreationValidation\\"}"
```
##### <a name="ParametersServiceValidateInputsByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name|resource_group_name|resourceGroupName|
|**--location**|string|The location of the resource|location|location|
|**--create-job-validations**|object|It does all pre-job creation validations.|create_job_validations|CreateJobValidations|
