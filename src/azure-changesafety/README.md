# Azure CLI Change Safety Extension
Azure CLI extension for managing Change Safety `ChangeState` resources used to coordinate operational changes across Azure targets.

## Installation
```bash
az extension add --source <path-to-extension-dist> --yes
# or install the latest published build
az extension add --name azure-changesafety
```

## Commands
```bash
az changesafety changerecord create  # Create a ChangeState definition for one or more targets.
az changesafety changerecord update  # Update metadata, rollout configuration, or target definitions.
az changesafety changerecord delete  # Delete a ChangeState resource.
az changesafety changerecord show    # Display details for a ChangeState resource.
```

Run `az changesafety changerecord -h` to see full parameter details and examples.

## Examples
Create a ChangeState describing a web app rollout:
```bash
az changesafety changerecord create \
  -g MyResourceGroup \
  -n changerecord-webapp-rollout \
  --change-type AppDeployment \
  --rollout-type Normal \
  --targets "resourceId=/subscriptions/<subId>/resourceGroups/MyResourceGroup/providers/Microsoft.Web/sites/myApp,operation=create" \
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

Delete a ChangeState:
```bash
az changesafety changerecord delete -g MyResourceGroup -n changerecord-webapp-rollout --yes
```

## Additional Information
- View command documentation: `az changesafety changerecord -h`
- Remove the extension when no longer needed: `az extension remove --name azure-changesafety`
