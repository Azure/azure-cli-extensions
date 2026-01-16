# Azure CLI VM Repair Extension #
This is an extension for repairing VMs. Usually this is used to repair VMs that cannot boot by copying the 
OS Disk to a separate repair VM copy and run [repair scripts](https://github.com/Azure/repair-script-library) against it. 
VM Repair can also run repair scripts against the source VM itself.
You can also create then run your own custom repair scripts, seen in the `--custom-script-file` parameter in the `az vm repair run` command. 

### How to use ###
Install this extension using the below CLI command
```
az extension add --name vm-repair
```

### Sample Commands ###
Create repair VM command
```
az vm repair create -g MyResourceGroup -n myVM --verbose
```
Run a repair script on the new repair VM
```
az vm repair run -g MyResourceGroup -n MySourceWinVM --run-id win-hello-world --run-on-repair --verbose
```
Restore the now fixed copied OS disk from the repair VM to the original VM
```
az vm repair restore -g MyResourceGroup -n myVM --verbose
```
