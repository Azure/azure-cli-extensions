# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az offazure|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az offazure` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az offazure hyperv cluster|HyperVCluster|[commands](#CommandsInHyperVCluster)|
|az offazure hyperv host|HyperVHost|[commands](#CommandsInHyperVHost)|
|az offazure hyperv machine|HyperVMachines|[commands](#CommandsInHyperVMachines)|
|az offazure hyperv run-as-account|HyperVRunAsAccounts|[commands](#CommandsInHyperVRunAsAccounts)|
|az offazure hyperv site|HyperVSites|[commands](#CommandsInHyperVSites)|
|az offazure vmware machine|Machines|[commands](#CommandsInMachines)|
|az offazure vmware run-as-account|RunAsAccounts|[commands](#CommandsInRunAsAccounts)|
|az offazure vmware site|Sites|[commands](#CommandsInSites)|
|az offazure vmware vcenter|VCenter|[commands](#CommandsInVCenter)|

## COMMANDS
### <a name="CommandsInHyperVCluster">Commands in `az offazure hyperv cluster` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az offazure hyperv cluster list](#HyperVClusterGetAllClustersInSite)|GetAllClustersInSite|[Parameters](#ParametersHyperVClusterGetAllClustersInSite)|[Example](#ExamplesHyperVClusterGetAllClustersInSite)|
|[az offazure hyperv cluster show](#HyperVClusterGetCluster)|GetCluster|[Parameters](#ParametersHyperVClusterGetCluster)|[Example](#ExamplesHyperVClusterGetCluster)|

### <a name="CommandsInHyperVHost">Commands in `az offazure hyperv host` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az offazure hyperv host list](#HyperVHostGetAllHostsInSite)|GetAllHostsInSite|[Parameters](#ParametersHyperVHostGetAllHostsInSite)|[Example](#ExamplesHyperVHostGetAllHostsInSite)|
|[az offazure hyperv host show](#HyperVHostGetHost)|GetHost|[Parameters](#ParametersHyperVHostGetHost)|[Example](#ExamplesHyperVHostGetHost)|

### <a name="CommandsInHyperVMachines">Commands in `az offazure hyperv machine` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az offazure hyperv machine list](#HyperVMachinesGetAllMachinesInSite)|GetAllMachinesInSite|[Parameters](#ParametersHyperVMachinesGetAllMachinesInSite)|[Example](#ExamplesHyperVMachinesGetAllMachinesInSite)|
|[az offazure hyperv machine show](#HyperVMachinesGetMachine)|GetMachine|[Parameters](#ParametersHyperVMachinesGetMachine)|[Example](#ExamplesHyperVMachinesGetMachine)|

### <a name="CommandsInHyperVRunAsAccounts">Commands in `az offazure hyperv run-as-account` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az offazure hyperv run-as-account list](#HyperVRunAsAccountsGetAllRunAsAccountsInSite)|GetAllRunAsAccountsInSite|[Parameters](#ParametersHyperVRunAsAccountsGetAllRunAsAccountsInSite)|[Example](#ExamplesHyperVRunAsAccountsGetAllRunAsAccountsInSite)|
|[az offazure hyperv run-as-account show](#HyperVRunAsAccountsGetRunAsAccount)|GetRunAsAccount|[Parameters](#ParametersHyperVRunAsAccountsGetRunAsAccount)|[Example](#ExamplesHyperVRunAsAccountsGetRunAsAccount)|

### <a name="CommandsInHyperVSites">Commands in `az offazure hyperv site` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az offazure hyperv site show](#HyperVSitesGetSite)|GetSite|[Parameters](#ParametersHyperVSitesGetSite)|[Example](#ExamplesHyperVSitesGetSite)|
|[az offazure hyperv site create](#HyperVSitesPutSite)|PutSite|[Parameters](#ParametersHyperVSitesPutSite)|[Example](#ExamplesHyperVSitesPutSite)|
|[az offazure hyperv site delete](#HyperVSitesDeleteSite)|DeleteSite|[Parameters](#ParametersHyperVSitesDeleteSite)|[Example](#ExamplesHyperVSitesDeleteSite)|

### <a name="CommandsInMachines">Commands in `az offazure vmware machine` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az offazure vmware machine list](#MachinesGetAllMachinesInSite)|GetAllMachinesInSite|[Parameters](#ParametersMachinesGetAllMachinesInSite)|[Example](#ExamplesMachinesGetAllMachinesInSite)|
|[az offazure vmware machine show](#MachinesGetMachine)|GetMachine|[Parameters](#ParametersMachinesGetMachine)|[Example](#ExamplesMachinesGetMachine)|

### <a name="CommandsInRunAsAccounts">Commands in `az offazure vmware run-as-account` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az offazure vmware run-as-account list](#RunAsAccountsGetAllRunAsAccountsInSite)|GetAllRunAsAccountsInSite|[Parameters](#ParametersRunAsAccountsGetAllRunAsAccountsInSite)|[Example](#ExamplesRunAsAccountsGetAllRunAsAccountsInSite)|
|[az offazure vmware run-as-account show](#RunAsAccountsGetRunAsAccount)|GetRunAsAccount|[Parameters](#ParametersRunAsAccountsGetRunAsAccount)|[Example](#ExamplesRunAsAccountsGetRunAsAccount)|

### <a name="CommandsInSites">Commands in `az offazure vmware site` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az offazure vmware site show](#SitesGetSite)|GetSite|[Parameters](#ParametersSitesGetSite)|[Example](#ExamplesSitesGetSite)|
|[az offazure vmware site create](#SitesPutSite)|PutSite|[Parameters](#ParametersSitesPutSite)|[Example](#ExamplesSitesPutSite)|
|[az offazure vmware site delete](#SitesDeleteSite)|DeleteSite|[Parameters](#ParametersSitesDeleteSite)|[Example](#ExamplesSitesDeleteSite)|

### <a name="CommandsInVCenter">Commands in `az offazure vmware vcenter` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az offazure vmware vcenter list](#VCenterGetAllVCentersInSite)|GetAllVCentersInSite|[Parameters](#ParametersVCenterGetAllVCentersInSite)|[Example](#ExamplesVCenterGetAllVCentersInSite)|
|[az offazure vmware vcenter show](#VCenterGetVCenter)|GetVCenter|[Parameters](#ParametersVCenterGetVCenter)|[Example](#ExamplesVCenterGetVCenter)|


## COMMAND DETAILS

### group `az offazure hyperv cluster`
#### <a name="HyperVClusterGetAllClustersInSite">Command `az offazure hyperv cluster list`</a>

##### <a name="ExamplesHyperVClusterGetAllClustersInSite">Example</a>
```
az offazure hyperv cluster list --resource-group "ipsahoo-RI-121119" --site-name "hyperv121319c813site" \
--subscription-id "4bd2aa0f-2bd2-4d67-91a8-5a4533d58600"
```
##### <a name="ParametersHyperVClusterGetAllClustersInSite">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--subscription-id**|string|The ID of the target subscription.|subscription_id|subscriptionId|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--site-name**|string|Site name.|site_name|siteName|
|**--filter**|string||filter|$filter|

#### <a name="HyperVClusterGetCluster">Command `az offazure hyperv cluster show`</a>

##### <a name="ExamplesHyperVClusterGetCluster">Example</a>
```
az offazure hyperv cluster show --cluster-name "hypgqlclusrs1-ntdev-corp-micros-11e77b27-67cc-5e46-a5d8-0ff3dc2ef179" \
--resource-group "ipsahoo-RI-121119" --site-name "hyperv121319c813site" --subscription-id \
"4bd2aa0f-2bd2-4d67-91a8-5a4533d58600"
```
##### <a name="ParametersHyperVClusterGetCluster">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--subscription-id**|string|The ID of the target subscription.|subscription_id|subscriptionId|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--site-name**|string|Site name.|site_name|siteName|
|**--cluster-name**|string|Cluster ARM name.|cluster_name|clusterName|

### group `az offazure hyperv host`
#### <a name="HyperVHostGetAllHostsInSite">Command `az offazure hyperv host list`</a>

##### <a name="ExamplesHyperVHostGetAllHostsInSite">Example</a>
```
az offazure hyperv host list --resource-group "pajindTest" --site-name "appliance1e39site" --subscription-id \
"4bd2aa0f-2bd2-4d67-91a8-5a4533d58600"
```
##### <a name="ParametersHyperVHostGetAllHostsInSite">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--subscription-id**|string|The ID of the target subscription.|subscription_id|subscriptionId|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--site-name**|string|Site name.|site_name|siteName|
|**--filter**|string||filter|$filter|

#### <a name="HyperVHostGetHost">Command `az offazure hyperv host show`</a>

##### <a name="ExamplesHyperVHostGetHost">Example</a>
```
az offazure hyperv host show --host-name "bcdr-ewlab-46-ntdev-corp-micros-e4638031-3b19-5642-926d-385da60cfb8a" \
--resource-group "pajindTest" --site-name "appliance1e39site" --subscription-id "4bd2aa0f-2bd2-4d67-91a8-5a4533d58600"
```
##### <a name="ParametersHyperVHostGetHost">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--subscription-id**|string|The ID of the target subscription.|subscription_id|subscriptionId|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--site-name**|string|Site name.|site_name|siteName|
|**--host-name**|string|Host ARM name.|host_name|hostName|

### group `az offazure hyperv machine`
#### <a name="HyperVMachinesGetAllMachinesInSite">Command `az offazure hyperv machine list`</a>

##### <a name="ExamplesHyperVMachinesGetAllMachinesInSite">Example</a>
```
az offazure hyperv machine list --resource-group "pajindTest" --site-name "appliance1e39site" --subscription-id \
"4bd2aa0f-2bd2-4d67-91a8-5a4533d58600"
```
##### <a name="ParametersHyperVMachinesGetAllMachinesInSite">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--subscription-id**|string|The ID of the target subscription.|subscription_id|subscriptionId|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--site-name**|string|Site name.|site_name|siteName|
|**--filter**|string||filter|$filter|
|**--top**|integer||top|$top|
|**--continuation-token**|string|Optional parameter for continuation token.|continuation_token|continuationToken|
|**--total-record-count**|integer|Total count of machines in the given site.|total_record_count|totalRecordCount|

#### <a name="HyperVMachinesGetMachine">Command `az offazure hyperv machine show`</a>

##### <a name="ExamplesHyperVMachinesGetMachine">Example</a>
```
az offazure hyperv machine show --machine-name "96d27052-052b-48db-aa84-b9978eddbf5d" --resource-group "pajindTest" \
--site-name "appliance1e39site" --subscription-id "4bd2aa0f-2bd2-4d67-91a8-5a4533d58600"
```
##### <a name="ParametersHyperVMachinesGetMachine">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--subscription-id**|string|The ID of the target subscription.|subscription_id|subscriptionId|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--site-name**|string|Site name.|site_name|siteName|
|**--machine-name**|string|Machine ARM name.|machine_name|machineName|

### group `az offazure hyperv run-as-account`
#### <a name="HyperVRunAsAccountsGetAllRunAsAccountsInSite">Command `az offazure hyperv run-as-account list`</a>

##### <a name="ExamplesHyperVRunAsAccountsGetAllRunAsAccountsInSite">Example</a>
```
az offazure hyperv run-as-account list --resource-group "pajindTest" --site-name "appliance1e39site" --subscription-id \
"4bd2aa0f-2bd2-4d67-91a8-5a4533d58600"
```
##### <a name="ParametersHyperVRunAsAccountsGetAllRunAsAccountsInSite">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--subscription-id**|string|The ID of the target subscription.|subscription_id|subscriptionId|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--site-name**|string|Site name.|site_name|siteName|

#### <a name="HyperVRunAsAccountsGetRunAsAccount">Command `az offazure hyperv run-as-account show`</a>

##### <a name="ExamplesHyperVRunAsAccountsGetRunAsAccount">Example</a>
```
az offazure hyperv run-as-account show --account-name "account1" --resource-group "pajindTest" --site-name \
"appliance1e39site" --subscription-id "4bd2aa0f-2bd2-4d67-91a8-5a4533d58600"
```
##### <a name="ParametersHyperVRunAsAccountsGetRunAsAccount">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--subscription-id**|string|The ID of the target subscription.|subscription_id|subscriptionId|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--site-name**|string|Site name.|site_name|siteName|
|**--account-name**|string|Run as account ARM name.|account_name|accountName|

### group `az offazure hyperv site`
#### <a name="HyperVSitesGetSite">Command `az offazure hyperv site show`</a>

##### <a name="ExamplesHyperVSitesGetSite">Example</a>
```
az offazure hyperv site show --resource-group "pajindTest" --site-name "appliance1e39site" --subscription-id \
"4bd2aa0f-2bd2-4d67-91a8-5a4533d58600"
```
##### <a name="ParametersHyperVSitesGetSite">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--subscription-id**|string|The ID of the target subscription.|subscription_id|subscriptionId|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--site-name**|string|Site name.|site_name|siteName|

#### <a name="HyperVSitesPutSite">Command `az offazure hyperv site create`</a>

##### <a name="ExamplesHyperVSitesPutSite">Example</a>
```
az offazure hyperv site create --location "eastus" --service-principal-identity-details aad-authority="https://login.wi\
ndows.net/72f988bf-86f1-41af-91ab-2d7cd011db47" application-id="e9f013df-2a2a-4871-b766-e79867f30348" \
audience="https://72f988bf-86f1-41af-91ab-2d7cd011db47/MaheshSite17ac9agentauthaadapp" object-id="2cd492bc-7ef3-4ee0-b3\
01-59a88108b47b" tenant-id="72f988bf-86f1-41af-91ab-2d7cd011db47" --resource-group "pajindTest" --site-name \
"appliance1e39site" --subscription-id "4bd2aa0f-2bd2-4d67-91a8-5a4533d58600"
```
##### <a name="ParametersHyperVSitesPutSite">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--subscription-id**|string|The ID of the target subscription.|subscription_id|subscriptionId|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--site-name**|string|Site name.|site_name|siteName|
|**--name**|string|Name of the Hyper-V site.|name|name|
|**--tags**|dictionary|Dictionary of <string>|tags|tags|
|**--e-tag**|string|eTag for concurrency control.|e_tag|eTag|
|**--location**|string|Azure location in which Sites is created.|location|location|
|**--service-principal-identity-details**|object|Service principal identity details used by agent for communication to the service.|service_principal_identity_details|servicePrincipalIdentityDetails|
|**--agent-details**|object|On-premises agent details.|agent_details|agentDetails|
|**--discovery-solution-id**|string|ARM ID of migration hub solution for SDS.|discovery_solution_id|discoverySolutionId|
|**--appliance-name**|string|Appliance Name.|appliance_name|applianceName|

#### <a name="HyperVSitesDeleteSite">Command `az offazure hyperv site delete`</a>

##### <a name="ExamplesHyperVSitesDeleteSite">Example</a>
```
az offazure hyperv site delete --resource-group "pajindTest" --site-name "appliance1e39site" --subscription-id \
"4bd2aa0f-2bd2-4d67-91a8-5a4533d58600"
```
##### <a name="ParametersHyperVSitesDeleteSite">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--subscription-id**|string|The ID of the target subscription.|subscription_id|subscriptionId|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--site-name**|string|Site name.|site_name|siteName|

### group `az offazure vmware machine`
#### <a name="MachinesGetAllMachinesInSite">Command `az offazure vmware machine list`</a>

##### <a name="ExamplesMachinesGetAllMachinesInSite">Example</a>
```
az offazure vmware machine list --resource-group "myResourceGroup" --site-name "pajind_site1" --subscription-id \
"75dd7e42-4fd1-4512-af04-83ad9864335b"
```
##### <a name="ParametersMachinesGetAllMachinesInSite">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--subscription-id**|string|The ID of the target subscription.|subscription_id|subscriptionId|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--site-name**|string|Site name.|site_name|siteName|
|**--filter**|string||filter|$filter|
|**--top**|integer||top|$top|
|**--continuation-token**|string|Optional parameter for continuation token.|continuation_token|continuationToken|
|**--total-record-count**|integer|Total count of machines in the given site.|total_record_count|totalRecordCount|

#### <a name="MachinesGetMachine">Command `az offazure vmware machine show`</a>

##### <a name="ExamplesMachinesGetMachine">Example</a>
```
az offazure vmware machine show --name "machine1" --resource-group "myResourceGroup" --site-name "pajind_site1" \
--subscription-id "75dd7e42-4fd1-4512-af04-83ad9864335b"
```
##### <a name="ParametersMachinesGetMachine">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--subscription-id**|string|The ID of the target subscription.|subscription_id|subscriptionId|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--site-name**|string|Site name.|site_name|siteName|
|**--machine-name**|string|Machine ARM name.|machine_name|machineName|

### group `az offazure vmware run-as-account`
#### <a name="RunAsAccountsGetAllRunAsAccountsInSite">Command `az offazure vmware run-as-account list`</a>

##### <a name="ExamplesRunAsAccountsGetAllRunAsAccountsInSite">Example</a>
```
az offazure vmware run-as-account list --resource-group "myResourceGroup" --site-name "pajind_site1" --subscription-id \
"75dd7e42-4fd1-4512-af04-83ad9864335b"
```
##### <a name="ParametersRunAsAccountsGetAllRunAsAccountsInSite">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--subscription-id**|string|The ID of the target subscription.|subscription_id|subscriptionId|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--site-name**|string|Site name.|site_name|siteName|

#### <a name="RunAsAccountsGetRunAsAccount">Command `az offazure vmware run-as-account show`</a>

##### <a name="ExamplesRunAsAccountsGetRunAsAccount">Example</a>
```
az offazure vmware run-as-account show --account-name "account1" --resource-group "myResourceGroup" --site-name \
"pajind_site1" --subscription-id "75dd7e42-4fd1-4512-af04-83ad9864335b"
```
##### <a name="ParametersRunAsAccountsGetRunAsAccount">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--subscription-id**|string|The ID of the target subscription.|subscription_id|subscriptionId|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--site-name**|string|Site name.|site_name|siteName|
|**--account-name**|string|Run as account ARM name.|account_name|accountName|

### group `az offazure vmware site`
#### <a name="SitesGetSite">Command `az offazure vmware site show`</a>

##### <a name="ExamplesSitesGetSite">Example</a>
```
az offazure vmware site show --resource-group "myResourceGroup" --name "pajind_site1" --subscription-id \
"75dd7e42-4fd1-4512-af04-83ad9864335b"
```
##### <a name="ParametersSitesGetSite">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--subscription-id**|string|The ID of the target subscription.|subscription_id|subscriptionId|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--site-name**|string|Site name.|site_name|siteName|

#### <a name="SitesPutSite">Command `az offazure vmware site create`</a>

##### <a name="ExamplesSitesPutSite">Example</a>
```
az offazure vmware site create --location "eastus" --service-principal-identity-details aad-authority="https://login.wi\
ndows.net/72f988bf-86f1-41af-91ab-2d7cd011db47" application-id="e9f013df-2a2a-4871-b766-e79867f30348" \
audience="https://72f988bf-86f1-41af-91ab-2d7cd011db47/MaheshSite17ac9agentauthaadapp" object-id="2cd492bc-7ef3-4ee0-b3\
01-59a88108b47b" tenant-id="72f988bf-86f1-41af-91ab-2d7cd011db47" --resource-group "pajindTest" --site-name \
"appliance1e39site" --subscription-id "4bd2aa0f-2bd2-4d67-91a8-5a4533d58600"
```
##### <a name="ParametersSitesPutSite">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--subscription-id**|string|The ID of the target subscription.|subscription_id|subscriptionId|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--site-name**|string|Site name.|site_name|siteName|
|**--name**|string|Name of the VMware site.|name|name|
|**--tags**|dictionary|Dictionary of <string>|tags|tags|
|**--e-tag**|string|eTag for concurrency control.|e_tag|eTag|
|**--location**|string|Azure location in which Sites is created.|location|location|
|**--service-principal-identity-details**|object|Service principal identity details used by agent for communication to the service.|service_principal_identity_details|servicePrincipalIdentityDetails|
|**--agent-details**|object|On-premises agent details.|agent_details|agentDetails|
|**--discovery-solution-id**|string|ARM ID of migration hub solution for SDS.|discovery_solution_id|discoverySolutionId|
|**--appliance-name**|string|Appliance Name.|appliance_name|applianceName|

#### <a name="SitesDeleteSite">Command `az offazure vmware site delete`</a>

##### <a name="ExamplesSitesDeleteSite">Example</a>
```
az offazure vmware site delete --resource-group "myResourceGroup" --name "pajind_site1" --subscription-id \
"75dd7e42-4fd1-4512-af04-83ad9864335b"
```
##### <a name="ParametersSitesDeleteSite">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--subscription-id**|string|The ID of the target subscription.|subscription_id|subscriptionId|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--site-name**|string|Site name.|site_name|siteName|

### group `az offazure vmware vcenter`
#### <a name="VCenterGetAllVCentersInSite">Command `az offazure vmware vcenter list`</a>

##### <a name="ExamplesVCenterGetAllVCentersInSite">Example</a>
```
az offazure vmware vcenter list --resource-group "rahasijaBugBash050919" --site-name "rahasapp122119d37csite" \
--subscription-id "4bd2aa0f-2bd2-4d67-91a8-5a4533d58600"
```
##### <a name="ParametersVCenterGetAllVCentersInSite">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--subscription-id**|string|The ID of the target subscription.|subscription_id|subscriptionId|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--site-name**|string|Site name.|site_name|siteName|
|**--filter**|string||filter|$filter|

#### <a name="VCenterGetVCenter">Command `az offazure vmware vcenter show`</a>

##### <a name="ExamplesVCenterGetVCenter">Example</a>
```
az offazure vmware vcenter show --resource-group "rahasijaBugBash050919" --site-name "rahasapp122119d37csite" \
--subscription-id "4bd2aa0f-2bd2-4d67-91a8-5a4533d58600" --name "10-150-8-50-6af5f800-e9f6-56ff-9c3c-7be56d242c31"
```
##### <a name="ParametersVCenterGetVCenter">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--subscription-id**|string|The ID of the target subscription.|subscription_id|subscriptionId|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--site-name**|string|Site name.|site_name|siteName|
|**--vcenter-name**|string|VCenter ARM name.|vcenter_name|vcenterName|
