# Azure CLI testbase Extension #
This is the extension for testbase

### How to use ###
Install this extension using the below CLI command
```
az extension add --name testbase
```

### Included Features ###
#### testbase sku ####
##### List #####
```
az testbase sku list
```
#### testbase test-base-account ####
##### Create #####
```
az testbase test-base-account create --location "westus" --name "S0" --resource-group "contoso-rg1" \
    --test-base-account-name "contoso-testBaseAccount1" 

az testbase test-base-account wait --created --resource-group "{rg}" --test-base-account-name "{myTestBaseAccount}"
```
##### Show #####
```
az testbase test-base-account show --resource-group "contoso-rg1" --name "contoso-testBaseAccount1"
```
##### List #####
```
az testbase test-base-account list --resource-group "contoso-rg1"
```
##### Update #####
```
az testbase test-base-account update --name "S0" --resource-group "contoso-rg1" \
    --test-base-account-name "contoso-testBaseAccount1" 
```
##### Check-package-name-availability #####
```
az testbase test-base-account check-package-name-availability --name "testApp" \
    --type "Microsoft.TestBase/testBaseAccounts/packages" --application-name "testApp" --version "1.0.0" \
    --resource-group "contoso-rg1" --test-base-account-name "contoso-testBaseAccount1" 
```
##### Get-file-upload-url #####
```
az testbase test-base-account get-file-upload-url --blob-name "package.zip" --resource-group "contoso-rg1" \
    --name "contoso-testBaseAccount1" 
```
##### Offboard #####
```
az testbase test-base-account offboard --resource-group "contoso-rg1" --name "contoso-testBaseAccount1"
```
##### Delete #####
```
az testbase test-base-account delete --resource-group "contoso-rg1" --name "contoso-testBaseAccount1"
```
#### testbase usage ####
##### List #####
```
az testbase usage list --resource-group "contoso-rg1" --test-base-account-name "contoso-testBaseAccount1"
```
#### testbase available-os ####
##### List #####
```
az testbase available-os list --os-update-type "SecurityUpdate" --resource-group "contoso-rg" \
    --test-base-account-name "contoso-testBaseAccount" 
```
##### Show #####
```
az testbase available-os show --available-os-resource-name "Windows-10-2004" --resource-group "contoso-rg" \
    --test-base-account-name "contoso-testBaseAccount" 
```
#### testbase flighting-ring ####
##### List #####
```
az testbase flighting-ring list --resource-group "contoso-rg" --test-base-account-name "contoso-testBaseAccount"
```
##### Show #####
```
az testbase flighting-ring show --flighting-ring-resource-name "Insider-Beta-Channel" --resource-group "contoso-rg" \
    --test-base-account-name "contoso-testBaseAccount" 
```
#### testbase test-type ####
##### List #####
```
az testbase test-type list --resource-group "contoso-rg" --test-base-account-name "contoso-testBaseAccount"
```
##### Show #####
```
az testbase test-type show --resource-group "contoso-rg" --test-base-account-name "contoso-testBaseAccount" \
    --test-type-resource-name "Functional-Test" 
```
#### testbase package ####
##### Create #####
```
az testbase package create --name "contoso-package2" --location "westus" --application-name "contoso-package2" \
    --blob-path "storageAccountPath/package.zip" --flighting-ring "Insider Beta Channel" \
    --target-os-list os-update-type="Security updates" target-o-ss="Windows 10 2004" target-o-ss="Windows 10 1903" \
    --tests "[{\\"isActive\\":true,\\"testType\\":\\"OutOfBoxTest\\",\\"commands\\":[{\\"name\\":\\"Install\\",\\"action\\":\\"Install\\",\\"alwaysRun\\":true,\\"applyUpdateBefore\\":false,\\"content\\":\\"app/scripts/install/job.ps1\\",\\"contentType\\":\\"Path\\",\\"maxRunTime\\":1800,\\"restartAfter\\":true,\\"runAsInteractive\\":true,\\"runElevated\\":true},{\\"name\\":\\"Launch\\",\\"action\\":\\"Launch\\",\\"alwaysRun\\":false,\\"applyUpdateBefore\\":true,\\"content\\":\\"app/scripts/launch/job.ps1\\",\\"contentType\\":\\"Path\\",\\"maxRunTime\\":1800,\\"restartAfter\\":false,\\"runAsInteractive\\":true,\\"runElevated\\":true},{\\"name\\":\\"Close\\",\\"action\\":\\"Close\\",\\"alwaysRun\\":false,\\"applyUpdateBefore\\":false,\\"content\\":\\"app/scripts/close/job.ps1\\",\\"contentType\\":\\"Path\\",\\"maxRunTime\\":1800,\\"restartAfter\\":false,\\"runAsInteractive\\":true,\\"runElevated\\":true},{\\"name\\":\\"Uninstall\\",\\"action\\":\\"Uninstall\\",\\"alwaysRun\\":true,\\"applyUpdateBefore\\":false,\\"content\\":\\"app/scripts/uninstall/job.ps1\\",\\"contentType\\":\\"Path\\",\\"maxRunTime\\":1800,\\"restartAfter\\":false,\\"runAsInteractive\\":true,\\"runElevated\\":true}]}]" \
    --version "1.0.0" --resource-group "contoso-rg1" --test-base-account-name "contoso-testBaseAccount1" 

az testbase package wait --created --name "{myPackage}" --resource-group "{rg}" \
    --test-base-account-name "{myTestBaseAccount}" 
```
##### Show #####
```
az testbase package show --name "contoso-package2" --resource-group "contoso-rg1" \
    --test-base-account-name "contoso-testBaseAccount1" 
```
##### List #####
```
az testbase package list --resource-group "contoso-rg1" --test-base-account-name "contoso-testBaseAccount1"
```
##### Update #####
```
az testbase package update --name "contoso-package2" --blob-path "storageAccountPath/package.zip" \
    --flighting-ring "Insider Beta Channel" --is-enabled false \
    --target-os-list os-update-type="Security updates" target-o-ss="Windows 10 2004" target-o-ss="Windows 10 1903" \
    --tests "[{\\"isActive\\":true,\\"testType\\":\\"OutOfBoxTest\\",\\"commands\\":[{\\"name\\":\\"Install\\",\\"action\\":\\"Install\\",\\"alwaysRun\\":true,\\"applyUpdateBefore\\":false,\\"content\\":\\"app/scripts/install/job.ps1\\",\\"contentType\\":\\"Path\\",\\"maxRunTime\\":1800,\\"restartAfter\\":true,\\"runAsInteractive\\":true,\\"runElevated\\":true},{\\"name\\":\\"Launch\\",\\"action\\":\\"Launch\\",\\"alwaysRun\\":false,\\"applyUpdateBefore\\":true,\\"content\\":\\"app/scripts/launch/job.ps1\\",\\"contentType\\":\\"Path\\",\\"maxRunTime\\":1800,\\"restartAfter\\":false,\\"runAsInteractive\\":true,\\"runElevated\\":true},{\\"name\\":\\"Close\\",\\"action\\":\\"Close\\",\\"alwaysRun\\":false,\\"applyUpdateBefore\\":false,\\"content\\":\\"app/scripts/close/job.ps1\\",\\"contentType\\":\\"Path\\",\\"maxRunTime\\":1800,\\"restartAfter\\":false,\\"runAsInteractive\\":true,\\"runElevated\\":true},{\\"name\\":\\"Uninstall\\",\\"action\\":\\"Uninstall\\",\\"alwaysRun\\":true,\\"applyUpdateBefore\\":false,\\"content\\":\\"app/scripts/uninstall/job.ps1\\",\\"contentType\\":\\"Path\\",\\"maxRunTime\\":1800,\\"restartAfter\\":false,\\"runAsInteractive\\":true,\\"runElevated\\":true}]}]" \
    --resource-group "contoso-rg1" --test-base-account-name "contoso-testBaseAccount1" 
```
##### Get-download-url #####
```
az testbase package get-download-url --name "contoso-package2" --resource-group "contoso-rg1" \
    --test-base-account-name "contoso-testBaseAccount1" 
```
##### Hard-delete #####
```
az testbase package hard-delete --name "contoso-package2" --resource-group "contoso-rg1" \
    --test-base-account-name "contoso-testBaseAccount1" 
```
##### Delete #####
```
az testbase package delete --name "contoso-package2" --resource-group "contoso-rg1" \
    --test-base-account-name "contoso-testBaseAccount1" 
```
#### testbase test-summary ####
##### List #####
```
az testbase test-summary list --resource-group "contoso-rg1" --test-base-account-name "contoso-testBaseAccount1"
```
##### Show #####
```
az testbase test-summary show --resource-group "contoso-rg1" --test-base-account-name "contoso-testBaseAccount1" \
    --name "contoso-package2-096bffb5-5d3d-4305-a66a-953372ed6e88" 
```
#### testbase test-result ####
##### List #####
```
az testbase test-result list --filter "osName eq \'Windows 10 2004\' and releaseName eq \'2020.11B\'" \
    --os-update-type "SecurityUpdate" --package-name "contoso-package2" --resource-group "contoso-rg1" \
    --test-base-account-name "contoso-testBaseAccount1" 
```
##### Show #####
```
az testbase test-result show --package-name "contoso-package2" --resource-group "contoso-rg1" \
    --test-base-account-name "contoso-testBaseAccount1" --name "Windows-10-1909-99b1f80d-03a9-4148-997f-806ba5bac8e0" 
```
##### Get-download-url #####
```
az testbase test-result get-download-url --package-name "contoso-package2" --resource-group "contoso-rg1" \
    --test-base-account-name "contoso-testBaseAccount1" --name "Windows-10-1909-99b1f80d-03a9-4148-997f-806ba5bac8e0" 
```
##### Get-video-download-url #####
```
az testbase test-result get-video-download-url --package-name "contoso-package2" --resource-group "contoso-rg1" \
    --test-base-account-name "contoso-testBaseAccount1" --name "Windows-10-1909-99b1f80d-03a9-4148-997f-806ba5bac8e0" 
```
#### testbase os-update ####
##### List #####
```
az testbase os-update list --os-update-type "SecurityUpdate" --package-name "contoso-package2" \
    --resource-group "contoso-rg1" --test-base-account-name "contoso-testBaseAccount1" 
```
##### Show #####
```
az testbase os-update show --os-update-resource-name "Windows-10-2004-2020-12-B-505" --package-name "contoso-package2" \
    --resource-group "contoso-rg1" --test-base-account-name "contoso-testBaseAccount1" 
```
#### testbase favorite-process ####
##### Create #####
```
az testbase favorite-process create --favorite-process-resource-name "testAppProcess" \
    --package-name "contoso-package2" --actual-process-name "testApp&.exe" --resource-group "contoso-rg1" \
    --test-base-account-name "contoso-testBaseAccount1" 
```
##### Show #####
```
az testbase favorite-process show --favorite-process-resource-name "testAppProcess" --package-name "contoso-package2" \
    --resource-group "contoso-rg1" --test-base-account-name "contoso-testBaseAccount1" 
```
##### List #####
```
az testbase favorite-process list --package-name "contoso-package2" --resource-group "contoso-rg1" \
    --test-base-account-name "contoso-testBaseAccount1" 
```
##### Delete #####
```
az testbase favorite-process delete --favorite-process-resource-name "testAppProcess" \
    --package-name "contoso-package2" --resource-group "contoso-rg1" \
    --test-base-account-name "contoso-testBaseAccount1" 
```
#### testbase analysis-result ####
##### List #####
```
az testbase analysis-result list --analysis-result-type "CPURegression" --package-name "contoso-package2" \
    --resource-group "contoso-rg1" --test-base-account-name "contoso-testBaseAccount1" \
    --test-result-name "Windows-10-1909-Test-Id" 
```
##### List #####
```
az testbase analysis-result list --analysis-result-type "CPUUtilization" --package-name "contoso-package2" \
    --resource-group "contoso-rg1" --test-base-account-name "contoso-testBaseAccount1" \
    --test-result-name "Windows-10-1909-Test-Id" 
```
##### List #####
```
az testbase analysis-result list --analysis-result-type "MemoryRegression" --package-name "contoso-package2" \
    --resource-group "contoso-rg1" --test-base-account-name "contoso-testBaseAccount1" \
    --test-result-name "Windows-10-1909-Test-Id" 
```
##### List #####
```
az testbase analysis-result list --analysis-result-type "MemoryUtilization" --package-name "contoso-package2" \
    --resource-group "contoso-rg1" --test-base-account-name "contoso-testBaseAccount1" \
    --test-result-name "Windows-10-1909-Test-Id" 
```
##### Show #####
```
az testbase analysis-result show --name "cpuRegression" --package-name "contoso-package2" \
    --resource-group "contoso-rg1" --test-base-account-name "contoso-testBaseAccount1" \
    --test-result-name "Windows-10-1909-Test-Id" 
```
##### Show #####
```
az testbase analysis-result show --name "cpuUtilization" --package-name "contoso-package2" \
    --resource-group "contoso-rg1" --test-base-account-name "contoso-testBaseAccount1" \
    --test-result-name "Windows-10-1909-Test-Id" 
```
##### Show #####
```
az testbase analysis-result show --name "memoryRegression" --package-name "contoso-package2" \
    --resource-group "contoso-rg1" --test-base-account-name "contoso-testBaseAccount1" \
    --test-result-name "Windows-10-1909-Test-Id" 
```
##### Show #####
```
az testbase analysis-result show --name "memoryUtilization" --package-name "contoso-package2" \
    --resource-group "contoso-rg1" --test-base-account-name "contoso-testBaseAccount1" \
    --test-result-name "Windows-10-1909-Test-Id" 
```
#### testbase email-event ####
##### List #####
```
az testbase email-event list --resource-group "contoso-rg" --test-base-account-name "contoso-testBaseAccount"
```
##### Show #####
```
az testbase email-event show --email-event-resource-name "weekly-summary" --resource-group "contoso-rg" \
    --test-base-account-name "contoso-testBaseAccount" 
```
#### testbase customer-event ####
##### Create #####
```
az testbase customer-event create --name "WeeklySummary" --event-name "WeeklySummary" \
    --receivers "[{\\"receiverType\\":\\"UserObjects\\",\\"receiverValue\\":{\\"userObjectReceiverValue\\":{\\"userObjectIds\\":[\\"245245245245325\\",\\"365365365363565\\"]}}},{\\"receiverType\\":\\"DistributionGroup\\",\\"receiverValue\\":{\\"distributionGroupListReceiverValue\\":{\\"distributionGroups\\":[\\"test@microsoft.com\\"]}}}]" \
    --resource-group "contoso-rg1" --test-base-account-name "contoso-testBaseAccount1" 
```
##### Show #####
```
az testbase customer-event show --name "WeeklySummary" --resource-group "contoso-rg1" \
    --test-base-account-name "contoso-testBaseAccount1" 
```
##### List #####
```
az testbase customer-event list --resource-group "contoso-rg1" --test-base-account-name "contoso-testBaseAccount1"
```
##### Delete #####
```
az testbase customer-event delete --name "WeeklySummary" --resource-group "contoso-rg1" \
    --test-base-account-name "contoso-testBaseAccount1" 
```