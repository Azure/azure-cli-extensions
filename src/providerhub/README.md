# Azure CLI providerhub Extension

This is the extension for providerhub

### How to use

Install this extension using the below CLI command

```
az extension add --name providerhub
```

### Included Features

#### providerhub custom-rollout

##### Create

```
az providerhub custom-rollout create \
--provider-namespace "Microsoft.DevicePoC" --rollout-name "canaryTesting01" \
--canary regions="centralus" regions="northeurope" regions="westeurope"
```

##### Show

```
az providerhub custom-rollout show --provider-namespace "Microsoft.Contoso" --rollout-name "canaryTesting99"
```

##### List

```
az providerhub custom-rollout list --provider-namespace "Microsoft.Contoso"
```

#### providerhub default-rollout

##### Create

```
az providerhub default-rollout create \
--provider-namespace "Microsoft.Contoso" --rollout-name "2021week20" \
--canary skip-regions="eastus2euap" \
--row2 wait-duration="PT4H"
```

##### Show

```
az providerhub default-rollout show --provider-namespace "Microsoft.Contoso" --rollout-name "2021week20"
```

##### List

```
az providerhub default-rollout list --provider-namespace "Microsoft.Contoso"
```

##### Stop

```
az providerhub default-rollout stop --provider-namespace "Microsoft.Contoso" --rollout-name "2021week20"
```

##### Delete

```
az providerhub default-rollout delete --provider-namespace "Microsoft.Contoso" --rollout-name "2021week20"
```

#### providerhub manifest

##### Checkin

```
az providerhub manifest checkin --provider-namespace "Microsoft.Contoso"
```

##### Generate

```
az providerhub manifest generate --provider-namespace "Microsoft.Contoso"
```

#### providerhub provider-registration

##### Create

```
az providerhub provider-registration create \
--providerhub-metadata-authorizations application-id="00000000-0000-0000-0000-000000000000" \
role-definition-id="00000000-0000-0000-0000-000000000000" \
--providerhub-metadata-authentication allowed-audiences="https://management.core.windows.net/" \
--service-tree-infos service-id="00000000-0000-0000-0000-000000000000" \
component-id="00000000-0000-0000-0000-000000000000" \
--capabilities effect="Allow" quota-id="CSP_2015-05-01" \
--capabilities effect="Allow" quota-id="CSP_MG_2017-12-01" \
--manifest-owners "SPARTA-PlatformServiceAdministrator" \
--incident-contact-email "helpme@contoso.com" \
--incident-routing-service "Contoso Resource Provider" \
--incident-routing-team "Contoso Triage" \
--provider-type "Internal" \
--provider-version "2.0" \
--provider-namespace "Microsoft.Contoso"
```

##### Show

```
az providerhub provider-registration show --provider-namespace "Microsoft.Contoso"
```

##### List

```
az providerhub provider-registration list --resource-group "sampleResourceGroup"
```

##### Generate-operation

```
az providerhub provider-registration generate-operation --provider-namespace "Microsoft.Contoso"
```

##### Delete

```
az providerhub provider-registration delete --provider-namespace "Microsoft.Contoso"
```

#### providerhub resource-type-registration

##### List

```
az providerhub resource-type-registration list --provider-namespace "Microsoft.Contoso"
```

##### Show

```
az providerhub resource-type-registration show --provider-namespace "Microsoft.Contoso" --resource-type "testResourceType"
```

##### Create

```
az providerhub resource-type-registration create \
--resource-type "testResourceType" \
--endpoints api-versions="2018-11-01-preview" api-versions="2020-01-01-preview" api-versions="2019-01-01" locations="West US" locations="North Europe" \
required-features="Microsoft.Contoso/RPaaSSampleApp" \
extension-endpoint-uri="https://contoso-test-extension-endpoint.com/" \
extension-categories="ResourceReadValidate" extension-categories="ResourceDeletionValidate" \
--regionality "Regional" \
--routing-type "ProxyOnly" \
--swagger-specifications api-versions="2018-11-01-preview" api-versions="2020-01-01-preview" api-versions="2019-01-01" \
swagger-spec-folder-uri="https://github.com/pathtoresourceproviderswaggerspecfolder" \
--provider-namespace "Microsoft.Contoso" \
--enable-async-operation false \
--template-deployment-options preflight-supported="true" \
preflight-options="DefaultValidationOnly" preflight-options="continueDeploymentOnFailure"
```

```
az providerhub resource-type-registration create \
--resource-type "testResourceType/nestedResourceType" \
--endpoints api-versions="2019-01-01" locations="Global" \
required-features="Microsoft.Contoso/RPaaSSampleApp" \
extensions=[{{\\"endpointUri\\":\\"https://contoso-test-extension-endpoint.com/\\",\\"extensionCategories\\":[\\"ResourceReadValidate\\",\\"ResourceDeletionValidate\\"]}}] \
--regionality "Global" \
--routing-type "ProxyOnly" \
--swagger-specifications api-versions="2019-01-01" \
swagger-spec-folder-uri="https://github.com/Azuew/pathtoresourceproviderswaggerspecfolder" \
--provider-namespace "Microsoft.Contoso"
```

##### Delete

```
az providerhub resource-type-registration delete \
--provider-namespace "Microsoft.Contoso" \
--resource-type "testResourceType"
```

#### providerhub notification-registration

##### Create

```
az providerhub notification-registration create \
--name "notificationRegistrationName" \
--included-events "*/write" "Microsoft.Contoso/employees/delete" \
--message-scope "RegisteredSubscriptions" \
--notification-endpoints locations="" locations="East US" notification-destination="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/mgmtexp-eastus/providers/Microsoft.EventHub/namespaces/unitedstates-mgmtexpint/eventhubs/armlinkednotifications" \
--notification-endpoints locations="East US" notification-destination="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/providers/Microsoft.EventHub/namespaces/europe-mgmtexpint/eventhubs/armlinkednotifications" \
--notification-mode "EventHub" \
--provider-namespace "Microsoft.Contoso"
```

#### Show

```
az providerhub notification-registration show \
--name "notificationRegistrationName" \
--provider-namespace "Microsoft.Contoso"
```

#### List

```
az providerhub notification-registration list \
--provider-namespace "Microsoft.Contoso"
```

#### Delete

```
az providerhub notification-registration delete -y \
--name "notificationRegistrationName" \
--provider-namespace "Microsoft.Contoso"
```

### providerhub operation

#### Create

```
az providerhub operation create \
--contents "[{{\\"name\\":\\"Microsoft.Contoso/testResource/Read\\",\\"display\\":{{\\"description\\":\\"Read testResource\\",\\"operation\\":\\"Gets/List testResource resources\\",\\"provider\\":\\"Microsoft.Contoso\\",\\"resource\\":\\"testResource\\"}}}}]" \
--provider-namespace "Microsoft.Contoso"
```

#### List

```
az providerhub operation list \
--provider-namespace "Microsoft.Contoso"
```

#### Delete

```
az providerhub operation delete -y \
--provider-namespace "Microsoft.Contoso"
```

### providerhub sku

#### Create

```
az providerhub sku create \
--sku-settings "[{{\\"name\\":\\"freeSku\\",\\"kind\\":\\"Standard\\",\\"tier\\":\\"Tier1\\"}},{{\\"name\\":\\"premiumSku\\",\\"costs\\":[{{\\"meterId\\":\\"xxx\\"}}],\\"kind\\":\\"Premium\\",\\"tier\\":\\"Tier2\\"}}]" \
--provider-namespace "Microsoft.Contoso" \
--resource-type "resourceTypeName" \
--sku "skuName"
```

#### Show

```
az providerhub sku show \
--provider-namespace "Microsoft.Contoso" \
--resource-type "resourceTypeName" \
--sku "skuName"
```

#### List

```
az providerhub sku list \
--provider-namespace "Microsoft.Contoso" \
--resource-type "resourceTypeName"
```

#### Delete

```
az providerhub sku delete -y \
--provider-namespace "Microsoft.Contoso" \
--resource-type "resourceTypeName" \
--sku "skuName"
```
