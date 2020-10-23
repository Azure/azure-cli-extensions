# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az databoxedge|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az databoxedge` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az databoxedge device|Devices|[commands](#CommandsInDevices)|
|az databoxedge alert|Alerts|[commands](#CommandsInAlerts)|
|az databoxedge bandwidth-schedule|BandwidthSchedules|[commands](#CommandsInBandwidthSchedules)|
|az databoxedge job|Jobs|[commands](#CommandsInJobs)|
|az databoxedge node|Nodes|[commands](#CommandsInNodes)|
|az databoxedge operation-status|OperationsStatus|[commands](#CommandsInOperationsStatus)|
|az databoxedge order|Orders|[commands](#CommandsInOrders)|
|az databoxedge role|Roles|[commands](#CommandsInRoles)|
|az databoxedge share|Shares|[commands](#CommandsInShares)|
|az databoxedge storage-account-credentials|StorageAccountCredentials|[commands](#CommandsInStorageAccountCredentials)|
|az databoxedge storage-account|StorageAccounts|[commands](#CommandsInStorageAccounts)|
|az databoxedge container|Containers|[commands](#CommandsInContainers)|
|az databoxedge trigger|Triggers|[commands](#CommandsInTriggers)|
|az databoxedge user|Users|[commands](#CommandsInUsers)|
|az databoxedge sku|Skus|[commands](#CommandsInSkus)|

## COMMANDS
### <a name="CommandsInAlerts">Commands in `az databoxedge alert` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az databoxedge alert list](#AlertsListByDataBoxEdgeDevice)|ListByDataBoxEdgeDevice|[Parameters](#ParametersAlertsListByDataBoxEdgeDevice)|[Example](#ExamplesAlertsListByDataBoxEdgeDevice)|
|[az databoxedge alert show](#AlertsGet)|Get|[Parameters](#ParametersAlertsGet)|[Example](#ExamplesAlertsGet)|

### <a name="CommandsInBandwidthSchedules">Commands in `az databoxedge bandwidth-schedule` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az databoxedge bandwidth-schedule list](#BandwidthSchedulesListByDataBoxEdgeDevice)|ListByDataBoxEdgeDevice|[Parameters](#ParametersBandwidthSchedulesListByDataBoxEdgeDevice)|[Example](#ExamplesBandwidthSchedulesListByDataBoxEdgeDevice)|
|[az databoxedge bandwidth-schedule show](#BandwidthSchedulesGet)|Get|[Parameters](#ParametersBandwidthSchedulesGet)|[Example](#ExamplesBandwidthSchedulesGet)|
|[az databoxedge bandwidth-schedule create](#BandwidthSchedulesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersBandwidthSchedulesCreateOrUpdate#Create)|[Example](#ExamplesBandwidthSchedulesCreateOrUpdate#Create)|
|[az databoxedge bandwidth-schedule update](#BandwidthSchedulesCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersBandwidthSchedulesCreateOrUpdate#Update)|Not Found|
|[az databoxedge bandwidth-schedule delete](#BandwidthSchedulesDelete)|Delete|[Parameters](#ParametersBandwidthSchedulesDelete)|[Example](#ExamplesBandwidthSchedulesDelete)|

### <a name="CommandsInContainers">Commands in `az databoxedge container` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az databoxedge container list](#ContainersListByStorageAccount)|ListByStorageAccount|[Parameters](#ParametersContainersListByStorageAccount)|[Example](#ExamplesContainersListByStorageAccount)|
|[az databoxedge container show](#ContainersGet)|Get|[Parameters](#ParametersContainersGet)|[Example](#ExamplesContainersGet)|
|[az databoxedge container create](#ContainersCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersContainersCreateOrUpdate#Create)|[Example](#ExamplesContainersCreateOrUpdate#Create)|
|[az databoxedge container update](#ContainersCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersContainersCreateOrUpdate#Update)|Not Found|
|[az databoxedge container delete](#ContainersDelete)|Delete|[Parameters](#ParametersContainersDelete)|[Example](#ExamplesContainersDelete)|
|[az databoxedge container refresh](#ContainersRefresh)|Refresh|[Parameters](#ParametersContainersRefresh)|[Example](#ExamplesContainersRefresh)|

### <a name="CommandsInDevices">Commands in `az databoxedge device` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az databoxedge device list](#DevicesListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersDevicesListByResourceGroup)|[Example](#ExamplesDevicesListByResourceGroup)|
|[az databoxedge device list](#DevicesListBySubscription)|ListBySubscription|[Parameters](#ParametersDevicesListBySubscription)|[Example](#ExamplesDevicesListBySubscription)|
|[az databoxedge device show](#DevicesGet)|Get|[Parameters](#ParametersDevicesGet)|[Example](#ExamplesDevicesGet)|
|[az databoxedge device create](#DevicesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersDevicesCreateOrUpdate#Create)|[Example](#ExamplesDevicesCreateOrUpdate#Create)|
|[az databoxedge device update](#DevicesUpdate)|Update|[Parameters](#ParametersDevicesUpdate)|[Example](#ExamplesDevicesUpdate)|
|[az databoxedge device delete](#DevicesDelete)|Delete|[Parameters](#ParametersDevicesDelete)|[Example](#ExamplesDevicesDelete)|
|[az databoxedge device create-or-update-security-setting](#DevicesCreateOrUpdateSecuritySettings)|CreateOrUpdateSecuritySettings|[Parameters](#ParametersDevicesCreateOrUpdateSecuritySettings)|[Example](#ExamplesDevicesCreateOrUpdateSecuritySettings)|
|[az databoxedge device download-update](#DevicesDownloadUpdates)|DownloadUpdates|[Parameters](#ParametersDevicesDownloadUpdates)|[Example](#ExamplesDevicesDownloadUpdates)|
|[az databoxedge device get-extended-information](#DevicesGetExtendedInformation)|GetExtendedInformation|[Parameters](#ParametersDevicesGetExtendedInformation)|[Example](#ExamplesDevicesGetExtendedInformation)|
|[az databoxedge device get-network-setting](#DevicesGetNetworkSettings)|GetNetworkSettings|[Parameters](#ParametersDevicesGetNetworkSettings)|[Example](#ExamplesDevicesGetNetworkSettings)|
|[az databoxedge device get-update-summary](#DevicesGetUpdateSummary)|GetUpdateSummary|[Parameters](#ParametersDevicesGetUpdateSummary)|[Example](#ExamplesDevicesGetUpdateSummary)|
|[az databoxedge device install-update](#DevicesInstallUpdates)|InstallUpdates|[Parameters](#ParametersDevicesInstallUpdates)|[Example](#ExamplesDevicesInstallUpdates)|
|[az databoxedge device scan-for-update](#DevicesScanForUpdates)|ScanForUpdates|[Parameters](#ParametersDevicesScanForUpdates)|[Example](#ExamplesDevicesScanForUpdates)|
|[az databoxedge device upload-certificate](#DevicesUploadCertificate)|UploadCertificate|[Parameters](#ParametersDevicesUploadCertificate)|[Example](#ExamplesDevicesUploadCertificate)|

### <a name="CommandsInJobs">Commands in `az databoxedge job` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az databoxedge job show](#JobsGet)|Get|[Parameters](#ParametersJobsGet)|[Example](#ExamplesJobsGet)|

### <a name="CommandsInNodes">Commands in `az databoxedge node` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az databoxedge node list](#NodesListByDataBoxEdgeDevice)|ListByDataBoxEdgeDevice|[Parameters](#ParametersNodesListByDataBoxEdgeDevice)|[Example](#ExamplesNodesListByDataBoxEdgeDevice)|

### <a name="CommandsInOperationsStatus">Commands in `az databoxedge operation-status` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az databoxedge operation-status show](#OperationsStatusGet)|Get|[Parameters](#ParametersOperationsStatusGet)|[Example](#ExamplesOperationsStatusGet)|

### <a name="CommandsInOrders">Commands in `az databoxedge order` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az databoxedge order list](#OrdersListByDataBoxEdgeDevice)|ListByDataBoxEdgeDevice|[Parameters](#ParametersOrdersListByDataBoxEdgeDevice)|[Example](#ExamplesOrdersListByDataBoxEdgeDevice)|
|[az databoxedge order show](#OrdersGet)|Get|[Parameters](#ParametersOrdersGet)|[Example](#ExamplesOrdersGet)|
|[az databoxedge order create](#OrdersCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersOrdersCreateOrUpdate#Create)|[Example](#ExamplesOrdersCreateOrUpdate#Create)|
|[az databoxedge order update](#OrdersCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersOrdersCreateOrUpdate#Update)|Not Found|
|[az databoxedge order delete](#OrdersDelete)|Delete|[Parameters](#ParametersOrdersDelete)|[Example](#ExamplesOrdersDelete)|

### <a name="CommandsInRoles">Commands in `az databoxedge role` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az databoxedge role list](#RolesListByDataBoxEdgeDevice)|ListByDataBoxEdgeDevice|[Parameters](#ParametersRolesListByDataBoxEdgeDevice)|[Example](#ExamplesRolesListByDataBoxEdgeDevice)|
|[az databoxedge role show](#RolesGet)|Get|[Parameters](#ParametersRolesGet)|[Example](#ExamplesRolesGet)|
|[az databoxedge role create](#RolesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersRolesCreateOrUpdate#Create)|[Example](#ExamplesRolesCreateOrUpdate#Create)|
|[az databoxedge role update](#RolesCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersRolesCreateOrUpdate#Update)|Not Found|
|[az databoxedge role delete](#RolesDelete)|Delete|[Parameters](#ParametersRolesDelete)|[Example](#ExamplesRolesDelete)|

### <a name="CommandsInShares">Commands in `az databoxedge share` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az databoxedge share list](#SharesListByDataBoxEdgeDevice)|ListByDataBoxEdgeDevice|[Parameters](#ParametersSharesListByDataBoxEdgeDevice)|[Example](#ExamplesSharesListByDataBoxEdgeDevice)|
|[az databoxedge share show](#SharesGet)|Get|[Parameters](#ParametersSharesGet)|[Example](#ExamplesSharesGet)|
|[az databoxedge share create](#SharesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersSharesCreateOrUpdate#Create)|[Example](#ExamplesSharesCreateOrUpdate#Create)|
|[az databoxedge share update](#SharesCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersSharesCreateOrUpdate#Update)|Not Found|
|[az databoxedge share delete](#SharesDelete)|Delete|[Parameters](#ParametersSharesDelete)|[Example](#ExamplesSharesDelete)|
|[az databoxedge share refresh](#SharesRefresh)|Refresh|[Parameters](#ParametersSharesRefresh)|[Example](#ExamplesSharesRefresh)|

### <a name="CommandsInSkus">Commands in `az databoxedge sku` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az databoxedge sku list](#SkusList)|List|[Parameters](#ParametersSkusList)|[Example](#ExamplesSkusList)|

### <a name="CommandsInStorageAccounts">Commands in `az databoxedge storage-account` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az databoxedge storage-account list](#StorageAccountsListByDataBoxEdgeDevice)|ListByDataBoxEdgeDevice|[Parameters](#ParametersStorageAccountsListByDataBoxEdgeDevice)|[Example](#ExamplesStorageAccountsListByDataBoxEdgeDevice)|
|[az databoxedge storage-account show](#StorageAccountsGet)|Get|[Parameters](#ParametersStorageAccountsGet)|[Example](#ExamplesStorageAccountsGet)|
|[az databoxedge storage-account create](#StorageAccountsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersStorageAccountsCreateOrUpdate#Create)|[Example](#ExamplesStorageAccountsCreateOrUpdate#Create)|
|[az databoxedge storage-account update](#StorageAccountsCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersStorageAccountsCreateOrUpdate#Update)|Not Found|
|[az databoxedge storage-account delete](#StorageAccountsDelete)|Delete|[Parameters](#ParametersStorageAccountsDelete)|[Example](#ExamplesStorageAccountsDelete)|

### <a name="CommandsInStorageAccountCredentials">Commands in `az databoxedge storage-account-credentials` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az databoxedge storage-account-credentials list](#StorageAccountCredentialsListByDataBoxEdgeDevice)|ListByDataBoxEdgeDevice|[Parameters](#ParametersStorageAccountCredentialsListByDataBoxEdgeDevice)|[Example](#ExamplesStorageAccountCredentialsListByDataBoxEdgeDevice)|
|[az databoxedge storage-account-credentials show](#StorageAccountCredentialsGet)|Get|[Parameters](#ParametersStorageAccountCredentialsGet)|[Example](#ExamplesStorageAccountCredentialsGet)|
|[az databoxedge storage-account-credentials create](#StorageAccountCredentialsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersStorageAccountCredentialsCreateOrUpdate#Create)|[Example](#ExamplesStorageAccountCredentialsCreateOrUpdate#Create)|
|[az databoxedge storage-account-credentials update](#StorageAccountCredentialsCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersStorageAccountCredentialsCreateOrUpdate#Update)|Not Found|
|[az databoxedge storage-account-credentials delete](#StorageAccountCredentialsDelete)|Delete|[Parameters](#ParametersStorageAccountCredentialsDelete)|[Example](#ExamplesStorageAccountCredentialsDelete)|

### <a name="CommandsInTriggers">Commands in `az databoxedge trigger` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az databoxedge trigger list](#TriggersListByDataBoxEdgeDevice)|ListByDataBoxEdgeDevice|[Parameters](#ParametersTriggersListByDataBoxEdgeDevice)|[Example](#ExamplesTriggersListByDataBoxEdgeDevice)|
|[az databoxedge trigger show](#TriggersGet)|Get|[Parameters](#ParametersTriggersGet)|[Example](#ExamplesTriggersGet)|
|[az databoxedge trigger create](#TriggersCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersTriggersCreateOrUpdate#Create)|[Example](#ExamplesTriggersCreateOrUpdate#Create)|
|[az databoxedge trigger update](#TriggersCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersTriggersCreateOrUpdate#Update)|Not Found|
|[az databoxedge trigger delete](#TriggersDelete)|Delete|[Parameters](#ParametersTriggersDelete)|[Example](#ExamplesTriggersDelete)|

### <a name="CommandsInUsers">Commands in `az databoxedge user` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az databoxedge user list](#UsersListByDataBoxEdgeDevice)|ListByDataBoxEdgeDevice|[Parameters](#ParametersUsersListByDataBoxEdgeDevice)|[Example](#ExamplesUsersListByDataBoxEdgeDevice)|
|[az databoxedge user show](#UsersGet)|Get|[Parameters](#ParametersUsersGet)|[Example](#ExamplesUsersGet)|
|[az databoxedge user create](#UsersCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersUsersCreateOrUpdate#Create)|[Example](#ExamplesUsersCreateOrUpdate#Create)|
|[az databoxedge user update](#UsersCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersUsersCreateOrUpdate#Update)|Not Found|
|[az databoxedge user delete](#UsersDelete)|Delete|[Parameters](#ParametersUsersDelete)|[Example](#ExamplesUsersDelete)|


## COMMAND DETAILS

### group `az databoxedge alert`
#### <a name="AlertsListByDataBoxEdgeDevice">Command `az databoxedge alert list`</a>

##### <a name="ExamplesAlertsListByDataBoxEdgeDevice">Example</a>
```
az databoxedge alert list --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersAlertsListByDataBoxEdgeDevice">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

#### <a name="AlertsGet">Command `az databoxedge alert show`</a>

##### <a name="ExamplesAlertsGet">Example</a>
```
az databoxedge alert show --name "159a00c7-8543-4343-9435-263ac87df3bb" --device-name "testedgedevice" \
--resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersAlertsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The alert name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### group `az databoxedge bandwidth-schedule`
#### <a name="BandwidthSchedulesListByDataBoxEdgeDevice">Command `az databoxedge bandwidth-schedule list`</a>

##### <a name="ExamplesBandwidthSchedulesListByDataBoxEdgeDevice">Example</a>
```
az databoxedge bandwidth-schedule list --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersBandwidthSchedulesListByDataBoxEdgeDevice">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

#### <a name="BandwidthSchedulesGet">Command `az databoxedge bandwidth-schedule show`</a>

##### <a name="ExamplesBandwidthSchedulesGet">Example</a>
```
az databoxedge bandwidth-schedule show --name "bandwidth-1" --device-name "testedgedevice" --resource-group \
"GroupForEdgeAutomation"
```
##### <a name="ParametersBandwidthSchedulesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The bandwidth schedule name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

#### <a name="BandwidthSchedulesCreateOrUpdate#Create">Command `az databoxedge bandwidth-schedule create`</a>

##### <a name="ExamplesBandwidthSchedulesCreateOrUpdate#Create">Example</a>
```
az databoxedge bandwidth-schedule create --name "bandwidth-1" --device-name "testedgedevice" --days "Sunday" --days \
"Monday" --rate-in-mbps 100 --start "0:0:0" --stop "13:59:0" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersBandwidthSchedulesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The bandwidth schedule name which needs to be added/updated.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--start**|string|The start time of the schedule in UTC.|start|start|
|**--stop**|string|The stop time of the schedule in UTC.|stop|stop|
|**--rate-in-mbps**|integer|The bandwidth rate in Mbps.|rate_in_mbps|rateInMbps|
|**--days**|array|The days of the week when this schedule is applicable.|days|days|

#### <a name="BandwidthSchedulesCreateOrUpdate#Update">Command `az databoxedge bandwidth-schedule update`</a>

##### <a name="ParametersBandwidthSchedulesCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The bandwidth schedule name which needs to be added/updated.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--start**|string|The start time of the schedule in UTC.|start|start|
|**--stop**|string|The stop time of the schedule in UTC.|stop|stop|
|**--rate-in-mbps**|integer|The bandwidth rate in Mbps.|rate_in_mbps|rateInMbps|
|**--days**|array|The days of the week when this schedule is applicable.|days|days|

#### <a name="BandwidthSchedulesDelete">Command `az databoxedge bandwidth-schedule delete`</a>

##### <a name="ExamplesBandwidthSchedulesDelete">Example</a>
```
az databoxedge bandwidth-schedule delete --name "bandwidth-1" --device-name "testedgedevice" --resource-group \
"GroupForEdgeAutomation"
```
##### <a name="ParametersBandwidthSchedulesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The bandwidth schedule name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### group `az databoxedge container`
#### <a name="ContainersListByStorageAccount">Command `az databoxedge container list`</a>

##### <a name="ExamplesContainersListByStorageAccount">Example</a>
```
az databoxedge container list --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation" \
--storage-account-name "storageaccount1"
```
##### <a name="ParametersContainersListByStorageAccount">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--storage-account-name**|string|The storage Account name.|storage_account_name|storageAccountName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

#### <a name="ContainersGet">Command `az databoxedge container show`</a>

##### <a name="ExamplesContainersGet">Example</a>
```
az databoxedge container show --name "blobcontainer1" --device-name "testedgedevice" --resource-group \
"GroupForEdgeAutomation" --storage-account-name "storageaccount1"
```
##### <a name="ParametersContainersGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--storage-account-name**|string|The Storage Account Name|storage_account_name|storageAccountName|
|**--container-name**|string|The container Name|container_name|containerName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

#### <a name="ContainersCreateOrUpdate#Create">Command `az databoxedge container create`</a>

##### <a name="ExamplesContainersCreateOrUpdate#Create">Example</a>
```
az databoxedge container create --data-format "BlockBlob" --name "blobcontainer1" --device-name "testedgedevice" \
--resource-group "GroupForEdgeAutomation" --storage-account-name "storageaccount1"
```
##### <a name="ParametersContainersCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--storage-account-name**|string|The Storage Account Name|storage_account_name|storageAccountName|
|**--container-name**|string|The container name.|container_name|containerName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--data-format**|choice|DataFormat for Container|data_format|dataFormat|

#### <a name="ContainersCreateOrUpdate#Update">Command `az databoxedge container update`</a>

##### <a name="ParametersContainersCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--storage-account-name**|string|The Storage Account Name|storage_account_name|storageAccountName|
|**--container-name**|string|The container name.|container_name|containerName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--data-format**|choice|DataFormat for Container|data_format|dataFormat|

#### <a name="ContainersDelete">Command `az databoxedge container delete`</a>

##### <a name="ExamplesContainersDelete">Example</a>
```
az databoxedge container delete --name "blobcontainer1" --device-name "testedgedevice" --resource-group \
"GroupForEdgeAutomation" --storage-account-name "storageaccount1"
```
##### <a name="ParametersContainersDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--storage-account-name**|string|The Storage Account Name|storage_account_name|storageAccountName|
|**--container-name**|string|The container name.|container_name|containerName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

#### <a name="ContainersRefresh">Command `az databoxedge container refresh`</a>

##### <a name="ExamplesContainersRefresh">Example</a>
```
az databoxedge container refresh --name "blobcontainer1" --device-name "testedgedevice" --resource-group \
"GroupForEdgeAutomation" --storage-account-name "storageaccount1"
```
##### <a name="ParametersContainersRefresh">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--storage-account-name**|string|The Storage Account Name|storage_account_name|storageAccountName|
|**--container-name**|string|The container name.|container_name|containerName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### group `az databoxedge device`
#### <a name="DevicesListByResourceGroup">Command `az databoxedge device list`</a>

##### <a name="ExamplesDevicesListByResourceGroup">Example</a>
```
az databoxedge device list --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersDevicesListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--expand**|string|Specify $expand=details to populate additional fields related to the resource or Specify $skipToken=:code:`<token>` to populate the next page in the list.|expand|$expand|

#### <a name="DevicesListBySubscription">Command `az databoxedge device list`</a>

##### <a name="ExamplesDevicesListBySubscription">Example</a>
```
az databoxedge device list
```
##### <a name="ParametersDevicesListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="DevicesGet">Command `az databoxedge device show`</a>

##### <a name="ExamplesDevicesGet">Example</a>
```
az databoxedge device show --name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersDevicesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

#### <a name="DevicesCreateOrUpdate#Create">Command `az databoxedge device create`</a>

##### <a name="ExamplesDevicesCreateOrUpdate#Create">Example</a>
```
az databoxedge device create --location "eastus" --sku name="Edge" tier="Standard" --name "testedgedevice" \
--resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersDevicesCreateOrUpdate#Create">Parameters</a> 
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

#### <a name="DevicesUpdate">Command `az databoxedge device update`</a>

##### <a name="ExamplesDevicesUpdate">Example</a>
```
az databoxedge device update --name "testedgedevice" --tags Key1="value1" Key2="value2" --resource-group \
"GroupForEdgeAutomation"
```
##### <a name="ParametersDevicesUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--tags**|dictionary|The tags attached to the Data Box Edge/Gateway resource.|tags|tags|

#### <a name="DevicesDelete">Command `az databoxedge device delete`</a>

##### <a name="ExamplesDevicesDelete">Example</a>
```
az databoxedge device delete --name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersDevicesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

#### <a name="DevicesCreateOrUpdateSecuritySettings">Command `az databoxedge device create-or-update-security-setting`</a>

##### <a name="ExamplesDevicesCreateOrUpdateSecuritySettings">Example</a>
```
az databoxedge device create-or-update-security-setting --name "testedgedevice" --resource-group "AzureVM" \
--device-admin-password encryption-algorithm="AES256" encryption-cert-thumbprint="7DCBDFC44ED968D232C9A998FC105B5C70E84\
BE0" value="jJ5MvXa/AEWvwxviS92uCjatCXeyLYTy8jx/k105MjQRXT7i6Do8qpEcQ8d+OBbwmQTnwKW0CYyzzVRCc0uZcPCf6PsWtP4l6wvcKGAP66P\
wK68eEkTUOmp+wUHc4hk02kWmTWeAjBZkuDBP3xK1RnZo95g2RE4i1UgKNP5BEKCLd71O104DW3AWW41mh9XLWNOaxw+VjQY7wmvlE6XkvpkMhcGuha2u7l\
x8zi9ZkcMvJVYDYK36Fb/K3KhBAmDjjDmVq04jtBlcSTXQObt0nlj4BwGGtdrpeIpr67zqr5i3cPm6e6AleIaIhp6sI/uyGSMiT3oev2eg49u2ii7kVA=="
```
##### <a name="ParametersDevicesCreateOrUpdateSecuritySettings">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--device-admin-password**|object|Device administrator password as an encrypted string (encrypted using RSA PKCS #1) is used to sign into the  local web UI of the device. The Actual password should have at least 8 characters that are a combination of  uppercase, lowercase, numeric, and special characters.|device_admin_password|deviceAdminPassword|

#### <a name="DevicesDownloadUpdates">Command `az databoxedge device download-update`</a>

##### <a name="ExamplesDevicesDownloadUpdates">Example</a>
```
az databoxedge device download-update --name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersDevicesDownloadUpdates">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

#### <a name="DevicesGetExtendedInformation">Command `az databoxedge device get-extended-information`</a>

##### <a name="ExamplesDevicesGetExtendedInformation">Example</a>
```
az databoxedge device get-extended-information --name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersDevicesGetExtendedInformation">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

#### <a name="DevicesGetNetworkSettings">Command `az databoxedge device get-network-setting`</a>

##### <a name="ExamplesDevicesGetNetworkSettings">Example</a>
```
az databoxedge device get-network-setting --name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersDevicesGetNetworkSettings">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

#### <a name="DevicesGetUpdateSummary">Command `az databoxedge device get-update-summary`</a>

##### <a name="ExamplesDevicesGetUpdateSummary">Example</a>
```
az databoxedge device get-update-summary --name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersDevicesGetUpdateSummary">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

#### <a name="DevicesInstallUpdates">Command `az databoxedge device install-update`</a>

##### <a name="ExamplesDevicesInstallUpdates">Example</a>
```
az databoxedge device install-update --name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersDevicesInstallUpdates">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

#### <a name="DevicesScanForUpdates">Command `az databoxedge device scan-for-update`</a>

##### <a name="ExamplesDevicesScanForUpdates">Example</a>
```
az databoxedge device scan-for-update --name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersDevicesScanForUpdates">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

#### <a name="DevicesUploadCertificate">Command `az databoxedge device upload-certificate`</a>

##### <a name="ExamplesDevicesUploadCertificate">Example</a>
```
az databoxedge device upload-certificate --name "testedgedevice" --certificate "MIIC9DCCAdygAwIBAgIQWJae7GNjiI9Mcv/gJyr\
OPTANBgkqhkiG9w0BAQUFADASMRAwDgYDVQQDDAdXaW5kb3dzMB4XDTE4MTEyNzAwMTA0NVoXDTIxMTEyODAwMTA0NVowEjEQMA4GA1UEAwwHV2luZG93cz\
CCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAKxkRExqxf0qH1avnyORptIbRC2yQwqe3EIbJ2FPKr5jtAppGeX/dGKrFSnX+7/0HFr77aJHafdpE\
AtOiLyJ4zCAVs0obZCCIq4qJdmjYUTU0UXH/w/YzXfQA0d9Zh9AN+NJBX9xj05NzgsT24fkgsK2v6mWJQXT7YcWAsl5sEYPnx1e+MrupNyVSL/RUJmrS+et\
JSysHtFeWRhsUhVAs1DD5ExJvBLU3WH0IsojEvpXcjrutB5/MDQNrd/StGI6WovoSSPH7FyT9tgERx+q+Yg3YUGzfaIPCctlrRGehcdtzdNoKd0rsX62yCq\
0U6POoSfwe22NJu41oAUMd7e6R8cCAwEAAaNGMEQwEwYDVR0lBAwwCgYIKwYBBQUHAwIwHQYDVR0OBBYEFDd0VxnS3LnMIfwc7xW4b4IZWG5GMA4GA1UdDw\
EB/wQEAwIFIDANBgkqhkiG9w0BAQUFAAOCAQEAPQRby2u9celvtvL/DLEb5Vt3/tPStRQC5MyTD62L5RT/q8E6EMCXVZNkXF5WlWucLJi/18tY+9PNgP9xW\
LJh7kpSWlWdi9KPtwMqKDlEH8L2TnQdjimt9XuiCrTnoFy/1X2BGLY/rCaUJNSd15QCkz2xeW+Z+YSk2GwAc/A/4YfNpqSIMfNuPrT76o02VdD9WmJUA3fS\
/HY0sU9qgQRS/3F5/0EPS+HYQ0SvXCK9tggcCd4O050ytNBMJC9qMOJ7yE0iOrFfOJSCfDAuPhn/rHFh79Kn1moF+/CE+nc0/2RPiLC8r54/rt5dYyyxJDf\
Xg0a3VrrX39W69WZGW5OXiw==" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersDevicesUploadCertificate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--certificate**|string|The base64 encoded certificate raw data.|certificate|certificate|
|**--authentication-type**|choice|The authentication type.|authentication_type|authenticationType|

### group `az databoxedge job`
#### <a name="JobsGet">Command `az databoxedge job show`</a>

##### <a name="ExamplesJobsGet">Example</a>
```
az databoxedge job show --name "159a00c7-8543-4343-9435-263ac87df3bb" --device-name "testedgedevice" --resource-group \
"GroupForEdgeAutomation"
```
##### <a name="ParametersJobsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The job name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### group `az databoxedge node`
#### <a name="NodesListByDataBoxEdgeDevice">Command `az databoxedge node list`</a>

##### <a name="ExamplesNodesListByDataBoxEdgeDevice">Example</a>
```
az databoxedge node list --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersNodesListByDataBoxEdgeDevice">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### group `az databoxedge operation-status`
#### <a name="OperationsStatusGet">Command `az databoxedge operation-status show`</a>

##### <a name="ExamplesOperationsStatusGet">Example</a>
```
az databoxedge operation-status show --name "159a00c7-8543-4343-9435-263ac87df3bb" --device-name "testedgedevice" \
--resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersOperationsStatusGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The job name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### group `az databoxedge order`
#### <a name="OrdersListByDataBoxEdgeDevice">Command `az databoxedge order list`</a>

##### <a name="ExamplesOrdersListByDataBoxEdgeDevice">Example</a>
```
az databoxedge order list --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersOrdersListByDataBoxEdgeDevice">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

#### <a name="OrdersGet">Command `az databoxedge order show`</a>

##### <a name="ExamplesOrdersGet">Example</a>
```
az databoxedge order show --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersOrdersGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

#### <a name="OrdersCreateOrUpdate#Create">Command `az databoxedge order create`</a>

##### <a name="ExamplesOrdersCreateOrUpdate#Create">Example</a>
```
az databoxedge order create --device-name "testedgedevice" --contact-information company-name="Microsoft" \
contact-person="John Mcclane" email-list="john@microsoft.com" phone="(800) 426-9400" --shipping-address \
address-line1="Microsoft Corporation" address-line2="One Microsoft Way" address-line3="Redmond" city="WA" \
country="USA" postal-code="98052" state="WA" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersOrdersCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The order details of a device.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--contact-information**|object|The contact details.|contact_information|contactInformation|
|**--shipping-address**|object|The shipping address.|shipping_address|shippingAddress|
|**--current-status-status**|choice|Status of the order as per the allowed status types.|status|status|
|**--current-status-comments**|string|Comments related to this status change.|comments|comments|

#### <a name="OrdersCreateOrUpdate#Update">Command `az databoxedge order update`</a>

##### <a name="ParametersOrdersCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The order details of a device.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--contact-information**|object|The contact details.|contact_information|contactInformation|
|**--shipping-address**|object|The shipping address.|shipping_address|shippingAddress|
|**--current-status-status**|choice|Status of the order as per the allowed status types.|status|status|
|**--current-status-comments**|string|Comments related to this status change.|comments|comments|

#### <a name="OrdersDelete">Command `az databoxedge order delete`</a>

##### <a name="ExamplesOrdersDelete">Example</a>
```
az databoxedge order delete --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersOrdersDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### group `az databoxedge role`
#### <a name="RolesListByDataBoxEdgeDevice">Command `az databoxedge role list`</a>

##### <a name="ExamplesRolesListByDataBoxEdgeDevice">Example</a>
```
az databoxedge role list --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersRolesListByDataBoxEdgeDevice">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

#### <a name="RolesGet">Command `az databoxedge role show`</a>

##### <a name="ExamplesRolesGet">Example</a>
```
az databoxedge role show --name "IoTRole1" --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersRolesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The role name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

#### <a name="RolesCreateOrUpdate#Create">Command `az databoxedge role create`</a>

##### <a name="ExamplesRolesCreateOrUpdate#Create">Example</a>
```
az databoxedge role create --name "IoTRole1" --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation" \
--role "{\\"kind\\":\\"IOT\\",\\"properties\\":{\\"hostPlatform\\":\\"Linux\\",\\"ioTDeviceDetails\\":{\\"authenticatio\
n\\":{\\"symmetricKey\\":{\\"connectionString\\":{\\"encryptionAlgorithm\\":\\"AES256\\",\\"encryptionCertThumbprint\\"\
:\\"348586569999244\\",\\"value\\":\\"Encrypted<<HostName=iothub.azure-devices.net;DeviceId=iotDevice;SharedAccessKey=2\
C750FscEas3JmQ8Bnui5yQWZPyml0/UiRt1bQwd8=>>\\"}}},\\"deviceId\\":\\"iotdevice\\",\\"ioTHostHub\\":\\"iothub.azure-devic\
es.net\\"},\\"ioTEdgeDeviceDetails\\":{\\"authentication\\":{\\"symmetricKey\\":{\\"connectionString\\":{\\"encryptionA\
lgorithm\\":\\"AES256\\",\\"encryptionCertThumbprint\\":\\"1245475856069999244\\",\\"value\\":\\"Encrypted<<HostName=io\
thub.azure-devices.net;DeviceId=iotEdge;SharedAccessKey=2C750FscEas3JmQ8Bnui5yQWZPyml0/UiRt1bQwd8=>>\\"}}},\\"deviceId\
\\":\\"iotEdge\\",\\"ioTHostHub\\":\\"iothub.azure-devices.net\\"},\\"roleStatus\\":\\"Enabled\\",\\"shareMappings\\":[\
]}}"
```
##### <a name="ParametersRolesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The role name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--role**|object|The role properties.|role|role|

#### <a name="RolesCreateOrUpdate#Update">Command `az databoxedge role update`</a>

##### <a name="ParametersRolesCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The role name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--role**|object|The role properties.|role|role|

#### <a name="RolesDelete">Command `az databoxedge role delete`</a>

##### <a name="ExamplesRolesDelete">Example</a>
```
az databoxedge role delete --name "IoTRole1" --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersRolesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The role name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### group `az databoxedge share`
#### <a name="SharesListByDataBoxEdgeDevice">Command `az databoxedge share list`</a>

##### <a name="ExamplesSharesListByDataBoxEdgeDevice">Example</a>
```
az databoxedge share list --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersSharesListByDataBoxEdgeDevice">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

#### <a name="SharesGet">Command `az databoxedge share show`</a>

##### <a name="ExamplesSharesGet">Example</a>
```
az databoxedge share show --name "smbshare" --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersSharesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The share name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

#### <a name="SharesCreateOrUpdate#Create">Command `az databoxedge share create`</a>

##### <a name="ExamplesSharesCreateOrUpdate#Create">Example</a>
```
az databoxedge share create --name "smbshare" --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation" \
--description "" --access-protocol "SMB" --azure-container-info container-name="testContainerSMB" \
data-format="BlockBlob" storage-account-credential-id="/subscriptions/4385cf00-2d3a-425a-832f-f4285b1c9dce/resourceGrou\
ps/GroupForEdgeAutomation/providers/Microsoft.DataBoxEdge/dataBoxEdgeDevices/testedgedevice/storageAccountCredentials/s\
ac1" --data-policy "Cloud" --monitoring-status "Enabled" --share-status "Online" --user-access-rights \
access-type="Change" user-id="/subscriptions/4385cf00-2d3a-425a-832f-f4285b1c9dce/resourceGroups/GroupForEdgeAutomation\
/providers/Microsoft.DataBoxEdge/dataBoxEdgeDevices/testedgedevice/users/user2"
```
##### <a name="ParametersSharesCreateOrUpdate#Create">Parameters</a> 
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

#### <a name="SharesCreateOrUpdate#Update">Command `az databoxedge share update`</a>

##### <a name="ParametersSharesCreateOrUpdate#Update">Parameters</a> 
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

#### <a name="SharesDelete">Command `az databoxedge share delete`</a>

##### <a name="ExamplesSharesDelete">Example</a>
```
az databoxedge share delete --name "smbshare" --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersSharesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The share name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

#### <a name="SharesRefresh">Command `az databoxedge share refresh`</a>

##### <a name="ExamplesSharesRefresh">Example</a>
```
az databoxedge share refresh --name "smbshare" --device-name "testedgedevice" --resource-group \
"GroupForEdgeAutomation"
```
##### <a name="ParametersSharesRefresh">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The share name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### group `az databoxedge sku`
#### <a name="SkusList">Command `az databoxedge sku list`</a>

##### <a name="ExamplesSkusList">Example</a>
```
az databoxedge sku list
```
##### <a name="ParametersSkusList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--filter**|string|Specify $filter='location eq :code:`<location>`' to filter on location.|filter|$filter|

### group `az databoxedge storage-account`
#### <a name="StorageAccountsListByDataBoxEdgeDevice">Command `az databoxedge storage-account list`</a>

##### <a name="ExamplesStorageAccountsListByDataBoxEdgeDevice">Example</a>
```
az databoxedge storage-account list --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersStorageAccountsListByDataBoxEdgeDevice">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

#### <a name="StorageAccountsGet">Command `az databoxedge storage-account show`</a>

##### <a name="ExamplesStorageAccountsGet">Example</a>
```
az databoxedge storage-account show --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation" --name \
"blobstorageaccount1"
```
##### <a name="ParametersStorageAccountsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--storage-account-name**|string|The storage account name.|storage_account_name|storageAccountName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

#### <a name="StorageAccountsCreateOrUpdate#Create">Command `az databoxedge storage-account create`</a>

##### <a name="ExamplesStorageAccountsCreateOrUpdate#Create">Example</a>
```
az databoxedge storage-account create --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation" \
--description "It\'s an awesome storage account" --data-policy "Cloud" --storage-account-credential-id \
"/subscriptions/4385cf00-2d3a-425a-832f-f4285b1c9dce/resourceGroups/GroupForDataBoxEdgeAutomation/providers/Microsoft.D\
ataBoxEdge/dataBoxEdgeDevices/testedgedevice/storageAccountCredentials/cisbvt" --storage-account-status "OK" --name \
"blobstorageaccount1"
```
##### <a name="ParametersStorageAccountsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--storage-account-name**|string|The StorageAccount name.|storage_account_name|storageAccountName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--description**|string|Description for the storage Account.|description|description|
|**--storage-account-status**|choice|Current status of the storage account|storage_account_status|storageAccountStatus|
|**--data-policy**|choice|Data policy of the storage Account.|data_policy|dataPolicy|
|**--storage-account-credential-id**|string|Storage Account Credential Id|storage_account_credential_id|storageAccountCredentialId|

#### <a name="StorageAccountsCreateOrUpdate#Update">Command `az databoxedge storage-account update`</a>

##### <a name="ParametersStorageAccountsCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--storage-account-name**|string|The StorageAccount name.|storage_account_name|storageAccountName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--description**|string|Description for the storage Account.|description|description|
|**--storage-account-status**|choice|Current status of the storage account|storage_account_status|storageAccountStatus|
|**--data-policy**|choice|Data policy of the storage Account.|data_policy|dataPolicy|
|**--storage-account-credential-id**|string|Storage Account Credential Id|storage_account_credential_id|storageAccountCredentialId|

#### <a name="StorageAccountsDelete">Command `az databoxedge storage-account delete`</a>

##### <a name="ExamplesStorageAccountsDelete">Example</a>
```
az databoxedge storage-account delete --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation" --name \
"storageaccount1"
```
##### <a name="ParametersStorageAccountsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--storage-account-name**|string|The StorageAccount name.|storage_account_name|storageAccountName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### group `az databoxedge storage-account-credentials`
#### <a name="StorageAccountCredentialsListByDataBoxEdgeDevice">Command `az databoxedge storage-account-credentials list`</a>

##### <a name="ExamplesStorageAccountCredentialsListByDataBoxEdgeDevice">Example</a>
```
az databoxedge storage-account-credentials list --device-name "testedgedevice" --resource-group \
"GroupForEdgeAutomation"
```
##### <a name="ParametersStorageAccountCredentialsListByDataBoxEdgeDevice">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

#### <a name="StorageAccountCredentialsGet">Command `az databoxedge storage-account-credentials show`</a>

##### <a name="ExamplesStorageAccountCredentialsGet">Example</a>
```
az databoxedge storage-account-credentials show --name "sac1" --device-name "testedgedevice" --resource-group \
"GroupForEdgeAutomation"
```
##### <a name="ParametersStorageAccountCredentialsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The storage account credential name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

#### <a name="StorageAccountCredentialsCreateOrUpdate#Create">Command `az databoxedge storage-account-credentials create`</a>

##### <a name="ExamplesStorageAccountCredentialsCreateOrUpdate#Create">Example</a>
```
az databoxedge storage-account-credentials create --name "sac1" --device-name "testedgedevice" --resource-group \
"GroupForEdgeAutomation" --account-key encryption-algorithm="AES256" encryption-cert-thumbprint="2A9D8D6BE51574B5461230\
AEF02F162C5F01AD31" value="lAeZEYi6rNP1/EyNaVUYmTSZEYyaIaWmwUsGwek0+xiZj54GM9Ue9/UA2ed/ClC03wuSit2XzM/cLRU5eYiFBwks23rG\
wiQOr3sruEL2a74EjPD050xYjA6M1I2hu/w2yjVHhn5j+DbXS4Xzi+rHHNZK3DgfDO3PkbECjPck+PbpSBjy9+6Mrjcld5DIZhUAeMlMHrFlg+WKRKB14o/\
og56u5/xX6WKlrMLEQ+y6E18dUwvWs2elTNoVO8PBE8SM/CfooX4AMNvaNdSObNBPdP+F6Lzc556nFNWXrBLRt0vC7s9qTiVRO4x/qCNaK/B4y7IqXMllwQ\
Ff4Np9UQ2ECA==" --account-type "BlobStorage" --alias "sac1" --ssl-status "Disabled" --user-name "cisbvt"
```
##### <a name="ParametersStorageAccountCredentialsCreateOrUpdate#Create">Parameters</a> 
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

#### <a name="StorageAccountCredentialsCreateOrUpdate#Update">Command `az databoxedge storage-account-credentials update`</a>

##### <a name="ParametersStorageAccountCredentialsCreateOrUpdate#Update">Parameters</a> 
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

#### <a name="StorageAccountCredentialsDelete">Command `az databoxedge storage-account-credentials delete`</a>

##### <a name="ExamplesStorageAccountCredentialsDelete">Example</a>
```
az databoxedge storage-account-credentials delete --name "sac1" --device-name "testedgedevice" --resource-group \
"GroupForEdgeAutomation"
```
##### <a name="ParametersStorageAccountCredentialsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The storage account credential name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### group `az databoxedge trigger`
#### <a name="TriggersListByDataBoxEdgeDevice">Command `az databoxedge trigger list`</a>

##### <a name="ExamplesTriggersListByDataBoxEdgeDevice">Example</a>
```
az databoxedge trigger list --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersTriggersListByDataBoxEdgeDevice">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--filter**|string|Specify $filter='CustomContextTag eq :code:`<tag>`' to filter on custom context tag property|filter|$filter|

#### <a name="TriggersGet">Command `az databoxedge trigger show`</a>

##### <a name="ExamplesTriggersGet">Example</a>
```
az databoxedge trigger show --name "trigger1" --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersTriggersGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The trigger name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

#### <a name="TriggersCreateOrUpdate#Create">Command `az databoxedge trigger create`</a>

##### <a name="ExamplesTriggersCreateOrUpdate#Create">Example</a>
```
az databoxedge trigger create --name "trigger1" --device-name "testedgedevice" --resource-group \
"GroupForEdgeAutomation" --file-event-trigger custom-context-tag="CustomContextTags-1235346475"
```
##### <a name="ParametersTriggersCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|Creates or updates a trigger|device_name|deviceName|
|**--name**|string|The trigger name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--file-event-trigger**|object|Trigger details.|file_event_trigger|FileEventTrigger|
|**--periodic-timer-event-trigger**|object|Trigger details.|periodic_timer_event_trigger|PeriodicTimerEventTrigger|

#### <a name="TriggersCreateOrUpdate#Update">Command `az databoxedge trigger update`</a>

##### <a name="ParametersTriggersCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|Creates or updates a trigger|device_name|deviceName|
|**--name**|string|The trigger name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--file-event-trigger**|object|Trigger details.|file_event_trigger|FileEventTrigger|
|**--periodic-timer-event-trigger**|object|Trigger details.|periodic_timer_event_trigger|PeriodicTimerEventTrigger|

#### <a name="TriggersDelete">Command `az databoxedge trigger delete`</a>

##### <a name="ExamplesTriggersDelete">Example</a>
```
az databoxedge trigger delete --name "trigger1" --device-name "testedgedevice" --resource-group \
"GroupForEdgeAutomation"
```
##### <a name="ParametersTriggersDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The trigger name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### group `az databoxedge user`
#### <a name="UsersListByDataBoxEdgeDevice">Command `az databoxedge user list`</a>

##### <a name="ExamplesUsersListByDataBoxEdgeDevice">Example</a>
```
az databoxedge user list --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersUsersListByDataBoxEdgeDevice">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--filter**|string|Specify $filter='UserType eq :code:`<type>`' to filter on user type property|filter|$filter|

#### <a name="UsersGet">Command `az databoxedge user show`</a>

##### <a name="ExamplesUsersGet">Example</a>
```
az databoxedge user show --name "user1" --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersUsersGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The user name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

#### <a name="UsersCreateOrUpdate#Create">Command `az databoxedge user create`</a>

##### <a name="ExamplesUsersCreateOrUpdate#Create">Example</a>
```
az databoxedge user create --name "user1" --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation" \
--encrypted-password encryption-algorithm="None" encryption-cert-thumbprint="blah" value="Password@1" --user-type \
"Share"
```
##### <a name="ParametersUsersCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The user name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--user-type**|choice|Type of the user.|user_type|userType|
|**--encrypted-password**|object|The password details.|encrypted_password|encryptedPassword|
|**--share-access-rights**|array|List of shares that the user has rights on. This field should not be specified during user creation.|share_access_rights|shareAccessRights|

#### <a name="UsersCreateOrUpdate#Update">Command `az databoxedge user update`</a>

##### <a name="ParametersUsersCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The user name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--user-type**|choice|Type of the user.|user_type|userType|
|**--encrypted-password**|object|The password details.|encrypted_password|encryptedPassword|
|**--share-access-rights**|array|List of shares that the user has rights on. This field should not be specified during user creation.|share_access_rights|shareAccessRights|

#### <a name="UsersDelete">Command `az databoxedge user delete`</a>

##### <a name="ExamplesUsersDelete">Example</a>
```
az databoxedge user delete --name "user1" --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersUsersDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The user name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
