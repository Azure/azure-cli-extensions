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
|az disk-pool|DiskPoolZones|[commands](#CommandsInDiskPoolZones)|
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
|[az disk-pool list-outbound-network-dependency-endpoint](#DiskPoolsListOutboundNetworkDependenciesEndpoints)|ListOutboundNetworkDependenciesEndpoints|[Parameters](#ParametersDiskPoolsListOutboundNetworkDependenciesEndpoints)|[Example](#ExamplesDiskPoolsListOutboundNetworkDependenciesEndpoints)|
|[az disk-pool redeploy](#DiskPoolsUpgrade)|Upgrade|[Parameters](#ParametersDiskPoolsUpgrade)|[Example](#ExamplesDiskPoolsUpgrade)|
|[az disk-pool start](#DiskPoolsStart)|Start|[Parameters](#ParametersDiskPoolsStart)|[Example](#ExamplesDiskPoolsStart)|
|[az disk-pool stop](#DiskPoolsDeallocate)|Deallocate|[Parameters](#ParametersDiskPoolsDeallocate)|[Example](#ExamplesDiskPoolsDeallocate)|

### <a name="CommandsInDiskPoolZones">Commands in `az disk-pool` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az disk-pool list-skus](#DiskPoolZonesList)|List|[Parameters](#ParametersDiskPoolZonesList)|[Example](#ExamplesDiskPoolZonesList)|
|[az disk-pool list-zones](#DiskPoolZonesList)|List|[Parameters](#ParametersDiskPoolZonesList)|[Example](#ExamplesDiskPoolZonesList)|

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
|**--disk-pool-name**|string|The name of the Disk Pool.|disk_pool_name|diskPoolName|

#### <a name="DiskPoolsCreateOrUpdate#Create">Command `az disk-pool create`</a>

##### <a name="ExamplesDiskPoolsCreateOrUpdate#Create">Example</a>
```
az disk-pool create --location "westus" --availability-zones "1" --disks "/subscriptions/11111111-1111-1111-1111-111111\
111111/resourceGroups/myResourceGroup/providers/Microsoft.Compute/disks/vm-name_DataDisk_0" --disks \
"/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/myResourceGroup/providers/Microsoft.Compute/disks/v\
m-name_DataDisk_1" --subnet-id "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/prov\
iders/Microsoft.Network/virtualNetworks/myvnet/subnets/mysubnet" --sku name="Basic_V1" tier="Basic" --tags key="value" \
--name "myDiskPool" --resource-group "myResourceGroup"
```
##### <a name="ParametersDiskPoolsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--disk-pool-name**|string|The name of the Disk Pool.|disk_pool_name|diskPoolName|
|**--sku**|object|Determines the SKU of the Disk Pool|sku|sku|
|**--location**|string|The geo-location where the resource lives.|location|location|
|**--subnet-id**|string|Azure Resource ID of a Subnet for the Disk Pool.|subnet_id|subnetId|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--managed-by**|string|Azure resource id. Indicates if this resource is managed by another Azure resource.|managed_by|managedBy|
|**--managed-by-extended**|array|List of Azure resource ids that manage this resource.|managed_by_extended|managedByExtended|
|**--availability-zones**|array|Logical zone for Disk Pool resource; example: ["1"].|availability_zones|availabilityZones|
|**--disks**|array|List of Azure Managed Disks to attach to a Disk Pool.|disks|disks|
|**--additional-capabilities**|array|List of additional capabilities for a Disk Pool.|additional_capabilities|additionalCapabilities|

#### <a name="DiskPoolsUpdate">Command `az disk-pool update`</a>

##### <a name="ExamplesDiskPoolsUpdate">Example</a>
```
az disk-pool update --name "myDiskPool" --disks "/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/myR\
esourceGroup/providers/Microsoft.Compute/disks/vm-name_DataDisk_0" --disks "/subscriptions/11111111-1111-1111-1111-1111\
11111111/resourceGroups/myResourceGroup/providers/Microsoft.Compute/disks/vm-name_DataDisk_1" --sku name="Basic_B1" \
tier="Basic" --tags key="value" --resource-group "myResourceGroup"
```
##### <a name="ParametersDiskPoolsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--disk-pool-name**|string|The name of the Disk Pool.|disk_pool_name|diskPoolName|
|**--managed-by**|string|Azure resource id. Indicates if this resource is managed by another Azure resource.|managed_by|managedBy|
|**--managed-by-extended**|array|List of Azure resource ids that manage this resource.|managed_by_extended|managedByExtended|
|**--sku**|object|Determines the SKU of the Disk Pool|sku|sku|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--disks**|array|List of Azure Managed Disks to attach to a Disk Pool.|disks|disks|

#### <a name="DiskPoolsDelete">Command `az disk-pool delete`</a>

##### <a name="ExamplesDiskPoolsDelete">Example</a>
```
az disk-pool delete --name "myDiskPool" --resource-group "myResourceGroup"
```
##### <a name="ParametersDiskPoolsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--disk-pool-name**|string|The name of the Disk Pool.|disk_pool_name|diskPoolName|

#### <a name="DiskPoolsListOutboundNetworkDependenciesEndpoints">Command `az disk-pool list-outbound-network-dependency-endpoint`</a>

##### <a name="ExamplesDiskPoolsListOutboundNetworkDependenciesEndpoints">Example</a>
```
az disk-pool list-outbound-network-dependency-endpoint --name "SampleAse" --resource-group \
"Sample-WestUSResourceGroup"
```
##### <a name="ParametersDiskPoolsListOutboundNetworkDependenciesEndpoints">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--disk-pool-name**|string|The name of the Disk Pool.|disk_pool_name|diskPoolName|

#### <a name="DiskPoolsUpgrade">Command `az disk-pool redeploy`</a>

##### <a name="ExamplesDiskPoolsUpgrade">Example</a>
```
az disk-pool redeploy --name "myDiskPool" --resource-group "myResourceGroup"
```
##### <a name="ParametersDiskPoolsUpgrade">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--disk-pool-name**|string|The name of the Disk Pool.|disk_pool_name|diskPoolName|

#### <a name="DiskPoolsStart">Command `az disk-pool start`</a>

##### <a name="ExamplesDiskPoolsStart">Example</a>
```
az disk-pool start --name "myDiskPool" --resource-group "myResourceGroup"
```
##### <a name="ParametersDiskPoolsStart">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--disk-pool-name**|string|The name of the Disk Pool.|disk_pool_name|diskPoolName|

#### <a name="DiskPoolsDeallocate">Command `az disk-pool stop`</a>

##### <a name="ExamplesDiskPoolsDeallocate">Example</a>
```
az disk-pool stop --name "myDiskPool" --resource-group "myResourceGroup"
```
##### <a name="ParametersDiskPoolsDeallocate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--disk-pool-name**|string|The name of the Disk Pool.|disk_pool_name|diskPoolName|

### group `az disk-pool`
#### <a name="DiskPoolZonesList">Command `az disk-pool list-skus`</a>

##### <a name="ExamplesDiskPoolZonesList">Example</a>
```
az disk-pool list-skus --location "eastus"
```
##### <a name="ParametersDiskPoolZonesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location**|string|The location of the resource.|location|location|

#### <a name="DiskPoolZonesList">Command `az disk-pool list-zones`</a>

##### <a name="ExamplesDiskPoolZonesList">Example</a>
```
az disk-pool list-zones --location "eastus"
```
##### <a name="ParametersDiskPoolZonesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location**|string|The location of the resource.|location|location|

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
|**--disk-pool-name**|string|The name of the Disk Pool.|disk_pool_name|diskPoolName|

#### <a name="IscsiTargetsGet">Command `az disk-pool iscsi-target show`</a>

##### <a name="ExamplesIscsiTargetsGet">Example</a>
```
az disk-pool iscsi-target show --disk-pool-name "myDiskPool" --name "myIscsiTarget" --resource-group "myResourceGroup"
```
##### <a name="ParametersIscsiTargetsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--disk-pool-name**|string|The name of the Disk Pool.|disk_pool_name|diskPoolName|
|**--iscsi-target-name**|string|The name of the iSCSI Target.|iscsi_target_name|iscsiTargetName|

#### <a name="IscsiTargetsCreateOrUpdate#Create">Command `az disk-pool iscsi-target create`</a>

##### <a name="ExamplesIscsiTargetsCreateOrUpdate#Create">Example</a>
```
az disk-pool iscsi-target create --disk-pool-name "myDiskPool" --acl-mode "Dynamic" --luns name="lun0" \
managed-disk-azure-resource-id="/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/myResourceGroup/prov\
iders/Microsoft.Compute/disks/vm-name_DataDisk_1" --target-iqn "iqn.2005-03.org.iscsi:server1" --name "myIscsiTarget" \
--resource-group "myResourceGroup"
```
##### <a name="ParametersIscsiTargetsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--disk-pool-name**|string|The name of the Disk Pool.|disk_pool_name|diskPoolName|
|**--iscsi-target-name**|string|The name of the iSCSI Target.|iscsi_target_name|iscsiTargetName|
|**--acl-mode**|choice|Mode for Target connectivity.|acl_mode|aclMode|
|**--managed-by**|string|Azure resource id. Indicates if this resource is managed by another Azure resource.|managed_by|managedBy|
|**--managed-by-extended**|array|List of Azure resource ids that manage this resource.|managed_by_extended|managedByExtended|
|**--target-iqn**|string|iSCSI Target IQN (iSCSI Qualified Name); example: "iqn.2005-03.org.iscsi:server".|target_iqn|targetIqn|
|**--static-acls**|array|Access Control List (ACL) for an iSCSI Target; defines LUN masking policy|static_acls|staticAcls|
|**--luns**|array|List of LUNs to be exposed through iSCSI Target.|luns|luns|

#### <a name="IscsiTargetsUpdate">Command `az disk-pool iscsi-target update`</a>

##### <a name="ExamplesIscsiTargetsUpdate">Example</a>
```
az disk-pool iscsi-target update --disk-pool-name "myDiskPool" --name "myIscsiTarget" --luns name="lun0" \
managed-disk-azure-resource-id="/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/myResourceGroup/prov\
iders/Microsoft.Compute/disks/vm-name_DataDisk_1" --static-acls initiator-iqn="iqn.2005-03.org.iscsi:client" \
mapped-luns="lun0" --resource-group "myResourceGroup"
```
##### <a name="ParametersIscsiTargetsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--disk-pool-name**|string|The name of the Disk Pool.|disk_pool_name|diskPoolName|
|**--iscsi-target-name**|string|The name of the iSCSI Target.|iscsi_target_name|iscsiTargetName|
|**--managed-by**|string|Azure resource id. Indicates if this resource is managed by another Azure resource.|managed_by|managedBy|
|**--managed-by-extended**|array|List of Azure resource ids that manage this resource.|managed_by_extended|managedByExtended|
|**--static-acls**|array|Access Control List (ACL) for an iSCSI Target; defines LUN masking policy|static_acls|staticAcls|
|**--luns**|array|List of LUNs to be exposed through iSCSI Target.|luns|luns|

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
|**--disk-pool-name**|string|The name of the Disk Pool.|disk_pool_name|diskPoolName|
|**--iscsi-target-name**|string|The name of the iSCSI Target.|iscsi_target_name|iscsiTargetName|
