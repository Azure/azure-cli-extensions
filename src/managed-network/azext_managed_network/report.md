# Azure CLI Module Creation Report

## managed-network

### managed-network list

list a managed-network.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
## managed-network group

### managed-network group create

create a managed-network group.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|The name of the resource group.|resource_group_name|resourceGroupName|
|**--managed-network-name**|str|The name of the Managed Network.|managed_network_name|managedNetworkName|
|**--name**|str|The name of the Managed Network Group.|managed_network_group_name|managedNetworkGroupName|
|--location|str|The geo-location where the resource lives|/location|/location|
|--management-groups|str|The collection of management groups covered by the Managed Network|//management_groups/id|//managementGroups/id|
|--subscriptions|str|The collection of subscriptions covered by the Managed Network|//subscriptions/id|//subscriptions/id|
|--virtual-networks|str|The collection of virtual nets covered by the Managed Network|//virtual_networks/id|//virtualNetworks/id|
|--subnets|str|The collection of  subnets covered by the Managed Network|//subnets/id|//subnets/id|
|--kind|str|Responsibility role under which this Managed Network Group will be created|/kind|/kind|

**Example: ManagementNetworkGroupsPut**

```
managed-network group create --resource-group myResourceGroup
        --managed-network-name myManagedNetwork
        --name myManagedNetworkGroup1
```
### managed-network group update

update a managed-network group.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|The name of the resource group.|resource_group_name|resourceGroupName|
|**--managed-network-name**|str|The name of the Managed Network.|managed_network_name|managedNetworkName|
|**--name**|str|The name of the Managed Network Group.|managed_network_group_name|managedNetworkGroupName|
|--location|str|The geo-location where the resource lives|/location|/location|
|--management-groups|str|The collection of management groups covered by the Managed Network|//management_groups/id|//managementGroups/id|
|--subscriptions|str|The collection of subscriptions covered by the Managed Network|//subscriptions/id|//subscriptions/id|
|--virtual-networks|str|The collection of virtual nets covered by the Managed Network|//virtual_networks/id|//virtualNetworks/id|
|--subnets|str|The collection of  subnets covered by the Managed Network|//subnets/id|//subnets/id|
|--kind|str|Responsibility role under which this Managed Network Group will be created|/kind|/kind|
### managed-network group delete

delete a managed-network group.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|The name of the resource group.|resource_group_name|resourceGroupName|
|**--managed-network-name**|str|The name of the Managed Network.|managed_network_name|managedNetworkName|
|**--name**|str|The name of the Managed Network Group.|managed_network_group_name|managedNetworkGroupName|

**Example: ManagementNetworkGroupsDelete**

```
managed-network group delete --resource-group myResourceGroup
        --managed-network-name myManagedNetwork
        --name myManagedNetworkGroup1
```
### managed-network group list

list a managed-network group.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|The name of the resource group.|resource_group_name|resourceGroupName|
|**--managed-network-name**|str|The name of the Managed Network.|managed_network_name|managedNetworkName|
### managed-network group show

show a managed-network group.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|The name of the resource group.|resource_group_name|resourceGroupName|
|**--managed-network-name**|str|The name of the Managed Network.|managed_network_name|managedNetworkName|
|**--name**|str|The name of the Managed Network Group.|managed_network_group_name|managedNetworkGroupName|
## managed-network peering-policy

### managed-network peering-policy create

create a managed-network peering-policy.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|The name of the resource group.|resource_group_name|resourceGroupName|
|**--managed-network-name**|str|The name of the Managed Network.|managed_network_name|managedNetworkName|
|**--name**|str|The name of the Managed Network Peering Policy.|managed_network_peering_policy_name|managedNetworkPeeringPolicyName|
|**--type**|str|Gets or sets the connectivity type of a network structure policy|//type|//type|
|--location|str|The geo-location where the resource lives|/location|/location|
|--hub-id|str|Resource Id|//hub/id|//hub/id|
|--spokes|str|Gets or sets the spokes group IDs|//spokes/id|//spokes/id|
|--mesh|str|Gets or sets the mesh group IDs|//mesh/id|//mesh/id|

**Example: ManagedNetworkPeeringPoliciesPut**

```
managed-network peering-policy create --resource-group myResourceGroup
        --managed-network-name myManagedNetwork
        --name myHubAndSpoke
```
### managed-network peering-policy update

update a managed-network peering-policy.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|The name of the resource group.|resource_group_name|resourceGroupName|
|**--managed-network-name**|str|The name of the Managed Network.|managed_network_name|managedNetworkName|
|**--name**|str|The name of the Managed Network Peering Policy.|managed_network_peering_policy_name|managedNetworkPeeringPolicyName|
|**--type**|str|Gets or sets the connectivity type of a network structure policy|//type|//type|
|--location|str|The geo-location where the resource lives|/location|/location|
|--hub-id|str|Resource Id|//hub/id|//hub/id|
|--spokes|str|Gets or sets the spokes group IDs|//spokes/id|//spokes/id|
|--mesh|str|Gets or sets the mesh group IDs|//mesh/id|//mesh/id|
### managed-network peering-policy delete

delete a managed-network peering-policy.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|The name of the resource group.|resource_group_name|resourceGroupName|
|**--managed-network-name**|str|The name of the Managed Network.|managed_network_name|managedNetworkName|
|**--name**|str|The name of the Managed Network Peering Policy.|managed_network_peering_policy_name|managedNetworkPeeringPolicyName|

**Example: ManagedNetworkPeeringPoliciesDelete**

```
managed-network peering-policy delete --resource-group myResourceGroup
        --managed-network-name myManagedNetwork
        --name myHubAndSpoke
```
### managed-network peering-policy list

list a managed-network peering-policy.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|The name of the resource group.|resource_group_name|resourceGroupName|
|**--managed-network-name**|str|The name of the Managed Network.|managed_network_name|managedNetworkName|
### managed-network peering-policy show

show a managed-network peering-policy.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|The name of the resource group.|resource_group_name|resourceGroupName|
|**--managed-network-name**|str|The name of the Managed Network.|managed_network_name|managedNetworkName|
|**--name**|str|The name of the Managed Network Peering Policy.|managed_network_peering_policy_name|managedNetworkPeeringPolicyName|
## managed-network scope-assignment

### managed-network scope-assignment create

create a managed-network scope-assignment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--name**|str|The name of the scope assignment to create.|scope_assignment_name|scopeAssignmentName|
|--scope|str|The base resource of the scope assignment to create. The scope can be any REST resource instance. For example, use 'subscriptions/{subscription-id}' for a subscription, 'subscriptions/{subscription-id}/resourceGroups/{resource-group-name}' for a resource group, and 'subscriptions/{subscription-id}/resourceGroups/{resource-group-name}/providers/{resource-provider}/{resource-type}/{resource-name}' for a resource.|scope|scope|
|--location|str|The geo-location where the resource lives|/location|/location|
|--assigned-managed-network|str|The managed network ID with scope will be assigned to.|//assigned_managed_network|//assignedManagedNetwork|

**Example: ScopeAssignmentsPut**

```
managed-network scope-assignment create --scope subscriptions/subscriptionC
        --name subscriptionCAssignment
```
### managed-network scope-assignment update

update a managed-network scope-assignment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--name**|str|The name of the scope assignment to create.|scope_assignment_name|scopeAssignmentName|
|--scope|str|The base resource of the scope assignment to create. The scope can be any REST resource instance. For example, use 'subscriptions/{subscription-id}' for a subscription, 'subscriptions/{subscription-id}/resourceGroups/{resource-group-name}' for a resource group, and 'subscriptions/{subscription-id}/resourceGroups/{resource-group-name}/providers/{resource-provider}/{resource-type}/{resource-name}' for a resource.|scope|scope|
|--location|str|The geo-location where the resource lives|/location|/location|
|--assigned-managed-network|str|The managed network ID with scope will be assigned to.|//assigned_managed_network|//assignedManagedNetwork|
### managed-network scope-assignment delete

delete a managed-network scope-assignment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--name**|str|The name of the scope assignment to create.|scope_assignment_name|scopeAssignmentName|
|--scope|str|The base resource of the scope assignment to create. The scope can be any REST resource instance. For example, use 'subscriptions/{subscription-id}' for a subscription, 'subscriptions/{subscription-id}/resourceGroups/{resource-group-name}' for a resource group, and 'subscriptions/{subscription-id}/resourceGroups/{resource-group-name}/providers/{resource-provider}/{resource-type}/{resource-name}' for a resource.|scope|scope|

**Example: ScopeAssignmentsDelete**

```
managed-network scope-assignment delete --scope subscriptions/subscriptionC
        --name subscriptionCAssignment
```
### managed-network scope-assignment list

list a managed-network scope-assignment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|--scope|str|The base resource of the scope assignment to create. The scope can be any REST resource instance. For example, use 'subscriptions/{subscription-id}' for a subscription, 'subscriptions/{subscription-id}/resourceGroups/{resource-group-name}' for a resource group, and 'subscriptions/{subscription-id}/resourceGroups/{resource-group-name}/providers/{resource-provider}/{resource-type}/{resource-name}' for a resource.|scope|scope|
### managed-network scope-assignment show

show a managed-network scope-assignment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--name**|str|The name of the scope assignment to create.|scope_assignment_name|scopeAssignmentName|
|--scope|str|The base resource of the scope assignment to create. The scope can be any REST resource instance. For example, use 'subscriptions/{subscription-id}' for a subscription, 'subscriptions/{subscription-id}/resourceGroups/{resource-group-name}' for a resource group, and 'subscriptions/{subscription-id}/resourceGroups/{resource-group-name}/providers/{resource-provider}/{resource-type}/{resource-name}' for a resource.|scope|scope|