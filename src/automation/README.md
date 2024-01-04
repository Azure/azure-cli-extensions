# Azure CLI automation Extension #
This package is for the 'automation' extension, i.e. 'az automation'.

### How to use ###
Install this extension using the below CLI command
```
az extension add --name automation
```

### Included Features
#### Automation Management:
Manage Automation: [more info](https://docs.microsoft.com/en-us/azure/automation/)\
*Examples:*

##### Create an Automation Account

```
az automation account create \
    --resource-group groupName \
    --name accountName \
    --location westus
```

##### Create a runbook
```
az automation runbook create \
    --resource-group groupName \
    --automation-account-name accountName \
    --name runbookName \
    --type PowerShell \
    --location westus
```

##### Set runbook content (Download [AzureAutomationTutorial.ps1](https://github.com/Azure/azure-quickstart-templates/blob/master/quickstarts/microsoft.automation/101-automation/scripts/AzureAutomationTutorial.ps1) as an example)
```
az automation runbook replace-content \
    --resource-group groupName \
    --automation-account-name accountName \
    --name runbookName \
    --content @/path/to/local/script
```

##### Publish a runbook
```
az automation runbook publish \
    --resource-group groupName \
    --automation-account-name accountName \
    --name runbookName
```

##### Start a runbook
```
az automation runbook start \
    --resource-group groupName \
    --automation-account-name accountName \
    --name runbookName
```

##### List automation jobs
```
az automation job list \
    --resource-group groupName \
    --automation-account-name accountName
```

##### Stop an automation job
```
az automation job stop \
    --resource-group groupName \
    --automation-account-name accountName \
    --name jobName
```

##### Suspend an automation job
```
az automation job suspend \
    --resource-group groupName \
    --automation-account-name accountName \
    --name jobName
```

##### Resume an automation job
```
az automation job resume \
    --resource-group groupName \
    --automation-account-name accountName \
    --name jobName
```

##### Create a hybrid runbook worker group
```
az automation hrwg create \
    --automation-account-name accountName \
    --resource-group groupName \
    --name hybridrunbookworkergroupName
```

##### List all hybrid runbook worker groups 
```
az automation hrwg list \
    --automation-account-name accountName \
    --resource-group groupName 
```

##### Get hybrid worker group
```
az automation hrwg show \
    --automation-account-name accountName \
    --resource-group groupName  \
    --name hybridrunbookworkergroupName
```

##### Update hybrid worker group
```
az automation hrwg update \
    --automation-account-name accountName \
    --resource-group groupName  \
    --name hybridrunbookworkergroupName \
    --credential "{name: credentialname}" 
```

##### Delete hybrid worker group
```
az automation hrwg delete \
    --automation-account-name accountName \
    --resource-group groupName  \
    --name hybridrunbookworkergroupName
```

##### Create a hybrid runbook worker
```
az automation hrwg hrw create \
    --automation-account-name accountName \
    --resource-group groupName \
    --hybrid-runbook-worker-group-name hybridRunbookWorkerGroupName \
    --hybrid-runbook-worker-id hybridRunbookWorkerId \
    --vm-resource-id vmResourceId
```

##### List all hybrid runbook workers in a worker group
```
az automation hrwg hrw list \
    --automation-account-name accountName \
    --resource-group groupName \
    --hybrid-runbook-worker-group-name hybridRunbookWorkerGroupName 
```

##### Get hybrid runbook worker
```
az automation hrwg hrw show \
    --automation-account-name accountName \
    --resource-group groupName \
    --hybrid-runbook-worker-group-name hybridRunbookWorkerGroupName \
    --hybrid-runbook-worker-id hybridRunbookWorkerId
```

##### delete a hybrid worker 
```
az automation hrwg hrw delete \
    --automation-account-name accountName \
    --resource-group groupName \
    --hybrid-runbook-worker-group-name hybridRunbookWorkerGroupName \
    --hybrid-runbook-worker-id hybridRunbookWorkerId
```

##### Move a hybrid runbook worker to a different hybrid runbook worker group
```
az automation hrwg hrw move \
    --automation-account-name accountName \
    --resource-group groupName \
    --hybrid-runbook-worker-group-name hybridRunbookWorkerGroupName \
    --target-hybrid-runbook-worker-group-name targetHybridWorkerGroupName \
    --hybrid-runbook-worker-id hybridRunbookWorkerId
```



If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.
