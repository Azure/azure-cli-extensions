# Azure CLI devops Extension #
This is the extension for devops

### How to use ###
Install this extension using the below CLI command
```
az extension add --name devops
```

### Included Features ###
#### devops pipeline-template-definition ####
##### List #####
```
az devops pipeline-template-definition list
```
#### devops pipeline ####
##### Create #####
```
az devops pipeline create --location "South India" \
    --bootstrap-configuration-repository-properties bootstrapConfiguration={"template":{"id":"ms.vss-continuous-delivery-pipeline-templates.aspnet-windowswebapp","parameters":{"appInsightLocation":"South India","appServicePlan":"S1 Standard","azureAuth":"{\\"scheme\\":\\"ServicePrincipal\\",\\"parameters\\":{\\"tenantid\\":\\"{subscriptionTenantId}\\",\\"objectid\\":\\"{appObjectId}\\",\\"serviceprincipalid\\":\\"{appId}\\",\\"serviceprincipalkey\\":\\"{appSecret}\\"}}","location":"South India","resourceGroup":"myAspNetWebAppPipeline-rg","subscriptionId":"{subscriptionId}","webAppName":"myAspNetWebApp"}}} organization={"name":"myAspNetWebAppPipeline-org"} project={"name":"myAspNetWebAppPipeline-project"} \
    --name "myAspNetWebAppPipeline" --resource-group "myAspNetWebAppPipeline-rg" 
```
##### Show #####
```
az devops pipeline show --name "myAspNetWebAppPipeline" --resource-group "myAspNetWebAppPipeline-rg"
```
##### List #####
```
az devops pipeline list --resource-group "myAspNetWebAppPipeline-rg"
```
##### Update #####
```
az devops pipeline update --name "myAspNetWebAppPipeline" --resource-group "myAspNetWebAppPipeline-rg" \
    --tags tagKey="tagvalue" 
```
##### Delete #####
```
az devops pipeline delete --name "myAspNetWebAppPipeline" --resource-group "myAspNetWebAppPipeline-rg"
```