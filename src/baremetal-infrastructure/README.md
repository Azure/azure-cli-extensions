# Azure CLI BaremetalInfrastructure Extension #

This is an extension to Azure CLI to manage BaremetalInfrastructure resources.

# Install

To install this extension just use the CLI extension add command:

```
az extension add baremetal-infrastructure
```

# Usage

## Compute Operations

To create a BareMetal instance:

```bash
az baremetalinstance create -g $RESOURCE_GROUP -n $BM_INSTANCE_NAME -l $LOCATION --sku $SKU
```

To delete a BareMetal instance:

```bash
az baremetalinstance delete --resource-group $RESOURCE_GROUP --instance-name $BM_INSTANCE_NAME
```

To list all BareMetal instances for the subscription:

```bash
az baremetalinstance list
```

To show details about a specific BareMetal instance:

```bash
az baremetalinstance show --resource-group $RESOURCE_GROUP --instance-name $BM_INSTANCE_NAME
```

To add a key-value pair to the Tags field of a specific BareMetal instance:

```bash
az baremetalinstance update --resource-group $RESOURCE_GROUP --instance-name $BM_INSTANCE_NAME --set tags.newKey=value
```

To update a key-value pair in the Tags field of a specific BareMetal instance:

```bash
az baremetalinstance update --resource-group $RESOURCE_GROUP --instance-name $BM_INSTANCE_NAME --set tags.key=updatedValue
```

To delete a key-value pair from the Tags field of a specific BareMetal instance:

```bash
az baremetalinstance update --resource-group $RESOURCE_GROUP --instance-name $BM_INSTANCE_NAME --remove tags.key
```

To delete all key-value pairs in the Tags field of a specific BareMetal instance:

```bash
az baremetalinstance update --resource-group $RESOURCE_GROUP --instance-name $BM_INSTANCE_NAME --set tags={}
```

To delete a BareMetal instance:

```bash
az baremetalinstance delete --resource-group $RESOURCE_GROUP --instance-name $BM_INSTANCE_NAME
```

To start a specific BareMetal instance:

```bash
az baremetalinstance start --resource-group $RESOURCE_GROUP --instance-name $BM_INSTANCE_NAME
```

To restart a specific BareMetal instance:

```bash
az baremetalinstance restart --resource-group $RESOURCE_GROUP --instance-name $BM_INSTANCE_NAME
```

To force restart a specific BareMetal instance:

```bash
az baremetalinstance restart --resource-group $RESOURCE_GROUP --instance-name $BM_INSTANCE_NAME --force
```

To shutdown a specific BareMetal instance:

```bash
az baremetalinstance shutdown --resource-group $RESOURCE_GROUP --instance-name $BM_INSTANCE_NAME
```

## Storage Operations

To create a BareMetal Storage instance:

```bash
az baremetalstorageinstance create -g myResourceGroup -n myAzureBareMetalStorageInstance -l westus2 --sku S72
```

To delete a BareMetal Storage instance:

```bash
az baremetalstorageinstance delete --resource-group $RESOURCE_GROUP --instance-name $BM_STORAGE_INSTANCE_NAME
```

To list all BareMetal Storage instances for the subscription:

```bash
az baremetalstorageinstance list
```

To list all BareMetal Storage instances for a specific subscription and resource group:

```bash
az baremetalstorageinstance list -g myResourceGroup
```

To show details about a specific BareMetal Storage instance:

```bash
az baremetalstorageinstance show -g $RESOURCE_GROUP -n $BM_STORAGE_INSTANCE_NAME
```
