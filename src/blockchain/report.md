# Azure CLI Module Creation Report

### blockchain blockchain-member create

create a blockchain blockchain-member.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--blockchain-member-name**|string|Blockchain member name.|blockchain_member_name|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|
|**--location**|string|The GEO location of the blockchain service.|location|
|**--tags**|dictionary|Tags of the service which is a list of key value pairs that describes the resource.|tags|
|**--sku**|object|Gets or sets the blockchain member Sku.|sku|
|**--protocol**|choice|Gets or sets the blockchain protocol.|protocol|
|**--validator-nodes-sku**|object|Gets or sets the blockchain validator nodes Sku.|validator_nodes_sku|
|**--password**|string|Sets the basic auth password of the blockchain member.|password|
|**--consortium**|string|Gets or sets the consortium for the blockchain member.|consortium|
|**--consortium-management-account-password**|string|Sets the managed consortium management account password.|consortium_management_account_password|
|**--consortium-role**|string|Gets the role of the member in the consortium.|consortium_role|
|**--consortium-member-display-name**|string|Gets the display name of the member in the consortium.|consortium_member_display_name|
|**--firewall-rules**|array|Gets or sets firewall rules|firewall_rules|
### blockchain blockchain-member delete

delete a blockchain blockchain-member.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--blockchain-member-name**|string|Blockchain member name|blockchain_member_name|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|
### blockchain blockchain-member list

list a blockchain blockchain-member.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|
### blockchain blockchain-member list-all

list-all a blockchain blockchain-member.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
### blockchain blockchain-member list-api-key

list-api-key a blockchain blockchain-member.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--blockchain-member-name**|string|Blockchain member name.|blockchain_member_name|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|
### blockchain blockchain-member list-consortium-member

list-consortium-member a blockchain blockchain-member.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--blockchain-member-name**|string|Blockchain member name.|blockchain_member_name|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|
### blockchain blockchain-member regenerate-api-key

regenerate-api-key a blockchain blockchain-member.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--blockchain-member-name**|string|Blockchain member name.|blockchain_member_name|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|
|**--key-name**|string|Gets or sets the API key name.|key_name|
|**--value**|string|Gets or sets the API key value.|value|
### blockchain blockchain-member show

show a blockchain blockchain-member.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--blockchain-member-name**|string|Blockchain member name.|blockchain_member_name|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|
### blockchain blockchain-member update

update a blockchain blockchain-member.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--blockchain-member-name**|string|Blockchain member name.|blockchain_member_name|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|
|**--tags**|dictionary|Tags of the service which is a list of key value pairs that describes the resource.|tags|
|**--password**|string|Sets the transaction node dns endpoint basic auth password.|password|
|**--firewall-rules**|array|Gets or sets the firewall rules.|firewall_rules|
|**--consortium-management-account-password**|string|Sets the managed consortium management account password.|consortium_management_account_password|
### blockchain blockchain-member-operation-result show

show a blockchain blockchain-member-operation-result.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--location-name**|string|Location name.|location_name|
|**--operation-id**|string|Operation Id.|operation_id|
### blockchain consortium list

list a blockchain consortium.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--location-name**|string|Location Name.|location_name|
### blockchain sku list

list a blockchain sku.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
### blockchain transaction-node create

create a blockchain transaction-node.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--blockchain-member-name**|string|Blockchain member name.|blockchain_member_name|
|**--transaction-node-name**|string|Transaction node name.|transaction_node_name|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|
|**--location**|string|Gets or sets the transaction node location.|location|
|**--password**|string|Sets the transaction node dns endpoint basic auth password.|password|
|**--firewall-rules**|array|Gets or sets the firewall rules.|firewall_rules|
### blockchain transaction-node delete

delete a blockchain transaction-node.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--blockchain-member-name**|string|Blockchain member name.|blockchain_member_name|
|**--transaction-node-name**|string|Transaction node name.|transaction_node_name|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|
### blockchain transaction-node list

list a blockchain transaction-node.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--blockchain-member-name**|string|Blockchain member name.|blockchain_member_name|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|
### blockchain transaction-node list-api-key

list-api-key a blockchain transaction-node.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--blockchain-member-name**|string|Blockchain member name.|blockchain_member_name|
|**--transaction-node-name**|string|Transaction node name.|transaction_node_name|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|
### blockchain transaction-node regenerate-api-key

regenerate-api-key a blockchain transaction-node.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--blockchain-member-name**|string|Blockchain member name.|blockchain_member_name|
|**--transaction-node-name**|string|Transaction node name.|transaction_node_name|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|
|**--key-name**|string|Gets or sets the API key name.|key_name|
|**--value**|string|Gets or sets the API key value.|value|
### blockchain transaction-node show

show a blockchain transaction-node.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--blockchain-member-name**|string|Blockchain member name.|blockchain_member_name|
|**--transaction-node-name**|string|Transaction node name.|transaction_node_name|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|
### blockchain transaction-node update

update a blockchain transaction-node.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--blockchain-member-name**|string|Blockchain member name.|blockchain_member_name|
|**--transaction-node-name**|string|Transaction node name.|transaction_node_name|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|
|**--password**|string|Sets the transaction node dns endpoint basic auth password.|password|
|**--firewall-rules**|array|Gets or sets the firewall rules.|firewall_rules|