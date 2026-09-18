# TSG: Remote SSH Certificate Creation Failures

## 1. Metadata

| Field | Value |
|-------|-------|
| **TSG_ID** | PM-SSH-CERT-001 |
| **Title** | Troubleshooting `az provisionedmachine ssh-cert-create` Failures |
| **Description** | Covers all failure modes when creating JIT SSH certificates for Azure Stack HCI Provisioned Machines, including authentication, PIM, Key Vault, and local environment issues |
| **ConfidenceScore** | 85 |
| **Applies To** | `provisionedmachine` CLI extension v1.0.0b5+ |
| **Last Updated** | 2026-07-23 |
| **Owner** | Azure Stack HCI - Provisioned Machine Team |

---

## 2. Error Codes

### Category A: Input Validation Errors

| Error Code | Error Message | Component | Trigger |
|------------|--------------|-----------|---------|
| `InvalidArgumentValueError` | `'{value}' is not a valid ARM resource ID` | `validate_resource_id()` | `--resource-id` doesn't match `/subscriptions/{guid}/resourceGroups/{rg}/providers/{provider}/{type}/{name}` |
| `InvalidArgumentValueError` | `'{value}' is not a valid Key Vault name` | `validate_vault_name()` | `--vault-name` doesn't match 3-24 chars, starts with letter, alphanumeric + hyphens |
| `InvalidArgumentValueError` | `Directory '{path}' does not exist` | `_execute_ssh_cert_create()` | `--private-key-path` or `--cert-path` parent directory doesn't exist |

### Category B: Authentication Errors

| Error Code | Error Message | Component | Trigger |
|------------|--------------|-----------|---------|
| `AuthenticationError` | `Unable to determine the signed-in user. Please run 'az login' first.` | `get_current_user_principal()` | No active `az login` session |
| `AuthenticationError` | `No signed-in user found. Please run 'az login' first.` | `get_current_user_principal()` | Login session exists but user is empty |
| `AuthenticationError` | `Failed to acquire a management token for PIM eligibility check.` | `check_pim_eligibility()` | Token acquisition for management.azure.com fails |
| `AuthenticationError` | `Failed to acquire an access token. Please run 'az login'.` | `_get_current_user_object_id()` | Token acquisition fails during OID extraction |
| `AuthenticationError` | `Failed to acquire a Key Vault access token for vault '{name}'` | `_get_kv_token()` | Token for vault.azure.net scope fails |

### Category C: PIM / Role Errors

| Error Code | Error Message | Component | Trigger |
|------------|--------------|-----------|---------|
| `AuthenticationError` | `No active PIM role assignment found for the current user on resource '{id}'` | `check_pim_eligibility()` | User has never activated a PIM role on this resource |
| `AuthenticationError` | `Your PIM activation on resource '{id}' has expired or been deactivated` | `check_pim_eligibility()` | All historical PIM activations are expired/deactivated |
| `AuthenticationError` | `Your PIM activation has expired (ended {time})` | `check_pim_eligibility()` | Computed end time is in the past |
| `AuthenticationError` | `No Provisioned Machine Reader, Contributor, or Admin role assignment found` | `resolve_user_role()` | After 3 retries (30s total), no matching role found in PIM instances |

### Category D: Key Vault Errors

| Error Code | Error Message | Component | Trigger |
|------------|--------------|-----------|---------|
| `AuthenticationError` | `Access denied to Key Vault '{name}'. Ensure the signed-in identity has 'Key Get' permission.` | `_get_ca_public_key()` | HTTP 401 from Key Vault Get Key API |
| `AuthenticationError` | `Access denied to Key Vault '{name}'. Ensure the signed-in identity has 'Key Sign' permission on the '{key}' key.` | `_kv_sign_digest()` | HTTP 401 from Key Vault Sign API |
| `ResourceNotFoundError` | `Key '{deviceId}-ssh-ca' not found in vault '{name}'.` | `_get_ca_public_key()` / `_kv_sign_digest()` | HTTP 404 — CA key doesn't exist in vault |
| `CLIInternalError` | `Unable to connect to Key Vault '{name}'.` | `_get_ca_public_key()` / `_kv_sign_digest()` | DNS resolution failure or network unreachable |
| `CLIInternalError` | `Key Vault request timed out after 30s.` | `_get_ca_public_key()` / `_kv_sign_digest()` | Network latency or vault throttling |
| `CLIInternalError` | `CA key '{key}' is not an RSA key (found: {type}).` | `_get_ca_public_key()` | CA key in vault is EC or other non-RSA type |

### Category E: Resource Errors

| Error Code | Error Message | Component | Trigger |
|------------|--------------|-----------|---------|
| `ResourceNotFoundError` | `Resource '{id}' was not found. Verify the resource ID is correct.` | `check_pim_eligibility()` | HTTP 404 from PIM API — resource doesn't exist |
| `CLIInternalError` | `PIM eligibility check failed (HTTP {code}): {body}` | `check_pim_eligibility()` | Unexpected HTTP status from PIM API |

### Category F: Local Environment Errors

| Error Code | Error Message | Component | Trigger |
|------------|--------------|-----------|---------|
| `CLIInternalError` | `ssh-keygen not found. Ensure OpenSSH is installed or provide --ssh-client-folder.` | `generate_ephemeral_keypair()` | OpenSSH not installed on the machine |
| `CLIInternalError` | `ssh-keygen timed out while generating the key pair.` | `generate_ephemeral_keypair()` | Key generation took > 30s (system resource issue) |
| `CLIInternalError` | `ssh-keygen exited with code {code}.` | `generate_ephemeral_keypair()` | ssh-keygen binary error |
| `PermissionError` | `[WinError 5] Access is denied` | Azure CLI runtime | Terminal not running as Administrator (Windows) |

### Category G: Infrastructure Setup Errors (One-Time)

| Error Code | Error Message | Component | Trigger |
|------------|--------------|-----------|---------|
| `ForbiddenError` | `Caller is not authorized to perform action 'Microsoft.KeyVault/vaults/keys/create/action'` | Key Vault / ARM | Service principal or user lacks Key Vault Crypto Officer role when creating the CA key |
| `AuthorizationFailed` | `authorization to perform Microsoft.Authorization/roleAssignments/write` | ARM RBAC | User lacks Owner/User Access Administrator to assign KV roles to others |

---

## 3. Symptoms

### Symptom Flow (Root → Visible → Downstream)

```
Root Trigger: Missing PIM activation / expired session / wrong tenant
     ↓
Visible Failure: CLI returns AuthenticationError with guidance
     ↓
Downstream Impact: User cannot SSH to device
```

### Symptom-to-Category Mapping

| Customer Symptom | Likely Category | First Check |
|-----------------|-----------------|-------------|
| "Command says I'm not logged in" | B (Auth) | `az account show` |
| "Says PIM not activated" | C (PIM/Role) | Azure Portal → PIM → My roles |
| "PIM needs approval" | C (PIM/Role) | Contact approver, then retry |
| "Key not found in vault" | D (Key Vault) | Verify CA key exists: `{deviceId}-ssh-ca` |
| "Access denied to Key Vault" | D (Key Vault) | Check KV RBAC — need Key Vault Crypto User |
| "authorization to perform roleAssignments/write" | D (Key Vault Setup) | Need Owner to grant KV Crypto Officer |
| "ssh-keygen not found" | F (Local) | Install OpenSSH |
| "Resource not found" | E (Resource) | Verify resource ID in Azure Portal |
| "Invalid resource ID" | A (Input) | Check ARM resource ID format |
| "Wrong tenant" error from Azure | B (Auth) | Login to correct tenant |
| `PermissionError: [WinError 5] Access is denied` | F (Local) | Run terminal as Administrator |
| "unable to convert private key - checksum corrupted" | D (Key Vault) | Re-create KV key version |
| Certificate generated but SSH fails | Device-side | Check `TrustedUserCAKeys` config on device |
| Device-side JIT changes cannot be applied | Device-side | Use containerized test environment |

---

## 4. Issue Validation

### Step 1: Verify Azure CLI Environment

```powershell
#StartRunCommand
# Check CLI version and extension
az --version | Select-String "azure-cli|provisionedmachine"
az extension list --query "[?name=='provisionedmachine'].{Name:name, Version:version}" -o table
#EndRunCommand
```

**Expected**: `azure-cli 2.60+` and `provisionedmachine 1.0.0b5`

### Step 2: Verify Login Context

```powershell
#StartRunCommand
# Check current tenant and user
az account show --query "{Tenant:tenantId, User:user.name, Subscription:id}" -o table
#EndRunCommand
```

**Expected**: Correct tenant ID matching the resource's subscription.

### Step 3: Verify PIM Activation Status

```powershell
#StartRunCommand
# Check active PIM role on the resource
$userOid = az ad signed-in-user show --query id -o tsv
$resourceId = "<EDGE_MACHINE_RESOURCE_ID>"
$token = az account get-access-token --resource https://management.azure.com --query accessToken -o tsv

$url = "https://management.azure.com${resourceId}/providers/Microsoft.Authorization/roleAssignmentScheduleInstances?api-version=2020-10-01&`$filter=assignedTo('${userOid}')"
$response = Invoke-RestMethod -Uri $url -Headers @{Authorization="Bearer $token"}
$response.value | ForEach-Object {
    $role = $_.properties.expandedProperties.roleDefinition.displayName
    Write-Host "Active: $role"
}
#EndRunCommand
```

**Expected**: Should list `Provisioned Machine Admin`, `Contributor`, or `Reader`.

### Step 4: Verify Key Vault Access

```powershell
#StartRunCommand
# Check if the CA key exists and you have access
$vaultName = "<VAULT_NAME>"
$deviceId = "<DEVICE_NAME>"
az keyvault key show --vault-name $vaultName --name "${deviceId}-ssh-ca" --query "{Name:key.kid, KeyType:key.kty}" -o table
#EndRunCommand
```

**Expected**: Shows the key with type `RSA` or `RSA-HSM`.

### Step 5: Verify OpenSSH is Available

```powershell
#StartRunCommand
# Check ssh-keygen is available
ssh-keygen -V 2>&1 | Select-Object -First 1
where.exe ssh-keygen
#EndRunCommand
```

**Expected**: Path to `ssh-keygen.exe` (usually `C:\Windows\System32\OpenSSH\ssh-keygen.exe`).

### Step 6: Run Command with Debug

```powershell
#StartRunCommand
az provisionedmachine ssh-cert-create `
    --vault-name <VAULT_NAME> `
    --resource-id <RESOURCE_ID> `
    --debug 2>&1 | Tee-Object -FilePath ssh-cert-debug.log
#EndRunCommand
```

---

## 5. Kusto Queries

<!-- INTERNAL_START -->

```kusto
//StartKustoQuery
//KustoDatabase: AzureStackHCITelemetry
// Find ssh-cert-create command executions and their outcomes
AzureCLITelemetry
| where TimeGenerated > ago(7d)
| where CommandName == "provisionedmachine ssh-cert-create"
| project TimeGenerated, SubscriptionId, UserId, Success, ErrorType, ErrorMessage, DurationMs
| order by TimeGenerated desc
| take 100
//EndKustoQuery
```

```kusto
//StartKustoQuery
//KustoDatabase: AzureStackHCITelemetry
// Key Vault sign operation failures for provisioned machine CA keys
AzureKeyVaultAudit
| where TimeGenerated > ago(7d)
| where OperationName == "KeySign"
| where ResourceId contains "ssh-ca"
| where ResultType != "Success"
| project TimeGenerated, VaultName, KeyName, ResultType, CallerIPAddress, Identity
| order by TimeGenerated desc
//EndKustoQuery
```

```kusto
//StartKustoQuery
//KustoDatabase: AzureStackHCITelemetry
// PIM activation failures on edge machines
AzurePIMAudit
| where TimeGenerated > ago(7d)
| where ResourceType contains "edgeMachines" or ResourceType contains "ProvisionedMachine"
| where OperationName contains "RoleAssignment"
| where Status != "Succeeded"
| project TimeGenerated, PrincipalId, RoleName, Status, FailureReason
| order by TimeGenerated desc
//EndKustoQuery
```

<!-- INTERNAL_END -->

---

## 6. Cause

The most common causes of `ssh-cert-create` failures (based on real incidents):

1. **PIM role not activated or expired** — The command requires an active (Provisioned) JIT role assignment on the specific edge machine resource. PIM activations are time-bound (max 8 hours) and must be refreshed. May also require **manager approval** before activation completes.

2. **Missing Key Vault permissions (dual-permission requirement)** — Users need BOTH:
   - Active PIM role on the Edge Machine (Provisioned Machine Admin/Contributor/Reader)
   - Key Vault signing permissions (Key Vault Crypto User) on the CA key vault
   
   These are **separate PIM activations** and both must be active simultaneously.

3. **Wrong tenant context** — The user is logged into a different Azure AD tenant than the one hosting the subscription/resource. Results in `InvalidAuthenticationTokenTenant` errors.

4. **CA key not provisioned or corrupted** — The device's CA signing key (`{deviceId}-ssh-ca`) was not created in Key Vault during device provisioning, or the key material became corrupted (checksum errors during private key conversion). Resolution: re-create the KV key.

5. **ARM propagation delay** — After PIM activation, ARM takes up to 30 seconds to propagate the role. The CLI retries 3 times with 10-second intervals, but in rare cases this may not be sufficient.

6. **Azure CLI local permission issues** — On Windows, `az login` or extension operations may fail with `PermissionError: [WinError 5] Access is denied` if the terminal is not elevated. Run as Administrator.

7. **Device-side JIT SSH configuration not ready** — The edge device's sshd must be configured with `TrustedUserCAKeys` pointing to the CA public key. If device-side changes haven't been applied, certificate generation succeeds but SSH login fails.

8. **Key Vault RBAC role assignment blocked** — Setting up the CA vault requires Owner access to assign `Key Vault Crypto Officer`. Without it, you get `authorization to perform Microsoft.Authorization/roleAssignments/write` errors.

9. **Organizational security policies blocking key access** — Corporate DLP or conditional access policies may prevent users from downloading/opening the CA public key file. Workaround: have another authorized user share the key directly.

---

## 7. Preconditions

### One-Time Infrastructure Setup (Admin / IT Ops)

Before any user can run `ssh-cert-create`, the following infrastructure must be provisioned:

```powershell
#StartRunCommand
# === Step 1: Create the Key Vault (if not exists) ===
az keyvault create \
    --name <VAULT_NAME> \
    --resource-group <RG_NAME> \
    --location <LOCATION> \
    --enable-rbac-authorization true

# === Step 2: Create the CA signing key (RSA, non-exportable) ===
# Key name convention: {deviceId}-ssh-ca
az keyvault key create \
    --vault-name <VAULT_NAME> \
    --name "<DEVICE_ID>-ssh-ca" \
    --kty RSA \
    --size 4096 \
    --ops sign verify \
    --protection software
# NOTE: Use --protection hsm for HSM-backed keys (higher security)

# === Step 3: Export the CA public key for device deployment ===
az keyvault key download \
    --vault-name <VAULT_NAME> \
    --name "<DEVICE_ID>-ssh-ca" \
    --file ca_pub.pem \
    --encoding PEM

# === Step 4: Deploy CA public key to the device ===
# Copy ca_pub.pem content to device: /etc/ssh/trusted_ca_keys
# Add to /etc/ssh/sshd_config:
#   TrustedUserCAKeys /etc/ssh/trusted_ca_keys
# Restart sshd: sudo systemctl restart sshd
#EndRunCommand
```

### Required RBAC Role Assignments (Admin)

| Who | Role | Scope | Purpose |
|-----|------|-------|---------|
| **Setup Admin** | Key Vault Crypto Officer | Key Vault resource | Create/manage CA keys (`keys/create`, `keys/read`, `keys/sign`) |
| **Setup Admin** | Owner (or User Access Administrator) | Key Vault resource | Assign RBAC roles to other users |
| **SSH Users** | Key Vault Crypto User (PIM-eligible) | Key Vault resource | Sign certificates at runtime (`keys/read`, `keys/sign`) |
| **SSH Users** | Provisioned Machine Admin / Contributor / Reader (PIM-eligible) | Edge Machine resource | Determines SSH role principal in certificate |

```powershell
#StartRunCommand
# === Assign Key Vault Crypto Officer to setup admin ===
az role assignment create \
    --assignee "<ADMIN_OBJECT_ID>" \
    --role "Key Vault Crypto Officer" \
    --scope "/subscriptions/<SUB>/resourceGroups/<RG>/providers/Microsoft.KeyVault/vaults/<VAULT>"

# === Assign Key Vault Crypto User (PIM-eligible) to SSH users ===
# This is done via Azure Portal → PIM → Azure resources → Assign eligibility
# Or via PIM API:
# POST roleEligibilityScheduleRequests with:
#   roleDefinitionId = Key Vault Crypto User
#   scope = Key Vault resource ID
#   principalId = user object ID

# === Assign Provisioned Machine Admin (PIM-eligible) to SSH users ===
# Same process via PIM for the edge machine resource scope
#EndRunCommand
```

### Per-Session Checklist (SSH User)

Before running `ssh-cert-create`, ensure:

- [ ] **Azure CLI 2.60+** installed (`az --version`)
- [ ] **provisionedmachine extension** installed (`az extension list`)
- [ ] **OpenSSH** installed on the machine (`ssh-keygen` available in PATH)
- [ ] **Terminal running as Administrator** (Windows — avoids WinError 5)
- [ ] **Correct tenant login** — `az login --tenant <TENANT_ID>`
- [ ] **Correct subscription** — `az account set --subscription <SUB_ID>`
- [ ] **PIM role activated on Edge Machine** — Provisioned Machine Admin/Contributor/Reader
- [ ] **PIM role activated on Key Vault** — Key Vault Crypto User
- [ ] **PIM approval obtained** (if approval workflow is configured)
- [ ] **Wait 60s** after PIM activation for ARM propagation

### Important Security Design Notes

<!-- INTERNAL_START -->
- **Role is auto-derived** — The SSH role principal is automatically resolved from PIM/RBAC assignments. Users cannot supply `--role` as CLI input to prevent privilege manipulation.
- **CLI performs KV signing** — The Azure CLI performs Key Vault signing in the user's own context (not via RP/service). This prevents the RP from becoming a security failure point with access to customer Key Vaults.
- **CA private key is non-exportable** — Only the Key Vault Sign API is used. The private key never leaves Key Vault.
- **Certificate validity is bounded** — Max 8 hours, enforced at the device level regardless of what the cert claims.
<!-- INTERNAL_END -->

---

## 8. Mitigation

### Scenario A: "No active PIM role assignment" / "PIM activation expired"

```powershell
#StartRunCommand
# Step 1: Activate PIM role on the edge machine
# Go to: Azure Portal → Privileged Identity Management → My roles → Azure resources
# Find "Provisioned Machine Admin" on the target resource → Click "Activate"
# Provide justification, select duration (up to 8h), confirm

# Step 2: Verify activation propagated (wait ~60 seconds)
$userOid = az ad signed-in-user show --query id -o tsv
$resourceId = "<EDGE_MACHINE_RESOURCE_ID>"
$token = az account get-access-token --resource https://management.azure.com --query accessToken -o tsv
Invoke-RestMethod -Uri "https://management.azure.com${resourceId}/providers/Microsoft.Authorization/roleAssignmentScheduleInstances?api-version=2020-10-01&`$filter=assignedTo('${userOid}')" -Headers @{Authorization="Bearer $token"} | Select-Object -ExpandProperty value | ForEach-Object { Write-Host $_.properties.expandedProperties.roleDefinition.displayName }

# Step 3: Retry the command
az provisionedmachine ssh-cert-create --vault-name <VAULT> --resource-id <RESOURCE_ID>
#EndRunCommand
```

**Verification**: Command returns JSON with `privateKeyPath` and `certificatePath`.

---

### Scenario B: "Access denied to Key Vault" / "Key Vault Crypto User"

```powershell
#StartRunCommand
# Step 1: Activate Key Vault Crypto User PIM role
# Go to: Azure Portal → PIM → My roles → Azure resources
# Find "Key Vault Crypto User" on the Key Vault resource → Activate

# Step 2: Verify KV access (wait ~60 seconds)
$vaultName = "<VAULT_NAME>"
$deviceId = "<DEVICE_NAME>"
az keyvault key show --vault-name $vaultName --name "${deviceId}-ssh-ca" -o table

# Step 3: Retry
az provisionedmachine ssh-cert-create --vault-name $vaultName --resource-id <RESOURCE_ID>
#EndRunCommand
```

**Verification**: `az keyvault key show` returns the key metadata without 403.

---

### Scenario C: "Key not found in vault" (404)

```powershell
#StartRunCommand
# Step 1: List all keys in the vault to find the correct CA key
az keyvault key list --vault-name <VAULT_NAME> --query "[?contains(kid, 'ssh-ca')].{Name:kid}" -o table

# Step 2: Verify the device ID matches
# The key name must be: {deviceId}-ssh-ca
# where deviceId = last segment of the resource ID
# E.g. resource ID ends with .../edgeMachines/myDevice → key = "myDevice-ssh-ca"

# Step 3: If key doesn't exist, the device was not properly provisioned
# Contact the infrastructure team to re-run device provisioning
#EndRunCommand
```

**Verification**: Key list shows `{deviceId}-ssh-ca` for your target device.

---

### Scenario D: "InvalidAuthenticationTokenTenant" (Wrong Tenant)

```powershell
#StartRunCommand
# Step 1: Check current tenant
az account show --query tenantId -o tsv

# Step 2: Login to the correct tenant
az login --tenant <CORRECT_TENANT_ID>
az account set --subscription <SUBSCRIPTION_ID>

# Step 3: Verify
az account show --query "{Tenant:tenantId, Sub:id}" -o table

# Step 4: Retry
az provisionedmachine ssh-cert-create --vault-name <VAULT> --resource-id <RESOURCE_ID>
#EndRunCommand
```

---

### Scenario E: "ssh-keygen not found"

```powershell
#StartRunCommand
# Windows: Install OpenSSH Client
Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0

# Verify
ssh-keygen -V

# macOS:
# brew install openssh

# Linux (Ubuntu/Debian):
# sudo apt-get install openssh-client

# Retry
az provisionedmachine ssh-cert-create --vault-name <VAULT> --resource-id <RESOURCE_ID>
#EndRunCommand
```

---

### Scenario F: Certificate Generated but SSH Login Fails

```powershell
#StartRunCommand
# Step 1: Inspect the certificate
ssh-keygen -L -f <CERTIFICATE_PATH>
# Verify:
#   - Type: ssh-rsa-cert-v01@openssh.com user certificate
#   - Signing CA: rsa-sha2-512
#   - Principals: username=<alias>, role=provisionedmachineadmin
#   - Valid: not expired

# Step 2: Test SSH connection with verbose output
ssh -vvv -i <PRIVATE_KEY_PATH> -o CertificateFile=<CERT_PATH> <username>_jit@<device-ip>

# Step 3: Common device-side issues:
#   - TrustedUserCAKeys not configured in /etc/ssh/sshd_config
#   - CA public key not deployed to /etc/ssh/trusted_ca_keys
#   - AuthorizedPrincipalsFile not configured for principal matching
#   - Certificate expired (check Valid: field)
#   - Wrong username format (must be <alias>_jit)
#EndRunCommand
```

---

### Scenario G: "No Provisioned Machine Reader, Contributor, or Admin role" after PIM activation

```powershell
#StartRunCommand
# This occurs due to ARM eventual consistency (propagation delay)
# The CLI already retries 3x with 10s intervals (30s total)

# Step 1: Wait 60 seconds after PIM activation
Start-Sleep -Seconds 60

# Step 2: Manually verify the role is visible
$userOid = az ad signed-in-user show --query id -o tsv
$resourceId = "<EDGE_MACHINE_RESOURCE_ID>"
$token = az account get-access-token --resource https://management.azure.com --query accessToken -o tsv
$url = "https://management.azure.com${resourceId}/providers/Microsoft.Authorization/roleAssignmentScheduleInstances?api-version=2020-10-01&`$filter=assignedTo('${userOid}')"
(Invoke-RestMethod -Uri $url -Headers @{Authorization="Bearer $token"}).value | ForEach-Object {
    Write-Host "$($_.properties.expandedProperties.roleDefinition.displayName) - Status: Active"
}

# Step 3: If role shows, retry the command
az provisionedmachine ssh-cert-create --vault-name <VAULT> --resource-id <RESOURCE_ID>

# Step 4: If role doesn't show after 2 minutes, verify:
#   - The PIM activation scope matches the exact resource (not parent RG)
#   - The role name is one of: Provisioned Machine Admin/Contributor/Reader
#   - There's no PendingApproval state (may need manager approval)
#EndRunCommand
```

---

### Scenario H: `PermissionError: [WinError 5] Access is denied` during `az login`

```powershell
#StartRunCommand
# This occurs when the Azure CLI extensions directory has restricted permissions.
# The terminal must be run as Administrator.

# Step 1: Close current terminal
# Step 2: Right-click PowerShell / Windows Terminal → "Run as administrator"
# Step 3: Retry
az login --tenant <TENANT_ID>
az provisionedmachine ssh-cert-create --vault-name <VAULT> --resource-id <RESOURCE_ID>
#EndRunCommand
```

**Verification**: `az login` completes without permission errors.

---

### Scenario I: "authorization to perform roleAssignments/write" (Key Vault Setup)

```powershell
#StartRunCommand
# This occurs during initial Key Vault setup when assigning Crypto Officer role.
# You need Owner access on the Key Vault resource to assign RBAC roles.

# Step 1: Ask a subscription Owner or Key Vault Owner to assign the role:
az role assignment create \
    --assignee <USER_OBJECT_ID> \
    --role "Key Vault Crypto Officer" \
    --scope /subscriptions/<SUB>/resourceGroups/<RG>/providers/Microsoft.KeyVault/vaults/<VAULT>

# Step 2: Alternatively, ask the Owner to grant you Owner on the KV resource
# Step 3: Once assigned, you can manage keys and sign operations
#EndRunCommand
```

**Verification**: `az keyvault key list --vault-name <VAULT>` succeeds.

---

### Scenario J: "Unable to convert private key - checksum corrupted"

```powershell
#StartRunCommand
# This occurs when the Key Vault CA key material becomes corrupted.
# Resolution: Generate a fresh key version in Key Vault.

# Step 1: Check current key versions
$vaultName = "<VAULT_NAME>"
$keyName = "<DEVICE_ID>-ssh-ca"
az keyvault key list-versions --vault-name $vaultName --name $keyName -o table

# Step 2: Create a new key version (this does NOT delete old versions)
az keyvault key create --vault-name $vaultName --name $keyName --kty RSA --size 4096 --ops sign verify

# Step 3: Export the NEW CA public key and redeploy to the device
az keyvault key download --vault-name $vaultName --name $keyName --file ca_pub.pem --encoding PEM
# Copy ca_pub.pem content to device's /etc/ssh/trusted_ca_keys

# Step 4: Restart sshd on the device to pick up the new CA key
# ssh admin@device "sudo systemctl restart sshd"

# Step 5: Retry certificate creation
az provisionedmachine ssh-cert-create --vault-name $vaultName --resource-id <RESOURCE_ID>
#EndRunCommand
```

**Verification**: Certificate generation succeeds and SSH login works with the new key version.

---

### Scenario K: Device-Side JIT SSH Configuration Issues

```powershell
#StartRunCommand
# Certificate generates successfully but SSH login fails.
# The device sshd must be configured to trust the CA and match principals.

# Step 1: Verify device sshd_config has these settings:
#   TrustedUserCAKeys /etc/ssh/trusted_ca_keys
#   AuthorizedPrincipalsCommand /usr/local/bin/validate-ssh-principals %u %k %t
#   (or AuthorizedPrincipalsFile with appropriate principal matching)

# Step 2: Verify CA public key is deployed
# ssh admin@device "cat /etc/ssh/trusted_ca_keys"
# Should show the RSA public key matching the Key Vault CA key

# Step 3: If device-side changes cannot be applied to existing setup:
#   - Use the containerized test environment (Docker image with pre-configured sshd)
#   - Contact the device team for assistance

# Step 4: Verify principal matching
ssh-keygen -L -f <CERT_PATH>
# Principals should show:
#   username=<alias>
#   role=provisionedmachineadmin (or contributor/reader)
# Login user must be: <alias>_jit

# Step 5: Test with verbose SSH
ssh -vvv -i <KEY_PATH> -o CertificateFile=<CERT_PATH> <alias>_jit@<device-ip> -p <port>
# Look for: "Server accepts key: ... ssh-rsa-cert-v01@openssh.com"
# If not seen: CA key mismatch or sshd config issue
#EndRunCommand
```

---

### Scenario L: PIM Activation Requires Approval

```powershell
#StartRunCommand
# PIM returns "PendingApproval" status instead of "Provisioned"

# Step 1: Check activation status
$userOid = az ad signed-in-user show --query id -o tsv
$resourceId = "<EDGE_MACHINE_RESOURCE_ID>"
$token = az account get-access-token --resource https://management.azure.com --query accessToken -o tsv
$url = "https://management.azure.com${resourceId}/providers/Microsoft.Authorization/roleAssignmentScheduleRequests?api-version=2020-10-01"
$requests = (Invoke-RestMethod -Uri $url -Headers @{Authorization="Bearer $token"}).value
$requests | Where-Object { $_.properties.principalId -eq $userOid } | ForEach-Object {
    Write-Host "Status: $($_.properties.status) | Role: $($_.properties.expandedProperties.roleDefinition.displayName)"
}

# Step 2: If status is "PendingApproval":
#   - Contact your approver (manager or designated approver)
#   - They approve via: Azure Portal → PIM → Approve requests
#   - Wait for status to change to "Provisioned"

# Step 3: After approval, wait 60 seconds and retry
az provisionedmachine ssh-cert-create --vault-name <VAULT> --resource-id <RESOURCE_ID>
#EndRunCommand
```

---

## Quick Reference Card

| Problem | Fix |
|---------|-----|
| Not logged in | `az login --tenant <TENANT>` |
| Wrong tenant | `az login --tenant <CORRECT_TENANT>` |
| PIM expired | Reactivate in Azure Portal → PIM → My roles |
| PIM needs approval | Contact approver, wait for "Provisioned" status |
| KV access denied | Activate "Key Vault Crypto User" PIM role on the vault |
| Can't assign KV roles | Need Owner to grant you the role |
| Key not found | Verify device CA key exists: `{deviceId}-ssh-ca` |
| Key checksum corrupted | `az keyvault key create` to generate new version, redeploy CA public key |
| ssh-keygen missing | Install OpenSSH (`Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0`) |
| WinError 5 - Access denied | Run terminal as Administrator |
| ARM propagation | Wait 60s after PIM activation, then retry |
| SSH login fails | `ssh-keygen -L -f <cert>` to inspect; check device sshd config |
| Device-side not configured | Verify `TrustedUserCAKeys` in sshd_config; use container test env |
