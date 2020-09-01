# Azure CLI Module Creation Report

### logic integration-account create

create a logic integration-account.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--location**|string|The resource location.|location|
|**--tags**|dictionary|The resource tags.|tags|
|**--sku-name**|choice|The sku name.|name_sku_name|
|**--integration-service-environment**|object|The integration service environment.|integration_service_environment|
|**--state**|choice|The workflow state.|state|
### logic integration-account delete

delete a logic integration-account.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
### logic integration-account list

list a logic integration-account.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--top**|integer|The number of items to be included in the result.|top|
### logic integration-account list-callback-url

list-callback-url a logic integration-account.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--not-after**|date-time|The expiry time.|not_after|
|**--key-type**|choice|The key type.|key_type|
### logic integration-account list-key-vault-key

list-key-vault-key a logic integration-account.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--skip-token**|string|The skip token.|skip_token|
|**--key-vault-id**|string|The resource id.|id_properties_integration_service_environment_id|
### logic integration-account log-tracking-event

log-tracking-event a logic integration-account.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--source-type**|string|The source type.|source_type|
|**--events**|array|The events.|events|
|**--track-events-options**|choice|The track events options.|track_events_options|
### logic integration-account regenerate-access-key

regenerate-access-key a logic integration-account.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--key-type**|choice|The key type.|key_type|
### logic integration-account show

show a logic integration-account.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
### logic integration-account update

update a logic integration-account.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--location**|string|The resource location.|location|
|**--tags**|dictionary|The resource tags.|tags|
|**--sku-name**|choice|The sku name.|name_sku_name|
|**--integration-service-environment**|object|The integration service environment.|integration_service_environment|
|**--state**|choice|The workflow state.|state|
### logic integration-account-agreement create

create a logic integration-account-agreement.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--agreement-name**|string|The integration account agreement name.|agreement_name|
|**--agreement-type**|sealed-choice|The agreement type.|agreement_type|
|**--host-partner**|string|The integration account partner that is set as host partner for this agreement.|host_partner|
|**--guest-partner**|string|The integration account partner that is set as guest partner for this agreement.|guest_partner|
|**--host-identity**|object|The business identity of the host partner.|host_identity|
|**--guest-identity**|object|The business identity of the guest partner.|guest_identity|
|**--content**|object|The agreement content.|content|
|**--location**|string|The resource location.|location|
|**--tags**|dictionary|The resource tags.|tags|
|**--metadata**|any|The metadata.|metadata|
### logic integration-account-agreement delete

delete a logic integration-account-agreement.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--agreement-name**|string|The integration account agreement name.|agreement_name|
### logic integration-account-agreement list

list a logic integration-account-agreement.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--top**|integer|The number of items to be included in the result.|top|
|**--filter**|string|The filter to apply on the operation. Options for filters include: AgreementType.|filter|
### logic integration-account-agreement list-content-callback-url

list-content-callback-url a logic integration-account-agreement.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--agreement-name**|string|The integration account agreement name.|agreement_name|
|**--not-after**|date-time|The expiry time.|not_after|
|**--key-type**|choice|The key type.|key_type|
### logic integration-account-agreement show

show a logic integration-account-agreement.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--agreement-name**|string|The integration account agreement name.|agreement_name|
### logic integration-account-agreement update

create a logic integration-account-agreement.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--agreement-name**|string|The integration account agreement name.|agreement_name|
|**--agreement-type**|sealed-choice|The agreement type.|agreement_type|
|**--host-partner**|string|The integration account partner that is set as host partner for this agreement.|host_partner|
|**--guest-partner**|string|The integration account partner that is set as guest partner for this agreement.|guest_partner|
|**--host-identity**|object|The business identity of the host partner.|host_identity|
|**--guest-identity**|object|The business identity of the guest partner.|guest_identity|
|**--content**|object|The agreement content.|content|
|**--location**|string|The resource location.|location|
|**--tags**|dictionary|The resource tags.|tags|
|**--metadata**|any|The metadata.|metadata|
### logic integration-account-assembly create

create a logic integration-account-assembly.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--assembly-artifact-name**|string|The assembly artifact name.|assembly_artifact_name|
|**--properties**|object|The assembly properties.|properties|
|**--location**|string|The resource location.|location|
|**--tags**|dictionary|The resource tags.|tags|
### logic integration-account-assembly delete

delete a logic integration-account-assembly.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--assembly-artifact-name**|string|The assembly artifact name.|assembly_artifact_name|
### logic integration-account-assembly list

list a logic integration-account-assembly.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
### logic integration-account-assembly list-content-callback-url

list-content-callback-url a logic integration-account-assembly.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--assembly-artifact-name**|string|The assembly artifact name.|assembly_artifact_name|
### logic integration-account-assembly show

show a logic integration-account-assembly.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--assembly-artifact-name**|string|The assembly artifact name.|assembly_artifact_name|
### logic integration-account-assembly update

create a logic integration-account-assembly.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--assembly-artifact-name**|string|The assembly artifact name.|assembly_artifact_name|
|**--properties**|object|The assembly properties.|properties|
|**--location**|string|The resource location.|location|
|**--tags**|dictionary|The resource tags.|tags|
### logic integration-account-batch-configuration create

create a logic integration-account-batch-configuration.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--batch-configuration-name**|string|The batch configuration name.|batch_configuration_name|
|**--batch-group-name**|string|The name of the batch group.|batch_group_name|
|**--location**|string|The resource location.|location|
|**--tags**|dictionary|The resource tags.|tags|
|**--created-time**|date-time|The artifact creation time.|created_time|
|**--changed-time**|date-time|The artifact changed time.|changed_time|
|**--metadata**|any|Any object|metadata|
|**--release-criteria-message-count**|integer|The message count.|message_count|
|**--release-criteria-batch-size**|integer|The batch size in bytes.|batch_size|
|**--release-criteria-recurrence-frequency**|choice|The frequency.|frequency|
|**--release-criteria-recurrence-interval**|integer|The interval.|interval|
|**--release-criteria-recurrence-start-time**|string|The start time.|start_time|
|**--release-criteria-recurrence-end-time**|string|The end time.|end_time|
|**--release-criteria-recurrence-time-zone**|string|The time zone.|time_zone|
|**--release-criteria-recurrence-schedule-minutes**|array|The minutes.|minutes|
|**--release-criteria-recurrence-schedule-hours**|array|The hours.|hours|
|**--release-criteria-recurrence-schedule-week-days**|array|The days of the week.|week_days|
|**--release-criteria-recurrence-schedule-month-days**|array|The month days.|month_days|
|**--release-criteria-recurrence-schedule-monthly-occurrences**|array|The monthly occurrences.|monthly_occurrences|
### logic integration-account-batch-configuration delete

delete a logic integration-account-batch-configuration.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--batch-configuration-name**|string|The batch configuration name.|batch_configuration_name|
### logic integration-account-batch-configuration list

list a logic integration-account-batch-configuration.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
### logic integration-account-batch-configuration show

show a logic integration-account-batch-configuration.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--batch-configuration-name**|string|The batch configuration name.|batch_configuration_name|
### logic integration-account-batch-configuration update

create a logic integration-account-batch-configuration.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--batch-configuration-name**|string|The batch configuration name.|batch_configuration_name|
|**--batch-group-name**|string|The name of the batch group.|batch_group_name|
|**--location**|string|The resource location.|location|
|**--tags**|dictionary|The resource tags.|tags|
|**--created-time**|date-time|The artifact creation time.|created_time|
|**--changed-time**|date-time|The artifact changed time.|changed_time|
|**--metadata**|any|Any object|metadata|
|**--release-criteria-message-count**|integer|The message count.|message_count|
|**--release-criteria-batch-size**|integer|The batch size in bytes.|batch_size|
|**--release-criteria-recurrence-frequency**|choice|The frequency.|frequency|
|**--release-criteria-recurrence-interval**|integer|The interval.|interval|
|**--release-criteria-recurrence-start-time**|string|The start time.|start_time|
|**--release-criteria-recurrence-end-time**|string|The end time.|end_time|
|**--release-criteria-recurrence-time-zone**|string|The time zone.|time_zone|
|**--release-criteria-recurrence-schedule-minutes**|array|The minutes.|minutes|
|**--release-criteria-recurrence-schedule-hours**|array|The hours.|hours|
|**--release-criteria-recurrence-schedule-week-days**|array|The days of the week.|week_days|
|**--release-criteria-recurrence-schedule-month-days**|array|The month days.|month_days|
|**--release-criteria-recurrence-schedule-monthly-occurrences**|array|The monthly occurrences.|monthly_occurrences|
### logic integration-account-certificate create

create a logic integration-account-certificate.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--certificate-name**|string|The integration account certificate name.|certificate_name|
|**--location**|string|The resource location.|location|
|**--tags**|dictionary|The resource tags.|tags|
|**--metadata**|any|The metadata.|metadata|
|**--public-certificate**|string|The public certificate.|public_certificate|
|**--key-key-vault**|object|The key vault reference.|key_vault|
|**--key-key-name**|string|The private key name in key vault.|key_name|
|**--key-key-version**|string|The private key version in key vault.|key_version|
### logic integration-account-certificate delete

delete a logic integration-account-certificate.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--certificate-name**|string|The integration account certificate name.|certificate_name|
### logic integration-account-certificate list

list a logic integration-account-certificate.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--top**|integer|The number of items to be included in the result.|top|
### logic integration-account-certificate show

show a logic integration-account-certificate.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--certificate-name**|string|The integration account certificate name.|certificate_name|
### logic integration-account-certificate update

create a logic integration-account-certificate.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--certificate-name**|string|The integration account certificate name.|certificate_name|
|**--location**|string|The resource location.|location|
|**--tags**|dictionary|The resource tags.|tags|
|**--metadata**|any|The metadata.|metadata|
|**--public-certificate**|string|The public certificate.|public_certificate|
|**--key-key-vault**|object|The key vault reference.|key_vault|
|**--key-key-name**|string|The private key name in key vault.|key_name|
|**--key-key-version**|string|The private key version in key vault.|key_version|
### logic integration-account-map create

create a logic integration-account-map.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--map-name**|string|The integration account map name.|map_name|
|**--map-type**|choice|The map type.|map_type|
|**--location**|string|The resource location.|location|
|**--tags**|dictionary|The resource tags.|tags|
|**--content**|string|The content.|content|
|**--properties-content-type**|string|The content type.|content_type|
|**--metadata**|any|The metadata.|metadata|
|**--parameters-schema-ref**|string|The reference name.|ref|
### logic integration-account-map delete

delete a logic integration-account-map.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--map-name**|string|The integration account map name.|map_name|
### logic integration-account-map list

list a logic integration-account-map.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--top**|integer|The number of items to be included in the result.|top|
|**--filter**|string|The filter to apply on the operation. Options for filters include: MapType.|filter|
### logic integration-account-map list-content-callback-url

list-content-callback-url a logic integration-account-map.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--map-name**|string|The integration account map name.|map_name|
|**--not-after**|date-time|The expiry time.|not_after|
|**--key-type**|choice|The key type.|key_type|
### logic integration-account-map show

show a logic integration-account-map.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--map-name**|string|The integration account map name.|map_name|
### logic integration-account-map update

create a logic integration-account-map.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--map-name**|string|The integration account map name.|map_name|
|**--map-type**|choice|The map type.|map_type|
|**--location**|string|The resource location.|location|
|**--tags**|dictionary|The resource tags.|tags|
|**--content**|string|The content.|content|
|**--properties-content-type**|string|The content type.|content_type|
|**--metadata**|any|The metadata.|metadata|
|**--parameters-schema-ref**|string|The reference name.|ref|
### logic integration-account-partner create

create a logic integration-account-partner.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--partner-name**|string|The integration account partner name.|partner_name|
|**--partner-type**|choice|The partner type.|partner_type|
|**--location**|string|The resource location.|location|
|**--tags**|dictionary|The resource tags.|tags|
|**--metadata**|any|The metadata.|metadata|
|**--content-b2b-business-identities**|array|The list of partner business identities.|business_identities|
### logic integration-account-partner delete

delete a logic integration-account-partner.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--partner-name**|string|The integration account partner name.|partner_name|
### logic integration-account-partner list

list a logic integration-account-partner.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--top**|integer|The number of items to be included in the result.|top|
|**--filter**|string|The filter to apply on the operation. Options for filters include: PartnerType.|filter|
### logic integration-account-partner list-content-callback-url

list-content-callback-url a logic integration-account-partner.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--partner-name**|string|The integration account partner name.|partner_name|
|**--not-after**|date-time|The expiry time.|not_after|
|**--key-type**|choice|The key type.|key_type|
### logic integration-account-partner show

show a logic integration-account-partner.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--partner-name**|string|The integration account partner name.|partner_name|
### logic integration-account-partner update

create a logic integration-account-partner.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--partner-name**|string|The integration account partner name.|partner_name|
|**--partner-type**|choice|The partner type.|partner_type|
|**--location**|string|The resource location.|location|
|**--tags**|dictionary|The resource tags.|tags|
|**--metadata**|any|The metadata.|metadata|
|**--content-b2b-business-identities**|array|The list of partner business identities.|business_identities|
### logic integration-account-schema create

create a logic integration-account-schema.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--schema-name**|string|The integration account schema name.|schema_name|
|**--schema-type**|choice|The schema type.|schema_type|
|**--location**|string|The resource location.|location|
|**--tags**|dictionary|The resource tags.|tags|
|**--target-namespace**|string|The target namespace of the schema.|target_namespace|
|**--document-name**|string|The document name.|document_name|
|**--file-name**|string|The file name.|file_name|
|**--metadata**|any|The metadata.|metadata|
|**--content**|string|The content.|content|
|**--properties-content-type**|string|The content type.|content_type|
### logic integration-account-schema delete

delete a logic integration-account-schema.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--schema-name**|string|The integration account schema name.|schema_name|
### logic integration-account-schema list

list a logic integration-account-schema.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--top**|integer|The number of items to be included in the result.|top|
|**--filter**|string|The filter to apply on the operation. Options for filters include: SchemaType.|filter|
### logic integration-account-schema list-content-callback-url

list-content-callback-url a logic integration-account-schema.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--schema-name**|string|The integration account schema name.|schema_name|
|**--not-after**|date-time|The expiry time.|not_after|
|**--key-type**|choice|The key type.|key_type|
### logic integration-account-schema show

show a logic integration-account-schema.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--schema-name**|string|The integration account schema name.|schema_name|
### logic integration-account-schema update

create a logic integration-account-schema.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--schema-name**|string|The integration account schema name.|schema_name|
|**--schema-type**|choice|The schema type.|schema_type|
|**--location**|string|The resource location.|location|
|**--tags**|dictionary|The resource tags.|tags|
|**--target-namespace**|string|The target namespace of the schema.|target_namespace|
|**--document-name**|string|The document name.|document_name|
|**--file-name**|string|The file name.|file_name|
|**--metadata**|any|The metadata.|metadata|
|**--content**|string|The content.|content|
|**--properties-content-type**|string|The content type.|content_type|
### logic integration-account-session create

create a logic integration-account-session.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--session-name**|string|The integration account session name.|session_name|
|**--location**|string|The resource location.|location|
|**--tags**|dictionary|The resource tags.|tags|
|**--content**|any|The session content.|content|
### logic integration-account-session delete

delete a logic integration-account-session.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--session-name**|string|The integration account session name.|session_name|
### logic integration-account-session list

list a logic integration-account-session.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--top**|integer|The number of items to be included in the result.|top|
|**--filter**|string|The filter to apply on the operation. Options for filters include: ChangedTime.|filter|
### logic integration-account-session show

show a logic integration-account-session.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--session-name**|string|The integration account session name.|session_name|
### logic integration-account-session update

create a logic integration-account-session.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--integration-account-name**|string|The integration account name.|integration_account_name|
|**--session-name**|string|The integration account session name.|session_name|
|**--location**|string|The resource location.|location|
|**--tags**|dictionary|The resource tags.|tags|
|**--content**|any|The session content.|content|
### logic integration-service-environment create

create a logic integration-service-environment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|string|The resource group.|resource_group|
|**--integration-service-environment-name**|string|The integration service environment name.|integration_service_environment_name|
|**--location**|string|The resource location.|location|
|**--tags**|dictionary|The resource tags.|tags|
|**--sku**|object|The sku.|sku|
|**--provisioning-state**|choice|The provisioning state.|provisioning_state|
|**--state**|choice|The integration service environment state.|state|
|**--integration-service-environment-id**|string|Gets the tracking id.|integration_service_environment_id|
|**--endpoints-configuration**|object|The endpoints configuration.|endpoints_configuration|
|**--network-configuration**|object|The network configuration.|network_configuration|
### logic integration-service-environment delete

delete a logic integration-service-environment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|string|The resource group.|resource_group|
|**--integration-service-environment-name**|string|The integration service environment name.|integration_service_environment_name|
### logic integration-service-environment list

list a logic integration-service-environment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|string|The resource group.|resource_group|
|**--top**|integer|The number of items to be included in the result.|top|
### logic integration-service-environment restart

restart a logic integration-service-environment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|string|The resource group.|resource_group|
|**--integration-service-environment-name**|string|The integration service environment name.|integration_service_environment_name|
### logic integration-service-environment show

show a logic integration-service-environment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|string|The resource group.|resource_group|
|**--integration-service-environment-name**|string|The integration service environment name.|integration_service_environment_name|
### logic integration-service-environment update

update a logic integration-service-environment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|string|The resource group.|resource_group|
|**--integration-service-environment-name**|string|The integration service environment name.|integration_service_environment_name|
|**--location**|string|The resource location.|location|
|**--tags**|dictionary|The resource tags.|tags|
|**--sku**|object|The sku.|sku|
|**--provisioning-state**|choice|The provisioning state.|provisioning_state|
|**--state**|choice|The integration service environment state.|state|
|**--integration-service-environment-id**|string|Gets the tracking id.|integration_service_environment_id|
|**--endpoints-configuration**|object|The endpoints configuration.|endpoints_configuration|
|**--network-configuration**|object|The network configuration.|network_configuration|
### logic integration-service-environment-managed-api delete

delete a logic integration-service-environment-managed-api.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|string|The resource group.|resource_group|
|**--integration-service-environment-name**|string|The integration service environment name.|integration_service_environment_name|
|**--api-name**|string|The api name.|api_name|
### logic integration-service-environment-managed-api list

list a logic integration-service-environment-managed-api.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|string|The resource group.|resource_group|
|**--integration-service-environment-name**|string|The integration service environment name.|integration_service_environment_name|
### logic integration-service-environment-managed-api put

put a logic integration-service-environment-managed-api.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|string|The resource group name.|resource_group|
|**--integration-service-environment-name**|string|The integration service environment name.|integration_service_environment_name|
|**--api-name**|string|The api name.|api_name|
### logic integration-service-environment-managed-api show

show a logic integration-service-environment-managed-api.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|string|The resource group name.|resource_group|
|**--integration-service-environment-name**|string|The integration service environment name.|integration_service_environment_name|
|**--api-name**|string|The api name.|api_name|
### logic integration-service-environment-managed-api-operation list

list a logic integration-service-environment-managed-api-operation.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|string|The resource group.|resource_group|
|**--integration-service-environment-name**|string|The integration service environment name.|integration_service_environment_name|
|**--api-name**|string|The api name.|api_name|
### logic integration-service-environment-network-health show

show a logic integration-service-environment-network-health.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|string|The resource group.|resource_group|
|**--integration-service-environment-name**|string|The integration service environment name.|integration_service_environment_name|
### logic integration-service-environment-sku list

list a logic integration-service-environment-sku.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|string|The resource group.|resource_group|
|**--integration-service-environment-name**|string|The integration service environment name.|integration_service_environment_name|
### logic workflow create

create a logic workflow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
|**--location**|string|The resource location.|location|
|**--tags**|dictionary|The resource tags.|tags|
|**--state**|choice|The state.|state|
|**--definition**|any|The definition.|definition|
|**--parameters**|dictionary|The parameters.|parameters|
|**--integration-service-environment-id**|string|The resource id.|id_properties_integration_service_environment_id|
|**--integration-account-id**|string|The resource id.|id_properties_integration_service_environment_id|
|**--access-control-triggers**|object|The access control configuration for invoking workflow triggers.|triggers|
|**--access-control-contents**|object|The access control configuration for accessing workflow run contents.|contents|
|**--access-control-actions**|object|The access control configuration for workflow actions.|actions|
|**--access-control-workflow-management**|object|The access control configuration for workflow management.|workflow_management|
|**--endpoints-configuration-workflow**|object|The workflow endpoints.|workflow|
|**--endpoints-configuration-connector**|object|The connector endpoints.|connector|
### logic workflow delete

delete a logic workflow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
### logic workflow disable

disable a logic workflow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
### logic workflow enable

enable a logic workflow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
### logic workflow generate-upgraded-definition

generate-upgraded-definition a logic workflow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
|**--target-schema-version**|string|The target schema version.|target_schema_version|
### logic workflow list

list a logic workflow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--top**|integer|The number of items to be included in the result.|top|
|**--filter**|string|The filter to apply on the operation. Options for filters include: State, Trigger, and ReferencedResourceId.|filter|
### logic workflow list-callback-url

list-callback-url a logic workflow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
|**--not-after**|date-time|The expiry time.|not_after|
|**--key-type**|choice|The key type.|key_type|
### logic workflow list-swagger

list-swagger a logic workflow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
### logic workflow move

move a logic workflow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
|**--id-properties-integration-service-environment-id**|string|The resource id.|id_properties_integration_service_environment_id|
### logic workflow regenerate-access-key

regenerate-access-key a logic workflow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
|**--key-type**|choice|The key type.|key_type|
### logic workflow show

show a logic workflow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
### logic workflow update

update a logic workflow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
### logic workflow validate-by-location

validate-by-location a logic workflow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--location**|string|The workflow location.|location|
|**--workflow-name**|string|The workflow name.|workflow_name|
|**--location**|string|The resource location.|location|
|**--tags**|dictionary|The resource tags.|tags|
|**--state**|choice|The state.|state|
|**--definition**|any|The definition.|definition|
|**--parameters**|dictionary|The parameters.|parameters|
|**--integration-service-environment-id**|string|The resource id.|id_properties_integration_service_environment_id|
|**--integration-account-id**|string|The resource id.|id_properties_integration_service_environment_id|
|**--access-control-triggers**|object|The access control configuration for invoking workflow triggers.|triggers|
|**--access-control-contents**|object|The access control configuration for accessing workflow run contents.|contents|
|**--access-control-actions**|object|The access control configuration for workflow actions.|actions|
|**--access-control-workflow-management**|object|The access control configuration for workflow management.|workflow_management|
|**--endpoints-configuration-workflow**|object|The workflow endpoints.|workflow|
|**--endpoints-configuration-connector**|object|The connector endpoints.|connector|
### logic workflow validate-by-resource-group

validate-by-resource-group a logic workflow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
|**--location**|string|The resource location.|location|
|**--tags**|dictionary|The resource tags.|tags|
|**--state**|choice|The state.|state|
|**--definition**|any|The definition.|definition|
|**--parameters**|dictionary|The parameters.|parameters|
|**--integration-service-environment-id**|string|The resource id.|id_properties_integration_service_environment_id|
|**--integration-account-id**|string|The resource id.|id_properties_integration_service_environment_id|
|**--access-control-triggers**|object|The access control configuration for invoking workflow triggers.|triggers|
|**--access-control-contents**|object|The access control configuration for accessing workflow run contents.|contents|
|**--access-control-actions**|object|The access control configuration for workflow actions.|actions|
|**--access-control-workflow-management**|object|The access control configuration for workflow management.|workflow_management|
|**--endpoints-configuration-workflow**|object|The workflow endpoints.|workflow|
|**--endpoints-configuration-connector**|object|The connector endpoints.|connector|
### logic workflow-run cancel

cancel a logic workflow-run.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
|**--run-name**|string|The workflow run name.|run_name|
### logic workflow-run list

list a logic workflow-run.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
|**--top**|integer|The number of items to be included in the result.|top|
|**--filter**|string|The filter to apply on the operation. Options for filters include: Status, StartTime, and ClientTrackingId.|filter|
### logic workflow-run show

show a logic workflow-run.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
|**--run-name**|string|The workflow run name.|run_name|
### logic workflow-run-action list

list a logic workflow-run-action.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
|**--run-name**|string|The workflow run name.|run_name|
|**--top**|integer|The number of items to be included in the result.|top|
|**--filter**|string|The filter to apply on the operation. Options for filters include: Status.|filter|
### logic workflow-run-action list-expression-trace

list-expression-trace a logic workflow-run-action.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
|**--run-name**|string|The workflow run name.|run_name|
|**--action-name**|string|The workflow action name.|action_name|
### logic workflow-run-action show

show a logic workflow-run-action.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
|**--run-name**|string|The workflow run name.|run_name|
|**--action-name**|string|The workflow action name.|action_name|
### logic workflow-run-action-repetition list

list a logic workflow-run-action-repetition.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
|**--run-name**|string|The workflow run name.|run_name|
|**--action-name**|string|The workflow action name.|action_name|
### logic workflow-run-action-repetition list-expression-trace

list-expression-trace a logic workflow-run-action-repetition.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
|**--run-name**|string|The workflow run name.|run_name|
|**--action-name**|string|The workflow action name.|action_name|
|**--repetition-name**|string|The workflow repetition.|repetition_name|
### logic workflow-run-action-repetition show

show a logic workflow-run-action-repetition.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
|**--run-name**|string|The workflow run name.|run_name|
|**--action-name**|string|The workflow action name.|action_name|
|**--repetition-name**|string|The workflow repetition.|repetition_name|
### logic workflow-run-action-repetition-request-history list

list a logic workflow-run-action-repetition-request-history.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
|**--run-name**|string|The workflow run name.|run_name|
|**--action-name**|string|The workflow action name.|action_name|
|**--repetition-name**|string|The workflow repetition.|repetition_name|
### logic workflow-run-action-repetition-request-history show

show a logic workflow-run-action-repetition-request-history.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
|**--run-name**|string|The workflow run name.|run_name|
|**--action-name**|string|The workflow action name.|action_name|
|**--repetition-name**|string|The workflow repetition.|repetition_name|
|**--request-history-name**|string|The request history name.|request_history_name|
### logic workflow-run-action-request-history list

list a logic workflow-run-action-request-history.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
|**--run-name**|string|The workflow run name.|run_name|
|**--action-name**|string|The workflow action name.|action_name|
### logic workflow-run-action-request-history show

show a logic workflow-run-action-request-history.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
|**--run-name**|string|The workflow run name.|run_name|
|**--action-name**|string|The workflow action name.|action_name|
|**--request-history-name**|string|The request history name.|request_history_name|
### logic workflow-run-action-scope-repetition list

list a logic workflow-run-action-scope-repetition.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
|**--run-name**|string|The workflow run name.|run_name|
|**--action-name**|string|The workflow action name.|action_name|
### logic workflow-run-action-scope-repetition show

show a logic workflow-run-action-scope-repetition.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
|**--run-name**|string|The workflow run name.|run_name|
|**--action-name**|string|The workflow action name.|action_name|
|**--repetition-name**|string|The workflow repetition.|repetition_name|
### logic workflow-run-operation show

show a logic workflow-run-operation.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
|**--run-name**|string|The workflow run name.|run_name|
|**--operation-id**|string|The workflow operation id.|operation_id|
### logic workflow-trigger get-schema-json

get-schema-json a logic workflow-trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
|**--trigger-name**|string|The workflow trigger name.|trigger_name|
### logic workflow-trigger list

list a logic workflow-trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
|**--top**|integer|The number of items to be included in the result.|top|
|**--filter**|string|The filter to apply on the operation.|filter|
### logic workflow-trigger list-callback-url

list-callback-url a logic workflow-trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
|**--trigger-name**|string|The workflow trigger name.|trigger_name|
### logic workflow-trigger reset

reset a logic workflow-trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
|**--trigger-name**|string|The workflow trigger name.|trigger_name|
### logic workflow-trigger run

run a logic workflow-trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
|**--trigger-name**|string|The workflow trigger name.|trigger_name|
### logic workflow-trigger set-state

set-state a logic workflow-trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
|**--trigger-name**|string|The workflow trigger name.|trigger_name|
|**--source**|object|The source.|source|
### logic workflow-trigger show

show a logic workflow-trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
|**--trigger-name**|string|The workflow trigger name.|trigger_name|
### logic workflow-trigger-history list

list a logic workflow-trigger-history.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
|**--trigger-name**|string|The workflow trigger name.|trigger_name|
|**--top**|integer|The number of items to be included in the result.|top|
|**--filter**|string|The filter to apply on the operation. Options for filters include: Status, StartTime, and ClientTrackingId.|filter|
### logic workflow-trigger-history resubmit

resubmit a logic workflow-trigger-history.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
|**--trigger-name**|string|The workflow trigger name.|trigger_name|
|**--history-name**|string|The workflow trigger history name. Corresponds to the run name for triggers that resulted in a run.|history_name|
### logic workflow-trigger-history show

show a logic workflow-trigger-history.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
|**--trigger-name**|string|The workflow trigger name.|trigger_name|
|**--history-name**|string|The workflow trigger history name. Corresponds to the run name for triggers that resulted in a run.|history_name|
### logic workflow-version list

list a logic workflow-version.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
|**--top**|integer|The number of items to be included in the result.|top|
### logic workflow-version show

show a logic workflow-version.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
|**--version-id**|string|The workflow versionId.|version_id|
### logic workflow-version-trigger list-callback-url

list-callback-url a logic workflow-version-trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--workflow-name**|string|The workflow name.|workflow_name|
|**--version-id**|string|The workflow versionId.|version_id|
|**--trigger-name**|string|The workflow trigger name.|trigger_name|
|**--not-after**|date-time|The expiry time.|not_after|
|**--key-type**|choice|The key type.|key_type|