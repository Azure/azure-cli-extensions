# Azure CLI Fileshares Extension

Manage Azure File Shares resources (API version `2026-09-01`).

## Install

Version `1.1.0b1` is a preview release. Install it with `--allow-preview`; without it, `az extension add` installs the latest stable version (`1.0.2`, API version `2026-06-01`).

```bash
az extension add --name fileshare --allow-preview true
```

API version `2026-09-01` is currently available only in the East US 2 EUAP region (`eastus2euap`).

## Usage

### Create a file share

```bash
az fileshare create --name <share-name> --resource-group <resource-group> \
    --location <location> --protocol NFS --media-tier SSD --redundancy Local \
    --provisioned-storage-gib <storage-gib> --provisioned-iops <iops> \
    --provisioned-throughput-mib <throughput-mib>
```

### List file shares in a subscription

```bash
az fileshare list
```

### Show a file share

```bash
az fileshare show --name <share-name> --resource-group <resource-group>
```

### Check name availability

```bash
az fileshare check-name-availability --name <share-name> --location <location>
```

### Assign a managed identity

```bash
az fileshare identity assign --name <share-name> --resource-group <resource-group> --system-assigned
```

### Create a snapshot

```bash
az fileshare snapshot create --resource-name <share-name> --resource-group <resource-group> \
    --name <snapshot-name>
```

### Delete a file share

```bash
az fileshare delete --name <share-name> --resource-group <resource-group>
```

For a full list of commands and parameters, run:

```bash
az fileshare --help
```
