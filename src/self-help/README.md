# Azure CLI SelfHelp Extension

This is an extension to Azure CLI to manage SelfHelp resources.

## How to use

Install this extension using the below CLI command. For details on each command, use `-h` or `--help`.

```
az extension add --name self-help
```

## Included Commands

### _"Discovery-Solution"_ commands

- #### List DiscoverySolutions

  _Examples:_

  ```
  # Gets list of solution metadata for an azure resource.
  az self-help discovery-solution list --filter "ProblemClassificationId eq '00000000-0000-0000-0000-000000000000'" --scope 'subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myresourceGroup/providers/Microsoft.KeyVault/vaults/test-keyvault-non-read'
  ```

### _"Diagnostic"_ commands

- #### Create Diagnostic for a resource

  _Examples:_

  ```
  # Creates a diagnostic for a resource
  az self-help diagnostic create --diagnostic-name diagnostic-name  --insights [{solutionId:Demo2InsightV2}] --scope 'subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myresourceGroup/providers/Microsoft.KeyVault/vaults/test-keyvault-non-read'
  ```

- #### Show Diagnostic for a resource

  _Examples:_

  ```
  # Shows diagnostic for a resource.
  az self-help diagnostic show --diagnostic-name diagnostic-name --scope 'subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myresourceGroup/providers/Microsoft.KeyVault/vaults/test-keyvault-non-read'
  ```

### _"Solution"_ commands

- #### Create Solution for a resource

  _Examples:_

  ```
  # Creates a solution for a resource
  az self-help solution create --solution-name solution-name --trigger-criteria [{name:solutionid,value:Demo2InsightV2}] --parameters {} --scope 'subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myresourceGroup/providers/Microsoft.KeyVault/vaults/test-keyvault-non-read'
  ```

- #### Show Solution for a resource

  _Examples:_

  ```
  # Shows solution for a resource.
  az elf-help solution show --solution-name solution-name --scope 'subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myresourceGroup/providers/Microsoft.KeyVault/vaults/test-keyvault-non-read'
  ```

- #### Update Solution for a resource

  _Examples:_

  ```
  # Updates solution for a resource.
  az self-help solution update --solution-name solution-name --trigger-criteria [{name:ReplacementKey,value:<!--56ee7509-92e1-4b9e-97c2-dda53065294c-->}] --parameters {SearchText:CanNotRDP,SymptomId:KeyVaultVaultNotFoundInsight} --scope 'subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myresourceGroup/providers/Microsoft.KeyVault/vaults/test-keyvault-non-read'
  ```

### _"Troubleshooter"_ commands

- #### Create Troubleshooter for a resource

  _Examples:_

  ```
  # Creates a troubleshooter for a resource
  az self-help troubleshooter create --troubleshooter-name 12345678-BBBb-cCCCC-0000-123456789012 --solution-id e104dbdf-9e14-4c9f-bc78-21ac90382231 --parameters {ResourceUri:'subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myresourceGroup/providers/Microsoft.KeyVault/vaults/test-keyvault-non-read'} --scope 'subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myresourceGroup/providers/Microsoft.KeyVault/vaults/test-keyvault-non-read'
  ```

- #### Show troubleshooter for a resource

  _Examples:_

  ```
  # Show troubleshooter for a resource.
  az self-help troubleshooter show --troubleshooter-name 12345678-BBBb-cCCCC-0000-123456789012 --scope 'subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myresourceGroup/providers/Microsoft.KeyVault/vaults/test-keyvault-non-read'
  ```

- #### Restart troubleshooter for a resource

  _Examples:_

  ```
  # Restarts troubleshooter for a resource.
  az self-help troubleshooter restart --troubleshooter-name 12345678-BBBb-cCCCC-0000-123456789012 --scope 'subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myresourceGroup/providers/Microsoft.KeyVault/vaults/test-keyvault-non-read'
  ```

- #### End troubleshooter for a resource

  _Examples:_

  ```
  # Ends troubleshooter for a resource.
  az self-help troubleshooter end --troubleshooter-name 12345678-BBBb-cCCCC-0000-123456789012 --scope 'subscriptions/0d0fcd2e-c4fd-4349-8497-200edb3923c6/resourceGroups/myresourceGroup/providers/Microsoft.KeyVault/vaults/test-keyvault-non-read'
  ```

- #### Continue troubleshooter for a resource

  _Examples:_

  ```
  # Continues troubleshooter for a resource.
  az self-help troubleshooter continue --troubleshooter-name 12345678-BBBb-cCCCC-0000-123456789012 --step-id step-id --responses [] --scope 'subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myresourceGroup/providers/Microsoft.KeyVault/vaults/test-keyvault-non-read'
  ```

### _"Check-Name-Availability"_ commands

- #### CheckName Availabiliity

  _Examples:_

  ```
  # Check Resource Uniqueness
  az self-help check-name-availability --scope subscriptions/00000000-0000-0000-0000-000000000000 --name diagnostic-name --type 'Microsoft.Help/diagnostics'
  az self-help check-name-availability --scope subscriptions/00000000-0000-0000-0000-000000000000 --name solution-name --type 'Microsoft.Help/solutions'
  az self-help check-name-availability --scope subscriptions/00000000-0000-0000-0000-000000000000 --name 12345678-BBBb-cCCCC-0000-123456789012 --type 'Microsoft.Help/troubleshooters'
  ```
