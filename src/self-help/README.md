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
  az self-help discovery-solution list --scope {scope}
  ```

### _"Diagnostic"_ commands

- #### Create Diagnostic for a resource

  _Examples:_

  ```
  # Creates a diagnostic for a resource
  az self-help diagnostic create --diagnostic-name {diagnostic-name}  --insights [{solutionId:Demo2InsightV2}] --scope {scope}
  ```

- #### Show Diagnostic for a resource

  _Examples:_

  ```
  # Shows diagnostic for a resource.
  az self-help diagnostic show --diagnostic-name {diagnostic-name} --scope {scope}
  ```

### _"Solution"_ commands

- #### Create Solution for a resource

  _Examples:_

  ```
  # Creates a solution for a resource
  az self-help solution create --solution-name {solution-name} --trigger-criteria {trigger-criteria} --parameters {parameters} --scope {scope}
  ```

- #### Show Solution for a resource

  _Examples:_

  ```
  # Shows solution for a resource.
  az self-help solution show --solution-name {solution-name} --scope {scope}
  ```

- #### Update Solution for a resource

  _Examples:_

  ```
  # Updates solution for a resource.
  az self-help solution update --solution-name {solution-name} --trigger-criteria {trigger-criteria} --parameters {parameters} --scope {scope}
  ```

### _"Troubleshooter"_ commands

- #### Create Troubleshooter for a resource

  _Examples:_

  ```
  # Creates a troubleshooter for a resource
  az self-help troubleshooter create --troubleshooter-name {troubleshooter-name} --solution-id {solution-id} --parameters {parameters} --scope {scope}
  ```

- #### Show troubleshooter for a resource

  _Examples:_

  ```
  # Show troubleshooter for a resource.
  az self-help troubleshooter show --troubleshooter-name {troubleshooter-name} --scope {scope}
  ```

- #### Restart troubleshooter for a resource

  _Examples:_

  ```
  # Restarts troubleshooter for a resource.
  az self-help troubleshooter restart --troubleshooter-name {troubleshooter-name} --scope {scope}
  ```

- #### End troubleshooter for a resource

  _Examples:_

  ```
  # Ends troubleshooter for a resource.
  az self-help troubleshooter show --troubleshooter-name {troubleshooter-name} --scope {scope}
  ```

- #### Continue troubleshooter for a resource

  _Examples:_

  ```
  # Continues troubleshooter for a resource.
  az self-help troubleshooter continue --troubleshooter-name {troubleshooter-name} --step-id {step-id} --responses [] --scope {scope}
  ```

### _"Check-Name-Availability"_ commands

- #### CheckName Availabiliity

  _Examples:_

  ```
  # Check Resource Uniqueness
  az self-help check-name-availability --scope subscriptions/{subId} --name {diagnostic-name} --type 'Microsoft.Help/diagnostics'
  az self-help check-name-availability --scope subscriptions/{subId} --name {solution-name} --type 'Microsoft.Help/solutions'
  az self-help check-name-availability --scope subscriptions/{subId} --name {troubleshooter-name} --type 'Microsoft.Help/troubleshooters'
  ```
