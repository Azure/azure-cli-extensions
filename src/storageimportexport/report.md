# Azure CLI Module Creation Report

### storageimportexport bit-locker-key list

list a storageimportexport bit-locker-key.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storageimportexport bit-locker-key|BitLockerKeys|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--job-name**|string|The name of the import/export job.|job_name|jobName|
|**--resource-group-name**|string|The resource group name uniquely identifies the resource group within the user subscription.|resource_group_name|resourceGroupName|

### storageimportexport job create

create a storageimportexport job.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storageimportexport job|Jobs|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--job-name**|string|The name of the import/export job.|job_name|jobName|
|**--resource-group-name**|string|The resource group name uniquely identifies the resource group within the user subscription.|resource_group_name|resourceGroupName|
|**--client-tenant-id**|string|The tenant ID of the client making the request.|client_tenant_id|ClientTenantId|
|**--location**|string|Specifies the supported Azure location where the job should be created|location|location|
|**--tags**|any|Specifies the tags that will be assigned to the job.|tags|tags|
|**--storage-account-id**|string|The resource identifier of the storage account where data will be imported to or exported from.|storage_account_id|storageAccountId|
|**--job-type**|string|The type of job|job_type|jobType|
|**--return-address**|object|Specifies the return address information for the job.|return_address|returnAddress|
|**--return-shipping**|object|Specifies the return carrier and customer's account with the carrier.|return_shipping|returnShipping|
|**--shipping-information**|object|Contains information about the Microsoft datacenter to which the drives should be shipped.|shipping_information|shippingInformation|
|**--delivery-package**|object|Contains information about the package being shipped by the customer to the Microsoft data center.|delivery_package|deliveryPackage|
|**--return-package**|object|Contains information about the package being shipped from the Microsoft data center to the customer to return the drives. The format is the same as the deliveryPackage property above. This property is not included if the drives have not yet been returned.|return_package|returnPackage|
|**--diagnostics-path**|string|The virtual blob directory to which the copy logs and backups of drive manifest files (if enabled) will be stored.|diagnostics_path|diagnosticsPath|
|**--log-level**|string|Default value is Error. Indicates whether error logging or verbose logging will be enabled.|log_level|logLevel|
|**--backup-drive-manifest**|boolean|Default value is false. Indicates whether the manifest files on the drives should be copied to block blobs.|backup_drive_manifest|backupDriveManifest|
|**--state**|string|Current state of the job.|state|state|
|**--cancel-requested**|boolean|Indicates whether a request has been submitted to cancel the job.|cancel_requested|cancelRequested|
|**--percent-complete**|integer|Overall percentage completed for the job.|percent_complete|percentComplete|
|**--incomplete-blob-list-uri**|string|A blob path that points to a block blob containing a list of blob names that were not exported due to insufficient drive space. If all blobs were exported successfully, then this element is not included in the response.|incomplete_blob_list_uri|incompleteBlobListUri|
|**--drive-list**|array|List of up to ten drives that comprise the job. The drive list is a required element for an import job; it is not specified for export jobs.|drive_list|driveList|
|**--provisioning-state**|string|Specifies the provisioning state of the job.|provisioning_state|provisioningState|
|**--export-blob-listblob-path**|string|The relative URI to the block blob that contains the list of blob paths or blob path prefixes as defined above, beginning with the container name. If the blob is in root container, the URI must begin with $root.|blob_listblob_path|blobListblobPath|
|**--export-blob-list-blob-path**|array|A collection of blob-path strings.|blob_path|blobPath|
|**--export-blob-list-blob-path-prefix**|array|A collection of blob-prefix strings.|blob_path_prefix|blobPathPrefix|

### storageimportexport job delete

delete a storageimportexport job.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storageimportexport job|Jobs|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--job-name**|string|The name of the import/export job.|job_name|jobName|
|**--resource-group-name**|string|The resource group name uniquely identifies the resource group within the user subscription.|resource_group_name|resourceGroupName|

### storageimportexport job list

list a storageimportexport job.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storageimportexport job|Jobs|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByResourceGroup|
|list|ListBySubscription|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name uniquely identifies the resource group within the user subscription.|resource_group_name|resourceGroupName|
|**--top**|integer|An integer value that specifies how many jobs at most should be returned. The value cannot exceed 100.|top|$top|
|**--filter**|string|Can be used to restrict the results to certain conditions.|filter|$filter|

### storageimportexport job show

show a storageimportexport job.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storageimportexport job|Jobs|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--job-name**|string|The name of the import/export job.|job_name|jobName|
|**--resource-group-name**|string|The resource group name uniquely identifies the resource group within the user subscription.|resource_group_name|resourceGroupName|

### storageimportexport job update

update a storageimportexport job.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storageimportexport job|Jobs|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--job-name**|string|The name of the import/export job.|job_name|jobName|
|**--resource-group-name**|string|The resource group name uniquely identifies the resource group within the user subscription.|resource_group_name|resourceGroupName|
|**--tags**|any|Specifies the tags that will be assigned to the job|tags|tags|
|**--cancel-requested**|boolean|If specified, the value must be true. The service will attempt to cancel the job.|cancel_requested|cancelRequested|
|**--state**|string|If specified, the value must be Shipping, which tells the Import/Export service that the package for the job has been shipped. The ReturnAddress and DeliveryPackage properties must have been set either in this request or in a previous request, otherwise the request will fail.|state|state|
|**--return-address**|object|Specifies the return address information for the job.|return_address|returnAddress|
|**--return-shipping**|object|Specifies the return carrier and customer's account with the carrier.|return_shipping|returnShipping|
|**--delivery-package**|object|Contains information about the package being shipped by the customer to the Microsoft data center.|delivery_package|deliveryPackage|
|**--log-level**|string|Indicates whether error logging or verbose logging is enabled.|log_level|logLevel|
|**--backup-drive-manifest**|boolean|Indicates whether the manifest files on the drives should be copied to block blobs.|backup_drive_manifest|backupDriveManifest|
|**--drive-list**|array|List of drives that comprise the job.|drive_list|driveList|

### storageimportexport location list

list a storageimportexport location.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storageimportexport location|Locations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

### storageimportexport location show

show a storageimportexport location.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storageimportexport location|Locations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location-name**|string|The name of the location. For example, West US or westus.|location_name|locationName|
