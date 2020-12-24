# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az guestconfig|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az guestconfig` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az guestconfig guest-configuration-assignment|GuestConfigurationAssignments|[commands](#CommandsInGuestConfigurationAssignments)|
|az guestconfig guest-configuration-assignment-report|GuestConfigurationAssignmentReports|[commands](#CommandsInGuestConfigurationAssignmentReports)|
|az guestconfig guest-configuration-hcrp-assignment|GuestConfigurationHCRPAssignments|[commands](#CommandsInGuestConfigurationHCRPAssignments)|
|az guestconfig guest-configuration-hcrp-assignment-report|GuestConfigurationHCRPAssignmentReports|[commands](#CommandsInGuestConfigurationHCRPAssignmentReports)|

## COMMANDS
### <a name="CommandsInGuestConfigurationAssignments">Commands in `az guestconfig guest-configuration-assignment` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az guestconfig guest-configuration-assignment list](#GuestConfigurationAssignmentsList)|List|[Parameters](#ParametersGuestConfigurationAssignmentsList)|[Example](#ExamplesGuestConfigurationAssignmentsList)|
|[az guestconfig guest-configuration-assignment show](#GuestConfigurationAssignmentsGet)|Get|[Parameters](#ParametersGuestConfigurationAssignmentsGet)|[Example](#ExamplesGuestConfigurationAssignmentsGet)|

### <a name="CommandsInGuestConfigurationAssignmentReports">Commands in `az guestconfig guest-configuration-assignment-report` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az guestconfig guest-configuration-assignment-report list](#GuestConfigurationAssignmentReportsList)|List|[Parameters](#ParametersGuestConfigurationAssignmentReportsList)|[Example](#ExamplesGuestConfigurationAssignmentReportsList)|
|[az guestconfig guest-configuration-assignment-report show](#GuestConfigurationAssignmentReportsGet)|Get|[Parameters](#ParametersGuestConfigurationAssignmentReportsGet)|[Example](#ExamplesGuestConfigurationAssignmentReportsGet)|

### <a name="CommandsInGuestConfigurationHCRPAssignments">Commands in `az guestconfig guest-configuration-hcrp-assignment` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az guestconfig guest-configuration-hcrp-assignment list](#GuestConfigurationHCRPAssignmentsList)|List|[Parameters](#ParametersGuestConfigurationHCRPAssignmentsList)|[Example](#ExamplesGuestConfigurationHCRPAssignmentsList)|
|[az guestconfig guest-configuration-hcrp-assignment show](#GuestConfigurationHCRPAssignmentsGet)|Get|[Parameters](#ParametersGuestConfigurationHCRPAssignmentsGet)|[Example](#ExamplesGuestConfigurationHCRPAssignmentsGet)|

### <a name="CommandsInGuestConfigurationHCRPAssignmentReports">Commands in `az guestconfig guest-configuration-hcrp-assignment-report` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az guestconfig guest-configuration-hcrp-assignment-report list](#GuestConfigurationHCRPAssignmentReportsList)|List|[Parameters](#ParametersGuestConfigurationHCRPAssignmentReportsList)|[Example](#ExamplesGuestConfigurationHCRPAssignmentReportsList)|
|[az guestconfig guest-configuration-hcrp-assignment-report show](#GuestConfigurationHCRPAssignmentReportsGet)|Get|[Parameters](#ParametersGuestConfigurationHCRPAssignmentReportsGet)|[Example](#ExamplesGuestConfigurationHCRPAssignmentReportsGet)|


## COMMAND DETAILS

### group `az guestconfig guest-configuration-assignment`
#### <a name="GuestConfigurationAssignmentsList">Command `az guestconfig guest-configuration-assignment list`</a>

##### <a name="ExamplesGuestConfigurationAssignmentsList">Example</a>
```
az guestconfig guest-configuration-assignment list --resource-group "myResourceGroupName" --vm-name "myVMName"
```
##### <a name="ParametersGuestConfigurationAssignmentsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--vm-name**|string|The name of the virtual machine.|vm_name|vmName|

#### <a name="GuestConfigurationAssignmentsGet">Command `az guestconfig guest-configuration-assignment show`</a>

##### <a name="ExamplesGuestConfigurationAssignmentsGet">Example</a>
```
az guestconfig guest-configuration-assignment show --name "SecureProtocol" --resource-group "myResourceGroupName" \
--vm-name "myVMName"
```
##### <a name="ParametersGuestConfigurationAssignmentsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--guest-configuration-assignment-name**|string|The guest configuration assignment name.|guest_configuration_assignment_name|guestConfigurationAssignmentName|
|**--vm-name**|string|The name of the virtual machine.|vm_name|vmName|

### group `az guestconfig guest-configuration-assignment-report`
#### <a name="GuestConfigurationAssignmentReportsList">Command `az guestconfig guest-configuration-assignment-report list`</a>

##### <a name="ExamplesGuestConfigurationAssignmentReportsList">Example</a>
```
az guestconfig guest-configuration-assignment-report list --guest-configuration-assignment-name "AuditSecureProtocol" \
--resource-group "myResourceGroupName" --vm-name "myVMName"
```
##### <a name="ParametersGuestConfigurationAssignmentReportsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--guest-configuration-assignment-name**|string|The guest configuration assignment name.|guest_configuration_assignment_name|guestConfigurationAssignmentName|
|**--vm-name**|string|The name of the virtual machine.|vm_name|vmName|

#### <a name="GuestConfigurationAssignmentReportsGet">Command `az guestconfig guest-configuration-assignment-report show`</a>

##### <a name="ExamplesGuestConfigurationAssignmentReportsGet">Example</a>
```
az guestconfig guest-configuration-assignment-report show --guest-configuration-assignment-name "AuditSecureProtocol" \
--report-id "7367cbb8-ae99-47d0-a33b-a283564d2cb1" --resource-group "myResourceGroupName" --vm-name "myvm"
```
##### <a name="ParametersGuestConfigurationAssignmentReportsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--guest-configuration-assignment-name**|string|The guest configuration assignment name.|guest_configuration_assignment_name|guestConfigurationAssignmentName|
|**--report-id**|string|The GUID for the guest configuration assignment report.|report_id|reportId|
|**--vm-name**|string|The name of the virtual machine.|vm_name|vmName|

### group `az guestconfig guest-configuration-hcrp-assignment`
#### <a name="GuestConfigurationHCRPAssignmentsList">Command `az guestconfig guest-configuration-hcrp-assignment list`</a>

##### <a name="ExamplesGuestConfigurationHCRPAssignmentsList">Example</a>
```
az guestconfig guest-configuration-hcrp-assignment list --machine-name "myMachineName" --resource-group \
"myResourceGroupName"
```
##### <a name="ParametersGuestConfigurationHCRPAssignmentsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--machine-name**|string|The name of the ARC machine.|machine_name|machineName|

#### <a name="GuestConfigurationHCRPAssignmentsGet">Command `az guestconfig guest-configuration-hcrp-assignment show`</a>

##### <a name="ExamplesGuestConfigurationHCRPAssignmentsGet">Example</a>
```
az guestconfig guest-configuration-hcrp-assignment show --guest-configuration-assignment-name "SecureProtocol" \
--machine-name "myMachineName" --resource-group "myResourceGroupName"
```
##### <a name="ParametersGuestConfigurationHCRPAssignmentsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--guest-configuration-assignment-name**|string|The guest configuration assignment name.|guest_configuration_assignment_name|guestConfigurationAssignmentName|
|**--machine-name**|string|The name of the ARC machine.|machine_name|machineName|

### group `az guestconfig guest-configuration-hcrp-assignment-report`
#### <a name="GuestConfigurationHCRPAssignmentReportsList">Command `az guestconfig guest-configuration-hcrp-assignment-report list`</a>

##### <a name="ExamplesGuestConfigurationHCRPAssignmentReportsList">Example</a>
```
az guestconfig guest-configuration-hcrp-assignment-report list --guest-configuration-assignment-name \
"AuditSecureProtocol" --machine-name "myMachineName" --resource-group "myResourceGroupName"
```
##### <a name="ParametersGuestConfigurationHCRPAssignmentReportsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--guest-configuration-assignment-name**|string|The guest configuration assignment name.|guest_configuration_assignment_name|guestConfigurationAssignmentName|
|**--machine-name**|string|The name of the ARC machine.|machine_name|machineName|

#### <a name="GuestConfigurationHCRPAssignmentReportsGet">Command `az guestconfig guest-configuration-hcrp-assignment-report show`</a>

##### <a name="ExamplesGuestConfigurationHCRPAssignmentReportsGet">Example</a>
```
az guestconfig guest-configuration-hcrp-assignment-report show --guest-configuration-assignment-name \
"AuditSecureProtocol" --machine-name "myMachineName" --report-id "7367cbb8-ae99-47d0-a33b-a283564d2cb1" \
--resource-group "myResourceGroupName"
```
##### <a name="ParametersGuestConfigurationHCRPAssignmentReportsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--guest-configuration-assignment-name**|string|The guest configuration assignment name.|guest_configuration_assignment_name|guestConfigurationAssignmentName|
|**--report-id**|string|The GUID for the guest configuration assignment report.|report_id|reportId|
|**--machine-name**|string|The name of the ARC machine.|machine_name|machineName|
