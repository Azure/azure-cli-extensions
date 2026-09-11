# ALDO Edge Operator Billing CLI One-Page Operator Runbook

## Scope
- Manage billing configuration singleton and its snapshots for the current Azure subscription.
- Command group: `az aldo-edge-operator billing-configuration`

## Prerequisites
- Azure CLI logged in:
  - `az login`
- Correct subscription selected:
  - `az account set --subscription <subscription-id>`
- Extension installed and discoverable:
  - `az extension list -o table | findstr aldo-edge-operator`

## Quick Command Map
1. Show active billing configuration
   - `az aldo-edge-operator billing-configuration show`

2. Create or replace active billing configuration
   - `az aldo-edge-operator billing-configuration create-or-update --resource-id <resource-id> --resource-name <resource-name> --stamp-id <stamp-guid> --location <region> --billing-model <model> --connection-intent <intent> --auto-renew <Enabled|Disabled> --billing-status <Enabled|Disabled> --current-cores <int> --current-pricing-model <model> --current-start-date <YYYY-MM-DD>`

3. List billing configurations in subscription
   - `az aldo-edge-operator billing-configuration list`

4. List snapshots
   - `az aldo-edge-operator billing-configuration snapshot list`

5. Show one snapshot
   - `az aldo-edge-operator billing-configuration snapshot show --snapshot-name <snapshot-name>`

## Minimum Required Arguments for create-or-update
- Required:
  - `--resource-id`
  - `--resource-name`
  - `--stamp-id`
  - `--location`
  - `--billing-model`
  - `--connection-intent`
  - `--auto-renew`
  - `--billing-status`
  - `--current-cores`
  - `--current-pricing-model`
  - `--current-start-date`

- Optional:
  - `--current-end-date`
  - `--cloud`
  - `--upcoming-cores`
  - `--upcoming-pricing-model`
  - `--upcoming-start-date`
  - `--upcoming-end-date`
  - `--azure-hybrid-windows-server-benefit`
  - `--windows-server-vm-count`

## Validation Rule You Must Remember
- If any upcoming-period field is provided, all of these must be present:
  - `--upcoming-cores`
  - `--upcoming-pricing-model`
  - `--upcoming-start-date`

## Example: Standard Update Flow
1. Inspect current state
   - `az aldo-edge-operator billing-configuration show -o jsonc`

2. Apply full replacement
   - `az aldo-edge-operator billing-configuration create-or-update --resource-id subscriptions/123/providers/Microsoft.Edge/disconnectedOperations/demo-resource --resource-name demo-resource --stamp-id 12345678-FFFF-1234-1234-123456789012 --location eastus --billing-model Capacity --connection-intent Connected --auto-renew Enabled --billing-status Enabled --current-cores 12 --current-pricing-model Trial --current-start-date 2025-11-01`

3. Verify write
   - `az aldo-edge-operator billing-configuration show -o jsonc`

4. Optional audit trail
   - `az aldo-edge-operator billing-configuration snapshot list -o table`

## Expected Result Shapes
- Show/create-or-update returns a billing configuration resource object with:
  - `id`, `name`, `type`, `properties`
- List returns an array of billing configuration resources.
- Snapshot list returns an array of snapshot resources.
- Snapshot show returns one snapshot resource.

## Common Errors and Fast Fixes
1. Missing required argument
   - Symptom: `the following arguments are required: --stamp-id`
   - Fix: Add the missing required parameter and rerun.

2. Missing snapshot name
   - Symptom: `the following arguments are required: --snapshot-name/-n`
   - Fix: Provide `--snapshot-name <value>`.

3. Partial upcoming period values
   - Symptom: `When specifying an upcoming billing period, --upcoming-cores, --upcoming-pricing-model, and --upcoming-start-date are required.`
   - Fix: Provide all three required upcoming fields, or remove upcoming fields entirely.

4. Wrong subscription context
   - Symptom: 404 or empty list when you expect data.
   - Fix:
     - `az account show`
     - `az account set --subscription <expected-subscription-id>`
     - Retry.

5. Permission errors
   - Symptom: 403 Forbidden or authorization failure.
   - Fix: Verify RBAC role for the target subscription/resource provider and retry after role propagation.

## Recommended Safe Update Sequence
1. Read current configuration with show.
2. Prepare full intended state values (this operation is replace-style).
3. Run create-or-update once with complete required arguments.
4. Re-run show and compare key fields:
   - billing model
   - connection intent
   - auto renew
   - billing status
   - current period values
5. Check snapshots list for operational traceability.
6. Capture final output in deployment logs.

## Operational Tips
- Keep date format strict: `YYYY-MM-DD`.
- Prefer jsonc output while validating manually:
  - add `-o jsonc`
- Use table output for quick inventory:
  - add `-o table`
