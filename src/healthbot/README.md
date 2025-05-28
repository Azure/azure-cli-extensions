# Azure CLI healthbot Extension #
This is the extension for healthbot.
The Azure Health Bot service empowers healthcare organizations to build and deploy an AI-powered, compliant, conversational healthcare experience at scale.
The service combines built-in medical intelligence with natural language capabilities, extensibility tools and compliance constructs, allowing healthcare organizations such as Providers, Payers, Pharma, HMOs, Telehealth to give people access to trusted and relevant healthcare services and information.

### How to use ###
Install this extension using the below CLI command
```
az extension add --name healthbot
```

### Included Features ###
#### healthbot ####
##### Create #####
```
az healthbot create --name "samplebotname" --location "East US" --sku "F0" --resource-group "healthbotClient"
```
##### Show #####
```
az healthbot show --name "samplebotname" --resource-group "healthbotClient"
```
##### List #####
```
az healthbot list --resource-group "OneResourceGroupName"
```
##### Update #####
```
az healthbot update --name "samplebotname" --sku "F0" --resource-group "healthbotClient"
```
##### Delete #####
```
az healthbot delete --name "samplebotname" --resource-group "healthbotClient"
```