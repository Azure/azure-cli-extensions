# Azure CLI providerhub Extension #
This is the extension for providerhub

### How to use ###
Install this extension using the below CLI command
```
az extension add --name providerhub
```

### Included Features ###
#### providerhub custom-rollout ####
##### Create #####
```
az providerhub custom-rollout create --provider-namespace "Microsoft.Contoso" --rollout-name "brazilUsShoeBoxTesting"
```
##### Show #####
```
az providerhub custom-rollout show --provider-namespace "Microsoft.Contoso" --rollout-name "canaryTesting99"
```
##### List #####
```
az providerhub custom-rollout list --provider-namespace "Microsoft.Contoso"
```
#### providerhub default-rollout ####
##### Create #####
```
az providerhub default-rollout create --provider-namespace "Microsoft.Contoso" --rollout-name "2020week10"
```
##### Show #####
```
az providerhub default-rollout show --provider-namespace "Microsoft.Contoso" --rollout-name "2020week10"
```
##### List #####
```
az providerhub default-rollout list --provider-namespace "Microsoft.Contoso"
```
##### Stop #####
```
az providerhub default-rollout stop --provider-namespace "Microsoft.Contoso" --rollout-name "2020week10"
```
##### Delete #####
```
az providerhub default-rollout delete --provider-namespace "Microsoft.Contoso" --rollout-name "2020week10"
```
#### providerhub manifest ####
##### Checkin #####
```
az providerhub manifest checkin --provider-namespace "Microsoft.Contoso"
```
##### Generate #####
```
az providerhub manifest generate --provider-namespace "Microsoft.Contoso"
```
#### providerhub provider-registration ####
##### Create #####
```
az providerhub provider-registration create --capabilities effect="Allow" quota-id="CSP_2015-05-01" \
    --capabilities effect="Allow" quota-id="CSP_MG_2017-12-01" --incident-contact-email "helpme@contoso.com" \
    --incident-routing-service "Contoso Resource Provider" --incident-routing-team "Contoso Triage" \
    --provider-type "Internal" --provider-version "2.0" --provider-namespace "Microsoft.Contoso"
```
##### Show #####
```
az providerhub provider-registration show --provider-namespace "Microsoft.Contoso"
```
##### List #####
```
az providerhub provider-registration list --resource-group "sampleResourceGroup"
```
##### Generate-operation #####
```
az providerhub provider-registration generate-operation --provider-namespace "Microsoft.Contoso"
```
##### Delete #####
```
az providerhub provider-registration delete --provider-namespace "Microsoft.Contoso"
```
#### providerhub resource-type-registration ####
##### List #####
```
az providerhub resource-type-registration list --provider-namespace "Microsoft.Contoso"
```
##### Show #####
```
az providerhub resource-type-registration show --provider-namespace "Microsoft.Contoso" --resource-type "employees"
```
#### providerhub resource-type-registration ####
##### Create #####
```
az providerhub resource-type-registration create --provider-namespace "Microsoft.Contoso" --resource-type "employees"
```
##### Delete #####
```
az providerhub resource-type-registration delete --provider-namespace "Microsoft.Contoso" \
    --resource-type "testResourceType"
```
