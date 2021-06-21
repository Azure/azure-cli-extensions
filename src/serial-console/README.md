# Azure CLI Serial Console Extension #
This is a extension for Serial Console Connections

### How to use ###
Install this extension using the below CLI command
```
az extension add --name serial-console
```

### Included Features ###
#### Connect to text-based Serial Console VM or VMSS Instance ####
```
az serial-console connect -n MyVM -g MyResourceGroup
```
#### Send a Non-Maskable Interrupt (NMI) to a VM or VMSS Instance ####
```
az serial-console send nmi -n MyVM -g MyResourceGroup
```
#### Send SysRq sequence to a VM or VMSS Instance ####
```
az serial-console send sysrq -n MyVM -g MyResourceGroup --input c
```
#### Perform a "hard" restart of the VM or VMSS Instance ####
```
az serial-console send reset -n MyVM -g MyResourceGroup
```