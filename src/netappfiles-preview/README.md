# Azure CLI for Azure NetApp Files (ANF) Extension #
This is an extension to azure cli which provides commands to create and manage Azure NetApp File (ANF) storage resources.

## How to use ##
First, install the extension:
```
az extension add --name netappfiles-preview
```

It can then be used to create volumes and snapshots. The typical sequence would be to first create an account
```
az netappfiles account create --resource-group rg -n account_name
```

Then allocate a storage pool in which volumes can be created
```
az netappfiles pool create --resource-group rg -a account_name -n pool_name -l location --size 4398046511104 --service-level "Premium"
```

Volumes are created within the pool resource
```
az netappfiles volume create --resource-group rg -a account_name -p pool_name -n volume_name -l location --service-level "Premium" --usage-threshold 107374182400 --creation-token "unique-token" --subnet-id "/subscriptions/mysubsid/resourceGroups/myrg/providers/Microsoft.Network/virtualNetworks/myvnet/subnets/default"
```

Snapshots of volumes can also be created
```
az netappfiles snapshot create --resource-group rg -a account_name --p pool_name -v vname -n snapshot_name -l location --file-system-id volume-uuid
```

These resources can be updated, deleted and listed. See the help to find out more
```
az netappfiles --help
```
