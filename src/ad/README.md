# Azure CLI ad Extension #
This is the extension for ad

### How to use ###
Install this extension using the below CLI command
```
az extension add --name ad
```

### Included Features ###
#### ad ds ####
##### Create #####
```
az ad ds create --domain "TestDomainService.com" --ntlm-v1 "Enabled" --sync-ntlm-passwords "Enabled" \
    --tls-v1 "Disabled" --filtered-sync "Enabled" --external-access "Enabled" --ldaps "Enabled" \
    --pfx-certificate "MIIDPDCCAiSgAwIBAgIQQUI9P6tq2p9OFIJa7DLNvTANBgkqhkiG9w0BAQsFADAgMR4w..." \
    --pfx-certificate-password "<pfxCertificatePassword>" \
    --additional-recipients "jicha@microsoft.com" "caalmont@microsoft.com" --notify-dc-admins "Enabled" \
    --notify-global-admins "Enabled" \
    --replica-sets location="West US" subnet-id="/subscriptions/1639790a-76a2-4ac4-98d9-8562f5dfcb4d/resourceGroups/TestNetworkResourceGroup/providers/Microsoft.Network/virtualNetworks/TestVnetWUS/subnets/TestSubnetWUS" \
    --name "TestDomainService.com" --resource-group "TestResourceGroup" 

az ad ds wait --created --name "{myDomainService}" --resource-group "{rg}"
```
##### Show #####
```
az ad ds show --name "TestDomainService.com" --resource-group "TestResourceGroup"
```
##### List #####
```
az ad ds list --resource-group "TestResourceGroup"
```
##### Update #####
```
az ad ds update --ntlm-v1 "Enabled" --sync-ntlm-passwords "Enabled" --tls-v1 "Disabled" --filtered-sync "Enabled" \
    --external-access "Enabled" --ldaps "Enabled" \
    --pfx-certificate "MIIDPDCCAiSgAwIBAgIQQUI9P6tq2p9OFIJa7DLNvTANBgkqhkiG9w0BAQsFADAgMR4w..." \
    --pfx-certificate-password "<pfxCertificatePassword>" \
    --additional-recipients "jicha@microsoft.com" "caalmont@microsoft.com" --notify-dc-admins "Enabled" \
    --notify-global-admins "Enabled" \
    --replica-sets location="West US" subnet-id="/subscriptions/1639790a-76a2-4ac4-98d9-8562f5dfcb4d/resourceGroups/TestNetworkResourceGroup/providers/Microsoft.Network/virtualNetworks/TestVnetWUS/subnets/TestSubnetWUS" \
    --replica-sets location="East US" subnet-id="/subscriptions/1639790a-76a2-4ac4-98d9-8562f5dfcb4d/resourceGroups/TestNetworkResourceGroup/providers/Microsoft.Network/virtualNetworks/TestVnetEUS/subnets/TestSubnetEUS" \
    --name "TestDomainService.com" --resource-group "TestResourceGroup" 
```
##### Delete #####
```
az ad ds delete --name "TestDomainService.com" --resource-group "TestResourceGroup"
```