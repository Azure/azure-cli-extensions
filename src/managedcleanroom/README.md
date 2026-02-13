# Azure CLI ManagedCleanRoom Extension #
This is an extension to Azure CLI to manage Microsoft.CleanRoom resources.

## How to use ##
Install this extension using the below CLI command
```
az extension add --name managedcleanroom
```

### Included Features
#### CleanRoom Management:
Manage CleanRoom: [more info](https://learn.microsoft.com/en-us/azure/confidential-computing/confidential-clean-rooms)\
*Examples:*

##### Create a Consortium

```
az managedcleanroom consortium create \
    --resource-group groupName \
    --consortium-name consortiumName \
    --location westus
```

## SDK Regeneration Guide ##

When regenerating `analytics_frontend_api/` SDK using autorest:

```bash
autorest --input-file=../frontend.yaml --python --output-folder=./generated-cmdlets-frontend
```

Update the following files to match SDK changes:

### 1. Map SDK Method Names
**File:** `_frontend_custom.py`
- Update `client.collaboration.<old_method>()` → `client.collaboration.<new_method>()`
- Update function parameter names to match SDK

### 2. Update Parameter Definitions
**File:** `_params.py`
- Rename argument types (e.g., `query_id_type` → `document_id_type`)
- Update `options_list` and `help` text
- Add/remove parameter contexts in `with self.argument_context()` blocks

### 3. Update Command Registration
**File:** `_frontend_commands.py`
- Update command group paths if SDK URLs changed
- Update function names in `g.custom_command()` calls

### 4. Update Help Documentation
**File:** `_help.py`
- Update parameter names in examples
- Update command paths for new/renamed commands
- Add help entries for new commands

### 5. Update Unit Tests
**Files:** `tests/latest/test_frontend_*.py`
- Update mock paths: `mock_client.collaboration.<old_method>` → `<new_method>`
- Update function parameter names in test calls
- Update function imports if renamed

### 6. Validate Changes
```bash
# Run tests
cd src/managedcleanroom
python -m pytest azext_managedcleanroom/tests/latest/ -v
```