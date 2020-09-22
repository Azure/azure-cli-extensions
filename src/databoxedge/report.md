# Azure CLI Module Creation Report

### databoxedge alert list

list a databoxedge alert.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge alert|Alerts|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByDataBoxEdgeDevice|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### databoxedge alert show

show a databoxedge alert.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge alert|Alerts|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The alert name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### databoxedge bandwidth-schedule create

create a databoxedge bandwidth-schedule.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge bandwidth-schedule|BandwidthSchedules|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The bandwidth schedule name which needs to be added/updated.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--start**|string|The start time of the schedule in UTC.|start|start|
|**--stop**|string|The stop time of the schedule in UTC.|stop|stop|
|**--rate-in-mbps**|integer|The bandwidth rate in Mbps.|rate_in_mbps|rateInMbps|
|**--days**|array|The days of the week when this schedule is applicable.|days|days|

### databoxedge bandwidth-schedule delete

delete a databoxedge bandwidth-schedule.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge bandwidth-schedule|BandwidthSchedules|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The bandwidth schedule name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### databoxedge bandwidth-schedule list

list a databoxedge bandwidth-schedule.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge bandwidth-schedule|BandwidthSchedules|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByDataBoxEdgeDevice|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### databoxedge bandwidth-schedule show

show a databoxedge bandwidth-schedule.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge bandwidth-schedule|BandwidthSchedules|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The bandwidth schedule name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### databoxedge bandwidth-schedule update

update a databoxedge bandwidth-schedule.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge bandwidth-schedule|BandwidthSchedules|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|CreateOrUpdate#Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The bandwidth schedule name which needs to be added/updated.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--start**|string|The start time of the schedule in UTC.|start|start|
|**--stop**|string|The stop time of the schedule in UTC.|stop|stop|
|**--rate-in-mbps**|integer|The bandwidth rate in Mbps.|rate_in_mbps|rateInMbps|
|**--days**|array|The days of the week when this schedule is applicable.|days|days|

### databoxedge container create

create a databoxedge container.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge container|Containers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--storage-account-name**|string|The Storage Account Name|storage_account_name|storageAccountName|
|**--container-name**|string|The container name.|container_name|containerName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--data-format**|choice|DataFormat for Container|data_format|dataFormat|

### databoxedge container delete

delete a databoxedge container.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge container|Containers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--storage-account-name**|string|The Storage Account Name|storage_account_name|storageAccountName|
|**--container-name**|string|The container name.|container_name|containerName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### databoxedge container list

list a databoxedge container.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge container|Containers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByStorageAccount|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--storage-account-name**|string|The storage Account name.|storage_account_name|storageAccountName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### databoxedge container refresh

refresh a databoxedge container.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge container|Containers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|refresh|Refresh|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--storage-account-name**|string|The Storage Account Name|storage_account_name|storageAccountName|
|**--container-name**|string|The container name.|container_name|containerName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### databoxedge container show

show a databoxedge container.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge container|Containers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--storage-account-name**|string|The Storage Account Name|storage_account_name|storageAccountName|
|**--container-name**|string|The container Name|container_name|containerName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### databoxedge container update

update a databoxedge container.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge container|Containers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|CreateOrUpdate#Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--storage-account-name**|string|The Storage Account Name|storage_account_name|storageAccountName|
|**--container-name**|string|The container name.|container_name|containerName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--data-format**|choice|DataFormat for Container|data_format|dataFormat|

### databoxedge device create

create a databoxedge device.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge device|Devices|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--location**|string|The location of the device. This is a supported and registered Azure geographical region (for example, West US, East US, or Southeast Asia). The geographical region of a device cannot be changed once it is created, but if an identical geographical region is specified on update, the request will succeed.|location|location|
|**--tags**|dictionary|The list of tags that describe the device. These tags can be used to view and group this device (across resource groups).|tags|tags|
|**--sku**|object|The SKU type.|sku|sku|
|**--etag**|string|The etag for the devices.|etag|etag|
|**--data-box-edge-device-status**|choice|The status of the Data Box Edge/Gateway device.|data_box_edge_device_status|dataBoxEdgeDeviceStatus|
|**--description**|string|The Description of the Data Box Edge/Gateway device.|description|description|
|**--model-description**|string|The description of the Data Box Edge/Gateway device model.|model_description|modelDescription|
|**--friendly-name**|string|The Data Box Edge/Gateway device name.|friendly_name|friendlyName|

### databoxedge device create-or-update-security-setting

create-or-update-security-setting a databoxedge device.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge device|Devices|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create-or-update-security-setting|CreateOrUpdateSecuritySettings|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--device-admin-password**|object|Device administrator password as an encrypted string (encrypted using RSA PKCS #1) is used to sign into the  local web UI of the device. The Actual password should have at least 8 characters that are a combination of  uppercase, lowercase, numeric, and special characters.|device_admin_password|deviceAdminPassword|

### databoxedge device delete

delete a databoxedge device.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge device|Devices|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### databoxedge device download-update

download-update a databoxedge device.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge device|Devices|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|download-update|DownloadUpdates|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### databoxedge device get-extended-information

get-extended-information a databoxedge device.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge device|Devices|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|get-extended-information|GetExtendedInformation|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### databoxedge device get-network-setting

get-network-setting a databoxedge device.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge device|Devices|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|get-network-setting|GetNetworkSettings|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### databoxedge device get-update-summary

get-update-summary a databoxedge device.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge device|Devices|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|get-update-summary|GetUpdateSummary|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### databoxedge device install-update

install-update a databoxedge device.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge device|Devices|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|install-update|InstallUpdates|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### databoxedge device list

list a databoxedge device.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge device|Devices|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByResourceGroup|
|list|ListBySubscription|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--expand**|string|Specify $expand=details to populate additional fields related to the resource or Specify $skipToken=:code:`<token>` to populate the next page in the list.|expand|$expand|

### databoxedge device scan-for-update

scan-for-update a databoxedge device.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge device|Devices|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|scan-for-update|ScanForUpdates|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### databoxedge device show

show a databoxedge device.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge device|Devices|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### databoxedge device update

update a databoxedge device.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge device|Devices|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--tags**|dictionary|The tags attached to the Data Box Edge/Gateway resource.|tags|tags|

### databoxedge device upload-certificate

upload-certificate a databoxedge device.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge device|Devices|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|upload-certificate|UploadCertificate|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--certificate**|string|The base64 encoded certificate raw data.|certificate|certificate|
|**--authentication-type**|choice|The authentication type.|authentication_type|authenticationType|

### databoxedge job show

show a databoxedge job.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge job|Jobs|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The job name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### databoxedge node list

list a databoxedge node.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge node|Nodes|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByDataBoxEdgeDevice|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### databoxedge operation-status show

show a databoxedge operation-status.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge operation-status|OperationsStatus|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The job name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### databoxedge order create

create a databoxedge order.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge order|Orders|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The order details of a device.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--contact-information**|object|The contact details.|contact_information|contactInformation|
|**--shipping-address**|object|The shipping address.|shipping_address|shippingAddress|
|**--current-status-status**|choice|Status of the order as per the allowed status types.|status|status|
|**--current-status-comments**|string|Comments related to this status change.|comments|comments|

### databoxedge order delete

delete a databoxedge order.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge order|Orders|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### databoxedge order list

list a databoxedge order.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge order|Orders|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByDataBoxEdgeDevice|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### databoxedge order show

show a databoxedge order.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge order|Orders|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### databoxedge order update

update a databoxedge order.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge order|Orders|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|CreateOrUpdate#Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The order details of a device.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--contact-information**|object|The contact details.|contact_information|contactInformation|
|**--shipping-address**|object|The shipping address.|shipping_address|shippingAddress|
|**--current-status-status**|choice|Status of the order as per the allowed status types.|status|status|
|**--current-status-comments**|string|Comments related to this status change.|comments|comments|

### databoxedge role create

create a databoxedge role.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge role|Roles|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The role name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--role**|object|The role properties.|role|role|

### databoxedge role delete

delete a databoxedge role.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge role|Roles|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The role name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### databoxedge role list

list a databoxedge role.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge role|Roles|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByDataBoxEdgeDevice|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### databoxedge role show

show a databoxedge role.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge role|Roles|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The role name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### databoxedge role update

update a databoxedge role.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge role|Roles|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|CreateOrUpdate#Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The role name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--role**|object|The role properties.|role|role|

### databoxedge share create

create a databoxedge share.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge share|Shares|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The share name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--share-status**|choice|Current status of the share.|share_status|shareStatus|
|**--monitoring-status**|choice|Current monitoring status of the share.|monitoring_status|monitoringStatus|
|**--access-protocol**|choice|Access protocol to be used by the share.|access_protocol|accessProtocol|
|**--description**|string|Description for the share.|description|description|
|**--azure-container-info**|object|Azure container mapping for the share.|azure_container_info|azureContainerInfo|
|**--user-access-rights**|array|Mapping of users and corresponding access rights on the share (required for SMB protocol).|user_access_rights|userAccessRights|
|**--client-access-rights**|array|List of IP addresses and corresponding access rights on the share(required for NFS protocol).|client_access_rights|clientAccessRights|
|**--refresh-details**|object|Details of the refresh job on this share.|refresh_details|refreshDetails|
|**--data-policy**|choice|Data policy of the share.|data_policy|dataPolicy|

### databoxedge share delete

delete a databoxedge share.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge share|Shares|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The share name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### databoxedge share list

list a databoxedge share.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge share|Shares|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByDataBoxEdgeDevice|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### databoxedge share refresh

refresh a databoxedge share.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge share|Shares|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|refresh|Refresh|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The share name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### databoxedge share show

show a databoxedge share.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge share|Shares|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The share name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### databoxedge share update

update a databoxedge share.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge share|Shares|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|CreateOrUpdate#Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The share name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--share-status**|choice|Current status of the share.|share_status|shareStatus|
|**--monitoring-status**|choice|Current monitoring status of the share.|monitoring_status|monitoringStatus|
|**--access-protocol**|choice|Access protocol to be used by the share.|access_protocol|accessProtocol|
|**--description**|string|Description for the share.|description|description|
|**--azure-container-info**|object|Azure container mapping for the share.|azure_container_info|azureContainerInfo|
|**--user-access-rights**|array|Mapping of users and corresponding access rights on the share (required for SMB protocol).|user_access_rights|userAccessRights|
|**--client-access-rights**|array|List of IP addresses and corresponding access rights on the share(required for NFS protocol).|client_access_rights|clientAccessRights|
|**--refresh-details**|object|Details of the refresh job on this share.|refresh_details|refreshDetails|
|**--data-policy**|choice|Data policy of the share.|data_policy|dataPolicy|

### databoxedge sku list

list a databoxedge sku.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge sku|Skus|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--filter**|string|Specify $filter='location eq :code:`<location>`' to filter on location.|filter|$filter|

### databoxedge storage-account create

create a databoxedge storage-account.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge storage-account|StorageAccounts|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--storage-account-name**|string|The StorageAccount name.|storage_account_name|storageAccountName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--description**|string|Description for the storage Account.|description|description|
|**--storage-account-status**|choice|Current status of the storage account|storage_account_status|storageAccountStatus|
|**--data-policy**|choice|Data policy of the storage Account.|data_policy|dataPolicy|
|**--storage-account-credential-id**|string|Storage Account Credential Id|storage_account_credential_id|storageAccountCredentialId|

### databoxedge storage-account delete

delete a databoxedge storage-account.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge storage-account|StorageAccounts|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--storage-account-name**|string|The StorageAccount name.|storage_account_name|storageAccountName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### databoxedge storage-account list

list a databoxedge storage-account.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge storage-account|StorageAccounts|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByDataBoxEdgeDevice|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### databoxedge storage-account show

show a databoxedge storage-account.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge storage-account|StorageAccounts|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--storage-account-name**|string|The storage account name.|storage_account_name|storageAccountName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### databoxedge storage-account update

update a databoxedge storage-account.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge storage-account|StorageAccounts|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|CreateOrUpdate#Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--storage-account-name**|string|The StorageAccount name.|storage_account_name|storageAccountName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--description**|string|Description for the storage Account.|description|description|
|**--storage-account-status**|choice|Current status of the storage account|storage_account_status|storageAccountStatus|
|**--data-policy**|choice|Data policy of the storage Account.|data_policy|dataPolicy|
|**--storage-account-credential-id**|string|Storage Account Credential Id|storage_account_credential_id|storageAccountCredentialId|

### databoxedge storage-account-credentials create

create a databoxedge storage-account-credentials.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge storage-account-credentials|StorageAccountCredentials|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The storage account credential name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--alias**|string|Alias for the storage account.|alias|alias|
|**--ssl-status**|choice|Signifies whether SSL needs to be enabled or not.|ssl_status|sslStatus|
|**--account-type**|choice|Type of storage accessed on the storage account.|account_type|accountType|
|**--user-name**|string|Username for the storage account.|user_name|userName|
|**--account-key**|object|Encrypted storage key.|account_key|accountKey|
|**--connection-string**|string|Connection string for the storage account. Use this string if username and account key are not specified.|connection_string|connectionString|
|**--blob-domain-name**|string|Blob end point for private clouds.|blob_domain_name|blobDomainName|
|**--storage-account-id**|string|Id of the storage account.|storage_account_id|storageAccountId|

### databoxedge storage-account-credentials delete

delete a databoxedge storage-account-credentials.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge storage-account-credentials|StorageAccountCredentials|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The storage account credential name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### databoxedge storage-account-credentials list

list a databoxedge storage-account-credentials.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge storage-account-credentials|StorageAccountCredentials|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByDataBoxEdgeDevice|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### databoxedge storage-account-credentials show

show a databoxedge storage-account-credentials.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge storage-account-credentials|StorageAccountCredentials|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The storage account credential name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### databoxedge storage-account-credentials update

update a databoxedge storage-account-credentials.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge storage-account-credentials|StorageAccountCredentials|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|CreateOrUpdate#Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The storage account credential name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--alias**|string|Alias for the storage account.|alias|alias|
|**--ssl-status**|choice|Signifies whether SSL needs to be enabled or not.|ssl_status|sslStatus|
|**--account-type**|choice|Type of storage accessed on the storage account.|account_type|accountType|
|**--user-name**|string|Username for the storage account.|user_name|userName|
|**--account-key**|object|Encrypted storage key.|account_key|accountKey|
|**--connection-string**|string|Connection string for the storage account. Use this string if username and account key are not specified.|connection_string|connectionString|
|**--blob-domain-name**|string|Blob end point for private clouds.|blob_domain_name|blobDomainName|
|**--storage-account-id**|string|Id of the storage account.|storage_account_id|storageAccountId|

### databoxedge trigger create

create a databoxedge trigger.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge trigger|Triggers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|Creates or updates a trigger|device_name|deviceName|
|**--name**|string|The trigger name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--file-event-trigger**|object|Trigger details.|file_event_trigger|FileEventTrigger|
|**--periodic-timer-event-trigger**|object|Trigger details.|periodic_timer_event_trigger|PeriodicTimerEventTrigger|

### databoxedge trigger delete

delete a databoxedge trigger.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge trigger|Triggers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The trigger name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### databoxedge trigger list

list a databoxedge trigger.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge trigger|Triggers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByDataBoxEdgeDevice|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--filter**|string|Specify $filter='CustomContextTag eq :code:`<tag>`' to filter on custom context tag property|filter|$filter|

### databoxedge trigger show

show a databoxedge trigger.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge trigger|Triggers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The trigger name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### databoxedge trigger update

update a databoxedge trigger.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge trigger|Triggers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|CreateOrUpdate#Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|Creates or updates a trigger|device_name|deviceName|
|**--name**|string|The trigger name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--file-event-trigger**|object|Trigger details.|file_event_trigger|FileEventTrigger|
|**--periodic-timer-event-trigger**|object|Trigger details.|periodic_timer_event_trigger|PeriodicTimerEventTrigger|

### databoxedge user create

create a databoxedge user.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge user|Users|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The user name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--user-type**|choice|Type of the user.|user_type|userType|
|**--encrypted-password**|object|The password details.|encrypted_password|encryptedPassword|
|**--share-access-rights**|array|List of shares that the user has rights on. This field should not be specified during user creation.|share_access_rights|shareAccessRights|

### databoxedge user delete

delete a databoxedge user.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge user|Users|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The user name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### databoxedge user list

list a databoxedge user.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge user|Users|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByDataBoxEdgeDevice|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--filter**|string|Specify $filter='UserType eq :code:`<type>`' to filter on user type property|filter|$filter|

### databoxedge user show

show a databoxedge user.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge user|Users|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The user name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### databoxedge user update

update a databoxedge user.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|databoxedge user|Users|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|CreateOrUpdate#Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The user name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--user-type**|choice|Type of the user.|user_type|userType|
|**--encrypted-password**|object|The password details.|encrypted_password|encryptedPassword|
|**--share-access-rights**|array|List of shares that the user has rights on. This field should not be specified during user creation.|share_access_rights|shareAccessRights|
