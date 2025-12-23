# Azure CLI Change Safety Extension
Azure CLI extension for managing Change Safety `ChangeRecord` resources. A ChangeRecord describes a planned change to one or more Azure resources, enabling coordination, tracking, and safe deployment across your environment.

## Installation
```bash
az extension add --source <path-to-extension-dist> --yes
# or install the latest published build
az extension add --name azure-changesafety
```

## Commands
```bash
az changesafety changerecord create  # Create a ChangeRecord for one or more targets.
az changesafety changerecord update  # Update metadata, rollout configuration, or target definitions.
az changesafety changerecord delete  # Delete a ChangeRecord resource.
az changesafety changerecord show    # Display details for a ChangeRecord resource.
```

Run `az changesafety changerecord -h` to see full parameter details and examples.

## Examples
Create a ChangeRecord for a manual touch operation (e.g., VM maintenance):
```bash
az changesafety changerecord create \
  -g MyResourceGroup \
  -n changerecord-vm-maintenance \
  --change-type ManualTouch \
  --rollout-type Normal \
  --targets "resourceId=/subscriptions/<subId>/resourceGroups/MyResourceGroup/providers/Microsoft.Compute/virtualMachines/myVm,operation=PATCH" \
  --stagemap-name myStageMap
```

Create a ChangeRecord for an app deployment with a StageMap reference:
```bash
az changesafety changerecord create \
  -g MyResourceGroup \
  -n changerecord-webapp-rollout \
  --change-type AppDeployment \
  --rollout-type Normal \
  --targets "resourceId=/subscriptions/<subId>/resourceGroups/MyResourceGroup/providers/Microsoft.Web/sites/myApp,operation=PUT" \
  --stage-map "{resource-id:/subscriptions/<subId>/resourceGroups/MyResourceGroup/providers/Microsoft.ChangeSafety/stageMaps/rolloutStageMap}" \
  --links name=Runbook uri=https://contoso.com/runbook
```

Update the rollout type and add a comment:
```bash
az changesafety changerecord update \
  -g MyResourceGroup \
  -n changerecord-webapp-rollout \
  --rollout-type Emergency \
  --comments "Escalated due to customer impact"
```

Delete a ChangeRecord:
```bash
az changesafety changerecord delete -g MyResourceGroup -n changerecord-webapp-rollout --yes
```

## Additional Information
- View command documentation: `az changesafety changerecord -h`
- Remove the extension when no longer needed: `az extension remove --name azure-changesafety`
