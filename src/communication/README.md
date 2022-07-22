# Azure CLI communication Extension #
This is the extension for communication

### How to use ###
Install this extension using the below CLI command
```
az extension add --name communication
```

Then set the `AZURE_COMMUNICATION_CONNECTION_STRING` environment variable with your ACS connection string.

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
##### Issue-Access-Token #####
```
az communication identity issue-access-token --scope chat

az communication identity issue-access-token --scope chat voip --userid "8:acs:xxxxxx"
```
##### Send-SMS #####
```
az communication sms send-sms --sender "+1833xxxxxxx" \
    --recipient "+1425xxxxxxx" "+1426xxxxxxx" "+1427xxxxxxx" --message "Hello there!!"
```
##### List-Phonenumbers #####
```
az communication phonenumbers list-phonenumbers
```
##### Show-Phonenumber #####
```
az communication phonenumbers show-phonenumber --phonenumber "+1833xxxxxxx"
```
