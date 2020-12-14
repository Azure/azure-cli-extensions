# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az postgresqlhsc|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az postgresqlhsc` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az postgresqlhsc server-group|ServerGroups|[commands](#CommandsInServerGroups)|
|az postgresqlhsc server|Servers|[commands](#CommandsInServers)|
|az postgresqlhsc configuration|Configurations|[commands](#CommandsInConfigurations)|
|az postgresqlhsc firewall-rule|FirewallRules|[commands](#CommandsInFirewallRules)|
|az postgresqlhsc role|Roles|[commands](#CommandsInRoles)|

## COMMANDS
### <a name="CommandsInConfigurations">Commands in `az postgresqlhsc configuration` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az postgresqlhsc configuration list](#ConfigurationsListByServer)|ListByServer|[Parameters](#ParametersConfigurationsListByServer)|[Example](#ExamplesConfigurationsListByServer)|
|[az postgresqlhsc configuration list](#ConfigurationsListByServerGroup)|ListByServerGroup|[Parameters](#ParametersConfigurationsListByServerGroup)|[Example](#ExamplesConfigurationsListByServerGroup)|
|[az postgresqlhsc configuration show](#ConfigurationsGet)|Get|[Parameters](#ParametersConfigurationsGet)|[Example](#ExamplesConfigurationsGet)|
|[az postgresqlhsc configuration update](#ConfigurationsUpdate)|Update|[Parameters](#ParametersConfigurationsUpdate)|[Example](#ExamplesConfigurationsUpdate)|

### <a name="CommandsInFirewallRules">Commands in `az postgresqlhsc firewall-rule` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az postgresqlhsc firewall-rule list](#FirewallRulesListByServerGroup)|ListByServerGroup|[Parameters](#ParametersFirewallRulesListByServerGroup)|[Example](#ExamplesFirewallRulesListByServerGroup)|
|[az postgresqlhsc firewall-rule show](#FirewallRulesGet)|Get|[Parameters](#ParametersFirewallRulesGet)|[Example](#ExamplesFirewallRulesGet)|
|[az postgresqlhsc firewall-rule create](#FirewallRulesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersFirewallRulesCreateOrUpdate#Create)|[Example](#ExamplesFirewallRulesCreateOrUpdate#Create)|
|[az postgresqlhsc firewall-rule update](#FirewallRulesCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersFirewallRulesCreateOrUpdate#Update)|Not Found|
|[az postgresqlhsc firewall-rule delete](#FirewallRulesDelete)|Delete|[Parameters](#ParametersFirewallRulesDelete)|[Example](#ExamplesFirewallRulesDelete)|

### <a name="CommandsInRoles">Commands in `az postgresqlhsc role` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az postgresqlhsc role list](#RolesListByServerGroup)|ListByServerGroup|[Parameters](#ParametersRolesListByServerGroup)|[Example](#ExamplesRolesListByServerGroup)|
|[az postgresqlhsc role create](#RolesCreate)|Create|[Parameters](#ParametersRolesCreate)|[Example](#ExamplesRolesCreate)|
|[az postgresqlhsc role delete](#RolesDelete)|Delete|[Parameters](#ParametersRolesDelete)|[Example](#ExamplesRolesDelete)|

### <a name="CommandsInServers">Commands in `az postgresqlhsc server` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az postgresqlhsc server list](#ServersListByServerGroup)|ListByServerGroup|[Parameters](#ParametersServersListByServerGroup)|[Example](#ExamplesServersListByServerGroup)|
|[az postgresqlhsc server show](#ServersGet)|Get|[Parameters](#ParametersServersGet)|[Example](#ExamplesServersGet)|

### <a name="CommandsInServerGroups">Commands in `az postgresqlhsc server-group` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az postgresqlhsc server-group list](#ServerGroupsListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersServerGroupsListByResourceGroup)|[Example](#ExamplesServerGroupsListByResourceGroup)|
|[az postgresqlhsc server-group list](#ServerGroupsList)|List|[Parameters](#ParametersServerGroupsList)|[Example](#ExamplesServerGroupsList)|
|[az postgresqlhsc server-group show](#ServerGroupsGet)|Get|[Parameters](#ParametersServerGroupsGet)|[Example](#ExamplesServerGroupsGet)|
|[az postgresqlhsc server-group create](#ServerGroupsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersServerGroupsCreateOrUpdate#Create)|[Example](#ExamplesServerGroupsCreateOrUpdate#Create)|
|[az postgresqlhsc server-group update](#ServerGroupsUpdate)|Update|[Parameters](#ParametersServerGroupsUpdate)|[Example](#ExamplesServerGroupsUpdate)|
|[az postgresqlhsc server-group delete](#ServerGroupsDelete)|Delete|[Parameters](#ParametersServerGroupsDelete)|[Example](#ExamplesServerGroupsDelete)|
|[az postgresqlhsc server-group restart](#ServerGroupsRestart)|Restart|[Parameters](#ParametersServerGroupsRestart)|[Example](#ExamplesServerGroupsRestart)|
|[az postgresqlhsc server-group start](#ServerGroupsStart)|Start|[Parameters](#ParametersServerGroupsStart)|[Example](#ExamplesServerGroupsStart)|
|[az postgresqlhsc server-group stop](#ServerGroupsStop)|Stop|[Parameters](#ParametersServerGroupsStop)|[Example](#ExamplesServerGroupsStop)|


## COMMAND DETAILS

### group `az postgresqlhsc configuration`
#### <a name="ConfigurationsListByServer">Command `az postgresqlhsc configuration list`</a>

##### <a name="ExamplesConfigurationsListByServer">Example</a>
```
az postgresqlhsc configuration list --resource-group "TestResourceGroup" --server-group-name "hsctestsg" --server-name \
"testserver"
```
##### <a name="ParametersConfigurationsListByServer">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--server-group-name**|string|The name of the server group.|server_group_name|serverGroupName|
|**--server-name**|string|The name of the server.|server_name|serverName|

#### <a name="ConfigurationsListByServerGroup">Command `az postgresqlhsc configuration list`</a>

##### <a name="ExamplesConfigurationsListByServerGroup">Example</a>
```
az postgresqlhsc configuration list --resource-group "TestResourceGroup" --server-group-name "hsctestsg"
```
##### <a name="ParametersConfigurationsListByServerGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="ConfigurationsGet">Command `az postgresqlhsc configuration show`</a>

##### <a name="ExamplesConfigurationsGet">Example</a>
```
az postgresqlhsc configuration show --name "array_nulls" --resource-group "TestResourceGroup" --server-group-name \
"hsctestsg"
```
##### <a name="ParametersConfigurationsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--server-group-name**|string|The name of the server group.|server_group_name|serverGroupName|
|**--configuration-name**|string|The name of the server group configuration.|configuration_name|configurationName|

#### <a name="ConfigurationsUpdate">Command `az postgresqlhsc configuration update`</a>

##### <a name="ExamplesConfigurationsUpdate">Example</a>
```
az postgresqlhsc configuration update --name "array_nulls" --server-role-group-configurations role="Coordinator" \
value="on" --server-role-group-configurations role="Worker" value="off" --resource-group "TestResourceGroup" \
--server-group-name "hsctestsg"
```
##### <a name="ParametersConfigurationsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--server-group-name**|string|The name of the server group.|server_group_name|serverGroupName|
|**--configuration-name**|string|The name of the server group configuration.|configuration_name|configurationName|
|**--server-role-group-configurations**|array|The list of server role group configuration values.|server_role_group_configurations|serverRoleGroupConfigurations|

### group `az postgresqlhsc firewall-rule`
#### <a name="FirewallRulesListByServerGroup">Command `az postgresqlhsc firewall-rule list`</a>

##### <a name="ExamplesFirewallRulesListByServerGroup">Example</a>
```
az postgresqlhsc firewall-rule list --resource-group "TestGroup" --server-group-name "pgtestsvc4"
```
##### <a name="ParametersFirewallRulesListByServerGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--server-group-name**|string|The name of the server group.|server_group_name|serverGroupName|

#### <a name="FirewallRulesGet">Command `az postgresqlhsc firewall-rule show`</a>

##### <a name="ExamplesFirewallRulesGet">Example</a>
```
az postgresqlhsc firewall-rule show --name "rule1" --resource-group "TestGroup" --server-group-name "pgtestsvc4"
```
##### <a name="ParametersFirewallRulesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--server-group-name**|string|The name of the server group.|server_group_name|serverGroupName|
|**--firewall-rule-name**|string|The name of the server group firewall rule.|firewall_rule_name|firewallRuleName|

#### <a name="FirewallRulesCreateOrUpdate#Create">Command `az postgresqlhsc firewall-rule create`</a>

##### <a name="ExamplesFirewallRulesCreateOrUpdate#Create">Example</a>
```
az postgresqlhsc firewall-rule create --name "rule1" --end-ip-address "255.255.255.255" --start-ip-address "0.0.0.0" \
--resource-group "TestGroup" --server-group-name "pgtestsvc4"
```
##### <a name="ParametersFirewallRulesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--server-group-name**|string|The name of the server group.|server_group_name|serverGroupName|
|**--firewall-rule-name**|string|The name of the server group firewall rule.|firewall_rule_name|firewallRuleName|
|**--start-ip-address**|string|The start IP address of the server group firewall rule. Must be IPv4 format.|start_ip_address|startIpAddress|
|**--end-ip-address**|string|The end IP address of the server group firewall rule. Must be IPv4 format.|end_ip_address|endIpAddress|

#### <a name="FirewallRulesCreateOrUpdate#Update">Command `az postgresqlhsc firewall-rule update`</a>

##### <a name="ParametersFirewallRulesCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--server-group-name**|string|The name of the server group.|server_group_name|serverGroupName|
|**--firewall-rule-name**|string|The name of the server group firewall rule.|firewall_rule_name|firewallRuleName|
|**--start-ip-address**|string|The start IP address of the server group firewall rule. Must be IPv4 format.|start_ip_address|startIpAddress|
|**--end-ip-address**|string|The end IP address of the server group firewall rule. Must be IPv4 format.|end_ip_address|endIpAddress|

#### <a name="FirewallRulesDelete">Command `az postgresqlhsc firewall-rule delete`</a>

##### <a name="ExamplesFirewallRulesDelete">Example</a>
```
az postgresqlhsc firewall-rule delete --name "rule1" --resource-group "TestGroup" --server-group-name "pgtestsvc4"
```
##### <a name="ParametersFirewallRulesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--server-group-name**|string|The name of the server group.|server_group_name|serverGroupName|
|**--firewall-rule-name**|string|The name of the server group firewall rule.|firewall_rule_name|firewallRuleName|

### group `az postgresqlhsc role`
#### <a name="RolesListByServerGroup">Command `az postgresqlhsc role list`</a>

##### <a name="ExamplesRolesListByServerGroup">Example</a>
```
az postgresqlhsc role list --resource-group "TestGroup" --server-group-name "pgtestsvc4"
```
##### <a name="ParametersRolesListByServerGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--server-group-name**|string|The name of the server group.|server_group_name|serverGroupName|

#### <a name="RolesCreate">Command `az postgresqlhsc role create`</a>

##### <a name="ExamplesRolesCreate">Example</a>
```
az postgresqlhsc role create --password "secret" --resource-group "TestGroup" --name "role1" --server-group-name \
"pgtestsvc4"
```
##### <a name="ParametersRolesCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--server-group-name**|string|The name of the server group.|server_group_name|serverGroupName|
|**--role-name**|string|The name of the server group role name.|role_name|roleName|
|**--password**|credential|The password of the server group role.|password|password|

#### <a name="RolesDelete">Command `az postgresqlhsc role delete`</a>

##### <a name="ExamplesRolesDelete">Example</a>
```
az postgresqlhsc role delete --resource-group "TestGroup" --name "role1" --server-group-name "pgtestsvc4"
```
##### <a name="ParametersRolesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--server-group-name**|string|The name of the server group.|server_group_name|serverGroupName|
|**--role-name**|string|The name of the server group role name.|role_name|roleName|

### group `az postgresqlhsc server`
#### <a name="ServersListByServerGroup">Command `az postgresqlhsc server list`</a>

##### <a name="ExamplesServersListByServerGroup">Example</a>
```
az postgresqlhsc server list --resource-group "TestGroup" --server-group-name "hsctestsg1"
```
##### <a name="ParametersServersListByServerGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--server-group-name**|string|The name of the server group.|server_group_name|serverGroupName|

#### <a name="ServersGet">Command `az postgresqlhsc server show`</a>

##### <a name="ExamplesServersGet">Example</a>
```
az postgresqlhsc server show --resource-group "TestGroup" --server-group-name "hsctestsg1" --name "hsctestsg1-c"
```
##### <a name="ParametersServersGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--server-group-name**|string|The name of the server group.|server_group_name|serverGroupName|
|**--server-name**|string|The name of the server.|server_name|serverName|

### group `az postgresqlhsc server-group`
#### <a name="ServerGroupsListByResourceGroup">Command `az postgresqlhsc server-group list`</a>

##### <a name="ExamplesServerGroupsListByResourceGroup">Example</a>
```
az postgresqlhsc server-group list --resource-group "TestGroup"
```
##### <a name="ParametersServerGroupsListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="ServerGroupsList">Command `az postgresqlhsc server-group list`</a>

##### <a name="ExamplesServerGroupsList">Example</a>
```
az postgresqlhsc server-group list
```
##### <a name="ParametersServerGroupsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="ServerGroupsGet">Command `az postgresqlhsc server-group show`</a>

##### <a name="ExamplesServerGroupsGet">Example</a>
```
az postgresqlhsc server-group show --resource-group "TestGroup" --name "hsctestsg1"
```
##### <a name="ParametersServerGroupsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--server-group-name**|string|The name of the server group.|server_group_name|serverGroupName|

#### <a name="ServerGroupsCreateOrUpdate#Create">Command `az postgresqlhsc server-group create`</a>

##### <a name="ExamplesServerGroupsCreateOrUpdate#Create">Example</a>
```
az postgresqlhsc server-group create --location "westus" --administrator-login "citus" --administrator-login-password \
"password" --availability-zone "1" --backup-retention-days 35 --citus-version "9.5" --enable-mx true --enable-zfs \
false --postgresql-version "12" --server-role-groups name="" enable-ha=true role="Coordinator" server-count=1 \
server-edition="GeneralPurpose" storage-quota-in-mb=524288 v-cores=4 --server-role-groups name="" enable-ha=false \
role="Worker" server-count=3 server-edition="MemoryOptimized" storage-quota-in-mb=524288 v-cores=4 \
--standby-availability-zone "2" --tags ElasticServer="1" --resource-group "TestGroup" --name "hsctestsg"
```
##### <a name="ExamplesServerGroupsCreateOrUpdate#Create">Example</a>
```
az postgresqlhsc server-group create --location "westus" --create-mode "PointInTimeRestore" --enable-mx true \
--enable-zfs false --point-in-time-utc "2017-12-14T00:00:37.467Z" --source-location "eastus" \
--source-resource-group-name "SourceGroup" --source-server-group-name "pgtests-source-server-group" \
--source-subscription-id "dddddddd-dddd-dddd-dddd-dddddddddddd" --resource-group "TestGroup" --name "hsctestsg"
```
##### <a name="ParametersServerGroupsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--server-group-name**|string|The name of the server group.|server_group_name|serverGroupName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--create-mode**|choice|The mode to create a new server group.|create_mode|createMode|
|**--administrator-login**|string|The administrator's login name of servers in server group. Can only be specified when the server is being created (and is required for creation).|administrator_login|administratorLogin|
|**--administrator-login-password**|credential|The password of the administrator login.|administrator_login_password|administratorLoginPassword|
|**--backup-retention-days**|integer|The backup retention days for server group.|backup_retention_days|backupRetentionDays|
|**--postgresql-version**|choice|The PostgreSQL version of server group.|postgresql_version|postgresqlVersion|
|**--citus-version**|choice|The Citus version of server group.|citus_version|citusVersion|
|**--enable-mx**|boolean|If Citus MX is enabled or not for the server group.|enable_mx|enableMx|
|**--enable-zfs**|boolean|If ZFS compression is enabled or not for the server group.|enable_zfs|enableZfs|
|**--enable-shards-on-coordinator**|boolean|If shards on coordinator is enabled or not for the server group.|enable_shards_on_coordinator|enableShardsOnCoordinator|
|**--server-role-groups**|array|The list of server role groups.|server_role_groups|serverRoleGroups|
|**--maintenance-window**|object|Maintenance window of a server group.|maintenance_window|maintenanceWindow|
|**--availability-zone**|string|Availability Zone information of the server group.|availability_zone|availabilityZone|
|**--standby-availability-zone**|string|Standby Availability Zone information of the server group.|standby_availability_zone|standbyAvailabilityZone|
|**--source-subscription-id**|string|The source subscription id to restore from. It's required when 'createMode' is 'PointInTimeRestore'|source_subscription_id|sourceSubscriptionId|
|**--source-resource-group-name**|string|The source resource group name to restore from. It's required when 'createMode' is 'PointInTimeRestore'|source_resource_group_name|sourceResourceGroupName|
|**--source-server-group-name**|string|The source server group name to restore from. It's required when 'createMode' is 'PointInTimeRestore'|source_server_group_name|sourceServerGroupName|
|**--source-location**|string|The source server group location to restore from. It's required when 'createMode' is 'PointInTimeRestore'|source_location|sourceLocation|
|**--point-in-time-utc**|date-time|Restore point creation time (ISO8601 format), specifying the time to restore from. It's required when 'createMode' is 'PointInTimeRestore'|point_in_time_utc|pointInTimeUTC|
|**--delegated-subnet-arguments-subnet-arm-resource-id**|string|delegated subnet arm resource id.|subnet_arm_resource_id|subnetArmResourceId|

#### <a name="ServerGroupsUpdate">Command `az postgresqlhsc server-group update`</a>

##### <a name="ExamplesServerGroupsUpdate">Example</a>
```
az postgresqlhsc server-group update --location "westus" --server-role-groups name="" role="Worker" server-count=10 \
--resource-group "TestGroup" --name "hsctestsg"
```
##### <a name="ExamplesServerGroupsUpdate">Example</a>
```
az postgresqlhsc server-group update --location "westus" --server-role-groups name="" role="Coordinator" v-cores=16 \
--resource-group "TestGroup" --name "hsctestsg"
```
##### <a name="ExamplesServerGroupsUpdate">Example</a>
```
az postgresqlhsc server-group update --location "westus" --server-role-groups name="" role="Worker" \
storage-quota-in-mb=8388608 --resource-group "TestGroup" --name "hsctestsg"
```
##### <a name="ExamplesServerGroupsUpdate">Example</a>
```
az postgresqlhsc server-group update --maintenance-window custom-window="Enabled" day-of-week=0 start-hour=8 \
start-minute=0 --resource-group "TestGroup" --name "hsctestsg"
```
##### <a name="ExamplesServerGroupsUpdate">Example</a>
```
az postgresqlhsc server-group update --administrator-login-password "secret" --backup-retention-days 30 \
--postgresql-version "12" --server-role-groups name="" enable-ha=false role="Coordinator" server-count=1 \
server-edition="GeneralPurpose" storage-quota-in-mb=1048576 v-cores=8 --server-role-groups name="" enable-ha=true \
role="Worker" server-count=4 server-edition="MemoryOptimized" storage-quota-in-mb=524288 v-cores=4 --tags \
ElasticServer="2" --resource-group "TestGroup" --name "hsctestsg"
```
##### <a name="ParametersServerGroupsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--server-group-name**|string|The name of the server group.|server_group_name|serverGroupName|
|**--location**|string|The location the resource resides in.|location|location|
|**--tags**|dictionary|Application-specific metadata in the form of key-value pairs.|tags|tags|
|**--administrator-login-password**|credential|The password of the administrator login.|administrator_login_password|administratorLoginPassword|
|**--backup-retention-days**|integer|The backup retention days for server group.|backup_retention_days|backupRetentionDays|
|**--postgresql-version**|choice|The PostgreSQL version of server group.|postgresql_version|postgresqlVersion|
|**--citus-version**|choice|The Citus version of server group.|citus_version|citusVersion|
|**--enable-shards-on-coordinator**|boolean|If shards on coordinator is enabled or not for the server group.|enable_shards_on_coordinator|enableShardsOnCoordinator|
|**--server-role-groups**|array|The list of server role groups.|server_role_groups|serverRoleGroups|
|**--maintenance-window**|object|Maintenance window of a server group.|maintenance_window|maintenanceWindow|
|**--availability-zone**|string|Availability Zone information of the server group.|availability_zone|availabilityZone|
|**--standby-availability-zone**|string|Standby Availability Zone information of the server group.|standby_availability_zone|standbyAvailabilityZone|

#### <a name="ServerGroupsDelete">Command `az postgresqlhsc server-group delete`</a>

##### <a name="ExamplesServerGroupsDelete">Example</a>
```
az postgresqlhsc server-group delete --resource-group "TestGroup" --name "testservergroup"
```
##### <a name="ParametersServerGroupsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--server-group-name**|string|The name of the server group.|server_group_name|serverGroupName|

#### <a name="ServerGroupsRestart">Command `az postgresqlhsc server-group restart`</a>

##### <a name="ExamplesServerGroupsRestart">Example</a>
```
az postgresqlhsc server-group restart --resource-group "TestGroup" --name "hsctestsg1"
```
##### <a name="ParametersServerGroupsRestart">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--server-group-name**|string|The name of the server group.|server_group_name|serverGroupName|

#### <a name="ServerGroupsStart">Command `az postgresqlhsc server-group start`</a>

##### <a name="ExamplesServerGroupsStart">Example</a>
```
az postgresqlhsc server-group start --resource-group "TestGroup" --name "hsctestsg1"
```
##### <a name="ParametersServerGroupsStart">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--server-group-name**|string|The name of the server group.|server_group_name|serverGroupName|

#### <a name="ServerGroupsStop">Command `az postgresqlhsc server-group stop`</a>

##### <a name="ExamplesServerGroupsStop">Example</a>
```
az postgresqlhsc server-group stop --resource-group "TestGroup" --name "hsctestsg1"
```
##### <a name="ParametersServerGroupsStop">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--server-group-name**|string|The name of the server group.|server_group_name|serverGroupName|
