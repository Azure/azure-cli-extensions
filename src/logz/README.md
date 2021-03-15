# Azure CLI logz Extension #
This is the extension for logz

### How to use ###
Install this extension using the below CLI command
```
az extension add --name logz
```

### Included Features ###
#### logz monitor ####
##### Create #####
```
az logz monitor create --name "myMonitor" --location "West US" \
    --plan-data billing-cycle="Monthly" effective-date="2019-08-30T15:14:33+02:00" plan-details="logzapitestplan" usage-type="Committed" \
    --user-info email-address="alice@microsoft.com" first-name="Alice" last-name="Bob" phone-number="123456" \
    --tags Environment="Dev" --resource-group "myResourceGroup" 

az logz monitor wait --created --name "{myMonitor}" --resource-group "{rg}"
```
##### Show #####
```
az logz monitor show --name "myMonitor" --resource-group "myResourceGroup"
```
##### List #####
```
az logz monitor list --resource-group "myResourceGroup"
```
##### Update #####
```
az logz monitor update --name "myMonitor" --monitoring-status "Enabled" --tags Environment="Dev" \
    --resource-group "myResourceGroup" 
```
##### List-monitored-resource #####
```
az logz monitor list-monitored-resource --name "myMonitor" --resource-group "myResourceGroup"
```
##### Delete #####
```
az logz monitor delete --name "myMonitor" --resource-group "myResourceGroup"
```
#### logz tag-rule ####
##### Create #####
```
az logz tag-rule create --monitor-name "myMonitor" --filtering-tags name="Environment" action="Include" value="Prod" \
    --filtering-tags name="Environment" action="Exclude" value="Dev" --send-aad-logs false --send-activity-logs true \
    --send-subscription-logs true --resource-group "myResourceGroup" --rule-set-name "default" 
```
##### Show #####
```
az logz tag-rule show --monitor-name "myMonitor" --resource-group "myResourceGroup" --rule-set-name "default"
```
##### List #####
```
az logz tag-rule list --monitor-name "myMonitor" --resource-group "myResourceGroup"
```
##### Delete #####
```
az logz tag-rule delete --monitor-name "myMonitor" --resource-group "myResourceGroup" --rule-set-name "default"
```
#### logz single-sign-on ####
##### Create #####
```
az logz single-sign-on create --configuration-name "default" --monitor-name "myMonitor" \
    --properties enterprise-app-id="00000000-0000-0000-0000-000000000000" single-sign-on-state="Enable" single-sign-on-url=null \
    --resource-group "myResourceGroup" 
```
##### Show #####
```
az logz single-sign-on show --configuration-name "default" --monitor-name "myMonitor" \
    --resource-group "myResourceGroup" 
```
##### List #####
```
az logz single-sign-on list --monitor-name "myMonitor" --resource-group "myResourceGroup"
```
#### logz sub-account ####
##### Create #####
```
az logz sub-account create --monitor-name "myMonitor" --type "Microsoft.Logz/monitors" --location "West US" \
    --monitoring-status "Enabled" --tags Environment="Dev" --resource-group "myResourceGroup" --name "SubAccount1" 

az logz sub-account wait --created --resource-group "{rg}" --name "{mySubAccount}"
```
##### Show #####
```
az logz sub-account show --monitor-name "myMonitor" --resource-group "myResourceGroup" --name "SubAccount1"
```
##### List #####
```
az logz sub-account list --monitor-name "myMonitor" --resource-group "myResourceGroup"
```
##### Update #####
```
az logz sub-account update --monitor-name "myMonitor" --monitoring-status "Enabled" --tags Environment="Dev" \
    --resource-group "myResourceGroup" --name "SubAccount1" 
```
##### List-monitored-resource #####
```
az logz sub-account list-monitored-resource --monitor-name "myMonitor" --resource-group "myResourceGroup" \
    --name "SubAccount1" 
```
##### Delete #####
```
az logz sub-account delete --monitor-name "myMonitor" --resource-group "myResourceGroup" --name "someName"
```
#### logz sub-account-tag-rule ####
##### Create #####
```
az logz sub-account-tag-rule create --monitor-name "myMonitor" \
    --filtering-tags name="Environment" action="Include" value="Prod" \
    --filtering-tags name="Environment" action="Exclude" value="Dev" --send-aad-logs false --send-activity-logs true \
    --send-subscription-logs true --resource-group "myResourceGroup" --rule-set-name "default" \
    --sub-account-name "SubAccount1" 
```
##### Show #####
```
az logz sub-account-tag-rule show --monitor-name "myMonitor" --resource-group "myResourceGroup" \
    --rule-set-name "default" --sub-account-name "SubAccount1" 
```
##### List #####
```
az logz sub-account-tag-rule list --monitor-name "myMonitor" --resource-group "myResourceGroup" \
    --sub-account-name "SubAccount1" 
```
##### Delete #####
```
az logz sub-account-tag-rule delete --monitor-name "myMonitor" --resource-group "myResourceGroup" \
    --rule-set-name "default" --sub-account-name "SubAccount1" 
```