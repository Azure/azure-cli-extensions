Microsoft Azure CLI 'scheduled-query' Extension
==========================================

This package is for the 'scheduled-query' extension.
i.e. 'az scheduled-query'

### How to use ###

Install this extension using the below CLI command:

```
az extension add --name scheduled-query
```

### Sample Commands ###

Create a scheduled query for a vm:

```
az monitor scheduled-query create -g {ResourceGroup} -n {nameofthealert} --scopes {vm_id} --condition "count \'union Event, Syslog | where TimeGenerated > ago(1h) | where EventLevelName == \"Error\" or SeverityLevel== \"err\"\' > 360" --description {descriptionofthealert}
```

Update the scheduled query for a vm:

```
az monitor scheduled-query update -g {ResourceGroup} -n {nameofthealert} --condition "count \'union Event, Syslog | where TimeGenerated > ago(1h) | where EventLevelName == \"Error\" or SeverityLevel== \"err\"\' > 360" --description {descriptionofthealert}
```

Show the detail of a scheduled query:

```
az monitor scheduled-query show -g {ResourceGroup} -n {nameofthealert}
```

List all scheduled queries in a resource group:

```
az monitor scheduled-query list -g {ResourceGroup}
```

List scheduled query by id:

```
az monitor scheduled-query show --ids {RuleResourceId}
```

Delete the scheduled query:

```
az monitor scheduled-query delete -g {ResourceGroup} -n {nameofthealert}
```
