# Azure CLI communication Extension #
This is the extension for communication

### How to use ###
Install this extension using the below CLI command
```
az extension add --name communication
```

### Included Features ###

##### Create #####
```
az communication create --name "MyCommunicationResource" --location "Global" \
    --data-location "United States" --resource-group "MyResourceGroup"

az communication wait --created --name "{myCommunicationService}" --resource-group "{rg}"
```
##### Show #####
```
az communication show --name "MyCommunicationResource" --resource-group "MyResourceGroup"
```
##### List #####
```
az communication list --resource-group "MyResourceGroup"
```
##### Update #####
```
az communication update --name "MyCommunicationResource" --tags newTag="newVal" \
    --resource-group "MyResourceGroup"
```
##### Link-notification-hub #####
```
az communication link-notification-hub --name "MyCommunicationResource" \
    --connection-string "Endpoint=sb://MyNamespace.servicebus.windows.net/;SharedAccessKey=abcd1234" \
    --resource-id "/subscriptions/12345/resourceGroups/MyOtherResourceGroup/providers/Microsoft.NotificationHubs/namespaces/MyNamespace/notificationHubs/MyHub" \
    --resource-group "MyResourceGroup"
```
##### List-key #####
```
az communication list-key --name "MyCommunicationResource" --resource-group "MyResourceGroup"
```
##### Regenerate-key #####
```
az communication regenerate-key --name "MyCommunicationResource" --key-type "Primary" \
    --resource-group "MyResourceGroup"
```
##### Delete #####
```
az communication delete --name "MyCommunicationResource" --resource-group "MyResourceGroup"
```
##### Show-status #####
```
az communication show-status --operation-id "db5f291f-284d-46e9-9152-d5c83f7c14b8" --location "westus2"
```
