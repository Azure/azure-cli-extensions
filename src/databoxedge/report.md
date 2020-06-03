# Azure CLI Module Creation Report

### databoxedge alert list

list a databoxedge alert.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
### databoxedge alert show

show a databoxedge alert.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--name**|string|The alert name.|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
### databoxedge bandwidth-schedule create

create a databoxedge bandwidth-schedule.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--name**|string|The bandwidth schedule name which needs to be added/updated.|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--start**|string|The start time of the schedule in UTC.|start|
|**--stop**|string|The stop time of the schedule in UTC.|stop|
|**--rate-in-mbps**|integer|The bandwidth rate in Mbps.|rate_in_mbps|
|**--days**|array|The days of the week when this schedule is applicable.|days|
### databoxedge bandwidth-schedule delete

delete a databoxedge bandwidth-schedule.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--name**|string|The bandwidth schedule name.|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
### databoxedge bandwidth-schedule list

list a databoxedge bandwidth-schedule.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
### databoxedge bandwidth-schedule show

show a databoxedge bandwidth-schedule.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--name**|string|The bandwidth schedule name.|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
### databoxedge bandwidth-schedule update

create a databoxedge bandwidth-schedule.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--name**|string|The bandwidth schedule name which needs to be added/updated.|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--start**|string|The start time of the schedule in UTC.|start|
|**--stop**|string|The stop time of the schedule in UTC.|stop|
|**--rate-in-mbps**|integer|The bandwidth rate in Mbps.|rate_in_mbps|
|**--days**|array|The days of the week when this schedule is applicable.|days|
### databoxedge container create

create a databoxedge container.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--storage-account-name**|string|The Storage Account Name|storage_account_name|
|**--container-name**|string|The container name.|container_name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--data-format**|choice|DataFormat for Container|data_format|
### databoxedge container delete

delete a databoxedge container.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--storage-account-name**|string|The Storage Account Name|storage_account_name|
|**--container-name**|string|The container name.|container_name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
### databoxedge container list

list a databoxedge container.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--storage-account-name**|string|The storage Account name.|storage_account_name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
### databoxedge container refresh

refresh a databoxedge container.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--storage-account-name**|string|The Storage Account Name|storage_account_name|
|**--container-name**|string|The container name.|container_name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
### databoxedge container show

show a databoxedge container.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--storage-account-name**|string|The Storage Account Name|storage_account_name|
|**--container-name**|string|The container Name|container_name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
### databoxedge container update

create a databoxedge container.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--storage-account-name**|string|The Storage Account Name|storage_account_name|
|**--container-name**|string|The container name.|container_name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--data-format**|choice|DataFormat for Container|data_format|
### databoxedge device create

create a databoxedge device.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--location**|string|The location of the device. This is a supported and registered Azure geographical region (for example, West US, East US, or Southeast Asia). The geographical region of a device cannot be changed once it is created, but if an identical geographical region is specified on update, the request will succeed.|location|
|**--tags**|dictionary|The list of tags that describe the device. These tags can be used to view and group this device (across resource groups).|tags|
|**--sku**|object|The SKU type.|sku|
|**--etag**|string|The etag for the devices.|etag|
|**--data-box-edge-device-status**|choice|The status of the Data Box Edge/Gateway device.|data_box_edge_device_status|
|**--description**|string|The Description of the Data Box Edge/Gateway device.|description|
|**--model-description**|string|The description of the Data Box Edge/Gateway device model.|model_description|
|**--friendly-name**|string|The Data Box Edge/Gateway device name.|friendly_name|
### databoxedge device create-or-update-security-setting

create-or-update-security-setting a databoxedge device.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--device-admin-password**|object|Device administrator password as an encrypted string (encrypted using RSA PKCS #1) is used to sign into the  local web UI of the device. The Actual password should have at least 8 characters that are a combination of  uppercase, lowercase, numeric, and special characters.|device_admin_password|
### databoxedge device delete

delete a databoxedge device.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
### databoxedge device download-update

download-update a databoxedge device.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
### databoxedge device get-extended-information

get-extended-information a databoxedge device.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
### databoxedge device install-update

install-update a databoxedge device.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
### databoxedge device list

list a databoxedge device.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--expand**|string|Specify $expand=details to populate additional fields related to the resource or Specify $skipToken=:code:`<token>` to populate the next page in the list.|expand|
### databoxedge device scan-for-update

scan-for-update a databoxedge device.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
### databoxedge device show

show a databoxedge device.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
### databoxedge device update

update a databoxedge device.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--tags**|dictionary|The tags attached to the Data Box Edge/Gateway resource.|tags|
### databoxedge device upload-certificate

upload-certificate a databoxedge device.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--certificate**|string|The base64 encoded certificate raw data.|certificate|
|**--authentication-type**|choice|The authentication type.|authentication_type|
### databoxedge job show

show a databoxedge job.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--name**|string|The job name.|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
### databoxedge node list

list a databoxedge node.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
### databoxedge operation-status show

show a databoxedge operation-status.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--name**|string|The job name.|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
### databoxedge order create

create a databoxedge order.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The order details of a device.|device_name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--contact-information**|object|The contact details.|contact_information|
|**--shipping-address**|object|The shipping address.|shipping_address|
|**--current-status-status**|choice|Status of the order as per the allowed status types.|status|
|**--current-status-comments**|string|Comments related to this status change.|comments|
### databoxedge order delete

delete a databoxedge order.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
### databoxedge order list

list a databoxedge order.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
### databoxedge order show

show a databoxedge order.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
### databoxedge order update

create a databoxedge order.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The order details of a device.|device_name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--contact-information**|object|The contact details.|contact_information|
|**--shipping-address**|object|The shipping address.|shipping_address|
|**--current-status-status**|choice|Status of the order as per the allowed status types.|status|
|**--current-status-comments**|string|Comments related to this status change.|comments|
### databoxedge role create

create a databoxedge role.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--name**|string|The role name.|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--role**|object|The role properties.|role|
### databoxedge role delete

delete a databoxedge role.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--name**|string|The role name.|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
### databoxedge role list

list a databoxedge role.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
### databoxedge role show

show a databoxedge role.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--name**|string|The role name.|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
### databoxedge role update

create a databoxedge role.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--name**|string|The role name.|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--role**|object|The role properties.|role|
### databoxedge share create

create a databoxedge share.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--name**|string|The share name.|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--share-status**|choice|Current status of the share.|share_status|
|**--monitoring-status**|choice|Current monitoring status of the share.|monitoring_status|
|**--access-protocol**|choice|Access protocol to be used by the share.|access_protocol|
|**--description**|string|Description for the share.|description|
|**--azure-container-info**|object|Azure container mapping for the share.|azure_container_info|
|**--user-access-rights**|array|Mapping of users and corresponding access rights on the share (required for SMB protocol).|user_access_rights|
|**--client-access-rights**|array|List of IP addresses and corresponding access rights on the share(required for NFS protocol).|client_access_rights|
|**--refresh-details**|object|Details of the refresh job on this share.|refresh_details|
|**--data-policy**|choice|Data policy of the share.|data_policy|
### databoxedge share delete

delete a databoxedge share.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--name**|string|The share name.|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
### databoxedge share list

list a databoxedge share.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
### databoxedge share refresh

refresh a databoxedge share.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--name**|string|The share name.|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
### databoxedge share show

show a databoxedge share.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--name**|string|The share name.|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
### databoxedge share update

create a databoxedge share.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--name**|string|The share name.|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--share-status**|choice|Current status of the share.|share_status|
|**--monitoring-status**|choice|Current monitoring status of the share.|monitoring_status|
|**--access-protocol**|choice|Access protocol to be used by the share.|access_protocol|
|**--description**|string|Description for the share.|description|
|**--azure-container-info**|object|Azure container mapping for the share.|azure_container_info|
|**--user-access-rights**|array|Mapping of users and corresponding access rights on the share (required for SMB protocol).|user_access_rights|
|**--client-access-rights**|array|List of IP addresses and corresponding access rights on the share(required for NFS protocol).|client_access_rights|
|**--refresh-details**|object|Details of the refresh job on this share.|refresh_details|
|**--data-policy**|choice|Data policy of the share.|data_policy|
### databoxedge sku list

list a databoxedge sku.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--filter**|string|Specify $filter='location eq :code:`<location>`' to filter on location.|filter|
### databoxedge storage-account create

create a databoxedge storage-account.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--storage-account-name**|string|The StorageAccount name.|storage_account_name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--description**|string|Description for the storage Account.|description|
|**--storage-account-status**|choice|Current status of the storage account|storage_account_status|
|**--data-policy**|choice|Data policy of the storage Account.|data_policy|
|**--storage-account-credential-id**|string|Storage Account Credential Id|storage_account_credential_id|
### databoxedge storage-account delete

delete a databoxedge storage-account.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--storage-account-name**|string|The StorageAccount name.|storage_account_name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
### databoxedge storage-account list

list a databoxedge storage-account.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
### databoxedge storage-account show

show a databoxedge storage-account.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--storage-account-name**|string|The storage account name.|storage_account_name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
### databoxedge storage-account update

create a databoxedge storage-account.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--storage-account-name**|string|The StorageAccount name.|storage_account_name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--description**|string|Description for the storage Account.|description|
|**--storage-account-status**|choice|Current status of the storage account|storage_account_status|
|**--data-policy**|choice|Data policy of the storage Account.|data_policy|
|**--storage-account-credential-id**|string|Storage Account Credential Id|storage_account_credential_id|
### databoxedge storage-account-credentials create

create a databoxedge storage-account-credentials.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--name**|string|The storage account credential name.|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--alias**|string|Alias for the storage account.|alias|
|**--ssl-status**|choice|Signifies whether SSL needs to be enabled or not.|ssl_status|
|**--account-type**|choice|Type of storage accessed on the storage account.|account_type|
|**--user-name**|string|Username for the storage account.|user_name|
|**--account-key**|object|Encrypted storage key.|account_key|
|**--connection-string**|string|Connection string for the storage account. Use this string if username and account key are not specified.|connection_string|
|**--blob-domain-name**|string|Blob end point for private clouds.|blob_domain_name|
|**--storage-account-id**|string|Id of the storage account.|storage_account_id|
### databoxedge storage-account-credentials delete

delete a databoxedge storage-account-credentials.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--name**|string|The storage account credential name.|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
### databoxedge storage-account-credentials list

list a databoxedge storage-account-credentials.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
### databoxedge storage-account-credentials show

show a databoxedge storage-account-credentials.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--name**|string|The storage account credential name.|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
### databoxedge storage-account-credentials update

create a databoxedge storage-account-credentials.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--name**|string|The storage account credential name.|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--alias**|string|Alias for the storage account.|alias|
|**--ssl-status**|choice|Signifies whether SSL needs to be enabled or not.|ssl_status|
|**--account-type**|choice|Type of storage accessed on the storage account.|account_type|
|**--user-name**|string|Username for the storage account.|user_name|
|**--account-key**|object|Encrypted storage key.|account_key|
|**--connection-string**|string|Connection string for the storage account. Use this string if username and account key are not specified.|connection_string|
|**--blob-domain-name**|string|Blob end point for private clouds.|blob_domain_name|
|**--storage-account-id**|string|Id of the storage account.|storage_account_id|
### databoxedge trigger create

create a databoxedge trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|Creates or updates a trigger|device_name|
|**--name**|string|The trigger name.|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--file-event-trigger**|object|Trigger details.|file_event_trigger|
|**--periodic-timer-event-trigger**|object|Trigger details.|periodic_timer_event_trigger|
### databoxedge trigger delete

delete a databoxedge trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--name**|string|The trigger name.|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
### databoxedge trigger list

list a databoxedge trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--filter**|string|Specify $filter='CustomContextTag eq :code:`<tag>`' to filter on custom context tag property|filter|
### databoxedge trigger show

show a databoxedge trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--name**|string|The trigger name.|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
### databoxedge trigger update

create a databoxedge trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|Creates or updates a trigger|device_name|
|**--name**|string|The trigger name.|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--file-event-trigger**|object|Trigger details.|file_event_trigger|
|**--periodic-timer-event-trigger**|object|Trigger details.|periodic_timer_event_trigger|
### databoxedge user create

create a databoxedge user.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--name**|string|The user name.|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--user-type**|choice|Type of the user.|user_type|
|**--encrypted-password**|object|The password details.|encrypted_password|
|**--share-access-rights**|array|List of shares that the user has rights on. This field should not be specified during user creation.|share_access_rights|
### databoxedge user delete

delete a databoxedge user.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--name**|string|The user name.|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
### databoxedge user list

list a databoxedge user.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--filter**|string|Specify $filter='UserType eq :code:`<type>`' to filter on user type property|filter|
### databoxedge user show

show a databoxedge user.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--name**|string|The user name.|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
### databoxedge user update

create a databoxedge user.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--device-name**|string|The device name.|device_name|
|**--name**|string|The user name.|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--user-type**|choice|Type of the user.|user_type|
|**--encrypted-password**|object|The password details.|encrypted_password|
|**--share-access-rights**|array|List of shares that the user has rights on. This field should not be specified during user creation.|share_access_rights|