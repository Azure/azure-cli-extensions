# Azure CLI Module Creation Report

### blockchain blockchain-member create

create a blockchain blockchain-member.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|blockchain blockchain-member|BlockchainMembers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--blockchain-member-name**|string|Blockchain member name.|blockchain_member_name|blockchainMemberName|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--location**|string|The GEO location of the blockchain service.|location|location|
|**--tags**|dictionary|Tags of the service which is a list of key value pairs that describes the resource.|tags|tags|
|**--sku**|object|Gets or sets the blockchain member Sku.|sku|sku|
|**--protocol**|choice|Gets or sets the blockchain protocol.|protocol|protocol|
|**--validator-nodes-sku**|object|Gets or sets the blockchain validator nodes Sku.|validator_nodes_sku|validatorNodesSku|
|**--password**|string|Sets the basic auth password of the blockchain member.|password|password|
|**--consortium**|string|Gets or sets the consortium for the blockchain member.|consortium|consortium|
|**--consortium-management-account-password**|string|Sets the managed consortium management account password.|consortium_management_account_password|consortiumManagementAccountPassword|
|**--consortium-role**|string|Gets the role of the member in the consortium.|consortium_role|consortiumRole|
|**--consortium-member-display-name**|string|Gets the display name of the member in the consortium.|consortium_member_display_name|consortiumMemberDisplayName|
|**--firewall-rules**|array|Gets or sets firewall rules|firewall_rules|firewallRules|

### blockchain blockchain-member delete

delete a blockchain blockchain-member.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|blockchain blockchain-member|BlockchainMembers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--blockchain-member-name**|string|Blockchain member name|blockchain_member_name|blockchainMemberName|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|

### blockchain blockchain-member list

list a blockchain blockchain-member.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|blockchain blockchain-member|BlockchainMembers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|

### blockchain blockchain-member list-all

list-all a blockchain blockchain-member.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|blockchain blockchain-member|BlockchainMembers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list-all|ListAll|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

### blockchain blockchain-member list-api-key

list-api-key a blockchain blockchain-member.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|blockchain blockchain-member|BlockchainMembers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list-api-key|ListApiKeys|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--blockchain-member-name**|string|Blockchain member name.|blockchain_member_name|blockchainMemberName|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|

### blockchain blockchain-member list-consortium-member

list-consortium-member a blockchain blockchain-member.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|blockchain blockchain-member|BlockchainMembers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list-consortium-member|ListConsortiumMembers|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--blockchain-member-name**|string|Blockchain member name.|blockchain_member_name|blockchainMemberName|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|

### blockchain blockchain-member regenerate-api-key

regenerate-api-key a blockchain blockchain-member.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|blockchain blockchain-member|BlockchainMembers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|regenerate-api-key|RegenerateApiKeys|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--blockchain-member-name**|string|Blockchain member name.|blockchain_member_name|blockchainMemberName|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--key-name**|string|Gets or sets the API key name.|key_name|keyName|
|**--value**|string|Gets or sets the API key value.|value|value|

### blockchain blockchain-member show

show a blockchain blockchain-member.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|blockchain blockchain-member|BlockchainMembers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--blockchain-member-name**|string|Blockchain member name.|blockchain_member_name|blockchainMemberName|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|

### blockchain blockchain-member update

update a blockchain blockchain-member.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|blockchain blockchain-member|BlockchainMembers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--blockchain-member-name**|string|Blockchain member name.|blockchain_member_name|blockchainMemberName|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--tags**|dictionary|Tags of the service which is a list of key value pairs that describes the resource.|tags|tags|
|**--password**|string|Sets the transaction node dns endpoint basic auth password.|password|password|
|**--firewall-rules**|array|Gets or sets the firewall rules.|firewall_rules|firewallRules|
|**--consortium-management-account-password**|string|Sets the managed consortium management account password.|consortium_management_account_password|consortiumManagementAccountPassword|

### blockchain blockchain-member-operation-result show

show a blockchain blockchain-member-operation-result.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|blockchain blockchain-member-operation-result|BlockchainMemberOperationResults|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location-name**|string|Location name.|location_name|locationName|
|**--operation-id**|string|Operation Id.|operation_id|operationId|

### blockchain consortium list

list a blockchain consortium.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|blockchain consortium|Locations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListConsortiums|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location-name**|string|Location Name.|location_name|locationName|

### blockchain sku list

list a blockchain sku.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|blockchain sku|Skus|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

### blockchain transaction-node create

create a blockchain transaction-node.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|blockchain transaction-node|TransactionNodes|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--blockchain-member-name**|string|Blockchain member name.|blockchain_member_name|blockchainMemberName|
|**--transaction-node-name**|string|Transaction node name.|transaction_node_name|transactionNodeName|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--location**|string|Gets or sets the transaction node location.|location|location|
|**--password**|string|Sets the transaction node dns endpoint basic auth password.|password|password|
|**--firewall-rules**|array|Gets or sets the firewall rules.|firewall_rules|firewallRules|

### blockchain transaction-node delete

delete a blockchain transaction-node.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|blockchain transaction-node|TransactionNodes|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--blockchain-member-name**|string|Blockchain member name.|blockchain_member_name|blockchainMemberName|
|**--transaction-node-name**|string|Transaction node name.|transaction_node_name|transactionNodeName|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|

### blockchain transaction-node list

list a blockchain transaction-node.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|blockchain transaction-node|TransactionNodes|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--blockchain-member-name**|string|Blockchain member name.|blockchain_member_name|blockchainMemberName|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|

### blockchain transaction-node list-api-key

list-api-key a blockchain transaction-node.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|blockchain transaction-node|TransactionNodes|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list-api-key|ListApiKeys|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--blockchain-member-name**|string|Blockchain member name.|blockchain_member_name|blockchainMemberName|
|**--transaction-node-name**|string|Transaction node name.|transaction_node_name|transactionNodeName|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|

### blockchain transaction-node regenerate-api-key

regenerate-api-key a blockchain transaction-node.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|blockchain transaction-node|TransactionNodes|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|regenerate-api-key|RegenerateApiKeys|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--blockchain-member-name**|string|Blockchain member name.|blockchain_member_name|blockchainMemberName|
|**--transaction-node-name**|string|Transaction node name.|transaction_node_name|transactionNodeName|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--key-name**|string|Gets or sets the API key name.|key_name|keyName|
|**--value**|string|Gets or sets the API key value.|value|value|

### blockchain transaction-node show

show a blockchain transaction-node.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|blockchain transaction-node|TransactionNodes|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--blockchain-member-name**|string|Blockchain member name.|blockchain_member_name|blockchainMemberName|
|**--transaction-node-name**|string|Transaction node name.|transaction_node_name|transactionNodeName|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|

### blockchain transaction-node update

update a blockchain transaction-node.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|blockchain transaction-node|TransactionNodes|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--blockchain-member-name**|string|Blockchain member name.|blockchain_member_name|blockchainMemberName|
|**--transaction-node-name**|string|Transaction node name.|transaction_node_name|transactionNodeName|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--password**|string|Sets the transaction node dns endpoint basic auth password.|password|password|
|**--firewall-rules**|array|Gets or sets the firewall rules.|firewall_rules|firewallRules|
