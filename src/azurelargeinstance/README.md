# Azure CLI Azurelargeinstance Extension #
This is an extension to Azure CLI to manage Azure Large Instance resources.

## Setup:
1. Install CLI first: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
2. Install the extension by running `az extension add -n azurelargeinstance`

## Usage Examples:
### Compute Operations
To create an Azure Large Instance
`az large-instance create -g $RESOURCE_GROUP -n $NAME --location westus2 --ali-id $UNIQUE_MACHINE_ID --hardware-profile "{hardware-type:Cisco_UCS,azure-large-instance-size:S72}" --storage-profile "{nfs-ip-address:00.000.000.00,os-disks:[{name:t250_sles_boot_vol,diskSizeGB:50}]}" --network-profile "{circuit-id:none,network-interfaces:[{ipAddress:10.0.61.31}]}" --os-profile "{computer-name:test,osType:'SLES 12 SP5',version:'12 SP5'}"`

To list Azure Large Instances in a subscription

`az large-instance list --subscription $SUBSCRIPTION_ID`

To list Azure Large Instances in a specific subscription and resource group

`az large-instance list --subscription $SUBSCRIPTION_ID --resource-group $RESOURCE_GROUP`

To restart an Azure Large Instance

`az large-instance restart --subscription $SUBSCRIPTION_ID --resource-group $RESOURCE_GROUP --instance-name $INSTANCE_NAME`

To show details about an Azure Large Instance

`az large-instance show --subscription $SUBSCRIPTION_ID --instance-name $INSTANCE_NAME --resource-group $RESOURCE_GROUP`

To shutdown an Azure Large Instance

`az large-instance shutdown --subscription $SUBSCRIPTION_ID --resource-group $RESOURCE_GROUP --instance-name $INSTANCE_NAME`

To start an Azure Large Instance

`az large-instance start --subscription $SUBSCRIPTION_ID --resource-group $RESOURCE_GROUP --instance-name $INSTANCE_NAME`

To add an Azure Large Instance tag

`az large-instance update --subscription $SUBSCRIPTION_ID --instance-name=$INSTANCE_NAME --resource-group=$RESOURCE_GROUP --tags newKey=value`

### Storage Operations
To create an Azure Large Storage Instance

`az arge-instance create -g $RESOURCE_GROUP -n $INSTANCE_NAME -l westus2 --alsi-id $UNIQUE_MACHINE_ID --storage-properties "{offering-type:EPIC,storage-type:FC,generation:Gen4.5,hardware-type:NetApp,workload-type:ODB,storage-billing-properties:{billing-mode:PAYG,sku:n10}}"`

To list Azure Large Storage Instances in a subscription

`az large-storage-instance list --subscription $SUBSCRIPTION_ID`

To list Azure Large Storage Instances in a specific subscription and resource group

`az large-storage-instance list --subscription $SUBSCRIPTIONID --resource-group $RESOURCE_GROUP`

To show details about a specific Azure Large Storage Instance

`az large-storage-instance show --subscription $SUBSCRIPTION_ID --instance-name $INSTANCE_NAME --resource-group $RESOURCE_GROUP`

To add an Azure Large Storage Instance tag

`az large-storage-instance update --subscription $SUBSCRIPTION_ID --instance-name $INSTANCE_NAME --resource-group $RESOURCE_GROUP --tags newKey=value`