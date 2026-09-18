# Connect to small form factor deployments of Azure Local using just-in-time (JIT) access (preview)

This article describes how to use just-in-time (JIT) access to connect to a small form factor deployment of Azure Local running Azure Linux. By using JIT access, an administrator grants users eligible role assignments through Microsoft Entra Privileged Identity Management (PIM). Users activate the role only when they need it, for a limited period of time, and connect to the device over SSH by using a short-lived certificate.

JIT access lets any authorized user reach the device temporarily, without standing administrative permissions on the resource.

The workflow has two roles:

- **Administrator**: configures eligible PIM assignments, sets up the Key Vault CA key, and approves activation requests.
- **User**: installs the Azure CLI extension, activates their role, and connects to the device.

> [!NOTE]
> The `provisionedmachine` Azure CLI extension is in **preview**. Preview features are provided without a service-level agreement and aren't recommended for production workloads. Some features might not be supported or might have constrained capabilities.

> [!IMPORTANT]
> This feature is currently in PREVIEW. See the [Supplemental Terms of Use for Microsoft Azure Previews](https://azure.microsoft.com/support/legal/preview-supplemental-terms/) for legal terms that apply to Azure features that are in beta, preview, or otherwise not yet released into general availability.

## Prerequisites

Before you begin, make sure you have:

- An Azure Local device with a provisioned machine resource in your subscription.
- An administrator with permission to manage role assignments in Microsoft Entra PIM for the target resource.
- The latest version of the [Azure CLI](/cli/azure/install-azure-cli) installed on the user's workstation.
- OpenSSH installed on the user's workstation (`ssh-keygen` must be available in the system PATH).
- The `provisionedmachine` Azure CLI extension `.whl` package, which provides the provisioned machine SSH command.

## Roles used in this workflow

JIT access uses the following provisioned machine roles. An administrator assigns one or more of these roles as eligible roles, and the user activates them when needed.

| Role | Typical use | Certificate principal |
|------|------------|----------------------|
| Provisioned Machine Administrator | Full administrative access to the device | `provisionedmachineadmin` |
| Provisioned Machine Contributor | Manage device configuration without full admin access | `provisionedmachinecontributor` |
| Provisioned Machine Reader | Read-only access to the device | `provisionedmachinereader` |

> [!IMPORTANT]
> Users need **two separate role activations** to generate an SSH certificate:
>
> 1. A **Provisioned Machine role** (Administrator, Contributor, or Reader) on the edge machine resource — determines the SSH access level.
> 2. The **Key Vault Crypto User** role on the device's key vault — allows the CLI to sign the certificate using the CA key.
>
> Both roles must be active simultaneously.

## Administrator: Set up the Key Vault CA key

Each provisioned machine has a corresponding CA (Certificate Authority) signing key stored in Azure Key Vault. The CLI uses this key to sign SSH certificates. The key name must follow the convention `<provisioned-machine-name>-ssh-ca`.

For example, if the provisioned machine is named `machine1`, the Key Vault key name must be `machine1-ssh-ca`.

> [!NOTE]
> The CA private key is **non-exportable** and never leaves Key Vault. Only the Key Vault Sign API is used to sign certificates. This is a security design choice — the CA private key material is never exposed to any client.

### Create the Key Vault (one-time setup)

If a key vault for the device doesn't already exist:

1. In the [Azure portal](https://portal.azure.com/), search for **Key vaults** and select **Create**.
2. Fill in the required fields:
   - **Subscription**: Select the subscription that contains your provisioned machine.
   - **Resource group**: Select or create a resource group.
   - **Key vault name**: Enter a descriptive name (for example, `machine1-keyvault`).
   - **Region**: Select the same region as your provisioned machine.
3. On the **Access configuration** tab, select **Azure role-based access control** as the permission model.
4. Select **Review + create**, and then **Create**.

### Create the CA signing key (one-time setup)

1. In the [Azure portal](https://portal.azure.com/), navigate to the key vault you created.
2. Under **Objects**, select **Keys** > **Generate/Import**.
3. Fill in the key settings:
   - **Options**: Select **Generate**.
   - **Name**: Enter `<provisioned-machine-name>-ssh-ca` (for example, `machine1-ssh-ca`).
   - **Key type**: Select **RSA**.
   - **RSA key size**: Select **4096**.
4. Under **Permitted operations**, select only **Sign** and **Verify**.
5. Select **Create**.

> [!IMPORTANT]
> The key name **must** follow the format `<provisioned-machine-name>-ssh-ca`. The CLI uses this naming convention to locate the correct CA key for each device.

### Assign Key Vault roles

The administrator who creates and manages CA keys needs the **Key Vault Crypto Officer** role on the vault. Users who generate SSH certificates need the **Key Vault Crypto User** role.

| Who | Role | Scope | Purpose |
|-----|------|-------|---------|
| Administrator | Key Vault Crypto Officer | Key Vault resource | Create and manage CA keys |
| SSH User | Key Vault Crypto User (PIM-eligible) | Key Vault resource | Sign certificates at runtime |

To assign roles on the key vault:

1. In the [Azure portal](https://portal.azure.com/), navigate to the key vault resource.
2. Select **Access control (IAM)** > **Add** > **Add role assignment**.
3. On the **Role** tab, search for and select **Key Vault Crypto Officer** (for administrators) or **Key Vault Crypto User** (for SSH users).
4. On the **Members** tab, select the users or groups to assign.
5. Select **Review + assign**.

For PIM-eligible assignments (recommended for SSH users):

1. Open **Microsoft Entra Privileged Identity Management** > **Azure resources**.
2. Navigate to the key vault resource.
3. Select **Assignments** > **Add assignments**.
4. Select **Key Vault Crypto User** as the role.
5. Select the users who need SSH access.
6. Set the assignment type to **Eligible**.
7. Complete the assignment.

## Administrator: Configure eligible PIM assignments

As an administrator, use Microsoft Entra PIM to grant users eligible assignments on the specific resource. Eligible assignments aren't active by default. The user must activate them when access is needed.

1. Sign in to the [Azure portal](https://portal.azure.com/) and open **Microsoft Entra Privileged Identity Management**.
2. Select **Azure resources**, and then select the specific provisioned machine resource you want to grant access to.
3. Select **Assignments** > **Add assignments**.
4. Choose the role to assign to users — **Provisioned Machine Reader**, **Provisioned Machine Contributor**, or **Provisioned Machine Administrator**.
5. Select the users who should receive the assignment.
6. On the **Settings** tab, set the assignment type to **Eligible**.

> [!IMPORTANT]
> Make sure the assignment type is **Eligible**, not **Active**. Users must activate eligible assignments through PIM before they take effect.

7. Complete the assignment.
8. Repeat the process for the **Key Vault Crypto User** role on the device's key vault (see [Set up the Key Vault CA key](#administrator-set-up-the-key-vault-ca-key)).

## User: Install the Azure CLI extension

The `provisionedmachine` Azure CLI extension provides the provisioned machine SSH command. Install it from the `.whl` package.

1. Download the `provisionedmachine` extension `.whl` file.
2. Install the extension:

    ```azurecli
    az extension add --source <path-to-provisionedmachine.whl>
    ```

3. If the extension is already installed, remove it and reinstall it to make sure you have the correct version:

    ```azurecli
    az extension remove --name provisionedmachine
    az extension add --source <path-to-provisionedmachine.whl>
    ```

4. Confirm the extension is installed:

    ```azurecli
    az extension list --output table
    ```

## User: Request and activate JIT access

### Step 1: Activate your PIM roles

You need to activate **two** roles before generating an SSH certificate:

1. In the [Azure portal](https://portal.azure.com/), open **Microsoft Entra Privileged Identity Management** > **My roles** > **Azure resources**.
2. Find your eligible **Provisioned Machine** role (Administrator, Contributor, or Reader) on the target device resource.
3. Under **Action**, select **Activate**.
4. Set the **duration** you need access for, up to a maximum of **8 hours**.
5. Enter a justification for the request, and then submit it.
6. **Repeat** for the **Key Vault Crypto User** role on the device's key vault.

> [!NOTE]
> Access is temporary. When the duration you selected expires, the role is automatically deactivated and you need to activate it again the next time you connect. If your organization requires approval, wait for the administrator to approve your request before proceeding.

After both roles are activated, wait approximately **60 seconds** for the role assignments to propagate before running the certificate command.

### Step 2: Generate the SSH certificate

Sign in to the Azure CLI with the correct tenant and subscription, then run the SSH certificate creation command:

```azurecli
az login --tenant <tenant-id>
az account set --subscription <subscription-id>

az provisionedmachine ssh-cert-create \
    --vault-name <vault-name> \
    --resource-id <resource-id>
```

If the command succeeds, it returns output similar to the following:

```output
{
  "certificatePath": "C:\\Users\\username\\AppData\\Local\\Temp\\azssh_pm_abc123\\id_rsa.pem-cert.pub",
  "privateKeyPath": "C:\\Users\\username\\AppData\\Local\\Temp\\azssh_pm_abc123\\id_rsa.pem"
}
SSH certificate created successfully.
  Private key : C:\Users\username\AppData\Local\Temp\azssh_pm_abc123\id_rsa.pem
  Certificate : C:\Users\username\AppData\Local\Temp\azssh_pm_abc123\id_rsa.pem-cert.pub
  Usage: ssh -i C:\Users\...\id_rsa.pem -o CertificateFile=C:\Users\...\id_rsa.pem-cert.pub username_jit@<device-hostname>
```

You can optionally specify custom output paths for the key and certificate:

```azurecli
az provisionedmachine ssh-cert-create \
    --vault-name <vault-name> \
    --resource-id <resource-id> \
    --private-key-path ~/.ssh/device_key \
    --cert-path ~/.ssh/device_cert.pub
```

### Troubleshoot certificate generation errors

| Error message | Cause | Resolution |
|--------------|-------|------------|
| `No Provisioned Machine Reader, Contributor, or Admin role assignment found` | PIM role on the edge machine isn't activated yet | Activate your Provisioned Machine role in PIM, wait 60 seconds, then retry |
| `Your PIM activation has expired or been deactivated` | PIM session timed out | Re-activate the role in PIM |
| `Access denied to Key Vault` | Key Vault Crypto User role isn't activated | Activate the Key Vault Crypto User role in PIM on the device's key vault |
| `Key '{name}' not found in vault` | The CA signing key doesn't exist | Verify the key `<provisioned-machine-name>-ssh-ca` exists in the vault. Contact your administrator if it's missing. |
| `InvalidAuthenticationTokenTenant` | Signed in to the wrong Azure AD tenant | Run `az login --tenant <correct-tenant-id>` |
| `ssh-keygen not found` | OpenSSH isn't installed | Install OpenSSH on your workstation |
| `PermissionError: [WinError 5] Access is denied` | Terminal doesn't have admin permissions | Run the terminal as Administrator (Windows) |

## User: Connect to the device

1. Copy the SSH command from the certificate command output and run it:

    ```bash
    ssh -i <privateKeyPath> -o CertificateFile=<certificatePath> <username>_jit@<device-hostname>
    ```

    Replace `<device-hostname>` with the IP address or hostname of the device.

2. When you connect successfully, you see a welcome message:

    ```output
    Welcome to Microsoft Azure Linux
    ```

    The message includes the `<username>_jit` account created for this JIT session.

You're now connected to the Azure Local small form factor device over a temporary, just-in-time session. When the activated role expires, access ends automatically.

> [!WARNING]
> The private key file is sensitive. Delete the temporary key directory after the certificate expires. The CLI prints a warning with the directory path.
