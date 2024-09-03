# Azure CLI BaremetalInfrastructure Extension #
This is an extension to Azure CLI to manage BaremetalInfrastructure resources.

# Install

To install this extension just use the CLI extension add command:

```
az extension add baremetal-infrastructure
```

# Usage

To create a BareMetal instance:

```
az baremetalinstance create --resource-group $RESOURCE_GROUP --instance-name $BM_INSTANCE_NAME --location $LOCATION --sku $SKU --tags key1=value1 key2=value2
```

To delete a BareMetal instance:

```
az baremetalinstance delete --resource-group $RESOURCE_GROUP --instance-name $BM_INSTANCE_NAME
```

To list all BareMetal instances for the subscription:

```
az baremetalinstance list
```

To show details about a specific BareMetal instance:

```
az baremetalinstance show --resource-group $RESOURCE_GROUP --instance-name $BM_INSTANCE_NAME
```

To add a key-value pair to the Tags field of a specific BareMetal instance:

```
az baremetalinstance update --resource-group $RESOURCE_GROUP --instance-name $BM_INSTANCE_NAME --set tags.newKey=value
```

To update a key-value pair in the Tags field of a specific BareMetal instance:

```
az baremetalinstance update --resource-group $RESOURCE_GROUP --instance-name $BM_INSTANCE_NAME --set tags.key=updatedValue
```

To delete a key-value pair from the Tags field of a specific BareMetal instance:

```
az baremetalinstance update --resource-group $RESOURCE_GROUP --instance-name $BM_INSTANCE_NAME --remove tags.key
```

To delete all key-value pairs in the Tags field of a specific BareMetal instance:

```
az baremetalinstance update --resource-group $RESOURCE_GROUP --instance-name $BM_INSTANCE_NAME --set tags={}
```

To delete a BareMetal instance:

```
az baremetalinstance delete --resource-group $RESOURCE_GROUP --instance-name $BM_INSTANCE_NAME
```

To start a specific BareMetal instance:

```
az baremetalinstance start --resource-group $RESOURCE_GROUP --instance-name $BM_INSTANCE_NAME
```

To restart a specific BareMetal instance:

```
az baremetalinstance restart --resource-group $RESOURCE_GROUP --instance-name $BM_INSTANCE_NAME
```

To force restart a specific BareMetal instance:

```
az baremetalinstance restart --resource-group $RESOURCE_GROUP --instance-name $BM_INSTANCE_NAME --force
```

To shutdown a specific BareMetal instance:

```
az baremetalinstance shutdown --resource-group $RESOURCE_GROUP --instance-name $BM_INSTANCE_NAME
```