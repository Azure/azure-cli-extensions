# Azure CLI Module Creation Report

### stack-hci cluster create

create a stack-hci cluster.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--cluster-name**|string|The name of the cluster.|cluster_name|
|**--location**|string|The geo-location where the resource lives|location|
|**--tags**|dictionary|Resource tags.|tags|
|**--aad-client-id**|string|App id of cluster AAD identity.|aad_client_id|
|**--aad-tenant-id**|string|Tenant id of cluster AAD identity.|aad_tenant_id|
### stack-hci cluster delete

delete a stack-hci cluster.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--cluster-name**|string|The name of the cluster.|cluster_name|
### stack-hci cluster list

list a stack-hci cluster.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
### stack-hci cluster show

show a stack-hci cluster.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--cluster-name**|string|The name of the cluster.|cluster_name|
### stack-hci cluster update

update a stack-hci cluster.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--cluster-name**|string|The name of the cluster.|cluster_name|
|**--tags**|dictionary|Resource tags.|tags|