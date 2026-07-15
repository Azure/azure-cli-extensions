# End-to-End Testing Guide: `az provisionedmachine ssh-cert-create`

This guide covers the complete flow for testing SSH certificate-based authentication
using the `provisionedmachine ssh-cert-create` Azure CLI extension command.

The `.whl` file is located at: `src/provisionedmachine/dist/provisionedmachine-1.0.0b3-py3-none-any.whl`

---

## Prerequisites

| Item | Details |
|------|---------|
| **Azure CLI** | 2.60+ |
| **OpenSSH Client** | `ssh-keygen` must be on PATH |
| **Python** | `cryptography` package (for CA key conversion in Part A only) |
| **Azure Login** | `az login --tenant <tenant-id>` |
| **PIM-eligible role** | Provisioned Machine Admin on the target edge machine resource |
| **Key Vault** | With an RSA key named `<deviceId>-ssh-ca` (sign + verify ops) |
| **Key Vault Permissions** | Signed-in user needs `Key Get` + `Key Sign` on the vault |
| **Target device** | Linux edge machine with sshd running, reachable via SSH |

---

## Part 0 — Install the Extension

```powershell
# Install
az extension add --source provisionedmachine-1.0.0b3-py3-none-any.whl --yes

# Verify
az extension list --query "[?name=='provisionedmachine']" -o table

# Check help
az provisionedmachine ssh-cert-create -h
```

---

## Part A — One-Time Infra Setup (Admin)

> These steps are done **once per device** by the platform admin, not by the SSH user.

### A1. Create CA Key in Key Vault

```powershell
az keyvault key create \
    --vault-name <vault-name> \
    --name <deviceId>-ssh-ca \
    --kty RSA --size 2048 --ops sign verify
```

Example:
```powershell
az keyvault key create --vault-name sshCaTestVault \
    --name 0aed6ef3-27d0-43ed-91ec-2aef352ebc67-ssh-ca \
    --kty RSA --size 2048 --ops sign verify
```

### A2. Get CA Public Key in OpenSSH Format

```powershell
# Download PEM
az keyvault key download --vault-name <vault-name> \
    --name <deviceId>-ssh-ca --file ca_key.pem --encoding PEM

# Convert PEM → OpenSSH
python -c "
from cryptography.hazmat.primitives.serialization import load_pem_public_key, Encoding, PublicFormat
import sys
key = load_pem_public_key(open(sys.argv[1],'rb').read())
print(key.public_bytes(Encoding.OpenSSH, PublicFormat.OpenSSH).decode())
" ca_key.pem
```

Copy the output (`ssh-rsa AAAA...`).

### A3. Server-Side Setup (on the device)

SSH into the device (via Arc SSH, password, or existing key) and run:

```bash
# Deploy CA public key
echo 'ssh-rsa AAAA...your-ca-public-key...' | sudo tee /etc/ssh/ssh_ca.pub > /dev/null
sudo chmod 644 /etc/ssh/ssh_ca.pub

# Create authorized principals for login user(s)
sudo mkdir -p /etc/ssh/auth_principals

# For shared user (edgeuser):
printf 'username=<user-alias>\nrole=Provisioned Machine Admin\n' | sudo tee /etc/ssh/auth_principals/edgeuser > /dev/null
sudo chmod 644 /etc/ssh/auth_principals/edgeuser

# For per-user JIT account (optional):
sudo useradd -m <user-alias>_jit
printf 'username=<user-alias>\nrole=Provisioned Machine Admin\n' | sudo tee /etc/ssh/auth_principals/<user-alias>_jit > /dev/null
sudo chmod 644 /etc/ssh/auth_principals/<user-alias>_jit

# Configure sshd
echo "" | sudo tee -a /etc/ssh/sshd_config > /dev/null
echo "# CA-based SSH certificate authentication" | sudo tee -a /etc/ssh/sshd_config > /dev/null
echo "TrustedUserCAKeys /etc/ssh/ssh_ca.pub" | sudo tee -a /etc/ssh/sshd_config > /dev/null
echo "AuthorizedPrincipalsFile /etc/ssh/auth_principals/%u" | sudo tee -a /etc/ssh/sshd_config > /dev/null

# Validate and restart
sudo sshd -t && sudo systemctl restart sshd
```

### A4. Create PIM-Eligible Role Assignment

```powershell
# Get user's Object ID
$userOid = (az ad signed-in-user show --query id -o tsv)

# Get the Provisioned Machine Admin role definition ID
$roleDefId = (az role definition list --name "Provisioned Machine Admin" --query "[0].id" -o tsv)

# Create PIM-eligible assignment on the edge machine
$guid = [guid]::NewGuid().ToString()
$scope = "<full-resource-id-of-edge-machine>"

az rest --method PUT `
    --url "https://management.azure.com${scope}/providers/Microsoft.Authorization/roleEligibilityScheduleRequests/${guid}?api-version=2020-10-01" `
    --headers "Content-Type=application/json" `
    --body "{'properties':{'principalId':'${userOid}','roleDefinitionId':'${roleDefId}','requestType':'AdminAssign','scheduleInfo':{'expiration':{'type':'AfterDuration','duration':'P365D'}}}}"
```

### A5. Grant Key Vault Crypto User on the Vault

```powershell
az role assignment create `
    --assignee "$userOid" `
    --role "Key Vault Crypto User" `
    --scope "/subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.KeyVault/vaults/<vault-name>"
```

> This grants `Key Get` + `Key Sign` on the vault (data-plane access needed for certificate signing).

---

## Part B — User Flow (Repeatable)

> These steps are done each time a user needs SSH access.

### B1. Activate PIM Role

**Option A — Via Azure Portal:**

1. Go to **Azure Portal → Privileged Identity Management → My roles**
2. Select **Azure resources** → find your eligible role on the target device
3. Click **Activate** → provide justification
4. Wait 1-2 minutes for propagation

**Option B — Via CLI:**

```powershell
# 1. Find your eligibility schedule ID
$scope = "<full-resource-id-of-edge-machine>"
$userOid = (az ad signed-in-user show --query id -o tsv)
$roleDefId = (az role definition list --name "Provisioned Machine Admin" --query "[0].id" -o tsv)

# List eligible assignments to find the schedule ID
az rest --method GET `
    --url "https://management.azure.com${scope}/providers/Microsoft.Authorization/roleEligibilityScheduleInstances?api-version=2020-10-01" `
    --query "value[?properties.principalId=='${userOid}' && properties.expandedProperties.roleDefinition.displayName=='Provisioned Machine Admin'].name" -o tsv

# 2. Activate (replace <eligibilityScheduleId> with the value from above)
$guid = [guid]::NewGuid().ToString()
az rest --method PUT `
    --url "https://management.azure.com${scope}/providers/Microsoft.Authorization/roleAssignmentScheduleRequests/${guid}?api-version=2020-10-01" `
    --headers "Content-Type=application/json" `
    --body "{'properties':{'principalId':'${userOid}','roleDefinitionId':'${roleDefId}','requestType':'SelfActivate','linkedRoleEligibilityScheduleId':'<eligibilityScheduleId>','justification':'SSH certificate generation','scheduleInfo':{'expiration':{'type':'AfterDuration','duration':'PT2H'}}}}"
```

### B2. Generate SSH Certificate

```powershell
az provisionedmachine ssh-cert-create \
    --vault-name <vault-name> \
    --resource-id "<full-arm-resource-id>"
```

Example:
```powershell
az provisionedmachine ssh-cert-create \
    --vault-name sshCaTestVault \
    --resource-id "/subscriptions/ff0aa6da-20f8-44fe-9aee-381c8e8a4aeb/resourceGroups/schedrun-eus-rg2606111y9/providers/Microsoft.AzureStackHCI/edgeMachines/0aed6ef3-27d0-43ed-91ec-2aef352ebc67"
```

With custom output paths:
```powershell
az provisionedmachine ssh-cert-create \
    --vault-name sshCaTestVault \
    --resource-id "<resource-id>" \
    --private-key-path "$HOME\.ssh\device_key" \
    --cert-path "$HOME\.ssh\device_cert.pub"
```

Expected output:
```json
{
  "certificatePath": "C:\\Users\\...\\azssh_pm_xxxx\\id_rsa.pem-cert.pub",
  "privateKeyPath": "C:\\Users\\...\\azssh_pm_xxxx\\id_rsa.pem"
}
```

### B3. (Optional) Inspect the Certificate

```powershell
ssh-keygen -L -f "<certificatePath>"
```

Verify:
- Type: `ssh-rsa-cert-v01@openssh.com user certificate`
- Principals: `username=<alias>`, `role=Provisioned Machine Admin`
- Valid window matches PIM activation
- Critical Options: (none)
- Extensions: `permit-pty`

### B4. SSH into the Device

**Direct SSH (from a machine with network access to the device):**
```powershell
ssh -i "<privateKeyPath>" \
    -o CertificateFile="<certificatePath>" \
    -o StrictHostKeyChecking=no \
    <user>@<device-ip>
```

Examples:
```powershell
# As shared user:
ssh -i "C:\Users\...\id_rsa.pem" \
    -o CertificateFile="C:\Users\...\id_rsa.pem-cert.pub" \
    -o StrictHostKeyChecking=no \
    edgeuser@10.20.1.100

# As per-user JIT account:
ssh -i "C:\Users\...\id_rsa.pem" \
    -o CertificateFile="C:\Users\...\id_rsa.pem-cert.pub" \
    -o StrictHostKeyChecking=no \
    pusrivastava_jit@10.20.1.100
```

**Via Azure Arc SSH (when device is not directly reachable):**
```powershell
az ssh arc \
    --subscription "<sub-id>" \
    --resource-group "<managed-rg>" \
    --name "<arc-machine-name>" \
    --local-user "edgeuser" \
    --private-key-file "<privateKeyPath>" \
    --certificate-file "<certificatePath>" \
    --yes
```

### B5. Cleanup

```powershell
# Delete ephemeral key files after use
Remove-Item -Recurse -Force "<temp-directory>"
```

---

## Part C — Building the .whl

```powershell
cd src\provisionedmachine
python setup.py bdist_wheel
# Output: src/provisionedmachine/dist/provisionedmachine-1.0.0b3-py3-none-any.whl
```

Install on another machine:
```powershell
az extension add --source provisionedmachine-1.0.0b3-py3-none-any.whl --yes
```

Uninstall:
```powershell
az extension remove --name provisionedmachine
```

---

## Troubleshooting

### PIM Errors

| Error | Cause | Fix |
|-------|-------|-----|
| "No active PIM role assignment found" | PIM not activated | Activate via Portal → PIM → My roles |
| "Direct (permanent) role assignment" | Direct RBAC + no PIM activated | Activate PIM; direct assignments alone are rejected |
| "PIM activation has expired" | JIT window elapsed | Re-activate PIM |

> **Note:** In some tenants (particularly with custom roles like `Provisioned Machine Admin`),
> PIM-activated assignments may not appear in `roleAssignmentScheduleInstances` with
> `assignmentType = "Activated"`. The extension handles this by also querying
> `roleAssignmentScheduleRequests` as a fallback. If PIM activation appears stuck,
> wait 2-5 minutes for propagation.

### Key Vault Errors

| Error | Cause | Fix |
|-------|-------|-----|
| "Unable to connect to Key Vault" | Vault name wrong or doesn't exist | Verify vault name |
| "Key not found in vault" | `<deviceId>-ssh-ca` key missing | Create it with `az keyvault key create` |
| "Access denied to Key Vault" | Missing Key Get/Sign permission | Grant `Key Vault Crypto User` role |

### SSH Errors

| Error | Cause | Fix |
|-------|-------|-----|
| "Connection timed out" | No network route to device | Use Arc SSH or connect from a machine on the same network |
| "no matching principal found" | Principals file mismatch | Verify `/etc/ssh/auth_principals/<user>` matches cert principals |
| "key not certified by trusted CA" | Wrong CA key on device | Verify `/etc/ssh/ssh_ca.pub` matches the KV key |
| "certificate has expired" | PIM window ended | Re-activate PIM and regenerate cert |

### Recovery — Remove CA Config from sshd

```bash
sudo sed -i '/TrustedUserCAKeys/d; /AuthorizedPrincipalsFile/d; /# CA-based SSH/d' /etc/ssh/sshd_config
sudo systemctl daemon-reload && sudo systemctl restart sshd
```

---

## Test Environment Reference

### Environment 1 — ALCS Tenant (Primary)

| Item | Value |
|------|-------|
| Subscription | `98f24b96-fffa-4142-bec5-8472d0f30749` (AzureStack_ALCS_CI1) |
| Tenant | `2ffc1db7-b373-4be0-a5ec-f54edd5bf695` (azurestackinfra) |
| Key Vault | `remote-ssh-poc1` |
| Edge Machine | `aurosffeus16062026B` |
| Resource Group | `ar-sff-rg` |
| Custom Roles | Provisioned Machine Admin / Contributor / Reader |
| CA Key Name | `aurosffeus16062026B-ssh-ca` |

### Environment 2 — Microsoft Tenant

| Item | Value |
|------|-------|
| Subscription | `ff0aa6da-20f8-44fe-9aee-381c8e8a4aeb` (HCI IDC Test) |
| Tenant | `72f988bf-86f1-41af-91ab-2d7cd011db47` (Microsoft) |
| Key Vault | `sshCaTestVault` |
| Edge Machine | `0aed6ef3-27d0-43ed-91ec-2aef352ebc67` |
| Resource Group | `schedrun-eus-rg2606111y9` |
| Arc Machine | `dfd4c006-c865-4dd2-b304-bbae7d1c30a5-1` (in `managed-schedrun-eus-rg2606111y9`) |
| Device IP | `10.20.1.100` |
| Azure VM (host) | `schedrun-eus1y9-vm` (public IP: `68.218.94.58`) |
| Device OS Users | `edgeuser`, `pusrivastava_jit` |
| CA Key Name | `0aed6ef3-27d0-43ed-91ec-2aef352ebc67-ssh-ca` |

---

## Part D — Full E2E with Docker Container (Simulated Edge Device)

> This is the **complete runbook** for testing the SSH certificate flow against a local
> Docker container. Follow steps in order. Replace `<placeholders>` with your values.

### Prerequisites for Part D

| Item | Details |
|------|---------|
| **Docker** | Docker Desktop running (`docker info` succeeds) |
| **Azure CLI** | Logged in: `az login --tenant <tenant-id>` |
| **Extension** | Installed: `az extension add --source provisionedmachine-1.0.0b3-py3-none-any.whl --yes` |
| **Subscription** | Set: `az account set --subscription <sub-id>` |
| **PIM Eligibility** | `Provisioned Machine Admin` eligible on the edge machine resource |
| **Key Vault Access** | `Key Vault Crypto User` role on the vault |

---

### Step 1: Run the Container

```powershell
# Pull Azure Linux 3.0 base image
docker pull mcr.microsoft.com/azurelinux/base/core:3.0

# Run container with SSH port mapped
docker run -d -p 2222:22 --name ssh-jit-tester mcr.microsoft.com/azurelinux/base/core:3.0 sleep infinity

# Verify it's running
docker ps --filter name=ssh-jit-tester --format "table {{.Names}}\t{{.Status}}"
```

> **Alternative**: If you have access to Eric's pre-built image:
> ```powershell
> az acr login --name sshjittester-b0buhpcygxeyg0hq.azurecr.io
> docker pull sshjittester-b0buhpcygxeyg0hq.azurecr.io/sshjittester:0.0.1
> docker run -d -p 2222:22 --name ssh-jit-tester sshjittester-b0buhpcygxeyg0hq.azurecr.io/sshjittester:0.0.1
> ```

---

### Step 2: Get Root Shell and Install SSH Server

```powershell
docker exec -it ssh-jit-tester /bin/bash
```

Inside the container:
```bash
# Install prerequisites
tdnf install -y openssh-server sudo procps-ng

# Generate host keys
ssh-keygen -A

# Start sshd
/usr/sbin/sshd

# Verify it's running
ps aux | grep sshd
```

---

### Step 3: Create CA Key in Key Vault (if not already done)

Back on your local machine:
```powershell
# Create a new RSA key for SSH CA signing (skip if key already exists)
az keyvault key create `
    --vault-name <vault-name> `
    --name <deviceId>-ssh-ca `
    --kty RSA --size 2048 --ops sign verify
```

---

### Step 4: Export CA Public Key in OpenSSH Format

```powershell
# Remove any stale local file first
Remove-Item ca_key.pem -ErrorAction SilentlyContinue

# Download the public key from Key Vault
az keyvault key download `
    --vault-name <vault-name> `
    --name <deviceId>-ssh-ca `
    --file ca_key.pem --encoding PEM

# Convert PEM → OpenSSH format
python -c "
from cryptography.hazmat.primitives.serialization import load_pem_public_key, Encoding, PublicFormat
import sys
key = load_pem_public_key(open(sys.argv[1],'rb').read())
print(key.public_bytes(Encoding.OpenSSH, PublicFormat.OpenSSH).decode())
" ca_key.pem > ca.pub

# Verify the fingerprint (note this — it must match what signs the cert)
ssh-keygen -l -f ca.pub
```

---

### Step 5: Deploy CA Key to the Container

```powershell
# Copy the CA public key into the container
docker cp ca.pub ssh-jit-tester:/tmp/ca.pub
```

Inside the container (root shell via `docker exec -it ssh-jit-tester /bin/bash`):
```bash
# Place CA key at the expected location
mkdir -p /etc/ssh/jit
mv /tmp/ca.pub /etc/ssh/jit/ca.pub
chmod 0444 /etc/ssh/jit/ca.pub

# Verify fingerprint matches what you saw in Step 4
ssh-keygen -l -f /etc/ssh/jit/ca.pub
```

---

### Step 6: Configure sshd for Certificate Authentication

Inside the container:
```bash
# Add CA trust and principals config to sshd
echo "" >> /etc/ssh/sshd_config
echo "# CA-based SSH certificate authentication" >> /etc/ssh/sshd_config
echo "TrustedUserCAKeys /etc/ssh/jit/ca.pub" >> /etc/ssh/sshd_config
echo "AuthorizedPrincipalsFile /etc/ssh/auth_principals/%u" >> /etc/ssh/sshd_config

# Create the JIT user
useradd -m <your-alias>_jit

# Create principals file for the JIT user
mkdir -p /etc/ssh/auth_principals
printf 'username=<your-alias>\nrole=Provisioned Machine Admin\n' > /etc/ssh/auth_principals/<your-alias>_jit
chmod 644 /etc/ssh/auth_principals/<your-alias>_jit

# Verify
cat /etc/ssh/auth_principals/<your-alias>_jit

# Validate sshd config and restart
sshd -t && pkill sshd && /usr/sbin/sshd
echo "sshd restarted successfully"
```

---

### Step 7: Activate PIM Role

Back on your local machine:
```powershell
# Set variables
$scope = "<full-resource-id-of-edge-machine>"
$userOid = (az ad signed-in-user show --query id -o tsv)
$roleDefId = (az role definition list --name "Provisioned Machine Admin" --query "[0].id" -o tsv)

# Find your eligibility schedule ID
$token = (az account get-access-token --resource https://management.azure.com --query accessToken -o tsv)
$resp = Invoke-RestMethod -Uri "https://management.azure.com${scope}/providers/Microsoft.Authorization/roleEligibilityScheduleInstances?api-version=2020-10-01&`$filter=assignedTo('${userOid}')" -Headers @{Authorization="Bearer $token"}
$eligId = ($resp.value | Where-Object {
    $_.properties.expandedProperties.roleDefinition.displayName -eq "Provisioned Machine Admin" -and
    $_.properties.memberType -eq "Direct"
}).name
Write-Host "Eligibility ID: $eligId"

# Activate PIM (2 hour window)
$guid = [guid]::NewGuid().ToString()
az rest --method PUT `
    --url "https://management.azure.com${scope}/providers/Microsoft.Authorization/roleAssignmentScheduleRequests/${guid}?api-version=2020-10-01" `
    --headers "Content-Type=application/json" `
    --body "{'properties':{'principalId':'${userOid}','roleDefinitionId':'${roleDefId}','requestType':'SelfActivate','linkedRoleEligibilityScheduleId':'${eligId}','justification':'SSH certificate generation','scheduleInfo':{'expiration':{'type':'AfterDuration','duration':'PT2H'}}}}"

# Wait for status = "Provisioned"
```

> **Or activate via Portal**: Azure Portal → PIM → My roles → Azure resources → Activate

---

### Step 8: Generate SSH Certificate

```powershell
az provisionedmachine ssh-cert-create `
    --vault-name <vault-name> `
    --resource-id "<full-resource-id-of-edge-machine>"
```

Expected output:
```json
{
  "certificatePath": "C:\\Users\\...\\azssh_pm_xxxx\\id_rsa.pem-cert.pub",
  "privateKeyPath": "C:\\Users\\...\\azssh_pm_xxxx\\id_rsa.pem"
}
```

Save the paths:
```powershell
$keyPath = "<privateKeyPath from output>"
$certPath = "<certificatePath from output>"
```

---

### Step 9: (Optional) Inspect the Certificate

```powershell
ssh-keygen -L -f "$certPath"
```

Verify:
- **Principals**: `username=<your-alias>`, `role=Provisioned Machine Admin`
- **Signing CA fingerprint** matches what you saw in Step 4
- **Valid window** covers current time
- **Extensions**: `permit-pty`

---

### Step 10: SSH into the Container

```powershell
# Clear old known_hosts entry
ssh-keygen -f "$HOME\.ssh\known_hosts" -R "[localhost]:2222" 2>$null

# SSH using the certificate
ssh -i "$keyPath" `
    -o CertificateFile="$certPath" `
    -o StrictHostKeyChecking=no `
    -p 2222 `
    <your-alias>_jit@localhost
```

**Expected**: You get a shell inside the container as `<your-alias>_jit`.

Verify:
```bash
whoami       # → <your-alias>_jit
id           # → uid=1000(...) gid=1000(...)
```

---

### Step 11: Cleanup

```powershell
# Stop and remove the container
docker stop ssh-jit-tester
docker rm ssh-jit-tester

# Delete ephemeral key files
Remove-Item -Recurse -Force (Split-Path $keyPath)

# (Optional) Remove local key files
Remove-Item ca_key.pem, ca.pub -ErrorAction SilentlyContinue
```

---

### Quick Reference — Example with Real Values

```powershell
# === FULL EXAMPLE (ALCS Tenant) ===

# Login
az login --tenant 2ffc1db7-b373-4be0-a5ec-f54edd5bf695
az account set --subscription 98f24b96-fffa-4142-bec5-8472d0f30749

# Install extension
az extension add --source provisionedmachine-1.0.0b3-py3-none-any.whl --yes

# Run container
docker pull mcr.microsoft.com/azurelinux/base/core:3.0
docker run -d -p 2222:22 --name ssh-jit-tester mcr.microsoft.com/azurelinux/base/core:3.0 sleep infinity
docker exec ssh-jit-tester bash -c "tdnf install -y openssh-server procps-ng && ssh-keygen -A && /usr/sbin/sshd"

# Export CA key
Remove-Item ca_key.pem -ErrorAction SilentlyContinue
az keyvault key download --vault-name remote-ssh-poc1 --name aurosffeus16062026B-ssh-ca --file ca_key.pem --encoding PEM
python -c "from cryptography.hazmat.primitives.serialization import load_pem_public_key,Encoding,PublicFormat;import sys;key=load_pem_public_key(open(sys.argv[1],'rb').read());print(key.public_bytes(Encoding.OpenSSH,PublicFormat.OpenSSH).decode())" ca_key.pem > ca.pub

# Deploy to container
docker cp ca.pub ssh-jit-tester:/tmp/ca.pub
docker exec ssh-jit-tester bash -c '
  mkdir -p /etc/ssh/jit && mv /tmp/ca.pub /etc/ssh/jit/ca.pub && chmod 0444 /etc/ssh/jit/ca.pub
  echo "" >> /etc/ssh/sshd_config
  echo "TrustedUserCAKeys /etc/ssh/jit/ca.pub" >> /etc/ssh/sshd_config
  echo "AuthorizedPrincipalsFile /etc/ssh/auth_principals/%u" >> /etc/ssh/sshd_config
  useradd -m pusrivastava_jit
  mkdir -p /etc/ssh/auth_principals
  printf "username=pusrivastava\nrole=Provisioned Machine Admin\n" > /etc/ssh/auth_principals/pusrivastava_jit
  chmod 644 /etc/ssh/auth_principals/pusrivastava_jit
  pkill sshd; /usr/sbin/sshd
'

# Activate PIM (via Portal or CLI) — then generate cert
az provisionedmachine ssh-cert-create --vault-name remote-ssh-poc1 `
    --resource-id "/subscriptions/98f24b96-fffa-4142-bec5-8472d0f30749/resourceGroups/ar-sff-rg/providers/Microsoft.AzureStackHCI/edgeMachines/aurosffeus16062026B"

# SSH in (use paths from output above)
ssh -i "<privateKeyPath>" -o CertificateFile="<certPath>" -o StrictHostKeyChecking=no -p 2222 pusrivastava_jit@localhost
```
