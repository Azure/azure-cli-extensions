# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az blockchain|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az blockchain` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az blockchain blockchain-member|BlockchainMembers|[commands](#CommandsInBlockchainMembers)|
|az blockchain blockchain-member-operation-result|BlockchainMemberOperationResults|[commands](#CommandsInBlockchainMemberOperationResults)|
|az blockchain consortium|Locations|[commands](#CommandsInLocations)|
|az blockchain sku|Skus|[commands](#CommandsInSkus)|
|az blockchain transaction-node|TransactionNodes|[commands](#CommandsInTransactionNodes)|

## COMMANDS
### <a name="CommandsInBlockchainMembers">Commands in `az blockchain blockchain-member` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az blockchain blockchain-member list](#BlockchainMembersList)|List|[Parameters](#ParametersBlockchainMembersList)|[Example](#ExamplesBlockchainMembersList)|
|[az blockchain blockchain-member show](#BlockchainMembersGet)|Get|[Parameters](#ParametersBlockchainMembersGet)|[Example](#ExamplesBlockchainMembersGet)|
|[az blockchain blockchain-member create](#BlockchainMembersCreate)|Create|[Parameters](#ParametersBlockchainMembersCreate)|[Example](#ExamplesBlockchainMembersCreate)|
|[az blockchain blockchain-member update](#BlockchainMembersUpdate)|Update|[Parameters](#ParametersBlockchainMembersUpdate)|[Example](#ExamplesBlockchainMembersUpdate)|
|[az blockchain blockchain-member delete](#BlockchainMembersDelete)|Delete|[Parameters](#ParametersBlockchainMembersDelete)|[Example](#ExamplesBlockchainMembersDelete)|
|[az blockchain blockchain-member list-all](#BlockchainMembersListAll)|ListAll|[Parameters](#ParametersBlockchainMembersListAll)|[Example](#ExamplesBlockchainMembersListAll)|
|[az blockchain blockchain-member list-api-key](#BlockchainMembersListApiKeys)|ListApiKeys|[Parameters](#ParametersBlockchainMembersListApiKeys)|[Example](#ExamplesBlockchainMembersListApiKeys)|
|[az blockchain blockchain-member list-consortium-member](#BlockchainMembersListConsortiumMembers)|ListConsortiumMembers|[Parameters](#ParametersBlockchainMembersListConsortiumMembers)|[Example](#ExamplesBlockchainMembersListConsortiumMembers)|
|[az blockchain blockchain-member regenerate-api-key](#BlockchainMembersRegenerateApiKeys)|RegenerateApiKeys|[Parameters](#ParametersBlockchainMembersRegenerateApiKeys)|[Example](#ExamplesBlockchainMembersRegenerateApiKeys)|

### <a name="CommandsInBlockchainMemberOperationResults">Commands in `az blockchain blockchain-member-operation-result` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az blockchain blockchain-member-operation-result show](#BlockchainMemberOperationResultsGet)|Get|[Parameters](#ParametersBlockchainMemberOperationResultsGet)|[Example](#ExamplesBlockchainMemberOperationResultsGet)|

### <a name="CommandsInLocations">Commands in `az blockchain consortium` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az blockchain consortium list](#LocationsListConsortiums)|ListConsortiums|[Parameters](#ParametersLocationsListConsortiums)|[Example](#ExamplesLocationsListConsortiums)|

### <a name="CommandsInSkus">Commands in `az blockchain sku` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az blockchain sku list](#SkusList)|List|[Parameters](#ParametersSkusList)|[Example](#ExamplesSkusList)|

### <a name="CommandsInTransactionNodes">Commands in `az blockchain transaction-node` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az blockchain transaction-node list](#TransactionNodesList)|List|[Parameters](#ParametersTransactionNodesList)|[Example](#ExamplesTransactionNodesList)|
|[az blockchain transaction-node show](#TransactionNodesGet)|Get|[Parameters](#ParametersTransactionNodesGet)|[Example](#ExamplesTransactionNodesGet)|
|[az blockchain transaction-node create](#TransactionNodesCreate)|Create|[Parameters](#ParametersTransactionNodesCreate)|[Example](#ExamplesTransactionNodesCreate)|
|[az blockchain transaction-node update](#TransactionNodesUpdate)|Update|[Parameters](#ParametersTransactionNodesUpdate)|[Example](#ExamplesTransactionNodesUpdate)|
|[az blockchain transaction-node delete](#TransactionNodesDelete)|Delete|[Parameters](#ParametersTransactionNodesDelete)|[Example](#ExamplesTransactionNodesDelete)|
|[az blockchain transaction-node list-api-key](#TransactionNodesListApiKeys)|ListApiKeys|[Parameters](#ParametersTransactionNodesListApiKeys)|[Example](#ExamplesTransactionNodesListApiKeys)|
|[az blockchain transaction-node regenerate-api-key](#TransactionNodesRegenerateApiKeys)|RegenerateApiKeys|[Parameters](#ParametersTransactionNodesRegenerateApiKeys)|[Example](#ExamplesTransactionNodesRegenerateApiKeys)|


## COMMAND DETAILS

### group `az blockchain blockchain-member`
#### <a name="BlockchainMembersList">Command `az blockchain blockchain-member list`</a>

##### <a name="ExamplesBlockchainMembersList">Example</a>
```
az blockchain blockchain-member list --resource-group "mygroup"
```
##### <a name="ParametersBlockchainMembersList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|

#### <a name="BlockchainMembersGet">Command `az blockchain blockchain-member show`</a>

##### <a name="ExamplesBlockchainMembersGet">Example</a>
```
az blockchain blockchain-member show --name "contosemember1" --resource-group "mygroup"
```
##### <a name="ParametersBlockchainMembersGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--blockchain-member-name**|string|Blockchain member name.|blockchain_member_name|blockchainMemberName|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|

#### <a name="BlockchainMembersCreate">Command `az blockchain blockchain-member create`</a>

##### <a name="ExamplesBlockchainMembersCreate">Example</a>
```
az blockchain blockchain-member create --location "southeastasia" --consortium "ContoseConsortium" \
--consortium-management-account-password "<consortiumManagementAccountPassword>" --password "<password>" --protocol \
"Quorum" --name "contosemember1" --resource-group "mygroup"
```
##### <a name="ParametersBlockchainMembersCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--blockchain-member-name**|string|Blockchain member name.|blockchain_member_name|blockchainMemberName|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--location**|string|The GEO location of the blockchain service.|location|location|
|**--tags**|dictionary|Tags of the service which is a list of key value pairs that describes the resource.|tags|tags|
|**--sku**|object|Gets or sets the blockchain member Sku.|sku|sku|
|**--protocol**|choice|Gets or sets the blockchain protocol.|protocol|protocol|
|**--password**|string|Sets the basic auth password of the blockchain member.|password|password|
|**--consortium**|string|Gets or sets the consortium for the blockchain member.|consortium|consortium|
|**--consortium-management-account-password**|string|Sets the managed consortium management account password.|consortium_management_account_password|consortiumManagementAccountPassword|
|**--consortium-role**|string|Gets the role of the member in the consortium.|consortium_role|consortiumRole|
|**--consortium-member-display-name**|string|Gets the display name of the member in the consortium.|consortium_member_display_name|consortiumMemberDisplayName|
|**--firewall-rules**|array|Gets or sets firewall rules|firewall_rules|firewallRules|
|**--validator-nodes-sku-capacity**|integer|Gets or sets the nodes capacity.|capacity|capacity|

#### <a name="BlockchainMembersUpdate">Command `az blockchain blockchain-member update`</a>

##### <a name="ExamplesBlockchainMembersUpdate">Example</a>
```
az blockchain blockchain-member update --consortium-management-account-password "<consortiumManagementAccountPassword>"\
 --password "<password>" --name "ContoseMember1" --resource-group "mygroup"
```
##### <a name="ParametersBlockchainMembersUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--blockchain-member-name**|string|Blockchain member name.|blockchain_member_name|blockchainMemberName|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--tags**|dictionary|Tags of the service which is a list of key value pairs that describes the resource.|tags|tags|
|**--password**|string|Sets the transaction node dns endpoint basic auth password.|password|password|
|**--firewall-rules**|array|Gets or sets the firewall rules.|firewall_rules|firewallRules|
|**--consortium-management-account-password**|string|Sets the managed consortium management account password.|consortium_management_account_password|consortiumManagementAccountPassword|

#### <a name="BlockchainMembersDelete">Command `az blockchain blockchain-member delete`</a>

##### <a name="ExamplesBlockchainMembersDelete">Example</a>
```
az blockchain blockchain-member delete --name "contosemember1" --resource-group "mygroup"
```
##### <a name="ParametersBlockchainMembersDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--blockchain-member-name**|string|Blockchain member name|blockchain_member_name|blockchainMemberName|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|

#### <a name="BlockchainMembersListAll">Command `az blockchain blockchain-member list-all`</a>

##### <a name="ExamplesBlockchainMembersListAll">Example</a>
```
az blockchain blockchain-member list-all
```
##### <a name="ParametersBlockchainMembersListAll">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="BlockchainMembersListApiKeys">Command `az blockchain blockchain-member list-api-key`</a>

##### <a name="ExamplesBlockchainMembersListApiKeys">Example</a>
```
az blockchain blockchain-member list-api-key --name "contosemember1" --resource-group "mygroup"
```
##### <a name="ParametersBlockchainMembersListApiKeys">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--blockchain-member-name**|string|Blockchain member name.|blockchain_member_name|blockchainMemberName|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|

#### <a name="BlockchainMembersListConsortiumMembers">Command `az blockchain blockchain-member list-consortium-member`</a>

##### <a name="ExamplesBlockchainMembersListConsortiumMembers">Example</a>
```
az blockchain blockchain-member list-consortium-member --name "contosemember1" --resource-group "mygroup"
```
##### <a name="ParametersBlockchainMembersListConsortiumMembers">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--blockchain-member-name**|string|Blockchain member name.|blockchain_member_name|blockchainMemberName|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|

#### <a name="BlockchainMembersRegenerateApiKeys">Command `az blockchain blockchain-member regenerate-api-key`</a>

##### <a name="ExamplesBlockchainMembersRegenerateApiKeys">Example</a>
```
az blockchain blockchain-member regenerate-api-key --key-name "key1" --name "contosemember1" --resource-group \
"mygroup"
```
##### <a name="ParametersBlockchainMembersRegenerateApiKeys">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--blockchain-member-name**|string|Blockchain member name.|blockchain_member_name|blockchainMemberName|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--key-name**|string|Gets or sets the API key name.|key_name|keyName|
|**--value**|string|Gets or sets the API key value.|value|value|

### group `az blockchain blockchain-member-operation-result`
#### <a name="BlockchainMemberOperationResultsGet">Command `az blockchain blockchain-member-operation-result show`</a>

##### <a name="ExamplesBlockchainMemberOperationResultsGet">Example</a>
```
az blockchain blockchain-member-operation-result show --operation-id "12f4b309-01e3-4fcf-bc0b-1cc034ca03f8" \
--location-name "southeastasia"
```
##### <a name="ParametersBlockchainMemberOperationResultsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location-name**|string|Location name.|location_name|locationName|
|**--operation-id**|string|Operation Id.|operation_id|operationId|

### group `az blockchain consortium`
#### <a name="LocationsListConsortiums">Command `az blockchain consortium list`</a>

##### <a name="ExamplesLocationsListConsortiums">Example</a>
```
az blockchain consortium list --name "southeastasia"
```
##### <a name="ParametersLocationsListConsortiums">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location-name**|string|Location Name.|location_name|locationName|

### group `az blockchain sku`
#### <a name="SkusList">Command `az blockchain sku list`</a>

##### <a name="ExamplesSkusList">Example</a>
```
az blockchain sku list
```
##### <a name="ParametersSkusList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
### group `az blockchain transaction-node`
#### <a name="TransactionNodesList">Command `az blockchain transaction-node list`</a>

##### <a name="ExamplesTransactionNodesList">Example</a>
```
az blockchain transaction-node list --blockchain-member-name "contosemember1" --resource-group "mygroup"
```
##### <a name="ParametersTransactionNodesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--blockchain-member-name**|string|Blockchain member name.|blockchain_member_name|blockchainMemberName|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|

#### <a name="TransactionNodesGet">Command `az blockchain transaction-node show`</a>

##### <a name="ExamplesTransactionNodesGet">Example</a>
```
az blockchain transaction-node show --blockchain-member-name "contosemember1" --resource-group "mygroup" --name \
"txnode2"
```
##### <a name="ParametersTransactionNodesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--blockchain-member-name**|string|Blockchain member name.|blockchain_member_name|blockchainMemberName|
|**--transaction-node-name**|string|Transaction node name.|transaction_node_name|transactionNodeName|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|

#### <a name="TransactionNodesCreate">Command `az blockchain transaction-node create`</a>

##### <a name="ExamplesTransactionNodesCreate">Example</a>
```
az blockchain transaction-node create --blockchain-member-name "contosemember1" --resource-group "mygroup" --location \
"southeastasia" --password "<password>" --name "txnode2"
```
##### <a name="ParametersTransactionNodesCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--blockchain-member-name**|string|Blockchain member name.|blockchain_member_name|blockchainMemberName|
|**--transaction-node-name**|string|Transaction node name.|transaction_node_name|transactionNodeName|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--location**|string|Gets or sets the transaction node location.|location|location|
|**--password**|string|Sets the transaction node dns endpoint basic auth password.|password|password|
|**--firewall-rules**|array|Gets or sets the firewall rules.|firewall_rules|firewallRules|

#### <a name="TransactionNodesUpdate">Command `az blockchain transaction-node update`</a>

##### <a name="ExamplesTransactionNodesUpdate">Example</a>
```
az blockchain transaction-node update --blockchain-member-name "contosemember1" --resource-group "mygroup" --password \
"<password>" --name "txnode2"
```
##### <a name="ParametersTransactionNodesUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--blockchain-member-name**|string|Blockchain member name.|blockchain_member_name|blockchainMemberName|
|**--transaction-node-name**|string|Transaction node name.|transaction_node_name|transactionNodeName|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--password**|string|Sets the transaction node dns endpoint basic auth password.|password|password|
|**--firewall-rules**|array|Gets or sets the firewall rules.|firewall_rules|firewallRules|

#### <a name="TransactionNodesDelete">Command `az blockchain transaction-node delete`</a>

##### <a name="ExamplesTransactionNodesDelete">Example</a>
```
az blockchain transaction-node delete --blockchain-member-name "contosemember1" --resource-group "mygroup" --name \
"txNode2"
```
##### <a name="ParametersTransactionNodesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--blockchain-member-name**|string|Blockchain member name.|blockchain_member_name|blockchainMemberName|
|**--transaction-node-name**|string|Transaction node name.|transaction_node_name|transactionNodeName|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|

#### <a name="TransactionNodesListApiKeys">Command `az blockchain transaction-node list-api-key`</a>

##### <a name="ExamplesTransactionNodesListApiKeys">Example</a>
```
az blockchain transaction-node list-api-key --blockchain-member-name "contosemember1" --resource-group "mygroup" \
--name "txnode2"
```
##### <a name="ParametersTransactionNodesListApiKeys">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--blockchain-member-name**|string|Blockchain member name.|blockchain_member_name|blockchainMemberName|
|**--transaction-node-name**|string|Transaction node name.|transaction_node_name|transactionNodeName|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|

#### <a name="TransactionNodesRegenerateApiKeys">Command `az blockchain transaction-node regenerate-api-key`</a>

##### <a name="ExamplesTransactionNodesRegenerateApiKeys">Example</a>
```
az blockchain transaction-node regenerate-api-key --key-name "key1" --blockchain-member-name "contosemember1" \
--resource-group "mygroup" --name "txnode2"
```
##### <a name="ParametersTransactionNodesRegenerateApiKeys">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--blockchain-member-name**|string|Blockchain member name.|blockchain_member_name|blockchainMemberName|
|**--transaction-node-name**|string|Transaction node name.|transaction_node_name|transactionNodeName|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--key-name**|string|Gets or sets the API key name.|key_name|keyName|
|**--value**|string|Gets or sets the API key value.|value|value|
