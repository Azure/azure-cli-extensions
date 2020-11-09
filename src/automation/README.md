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

##### Set runbook content (Download [AzureAutomationTutorial.ps1](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/101-automation/scripts/AzureAutomationTutorial.ps1) as an example)
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

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.