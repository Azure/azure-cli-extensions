# Azure CLI Module Creation Report

### migrateprojects database enumerate-database

enumerate-database a migrateprojects database.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|Name of the Azure Resource Group that migrate project is part of.|resource_group_name|resource_group_name|
|**--migrate_project_name**|string|Name of the Azure Migrate project.|migrate_project_name|migrate_project_name|
|**--continuation_token**|string|The continuation token.|continuation_token|continuation_token|
|**--page_size**|integer|The number of items to be returned in a single page. This value is honored only if it is less than the 100.|page_size|page_size|
### migrateprojects database show

show a migrateprojects database.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|Name of the Azure Resource Group that migrate project is part of.|resource_group_name|resource_group_name|
|**--migrate_project_name**|string|Name of the Azure Migrate project.|migrate_project_name|migrate_project_name|
|**--database_name**|string|Unique name of a database in Azure migration hub.|database_name|database_name|
### migrateprojects database-instance enumerate-database-instance

enumerate-database-instance a migrateprojects database-instance.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|Name of the Azure Resource Group that migrate project is part of.|resource_group_name|resource_group_name|
|**--migrate_project_name**|string|Name of the Azure Migrate project.|migrate_project_name|migrate_project_name|
|**--continuation_token**|string|The continuation token.|continuation_token|continuation_token|
|**--page_size**|integer|The number of items to be returned in a single page. This value is honored only if it is less than the 100.|page_size|page_size|
### migrateprojects database-instance show

show a migrateprojects database-instance.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|Name of the Azure Resource Group that migrate project is part of.|resource_group_name|resource_group_name|
|**--migrate_project_name**|string|Name of the Azure Migrate project.|migrate_project_name|migrate_project_name|
|**--database_instance_name**|string|Unique name of a database instance in Azure migration hub.|database_instance_name|database_instance_name|
### migrateprojects event delete

delete a migrateprojects event.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|Name of the Azure Resource Group that migrate project is part of.|resource_group_name|resource_group_name|
|**--migrate_project_name**|string|Name of the Azure Migrate project.|migrate_project_name|migrate_project_name|
|**--event_name**|string|Unique name of an event within a migrate project.|event_name|event_name|
### migrateprojects event enumerate-event

enumerate-event a migrateprojects event.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|Name of the Azure Resource Group that migrate project is part of.|resource_group_name|resource_group_name|
|**--migrate_project_name**|string|Name of the Azure Migrate project.|migrate_project_name|migrate_project_name|
|**--continuation_token**|string|The continuation token.|continuation_token|continuation_token|
|**--page_size**|integer|The number of items to be returned in a single page. This value is honored only if it is less than the 100.|page_size|page_size|
### migrateprojects event show

show a migrateprojects event.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|Name of the Azure Resource Group that migrate project is part of.|resource_group_name|resource_group_name|
|**--migrate_project_name**|string|Name of the Azure Migrate project.|migrate_project_name|migrate_project_name|
|**--event_name**|string|Unique name of an event within a migrate project.|event_name|event_name|
### migrateprojects machine enumerate-machine

enumerate-machine a migrateprojects machine.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|Name of the Azure Resource Group that migrate project is part of.|resource_group_name|resource_group_name|
|**--migrate_project_name**|string|Name of the Azure Migrate project.|migrate_project_name|migrate_project_name|
|**--continuation_token**|string|The continuation token.|continuation_token|continuation_token|
|**--page_size**|integer|The number of items to be returned in a single page. This value is honored only if it is less than the 100.|page_size|page_size|
### migrateprojects machine show

show a migrateprojects machine.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|Name of the Azure Resource Group that migrate project is part of.|resource_group_name|resource_group_name|
|**--migrate_project_name**|string|Name of the Azure Migrate project.|migrate_project_name|migrate_project_name|
|**--machine_name**|string|Unique name of a machine in Azure migration hub.|machine_name|machine_name|
### migrateprojects migrate-project delete

delete a migrateprojects migrate-project.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|Name of the Azure Resource Group that migrate project is part of.|resource_group_name|resource_group_name|
|**--migrate_project_name**|string|Name of the Azure Migrate project.|migrate_project_name|migrate_project_name|
### migrateprojects migrate-project patch-migrate-project

patch-migrate-project a migrateprojects migrate-project.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|Name of the Azure Resource Group that migrate project is part of.|resource_group_name|resource_group_name|
|**--migrate_project_name**|string|Name of the Azure Migrate project.|migrate_project_name|migrate_project_name|
|**--e_tag**|string|Gets or sets the eTag for concurrency control.|e_tag|e_tag|
|**--location**|string|Gets or sets the Azure location in which migrate project is created.|location|location|
|**--properties**|object|Gets or sets the nested properties.|properties|properties|
|**--tags**|object|Gets or sets the tags.|tags|tags|
### migrateprojects migrate-project put-migrate-project

put-migrate-project a migrateprojects migrate-project.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|Name of the Azure Resource Group that migrate project is part of.|resource_group_name|resource_group_name|
|**--migrate_project_name**|string|Name of the Azure Migrate project.|migrate_project_name|migrate_project_name|
|**--e_tag**|string|Gets or sets the eTag for concurrency control.|e_tag|e_tag|
|**--location**|string|Gets or sets the Azure location in which migrate project is created.|location|location|
|**--properties**|object|Gets or sets the nested properties.|properties|properties|
|**--tags**|object|Gets or sets the tags.|tags|tags|
### migrateprojects migrate-project refresh-migrate-project-summary

refresh-migrate-project-summary a migrateprojects migrate-project.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|Name of the Azure Resource Group that migrate project is part of.|resource_group_name|resource_group_name|
|**--migrate_project_name**|string|Name of the Azure Migrate project.|migrate_project_name|migrate_project_name|
|**--goal**|choice|Gets or sets the goal for which summary needs to be refreshed.|goal|goal|
### migrateprojects migrate-project register-tool

register-tool a migrateprojects migrate-project.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|Name of the Azure Resource Group that migrate project is part of.|resource_group_name|resource_group_name|
|**--migrate_project_name**|string|Name of the Azure Migrate project.|migrate_project_name|migrate_project_name|
|**--tool**|choice|Gets or sets the tool to be registered.|tool|tool|
### migrateprojects migrate-project show

show a migrateprojects migrate-project.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|Name of the Azure Resource Group that migrate project is part of.|resource_group_name|resource_group_name|
|**--migrate_project_name**|string|Name of the Azure Migrate project.|migrate_project_name|migrate_project_name|
### migrateprojects solution cleanup-solution-data

cleanup-solution-data a migrateprojects solution.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|Name of the Azure Resource Group that migrate project is part of.|resource_group_name|resource_group_name|
|**--migrate_project_name**|string|Name of the Azure Migrate project.|migrate_project_name|migrate_project_name|
|**--solution_name**|string|Unique name of a migration solution within a migrate project.|solution_name|solution_name|
### migrateprojects solution delete

delete a migrateprojects solution.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|Name of the Azure Resource Group that migrate project is part of.|resource_group_name|resource_group_name|
|**--migrate_project_name**|string|Name of the Azure Migrate project.|migrate_project_name|migrate_project_name|
|**--solution_name**|string|Unique name of a migration solution within a migrate project.|solution_name|solution_name|
### migrateprojects solution enumerate-solution

enumerate-solution a migrateprojects solution.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|Name of the Azure Resource Group that migrate project is part of.|resource_group_name|resource_group_name|
|**--migrate_project_name**|string|Name of the Azure Migrate project.|migrate_project_name|migrate_project_name|
### migrateprojects solution get-config

get-config a migrateprojects solution.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|Name of the Azure Resource Group that migrate project is part of.|resource_group_name|resource_group_name|
|**--migrate_project_name**|string|Name of the Azure Migrate project.|migrate_project_name|migrate_project_name|
|**--solution_name**|string|Unique name of a migration solution within a migrate project.|solution_name|solution_name|
### migrateprojects solution patch-solution

patch-solution a migrateprojects solution.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|Name of the Azure Resource Group that migrate project is part of.|resource_group_name|resource_group_name|
|**--migrate_project_name**|string|Name of the Azure Migrate project.|migrate_project_name|migrate_project_name|
|**--solution_name**|string|Unique name of a migration solution within a migrate project.|solution_name|solution_name|
|**--etag**|string|Gets or sets the ETAG for optimistic concurrency control.|etag|etag|
|**--properties**|object|Gets or sets the properties of the solution.|properties|properties|
### migrateprojects solution put-solution

put-solution a migrateprojects solution.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|Name of the Azure Resource Group that migrate project is part of.|resource_group_name|resource_group_name|
|**--migrate_project_name**|string|Name of the Azure Migrate project.|migrate_project_name|migrate_project_name|
|**--solution_name**|string|Unique name of a migration solution within a migrate project.|solution_name|solution_name|
|**--etag**|string|Gets or sets the ETAG for optimistic concurrency control.|etag|etag|
|**--properties**|object|Gets or sets the properties of the solution.|properties|properties|
### migrateprojects solution show

show a migrateprojects solution.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|Name of the Azure Resource Group that migrate project is part of.|resource_group_name|resource_group_name|
|**--migrate_project_name**|string|Name of the Azure Migrate project.|migrate_project_name|migrate_project_name|
|**--solution_name**|string|Unique name of a migration solution within a migrate project.|solution_name|solution_name|