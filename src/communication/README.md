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
```az communication identity token issue --scope chat```.

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
##### Create-User #####
```
az communication identity user create
```
##### Delete-User #####
```
az communication identity user delete --user "8:acs:xxxxxx"
```
##### Issue-Access-Token #####
```
az communication identity token issue --scope chat

az communication identity token issue --scope chat voip --user "8:acs:xxxxxx"
```
##### Revoke-Access-Tokens #####
```
az communication identity token revoke --user "8:acs:xxxxxx"
```
##### Get-Token-For-Teams-User #####
```
az communication identity token get-for-teams-user --aad-token "MyAzureADToken" --client "MyAzureADAppId" --aad-user "MyTeamsUserId"
```
##### Send-SMS #####
```
az communication sms send --sender "+1833xxxxxxx" \
    --recipient "+1425xxxxxxx" "+1426xxxxxxx" "+1427xxxxxxx" --message "Hello there!!"
```
##### List-Phonenumbers #####
```
az communication phonenumber list
```
##### Show-Phonenumber #####
```
az communication phonenumber show --phonenumber "+1833xxxxxxx"
```
##### List-Threads #####
```
az communication chat thread list --start-time "2022-07-14T10:20:30"
```
##### Create-Thread #####
```
az communication chat thread create --topic "New Topic for Chat!" --idempotency-token "abc187xxxxxx"
```
##### Delete-Thread #####
```
az communication chat thread delete --thread "19:xxxxxx"
```
##### Update-Topic #####
```
az communication chat thread update-topic --thread "19:xxxxxx" --topic "New topic!"
```
##### List-Participants #####
```
az communication chat participant list --thread "19:xxxxxx" --skip "5"
```
##### Add-Participant #####
```
az communication chat participant add --thread "19:xxxxxx" --user "8:acs:xxxxxx" --display-name "John Doe" --start-time "2022-06-30T00:00:00"
```
##### Remove-Participant #####
```
az communication chat participant remove --thread "19:xxxxxx" --user "8:acs:xxxxxx" 
```
##### Send-Message #####
```
az communication chat message send --thread "19:xxxxxx" --display-name "John Doe" --content "Hello there!" --message-type "text"
```
##### List-Messages #####
```
az communication chat message list --thread "19:xxxxxx" --start-time "2022-07-14T10:20:30"
```
##### Get-Message #####
```
az communication chat message get --thread "19:xxxxxx" --message-id "1xxxxxxxxxxxx"
```
##### Update-Message #####
```
az communication chat message update --thread "19:xxxxxx" --message-id "1xxxxxxxxxxxx" --content "Hello there, again!"
```
##### Delete-Message #####
```
az communication chat message delete --thread "19:xxxxxx" --message-id "1xxxxxxxxxxxx"
```
##### List-Read-Receipts #####
```
az communication chat message receipt list --thread "19:xxxxxx" --skip "5"
```
##### Send-Read-Receipt #####
```
az communication chat message receipt send --thread "19:xxxxxx" --message-id "1xxxxxxxxxxxx"
```
##### Get-Room #####
```
az communication rooms get --room "roomId"
```
##### Create-Room #####
```
 az communication rooms create --valid-from "2023-03-31T10:20:30" --valid-to "2023-06-31T10:20:30" --presenter-participants "8:acs:xxxxxx" "8:acs:xxxxxx" --attendee-participants "8:acs:xxxxxx" "8:acs:xxxxxx" --consumer-participants "8:acs:xxxxxx" "8:acs:xxxxxx"
```
##### Update-Room #####
```
az communication rooms update --room "roomId" --valid-from "2023-03-31T10:20:30" --valid-to "2023-06-31T10:20:30"
```
##### Delete-Room #####
```
az communication rooms delete --room "roomId"
```
##### List-Rooms #####
```
az communication rooms list
```
##### Get-Room-Participants #####
```
az communication rooms participant get --room "roomId"
```
##### Add-Or-Update-Room-Participants #####
```
az communication rooms participant add-or-update --room "roomId" --presenter-participants "8:acs:xxxxxx" "8:acs:xxxxxx" --attendee-participants "8:acs:xxxxxx" "8:acs:xxxxxx" --consumer-participants "8:acs:xxxxxx" "8:acs:xxxxxx"
```
##### Remove-Room-Participants #####
```
az communication rooms participant remove --room "roomId" --participants "8:acs:xxxxxx" "8:acs:xxxxxx" "8:acs:xxxxxx" "8:acs:xxxxxx"
```
##### Send-Email #####
```
az communication email send --sender "NoReply@contoso.com" --subject "Contoso Update" --to "user1@user1-domain.com" "user2@user2-domain.com" --text "Hello valued client. There is an update."
```