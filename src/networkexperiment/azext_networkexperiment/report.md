# Azure CLI Module Creation Report

## -

## networkexperiment experiment

### networkexperiment experiment create

create a networkexperiment experiment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|Name of the Resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--profile-name**|str|The Profile identifier associated with the Tenant and Partner|profile_name|profileName|
|**--name**|str|The Experiment identifier associated with the Experiment|experiment_name|experimentName|
|--location|str|Resource location.|/location|/location|
|--tags|dictionary|Resource tags.|/tags|/tags|
|--description|str|The description of the details or intents of the Experiment|/description|/properties/description|
|--endpoint-a-name|str|The name of the endpoint|/endpoint_a/name|/properties/endpointA/name|
|--endpoint-a-endpoint|str|The endpoint URL|/endpoint_a/endpoint|/properties/endpointA/endpoint|
|--endpoint-b-name|str|The name of the endpoint|/endpoint_b/name|/properties/endpointB/name|
|--endpoint-b-endpoint|str|The endpoint URL|/endpoint_b/endpoint|/properties/endpointB/endpoint|
|--enabled-state|str|The state of the Experiment|/enabled_state|/properties/enabledState|
|--resource-state|str|Resource status.|/resource_state|/properties/resourceState|

**Example: Creates an Experiment**

```
networkexperiment experiment create --resource-group rg1
        --profile-name Profile1
        --name Experiment1
        --description "this is my first experiment!"
        --endpoint-a-name "endpoint A"
        --endpoint-a-endpoint endpointA.net
        --endpoint-b-name "endpoint B"
        --endpoint-b-endpoint endpointB.net
        --enabled-state Enabled
```
### networkexperiment experiment update

update a networkexperiment experiment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|Name of the Resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--profile-name**|str|The Profile identifier associated with the Tenant and Partner|profile_name|profileName|
|**--name**|str|The Experiment identifier associated with the Experiment|experiment_name|experimentName|
|--location|str|Resource location.|/location|/location|
|--tags|dictionary|Resource tags.|/tags|/tags|
|--description|str|The description of the details or intents of the Experiment|/description|/properties/description|
|--endpoint-a-name|str|The name of the endpoint|/endpoint_a/name|/properties/endpointA/name|
|--endpoint-a-endpoint|str|The endpoint URL|/endpoint_a/endpoint|/properties/endpointA/endpoint|
|--endpoint-b-name|str|The name of the endpoint|/endpoint_b/name|/properties/endpointB/name|
|--endpoint-b-endpoint|str|The endpoint URL|/endpoint_b/endpoint|/properties/endpointB/endpoint|
|--enabled-state|str|The state of the Experiment|/enabled_state|/properties/enabledState|
|--resource-state|str|Resource status.|/resource_state|/properties/resourceState|

**Example: Updates an Experiment**

```
networkexperiment experiment update --resource-group rg1
        --profile-name Profile1
        --name Experiment1
        --description string
        --enabled-state Enabled
```
### networkexperiment experiment delete

delete a networkexperiment experiment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|Name of the Resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--profile-name**|str|The Profile identifier associated with the Tenant and Partner|profile_name|profileName|
|**--name**|str|The Experiment identifier associated with the Experiment|experiment_name|experimentName|

**Example: Deletes an Experiment**

```
networkexperiment experiment delete --resource-group rg1
        --profile-name Profile1
        --name Experiment1
```
### networkexperiment experiment list

list a networkexperiment experiment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|Name of the Resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--profile-name**|str|The Profile identifier associated with the Tenant and Partner|profile_name|profileName|
### networkexperiment experiment show

show a networkexperiment experiment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|Name of the Resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--profile-name**|str|The Profile identifier associated with the Tenant and Partner|profile_name|profileName|
|**--name**|str|The Experiment identifier associated with the Experiment|experiment_name|experimentName|
## networkexperiment profile

### networkexperiment profile create

create a networkexperiment profile.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--profile-name**|str|The Profile identifier associated with the Tenant and Partner|profile_name|profileName|
|**--name**|str|Name of the Resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|--location|str|Resource location.|/location|/location|
|--tags|dictionary|Resource tags.|/tags|/tags|
|--resource-state|str|Resource status.|/resource_state|/properties/resourceState|
|--enabled-state|str|The state of the Experiment|/enabled_state|/properties/enabledState|
|--etag|str|Gets a unique read-only string that changes whenever the resource is updated.|/etag|/etag|

**Example: Creates an NetworkExperiment Profile in a Resource Group**

```
networkexperiment profile create --profile-name Profile1
        --name rg1
        --location WestUs
        --enabled-state Enabled
```
### networkexperiment profile update

update a networkexperiment profile.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--profile-name**|str|The Profile identifier associated with the Tenant and Partner|profile_name|profileName|
|**--name**|str|Name of the Resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|--location|str|Resource location.|/location|/location|
|--tags|dictionary|Resource tags.|/tags|/tags|
|--resource-state|str|Resource status.|/resource_state|/properties/resourceState|
|--enabled-state|str|The state of the Experiment|/enabled_state|/properties/enabledState|
|--etag|str|Gets a unique read-only string that changes whenever the resource is updated.|/etag|/etag|

**Example: Updates an Experiment**

```
networkexperiment profile update --profile-name Profile1
        --name rg1
        --enabled-state Enabled
```
### networkexperiment profile delete

delete a networkexperiment profile.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--name**|str|Name of the Resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--profile-name**|str|The Profile identifier associated with the Tenant and Partner|profile_name|profileName|

**Example: Deletes an NetworkExperiment Profile by ProfileName**

```
networkexperiment profile delete --name rg1
        --profile-name Profile1
```
### networkexperiment profile list

list a networkexperiment profile.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--name**|str|Name of the Resource group within the Azure subscription.|resource_group_name|resourceGroupName|
### networkexperiment profile show

show a networkexperiment profile.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--name**|str|Name of the Resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--profile-name**|str|The Profile identifier associated with the Tenant and Partner|profile_name|profileName|