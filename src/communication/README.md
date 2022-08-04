# Azure CLI communication Extension #
This is the extension for communication

### How to use ###
Install this extension using the below CLI command
```
az extension add --name communication
```

Then set the `AZURE_COMMUNICATION_CONNECTION_STRING` environment variable with your ACS connection string.

For chat module, set both `AZURE_COMMUNICAITON_ENDPOINT` and `AZURE_COMMUNICATION_ACCESS_TOKEN` environment variables.
You can find your endpoint from your in Azure Portal under your communication resource, and an access token can be created with 
```az communication identity issue-access-token --scope chat```.

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
##### Revoke-Access-Tokens #####
```
az communication identity revoke-access-tokens --userid "8:acs:xxxxxx"

az communication identity revoke-access-tokens --userid "8:acs:xxxxxx" "8:acs:xxxxxy" "8:acs:xxxxxz"
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
##### List-Threads #####
```
az communication chat list-threads --start-time "2022-07-14T10:20:30"
```
##### Create-Thread #####
```
az communication chat create-thread --topic "New Topic for Chat!" --idempotency-token "abc187xxxxxx"
```
##### Delete-Thread #####
```
az communication chat delete-thread --thread-id "19:xxxxxx"
```
##### List-Participants #####
```
az communication chat list-participants --thread-id "19:xxxxxx" --skip "5"
```
##### Add-Participant #####
```
az communication chat add-participant --thread-id "19:xxxxxx" --user-id "8:acs:xxxxxx" --display-name "John Doe" --start-time "2022-06-30T00:00:00"
```
##### Remove-Participant #####
```
az communication chat remove-participant --thread-id "19:xxxxxx" --user-id "8:acs:xxxxxx" 
```
##### Send-Message #####
```
az communication chat send-message --thread-id "19:xxxxxx" --display-name "John Doe" --content "Hello there!" --message-type "text"
```
##### List-Messages #####
```
az communication chat list-messages --thread-id "19:xxxxxx" --start-time "2022-07-14T10:20:30"
```
##### Get-Message #####
```
az communication chat get-message --thread-id "19:xxxxxx" --message-id "1xxxxxxxxxxxx"
```
##### Update-Message #####
```
az communication chat update-message --thread-id "19:xxxxxx" --message-id "1xxxxxxxxxxxx" --message_content "Hello there, again!"
```
##### Delete-Message #####
```
az communication chat delete-message --thread-id "19:xxxxxx" --message-id "1xxxxxxxxxxxx"
```
##### Update Topic #####
```
az communication chat update-topic --thread-id "19:xxxxxx" --topic "New topic!"
```
##### List-Read-Receipts #####
```
az communication chat list-read-receipts --thread-id "19:xxxxxx" --skip "5"
```
##### Send-Read-Receipt #####
```
az communication chat send-read-receipt --thread-id "19:xxxxxx" --message-id "1xxxxxxxxxxxx"
```
