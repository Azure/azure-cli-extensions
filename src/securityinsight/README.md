# Azure CLI sentinel Extension #
This is the extension for sentinel

### How to use ###
Install this extension using the below CLI command
```
az extension add --name sentinel
```

### Included Features ###
#### sentinel alert-rule ####
##### Create #####
```
az sentinel alert-rule create --etag "\\"0300bf09-0000-0000-0000-5c37296e0000\\"" \
    --logic-app-resource-id "/subscriptions/d0cfe6b2-9ac0-4464-9919-dccaee2e48c0/resourceGroups/myRg/providers/Microsoft.Logic/workflows/MyAlerts" \
    --trigger-uri "https://prod-31.northcentralus.logic.azure.com:443/workflows/cd3765391efd48549fd7681ded1d48d7/triggers/manual/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=signature" \
    --action-id "912bec42-cb66-4c03-ac63-1761b6898c3e" --resource-group "myRg" \
    --rule-id "73e01a99-5cd7-4139-a149-9f2736ff2ab5" --workspace-name "myWorkspace" 
```
##### Show #####
```
az sentinel alert-rule show --resource-group "myRg" --rule-id "myFirstFusionRule" --workspace-name "myWorkspace"
```
##### Show #####
```
az sentinel alert-rule show --resource-group "myRg" --rule-id "microsoftSecurityIncidentCreationRuleExample" \
    --workspace-name "myWorkspace" 
```
##### Show #####
```
az sentinel alert-rule show --resource-group "myRg" --rule-id "73e01a99-5cd7-4139-a149-9f2736ff2ab5" \
    --workspace-name "myWorkspace" 
```
##### List #####
```
az sentinel alert-rule list --resource-group "myRg" --workspace-name "myWorkspace"
```
##### Get-action #####
```
az sentinel alert-rule get-action --action-id "912bec42-cb66-4c03-ac63-1761b6898c3e" --resource-group "myRg" \
    --rule-id "73e01a99-5cd7-4139-a149-9f2736ff2ab5" --workspace-name "myWorkspace" 
```
##### Delete #####
```
az sentinel alert-rule delete --action-id "912bec42-cb66-4c03-ac63-1761b6898c3e" --resource-group "myRg" \
    --rule-id "73e01a99-5cd7-4139-a149-9f2736ff2ab5" --workspace-name "myWorkspace" 
```
#### sentinel action ####
##### List #####
```
az sentinel action list --resource-group "myRg" --rule-id "73e01a99-5cd7-4139-a149-9f2736ff2ab5" \
    --workspace-name "myWorkspace" 
```
#### sentinel alert-rule-template ####
##### List #####
```
az sentinel alert-rule-template list --resource-group "myRg" --workspace-name "myWorkspace"
```
##### Show #####
```
az sentinel alert-rule-template show --alert-rule-template-id "65360bb0-8986-4ade-a89d-af3cf44d28aa" \
    --resource-group "myRg" --workspace-name "myWorkspace" 
```
#### sentinel bookmark ####
##### Create #####
```
az sentinel bookmark create --etag "\\"0300bf09-0000-0000-0000-5c37296e0000\\"" --created "2019-01-01T13:15:30Z" \
    --display-name "My bookmark" --labels "Tag1" --labels "Tag2" --notes "Found a suspicious activity" \
    --query "SecurityEvent | where TimeGenerated > ago(1d) and TimeGenerated < ago(2d)" \
    --query-result "Security Event query result" --updated "2019-01-01T13:15:30Z" \
    --bookmark-id "73e01a99-5cd7-4139-a149-9f2736ff2ab5" --resource-group "myRg" --workspace-name "myWorkspace" 
```
##### Show #####
```
az sentinel bookmark show --bookmark-id "73e01a99-5cd7-4139-a149-9f2736ff2ab5" --resource-group "myRg" \
    --workspace-name "myWorkspace" 
```
##### List #####
```
az sentinel bookmark list --resource-group "myRg" --workspace-name "myWorkspace"
```
##### Delete #####
```
az sentinel bookmark delete --bookmark-id "73e01a99-5cd7-4139-a149-9f2736ff2ab5" --resource-group "myRg" \
    --workspace-name "myWorkspace" 
```
#### sentinel data-connector ####
##### Create #####
```
az sentinel data-connector create \
    --office-data-connector etag="\\"0300bf09-0000-0000-0000-5c37296e0000\\"" tenant-id="2070ecc9-b4d5-4ae4-adaa-936fa1954fa8" \
    --data-connector-id "73e01a99-5cd7-4139-a149-9f2736ff2ab5" --resource-group "myRg" --workspace-name "myWorkspace" 
```
##### Show #####
```
az sentinel data-connector show --data-connector-id "763f9fa1-c2d3-4fa2-93e9-bccd4899aa12" --resource-group "myRg" \
    --workspace-name "myWorkspace" 
```
##### Show #####
```
az sentinel data-connector show --data-connector-id "b96d014d-b5c2-4a01-9aba-a8058f629d42" --resource-group "myRg" \
    --workspace-name "myWorkspace" 
```
##### Show #####
```
az sentinel data-connector show --data-connector-id "06b3ccb8-1384-4bcc-aec7-852f6d57161b" --resource-group "myRg" \
    --workspace-name "myWorkspace" 
```
##### Show #####
```
az sentinel data-connector show --data-connector-id "c345bf40-8509-4ed2-b947-50cb773aaf04" --resource-group "myRg" \
    --workspace-name "myWorkspace" 
```
##### Show #####
```
az sentinel data-connector show --data-connector-id "f0cd27d2-5f03-4c06-ba31-d2dc82dcb51d" --resource-group "myRg" \
    --workspace-name "myWorkspace" 
```
##### Show #####
```
az sentinel data-connector show --data-connector-id "07e42cb3-e658-4e90-801c-efa0f29d3d44" --resource-group "myRg" \
    --workspace-name "myWorkspace" 
```
##### Show #####
```
az sentinel data-connector show --data-connector-id "c345bf40-8509-4ed2-b947-50cb773aaf04" --resource-group "myRg" \
    --workspace-name "myWorkspace" 
```
##### Show #####
```
az sentinel data-connector show --data-connector-id "73e01a99-5cd7-4139-a149-9f2736ff2ab5" --resource-group "myRg" \
    --workspace-name "myWorkspace" 
```
##### List #####
```
az sentinel data-connector list --resource-group "myRg" --workspace-name "myWorkspace"
```
##### Delete #####
```
az sentinel data-connector delete --data-connector-id "73e01a99-5cd7-4139-a149-9f2736ff2ab5" --resource-group "myRg" \
    --workspace-name "myWorkspace" 
```
#### sentinel incident ####
##### Create #####
```
az sentinel incident create --etag "\\"0300bf09-0000-0000-0000-5c37296e0000\\"" \
    --description "This is a demo incident" --classification "FalsePositive" \
    --classification-comment "Not a malicious activity" --classification-reason "IncorrectAlertLogic" \
    --first-activity-time-utc "2019-01-01T13:00:30Z" --last-activity-time-utc "2019-01-01T13:05:30Z" \
    --owner object-id="2046feea-040d-4a46-9e2b-91c2941bfa70" --severity "High" --status "Closed" --title "My incident" \
    --incident-id "73e01a99-5cd7-4139-a149-9f2736ff2ab5" --resource-group "myRg" --workspace-name "myWorkspace" 
```
##### Show #####
```
az sentinel incident show --incident-id "73e01a99-5cd7-4139-a149-9f2736ff2ab5" --resource-group "myRg" \
    --workspace-name "myWorkspace" 
```
##### List #####
```
az sentinel incident list --orderby "properties/createdTimeUtc desc" --top 1 --resource-group "myRg" \
    --workspace-name "myWorkspace" 
```
##### Delete #####
```
az sentinel incident delete --incident-id "73e01a99-5cd7-4139-a149-9f2736ff2ab5" --resource-group "myRg" \
    --workspace-name "myWorkspace" 
```
#### sentinel incident-comment ####
##### Create #####
```
az sentinel incident-comment create --message "Some message" \
    --incident-comment-id "4bb36b7b-26ff-4d1c-9cbe-0d8ab3da0014" --incident-id "73e01a99-5cd7-4139-a149-9f2736ff2ab5" \
    --resource-group "myRg" --workspace-name "myWorkspace" 
```
##### Show #####
```
az sentinel incident-comment show --incident-comment-id "4bb36b7b-26ff-4d1c-9cbe-0d8ab3da0014" \
    --incident-id "73e01a99-5cd7-4139-a149-9f2736ff2ab5" --resource-group "myRg" --workspace-name "myWorkspace" 
```
##### List #####
```
az sentinel incident-comment list --incident-id "73e01a99-5cd7-4139-a149-9f2736ff2ab5" --resource-group "myRg" \
    --workspace-name "myWorkspace" 
```