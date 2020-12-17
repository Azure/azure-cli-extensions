# Azure CLI account Extension #
This is the extension for account

### How to use ###
Install this extension using the below CLI command
```
az extension add --name account
```

### Included Features ###
#### account subscription ####
##### List #####
```
az account subscription list
```
##### Show #####
```
az account subscription show --subscription-id "83aa47df-e3e9-49ff-877b-94304bf3d3ad"
```
##### List-location #####
```
az account subscription list-location --subscription-id "83aa47df-e3e9-49ff-877b-94304bf3d3ad"
```
#### account tenant ####
##### List #####
```
az account tenant list
```
#### account subscription ####
##### Cancel #####
```
az account subscription cancel --subscription-id "83aa47df-e3e9-49ff-877b-94304bf3d3ad"
```
##### Enable #####
```
az account subscription enable --subscription-id "7948bcee-488c-47ce-941c-38e20ede803d"
```
##### Rename #####
```
az account subscription rename --name "Test Sub" --subscription-id "83aa47df-e3e9-49ff-877b-94304bf3d3ad"
```
#### account alias ####
##### Create #####
```
az account alias create --name "aliasForNewSub" \
    --properties billing-scope="/providers/Microsoft.Billing/billingAccounts/e879cf0f-2b4d-5431-109a-f72fc9868693:024cabf4-7321-4cf9-be59-df0c77ca51de_2019-05-31/billingProfiles/PE2Q-NOIT-BG7-TGB/invoiceSections/MTT4-OBS7-PJA-TGB" display-name="Contoso MCA subscription" workload="Production" 
```
##### Show #####
```
az account alias show --name "aliasForNewSub"
```
##### List #####
```
az account alias list
```
##### Delete #####
```
az account alias delete --name "aliasForNewSub"
```