# Azure CLI migrate Extension #
This is the extension for migrate

### How to use ###
Install this extension using the below CLI command
```
az extension add --name migrate
```

### Included Features ###
#### migrate project ####
##### Create #####
```
az migrate project create --e-tag "" --location "West Europe" \
    --properties assessment-solution-id="/subscriptions/6393a73f-8d55-47ef-b6dd-179b3e0c7910/resourcegroups/abgoyal-westeurope/providers/microsoft.migrate/migrateprojects/abgoyalweselfhost/Solutions/Servers-Assessment-ServerAssessment" customer-workspace-id=null customer-workspace-location=null project-status="Active" \
    --tags "{}" --name "abGoyalProject2" --resource-group "abgoyal-westEurope" 
```
##### Show #####
```
az migrate project show --name "abgoyalWEselfhostb72bproject" --resource-group "abgoyal-westEurope"
```
##### List #####
```
az migrate project list --resource-group "abgoyal-westEurope"
```
##### Update #####
```
az migrate project update --e-tag "" --location "West Europe" \
    --properties assessment-solution-id="/subscriptions/6393a73f-8d55-47ef-b6dd-179b3e0c7910/resourcegroups/abgoyal-westeurope/providers/microsoft.migrate/migrateprojects/abgoyalweselfhost/Solutions/Servers-Assessment-ServerAssessment" customer-workspace-id=null customer-workspace-location=null project-status="Active" \
    --tags "{}" --name "abGoyalProject2" --resource-group "abgoyal-westEurope" 
```
##### Assessment-option #####
```
az migrate project assessment-option --assessment-options-name "default" --name "abgoyalWEselfhostb72bproject" \
    --resource-group "abgoyal-westEurope" 
```
##### Assessment-option-list #####
```
az migrate project assessment-option-list --name "abgoyalWEselfhostb72bproject" --resource-group "abgoyal-westEurope"
```
##### Delete #####
```
az migrate project delete --name "abGoyalProject2" --resource-group "abgoyal-westEurope"
```
#### migrate machine ####
##### List #####
```
az migrate machine list --project-name "abgoyalWEselfhostb72bproject" --resource-group "abgoyal-westEurope"
```
##### Show #####
```
az migrate machine show --name "269ef295-a38d-4f8f-9779-77ce79088311" --project-name "abgoyalWEselfhostb72bproject" \
    --resource-group "abgoyal-westEurope" 
```
#### migrate group ####
##### Create #####
```
az migrate group create --e-tag "\\"1e000c2c-0000-0d00-0000-5cdaa4190000\\"" --name "Group2" \
    --project-name "abgoyalWEselfhostb72bproject" --resource-group "abgoyal-westEurope" 
```
##### Show #####
```
az migrate group show --name "Test1" --project-name "abgoyalWEselfhostb72bproject" \
    --resource-group "abgoyal-westEurope" 
```
##### List #####
```
az migrate group list --project-name "abgoyalWEselfhostb72bproject" --resource-group "abgoyal-westEurope"
```
##### Update-machine #####
```
az migrate group update-machine --e-tag "\\"1e000c2c-0000-0d00-0000-5cdaa4190000\\"" \
    --properties machines="/subscriptions/6393a73f-8d55-47ef-b6dd-179b3e0c7910/resourceGroups/abgoyal-westeurope/providers/Microsoft.Migrate/assessmentprojects/abgoyalWEselfhostb72bproject/machines/amansing_vm1" operation-type="Add" \
    --name "Group2" --project-name "abgoyalWEselfhostb72bproject" --resource-group "abgoyal-westEurope" 
```
##### Delete #####
```
az migrate group delete --name "Test1" --project-name "abgoyalWEselfhostb72bproject" \
    --resource-group "abgoyal-westEurope" 
```
#### migrate assessment ####
##### Create #####
```
az migrate assessment create --e-tag "\\"1e000c2c-0000-0d00-0000-5cdaa4190000\\"" \
    --azure-disk-type "StandardOrPremium" --azure-hybrid-use-benefit "Yes" --azure-location "NorthEurope" \
    --azure-offer-code "MSAZR0003P" --azure-pricing-tier "Standard" --azure-storage-redundancy "LocallyRedundant" \
    --azure-vm-families "Dv2_series" --azure-vm-families "F_series" --azure-vm-families "Dv3_series" \
    --azure-vm-families "DS_series" --azure-vm-families "DSv2_series" --azure-vm-families "Fs_series" \
    --azure-vm-families "Dsv3_series" --azure-vm-families "Ev3_series" --azure-vm-families "Esv3_series" \
    --azure-vm-families "D_series" --azure-vm-families "M_series" --azure-vm-families "Fsv2_series" \
    --azure-vm-families "H_series" --currency "USD" --discount-percentage 100 --percentile "Percentile95" \
    --reserved-instance "RI3Year" --scaling-factor 1 --sizing-criterion "PerformanceBased" --stage "InProgress" \
    --time-range "Day" --vm-uptime days-per-month=31 hours-per-day=24 --name "assessment_5_14_2019_16_48_47" \
    --group-name "Group2" --project-name "abgoyalWEselfhostb72bproject" --resource-group "abgoyal-westEurope" 
```
##### Show #####
```
az migrate assessment show --name "assessment_5_9_2019_16_22_14" --group-name "Test1" \
    --project-name "abgoyalWEselfhostb72bproject" --resource-group "abgoyal-westEurope" 
```
##### List #####
```
az migrate assessment list --group-name "Test1" --project-name "abgoyalWEselfhostb72bproject" \
    --resource-group "abgoyal-westEurope" 
```
##### Get-report-download-url #####
```
az migrate assessment get-report-download-url --name "assessment_5_9_2019_16_22_14" --group-name "Test1" \
    --project-name "abgoyalWEselfhostb72bproject" --resource-group "abgoyal-westEurope" 
```
##### Delete #####
```
az migrate assessment delete --name "assessment_5_9_2019_16_22_14" --group-name "Test1" \
    --project-name "abgoyalWEselfhostb72bproject" --resource-group "abgoyal-westEurope" 
```
#### migrate assessed-machine ####
##### List #####
```
az migrate assessed-machine list --assessment-name "assessment_5_9_2019_16_22_14" --group-name "Test1" \
    --project-name "abgoyalWEselfhostb72bproject" --resource-group "abgoyal-westEurope" 
```
##### Show #####
```
az migrate assessed-machine show --name "f57fe432-3bd2-486a-a83a-6f4d99f1a952" \
    --assessment-name "assessment_5_9_2019_16_22_14" --group-name "Test1" \
    --project-name "abgoyalWEselfhostb72bproject" --resource-group "abgoyal-westEurope" 
```
#### migrate hyper-v-collector ####
##### Create #####
```
az migrate hyper-v-collector create --e-tag "\\"00000981-0000-0300-0000-5d74cd5f0000\\"" \
    --agent-properties-spn-details application-id="827f1053-44dc-439f-b832-05416dcce12b" audience="https://72f988bf-86f1-41af-91ab-2d7cd011db47/migrateprojectce73agentauthaadapp" authority="https://login.windows.net/72f988bf-86f1-41af-91ab-2d7cd011db47" object-id="be75098e-c0fc-4ac4-98c7-282ebbcf8370" tenant-id="72f988bf-86f1-41af-91ab-2d7cd011db47" \
    --discovery-site-id "/subscriptions/8c3c936a-c09b-4de3-830b-3f5f244d72e9/resourceGroups/ContosoITHyperV/providers/Microsoft.OffAzure/HyperVSites/migrateprojectce73site" \
    --name "migrateprojectce73collector" --project-name "migrateprojectce73project" --resource-group "contosoithyperv" 
```
##### Show #####
```
az migrate hyper-v-collector show --name "migrateprojectce73collector" --project-name "migrateprojectce73project" \
    --resource-group "contosoithyperv" 
```
##### List #####
```
az migrate hyper-v-collector list --project-name "migrateprojectce73project" --resource-group "contosoithyperv"
```
##### Delete #####
```
az migrate hyper-v-collector delete --name "migrateprojectce73collector" --project-name "migrateprojectce73project" \
    --resource-group "contosoithyperv" 
```
#### migrate v-mware-collector ####
##### Create #####
```
az migrate v-mware-collector create --e-tag "\\"01003d32-0000-0d00-0000-5d74d2e50000\\"" \
    --agent-properties-spn-details application-id="fc717575-8173-4b21-92a5-658b655e613e" audience="https://72f988bf-86f1-41af-91ab-2d7cd011db47/PortalvCenterbc2fagentauthaadapp" authority="https://login.windows.net/72f988bf-86f1-41af-91ab-2d7cd011db47" object-id="29d94f38-db94-4980-aec0-0cfd55ab1cd0" tenant-id="72f988bf-86f1-41af-91ab-2d7cd011db47" \
    --discovery-site-id "/subscriptions/6393a73f-8d55-47ef-b6dd-179b3e0c7910/resourceGroups/abgoyal-westEurope/providers/Microsoft.OffAzure/VMwareSites/PortalvCenterbc2fsite" \
    --project-name "abgoyalWEselfhostb72bproject" --resource-group "abgoyal-westEurope" \
    --name "PortalvCenterbc2fcollector" 
```
##### Show #####
```
az migrate v-mware-collector show --project-name "abgoyalWEselfhostb72bproject" --resource-group "abgoyal-westEurope" \
    --name "PortalvCenterbc2fcollector" 
```
##### List #####
```
az migrate v-mware-collector list --project-name "abgoyalWEselfhostb72bproject" --resource-group "abgoyal-westEurope"
```
##### Delete #####
```
az migrate v-mware-collector delete --project-name "abgoyalWEselfhostb72bproject" \
    --resource-group "abgoyal-westEurope" --name "PortalvCenterbc2fcollector" 
```