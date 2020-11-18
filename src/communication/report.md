# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az communication|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az communication` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az communication|CommunicationService|[commands](#CommandsInCommunicationService)|
|az communication|OperationStatuses|[commands](#CommandsInOperationStatuses)|

## COMMANDS
### <a name="CommandsInOperationStatuses">Commands in `az communication` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az communication show-status](#OperationStatusesGet)|Get|[Parameters](#ParametersOperationStatusesGet)|[Example](#ExamplesOperationStatusesGet)|


## COMMAND DETAILS

### group `az communication`
#### <a name="OperationStatusesGet">Command `az communication show-status`</a>

##### <a name="ExamplesOperationStatusesGet">Example</a>
```
az communication show-status --operation-id "db5f291f-284d-46e9-9152-d5c83f7c14b8" --location "westus2"
```
##### <a name="ParametersOperationStatusesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location**|string|The Azure region|location|location|
|**--operation-id**|string|The ID of an ongoing async operation|operation_id|operationId|
