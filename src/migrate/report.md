# Azure CLI Module Creation Report

### migrate assessed-machines list

list a migrate assessed-machines.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### migrate assessed-machines show

show a migrate assessed-machines.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### migrate assessment-options show

show a migrate assessment-options.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### migrate assessments create

create a migrate assessments.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--azure-location**|choice|Target Azure location for which the machines should be assessed. These enums are the same as used by Compute API.|/something/my_option|/something/myOption|
|**--azure-offer-code**|choice|Offer code according to which cost estimation is done.|/something/my_option|/something/myOption|
|**--azure-pricing-tier**|choice|Pricing tier for Size evaluation.|/something/my_option|/something/myOption|
|**--azure-storage-redundancy**|choice|Storage Redundancy type offered by Azure.|/something/my_option|/something/myOption|
|**--scaling-factor**|number|Scaling factor used over utilization data to add a performance buffer for new machines to be created in Azure. Min Value = 1.0, Max value = 1.9, Default = 1.3.|/something/my_option|/something/myOption|
|**--percentile**|choice|Percentile of performance data used to recommend Azure size.|/something/my_option|/something/myOption|
|**--time-range**|choice|Time range of performance data used to recommend a size.|/something/my_option|/something/myOption|
|**--stage**|choice|User configurable setting that describes the status of the assessment.|/something/my_option|/something/myOption|
|**--currency**|choice|Currency to report prices in.|/something/my_option|/something/myOption|
|**--azure-hybrid-use-benefit**|choice|AHUB discount on windows virtual machines.|/something/my_option|/something/myOption|
|**--discount-percentage**|number|Custom discount percentage to be applied on final costs. Can be in the range [0, 100].|/something/my_option|/something/myOption|
|**--sizing-criterion**|choice|Assessment sizing criterion.|/something/my_option|/something/myOption|
|--assessment**|object|New or Updated Assessment object.|/something/my_option|/something/myOption|
|--e-tag**|string|For optimistic concurrency control.|/something/my_option|/something/myOption|
### migrate assessments delete

delete a migrate assessments.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### migrate assessments get-report-download-url

get-report-download-url a migrate assessments.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### migrate assessments list

list a migrate assessments.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### migrate assessments show

show a migrate assessments.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### migrate groups create

create a migrate groups.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--machines**|array|List of machine names that are part of this group.|/something/my_option|/something/myOption|
|--group**|object|New or Updated Group object.|/something/my_option|/something/myOption|
|--e-tag**|string|For optimistic concurrency control.|/something/my_option|/something/myOption|
### migrate groups delete

delete a migrate groups.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### migrate groups list

list a migrate groups.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### migrate groups show

show a migrate groups.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### migrate location check-name-availability

check-name-availability a migrate location.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--parameters**|object|Properties needed to check the availability of a name.|/something/my_option|/something/myOption|
|**--name**|string|The name to check for availability|/something/my_option|/something/myOption|
|**--type**|constant|The resource type. Must be set to Microsoft.Migrate/projects|/something/my_option|/something/myOption|
### migrate machines list

list a migrate machines.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### migrate machines show

show a migrate machines.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### migrate operations list

list a migrate operations.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
### migrate projects create

create a migrate projects.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|--project**|object|New or Updated project object.|/something/my_option|/something/myOption|
|--e-tag**|string|For optimistic concurrency control.|/something/my_option|/something/myOption|
|--location**|string|Azure location in which project is created.|/something/my_option|/something/myOption|
|--customer-workspace-id**|string|ARM ID of the Service Map workspace created by user.|/something/my_option|/something/myOption|
|--customer-workspace-location**|string|Location of the Service Map workspace created by user.|/something/my_option|/something/myOption|
|--provisioning-state**|choice|Provisioning state of the project.|/something/my_option|/something/myOption|
### migrate projects delete

delete a migrate projects.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### migrate projects get-keys

get-keys a migrate projects.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### migrate projects list

list a migrate projects.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### migrate projects show

show a migrate projects.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### migrate projects update

update a migrate projects.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|--project**|object|New or Updated project object.|/something/my_option|/something/myOption|
|--e-tag**|string|For optimistic concurrency control.|/something/my_option|/something/myOption|
|--location**|string|Azure location in which project is created.|/something/my_option|/something/myOption|
|--customer-workspace-id**|string|ARM ID of the Service Map workspace created by user.|/something/my_option|/something/myOption|
|--customer-workspace-location**|string|Location of the Service Map workspace created by user.|/something/my_option|/something/myOption|
|--provisioning-state**|choice|Provisioning state of the project.|/something/my_option|/something/myOption|