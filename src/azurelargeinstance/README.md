# Azure CLI Azurelargeinstance Extension #
This is an extension to Azure CLI to manage Azure Large Instance resources.

## Setup:
1. Install CLI first: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
2. Install the extension by running `az extension add -n azurelargeinstance`

## Usage Examples:
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

To list Azure Large Storage Instances in a subscription

`az large-storage-instance list --subscription $SUBSCRIPTION_ID`

To list Azure Large Storage Instances in a specific subscription and resource group

`az large-storage-instance list --subscription $SUBSCRIPTIONID --resource-group $RESOURCE_GROUP`

To show details about a specific Azure Large Storage Instance

`az large-storage-instance show --subscription $SUBSCRIPTION_ID --instance-name $INSTANCE_NAME --resource-group $RESOURCE_GROUP`

To add an Azure Large Storage Instance tag

`az large-storage-instance update --subscription $SUBSCRIPTION_ID --instance-name $INSTANCE_NAME --resource-group $RESOURCE_GROUP --tags newKey=value`