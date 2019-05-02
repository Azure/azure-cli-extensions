# Azure CLI VM Repair Extension #
This is a extension for repairing faulty VMs.

### How to use ###
Install this extension using the below CLI command
```
az extension add --name vm-repair
```

### Sample Commands ###
Swap disk command
```
az vm repair swap-disk -g MyResourceGroup -n myVM --verbose
```
Restore swap command
```
az vm repair restore-swap -g MyResourceGroup -n myVM --verbose
```