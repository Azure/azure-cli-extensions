# Azure CLI windows-iot-services Extension #
This is the extension for windows-iot-services

### How to use ###
Install this extension using the below CLI command
```
az extension add --name windows-iot-services
```

### Included Features ###
#### windows-iot-services service ####
##### Create #####
```
az windows-iot-services service create --device-name "service4445" --admin-domain-name "d.e.f" \
    --billing-domain-name "a.b.c" --notes "blah" --quantity 1000000 --resource-group "res9101" 
```
##### Show #####
```
az windows-iot-services service show --device-name "service8596" --resource-group "res9407"
```
##### List #####
```
az windows-iot-services service list --resource-group "res6117"
```
##### Update #####
```
az windows-iot-services service update --device-name "service8596" --admin-domain-name "d.e.f" \
    --billing-domain-name "a.b.c" --notes "blah" --quantity 1000000 --resource-group "res9407" 
```
##### Check-device-service-name-availability #####
```
az windows-iot-services service check-device-service-name-availability --name "service3363"
```
##### Delete #####
```
az windows-iot-services service delete --device-name "service2434" --resource-group "res4228"
```