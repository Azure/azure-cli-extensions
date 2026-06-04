# End-to-End Testing Guide: `az provisionedmachine cert-create`

This guide covers the full flow for testing SSH certificate-based authentication
using the `provisionedmachine cert-create` Azure CLI extension command.

---

## Prerequisites

| Item | Details |
|------|---------|
| **Azure CLI** | 2.60+ with Python 3.10+ |
| **PIM-eligible role** | Provisioned Machine Admin / Contributor / Reader on the target resource |
| **Key Vault** | With an RSA key named `<deviceId>-ssh-ca` (sign + verify ops) |
| **Target device** | Linux machine (edge device) reachable via SSH |
| **Python packages** | `cryptography` (for CA public key conversion) |

---

## Part A — Server-Side Setup (on the target Linux device)

> **Run these steps once per device.** You need root/sudo access on the device.

### A1. Get the CA Public Key in OpenSSH Format

Download the PEM public key from Azure Portal:

```
Azure Portal → Key Vault → Keys → <deviceId>-ssh-ca → Download public key
```

Save the file as `ca_key.pem`, then convert PEM → OpenSSH format:

```bash
python3 -c "
from cryptography.hazmat.primitives.serialization import load_pem_public_key, Encoding, PublicFormat
key = load_pem_public_key(open('ca_key.pem','rb').read())
print(key.public_bytes(Encoding.OpenSSH, PublicFormat.OpenSSH).decode())
"
```

Copy the output — it will look like `ssh-rsa AAAA...`.

### A2. Write the CA Public Key to the Device

```bash
echo 'ssh-rsa AAAA...your-ca-public-key...' | sudo tee /etc/ssh/ssh_ca.pub > /dev/null
sudo chmod 644 /etc/ssh/ssh_ca.pub
```

### A3. Create Authorized Principals for the Login User

The principals file maps which certificate holders can log in as a given OS user.
The certificate embeds `username=<alias>` and `role=<role>` as principals.

```bash
sudo mkdir -p /etc/ssh/auth_principals

# Replace 'edgeuser' with the OS username on the device.
# Replace the username= value with the Azure AD alias (without @domain).
# Replace the role= value with the PIM role name.
printf 'username=pusrivastava\nrole=Provisioned Machine Admin\n' \
  | sudo tee /etc/ssh/auth_principals/edgeuser > /dev/null

sudo chmod 644 /etc/ssh/auth_principals/edgeuser
```

> **Note:** The `username=` value must match the alias portion of the Azure AD
> UPN (e.g., `pusrivastava` for `pusrivastava@microsoft.com`). The command
> extracts this automatically.

### A4. Configure sshd for CA-Based Authentication

```bash
printf '\n# CA-based SSH certificate authentication\nTrustedUserCAKeys /etc/ssh/ssh_ca.pub\nAuthorizedPrincipalsFile /etc/ssh/auth_principals/%%u\n' \
  | sudo tee -a /etc/ssh/sshd_config > /dev/null
```

### A5. Validate and Restart sshd

```bash
sudo sshd -t && sudo systemctl restart sshd
```

If `sshd -t` reports errors, fix them before restarting.

---

## Part B — Client-Side: Generate Certificate and SSH

### B1. Activate PIM Role

Before generating a certificate, activate your PIM-eligible role:

1. Go to **Azure Portal → Privileged Identity Management → My roles**
2. Select **Azure resources** → find your eligible role on the target resource
3. Click **Activate** and provide a justification
4. Wait 1–2 minutes for propagation

### B2. Generate the SSH Certificate

#### Option 1: Using the repo code (development/testing)

```powershell
# Activate the venv
& "C:\az-development\az-cli-provisioned-machine\azure-cli-extensions\.venv\Scripts\Activate.ps1"

# Point to the extension source
$env:AZURE_EXTENSION_DEV_SOURCES = "C:\az-development\az-cli-provisioned-machine\azure-cli-extensions\src\ssh"

# Login (if needed)
az login --tenant <tenant-id>

# Generate certificate
az provisionedmachine cert-create `
  --vault-name <vault-name> `
  --resource-id "<full-ARM-resource-id>"
```

#### Option 2: Using the .whl file (customer handover)

```powershell
# Install the extension from the wheel file
az extension add --source path/to/ssh-<version>-py3-none-any.whl --yes

# Login
az login --tenant <tenant-id>

# Generate certificate
az provisionedmachine cert-create `
  --vault-name <vault-name> `
  --resource-id "<full-ARM-resource-id>"
```

#### Example

```powershell
az provisionedmachine cert-create `
  --vault-name remote-ssh-poc1 `
  --resource-id "/subscriptions/98f24b96-fffa-4142-bec5-8472d0f30749/resourceGroups/push-sff-rg/providers/Microsoft.AzureStackHCI/edgeMachines/aurosffnebvt22052026A"
```

#### Expected Output

```json
{
  "certificatePath": "C:\\Users\\...\\azssh_pm_xxxx\\id_rsa.pem-cert.pub",
  "privateKeyPath": "C:\\Users\\...\\azssh_pm_xxxx\\id_rsa.pem"
}
```
```
SSH certificate created successfully.
  Private key : C:\Users\...\azssh_pm_xxxx\id_rsa.pem
  Certificate : C:\Users\...\azssh_pm_xxxx\id_rsa.pem-cert.pub
  Usage: ssh -i <privateKeyPath> -o CertificateFile=<certPath> <alias>_jit@<device-hostname>
```

### B3. SSH into the Device

Use the paths from the command output:

```powershell
ssh -i "<privateKeyPath>" `
    -o CertificateFile="<certPath>" `
    -o StrictHostKeyChecking=no `
    edgeuser@<device-ip-or-hostname>
```

#### Example

```powershell
ssh -i "C:\Users\PUSRIV~1\AppData\Local\Temp\azssh_pm_xxxx\id_rsa.pem" `
    -o CertificateFile="C:\Users\PUSRIV~1\AppData\Local\Temp\azssh_pm_xxxx\id_rsa.pem-cert.pub" `
    -o StrictHostKeyChecking=no `
    edgeuser@172.18.173.125
```

### B4. (Optional) Inspect the Certificate

```bash
ssh-keygen -L -f "<certPath>"
```

This shows the certificate details: principals, validity window, signing CA, etc.

---

## Part C — Building the .whl for Customer Handover

```powershell
# From the repo root
cd src\ssh
python setup.py bdist_wheel

# The .whl file will be in src\ssh\dist\
# e.g., ssh-<version>-py3-none-any.whl
```

Customer installs it with:

```powershell
az extension add --source ssh-<version>-py3-none-any.whl --yes
```

---

## Troubleshooting

### PIM Errors

| Error | Cause | Fix |
|-------|-------|-----|
| "No active PIM role assignment found" | PIM role not activated | Activate via Azure Portal → PIM → My roles |
| "Direct (permanent) role assignment" | Direct RBAC exists alongside PIM | The command requires PIM-only; remove direct assignments or ensure PIM activation is present |
| "PIM activation has expired" | JIT window elapsed | Re-activate the PIM role |

### sshd Errors

| Symptom | Fix |
|---------|-----|
| `sshd -t` fails | Check `/etc/ssh/sshd_config` syntax |
| "no matching principal found" | Verify `/etc/ssh/auth_principals/<user>` contains `username=<alias>` matching the cert |
| "key not certified by trusted CA" | Verify `/etc/ssh/ssh_ca.pub` matches the Key Vault CA key |

### Recovery: Remove CA Config from sshd

If sshd breaks after the CA configuration changes:

```bash
sudo sed -i '/TrustedUserCAKeys/d; /AuthorizedPrincipalsFile \/etc\/ssh\/auth_principals/d; /# CA-based SSH/d' /etc/ssh/sshd_config
sudo systemctl daemon-reload && sudo systemctl restart sshd
```

### Cleanup: Delete Ephemeral Keys

The private key and certificate are stored in a temp directory. Delete them after use:

```powershell
Remove-Item -Recurse -Force "C:\Users\...\AppData\Local\Temp\azssh_pm_xxxx"
```

---

## Test Matrix

| # | Scenario | Expected Result |
|---|----------|-----------------|
| 1 | No PIM activation | Error: "No active PIM role assignment found" |
| 2 | Direct role only (no PIM) | Error: "Direct (permanent) role assignment" |
| 3 | PIM activated, valid cert | Certificate generated, SSH succeeds |
| 4 | Expired PIM activation | Error: "PIM activation has expired" |
| 5 | Invalid vault name | Error: "Vault name must be 3–24 chars..." |
| 6 | Invalid resource ID | Error: "Resource ID must start with /subscriptions..." |
| 7 | Missing CA key in vault | Error from Key Vault (key not found) |
| 8 | Certificate expired (wait for expiry) | SSH rejected by server |
| 9 | Wrong principals on server | SSH rejected: "no matching principal found" |
| 10 | Run from Linux client | Same flow works cross-platform |
