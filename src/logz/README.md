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
##### List-payload #####
```
az logz monitor list-payload --name "myMonitor" --resource-group "myResourceGroup"
```
##### List-resource #####
```
az logz monitor list-resource --name "myMonitor" --resource-group "myResourceGroup"
```
##### List-role #####
```
az logz monitor list-role --name "myMonitor" --resource-group "myResourceGroup"
```
##### List-vm #####
```
az logz monitor list-vm --name "myMonitor" --resource-group "myResourceGroup"
```
##### Update-vm #####
```
az logz monitor update-vm --name "myMonitor" --state "Install" --resource-group "myResourceGroup"
```
##### Delete #####
```
az logz monitor delete --name "myMonitor" --resource-group "myResourceGroup"
```
#### logz rule ####
##### Create #####
```
az logz rule create --monitor-name "myMonitor" --filtering-tags name="Environment" action="Include" value="Prod" \
    --filtering-tags name="Environment" action="Exclude" value="Dev" --send-aad-logs false --send-activity-logs true \
    --send-subscription-logs true --resource-group "myResourceGroup" --rule-set-name "default" 
```
##### Show #####
```
az logz rule show --monitor-name "myMonitor" --resource-group "myResourceGroup" --rule-set-name "default"
```
##### List #####
```
az logz rule list --monitor-name "myMonitor" --resource-group "myResourceGroup"
```
##### Delete #####
```
az logz rule delete --monitor-name "myMonitor" --resource-group "myResourceGroup" --rule-set-name "default"
```
#### logz sso ####
##### Create #####
```
az logz sso create --configuration-name "default" --monitor-name "myMonitor" \
    --properties enterprise-app-id="00000000-0000-0000-0000-000000000000" single-sign-on-state="Enable" single-sign-on-url=null \
    --resource-group "myResourceGroup" 
```
##### Show #####
```
az logz sso show --configuration-name "default" --monitor-name "myMonitor" --resource-group "myResourceGroup"
```
##### List #####
```
az logz sso list --monitor-name "myMonitor" --resource-group "myResourceGroup"
```
#### logz sub-account ####
##### Create #####
```
az logz sub-account create --monitor-name "myMonitor" --type "Microsoft.Logz/monitors" --location "West US" \
    --monitoring-status "Enabled" --tags Environment="Dev" --resource-group "myResourceGroup" --name "SubAccount1" 

az logz sub-account wait --created --monitor-name "{myMonitor}" --resource-group "{rg}" --name "{mySubAccount}"
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
##### List-payload #####
```
az logz sub-account list-payload --monitor-name "myMonitor" --resource-group "myResourceGroup" --name "SubAccount1"
```
##### List-resource #####
```
az logz sub-account list-resource --monitor-name "myMonitor" --resource-group "myResourceGroup" --name "SubAccount1"
```
##### List-vm #####
```
az logz sub-account list-vm --monitor-name "myMonitor" --resource-group "myResourceGroup" --name "SubAccount1"
```
##### Update-vm #####
```
az logz sub-account update-vm --monitor-name "myMonitor" --state "Install" --resource-group "myResourceGroup" \
    --name "SubAccount1" 
```
##### Delete #####
```
az logz sub-account delete --monitor-name "myMonitor" --resource-group "myResourceGroup" --name "someName"
```
#### logz sub-rule ####
##### Create #####
```
az logz sub-rule create --monitor-name "myMonitor" --filtering-tags name="Environment" action="Include" value="Prod" \
    --filtering-tags name="Environment" action="Exclude" value="Dev" --send-aad-logs false --send-activity-logs true \
    --send-subscription-logs true --resource-group "myResourceGroup" --rule-set-name "default" \
    --sub-account-name "SubAccount1" 
```
##### Show #####
```
az logz sub-rule show --monitor-name "myMonitor" --resource-group "myResourceGroup" --rule-set-name "default" \
    --sub-account-name "SubAccount1" 
```
##### List #####
```
az logz sub-rule list --monitor-name "myMonitor" --resource-group "myResourceGroup" --sub-account-name "SubAccount1"
```
##### Delete #####
```
az logz sub-rule delete --monitor-name "myMonitor" --resource-group "myResourceGroup" --rule-set-name "default" \
    --sub-account-name "SubAccount1" 
```