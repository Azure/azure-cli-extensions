# Azure CLI VoiceService Extension #
This is an extension to Azure CLI to manage VoiceService resources.

## How to use ##
Install this extension using the below CLI command
```
az extension add --name voice-service
```

### Included Features ###
#### voice-service gateway ####
##### Create #####
```
az voice-service gateway create -n gateway-name -g rg --service-locations '[{name:useast,PrimaryRegionProperties:{operatorAddresses:[198.51.100.1],allowedSignalingSourceAddressPrefixes:[10.1.1.0/24],allowedMediaSourceAddressPrefixes:[10.1.2.0/24]}},{name:useast2,PrimaryRegionProperties:{operatorAddresses:[198.51.100.2],allowedSignalingSourceAddressPrefixes:[10.2.1.0/24],allowedMediaSourceAddressPrefixes:[10.2.2.0/24]}}]' --connectivity PublicAddress --codecs '[PCMA]' --e911-type Standard --platforms '[OperatorConnect]'

```
##### Show #####
```
az voice-service gateway show -n gateway-name -g rg
```
##### List #####
```
az voice-service gateway list -g rg
```
##### Update #####
```
az voice-service gateway update -n gateway-name -g rg --tags "{tag:test,tag2:test2}"
```

##### Delete #####
```
az voice-service gateway delete -n gateway-name -g rg -y
```

#### voice-service test-line ####
##### Create #####
```
az voice-service test-line create -n test-line-name -g rg --gateway-name gateway-name --phone-number "+1-555-1234" --purpose Automated

```
##### Show #####
```
az voice-service test-line show -n test-line-name --gateway-name gateway-name -g rg
```
##### List #####
```
az voice-service test-line list -g rg --gateway-name gateway-name
```
##### Update #####
```
az voice-service test-line update -n test-line-name -g rg --gateway-name gateway-name --tags "{tag:test,tag2:test2}"
```

##### Delete #####
```
az voice-service test-line delete -n test-line-name -g rg --gateway-name gateway-name -y
```

#### voice-service check-name-availability ####
```
az voice-service check-name-availability -l centraluseuap --name voicenametest --type microsoft.voiceservices/communicationsgateways/testlines
```
