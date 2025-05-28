# Azure CLI Module Creation Report

### guestconfig guest-configuration-assignment create

create a guestconfig guest-configuration-assignment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--guest-configuration-assignment-name**|string|Name of the guest configuration assignment.|guest_configuration_assignment_name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--vm-name**|string|The name of the virtual machine.|vm_name|
|**--name**|string|Name of the guest configuration assignment.|name|
|**--location**|string|Region where the VM is located.|location|
|**--context**|string|The source which initiated the guest configuration assignment. Ex: Azure Policy|context|
|**--latest-assignment-report-assignment**|object|Configuration details of the guest configuration assignment.|assignment|
|**--guest-configuration-name**|string|Name of the guest configuration.|name_properties_guest_configuration_name|
|**--guest-configuration-version**|string|Version of the guest configuration.|version|
|**--guest-configuration-configuration-parameter**|array|The configuration parameters for the guest configuration.|configuration_parameter|
|**--guest-configuration-configuration-setting**|object|The configuration setting for the guest configuration.|configuration_setting|
### guestconfig guest-configuration-assignment delete

delete a guestconfig guest-configuration-assignment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--guest-configuration-assignment-name**|string|Name of the guest configuration assignment|guest_configuration_assignment_name|
|**--vm-name**|string|The name of the virtual machine.|vm_name|
### guestconfig guest-configuration-assignment list

list a guestconfig guest-configuration-assignment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--vm-name**|string|The name of the virtual machine.|vm_name|
### guestconfig guest-configuration-assignment show

show a guestconfig guest-configuration-assignment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--guest-configuration-assignment-name**|string|The guest configuration assignment name.|guest_configuration_assignment_name|
|**--vm-name**|string|The name of the virtual machine.|vm_name|
### guestconfig guest-configuration-assignment update

create a guestconfig guest-configuration-assignment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--guest-configuration-assignment-name**|string|Name of the guest configuration assignment.|guest_configuration_assignment_name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--vm-name**|string|The name of the virtual machine.|vm_name|
|**--name**|string|Name of the guest configuration assignment.|name|
|**--location**|string|Region where the VM is located.|location|
|**--context**|string|The source which initiated the guest configuration assignment. Ex: Azure Policy|context|
|**--latest-assignment-report-assignment**|object|Configuration details of the guest configuration assignment.|assignment|
|**--guest-configuration-name**|string|Name of the guest configuration.|name_properties_guest_configuration_name|
|**--guest-configuration-version**|string|Version of the guest configuration.|version|
|**--guest-configuration-configuration-parameter**|array|The configuration parameters for the guest configuration.|configuration_parameter|
|**--guest-configuration-configuration-setting**|object|The configuration setting for the guest configuration.|configuration_setting|
### guestconfig guest-configuration-assignment-report list

list a guestconfig guest-configuration-assignment-report.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--guest-configuration-assignment-name**|string|The guest configuration assignment name.|guest_configuration_assignment_name|
|**--vm-name**|string|The name of the virtual machine.|vm_name|
### guestconfig guest-configuration-assignment-report show

show a guestconfig guest-configuration-assignment-report.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--guest-configuration-assignment-name**|string|The guest configuration assignment name.|guest_configuration_assignment_name|
|**--report-id**|string|The GUID for the guest configuration assignment report.|report_id|
|**--vm-name**|string|The name of the virtual machine.|vm_name|
### guestconfig guest-configuration-hcrp-assignment create

create a guestconfig guest-configuration-hcrp-assignment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--guest-configuration-assignment-name**|string|Name of the guest configuration assignment.|guest_configuration_assignment_name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--machine-name**|string|The name of the ARC machine.|machine_name|
|**--name**|string|Name of the guest configuration assignment.|name|
|**--location**|string|Region where the VM is located.|location|
|**--context**|string|The source which initiated the guest configuration assignment. Ex: Azure Policy|context|
|**--latest-assignment-report-assignment**|object|Configuration details of the guest configuration assignment.|assignment|
|**--guest-configuration-name**|string|Name of the guest configuration.|name_properties_guest_configuration_name|
|**--guest-configuration-version**|string|Version of the guest configuration.|version|
|**--guest-configuration-configuration-parameter**|array|The configuration parameters for the guest configuration.|configuration_parameter|
|**--guest-configuration-configuration-setting**|object|The configuration setting for the guest configuration.|configuration_setting|
### guestconfig guest-configuration-hcrp-assignment delete

delete a guestconfig guest-configuration-hcrp-assignment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--guest-configuration-assignment-name**|string|Name of the guest configuration assignment|guest_configuration_assignment_name|
|**--machine-name**|string|The name of the ARC machine.|machine_name|
### guestconfig guest-configuration-hcrp-assignment list

list a guestconfig guest-configuration-hcrp-assignment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--machine-name**|string|The name of the ARC machine.|machine_name|
### guestconfig guest-configuration-hcrp-assignment show

show a guestconfig guest-configuration-hcrp-assignment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--guest-configuration-assignment-name**|string|The guest configuration assignment name.|guest_configuration_assignment_name|
|**--machine-name**|string|The name of the ARC machine.|machine_name|
### guestconfig guest-configuration-hcrp-assignment update

create a guestconfig guest-configuration-hcrp-assignment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--guest-configuration-assignment-name**|string|Name of the guest configuration assignment.|guest_configuration_assignment_name|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--machine-name**|string|The name of the ARC machine.|machine_name|
|**--name**|string|Name of the guest configuration assignment.|name|
|**--location**|string|Region where the VM is located.|location|
|**--context**|string|The source which initiated the guest configuration assignment. Ex: Azure Policy|context|
|**--latest-assignment-report-assignment**|object|Configuration details of the guest configuration assignment.|assignment|
|**--guest-configuration-name**|string|Name of the guest configuration.|name_properties_guest_configuration_name|
|**--guest-configuration-version**|string|Version of the guest configuration.|version|
|**--guest-configuration-configuration-parameter**|array|The configuration parameters for the guest configuration.|configuration_parameter|
|**--guest-configuration-configuration-setting**|object|The configuration setting for the guest configuration.|configuration_setting|
### guestconfig guest-configuration-hcrp-assignment-report list

list a guestconfig guest-configuration-hcrp-assignment-report.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--guest-configuration-assignment-name**|string|The guest configuration assignment name.|guest_configuration_assignment_name|
|**--machine-name**|string|The name of the ARC machine.|machine_name|
### guestconfig guest-configuration-hcrp-assignment-report show

show a guestconfig guest-configuration-hcrp-assignment-report.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--guest-configuration-assignment-name**|string|The guest configuration assignment name.|guest_configuration_assignment_name|
|**--report-id**|string|The GUID for the guest configuration assignment report.|report_id|
|**--machine-name**|string|The name of the ARC machine.|machine_name|