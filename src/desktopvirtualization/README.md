# Azure CLI Desktop Virtualization Extension #
This is a extension for desktop virtualization features.

### How to use ###
Install this extension using the below CLI command
```
az extension add --name desktopvirtualization
```

### Included Features
The desktop virtualization is a desktop and app virtualization service that runs on the cloud. [more info](https://docs.microsoft.com/en-us/azure/virtual-desktop/overview)
#### Host Pool:
Host pools are a collection of one or more identical virtual machines (VMs) within Windows Virtual Desktop environments: [more info](https://docs.microsoft.com/en-us/azure/virtual-desktop/create-host-pools-azure-marketplace)\
*Examples:*
```
az desktopvirtualization hostpool create \
    --location "centralus" \
    --description "des1" \
    --friendly-name "friendly" \
    --host-pool-type "Pooled" \
    --load-balancer-type "BreadthFirst" \
    --max-session-limit 999999 \
    --personal-desktop-assignment-type "Automatic" \
    --registration-info expiration-time="2020-10-01T14:01:54.9571247Z" registration-token-operation="Update" \
    --sso-context "KeyVaultPath" \
    --tags tag1="value1" tag2="value2" \
    --name "MyHostPool" \
    --resource-group "MyResourceGroup"
```

#### Application Group:
Each host pool can contain an application group that users can interact with as they would on a physical desktop: [more info](https://docs.microsoft.com/en-us/azure/virtual-desktop/manage-app-groups)\
*Examples:*
```
az desktopvirtualization applicationgroup create \
    --location "centralus" \
    --description "des1" \
    --application-group-type "RemoteApp" \
    --friendly-name "friendly" \
    --host-pool-arm-path "/subscriptions/daefabc0-95b4-48b3-b645-8a753a63c4fa/resourceGroups/MyResourceGroup/providers/Microsoft.DesktopVirtualization/hostPools/MyHostPool" \
    --tags tag1="value1" tag2="value2" \
    --name "MyApplicationGroup" \
    --resource-group "MyResourceGroup"
```

#### Workspace:
An application group can be registered to a workspace: [more info](https://docs.microsoft.com/en-us/azure/virtual-desktop/create-validation-host-pool)\
*Examples:*
```
az desktopvirtualization workspace create \
    --resource-group "MyResourceGroup" \
    --location "centralus" \
    --description "des1" \
    --friendly-name "friendly" \
    --tags tag1="value1" tag2="value2" \
    --name "MyWorkspace"
```

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.