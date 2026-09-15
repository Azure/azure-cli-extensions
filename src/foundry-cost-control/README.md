# Azure CLI Foundry Cost Control Extension

This is an extension to Azure CLI to manage Foundry Cost Control policies.

## Install and get usage help

Add the extension:

```
az extension add --name foundry-cost-control
```

Verify your installation by viewing all extensions:

```
az extension list --output table
```

Get help on the commands:

```
az cognitiveservices account --help
az cognitiveservices account deployment --help
az cognitiveservices account costcontrol --help
```

For usage examples see the test file `azext_foundry_cost_control/tests/latest/test_foundry_cost_control.py`.

## Cost control CRUD operations

Cost-control policy commands use `az cognitiveservices account costcontrol`.
The examples below assume that the owning AI Services account already exists.

First, save the following rule definition as `cost-control-rules.json`:

```json
[
  {
    "name": "per-agent-monthly",
    "counterKey": [
      {
        "type": "agent"
      }
    ],
    "unit": "usd",
    "amount": 200,
    "period": "month",
    "recurring": true,
    "match": {
      "foundryCallerAgentId": [
        "agent-123"
      ]
    },
    "thresholds": [
      {
        "type": "percentage",
        "value": 80,
        "action": "alert"
      },
      {
        "type": "absolute",
        "value": 0,
        "action": "audit"
      }
    ]
  }
]
```

Set values used by the examples:

```powershell
$resourceGroup = "my-resource-group"
$accountName = "my-account"
$costControlName = "production-agents"
$rulesFile = ".\cost-control-rules.json"
```

### Create

Create a cost control and save its resource ID for use when attaching it to an
account or deployment:

```powershell
$costControlId = az cognitiveservices account costcontrol create `
  --resource-group $resourceGroup `
  --account-name $accountName `
  --cost-control-name $costControlName `
  --display-name "Production agent monthly budget" `
  --rules "@$rulesFile" `
  --query id `
  --output tsv
```

### List

List all cost controls owned by an account:

```powershell
az cognitiveservices account costcontrol list `
  --resource-group $resourceGroup `
  --account-name $accountName `
  --output table
```

### Show

Get a specific cost control:

```powershell
az cognitiveservices account costcontrol show `
  --resource-group $resourceGroup `
  --account-name $accountName `
  --cost-control-name $costControlName
```

### Update

Update the display name while preserving the existing rules:

```powershell
az cognitiveservices account costcontrol update `
  --resource-group $resourceGroup `
  --account-name $accountName `
  --cost-control-name $costControlName `
  --display-name "Updated production agent monthly budget"
```

To replace the rules, also pass `--rules "@$rulesFile"` with the updated rules
file.

### Delete

Detach the cost control from any accounts or deployments that use it, and then
delete it:

```powershell
az cognitiveservices account costcontrol delete `
  --resource-group $resourceGroup `
  --account-name $accountName `
  --cost-control-name $costControlName `
  --yes
```

## Attach cost controls to an account

The extension overrides `az cognitiveservices account update` to add preview
arguments for attaching cost controls and configuring account-level telemetry
and event connections:

```powershell
az cognitiveservices account update `
  --name my-account `
  --resource-group my-resource-group `
  --cost-control-ids $costControlId1 $costControlId2 `
  --cost-control-connections '{
    "appInsightsConnectionId": "/subscriptions/.../connections/application-insights",
    "eventGridConnectionId": "/subscriptions/.../connections/event-grid"
  }'
```

Remove all cost-control attachments by specifying the argument without values:

```powershell
az cognitiveservices account update `
  --name my-account `
  --resource-group my-resource-group `
  --cost-control-ids
```

Remove the configured account-level connections with:

```powershell
az cognitiveservices account update `
  --name my-account `
  --resource-group my-resource-group `
  --clear-cost-control-connections
```

These arguments use the `2026-09-15-preview` Cognitive Services Management API.

## Attach a cost control to a deployment

Create a deployment with its cost-control attachment in the same request:

```powershell
az cognitiveservices account deployment create `
  --name my-account `
  --resource-group my-resource-group `
  --deployment-name my-deployment `
  --model-name gpt-4.1 `
  --model-version 2025-04-14 `
  --model-format OpenAI `
  --sku-name GlobalStandard `
  --sku-capacity 10 `
  --cost-control-ids $costControlId
```

Update or clear the attachment on an existing deployment:

```powershell
az cognitiveservices account deployment update `
  --name my-account `
  --resource-group my-resource-group `
  --deployment-name my-deployment `
  --cost-control-ids $costControlId

az cognitiveservices account deployment update `
  --name my-account `
  --resource-group my-resource-group `
  --deployment-name my-deployment `
  --cost-control-ids
```

The current preview supports at most one cost control per deployment.