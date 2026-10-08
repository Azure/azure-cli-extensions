# Azure CLI monitor-trace-association Extension #

This is an extension to Azure CLI to manage Azure Monitor **Trace Associations**
(`Microsoft.Monitor/traceAssociations`) resources.

A trace association is an ARM **extension resource** that maps a scope (an Application
Insights component, a resource group, or a subscription) to an Azure Monitor Workspace
for trace routing. Each scope has at most one direct association (singleton `default`);
multi-homing is achieved through inheritance from parent scopes.

> **Preview / DRAFT.** This extension targets API version `2026-01-01-preview`, whose
> spec currently lives in the private `azure-rest-api-specs-pr` repo
> (PR [#27737](https://github.com/Azure/azure-rest-api-specs-pr/pull/27737)). The command
> bodies here are a functional prototype that call ARM directly; they will be **replaced
> by aaz-dev-generated code** once the spec is published to the public
> `Azure/azure-rest-api-specs` repo. Do not merge until then.

## How to use ##
Install this extension using the below CLI command
```
az extension add --name monitor-trace-association
```

### Included Features
#### trace-association
##### Create / update
```
az monitor trace-association create \
  --resource-uri "subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myRg/providers/Microsoft.Insights/components/myAppInsights" \
  --azure-monitor-workspace-resource-id "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/obs-rg/providers/Microsoft.Monitor/accounts/app-amw"
```
##### Show
```
az monitor trace-association show \
  --resource-uri "subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myRg/providers/Microsoft.Insights/components/myAppInsights"
```
##### List (by scope)
```
az monitor trace-association list \
  --resource-uri "subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myRg/providers/Microsoft.Insights/components/myAppInsights"
```
##### Delete
```
az monitor trace-association delete \
  --resource-uri "subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myRg/providers/Microsoft.Insights/components/myAppInsights"
```

The singleton name defaults to `default`; pass `--name/-n default` to be explicit.
