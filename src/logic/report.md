# Azure CLI Module Creation Report

### logic integration-account create

create a logic integration-account.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account|IntegrationAccounts|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--location**|string|The resource location.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|
|**--sku-name**|choice|The sku name.|name|name|
|**--integration-service-environment**|object|The integration service environment.|integration_service_environment|integrationServiceEnvironment|
|**--state**|choice|The workflow state.|state|state|

### logic integration-account delete

delete a logic integration-account.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account|IntegrationAccounts|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|

### logic integration-account list

list a logic integration-account.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account|IntegrationAccounts|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByResourceGroup|
|list|ListBySubscription|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--top**|integer|The number of items to be included in the result.|top|$top|

### logic integration-account list-callback-url

list-callback-url a logic integration-account.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account|IntegrationAccounts|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list-callback-url|ListCallbackUrl|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--not-after**|date-time|The expiry time.|not_after|notAfter|
|**--key-type**|choice|The key type.|key_type|keyType|

### logic integration-account list-key-vault-key

list-key-vault-key a logic integration-account.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account|IntegrationAccounts|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list-key-vault-key|ListKeyVaultKeys|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--skip-token**|string|The skip token.|skip_token|skipToken|
|**--key-vault-id**|string|The resource id.|id|id|

### logic integration-account log-tracking-event

log-tracking-event a logic integration-account.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account|IntegrationAccounts|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|log-tracking-event|LogTrackingEvents|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--source-type**|string|The source type.|source_type|sourceType|
|**--events**|array|The events.|events|events|
|**--track-events-options**|choice|The track events options.|track_events_options|trackEventsOptions|

### logic integration-account regenerate-access-key

regenerate-access-key a logic integration-account.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account|IntegrationAccounts|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|regenerate-access-key|RegenerateAccessKey|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--key-type**|choice|The key type.|key_type|keyType|

### logic integration-account show

show a logic integration-account.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account|IntegrationAccounts|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|

### logic integration-account update

update a logic integration-account.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account|IntegrationAccounts|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--location**|string|The resource location.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|
|**--sku-name**|choice|The sku name.|name|name|
|**--integration-service-environment**|object|The integration service environment.|integration_service_environment|integrationServiceEnvironment|
|**--state**|choice|The workflow state.|state|state|

### logic integration-account-agreement create

create a logic integration-account-agreement.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-agreement|IntegrationAccountAgreements|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--agreement-name**|string|The integration account agreement name.|agreement_name|agreementName|
|**--agreement-type**|sealed-choice|The agreement type.|agreement_type|agreementType|
|**--host-partner**|string|The integration account partner that is set as host partner for this agreement.|host_partner|hostPartner|
|**--guest-partner**|string|The integration account partner that is set as guest partner for this agreement.|guest_partner|guestPartner|
|**--host-identity**|object|The business identity of the host partner.|host_identity|hostIdentity|
|**--guest-identity**|object|The business identity of the guest partner.|guest_identity|guestIdentity|
|**--content**|object|The agreement content.|content|content|
|**--location**|string|The resource location.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|
|**--metadata**|any|The metadata.|metadata|metadata|

### logic integration-account-agreement delete

delete a logic integration-account-agreement.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-agreement|IntegrationAccountAgreements|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--agreement-name**|string|The integration account agreement name.|agreement_name|agreementName|

### logic integration-account-agreement list

list a logic integration-account-agreement.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-agreement|IntegrationAccountAgreements|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--top**|integer|The number of items to be included in the result.|top|$top|
|**--filter**|string|The filter to apply on the operation. Options for filters include: AgreementType.|filter|$filter|

### logic integration-account-agreement list-content-callback-url

list-content-callback-url a logic integration-account-agreement.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-agreement|IntegrationAccountAgreements|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list-content-callback-url|ListContentCallbackUrl|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--agreement-name**|string|The integration account agreement name.|agreement_name|agreementName|
|**--not-after**|date-time|The expiry time.|not_after|notAfter|
|**--key-type**|choice|The key type.|key_type|keyType|

### logic integration-account-agreement show

show a logic integration-account-agreement.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-agreement|IntegrationAccountAgreements|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--agreement-name**|string|The integration account agreement name.|agreement_name|agreementName|

### logic integration-account-agreement update

update a logic integration-account-agreement.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-agreement|IntegrationAccountAgreements|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|CreateOrUpdate#Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--agreement-name**|string|The integration account agreement name.|agreement_name|agreementName|
|**--agreement-type**|sealed-choice|The agreement type.|agreement_type|agreementType|
|**--host-partner**|string|The integration account partner that is set as host partner for this agreement.|host_partner|hostPartner|
|**--guest-partner**|string|The integration account partner that is set as guest partner for this agreement.|guest_partner|guestPartner|
|**--host-identity**|object|The business identity of the host partner.|host_identity|hostIdentity|
|**--guest-identity**|object|The business identity of the guest partner.|guest_identity|guestIdentity|
|**--content**|object|The agreement content.|content|content|
|**--location**|string|The resource location.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|
|**--metadata**|any|The metadata.|metadata|metadata|

### logic integration-account-assembly create

create a logic integration-account-assembly.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-assembly|IntegrationAccountAssemblies|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--assembly-artifact-name**|string|The assembly artifact name.|assembly_artifact_name|assemblyArtifactName|
|**--properties**|object|The assembly properties.|properties|properties|
|**--location**|string|The resource location.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|

### logic integration-account-assembly delete

delete a logic integration-account-assembly.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-assembly|IntegrationAccountAssemblies|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--assembly-artifact-name**|string|The assembly artifact name.|assembly_artifact_name|assemblyArtifactName|

### logic integration-account-assembly list

list a logic integration-account-assembly.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-assembly|IntegrationAccountAssemblies|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|

### logic integration-account-assembly list-content-callback-url

list-content-callback-url a logic integration-account-assembly.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-assembly|IntegrationAccountAssemblies|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list-content-callback-url|ListContentCallbackUrl|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--assembly-artifact-name**|string|The assembly artifact name.|assembly_artifact_name|assemblyArtifactName|

### logic integration-account-assembly show

show a logic integration-account-assembly.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-assembly|IntegrationAccountAssemblies|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--assembly-artifact-name**|string|The assembly artifact name.|assembly_artifact_name|assemblyArtifactName|

### logic integration-account-assembly update

update a logic integration-account-assembly.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-assembly|IntegrationAccountAssemblies|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|CreateOrUpdate#Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--assembly-artifact-name**|string|The assembly artifact name.|assembly_artifact_name|assemblyArtifactName|
|**--properties**|object|The assembly properties.|properties|properties|
|**--location**|string|The resource location.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|

### logic integration-account-batch-configuration create

create a logic integration-account-batch-configuration.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-batch-configuration|IntegrationAccountBatchConfigurations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--batch-configuration-name**|string|The batch configuration name.|batch_configuration_name|batchConfigurationName|
|**--batch-group-name**|string|The name of the batch group.|batch_group_name|batchGroupName|
|**--location**|string|The resource location.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|
|**--created-time**|date-time|The artifact creation time.|created_time|createdTime|
|**--changed-time**|date-time|The artifact changed time.|changed_time|changedTime|
|**--metadata**|any|Any object|metadata|metadata|
|**--release-criteria-message-count**|integer|The message count.|message_count|messageCount|
|**--release-criteria-batch-size**|integer|The batch size in bytes.|batch_size|batchSize|
|**--release-criteria-recurrence-frequency**|choice|The frequency.|frequency|frequency|
|**--release-criteria-recurrence-interval**|integer|The interval.|interval|interval|
|**--release-criteria-recurrence-start-time**|string|The start time.|start_time|startTime|
|**--release-criteria-recurrence-end-time**|string|The end time.|end_time|endTime|
|**--release-criteria-recurrence-time-zone**|string|The time zone.|time_zone|timeZone|
|**--release-criteria-recurrence-schedule-minutes**|array|The minutes.|minutes|minutes|
|**--release-criteria-recurrence-schedule-hours**|array|The hours.|hours|hours|
|**--release-criteria-recurrence-schedule-week-days**|array|The days of the week.|week_days|weekDays|
|**--release-criteria-recurrence-schedule-month-days**|array|The month days.|month_days|monthDays|
|**--release-criteria-recurrence-schedule-monthly-occurrences**|array|The monthly occurrences.|monthly_occurrences|monthlyOccurrences|

### logic integration-account-batch-configuration delete

delete a logic integration-account-batch-configuration.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-batch-configuration|IntegrationAccountBatchConfigurations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--batch-configuration-name**|string|The batch configuration name.|batch_configuration_name|batchConfigurationName|

### logic integration-account-batch-configuration list

list a logic integration-account-batch-configuration.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-batch-configuration|IntegrationAccountBatchConfigurations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|

### logic integration-account-batch-configuration show

show a logic integration-account-batch-configuration.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-batch-configuration|IntegrationAccountBatchConfigurations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--batch-configuration-name**|string|The batch configuration name.|batch_configuration_name|batchConfigurationName|

### logic integration-account-batch-configuration update

update a logic integration-account-batch-configuration.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-batch-configuration|IntegrationAccountBatchConfigurations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|CreateOrUpdate#Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--batch-configuration-name**|string|The batch configuration name.|batch_configuration_name|batchConfigurationName|
|**--batch-group-name**|string|The name of the batch group.|batch_group_name|batchGroupName|
|**--location**|string|The resource location.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|
|**--created-time**|date-time|The artifact creation time.|created_time|createdTime|
|**--changed-time**|date-time|The artifact changed time.|changed_time|changedTime|
|**--metadata**|any|Any object|metadata|metadata|
|**--release-criteria-message-count**|integer|The message count.|message_count|messageCount|
|**--release-criteria-batch-size**|integer|The batch size in bytes.|batch_size|batchSize|
|**--release-criteria-recurrence-frequency**|choice|The frequency.|frequency|frequency|
|**--release-criteria-recurrence-interval**|integer|The interval.|interval|interval|
|**--release-criteria-recurrence-start-time**|string|The start time.|start_time|startTime|
|**--release-criteria-recurrence-end-time**|string|The end time.|end_time|endTime|
|**--release-criteria-recurrence-time-zone**|string|The time zone.|time_zone|timeZone|
|**--release-criteria-recurrence-schedule-minutes**|array|The minutes.|minutes|minutes|
|**--release-criteria-recurrence-schedule-hours**|array|The hours.|hours|hours|
|**--release-criteria-recurrence-schedule-week-days**|array|The days of the week.|week_days|weekDays|
|**--release-criteria-recurrence-schedule-month-days**|array|The month days.|month_days|monthDays|
|**--release-criteria-recurrence-schedule-monthly-occurrences**|array|The monthly occurrences.|monthly_occurrences|monthlyOccurrences|

### logic integration-account-certificate create

create a logic integration-account-certificate.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-certificate|IntegrationAccountCertificates|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--certificate-name**|string|The integration account certificate name.|certificate_name|certificateName|
|**--location**|string|The resource location.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|
|**--metadata**|any|The metadata.|metadata|metadata|
|**--public-certificate**|string|The public certificate.|public_certificate|publicCertificate|
|**--key-key-vault**|object|The key vault reference.|key_vault|keyVault|
|**--key-key-name**|string|The private key name in key vault.|key_name|keyName|
|**--key-key-version**|string|The private key version in key vault.|key_version|keyVersion|

### logic integration-account-certificate delete

delete a logic integration-account-certificate.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-certificate|IntegrationAccountCertificates|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--certificate-name**|string|The integration account certificate name.|certificate_name|certificateName|

### logic integration-account-certificate list

list a logic integration-account-certificate.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-certificate|IntegrationAccountCertificates|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--top**|integer|The number of items to be included in the result.|top|$top|

### logic integration-account-certificate show

show a logic integration-account-certificate.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-certificate|IntegrationAccountCertificates|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--certificate-name**|string|The integration account certificate name.|certificate_name|certificateName|

### logic integration-account-certificate update

update a logic integration-account-certificate.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-certificate|IntegrationAccountCertificates|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|CreateOrUpdate#Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--certificate-name**|string|The integration account certificate name.|certificate_name|certificateName|
|**--location**|string|The resource location.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|
|**--metadata**|any|The metadata.|metadata|metadata|
|**--public-certificate**|string|The public certificate.|public_certificate|publicCertificate|
|**--key-key-vault**|object|The key vault reference.|key_vault|keyVault|
|**--key-key-name**|string|The private key name in key vault.|key_name|keyName|
|**--key-key-version**|string|The private key version in key vault.|key_version|keyVersion|

### logic integration-account-map create

create a logic integration-account-map.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-map|IntegrationAccountMaps|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--map-name**|string|The integration account map name.|map_name|mapName|
|**--map-type**|choice|The map type.|map_type|mapType|
|**--location**|string|The resource location.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|
|**--content**|string|The content.|content|content|
|**--properties-content-type**|string|The content type.|content_type|contentType|
|**--metadata**|any|The metadata.|metadata|metadata|
|**--parameters-schema-ref**|string|The reference name.|ref|ref|

### logic integration-account-map delete

delete a logic integration-account-map.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-map|IntegrationAccountMaps|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--map-name**|string|The integration account map name.|map_name|mapName|

### logic integration-account-map list

list a logic integration-account-map.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-map|IntegrationAccountMaps|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--top**|integer|The number of items to be included in the result.|top|$top|
|**--filter**|string|The filter to apply on the operation. Options for filters include: MapType.|filter|$filter|

### logic integration-account-map list-content-callback-url

list-content-callback-url a logic integration-account-map.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-map|IntegrationAccountMaps|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list-content-callback-url|ListContentCallbackUrl|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--map-name**|string|The integration account map name.|map_name|mapName|
|**--not-after**|date-time|The expiry time.|not_after|notAfter|
|**--key-type**|choice|The key type.|key_type|keyType|

### logic integration-account-map show

show a logic integration-account-map.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-map|IntegrationAccountMaps|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--map-name**|string|The integration account map name.|map_name|mapName|

### logic integration-account-map update

update a logic integration-account-map.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-map|IntegrationAccountMaps|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|CreateOrUpdate#Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--map-name**|string|The integration account map name.|map_name|mapName|
|**--map-type**|choice|The map type.|map_type|mapType|
|**--location**|string|The resource location.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|
|**--content**|string|The content.|content|content|
|**--properties-content-type**|string|The content type.|content_type|contentType|
|**--metadata**|any|The metadata.|metadata|metadata|
|**--parameters-schema-ref**|string|The reference name.|ref|ref|

### logic integration-account-partner create

create a logic integration-account-partner.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-partner|IntegrationAccountPartners|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--partner-name**|string|The integration account partner name.|partner_name|partnerName|
|**--partner-type**|choice|The partner type.|partner_type|partnerType|
|**--location**|string|The resource location.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|
|**--metadata**|any|The metadata.|metadata|metadata|
|**--content-b2b-business-identities**|array|The list of partner business identities.|business_identities|businessIdentities|

### logic integration-account-partner delete

delete a logic integration-account-partner.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-partner|IntegrationAccountPartners|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--partner-name**|string|The integration account partner name.|partner_name|partnerName|

### logic integration-account-partner list

list a logic integration-account-partner.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-partner|IntegrationAccountPartners|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--top**|integer|The number of items to be included in the result.|top|$top|
|**--filter**|string|The filter to apply on the operation. Options for filters include: PartnerType.|filter|$filter|

### logic integration-account-partner list-content-callback-url

list-content-callback-url a logic integration-account-partner.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-partner|IntegrationAccountPartners|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list-content-callback-url|ListContentCallbackUrl|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--partner-name**|string|The integration account partner name.|partner_name|partnerName|
|**--not-after**|date-time|The expiry time.|not_after|notAfter|
|**--key-type**|choice|The key type.|key_type|keyType|

### logic integration-account-partner show

show a logic integration-account-partner.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-partner|IntegrationAccountPartners|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--partner-name**|string|The integration account partner name.|partner_name|partnerName|

### logic integration-account-partner update

update a logic integration-account-partner.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-partner|IntegrationAccountPartners|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|CreateOrUpdate#Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--partner-name**|string|The integration account partner name.|partner_name|partnerName|
|**--partner-type**|choice|The partner type.|partner_type|partnerType|
|**--location**|string|The resource location.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|
|**--metadata**|any|The metadata.|metadata|metadata|
|**--content-b2b-business-identities**|array|The list of partner business identities.|business_identities|businessIdentities|

### logic integration-account-schema create

create a logic integration-account-schema.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-schema|IntegrationAccountSchemas|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--schema-name**|string|The integration account schema name.|schema_name|schemaName|
|**--schema-type**|choice|The schema type.|schema_type|schemaType|
|**--location**|string|The resource location.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|
|**--target-namespace**|string|The target namespace of the schema.|target_namespace|targetNamespace|
|**--document-name**|string|The document name.|document_name|documentName|
|**--file-name**|string|The file name.|file_name|fileName|
|**--metadata**|any|The metadata.|metadata|metadata|
|**--content**|string|The content.|content|content|
|**--properties-content-type**|string|The content type.|content_type|contentType|

### logic integration-account-schema delete

delete a logic integration-account-schema.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-schema|IntegrationAccountSchemas|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--schema-name**|string|The integration account schema name.|schema_name|schemaName|

### logic integration-account-schema list

list a logic integration-account-schema.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-schema|IntegrationAccountSchemas|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--top**|integer|The number of items to be included in the result.|top|$top|
|**--filter**|string|The filter to apply on the operation. Options for filters include: SchemaType.|filter|$filter|

### logic integration-account-schema list-content-callback-url

list-content-callback-url a logic integration-account-schema.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-schema|IntegrationAccountSchemas|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list-content-callback-url|ListContentCallbackUrl|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--schema-name**|string|The integration account schema name.|schema_name|schemaName|
|**--not-after**|date-time|The expiry time.|not_after|notAfter|
|**--key-type**|choice|The key type.|key_type|keyType|

### logic integration-account-schema show

show a logic integration-account-schema.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-schema|IntegrationAccountSchemas|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--schema-name**|string|The integration account schema name.|schema_name|schemaName|

### logic integration-account-schema update

update a logic integration-account-schema.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-schema|IntegrationAccountSchemas|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|CreateOrUpdate#Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--schema-name**|string|The integration account schema name.|schema_name|schemaName|
|**--schema-type**|choice|The schema type.|schema_type|schemaType|
|**--location**|string|The resource location.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|
|**--target-namespace**|string|The target namespace of the schema.|target_namespace|targetNamespace|
|**--document-name**|string|The document name.|document_name|documentName|
|**--file-name**|string|The file name.|file_name|fileName|
|**--metadata**|any|The metadata.|metadata|metadata|
|**--content**|string|The content.|content|content|
|**--properties-content-type**|string|The content type.|content_type|contentType|

### logic integration-account-session create

create a logic integration-account-session.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-session|IntegrationAccountSessions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--session-name**|string|The integration account session name.|session_name|sessionName|
|**--location**|string|The resource location.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|
|**--content**|any|The session content.|content|content|

### logic integration-account-session delete

delete a logic integration-account-session.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-session|IntegrationAccountSessions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--session-name**|string|The integration account session name.|session_name|sessionName|

### logic integration-account-session list

list a logic integration-account-session.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-session|IntegrationAccountSessions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--top**|integer|The number of items to be included in the result.|top|$top|
|**--filter**|string|The filter to apply on the operation. Options for filters include: ChangedTime.|filter|$filter|

### logic integration-account-session show

show a logic integration-account-session.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-session|IntegrationAccountSessions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--session-name**|string|The integration account session name.|session_name|sessionName|

### logic integration-account-session update

update a logic integration-account-session.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-account-session|IntegrationAccountSessions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|CreateOrUpdate#Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--session-name**|string|The integration account session name.|session_name|sessionName|
|**--location**|string|The resource location.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|
|**--content**|any|The session content.|content|content|

### logic integration-service-environment create

create a logic integration-service-environment.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-service-environment|IntegrationServiceEnvironments|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group**|string|The resource group.|resource_group|resourceGroup|
|**--integration-service-environment-name**|string|The integration service environment name.|integration_service_environment_name|integrationServiceEnvironmentName|
|**--location**|string|The resource location.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|
|**--sku**|object|The sku.|sku|sku|
|**--provisioning-state**|choice|The provisioning state.|provisioning_state|provisioningState|
|**--state**|choice|The integration service environment state.|state|state|
|**--integration-service-environment-id**|string|Gets the tracking id.|integration_service_environment_id|integrationServiceEnvironmentId|
|**--endpoints-configuration**|object|The endpoints configuration.|endpoints_configuration|endpointsConfiguration|
|**--network-configuration**|object|The network configuration.|network_configuration|networkConfiguration|

### logic integration-service-environment delete

delete a logic integration-service-environment.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-service-environment|IntegrationServiceEnvironments|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group**|string|The resource group.|resource_group|resourceGroup|
|**--integration-service-environment-name**|string|The integration service environment name.|integration_service_environment_name|integrationServiceEnvironmentName|

### logic integration-service-environment list

list a logic integration-service-environment.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-service-environment|IntegrationServiceEnvironments|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByResourceGroup|
|list|ListBySubscription|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group**|string|The resource group.|resource_group|resourceGroup|
|**--top**|integer|The number of items to be included in the result.|top|$top|

### logic integration-service-environment restart

restart a logic integration-service-environment.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-service-environment|IntegrationServiceEnvironments|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|restart|Restart|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group**|string|The resource group.|resource_group|resourceGroup|
|**--integration-service-environment-name**|string|The integration service environment name.|integration_service_environment_name|integrationServiceEnvironmentName|

### logic integration-service-environment show

show a logic integration-service-environment.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-service-environment|IntegrationServiceEnvironments|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group**|string|The resource group.|resource_group|resourceGroup|
|**--integration-service-environment-name**|string|The integration service environment name.|integration_service_environment_name|integrationServiceEnvironmentName|

### logic integration-service-environment update

update a logic integration-service-environment.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-service-environment|IntegrationServiceEnvironments|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group**|string|The resource group.|resource_group|resourceGroup|
|**--integration-service-environment-name**|string|The integration service environment name.|integration_service_environment_name|integrationServiceEnvironmentName|
|**--location**|string|The resource location.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|
|**--sku**|object|The sku.|sku|sku|
|**--provisioning-state**|choice|The provisioning state.|provisioning_state|provisioningState|
|**--state**|choice|The integration service environment state.|state|state|
|**--integration-service-environment-id**|string|Gets the tracking id.|integration_service_environment_id|integrationServiceEnvironmentId|
|**--endpoints-configuration**|object|The endpoints configuration.|endpoints_configuration|endpointsConfiguration|
|**--network-configuration**|object|The network configuration.|network_configuration|networkConfiguration|

### logic integration-service-environment-managed-api delete

delete a logic integration-service-environment-managed-api.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-service-environment-managed-api|IntegrationServiceEnvironmentManagedApis|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group**|string|The resource group.|resource_group|resourceGroup|
|**--integration-service-environment-name**|string|The integration service environment name.|integration_service_environment_name|integrationServiceEnvironmentName|
|**--api-name**|string|The api name.|api_name|apiName|

### logic integration-service-environment-managed-api list

list a logic integration-service-environment-managed-api.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-service-environment-managed-api|IntegrationServiceEnvironmentManagedApis|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group**|string|The resource group.|resource_group|resourceGroup|
|**--integration-service-environment-name**|string|The integration service environment name.|integration_service_environment_name|integrationServiceEnvironmentName|

### logic integration-service-environment-managed-api put

put a logic integration-service-environment-managed-api.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-service-environment-managed-api|IntegrationServiceEnvironmentManagedApis|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|put|Put|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group**|string|The resource group name.|resource_group|resourceGroup|
|**--integration-service-environment-name**|string|The integration service environment name.|integration_service_environment_name|integrationServiceEnvironmentName|
|**--api-name**|string|The api name.|api_name|apiName|

### logic integration-service-environment-managed-api show

show a logic integration-service-environment-managed-api.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-service-environment-managed-api|IntegrationServiceEnvironmentManagedApis|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group**|string|The resource group name.|resource_group|resourceGroup|
|**--integration-service-environment-name**|string|The integration service environment name.|integration_service_environment_name|integrationServiceEnvironmentName|
|**--api-name**|string|The api name.|api_name|apiName|

### logic integration-service-environment-managed-api-operation list

list a logic integration-service-environment-managed-api-operation.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-service-environment-managed-api-operation|IntegrationServiceEnvironmentManagedApiOperations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group**|string|The resource group.|resource_group|resourceGroup|
|**--integration-service-environment-name**|string|The integration service environment name.|integration_service_environment_name|integrationServiceEnvironmentName|
|**--api-name**|string|The api name.|api_name|apiName|

### logic integration-service-environment-network-health show

show a logic integration-service-environment-network-health.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-service-environment-network-health|IntegrationServiceEnvironmentNetworkHealth|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group**|string|The resource group.|resource_group|resourceGroup|
|**--integration-service-environment-name**|string|The integration service environment name.|integration_service_environment_name|integrationServiceEnvironmentName|

### logic integration-service-environment-sku list

list a logic integration-service-environment-sku.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic integration-service-environment-sku|IntegrationServiceEnvironmentSkus|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group**|string|The resource group.|resource_group|resourceGroup|
|**--integration-service-environment-name**|string|The integration service environment name.|integration_service_environment_name|integrationServiceEnvironmentName|

### logic workflow create

create a logic workflow.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow|Workflows|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--location**|string|The resource location.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|
|**--state**|choice|The state.|state|state|
|**--definition**|any|The definition.|definition|definition|
|**--parameters**|dictionary|The parameters.|parameters|parameters|
|**--integration-service-environment-id**|string|The resource id.|id|id|
|**--integration-account-id**|string|The resource id.|resource_reference_id|id|
|**--access-control-triggers**|object|The access control configuration for invoking workflow triggers.|triggers|triggers|
|**--access-control-contents**|object|The access control configuration for accessing workflow run contents.|contents|contents|
|**--access-control-actions**|object|The access control configuration for workflow actions.|actions|actions|
|**--access-control-workflow-management**|object|The access control configuration for workflow management.|workflow_management|workflowManagement|
|**--endpoints-configuration-workflow**|object|The workflow endpoints.|workflow|workflow|
|**--endpoints-configuration-connector**|object|The connector endpoints.|connector|connector|

### logic workflow delete

delete a logic workflow.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow|Workflows|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|

### logic workflow disable

disable a logic workflow.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow|Workflows|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|disable|Disable|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|

### logic workflow enable

enable a logic workflow.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow|Workflows|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|enable|Enable|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|

### logic workflow generate-upgraded-definition

generate-upgraded-definition a logic workflow.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow|Workflows|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|generate-upgraded-definition|GenerateUpgradedDefinition|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--target-schema-version**|string|The target schema version.|target_schema_version|targetSchemaVersion|

### logic workflow list

list a logic workflow.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow|Workflows|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByResourceGroup|
|list|ListBySubscription|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--top**|integer|The number of items to be included in the result.|top|$top|
|**--filter**|string|The filter to apply on the operation. Options for filters include: State, Trigger, and ReferencedResourceId.|filter|$filter|

### logic workflow list-callback-url

list-callback-url a logic workflow.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow|Workflows|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list-callback-url|ListCallbackUrl|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--not-after**|date-time|The expiry time.|not_after|notAfter|
|**--key-type**|choice|The key type.|key_type|keyType|

### logic workflow list-swagger

list-swagger a logic workflow.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow|Workflows|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list-swagger|ListSwagger|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|

### logic workflow move

move a logic workflow.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow|Workflows|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|move|Move|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--id**|string|The resource id.|id|id|

### logic workflow regenerate-access-key

regenerate-access-key a logic workflow.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow|Workflows|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|regenerate-access-key|RegenerateAccessKey|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--key-type**|choice|The key type.|key_type|keyType|

### logic workflow show

show a logic workflow.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow|Workflows|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|

### logic workflow update

update a logic workflow.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow|Workflows|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|

### logic workflow validate-by-location

validate-by-location a logic workflow.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow|Workflows|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|validate-by-location|ValidateByLocation|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--location**|string|The workflow location.|location|location|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--resource-location**|string|The resource location.|resource_location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|
|**--state**|choice|The state.|state|state|
|**--definition**|any|The definition.|definition|definition|
|**--parameters**|dictionary|The parameters.|parameters|parameters|
|**--integration-service-environment-id**|string|The resource id.|id|id|
|**--integration-account-id**|string|The resource id.|resource_reference_id|id|
|**--access-control-triggers**|object|The access control configuration for invoking workflow triggers.|triggers|triggers|
|**--access-control-contents**|object|The access control configuration for accessing workflow run contents.|contents|contents|
|**--access-control-actions**|object|The access control configuration for workflow actions.|actions|actions|
|**--access-control-workflow-management**|object|The access control configuration for workflow management.|workflow_management|workflowManagement|
|**--endpoints-configuration-workflow**|object|The workflow endpoints.|workflow|workflow|
|**--endpoints-configuration-connector**|object|The connector endpoints.|connector|connector|

### logic workflow validate-by-resource-group

validate-by-resource-group a logic workflow.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow|Workflows|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|validate-by-resource-group|ValidateByResourceGroup|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--location**|string|The resource location.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|
|**--state**|choice|The state.|state|state|
|**--definition**|any|The definition.|definition|definition|
|**--parameters**|dictionary|The parameters.|parameters|parameters|
|**--integration-service-environment-id**|string|The resource id.|id|id|
|**--integration-account-id**|string|The resource id.|resource_reference_id|id|
|**--access-control-triggers**|object|The access control configuration for invoking workflow triggers.|triggers|triggers|
|**--access-control-contents**|object|The access control configuration for accessing workflow run contents.|contents|contents|
|**--access-control-actions**|object|The access control configuration for workflow actions.|actions|actions|
|**--access-control-workflow-management**|object|The access control configuration for workflow management.|workflow_management|workflowManagement|
|**--endpoints-configuration-workflow**|object|The workflow endpoints.|workflow|workflow|
|**--endpoints-configuration-connector**|object|The connector endpoints.|connector|connector|

### logic workflow-run cancel

cancel a logic workflow-run.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow-run|WorkflowRuns|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|cancel|Cancel|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--run-name**|string|The workflow run name.|run_name|runName|

### logic workflow-run list

list a logic workflow-run.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow-run|WorkflowRuns|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--top**|integer|The number of items to be included in the result.|top|$top|
|**--filter**|string|The filter to apply on the operation. Options for filters include: Status, StartTime, and ClientTrackingId.|filter|$filter|

### logic workflow-run show

show a logic workflow-run.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow-run|WorkflowRuns|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--run-name**|string|The workflow run name.|run_name|runName|

### logic workflow-run-action list

list a logic workflow-run-action.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow-run-action|WorkflowRunActions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--run-name**|string|The workflow run name.|run_name|runName|
|**--top**|integer|The number of items to be included in the result.|top|$top|
|**--filter**|string|The filter to apply on the operation. Options for filters include: Status.|filter|$filter|

### logic workflow-run-action list-expression-trace

list-expression-trace a logic workflow-run-action.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow-run-action|WorkflowRunActions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list-expression-trace|ListExpressionTraces|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--run-name**|string|The workflow run name.|run_name|runName|
|**--action-name**|string|The workflow action name.|action_name|actionName|

### logic workflow-run-action show

show a logic workflow-run-action.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow-run-action|WorkflowRunActions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--run-name**|string|The workflow run name.|run_name|runName|
|**--action-name**|string|The workflow action name.|action_name|actionName|

### logic workflow-run-action-repetition list

list a logic workflow-run-action-repetition.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow-run-action-repetition|WorkflowRunActionRepetitions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--run-name**|string|The workflow run name.|run_name|runName|
|**--action-name**|string|The workflow action name.|action_name|actionName|

### logic workflow-run-action-repetition list-expression-trace

list-expression-trace a logic workflow-run-action-repetition.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow-run-action-repetition|WorkflowRunActionRepetitions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list-expression-trace|ListExpressionTraces|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--run-name**|string|The workflow run name.|run_name|runName|
|**--action-name**|string|The workflow action name.|action_name|actionName|
|**--repetition-name**|string|The workflow repetition.|repetition_name|repetitionName|

### logic workflow-run-action-repetition show

show a logic workflow-run-action-repetition.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow-run-action-repetition|WorkflowRunActionRepetitions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--run-name**|string|The workflow run name.|run_name|runName|
|**--action-name**|string|The workflow action name.|action_name|actionName|
|**--repetition-name**|string|The workflow repetition.|repetition_name|repetitionName|

### logic workflow-run-action-repetition-request-history list

list a logic workflow-run-action-repetition-request-history.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow-run-action-repetition-request-history|WorkflowRunActionRepetitionsRequestHistories|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--run-name**|string|The workflow run name.|run_name|runName|
|**--action-name**|string|The workflow action name.|action_name|actionName|
|**--repetition-name**|string|The workflow repetition.|repetition_name|repetitionName|

### logic workflow-run-action-repetition-request-history show

show a logic workflow-run-action-repetition-request-history.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow-run-action-repetition-request-history|WorkflowRunActionRepetitionsRequestHistories|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--run-name**|string|The workflow run name.|run_name|runName|
|**--action-name**|string|The workflow action name.|action_name|actionName|
|**--repetition-name**|string|The workflow repetition.|repetition_name|repetitionName|
|**--request-history-name**|string|The request history name.|request_history_name|requestHistoryName|

### logic workflow-run-action-request-history list

list a logic workflow-run-action-request-history.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow-run-action-request-history|WorkflowRunActionRequestHistories|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--run-name**|string|The workflow run name.|run_name|runName|
|**--action-name**|string|The workflow action name.|action_name|actionName|

### logic workflow-run-action-request-history show

show a logic workflow-run-action-request-history.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow-run-action-request-history|WorkflowRunActionRequestHistories|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--run-name**|string|The workflow run name.|run_name|runName|
|**--action-name**|string|The workflow action name.|action_name|actionName|
|**--request-history-name**|string|The request history name.|request_history_name|requestHistoryName|

### logic workflow-run-action-scope-repetition list

list a logic workflow-run-action-scope-repetition.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow-run-action-scope-repetition|WorkflowRunActionScopeRepetitions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--run-name**|string|The workflow run name.|run_name|runName|
|**--action-name**|string|The workflow action name.|action_name|actionName|

### logic workflow-run-action-scope-repetition show

show a logic workflow-run-action-scope-repetition.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow-run-action-scope-repetition|WorkflowRunActionScopeRepetitions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--run-name**|string|The workflow run name.|run_name|runName|
|**--action-name**|string|The workflow action name.|action_name|actionName|
|**--repetition-name**|string|The workflow repetition.|repetition_name|repetitionName|

### logic workflow-run-operation show

show a logic workflow-run-operation.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow-run-operation|WorkflowRunOperations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--run-name**|string|The workflow run name.|run_name|runName|
|**--operation-id**|string|The workflow operation id.|operation_id|operationId|

### logic workflow-trigger get-schema-json

get-schema-json a logic workflow-trigger.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow-trigger|WorkflowTriggers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|get-schema-json|GetSchemaJson|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--trigger-name**|string|The workflow trigger name.|trigger_name|triggerName|

### logic workflow-trigger list

list a logic workflow-trigger.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow-trigger|WorkflowTriggers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--top**|integer|The number of items to be included in the result.|top|$top|
|**--filter**|string|The filter to apply on the operation.|filter|$filter|

### logic workflow-trigger list-callback-url

list-callback-url a logic workflow-trigger.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow-trigger|WorkflowTriggers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list-callback-url|ListCallbackUrl|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--trigger-name**|string|The workflow trigger name.|trigger_name|triggerName|

### logic workflow-trigger reset

reset a logic workflow-trigger.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow-trigger|WorkflowTriggers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|reset|Reset|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--trigger-name**|string|The workflow trigger name.|trigger_name|triggerName|

### logic workflow-trigger run

run a logic workflow-trigger.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow-trigger|WorkflowTriggers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|run|Run|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--trigger-name**|string|The workflow trigger name.|trigger_name|triggerName|

### logic workflow-trigger set-state

set-state a logic workflow-trigger.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow-trigger|WorkflowTriggers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|set-state|SetState|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--trigger-name**|string|The workflow trigger name.|trigger_name|triggerName|
|**--source**|object|The source.|source|source|

### logic workflow-trigger show

show a logic workflow-trigger.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow-trigger|WorkflowTriggers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--trigger-name**|string|The workflow trigger name.|trigger_name|triggerName|

### logic workflow-trigger-history list

list a logic workflow-trigger-history.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow-trigger-history|WorkflowTriggerHistories|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--trigger-name**|string|The workflow trigger name.|trigger_name|triggerName|
|**--top**|integer|The number of items to be included in the result.|top|$top|
|**--filter**|string|The filter to apply on the operation. Options for filters include: Status, StartTime, and ClientTrackingId.|filter|$filter|

### logic workflow-trigger-history resubmit

resubmit a logic workflow-trigger-history.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow-trigger-history|WorkflowTriggerHistories|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|resubmit|Resubmit|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--trigger-name**|string|The workflow trigger name.|trigger_name|triggerName|
|**--history-name**|string|The workflow trigger history name. Corresponds to the run name for triggers that resulted in a run.|history_name|historyName|

### logic workflow-trigger-history show

show a logic workflow-trigger-history.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow-trigger-history|WorkflowTriggerHistories|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--trigger-name**|string|The workflow trigger name.|trigger_name|triggerName|
|**--history-name**|string|The workflow trigger history name. Corresponds to the run name for triggers that resulted in a run.|history_name|historyName|

### logic workflow-version list

list a logic workflow-version.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow-version|WorkflowVersions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--top**|integer|The number of items to be included in the result.|top|$top|

### logic workflow-version show

show a logic workflow-version.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow-version|WorkflowVersions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--version-id**|string|The workflow versionId.|version_id|versionId|

### logic workflow-version-trigger list-callback-url

list-callback-url a logic workflow-version-trigger.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|logic workflow-version-trigger|WorkflowVersionTriggers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list-callback-url|ListCallbackUrl|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--version-id**|string|The workflow versionId.|version_id|versionId|
|**--trigger-name**|string|The workflow trigger name.|trigger_name|triggerName|
|**--not-after**|date-time|The expiry time.|not_after|notAfter|
|**--key-type**|choice|The key type.|key_type|keyType|
