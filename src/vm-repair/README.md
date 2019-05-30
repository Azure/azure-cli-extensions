# Azure CLI VM Repair Extension #
This is a extension for repairing VMs.

### How to use ###
Install this extension using the below CLI command
```
az extension add --name vm-repair
```

### Sample Commands ###
Repair create command
```
az vm repair create -g MyResourceGroup -n myVM --verbose
```
Restore command
```
az vm repair restore -g MyResourceGroup -n myVM --verbose
```