# Azure CLI Edgezones Extension #
This is an extension to Azure CLI to manage Edgezones resources.

## How to use ##
Install this extension using the below CLI command
```
az extension add --name edgezones
```

### Included Features
##### List extended zones
```
az edge-zones extended-zone list
```
##### Show extended zone
```
az edge-zones extended-zone show \
    --extended-zone-name "losangeles"
```
##### Register extended zone
```
az edge-zones extended-zone register \
    --extended-zone-name "losangeles"
```
##### Unregister extended zone
```
az edge-zones extended-zone unregister \
    --extended-zone-name "losangeles"
```