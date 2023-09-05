# Azure CLI stack-hci-vm Extension

This is the extension for stack-hci-vm

### How to use

Install this extension using the below CLI command

```
az extension add --name stack-hci-vm
```

### Included Features

#### stack-hci-vm arc-setting

##### Create

```
az stack-hci-vm arc-setting create --name "default" --cluster-name "myCluster" --resource-group "test-rg"
```

##### Show

```
az stack-hci-vm arc-setting show --name "default" --cluster-name "myCluster" --resource-group "test-rg"
```

##### List

```
az stack-hci-vm arc-setting list --cluster-name "myCluster" --resource-group "test-rg"
```

##### Update

```
az stack-hci-vm arc-setting update --connectivity-properties "{\\"enabled\\":true}" --name "default" \
    --cluster-name "myCluster" --resource-group "test-rg"
```

##### Create-identity

```
az stack-hci-vm arc-setting create-identity --name "default" --cluster-name "myCluster" --resource-group "test-rg"
```

##### Generate-password

```
az stack-hci-vm arc-setting generate-password --name "default" --cluster-name "myCluster" --resource-group "test-rg"
```

##### Delete

```
az stack-hci-vm arc-setting delete --name "default" --cluster-name "myCluster" --resource-group "test-rg"
```

#### stack-hci-vm cluster

##### Create

```
az stack-hci-vm cluster create --location "East US" --aad-client-id "24a6e53d-04e5-44d2-b7cc-1b732a847dfc" \
    --aad-tenant-id "7e589cc1-a8b6-4dff-91bd-5ec0fa18db94" \
    --endpoint "https://98294836-31be-4668-aeae-698667faf99b.waconazure.com" --name "myCluster" \
    --resource-group "test-rg"
```

##### Show

```
az stack-hci-vm cluster show --name "myCluster" --resource-group "test-rg"
```

##### List

```
az stack-hci-vm cluster list --resource-group "test-rg"
```

##### Update

```
az stack-hci-vm cluster update --endpoint "https://98294836-31be-4668-aeae-698667faf99b.waconazure.com" \
    --desired-properties diagnostic-level="Basic" windows-server-subscription="Enabled" \
    --tags tag1="value1" tag2="value2" --name "myCluster" --resource-group "test-rg"
```

##### Create-identity

```
az stack-hci-vm cluster create-identity --name "myCluster" --resource-group "test-rg"
```

##### Delete

```
az stack-hci-vm cluster delete --name "myCluster" --resource-group "test-rg"
```

#### stack-hci-vm extension

##### Create

```
az stack-hci-vm extension create --arc-setting-name "default" --cluster-name "myCluster" \
    --type "MicrosoftMonitoringAgent" --protected-settings "{\\"workspaceKey\\":\\"xx\\"}" \
    --publisher "Microsoft.Compute" --settings "{\\"workspaceId\\":\\"xx\\"}" --type-handler-version "1.10" \
    --name "MicrosoftMonitoringAgent" --resource-group "test-rg"

az stack-hci-vm extension wait --created --arc-setting-name "{myArcSetting}" --cluster-name "{myCluster}" \
    --name "{myExtension}" --resource-group "{rg}"
```

##### Show

```
az stack-hci-vm extension show --arc-setting-name "default" --cluster-name "myCluster" --name "MicrosoftMonitoringAgent" \
    --resource-group "test-rg"
```

##### List

```
az stack-hci-vm extension list --arc-setting-name "default" --cluster-name "myCluster" --resource-group "test-rg"
```

##### Delete

```
az stack-hci-vm extension delete --arc-setting-name "default" --cluster-name "myCluster" \
    --name "MicrosoftMonitoringAgent" --resource-group "test-rg"
```
