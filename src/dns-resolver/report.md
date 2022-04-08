# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az dns-resolver|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az dns-resolver` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az dns-resolver|DnsResolvers|[commands](#CommandsInDnsResolvers)|
|az dns-resolver dns-forwarding-ruleset|DnsForwardingRulesets|[commands](#CommandsInDnsForwardingRulesets)|
|az dns-resolver forwarding-rule|ForwardingRules|[commands](#CommandsInForwardingRules)|
|az dns-resolver inbound-endpoint|InboundEndpoints|[commands](#CommandsInInboundEndpoints)|
|az dns-resolver outbound-endpoint|OutboundEndpoints|[commands](#CommandsInOutboundEndpoints)|
|az dns-resolver virtual-network-link|VirtualNetworkLinks|[commands](#CommandsInVirtualNetworkLinks)|

## COMMANDS
### <a name="CommandsInDnsResolvers">Commands in `az dns-resolver` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az dns-resolver list](#DnsResolversListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersDnsResolversListByResourceGroup)|[Example](#ExamplesDnsResolversListByResourceGroup)|
|[az dns-resolver list](#DnsResolversList)|List|[Parameters](#ParametersDnsResolversList)|[Example](#ExamplesDnsResolversList)|
|[az dns-resolver show](#DnsResolversGet)|Get|[Parameters](#ParametersDnsResolversGet)|[Example](#ExamplesDnsResolversGet)|
|[az dns-resolver create](#DnsResolversCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersDnsResolversCreateOrUpdate#Create)|[Example](#ExamplesDnsResolversCreateOrUpdate#Create)|
|[az dns-resolver update](#DnsResolversUpdate)|Update|[Parameters](#ParametersDnsResolversUpdate)|[Example](#ExamplesDnsResolversUpdate)|
|[az dns-resolver delete](#DnsResolversDelete)|Delete|[Parameters](#ParametersDnsResolversDelete)|[Example](#ExamplesDnsResolversDelete)|
|[az dns-resolver list-by-virtual-network](#DnsResolversListByVirtualNetwork)|ListByVirtualNetwork|[Parameters](#ParametersDnsResolversListByVirtualNetwork)|[Example](#ExamplesDnsResolversListByVirtualNetwork)|

### <a name="CommandsInDnsForwardingRulesets">Commands in `az dns-resolver dns-forwarding-ruleset` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az dns-resolver dns-forwarding-ruleset list](#DnsForwardingRulesetsListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersDnsForwardingRulesetsListByResourceGroup)|[Example](#ExamplesDnsForwardingRulesetsListByResourceGroup)|
|[az dns-resolver dns-forwarding-ruleset list](#DnsForwardingRulesetsList)|List|[Parameters](#ParametersDnsForwardingRulesetsList)|[Example](#ExamplesDnsForwardingRulesetsList)|
|[az dns-resolver dns-forwarding-ruleset show](#DnsForwardingRulesetsGet)|Get|[Parameters](#ParametersDnsForwardingRulesetsGet)|[Example](#ExamplesDnsForwardingRulesetsGet)|
|[az dns-resolver dns-forwarding-ruleset create](#DnsForwardingRulesetsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersDnsForwardingRulesetsCreateOrUpdate#Create)|[Example](#ExamplesDnsForwardingRulesetsCreateOrUpdate#Create)|
|[az dns-resolver dns-forwarding-ruleset update](#DnsForwardingRulesetsUpdate)|Update|[Parameters](#ParametersDnsForwardingRulesetsUpdate)|[Example](#ExamplesDnsForwardingRulesetsUpdate)|
|[az dns-resolver dns-forwarding-ruleset delete](#DnsForwardingRulesetsDelete)|Delete|[Parameters](#ParametersDnsForwardingRulesetsDelete)|[Example](#ExamplesDnsForwardingRulesetsDelete)|
|[az dns-resolver dns-forwarding-ruleset list-by-virtual-network](#DnsForwardingRulesetsListByVirtualNetwork)|ListByVirtualNetwork|[Parameters](#ParametersDnsForwardingRulesetsListByVirtualNetwork)|[Example](#ExamplesDnsForwardingRulesetsListByVirtualNetwork)|

### <a name="CommandsInForwardingRules">Commands in `az dns-resolver forwarding-rule` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az dns-resolver forwarding-rule list](#ForwardingRulesList)|List|[Parameters](#ParametersForwardingRulesList)|[Example](#ExamplesForwardingRulesList)|
|[az dns-resolver forwarding-rule show](#ForwardingRulesGet)|Get|[Parameters](#ParametersForwardingRulesGet)|[Example](#ExamplesForwardingRulesGet)|
|[az dns-resolver forwarding-rule create](#ForwardingRulesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersForwardingRulesCreateOrUpdate#Create)|[Example](#ExamplesForwardingRulesCreateOrUpdate#Create)|
|[az dns-resolver forwarding-rule update](#ForwardingRulesUpdate)|Update|[Parameters](#ParametersForwardingRulesUpdate)|[Example](#ExamplesForwardingRulesUpdate)|
|[az dns-resolver forwarding-rule delete](#ForwardingRulesDelete)|Delete|[Parameters](#ParametersForwardingRulesDelete)|[Example](#ExamplesForwardingRulesDelete)|

### <a name="CommandsInInboundEndpoints">Commands in `az dns-resolver inbound-endpoint` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az dns-resolver inbound-endpoint list](#InboundEndpointsList)|List|[Parameters](#ParametersInboundEndpointsList)|[Example](#ExamplesInboundEndpointsList)|
|[az dns-resolver inbound-endpoint show](#InboundEndpointsGet)|Get|[Parameters](#ParametersInboundEndpointsGet)|[Example](#ExamplesInboundEndpointsGet)|
|[az dns-resolver inbound-endpoint create](#InboundEndpointsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersInboundEndpointsCreateOrUpdate#Create)|[Example](#ExamplesInboundEndpointsCreateOrUpdate#Create)|
|[az dns-resolver inbound-endpoint update](#InboundEndpointsUpdate)|Update|[Parameters](#ParametersInboundEndpointsUpdate)|[Example](#ExamplesInboundEndpointsUpdate)|
|[az dns-resolver inbound-endpoint delete](#InboundEndpointsDelete)|Delete|[Parameters](#ParametersInboundEndpointsDelete)|[Example](#ExamplesInboundEndpointsDelete)|

### <a name="CommandsInOutboundEndpoints">Commands in `az dns-resolver outbound-endpoint` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az dns-resolver outbound-endpoint list](#OutboundEndpointsList)|List|[Parameters](#ParametersOutboundEndpointsList)|[Example](#ExamplesOutboundEndpointsList)|
|[az dns-resolver outbound-endpoint show](#OutboundEndpointsGet)|Get|[Parameters](#ParametersOutboundEndpointsGet)|[Example](#ExamplesOutboundEndpointsGet)|
|[az dns-resolver outbound-endpoint create](#OutboundEndpointsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersOutboundEndpointsCreateOrUpdate#Create)|[Example](#ExamplesOutboundEndpointsCreateOrUpdate#Create)|
|[az dns-resolver outbound-endpoint update](#OutboundEndpointsUpdate)|Update|[Parameters](#ParametersOutboundEndpointsUpdate)|[Example](#ExamplesOutboundEndpointsUpdate)|
|[az dns-resolver outbound-endpoint delete](#OutboundEndpointsDelete)|Delete|[Parameters](#ParametersOutboundEndpointsDelete)|[Example](#ExamplesOutboundEndpointsDelete)|

### <a name="CommandsInVirtualNetworkLinks">Commands in `az dns-resolver virtual-network-link` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az dns-resolver virtual-network-link list](#VirtualNetworkLinksList)|List|[Parameters](#ParametersVirtualNetworkLinksList)|[Example](#ExamplesVirtualNetworkLinksList)|
|[az dns-resolver virtual-network-link show](#VirtualNetworkLinksGet)|Get|[Parameters](#ParametersVirtualNetworkLinksGet)|[Example](#ExamplesVirtualNetworkLinksGet)|
|[az dns-resolver virtual-network-link create](#VirtualNetworkLinksCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersVirtualNetworkLinksCreateOrUpdate#Create)|[Example](#ExamplesVirtualNetworkLinksCreateOrUpdate#Create)|
|[az dns-resolver virtual-network-link update](#VirtualNetworkLinksUpdate)|Update|[Parameters](#ParametersVirtualNetworkLinksUpdate)|[Example](#ExamplesVirtualNetworkLinksUpdate)|
|[az dns-resolver virtual-network-link delete](#VirtualNetworkLinksDelete)|Delete|[Parameters](#ParametersVirtualNetworkLinksDelete)|[Example](#ExamplesVirtualNetworkLinksDelete)|


## COMMAND DETAILS
### group `az dns-resolver`
#### <a name="DnsResolversListByResourceGroup">Command `az dns-resolver list`</a>

##### <a name="ExamplesDnsResolversListByResourceGroup">Example</a>
```
az dns-resolver list --resource-group "sampleResourceGroup"
```
##### <a name="ParametersDnsResolversListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--top**|integer|The maximum number of results to return. If not specified, returns up to 100 results.|top|$top|

#### <a name="DnsResolversList">Command `az dns-resolver list`</a>

##### <a name="ExamplesDnsResolversList">Example</a>
```
az dns-resolver list
```
##### <a name="ParametersDnsResolversList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--top**|integer|The maximum number of results to return. If not specified, returns up to 100 results.|top|$top|

#### <a name="DnsResolversGet">Command `az dns-resolver show`</a>

##### <a name="ExamplesDnsResolversGet">Example</a>
```
az dns-resolver show --name "sampleDnsResolver" --resource-group "sampleResourceGroup"
```
##### <a name="ParametersDnsResolversGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--dns-resolver-name**|string|The name of the DNS resolver.|dns_resolver_name|dnsResolverName|

#### <a name="DnsResolversCreateOrUpdate#Create">Command `az dns-resolver create`</a>

##### <a name="ExamplesDnsResolversCreateOrUpdate#Create">Example</a>
```
az dns-resolver create --name "sampleDnsResolver" --location "westus2" --id "/subscriptions/cbb1387e-4b03-44f2-ad41-58d\
4677b9873/resourceGroups/virtualNetworkResourceGroup/providers/Microsoft.Network/virtualNetworks/sampleVirtualNetwork" \
--tags key1="value1" --resource-group "sampleResourceGroup"
```
##### <a name="ParametersDnsResolversCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--dns-resolver-name**|string|The name of the DNS resolver.|dns_resolver_name|dnsResolverName|
|**--if-match**|string|ETag of the resource. Omit this value to always overwrite the current resource. Specify the last-seen ETag value to prevent accidentally overwriting any concurrent changes.|if_match|IfMatch|
|**--if-none-match**|string|Set to '*' to allow a new resource to be created, but to prevent updating an existing resource. Other values will be ignored.|if_none_match|IfNoneMatch|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--id**|string|Resource ID.|id|id|

#### <a name="DnsResolversUpdate">Command `az dns-resolver update`</a>

##### <a name="ExamplesDnsResolversUpdate">Example</a>
```
az dns-resolver update --name "sampleDnsResolver" --tags key1="value1" --resource-group "sampleResourceGroup"
```
##### <a name="ParametersDnsResolversUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--dns-resolver-name**|string|The name of the DNS resolver.|dns_resolver_name|dnsResolverName|
|**--if-match**|string|ETag of the resource. Omit this value to always overwrite the current resource. Specify the last-seen ETag value to prevent accidentally overwriting any concurrent changes.|if_match|IfMatch|
|**--tags**|dictionary|Tags for DNS Resolver.|tags|tags|

#### <a name="DnsResolversDelete">Command `az dns-resolver delete`</a>

##### <a name="ExamplesDnsResolversDelete">Example</a>
```
az dns-resolver delete --name "sampleDnsResolver" --resource-group "sampleResourceGroup"
```
##### <a name="ParametersDnsResolversDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--dns-resolver-name**|string|The name of the DNS resolver.|dns_resolver_name|dnsResolverName|
|**--if-match**|string|ETag of the resource. Omit this value to always overwrite the current resource. Specify the last-seen ETag value to prevent accidentally overwriting any concurrent changes.|if_match|IfMatch|

#### <a name="DnsResolversListByVirtualNetwork">Command `az dns-resolver list-by-virtual-network`</a>

##### <a name="ExamplesDnsResolversListByVirtualNetwork">Example</a>
```
az dns-resolver list-by-virtual-network --resource-group "sampleResourceGroup" --virtual-network-name \
"sampleVirtualNetwork"
```
##### <a name="ParametersDnsResolversListByVirtualNetwork">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--virtual-network-name**|string|The name of the virtual network.|virtual_network_name|virtualNetworkName|
|**--top**|integer|The maximum number of results to return. If not specified, returns up to 100 results.|top|$top|

### group `az dns-resolver dns-forwarding-ruleset`
#### <a name="DnsForwardingRulesetsListByResourceGroup">Command `az dns-resolver dns-forwarding-ruleset list`</a>

##### <a name="ExamplesDnsForwardingRulesetsListByResourceGroup">Example</a>
```
az dns-resolver dns-forwarding-ruleset list --resource-group "sampleResourceGroup"
```
##### <a name="ParametersDnsForwardingRulesetsListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--top**|integer|The maximum number of results to return. If not specified, returns up to 100 results.|top|$top|

#### <a name="DnsForwardingRulesetsList">Command `az dns-resolver dns-forwarding-ruleset list`</a>

##### <a name="ExamplesDnsForwardingRulesetsList">Example</a>
```
az dns-resolver dns-forwarding-ruleset list
```
##### <a name="ParametersDnsForwardingRulesetsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--top**|integer|The maximum number of results to return. If not specified, returns up to 100 results.|top|$top|

#### <a name="DnsForwardingRulesetsGet">Command `az dns-resolver dns-forwarding-ruleset show`</a>

##### <a name="ExamplesDnsForwardingRulesetsGet">Example</a>
```
az dns-resolver dns-forwarding-ruleset show --name "sampleDnsForwardingRuleset" --resource-group "sampleResourceGroup"
```
##### <a name="ParametersDnsForwardingRulesetsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--dns-forwarding-ruleset-name**|string|The name of the DNS forwarding ruleset.|dns_forwarding_ruleset_name|dnsForwardingRulesetName|

#### <a name="DnsForwardingRulesetsCreateOrUpdate#Create">Command `az dns-resolver dns-forwarding-ruleset create`</a>

##### <a name="ExamplesDnsForwardingRulesetsCreateOrUpdate#Create">Example</a>
```
az dns-resolver dns-forwarding-ruleset create --name "samplednsForwardingRuleset" --location "westus2" \
--dns-resolver-outbound-endpoints id="/subscriptions/abdd4249-9f34-4cc6-8e42-c2e32110603e/resourceGroups/sampleResource\
Group/providers/Microsoft.Network/dnsResolvers/sampleDnsResolver/outboundEndpoints/sampleOutboundEndpoint0" \
--dns-resolver-outbound-endpoints id="/subscriptions/abdd4249-9f34-4cc6-8e42-c2e32110603e/resourceGroups/sampleResource\
Group/providers/Microsoft.Network/dnsResolvers/sampleDnsResolver/outboundEndpoints/sampleOutboundEndpoint1" --tags \
key1="value1" --resource-group "sampleResourceGroup"
```
##### <a name="ParametersDnsForwardingRulesetsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--dns-forwarding-ruleset-name**|string|The name of the DNS forwarding ruleset.|dns_forwarding_ruleset_name|dnsForwardingRulesetName|
|**--if-match**|string|ETag of the resource. Omit this value to always overwrite the current resource. Specify the last-seen ETag value to prevent accidentally overwriting any concurrent changes.|if_match|IfMatch|
|**--if-none-match**|string|Set to '*' to allow a new resource to be created, but to prevent updating an existing resource. Other values will be ignored.|if_none_match|IfNoneMatch|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--dns-resolver-outbound-endpoints**|array|The reference to the DNS resolver outbound endpoints that are used to route DNS queries matching the forwarding rules in the ruleset to the target DNS servers.|dns_resolver_outbound_endpoints|dnsResolverOutboundEndpoints|

#### <a name="DnsForwardingRulesetsUpdate">Command `az dns-resolver dns-forwarding-ruleset update`</a>

##### <a name="ExamplesDnsForwardingRulesetsUpdate">Example</a>
```
az dns-resolver dns-forwarding-ruleset update --name "sampleDnsForwardingRuleset" --tags key1="value1" \
--resource-group "sampleResourceGroup"
```
##### <a name="ParametersDnsForwardingRulesetsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--dns-forwarding-ruleset-name**|string|The name of the DNS forwarding ruleset.|dns_forwarding_ruleset_name|dnsForwardingRulesetName|
|**--if-match**|string|ETag of the resource. Omit this value to always overwrite the current resource. Specify the last-seen ETag value to prevent accidentally overwriting any concurrent changes.|if_match|IfMatch|
|**--tags**|dictionary|Tags for DNS Resolver.|tags|tags|

#### <a name="DnsForwardingRulesetsDelete">Command `az dns-resolver dns-forwarding-ruleset delete`</a>

##### <a name="ExamplesDnsForwardingRulesetsDelete">Example</a>
```
az dns-resolver dns-forwarding-ruleset delete --name "samplednsForwardingRulesetName" --resource-group \
"sampleResourceGroup"
```
##### <a name="ParametersDnsForwardingRulesetsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--dns-forwarding-ruleset-name**|string|The name of the DNS forwarding ruleset.|dns_forwarding_ruleset_name|dnsForwardingRulesetName|
|**--if-match**|string|ETag of the resource. Omit this value to always overwrite the current resource. Specify the last-seen ETag value to prevent accidentally overwriting any concurrent changes.|if_match|IfMatch|

#### <a name="DnsForwardingRulesetsListByVirtualNetwork">Command `az dns-resolver dns-forwarding-ruleset list-by-virtual-network`</a>

##### <a name="ExamplesDnsForwardingRulesetsListByVirtualNetwork">Example</a>
```
az dns-resolver dns-forwarding-ruleset list-by-virtual-network --resource-group "sampleResourceGroup" \
--virtual-network-name "sampleVirtualNetwork"
```
##### <a name="ParametersDnsForwardingRulesetsListByVirtualNetwork">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--virtual-network-name**|string|The name of the virtual network.|virtual_network_name|virtualNetworkName|
|**--top**|integer|The maximum number of results to return. If not specified, returns up to 100 results.|top|$top|

### group `az dns-resolver forwarding-rule`
#### <a name="ForwardingRulesList">Command `az dns-resolver forwarding-rule list`</a>

##### <a name="ExamplesForwardingRulesList">Example</a>
```
az dns-resolver forwarding-rule list --dns-forwarding-ruleset-name "sampleDnsForwardingRuleset" --resource-group \
"sampleResourceGroup"
```
##### <a name="ParametersForwardingRulesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--dns-forwarding-ruleset-name**|string|The name of the DNS forwarding ruleset.|dns_forwarding_ruleset_name|dnsForwardingRulesetName|
|**--top**|integer|The maximum number of results to return. If not specified, returns up to 100 results.|top|$top|

#### <a name="ForwardingRulesGet">Command `az dns-resolver forwarding-rule show`</a>

##### <a name="ExamplesForwardingRulesGet">Example</a>
```
az dns-resolver forwarding-rule show --dns-forwarding-ruleset-name "sampleDnsForwardingRuleset" --name \
"sampleForwardingRule" --resource-group "sampleResourceGroup"
```
##### <a name="ParametersForwardingRulesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--dns-forwarding-ruleset-name**|string|The name of the DNS forwarding ruleset.|dns_forwarding_ruleset_name|dnsForwardingRulesetName|
|**--forwarding-rule-name**|string|The name of the forwarding rule.|forwarding_rule_name|forwardingRuleName|

#### <a name="ForwardingRulesCreateOrUpdate#Create">Command `az dns-resolver forwarding-rule create`</a>

##### <a name="ExamplesForwardingRulesCreateOrUpdate#Create">Example</a>
```
az dns-resolver forwarding-rule create --dns-forwarding-ruleset-name "sampleDnsForwardingRuleset" --name \
"sampleForwardingRule" --domain-name "contoso.com." --forwarding-rule-state "Enabled" --metadata \
additionalProp1="value1" --target-dns-servers ip-address="10.0.0.1" port=53 --target-dns-servers ip-address="10.0.0.2" \
port=53 --resource-group "sampleResourceGroup"
```
##### <a name="ParametersForwardingRulesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--dns-forwarding-ruleset-name**|string|The name of the DNS forwarding ruleset.|dns_forwarding_ruleset_name|dnsForwardingRulesetName|
|**--forwarding-rule-name**|string|The name of the forwarding rule.|forwarding_rule_name|forwardingRuleName|
|**--if-match**|string|ETag of the resource. Omit this value to always overwrite the current resource. Specify the last-seen ETag value to prevent accidentally overwriting any concurrent changes.|if_match|IfMatch|
|**--if-none-match**|string|Set to '*' to allow a new resource to be created, but to prevent updating an existing resource. Other values will be ignored.|if_none_match|IfNoneMatch|
|**--domain-name**|string|The domain name for the forwarding rule.|domain_name|domainName|
|**--target-dns-servers**|array|DNS servers to forward the DNS query to.|target_dns_servers|targetDnsServers|
|**--metadata**|dictionary|Metadata attached to the forwarding rule.|metadata|metadata|
|**--forwarding-rule-state**|choice|The state of forwarding rule.|forwarding_rule_state|forwardingRuleState|

#### <a name="ForwardingRulesUpdate">Command `az dns-resolver forwarding-rule update`</a>

##### <a name="ExamplesForwardingRulesUpdate">Example</a>
```
az dns-resolver forwarding-rule update --dns-forwarding-ruleset-name "sampleDnsForwardingRuleset" --name \
"sampleForwardingRule" --forwarding-rule-state "Disabled" --metadata additionalProp2="value2" --resource-group \
"sampleResourceGroup"
```
##### <a name="ParametersForwardingRulesUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--dns-forwarding-ruleset-name**|string|The name of the DNS forwarding ruleset.|dns_forwarding_ruleset_name|dnsForwardingRulesetName|
|**--forwarding-rule-name**|string|The name of the forwarding rule.|forwarding_rule_name|forwardingRuleName|
|**--if-match**|string|ETag of the resource. Omit this value to always overwrite the current resource. Specify the last-seen ETag value to prevent accidentally overwriting any concurrent changes.|if_match|IfMatch|
|**--target-dns-servers**|array|DNS servers to forward the DNS query to.|target_dns_servers|targetDnsServers|
|**--metadata**|dictionary|Metadata attached to the forwarding rule.|metadata|metadata|
|**--forwarding-rule-state**|choice|The state of forwarding rule.|forwarding_rule_state|forwardingRuleState|

#### <a name="ForwardingRulesDelete">Command `az dns-resolver forwarding-rule delete`</a>

##### <a name="ExamplesForwardingRulesDelete">Example</a>
```
az dns-resolver forwarding-rule delete --dns-forwarding-ruleset-name "sampleDnsForwardingRuleset" --name \
"sampleForwardingRule" --resource-group "sampleResourceGroup"
```
##### <a name="ParametersForwardingRulesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--dns-forwarding-ruleset-name**|string|The name of the DNS forwarding ruleset.|dns_forwarding_ruleset_name|dnsForwardingRulesetName|
|**--forwarding-rule-name**|string|The name of the forwarding rule.|forwarding_rule_name|forwardingRuleName|
|**--if-match**|string|ETag of the resource. Omit this value to always overwrite the current resource. Specify the last-seen ETag value to prevent accidentally overwriting any concurrent changes.|if_match|IfMatch|

### group `az dns-resolver inbound-endpoint`
#### <a name="InboundEndpointsList">Command `az dns-resolver inbound-endpoint list`</a>

##### <a name="ExamplesInboundEndpointsList">Example</a>
```
az dns-resolver inbound-endpoint list --dns-resolver-name "sampleDnsResolver" --resource-group "sampleResourceGroup"
```
##### <a name="ParametersInboundEndpointsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--dns-resolver-name**|string|The name of the DNS resolver.|dns_resolver_name|dnsResolverName|
|**--top**|integer|The maximum number of results to return. If not specified, returns up to 100 results.|top|$top|

#### <a name="InboundEndpointsGet">Command `az dns-resolver inbound-endpoint show`</a>

##### <a name="ExamplesInboundEndpointsGet">Example</a>
```
az dns-resolver inbound-endpoint show --dns-resolver-name "sampleDnsResolver" --name "sampleInboundEndpoint" \
--resource-group "sampleResourceGroup"
```
##### <a name="ParametersInboundEndpointsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--dns-resolver-name**|string|The name of the DNS resolver.|dns_resolver_name|dnsResolverName|
|**--inbound-endpoint-name**|string|The name of the inbound endpoint for the DNS resolver.|inbound_endpoint_name|inboundEndpointName|

#### <a name="InboundEndpointsCreateOrUpdate#Create">Command `az dns-resolver inbound-endpoint create`</a>

##### <a name="ExamplesInboundEndpointsCreateOrUpdate#Create">Example</a>
```
az dns-resolver inbound-endpoint create --dns-resolver-name "sampleDnsResolver" --name "sampleInboundEndpoint" \
--location "westus2" --ip-configurations private-ip-address="255.255.255.255" private-ip-allocation-method="Static" \
id="/subscriptions/0403cfa9-9659-4f33-9f30-1f191c51d111/resourceGroups/sampleVnetResourceGroupName/providers/Microsoft.\
Network/virtualNetworks/sampleVirtualNetwork/subnets/sampleSubnet" --tags key1="value1" --resource-group \
"sampleResourceGroup"
```
##### <a name="ParametersInboundEndpointsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--dns-resolver-name**|string|The name of the DNS resolver.|dns_resolver_name|dnsResolverName|
|**--inbound-endpoint-name**|string|The name of the inbound endpoint for the DNS resolver.|inbound_endpoint_name|inboundEndpointName|
|**--if-match**|string|ETag of the resource. Omit this value to always overwrite the current resource. Specify the last-seen ETag value to prevent accidentally overwriting any concurrent changes.|if_match|IfMatch|
|**--if-none-match**|string|Set to '*' to allow a new resource to be created, but to prevent updating an existing resource. Other values will be ignored.|if_none_match|IfNoneMatch|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--ip-configurations**|array|IP configurations for the inbound endpoint.|ip_configurations|ipConfigurations|

#### <a name="InboundEndpointsUpdate">Command `az dns-resolver inbound-endpoint update`</a>

##### <a name="ExamplesInboundEndpointsUpdate">Example</a>
```
az dns-resolver inbound-endpoint update --dns-resolver-name "sampleDnsResolver" --name "sampleInboundEndpoint" --tags \
key1="value1" --resource-group "sampleResourceGroup"
```
##### <a name="ParametersInboundEndpointsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--dns-resolver-name**|string|The name of the DNS resolver.|dns_resolver_name|dnsResolverName|
|**--inbound-endpoint-name**|string|The name of the inbound endpoint for the DNS resolver.|inbound_endpoint_name|inboundEndpointName|
|**--if-match**|string|ETag of the resource. Omit this value to always overwrite the current resource. Specify the last-seen ETag value to prevent accidentally overwriting any concurrent changes.|if_match|IfMatch|
|**--tags**|dictionary|Tags for inbound endpoint.|tags|tags|

#### <a name="InboundEndpointsDelete">Command `az dns-resolver inbound-endpoint delete`</a>

##### <a name="ExamplesInboundEndpointsDelete">Example</a>
```
az dns-resolver inbound-endpoint delete --dns-resolver-name "sampleDnsResolver" --name "sampleInboundEndpoint" \
--resource-group "sampleResourceGroup"
```
##### <a name="ParametersInboundEndpointsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--dns-resolver-name**|string|The name of the DNS resolver.|dns_resolver_name|dnsResolverName|
|**--inbound-endpoint-name**|string|The name of the inbound endpoint for the DNS resolver.|inbound_endpoint_name|inboundEndpointName|
|**--if-match**|string|ETag of the resource. Omit this value to always overwrite the current resource. Specify the last-seen ETag value to prevent accidentally overwriting any concurrent changes.|if_match|IfMatch|

### group `az dns-resolver outbound-endpoint`
#### <a name="OutboundEndpointsList">Command `az dns-resolver outbound-endpoint list`</a>

##### <a name="ExamplesOutboundEndpointsList">Example</a>
```
az dns-resolver outbound-endpoint list --dns-resolver-name "sampleDnsResolver" --resource-group "sampleResourceGroup"
```
##### <a name="ParametersOutboundEndpointsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--dns-resolver-name**|string|The name of the DNS resolver.|dns_resolver_name|dnsResolverName|
|**--top**|integer|The maximum number of results to return. If not specified, returns up to 100 results.|top|$top|

#### <a name="OutboundEndpointsGet">Command `az dns-resolver outbound-endpoint show`</a>

##### <a name="ExamplesOutboundEndpointsGet">Example</a>
```
az dns-resolver outbound-endpoint show --dns-resolver-name "sampleDnsResolver" --name "sampleOutboundEndpoint" \
--resource-group "sampleResourceGroup"
```
##### <a name="ParametersOutboundEndpointsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--dns-resolver-name**|string|The name of the DNS resolver.|dns_resolver_name|dnsResolverName|
|**--outbound-endpoint-name**|string|The name of the outbound endpoint for the DNS resolver.|outbound_endpoint_name|outboundEndpointName|

#### <a name="OutboundEndpointsCreateOrUpdate#Create">Command `az dns-resolver outbound-endpoint create`</a>

##### <a name="ExamplesOutboundEndpointsCreateOrUpdate#Create">Example</a>
```
az dns-resolver outbound-endpoint create --dns-resolver-name "sampleDnsResolver" --name "sampleOutboundEndpoint" \
--location "westus2" --id "/subscriptions/0403cfa9-9659-4f33-9f30-1f191c51d111/resourceGroups/sampleVnetResourceGroupNa\
me/providers/Microsoft.Network/virtualNetworks/sampleVirtualNetwork/subnets/sampleSubnet" --tags key1="value1" \
--resource-group "sampleResourceGroup"
```
##### <a name="ParametersOutboundEndpointsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--dns-resolver-name**|string|The name of the DNS resolver.|dns_resolver_name|dnsResolverName|
|**--outbound-endpoint-name**|string|The name of the outbound endpoint for the DNS resolver.|outbound_endpoint_name|outboundEndpointName|
|**--if-match**|string|ETag of the resource. Omit this value to always overwrite the current resource. Specify the last-seen ETag value to prevent accidentally overwriting any concurrent changes.|if_match|IfMatch|
|**--if-none-match**|string|Set to '*' to allow a new resource to be created, but to prevent updating an existing resource. Other values will be ignored.|if_none_match|IfNoneMatch|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--id**|string|Resource ID.|id|id|

#### <a name="OutboundEndpointsUpdate">Command `az dns-resolver outbound-endpoint update`</a>

##### <a name="ExamplesOutboundEndpointsUpdate">Example</a>
```
az dns-resolver outbound-endpoint update --dns-resolver-name "sampleDnsResolver" --name "sampleOutboundEndpoint" \
--tags key1="value1" --resource-group "sampleResourceGroup"
```
##### <a name="ParametersOutboundEndpointsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--dns-resolver-name**|string|The name of the DNS resolver.|dns_resolver_name|dnsResolverName|
|**--outbound-endpoint-name**|string|The name of the outbound endpoint for the DNS resolver.|outbound_endpoint_name|outboundEndpointName|
|**--if-match**|string|ETag of the resource. Omit this value to always overwrite the current resource. Specify the last-seen ETag value to prevent accidentally overwriting any concurrent changes.|if_match|IfMatch|
|**--tags**|dictionary|Tags for outbound endpoint.|tags|tags|

#### <a name="OutboundEndpointsDelete">Command `az dns-resolver outbound-endpoint delete`</a>

##### <a name="ExamplesOutboundEndpointsDelete">Example</a>
```
az dns-resolver outbound-endpoint delete --dns-resolver-name "sampleDnsResolver" --name "sampleOutboundEndpoint" \
--resource-group "sampleResourceGroup"
```
##### <a name="ParametersOutboundEndpointsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--dns-resolver-name**|string|The name of the DNS resolver.|dns_resolver_name|dnsResolverName|
|**--outbound-endpoint-name**|string|The name of the outbound endpoint for the DNS resolver.|outbound_endpoint_name|outboundEndpointName|
|**--if-match**|string|ETag of the resource. Omit this value to always overwrite the current resource. Specify the last-seen ETag value to prevent accidentally overwriting any concurrent changes.|if_match|IfMatch|

### group `az dns-resolver virtual-network-link`
#### <a name="VirtualNetworkLinksList">Command `az dns-resolver virtual-network-link list`</a>

##### <a name="ExamplesVirtualNetworkLinksList">Example</a>
```
az dns-resolver virtual-network-link list --dns-forwarding-ruleset-name "sampleDnsForwardingRuleset" --resource-group \
"sampleResourceGroup"
```
##### <a name="ParametersVirtualNetworkLinksList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--dns-forwarding-ruleset-name**|string|The name of the DNS forwarding ruleset.|dns_forwarding_ruleset_name|dnsForwardingRulesetName|
|**--top**|integer|The maximum number of results to return. If not specified, returns up to 100 results.|top|$top|

#### <a name="VirtualNetworkLinksGet">Command `az dns-resolver virtual-network-link show`</a>

##### <a name="ExamplesVirtualNetworkLinksGet">Example</a>
```
az dns-resolver virtual-network-link show --dns-forwarding-ruleset-name "sampleDnsForwardingRuleset" --resource-group \
"sampleResourceGroup" --name "sampleVirtualNetworkLink"
```
##### <a name="ParametersVirtualNetworkLinksGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--dns-forwarding-ruleset-name**|string|The name of the DNS forwarding ruleset.|dns_forwarding_ruleset_name|dnsForwardingRulesetName|
|**--virtual-network-link-name**|string|The name of the virtual network link.|virtual_network_link_name|virtualNetworkLinkName|

#### <a name="VirtualNetworkLinksCreateOrUpdate#Create">Command `az dns-resolver virtual-network-link create`</a>

##### <a name="ExamplesVirtualNetworkLinksCreateOrUpdate#Create">Example</a>
```
az dns-resolver virtual-network-link create --dns-forwarding-ruleset-name "sampleDnsForwardingRuleset" --metadata \
additionalProp1="value1" --id "/subscriptions/0403cfa9-9659-4f33-9f30-1f191c51d111/resourceGroups/sampleVnetResourceGro\
upName/providers/Microsoft.Network/virtualNetworks/sampleVirtualNetwork" --resource-group "sampleResourceGroup" --name \
"sampleVirtualNetworkLink"
```
##### <a name="ParametersVirtualNetworkLinksCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--dns-forwarding-ruleset-name**|string|The name of the DNS forwarding ruleset.|dns_forwarding_ruleset_name|dnsForwardingRulesetName|
|**--virtual-network-link-name**|string|The name of the virtual network link.|virtual_network_link_name|virtualNetworkLinkName|
|**--if-match**|string|ETag of the resource. Omit this value to always overwrite the current resource. Specify the last-seen ETag value to prevent accidentally overwriting any concurrent changes.|if_match|IfMatch|
|**--if-none-match**|string|Set to '*' to allow a new resource to be created, but to prevent updating an existing resource. Other values will be ignored.|if_none_match|IfNoneMatch|
|**--metadata**|dictionary|Metadata attached to the virtual network link.|metadata|metadata|
|**--id**|string|Resource ID.|id|id|

#### <a name="VirtualNetworkLinksUpdate">Command `az dns-resolver virtual-network-link update`</a>

##### <a name="ExamplesVirtualNetworkLinksUpdate">Example</a>
```
az dns-resolver virtual-network-link update --dns-forwarding-ruleset-name "sampleDnsForwardingRuleset" --metadata \
additionalProp1="value1" --resource-group "sampleResourceGroup" --name "sampleVirtualNetworkLink"
```
##### <a name="ParametersVirtualNetworkLinksUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--dns-forwarding-ruleset-name**|string|The name of the DNS forwarding ruleset.|dns_forwarding_ruleset_name|dnsForwardingRulesetName|
|**--virtual-network-link-name**|string|The name of the virtual network link.|virtual_network_link_name|virtualNetworkLinkName|
|**--if-match**|string|ETag of the resource. Omit this value to always overwrite the current resource. Specify the last-seen ETag value to prevent accidentally overwriting any concurrent changes.|if_match|IfMatch|
|**--metadata**|dictionary|Metadata attached to the virtual network link.|metadata|metadata|

#### <a name="VirtualNetworkLinksDelete">Command `az dns-resolver virtual-network-link delete`</a>

##### <a name="ExamplesVirtualNetworkLinksDelete">Example</a>
```
az dns-resolver virtual-network-link delete --dns-forwarding-ruleset-name "sampleDnsForwardingRuleset" \
--resource-group "sampleResourceGroup" --name "sampleVirtualNetworkLink"
```
##### <a name="ParametersVirtualNetworkLinksDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--dns-forwarding-ruleset-name**|string|The name of the DNS forwarding ruleset.|dns_forwarding_ruleset_name|dnsForwardingRulesetName|
|**--virtual-network-link-name**|string|The name of the virtual network link.|virtual_network_link_name|virtualNetworkLinkName|
|**--if-match**|string|ETag of the resource. Omit this value to always overwrite the current resource. Specify the last-seen ETag value to prevent accidentally overwriting any concurrent changes.|if_match|IfMatch|
