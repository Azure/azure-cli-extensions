# Azure CLI Module Creation Report

### databox job book-shipment-pick-up

book-shipment-pick-up a databox job.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The Resource Group Name|resource_group_name|
|**--job-name**|string|The name of the job Resource within the specified resource group. job names must be between 3 and 24 characters in length and use any alphanumeric and underscore only|job_name|
|**--start-time**|date-time|Minimum date after which the pick up should commence, this must be in local time of pick up area.|start_time|
|**--end-time**|date-time|Maximum date before which the pick up should commence, this must be in local time of pick up area.|end_time|
|**--shipment-location**|string|Shipment Location in the pickup place. Eg.front desk|shipment_location|
### databox job cancel

cancel a databox job.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The Resource Group Name|resource_group_name|
|**--job-name**|string|The name of the job Resource within the specified resource group. job names must be between 3 and 24 characters in length and use any alphanumeric and underscore only|job_name|
|**--reason**|string|Reason for cancellation.|reason|
### databox job create

create a databox job.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The Resource Group Name|resource_group_name|
|**--job-name**|string|The name of the job Resource within the specified resource group. job names must be between 3 and 24 characters in length and use any alphanumeric and underscore only|job_name|
|**--location**|string|The location of the resource. This will be one of the supported and registered Azure Regions (e.g. West US, East US, Southeast Asia, etc.). The region of a resource cannot be changed once it is created, but if an identical region is specified on update the request will succeed.|location|
|**--sku**|object|The sku type.|sku|
|**--transfer-type**|sealed-choice|Type of the data transfer.|transfer_type|
|**--tags**|dictionary|The list of key value pairs that describe the resource. These tags can be used in viewing and grouping this resource (across resource groups).|tags|
|**--identity-type**|string|Identity type|type|
|**--details**|object|Details of a job run. This field will only be sent for expand details filter.|details|
|**--delivery-type**|sealed-choice|Delivery type of Job.|delivery_type|
|**--delivery-info-scheduled-date-time**|date-time|Scheduled date time.|scheduled_date_time|
### databox job delete

delete a databox job.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The Resource Group Name|resource_group_name|
|**--job-name**|string|The name of the job Resource within the specified resource group. job names must be between 3 and 24 characters in length and use any alphanumeric and underscore only|job_name|
### databox job list

list a databox job.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The Resource Group Name|resource_group_name|
|**--skip-token**|string|$skipToken is supported on Get list of jobs, which provides the next page in the list of jobs.|skip_token|
### databox job list-credentials

list-credentials a databox job.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The Resource Group Name|resource_group_name|
|**--job-name**|string|The name of the job Resource within the specified resource group. job names must be between 3 and 24 characters in length and use any alphanumeric and underscore only|job_name|
### databox job show

show a databox job.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The Resource Group Name|resource_group_name|
|**--job-name**|string|The name of the job Resource within the specified resource group. job names must be between 3 and 24 characters in length and use any alphanumeric and underscore only|job_name|
|**--expand**|string|$expand is supported on details parameter for job, which provides details on the job stages.|expand|
### databox job update

update a databox job.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The Resource Group Name|resource_group_name|
|**--job-name**|string|The name of the job Resource within the specified resource group. job names must be between 3 and 24 characters in length and use any alphanumeric and underscore only|job_name|
|**--if-match**|string|Defines the If-Match condition. The patch will be performed only if the ETag of the job on the server matches this value.|if_match|
|**--tags**|dictionary|The list of key value pairs that describe the resource. These tags can be used in viewing and grouping this resource (across resource groups).|tags|
|**--identity-type**|string|Identity type|type|
|**--details**|object|Details of a job to be updated.|details|
### databox service list-available-sku-by-resource-group

list-available-sku-by-resource-group a databox service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The Resource Group Name|resource_group_name|
|**--location**|string|The location of the resource|location|
|**--transfer-type**|sealed-choice|Type of the transfer.|transfer_type|
|**--country**|string|ISO country code. Country for hardware shipment. For codes check: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2#Officially_assigned_code_elements|country|
|**--sku-names**|array|Sku Names to filter for available skus|sku_names|
### databox service region-configuration

region-configuration a databox service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--location**|string|The location of the resource|location|
|**--data-box-schedule-availability-request**|object|Request body to get the availability for scheduling data box orders orders.|data_box_schedule_availability_request|
|**--disk-schedule-availability-request**|object|Request body to get the availability for scheduling disk orders.|disk_schedule_availability_request|
|**--heavy-schedule-availability-request**|object|Request body to get the availability for scheduling heavy orders.|heavy_schedule_availability_request|
|**--transport-availability-request-sku-name**|sealed-choice|Type of the device.|sku_name|
### databox service region-configuration-by-resource-group

region-configuration-by-resource-group a databox service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The Resource Group Name|resource_group_name|
|**--location**|string|The location of the resource|location|
|**--data-box-schedule-availability-request**|object|Request body to get the availability for scheduling data box orders orders.|data_box_schedule_availability_request|
|**--disk-schedule-availability-request**|object|Request body to get the availability for scheduling disk orders.|disk_schedule_availability_request|
|**--heavy-schedule-availability-request**|object|Request body to get the availability for scheduling heavy orders.|heavy_schedule_availability_request|
|**--transport-availability-request-sku-name**|sealed-choice|Type of the device.|sku_name|
### databox service validate-address

validate-address a databox service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--location**|string|The location of the resource|location|
|**--validation-type**|sealed-choice|Identifies the type of validation request.|validation_type|
|**--shipping-address**|object|Shipping address of the customer.|shipping_address|
|**--device-type**|sealed-choice|Device type to be used for the job.|device_type|
|**--transport-preferences-preferred-shipment-type**|sealed-choice|Indicates Shipment Logistics type that the customer preferred.|preferred_shipment_type|
### databox service validate-input

validate-input a databox service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--location**|string|The location of the resource|location|
|**--create-job-validations**|object|It does all pre-job creation validations.|create_job_validations|
### databox service validate-input-by-resource-group

validate-input-by-resource-group a databox service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The Resource Group Name|resource_group_name|
|**--location**|string|The location of the resource|location|
|**--create-job-validations**|object|It does all pre-job creation validations.|create_job_validations|