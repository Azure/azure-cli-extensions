# Azure CLI Module Creation Report

### storageimportexport bit-locker-key list

list a storageimportexport bit-locker-key.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--job_name**|string|The name of the import/export job.|job_name|job_name|
|**--resource_group_name**|string|The resource group name uniquely identifies the resource group within the user subscription.|resource_group_name|resource_group_name|
### storageimportexport job create

create a storageimportexport job.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--job_name**|string|The name of the import/export job.|job_name|job_name|
|**--resource_group_name**|string|The resource group name uniquely identifies the resource group within the user subscription.|resource_group_name|resource_group_name|
|**--client_tenant_id**|string|The tenant ID of the client making the request.|client_tenant_id|client_tenant_id|
|**--location**|string|Specifies the supported Azure location where the job should be created|location|location|
|**--tags**|any|Specifies the tags that will be assigned to the job.|tags|tags|
|**--storage_account_id**|string|The resource identifier of the storage account where data will be imported to or exported from.|storage_account_id|properties_storage_account_id|
|**--job_type**|string|The type of job|job_type|properties_job_type|
|**--return_address**|object|Specifies the return address information for the job.|return_address|properties_return_address|
|**--return_shipping**|object|Specifies the return carrier and customer's account with the carrier.|return_shipping|properties_return_shipping|
|**--shipping_information**|object|Contains information about the Microsoft datacenter to which the drives should be shipped.|shipping_information|properties_shipping_information|
|**--delivery_package**|object|Contains information about the package being shipped by the customer to the Microsoft data center.|delivery_package|properties_delivery_package|
|**--return_package**|object|Contains information about the package being shipped from the Microsoft data center to the customer to return the drives. The format is the same as the deliveryPackage property above. This property is not included if the drives have not yet been returned.|return_package|properties_return_package|
|**--diagnostics_path**|string|The virtual blob directory to which the copy logs and backups of drive manifest files (if enabled) will be stored.|diagnostics_path|properties_diagnostics_path|
|**--log_level**|string|Default value is Error. Indicates whether error logging or verbose logging will be enabled.|log_level|properties_log_level|
|**--backup_drive_manifest**|boolean|Default value is false. Indicates whether the manifest files on the drives should be copied to block blobs.|backup_drive_manifest|properties_backup_drive_manifest|
|**--state**|string|Current state of the job.|state|properties_state|
|**--cancel_requested**|boolean|Indicates whether a request has been submitted to cancel the job.|cancel_requested|properties_cancel_requested|
|**--percent_complete**|integer|Overall percentage completed for the job.|percent_complete|properties_percent_complete|
|**--incomplete_blob_list_uri**|string|A blob path that points to a block blob containing a list of blob names that were not exported due to insufficient drive space. If all blobs were exported successfully, then this element is not included in the response.|incomplete_blob_list_uri|properties_incomplete_blob_list_uri|
|**--drive_list**|array|List of up to ten drives that comprise the job. The drive list is a required element for an import job; it is not specified for export jobs.|drive_list|properties_drive_list|
|**--export**|object|A property containing information about the blobs to be exported for an export job. This property is included for export jobs only.|export|properties_export|
|**--provisioning_state**|string|Specifies the provisioning state of the job.|provisioning_state|properties_provisioning_state|
### storageimportexport job delete

delete a storageimportexport job.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--job_name**|string|The name of the import/export job.|job_name|job_name|
|**--resource_group_name**|string|The resource group name uniquely identifies the resource group within the user subscription.|resource_group_name|resource_group_name|
### storageimportexport job list

list a storageimportexport job.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name uniquely identifies the resource group within the user subscription.|resource_group_name|resource_group_name|
|**--top**|integer|An integer value that specifies how many jobs at most should be returned. The value cannot exceed 100.|top|top|
|**--filter**|string|Can be used to restrict the results to certain conditions.|filter|filter|
### storageimportexport job show

show a storageimportexport job.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--job_name**|string|The name of the import/export job.|job_name|job_name|
|**--resource_group_name**|string|The resource group name uniquely identifies the resource group within the user subscription.|resource_group_name|resource_group_name|
### storageimportexport job update

update a storageimportexport job.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--job_name**|string|The name of the import/export job.|job_name|job_name|
|**--resource_group_name**|string|The resource group name uniquely identifies the resource group within the user subscription.|resource_group_name|resource_group_name|
|**--tags**|any|Specifies the tags that will be assigned to the job|tags|tags|
|**--cancel_requested**|boolean|If specified, the value must be true. The service will attempt to cancel the job.|cancel_requested|properties_cancel_requested|
|**--state**|string|If specified, the value must be Shipping, which tells the Import/Export service that the package for the job has been shipped. The ReturnAddress and DeliveryPackage properties must have been set either in this request or in a previous request, otherwise the request will fail.|state|properties_state|
|**--return_address**|object|Specifies the return address information for the job.|return_address|properties_return_address|
|**--return_shipping**|object|Specifies the return carrier and customer's account with the carrier.|return_shipping|properties_return_shipping|
|**--delivery_package**|object|Contains information about the package being shipped by the customer to the Microsoft data center.|delivery_package|properties_delivery_package|
|**--log_level**|string|Indicates whether error logging or verbose logging is enabled.|log_level|properties_log_level|
|**--backup_drive_manifest**|boolean|Indicates whether the manifest files on the drives should be copied to block blobs.|backup_drive_manifest|properties_backup_drive_manifest|
|**--drive_list**|array|List of drives that comprise the job.|drive_list|properties_drive_list|
### storageimportexport location list

list a storageimportexport location.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
### storageimportexport location show

show a storageimportexport location.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--location_name**|string|The name of the location. For example, West US or westus.|location_name|location_name|