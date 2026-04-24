# Azure CLI Fileshares Extension

Manage Azure File Shares resources (API version `2025-09-01-preview`).

## Install

```bash
az extension add --name fileshares
```

## Usage

### Create a file share

```bash
az fileshare create --name <share-name> --resource-group <resource-group> \
    --location <location> --provisioned-bandwidth-mi-bps <bandwidth> \
    --provisioned-iops <iops> --provisioned-storage-gi-b <storage-gib> \
    --file-share-protocol <protocol>
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
az fileshare check-name-availability --name <share-name>
```

### Create a snapshot

```bash
az fileshare snapshot create --file-share-name <share-name> --resource-group <resource-group> \
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