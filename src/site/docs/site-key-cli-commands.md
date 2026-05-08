# Azure Site Key CLI Commands

> Quick reference for testing `az site key` commands. These commands manage **Site Keys** for Azure Edge sites.

---

## Pre-requisites

```bash
# 1. Install the extension (from .whl file)
az extension add --source <path-to-site-1.0.0b2-py3-none-any.whl> --yes

# 2. Login and set your subscription
az login
az account set --subscription <your-subscription-id>
```

---

## Commands at a Glance

| Command | What it does |
|---------|-------------|
| `az site key create`   | Create a new site key linked to a site |
| `az site key show`     | View details of a specific site key |
| `az site key list`     | List all site keys in a resource group |
| `az site key download` | Download the site key token to a file |
| `az site key delete`   | Delete a site key |

---

> **Note:** All commands below also accept `--subscription` to target a specific subscription.
> If omitted, the subscription set via `az account set --subscription <id>` is used automatically.

## 1. Create a Site Key

Creates a new site key and links it to an existing site.

**Required arguments:**

| Argument | Description |
|----------|-------------|
| `--name` or `-n` | Name for the new site key |
| `--resource-group` or `-g` | Resource group containing the site |
| `--site-name` | Name of the site to link this key to |

**Optional arguments:**

| Argument | Description |
|----------|-------------|
| `--token-expiry-date` | Token expiry date (ISO 8601 format). Defaults to 7 days from now. |
| `--subscription` | Name or ID of subscription. If not provided, uses the currently set subscription. |

### Examples

**Minimum command:**
```bash
az site key create --name my-site-key -g MyResourceGroup --site-name MySite
```

**With custom token expiry:**
```bash
az site key create --name my-site-key -g MyResourceGroup --site-name MySite --token-expiry-date "2026-05-01T00:00:00Z"
```

**Targeting a specific subscription:**
```bash
az site key create --name my-site-key -g MyResourceGroup --site-name MySite --subscription cbeed921-3fd1-4242-b944-14bc7ce3cb48
```

---

## 2. Show a Site Key

View details of a specific site key (name, provisioning state, linked site, token expiry date, etc.)

**Required arguments:**

| Argument | Description |
|----------|-------------|
| `--name` or `-n` | Name of the site key |
| `--resource-group` or `-g` | Resource group containing the site key |

**Optional arguments:**

| Argument | Description |
|----------|-------------|
| `--subscription` | Name or ID of subscription. Uses the currently set subscription if omitted. |

### Example

```bash
az site key show --name my-site-key -g MyResourceGroup
```

---

## 3. List Site Keys

List all site keys in a resource group.

**Required arguments:**

| Argument | Description |
|----------|-------------|
| `--resource-group` or `-g` | Resource group to list site keys from |

**Optional arguments:**

| Argument | Description |
|----------|-------------|
| `--subscription` | Name or ID of subscription. Uses the currently set subscription if omitted. |

### Example

```bash
az site key list -g MyResourceGroup
```

---

## 4. Download a Site Key Token

Downloads the site key token and saves it to a file.

**Required arguments:**

| Argument | Description |
|----------|-------------|
| `--name` or `-n` | Name of the site key |
| `--resource-group` or `-g` | Resource group containing the site key |

**Optional arguments:**

| Argument | Description |
|----------|-------------|
| `--file` or `-f` | Output file path. Defaults to `<key-name>.SiteKey` in the current directory. |
| `--subscription` | Name or ID of subscription. Uses the currently set subscription if omitted. |

### Examples

**Minimum command** (saves to `my-site-key.SiteKey`):
```bash
az site key download --name my-site-key -g MyResourceGroup
```

**Save to a custom file:**
```bash
az site key download --name my-site-key -g MyResourceGroup --file ./tokens/my-token.SiteKey
```

---

## 5. Delete a Site Key

Deletes a site key. Prompts for confirmation unless `--yes` is specified.

**Required arguments:**

| Argument | Description |
|----------|-------------|
| `--name` or `-n` | Name of the site key to delete |
| `--resource-group` or `-g` | Resource group containing the site key |

**Optional arguments:**

| Argument | Description |
|----------|-------------|
| `--yes` or `-y` | Skip the confirmation prompt |
| `--subscription` | Name or ID of subscription. Uses the currently set subscription if omitted. |

### Examples

**With confirmation prompt:**
```bash
az site key delete --name my-site-key -g MyResourceGroup
```

**Skip confirmation:**
```bash
az site key delete --name my-site-key -g MyResourceGroup --yes
```

---

## Full Test Walkthrough

A step-by-step sequence to test all commands end-to-end:

```bash
# Setup
az account set --subscription <your-subscription-id>

# Step 1 — List existing site keys
az site key list -g MyResourceGroup

# Step 2 — Create a new site key
az site key create --name test-key -g MyResourceGroup --site-name MySite

# Step 3 — Show the newly created key
az site key show --name test-key -g MyResourceGroup

# Step 4 — Download the token
az site key download --name test-key -g MyResourceGroup

# Step 5 — Delete the test key
az site key delete --name test-key -g MyResourceGroup --yes
```
