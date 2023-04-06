# Azure CLI dns-resolver Extension #
This is the extension for dns-resolver

### How to use ###
Install this extension using the below CLI command
```
az extension add --name dns-resolver
```

### Included Features ###
#### dns-resolver ####
##### Create #####
```
az dns-resolver create --name "sampleDnsResolver" --location "westus2" \
    --id "/subscriptions/cbb1387e-4b03-44f2-ad41-58d4677b9873/resourceGroups/virtualNetworkResourceGroup/providers/Microsoft.Network/virtualNetworks/sampleVirtualNetwork" \
    --tags key1="value1" --resource-group "sampleResourceGroup" 

az dns-resolver wait --created --name "{myDnsResolver}" --resource-group "{rg}"
```
##### Show #####
```
az dns-resolver show --name "sampleDnsResolver" --resource-group "sampleResourceGroup"
```
##### List #####
```
az dns-resolver list --resource-group "sampleResourceGroup"
```
##### Update #####
```
az dns-resolver update --name "sampleDnsResolver" --tags key1="value1" --resource-group "sampleResourceGroup"
```
##### Delete #####
```
az dns-resolver delete --name "sampleDnsResolver" --resource-group "sampleResourceGroup"
```
#### dns-resolver inbound-endpoint ####
##### Create #####
```
az dns-resolver inbound-endpoint create --dns-resolver-name "sampleDnsResolver" --name "sampleInboundEndpoint" \
    --location "westus2" \
    --ip-configurations "[{private-ip-address:'',private-ip-allocation-method:Dynamic,id:/subscriptions/0403cfa9-9659-4f33-9f30-1f191c51d111/resourceGroups/sampleVnetResourceGroupName/providers/Microsoft.Network/virtualNetworks/sampleVirtualNetwork/subnets/sampleSubnet}]" \
    --tags key1="value1" --resource-group "sampleResourceGroup" 

az dns-resolver inbound-endpoint wait --created --dns-resolver-name "{myDnsResolver}" --name "{myInboundEndpoint}" \
    --resource-group "{rg}" 
```
##### Show #####
```
az dns-resolver inbound-endpoint show --dns-resolver-name "sampleDnsResolver" --name "sampleInboundEndpoint" \
    --resource-group "sampleResourceGroup" 
```
##### List #####
```
az dns-resolver inbound-endpoint list --dns-resolver-name "sampleDnsResolver" --resource-group "sampleResourceGroup"
```
##### Update #####
```
az dns-resolver inbound-endpoint update --dns-resolver-name "sampleDnsResolver" --name "sampleInboundEndpoint" \
    --tags key1="value1" --resource-group "sampleResourceGroup" 
```
##### Delete #####
```
az dns-resolver inbound-endpoint delete --dns-resolver-name "sampleDnsResolver" --name "sampleInboundEndpoint" \
    --resource-group "sampleResourceGroup" 
```
#### dns-resolver outbound-endpoint ####
##### Create #####
```
az dns-resolver outbound-endpoint create --dns-resolver-name "sampleDnsResolver" --name "sampleOutboundEndpoint" \
    --location "westus2" \
    --id "/subscriptions/0403cfa9-9659-4f33-9f30-1f191c51d111/resourceGroups/sampleVnetResourceGroupName/providers/Microsoft.Network/virtualNetworks/sampleVirtualNetwork/subnets/sampleSubnet" \
    --tags key1="value1" --resource-group "sampleResourceGroup" 

az dns-resolver outbound-endpoint wait --created --dns-resolver-name "{myDnsResolver}" --name "{myOutboundEndpoint}" \
    --resource-group "{rg}" 
```
##### Show #####
```
az dns-resolver outbound-endpoint show --dns-resolver-name "sampleDnsResolver" --name "sampleOutboundEndpoint" \
    --resource-group "sampleResourceGroup" 
```
##### List #####
```
az dns-resolver outbound-endpoint list --dns-resolver-name "sampleDnsResolver" --resource-group "sampleResourceGroup"
```
##### Update #####
```
az dns-resolver outbound-endpoint update --dns-resolver-name "sampleDnsResolver" --name "sampleOutboundEndpoint" \
    --tags key1="value1" --resource-group "sampleResourceGroup" 
```
##### Delete #####
```
az dns-resolver outbound-endpoint delete --dns-resolver-name "sampleDnsResolver" --name "sampleOutboundEndpoint" \
    --resource-group "sampleResourceGroup" 
```
#### dns-resolver forwarding-ruleset ####
##### Create #####
```
az dns-resolver forwarding-ruleset create --name "samplednsForwardingRuleset" --location "westus2" \
    --outbound-endpoints id="/subscriptions/abdd4249-9f34-4cc6-8e42-c2e32110603e/resourceGroups/sampleResourceGroup/providers/Microsoft.Network/dnsResolvers/sampleDnsResolver/outboundEndpoints/sampleOutboundEndpoint0" \
    --outbound-endpoints id="/subscriptions/abdd4249-9f34-4cc6-8e42-c2e32110603e/resourceGroups/sampleResourceGroup/providers/Microsoft.Network/dnsResolvers/sampleDnsResolver/outboundEndpoints/sampleOutboundEndpoint1" \
    --tags key1="value1" --resource-group "sampleResourceGroup" 

az dns-resolver forwarding-ruleset wait --created --name "{myDnsForwardingRuleset2}" --resource-group "{rg}"
```
##### Show #####
```
az dns-resolver forwarding-ruleset show --name "sampleDnsForwardingRuleset" --resource-group "sampleResourceGroup"
```
##### List #####
```
az dns-resolver forwarding-ruleset list --resource-group "sampleResourceGroup"
```
##### Update #####
```
az dns-resolver forwarding-ruleset update --name "sampleDnsForwardingRuleset" --tags key1="value1" \
    --resource-group "sampleResourceGroup" 
```
##### Delete #####
```
az dns-resolver forwarding-ruleset delete --name "samplednsForwardingRulesetName" \
    --resource-group "sampleResourceGroup" 
```
#### dns-resolver forwarding-rule ####
##### Create #####
```
az dns-resolver forwarding-rule create --ruleset-name "sampleDnsForwardingRuleset" \
    --name "sampleForwardingRule" --domain-name "contoso.com." --forwarding-rule-state "Enabled" \
    --metadata additionalProp1="value1" --target-dns-servers ip-address="10.0.0.1" port=53 \
    --target-dns-servers ip-address="10.0.0.2" port=53 --resource-group "sampleResourceGroup" 
```
##### Show #####
```
az dns-resolver forwarding-rule show --ruleset-name "sampleDnsForwardingRuleset" \
    --name "sampleForwardingRule" --resource-group "sampleResourceGroup" 
```
##### List #####
```
az dns-resolver forwarding-rule list --ruleset-name "sampleDnsForwardingRuleset" \
    --resource-group "sampleResourceGroup" 
```
##### Update #####
```
az dns-resolver forwarding-rule update --ruleset-name "sampleDnsForwardingRuleset" \
    --name "sampleForwardingRule" --forwarding-rule-state "Disabled" --metadata additionalProp2="value2" \
    --resource-group "sampleResourceGroup" 
```
##### Delete #####
```
az dns-resolver forwarding-rule delete --ruleset-name "sampleDnsForwardingRuleset" \
    --name "sampleForwardingRule" --resource-group "sampleResourceGroup" 
```
#### dns-resolver virtual-network-link ####
##### Create #####
```
az dns-resolver vnet-link create --ruleset-name "sampleDnsForwardingRuleset" \
    --metadata additionalProp1="value1" \
    --id "/subscriptions/0403cfa9-9659-4f33-9f30-1f191c51d111/resourceGroups/sampleVnetResourceGroupName/providers/Microsoft.Network/virtualNetworks/sampleVirtualNetwork" \
    --resource-group "sampleResourceGroup" --name "sampleVirtualNetworkLink" 

az dns-resolver vnet-link wait --created --ruleset-name "{myDnsForwardingRuleset}" \
    --resource-group "{rg}" --name "{myVirtualNetworkLink}" 
```
##### Show #####
```
az dns-resolver vnet-link show --ruleset-name "sampleDnsForwardingRuleset" \
    --resource-group "sampleResourceGroup" --name "sampleVirtualNetworkLink" 
```
##### List #####
```
az dns-resolver vnet-link list --ruleset-name "sampleDnsForwardingRuleset" \
    --resource-group "sampleResourceGroup" 
```
##### Update #####
```
az dns-resolver vnet-link update --ruleset-name "sampleDnsForwardingRuleset" \
    --metadata additionalProp1="value1" --resource-group "sampleResourceGroup" --name "sampleVirtualNetworkLink" 
```
##### Delete #####
```
az dns-resolver vnet-link delete --ruleset-name "sampleDnsForwardingRuleset" \
    --resource-group "sampleResourceGroup" --name "sampleVirtualNetworkLink" 
```