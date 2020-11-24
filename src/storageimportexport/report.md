# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az storageimportexport|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az storageimportexport` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az storageimportexport location|Locations|[commands](#CommandsInLocations)|
|az storageimportexport job|Jobs|[commands](#CommandsInJobs)|
|az storageimportexport bit-locker-key|BitLockerKeys|[commands](#CommandsInBitLockerKeys)|

## COMMANDS
### <a name="CommandsInBitLockerKeys">Commands in `az storageimportexport bit-locker-key` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az storageimportexport bit-locker-key list](#BitLockerKeysList)|List|[Parameters](#ParametersBitLockerKeysList)|[Example](#ExamplesBitLockerKeysList)|

### <a name="CommandsInJobs">Commands in `az storageimportexport job` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az storageimportexport job list](#JobsListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersJobsListByResourceGroup)|[Example](#ExamplesJobsListByResourceGroup)|
|[az storageimportexport job list](#JobsListBySubscription)|ListBySubscription|[Parameters](#ParametersJobsListBySubscription)|[Example](#ExamplesJobsListBySubscription)|
|[az storageimportexport job show](#JobsGet)|Get|[Parameters](#ParametersJobsGet)|[Example](#ExamplesJobsGet)|
|[az storageimportexport job create](#JobsCreate)|Create|[Parameters](#ParametersJobsCreate)|[Example](#ExamplesJobsCreate)|
|[az storageimportexport job update](#JobsUpdate)|Update|[Parameters](#ParametersJobsUpdate)|[Example](#ExamplesJobsUpdate)|
|[az storageimportexport job delete](#JobsDelete)|Delete|[Parameters](#ParametersJobsDelete)|[Example](#ExamplesJobsDelete)|

### <a name="CommandsInLocations">Commands in `az storageimportexport location` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az storageimportexport location list](#LocationsList)|List|[Parameters](#ParametersLocationsList)|[Example](#ExamplesLocationsList)|
|[az storageimportexport location show](#LocationsGet)|Get|[Parameters](#ParametersLocationsGet)|[Example](#ExamplesLocationsGet)|


## COMMAND DETAILS

### group `az storageimportexport bit-locker-key`
#### <a name="BitLockerKeysList">Command `az storageimportexport bit-locker-key list`</a>

##### <a name="ExamplesBitLockerKeysList">Example</a>
```
az storageimportexport bit-locker-key list --job-name "myJob" --resource-group "myResourceGroup"
```
##### <a name="ParametersBitLockerKeysList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--job-name**|string|The name of the import/export job.|job_name|jobName|
|**--resource-group-name**|string|The resource group name uniquely identifies the resource group within the user subscription.|resource_group_name|resourceGroupName|

### group `az storageimportexport job`
#### <a name="JobsListByResourceGroup">Command `az storageimportexport job list`</a>

##### <a name="ExamplesJobsListByResourceGroup">Example</a>
```
az storageimportexport job list --resource-group "myResourceGroup"
```
##### <a name="ParametersJobsListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name uniquely identifies the resource group within the user subscription.|resource_group_name|resourceGroupName|
|**--top**|integer|An integer value that specifies how many jobs at most should be returned. The value cannot exceed 100.|top|$top|
|**--filter**|string|Can be used to restrict the results to certain conditions.|filter|$filter|

#### <a name="JobsListBySubscription">Command `az storageimportexport job list`</a>

##### <a name="ExamplesJobsListBySubscription">Example</a>
```
az storageimportexport job list
```
##### <a name="ParametersJobsListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="JobsGet">Command `az storageimportexport job show`</a>

##### <a name="ExamplesJobsGet">Example</a>
```
az storageimportexport job show --name "myJob" --resource-group "myResourceGroup"
```
##### <a name="ParametersJobsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--job-name**|string|The name of the import/export job.|job_name|jobName|
|**--resource-group-name**|string|The resource group name uniquely identifies the resource group within the user subscription.|resource_group_name|resourceGroupName|

#### <a name="JobsCreate">Command `az storageimportexport job create`</a>

##### <a name="ExamplesJobsCreate">Example</a>
```
az storageimportexport job create --location "West US" --backup-drive-manifest true --diagnostics-path \
"waimportexport" --drive-list bit-locker-key="238810-662376-448998-450120-652806-203390-606320-483076" \
drive-header-hash="" drive-id="9CA995BB" manifest-file="\\\\DriveManifest.xml" manifest-hash="109B21108597EF36D5785F083\
03F3638" --job-type "Import" --log-level "Verbose" --return-address city="Redmond" country-or-region="USA" \
email="Test@contoso.com" phone="4250000000" postal-code="98007" recipient-name="Tets" state-or-province="wa" \
street-address1="Street1" street-address2="street2" --storage-account-id "/subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxx\
xxxxxx/resourceGroups/myResourceGroup/providers/Microsoft.ClassicStorage/storageAccounts/test" --name "myJob" \
--resource-group "myResourceGroup"
```
##### <a name="ParametersJobsCreate">Parameters</a> 
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
|**--export**|object|A property containing information about the blobs to be exported for an export job. This property is included for export jobs only.|export|export|
|**--provisioning-state**|string|Specifies the provisioning state of the job.|provisioning_state|provisioningState|

#### <a name="JobsUpdate">Command `az storageimportexport job update`</a>

##### <a name="ExamplesJobsUpdate">Example</a>
```
az storageimportexport job update --backup-drive-manifest true --log-level "Verbose" --state "" --name "myJob" \
--resource-group "myResourceGroup"
```
##### <a name="ParametersJobsUpdate">Parameters</a> 
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

#### <a name="JobsDelete">Command `az storageimportexport job delete`</a>

##### <a name="ExamplesJobsDelete">Example</a>
```
az storageimportexport job delete --name "myJob" --resource-group "myResourceGroup"
```
##### <a name="ParametersJobsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--job-name**|string|The name of the import/export job.|job_name|jobName|
|**--resource-group-name**|string|The resource group name uniquely identifies the resource group within the user subscription.|resource_group_name|resourceGroupName|

### group `az storageimportexport location`
#### <a name="LocationsList">Command `az storageimportexport location list`</a>

##### <a name="ExamplesLocationsList">Example</a>
```
az storageimportexport location list
```
##### <a name="ParametersLocationsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="LocationsGet">Command `az storageimportexport location show`</a>

##### <a name="ExamplesLocationsGet">Example</a>
```
az storageimportexport location show --name "West US"
```
##### <a name="ParametersLocationsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location-name**|string|The name of the location. For example, West US or westus.|location_name|locationName|
