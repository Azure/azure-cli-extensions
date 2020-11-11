# Azure CLI databoxedge Extension #
This is the extension for databoxedge

### How to use ###
Install this extension using the below CLI command
```
az extension add --name databoxedge
```

### Included Features ###
#### databoxedge device ####
##### Create #####
```
az databoxedge device create --location "eastus" --sku name="Edge" tier="Standard" --name "testedgedevice" \
    --resource-group "GroupForEdgeAutomation" 
```
##### Show #####
```
az databoxedge device show --name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### List #####
```
az databoxedge device list --resource-group "GroupForEdgeAutomation"
```
##### Update #####
```
az databoxedge device update --name "testedgedevice" --tags Key1="value1" Key2="value2" \
    --resource-group "GroupForEdgeAutomation" 
```
##### Create-or-update-security-setting #####
```
az databoxedge device create-or-update-security-setting --name "testedgedevice" --resource-group "AzureVM" \
    --device-admin-password encryption-algorithm="AES256" encryption-cert-thumbprint="7DCBDFC44ED968D232C9A998FC105B5C70E84BE0" value="jJ5MvXa/AEWvwxviS92uCjatCXeyLYTy8jx/k105MjQRXT7i6Do8qpEcQ8d+OBbwmQTnwKW0CYyzzVRCc0uZcPCf6PsWtP4l6wvcKGAP66PwK68eEkTUOmp+wUHc4hk02kWmTWeAjBZkuDBP3xK1RnZo95g2RE4i1UgKNP5BEKCLd71O104DW3AWW41mh9XLWNOaxw+VjQY7wmvlE6XkvpkMhcGuha2u7lx8zi9ZkcMvJVYDYK36Fb/K3KhBAmDjjDmVq04jtBlcSTXQObt0nlj4BwGGtdrpeIpr67zqr5i3cPm6e6AleIaIhp6sI/uyGSMiT3oev2eg49u2ii7kVA==" 
```
##### Download-update #####
```
az databoxedge device download-update --name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### Get-extended-information #####
```
az databoxedge device get-extended-information --name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### Get-network-setting #####
```
az databoxedge device get-network-setting --name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### Get-update-summary #####
```
az databoxedge device get-update-summary --name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### Install-update #####
```
az databoxedge device install-update --name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### Scan-for-update #####
```
az databoxedge device scan-for-update --name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### Upload-certificate #####
```
az databoxedge device upload-certificate --name "testedgedevice" \
    --certificate "MIIC9DCCAdygAwIBAgIQWJae7GNjiI9Mcv/gJyrOPTANBgkqhkiG9w0BAQUFADASMRAwDgYDVQQDDAdXaW5kb3dzMB4XDTE4MTEyNzAwMTA0NVoXDTIxMTEyODAwMTA0NVowEjEQMA4GA1UEAwwHV2luZG93czCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAKxkRExqxf0qH1avnyORptIbRC2yQwqe3EIbJ2FPKr5jtAppGeX/dGKrFSnX+7/0HFr77aJHafdpEAtOiLyJ4zCAVs0obZCCIq4qJdmjYUTU0UXH/w/YzXfQA0d9Zh9AN+NJBX9xj05NzgsT24fkgsK2v6mWJQXT7YcWAsl5sEYPnx1e+MrupNyVSL/RUJmrS+etJSysHtFeWRhsUhVAs1DD5ExJvBLU3WH0IsojEvpXcjrutB5/MDQNrd/StGI6WovoSSPH7FyT9tgERx+q+Yg3YUGzfaIPCctlrRGehcdtzdNoKd0rsX62yCq0U6POoSfwe22NJu41oAUMd7e6R8cCAwEAAaNGMEQwEwYDVR0lBAwwCgYIKwYBBQUHAwIwHQYDVR0OBBYEFDd0VxnS3LnMIfwc7xW4b4IZWG5GMA4GA1UdDwEB/wQEAwIFIDANBgkqhkiG9w0BAQUFAAOCAQEAPQRby2u9celvtvL/DLEb5Vt3/tPStRQC5MyTD62L5RT/q8E6EMCXVZNkXF5WlWucLJi/18tY+9PNgP9xWLJh7kpSWlWdi9KPtwMqKDlEH8L2TnQdjimt9XuiCrTnoFy/1X2BGLY/rCaUJNSd15QCkz2xeW+Z+YSk2GwAc/A/4YfNpqSIMfNuPrT76o02VdD9WmJUA3fS/HY0sU9qgQRS/3F5/0EPS+HYQ0SvXCK9tggcCd4O050ytNBMJC9qMOJ7yE0iOrFfOJSCfDAuPhn/rHFh79Kn1moF+/CE+nc0/2RPiLC8r54/rt5dYyyxJDfXg0a3VrrX39W69WZGW5OXiw==" \
    --resource-group "GroupForEdgeAutomation" 
```
##### Delete #####
```
az databoxedge device delete --name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
#### databoxedge alert ####
##### List #####
```
az databoxedge alert list --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### Show #####
```
az databoxedge alert show --name "159a00c7-8543-4343-9435-263ac87df3bb" --device-name "testedgedevice" \
    --resource-group "GroupForEdgeAutomation" 
```
#### databoxedge bandwidth-schedule ####
##### Create #####
```
az databoxedge bandwidth-schedule create --name "bandwidth-1" --device-name "testedgedevice" --days "Sunday" \
    --days "Monday" --rate-in-mbps 100 --start "0:0:0" --stop "13:59:0" --resource-group "GroupForEdgeAutomation" 
```
##### Show #####
```
az databoxedge bandwidth-schedule show --name "bandwidth-1" --device-name "testedgedevice" \
    --resource-group "GroupForEdgeAutomation" 
```
##### List #####
```
az databoxedge bandwidth-schedule list --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### Delete #####
```
az databoxedge bandwidth-schedule delete --name "bandwidth-1" --device-name "testedgedevice" \
    --resource-group "GroupForEdgeAutomation" 
```
#### databoxedge job ####
##### Show #####
```
az databoxedge job show --name "159a00c7-8543-4343-9435-263ac87df3bb" --device-name "testedgedevice" \
    --resource-group "GroupForEdgeAutomation" 
```
#### databoxedge node ####
##### List #####
```
az databoxedge node list --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
#### databoxedge operation-status ####
##### Show #####
```
az databoxedge operation-status show --name "159a00c7-8543-4343-9435-263ac87df3bb" --device-name "testedgedevice" \
    --resource-group "GroupForEdgeAutomation" 
```
#### databoxedge order ####
##### Create #####
```
az databoxedge order create --device-name "testedgedevice" \
    --contact-information company-name="Microsoft" contact-person="John Mcclane" email-list="john@microsoft.com" phone="(800) 426-9400" \
    --shipping-address address-line1="Microsoft Corporation" address-line2="One Microsoft Way" address-line3="Redmond" city="WA" country="USA" postal-code="98052" state="WA" \
    --resource-group "GroupForEdgeAutomation" 
```
##### Show #####
```
az databoxedge order show --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### List #####
```
az databoxedge order list --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### Delete #####
```
az databoxedge order delete --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
#### databoxedge role ####
##### Create #####
```
az databoxedge role create --name "IoTRole1" --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation" \
    --role "{\\"kind\\":\\"IOT\\",\\"properties\\":{\\"hostPlatform\\":\\"Linux\\",\\"ioTDeviceDetails\\":{\\"authentication\\":{\\"symmetricKey\\":{\\"connectionString\\":{\\"encryptionAlgorithm\\":\\"AES256\\",\\"encryptionCertThumbprint\\":\\"348586569999244\\",\\"value\\":\\"Encrypted<<HostName=iothub.azure-devices.net;DeviceId=iotDevice;SharedAccessKey=2C750FscEas3JmQ8Bnui5yQWZPyml0/UiRt1bQwd8=>>\\"}}},\\"deviceId\\":\\"iotdevice\\",\\"ioTHostHub\\":\\"iothub.azure-devices.net\\"},\\"ioTEdgeDeviceDetails\\":{\\"authentication\\":{\\"symmetricKey\\":{\\"connectionString\\":{\\"encryptionAlgorithm\\":\\"AES256\\",\\"encryptionCertThumbprint\\":\\"1245475856069999244\\",\\"value\\":\\"Encrypted<<HostName=iothub.azure-devices.net;DeviceId=iotEdge;SharedAccessKey=2C750FscEas3JmQ8Bnui5yQWZPyml0/UiRt1bQwd8=>>\\"}}},\\"deviceId\\":\\"iotEdge\\",\\"ioTHostHub\\":\\"iothub.azure-devices.net\\"},\\"roleStatus\\":\\"Enabled\\",\\"shareMappings\\":[]}}" 
```
##### Show #####
```
az databoxedge role show --name "IoTRole1" --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### List #####
```
az databoxedge role list --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### Delete #####
```
az databoxedge role delete --name "IoTRole1" --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
#### databoxedge share ####
##### Create #####
```
az databoxedge share create --name "smbshare" --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation" \
    --description "" --access-protocol "SMB" \
    --azure-container-info container-name="testContainerSMB" data-format="BlockBlob" storage-account-credential-id="/subscriptions/4385cf00-2d3a-425a-832f-f4285b1c9dce/resourceGroups/GroupForEdgeAutomation/providers/Microsoft.DataBoxEdge/dataBoxEdgeDevices/testedgedevice/storageAccountCredentials/sac1" \
    --data-policy "Cloud" --monitoring-status "Enabled" --share-status "Online" \
    --user-access-rights access-type="Change" user-id="/subscriptions/4385cf00-2d3a-425a-832f-f4285b1c9dce/resourceGroups/GroupForEdgeAutomation/providers/Microsoft.DataBoxEdge/dataBoxEdgeDevices/testedgedevice/users/user2" 
```
##### Show #####
```
az databoxedge share show --name "smbshare" --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### List #####
```
az databoxedge share list --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### Refresh #####
```
az databoxedge share refresh --name "smbshare" --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### Delete #####
```
az databoxedge share delete --name "smbshare" --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
#### databoxedge storage-account-credentials ####
##### Create #####
```
az databoxedge storage-account-credentials create --name "sac1" --device-name "testedgedevice" \
    --resource-group "GroupForEdgeAutomation" \
    --account-key encryption-algorithm="AES256" encryption-cert-thumbprint="2A9D8D6BE51574B5461230AEF02F162C5F01AD31" value="lAeZEYi6rNP1/EyNaVUYmTSZEYyaIaWmwUsGwek0+xiZj54GM9Ue9/UA2ed/ClC03wuSit2XzM/cLRU5eYiFBwks23rGwiQOr3sruEL2a74EjPD050xYjA6M1I2hu/w2yjVHhn5j+DbXS4Xzi+rHHNZK3DgfDO3PkbECjPck+PbpSBjy9+6Mrjcld5DIZhUAeMlMHrFlg+WKRKB14o/og56u5/xX6WKlrMLEQ+y6E18dUwvWs2elTNoVO8PBE8SM/CfooX4AMNvaNdSObNBPdP+F6Lzc556nFNWXrBLRt0vC7s9qTiVRO4x/qCNaK/B4y7IqXMllwQFf4Np9UQ2ECA==" \
    --account-type "BlobStorage" --alias "sac1" --ssl-status "Disabled" --user-name "cisbvt" 
```
##### Show #####
```
az databoxedge storage-account-credentials show --name "sac1" --device-name "testedgedevice" \
    --resource-group "GroupForEdgeAutomation" 
```
##### List #####
```
az databoxedge storage-account-credentials list --device-name "testedgedevice" \
    --resource-group "GroupForEdgeAutomation" 
```
##### Delete #####
```
az databoxedge storage-account-credentials delete --name "sac1" --device-name "testedgedevice" \
    --resource-group "GroupForEdgeAutomation" 
```
#### databoxedge storage-account ####
##### Create #####
```
az databoxedge storage-account create --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation" \
    --description "It\'s an awesome storage account" --data-policy "Cloud" \
    --storage-account-credential-id "/subscriptions/4385cf00-2d3a-425a-832f-f4285b1c9dce/resourceGroups/GroupForDataBoxEdgeAutomation/providers/Microsoft.DataBoxEdge/dataBoxEdgeDevices/testedgedevice/storageAccountCredentials/cisbvt" \
    --storage-account-status "OK" --name "blobstorageaccount1" 
```
##### Show #####
```
az databoxedge storage-account show --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation" \
    --name "blobstorageaccount1" 
```
##### List #####
```
az databoxedge storage-account list --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### Delete #####
```
az databoxedge storage-account delete --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation" \
    --name "storageaccount1" 
```
#### databoxedge container ####
##### Create #####
```
az databoxedge container create --data-format "BlockBlob" --name "blobcontainer1" --device-name "testedgedevice" \
    --resource-group "GroupForEdgeAutomation" --storage-account-name "storageaccount1" 
```
##### Show #####
```
az databoxedge container show --name "blobcontainer1" --device-name "testedgedevice" \
    --resource-group "GroupForEdgeAutomation" --storage-account-name "storageaccount1" 
```
##### List #####
```
az databoxedge container list --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation" \
    --storage-account-name "storageaccount1" 
```
##### Refresh #####
```
az databoxedge container refresh --name "blobcontainer1" --device-name "testedgedevice" \
    --resource-group "GroupForEdgeAutomation" --storage-account-name "storageaccount1" 
```
##### Delete #####
```
az databoxedge container delete --name "blobcontainer1" --device-name "testedgedevice" \
    --resource-group "GroupForEdgeAutomation" --storage-account-name "storageaccount1" 
```
#### databoxedge trigger ####
##### Create #####
```
az databoxedge trigger create --name "trigger1" --device-name "testedgedevice" \
    --resource-group "GroupForEdgeAutomation" --file-event-trigger custom-context-tag="CustomContextTags-1235346475" 
```
##### Show #####
```
az databoxedge trigger show --name "trigger1" --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### List #####
```
az databoxedge trigger list --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### Delete #####
```
az databoxedge trigger delete --name "trigger1" --device-name "testedgedevice" \
    --resource-group "GroupForEdgeAutomation" 
```
#### databoxedge user ####
##### Create #####
```
az databoxedge user create --name "user1" --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation" \
    --encrypted-password encryption-algorithm="None" encryption-cert-thumbprint="blah" value="Password@1" \
    --user-type "Share" 
```
##### Show #####
```
az databoxedge user show --name "user1" --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### List #####
```
az databoxedge user list --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### Delete #####
```
az databoxedge user delete --name "user1" --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
#### databoxedge sku ####
##### List #####
```
az databoxedge sku list
```