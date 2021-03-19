# Azure CLI elastic Extension #
This is the extension for elastic

### How to use ###
Install this extension using the below CLI command
```
az extension add --name elastic
```

### Included Features ###
#### elastic monitor ####
##### Create #####
```
az elastic monitor create --monitor-name "myMonitor" --name "myMonitor" --location "West US 2" \
    --user-info "{\\"companyInfo\\":{\\"business\\":\\"Technology\\",\\"country\\":\\"US\\",\\"domain\\":\\"microsoft.com\\",\\"employeeNumber\\":\\"10000\\",\\"state\\":\\"WA\\"},\\"companyName\\":\\"Microsoft\\",\\"emailAddress\\":\\"alice@microsoft.com\\",\\"firstName\\":\\"Alice\\",\\"lastName\\":\\"Bob\\"}" \
    --name "free_Monthly" --tags Environment="Dev" --resource-group "myResourceGroup" 

az elastic monitor wait --created --monitor-name "{myMonitor}" --resource-group "{rg}"
```
##### Show #####
```
az elastic monitor show --name "myMonitor" --resource-group "myResourceGroup"
```
##### List #####
```
az elastic monitor list --resource-group "myResourceGroup"
```
##### Update #####
```
az elastic monitor update --name "myMonitor" --tags Environment="Dev" --resource-group "myResourceGroup"
```
##### Delete #####
```
az elastic monitor delete --name "myMonitor" --resource-group "myResourceGroup"
```
#### elastic monitored-resource ####
##### List #####
```
az elastic monitored-resource list --monitor-name "myMonitor" --resource-group "myResourceGroup"
```
#### elastic deployment-info ####
##### List #####
```
az elastic deployment-info list --monitor-name "myMonitor" --resource-group "myResourceGroup"
```
#### elastic tag-rule ####
##### Create #####
```
az elastic tag-rule create --monitor-name "myMonitor" \
    --filtering-tags name="Environment" action="Include" value="Prod" \
    --filtering-tags name="Environment" action="Exclude" value="Dev" --send-aad-logs false --send-activity-logs true \
    --send-subscription-logs true --resource-group "myResourceGroup" --rule-set-name "default" 
```
##### Show #####
```
az elastic tag-rule show --monitor-name "myMonitor" --resource-group "myResourceGroup" --rule-set-name "default"
```
##### List #####
```
az elastic tag-rule list --monitor-name "myMonitor" --resource-group "myResourceGroup"
```
##### Delete #####
```
az elastic tag-rule delete --monitor-name "myMonitor" --resource-group "myResourceGroup" --rule-set-name "default"
```