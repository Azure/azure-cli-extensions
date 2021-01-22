# Azure CLI Module Creation Report

### swiftlet virtual-machine create

create a swiftlet virtual-machine.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|swiftlet virtual-machine|VirtualMachines|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user’s subscription ID.|resource_group_name|resourceGroupName|
|**--vm-name**|string|The name of the virtual machine.|vm_name|vmName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--swiftlet-bundle-sku**|string|Specifies the Swiftlet bundle of this virtual machine (which specifies the selected tier of memory, processing, and storage).|swiftlet_bundle_sku|swiftletBundleSku|
|**--swiftlet-image-id**|string|The image ID to use. The image "platform" must match the "supportedImagePlatform" of the specified swiftletBundleSku.|swiftlet_image_id|swiftletImageId|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--username**|string|The username for connecting the the virtual machine.|username|username|
|**--ssh-public-key**|string|The SSH public key used to connect to this virtual machine. Only supported on Linux images. If specified on a Windows image, an error will be returned.|ssh_public_key|sshPublicKey|
|**--password**|string|The password for connecting to this Swiftlet. If the image platform type is "linux", this is optional if sshPublicKey is set. If the image platform type is "windows", this is required.|password|password|
|**--ports**|array|The ports on which inbound traffic will be allowed.|ports|ports|
|**--startup-script**|string|An inline script that will run upon startup of the virtual machine.|startup_script|startupScript|

### swiftlet virtual-machine delete

delete a swiftlet virtual-machine.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|swiftlet virtual-machine|VirtualMachines|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user’s subscription ID.|resource_group_name|resourceGroupName|
|**--vm-name**|string|The name of the virtual machine.|vm_name|vmName|

### swiftlet virtual-machine list

list a swiftlet virtual-machine.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|swiftlet virtual-machine|VirtualMachines|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByResourceGroup|
|list|ListBySubscription|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user’s subscription ID.|resource_group_name|resourceGroupName|

### swiftlet virtual-machine list-bundle

list-bundle a swiftlet virtual-machine.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|swiftlet virtual-machine|VirtualMachines|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list-bundle|ListBundles|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location**|string|The name of a supported Azure region.|location|location|

### swiftlet virtual-machine list-image

list-image a swiftlet virtual-machine.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|swiftlet virtual-machine|VirtualMachines|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list-image|ListImages|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location**|string|The name of a supported Azure region.|location|location|

### swiftlet virtual-machine show

show a swiftlet virtual-machine.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|swiftlet virtual-machine|VirtualMachines|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user’s subscription ID.|resource_group_name|resourceGroupName|
|**--vm-name**|string|The name of the virtual machine.|vm_name|vmName|

### swiftlet virtual-machine start

start a swiftlet virtual-machine.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|swiftlet virtual-machine|VirtualMachines|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|start|Start|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--vm-name**|string|The name of the virtual machine.|vm_name|vmName|
|**--resource-group-name**|string|The name of the resource group within the user’s subscription ID.|resource_group_name|resourceGroupName|

### swiftlet virtual-machine stop

stop a swiftlet virtual-machine.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|swiftlet virtual-machine|VirtualMachines|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|stop|Stop|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--vm-name**|string|The name of the virtual machine.|vm_name|vmName|
|**--resource-group-name**|string|The name of the resource group within the user’s subscription ID.|resource_group_name|resourceGroupName|

### swiftlet virtual-machine update

update a swiftlet virtual-machine.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|swiftlet virtual-machine|VirtualMachines|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user’s subscription ID.|resource_group_name|resourceGroupName|
|**--vm-name**|string|The name of the virtual machine.|vm_name|vmName|
|**--tags**|dictionary|Resource tags|tags|tags|
|**--ports**|array|Specifies the list of ports to be opened.|ports|ports|
