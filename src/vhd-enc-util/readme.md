# Azure CLI VHD Encryption Utility #
This is an extension to azure cli which provides client side disk encryption 

## How to use ##
First, install the extension:
```
az extension add --name vhd-enc-util
```

Then, call it as you would any other az command:
```
az vm encryption encrypt-vhd --vhd-file ~/os_disk.vhd --storage-account myStorageAccount --container vhds --kv /subscriptions/xxxx/resourceGroups/myGroup/providers/Microsoft.KeyVault/vaults/myVault --kek myKey --storage-account myStorageAccount 
```