Microsoft Azure CLI 'peering' Extension
==========================================

This package is for the 'peering' extension. i.e. 'az peering'

### How to use ###
Install this extension using the below CLI command
```
az extension add --name peering
```

### Included Features ###
Manage peering


#### List legacy peerings.

```
az peering legacy list --kind "Exchange" --peering-location "peeringLocation0"
```

#### List peer ASNs.

```
az peering asn list
```

#### Create a peer ASN.

```
az peering asn create --peer-asn 65000 --peer-contact-detail email="noc@contoso.com" phone="+1 (234) 567-8999" role="Noc" --peer-contact-detail email="abc@contoso.com" phone="+1 (234) 567-8900" role="Policy" --peer-contact-detail email="xyz@contoso.com" phone="+1 (234) 567-8900" role="Technical" --peer-name "Contoso" --peer-asn-name "peerAsnName"
```

#### Get a peer ASN.

```
az peering asn show --peer-asn-name "peerAsnName"
```

#### Delete a peer ASN.

```
az peering asn delete --peer-asn-name "peerAsnName"
```

#### Create a peering service.

```
az peering service create --location "eastus" --peering-service-location "state1" --peering-service-provider "serviceProvider1" --peering-service-name "peeringServiceName" --resource-group "rgName"
```

#### Update a peering service.

```
az peering service update --peering-service-name "peeringServiceName" --resource-group "rgName" --tags tags={"tag0":"value0","tag1":"value1"}
```

#### Get a peering service.

```
az peering service show --peering-service-name "peeringServiceName" --resource-group "rgName"
```

#### List peering services.

```
az peering service list --resource-group "rgName"
```

#### Delete a peering service.

```
az peering service delete --peering-service-name "peeringServiceName" --resource-group "rgName"
```