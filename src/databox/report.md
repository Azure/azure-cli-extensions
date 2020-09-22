# Azure CLI Module Creation Report

### databox job book-shipment-pick-up

book-shipment-pick-up a databox job.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databox job|Jobs|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|book-shipment-pick-up|BookShipmentPickUp|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name|resource_group_name|resourceGroupName|
|**--job-name**|string|The name of the job Resource within the specified resource group. job names must be between 3 and 24 characters in length and use any alphanumeric and underscore only|job_name|jobName|
|**--start-time**|date-time|Minimum date after which the pick up should commence, this must be in local time of pick up area.|start_time|startTime|
|**--end-time**|date-time|Maximum date before which the pick up should commence, this must be in local time of pick up area.|end_time|endTime|
|**--shipment-location**|string|Shipment Location in the pickup place. Eg.front desk|shipment_location|shipmentLocation|

### databox job cancel

cancel a databox job.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databox job|Jobs|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|cancel|Cancel|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name|resource_group_name|resourceGroupName|
|**--job-name**|string|The name of the job Resource within the specified resource group. job names must be between 3 and 24 characters in length and use any alphanumeric and underscore only|job_name|jobName|
|**--reason**|string|Reason for cancellation.|reason|reason|

### databox job create

create a databox job.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databox job|Jobs|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name|resource_group_name|resourceGroupName|
|**--job-name**|string|The name of the job Resource within the specified resource group. job names must be between 3 and 24 characters in length and use any alphanumeric and underscore only|job_name|jobName|
|**--location**|string|The location of the resource. This will be one of the supported and registered Azure Regions (e.g. West US, East US, Southeast Asia, etc.). The region of a resource cannot be changed once it is created, but if an identical region is specified on update the request will succeed.|location|location|
|**--sku**|object|The sku type.|sku|sku|
|**--transfer-type**|sealed-choice|Type of the data transfer.|transfer_type|transferType|
|**--tags**|dictionary|The list of key value pairs that describe the resource. These tags can be used in viewing and grouping this resource (across resource groups).|tags|tags|
|**--identity-type**|string|Identity type|type|type|
|**--details**|object|Details of a job run. This field will only be sent for expand details filter.|details|details|
|**--delivery-type**|sealed-choice|Delivery type of Job.|delivery_type|deliveryType|
|**--delivery-info-scheduled-date-time**|date-time|Scheduled date time.|scheduled_date_time|scheduledDateTime|

### databox job delete

delete a databox job.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databox job|Jobs|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name|resource_group_name|resourceGroupName|
|**--job-name**|string|The name of the job Resource within the specified resource group. job names must be between 3 and 24 characters in length and use any alphanumeric and underscore only|job_name|jobName|

### databox job list

list a databox job.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databox job|Jobs|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByResourceGroup|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name|resource_group_name|resourceGroupName|
|**--skip-token**|string|$skipToken is supported on Get list of jobs, which provides the next page in the list of jobs.|skip_token|$skipToken|

### databox job list-credentials

list-credentials a databox job.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databox job|Jobs|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list-credentials|ListCredentials|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name|resource_group_name|resourceGroupName|
|**--job-name**|string|The name of the job Resource within the specified resource group. job names must be between 3 and 24 characters in length and use any alphanumeric and underscore only|job_name|jobName|

### databox job show

show a databox job.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databox job|Jobs|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name|resource_group_name|resourceGroupName|
|**--job-name**|string|The name of the job Resource within the specified resource group. job names must be between 3 and 24 characters in length and use any alphanumeric and underscore only|job_name|jobName|
|**--expand**|string|$expand is supported on details parameter for job, which provides details on the job stages.|expand|$expand|

### databox job update

update a databox job.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databox job|Jobs|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name|resource_group_name|resourceGroupName|
|**--job-name**|string|The name of the job Resource within the specified resource group. job names must be between 3 and 24 characters in length and use any alphanumeric and underscore only|job_name|jobName|
|**--if-match**|string|Defines the If-Match condition. The patch will be performed only if the ETag of the job on the server matches this value.|if_match|If-Match|
|**--tags**|dictionary|The list of key value pairs that describe the resource. These tags can be used in viewing and grouping this resource (across resource groups).|tags|tags|
|**--identity-type**|string|Identity type|type|type|
|**--details**|object|Details of a job to be updated.|details|details|

### databox service list-available-sku-by-resource-group

list-available-sku-by-resource-group a databox service.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databox service|Service|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list-available-sku-by-resource-group|ListAvailableSkusByResourceGroup|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name|resource_group_name|resourceGroupName|
|**--location**|string|The location of the resource|location|location|
|**--transfer-type**|sealed-choice|Type of the transfer.|transfer_type|transferType|
|**--country**|string|ISO country code. Country for hardware shipment. For codes check: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2#Officially_assigned_code_elements|country|country|
|**--available-sku-request-location**|string|Location for data transfer. For locations check: https://management.azure.com/subscriptions/SUBSCRIPTIONID/locations?api-version=2018-01-01|available_sku_request_location|location|
|**--sku-names**|array|Sku Names to filter for available skus|sku_names|skuNames|

### databox service region-configuration

region-configuration a databox service.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databox service|Service|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|region-configuration|RegionConfiguration|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location**|string|The location of the resource|location|location|
|**--data-box-schedule-availability-request**|object|Request body to get the availability for scheduling data box orders orders.|data_box_schedule_availability_request|DataBoxScheduleAvailabilityRequest|
|**--disk-schedule-availability-request**|object|Request body to get the availability for scheduling disk orders.|disk_schedule_availability_request|DiskScheduleAvailabilityRequest|
|**--heavy-schedule-availability-request**|object|Request body to get the availability for scheduling heavy orders.|heavy_schedule_availability_request|HeavyScheduleAvailabilityRequest|
|**--transport-availability-request-sku-name**|sealed-choice|Type of the device.|sku_name|skuName|

### databox service region-configuration-by-resource-group

region-configuration-by-resource-group a databox service.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databox service|Service|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|region-configuration-by-resource-group|RegionConfigurationByResourceGroup|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name|resource_group_name|resourceGroupName|
|**--location**|string|The location of the resource|location|location|
|**--data-box-schedule-availability-request**|object|Request body to get the availability for scheduling data box orders orders.|data_box_schedule_availability_request|DataBoxScheduleAvailabilityRequest|
|**--disk-schedule-availability-request**|object|Request body to get the availability for scheduling disk orders.|disk_schedule_availability_request|DiskScheduleAvailabilityRequest|
|**--heavy-schedule-availability-request**|object|Request body to get the availability for scheduling heavy orders.|heavy_schedule_availability_request|HeavyScheduleAvailabilityRequest|
|**--transport-availability-request-sku-name**|sealed-choice|Type of the device.|sku_name|skuName|

### databox service validate-address

validate-address a databox service.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databox service|Service|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|validate-address|ValidateAddress|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location**|string|The location of the resource|location|location|
|**--validation-type**|sealed-choice|Identifies the type of validation request.|validation_type|validationType|
|**--shipping-address**|object|Shipping address of the customer.|shipping_address|shippingAddress|
|**--device-type**|sealed-choice|Device type to be used for the job.|device_type|deviceType|
|**--transport-preferences-preferred-shipment-type**|sealed-choice|Indicates Shipment Logistics type that the customer preferred.|preferred_shipment_type|preferredShipmentType|

### databox service validate-input

validate-input a databox service.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databox service|Service|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|validate-input|ValidateInputs|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location**|string|The location of the resource|location|location|
|**--create-job-validations**|object|It does all pre-job creation validations.|create_job_validations|CreateJobValidations|

### databox service validate-input-by-resource-group

validate-input-by-resource-group a databox service.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databox service|Service|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|validate-input-by-resource-group|ValidateInputsByResourceGroup|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The Resource Group Name|resource_group_name|resourceGroupName|
|**--location**|string|The location of the resource|location|location|
|**--create-job-validations**|object|It does all pre-job creation validations.|create_job_validations|CreateJobValidations|
