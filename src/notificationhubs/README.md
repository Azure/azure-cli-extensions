# Azure CLI notificationhubs Extension #
This package is for the 'notificationhubs' extension, i.e. 'az notificationhubs'.

### How to use ###
Install this extension using the below CLI command
```
az extension add --name notificationhubs
```

### Included Features
#### Notification Hubs Management:
Manage Notification Hubs and namespaces: [more info](https://docs.microsoft.com/azure/notification-hubs)\
*Examples:*

##### Create a Notification Hub Namespace

```
az notificationhubs namespace create \
    --resource-group groupName \
    --name spaceName \
    --location localtionName \
    --sku "Basic"
```

##### Create a Notification Hub
```
az notificationhubs create \
    --resource-group groupName \
    --namespace-name spaceName \
    --name hubName \
    --location "South Central US" \
    --name "Basic"
```

##### Create a Notification Hub authorization rule
```
az notificationhubs authorization-rule create \
    --resource-group groupName \
    --namespace-name spaceName \
    --notification-hub-name hubName \
    --name ruleName \
    --rights "Listen"
```

##### List Notification Hub policy keys
```
az notificationhubs authorization-rule list-keys \
    --resource-group groupName \
    --namespace-name spaceName \
    --notification-hub-name hubName \
    --name ruleName
```

##### Update Android push API key
```
az notificationhubs credential gcm update \
    --resource-group groupName \
    --namespace-name spaceName \
    --notification-hub-name hubName \
    --google-api-key keyValue
```

##### Test sending message to Android devices
You may want to follow the [instructions](https://docs.microsoft.com/en-us/azure/notification-hubs/notification-hubs-android-push-notification-google-fcm-get-started) to set up an Android App to receive notifications.

```
az notificationhubs test-send \
    --resource-group groupName \
    --namespace-name spaceName \
    --notification-hub-name hubName \
    --notification-format gcm \
    --payload "{\"data\":{\"message\":\"test notification\"}}"
```
or
```
az notificationhubs test-send \
    --resource-group groupName \
    --namespace-name spaceName \
    --notification-hub-name hubName \
    --notification-format gcm \
    --payload @/path/to/json/file
```

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.
