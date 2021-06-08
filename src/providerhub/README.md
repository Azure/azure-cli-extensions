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
    --provider-namespace "Microsoft.Contoso" --rollout-name "canaryTesting99" \
    --canary regions="EastUS2EUAP" regions="centraluseuap"
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
az providerhub default-rollout create --provider-namespace "Microsoft.Contoso" --rollout-name "2021week20"
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

#### providerhub resource-type-registration

##### Create

```
az providerhub resource-type-registration create \
    --resource-type "testResourceType" \
    --endpoints api-versions="2019-01-01" locations="Global" \
    required-features="Microsoft.Contoso/RPaaSSampleApp" \
    extension-endpoint-uri="https://contoso-test-extension-endpoint.com/" \
    extension-categories="ResourceReadValidate" extension-categories="ResourceDeletionValidate" \
    --regionality "Global" \
    --routing-type "ProxyOnly" \
    --swagger-specifications api-versions="2019-01-01" \
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
    swagger-spec-folder-uri="https://github.com/pathtoresourceproviderswaggerspecfolder" \
    --provider-namespace "Microsoft.Contoso"
```

##### Delete

```
az providerhub resource-type-registration delete --provider-namespace "Microsoft.Contoso" \
    --resource-type "testResourceType"
```
