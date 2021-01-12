# Azure CLI windowsiotservices Extension #
This is the extension for windowsiotservices

### How to use ###
Install this extension using the below CLI command
```
az extension add --name windowsiotservices
```

### Included Features ###
#### windowsiotservices service ####
##### Create #####
```
az windowsiotservices service create --device-name "service4445" --location "East US" --admin-domain-name "d.e.f" \
    --billing-domain-name "a.b.c" --notes "blah" --quantity 1000000 --resource-group "res9101" 
```
##### Show #####
```
az windowsiotservices service show --device-name "service8596" --resource-group "res9407"
```
##### List #####
```
az windowsiotservices service list --resource-group "res6117"
```
##### Update #####
```
az windowsiotservices service update --device-name "service8596" --location "East US" --admin-domain-name "d.e.f" \
    --billing-domain-name "a.b.c" --notes "blah" --quantity 1000000 --resource-group "res9407" 
```
##### Check-device-service-name-availability #####
```
az windowsiotservices service check-device-service-name-availability --name "service3363"
```
##### Delete #####
```
az windowsiotservices service delete --device-name "service2434" --resource-group "res4228"
```