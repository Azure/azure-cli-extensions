# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az diskpool|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az diskpool` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az disk-pool|DiskPools|[commands](#CommandsInDiskPools)|
|az disk-pool iscsi-target|IscsiTargets|[commands](#CommandsInIscsiTargets)|

## COMMANDS
### <a name="CommandsInDiskPools">Commands in `az disk-pool` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az disk-pool list](#DiskPoolsListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersDiskPoolsListByResourceGroup)|[Example](#ExamplesDiskPoolsListByResourceGroup)|
|[az disk-pool list](#DiskPoolsListBySubscription)|ListBySubscription|[Parameters](#ParametersDiskPoolsListBySubscription)|[Example](#ExamplesDiskPoolsListBySubscription)|
|[az disk-pool show](#DiskPoolsGet)|Get|[Parameters](#ParametersDiskPoolsGet)|[Example](#ExamplesDiskPoolsGet)|
|[az disk-pool create](#DiskPoolsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersDiskPoolsCreateOrUpdate#Create)|[Example](#ExamplesDiskPoolsCreateOrUpdate#Create)|
|[az disk-pool update](#DiskPoolsUpdate)|Update|[Parameters](#ParametersDiskPoolsUpdate)|[Example](#ExamplesDiskPoolsUpdate)|
|[az disk-pool delete](#DiskPoolsDelete)|Delete|[Parameters](#ParametersDiskPoolsDelete)|[Example](#ExamplesDiskPoolsDelete)|

### <a name="CommandsInIscsiTargets">Commands in `az disk-pool iscsi-target` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az disk-pool iscsi-target list](#IscsiTargetsListByDiskPool)|ListByDiskPool|[Parameters](#ParametersIscsiTargetsListByDiskPool)|[Example](#ExamplesIscsiTargetsListByDiskPool)|
|[az disk-pool iscsi-target show](#IscsiTargetsGet)|Get|[Parameters](#ParametersIscsiTargetsGet)|[Example](#ExamplesIscsiTargetsGet)|
|[az disk-pool iscsi-target create](#IscsiTargetsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersIscsiTargetsCreateOrUpdate#Create)|[Example](#ExamplesIscsiTargetsCreateOrUpdate#Create)|
|[az disk-pool iscsi-target update](#IscsiTargetsUpdate)|Update|[Parameters](#ParametersIscsiTargetsUpdate)|[Example](#ExamplesIscsiTargetsUpdate)|
|[az disk-pool iscsi-target delete](#IscsiTargetsDelete)|Delete|[Parameters](#ParametersIscsiTargetsDelete)|[Example](#ExamplesIscsiTargetsDelete)|


## COMMAND DETAILS

### group `az disk-pool`
#### <a name="DiskPoolsListByResourceGroup">Command `az disk-pool list`</a>

##### <a name="ExamplesDiskPoolsListByResourceGroup">Example</a>
```
az disk-pool list --resource-group "myResourceGroup"
```
##### <a name="ParametersDiskPoolsListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="DiskPoolsListBySubscription">Command `az disk-pool list`</a>

##### <a name="ExamplesDiskPoolsListBySubscription">Example</a>
```
az disk-pool list
```
##### <a name="ParametersDiskPoolsListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="DiskPoolsGet">Command `az disk-pool show`</a>

##### <a name="ExamplesDiskPoolsGet">Example</a>
```
az disk-pool show --name "myDiskPool" --resource-group "myResourceGroup"
```
##### <a name="ParametersDiskPoolsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--disk-pool-name**|string|The name of the Disk pool.|disk_pool_name|diskPoolName|

#### <a name="DiskPoolsCreateOrUpdate#Create">Command `az disk-pool create`</a>

##### <a name="ExamplesDiskPoolsCreateOrUpdate#Create">Example</a>
```
az disk-pool create --location "westus" --availability-zones "1" --disks "/subscriptions/11111111-1111-1111-1111-111111\
111111/resourceGroups/myResourceGroup/providers/Microsoft.Compute/disks/vm-name_DataDisk_0" --disks \
"/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/myResourceGroup/providers/Microsoft.Compute/disks/v\
m-name_DataDisk_1" --subnet-id "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/prov\
iders/Microsoft.Network/virtualNetworks/myvnet/subnets/mysubnet" --tier "Basic" --tags key="value" --name "myDiskPool" \
--resource-group "myResourceGroup"
```
##### <a name="ParametersDiskPoolsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--disk-pool-name**|string|The name of the Disk pool.|disk_pool_name|diskPoolName|
|**--location**|string|The geo-location where the resource lives.|location|location|
|**--availability-zones**|array|Logical zone for Disk pool resource; example: ["1"].|availability_zones|availabilityZones|
|**--subnet-id**|string|Azure Resource ID of a Subnet for the Disk pool.|subnet_id|subnetId|
|**--tier**|choice|Determines the SKU of VM deployed for Disk pool|tier|tier|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--disks**|array|List of Azure Managed Disks to attach to a Disk pool. Can attach 8 disks at most.|disks|disks|
|**--additional-capabilities**|array|List of additional capabilities for a Disk pool.|additional_capabilities|additionalCapabilities|

#### <a name="DiskPoolsUpdate">Command `az disk-pool update`</a>

##### <a name="ExamplesDiskPoolsUpdate">Example</a>
```
az disk-pool update --name "myDiskPool" --disks "/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/myR\
esourceGroup/providers/Microsoft.Compute/disks/vm-name_DataDisk_0" --disks "/subscriptions/11111111-1111-1111-1111-1111\
11111111/resourceGroups/myResourceGroup/providers/Microsoft.Compute/disks/vm-name_DataDisk_1" --tags key="value" \
--resource-group "myResourceGroup"
```
##### <a name="ParametersDiskPoolsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--disk-pool-name**|string|The name of the Disk pool.|disk_pool_name|diskPoolName|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--disks**|array|List of Azure Managed Disks to attach to a Disk pool. Can attach 8 disks at most.|disks|disks|

#### <a name="DiskPoolsDelete">Command `az disk-pool delete`</a>

##### <a name="ExamplesDiskPoolsDelete">Example</a>
```
az disk-pool delete --name "myDiskPool" --resource-group "myResourceGroup"
```
##### <a name="ParametersDiskPoolsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--disk-pool-name**|string|The name of the Disk pool.|disk_pool_name|diskPoolName|

### group `az disk-pool iscsi-target`
#### <a name="IscsiTargetsListByDiskPool">Command `az disk-pool iscsi-target list`</a>

##### <a name="ExamplesIscsiTargetsListByDiskPool">Example</a>
```
az disk-pool iscsi-target list --disk-pool-name "myDiskPool" --resource-group "myResourceGroup"
```
##### <a name="ParametersIscsiTargetsListByDiskPool">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--disk-pool-name**|string|The name of the Disk pool.|disk_pool_name|diskPoolName|

#### <a name="IscsiTargetsGet">Command `az disk-pool iscsi-target show`</a>

##### <a name="ExamplesIscsiTargetsGet">Example</a>
```
az disk-pool iscsi-target show --disk-pool-name "myDiskPool" --name "myIscsiTarget" --resource-group "myResourceGroup"
```
##### <a name="ParametersIscsiTargetsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--disk-pool-name**|string|The name of the Disk pool.|disk_pool_name|diskPoolName|
|**--iscsi-target-name**|string|The name of the iSCSI target.|iscsi_target_name|iscsiTargetName|

#### <a name="IscsiTargetsCreateOrUpdate#Create">Command `az disk-pool iscsi-target create`</a>

##### <a name="ExamplesIscsiTargetsCreateOrUpdate#Create">Example</a>
```
az disk-pool iscsi-target create --disk-pool-name "myDiskPool" --target-iqn "iqn.2005-03.org.iscsi:server1" --tpgs \
"[{\\"acls\\":[{\\"credentials\\":{\\"password\\":\\"some_password\\",\\"username\\":\\"some_username\\"},\\"initiatorI\
qn\\":\\"iqn.2005-03.org.iscsi:client\\",\\"mappedLuns\\":[\\"lun0\\"]}],\\"attributes\\":{\\"authentication\\":true,\\\
"prodModeWriteProtect\\":false},\\"luns\\":[{\\"name\\":\\"lun0\\",\\"managedDiskAzureResourceId\\":\\"/subscriptions/1\
1111111-1111-1111-1111-111111111111/resourceGroups/myResourceGroup/providers/Microsoft.Compute/disks/vm-name_DataDisk_1\
\\"}]}]" --name "myIscsiTarget" --resource-group "myResourceGroup"
```
##### <a name="ParametersIscsiTargetsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--disk-pool-name**|string|The name of the Disk pool.|disk_pool_name|diskPoolName|
|**--iscsi-target-name**|string|The name of the iSCSI target.|iscsi_target_name|iscsiTargetName|
|**--tpgs**|array|List of iSCSI target portal groups. Can have 1 portal group at most.|tpgs|tpgs|
|**--target-iqn**|string|iSCSI target IQN (iSCSI Qualified Name); example: "iqn.2005-03.org.iscsi:server".|target_iqn|targetIqn|

#### <a name="IscsiTargetsUpdate">Command `az disk-pool iscsi-target update`</a>

##### <a name="ExamplesIscsiTargetsUpdate">Example</a>
```
az disk-pool iscsi-target update --disk-pool-name "myDiskPool" --name "myIscsiTarget" --tpgs \
"[{\\"acls\\":[{\\"credentials\\":{\\"password\\":\\"some_password\\",\\"username\\":\\"some_username\\"},\\"initiatorI\
qn\\":\\"iqn.2005-03.org.iscsi:client\\",\\"mappedLuns\\":[\\"lun0\\"]}],\\"luns\\":[{\\"name\\":\\"lun0\\",\\"managedD\
iskAzureResourceId\\":\\"/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/myResourceGroup/providers/M\
icrosoft.Compute/disks/vm-name_DataDisk_1\\"}]}]" --resource-group "myResourceGroup"
```
##### <a name="ParametersIscsiTargetsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--disk-pool-name**|string|The name of the Disk pool.|disk_pool_name|diskPoolName|
|**--iscsi-target-name**|string|The name of the iSCSI target.|iscsi_target_name|iscsiTargetName|
|**--tpgs**|array|List of iSCSI target portal groups. Can have 1 portal group at most.|tpgs|tpgs|

#### <a name="IscsiTargetsDelete">Command `az disk-pool iscsi-target delete`</a>

##### <a name="ExamplesIscsiTargetsDelete">Example</a>
```
az disk-pool iscsi-target delete --disk-pool-name "myDiskPool" --name "myIscsiTarget" --resource-group \
"myResourceGroup"
```
##### <a name="ParametersIscsiTargetsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--disk-pool-name**|string|The name of the Disk pool.|disk_pool_name|diskPoolName|
|**--iscsi-target-name**|string|The name of the iSCSI target.|iscsi_target_name|iscsiTargetName|
