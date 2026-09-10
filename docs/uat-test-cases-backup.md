# User Acceptance Test (UAT) Plan: `az provisionedmachine ssh-cert-create`

## Test Environment Setup

| Item | Value |
|------|-------|
| Extension | `provisionedmachine-1.0.0b3-py3-none-any.whl` |
| Key Vault | `sshCaTestVault` |
| Resource ID | `/subscriptions/ff0aa6da-20f8-44fe-9aee-381c8e8a4aeb/resourceGroups/ar-sff-rg/providers/Microsoft.AzureStackHCI/edgeMachines/aurosffaebvt14052026A` |
| Device IP | `172.18.173.125` |
| Device OS User | `edgeuser` |
| Tenant | `72f988bf-86f1-41af-91ab-2d7cd011db47` (Microsoft) |

### Pre-requisites
- Azure CLI 2.60+ installed
- Extension installed: `az extension add --source provisionedmachine-1.0.0b3-py3-none-any.whl --yes`
- Logged in: `az login --tenant 72f988bf-86f1-41af-91ab-2d7cd011db47`
- Network access to the device (for SSH tests)
- Server-side setup completed on device (CA key, principals, sshd config)

---

## Test Case 1: Extension Installation & Help

### TC-1.1: Install extension from .whl
```powershell
az extension add --source provisionedmachine-1.0.0b3-py3-none-any.whl --yes
```
**Expected:** Extension installs successfully without errors.

### TC-1.2: Verify extension listed
```powershell
az extension list --query "[?name=='provisionedmachine']" -o table
```
**Expected:** Shows `provisionedmachine` with version `1.0.0b3`.

### TC-1.3: Help text displays correctly
```powershell
az provisionedmachine -h
az provisionedmachine ssh-cert-create -h
```
**Expected:**
- Group help shows "Manage provisioned machine resources"
- Command help shows parameters `--vault-name`, `--resource-id`, `--cert-path`, `--private-key-path`
- Help text does NOT reveal implementation details (no mention of PIM, RBAC, Key Vault Sign API, RS512, role names)
- Example commands are displayed (default and custom path examples)

### TC-1.4: Uninstall and reinstall
```powershell
az extension remove --name provisionedmachine
az extension add --source provisionedmachine-1.0.0b3-py3-none-any.whl --yes
az provisionedmachine ssh-cert-create -h
```
**Expected:** Clean uninstall and reinstall works without issues.

---

## Test Case 2: Input Validation

### TC-2.1: Invalid resource ID — random string
```powershell
az provisionedmachine ssh-cert-create --vault-name sshCaTestVault --resource-id "invalid-string"
```
**Expected:** Error: `'invalid-string' is not a valid ARM resource ID.`

### TC-2.2: Invalid resource ID — missing subscriptions prefix
```powershell
az provisionedmachine ssh-cert-create --vault-name sshCaTestVault --resource-id "/resourceGroups/rg/providers/X/Y/Z"
```
**Expected:** Error about invalid ARM resource ID format.

### TC-2.3: Invalid resource ID — empty
```powershell
az provisionedmachine ssh-cert-create --vault-name sshCaTestVault --resource-id ""
```
**Expected:** Error about invalid ARM resource ID.

### TC-2.4: Invalid vault name — starts with digit
```powershell
az provisionedmachine ssh-cert-create --vault-name "1vault" --resource-id "/subscriptions/ff0aa6da-20f8-44fe-9aee-381c8e8a4aeb/resourceGroups/ar-sff-rg/providers/Microsoft.AzureStackHCI/edgeMachines/aurosffaebvt14052026A"
```
**Expected:** Error: `'1vault' is not a valid Key Vault name.`

### TC-2.5: Invalid vault name — special characters
```powershell
az provisionedmachine ssh-cert-create --vault-name "vault_name!" --resource-id "/subscriptions/ff0aa6da-20f8-44fe-9aee-381c8e8a4aeb/resourceGroups/ar-sff-rg/providers/Microsoft.AzureStackHCI/edgeMachines/aurosffaebvt14052026A"
```
**Expected:** Error about invalid Key Vault name.

### TC-2.6: Invalid vault name — too short (2 chars)
```powershell
az provisionedmachine ssh-cert-create --vault-name "ab" --resource-id "/subscriptions/ff0aa6da-20f8-44fe-9aee-381c8e8a4aeb/resourceGroups/ar-sff-rg/providers/Microsoft.AzureStackHCI/edgeMachines/aurosffaebvt14052026A"
```
**Expected:** Error about invalid Key Vault name.

### TC-2.7: Missing required parameter --vault-name
```powershell
az provisionedmachine ssh-cert-create --resource-id "/subscriptions/ff0aa6da-20f8-44fe-9aee-381c8e8a4aeb/resourceGroups/ar-sff-rg/providers/Microsoft.AzureStackHCI/edgeMachines/aurosffaebvt14052026A"
```
**Expected:** Error: `the following arguments are required: --vault-name`

### TC-2.8: Missing required parameter --resource-id
```powershell
az provisionedmachine ssh-cert-create --vault-name sshCaTestVault
```
**Expected:** Error: `the following arguments are required: --resource-id`

---

## Test Case 3: Authentication & Authorization

### TC-3.1: Not logged in
```powershell
az logout
az provisionedmachine ssh-cert-create --vault-name sshCaTestVault --resource-id "/subscriptions/ff0aa6da-20f8-44fe-9aee-381c8e8a4aeb/resourceGroups/ar-sff-rg/providers/Microsoft.AzureStackHCI/edgeMachines/aurosffaebvt14052026A"
```
**Expected:** Error about authentication / "Please run 'az login' first."

### TC-3.2: Logged in to wrong tenant
```powershell
az login --tenant <some-other-tenant>
az provisionedmachine ssh-cert-create --vault-name sshCaTestVault --resource-id "/subscriptions/ff0aa6da-20f8-44fe-9aee-381c8e8a4aeb/resourceGroups/ar-sff-rg/providers/Microsoft.AzureStackHCI/edgeMachines/aurosffaebvt14052026A"
```
**Expected:** Error about resource not found or authentication failure.

### TC-3.3: No PIM activation — only direct assignments
```powershell
# Do NOT activate PIM before running
az provisionedmachine ssh-cert-create --vault-name sshCaTestVault --resource-id "/subscriptions/ff0aa6da-20f8-44fe-9aee-381c8e8a4aeb/resourceGroups/ar-sff-rg/providers/Microsoft.AzureStackHCI/edgeMachines/aurosffaebvt14052026A"
```
**Expected:** Error: `You have a direct (permanent) role assignment... PIM-based JIT activation is required.`

### TC-3.4: PIM expired
```powershell
# Wait for PIM activation to expire, then run
az provisionedmachine ssh-cert-create --vault-name sshCaTestVault --resource-id "/subscriptions/ff0aa6da-20f8-44fe-9aee-381c8e8a4aeb/resourceGroups/ar-sff-rg/providers/Microsoft.AzureStackHCI/edgeMachines/aurosffaebvt14052026A"
```
**Expected:** Error: `Your PIM activation has expired...`

### TC-3.5: No role assignment at all on resource
```powershell
# Use a resource where the user has no RBAC assignment
az provisionedmachine ssh-cert-create --vault-name sshCaTestVault --resource-id "/subscriptions/ff0aa6da-20f8-44fe-9aee-381c8e8a4aeb/resourceGroups/ar-sff-rg/providers/Microsoft.AzureStackHCI/edgeMachines/someOtherDevice"
```
**Expected:** Error about no role assignments or resource not found.

---

## Test Case 4: Key Vault Errors

### TC-4.1: Non-existent vault
```powershell
# Activate PIM first
az provisionedmachine ssh-cert-create --vault-name "nonExistentVault123" --resource-id "/subscriptions/ff0aa6da-20f8-44fe-9aee-381c8e8a4aeb/resourceGroups/ar-sff-rg/providers/Microsoft.AzureStackHCI/edgeMachines/aurosffaebvt14052026A"
```
**Expected:** Error: `Unable to connect to Key Vault 'nonExistentVault123'.`

### TC-4.2: Vault exists but CA key missing
```powershell
# Use a vault that doesn't have the device's CA key
az provisionedmachine ssh-cert-create --vault-name remote-ssh-poc1 --resource-id "/subscriptions/ff0aa6da-20f8-44fe-9aee-381c8e8a4aeb/resourceGroups/ar-sff-rg/providers/Microsoft.AzureStackHCI/edgeMachines/aurosffaebvt14052026A"
```
**Expected:** Error: `Key 'aurosffaebvt14052026A-ssh-ca' not found in vault 'remote-ssh-poc1'.`

### TC-4.3: No Key Vault access (missing Key Get/Sign permission)
```powershell
# Use a vault where the user doesn't have Key permissions
az provisionedmachine ssh-cert-create --vault-name <vault-without-access> --resource-id "/subscriptions/ff0aa6da-20f8-44fe-9aee-381c8e8a4aeb/resourceGroups/ar-sff-rg/providers/Microsoft.AzureStackHCI/edgeMachines/aurosffaebvt14052026A"
```
**Expected:** Error: `Access denied to Key Vault... Ensure the signed-in identity has 'Key Get' permission.`

---

## Test Case 5: Happy Path — Certificate Generation

### TC-5.1: Successful certificate generation
```powershell
# 1. Activate PIM on the resource
# 2. Run ssh-cert-create
az provisionedmachine ssh-cert-create --vault-name sshCaTestVault --resource-id "/subscriptions/ff0aa6da-20f8-44fe-9aee-381c8e8a4aeb/resourceGroups/ar-sff-rg/providers/Microsoft.AzureStackHCI/edgeMachines/aurosffaebvt14052026A"
```
**Expected Output:**
```json
{
  "certificatePath": "C:\\Users\\...\\azssh_pm_xxxx\\id_rsa.pem-cert.pub",
  "privateKeyPath": "C:\\Users\\...\\azssh_pm_xxxx\\id_rsa.pem"
}
```
Plus:
```
SSH certificate created successfully.
  Private key : <path>
  Certificate : <path>
  Usage: ssh -i <key> -o CertificateFile=<cert> <username>_jit@<device-hostname>
```
And a WARNING about deleting the private key.

**Verification:**
- [ ] JSON output contains both `privateKeyPath` and `certificatePath`
- [ ] Both files exist on disk
- [ ] Private key file has restricted permissions (owner only)

### TC-5.2: Inspect generated certificate
```powershell
ssh-keygen -L -f "<certificatePath>"
```
**Expected:**
- [ ] Type: `ssh-rsa-cert-v01@openssh.com user certificate`
- [ ] Key ID: `<your-alias>` (e.g., `pusrivastava`)
- [ ] Principals: `username=<alias>` and `role=Provisioned Machine Admin`
- [ ] Valid from/to: matches PIM activation window
- [ ] Signing CA: RSA using `rsa-sha2-512`
- [ ] Critical Options: (none)
- [ ] Extensions: `permit-pty`

### TC-5.3: Multiple consecutive cert generations
```powershell
az provisionedmachine ssh-cert-create --vault-name sshCaTestVault --resource-id "..."
az provisionedmachine ssh-cert-create --vault-name sshCaTestVault --resource-id "..."
az provisionedmachine ssh-cert-create --vault-name sshCaTestVault --resource-id "..."
```
**Expected:** Each run creates a NEW temp directory with fresh keys. Previous keys remain until manually deleted.

### TC-5.4: Verify private key is RSA-4096
```powershell
ssh-keygen -l -f "<privateKeyPath>"
```
**Expected:** Shows `4096 SHA256:... (RSA)`

### TC-5.5: Certificate generation with custom output paths
```powershell
mkdir -Force $HOME\.ssh\test-output
az provisionedmachine ssh-cert-create --vault-name sshCaTestVault `
    --resource-id "/subscriptions/ff0aa6da-20f8-44fe-9aee-381c8e8a4aeb/resourceGroups/ar-sff-rg/providers/Microsoft.AzureStackHCI/edgeMachines/aurosffaebvt14052026A" `
    --private-key-path "$HOME\.ssh\test-output\my_key" `
    --cert-path "$HOME\.ssh\test-output\my_cert.pub"
```
**Expected:**
- [ ] JSON output shows the custom paths (not temp directory)
- [ ] Files exist at `$HOME\.ssh\test-output\my_key` and `$HOME\.ssh\test-output\my_cert.pub`
- [ ] Both files have restricted permissions (owner only)
- [ ] No WARNING about temp directory cleanup (since user chose the paths)

### TC-5.6: Certificate generation with only --private-key-path
```powershell
az provisionedmachine ssh-cert-create --vault-name sshCaTestVault `
    --resource-id "..." `
    --private-key-path "$HOME\.ssh\test-output\my_key2"
```
**Expected:**
- [ ] Private key saved to custom path
- [ ] Certificate saved to default temp directory
- [ ] WARNING about temp directory shown (cert still in temp)

### TC-5.7: Certificate generation with only --cert-path
```powershell
az provisionedmachine ssh-cert-create --vault-name sshCaTestVault `
    --resource-id "..." `
    --cert-path "$HOME\.ssh\test-output\my_cert2.pub"
```
**Expected:**
- [ ] Certificate saved to custom path
- [ ] Private key saved to default temp directory
- [ ] WARNING about temp directory shown (key still in temp)

### TC-5.8: Custom path with non-existent directory
```powershell
az provisionedmachine ssh-cert-create --vault-name sshCaTestVault `
    --resource-id "..." `
    --private-key-path "C:\nonexistent\folder\key"
```
**Expected:** Error: `Directory 'C:\nonexistent\folder' does not exist.`

---

## Test Case 6: SSH Connection (requires network access to device)

### TC-6.1: SSH with generated certificate
```powershell
ssh -i "<privateKeyPath>" `
    -o CertificateFile="<certificatePath>" `
    -o StrictHostKeyChecking=no `
    edgeuser@172.18.173.125
```
**Expected:** SSH session opens successfully. User gets a shell on the device.

### TC-6.2: SSH with expired certificate
```powershell
# Wait for the PIM window to expire (cert validity ends)
ssh -i "<privateKeyPath>" `
    -o CertificateFile="<certificatePath>" `
    -o StrictHostKeyChecking=no `
    edgeuser@172.18.173.125
```
**Expected:** SSH rejected by server (certificate expired).

### TC-6.3: SSH with wrong OS user
```powershell
ssh -i "<privateKeyPath>" `
    -o CertificateFile="<certificatePath>" `
    -o StrictHostKeyChecking=no `
    wronguser@172.18.173.125
```
**Expected:** SSH rejected — no matching principals for `wronguser`.

### TC-6.4: SSH without certificate (key only)
```powershell
ssh -i "<privateKeyPath>" `
    -o StrictHostKeyChecking=no `
    edgeuser@172.18.173.125
```
**Expected:** SSH rejected — key alone isn't authorized, cert is required.

---

## Test Case 7: Cleanup & Security

### TC-7.1: Verify temp directory cleanup on failure
```powershell
# Force a failure (e.g., use wrong vault so signing fails after keys are generated)
# Check that temp files are cleaned up
Get-ChildItem "$env:TEMP\azssh_pm_*"
```
**Expected:** No leftover `azssh_pm_*` directories after a failed run.

### TC-7.2: Manual cleanup after successful use
```powershell
Remove-Item -Recurse -Force "<temp-directory>"
Get-ChildItem "$env:TEMP\azssh_pm_*"
```
**Expected:** Directory removed successfully.

### TC-7.3: Private key permissions
```powershell
# On Windows, check the file isn't world-readable
icacls "<privateKeyPath>"
```
**Expected:** Only the current user has access (no Everyone/Users group).

---

## Test Case 8: Cross-Platform (if applicable)

### TC-8.1: Run on Windows
```powershell
az provisionedmachine ssh-cert-create --vault-name sshCaTestVault --resource-id "..."
```
**Expected:** Uses `ssh-keygen.exe`, generates cert successfully.

### TC-8.2: Run on Linux/macOS
```bash
az provisionedmachine ssh-cert-create --vault-name sshCaTestVault --resource-id "..."
```
**Expected:** Uses `ssh-keygen`, generates cert successfully.

### TC-8.3: ssh-keygen not installed
```powershell
# Temporarily rename/remove ssh-keygen from PATH
az provisionedmachine ssh-cert-create --vault-name sshCaTestVault --resource-id "..."
```
**Expected:** Error with platform-specific install instructions.

---

## Test Case 9: Edge Cases

### TC-9.1: Resource ID with trailing slash
```powershell
az provisionedmachine ssh-cert-create --vault-name sshCaTestVault --resource-id "/subscriptions/ff0aa6da-20f8-44fe-9aee-381c8e8a4aeb/resourceGroups/ar-sff-rg/providers/Microsoft.AzureStackHCI/edgeMachines/aurosffaebvt14052026A/"
```
**Expected:** Should fail validation (trailing slash not in regex pattern).

### TC-9.2: Vault name at boundary (3 chars)
```powershell
az provisionedmachine ssh-cert-create --vault-name "abc" --resource-id "..."
```
**Expected:** Passes vault name validation (may fail at KV lookup if vault doesn't exist).

### TC-9.3: Vault name at boundary (24 chars)
```powershell
az provisionedmachine ssh-cert-create --vault-name "abcdefghijklmnopqrstuvwx" --resource-id "..."
```
**Expected:** Passes vault name validation.

### TC-9.4: Very long PIM activation (8 hours)
```powershell
# Activate PIM for maximum 8 hours, then generate cert
ssh-keygen -L -f "<cert>"
```
**Expected:** Certificate valid-to matches PIM end time (up to 8 hours from now).

---

## Test Execution Summary

| Category | # Tests | Pass | Fail | Blocked |
|----------|---------|------|------|---------|
| 1. Installation & Help | 4 | | | |
| 2. Input Validation | 8 | | | |
| 3. Auth & Authorization | 5 | | | |
| 4. Key Vault Errors | 3 | | | |
| 5. Happy Path | 8 | | | |
| 6. SSH Connection | 4 | | | |
| 7. Cleanup & Security | 3 | | | |
| 8. Cross-Platform | 3 | | | |
| 9. Edge Cases | 4 | | | |
| **Total** | **42** | | | |

---

## Sign-Off

| Role | Name | Date | Status |
|------|------|------|--------|
| Tester | | | |
| Developer | | | |
| Reviewer | | | |
