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

### Abbreviations used in commands
- `<RID>` = `/subscriptions/ff0aa6da-20f8-44fe-9aee-381c8e8a4aeb/resourceGroups/ar-sff-rg/providers/Microsoft.AzureStackHCI/edgeMachines/aurosffaebvt14052026A`
- `<VN>` = `sshCaTestVault`

---

## 1. Extension Installation & Help

| S.No | Test Case | Desc | Command | Expected Result | Actual Result | Status |
|------|-----------|------|---------|-----------------|---------------|--------|
| 1.1 | Install extension | Install from .whl file | `az extension add --source provisionedmachine-1.0.0b3-py3-none-any.whl --yes` | Extension installs successfully without errors | | |
| 1.2 | Verify extension listed | Confirm extension appears in list | `az extension list --query "[?name=='provisionedmachine']" -o table` | Shows `provisionedmachine` with version `1.0.0b3` | | |
| 1.3 | Help text — group | Verify group help displays correctly | `az provisionedmachine -h` | Shows "Manage provisioned machine resources". No implementation details (no PIM, RBAC, KV Sign API, RS512, role names) | | |
| 1.4 | Help text — command | Verify command help displays correctly | `az provisionedmachine ssh-cert-create -h` | Shows params: `--vault-name`, `--resource-id`, `--cert-path`, `--private-key-path`. Shows examples for default and custom paths | | |
| 1.5 | Uninstall and reinstall | Clean uninstall/reinstall cycle | `az extension remove --name provisionedmachine` then `az extension add --source ...whl --yes` then `az provisionedmachine ssh-cert-create -h` | All three commands succeed without errors | | |

---

## 2. Input Validation

| S.No | Test Case | Desc | Command | Expected Result | Actual Result | Status |
|------|-----------|------|---------|-----------------|---------------|--------|
| 2.1 | Invalid resource ID — random string | Reject non-ARM format | `az provisionedmachine ssh-cert-create --vault-name <VN> --resource-id "invalid-string"` | Error: `'invalid-string' is not a valid ARM resource ID.` | | |
| 2.2 | Invalid resource ID — missing /subscriptions | Reject incomplete ARM path | `az provisionedmachine ssh-cert-create --vault-name <VN> --resource-id "/resourceGroups/rg/providers/X/Y/Z"` | Error about invalid ARM resource ID format | | |
| 2.3 | Invalid resource ID — empty | Reject empty string | `az provisionedmachine ssh-cert-create --vault-name <VN> --resource-id ""` | Error about invalid ARM resource ID | | |
| 2.4 | Invalid vault name — starts with digit | Reject vault name starting with number | `az provisionedmachine ssh-cert-create --vault-name "1vault" --resource-id <RID>` | Error: `'1vault' is not a valid Key Vault name.` | | |
| 2.5 | Invalid vault name — special chars | Reject underscores/symbols | `az provisionedmachine ssh-cert-create --vault-name "vault_name!" --resource-id <RID>` | Error about invalid Key Vault name | | |
| 2.6 | Invalid vault name — too short | Reject 2-char name | `az provisionedmachine ssh-cert-create --vault-name "ab" --resource-id <RID>` | Error about invalid Key Vault name | | |
| 2.7 | Missing --vault-name | Required param not provided | `az provisionedmachine ssh-cert-create --resource-id <RID>` | Error: `the following arguments are required: --vault-name` | | |
| 2.8 | Missing --resource-id | Required param not provided | `az provisionedmachine ssh-cert-create --vault-name <VN>` | Error: `the following arguments are required: --resource-id` | | |

---

## 3. Authentication & Authorization

| S.No | Test Case | Desc | Command | Expected Result | Actual Result | Status |
|------|-----------|------|---------|-----------------|---------------|--------|
| 3.1 | Not logged in | Run without az login | `az logout` then `az provisionedmachine ssh-cert-create --vault-name <VN> --resource-id <RID>` | Error: "Please run 'az login' first." | | |
| 3.2 | Wrong tenant | Login to a different tenant | `az login --tenant <other-tenant>` then `az provisionedmachine ssh-cert-create --vault-name <VN> --resource-id <RID>` | Error about resource not found or authentication failure | | |
| 3.3 | No PIM activation — direct only | Direct role exists but PIM not activated | `az provisionedmachine ssh-cert-create --vault-name <VN> --resource-id <RID>` (without PIM activation) | Error: `You have a direct (permanent) role assignment... PIM-based JIT activation is required.` | | |
| 3.4 | PIM expired | Run after PIM window has ended | `az provisionedmachine ssh-cert-create --vault-name <VN> --resource-id <RID>` (after PIM expires) | Error: `Your PIM activation has expired...` | | |
| 3.5 | No role assignment at all | Use resource with no RBAC for user | `az provisionedmachine ssh-cert-create --vault-name <VN> --resource-id ".../edgeMachines/someOtherDevice"` | Error about no role assignments or resource not found | | |

---

## 4. Key Vault Errors

| S.No | Test Case | Desc | Command | Expected Result | Actual Result | Status |
|------|-----------|------|---------|-----------------|---------------|--------|
| 4.1 | Non-existent vault | Vault DNS doesn't resolve | `az provisionedmachine ssh-cert-create --vault-name "nonExistentVault123" --resource-id <RID>` (PIM activated) | Error: `Unable to connect to Key Vault 'nonExistentVault123'.` | | |
| 4.2 | Vault exists but CA key missing | No `<deviceId>-ssh-ca` key in vault | `az provisionedmachine ssh-cert-create --vault-name remote-ssh-poc1 --resource-id <RID>` (PIM activated) | Error: `Key 'aurosffaebvt14052026A-ssh-ca' not found in vault 'remote-ssh-poc1'.` | | |
| 4.3 | No KV access permissions | User lacks Key Get/Sign permission | `az provisionedmachine ssh-cert-create --vault-name <vault-without-access> --resource-id <RID>` (PIM activated) | Error: `Access denied to Key Vault... Ensure the signed-in identity has 'Key Get' permission.` | | |

---

## 5. Happy Path — Certificate Generation

| S.No | Test Case | Desc | Command | Expected Result | Actual Result | Status |
|------|-----------|------|---------|-----------------|---------------|--------|
| 5.1 | Successful cert generation (default paths) | Full happy path with default temp output | `az provisionedmachine ssh-cert-create --vault-name <VN> --resource-id <RID>` (PIM activated) | JSON with `privateKeyPath` and `certificatePath`. Success message with SSH usage hint. WARNING about deleting private key. Both files exist on disk with restricted permissions. | | |
| 5.2 | Inspect generated certificate | Verify cert contents via ssh-keygen | `ssh-keygen -L -f "<certificatePath>"` | Type: `ssh-rsa-cert-v01@openssh.com user certificate`. Key ID: `<alias>`. Principals: `username=<alias>`, `role=Provisioned Machine Admin`. Valid window matches PIM. Signing CA: `rsa-sha2-512`. Critical Options: (none). Extensions: `permit-pty`. | | |
| 5.3 | Multiple consecutive generations | Each run creates fresh keys in new dir | Run `az provisionedmachine ssh-cert-create ...` three times consecutively | Each run creates a NEW temp directory with fresh keys. Previous keys remain until manually deleted. | | |
| 5.4 | Verify private key is RSA-4096 | Confirm key strength | `ssh-keygen -l -f "<privateKeyPath>"` | Shows `4096 SHA256:... (RSA)` | | |
| 5.5 | Custom output paths (both) | Both --cert-path and --private-key-path | `az provisionedmachine ssh-cert-create --vault-name <VN> --resource-id <RID> --private-key-path "$HOME\.ssh\test\my_key" --cert-path "$HOME\.ssh\test\my_cert.pub"` | JSON shows custom paths. Files exist at specified locations with restricted permissions. No WARNING about temp cleanup. | | |
| 5.6 | Custom --private-key-path only | Only key path customized | `az provisionedmachine ssh-cert-create --vault-name <VN> --resource-id <RID> --private-key-path "$HOME\.ssh\test\my_key2"` | Private key at custom path. Cert in temp directory. WARNING about temp directory shown. | | |
| 5.7 | Custom --cert-path only | Only cert path customized | `az provisionedmachine ssh-cert-create --vault-name <VN> --resource-id <RID> --cert-path "$HOME\.ssh\test\my_cert2.pub"` | Cert at custom path. Private key in temp directory. WARNING about temp directory shown. | | |
| 5.8 | Custom path — non-existent directory | Directory doesn't exist | `az provisionedmachine ssh-cert-create --vault-name <VN> --resource-id <RID> --private-key-path "C:\nonexistent\folder\key"` | Error: `Directory 'C:\nonexistent\folder' does not exist.` | | |

---

## 6. SSH Connection (requires network access to device)

| S.No | Test Case | Desc | Command | Expected Result | Actual Result | Status |
|------|-----------|------|---------|-----------------|---------------|--------|
| 6.1 | SSH with generated certificate | Full SSH login using cert | `ssh -i "<privateKeyPath>" -o CertificateFile="<certificatePath>" -o StrictHostKeyChecking=no edgeuser@172.18.173.125` | SSH session opens successfully. User gets a shell on the device. | | |
| 6.2 | SSH with expired certificate | Cert validity has ended | `ssh -i "<privateKeyPath>" -o CertificateFile="<certificatePath>" -o StrictHostKeyChecking=no edgeuser@172.18.173.125` (after PIM window expires) | SSH rejected by server (certificate expired) | | |
| 6.3 | SSH with wrong OS user | Login as non-existent user | `ssh -i "<privateKeyPath>" -o CertificateFile="<certificatePath>" -o StrictHostKeyChecking=no wronguser@172.18.173.125` | SSH rejected — no matching principals for `wronguser` | | |
| 6.4 | SSH without certificate | Key only, no cert | `ssh -i "<privateKeyPath>" -o StrictHostKeyChecking=no edgeuser@172.18.173.125` | SSH rejected — key alone isn't authorized, cert required | | |

---

## 7. Cleanup & Security

| S.No | Test Case | Desc | Command | Expected Result | Actual Result | Status |
|------|-----------|------|---------|-----------------|---------------|--------|
| 7.1 | Temp cleanup on failure | Verify ephemeral files removed after error | Force a failure (e.g., wrong vault after PIM check) then `Get-ChildItem "$env:TEMP\azssh_pm_*"` | No leftover `azssh_pm_*` directories after a failed run | | |
| 7.2 | Manual cleanup after success | Delete temp directory manually | `Remove-Item -Recurse -Force "<temp-directory>"` then `Get-ChildItem "$env:TEMP\azssh_pm_*"` | Directory removed successfully | | |
| 7.3 | Private key permissions | Verify file isn't world-readable | `icacls "<privateKeyPath>"` | Only the current user has access (no Everyone/Users group) | | |

---

## 8. Cross-Platform

| S.No | Test Case | Desc | Command | Expected Result | Actual Result | Status |
|------|-----------|------|---------|-----------------|---------------|--------|
| 8.1 | Run on Windows | Windows platform test | `az provisionedmachine ssh-cert-create --vault-name <VN> --resource-id <RID>` | Uses `ssh-keygen.exe`, generates cert successfully | | |
| 8.2 | Run on Linux/macOS | Unix platform test | `az provisionedmachine ssh-cert-create --vault-name <VN> --resource-id <RID>` | Uses `ssh-keygen`, generates cert successfully | | |
| 8.3 | ssh-keygen not installed | OpenSSH missing from system | Temporarily remove ssh-keygen from PATH then run `az provisionedmachine ssh-cert-create --vault-name <VN> --resource-id <RID>` | Error with platform-specific install instructions (Windows: OpenSSH.Client, macOS: brew, Linux: apt/dnf) | | |

---

## 9. Edge Cases

| S.No | Test Case | Desc | Command | Expected Result | Actual Result | Status |
|------|-----------|------|---------|-----------------|---------------|--------|
| 9.1 | Resource ID with trailing slash | Trailing `/` in resource ID | `az provisionedmachine ssh-cert-create --vault-name <VN> --resource-id "<RID>/"` | Fails validation (trailing slash not in regex pattern) | | |
| 9.2 | Vault name at min boundary (3 chars) | Minimum valid length | `az provisionedmachine ssh-cert-create --vault-name "abc" --resource-id <RID>` | Passes vault name validation (may fail at KV lookup) | | |
| 9.3 | Vault name at max boundary (24 chars) | Maximum valid length | `az provisionedmachine ssh-cert-create --vault-name "abcdefghijklmnopqrstuvwx" --resource-id <RID>` | Passes vault name validation (may fail at KV lookup) | | |
| 9.4 | Long PIM activation | Max PIM window | Activate PIM for 8 hours, generate cert, then `ssh-keygen -L -f "<cert>"` | Certificate valid-to matches PIM end time (up to 8 hours from now) | | |

---

## Test Execution Summary

| Category | # Tests | Pass | Fail | Blocked |
|----------|---------|------|------|---------|
| 1. Installation & Help | 5 | | | |
| 2. Input Validation | 8 | | | |
| 3. Auth & Authorization | 5 | | | |
| 4. Key Vault Errors | 3 | | | |
| 5. Happy Path | 8 | | | |
| 6. SSH Connection | 4 | | | |
| 7. Cleanup & Security | 3 | | | |
| 8. Cross-Platform | 3 | | | |
| 9. Edge Cases | 4 | | | |
| **Total** | **43** | | | |

---

## Sign-Off

| Role | Name | Date | Status |
|------|------|------|--------|
| Tester | | | |
| Developer | | | |
| Reviewer | | | |
