# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az swiftlet|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az swiftlet` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az swiftlet virtual-machine|VirtualMachines|[commands](#CommandsInVirtualMachines)|
|az swiftlet virtual-machine-image|VirtualMachineImages|[commands](#CommandsInVirtualMachineImages)|
|az swiftlet virtual-machine-bundle|VirtualMachineBundles|[commands](#CommandsInVirtualMachineBundles)|
|az swiftlet virtual-machine-snapshot|VirtualMachineSnapshots|[commands](#CommandsInVirtualMachineSnapshots)|

## COMMANDS
### <a name="CommandsInVirtualMachines">Commands in `az swiftlet virtual-machine` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az swiftlet virtual-machine list](#VirtualMachinesListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersVirtualMachinesListByResourceGroup)|[Example](#ExamplesVirtualMachinesListByResourceGroup)|
|[az swiftlet virtual-machine list](#VirtualMachinesListBySubscription)|ListBySubscription|[Parameters](#ParametersVirtualMachinesListBySubscription)|[Example](#ExamplesVirtualMachinesListBySubscription)|
|[az swiftlet virtual-machine show](#VirtualMachinesGet)|Get|[Parameters](#ParametersVirtualMachinesGet)|[Example](#ExamplesVirtualMachinesGet)|
|[az swiftlet virtual-machine create](#VirtualMachinesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersVirtualMachinesCreateOrUpdate#Create)|[Example](#ExamplesVirtualMachinesCreateOrUpdate#Create)|
|[az swiftlet virtual-machine update](#VirtualMachinesUpdate)|Update|[Parameters](#ParametersVirtualMachinesUpdate)|[Example](#ExamplesVirtualMachinesUpdate)|
|[az swiftlet virtual-machine delete](#VirtualMachinesDelete)|Delete|[Parameters](#ParametersVirtualMachinesDelete)|[Example](#ExamplesVirtualMachinesDelete)|
|[az swiftlet virtual-machine start](#VirtualMachinesStart)|Start|[Parameters](#ParametersVirtualMachinesStart)|[Example](#ExamplesVirtualMachinesStart)|
|[az swiftlet virtual-machine stop](#VirtualMachinesStop)|Stop|[Parameters](#ParametersVirtualMachinesStop)|[Example](#ExamplesVirtualMachinesStop)|

### <a name="CommandsInVirtualMachineBundles">Commands in `az swiftlet virtual-machine-bundle` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az swiftlet virtual-machine-bundle list](#VirtualMachineBundlesList)|List|[Parameters](#ParametersVirtualMachineBundlesList)|[Example](#ExamplesVirtualMachineBundlesList)|
|[az swiftlet virtual-machine-bundle show](#VirtualMachineBundlesGet)|Get|[Parameters](#ParametersVirtualMachineBundlesGet)|[Example](#ExamplesVirtualMachineBundlesGet)|

### <a name="CommandsInVirtualMachineImages">Commands in `az swiftlet virtual-machine-image` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az swiftlet virtual-machine-image list](#VirtualMachineImagesList)|List|[Parameters](#ParametersVirtualMachineImagesList)|[Example](#ExamplesVirtualMachineImagesList)|
|[az swiftlet virtual-machine-image show](#VirtualMachineImagesGet)|Get|[Parameters](#ParametersVirtualMachineImagesGet)|[Example](#ExamplesVirtualMachineImagesGet)|

### <a name="CommandsInVirtualMachineSnapshots">Commands in `az swiftlet virtual-machine-snapshot` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az swiftlet virtual-machine-snapshot list](#VirtualMachineSnapshotsListByVirtualMachine)|ListByVirtualMachine|[Parameters](#ParametersVirtualMachineSnapshotsListByVirtualMachine)|[Example](#ExamplesVirtualMachineSnapshotsListByVirtualMachine)|
|[az swiftlet virtual-machine-snapshot list](#VirtualMachineSnapshotsListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersVirtualMachineSnapshotsListByResourceGroup)|[Example](#ExamplesVirtualMachineSnapshotsListByResourceGroup)|
|[az swiftlet virtual-machine-snapshot list](#VirtualMachineSnapshotsListBySubscription)|ListBySubscription|[Parameters](#ParametersVirtualMachineSnapshotsListBySubscription)|[Example](#ExamplesVirtualMachineSnapshotsListBySubscription)|
|[az swiftlet virtual-machine-snapshot show](#VirtualMachineSnapshotsGet)|Get|[Parameters](#ParametersVirtualMachineSnapshotsGet)|[Example](#ExamplesVirtualMachineSnapshotsGet)|
|[az swiftlet virtual-machine-snapshot create](#VirtualMachineSnapshotsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersVirtualMachineSnapshotsCreateOrUpdate#Create)|[Example](#ExamplesVirtualMachineSnapshotsCreateOrUpdate#Create)|
|[az swiftlet virtual-machine-snapshot update](#VirtualMachineSnapshotsUpdate)|Update|[Parameters](#ParametersVirtualMachineSnapshotsUpdate)|[Example](#ExamplesVirtualMachineSnapshotsUpdate)|
|[az swiftlet virtual-machine-snapshot delete](#VirtualMachineSnapshotsDelete)|Delete|[Parameters](#ParametersVirtualMachineSnapshotsDelete)|[Example](#ExamplesVirtualMachineSnapshotsDelete)|


## COMMAND DETAILS

### group `az swiftlet virtual-machine`
#### <a name="VirtualMachinesListByResourceGroup">Command `az swiftlet virtual-machine list`</a>

##### <a name="ExamplesVirtualMachinesListByResourceGroup">Example</a>
```
az swiftlet virtual-machine list --resource-group "myResourceGroup"
```
##### <a name="ParametersVirtualMachinesListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user’s subscription ID.|resource_group_name|resourceGroupName|

#### <a name="VirtualMachinesListBySubscription">Command `az swiftlet virtual-machine list`</a>

##### <a name="ExamplesVirtualMachinesListBySubscription">Example</a>
```
az swiftlet virtual-machine list
```
##### <a name="ParametersVirtualMachinesListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="VirtualMachinesGet">Command `az swiftlet virtual-machine show`</a>

##### <a name="ExamplesVirtualMachinesGet">Example</a>
```
az swiftlet virtual-machine show --resource-group "myResourceGroup" --vm-name "myVirtualMachine"
```
##### <a name="ParametersVirtualMachinesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user’s subscription ID.|resource_group_name|resourceGroupName|
|**--vm-name**|string|The name of the virtual machine.|vm_name|vmName|

#### <a name="VirtualMachinesCreateOrUpdate#Create">Command `az swiftlet virtual-machine create`</a>

##### <a name="ExamplesVirtualMachinesCreateOrUpdate#Create">Example</a>
```
az swiftlet virtual-machine create --location "westus" --bundle-sku "Windows_1" --ports port-range="3389" protocol="*" \
--snapshot-id "subscription/{subscription-id}/resourceGroups/myResourceGroup/providers/Microsoft.Swiftlet/virtualMachin\
eSnapshots/myVmSnapshot" --tags key1="value1" key2="value2" --resource-group "myResourceGroup" --vm-name \
"myVirtualMachine"
```
##### <a name="ExamplesVirtualMachinesCreateOrUpdate#Create">Example</a>
```
az swiftlet virtual-machine create --location "westus" --bundle-sku "Windows_1" --image-id "windows-2019-datacenter" \
--password "{your-password}," --ports port-range="3389" protocol="*" --startup-script "{inline startup script}" \
--username "SwiftletUser" --tags key1="value1" key2="value2" --resource-group "myResourceGroup" --vm-name \
"myVirtualMachine"
```
##### <a name="ExamplesVirtualMachinesCreateOrUpdate#Create">Example</a>
```
az swiftlet virtual-machine create --location "westus" --bundle-sku "Linux_1" --image-id "ubuntu-18.04-lts" --ports \
port-range="22" protocol="*" --ssh-public-key "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCeClRAk2ipUs/l5voIsDC5q9RI+YSRd1Bv\
d/O+axgY4WiBzG+4FwJWZm/mLLe5DoOdHQwmU2FrKXZSW4w2sYE70KeWnrFViCOX5MTVvJgPE8ClugNl8RWth/tU849DvM9sT7vFgfVSHcAS2yDRyDlueii\
+8nF2ym8XWAPltFVCyLHRsyBp5YPqK8JFYIa1eybKsY3hEAxRCA+/7bq8et+Gj3coOsuRmrehav7rE6N12Pb80I6ofa6SM5XNYq4Xk0iYNx7R3kdz0Jj9Xg\
ZYWjAHjJmT0gTRoOnt6upOuxK7xI/ykWrllgpXrCPu3Ymz+c+ujaqcxDopnAl2lmf69/J1" --startup-script "{inline startup script}" \
--username "SwiftletUser" --tags key1="value1" key2="value2" --resource-group "myResourceGroup" --vm-name \
"myVirtualMachine"
```
##### <a name="ParametersVirtualMachinesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user’s subscription ID.|resource_group_name|resourceGroupName|
|**--vm-name**|string|The name of the virtual machine.|vm_name|vmName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--bundle-sku**|string|Specifies the Swiftlet VM bundle of this virtual machine (which specifies the selected tier of memory, processing, and storage).|bundle_sku|bundleSku|
|**--image-id**|string|The image ID to use. The image "platform" must match the "supportedImagePlatform" of the specified bundleSku.|image_id|imageId|
|**--snapshot-id**|string|The ID of the VM snapshot from which this VM was created.|snapshot_id|snapshotId|
|**--username**|string|The username for connecting the the virtual machine.|username|username|
|**--ssh-public-key**|string|The SSH public key used to connect to this virtual machine. Only supported on Linux images. If specified on a Windows image, an error will be returned.|ssh_public_key|sshPublicKey|
|**--ports**|array|The ports on which inbound traffic will be allowed.|ports|ports|
|**--password**|string|The password for connecting to this Swiftlet. If the image platform type is "linux", this is optional if sshPublicKey is set. If the image platform type is "windows", this is required.|password|password|
|**--startup-script**|string|An inline script that will run upon startup of the virtual machine.|startup_script|startupScript|

#### <a name="VirtualMachinesUpdate">Command `az swiftlet virtual-machine update`</a>

##### <a name="ExamplesVirtualMachinesUpdate">Example</a>
```
az swiftlet virtual-machine update --ports port-range="80" protocol="TCP" --ports port-range="50-60" protocol="UDP" \
--tags key3="value3" --resource-group "myResourceGroup" --vm-name "myVirtualMachine"
```
##### <a name="ParametersVirtualMachinesUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user’s subscription ID.|resource_group_name|resourceGroupName|
|**--vm-name**|string|The name of the virtual machine.|vm_name|vmName|
|**--tags**|dictionary|Resource tags|tags|tags|
|**--ports**|array|The ports on which inbound traffic will be allowed.|ports|ports|

#### <a name="VirtualMachinesDelete">Command `az swiftlet virtual-machine delete`</a>

##### <a name="ExamplesVirtualMachinesDelete">Example</a>
```
az swiftlet virtual-machine delete --resource-group "myResourceGroup" --vm-name "myVirtualMachine"
```
##### <a name="ParametersVirtualMachinesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user’s subscription ID.|resource_group_name|resourceGroupName|
|**--vm-name**|string|The name of the virtual machine.|vm_name|vmName|

#### <a name="VirtualMachinesStart">Command `az swiftlet virtual-machine start`</a>

##### <a name="ExamplesVirtualMachinesStart">Example</a>
```
az swiftlet virtual-machine start --resource-group "myResourceGroup" --vm-name "myVirtualMachine"
```
##### <a name="ParametersVirtualMachinesStart">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--vm-name**|string|The name of the virtual machine.|vm_name|vmName|
|**--resource-group-name**|string|The name of the resource group within the user’s subscription ID.|resource_group_name|resourceGroupName|

#### <a name="VirtualMachinesStop">Command `az swiftlet virtual-machine stop`</a>

##### <a name="ExamplesVirtualMachinesStop">Example</a>
```
az swiftlet virtual-machine stop --resource-group "myResourceGroup" --vm-name "myVirtualMachine"
```
##### <a name="ParametersVirtualMachinesStop">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--vm-name**|string|The name of the virtual machine.|vm_name|vmName|
|**--resource-group-name**|string|The name of the resource group within the user’s subscription ID.|resource_group_name|resourceGroupName|

### group `az swiftlet virtual-machine-bundle`
#### <a name="VirtualMachineBundlesList">Command `az swiftlet virtual-machine-bundle list`</a>

##### <a name="ExamplesVirtualMachineBundlesList">Example</a>
```
az swiftlet virtual-machine-bundle list --location "westus"
```
##### <a name="ParametersVirtualMachineBundlesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location**|string|The name of a supported Azure region.|location|location|

#### <a name="VirtualMachineBundlesGet">Command `az swiftlet virtual-machine-bundle show`</a>

##### <a name="ExamplesVirtualMachineBundlesGet">Example</a>
```
az swiftlet virtual-machine-bundle show --bundle-name "Windows_1" --location "westus"
```
##### <a name="ParametersVirtualMachineBundlesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--bundle-name**|string|The name of the virtual machine bundle.|bundle_name|bundleName|
|**--location**|string|The name of a supported Azure region.|location|location|

### group `az swiftlet virtual-machine-image`
#### <a name="VirtualMachineImagesList">Command `az swiftlet virtual-machine-image list`</a>

##### <a name="ExamplesVirtualMachineImagesList">Example</a>
```
az swiftlet virtual-machine-image list --location "westus"
```
##### <a name="ParametersVirtualMachineImagesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location**|string|The name of a supported Azure region.|location|location|

#### <a name="VirtualMachineImagesGet">Command `az swiftlet virtual-machine-image show`</a>

##### <a name="ExamplesVirtualMachineImagesGet">Example</a>
```
az swiftlet virtual-machine-image show --image-name "windows-2019-datacenter" --location "westus"
```
##### <a name="ParametersVirtualMachineImagesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--image-name**|string|The name of the virtual machine image.|image_name|imageName|
|**--location**|string|The name of a supported Azure region.|location|location|

### group `az swiftlet virtual-machine-snapshot`
#### <a name="VirtualMachineSnapshotsListByVirtualMachine">Command `az swiftlet virtual-machine-snapshot list`</a>

##### <a name="ExamplesVirtualMachineSnapshotsListByVirtualMachine">Example</a>
```
az swiftlet virtual-machine-snapshot list --resource-group "myResourceGroup" --vm-name "myVirtualMachine"
```
##### <a name="ParametersVirtualMachineSnapshotsListByVirtualMachine">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--vm-name**|string|The name of the virtual machine.|vm_name|vmName|
|**--resource-group-name**|string|The name of the resource group within the user’s subscription ID.|resource_group_name|resourceGroupName|

#### <a name="VirtualMachineSnapshotsListByResourceGroup">Command `az swiftlet virtual-machine-snapshot list`</a>

##### <a name="ExamplesVirtualMachineSnapshotsListByResourceGroup">Example</a>
```
az swiftlet virtual-machine-snapshot list --resource-group "myResourceGroup"
```
##### <a name="ParametersVirtualMachineSnapshotsListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="VirtualMachineSnapshotsListBySubscription">Command `az swiftlet virtual-machine-snapshot list`</a>

##### <a name="ExamplesVirtualMachineSnapshotsListBySubscription">Example</a>
```
az swiftlet virtual-machine-snapshot list
```
##### <a name="ParametersVirtualMachineSnapshotsListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="VirtualMachineSnapshotsGet">Command `az swiftlet virtual-machine-snapshot show`</a>

##### <a name="ExamplesVirtualMachineSnapshotsGet">Example</a>
```
az swiftlet virtual-machine-snapshot show --resource-group "myResourceGroup" --snapshot-name "myVmSnapshot"
```
##### <a name="ParametersVirtualMachineSnapshotsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user’s subscription ID.|resource_group_name|resourceGroupName|
|**--snapshot-name**|string|The name of the virtual machine snapshot.|snapshot_name|snapshotName|

#### <a name="VirtualMachineSnapshotsCreateOrUpdate#Create">Command `az swiftlet virtual-machine-snapshot create`</a>

##### <a name="ExamplesVirtualMachineSnapshotsCreateOrUpdate#Create">Example</a>
```
az swiftlet virtual-machine-snapshot create --location "westus" --virtual-machine-id "/subscriptions/{subscription-id}/\
resourceGroups/myResourceGroup/providers/Microsoft.Swiftlet/virtualMachines/myVirtualMachine" --tags key1="value1" \
key2="value2" --resource-group "myResourceGroup" --snapshot-name "myVmSnapshot"
```
##### <a name="ParametersVirtualMachineSnapshotsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user’s subscription ID.|resource_group_name|resourceGroupName|
|**--snapshot-name**|string|The name of the virtual machine snapshot.|snapshot_name|snapshotName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--virtual-machine-id**|string|The ID of the VM from which to create this snapshot.|virtual_machine_id|virtualMachineId|
|**--tags**|dictionary|Resource tags.|tags|tags|

#### <a name="VirtualMachineSnapshotsUpdate">Command `az swiftlet virtual-machine-snapshot update`</a>

##### <a name="ExamplesVirtualMachineSnapshotsUpdate">Example</a>
```
az swiftlet virtual-machine-snapshot update --tags key3="value3" --resource-group "myResourceGroup" --snapshot-name \
"myVmSnapshot"
```
##### <a name="ParametersVirtualMachineSnapshotsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user’s subscription ID.|resource_group_name|resourceGroupName|
|**--snapshot-name**|string|The name of the virtual machine snapshot.|snapshot_name|snapshotName|
|**--tags**|dictionary|Resource tags|tags|tags|

#### <a name="VirtualMachineSnapshotsDelete">Command `az swiftlet virtual-machine-snapshot delete`</a>

##### <a name="ExamplesVirtualMachineSnapshotsDelete">Example</a>
```
az swiftlet virtual-machine-snapshot delete --resource-group "myResourceGroup" --snapshot-name "myVmSnapshot"
```
##### <a name="ParametersVirtualMachineSnapshotsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user’s subscription ID.|resource_group_name|resourceGroupName|
|**--snapshot-name**|string|The name of the virtual machine snapshot.|snapshot_name|snapshotName|
