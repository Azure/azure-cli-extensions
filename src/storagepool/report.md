# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az storagepool|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az storagepool` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az storagepool disk-pool|DiskPools|[commands](#CommandsInDiskPools)|
|az storagepool iscsi-target|IscsiTargets|[commands](#CommandsInIscsiTargets)|

## COMMANDS
### <a name="CommandsInDiskPools">Commands in `az storagepool disk-pool` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az storagepool disk-pool list](#DiskPoolsListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersDiskPoolsListByResourceGroup)|[Example](#ExamplesDiskPoolsListByResourceGroup)|
|[az storagepool disk-pool list](#DiskPoolsListBySubscription)|ListBySubscription|[Parameters](#ParametersDiskPoolsListBySubscription)|[Example](#ExamplesDiskPoolsListBySubscription)|
|[az storagepool disk-pool show](#DiskPoolsGet)|Get|[Parameters](#ParametersDiskPoolsGet)|[Example](#ExamplesDiskPoolsGet)|
|[az storagepool disk-pool create](#DiskPoolsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersDiskPoolsCreateOrUpdate#Create)|[Example](#ExamplesDiskPoolsCreateOrUpdate#Create)|
|[az storagepool disk-pool update](#DiskPoolsUpdate)|Update|[Parameters](#ParametersDiskPoolsUpdate)|[Example](#ExamplesDiskPoolsUpdate)|
|[az storagepool disk-pool delete](#DiskPoolsDelete)|Delete|[Parameters](#ParametersDiskPoolsDelete)|[Example](#ExamplesDiskPoolsDelete)|

### <a name="CommandsInIscsiTargets">Commands in `az storagepool iscsi-target` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az storagepool iscsi-target list](#IscsiTargetsListByDiskPool)|ListByDiskPool|[Parameters](#ParametersIscsiTargetsListByDiskPool)|[Example](#ExamplesIscsiTargetsListByDiskPool)|
|[az storagepool iscsi-target show](#IscsiTargetsGet)|Get|[Parameters](#ParametersIscsiTargetsGet)|[Example](#ExamplesIscsiTargetsGet)|
|[az storagepool iscsi-target create](#IscsiTargetsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersIscsiTargetsCreateOrUpdate#Create)|[Example](#ExamplesIscsiTargetsCreateOrUpdate#Create)|
|[az storagepool iscsi-target update](#IscsiTargetsCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersIscsiTargetsCreateOrUpdate#Update)|Not Found|
|[az storagepool iscsi-target delete](#IscsiTargetsDelete)|Delete|[Parameters](#ParametersIscsiTargetsDelete)|[Example](#ExamplesIscsiTargetsDelete)|


## COMMAND DETAILS

### group `az storagepool disk-pool`
#### <a name="DiskPoolsListByResourceGroup">Command `az storagepool disk-pool list`</a>

##### <a name="ExamplesDiskPoolsListByResourceGroup">Example</a>
```
az storagepool disk-pool list --resource-group "myResourceGroup"
```
##### <a name="ParametersDiskPoolsListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="DiskPoolsListBySubscription">Command `az storagepool disk-pool list`</a>

##### <a name="ExamplesDiskPoolsListBySubscription">Example</a>
```
az storagepool disk-pool list
```
##### <a name="ParametersDiskPoolsListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="DiskPoolsGet">Command `az storagepool disk-pool show`</a>

##### <a name="ExamplesDiskPoolsGet">Example</a>
```
az storagepool disk-pool show --name "myDiskPool" --resource-group "myResourceGroup"
```
##### <a name="ParametersDiskPoolsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--disk-pool-name**|string|The name of the Disk Pool.|disk_pool_name|diskPoolName|

#### <a name="DiskPoolsCreateOrUpdate#Create">Command `az storagepool disk-pool create`</a>

##### <a name="ExamplesDiskPoolsCreateOrUpdate#Create">Example</a>
```
az storagepool disk-pool create --name "myDiskPool" --location "westus" --availability-zones "1" --disks \
id="/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/myResourceGroup/providers/Microsoft.Compute/disk\
s/vm-name_DataDisk_0" --disks id="/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/myResourceGroup/pr\
oviders/Microsoft.Compute/disks/vm-name_DataDisk_1" --subnet-id "/subscriptions/00000000-0000-0000-0000-000000000000/re\
sourceGroups/myResourceGroup/providers/Microsoft.Network/virtualNetworks/myvnet/subnets/mysubnet" --sku \
name="Standard_ABC" --tags key="value" --resource-group "myResourceGroup"
```
##### <a name="ParametersDiskPoolsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--disk-pool-name**|string|The name of the Disk Pool.|disk_pool_name|diskPoolName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--sku**|object|Sku description.|sku|sku|
|**--availability-zones**|array|Logical zone for DiskPool resource.|availability_zones|availabilityZones|
|**--disks**|array|List of Azure managed disks to attach to a DiskPool|disks|disks|
|**--subnet-id**|string|Azure resource id of the subnet for the DiskPool|subnet_id|subnetId|

#### <a name="DiskPoolsUpdate">Command `az storagepool disk-pool update`</a>

##### <a name="ExamplesDiskPoolsUpdate">Example</a>
```
az storagepool disk-pool update --name "myDiskPool" --location "westus" --availability-zones "1" --disks \
id="/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/myResourceGroup/providers/Microsoft.Compute/disk\
s/vm-name_DataDisk_0" --disks id="/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/myResourceGroup/pr\
oviders/Microsoft.Compute/disks/vm-name_DataDisk_1" --subnet-id "/subscriptions/00000000-0000-0000-0000-000000000000/re\
sourceGroups/myResourceGroup/providers/Microsoft.Network/virtualNetworks/myvnet/subnets/mysubnet" --tags key="value" \
--resource-group "myResourceGroup"
```
##### <a name="ParametersDiskPoolsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--disk-pool-name**|string|The name of the Disk Pool.|disk_pool_name|diskPoolName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--sku**|object|Sku description.|sku|sku|
|**--availability-zones**|array|Logical zone for DiskPool resource.|availability_zones|availabilityZones|
|**--disks**|array|List of Azure managed disks to attach to a DiskPool|disks|disks|
|**--subnet-id**|string|Azure resource id of the subnet for the DiskPool|subnet_id|subnetId|

#### <a name="DiskPoolsDelete">Command `az storagepool disk-pool delete`</a>

##### <a name="ExamplesDiskPoolsDelete">Example</a>
```
az storagepool disk-pool delete --name "myDiskPool" --resource-group "myResourceGroup"
```
##### <a name="ParametersDiskPoolsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--disk-pool-name**|string|The name of the Disk Pool.|disk_pool_name|diskPoolName|

### group `az storagepool iscsi-target`
#### <a name="IscsiTargetsListByDiskPool">Command `az storagepool iscsi-target list`</a>

##### <a name="ExamplesIscsiTargetsListByDiskPool">Example</a>
```
az storagepool iscsi-target list --disk-pool-name "myDiskPool" --resource-group "myResourceGroup"
```
##### <a name="ParametersIscsiTargetsListByDiskPool">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--disk-pool-name**|string|The name of the Disk Pool.|disk_pool_name|diskPoolName|

#### <a name="IscsiTargetsGet">Command `az storagepool iscsi-target show`</a>

##### <a name="ExamplesIscsiTargetsGet">Example</a>
```
az storagepool iscsi-target show --disk-pool-name "myDiskPool" --name "myIscsiTarget" --resource-group \
"myResourceGroup"
```
##### <a name="ParametersIscsiTargetsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--disk-pool-name**|string|The name of the Disk Pool.|disk_pool_name|diskPoolName|
|**--iscsi-target-name**|string|The name of the iSCSI target.|iscsi_target_name|iscsiTargetName|

#### <a name="IscsiTargetsCreateOrUpdate#Create">Command `az storagepool iscsi-target create`</a>

##### <a name="ExamplesIscsiTargetsCreateOrUpdate#Create">Example</a>
```
az storagepool iscsi-target create --disk-pool-name "myDiskPool" --name "myIscsiTarget" --target-iqn \
"iqn.2005-03.org.iscsi:server1" --tpgs "[{\\"acls\\":[{\\"credentials\\":{\\"password\\":\\"some_pa$$word\\",\\"usernam\
e\\":\\"some_username\\"},\\"initiatorIqn\\":\\"iqn.2005-03.org.iscsi:client\\",\\"mappedLuns\\":[\\"lun0\\"]}],\\"attr\
ibutes\\":{\\"authentication\\":true,\\"prodModeWriteProtect\\":false},\\"luns\\":[{\\"name\\":\\"lun0\\",\\"managedDis\
kAzureResourceId\\":\\"/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/myResourceGroup/providers/Mic\
rosoft.Compute/disks/vm-name_DataDisk_1\\"}]}]" --resource-group "myResourceGroup"
```
##### <a name="ParametersIscsiTargetsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--disk-pool-name**|string|The name of the Disk Pool.|disk_pool_name|diskPoolName|
|**--iscsi-target-name**|string|The name of the iSCSI target.|iscsi_target_name|iscsiTargetName|
|**--tpgs**|array|list of iSCSI target portal groups|tpgs|tpgs|
|**--target-iqn**|string|iSCSI target iqn (iSCSI Qualified Name); example: iqn.2005-03.org.iscsi:server|target_iqn|targetIqn|

#### <a name="IscsiTargetsCreateOrUpdate#Update">Command `az storagepool iscsi-target update`</a>

##### <a name="ParametersIscsiTargetsCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--disk-pool-name**|string|The name of the Disk Pool.|disk_pool_name|diskPoolName|
|**--iscsi-target-name**|string|The name of the iSCSI target.|iscsi_target_name|iscsiTargetName|
|**--tpgs**|array|list of iSCSI target portal groups|tpgs|tpgs|
|**--target-iqn**|string|iSCSI target iqn (iSCSI Qualified Name); example: iqn.2005-03.org.iscsi:server|target_iqn|targetIqn|

#### <a name="IscsiTargetsDelete">Command `az storagepool iscsi-target delete`</a>

##### <a name="ExamplesIscsiTargetsDelete">Example</a>
```
az storagepool iscsi-target delete --disk-pool-name "myDiskPool" --name "myIscsiTarget" --resource-group \
"myResourceGroup"
```
##### <a name="ParametersIscsiTargetsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--disk-pool-name**|string|The name of the Disk Pool.|disk_pool_name|diskPoolName|
|**--iscsi-target-name**|string|The name of the iSCSI target.|iscsi_target_name|iscsiTargetName|
