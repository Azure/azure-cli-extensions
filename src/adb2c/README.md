# Azure CLI adb2c Extension #
This is the extension for adb2c

### How to use ###
Install this extension using the below CLI command
```
az extension add --name adb2c
```

### Included Features ###
#### adb2c tenant ####
##### Create #####
```
az adb2c tenant create --location "United States" --properties display-name="Contoso" country-code="US" \
    --name "Standard" --resource-group "contosoResourceGroup" --resource-name "contoso.onmicrosoft.com" 
```
##### Show #####
```
az adb2c tenant show --resource-group "contosoResourceGroup" --resource-name "contoso.onmicrosoft.com"
```
##### List #####
```
az adb2c tenant list --resource-group "contosoResourceGroup"
```
##### Update #####
```
az adb2c tenant update --resource-group "contosoResourceGroup" --resource-name "contoso.onmicrosoft.com" \
    --billing-type "MAU" --name "PremiumP1" --tags key="value" 
```
##### Delete #####
```
az adb2c tenant delete --resource-group "rg1" --resource-name "contoso.onmicrosoft.com"
```