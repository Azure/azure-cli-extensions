# Neon CLI Extension Test Suite

## Overview
This directory contains comprehensive tests for the Azure CLI Neon extension, covering all 25 commands including the fixed parameter mapping for endpoint, role, and database create commands.

## Test Structure

### Test Files
- `test_neon.py` - Main test suite with comprehensive scenarios
- `test_config.py` - Test configuration and constants
- `test_requirements.txt` - Additional test dependencies
- `recordings/` - Test recordings for playback

### Test Categories

#### 1. Organization Lifecycle Tests (`test_neon_organization_lifecycle`)
- Organization creation with marketplace integration
- Organization listing and details retrieval
- Organization updates
- Organization deletion
- SSO configuration testing

#### 2. Complete Workflow Tests (`test_neon_complete_workflow`)
- End-to-end testing of all resource types
- Organization → Project → Branch → Endpoint/Database/Role creation
- Resource dependency validation
- Complete cleanup workflow

#### 3. Parameter Mapping Tests (`test_neon_fixed_parameter_mapping`)
- **Critical**: Tests the fixed parameter mapping for create commands
- Validates that endpoint, role, and database create commands no longer fail with "branch not found"
- Tests proper URL parameter mapping using project-id and branch-id

#### 4. Help Command Tests (`test_neon_help_commands`)
- Validates all help commands work correctly
- Tests command discovery and documentation

#### 5. Command Validation Tests (`test_neon_command_validation`)
- Tests required parameter enforcement
- Validates command syntax

## Running Tests

### Prerequisites
```bash
# Install the extension
az extension add --source /path/to/neon-1.0.0-py3-none-any.whl

# Install test dependencies
pip install -r azext_neon/tests/test_requirements.txt
```

### Run All Tests
```bash
cd /workspaces/azure-cli-extensions/src/neon
python -m pytest azext_neon/tests/latest/test_neon.py -v
```

### Run Specific Test Categories
```bash
# Test help commands (quick)
python -m pytest azext_neon/tests/latest/test_neon.py::NeonScenario::test_neon_help_commands -v

# Test command validation (quick)
python -m pytest azext_neon/tests/latest/test_neon.py::NeonScenario::test_neon_command_validation -v

# Test parameter mapping fixes (quick)
python -m pytest azext_neon/tests/latest/test_neon.py::NeonScenario::test_neon_fixed_parameter_mapping -v

# Test organization lifecycle (requires Azure resources)
python -m pytest azext_neon/tests/latest/test_neon.py::NeonScenario::test_neon_organization_lifecycle -v

# Test complete workflow (requires Azure resources, long-running)
python -m pytest azext_neon/tests/latest/test_neon.py::NeonScenario::test_neon_complete_workflow -v
```

### Run Tests with Coverage
```bash
python -m pytest azext_neon/tests/latest/test_neon.py --cov=azext_neon --cov-report=html
```

## Test Environment Setup

### Azure Authentication
```bash
az login
az account set --subscription "your-subscription-id"
```

### Resource Group
Tests use `ResourceGroupPreparer` which automatically creates and cleans up resource groups. The tests are designed to be isolated and not interfere with existing resources.

## Test Results Interpretation

### Expected Behaviors

#### ✅ Should Pass
- Help command tests
- Command validation tests
- Parameter mapping tests (even with API errors)

#### ⚠️ May Fail Due to Service Limits
- Endpoint creation (due to endpoint limits)
- Complex resource creation (due to marketplace integration requirements)

#### 🔍 What to Look For
- **Parameter Mapping Fixes**: Tests should fail with proper API errors (like "ParentResourceNotFound") instead of parameter mapping errors (like "branch not found")
- **Command Discovery**: All commands should be discoverable via help
- **Required Parameters**: Commands should properly validate required parameters

## Test Data

### Generated Test Data
Tests use randomized names to avoid conflicts:
- Organizations: `test-neon-org-{random}`
- Projects: `test-project-{random}`
- Branches: `test-branch-{random}`
- Endpoints: `test-endpoint-{random}`
- Databases: `test_db_{random}`
- Roles: `test_role_{random}`

### Test Constants
See `test_config.py` for configurable test constants including:
- Default locations and regions
- PostgreSQL versions
- Marketplace integration details
- Timeout settings

## Troubleshooting

### Common Issues

#### 1. Authentication Errors
```bash
# Ensure you're logged in
az login
az account show
```

#### 2. Resource Quota Limits
Some tests may fail due to subscription limits. This is expected behavior for:
- Endpoint creation (limited endpoints per branch)
- Complex marketplace integrations

#### 3. Test Isolation
Each test uses unique resource names and resource groups to avoid conflicts.

#### 4. Long-Running Tests
Complete workflow tests may take several minutes due to resource provisioning time.

### Debug Mode
```bash
# Run with debug output
python -m pytest azext_neon/tests/latest/test_neon.py -v -s --tb=short

# Run with Azure CLI debug
export AZURE_CLI_DEBUG=1
python -m pytest azext_neon/tests/latest/test_neon.py -v
```

## Test Coverage

### Commands Covered (25 total)

#### Organization Commands (6)
- create, list, show, update, delete, wait

#### Project Commands (7)  
- create, list, show, update, delete, get-connection-uri, wait

#### Branch Commands (6)
- create, list, show, update, delete, wait

#### Endpoint Commands (3) ✅ Fixed
- create, list, delete

#### Database Commands (3) ✅ Fixed
- create, list, delete

#### Role Commands (3) ✅ Fixed
- create, list, delete

#### Utility Commands (2)
- get-postgres-version, postgres create

### Key Test Validations

1. **Parameter Mapping Fixes** ✅
   - Endpoint create uses proper project-id/branch-id mapping
   - Role create uses proper project-id/branch-id mapping  
   - Database create uses proper project-id/branch-id mapping

2. **Command Registration** ✅
   - All 25 commands are discoverable
   - Help system works for all commands

3. **Parameter Validation** ✅
   - Required parameters are enforced
   - Optional parameters work correctly

4. **Error Handling** ✅
   - Proper API errors instead of parameter mapping errors
   - Graceful handling of service limits

5. **Resource Lifecycle** ✅
   - Create → List → Delete workflows
   - Resource dependency management

## Continuous Integration

### Recommended CI Pipeline
```yaml
# Example GitHub Actions workflow
- name: Install Extension
  run: az extension add --source dist/neon-1.0.0-py3-none-any.whl

- name: Run Quick Tests
  run: |
    python -m pytest azext_neon/tests/latest/test_neon.py::NeonScenario::test_neon_help_commands -v
    python -m pytest azext_neon/tests/latest/test_neon.py::NeonScenario::test_neon_command_validation -v
    python -m pytest azext_neon/tests/latest/test_neon.py::NeonScenario::test_neon_fixed_parameter_mapping -v

- name: Run Full Tests (Optional)
  run: python -m pytest azext_neon/tests/latest/test_neon.py -v
  continue-on-error: true  # Due to potential service limits
```

The test suite provides comprehensive coverage of all Neon CLI functionality with special focus on validating the parameter mapping fixes that resolved the "branch not found" issues in create commands.
