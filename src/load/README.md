# Azure CLI Load Testing Extension #
This is an extension to Azure CLI to create and manage Azure Load Testing resources.

## How to use ##

Install this extension using the below CLI command
```
az extension add --name load
```

### Create Azure Load Testing resource ###

```
az load create \
    --name sample-resource \
    --resource-group sample-rg \
    --location westus2
```

```
az load create \
    -n sample-resource \
    -g sample-rg \
    -l westus2
```

```
az load create \
    --name sample-resource \
    --resource-group sample-rg \
    --location westus2 \
    --tags type=testing target=infra
```

```
az load create \
    --name sample-resource \
    --resource-group sample-rg \
    --location westus2 \
    --identity-type SystemAssigned,UserAssigned \
    --user-assigned "{'/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/sample-rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/sample-mi':{}}"
```

```
az load create \
    --name sample-resource \
    --resource-group sample-rg \
    --location westus2 \
    --identity-type SystemAssigned,UserAssigned \
    --user-assigned "{'/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/sample-rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/sample-mi':{}}" \
    --encryption-key https://sample-kv.vault.azure.net/keys/samplekey/2d1ccd5c50234ea2a0858fe148b69cde \
    --encryption-identity /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/sample-rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/sample-mi

```
---
<br/>

### Update Azure Load Testing resource ###

```
az load update \
    --name sample-resource \
    --resource-group sample-rg \
    --identity-type SystemAssigned
```
```
az load update \
    --name sample-resource \
    --resource-group sample-rg \
    --tags type=server
```
```
az load update \
    --name sample-resource \
    --resource-group sample-rg \
    --encryption-key https://sample-kv.vault.azure.net/keys/samplekey2/2d1ccd5c50234ea2a0858fe148b69cde
```

```
az load update \
    --name sample-resource \
    --resource-group sample-rg \
    --identity-type SystemAssigned,UserAssigned \
    --user-assigned "{'/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/sample-rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/sample-mi':{}}" \
    --encryption-key https://sample-kv.vault.azure.net/keys/samplekey2/2d1ccd5c50234ea2a0858fe148b69cde \
    --encryption-identity SystemAssigned
```
---
<br/>

### List Azure Load Testing resources ###

```
az load list \
    --resource-group sample-rg 
```

```
az load list
```
---
<br/>

### Show Azure Load Testing resource ###

```
az load show \
    --name sample-resource \
    --resource-group sample-rg 
```

```
az load show \
    --ids /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/sample-rg/providers/Microsoft.LoadTestService/loadtests/sample-resource1 /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/sample-rg2/providers/Microsoft.LoadTestService/loadtests/sample-resource2 
```
---
<br/>

### Delete Azure Load Testing resource ###

```
az load delete \
    --name sample-resource \
    --resource-group sample-rg 
```

```
az load delete \
    --ids /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/sample-rg/providers/Microsoft.LoadTestService/loadtests/sample-resource1 /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/sample-rg2/providers/Microsoft.LoadTestService/loadtests/sample-resource2 
```
---
<br/>

## Project Structure ##

### Root Directory: `src/load/azext_load/` ###

- **_help.py**: Imports and updates help documentation for the extension commands both control and data plane.
- **commands.py**: Registers the control plane commands for the extension, `az load`.
- **data_plane/**: Contains the data plane commands and utilities.

### Data Plane Directory: `src/load/azext_load/data_plane/` ###

- **\_\_init\_\_.py**: Initializes the respective modules and sets up the command loader.
- **client_factory.py**: Provides factory methods to create instances of data plane clients, such as `LoadTestRunClient` and `LoadTestAdministrationClient`.
- **help.py**: Provides help documentation for the data plane commands.
- **params.py**: Defines the common parameters for the `az load test` and `az load test-run` commands.
- **load_test/**: Contains commands and utilities specific to load tests.
  - **commands.py**: Registers the sub command groups for `az load test`.
  - **custom.py**: Implements the logic for load test commands, such as creating, updating, and deleting load tests.
  - **help.py**: Provides help documentation with samples for load test commands.
  - **params.py**: Defines parameters for load test commands.
- **load_test_run/**: Contains commands and utilities specific to load test runs.
  - **commands.py**: Registers the sub command groups for `az load test-run`.
  - **custom.py**: Implements the logic for load test run commands, such as creating, updating, and deleting load test runs.
  - **help.py**: Provides help documentation with samples for load test run commands.
  - **params.py**: Defines parameters for load test run commands.
- **utils/**: Contains utility functions and constants.
  - **constants.py**: Defines constants used across the extension.
  - **utils.py**: Provides utility functions for common operations, such as uploading files, parsing YAML configurations, and handling errors.
  - **utils_yaml_config.py**: Provides functions to parse and validate YAML configuration data to be used for request payload for load tests.
  - **validators.py**: Implements validation functions to ensure that command parameters meet the required criteria.
  - **argtypes.py**: Creates custom argument types to handle specific input formats or validation rules required by the data plane commands. Also provides concise help texts to be displayed in CLI against each argument.
  - **completers.py**: Defines functions that provide dynamic completion suggestions for specific command-line arguments. We have these implemented for test id and test run id so far. *Note: Completers are not supported in powershell.*
  - **models.py**: Stores data models.
