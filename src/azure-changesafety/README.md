# Azure CLI Change Safety Extension
Azure CLI extension for managing Change Safety resources. This includes `ChangeRecord`, `StageMap`, and `StageProgression` resources for coordinating, tracking, and safely deploying changes across your Azure environment.

## Installation
```bash
az extension add --source <path-to-extension-dist> --yes
# or install the latest published build
az extension add --name azure-changesafety
```

## Commands

### ChangeRecord
```bash
az changesafety changerecord create  # Create a ChangeRecord for one or more targets.
az changesafety changerecord update  # Update metadata, rollout configuration, or target definitions.
az changesafety changerecord delete  # Delete a ChangeRecord resource.
az changesafety changerecord show    # Display details for a ChangeRecord resource.
az changesafety changerecord list    # List ChangeRecord resources.
```

### StageMap
```bash
az changesafety stagemap create  # Create a StageMap defining rollout stages.
az changesafety stagemap update  # Update StageMap stages.
az changesafety stagemap delete  # Delete a StageMap resource.
az changesafety stagemap show    # Display details for a StageMap resource.
az changesafety stagemap list    # List StageMap resources.
```

### StageProgression
```bash
az changesafety stageprogression create  # Create a StageProgression to track stage execution.
az changesafety stageprogression update  # Update StageProgression status or comments.
az changesafety stageprogression delete  # Delete a StageProgression resource.
az changesafety stageprogression show    # Display details for a StageProgression resource.
az changesafety stageprogression list    # List StageProgression resources for a ChangeRecord.
```

Run `az changesafety -h` to see full command groups and examples.

## Examples

### StageMap Examples
Create a two-stage StageMap for rollout:
```bash
az changesafety stagemap create \
  --stage-map-name rolloutStageMap \
  --stages "[{name:Canary,sequence:1},{name:Production,sequence:2}]"
```

### ChangeRecord Examples
Create a ChangeRecord for a manual touch operation (e.g., delete a Traffic Manager profile):
```bash
az changesafety changerecord create \
  -g MyResourceGroup \
  -n changerecord-delete-tm \
  --change-type ManualTouch \
  --rollout-type Hotfix \
  --targets "resourceId=/subscriptions/<subId>/resourceGroups/MyResourceGroup/providers/Microsoft.Network/trafficManagerProfiles/myProfile,operation=DELETE" \
  --description "Delete Traffic Manager profile for maintenance"
```

Create a ChangeRecord for an app deployment with a StageMap reference:
```bash
az changesafety changerecord create \
  -g MyResourceGroup \
  -n changerecord-webapp-rollout \
  --change-type AppDeployment \
  --rollout-type Normal \
  --targets "resourceId=/subscriptions/<subId>/resourceGroups/MyResourceGroup/providers/Microsoft.Web/sites/myApp,operation=PUT" \
  --stagemap-name rolloutStageMap \
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

### StageProgression Examples
Create a StageProgression for the Canary stage:
```bash
az changesafety stageprogression create \
  --change-record-name changerecord-webapp-rollout \
  -n canary-progression \
  --stage-reference Canary \
  --status InProgress
```

Update StageProgression to mark stage as completed:
```bash
az changesafety stageprogression update \
  --change-record-name changerecord-webapp-rollout \
  -n canary-progression \
  --status Completed \
  --comments "Canary validation passed"
```

## Additional Information
- View command documentation: `az changesafety -h`
- Remove the extension when no longer needed: `az extension remove --name azure-changesafety`
