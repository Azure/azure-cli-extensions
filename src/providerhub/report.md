# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az providerhub|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az providerhub` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az providerhub custom-rollout|CustomRollouts|[commands](#CommandsInCustomRollouts)|
|az providerhub default-rollout|DefaultRollouts|[commands](#CommandsInDefaultRollouts)|
|az providerhub||[commands](#CommandsIn)|
|az providerhub notification-registration|NotificationRegistrations|[commands](#CommandsInNotificationRegistrations)|
|az providerhub operation|Operations|[commands](#CommandsInOperations)|
|az providerhub provider-registration|ProviderRegistrations|[commands](#CommandsInProviderRegistrations)|
|az providerhub resource-type-registration|ResourceTypeRegistrations|[commands](#CommandsInResourceTypeRegistrations)|
|az providerhub sku|Skus|[commands](#CommandsInSkus)|

## COMMANDS
### <a name="CommandsIn">Commands in `az providerhub manifest` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az providerhub manifest generate](#GenerateManifest)|GenerateManifest|[Parameters](#ParametersGenerateManifest)|[Example](#ExamplesGenerateManifest)|
|[az providerhub manifest checkin](#CheckinManifest)|CheckinManifest|[Parameters](#ParametersCheckinManifest)|[Example](#ExamplesCheckinManifest)|

### <a name="CommandsInCustomRollouts">Commands in `az providerhub custom-rollout` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az providerhub custom-rollout list](#CustomRolloutsListByProviderRegistration)|ListByProviderRegistration|[Parameters](#ParametersCustomRolloutsListByProviderRegistration)|[Example](#ExamplesCustomRolloutsListByProviderRegistration)|
|[az providerhub custom-rollout show](#CustomRolloutsGet)|Get|[Parameters](#ParametersCustomRolloutsGet)|[Example](#ExamplesCustomRolloutsGet)|
|[az providerhub custom-rollout create](#CustomRolloutsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersCustomRolloutsCreateOrUpdate#Create)|[Example](#ExamplesCustomRolloutsCreateOrUpdate#Create)|

### <a name="CommandsInDefaultRollouts">Commands in `az providerhub default-rollout` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az providerhub default-rollout list](#DefaultRolloutsListByProviderRegistration)|ListByProviderRegistration|[Parameters](#ParametersDefaultRolloutsListByProviderRegistration)|[Example](#ExamplesDefaultRolloutsListByProviderRegistration)|
|[az providerhub default-rollout show](#DefaultRolloutsGet)|Get|[Parameters](#ParametersDefaultRolloutsGet)|[Example](#ExamplesDefaultRolloutsGet)|
|[az providerhub default-rollout create](#DefaultRolloutsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersDefaultRolloutsCreateOrUpdate#Create)|[Example](#ExamplesDefaultRolloutsCreateOrUpdate#Create)|
|[az providerhub default-rollout delete](#DefaultRolloutsDelete)|Delete|[Parameters](#ParametersDefaultRolloutsDelete)|[Example](#ExamplesDefaultRolloutsDelete)|
|[az providerhub default-rollout stop](#DefaultRolloutsStop)|Stop|[Parameters](#ParametersDefaultRolloutsStop)|[Example](#ExamplesDefaultRolloutsStop)|

### <a name="CommandsInNotificationRegistrations">Commands in `az providerhub notification-registration` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az providerhub notification-registration list](#NotificationRegistrationsListByProviderRegistration)|ListByProviderRegistration|[Parameters](#ParametersNotificationRegistrationsListByProviderRegistration)|[Example](#ExamplesNotificationRegistrationsListByProviderRegistration)|
|[az providerhub notification-registration show](#NotificationRegistrationsGet)|Get|[Parameters](#ParametersNotificationRegistrationsGet)|[Example](#ExamplesNotificationRegistrationsGet)|
|[az providerhub notification-registration create](#NotificationRegistrationsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersNotificationRegistrationsCreateOrUpdate#Create)|[Example](#ExamplesNotificationRegistrationsCreateOrUpdate#Create)|
|[az providerhub notification-registration delete](#NotificationRegistrationsDelete)|Delete|[Parameters](#ParametersNotificationRegistrationsDelete)|[Example](#ExamplesNotificationRegistrationsDelete)|

### <a name="CommandsInOperations">Commands in `az providerhub operation` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az providerhub operation list](#OperationsListByProviderRegistration)|ListByProviderRegistration|[Parameters](#ParametersOperationsListByProviderRegistration)|[Example](#ExamplesOperationsListByProviderRegistration)|
|[az providerhub operation create](#OperationsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersOperationsCreateOrUpdate#Create)|[Example](#ExamplesOperationsCreateOrUpdate#Create)|
|[az providerhub operation delete](#OperationsDelete)|Delete|[Parameters](#ParametersOperationsDelete)|[Example](#ExamplesOperationsDelete)|

### <a name="CommandsInProviderRegistrations">Commands in `az providerhub provider-registration` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az providerhub provider-registration show](#ProviderRegistrationsGet)|Get|[Parameters](#ParametersProviderRegistrationsGet)|[Example](#ExamplesProviderRegistrationsGet)|
|[az providerhub provider-registration create](#ProviderRegistrationsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersProviderRegistrationsCreateOrUpdate#Create)|[Example](#ExamplesProviderRegistrationsCreateOrUpdate#Create)|
|[az providerhub provider-registration delete](#ProviderRegistrationsDelete)|Delete|[Parameters](#ParametersProviderRegistrationsDelete)|[Example](#ExamplesProviderRegistrationsDelete)|
|[az providerhub provider-registration generate-operation](#ProviderRegistrationsGenerateOperations)|GenerateOperations|[Parameters](#ParametersProviderRegistrationsGenerateOperations)|[Example](#ExamplesProviderRegistrationsGenerateOperations)|

### <a name="CommandsInResourceTypeRegistrations">Commands in `az providerhub resource-type-registration` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az providerhub resource-type-registration list](#ResourceTypeRegistrationsListByProviderRegistration)|ListByProviderRegistration|[Parameters](#ParametersResourceTypeRegistrationsListByProviderRegistration)|[Example](#ExamplesResourceTypeRegistrationsListByProviderRegistration)|
|[az providerhub resource-type-registration show](#ResourceTypeRegistrationsGet)|Get|[Parameters](#ParametersResourceTypeRegistrationsGet)|[Example](#ExamplesResourceTypeRegistrationsGet)|
|[az providerhub resource-type-registration create](#ResourceTypeRegistrationsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersResourceTypeRegistrationsCreateOrUpdate#Create)|[Example](#ExamplesResourceTypeRegistrationsCreateOrUpdate#Create)|
|[az providerhub resource-type-registration delete](#ResourceTypeRegistrationsDelete)|Delete|[Parameters](#ParametersResourceTypeRegistrationsDelete)|[Example](#ExamplesResourceTypeRegistrationsDelete)|

### <a name="CommandsInSkus">Commands in `az providerhub sku` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az providerhub sku list](#SkusListByResourceTypeRegistrations)|ListByResourceTypeRegistrations|[Parameters](#ParametersSkusListByResourceTypeRegistrations)|[Example](#ExamplesSkusListByResourceTypeRegistrations)|
|[az providerhub sku show](#SkusGet)|Get|[Parameters](#ParametersSkusGet)|[Example](#ExamplesSkusGet)|
|[az providerhub sku create](#SkusCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersSkusCreateOrUpdate#Create)|[Example](#ExamplesSkusCreateOrUpdate#Create)|
|[az providerhub sku delete](#SkusDelete)|Delete|[Parameters](#ParametersSkusDelete)|[Example](#ExamplesSkusDelete)|


## COMMAND DETAILS

### group `az providerhub`
#### <a name="CheckinManifest">Command `az providerhub checkin-manifest`</a>

##### <a name="ExamplesCheckinManifest">Example</a>
```
az providerhub checkin-manifest --baseline-arm-manifest-location "EastUS2EUAP" --environment "Prod" \
--provider-namespace "Microsoft.Contoso"
```
##### <a name="ParametersCheckinManifest">Parameters</a>
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--provider-namespace**|string|The name of the resource provider hosted within ProviderHub.|provider_namespace|providerNamespace|
|**--environment**|string|The environment supplied to the checkin manifest operation.|environment|environment|
|**--baseline-arm-manifest-location**|string|The baseline ARM manifest location supplied to the checkin manifest operation.|baseline_arm_manifest_location|baselineArmManifestLocation|

#### <a name="GenerateManifest">Command `az providerhub generate-manifest`</a>

##### <a name="ExamplesGenerateManifest">Example</a>
```
az providerhub generate-manifest --provider-namespace "Microsoft.Contoso"
```
##### <a name="ParametersGenerateManifest">Parameters</a>
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--provider-namespace**|string|The name of the resource provider hosted within ProviderHub.|provider_namespace|providerNamespace|

### group `az providerhub custom-rollout`
#### <a name="CustomRolloutsListByProviderRegistration">Command `az providerhub custom-rollout list`</a>

##### <a name="ExamplesCustomRolloutsListByProviderRegistration">Example</a>
```
az providerhub custom-rollout list --provider-namespace "Microsoft.Contoso"
```
##### <a name="ParametersCustomRolloutsListByProviderRegistration">Parameters</a>
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--provider-namespace**|string|The name of the resource provider hosted within ProviderHub.|provider_namespace|providerNamespace|

#### <a name="CustomRolloutsGet">Command `az providerhub custom-rollout show`</a>

##### <a name="ExamplesCustomRolloutsGet">Example</a>
```
az providerhub custom-rollout show --provider-namespace "Microsoft.Contoso" --rollout-name "canaryTesting99"
```
##### <a name="ParametersCustomRolloutsGet">Parameters</a>
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--provider-namespace**|string|The name of the resource provider hosted within ProviderHub.|provider_namespace|providerNamespace|
|**--rollout-name**|string|The rollout name.|rollout_name|rolloutName|

#### <a name="CustomRolloutsCreateOrUpdate#Create">Command `az providerhub custom-rollout create`</a>

##### <a name="ExamplesCustomRolloutsCreateOrUpdate#Create">Example</a>
```
az providerhub custom-rollout create --canary regions="eastus2euap" --provider-namespace "Microsoft.Contoso" \
--rollout-name "customRollout20210601"
```
##### <a name="ParametersCustomRolloutsCreateOrUpdate#Create">Parameters</a>
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--provider-namespace**|string|The name of the resource provider hosted within ProviderHub.|provider_namespace|providerNamespace|
|**--rollout-name**|string|The rollout name.|rollout_name|rolloutName|
|**--canary**|object||canary|canary|

### group `az providerhub default-rollout`
#### <a name="DefaultRolloutsListByProviderRegistration">Command `az providerhub default-rollout list`</a>

##### <a name="ExamplesDefaultRolloutsListByProviderRegistration">Example</a>
```
az providerhub default-rollout list --provider-namespace "Microsoft.Contoso"
```
##### <a name="ParametersDefaultRolloutsListByProviderRegistration">Parameters</a>
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--provider-namespace**|string|The name of the resource provider hosted within ProviderHub.|provider_namespace|providerNamespace|

#### <a name="DefaultRolloutsGet">Command `az providerhub default-rollout show`</a>

##### <a name="ExamplesDefaultRolloutsGet">Example</a>
```
az providerhub default-rollout show --provider-namespace "Microsoft.Contoso" --rollout-name "2021week20"
```
##### <a name="ParametersDefaultRolloutsGet">Parameters</a>
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--provider-namespace**|string|The name of the resource provider hosted within ProviderHub.|provider_namespace|providerNamespace|
|**--rollout-name**|string|The rollout name.|rollout_name|rolloutName|

#### <a name="DefaultRolloutsCreateOrUpdate#Create">Command `az providerhub default-rollout create`</a>

##### <a name="ExamplesDefaultRolloutsCreateOrUpdate#Create">Example</a>
```
az providerhub default-rollout create \
--provider-namespace "Microsoft.Contoso" --rollout-name "2021week20" \
--canary skip-regions="eastus2euap" \
--row2 wait-duration="PT4H"
```
##### <a name="ParametersDefaultRolloutsCreateOrUpdate#Create">Parameters</a>
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--provider-namespace**|string|The name of the resource provider hosted within ProviderHub.|provider_namespace|providerNamespace|
|**--rollout-name**|string|The rollout name.|rollout_name|rolloutName|
|**--canary**|object||canary|canary|
|**--rest-of-the-world-group-two**|object||rest_of_the_world_group_two|restOfTheWorldGroupTwo|

#### <a name="DefaultRolloutsDelete">Command `az providerhub default-rollout delete`</a>

##### <a name="ExamplesDefaultRolloutsDelete">Example</a>
```
az providerhub default-rollout delete --provider-namespace "Microsoft.Contoso" --rollout-name "2021week20"
```
##### <a name="ParametersDefaultRolloutsDelete">Parameters</a>
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--provider-namespace**|string|The name of the resource provider hosted within ProviderHub.|provider_namespace|providerNamespace|
|**--rollout-name**|string|The rollout name.|rollout_name|rolloutName|

#### <a name="DefaultRolloutsStop">Command `az providerhub default-rollout stop`</a>

##### <a name="ExamplesDefaultRolloutsStop">Example</a>
```
az providerhub default-rollout stop --provider-namespace "Microsoft.Contoso" --rollout-name "2021week20"
```
##### <a name="ParametersDefaultRolloutsStop">Parameters</a>
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--provider-namespace**|string|The name of the resource provider hosted within ProviderHub.|provider_namespace|providerNamespace|
|**--rollout-name**|string|The rollout name.|rollout_name|rolloutName|

### group `az providerhub notification-registration`
#### <a name="NotificationRegistrationsListByProviderRegistration">Command `az providerhub notification-registration list`</a>

##### <a name="ExamplesNotificationRegistrationsListByProviderRegistration">Example</a>
```
az providerhub notification-registration list --provider-namespace "Microsoft.Contoso"
```
##### <a name="ParametersNotificationRegistrationsListByProviderRegistration">Parameters</a>
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--provider-namespace**|string|The name of the resource provider hosted within ProviderHub.|provider_namespace|providerNamespace|

#### <a name="NotificationRegistrationsGet">Command `az providerhub notification-registration show`</a>

##### <a name="ExamplesNotificationRegistrationsGet">Example</a>
```
az providerhub notification-registration show --name "fooNotificationRegistration" --provider-namespace \
"Microsoft.Contoso"
```
##### <a name="ParametersNotificationRegistrationsGet">Parameters</a>
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--provider-namespace**|string|The name of the resource provider hosted within ProviderHub.|provider_namespace|providerNamespace|
|**--notification-registration-name**|string|The notification registration.|notification_registration_name|notificationRegistrationName|

#### <a name="NotificationRegistrationsCreateOrUpdate#Create">Command `az providerhub notification-registration create`</a>

##### <a name="ExamplesNotificationRegistrationsCreateOrUpdate#Create">Example</a>
```
az providerhub notification-registration create --name "fooNotificationRegistration" --included-events "*/write" \
"Microsoft.Contoso/employees/delete" --message-scope "RegisteredSubscriptions" --notification-endpoints locations="" \
locations="East US" notification-destination="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/mgmtex\
p-eastus/providers/Microsoft.EventHub/namespaces/unitedstates-mgmtexpint/eventhubs/armlinkednotifications" \
--notification-endpoints locations="North Europe" notification-destination="/subscriptions/00000000-0000-0000-0000-000000000000\
89bf3e88/resourceGroups/mgmtexp-northeurope/providers/Microsoft.EventHub/namespaces/europe-mgmtexpint/eventhubs/armlink\
ednotifications" --notification-mode "EventHub" --provider-namespace "Microsoft.Contoso"
```
##### <a name="ParametersNotificationRegistrationsCreateOrUpdate#Create">Parameters</a>
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--provider-namespace**|string|The name of the resource provider hosted within ProviderHub.|provider_namespace|providerNamespace|
|**--notification-registration-name**|string|The notification registration.|notification_registration_name|notificationRegistrationName|
|**--notification-mode**|choice|The notification mode.|notification_mode|notificationMode|
|**--message-scope**|choice|The message scope.|message_scope|messageScope|
|**--included-events**|array|The included events.|included_events|includedEvents|
|**--notification-endpoints**|array|The notification endpoints.|notification_endpoints|notificationEndpoints|

#### <a name="NotificationRegistrationsDelete">Command `az providerhub notification-registration delete`</a>

##### <a name="ExamplesNotificationRegistrationsDelete">Example</a>
```
az providerhub notification-registration delete --name "fooNotificationRegistration" --provider-namespace \
"Microsoft.Contoso"
```
##### <a name="ParametersNotificationRegistrationsDelete">Parameters</a>
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--provider-namespace**|string|The name of the resource provider hosted within ProviderHub.|provider_namespace|providerNamespace|
|**--notification-registration-name**|string|The notification registration.|notification_registration_name|notificationRegistrationName|

### group `az providerhub operation`
#### <a name="OperationsListByProviderRegistration">Command `az providerhub operation list`</a>

##### <a name="ExamplesOperationsListByProviderRegistration">Example</a>
```
az providerhub operation list --provider-namespace "Microsoft.Contoso"
```
##### <a name="ParametersOperationsListByProviderRegistration">Parameters</a>
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--provider-namespace**|string|The name of the resource provider hosted within ProviderHub.|provider_namespace|providerNamespace|

#### <a name="OperationsCreateOrUpdate#Create">Command `az providerhub operation create`</a>

##### <a name="ExamplesOperationsCreateOrUpdate#Create">Example</a>
```
az providerhub operation create --contents "[{\\"name\\":\\"Microsoft.Contoso/Employees/Read\\",\\"display\\":{\\"descr\
iption\\":\\"Read employees\\",\\"operation\\":\\"Gets/List employee resources\\",\\"provider\\":\\"Microsoft.Contoso\\\
",\\"resource\\":\\"Employees\\"}}]" --provider-namespace "Microsoft.Contoso"
```
##### <a name="ParametersOperationsCreateOrUpdate#Create">Parameters</a>
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--provider-namespace**|string|The name of the resource provider hosted within ProviderHub.|provider_namespace|providerNamespace|
|**--contents**|array||contents|contents|

#### <a name="OperationsDelete">Command `az providerhub operation delete`</a>

##### <a name="ExamplesOperationsDelete">Example</a>
```
az providerhub operation delete --provider-namespace "Microsoft.Contoso"
```
##### <a name="ParametersOperationsDelete">Parameters</a>
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--provider-namespace**|string|The name of the resource provider hosted within ProviderHub.|provider_namespace|providerNamespace|

### group `az providerhub provider-registration`

#### <a name="ProviderRegistrationsGet">Command `az providerhub provider-registration show`</a>

##### <a name="ExamplesProviderRegistrationsGet">Example</a>
```
az providerhub provider-registration show --provider-namespace "Microsoft.Contoso"
```
##### <a name="ParametersProviderRegistrationsGet">Parameters</a>
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--provider-namespace**|string|The name of the resource provider hosted within ProviderHub.|provider_namespace|providerNamespace|

#### <a name="ProviderRegistrationsCreateOrUpdate#Create">Command `az providerhub provider-registration create`</a>

##### <a name="ExamplesProviderRegistrationsCreateOrUpdate#Create">Example</a>
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
##### <a name="ParametersProviderRegistrationsCreateOrUpdate#Create">Parameters</a>
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--provider-namespace**|string|The name of the resource provider hosted within ProviderHub.|provider_namespace|providerNamespace|
|**--provider-authentication**|object||provider_authentication|providerAuthentication|
|**--provider-authorizations**|array||provider_authorizations|providerAuthorizations|
|**--provider-version**|string||provider_version|providerVersion|
|**--provider-type**|choice||provider_type|providerType|
|**--required-features**|array|The required features.|required_features|requiredFeatures|
|**--capabilities**|array||capabilities|capabilities|
|**--metadata**|any|Any object|metadata|metadata|
|**--template-deployment-options**|object||template_deployment_options|templateDeploymentOptions|
|**--schema-owners**|array||schema_owners|schemaOwners|
|**--manifest-owners**|array||manifest_owners|manifestOwners|
|**--incident-routing-service**|string||incident_routing_service|incidentRoutingService|
|**--incident-routing-team**|string||incident_routing_team|incidentRoutingTeam|
|**--incident-contact-email**|string||incident_contact_email|incidentContactEmail|
|**--service-tree-infos**|array||service_tree_infos|serviceTreeInfos|
|**--resource-access-policy**|choice||resource_access_policy|resourceAccessPolicy|
|**--resource-access-roles**|array||resource_access_roles|resourceAccessRoles|
|**--opt-in-headers**|choice||opt_in_headers|optInHeaders|
|**--required-features-policy**|choice||required_features_policy|requiredFeaturesPolicy|
|**--subscription-state-override-actions**|array||subscription_state_override_actions|subscriptionStateOverrideActions|
|**--soft-delete-ttl**|duration|The soft delete time to live.|soft_delete_ttl|softDeleteTTL|
|**--providerhub-metadata-authorizations**|array||providerhub_metadata_authorizations|providerAuthorizations|
|**--providerhub-metadata-authentication**|object||providerhub_metadata_authentication|providerAuthentication|
|**--lighthouse-authorizations**|array|The lighthouse authorizations.|lighthouse_authorizations|authorizations|
|**--managed-by-tenant-id**|string|The managed by tenant identifier.|managed_by_tenant_id|managedByTenantId|

#### <a name="ProviderRegistrationsDelete">Command `az providerhub provider-registration delete`</a>

##### <a name="ExamplesProviderRegistrationsDelete">Example</a>
```
az providerhub provider-registration delete --provider-namespace "Microsoft.Contoso"
```
##### <a name="ParametersProviderRegistrationsDelete">Parameters</a>
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--provider-namespace**|string|The name of the resource provider hosted within ProviderHub.|provider_namespace|providerNamespace|

#### <a name="ProviderRegistrationsGenerateOperations">Command `az providerhub provider-registration generate-operation`</a>

##### <a name="ExamplesProviderRegistrationsGenerateOperations">Example</a>
```
az providerhub provider-registration generate-operation --provider-namespace "Microsoft.Contoso"
```
##### <a name="ParametersProviderRegistrationsGenerateOperations">Parameters</a>
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--provider-namespace**|string|The name of the resource provider hosted within ProviderHub.|provider_namespace|providerNamespace|

### group `az providerhub resource-type-registration`
#### <a name="ResourceTypeRegistrationsListByProviderRegistration">Command `az providerhub resource-type-registration list`</a>

##### <a name="ExamplesResourceTypeRegistrationsListByProviderRegistration">Example</a>
```
az providerhub resource-type-registration list --provider-namespace "Microsoft.Contoso"
```
##### <a name="ParametersResourceTypeRegistrationsListByProviderRegistration">Parameters</a>
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--provider-namespace**|string|The name of the resource provider hosted within ProviderHub.|provider_namespace|providerNamespace|

#### <a name="ResourceTypeRegistrationsGet">Command `az providerhub resource-type-registration show`</a>

##### <a name="ExamplesResourceTypeRegistrationsGet">Example</a>
```
az providerhub resource-type-registration show --provider-namespace "Microsoft.Contoso" --resource-type "employees"
```
##### <a name="ParametersResourceTypeRegistrationsGet">Parameters</a>
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--provider-namespace**|string|The name of the resource provider hosted within ProviderHub.|provider_namespace|providerNamespace|
|**--resource-type**|string|The resource type.|resource_type|resourceType|

#### <a name="ResourceTypeRegistrationsCreateOrUpdate#Create">Command `az providerhub resource-type-registration create`</a>

##### <a name="ExamplesResourceTypeRegistrationsCreateOrUpdate#Create">Example</a>
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
##### <a name="ParametersResourceTypeRegistrationsCreateOrUpdate#Create">Parameters</a>
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--provider-namespace**|string|The name of the resource provider hosted within ProviderHub.|provider_namespace|providerNamespace|
|**--resource-type**|string|The resource type.|resource_type|resourceType|
|**--routing-type**|choice||routing_type|routingType|
|**--regionality**|choice||regionality|regionality|
|**--endpoints**|array||endpoints|endpoints|
|**--marketplace-type**|choice||marketplace_type|marketplaceType|
|**--swagger-specifications**|array||swagger_specifications|swaggerSpecifications|
|**--allowed-unauthorized-actions**|array||allowed_unauthorized_actions|allowedUnauthorizedActions|
|**--authorization-action-mappings**|array||authorization_action_mappings|authorizationActionMappings|
|**--linked-access-checks**|array||linked_access_checks|linkedAccessChecks|
|**--default-api-version**|string||default_api_version|defaultApiVersion|
|**--logging-rules**|array||logging_rules|loggingRules|
|**--throttling-rules**|array||throttling_rules|throttlingRules|
|**--required-features**|array|The required features.|required_features|requiredFeatures|
|**--enable-async-operation**|boolean||enable_async_operation|enableAsyncOperation|
|**--enable-third-party-s2s**|boolean||enable_third_party_s2s|enableThirdPartyS2S|
|**--is-pure-proxy**|boolean||is_pure_proxy|isPureProxy|
|**--identity-management**|object||identity_management|identityManagement|
|**--check-name-availability-specifications**|object||check_name_availability_specifications|checkNameAvailabilitySpecifications|
|**--disallowed-action-verbs**|array||disallowed_action_verbs|disallowedActionVerbs|
|**--service-tree-infos**|array||service_tree_infos|serviceTreeInfos|
|**--subscription-state-rules**|array||subscription_state_rules|subscriptionStateRules|
|**--template-deployment-options**|object||template_deployment_options|templateDeploymentOptions|
|**--extended-locations**|array||extended_locations|extendedLocations|
|**--resource-move-policy**|object||resource_move_policy|resourceMovePolicy|
|**--resource-deletion-policy**|choice||resource_deletion_policy|resourceDeletionPolicy|
|**--opt-in-headers**|choice||opt_in_headers|optInHeaders|
|**--subscription-state-override-actions**|array||subscription_state_override_actions|subscriptionStateOverrideActions|
|**--soft-delete-ttl**|duration|The soft delete time to live.|soft_delete_ttl|softDeleteTTL|
|**--required-features-policy**|choice||required_features_policy|requiredFeaturesPolicy|
|**--resource-creation-begin**|object||resource_creation_begin|resourceCreationBegin|

#### <a name="ResourceTypeRegistrationsDelete">Command `az providerhub resource-type-registration delete`</a>

##### <a name="ExamplesResourceTypeRegistrationsDelete">Example</a>
```
az providerhub resource-type-registration delete --provider-namespace "Microsoft.Contoso" --resource-type \
"testResourceType"
```
##### <a name="ParametersResourceTypeRegistrationsDelete">Parameters</a>
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--provider-namespace**|string|The name of the resource provider hosted within ProviderHub.|provider_namespace|providerNamespace|
|**--resource-type**|string|The resource type.|resource_type|resourceType|

### group `az providerhub sku`

#### <a name="SkusListByResourceTypeRegistrations">Command `az providerhub sku list`</a>

##### <a name="ExamplesSkusListByResourceTypeRegistrations">Example</a>
```
az providerhub sku list --provider-namespace "Microsoft.Contoso" --resource-type "testResourceType"
```
##### <a name="ParametersSkusListByResourceTypeRegistrations">Parameters</a>
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="SkusGet">Command `az providerhub sku show`</a>

##### <a name="ExamplesSkusGet">Example</a>
```
az providerhub sku show --provider-namespace "Microsoft.Contoso" --resource-type "testResourceType" --sku "testSku"
```
##### <a name="ParametersSkusGet">Parameters</a>
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--provider-namespace**|string|The name of the resource provider hosted within ProviderHub.|provider_namespace|providerNamespace|
|**--resource-type**|string|The resource type.|resource_type|resourceType|
|**--sku**|string|The SKU.|sku|sku|

#### <a name="SkusCreateOrUpdate#Create">Command `az providerhub sku create`</a>

##### <a name="ExamplesSkusCreateOrUpdate#Create">Example</a>
```
az providerhub sku create --sku-settings "[{\\"name\\":\\"freeSku\\",\\"kind\\":\\"Standard\\",\\"tier\\":\\"Tier1\\"},\
{\\"name\\":\\"premiumSku\\",\\"costs\\":[{\\"meterId\\":\\"xxx\\"}],\\"kind\\":\\"Premium\\",\\"tier\\":\\"Tier2\\"}]"\
 --provider-namespace "Microsoft.Contoso" --resource-type "testResourceType" --sku "testSku"
```
##### <a name="ParametersSkusCreateOrUpdate#Create">Parameters</a>
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--provider-namespace**|string|The name of the resource provider hosted within ProviderHub.|provider_namespace|providerNamespace|
|**--resource-type**|string|The resource type.|resource_type|resourceType|
|**--sku**|string|The SKU.|sku|sku|
|**--sku-settings**|array||sku_settings|skuSettings|

#### <a name="SkusDelete">Command `az providerhub sku delete`</a>

##### <a name="ExamplesSkusDelete">Example</a>
```
az providerhub sku delete --provider-namespace "Microsoft.Contoso" --resource-type "testResourceType" --sku "testSku"
```
##### <a name="ParametersSkusDelete">Parameters</a>
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--provider-namespace**|string|The name of the resource provider hosted within ProviderHub.|provider_namespace|providerNamespace|
|**--resource-type**|string|The resource type.|resource_type|resourceType|
|**--sku**|string|The SKU.|sku|sku|
