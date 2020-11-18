# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az migrate|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az migrate` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az migrate project|Projects|[commands](#CommandsInProjects)|
|az migrate machine|Machines|[commands](#CommandsInMachines)|
|az migrate group|Groups|[commands](#CommandsInGroups)|
|az migrate assessment|Assessments|[commands](#CommandsInAssessments)|
|az migrate assessed-machine|AssessedMachines|[commands](#CommandsInAssessedMachines)|
|az migrate hyper-v-collector|HyperVCollectors|[commands](#CommandsInHyperVCollectors)|
|az migrate v-mware-collector|VMwareCollectors|[commands](#CommandsInVMwareCollectors)|

## COMMANDS
### <a name="CommandsInAssessedMachines">Commands in `az migrate assessed-machine` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az migrate assessed-machine list](#AssessedMachinesListByAssessment)|ListByAssessment|[Parameters](#ParametersAssessedMachinesListByAssessment)|[Example](#ExamplesAssessedMachinesListByAssessment)|
|[az migrate assessed-machine show](#AssessedMachinesGet)|Get|[Parameters](#ParametersAssessedMachinesGet)|[Example](#ExamplesAssessedMachinesGet)|

### <a name="CommandsInAssessments">Commands in `az migrate assessment` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az migrate assessment list](#AssessmentsListByGroup)|ListByGroup|[Parameters](#ParametersAssessmentsListByGroup)|[Example](#ExamplesAssessmentsListByGroup)|
|[az migrate assessment list](#AssessmentsListByProject)|ListByProject|[Parameters](#ParametersAssessmentsListByProject)|[Example](#ExamplesAssessmentsListByProject)|
|[az migrate assessment show](#AssessmentsGet)|Get|[Parameters](#ParametersAssessmentsGet)|[Example](#ExamplesAssessmentsGet)|
|[az migrate assessment create](#AssessmentsCreate)|Create|[Parameters](#ParametersAssessmentsCreate)|[Example](#ExamplesAssessmentsCreate)|
|[az migrate assessment delete](#AssessmentsDelete)|Delete|[Parameters](#ParametersAssessmentsDelete)|[Example](#ExamplesAssessmentsDelete)|
|[az migrate assessment get-report-download-url](#AssessmentsGetReportDownloadUrl)|GetReportDownloadUrl|[Parameters](#ParametersAssessmentsGetReportDownloadUrl)|[Example](#ExamplesAssessmentsGetReportDownloadUrl)|

### <a name="CommandsInGroups">Commands in `az migrate group` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az migrate group list](#GroupsListByProject)|ListByProject|[Parameters](#ParametersGroupsListByProject)|[Example](#ExamplesGroupsListByProject)|
|[az migrate group show](#GroupsGet)|Get|[Parameters](#ParametersGroupsGet)|[Example](#ExamplesGroupsGet)|
|[az migrate group create](#GroupsCreate)|Create|[Parameters](#ParametersGroupsCreate)|[Example](#ExamplesGroupsCreate)|
|[az migrate group delete](#GroupsDelete)|Delete|[Parameters](#ParametersGroupsDelete)|[Example](#ExamplesGroupsDelete)|
|[az migrate group update-machine](#GroupsUpdateMachines)|UpdateMachines|[Parameters](#ParametersGroupsUpdateMachines)|[Example](#ExamplesGroupsUpdateMachines)|

### <a name="CommandsInHyperVCollectors">Commands in `az migrate hyper-v-collector` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az migrate hyper-v-collector list](#HyperVCollectorsListByProject)|ListByProject|[Parameters](#ParametersHyperVCollectorsListByProject)|[Example](#ExamplesHyperVCollectorsListByProject)|
|[az migrate hyper-v-collector show](#HyperVCollectorsGet)|Get|[Parameters](#ParametersHyperVCollectorsGet)|[Example](#ExamplesHyperVCollectorsGet)|
|[az migrate hyper-v-collector create](#HyperVCollectorsCreate)|Create|[Parameters](#ParametersHyperVCollectorsCreate)|[Example](#ExamplesHyperVCollectorsCreate)|
|[az migrate hyper-v-collector delete](#HyperVCollectorsDelete)|Delete|[Parameters](#ParametersHyperVCollectorsDelete)|[Example](#ExamplesHyperVCollectorsDelete)|

### <a name="CommandsInMachines">Commands in `az migrate machine` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az migrate machine list](#MachinesListByProject)|ListByProject|[Parameters](#ParametersMachinesListByProject)|[Example](#ExamplesMachinesListByProject)|
|[az migrate machine show](#MachinesGet)|Get|[Parameters](#ParametersMachinesGet)|[Example](#ExamplesMachinesGet)|

### <a name="CommandsInProjects">Commands in `az migrate project` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az migrate project list](#ProjectsList)|List|[Parameters](#ParametersProjectsList)|[Example](#ExamplesProjectsList)|
|[az migrate project list](#ProjectsListBySubscription)|ListBySubscription|[Parameters](#ParametersProjectsListBySubscription)|[Example](#ExamplesProjectsListBySubscription)|
|[az migrate project show](#ProjectsGet)|Get|[Parameters](#ParametersProjectsGet)|[Example](#ExamplesProjectsGet)|
|[az migrate project create](#ProjectsCreate)|Create|[Parameters](#ParametersProjectsCreate)|[Example](#ExamplesProjectsCreate)|
|[az migrate project update](#ProjectsUpdate)|Update|[Parameters](#ParametersProjectsUpdate)|[Example](#ExamplesProjectsUpdate)|
|[az migrate project delete](#ProjectsDelete)|Delete|[Parameters](#ParametersProjectsDelete)|[Example](#ExamplesProjectsDelete)|
|[az migrate project assessment-option](#ProjectsAssessmentOptions)|AssessmentOptions|[Parameters](#ParametersProjectsAssessmentOptions)|[Example](#ExamplesProjectsAssessmentOptions)|
|[az migrate project assessment-option-list](#ProjectsAssessmentOptionsList)|AssessmentOptionsList|[Parameters](#ParametersProjectsAssessmentOptionsList)|[Example](#ExamplesProjectsAssessmentOptionsList)|

### <a name="CommandsInVMwareCollectors">Commands in `az migrate v-mware-collector` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az migrate v-mware-collector list](#VMwareCollectorsListByProject)|ListByProject|[Parameters](#ParametersVMwareCollectorsListByProject)|[Example](#ExamplesVMwareCollectorsListByProject)|
|[az migrate v-mware-collector show](#VMwareCollectorsGet)|Get|[Parameters](#ParametersVMwareCollectorsGet)|[Example](#ExamplesVMwareCollectorsGet)|
|[az migrate v-mware-collector create](#VMwareCollectorsCreate)|Create|[Parameters](#ParametersVMwareCollectorsCreate)|[Example](#ExamplesVMwareCollectorsCreate)|
|[az migrate v-mware-collector delete](#VMwareCollectorsDelete)|Delete|[Parameters](#ParametersVMwareCollectorsDelete)|[Example](#ExamplesVMwareCollectorsDelete)|


## COMMAND DETAILS

### group `az migrate assessed-machine`
#### <a name="AssessedMachinesListByAssessment">Command `az migrate assessed-machine list`</a>

##### <a name="ExamplesAssessedMachinesListByAssessment">Example</a>
```
az migrate assessed-machine list --assessment-name "assessment_5_9_2019_16_22_14" --group-name "Test1" --project-name \
"abgoyalWEselfhostb72bproject" --resource-group "abgoyal-westEurope"
```
##### <a name="ParametersAssessedMachinesListByAssessment">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the Azure Resource Group that project is part of.|resource_group_name|resourceGroupName|
|**--project-name**|string|Name of the Azure Migrate project.|project_name|projectName|
|**--group-name**|string|Unique name of a group within a project.|group_name|groupName|
|**--assessment-name**|string|Unique name of an assessment within a project.|assessment_name|assessmentName|

#### <a name="AssessedMachinesGet">Command `az migrate assessed-machine show`</a>

##### <a name="ExamplesAssessedMachinesGet">Example</a>
```
az migrate assessed-machine show --name "f57fe432-3bd2-486a-a83a-6f4d99f1a952" --assessment-name \
"assessment_5_9_2019_16_22_14" --group-name "Test1" --project-name "abgoyalWEselfhostb72bproject" --resource-group \
"abgoyal-westEurope"
```
##### <a name="ParametersAssessedMachinesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the Azure Resource Group that project is part of.|resource_group_name|resourceGroupName|
|**--project-name**|string|Name of the Azure Migrate project.|project_name|projectName|
|**--group-name**|string|Unique name of a group within a project.|group_name|groupName|
|**--assessment-name**|string|Unique name of an assessment within a project.|assessment_name|assessmentName|
|**--assessed-machine-name**|string|Unique name of an assessed machine evaluated as part of an assessment.|assessed_machine_name|assessedMachineName|

### group `az migrate assessment`
#### <a name="AssessmentsListByGroup">Command `az migrate assessment list`</a>

##### <a name="ExamplesAssessmentsListByGroup">Example</a>
```
az migrate assessment list --group-name "Test1" --project-name "abgoyalWEselfhostb72bproject" --resource-group \
"abgoyal-westEurope"
```
##### <a name="ParametersAssessmentsListByGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the Azure Resource Group that project is part of.|resource_group_name|resourceGroupName|
|**--project-name**|string|Name of the Azure Migrate project.|project_name|projectName|
|**--group-name**|string|Unique name of a group within a project.|group_name|groupName|

#### <a name="AssessmentsListByProject">Command `az migrate assessment list`</a>

##### <a name="ExamplesAssessmentsListByProject">Example</a>
```
az migrate assessment list --project-name "abgoyalWEselfhostb72bproject" --resource-group "abgoyal-westEurope"
```
##### <a name="ParametersAssessmentsListByProject">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="AssessmentsGet">Command `az migrate assessment show`</a>

##### <a name="ExamplesAssessmentsGet">Example</a>
```
az migrate assessment show --name "assessment_5_9_2019_16_22_14" --group-name "Test1" --project-name \
"abgoyalWEselfhostb72bproject" --resource-group "abgoyal-westEurope"
```
##### <a name="ParametersAssessmentsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the Azure Resource Group that project is part of.|resource_group_name|resourceGroupName|
|**--project-name**|string|Name of the Azure Migrate project.|project_name|projectName|
|**--group-name**|string|Unique name of a group within a project.|group_name|groupName|
|**--assessment-name**|string|Unique name of an assessment within a project.|assessment_name|assessmentName|

#### <a name="AssessmentsCreate">Command `az migrate assessment create`</a>

##### <a name="ExamplesAssessmentsCreate">Example</a>
```
az migrate assessment create --e-tag "\\"1e000c2c-0000-0d00-0000-5cdaa4190000\\"" --azure-disk-type \
"StandardOrPremium" --azure-hybrid-use-benefit "Yes" --azure-location "NorthEurope" --azure-offer-code "MSAZR0003P" \
--azure-pricing-tier "Standard" --azure-storage-redundancy "LocallyRedundant" --azure-vm-families "Dv2_series" \
--azure-vm-families "F_series" --azure-vm-families "Dv3_series" --azure-vm-families "DS_series" --azure-vm-families \
"DSv2_series" --azure-vm-families "Fs_series" --azure-vm-families "Dsv3_series" --azure-vm-families "Ev3_series" \
--azure-vm-families "Esv3_series" --azure-vm-families "D_series" --azure-vm-families "M_series" --azure-vm-families \
"Fsv2_series" --azure-vm-families "H_series" --currency "USD" --discount-percentage 100 --percentile "Percentile95" \
--reserved-instance "RI3Year" --scaling-factor 1 --sizing-criterion "PerformanceBased" --stage "InProgress" \
--time-range "Day" --vm-uptime days-per-month=31 hours-per-day=24 --name "assessment_5_14_2019_16_48_47" --group-name \
"Group2" --project-name "abgoyalWEselfhostb72bproject" --resource-group "abgoyal-westEurope"
```
##### <a name="ParametersAssessmentsCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the Azure Resource Group that project is part of.|resource_group_name|resourceGroupName|
|**--project-name**|string|Name of the Azure Migrate project.|project_name|projectName|
|**--group-name**|string|Unique name of a group within a project.|group_name|groupName|
|**--assessment-name**|string|Unique name of an assessment within a project.|assessment_name|assessmentName|
|**--e-tag**|string|For optimistic concurrency control.|e_tag|eTag|
|**--azure-location**|choice|Target Azure location for which the machines should be assessed. These enums are the same as used by Compute API.|azure_location|azureLocation|
|**--azure-offer-code**|choice|Offer code according to which cost estimation is done.|azure_offer_code|azureOfferCode|
|**--azure-pricing-tier**|choice|Pricing tier for Size evaluation.|azure_pricing_tier|azurePricingTier|
|**--azure-storage-redundancy**|choice|Storage Redundancy type offered by Azure.|azure_storage_redundancy|azureStorageRedundancy|
|**--scaling-factor**|number|Scaling factor used over utilization data to add a performance buffer for new machines to be created in Azure. Min Value = 1.0, Max value = 1.9, Default = 1.3.|scaling_factor|scalingFactor|
|**--percentile**|choice|Percentile of performance data used to recommend Azure size.|percentile|percentile|
|**--time-range**|choice|Time range of performance data used to recommend a size.|time_range|timeRange|
|**--stage**|choice|User configurable setting that describes the status of the assessment.|stage|stage|
|**--currency**|choice|Currency to report prices in.|currency|currency|
|**--azure-hybrid-use-benefit**|choice|AHUB discount on windows virtual machines.|azure_hybrid_use_benefit|azureHybridUseBenefit|
|**--discount-percentage**|number|Custom discount percentage to be applied on final costs. Can be in the range [0, 100].|discount_percentage|discountPercentage|
|**--sizing-criterion**|choice|Assessment sizing criterion.|sizing_criterion|sizingCriterion|
|**--reserved-instance**|choice|Azure reserved instance.|reserved_instance|reservedInstance|
|**--azure-vm-families**|array|List of azure VM families.|azure_vm_families|azureVmFamilies|
|**--azure-disk-type**|choice|Storage type selected for this disk.|azure_disk_type|azureDiskType|
|**--vm-uptime**|object|Specify the duration for which the VMs are up in the on-premises environment.|vm_uptime|vmUptime|

#### <a name="AssessmentsDelete">Command `az migrate assessment delete`</a>

##### <a name="ExamplesAssessmentsDelete">Example</a>
```
az migrate assessment delete --name "assessment_5_9_2019_16_22_14" --group-name "Test1" --project-name \
"abgoyalWEselfhostb72bproject" --resource-group "abgoyal-westEurope"
```
##### <a name="ParametersAssessmentsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the Azure Resource Group that project is part of.|resource_group_name|resourceGroupName|
|**--project-name**|string|Name of the Azure Migrate project.|project_name|projectName|
|**--group-name**|string|Unique name of a group within a project.|group_name|groupName|
|**--assessment-name**|string|Unique name of an assessment within a project.|assessment_name|assessmentName|

#### <a name="AssessmentsGetReportDownloadUrl">Command `az migrate assessment get-report-download-url`</a>

##### <a name="ExamplesAssessmentsGetReportDownloadUrl">Example</a>
```
az migrate assessment get-report-download-url --name "assessment_5_9_2019_16_22_14" --group-name "Test1" \
--project-name "abgoyalWEselfhostb72bproject" --resource-group "abgoyal-westEurope"
```
##### <a name="ParametersAssessmentsGetReportDownloadUrl">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the Azure Resource Group that project is part of.|resource_group_name|resourceGroupName|
|**--project-name**|string|Name of the Azure Migrate project.|project_name|projectName|
|**--group-name**|string|Unique name of a group within a project.|group_name|groupName|
|**--assessment-name**|string|Unique name of an assessment within a project.|assessment_name|assessmentName|

### group `az migrate group`
#### <a name="GroupsListByProject">Command `az migrate group list`</a>

##### <a name="ExamplesGroupsListByProject">Example</a>
```
az migrate group list --project-name "abgoyalWEselfhostb72bproject" --resource-group "abgoyal-westEurope"
```
##### <a name="ParametersGroupsListByProject">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the Azure Resource Group that project is part of.|resource_group_name|resourceGroupName|
|**--project-name**|string|Name of the Azure Migrate project.|project_name|projectName|

#### <a name="GroupsGet">Command `az migrate group show`</a>

##### <a name="ExamplesGroupsGet">Example</a>
```
az migrate group show --name "Test1" --project-name "abgoyalWEselfhostb72bproject" --resource-group \
"abgoyal-westEurope"
```
##### <a name="ParametersGroupsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the Azure Resource Group that project is part of.|resource_group_name|resourceGroupName|
|**--project-name**|string|Name of the Azure Migrate project.|project_name|projectName|
|**--group-name**|string|Unique name of a group within a project.|group_name|groupName|

#### <a name="GroupsCreate">Command `az migrate group create`</a>

##### <a name="ExamplesGroupsCreate">Example</a>
```
az migrate group create --e-tag "\\"1e000c2c-0000-0d00-0000-5cdaa4190000\\"" --name "Group2" --project-name \
"abgoyalWEselfhostb72bproject" --resource-group "abgoyal-westEurope"
```
##### <a name="ParametersGroupsCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the Azure Resource Group that project is part of.|resource_group_name|resourceGroupName|
|**--project-name**|string|Name of the Azure Migrate project.|project_name|projectName|
|**--group-name**|string|Unique name of a group within a project.|group_name|groupName|
|**--e-tag**|string|For optimistic concurrency control.|e_tag|eTag|

#### <a name="GroupsDelete">Command `az migrate group delete`</a>

##### <a name="ExamplesGroupsDelete">Example</a>
```
az migrate group delete --name "Test1" --project-name "abgoyalWEselfhostb72bproject" --resource-group \
"abgoyal-westEurope"
```
##### <a name="ParametersGroupsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the Azure Resource Group that project is part of.|resource_group_name|resourceGroupName|
|**--project-name**|string|Name of the Azure Migrate project.|project_name|projectName|
|**--group-name**|string|Unique name of a group within a project.|group_name|groupName|

#### <a name="GroupsUpdateMachines">Command `az migrate group update-machine`</a>

##### <a name="ExamplesGroupsUpdateMachines">Example</a>
```
az migrate group update-machine --e-tag "\\"1e000c2c-0000-0d00-0000-5cdaa4190000\\"" --properties \
machines="/subscriptions/6393a73f-8d55-47ef-b6dd-179b3e0c7910/resourceGroups/abgoyal-westeurope/providers/Microsoft.Mig\
rate/assessmentprojects/abgoyalWEselfhostb72bproject/machines/amansing_vm1" operation-type="Add" --name "Group2" \
--project-name "abgoyalWEselfhostb72bproject" --resource-group "abgoyal-westEurope"
```
##### <a name="ParametersGroupsUpdateMachines">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the Azure Resource Group that project is part of.|resource_group_name|resourceGroupName|
|**--project-name**|string|Name of the Azure Migrate project.|project_name|projectName|
|**--group-name**|string|Unique name of a group within a project.|group_name|groupName|
|**--e-tag**|string|For optimistic concurrency control.|e_tag|eTag|
|**--properties**|object|Properties of the group.|properties|properties|

### group `az migrate hyper-v-collector`
#### <a name="HyperVCollectorsListByProject">Command `az migrate hyper-v-collector list`</a>

##### <a name="ExamplesHyperVCollectorsListByProject">Example</a>
```
az migrate hyper-v-collector list --project-name "migrateprojectce73project" --resource-group "contosoithyperv"
```
##### <a name="ParametersHyperVCollectorsListByProject">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the Azure Resource Group that project is part of.|resource_group_name|resourceGroupName|
|**--project-name**|string|Name of the Azure Migrate project.|project_name|projectName|

#### <a name="HyperVCollectorsGet">Command `az migrate hyper-v-collector show`</a>

##### <a name="ExamplesHyperVCollectorsGet">Example</a>
```
az migrate hyper-v-collector show --name "migrateprojectce73collector" --project-name "migrateprojectce73project" \
--resource-group "contosoithyperv"
```
##### <a name="ParametersHyperVCollectorsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the Azure Resource Group that project is part of.|resource_group_name|resourceGroupName|
|**--project-name**|string|Name of the Azure Migrate project.|project_name|projectName|
|**--hyper-v-collector-name**|string|Unique name of a Hyper-V collector within a project.|hyper_v_collector_name|hyperVCollectorName|

#### <a name="HyperVCollectorsCreate">Command `az migrate hyper-v-collector create`</a>

##### <a name="ExamplesHyperVCollectorsCreate">Example</a>
```
az migrate hyper-v-collector create --e-tag "\\"00000981-0000-0300-0000-5d74cd5f0000\\"" \
--agent-properties-spn-details application-id="827f1053-44dc-439f-b832-05416dcce12b" audience="https://72f988bf-86f1-41\
af-91ab-2d7cd011db47/migrateprojectce73agentauthaadapp" authority="https://login.windows.net/72f988bf-86f1-41af-91ab-2d\
7cd011db47" object-id="be75098e-c0fc-4ac4-98c7-282ebbcf8370" tenant-id="72f988bf-86f1-41af-91ab-2d7cd011db47" \
--discovery-site-id "/subscriptions/8c3c936a-c09b-4de3-830b-3f5f244d72e9/resourceGroups/ContosoITHyperV/providers/Micro\
soft.OffAzure/HyperVSites/migrateprojectce73site" --name "migrateprojectce73collector" --project-name \
"migrateprojectce73project" --resource-group "contosoithyperv"
```
##### <a name="ParametersHyperVCollectorsCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the Azure Resource Group that project is part of.|resource_group_name|resourceGroupName|
|**--project-name**|string|Name of the Azure Migrate project.|project_name|projectName|
|**--hyper-v-collector-name**|string|Unique name of a Hyper-V collector within a project.|hyper_v_collector_name|hyperVCollectorName|
|**--e-tag**|string||e_tag|eTag|
|**--discovery-site-id**|string|The ARM id of the discovery service site.|discovery_site_id|discoverySiteId|
|**--agent-properties-spn-details**|object||spn_details|spnDetails|

#### <a name="HyperVCollectorsDelete">Command `az migrate hyper-v-collector delete`</a>

##### <a name="ExamplesHyperVCollectorsDelete">Example</a>
```
az migrate hyper-v-collector delete --name "migrateprojectce73collector" --project-name "migrateprojectce73project" \
--resource-group "contosoithyperv"
```
##### <a name="ParametersHyperVCollectorsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the Azure Resource Group that project is part of.|resource_group_name|resourceGroupName|
|**--project-name**|string|Name of the Azure Migrate project.|project_name|projectName|
|**--hyper-v-collector-name**|string|Unique name of a Hyper-V collector within a project.|hyper_v_collector_name|hyperVCollectorName|

### group `az migrate machine`
#### <a name="MachinesListByProject">Command `az migrate machine list`</a>

##### <a name="ExamplesMachinesListByProject">Example</a>
```
az migrate machine list --project-name "abgoyalWEselfhostb72bproject" --resource-group "abgoyal-westEurope"
```
##### <a name="ParametersMachinesListByProject">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the Azure Resource Group that project is part of.|resource_group_name|resourceGroupName|
|**--project-name**|string|Name of the Azure Migrate project.|project_name|projectName|

#### <a name="MachinesGet">Command `az migrate machine show`</a>

##### <a name="ExamplesMachinesGet">Example</a>
```
az migrate machine show --name "269ef295-a38d-4f8f-9779-77ce79088311" --project-name "abgoyalWEselfhostb72bproject" \
--resource-group "abgoyal-westEurope"
```
##### <a name="ParametersMachinesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the Azure Resource Group that project is part of.|resource_group_name|resourceGroupName|
|**--project-name**|string|Name of the Azure Migrate project.|project_name|projectName|
|**--machine-name**|string|Unique name of a machine in private datacenter.|machine_name|machineName|

### group `az migrate project`
#### <a name="ProjectsList">Command `az migrate project list`</a>

##### <a name="ExamplesProjectsList">Example</a>
```
az migrate project list --resource-group "abgoyal-westEurope"
```
##### <a name="ParametersProjectsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the Azure Resource Group that project is part of.|resource_group_name|resourceGroupName|

#### <a name="ProjectsListBySubscription">Command `az migrate project list`</a>

##### <a name="ExamplesProjectsListBySubscription">Example</a>
```
az migrate project list
```
##### <a name="ParametersProjectsListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="ProjectsGet">Command `az migrate project show`</a>

##### <a name="ExamplesProjectsGet">Example</a>
```
az migrate project show --name "abgoyalWEselfhostb72bproject" --resource-group "abgoyal-westEurope"
```
##### <a name="ParametersProjectsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the Azure Resource Group that project is part of.|resource_group_name|resourceGroupName|
|**--project-name**|string|Name of the Azure Migrate project.|project_name|projectName|

#### <a name="ProjectsCreate">Command `az migrate project create`</a>

##### <a name="ExamplesProjectsCreate">Example</a>
```
az migrate project create --e-tag "" --location "West Europe" --properties assessment-solution-id="/subscriptions/6393a\
73f-8d55-47ef-b6dd-179b3e0c7910/resourcegroups/abgoyal-westeurope/providers/microsoft.migrate/migrateprojects/abgoyalwe\
selfhost/Solutions/Servers-Assessment-ServerAssessment" customer-workspace-id=null customer-workspace-location=null \
project-status="Active" --tags "{}" --name "abGoyalProject2" --resource-group "abgoyal-westEurope"
```
##### <a name="ParametersProjectsCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the Azure Resource Group that project is part of.|resource_group_name|resourceGroupName|
|**--project-name**|string|Name of the Azure Migrate project.|project_name|projectName|
|**--e-tag**|string|For optimistic concurrency control.|e_tag|eTag|
|**--location**|string|Azure location in which project is created.|location|location|
|**--tags**|any|Tags provided by Azure Tagging service.|tags|tags|
|**--properties**|object|Properties of the project.|properties|properties|

#### <a name="ProjectsUpdate">Command `az migrate project update`</a>

##### <a name="ExamplesProjectsUpdate">Example</a>
```
az migrate project update --e-tag "" --location "West Europe" --properties assessment-solution-id="/subscriptions/6393a\
73f-8d55-47ef-b6dd-179b3e0c7910/resourcegroups/abgoyal-westeurope/providers/microsoft.migrate/migrateprojects/abgoyalwe\
selfhost/Solutions/Servers-Assessment-ServerAssessment" customer-workspace-id=null customer-workspace-location=null \
project-status="Active" --tags "{}" --name "abGoyalProject2" --resource-group "abgoyal-westEurope"
```
##### <a name="ParametersProjectsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the Azure Resource Group that project is part of.|resource_group_name|resourceGroupName|
|**--project-name**|string|Name of the Azure Migrate project.|project_name|projectName|
|**--e-tag**|string|For optimistic concurrency control.|e_tag|eTag|
|**--location**|string|Azure location in which project is created.|location|location|
|**--tags**|any|Tags provided by Azure Tagging service.|tags|tags|
|**--properties**|object|Properties of the project.|properties|properties|

#### <a name="ProjectsDelete">Command `az migrate project delete`</a>

##### <a name="ExamplesProjectsDelete">Example</a>
```
az migrate project delete --name "abGoyalProject2" --resource-group "abgoyal-westEurope"
```
##### <a name="ParametersProjectsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the Azure Resource Group that project is part of.|resource_group_name|resourceGroupName|
|**--project-name**|string|Name of the Azure Migrate project.|project_name|projectName|

#### <a name="ProjectsAssessmentOptions">Command `az migrate project assessment-option`</a>

##### <a name="ExamplesProjectsAssessmentOptions">Example</a>
```
az migrate project assessment-option --assessment-options-name "default" --name "abgoyalWEselfhostb72bproject" \
--resource-group "abgoyal-westEurope"
```
##### <a name="ParametersProjectsAssessmentOptions">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the Azure Resource Group that project is part of.|resource_group_name|resourceGroupName|
|**--project-name**|string|Name of the Azure Migrate project.|project_name|projectName|
|**--assessment-options-name**|string|Name of the assessment options. The only name accepted in default.|assessment_options_name|assessmentOptionsName|

#### <a name="ProjectsAssessmentOptionsList">Command `az migrate project assessment-option-list`</a>

##### <a name="ExamplesProjectsAssessmentOptionsList">Example</a>
```
az migrate project assessment-option-list --name "abgoyalWEselfhostb72bproject" --resource-group "abgoyal-westEurope"
```
##### <a name="ParametersProjectsAssessmentOptionsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the Azure Resource Group that project is part of.|resource_group_name|resourceGroupName|
|**--project-name**|string|Name of the Azure Migrate project.|project_name|projectName|

### group `az migrate v-mware-collector`
#### <a name="VMwareCollectorsListByProject">Command `az migrate v-mware-collector list`</a>

##### <a name="ExamplesVMwareCollectorsListByProject">Example</a>
```
az migrate v-mware-collector list --project-name "abgoyalWEselfhostb72bproject" --resource-group "abgoyal-westEurope"
```
##### <a name="ParametersVMwareCollectorsListByProject">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the Azure Resource Group that project is part of.|resource_group_name|resourceGroupName|
|**--project-name**|string|Name of the Azure Migrate project.|project_name|projectName|

#### <a name="VMwareCollectorsGet">Command `az migrate v-mware-collector show`</a>

##### <a name="ExamplesVMwareCollectorsGet">Example</a>
```
az migrate v-mware-collector show --project-name "abgoyalWEselfhostb72bproject" --resource-group "abgoyal-westEurope" \
--name "PortalvCenterbc2fcollector"
```
##### <a name="ParametersVMwareCollectorsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the Azure Resource Group that project is part of.|resource_group_name|resourceGroupName|
|**--project-name**|string|Name of the Azure Migrate project.|project_name|projectName|
|**--vm-ware-collector-name**|string|Unique name of a VMware collector within a project.|vm_ware_collector_name|vmWareCollectorName|

#### <a name="VMwareCollectorsCreate">Command `az migrate v-mware-collector create`</a>

##### <a name="ExamplesVMwareCollectorsCreate">Example</a>
```
az migrate v-mware-collector create --e-tag "\\"01003d32-0000-0d00-0000-5d74d2e50000\\"" \
--agent-properties-spn-details application-id="fc717575-8173-4b21-92a5-658b655e613e" audience="https://72f988bf-86f1-41\
af-91ab-2d7cd011db47/PortalvCenterbc2fagentauthaadapp" authority="https://login.windows.net/72f988bf-86f1-41af-91ab-2d7\
cd011db47" object-id="29d94f38-db94-4980-aec0-0cfd55ab1cd0" tenant-id="72f988bf-86f1-41af-91ab-2d7cd011db47" \
--discovery-site-id "/subscriptions/6393a73f-8d55-47ef-b6dd-179b3e0c7910/resourceGroups/abgoyal-westEurope/providers/Mi\
crosoft.OffAzure/VMwareSites/PortalvCenterbc2fsite" --project-name "abgoyalWEselfhostb72bproject" --resource-group \
"abgoyal-westEurope" --name "PortalvCenterbc2fcollector"
```
##### <a name="ParametersVMwareCollectorsCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the Azure Resource Group that project is part of.|resource_group_name|resourceGroupName|
|**--project-name**|string|Name of the Azure Migrate project.|project_name|projectName|
|**--vm-ware-collector-name**|string|Unique name of a VMware collector within a project.|vm_ware_collector_name|vmWareCollectorName|
|**--e-tag**|string||e_tag|eTag|
|**--discovery-site-id**|string|The ARM id of the discovery service site.|discovery_site_id|discoverySiteId|
|**--agent-properties-spn-details**|object||spn_details|spnDetails|

#### <a name="VMwareCollectorsDelete">Command `az migrate v-mware-collector delete`</a>

##### <a name="ExamplesVMwareCollectorsDelete">Example</a>
```
az migrate v-mware-collector delete --project-name "abgoyalWEselfhostb72bproject" --resource-group \
"abgoyal-westEurope" --name "PortalvCenterbc2fcollector"
```
##### <a name="ParametersVMwareCollectorsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the Azure Resource Group that project is part of.|resource_group_name|resourceGroupName|
|**--project-name**|string|Name of the Azure Migrate project.|project_name|projectName|
|**--vm-ware-collector-name**|string|Unique name of a VMware collector within a project.|vm_ware_collector_name|vmWareCollectorName|
