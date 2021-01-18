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
|az providerhub manifest||[commands](#CommandsInManifest)|
|az providerhub provider-registration|ProviderRegistrations|[commands](#CommandsInProviderRegistrations)|
|az providerhub resource-type-registration|ResourceTypeRegistrations|[commands](#CommandsInResourceTypeRegistrations)|
|az providerhub resource-type-registration|ResourceTypeRegistration|[commands](#CommandsInResourceTypeRegistration)|

## COMMANDS
### <a name="CommandsInManifest">Commands in `az providerhub manifest` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az providerhub manifest checkin](#CheckinManifest)|CheckinManifest|[Parameters](#ParametersCheckinManifest)|[Example](#ExamplesCheckinManifest)|
|[az providerhub manifest generate](#GenerateManifest)|GenerateManifest|[Parameters](#ParametersGenerateManifest)|[Example](#ExamplesGenerateManifest)|

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

### <a name="CommandsInProviderRegistrations">Commands in `az providerhub provider-registration` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az providerhub provider-registration list](#ProviderRegistrationsListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersProviderRegistrationsListByResourceGroup)|[Example](#ExamplesProviderRegistrationsListByResourceGroup)|
|[az providerhub provider-registration list](#ProviderRegistrationsList)|List|[Parameters](#ParametersProviderRegistrationsList)|[Example](#ExamplesProviderRegistrationsList)|
|[az providerhub provider-registration show](#ProviderRegistrationsGet)|Get|[Parameters](#ParametersProviderRegistrationsGet)|[Example](#ExamplesProviderRegistrationsGet)|
|[az providerhub provider-registration create](#ProviderRegistrationsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersProviderRegistrationsCreateOrUpdate#Create)|[Example](#ExamplesProviderRegistrationsCreateOrUpdate#Create)|
|[az providerhub provider-registration delete](#ProviderRegistrationsDelete)|Delete|[Parameters](#ParametersProviderRegistrationsDelete)|[Example](#ExamplesProviderRegistrationsDelete)|
|[az providerhub provider-registration generate-operation](#ProviderRegistrationsGenerateOperations)|GenerateOperations|[Parameters](#ParametersProviderRegistrationsGenerateOperations)|[Example](#ExamplesProviderRegistrationsGenerateOperations)|

### <a name="CommandsInResourceTypeRegistrations">Commands in `az providerhub resource-type-registration` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az providerhub resource-type-registration list](#ResourceTypeRegistrationsListByProviderRegistration)|ListByProviderRegistration|[Parameters](#ParametersResourceTypeRegistrationsListByProviderRegistration)|[Example](#ExamplesResourceTypeRegistrationsListByProviderRegistration)|
|[az providerhub resource-type-registration show](#ResourceTypeRegistrationsGet)|Get|[Parameters](#ParametersResourceTypeRegistrationsGet)|[Example](#ExamplesResourceTypeRegistrationsGet)|

### <a name="CommandsInResourceTypeRegistration">Commands in `az providerhub resource-type-registration` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az providerhub resource-type-registration create](#ResourceTypeRegistrationCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersResourceTypeRegistrationCreateOrUpdate#Create)|[Example](#ExamplesResourceTypeRegistrationCreateOrUpdate#Create)|
|[az providerhub resource-type-registration delete](#ResourceTypeRegistrationDelete)|Delete|[Parameters](#ParametersResourceTypeRegistrationDelete)|[Example](#ExamplesResourceTypeRegistrationDelete)|


## COMMAND DETAILS

### group `az providerhub manifest`
#### <a name="CheckinManifest">Command `az providerhub manifest checkin`</a>

##### <a name="ExamplesCheckinManifest">Example</a>
```
az providerhub manifest checkin --provider-namespace "Microsoft.Contoso"
```
##### <a name="ParametersCheckinManifest">Parameters</a>
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--provider-namespace**|string|The name of the resource provider hosted within ProviderHub.|provider_namespace|providerNamespace|
|**--arm-manifest-location**|string|The baseline ARM manifest location supplied to the checkin manifest operation.|arm_manifest_location|baselineArmManifestLocation|
|**--environment**|string|The environment supplied to the checkin manifest operation.|environment|environment|

#### <a name="GenerateManifest">Command `az providerhub manifest generate`</a>

##### <a name="ExamplesGenerateManifest">Example</a>
```
az providerhub manifest generate --provider-namespace "Microsoft.Contoso"
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
az providerhub custom-rollout create --provider-namespace "Microsoft.Contoso" --rollout-name "brazilUsShoeBoxTesting"
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
az providerhub default-rollout show --provider-namespace "Microsoft.Contoso" --rollout-name "2020week10"
```
##### <a name="ParametersDefaultRolloutsGet">Parameters</a>
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--provider-namespace**|string|The name of the resource provider hosted within ProviderHub.|provider_namespace|providerNamespace|
|**--rollout-name**|string|The rollout name.|rollout_name|rolloutName|

#### <a name="DefaultRolloutsCreateOrUpdate#Create">Command `az providerhub default-rollout create`</a>

##### <a name="ExamplesDefaultRolloutsCreateOrUpdate#Create">Example</a>
```
az providerhub default-rollout create --provider-namespace "Microsoft.Contoso" --rollout-name "2020week10"
```
##### <a name="ParametersDefaultRolloutsCreateOrUpdate#Create">Parameters</a>
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--provider-namespace**|string|The name of the resource provider hosted within ProviderHub.|provider_namespace|providerNamespace|
|**--rollout-name**|string|The rollout name.|rollout_name|rolloutName|
|**--row2-wait-duration**|string|The wait duration before the rollout begins in rest of the world two.|rest_of_the_world_group_two|restOfTheWorldGroupTwo|
|**--skip-regions**|string|The canary regions to skip.|skip_regions|skipRegions|

#### <a name="DefaultRolloutsDelete">Command `az providerhub default-rollout delete`</a>

##### <a name="ExamplesDefaultRolloutsDelete">Example</a>
```
az providerhub default-rollout delete --provider-namespace "Microsoft.Contoso" --rollout-name "2020week10"
```
##### <a name="ParametersDefaultRolloutsDelete">Parameters</a>
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--provider-namespace**|string|The name of the resource provider hosted within ProviderHub.|provider_namespace|providerNamespace|
|**--rollout-name**|string|The rollout name.|rollout_name|rolloutName|

#### <a name="DefaultRolloutsStop">Command `az providerhub default-rollout stop`</a>

##### <a name="ExamplesDefaultRolloutsStop">Example</a>
```
az providerhub default-rollout stop --provider-namespace "Microsoft.Contoso" --rollout-name "2020week10"
```
##### <a name="ParametersDefaultRolloutsStop">Parameters</a>
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--provider-namespace**|string|The name of the resource provider hosted within ProviderHub.|provider_namespace|providerNamespace|
|**--rollout-name**|string|The rollout name.|rollout_name|rolloutName|

##### <a name="ExamplesOperationsListByProviderRegistration">Example</a>
```
az providerhub operation list --provider-namespace "Microsoft.Contoso"
```
##### <a name="ParametersOperationsListByProviderRegistration">Parameters</a>
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--provider-namespace**|string|The name of the resource provider hosted within ProviderHub.|provider_namespace|providerNamespace|

### group `az providerhub provider-registration`
#### <a name="ProviderRegistrationsListByResourceGroup">Command `az providerhub provider-registration list`</a>

##### <a name="ExamplesProviderRegistrationsListByResourceGroup">Example</a>
```
az providerhub provider-registration list --resource-group "sampleResourceGroup"
```
##### <a name="ParametersProviderRegistrationsListByResourceGroup">Parameters</a>
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="ProviderRegistrationsList">Command `az providerhub provider-registration list`</a>

##### <a name="ExamplesProviderRegistrationsList">Example</a>
```
az providerhub provider-registration list
```
##### <a name="ParametersProviderRegistrationsList">Parameters</a>
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
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
az providerhub provider-registration create --capabilities effect="Allow" quota-id="CSP_2015-05-01" --capabilities \
effect="Allow" quota-id="CSP_MG_2017-12-01" --incident-contact-email "helpme@contoso.com" --incident-routing-service \
"Contoso Resource Provider" --incident-routing-team "Contoso Triage" --provider-type "Internal" --provider-version \
"2.0" --provider-namespace "Microsoft.Contoso"
```
##### <a name="ParametersProviderRegistrationsCreateOrUpdate#Create">Parameters</a>
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--provider-namespace**|string|The name of the resource provider hosted within ProviderHub.|provider_namespace|providerNamespace|
|**--provider-authentication**|object||provider_authentication|providerAuthentication|
|**--provider-authorizations**|array||provider_authorizations|providerAuthorizations|
|**--provider-version**|string||provider_version|providerVersion|
|**--provider-type**|choice||provider_type|providerType|
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
|**--required-features-policy**|choice||required_features_policy|requiredFeaturesPolicy|
|**--providerhub-metadata-provider-authorizations**|array||provider_hub_metadata_provider_authorizations|providerAuthorizations|
|**--providerhub-metadata-rp-authentication**|object||resource_provider_authentication|providerAuthentication|
|**--lighthouse_authorizations**|array||third_party_provider_authorization|thirdPartyAuthorization|
|**--managed-by-tenant-id**|string||managed_by_tenant_id|managedByTenantId|

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

### group `az providerhub resource-type-registration`
#### <a name="ResourceTypeRegistrationCreateOrUpdate#Create">Command `az providerhub resource-type-registration create`</a>

##### <a name="ExamplesResourceTypeRegistrationCreateOrUpdate#Create">Example</a>
```
az providerhub resource-type-registration create --endpoints api-versions="2020-01-01-preview,2019-01-01" locations="West US, West Central US" required-features="Microsoft.Contoso/RPaaSSampleApp" --regionality \
"regional" --routing-type "Default" --swagger-specifications api-versions="2020-06-01-preview" \
swagger-spec-folder-uri="https://github.com/Azure/azure-rest-api-specs/blob/feature/azure/contoso/specification/contoso\
/resource-manager/Microsoft.SampleRP/" --provider-namespace "Microsoft.Contoso" --resource-type "employees"
```
##### <a name="ParametersResourceTypeRegistrationCreateOrUpdate#Create">Parameters</a>
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--provider-namespace**|string|The name of the resource provider hosted within ProviderHub.|provider_namespace|providerNamespace|
|**--resource-type**|string|The resource type.|resource_type|resourceType|
|**--routing-type**|choice||routing_type|routingType|
|**--regionality**|choice||regionality|regionality|
|**--endpoints**|array||endpoints|endpoints|
|**--resource-patch-begin**|object||resource_patch_begin|resourcePatchBegin|
|**--resource-creation-begin**|object||resource_creation_begin|resourceCreationBegin|
|**--marketplace-type**|choice||marketplace_type|marketplaceType|
|**--swagger-specifications**|array||swagger_specifications|swaggerSpecifications|
|**--allowed-unauthorized-actions**|array||allowed_unauthorized_actions|allowedUnauthorizedActions|
|**--authorization-action-mappings**|array||authorization_action_mappings|authorizationActionMappings|
|**--linked-access-checks**|array||linked_access_checks|linkedAccessChecks|
|**--default-api-version**|string||default_api_version|defaultApiVersion|
|**--logging-rules**|array||logging_rules|loggingRules|
|**--throttling-rules**|array||throttling_rules|throttlingRules|
|**--required-features**|array||required_features|requiredFeatures|
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
|**--required-features-policy**|choice||required_features_policy|requiredFeaturesPolicy|

#### <a name="ResourceTypeRegistrationDelete">Command `az providerhub resource-type-registration delete`</a>

##### <a name="ExamplesResourceTypeRegistrationDelete">Example</a>
```
az providerhub resource-type-registration delete --provider-namespace "Microsoft.Contoso" --resource-type \
"testResourceType"
```
##### <a name="ParametersResourceTypeRegistrationDelete">Parameters</a>
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--provider-namespace**|string|The name of the resource provider hosted within ProviderHub.|provider_namespace|providerNamespace|
|**--resource-type**|string|The resource type.|resource_type|resourceType|
