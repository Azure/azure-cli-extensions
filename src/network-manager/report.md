# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az network|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az network` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az network manager|NetworkManagers|[commands](#CommandsInNetworkManagers)|
|az network manager commit|NetworkManagerCommits|[commands](#CommandsInNetworkManagerCommits)|
|az network manager deploy-status|NetworkManagerDeploymentStatus|[commands](#CommandsInNetworkManagerDeploymentStatus)|
|az network manager effect-vnet|EffectiveVirtualNetworks|[commands](#CommandsInEffectiveVirtualNetworks)|
|az network manager active-config|ActiveConfigurations|[commands](#CommandsInActiveConfigurations)|
|az network manager connect-config|ConnectivityConfigurations|[commands](#CommandsInConnectivityConfigurations)|
|az network effectiveconfiguration|EffectiveConfigurations|[commands](#CommandsInEffectiveConfigurations)|
|az network manager group|NetworkGroups|[commands](#CommandsInNetworkGroups)|
|az network manager security-config|SecurityConfigurations|[commands](#CommandsInSecurityConfigurations)|
|az network manager admin-rule|AdminRules|[commands](#CommandsInAdminRules)|
|az network manager user-rule|UserRules|[commands](#CommandsInUserRules)|

## COMMANDS
### <a name="CommandsInEffectiveConfigurations">Commands in `az network effectiveconfiguration` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az network effectiveconfiguration list](#EffectiveConfigurationsList)|List|[Parameters](#ParametersEffectiveConfigurationsList)|[Example](#ExamplesEffectiveConfigurationsList)|

### <a name="CommandsInNetworkManagers">Commands in `az network manager` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az network manager list](#NetworkManagersList)|List|[Parameters](#ParametersNetworkManagersList)|[Example](#ExamplesNetworkManagersList)|
|[az network manager show](#NetworkManagersGet)|Get|[Parameters](#ParametersNetworkManagersGet)|[Example](#ExamplesNetworkManagersGet)|
|[az network manager create](#NetworkManagersCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersNetworkManagersCreateOrUpdate#Create)|[Example](#ExamplesNetworkManagersCreateOrUpdate#Create)|
|[az network manager update](#NetworkManagersCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersNetworkManagersCreateOrUpdate#Update)|Not Found|
|[az network manager delete](#NetworkManagersDelete)|Delete|[Parameters](#ParametersNetworkManagersDelete)|[Example](#ExamplesNetworkManagersDelete)|

### <a name="CommandsInActiveConfigurations">Commands in `az network manager active-config` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az network manager active-config list](#ActiveConfigurationsList)|List|[Parameters](#ParametersActiveConfigurationsList)|[Example](#ExamplesActiveConfigurationsList)|

### <a name="CommandsInAdminRules">Commands in `az network manager admin-rule` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az network manager admin-rule list](#AdminRulesList)|List|[Parameters](#ParametersAdminRulesList)|[Example](#ExamplesAdminRulesList)|
|[az network manager admin-rule show](#AdminRulesGet)|Get|[Parameters](#ParametersAdminRulesGet)|[Example](#ExamplesAdminRulesGet)|
|[az network manager admin-rule delete](#AdminRulesDelete)|Delete|[Parameters](#ParametersAdminRulesDelete)|[Example](#ExamplesAdminRulesDelete)|

### <a name="CommandsInNetworkManagerCommits">Commands in `az network manager commit` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az network manager commit post](#NetworkManagerCommitsPost)|Post|[Parameters](#ParametersNetworkManagerCommitsPost)|[Example](#ExamplesNetworkManagerCommitsPost)|

### <a name="CommandsInConnectivityConfigurations">Commands in `az network manager connect-config` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az network manager connect-config list](#ConnectivityConfigurationsList)|List|[Parameters](#ParametersConnectivityConfigurationsList)|[Example](#ExamplesConnectivityConfigurationsList)|
|[az network manager connect-config show](#ConnectivityConfigurationsGet)|Get|[Parameters](#ParametersConnectivityConfigurationsGet)|[Example](#ExamplesConnectivityConfigurationsGet)|
|[az network manager connect-config create](#ConnectivityConfigurationsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersConnectivityConfigurationsCreateOrUpdate#Create)|[Example](#ExamplesConnectivityConfigurationsCreateOrUpdate#Create)|
|[az network manager connect-config update](#ConnectivityConfigurationsCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersConnectivityConfigurationsCreateOrUpdate#Update)|Not Found|
|[az network manager connect-config delete](#ConnectivityConfigurationsDelete)|Delete|[Parameters](#ParametersConnectivityConfigurationsDelete)|[Example](#ExamplesConnectivityConfigurationsDelete)|

### <a name="CommandsInNetworkManagerDeploymentStatus">Commands in `az network manager deploy-status` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az network manager deploy-status list](#NetworkManagerDeploymentStatusList)|List|[Parameters](#ParametersNetworkManagerDeploymentStatusList)|[Example](#ExamplesNetworkManagerDeploymentStatusList)|

### <a name="CommandsInEffectiveVirtualNetworks">Commands in `az network manager effect-vnet` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az network manager effect-vnet list-by-network-group](#EffectiveVirtualNetworksListByNetworkGroup)|ListByNetworkGroup|[Parameters](#ParametersEffectiveVirtualNetworksListByNetworkGroup)|[Example](#ExamplesEffectiveVirtualNetworksListByNetworkGroup)|
|[az network manager effect-vnet list-by-network-manager](#EffectiveVirtualNetworksListByNetworkManager)|ListByNetworkManager|[Parameters](#ParametersEffectiveVirtualNetworksListByNetworkManager)|[Example](#ExamplesEffectiveVirtualNetworksListByNetworkManager)|

### <a name="CommandsInNetworkGroups">Commands in `az network manager group` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az network manager group list](#NetworkGroupsList)|List|[Parameters](#ParametersNetworkGroupsList)|[Example](#ExamplesNetworkGroupsList)|
|[az network manager group show](#NetworkGroupsGet)|Get|[Parameters](#ParametersNetworkGroupsGet)|[Example](#ExamplesNetworkGroupsGet)|
|[az network manager group create](#NetworkGroupsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersNetworkGroupsCreateOrUpdate#Create)|[Example](#ExamplesNetworkGroupsCreateOrUpdate#Create)|
|[az network manager group update](#NetworkGroupsCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersNetworkGroupsCreateOrUpdate#Update)|Not Found|
|[az network manager group delete](#NetworkGroupsDelete)|Delete|[Parameters](#ParametersNetworkGroupsDelete)|[Example](#ExamplesNetworkGroupsDelete)|

### <a name="CommandsInSecurityConfigurations">Commands in `az network manager security-config` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az network manager security-config list](#SecurityConfigurationsList)|List|[Parameters](#ParametersSecurityConfigurationsList)|[Example](#ExamplesSecurityConfigurationsList)|
|[az network manager security-config show](#SecurityConfigurationsGet)|Get|[Parameters](#ParametersSecurityConfigurationsGet)|[Example](#ExamplesSecurityConfigurationsGet)|
|[az network manager security-config create](#SecurityConfigurationsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersSecurityConfigurationsCreateOrUpdate#Create)|[Example](#ExamplesSecurityConfigurationsCreateOrUpdate#Create)|
|[az network manager security-config update](#SecurityConfigurationsCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersSecurityConfigurationsCreateOrUpdate#Update)|Not Found|
|[az network manager security-config delete](#SecurityConfigurationsDelete)|Delete|[Parameters](#ParametersSecurityConfigurationsDelete)|[Example](#ExamplesSecurityConfigurationsDelete)|
|[az network manager security-config evaluate-import](#SecurityConfigurationsEvaluateImport)|EvaluateImport|[Parameters](#ParametersSecurityConfigurationsEvaluateImport)|[Example](#ExamplesSecurityConfigurationsEvaluateImport)|
|[az network manager security-config import](#SecurityConfigurationsImport)|Import|[Parameters](#ParametersSecurityConfigurationsImport)|[Example](#ExamplesSecurityConfigurationsImport)|

### <a name="CommandsInUserRules">Commands in `az network manager user-rule` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az network manager user-rule list](#UserRulesList)|List|[Parameters](#ParametersUserRulesList)|[Example](#ExamplesUserRulesList)|
|[az network manager user-rule show](#UserRulesGet)|Get|[Parameters](#ParametersUserRulesGet)|[Example](#ExamplesUserRulesGet)|
|[az network manager user-rule create](#UserRulesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersUserRulesCreateOrUpdate#Create)|[Example](#ExamplesUserRulesCreateOrUpdate#Create)|
|[az network manager user-rule update](#UserRulesCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersUserRulesCreateOrUpdate#Update)|Not Found|
|[az network manager user-rule delete](#UserRulesDelete)|Delete|[Parameters](#ParametersUserRulesDelete)|[Example](#ExamplesUserRulesDelete)|


## COMMAND DETAILS

### group `az network effectiveconfiguration`
#### <a name="EffectiveConfigurationsList">Command `az network effectiveconfiguration list`</a>

##### <a name="ExamplesEffectiveConfigurationsList">Example</a>
```
az network effectiveconfiguration list --resource-group "myResourceGroup" --virtual-network-name "testVirtualNetwork"
```
##### <a name="ParametersEffectiveConfigurationsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--virtual-network-name**|string|The name of the virtual network.|virtual_network_name|virtualNetworkName|
|**--top**|integer|An optional query parameter which specifies the maximum number of records to be returned by the server.|top|$top|
|**--skip-token**|string|SkipToken is only used if a previous operation returned a partial result. If a previous response contains a nextLink element, the value of the nextLink element will include a skipToken parameter that specifies a starting point to use for subsequent calls.|skip_token|$skipToken|

### group `az network manager`
#### <a name="NetworkManagersList">Command `az network manager list`</a>

##### <a name="ExamplesNetworkManagersList">Example</a>
```
az network manager list --resource-group "rg1"
```
##### <a name="ParametersNetworkManagersList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--top**|integer|An optional query parameter which specifies the maximum number of records to be returned by the server.|top|$top|
|**--skip-token**|string|SkipToken is only used if a previous operation returned a partial result. If a previous response contains a nextLink element, the value of the nextLink element will include a skipToken parameter that specifies a starting point to use for subsequent calls.|skip_token|$skipToken|

#### <a name="NetworkManagersGet">Command `az network manager show`</a>

##### <a name="ExamplesNetworkManagersGet">Example</a>
```
az network manager show --name "testNetworkManager" --resource-group "rg1"
```
##### <a name="ParametersNetworkManagersGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--network-manager-name**|string|The name of the network manager.|network_manager_name|networkManagerName|

#### <a name="NetworkManagersCreateOrUpdate#Create">Command `az network manager create`</a>

##### <a name="ExamplesNetworkManagersCreateOrUpdate#Create">Example</a>
```
az network manager create --name "TestNetworkManager" --description "My Test Network Manager" --display-name \
"TestNetworkManager" --network-manager-scope-accesses "Security" "Routing" "Connectivity" --network-manager-scopes \
management-groups="/Microsoft.Management/testmg" subscriptions="/subscriptions/00000000-0000-0000-0000-000000000000" \
--resource-group "rg1"
```
##### <a name="ParametersNetworkManagersCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--network-manager-name**|string|The name of the network manager.|network_manager_name|networkManagerName|
|**--id**|string|Resource ID.|id|id|
|**--location**|string|Resource location.|location|location|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--display-name**|string|A friendly name for the network manager.|display_name|displayName|
|**--description**|string|A description of the network manager.|description|description|
|**--network-manager-scopes**|object|Scope of Network Manager.|network_manager_scopes|networkManagerScopes|
|**--network-manager-scope-accesses**|array|Scope Access.|network_manager_scope_accesses|networkManagerScopeAccesses|

#### <a name="NetworkManagersCreateOrUpdate#Update">Command `az network manager update`</a>

##### <a name="ParametersNetworkManagersCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--network-manager-name**|string|The name of the network manager.|network_manager_name|networkManagerName|
|**--id**|string|Resource ID.|id|id|
|**--location**|string|Resource location.|location|location|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--display-name**|string|A friendly name for the network manager.|display_name|displayName|
|**--description**|string|A description of the network manager.|description|description|
|**--network-manager-scopes**|object|Scope of Network Manager.|network_manager_scopes|networkManagerScopes|
|**--network-manager-scope-accesses**|array|Scope Access.|network_manager_scope_accesses|networkManagerScopeAccesses|

#### <a name="NetworkManagersDelete">Command `az network manager delete`</a>

##### <a name="ExamplesNetworkManagersDelete">Example</a>
```
az network manager delete --name "testNetworkManager" --resource-group "rg1"
```
##### <a name="ParametersNetworkManagersDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--network-manager-name**|string|The name of the network manager.|network_manager_name|networkManagerName|

### group `az network manager active-config`
#### <a name="ActiveConfigurationsList">Command `az network manager active-config list`</a>

##### <a name="ExamplesActiveConfigurationsList">Example</a>
```
az network manager active-config list --network-manager-name "testNetworkManager" --resource-group "myResourceGroup"
```
##### <a name="ParametersActiveConfigurationsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--network-manager-name**|string|The name of the network manager.|network_manager_name|networkManagerName|
|**--top**|integer|An optional query parameter which specifies the maximum number of records to be returned by the server.|top|$top|
|**--skip-token**|string|SkipToken is only used if a previous operation returned a partial result. If a previous response contains a nextLink element, the value of the nextLink element will include a skipToken parameter that specifies a starting point to use for subsequent calls.|skip_token|$skipToken|
|**--region**|string|Location name|region|region|

### group `az network manager admin-rule`
#### <a name="AdminRulesList">Command `az network manager admin-rule list`</a>

##### <a name="ExamplesAdminRulesList">Example</a>
```
az network manager admin-rule list --configuration-name "myTestSecurityConfig" --network-manager-name \
"testNetworkManager" --resource-group "rg1"
```
##### <a name="ParametersAdminRulesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--network-manager-name**|string|The name of the network manager.|network_manager_name|networkManagerName|
|**--configuration-name**|string|The name of the network manager security Configuration.|configuration_name|configurationName|
|**--top**|integer|An optional query parameter which specifies the maximum number of records to be returned by the server.|top|$top|
|**--skip-token**|string|SkipToken is only used if a previous operation returned a partial result. If a previous response contains a nextLink element, the value of the nextLink element will include a skipToken parameter that specifies a starting point to use for subsequent calls.|skip_token|$skipToken|

#### <a name="AdminRulesGet">Command `az network manager admin-rule show`</a>

##### <a name="ExamplesAdminRulesGet">Example</a>
```
az network manager admin-rule show --configuration-name "myTestSecurityConfig" --network-manager-name \
"testNetworkManager" --resource-group "rg1" --rule-name "SampleAdminRule"
```
##### <a name="ParametersAdminRulesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--network-manager-name**|string|The name of the network manager.|network_manager_name|networkManagerName|
|**--configuration-name**|string|The name of the network manager security Configuration.|configuration_name|configurationName|
|**--rule-name**|string|The name of the rule.|rule_name|ruleName|

#### <a name="AdminRulesDelete">Command `az network manager admin-rule delete`</a>

##### <a name="ExamplesAdminRulesDelete">Example</a>
```
az network manager admin-rule delete --configuration-name "myTestSecurityConfig" --network-manager-name \
"testNetworkManager" --resource-group "rg1" --rule-name "SampleAdminRule"
```
##### <a name="ParametersAdminRulesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--network-manager-name**|string|The name of the network manager.|network_manager_name|networkManagerName|
|**--configuration-name**|string|The name of the network manager security Configuration.|configuration_name|configurationName|
|**--rule-name**|string|The name of the rule.|rule_name|ruleName|

### group `az network manager commit`
#### <a name="NetworkManagerCommitsPost">Command `az network manager commit post`</a>

##### <a name="ExamplesNetworkManagerCommitsPost">Example</a>
```
az network manager commit post --network-manager-name "testNetworkManager" --commit-type "AdminPolicy" \
--configuration-ids "/subscriptions/subscriptionC/resourceGroups/resoureGroupSample/providers/Microsoft.Network/network\
Managers/testNetworkManager/securityConfigurations/SampleSecurityConfig" --target-locations "usest" --resource-group \
"resoureGroupSample"
```
##### <a name="ParametersNetworkManagerCommitsPost">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--network-manager-name**|string|The name of the network manager.|network_manager_name|networkManagerName|
|**--target-locations**|array|List of target locations.|target_locations|targetLocations|
|**--configuration-ids**|array|List of configuration ids.|configuration_ids|configurationIds|
|**--commit-type**|choice|Commit Type.|commit_type|commitType|

### group `az network manager connect-config`
#### <a name="ConnectivityConfigurationsList">Command `az network manager connect-config list`</a>

##### <a name="ExamplesConnectivityConfigurationsList">Example</a>
```
az network manager connect-config list --network-manager-name "testNetworkManager" --resource-group "myResourceGroup"
```
##### <a name="ParametersConnectivityConfigurationsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--network-manager-name**|string|The name of the network manager.|network_manager_name|networkManagerName|
|**--top**|integer|An optional query parameter which specifies the maximum number of records to be returned by the server.|top|$top|
|**--skip-token**|string|SkipToken is only used if a previous operation returned a partial result. If a previous response contains a nextLink element, the value of the nextLink element will include a skipToken parameter that specifies a starting point to use for subsequent calls.|skip_token|$skipToken|

#### <a name="ConnectivityConfigurationsGet">Command `az network manager connect-config show`</a>

##### <a name="ExamplesConnectivityConfigurationsGet">Example</a>
```
az network manager connect-config show --configuration-name "myTestConnectivityConfig" --network-manager-name \
"testNetworkManager" --resource-group "myResourceGroup"
```
##### <a name="ParametersConnectivityConfigurationsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--network-manager-name**|string|The name of the network manager.|network_manager_name|networkManagerName|
|**--configuration-name**|string|The name of the network manager connectivity configuration.|configuration_name|configurationName|

#### <a name="ConnectivityConfigurationsCreateOrUpdate#Create">Command `az network manager connect-config create`</a>

##### <a name="ExamplesConnectivityConfigurationsCreateOrUpdate#Create">Example</a>
```
az network manager connect-config create --configuration-name "myTestConnectivityConfig" --description "Sample \
Configuration" --applies-to-groups group-connectivity="Transitive" is-global=false network-group-id="subscriptions/subs\
criptionA/resourceGroups/myResourceGroup/providers/Microsoft.Network/networkManagers/testNetworkManager/networkManagerG\
roups/group1" use-hub-gateway=true --connectivity-topology "HubAndSpokeTopology" --delete-existing-peering true \
--display-name "myTestConnectivityConfig" --hub-id "subscriptions/subscriptionA/resourceGroups/myResourceGroup/provider\
s/Microsoft.Network/virtualNetworks/myTestConnectivityConfig" --is-global true --network-manager-name \
"testNetworkManager" --resource-group "myResourceGroup"
```
##### <a name="ParametersConnectivityConfigurationsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--network-manager-name**|string|The name of the network manager.|network_manager_name|networkManagerName|
|**--configuration-name**|string|The name of the network manager connectivity configuration.|configuration_name|configurationName|
|**--display-name**|string|A friendly name for the resource.|display_name|displayName|
|**--description**|string|A description of the connectivity configuration.|description|description|
|**--connectivity-topology**|choice|Connectivity topology type.|connectivity_topology|connectivityTopology|
|**--hub-id**|string|The hub vnet Id.|hub_id|hubId|
|**--is-global**|boolean|Flag if global mesh is supported.|is_global|isGlobal|
|**--applies-to-groups**|array|Groups for configuration|applies_to_groups|appliesToGroups|
|**--delete-existing-peering**|boolean|Flag if need to remove current existing peerings.|delete_existing_peering|deleteExistingPeering|

#### <a name="ConnectivityConfigurationsCreateOrUpdate#Update">Command `az network manager connect-config update`</a>

##### <a name="ParametersConnectivityConfigurationsCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--network-manager-name**|string|The name of the network manager.|network_manager_name|networkManagerName|
|**--configuration-name**|string|The name of the network manager connectivity configuration.|configuration_name|configurationName|
|**--display-name**|string|A friendly name for the resource.|display_name|displayName|
|**--description**|string|A description of the connectivity configuration.|description|description|
|**--connectivity-topology**|choice|Connectivity topology type.|connectivity_topology|connectivityTopology|
|**--hub-id**|string|The hub vnet Id.|hub_id|hubId|
|**--is-global**|boolean|Flag if global mesh is supported.|is_global|isGlobal|
|**--applies-to-groups**|array|Groups for configuration|applies_to_groups|appliesToGroups|
|**--delete-existing-peering**|boolean|Flag if need to remove current existing peerings.|delete_existing_peering|deleteExistingPeering|

#### <a name="ConnectivityConfigurationsDelete">Command `az network manager connect-config delete`</a>

##### <a name="ExamplesConnectivityConfigurationsDelete">Example</a>
```
az network manager connect-config delete --configuration-name "myTestConnectivityConfig" --network-manager-name \
"testNetworkManager" --resource-group "myResourceGroup"
```
##### <a name="ParametersConnectivityConfigurationsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--network-manager-name**|string|The name of the network manager.|network_manager_name|networkManagerName|
|**--configuration-name**|string|The name of the network manager connectivity configuration.|configuration_name|configurationName|

### group `az network manager deploy-status`
#### <a name="NetworkManagerDeploymentStatusList">Command `az network manager deploy-status list`</a>

##### <a name="ExamplesNetworkManagerDeploymentStatusList">Example</a>
```
az network manager deploy-status list --network-manager-name "testNetworkManager" --deployment-types "Connectivity" \
"AdminPolicy" --regions "eastus" "westus" --resource-group "resoureGroupSample"
```
##### <a name="ParametersNetworkManagerDeploymentStatusList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--network-manager-name**|string|The name of the network manager.|network_manager_name|networkManagerName|
|**--top**|integer|An optional query parameter which specifies the maximum number of records to be returned by the server.|top|$top|
|**--skip-token**|string|SkipToken is only used if a previous operation returned a partial result. If a previous response contains a nextLink element, the value of the nextLink element will include a skipToken parameter that specifies a starting point to use for subsequent calls.|skip_token|$skipToken|
|**--regions**|array|List of locations.|regions|regions|
|**--deployment-types**|array|List of configurations' deployment types.|deployment_types|deploymentTypes|

### group `az network manager effect-vnet`
#### <a name="EffectiveVirtualNetworksListByNetworkGroup">Command `az network manager effect-vnet list-by-network-group`</a>

##### <a name="ExamplesEffectiveVirtualNetworksListByNetworkGroup">Example</a>
```
az network manager effect-vnet list-by-network-group --network-group-name "TestNetworkGroup" --network-manager-name \
"testNetworkManager" --resource-group "rg1"
```
##### <a name="ParametersEffectiveVirtualNetworksListByNetworkGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--network-manager-name**|string|The name of the network manager.|network_manager_name|networkManagerName|
|**--network-group-name**|string|The name of the network group to get.|network_group_name|networkGroupName|
|**--top**|integer|An optional query parameter which specifies the maximum number of records to be returned by the server.|top|$top|
|**--skip-token**|string|SkipToken is only used if a previous operation returned a partial result. If a previous response contains a nextLink element, the value of the nextLink element will include a skipToken parameter that specifies a starting point to use for subsequent calls.|skip_token|$skipToken|

#### <a name="EffectiveVirtualNetworksListByNetworkManager">Command `az network manager effect-vnet list-by-network-manager`</a>

##### <a name="ExamplesEffectiveVirtualNetworksListByNetworkManager">Example</a>
```
az network manager effect-vnet list-by-network-manager --network-manager-name "testNetworkManager" \
--conditional-members "location=\'useast2\'" --resource-group "rg1"
```
##### <a name="ParametersEffectiveVirtualNetworksListByNetworkManager">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--network-manager-name**|string|The name of the network manager.|network_manager_name|networkManagerName|
|**--top**|integer|An optional query parameter which specifies the maximum number of records to be returned by the server.|top|$top|
|**--skip-token**|string|SkipToken is only used if a previous operation returned a partial result. If a previous response contains a nextLink element, the value of the nextLink element will include a skipToken parameter that specifies a starting point to use for subsequent calls.|skip_token|$skipToken|
|**--conditional-members**|string|Conditional Members.|conditional_members|conditionalMembers|

### group `az network manager group`
#### <a name="NetworkGroupsList">Command `az network manager group list`</a>

##### <a name="ExamplesNetworkGroupsList">Example</a>
```
az network manager group list --network-manager-name "testNetworkManager" --resource-group "rg1"
```
##### <a name="ParametersNetworkGroupsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--network-manager-name**|string|The name of the network manager.|network_manager_name|networkManagerName|
|**--top**|integer|An optional query parameter which specifies the maximum number of records to be returned by the server.|top|$top|
|**--skip-token**|string|SkipToken is only used if a previous operation returned a partial result. If a previous response contains a nextLink element, the value of the nextLink element will include a skipToken parameter that specifies a starting point to use for subsequent calls.|skip_token|$skipToken|

#### <a name="NetworkGroupsGet">Command `az network manager group show`</a>

##### <a name="ExamplesNetworkGroupsGet">Example</a>
```
az network manager group show --name "TestNetworkGroup" --network-manager-name "testNetworkManager" --resource-group \
"rg1"
```
##### <a name="ParametersNetworkGroupsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--network-manager-name**|string|The name of the network manager.|network_manager_name|networkManagerName|
|**--network-group-name**|string|The name of the network group to get.|network_group_name|networkGroupName|

#### <a name="NetworkGroupsCreateOrUpdate#Create">Command `az network manager group create`</a>

##### <a name="ExamplesNetworkGroupsCreateOrUpdate#Create">Example</a>
```
az network manager group create --name "TestNetworkGroup" --network-manager-name "testNetworkManager" --description "A \
sample group" --conditional-membership "" --display-name "My Network Group" --group-members \
resource-id="/subscriptions/subscriptionC/resourceGroup/rg1/providers/Microsoft.Network/virtualnetworks/vnet1" \
--member-type "VirtualNetwork" --resource-group "rg1"
```
##### <a name="ParametersNetworkGroupsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--network-manager-name**|string|The name of the network manager.|network_manager_name|networkManagerName|
|**--network-group-name**|string|The name of the network group to get.|network_group_name|networkGroupName|
|**--if-match**|string|The ETag of the transformation. Omit this value to always overwrite the current resource. Specify the last-seen ETag value to prevent accidentally overwriting concurrent changes.|if_match|IfMatch|
|**--display-name**|string|A friendly name for the network group.|display_name|displayName|
|**--description**|string|A description of the network group.|description|description|
|**--member-type**|choice|Group member type.|member_type|memberType|
|**--group-members**|array|Group members of network group.|group_members|groupMembers|
|**--conditional-membership**|string|Network group conditional filter.|conditional_membership|conditionalMembership|

#### <a name="NetworkGroupsCreateOrUpdate#Update">Command `az network manager group update`</a>

##### <a name="ParametersNetworkGroupsCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--network-manager-name**|string|The name of the network manager.|network_manager_name|networkManagerName|
|**--network-group-name**|string|The name of the network group to get.|network_group_name|networkGroupName|
|**--if-match**|string|The ETag of the transformation. Omit this value to always overwrite the current resource. Specify the last-seen ETag value to prevent accidentally overwriting concurrent changes.|if_match|IfMatch|
|**--display-name**|string|A friendly name for the network group.|display_name|displayName|
|**--description**|string|A description of the network group.|description|description|
|**--member-type**|choice|Group member type.|member_type|memberType|
|**--group-members**|array|Group members of network group.|group_members|groupMembers|
|**--conditional-membership**|string|Network group conditional filter.|conditional_membership|conditionalMembership|

#### <a name="NetworkGroupsDelete">Command `az network manager group delete`</a>

##### <a name="ExamplesNetworkGroupsDelete">Example</a>
```
az network manager group delete --name "TestNetworkGroup" --network-manager-name "testNetworkManager" --resource-group \
"rg1"
```
##### <a name="ParametersNetworkGroupsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--network-manager-name**|string|The name of the network manager.|network_manager_name|networkManagerName|
|**--network-group-name**|string|The name of the network group to get.|network_group_name|networkGroupName|

### group `az network manager security-config`
#### <a name="SecurityConfigurationsList">Command `az network manager security-config list`</a>

##### <a name="ExamplesSecurityConfigurationsList">Example</a>
```
az network manager security-config list --network-manager-name "testNetworkManager" --resource-group "rg1"
```
##### <a name="ParametersSecurityConfigurationsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--network-manager-name**|string|The name of the network manager.|network_manager_name|networkManagerName|
|**--top**|integer|An optional query parameter which specifies the maximum number of records to be returned by the server.|top|$top|
|**--skip-token**|string|SkipToken is only used if a previous operation returned a partial result. If a previous response contains a nextLink element, the value of the nextLink element will include a skipToken parameter that specifies a starting point to use for subsequent calls.|skip_token|$skipToken|

#### <a name="SecurityConfigurationsGet">Command `az network manager security-config show`</a>

##### <a name="ExamplesSecurityConfigurationsGet">Example</a>
```
az network manager security-config show --configuration-name "myTestSecurityConfig" --network-manager-name \
"testNetworkManager" --resource-group "rg1"
```
##### <a name="ParametersSecurityConfigurationsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--network-manager-name**|string|The name of the network manager.|network_manager_name|networkManagerName|
|**--configuration-name**|string|The name of the network manager security Configuration.|configuration_name|configurationName|

#### <a name="SecurityConfigurationsCreateOrUpdate#Create">Command `az network manager security-config create`</a>

##### <a name="ExamplesSecurityConfigurationsCreateOrUpdate#Create">Example</a>
```
az network manager security-config create --configuration-name "myTestSecurityConfig" --network-manager-name \
"testNetworkManager" --resource-group "rg1" --description "A sample policy" --applies-to-groups \
network-group-id="/subscriptions/subId/resourceGroups/rg1/providers/Microsoft.Network/networkManagers/testNetworkManage\
r/networkGroups/testGroup" --delete-existing-ns-gs true --security-type "UserPolicy"
```
##### <a name="ParametersSecurityConfigurationsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--network-manager-name**|string|The name of the network manager.|network_manager_name|networkManagerName|
|**--configuration-name**|string|The name of the network manager security Configuration.|configuration_name|configurationName|
|**--display-name**|string|A display name of the security Configuration.|display_name|displayName|
|**--description**|string|A description of the security Configuration.|description|description|
|**--security-type**|choice|Security Type.|security_type|securityType|
|**--delete-existing-ns-gs**|boolean|Flag if need to delete existing network security groups.|delete_existing_ns_gs|deleteExistingNSGs|
|**--applies-to-groups**|array|Groups for configuration|applies_to_groups|appliesToGroups|

#### <a name="SecurityConfigurationsCreateOrUpdate#Update">Command `az network manager security-config update`</a>

##### <a name="ParametersSecurityConfigurationsCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--network-manager-name**|string|The name of the network manager.|network_manager_name|networkManagerName|
|**--configuration-name**|string|The name of the network manager security Configuration.|configuration_name|configurationName|
|**--display-name**|string|A display name of the security Configuration.|display_name|displayName|
|**--description**|string|A description of the security Configuration.|description|description|
|**--security-type**|choice|Security Type.|security_type|securityType|
|**--delete-existing-ns-gs**|boolean|Flag if need to delete existing network security groups.|delete_existing_ns_gs|deleteExistingNSGs|
|**--applies-to-groups**|array|Groups for configuration|applies_to_groups|appliesToGroups|

#### <a name="SecurityConfigurationsDelete">Command `az network manager security-config delete`</a>

##### <a name="ExamplesSecurityConfigurationsDelete">Example</a>
```
az network manager security-config delete --configuration-name "myTestSecurityConfig" --network-manager-name \
"testNetworkManager" --resource-group "rg1"
```
##### <a name="ParametersSecurityConfigurationsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--network-manager-name**|string|The name of the network manager.|network_manager_name|networkManagerName|
|**--configuration-name**|string|The name of the network manager security Configuration.|configuration_name|configurationName|

#### <a name="SecurityConfigurationsEvaluateImport">Command `az network manager security-config evaluate-import`</a>

##### <a name="ExamplesSecurityConfigurationsEvaluateImport">Example</a>
```
az network manager security-config evaluate-import --configuration-name "myTestConfig" --network-manager-name \
"testNetworkManager" --admin-security-configuration-uri "/subscriptions/subId/resourceGroups/rg1/providers/Microsoft.Ne\
twork/networkManagers/testNetworkManager/securityConfigurations/adminConfig" --import-deny-rules-as-admin-rules true \
--network-security-group-imports network-security-group-uri="/subscriptions/subid/resourceGroups/rg1/providers/Microsof\
t.Network/networkSecurityGroups/testnsg/securityRules/rule1" --remove-allow-azure-load-balancer-inbound-rule true \
--remove-allow-internet-outbound-rule true --remove-allow-vnet-inbound-rule true --remove-allow-vnet-outbound-rule \
true --resource-group "rg1"
```
##### <a name="ParametersSecurityConfigurationsEvaluateImport">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--network-manager-name**|string|The name of the network manager.|network_manager_name|networkManagerName|
|**--configuration-name**|string|The name of the network manager security Configuration.|configuration_name|configurationName|
|**--top**|integer|An optional query parameter which specifies the maximum number of records to be returned by the server.|top|$top|
|**--skip-token**|string|SkipToken is only used if a previous operation returned a partial result. If a previous response contains a nextLink element, the value of the nextLink element will include a skipToken parameter that specifies a starting point to use for subsequent calls.|skip_token|$skipToken|
|**--network-security-group-imports**|array|List of nsg uris.|network_security_group_imports|networkSecurityGroupImports|
|**--import-deny-rules-as-admin-rules**|boolean|Flag if import deny rules as admin rules.|import_deny_rules_as_admin_rules|importDenyRulesAsAdminRules|
|**--admin-security-configuration-uri**|string|Admin security configuration Uri.|admin_security_configuration_uri|adminSecurityConfigurationUri|
|**--remove-allow-vnet-inbound-rule**|boolean|Flag if need to remove allow vnet inbound rule.|remove_allow_vnet_inbound_rule|removeAllowVnetInboundRule|
|**--remove-allow-azure-load-balancer-inbound-rule**|boolean|Flag if need to remove allow azure load balancer inbound rule.|remove_allow_azure_load_balancer_inbound_rule|removeAllowAzureLoadBalancerInboundRule|
|**--remove-allow-vnet-outbound-rule**|boolean|Flag if need to remove allow vnet outbound rule.|remove_allow_vnet_outbound_rule|removeAllowVnetOutboundRule|
|**--remove-allow-internet-outbound-rule**|boolean|Flag if need to remove allow Internet outbound rule.|remove_allow_internet_outbound_rule|removeAllowInternetOutboundRule|

#### <a name="SecurityConfigurationsImport">Command `az network manager security-config import`</a>

##### <a name="ExamplesSecurityConfigurationsImport">Example</a>
```
az network manager security-config import --configuration-name "myTestConfig" --network-manager-name \
"testNetworkManager" --admin-security-configuration-uri "/subscriptions/subId/resourceGroups/rg1/providers/Microsoft.Ne\
twork/networkManagers/testNetworkManager/securityConfigurations/adminConfig" --import-deny-rules-as-admin-rules true \
--network-security-group-imports network-security-group-uri="/subscriptions/subid/resourceGroups/rg1/providers/Microsof\
t.Network/networkSecurityGroups/testnsg/securityRules/rule1" --remove-allow-azure-load-balancer-inbound-rule true \
--remove-allow-internet-outbound-rule true --remove-allow-vnet-inbound-rule true --remove-allow-vnet-outbound-rule \
true --resource-group "rg1"
```
##### <a name="ParametersSecurityConfigurationsImport">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--network-manager-name**|string|The name of the network manager.|network_manager_name|networkManagerName|
|**--configuration-name**|string|The name of the network manager security Configuration.|configuration_name|configurationName|
|**--network-security-group-imports**|array|List of nsg uris.|network_security_group_imports|networkSecurityGroupImports|
|**--import-deny-rules-as-admin-rules**|boolean|Flag if import deny rules as admin rules.|import_deny_rules_as_admin_rules|importDenyRulesAsAdminRules|
|**--admin-security-configuration-uri**|string|Admin security configuration Uri.|admin_security_configuration_uri|adminSecurityConfigurationUri|
|**--remove-allow-vnet-inbound-rule**|boolean|Flag if need to remove allow vnet inbound rule.|remove_allow_vnet_inbound_rule|removeAllowVnetInboundRule|
|**--remove-allow-azure-load-balancer-inbound-rule**|boolean|Flag if need to remove allow azure load balancer inbound rule.|remove_allow_azure_load_balancer_inbound_rule|removeAllowAzureLoadBalancerInboundRule|
|**--remove-allow-vnet-outbound-rule**|boolean|Flag if need to remove allow vnet outbound rule.|remove_allow_vnet_outbound_rule|removeAllowVnetOutboundRule|
|**--remove-allow-internet-outbound-rule**|boolean|Flag if need to remove allow Internet outbound rule.|remove_allow_internet_outbound_rule|removeAllowInternetOutboundRule|

### group `az network manager user-rule`
#### <a name="UserRulesList">Command `az network manager user-rule list`</a>

##### <a name="ExamplesUserRulesList">Example</a>
```
az network manager user-rule list --configuration-name "myTestConnectivityConfig" --network-manager-name \
"testNetworkManager" --resource-group "rg1"
```
##### <a name="ParametersUserRulesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--network-manager-name**|string|The name of the network manager.|network_manager_name|networkManagerName|
|**--configuration-name**|string|The name of the network manager security Configuration.|configuration_name|configurationName|
|**--top**|integer|An optional query parameter which specifies the maximum number of records to be returned by the server.|top|$top|
|**--skip-token**|string|SkipToken is only used if a previous operation returned a partial result. If a previous response contains a nextLink element, the value of the nextLink element will include a skipToken parameter that specifies a starting point to use for subsequent calls.|skip_token|$skipToken|

#### <a name="UserRulesGet">Command `az network manager user-rule show`</a>

##### <a name="ExamplesUserRulesGet">Example</a>
```
az network manager user-rule show --configuration-name "myTestSecurityConfig" --network-manager-name \
"testNetworkManager" --resource-group "rg1" --rule-name "SampleUserRule"
```
##### <a name="ParametersUserRulesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--network-manager-name**|string|The name of the network manager.|network_manager_name|networkManagerName|
|**--configuration-name**|string|The name of the network manager security Configuration.|configuration_name|configurationName|
|**--rule-name**|string|The name of the rule.|rule_name|ruleName|

#### <a name="UserRulesCreateOrUpdate#Create">Command `az network manager user-rule create`</a>

##### <a name="ExamplesUserRulesCreateOrUpdate#Create">Example</a>
```
az network manager user-rule create --configuration-name "myTestSecurityConfig" --network-manager-name \
"testNetworkManager" --resource-group "rg1" --rule-name "SampleUserRule" --description "Sample User Rule" \
--destination address-prefix="*" address-prefix-type="IPPrefix" --destination-port-ranges "22" --direction "Inbound" \
--source address-prefix="*" address-prefix-type="IPPrefix" --source-port-ranges "0-65535" --protocol "Tcp"
```
##### <a name="ParametersUserRulesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--network-manager-name**|string|The name of the network manager.|network_manager_name|networkManagerName|
|**--configuration-name**|string|The name of the network manager security Configuration.|configuration_name|configurationName|
|**--rule-name**|string|The name of the rule.|rule_name|ruleName|
|**--display-name**|string|A friendly name for the rule.|display_name|displayName|
|**--description**|string|A description for this rule. Restricted to 140 chars.|description|description|
|**--protocol**|choice|Network protocol this rule applies to.|protocol|protocol|
|**--source**|array|The CIDR or source IP ranges.|source|source|
|**--destination**|array|The destination address prefixes. CIDR or destination IP ranges.|destination|destination|
|**--source-port-ranges**|array|The source port ranges.|source_port_ranges|sourcePortRanges|
|**--destination-port-ranges**|array|The destination port ranges.|destination_port_ranges|destinationPortRanges|
|**--direction**|choice|Indicates if the traffic matched against the rule in inbound or outbound.|direction|direction|

#### <a name="UserRulesCreateOrUpdate#Update">Command `az network manager user-rule update`</a>

##### <a name="ParametersUserRulesCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--network-manager-name**|string|The name of the network manager.|network_manager_name|networkManagerName|
|**--configuration-name**|string|The name of the network manager security Configuration.|configuration_name|configurationName|
|**--rule-name**|string|The name of the rule.|rule_name|ruleName|
|**--display-name**|string|A friendly name for the rule.|display_name|displayName|
|**--description**|string|A description for this rule. Restricted to 140 chars.|description|description|
|**--protocol**|choice|Network protocol this rule applies to.|protocol|protocol|
|**--source**|array|The CIDR or source IP ranges.|source|source|
|**--destination**|array|The destination address prefixes. CIDR or destination IP ranges.|destination|destination|
|**--source-port-ranges**|array|The source port ranges.|source_port_ranges|sourcePortRanges|
|**--destination-port-ranges**|array|The destination port ranges.|destination_port_ranges|destinationPortRanges|
|**--direction**|choice|Indicates if the traffic matched against the rule in inbound or outbound.|direction|direction|

#### <a name="UserRulesDelete">Command `az network manager user-rule delete`</a>

##### <a name="ExamplesUserRulesDelete">Example</a>
```
az network manager user-rule delete --configuration-name "myTestSecurityConfig" --network-manager-name \
"testNetworkManager" --resource-group "rg1" --rule-name "SampleUserRule"
```
##### <a name="ParametersUserRulesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--network-manager-name**|string|The name of the network manager.|network_manager_name|networkManagerName|
|**--configuration-name**|string|The name of the network manager security Configuration.|configuration_name|configurationName|
|**--rule-name**|string|The name of the rule.|rule_name|ruleName|
