# Azure CLI Module Creation Report

## managednetwork

### managednetwork list

list a managednetwork.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
## managednetwork managed-network-group

### managednetwork managed-network-group create

create a managednetwork managed-network-group.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|The name of the resource group.|resource_group_name|resourceGroupName|
|**--managed-network-name**|str|The name of the Managed Network.|managed_network_name|managedNetworkName|
|**--name**|str|The name of the Managed Network Group.|managed_network_group_name|managedNetworkGroupName|
|--location|str|The geo-location where the resource lives|/location|/location|
|--management-groups|dict|The collection of management groups covered by the Managed Network|//management_groups|//managementGroups|
|--subscriptions|dict|The collection of subscriptions covered by the Managed Network|//subscriptions|//subscriptions|
|--virtual-networks|dict|The collection of virtual nets covered by the Managed Network|//virtual_networks|//virtualNetworks|
|--subnets|dict|The collection of  subnets covered by the Managed Network|//subnets|//subnets|
|--kind|str|Responsibility role under which this Managed Network Group will be created|/kind|/kind|

**Example: ManagementNetworkGroupsPut**

```
managednetwork managed-network-group create --resource-group myResourceGroup
        --managed-network-name myManagedNetwork
        --name myManagedNetworkGroup1
```
### managednetwork managed-network-group update

update a managednetwork managed-network-group.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|The name of the resource group.|resource_group_name|resourceGroupName|
|**--managed-network-name**|str|The name of the Managed Network.|managed_network_name|managedNetworkName|
|**--name**|str|The name of the Managed Network Group.|managed_network_group_name|managedNetworkGroupName|
|--location|str|The geo-location where the resource lives|/location|/location|
|--management-groups|dict|The collection of management groups covered by the Managed Network|//management_groups|//managementGroups|
|--subscriptions|dict|The collection of subscriptions covered by the Managed Network|//subscriptions|//subscriptions|
|--virtual-networks|dict|The collection of virtual nets covered by the Managed Network|//virtual_networks|//virtualNetworks|
|--subnets|dict|The collection of  subnets covered by the Managed Network|//subnets|//subnets|
|--kind|str|Responsibility role under which this Managed Network Group will be created|/kind|/kind|
### managednetwork managed-network-group delete

delete a managednetwork managed-network-group.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|The name of the resource group.|resource_group_name|resourceGroupName|
|**--managed-network-name**|str|The name of the Managed Network.|managed_network_name|managedNetworkName|
|**--name**|str|The name of the Managed Network Group.|managed_network_group_name|managedNetworkGroupName|

**Example: ManagementNetworkGroupsDelete**

```
managednetwork managed-network-group delete --resource-group myResourceGroup
        --managed-network-name myManagedNetwork
        --name myManagedNetworkGroup1
```
### managednetwork managed-network-group list

list a managednetwork managed-network-group.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|The name of the resource group.|resource_group_name|resourceGroupName|
|**--managed-network-name**|str|The name of the Managed Network.|managed_network_name|managedNetworkName|
### managednetwork managed-network-group show

show a managednetwork managed-network-group.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|The name of the resource group.|resource_group_name|resourceGroupName|
|**--managed-network-name**|str|The name of the Managed Network.|managed_network_name|managedNetworkName|
|**--name**|str|The name of the Managed Network Group.|managed_network_group_name|managedNetworkGroupName|
## managednetwork managed-network-peering-policy

### managednetwork managed-network-peering-policy create

create a managednetwork managed-network-peering-policy.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|The name of the resource group.|resource_group_name|resourceGroupName|
|**--managed-network-name**|str|The name of the Managed Network.|managed_network_name|managedNetworkName|
|**--name**|str|The name of the Managed Network Peering Policy.|managed_network_peering_policy_name|managedNetworkPeeringPolicyName|
|**--type**|str|Gets or sets the connectivity type of a network structure policy|//type|//type|
|--location|str|The geo-location where the resource lives|/location|/location|
|--hub-id|str|Resource Id|//hub/id|//hub/id|
|--spokes|dict|Gets or sets the spokes group IDs|//spokes|//spokes|
|--mesh|dict|Gets or sets the mesh group IDs|//mesh|//mesh|

**Example: ManagedNetworkPeeringPoliciesPut**

```
managednetwork managed-network-peering-policy create --resource-group myResourceGroup
        --managed-network-name myManagedNetwork
        --name myHubAndSpoke
```
### managednetwork managed-network-peering-policy update

update a managednetwork managed-network-peering-policy.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|The name of the resource group.|resource_group_name|resourceGroupName|
|**--managed-network-name**|str|The name of the Managed Network.|managed_network_name|managedNetworkName|
|**--name**|str|The name of the Managed Network Peering Policy.|managed_network_peering_policy_name|managedNetworkPeeringPolicyName|
|**--type**|str|Gets or sets the connectivity type of a network structure policy|//type|//type|
|--location|str|The geo-location where the resource lives|/location|/location|
|--hub-id|str|Resource Id|//hub/id|//hub/id|
|--spokes|dict|Gets or sets the spokes group IDs|//spokes|//spokes|
|--mesh|dict|Gets or sets the mesh group IDs|//mesh|//mesh|
### managednetwork managed-network-peering-policy delete

delete a managednetwork managed-network-peering-policy.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|The name of the resource group.|resource_group_name|resourceGroupName|
|**--managed-network-name**|str|The name of the Managed Network.|managed_network_name|managedNetworkName|
|**--name**|str|The name of the Managed Network Peering Policy.|managed_network_peering_policy_name|managedNetworkPeeringPolicyName|

**Example: ManagedNetworkPeeringPoliciesDelete**

```
managednetwork managed-network-peering-policy delete --resource-group myResourceGroup
        --managed-network-name myManagedNetwork
        --name myHubAndSpoke
```
### managednetwork managed-network-peering-policy list

list a managednetwork managed-network-peering-policy.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|The name of the resource group.|resource_group_name|resourceGroupName|
|**--managed-network-name**|str|The name of the Managed Network.|managed_network_name|managedNetworkName|
### managednetwork managed-network-peering-policy show

show a managednetwork managed-network-peering-policy.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|The name of the resource group.|resource_group_name|resourceGroupName|
|**--managed-network-name**|str|The name of the Managed Network.|managed_network_name|managedNetworkName|
|**--name**|str|The name of the Managed Network Peering Policy.|managed_network_peering_policy_name|managedNetworkPeeringPolicyName|
## managednetwork scope-assignment

### managednetwork scope-assignment create

create a managednetwork scope-assignment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--name**|str|The name of the scope assignment to create.|scope_assignment_name|scopeAssignmentName|
|--scope|str|The base resource of the scope assignment to create. The scope can be any REST resource instance. For example, use '/subscriptions/{subscription-id}/' for a subscription, '/subscriptions/{subscription-id}/resourceGroups/{resource-group-name}' for a resource group, and '/subscriptions/{subscription-id}/resourceGroups/{resource-group-name}/providers/{resource-provider}/{resource-type}/{resource-name}' for a resource.|scope|scope|
|--location|str|The geo-location where the resource lives|/location|/location|
|--assigned-managed-network|str|The managed network ID with scope will be assigned to.|//assigned_managed_network|//assignedManagedNetwork|

**Example: ScopeAssignmentsPut**

```
managednetwork scope-assignment create --scope "/subscriptions/{{ subscription_id }}"
        --name subscriptionCAssignment
```
### managednetwork scope-assignment update

update a managednetwork scope-assignment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--name**|str|The name of the scope assignment to create.|scope_assignment_name|scopeAssignmentName|
|--scope|str|The base resource of the scope assignment to create. The scope can be any REST resource instance. For example, use '/subscriptions/{subscription-id}/' for a subscription, '/subscriptions/{subscription-id}/resourceGroups/{resource-group-name}' for a resource group, and '/subscriptions/{subscription-id}/resourceGroups/{resource-group-name}/providers/{resource-provider}/{resource-type}/{resource-name}' for a resource.|scope|scope|
|--location|str|The geo-location where the resource lives|/location|/location|
|--assigned-managed-network|str|The managed network ID with scope will be assigned to.|//assigned_managed_network|//assignedManagedNetwork|
### managednetwork scope-assignment delete

delete a managednetwork scope-assignment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--name**|str|The name of the scope assignment to create.|scope_assignment_name|scopeAssignmentName|
|--scope|str|The base resource of the scope assignment to create. The scope can be any REST resource instance. For example, use '/subscriptions/{subscription-id}/' for a subscription, '/subscriptions/{subscription-id}/resourceGroups/{resource-group-name}' for a resource group, and '/subscriptions/{subscription-id}/resourceGroups/{resource-group-name}/providers/{resource-provider}/{resource-type}/{resource-name}' for a resource.|scope|scope|

**Example: ScopeAssignmentsDelete**

```
managednetwork scope-assignment delete --scope "/subscriptions/{{ subscription_id }}"
        --name subscriptionCAssignment
```
### managednetwork scope-assignment list

list a managednetwork scope-assignment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|--scope|str|The base resource of the scope assignment to create. The scope can be any REST resource instance. For example, use '/subscriptions/{subscription-id}/' for a subscription, '/subscriptions/{subscription-id}/resourceGroups/{resource-group-name}' for a resource group, and '/subscriptions/{subscription-id}/resourceGroups/{resource-group-name}/providers/{resource-provider}/{resource-type}/{resource-name}' for a resource.|scope|scope|
### managednetwork scope-assignment show

show a managednetwork scope-assignment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--name**|str|The name of the scope assignment to create.|scope_assignment_name|scopeAssignmentName|
|--scope|str|The base resource of the scope assignment to create. The scope can be any REST resource instance. For example, use '/subscriptions/{subscription-id}/' for a subscription, '/subscriptions/{subscription-id}/resourceGroups/{resource-group-name}' for a resource group, and '/subscriptions/{subscription-id}/resourceGroups/{resource-group-name}/providers/{resource-provider}/{resource-type}/{resource-name}' for a resource.|scope|scope|