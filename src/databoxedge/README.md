# Azure CLI data-box-edge Extension #
This is the extension for data-box-edge

### How to use ###
Install this extension using the below CLI command
```
az extension add --name data-box-edge
```

### Included Features ###
#### data-box-edge device ####
##### Create #####
```
az data-box-edge device create --location "eastus" --sku name="Edge" tier="Standard" --name "testedgedevice" \
    --resource-group "GroupForEdgeAutomation" 
```
##### Show #####
```
az data-box-edge device show --name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### List #####
```
az data-box-edge device list --resource-group "GroupForEdgeAutomation"
```
##### Update #####
```
az data-box-edge device update --name "testedgedevice" --tags Key1="value1" Key2="value2" \
    --resource-group "GroupForEdgeAutomation" 
```
##### Download-update #####
```
az data-box-edge device download-update --name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### Get-update-summary #####
```
az data-box-edge device get-update-summary --name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### Install-update #####
```
az data-box-edge device install-update --name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### Scan-for-update #####
```
az data-box-edge device scan-for-update --name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### Delete #####
```
az data-box-edge device delete --name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
#### data-box-edge alert ####
##### List #####
```
az data-box-edge alert list --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### Show #####
```
az data-box-edge alert show --name "159a00c7-8543-4343-9435-263ac87df3bb" --device-name "testedgedevice" \
    --resource-group "GroupForEdgeAutomation" 
```
#### data-box-edge bandwidth-schedule ####
##### Create #####
```
az data-box-edge bandwidth-schedule create --name "bandwidth-1" --device-name "testedgedevice" --days "Sunday" \
    --days "Monday" --rate-in-mbps 100 --start "0:0:0" --stop "13:59:0" --resource-group "GroupForEdgeAutomation" 
```
##### Show #####
```
az data-box-edge bandwidth-schedule show --name "bandwidth-1" --device-name "testedgedevice" \
    --resource-group "GroupForEdgeAutomation" 
```
##### List #####
```
az data-box-edge bandwidth-schedule list --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### Delete #####
```
az data-box-edge bandwidth-schedule delete --name "bandwidth-1" --device-name "testedgedevice" \
    --resource-group "GroupForEdgeAutomation" 
```
#### data-box-edge ####
##### Show-job #####
```
az data-box-edge show-job --name "159a00c7-8543-4343-9435-263ac87df3bb" --device-name "testedgedevice" \
    --resource-group "GroupForEdgeAutomation" 
```
#### data-box-edge ####
##### List-node #####
```
az data-box-edge list-node --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
#### data-box-edge order ####
##### Create #####
```
az data-box-edge order create --device-name "testedgedevice" --company-name "Microsoft" \
    --contact-person "John Mcclane" --email-list "john@microsoft.com" --phone "(800) 426-9400" \
    --address-line1 "Microsoft Corporation" --address-line2 "One Microsoft Way" --address-line3 "Redmond" --city "WA" \
    --country "USA" --postal-code "98052" --state "WA" --resource-group "GroupForEdgeAutomation" 
```
##### Show #####
```
az data-box-edge order show --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### List #####
```
az data-box-edge order list --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
##### Delete #####
```
az data-box-edge order delete --device-name "testedgedevice" --resource-group "GroupForEdgeAutomation"
```
#### data-box-edge ####
##### List-sku #####
```
az data-box-edge list-sku
```