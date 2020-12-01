# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az data-box-edge|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az data-box-edge` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az data-box-edge device|Devices|[commands](#CommandsInDevices)|
|az data-box-edge alert|Alerts|[commands](#CommandsInAlerts)|
|az data-box-edge bandwidth-schedule|BandwidthSchedules|[commands](#CommandsInBandwidthSchedules)|
|az data-box-edge|Jobs|[commands](#CommandsInJobs)|
|az data-box-edge|Nodes|[commands](#CommandsInNodes)|
|az data-box-edge order|Orders|[commands](#CommandsInOrders)|
|az data-box-edge|Skus|[commands](#CommandsInSkus)|

## COMMANDS
### <a name="CommandsInJobs">Commands in `az data-box-edge` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az data-box-edge show-job](#JobsGet)|Get|[Parameters](#ParametersJobsGet)|[Example](#ExamplesJobsGet)|

### <a name="CommandsInNodes">Commands in `az data-box-edge` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az data-box-edge list-node](#NodesListByDataBoxEdgeDevice)|ListByDataBoxEdgeDevice|[Parameters](#ParametersNodesListByDataBoxEdgeDevice)|[Example](#ExamplesNodesListByDataBoxEdgeDevice)|

### <a name="CommandsInSkus">Commands in `az data-box-edge` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az data-box-edge list-sku](#SkusList)|List|[Parameters](#ParametersSkusList)|[Example](#ExamplesSkusList)|

### <a name="CommandsInAlerts">Commands in `az data-box-edge alert` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az data-box-edge alert list](#AlertsListByDataBoxEdgeDevice)|ListByDataBoxEdgeDevice|[Parameters](#ParametersAlertsListByDataBoxEdgeDevice)|[Example](#ExamplesAlertsListByDataBoxEdgeDevice)|
|[az data-box-edge alert show](#AlertsGet)|Get|[Parameters](#ParametersAlertsGet)|[Example](#ExamplesAlertsGet)|

### <a name="CommandsInBandwidthSchedules">Commands in `az data-box-edge bandwidth-schedule` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az data-box-edge bandwidth-schedule list](#BandwidthSchedulesListByDataBoxEdgeDevice)|ListByDataBoxEdgeDevice|[Parameters](#ParametersBandwidthSchedulesListByDataBoxEdgeDevice)|[Example](#ExamplesBandwidthSchedulesListByDataBoxEdgeDevice)|
|[az data-box-edge bandwidth-schedule show](#BandwidthSchedulesGet)|Get|[Parameters](#ParametersBandwidthSchedulesGet)|[Example](#ExamplesBandwidthSchedulesGet)|
|[az data-box-edge bandwidth-schedule create](#BandwidthSchedulesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersBandwidthSchedulesCreateOrUpdate#Create)|[Example](#ExamplesBandwidthSchedulesCreateOrUpdate#Create)|
|[az data-box-edge bandwidth-schedule update](#BandwidthSchedulesCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersBandwidthSchedulesCreateOrUpdate#Update)|Not Found|
|[az data-box-edge bandwidth-schedule delete](#BandwidthSchedulesDelete)|Delete|[Parameters](#ParametersBandwidthSchedulesDelete)|[Example](#ExamplesBandwidthSchedulesDelete)|

### <a name="CommandsInDevices">Commands in `az data-box-edge device` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az data-box-edge device list](#DevicesListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersDevicesListByResourceGroup)|[Example](#ExamplesDevicesListByResourceGroup)|
|[az data-box-edge device list](#DevicesListBySubscription)|ListBySubscription|[Parameters](#ParametersDevicesListBySubscription)|[Example](#ExamplesDevicesListBySubscription)|
|[az data-box-edge device show](#DevicesGet)|Get|[Parameters](#ParametersDevicesGet)|[Example](#ExamplesDevicesGet)|
|[az data-box-edge device create](#DevicesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersDevicesCreateOrUpdate#Create)|[Example](#ExamplesDevicesCreateOrUpdate#Create)|
|[az data-box-edge device update](#DevicesUpdate)|Update|[Parameters](#ParametersDevicesUpdate)|[Example](#ExamplesDevicesUpdate)|
|[az data-box-edge device delete](#DevicesDelete)|Delete|[Parameters](#ParametersDevicesDelete)|[Example](#ExamplesDevicesDelete)|
|[az data-box-edge device download-update](#DevicesDownloadUpdates)|DownloadUpdates|[Parameters](#ParametersDevicesDownloadUpdates)|[Example](#ExamplesDevicesDownloadUpdates)|
|[az data-box-edge device install-update](#DevicesInstallUpdates)|InstallUpdates|[Parameters](#ParametersDevicesInstallUpdates)|[Example](#ExamplesDevicesInstallUpdates)|
|[az data-box-edge device scan-for-update](#DevicesScanForUpdates)|ScanForUpdates|[Parameters](#ParametersDevicesScanForUpdates)|[Example](#ExamplesDevicesScanForUpdates)|
|[az data-box-edge device show-update-summary](#DevicesGetUpdateSummary)|GetUpdateSummary|[Parameters](#ParametersDevicesGetUpdateSummary)|[Example](#ExamplesDevicesGetUpdateSummary)|

### <a name="CommandsInOrders">Commands in `az data-box-edge order` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az data-box-edge order list](#OrdersListByDataBoxEdgeDevice)|ListByDataBoxEdgeDevice|[Parameters](#ParametersOrdersListByDataBoxEdgeDevice)|[Example](#ExamplesOrdersListByDataBoxEdgeDevice)|
|[az data-box-edge order show](#OrdersGet)|Get|[Parameters](#ParametersOrdersGet)|[Example](#ExamplesOrdersGet)|
|[az data-box-edge order create](#OrdersCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersOrdersCreateOrUpdate#Create)|[Example](#ExamplesOrdersCreateOrUpdate#Create)|
|[az data-box-edge order update](#OrdersCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersOrdersCreateOrUpdate#Update)|Not Found|
|[az data-box-edge order delete](#OrdersDelete)|Delete|[Parameters](#ParametersOrdersDelete)|[Example](#ExamplesOrdersDelete)|


## COMMAND DETAILS

### group `az data-box-edge`
#### <a name="JobsGet">Command `az data-box-edge show-job`</a>

##### <a name="ExamplesJobsGet">Example</a>
```
az data-box-edge show-job --name "159a00c7-8543-4343-9435-263ac87df3bb" --device-name "testedgedevice" \
--resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersJobsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The job name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### group `az data-box-edge`
#### <a name="NodesListByDataBoxEdgeDevice">Command `az data-box-edge list-node`</a>

##### <a name="ExamplesNodesListByDataBoxEdgeDevice">Example</a>
```
az data-box-edge list-node --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersNodesListByDataBoxEdgeDevice">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### group `az data-box-edge`
#### <a name="SkusList">Command `az data-box-edge list-sku`</a>

##### <a name="ExamplesSkusList">Example</a>
```
az data-box-edge list-sku
```
##### <a name="ParametersSkusList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--filter**|string|Specify $filter='location eq :code:`<location>`' to filter on location.|filter|$filter|

### group `az data-box-edge alert`
#### <a name="AlertsListByDataBoxEdgeDevice">Command `az data-box-edge alert list`</a>

##### <a name="ExamplesAlertsListByDataBoxEdgeDevice">Example</a>
```
az data-box-edge alert list --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersAlertsListByDataBoxEdgeDevice">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

#### <a name="AlertsGet">Command `az data-box-edge alert show`</a>

##### <a name="ExamplesAlertsGet">Example</a>
```
az data-box-edge alert show --name "159a00c7-8543-4343-9435-263ac87df3bb" --device-name "testedgedevice" \
--resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersAlertsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The alert name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### group `az data-box-edge bandwidth-schedule`
#### <a name="BandwidthSchedulesListByDataBoxEdgeDevice">Command `az data-box-edge bandwidth-schedule list`</a>

##### <a name="ExamplesBandwidthSchedulesListByDataBoxEdgeDevice">Example</a>
```
az data-box-edge bandwidth-schedule list --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersBandwidthSchedulesListByDataBoxEdgeDevice">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

#### <a name="BandwidthSchedulesGet">Command `az data-box-edge bandwidth-schedule show`</a>

##### <a name="ExamplesBandwidthSchedulesGet">Example</a>
```
az data-box-edge bandwidth-schedule show --name "bandwidth-1" --device-name "testedgedevice" --resource-group \
"GroupForEdgeAutomation"
```
##### <a name="ParametersBandwidthSchedulesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The bandwidth schedule name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

#### <a name="BandwidthSchedulesCreateOrUpdate#Create">Command `az data-box-edge bandwidth-schedule create`</a>

##### <a name="ExamplesBandwidthSchedulesCreateOrUpdate#Create">Example</a>
```
az data-box-edge bandwidth-schedule create --name "bandwidth-1" --device-name "testedgedevice" --days "Sunday" --days \
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

#### <a name="BandwidthSchedulesCreateOrUpdate#Update">Command `az data-box-edge bandwidth-schedule update`</a>

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

#### <a name="BandwidthSchedulesDelete">Command `az data-box-edge bandwidth-schedule delete`</a>

##### <a name="ExamplesBandwidthSchedulesDelete">Example</a>
```
az data-box-edge bandwidth-schedule delete --name "bandwidth-1" --device-name "testedgedevice" --resource-group \
"GroupForEdgeAutomation"
```
##### <a name="ParametersBandwidthSchedulesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--name**|string|The bandwidth schedule name.|name|name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### group `az data-box-edge device`
#### <a name="DevicesListByResourceGroup">Command `az data-box-edge device list`</a>

##### <a name="ExamplesDevicesListByResourceGroup">Example</a>
```
az data-box-edge device list --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersDevicesListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--expand**|string|Specify $expand=details to populate additional fields related to the resource or Specify $skipToken=:code:`<token>` to populate the next page in the list.|expand|$expand|

#### <a name="DevicesListBySubscription">Command `az data-box-edge device list`</a>

##### <a name="ExamplesDevicesListBySubscription">Example</a>
```
az data-box-edge device list
```
##### <a name="ParametersDevicesListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="DevicesGet">Command `az data-box-edge device show`</a>

##### <a name="ExamplesDevicesGet">Example</a>
```
az data-box-edge device show --name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersDevicesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

#### <a name="DevicesCreateOrUpdate#Create">Command `az data-box-edge device create`</a>

##### <a name="ExamplesDevicesCreateOrUpdate#Create">Example</a>
```
az data-box-edge device create --location "eastus" --sku name="Edge" tier="Standard" --name "testedgedevice" \
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

#### <a name="DevicesUpdate">Command `az data-box-edge device update`</a>

##### <a name="ExamplesDevicesUpdate">Example</a>
```
az data-box-edge device update --name "testedgedevice" --tags Key1="value1" Key2="value2" --resource-group \
"GroupForEdgeAutomation"
```
##### <a name="ParametersDevicesUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--tags**|dictionary|The tags attached to the Data Box Edge/Gateway resource.|tags|tags|

#### <a name="DevicesDelete">Command `az data-box-edge device delete`</a>

##### <a name="ExamplesDevicesDelete">Example</a>
```
az data-box-edge device delete --name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersDevicesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

#### <a name="DevicesDownloadUpdates">Command `az data-box-edge device download-update`</a>

##### <a name="ExamplesDevicesDownloadUpdates">Example</a>
```
az data-box-edge device download-update --name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersDevicesDownloadUpdates">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

#### <a name="DevicesInstallUpdates">Command `az data-box-edge device install-update`</a>

##### <a name="ExamplesDevicesInstallUpdates">Example</a>
```
az data-box-edge device install-update --name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersDevicesInstallUpdates">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

#### <a name="DevicesScanForUpdates">Command `az data-box-edge device scan-for-update`</a>

##### <a name="ExamplesDevicesScanForUpdates">Example</a>
```
az data-box-edge device scan-for-update --name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersDevicesScanForUpdates">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

#### <a name="DevicesGetUpdateSummary">Command `az data-box-edge device show-update-summary`</a>

##### <a name="ExamplesDevicesGetUpdateSummary">Example</a>
```
az data-box-edge device show-update-summary --name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersDevicesGetUpdateSummary">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### group `az data-box-edge order`
#### <a name="OrdersListByDataBoxEdgeDevice">Command `az data-box-edge order list`</a>

##### <a name="ExamplesOrdersListByDataBoxEdgeDevice">Example</a>
```
az data-box-edge order list --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersOrdersListByDataBoxEdgeDevice">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

#### <a name="OrdersGet">Command `az data-box-edge order show`</a>

##### <a name="ExamplesOrdersGet">Example</a>
```
az data-box-edge order show --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersOrdersGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

#### <a name="OrdersCreateOrUpdate#Create">Command `az data-box-edge order create`</a>

##### <a name="ExamplesOrdersCreateOrUpdate#Create">Example</a>
```
az data-box-edge order create --device-name "testedgedevice" --company-name "Microsoft" --contact-person "John \
Mcclane" --email-list "john@microsoft.com" --phone "(800) 426-9400" --address-line1 "Microsoft Corporation" \
--address-line2 "One Microsoft Way" --address-line3 "Redmond" --city "WA" --country "USA" --postal-code "98052" \
--state "WA" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersOrdersCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The order details of a device.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--current-status-status**|choice|Status of the order as per the allowed status types.|status|status|
|**--current-status-comments**|string|Comments related to this status change.|comments|comments|
|**--shipping-address-address-line1**|string|The address line1.|address_line1|addressLine1|
|**--shipping-address-address-line2**|string|The address line2.|address_line2|addressLine2|
|**--shipping-address-address-line3**|string|The address line3.|address_line3|addressLine3|
|**--shipping-address-postal-code**|string|The postal code.|postal_code|postalCode|
|**--shipping-address-city**|string|The city name.|city|city|
|**--shipping-address-state**|string|The state name.|state|state|
|**--shipping-address-country**|string|The country name.|country|country|
|**--contact-information-contact-person**|string|The contact person name.|contact_person|contactPerson|
|**--contact-information-company-name**|string|The name of the company.|company_name|companyName|
|**--contact-information-phone**|string|The phone number.|phone|phone|
|**--contact-information-email-list**|array|The email list.|email_list|emailList|

#### <a name="OrdersCreateOrUpdate#Update">Command `az data-box-edge order update`</a>

##### <a name="ParametersOrdersCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The order details of a device.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--current-status-status**|choice|Status of the order as per the allowed status types.|status|status|
|**--current-status-comments**|string|Comments related to this status change.|comments|comments|
|**--shipping-address-address-line1**|string|The address line1.|address_line1|addressLine1|
|**--shipping-address-address-line2**|string|The address line2.|address_line2|addressLine2|
|**--shipping-address-address-line3**|string|The address line3.|address_line3|addressLine3|
|**--shipping-address-postal-code**|string|The postal code.|postal_code|postalCode|
|**--shipping-address-city**|string|The city name.|city|city|
|**--shipping-address-state**|string|The state name.|state|state|
|**--shipping-address-country**|string|The country name.|country|country|
|**--contact-information-contact-person**|string|The contact person name.|contact_person|contactPerson|
|**--contact-information-company-name**|string|The name of the company.|company_name|companyName|
|**--contact-information-phone**|string|The phone number.|phone|phone|
|**--contact-information-email-list**|array|The email list.|email_list|emailList|

#### <a name="OrdersDelete">Command `az data-box-edge order delete`</a>

##### <a name="ExamplesOrdersDelete">Example</a>
```
az data-box-edge order delete --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### <a name="ParametersOrdersDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--device-name**|string|The device name.|device_name|deviceName|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
