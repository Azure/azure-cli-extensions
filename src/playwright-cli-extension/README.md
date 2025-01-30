# Azure CLI PlaywrightCliExtension Extension #
This is an extension to Azure CLI to create and manage Playwright Testing resources.

## How to use ##

Install this extension using the below CLI command
```
az extension add --name playwright-cli-extension
```

### Create Azure Playwright Testing resource ###

```
az playwright-testing workspace create \
    --resource-group SampleRG \
    --workspace-name myPlaywrightWorkspace \
    --location westus \
    --regional-affinity Enabled
```

```
az playwright-testing workspace create \
    -g SampleRG \
    -n myPlaywrightWorkspace \
    -l westus \
    --regional-affinity Enabled
```

```
az playwright-testing workspace create \
    -g SampleRG \
    -n myPlaywrightWorkspace \
    -l westus \
    --local-auth Enabled
```
---
<br/>

### Update Azure Playwright Testing resource  ###

```
az playwright-testing workspace update \
    --resource-group SampleRG \
    --workspace-name myPlaywrightWorkspace \
    --regional-affinity Disabled
```

```
az playwright-testing workspace update \
    --resource-group SampleRG \
    --workspace-name myPlaywrightWorkspace \
    --reporting Disabled
```
---
<br/>

### List Azure Playwright Testing resource ###

```
az playwright-testing workspace list \
    --resource-group sample-rg 
```

```
az playwright-testing workspace list
```
---
<br/>

### Show Azure Playwright Testing resource ###

```
az playwright-testing workspace show \
     --resource-group SampleRG \
     --workspace-name myPlaywrightWorkspace
```
---
<br/>

### Delete Azure Playwright Testing resource ###

```
az playwright-testing workspace delete \
    --resource-group SampleRG \
    --workspace-name myPlaywrightWorkspace
```
---
<br/>

### List Azure Playwright Testing resource quota ###

```
az playwright-testing workspace quota list \
    --resource-group SampleRG \
    --workspace-name myPlaywrightWorkspace
```
---
<br/>

### Show Azure Playwright Testing resource quota ###

```
az playwright-testing workspace quota show \
    --resource-group SampleRG \
    --workspace-name myPlaywrightWorkspace \
    --quota-name ScalableExecution
```

```
az playwright-testing workspace quota show \
    --resource-group SampleRG \
    --workspace-name myPlaywrightWorkspace \
    --quota-name Reporting
```
---
<br/>

### List Azure Playwright Testing quota ###

```
az playwright-testing quota list \
    --location eastus
```
---
<br/>

### Show Azure Playwright Testing quota ###

```
az playwright-testing quota show \
    --location eastus \
    --quota-name ScalableExecution
```

```
az playwright-testing quota show \
    --location eastus \
    --quota-name Reporting
```
---
<br/>