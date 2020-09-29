# Azure CLI stack-hci Extension #
This package is for the 'stack-hci' extension, i.e. 'az stack-hci'

### How to use ###
Install this extension using the below CLI command
```
az extension add --name stack-hci
```

### Included Features
#### Stack HCI Management:
Manage Stack HCI: [more info](https://docs.microsoft.com/en-us/azure-stack/hci/) \
*Examples:*

##### Create an HCI cluster
```
az stack-hci cluster create \
    --location "East US" \
    --aad-client-id "24a6e53d-04e5-44d2-b7cc-1b732a847dfc" \
    --aad-tenant-id "7e589cc1-a8b6-4dff-91bd-5ec0fa18db94" \
    --name "myCluster" \
    --resource-group "test-rg"
```

##### Delete an HCI cluster
```
az stack-hci cluster delete --name "myCluster" --resource-group "test-rg"
```

##### List the HCI clusters
```
az stack-hci cluster list
```
```
az stack-hci cluster list --resource-group "test-rg"
```
```
az stack-hci cluster list --subscription "test-sub"
```

##### Get details about the specified HCI cluster
```
az stack-hci cluster show --name "myCluster" --resource-group "test-rg"
```

##### Update an HCI cluster
```
az stack-hci cluster update --tags tag1="value1" tag2="value2" --name "myCluster" --resource-group "test-rg"
```

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.
