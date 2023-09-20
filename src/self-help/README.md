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
  # Show diagnostic for a resource.
  az self-help diagnostic show --diagnostic-name {diagnostic-name} --scope {scope}
  ```

### _"Check-Name-Availability"_ commands

- #### CheckName Availabiliity

  _Examples:_

  ```
  # Checks name available of a diagnostic resource.
  az self-help check-name-availability --scope subscriptionId/{subId} --name {diagnostic-name} --type 'Microsoft.Help/diagnostics'
  ```
