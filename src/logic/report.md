# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az logic|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az logic` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az logic workflow|Workflows|[commands](#CommandsInWorkflows)|
|az logic workflow-version|WorkflowVersions|[commands](#CommandsInWorkflowVersions)|
|az logic workflow-trigger|WorkflowTriggers|[commands](#CommandsInWorkflowTriggers)|
|az logic workflow-version-trigger|WorkflowVersionTriggers|[commands](#CommandsInWorkflowVersionTriggers)|
|az logic workflow-trigger-history|WorkflowTriggerHistories|[commands](#CommandsInWorkflowTriggerHistories)|
|az logic workflow-run|WorkflowRuns|[commands](#CommandsInWorkflowRuns)|
|az logic workflow-run-action|WorkflowRunActions|[commands](#CommandsInWorkflowRunActions)|
|az logic workflow-run-action-repetition|WorkflowRunActionRepetitions|[commands](#CommandsInWorkflowRunActionRepetitions)|
|az logic workflow-run-action-repetition-request-history|WorkflowRunActionRepetitionsRequestHistories|[commands](#CommandsInWorkflowRunActionRepetitionsRequestHistories)|
|az logic workflow-run-action-request-history|WorkflowRunActionRequestHistories|[commands](#CommandsInWorkflowRunActionRequestHistories)|
|az logic workflow-run-action-scope-repetition|WorkflowRunActionScopeRepetitions|[commands](#CommandsInWorkflowRunActionScopeRepetitions)|
|az logic workflow-run-operation|WorkflowRunOperations|[commands](#CommandsInWorkflowRunOperations)|
|az logic integration-account|IntegrationAccounts|[commands](#CommandsInIntegrationAccounts)|
|az logic integration-account-assembly|IntegrationAccountAssemblies|[commands](#CommandsInIntegrationAccountAssemblies)|
|az logic integration-account-batch-configuration|IntegrationAccountBatchConfigurations|[commands](#CommandsInIntegrationAccountBatchConfigurations)|
|az logic integration-account-schema|IntegrationAccountSchemas|[commands](#CommandsInIntegrationAccountSchemas)|
|az logic integration-account-map|IntegrationAccountMaps|[commands](#CommandsInIntegrationAccountMaps)|
|az logic integration-account-partner|IntegrationAccountPartners|[commands](#CommandsInIntegrationAccountPartners)|
|az logic integration-account-agreement|IntegrationAccountAgreements|[commands](#CommandsInIntegrationAccountAgreements)|
|az logic integration-account-certificate|IntegrationAccountCertificates|[commands](#CommandsInIntegrationAccountCertificates)|
|az logic integration-account-session|IntegrationAccountSessions|[commands](#CommandsInIntegrationAccountSessions)|
|az logic integration-service-environment|IntegrationServiceEnvironments|[commands](#CommandsInIntegrationServiceEnvironments)|
|az logic integration-service-environment-sku|IntegrationServiceEnvironmentSkus|[commands](#CommandsInIntegrationServiceEnvironmentSkus)|
|az logic integration-service-environment-network-health|IntegrationServiceEnvironmentNetworkHealth|[commands](#CommandsInIntegrationServiceEnvironmentNetworkHealth)|
|az logic integration-service-environment-managed-api|IntegrationServiceEnvironmentManagedApis|[commands](#CommandsInIntegrationServiceEnvironmentManagedApis)|
|az logic integration-service-environment-managed-api-operation|IntegrationServiceEnvironmentManagedApiOperations|[commands](#CommandsInIntegrationServiceEnvironmentManagedApiOperations)|

## COMMANDS
### <a name="CommandsInIntegrationAccounts">Commands in `az logic integration-account` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az logic integration-account list](#IntegrationAccountsListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersIntegrationAccountsListByResourceGroup)|[Example](#ExamplesIntegrationAccountsListByResourceGroup)|
|[az logic integration-account list](#IntegrationAccountsListBySubscription)|ListBySubscription|[Parameters](#ParametersIntegrationAccountsListBySubscription)|[Example](#ExamplesIntegrationAccountsListBySubscription)|
|[az logic integration-account show](#IntegrationAccountsGet)|Get|[Parameters](#ParametersIntegrationAccountsGet)|[Example](#ExamplesIntegrationAccountsGet)|
|[az logic integration-account create](#IntegrationAccountsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersIntegrationAccountsCreateOrUpdate#Create)|[Example](#ExamplesIntegrationAccountsCreateOrUpdate#Create)|
|[az logic integration-account update](#IntegrationAccountsUpdate)|Update|[Parameters](#ParametersIntegrationAccountsUpdate)|[Example](#ExamplesIntegrationAccountsUpdate)|
|[az logic integration-account delete](#IntegrationAccountsDelete)|Delete|[Parameters](#ParametersIntegrationAccountsDelete)|[Example](#ExamplesIntegrationAccountsDelete)|
|[az logic integration-account list-callback-url](#IntegrationAccountsListCallbackUrl)|ListCallbackUrl|[Parameters](#ParametersIntegrationAccountsListCallbackUrl)|[Example](#ExamplesIntegrationAccountsListCallbackUrl)|
|[az logic integration-account list-key-vault-key](#IntegrationAccountsListKeyVaultKeys)|ListKeyVaultKeys|[Parameters](#ParametersIntegrationAccountsListKeyVaultKeys)|[Example](#ExamplesIntegrationAccountsListKeyVaultKeys)|
|[az logic integration-account log-tracking-event](#IntegrationAccountsLogTrackingEvents)|LogTrackingEvents|[Parameters](#ParametersIntegrationAccountsLogTrackingEvents)|[Example](#ExamplesIntegrationAccountsLogTrackingEvents)|
|[az logic integration-account regenerate-access-key](#IntegrationAccountsRegenerateAccessKey)|RegenerateAccessKey|[Parameters](#ParametersIntegrationAccountsRegenerateAccessKey)|[Example](#ExamplesIntegrationAccountsRegenerateAccessKey)|

### <a name="CommandsInIntegrationAccountAgreements">Commands in `az logic integration-account-agreement` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az logic integration-account-agreement list](#IntegrationAccountAgreementsList)|List|[Parameters](#ParametersIntegrationAccountAgreementsList)|[Example](#ExamplesIntegrationAccountAgreementsList)|
|[az logic integration-account-agreement show](#IntegrationAccountAgreementsGet)|Get|[Parameters](#ParametersIntegrationAccountAgreementsGet)|[Example](#ExamplesIntegrationAccountAgreementsGet)|
|[az logic integration-account-agreement create](#IntegrationAccountAgreementsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersIntegrationAccountAgreementsCreateOrUpdate#Create)|[Example](#ExamplesIntegrationAccountAgreementsCreateOrUpdate#Create)|
|[az logic integration-account-agreement update](#IntegrationAccountAgreementsCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersIntegrationAccountAgreementsCreateOrUpdate#Update)|Not Found|
|[az logic integration-account-agreement delete](#IntegrationAccountAgreementsDelete)|Delete|[Parameters](#ParametersIntegrationAccountAgreementsDelete)|[Example](#ExamplesIntegrationAccountAgreementsDelete)|
|[az logic integration-account-agreement list-content-callback-url](#IntegrationAccountAgreementsListContentCallbackUrl)|ListContentCallbackUrl|[Parameters](#ParametersIntegrationAccountAgreementsListContentCallbackUrl)|[Example](#ExamplesIntegrationAccountAgreementsListContentCallbackUrl)|

### <a name="CommandsInIntegrationAccountAssemblies">Commands in `az logic integration-account-assembly` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az logic integration-account-assembly list](#IntegrationAccountAssembliesList)|List|[Parameters](#ParametersIntegrationAccountAssembliesList)|[Example](#ExamplesIntegrationAccountAssembliesList)|
|[az logic integration-account-assembly show](#IntegrationAccountAssembliesGet)|Get|[Parameters](#ParametersIntegrationAccountAssembliesGet)|[Example](#ExamplesIntegrationAccountAssembliesGet)|
|[az logic integration-account-assembly create](#IntegrationAccountAssembliesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersIntegrationAccountAssembliesCreateOrUpdate#Create)|[Example](#ExamplesIntegrationAccountAssembliesCreateOrUpdate#Create)|
|[az logic integration-account-assembly update](#IntegrationAccountAssembliesCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersIntegrationAccountAssembliesCreateOrUpdate#Update)|Not Found|
|[az logic integration-account-assembly delete](#IntegrationAccountAssembliesDelete)|Delete|[Parameters](#ParametersIntegrationAccountAssembliesDelete)|[Example](#ExamplesIntegrationAccountAssembliesDelete)|
|[az logic integration-account-assembly list-content-callback-url](#IntegrationAccountAssembliesListContentCallbackUrl)|ListContentCallbackUrl|[Parameters](#ParametersIntegrationAccountAssembliesListContentCallbackUrl)|[Example](#ExamplesIntegrationAccountAssembliesListContentCallbackUrl)|

### <a name="CommandsInIntegrationAccountBatchConfigurations">Commands in `az logic integration-account-batch-configuration` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az logic integration-account-batch-configuration list](#IntegrationAccountBatchConfigurationsList)|List|[Parameters](#ParametersIntegrationAccountBatchConfigurationsList)|[Example](#ExamplesIntegrationAccountBatchConfigurationsList)|
|[az logic integration-account-batch-configuration show](#IntegrationAccountBatchConfigurationsGet)|Get|[Parameters](#ParametersIntegrationAccountBatchConfigurationsGet)|[Example](#ExamplesIntegrationAccountBatchConfigurationsGet)|
|[az logic integration-account-batch-configuration create](#IntegrationAccountBatchConfigurationsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersIntegrationAccountBatchConfigurationsCreateOrUpdate#Create)|[Example](#ExamplesIntegrationAccountBatchConfigurationsCreateOrUpdate#Create)|
|[az logic integration-account-batch-configuration update](#IntegrationAccountBatchConfigurationsCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersIntegrationAccountBatchConfigurationsCreateOrUpdate#Update)|Not Found|
|[az logic integration-account-batch-configuration delete](#IntegrationAccountBatchConfigurationsDelete)|Delete|[Parameters](#ParametersIntegrationAccountBatchConfigurationsDelete)|[Example](#ExamplesIntegrationAccountBatchConfigurationsDelete)|

### <a name="CommandsInIntegrationAccountCertificates">Commands in `az logic integration-account-certificate` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az logic integration-account-certificate list](#IntegrationAccountCertificatesList)|List|[Parameters](#ParametersIntegrationAccountCertificatesList)|[Example](#ExamplesIntegrationAccountCertificatesList)|
|[az logic integration-account-certificate show](#IntegrationAccountCertificatesGet)|Get|[Parameters](#ParametersIntegrationAccountCertificatesGet)|[Example](#ExamplesIntegrationAccountCertificatesGet)|
|[az logic integration-account-certificate create](#IntegrationAccountCertificatesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersIntegrationAccountCertificatesCreateOrUpdate#Create)|[Example](#ExamplesIntegrationAccountCertificatesCreateOrUpdate#Create)|
|[az logic integration-account-certificate update](#IntegrationAccountCertificatesCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersIntegrationAccountCertificatesCreateOrUpdate#Update)|Not Found|
|[az logic integration-account-certificate delete](#IntegrationAccountCertificatesDelete)|Delete|[Parameters](#ParametersIntegrationAccountCertificatesDelete)|[Example](#ExamplesIntegrationAccountCertificatesDelete)|

### <a name="CommandsInIntegrationAccountMaps">Commands in `az logic integration-account-map` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az logic integration-account-map list](#IntegrationAccountMapsList)|List|[Parameters](#ParametersIntegrationAccountMapsList)|[Example](#ExamplesIntegrationAccountMapsList)|
|[az logic integration-account-map show](#IntegrationAccountMapsGet)|Get|[Parameters](#ParametersIntegrationAccountMapsGet)|[Example](#ExamplesIntegrationAccountMapsGet)|
|[az logic integration-account-map create](#IntegrationAccountMapsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersIntegrationAccountMapsCreateOrUpdate#Create)|[Example](#ExamplesIntegrationAccountMapsCreateOrUpdate#Create)|
|[az logic integration-account-map update](#IntegrationAccountMapsCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersIntegrationAccountMapsCreateOrUpdate#Update)|Not Found|
|[az logic integration-account-map delete](#IntegrationAccountMapsDelete)|Delete|[Parameters](#ParametersIntegrationAccountMapsDelete)|[Example](#ExamplesIntegrationAccountMapsDelete)|
|[az logic integration-account-map list-content-callback-url](#IntegrationAccountMapsListContentCallbackUrl)|ListContentCallbackUrl|[Parameters](#ParametersIntegrationAccountMapsListContentCallbackUrl)|[Example](#ExamplesIntegrationAccountMapsListContentCallbackUrl)|

### <a name="CommandsInIntegrationAccountPartners">Commands in `az logic integration-account-partner` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az logic integration-account-partner list](#IntegrationAccountPartnersList)|List|[Parameters](#ParametersIntegrationAccountPartnersList)|[Example](#ExamplesIntegrationAccountPartnersList)|
|[az logic integration-account-partner show](#IntegrationAccountPartnersGet)|Get|[Parameters](#ParametersIntegrationAccountPartnersGet)|[Example](#ExamplesIntegrationAccountPartnersGet)|
|[az logic integration-account-partner create](#IntegrationAccountPartnersCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersIntegrationAccountPartnersCreateOrUpdate#Create)|[Example](#ExamplesIntegrationAccountPartnersCreateOrUpdate#Create)|
|[az logic integration-account-partner update](#IntegrationAccountPartnersCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersIntegrationAccountPartnersCreateOrUpdate#Update)|Not Found|
|[az logic integration-account-partner delete](#IntegrationAccountPartnersDelete)|Delete|[Parameters](#ParametersIntegrationAccountPartnersDelete)|[Example](#ExamplesIntegrationAccountPartnersDelete)|
|[az logic integration-account-partner list-content-callback-url](#IntegrationAccountPartnersListContentCallbackUrl)|ListContentCallbackUrl|[Parameters](#ParametersIntegrationAccountPartnersListContentCallbackUrl)|[Example](#ExamplesIntegrationAccountPartnersListContentCallbackUrl)|

### <a name="CommandsInIntegrationAccountSchemas">Commands in `az logic integration-account-schema` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az logic integration-account-schema list](#IntegrationAccountSchemasList)|List|[Parameters](#ParametersIntegrationAccountSchemasList)|[Example](#ExamplesIntegrationAccountSchemasList)|
|[az logic integration-account-schema show](#IntegrationAccountSchemasGet)|Get|[Parameters](#ParametersIntegrationAccountSchemasGet)|[Example](#ExamplesIntegrationAccountSchemasGet)|
|[az logic integration-account-schema create](#IntegrationAccountSchemasCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersIntegrationAccountSchemasCreateOrUpdate#Create)|[Example](#ExamplesIntegrationAccountSchemasCreateOrUpdate#Create)|
|[az logic integration-account-schema update](#IntegrationAccountSchemasCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersIntegrationAccountSchemasCreateOrUpdate#Update)|Not Found|
|[az logic integration-account-schema delete](#IntegrationAccountSchemasDelete)|Delete|[Parameters](#ParametersIntegrationAccountSchemasDelete)|[Example](#ExamplesIntegrationAccountSchemasDelete)|
|[az logic integration-account-schema list-content-callback-url](#IntegrationAccountSchemasListContentCallbackUrl)|ListContentCallbackUrl|[Parameters](#ParametersIntegrationAccountSchemasListContentCallbackUrl)|[Example](#ExamplesIntegrationAccountSchemasListContentCallbackUrl)|

### <a name="CommandsInIntegrationAccountSessions">Commands in `az logic integration-account-session` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az logic integration-account-session list](#IntegrationAccountSessionsList)|List|[Parameters](#ParametersIntegrationAccountSessionsList)|[Example](#ExamplesIntegrationAccountSessionsList)|
|[az logic integration-account-session show](#IntegrationAccountSessionsGet)|Get|[Parameters](#ParametersIntegrationAccountSessionsGet)|[Example](#ExamplesIntegrationAccountSessionsGet)|
|[az logic integration-account-session create](#IntegrationAccountSessionsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersIntegrationAccountSessionsCreateOrUpdate#Create)|[Example](#ExamplesIntegrationAccountSessionsCreateOrUpdate#Create)|
|[az logic integration-account-session update](#IntegrationAccountSessionsCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersIntegrationAccountSessionsCreateOrUpdate#Update)|Not Found|
|[az logic integration-account-session delete](#IntegrationAccountSessionsDelete)|Delete|[Parameters](#ParametersIntegrationAccountSessionsDelete)|[Example](#ExamplesIntegrationAccountSessionsDelete)|

### <a name="CommandsInIntegrationServiceEnvironments">Commands in `az logic integration-service-environment` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az logic integration-service-environment list](#IntegrationServiceEnvironmentsListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersIntegrationServiceEnvironmentsListByResourceGroup)|[Example](#ExamplesIntegrationServiceEnvironmentsListByResourceGroup)|
|[az logic integration-service-environment list](#IntegrationServiceEnvironmentsListBySubscription)|ListBySubscription|[Parameters](#ParametersIntegrationServiceEnvironmentsListBySubscription)|[Example](#ExamplesIntegrationServiceEnvironmentsListBySubscription)|
|[az logic integration-service-environment show](#IntegrationServiceEnvironmentsGet)|Get|[Parameters](#ParametersIntegrationServiceEnvironmentsGet)|[Example](#ExamplesIntegrationServiceEnvironmentsGet)|
|[az logic integration-service-environment create](#IntegrationServiceEnvironmentsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersIntegrationServiceEnvironmentsCreateOrUpdate#Create)|[Example](#ExamplesIntegrationServiceEnvironmentsCreateOrUpdate#Create)|
|[az logic integration-service-environment update](#IntegrationServiceEnvironmentsUpdate)|Update|[Parameters](#ParametersIntegrationServiceEnvironmentsUpdate)|[Example](#ExamplesIntegrationServiceEnvironmentsUpdate)|
|[az logic integration-service-environment delete](#IntegrationServiceEnvironmentsDelete)|Delete|[Parameters](#ParametersIntegrationServiceEnvironmentsDelete)|[Example](#ExamplesIntegrationServiceEnvironmentsDelete)|
|[az logic integration-service-environment restart](#IntegrationServiceEnvironmentsRestart)|Restart|[Parameters](#ParametersIntegrationServiceEnvironmentsRestart)|[Example](#ExamplesIntegrationServiceEnvironmentsRestart)|

### <a name="CommandsInIntegrationServiceEnvironmentManagedApis">Commands in `az logic integration-service-environment-managed-api` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az logic integration-service-environment-managed-api list](#IntegrationServiceEnvironmentManagedApisList)|List|[Parameters](#ParametersIntegrationServiceEnvironmentManagedApisList)|[Example](#ExamplesIntegrationServiceEnvironmentManagedApisList)|
|[az logic integration-service-environment-managed-api show](#IntegrationServiceEnvironmentManagedApisGet)|Get|[Parameters](#ParametersIntegrationServiceEnvironmentManagedApisGet)|[Example](#ExamplesIntegrationServiceEnvironmentManagedApisGet)|
|[az logic integration-service-environment-managed-api delete](#IntegrationServiceEnvironmentManagedApisDelete)|Delete|[Parameters](#ParametersIntegrationServiceEnvironmentManagedApisDelete)|[Example](#ExamplesIntegrationServiceEnvironmentManagedApisDelete)|
|[az logic integration-service-environment-managed-api put](#IntegrationServiceEnvironmentManagedApisPut)|Put|[Parameters](#ParametersIntegrationServiceEnvironmentManagedApisPut)|[Example](#ExamplesIntegrationServiceEnvironmentManagedApisPut)|

### <a name="CommandsInIntegrationServiceEnvironmentManagedApiOperations">Commands in `az logic integration-service-environment-managed-api-operation` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az logic integration-service-environment-managed-api-operation list](#IntegrationServiceEnvironmentManagedApiOperationsList)|List|[Parameters](#ParametersIntegrationServiceEnvironmentManagedApiOperationsList)|[Example](#ExamplesIntegrationServiceEnvironmentManagedApiOperationsList)|

### <a name="CommandsInIntegrationServiceEnvironmentNetworkHealth">Commands in `az logic integration-service-environment-network-health` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az logic integration-service-environment-network-health show](#IntegrationServiceEnvironmentNetworkHealthGet)|Get|[Parameters](#ParametersIntegrationServiceEnvironmentNetworkHealthGet)|[Example](#ExamplesIntegrationServiceEnvironmentNetworkHealthGet)|

### <a name="CommandsInIntegrationServiceEnvironmentSkus">Commands in `az logic integration-service-environment-sku` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az logic integration-service-environment-sku list](#IntegrationServiceEnvironmentSkusList)|List|[Parameters](#ParametersIntegrationServiceEnvironmentSkusList)|[Example](#ExamplesIntegrationServiceEnvironmentSkusList)|

### <a name="CommandsInWorkflows">Commands in `az logic workflow` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az logic workflow list](#WorkflowsListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersWorkflowsListByResourceGroup)|[Example](#ExamplesWorkflowsListByResourceGroup)|
|[az logic workflow list](#WorkflowsListBySubscription)|ListBySubscription|[Parameters](#ParametersWorkflowsListBySubscription)|[Example](#ExamplesWorkflowsListBySubscription)|
|[az logic workflow show](#WorkflowsGet)|Get|[Parameters](#ParametersWorkflowsGet)|[Example](#ExamplesWorkflowsGet)|
|[az logic workflow create](#WorkflowsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersWorkflowsCreateOrUpdate#Create)|[Example](#ExamplesWorkflowsCreateOrUpdate#Create)|
|[az logic workflow update](#WorkflowsUpdate)|Update|[Parameters](#ParametersWorkflowsUpdate)|[Example](#ExamplesWorkflowsUpdate)|
|[az logic workflow delete](#WorkflowsDelete)|Delete|[Parameters](#ParametersWorkflowsDelete)|[Example](#ExamplesWorkflowsDelete)|
|[az logic workflow disable](#WorkflowsDisable)|Disable|[Parameters](#ParametersWorkflowsDisable)|[Example](#ExamplesWorkflowsDisable)|
|[az logic workflow enable](#WorkflowsEnable)|Enable|[Parameters](#ParametersWorkflowsEnable)|[Example](#ExamplesWorkflowsEnable)|
|[az logic workflow generate-upgraded-definition](#WorkflowsGenerateUpgradedDefinition)|GenerateUpgradedDefinition|[Parameters](#ParametersWorkflowsGenerateUpgradedDefinition)|[Example](#ExamplesWorkflowsGenerateUpgradedDefinition)|
|[az logic workflow list-callback-url](#WorkflowsListCallbackUrl)|ListCallbackUrl|[Parameters](#ParametersWorkflowsListCallbackUrl)|[Example](#ExamplesWorkflowsListCallbackUrl)|
|[az logic workflow list-swagger](#WorkflowsListSwagger)|ListSwagger|[Parameters](#ParametersWorkflowsListSwagger)|[Example](#ExamplesWorkflowsListSwagger)|
|[az logic workflow move](#WorkflowsMove)|Move|[Parameters](#ParametersWorkflowsMove)|[Example](#ExamplesWorkflowsMove)|
|[az logic workflow regenerate-access-key](#WorkflowsRegenerateAccessKey)|RegenerateAccessKey|[Parameters](#ParametersWorkflowsRegenerateAccessKey)|[Example](#ExamplesWorkflowsRegenerateAccessKey)|
|[az logic workflow validate-by-location](#WorkflowsValidateByLocation)|ValidateByLocation|[Parameters](#ParametersWorkflowsValidateByLocation)|[Example](#ExamplesWorkflowsValidateByLocation)|
|[az logic workflow validate-by-resource-group](#WorkflowsValidateByResourceGroup)|ValidateByResourceGroup|[Parameters](#ParametersWorkflowsValidateByResourceGroup)|[Example](#ExamplesWorkflowsValidateByResourceGroup)|

### <a name="CommandsInWorkflowRuns">Commands in `az logic workflow-run` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az logic workflow-run list](#WorkflowRunsList)|List|[Parameters](#ParametersWorkflowRunsList)|[Example](#ExamplesWorkflowRunsList)|
|[az logic workflow-run show](#WorkflowRunsGet)|Get|[Parameters](#ParametersWorkflowRunsGet)|[Example](#ExamplesWorkflowRunsGet)|
|[az logic workflow-run cancel](#WorkflowRunsCancel)|Cancel|[Parameters](#ParametersWorkflowRunsCancel)|[Example](#ExamplesWorkflowRunsCancel)|

### <a name="CommandsInWorkflowRunActions">Commands in `az logic workflow-run-action` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az logic workflow-run-action list](#WorkflowRunActionsList)|List|[Parameters](#ParametersWorkflowRunActionsList)|[Example](#ExamplesWorkflowRunActionsList)|
|[az logic workflow-run-action show](#WorkflowRunActionsGet)|Get|[Parameters](#ParametersWorkflowRunActionsGet)|[Example](#ExamplesWorkflowRunActionsGet)|
|[az logic workflow-run-action list-expression-trace](#WorkflowRunActionsListExpressionTraces)|ListExpressionTraces|[Parameters](#ParametersWorkflowRunActionsListExpressionTraces)|[Example](#ExamplesWorkflowRunActionsListExpressionTraces)|

### <a name="CommandsInWorkflowRunActionRepetitions">Commands in `az logic workflow-run-action-repetition` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az logic workflow-run-action-repetition list](#WorkflowRunActionRepetitionsList)|List|[Parameters](#ParametersWorkflowRunActionRepetitionsList)|[Example](#ExamplesWorkflowRunActionRepetitionsList)|
|[az logic workflow-run-action-repetition show](#WorkflowRunActionRepetitionsGet)|Get|[Parameters](#ParametersWorkflowRunActionRepetitionsGet)|[Example](#ExamplesWorkflowRunActionRepetitionsGet)|
|[az logic workflow-run-action-repetition list-expression-trace](#WorkflowRunActionRepetitionsListExpressionTraces)|ListExpressionTraces|[Parameters](#ParametersWorkflowRunActionRepetitionsListExpressionTraces)|[Example](#ExamplesWorkflowRunActionRepetitionsListExpressionTraces)|

### <a name="CommandsInWorkflowRunActionRepetitionsRequestHistories">Commands in `az logic workflow-run-action-repetition-request-history` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az logic workflow-run-action-repetition-request-history list](#WorkflowRunActionRepetitionsRequestHistoriesList)|List|[Parameters](#ParametersWorkflowRunActionRepetitionsRequestHistoriesList)|[Example](#ExamplesWorkflowRunActionRepetitionsRequestHistoriesList)|
|[az logic workflow-run-action-repetition-request-history show](#WorkflowRunActionRepetitionsRequestHistoriesGet)|Get|[Parameters](#ParametersWorkflowRunActionRepetitionsRequestHistoriesGet)|[Example](#ExamplesWorkflowRunActionRepetitionsRequestHistoriesGet)|

### <a name="CommandsInWorkflowRunActionRequestHistories">Commands in `az logic workflow-run-action-request-history` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az logic workflow-run-action-request-history list](#WorkflowRunActionRequestHistoriesList)|List|[Parameters](#ParametersWorkflowRunActionRequestHistoriesList)|[Example](#ExamplesWorkflowRunActionRequestHistoriesList)|
|[az logic workflow-run-action-request-history show](#WorkflowRunActionRequestHistoriesGet)|Get|[Parameters](#ParametersWorkflowRunActionRequestHistoriesGet)|[Example](#ExamplesWorkflowRunActionRequestHistoriesGet)|

### <a name="CommandsInWorkflowRunActionScopeRepetitions">Commands in `az logic workflow-run-action-scope-repetition` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az logic workflow-run-action-scope-repetition list](#WorkflowRunActionScopeRepetitionsList)|List|[Parameters](#ParametersWorkflowRunActionScopeRepetitionsList)|[Example](#ExamplesWorkflowRunActionScopeRepetitionsList)|
|[az logic workflow-run-action-scope-repetition show](#WorkflowRunActionScopeRepetitionsGet)|Get|[Parameters](#ParametersWorkflowRunActionScopeRepetitionsGet)|[Example](#ExamplesWorkflowRunActionScopeRepetitionsGet)|

### <a name="CommandsInWorkflowRunOperations">Commands in `az logic workflow-run-operation` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az logic workflow-run-operation show](#WorkflowRunOperationsGet)|Get|[Parameters](#ParametersWorkflowRunOperationsGet)|[Example](#ExamplesWorkflowRunOperationsGet)|

### <a name="CommandsInWorkflowTriggers">Commands in `az logic workflow-trigger` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az logic workflow-trigger list](#WorkflowTriggersList)|List|[Parameters](#ParametersWorkflowTriggersList)|[Example](#ExamplesWorkflowTriggersList)|
|[az logic workflow-trigger show](#WorkflowTriggersGet)|Get|[Parameters](#ParametersWorkflowTriggersGet)|[Example](#ExamplesWorkflowTriggersGet)|
|[az logic workflow-trigger get-schema-json](#WorkflowTriggersGetSchemaJson)|GetSchemaJson|[Parameters](#ParametersWorkflowTriggersGetSchemaJson)|[Example](#ExamplesWorkflowTriggersGetSchemaJson)|
|[az logic workflow-trigger list-callback-url](#WorkflowTriggersListCallbackUrl)|ListCallbackUrl|[Parameters](#ParametersWorkflowTriggersListCallbackUrl)|[Example](#ExamplesWorkflowTriggersListCallbackUrl)|
|[az logic workflow-trigger reset](#WorkflowTriggersReset)|Reset|[Parameters](#ParametersWorkflowTriggersReset)|[Example](#ExamplesWorkflowTriggersReset)|
|[az logic workflow-trigger run](#WorkflowTriggersRun)|Run|[Parameters](#ParametersWorkflowTriggersRun)|[Example](#ExamplesWorkflowTriggersRun)|
|[az logic workflow-trigger set-state](#WorkflowTriggersSetState)|SetState|[Parameters](#ParametersWorkflowTriggersSetState)|[Example](#ExamplesWorkflowTriggersSetState)|

### <a name="CommandsInWorkflowTriggerHistories">Commands in `az logic workflow-trigger-history` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az logic workflow-trigger-history list](#WorkflowTriggerHistoriesList)|List|[Parameters](#ParametersWorkflowTriggerHistoriesList)|[Example](#ExamplesWorkflowTriggerHistoriesList)|
|[az logic workflow-trigger-history show](#WorkflowTriggerHistoriesGet)|Get|[Parameters](#ParametersWorkflowTriggerHistoriesGet)|[Example](#ExamplesWorkflowTriggerHistoriesGet)|
|[az logic workflow-trigger-history resubmit](#WorkflowTriggerHistoriesResubmit)|Resubmit|[Parameters](#ParametersWorkflowTriggerHistoriesResubmit)|[Example](#ExamplesWorkflowTriggerHistoriesResubmit)|

### <a name="CommandsInWorkflowVersions">Commands in `az logic workflow-version` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az logic workflow-version list](#WorkflowVersionsList)|List|[Parameters](#ParametersWorkflowVersionsList)|[Example](#ExamplesWorkflowVersionsList)|
|[az logic workflow-version show](#WorkflowVersionsGet)|Get|[Parameters](#ParametersWorkflowVersionsGet)|[Example](#ExamplesWorkflowVersionsGet)|

### <a name="CommandsInWorkflowVersionTriggers">Commands in `az logic workflow-version-trigger` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az logic workflow-version-trigger list-callback-url](#WorkflowVersionTriggersListCallbackUrl)|ListCallbackUrl|[Parameters](#ParametersWorkflowVersionTriggersListCallbackUrl)|[Example](#ExamplesWorkflowVersionTriggersListCallbackUrl)|


## COMMAND DETAILS

### group `az logic integration-account`
#### <a name="IntegrationAccountsListByResourceGroup">Command `az logic integration-account list`</a>

##### <a name="ExamplesIntegrationAccountsListByResourceGroup">Example</a>
```
az logic integration-account list --resource-group "testResourceGroup"
```
##### <a name="ParametersIntegrationAccountsListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--top**|integer|The number of items to be included in the result.|top|$top|

#### <a name="IntegrationAccountsListBySubscription">Command `az logic integration-account list`</a>

##### <a name="ExamplesIntegrationAccountsListBySubscription">Example</a>
```
az logic integration-account list
```
##### <a name="ParametersIntegrationAccountsListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="IntegrationAccountsGet">Command `az logic integration-account show`</a>

##### <a name="ExamplesIntegrationAccountsGet">Example</a>
```
az logic integration-account show --name "testIntegrationAccount" --resource-group "testResourceGroup"
```
##### <a name="ParametersIntegrationAccountsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|

#### <a name="IntegrationAccountsCreateOrUpdate#Create">Command `az logic integration-account create`</a>

##### <a name="ExamplesIntegrationAccountsCreateOrUpdate#Create">Example</a>
```
az logic integration-account create --location "westus" --integration-service-environment-sku name="Standard" --name \
"testIntegrationAccount" --resource-group "testResourceGroup"
```
##### <a name="ParametersIntegrationAccountsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--location**|string|The resource location.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|
|**--state**|choice|The workflow state.|state|state|
|**--integration-service-environment-sku**|object|The sku.|sku|sku|
|**--integration-service-environment-properties-provisioning-state**|choice|The provisioning state.|provisioning_state|provisioningState|
|**--integration-service-environment-properties-integration-service-environment-id**|string|Gets the tracking id.|integration_service_environment_id|integrationServiceEnvironmentId|
|**--integration-service-environment-properties-endpoints-configuration**|object|The endpoints configuration.|endpoints_configuration|endpointsConfiguration|
|**--integration-service-environment-properties-network-configuration**|object|The network configuration.|network_configuration|networkConfiguration|
|**--integration-service-environment-properties-encryption-configuration**|object|The encryption configuration.|encryption_configuration|encryptionConfiguration|
|**--sku-name**|choice|The sku name.|name|name|

#### <a name="IntegrationAccountsUpdate">Command `az logic integration-account update`</a>

##### <a name="ExamplesIntegrationAccountsUpdate">Example</a>
```
az logic integration-account update --location "westus" --integration-service-environment-sku name="Standard" --name \
"testIntegrationAccount" --resource-group "testResourceGroup"
```
##### <a name="ParametersIntegrationAccountsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--location**|string|The resource location.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|
|**--state**|choice|The workflow state.|state|state|
|**--integration-service-environment-sku**|object|The sku.|sku|sku|
|**--integration-service-environment-properties-provisioning-state**|choice|The provisioning state.|provisioning_state|provisioningState|
|**--integration-service-environment-properties-integration-service-environment-id**|string|Gets the tracking id.|integration_service_environment_id|integrationServiceEnvironmentId|
|**--integration-service-environment-properties-endpoints-configuration**|object|The endpoints configuration.|endpoints_configuration|endpointsConfiguration|
|**--integration-service-environment-properties-network-configuration**|object|The network configuration.|network_configuration|networkConfiguration|
|**--integration-service-environment-properties-encryption-configuration**|object|The encryption configuration.|encryption_configuration|encryptionConfiguration|
|**--sku-name**|choice|The sku name.|name|name|

#### <a name="IntegrationAccountsDelete">Command `az logic integration-account delete`</a>

##### <a name="ExamplesIntegrationAccountsDelete">Example</a>
```
az logic integration-account delete --name "testIntegrationAccount" --resource-group "testResourceGroup"
```
##### <a name="ParametersIntegrationAccountsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|

#### <a name="IntegrationAccountsListCallbackUrl">Command `az logic integration-account list-callback-url`</a>

##### <a name="ExamplesIntegrationAccountsListCallbackUrl">Example</a>
```
az logic integration-account list-callback-url --name "testIntegrationAccount" --key-type "Primary" --not-after \
"2017-03-05T08:00:00Z" --resource-group "testResourceGroup"
```
##### <a name="ParametersIntegrationAccountsListCallbackUrl">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--not-after**|date-time|The expiry time.|not_after|notAfter|
|**--key-type**|choice|The key type.|key_type|keyType|

#### <a name="IntegrationAccountsListKeyVaultKeys">Command `az logic integration-account list-key-vault-key`</a>

##### <a name="ExamplesIntegrationAccountsListKeyVaultKeys">Example</a>
```
az logic integration-account list-key-vault-key --name "testIntegrationAccount" --key-vault-id \
"subscriptions/34adfa4f-cedf-4dc0-ba29-b6d1a69ab345/resourceGroups/testResourceGroup/providers/Microsoft.KeyVault/vault\
s/testKeyVault" --skip-token "testSkipToken" --resource-group "testResourceGroup"
```
##### <a name="ParametersIntegrationAccountsListKeyVaultKeys">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--skip-token**|string|The skip token.|skip_token|skipToken|
|**--key-vault-id**|string|The resource id.|id|id|

#### <a name="IntegrationAccountsLogTrackingEvents">Command `az logic integration-account log-tracking-event`</a>

##### <a name="ExamplesIntegrationAccountsLogTrackingEvents">Example</a>
```
az logic integration-account log-tracking-event --name "testIntegrationAccount" --events \
"[{\\"error\\":{\\"code\\":\\"NotFound\\",\\"message\\":\\"Some error occurred\\"},\\"eventLevel\\":\\"Informational\\"\
,\\"eventTime\\":\\"2016-08-05T01:54:49.505567Z\\",\\"record\\":{\\"agreementProperties\\":{\\"agreementName\\":\\"test\
Agreement\\",\\"as2From\\":\\"testas2from\\",\\"as2To\\":\\"testas2to\\",\\"receiverPartnerName\\":\\"testPartner2\\",\
\\"senderPartnerName\\":\\"testPartner1\\"},\\"messageProperties\\":{\\"IsMessageEncrypted\\":false,\\"IsMessageSigned\
\\":false,\\"correlationMessageId\\":\\"Unique message identifier\\",\\"direction\\":\\"Receive\\",\\"dispositionType\\\
":\\"received-success\\",\\"fileName\\":\\"test\\",\\"isMdnExpected\\":true,\\"isMessageCompressed\\":false,\\"isMessag\
eFailed\\":false,\\"isNrrEnabled\\":true,\\"mdnType\\":\\"Async\\",\\"messageId\\":\\"12345\\"}},\\"recordType\\":\\"AS\
2Message\\"}]" --source-type "Microsoft.Logic/workflows" --resource-group "testResourceGroup"
```
##### <a name="ParametersIntegrationAccountsLogTrackingEvents">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--source-type**|string|The source type.|source_type|sourceType|
|**--events**|array|The events.|events|events|
|**--track-events-options**|choice|The track events options.|track_events_options|trackEventsOptions|

#### <a name="IntegrationAccountsRegenerateAccessKey">Command `az logic integration-account regenerate-access-key`</a>

##### <a name="ExamplesIntegrationAccountsRegenerateAccessKey">Example</a>
```
az logic integration-account regenerate-access-key --name "testIntegrationAccount" --key-type "Primary" \
--resource-group "testResourceGroup"
```
##### <a name="ParametersIntegrationAccountsRegenerateAccessKey">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--key-type**|choice|The key type.|key_type|keyType|

### group `az logic integration-account-agreement`
#### <a name="IntegrationAccountAgreementsList">Command `az logic integration-account-agreement list`</a>

##### <a name="ExamplesIntegrationAccountAgreementsList">Example</a>
```
az logic integration-account-agreement list --integration-account-name "testIntegrationAccount" --resource-group \
"testResourceGroup"
```
##### <a name="ParametersIntegrationAccountAgreementsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--top**|integer|The number of items to be included in the result.|top|$top|
|**--filter**|string|The filter to apply on the operation. Options for filters include: AgreementType.|filter|$filter|

#### <a name="IntegrationAccountAgreementsGet">Command `az logic integration-account-agreement show`</a>

##### <a name="ExamplesIntegrationAccountAgreementsGet">Example</a>
```
az logic integration-account-agreement show --agreement-name "testAgreement" --integration-account-name \
"testIntegrationAccount" --resource-group "testResourceGroup"
```
##### <a name="ParametersIntegrationAccountAgreementsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--agreement-name**|string|The integration account agreement name.|agreement_name|agreementName|

#### <a name="IntegrationAccountAgreementsCreateOrUpdate#Create">Command `az logic integration-account-agreement create`</a>

##### <a name="ExamplesIntegrationAccountAgreementsCreateOrUpdate#Create">Example</a>
```
az logic integration-account-agreement create --agreement "{\\"location\\":\\"westus\\",\\"tags\\":{\\"IntegrationAccou\
ntAgreement\\":\\"<IntegrationAccountAgreementName>\\"},\\"metadata\\":{},\\"agreementType\\":\\"AS2\\",\\"hostPartner\
\\":\\"HostPartner\\",\\"guestPartner\\":\\"GuestPartner\\",\\"hostIdentity\\":{\\"qualifier\\":\\"ZZ\\",\\"value\\":\\\
"ZZ\\"},\\"guestIdentity\\":{\\"qualifier\\":\\"AA\\",\\"value\\":\\"AA\\"},\\"content\\":{\\"aS2\\":{\\"receiveAgreeme\
nt\\":{\\"protocolSettings\\":{\\"acknowledgementConnectionSettings\\":{\\"ignoreCertificateNameMismatch\\":true,\\"kee\
pHttpConnectionAlive\\":true,\\"supportHttpStatusCodeContinue\\":true,\\"unfoldHttpHeaders\\":true},\\"envelopeSettings\
\\":{\\"autogenerateFileName\\":true,\\"fileNameTemplate\\":\\"Test\\",\\"messageContentType\\":\\"text/plain\\",\\"sus\
pendMessageOnFileNameGenerationError\\":true,\\"transmitFileNameInMimeHeader\\":true},\\"errorSettings\\":{\\"resendIfM\
DNNotReceived\\":true,\\"suspendDuplicateMessage\\":true},\\"mdnSettings\\":{\\"dispositionNotificationTo\\":\\"http://\
tempuri.org\\",\\"mdnText\\":\\"Sample\\",\\"micHashingAlgorithm\\":\\"SHA1\\",\\"needMDN\\":true,\\"receiptDeliveryUrl\
\\":\\"http://tempuri.org\\",\\"sendInboundMDNToMessageBox\\":true,\\"sendMDNAsynchronously\\":true,\\"signMDN\\":true,\
\\"signOutboundMDNIfOptional\\":true},\\"messageConnectionSettings\\":{\\"ignoreCertificateNameMismatch\\":true,\\"keep\
HttpConnectionAlive\\":true,\\"supportHttpStatusCodeContinue\\":true,\\"unfoldHttpHeaders\\":true},\\"securitySettings\
\\":{\\"enableNRRForInboundDecodedMessages\\":true,\\"enableNRRForInboundEncodedMessages\\":true,\\"enableNRRForInbound\
MDN\\":true,\\"enableNRRForOutboundDecodedMessages\\":true,\\"enableNRRForOutboundEncodedMessages\\":true,\\"enableNRRF\
orOutboundMDN\\":true,\\"overrideGroupSigningCertificate\\":false},\\"validationSettings\\":{\\"checkCertificateRevocat\
ionListOnReceive\\":true,\\"checkCertificateRevocationListOnSend\\":true,\\"checkDuplicateMessage\\":true,\\"compressMe\
ssage\\":true,\\"encryptMessage\\":false,\\"encryptionAlgorithm\\":\\"AES128\\",\\"interchangeDuplicatesValidityDays\\"\
:100,\\"overrideMessageProperties\\":true,\\"signMessage\\":false}},\\"receiverBusinessIdentity\\":{\\"qualifier\\":\\"\
ZZ\\",\\"value\\":\\"ZZ\\"},\\"senderBusinessIdentity\\":{\\"qualifier\\":\\"AA\\",\\"value\\":\\"AA\\"}},\\"sendAgreem\
ent\\":{\\"protocolSettings\\":{\\"acknowledgementConnectionSettings\\":{\\"ignoreCertificateNameMismatch\\":true,\\"ke\
epHttpConnectionAlive\\":true,\\"supportHttpStatusCodeContinue\\":true,\\"unfoldHttpHeaders\\":true},\\"envelopeSetting\
s\\":{\\"autogenerateFileName\\":true,\\"fileNameTemplate\\":\\"Test\\",\\"messageContentType\\":\\"text/plain\\",\\"su\
spendMessageOnFileNameGenerationError\\":true,\\"transmitFileNameInMimeHeader\\":true},\\"errorSettings\\":{\\"resendIf\
MDNNotReceived\\":true,\\"suspendDuplicateMessage\\":true},\\"mdnSettings\\":{\\"dispositionNotificationTo\\":\\"http:/\
/tempuri.org\\",\\"mdnText\\":\\"Sample\\",\\"micHashingAlgorithm\\":\\"SHA1\\",\\"needMDN\\":true,\\"receiptDeliveryUr\
l\\":\\"http://tempuri.org\\",\\"sendInboundMDNToMessageBox\\":true,\\"sendMDNAsynchronously\\":true,\\"signMDN\\":true\
,\\"signOutboundMDNIfOptional\\":true},\\"messageConnectionSettings\\":{\\"ignoreCertificateNameMismatch\\":true,\\"kee\
pHttpConnectionAlive\\":true,\\"supportHttpStatusCodeContinue\\":true,\\"unfoldHttpHeaders\\":true},\\"securitySettings\
\\":{\\"enableNRRForInboundDecodedMessages\\":true,\\"enableNRRForInboundEncodedMessages\\":true,\\"enableNRRForInbound\
MDN\\":true,\\"enableNRRForOutboundDecodedMessages\\":true,\\"enableNRRForOutboundEncodedMessages\\":true,\\"enableNRRF\
orOutboundMDN\\":true,\\"overrideGroupSigningCertificate\\":false},\\"validationSettings\\":{\\"checkCertificateRevocat\
ionListOnReceive\\":true,\\"checkCertificateRevocationListOnSend\\":true,\\"checkDuplicateMessage\\":true,\\"compressMe\
ssage\\":true,\\"encryptMessage\\":false,\\"encryptionAlgorithm\\":\\"AES128\\",\\"interchangeDuplicatesValidityDays\\"\
:100,\\"overrideMessageProperties\\":true,\\"signMessage\\":false}},\\"receiverBusinessIdentity\\":{\\"qualifier\\":\\"\
AA\\",\\"value\\":\\"AA\\"},\\"senderBusinessIdentity\\":{\\"qualifier\\":\\"ZZ\\",\\"value\\":\\"ZZ\\"}}}}}" \
--agreement-name "testAgreement" --integration-account-name "testIntegrationAccount" --resource-group \
"testResourceGroup"
```
##### <a name="ParametersIntegrationAccountAgreementsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--agreement-name**|string|The integration account agreement name.|agreement_name|agreementName|
|**--agreement**|object|The integration account agreement.|agreement|agreement|

#### <a name="IntegrationAccountAgreementsCreateOrUpdate#Update">Command `az logic integration-account-agreement update`</a>

##### <a name="ParametersIntegrationAccountAgreementsCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--agreement-name**|string|The integration account agreement name.|agreement_name|agreementName|
|**--agreement**|object|The integration account agreement.|agreement|agreement|

#### <a name="IntegrationAccountAgreementsDelete">Command `az logic integration-account-agreement delete`</a>

##### <a name="ExamplesIntegrationAccountAgreementsDelete">Example</a>
```
az logic integration-account-agreement delete --agreement-name "testAgreement" --integration-account-name \
"testIntegrationAccount" --resource-group "testResourceGroup"
```
##### <a name="ParametersIntegrationAccountAgreementsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--agreement-name**|string|The integration account agreement name.|agreement_name|agreementName|

#### <a name="IntegrationAccountAgreementsListContentCallbackUrl">Command `az logic integration-account-agreement list-content-callback-url`</a>

##### <a name="ExamplesIntegrationAccountAgreementsListContentCallbackUrl">Example</a>
```
az logic integration-account-agreement list-content-callback-url --agreement-name "testAgreement" \
--integration-account-name "testIntegrationAccount" --key-type "Primary" --not-after "2018-04-19T16:00:00Z" \
--resource-group "testResourceGroup"
```
##### <a name="ParametersIntegrationAccountAgreementsListContentCallbackUrl">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--agreement-name**|string|The integration account agreement name.|agreement_name|agreementName|
|**--not-after**|date-time|The expiry time.|not_after|notAfter|
|**--key-type**|choice|The key type.|key_type|keyType|

### group `az logic integration-account-assembly`
#### <a name="IntegrationAccountAssembliesList">Command `az logic integration-account-assembly list`</a>

##### <a name="ExamplesIntegrationAccountAssembliesList">Example</a>
```
az logic integration-account-assembly list --integration-account-name "testIntegrationAccount" --resource-group \
"testResourceGroup"
```
##### <a name="ParametersIntegrationAccountAssembliesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|

#### <a name="IntegrationAccountAssembliesGet">Command `az logic integration-account-assembly show`</a>

##### <a name="ExamplesIntegrationAccountAssembliesGet">Example</a>
```
az logic integration-account-assembly show --assembly-artifact-name "testAssembly" --integration-account-name \
"testIntegrationAccount" --resource-group "testResourceGroup"
```
##### <a name="ParametersIntegrationAccountAssembliesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--assembly-artifact-name**|string|The assembly artifact name.|assembly_artifact_name|assemblyArtifactName|

#### <a name="IntegrationAccountAssembliesCreateOrUpdate#Create">Command `az logic integration-account-assembly create`</a>

##### <a name="ExamplesIntegrationAccountAssembliesCreateOrUpdate#Create">Example</a>
```
az logic integration-account-assembly create --location "westus" --properties assembly-name="System.IdentityModel.Token\
s.Jwt" content="Base64 encoded Assembly Content" metadata={} --assembly-artifact-name "testAssembly" \
--integration-account-name "testIntegrationAccount" --resource-group "testResourceGroup"
```
##### <a name="ParametersIntegrationAccountAssembliesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--assembly-artifact-name**|string|The assembly artifact name.|assembly_artifact_name|assemblyArtifactName|
|**--properties**|object|The assembly properties.|properties|properties|
|**--location**|string|The resource location.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|

#### <a name="IntegrationAccountAssembliesCreateOrUpdate#Update">Command `az logic integration-account-assembly update`</a>

##### <a name="ParametersIntegrationAccountAssembliesCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--assembly-artifact-name**|string|The assembly artifact name.|assembly_artifact_name|assemblyArtifactName|
|**--properties**|object|The assembly properties.|properties|properties|
|**--location**|string|The resource location.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|

#### <a name="IntegrationAccountAssembliesDelete">Command `az logic integration-account-assembly delete`</a>

##### <a name="ExamplesIntegrationAccountAssembliesDelete">Example</a>
```
az logic integration-account-assembly delete --assembly-artifact-name "testAssembly" --integration-account-name \
"testIntegrationAccount" --resource-group "testResourceGroup"
```
##### <a name="ParametersIntegrationAccountAssembliesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--assembly-artifact-name**|string|The assembly artifact name.|assembly_artifact_name|assemblyArtifactName|

#### <a name="IntegrationAccountAssembliesListContentCallbackUrl">Command `az logic integration-account-assembly list-content-callback-url`</a>

##### <a name="ExamplesIntegrationAccountAssembliesListContentCallbackUrl">Example</a>
```
az logic integration-account-assembly list-content-callback-url --assembly-artifact-name "testAssembly" \
--integration-account-name "testIntegrationAccount" --resource-group "testResourceGroup"
```
##### <a name="ParametersIntegrationAccountAssembliesListContentCallbackUrl">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--assembly-artifact-name**|string|The assembly artifact name.|assembly_artifact_name|assemblyArtifactName|

### group `az logic integration-account-batch-configuration`
#### <a name="IntegrationAccountBatchConfigurationsList">Command `az logic integration-account-batch-configuration list`</a>

##### <a name="ExamplesIntegrationAccountBatchConfigurationsList">Example</a>
```
az logic integration-account-batch-configuration list --integration-account-name "testIntegrationAccount" \
--resource-group "testResourceGroup"
```
##### <a name="ParametersIntegrationAccountBatchConfigurationsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|

#### <a name="IntegrationAccountBatchConfigurationsGet">Command `az logic integration-account-batch-configuration show`</a>

##### <a name="ExamplesIntegrationAccountBatchConfigurationsGet">Example</a>
```
az logic integration-account-batch-configuration show --batch-configuration-name "testBatchConfiguration" \
--integration-account-name "testIntegrationAccount" --resource-group "testResourceGroup"
```
##### <a name="ParametersIntegrationAccountBatchConfigurationsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--batch-configuration-name**|string|The batch configuration name.|batch_configuration_name|batchConfigurationName|

#### <a name="IntegrationAccountBatchConfigurationsCreateOrUpdate#Create">Command `az logic integration-account-batch-configuration create`</a>

##### <a name="ExamplesIntegrationAccountBatchConfigurationsCreateOrUpdate#Create">Example</a>
```
az logic integration-account-batch-configuration create --location "westus" --batch-group-name "DEFAULT" \
--release-criteria-batch-size 234567 --release-criteria-message-count 10 --release-criteria-recurrence-frequency \
"Minute" --release-criteria-recurrence-interval 1 --release-criteria-recurrence-start-time "2017-03-24T11:43:00" \
--release-criteria-recurrence-time-zone "India Standard Time" --batch-configuration-name "testBatchConfiguration" \
--integration-account-name "testIntegrationAccount" --resource-group "testResourceGroup"
```
##### <a name="ParametersIntegrationAccountBatchConfigurationsCreateOrUpdate#Create">Parameters</a> 
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

#### <a name="IntegrationAccountBatchConfigurationsCreateOrUpdate#Update">Command `az logic integration-account-batch-configuration update`</a>

##### <a name="ParametersIntegrationAccountBatchConfigurationsCreateOrUpdate#Update">Parameters</a> 
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

#### <a name="IntegrationAccountBatchConfigurationsDelete">Command `az logic integration-account-batch-configuration delete`</a>

##### <a name="ExamplesIntegrationAccountBatchConfigurationsDelete">Example</a>
```
az logic integration-account-batch-configuration delete --batch-configuration-name "testBatchConfiguration" \
--integration-account-name "testIntegrationAccount" --resource-group "testResourceGroup"
```
##### <a name="ParametersIntegrationAccountBatchConfigurationsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--batch-configuration-name**|string|The batch configuration name.|batch_configuration_name|batchConfigurationName|

### group `az logic integration-account-certificate`
#### <a name="IntegrationAccountCertificatesList">Command `az logic integration-account-certificate list`</a>

##### <a name="ExamplesIntegrationAccountCertificatesList">Example</a>
```
az logic integration-account-certificate list --integration-account-name "testIntegrationAccount" --resource-group \
"testResourceGroup"
```
##### <a name="ParametersIntegrationAccountCertificatesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--top**|integer|The number of items to be included in the result.|top|$top|

#### <a name="IntegrationAccountCertificatesGet">Command `az logic integration-account-certificate show`</a>

##### <a name="ExamplesIntegrationAccountCertificatesGet">Example</a>
```
az logic integration-account-certificate show --certificate-name "testCertificate" --integration-account-name \
"testIntegrationAccount" --resource-group "testResourceGroup"
```
##### <a name="ParametersIntegrationAccountCertificatesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--certificate-name**|string|The integration account certificate name.|certificate_name|certificateName|

#### <a name="IntegrationAccountCertificatesCreateOrUpdate#Create">Command `az logic integration-account-certificate create`</a>

##### <a name="ExamplesIntegrationAccountCertificatesCreateOrUpdate#Create">Example</a>
```
az logic integration-account-certificate create --location "brazilsouth" --public-certificate \
"<publicCertificateValue>" --certificate-name "testCertificate" --integration-account-name "testIntegrationAccount" \
--resource-group "testResourceGroup"
```
##### <a name="ParametersIntegrationAccountCertificatesCreateOrUpdate#Create">Parameters</a> 
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

#### <a name="IntegrationAccountCertificatesCreateOrUpdate#Update">Command `az logic integration-account-certificate update`</a>

##### <a name="ParametersIntegrationAccountCertificatesCreateOrUpdate#Update">Parameters</a> 
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

#### <a name="IntegrationAccountCertificatesDelete">Command `az logic integration-account-certificate delete`</a>

##### <a name="ExamplesIntegrationAccountCertificatesDelete">Example</a>
```
az logic integration-account-certificate delete --certificate-name "testCertificate" --integration-account-name \
"testIntegrationAccount" --resource-group "testResourceGroup"
```
##### <a name="ParametersIntegrationAccountCertificatesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--certificate-name**|string|The integration account certificate name.|certificate_name|certificateName|

### group `az logic integration-account-map`
#### <a name="IntegrationAccountMapsList">Command `az logic integration-account-map list`</a>

##### <a name="ExamplesIntegrationAccountMapsList">Example</a>
```
az logic integration-account-map list --integration-account-name "testIntegrationAccount" --resource-group \
"testResourceGroup"
```
##### <a name="ParametersIntegrationAccountMapsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--top**|integer|The number of items to be included in the result.|top|$top|
|**--filter**|string|The filter to apply on the operation. Options for filters include: MapType.|filter|$filter|

#### <a name="IntegrationAccountMapsGet">Command `az logic integration-account-map show`</a>

##### <a name="ExamplesIntegrationAccountMapsGet">Example</a>
```
az logic integration-account-map show --integration-account-name "testIntegrationAccount" --map-name "testMap" \
--resource-group "testResourceGroup"
```
##### <a name="ParametersIntegrationAccountMapsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--map-name**|string|The integration account map name.|map_name|mapName|

#### <a name="IntegrationAccountMapsCreateOrUpdate#Create">Command `az logic integration-account-map create`</a>

##### <a name="ExamplesIntegrationAccountMapsCreateOrUpdate#Create">Example</a>
```
az logic integration-account-map create --integration-account-name "testIntegrationAccount" --location "westus" \
--content "<?xml version=\\"1.0\\" encoding=\\"UTF-16\\"?>\\r\\n<xsl:stylesheet xmlns:xsl=\\"http://www.w3.org/1999/XSL\
/Transform\\" xmlns:msxsl=\\"urn:schemas-microsoft-com:xslt\\" xmlns:var=\\"http://schemas.microsoft.com/BizTalk/2003/v\
ar\\" exclude-result-prefixes=\\"msxsl var s0 userCSharp\\" version=\\"1.0\\" xmlns:ns0=\\"http://BizTalk_Server_Projec\
t4.StringFunctoidsDestinationSchema\\" xmlns:s0=\\"http://BizTalk_Server_Project4.StringFunctoidsSourceSchema\\" \
xmlns:userCSharp=\\"http://schemas.microsoft.com/BizTalk/2003/userCSharp\\">\\r\\n  <xsl:import \
href=\\"http://btsfunctoids.blob.core.windows.net/functoids/functoids.xslt\\" />\\r\\n  <xsl:output \
omit-xml-declaration=\\"yes\\" method=\\"xml\\" version=\\"1.0\\" />\\r\\n  <xsl:template match=\\"/\\">\\r\\n    \
<xsl:apply-templates select=\\"/s0:Root\\" />\\r\\n  </xsl:template>\\r\\n  <xsl:template match=\\"/s0:Root\\">\\r\\n  \
  <xsl:variable name=\\"var:v1\\" select=\\"userCSharp:StringFind(string(StringFindSource/text()) , \
&quot;SearchString&quot;)\\" />\\r\\n    <xsl:variable name=\\"var:v2\\" select=\\"userCSharp:StringLeft(string(StringL\
eftSource/text()) , &quot;2&quot;)\\" />\\r\\n    <xsl:variable name=\\"var:v3\\" select=\\"userCSharp:StringRight(stri\
ng(StringRightSource/text()) , &quot;2&quot;)\\" />\\r\\n    <xsl:variable name=\\"var:v4\\" \
select=\\"userCSharp:StringUpperCase(string(UppercaseSource/text()))\\" />\\r\\n    <xsl:variable name=\\"var:v5\\" \
select=\\"userCSharp:StringLowerCase(string(LowercaseSource/text()))\\" />\\r\\n    <xsl:variable name=\\"var:v6\\" \
select=\\"userCSharp:StringSize(string(SizeSource/text()))\\" />\\r\\n    <xsl:variable name=\\"var:v7\\" \
select=\\"userCSharp:StringSubstring(string(StringExtractSource/text()) , &quot;0&quot; , &quot;2&quot;)\\" />\\r\\n   \
 <xsl:variable name=\\"var:v8\\" select=\\"userCSharp:StringConcat(string(StringConcatSource/text()))\\" />\\r\\n    \
<xsl:variable name=\\"var:v9\\" select=\\"userCSharp:StringTrimLeft(string(StringLeftTrimSource/text()))\\" />\\r\\n   \
 <xsl:variable name=\\"var:v10\\" select=\\"userCSharp:StringTrimRight(string(StringRightTrimSource/text()))\\" \
/>\\r\\n    <ns0:Root>\\r\\n      <StringFindDestination>\\r\\n        <xsl:value-of select=\\"$var:v1\\" />\\r\\n     \
 </StringFindDestination>\\r\\n      <StringLeftDestination>\\r\\n        <xsl:value-of select=\\"$var:v2\\" />\\r\\n  \
    </StringLeftDestination>\\r\\n      <StringRightDestination>\\r\\n        <xsl:value-of select=\\"$var:v3\\" \
/>\\r\\n      </StringRightDestination>\\r\\n      <UppercaseDestination>\\r\\n        <xsl:value-of \
select=\\"$var:v4\\" />\\r\\n      </UppercaseDestination>\\r\\n      <LowercaseDestination>\\r\\n        \
<xsl:value-of select=\\"$var:v5\\" />\\r\\n      </LowercaseDestination>\\r\\n      <SizeDestination>\\r\\n        \
<xsl:value-of select=\\"$var:v6\\" />\\r\\n      </SizeDestination>\\r\\n      <StringExtractDestination>\\r\\n        \
<xsl:value-of select=\\"$var:v7\\" />\\r\\n      </StringExtractDestination>\\r\\n      <StringConcatDestination>\\r\\n\
        <xsl:value-of select=\\"$var:v8\\" />\\r\\n      </StringConcatDestination>\\r\\n      \
<StringLeftTrimDestination>\\r\\n        <xsl:value-of select=\\"$var:v9\\" />\\r\\n      \
</StringLeftTrimDestination>\\r\\n      <StringRightTrimDestination>\\r\\n        <xsl:value-of select=\\"$var:v10\\" \
/>\\r\\n      </StringRightTrimDestination>\\r\\n    </ns0:Root>\\r\\n  </xsl:template>\\r\\n</xsl:stylesheet>" \
--properties-content-type "application/xml" --map-type "Xslt" --metadata "{}" --map-name "testMap" --resource-group \
"testResourceGroup"
```
##### <a name="ParametersIntegrationAccountMapsCreateOrUpdate#Create">Parameters</a> 
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

#### <a name="IntegrationAccountMapsCreateOrUpdate#Update">Command `az logic integration-account-map update`</a>

##### <a name="ParametersIntegrationAccountMapsCreateOrUpdate#Update">Parameters</a> 
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

#### <a name="IntegrationAccountMapsDelete">Command `az logic integration-account-map delete`</a>

##### <a name="ExamplesIntegrationAccountMapsDelete">Example</a>
```
az logic integration-account-map delete --integration-account-name "testIntegrationAccount" --map-name "testMap" \
--resource-group "testResourceGroup"
```
##### <a name="ParametersIntegrationAccountMapsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--map-name**|string|The integration account map name.|map_name|mapName|

#### <a name="IntegrationAccountMapsListContentCallbackUrl">Command `az logic integration-account-map list-content-callback-url`</a>

##### <a name="ExamplesIntegrationAccountMapsListContentCallbackUrl">Example</a>
```
az logic integration-account-map list-content-callback-url --integration-account-name "testIntegrationAccount" \
--key-type "Primary" --not-after "2018-04-19T16:00:00Z" --map-name "testMap" --resource-group "testResourceGroup"
```
##### <a name="ParametersIntegrationAccountMapsListContentCallbackUrl">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--map-name**|string|The integration account map name.|map_name|mapName|
|**--not-after**|date-time|The expiry time.|not_after|notAfter|
|**--key-type**|choice|The key type.|key_type|keyType|

### group `az logic integration-account-partner`
#### <a name="IntegrationAccountPartnersList">Command `az logic integration-account-partner list`</a>

##### <a name="ExamplesIntegrationAccountPartnersList">Example</a>
```
az logic integration-account-partner list --integration-account-name "testIntegrationAccount" --resource-group \
"testResourceGroup"
```
##### <a name="ParametersIntegrationAccountPartnersList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--top**|integer|The number of items to be included in the result.|top|$top|
|**--filter**|string|The filter to apply on the operation. Options for filters include: PartnerType.|filter|$filter|

#### <a name="IntegrationAccountPartnersGet">Command `az logic integration-account-partner show`</a>

##### <a name="ExamplesIntegrationAccountPartnersGet">Example</a>
```
az logic integration-account-partner show --integration-account-name "testIntegrationAccount" --partner-name \
"testPartner" --resource-group "testResourceGroup"
```
##### <a name="ParametersIntegrationAccountPartnersGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--partner-name**|string|The integration account partner name.|partner_name|partnerName|

#### <a name="IntegrationAccountPartnersCreateOrUpdate#Create">Command `az logic integration-account-partner create`</a>

##### <a name="ExamplesIntegrationAccountPartnersCreateOrUpdate#Create">Example</a>
```
az logic integration-account-partner create --integration-account-name "testIntegrationAccount" --location "westus" \
--metadata "{}" --partner-type "B2B" --partner-name "testPartner" --resource-group "testResourceGroup"
```
##### <a name="ParametersIntegrationAccountPartnersCreateOrUpdate#Create">Parameters</a> 
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

#### <a name="IntegrationAccountPartnersCreateOrUpdate#Update">Command `az logic integration-account-partner update`</a>

##### <a name="ParametersIntegrationAccountPartnersCreateOrUpdate#Update">Parameters</a> 
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

#### <a name="IntegrationAccountPartnersDelete">Command `az logic integration-account-partner delete`</a>

##### <a name="ExamplesIntegrationAccountPartnersDelete">Example</a>
```
az logic integration-account-partner delete --integration-account-name "testIntegrationAccount" --partner-name \
"testPartner" --resource-group "testResourceGroup"
```
##### <a name="ParametersIntegrationAccountPartnersDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--partner-name**|string|The integration account partner name.|partner_name|partnerName|

#### <a name="IntegrationAccountPartnersListContentCallbackUrl">Command `az logic integration-account-partner list-content-callback-url`</a>

##### <a name="ExamplesIntegrationAccountPartnersListContentCallbackUrl">Example</a>
```
az logic integration-account-partner list-content-callback-url --integration-account-name "testIntegrationAccount" \
--key-type "Primary" --not-after "2018-04-19T16:00:00Z" --partner-name "testPartner" --resource-group \
"testResourceGroup"
```
##### <a name="ParametersIntegrationAccountPartnersListContentCallbackUrl">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--partner-name**|string|The integration account partner name.|partner_name|partnerName|
|**--not-after**|date-time|The expiry time.|not_after|notAfter|
|**--key-type**|choice|The key type.|key_type|keyType|

### group `az logic integration-account-schema`
#### <a name="IntegrationAccountSchemasList">Command `az logic integration-account-schema list`</a>

##### <a name="ExamplesIntegrationAccountSchemasList">Example</a>
```
az logic integration-account-schema list --integration-account-name "<integrationAccountName>" --resource-group \
"testResourceGroup"
```
##### <a name="ParametersIntegrationAccountSchemasList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--top**|integer|The number of items to be included in the result.|top|$top|
|**--filter**|string|The filter to apply on the operation. Options for filters include: SchemaType.|filter|$filter|

#### <a name="IntegrationAccountSchemasGet">Command `az logic integration-account-schema show`</a>

##### <a name="ExamplesIntegrationAccountSchemasGet">Example</a>
```
az logic integration-account-schema show --integration-account-name "testIntegrationAccount" --resource-group \
"testResourceGroup" --schema-name "testSchema"
```
##### <a name="ParametersIntegrationAccountSchemasGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--schema-name**|string|The integration account schema name.|schema_name|schemaName|

#### <a name="IntegrationAccountSchemasCreateOrUpdate#Create">Command `az logic integration-account-schema create`</a>

##### <a name="ExamplesIntegrationAccountSchemasCreateOrUpdate#Create">Example</a>
```
az logic integration-account-schema create --location "westus" --content "<?xml version=\\"1.0\\" \
encoding=\\"utf-16\\"?>\\r\\n<xs:schema xmlns:b=\\"http://schemas.microsoft.com/BizTalk/2003\\" \
xmlns=\\"http://Inbound_EDI.OrderFile\\" targetNamespace=\\"http://Inbound_EDI.OrderFile\\" \
xmlns:xs=\\"http://www.w3.org/2001/XMLSchema\\">\\r\\n  <xs:annotation>\\r\\n    <xs:appinfo>\\r\\n      <b:schemaInfo \
default_pad_char=\\" \\" count_positions_by_byte=\\"false\\" parser_optimization=\\"speed\\" lookahead_depth=\\"3\\" \
suppress_empty_nodes=\\"false\\" generate_empty_nodes=\\"true\\" allow_early_termination=\\"false\\" \
early_terminate_optional_fields=\\"false\\" allow_message_breakup_of_infix_root=\\"false\\" \
compile_parse_tables=\\"false\\" standard=\\"Flat File\\" root_reference=\\"OrderFile\\" />\\r\\n      \
<schemaEditorExtension:schemaInfo namespaceAlias=\\"b\\" extensionClass=\\"Microsoft.BizTalk.FlatFileExtension.FlatFile\
Extension\\" standardName=\\"Flat File\\" xmlns:schemaEditorExtension=\\"http://schemas.microsoft.com/BizTalk/2003/Sche\
maEditorExtensions\\" />\\r\\n    </xs:appinfo>\\r\\n  </xs:annotation>\\r\\n  <xs:element name=\\"OrderFile\\">\\r\\n \
   <xs:annotation>\\r\\n      <xs:appinfo>\\r\\n        <b:recordInfo structure=\\"delimited\\" \
preserve_delimiter_for_empty_data=\\"true\\" suppress_trailing_delimiters=\\"false\\" sequence_number=\\"1\\" />\\r\\n \
     </xs:appinfo>\\r\\n    </xs:annotation>\\r\\n    <xs:complexType>\\r\\n      <xs:sequence>\\r\\n        \
<xs:annotation>\\r\\n          <xs:appinfo>\\r\\n            <b:groupInfo sequence_number=\\"0\\" />\\r\\n          \
</xs:appinfo>\\r\\n        </xs:annotation>\\r\\n        <xs:element name=\\"Order\\">\\r\\n          \
<xs:annotation>\\r\\n            <xs:appinfo>\\r\\n              <b:recordInfo sequence_number=\\"1\\" \
structure=\\"delimited\\" preserve_delimiter_for_empty_data=\\"true\\" suppress_trailing_delimiters=\\"false\\" \
child_delimiter_type=\\"hex\\" child_delimiter=\\"0x0D 0x0A\\" child_order=\\"infix\\" />\\r\\n            \
</xs:appinfo>\\r\\n          </xs:annotation>\\r\\n          <xs:complexType>\\r\\n            <xs:sequence>\\r\\n     \
         <xs:annotation>\\r\\n                <xs:appinfo>\\r\\n                  <b:groupInfo sequence_number=\\"0\\" \
/>\\r\\n                </xs:appinfo>\\r\\n              </xs:annotation>\\r\\n              <xs:element \
name=\\"Header\\">\\r\\n                <xs:annotation>\\r\\n                  <xs:appinfo>\\r\\n                    \
<b:recordInfo sequence_number=\\"1\\" structure=\\"delimited\\" preserve_delimiter_for_empty_data=\\"true\\" \
suppress_trailing_delimiters=\\"false\\" child_delimiter_type=\\"char\\" child_delimiter=\\"|\\" \
child_order=\\"infix\\" tag_name=\\"HDR|\\" />\\r\\n                  </xs:appinfo>\\r\\n                \
</xs:annotation>\\r\\n                <xs:complexType>\\r\\n                  <xs:sequence>\\r\\n                    \
<xs:annotation>\\r\\n                      <xs:appinfo>\\r\\n                        <b:groupInfo \
sequence_number=\\"0\\" />\\r\\n                      </xs:appinfo>\\r\\n                    </xs:annotation>\\r\\n    \
                <xs:element name=\\"PODate\\" type=\\"xs:string\\">\\r\\n                      <xs:annotation>\\r\\n   \
                     <xs:appinfo>\\r\\n                          <b:fieldInfo sequence_number=\\"1\\" \
justification=\\"left\\" />\\r\\n                        </xs:appinfo>\\r\\n                      \
</xs:annotation>\\r\\n                    </xs:element>\\r\\n                    <xs:element name=\\"PONumber\\" \
type=\\"xs:string\\">\\r\\n                      <xs:annotation>\\r\\n                        <xs:appinfo>\\r\\n       \
                   <b:fieldInfo justification=\\"left\\" sequence_number=\\"2\\" />\\r\\n                        \
</xs:appinfo>\\r\\n                      </xs:annotation>\\r\\n                    </xs:element>\\r\\n                 \
   <xs:element name=\\"CustomerID\\" type=\\"xs:string\\">\\r\\n                      <xs:annotation>\\r\\n            \
            <xs:appinfo>\\r\\n                          <b:fieldInfo sequence_number=\\"3\\" justification=\\"left\\" \
/>\\r\\n                        </xs:appinfo>\\r\\n                      </xs:annotation>\\r\\n                    \
</xs:element>\\r\\n                    <xs:element name=\\"CustomerContactName\\" type=\\"xs:string\\">\\r\\n          \
            <xs:annotation>\\r\\n                        <xs:appinfo>\\r\\n                          <b:fieldInfo \
sequence_number=\\"4\\" justification=\\"left\\" />\\r\\n                        </xs:appinfo>\\r\\n                   \
   </xs:annotation>\\r\\n                    </xs:element>\\r\\n                    <xs:element \
name=\\"CustomerContactPhone\\" type=\\"xs:string\\">\\r\\n                      <xs:annotation>\\r\\n                 \
       <xs:appinfo>\\r\\n                          <b:fieldInfo sequence_number=\\"5\\" justification=\\"left\\" \
/>\\r\\n                        </xs:appinfo>\\r\\n                      </xs:annotation>\\r\\n                    \
</xs:element>\\r\\n                  </xs:sequence>\\r\\n                </xs:complexType>\\r\\n              \
</xs:element>\\r\\n              <xs:element minOccurs=\\"1\\" maxOccurs=\\"unbounded\\" name=\\"LineItems\\">\\r\\n   \
             <xs:annotation>\\r\\n                  <xs:appinfo>\\r\\n                    <b:recordInfo \
sequence_number=\\"2\\" structure=\\"delimited\\" preserve_delimiter_for_empty_data=\\"true\\" \
suppress_trailing_delimiters=\\"false\\" child_delimiter_type=\\"char\\" child_delimiter=\\"|\\" \
child_order=\\"infix\\" tag_name=\\"DTL|\\" />\\r\\n                  </xs:appinfo>\\r\\n                \
</xs:annotation>\\r\\n                <xs:complexType>\\r\\n                  <xs:sequence>\\r\\n                    \
<xs:annotation>\\r\\n                      <xs:appinfo>\\r\\n                        <b:groupInfo \
sequence_number=\\"0\\" />\\r\\n                      </xs:appinfo>\\r\\n                    </xs:annotation>\\r\\n    \
                <xs:element name=\\"PONumber\\" type=\\"xs:string\\">\\r\\n                      <xs:annotation>\\r\\n \
                       <xs:appinfo>\\r\\n                          <b:fieldInfo sequence_number=\\"1\\" \
justification=\\"left\\" />\\r\\n                        </xs:appinfo>\\r\\n                      \
</xs:annotation>\\r\\n                    </xs:element>\\r\\n                    <xs:element name=\\"ItemOrdered\\" \
type=\\"xs:string\\">\\r\\n                      <xs:annotation>\\r\\n                        <xs:appinfo>\\r\\n       \
                   <b:fieldInfo sequence_number=\\"2\\" justification=\\"left\\" />\\r\\n                        \
</xs:appinfo>\\r\\n                      </xs:annotation>\\r\\n                    </xs:element>\\r\\n                 \
   <xs:element name=\\"Quantity\\" type=\\"xs:string\\">\\r\\n                      <xs:annotation>\\r\\n              \
          <xs:appinfo>\\r\\n                          <b:fieldInfo sequence_number=\\"3\\" justification=\\"left\\" \
/>\\r\\n                        </xs:appinfo>\\r\\n                      </xs:annotation>\\r\\n                    \
</xs:element>\\r\\n                    <xs:element name=\\"UOM\\" type=\\"xs:string\\">\\r\\n                      \
<xs:annotation>\\r\\n                        <xs:appinfo>\\r\\n                          <b:fieldInfo \
sequence_number=\\"4\\" justification=\\"left\\" />\\r\\n                        </xs:appinfo>\\r\\n                   \
   </xs:annotation>\\r\\n                    </xs:element>\\r\\n                    <xs:element name=\\"Price\\" \
type=\\"xs:string\\">\\r\\n                      <xs:annotation>\\r\\n                        <xs:appinfo>\\r\\n       \
                   <b:fieldInfo sequence_number=\\"5\\" justification=\\"left\\" />\\r\\n                        \
</xs:appinfo>\\r\\n                      </xs:annotation>\\r\\n                    </xs:element>\\r\\n                 \
   <xs:element name=\\"ExtendedPrice\\" type=\\"xs:string\\">\\r\\n                      <xs:annotation>\\r\\n         \
               <xs:appinfo>\\r\\n                          <b:fieldInfo sequence_number=\\"6\\" \
justification=\\"left\\" />\\r\\n                        </xs:appinfo>\\r\\n                      \
</xs:annotation>\\r\\n                    </xs:element>\\r\\n                    <xs:element name=\\"Description\\" \
type=\\"xs:string\\">\\r\\n                      <xs:annotation>\\r\\n                        <xs:appinfo>\\r\\n       \
                   <b:fieldInfo sequence_number=\\"7\\" justification=\\"left\\" />\\r\\n                        \
</xs:appinfo>\\r\\n                      </xs:annotation>\\r\\n                    </xs:element>\\r\\n                 \
 </xs:sequence>\\r\\n                </xs:complexType>\\r\\n              </xs:element>\\r\\n            \
</xs:sequence>\\r\\n          </xs:complexType>\\r\\n        </xs:element>\\r\\n      </xs:sequence>\\r\\n    \
</xs:complexType>\\r\\n  </xs:element>\\r\\n</xs:schema>" --properties-content-type "application/xml" --metadata "{}" \
--schema-type "Xml" --tags integrationAccountSchemaName="IntegrationAccountSchema8120" --integration-account-name \
"testIntegrationAccount" --resource-group "testResourceGroup" --schema-name "testSchema"
```
##### <a name="ParametersIntegrationAccountSchemasCreateOrUpdate#Create">Parameters</a> 
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

#### <a name="IntegrationAccountSchemasCreateOrUpdate#Update">Command `az logic integration-account-schema update`</a>

##### <a name="ParametersIntegrationAccountSchemasCreateOrUpdate#Update">Parameters</a> 
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

#### <a name="IntegrationAccountSchemasDelete">Command `az logic integration-account-schema delete`</a>

##### <a name="ExamplesIntegrationAccountSchemasDelete">Example</a>
```
az logic integration-account-schema delete --integration-account-name "testIntegrationAccount" --resource-group \
"testResourceGroup" --schema-name "testSchema"
```
##### <a name="ParametersIntegrationAccountSchemasDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--schema-name**|string|The integration account schema name.|schema_name|schemaName|

#### <a name="IntegrationAccountSchemasListContentCallbackUrl">Command `az logic integration-account-schema list-content-callback-url`</a>

##### <a name="ExamplesIntegrationAccountSchemasListContentCallbackUrl">Example</a>
```
az logic integration-account-schema list-content-callback-url --integration-account-name "testIntegrationAccount" \
--key-type "Primary" --not-after "2018-04-19T16:00:00Z" --resource-group "testResourceGroup" --schema-name \
"testSchema"
```
##### <a name="ParametersIntegrationAccountSchemasListContentCallbackUrl">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--schema-name**|string|The integration account schema name.|schema_name|schemaName|
|**--not-after**|date-time|The expiry time.|not_after|notAfter|
|**--key-type**|choice|The key type.|key_type|keyType|

### group `az logic integration-account-session`
#### <a name="IntegrationAccountSessionsList">Command `az logic integration-account-session list`</a>

##### <a name="ExamplesIntegrationAccountSessionsList">Example</a>
```
az logic integration-account-session list --integration-account-name "testia123" --resource-group "testrg123"
```
##### <a name="ParametersIntegrationAccountSessionsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--top**|integer|The number of items to be included in the result.|top|$top|
|**--filter**|string|The filter to apply on the operation. Options for filters include: ChangedTime.|filter|$filter|

#### <a name="IntegrationAccountSessionsGet">Command `az logic integration-account-session show`</a>

##### <a name="ExamplesIntegrationAccountSessionsGet">Example</a>
```
az logic integration-account-session show --integration-account-name "testia123" --resource-group "testrg123" \
--session-name "testsession123-ICN"
```
##### <a name="ParametersIntegrationAccountSessionsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--session-name**|string|The integration account session name.|session_name|sessionName|

#### <a name="IntegrationAccountSessionsCreateOrUpdate#Create">Command `az logic integration-account-session create`</a>

##### <a name="ExamplesIntegrationAccountSessionsCreateOrUpdate#Create">Example</a>
```
az logic integration-account-session create --integration-account-name "testia123" --resource-group "testrg123" \
--content "{\\"controlNumber\\":\\"1234\\",\\"controlNumberChangedTime\\":\\"2017-02-21T22:30:11.9923759Z\\"}" \
--session-name "testsession123-ICN"
```
##### <a name="ParametersIntegrationAccountSessionsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--session-name**|string|The integration account session name.|session_name|sessionName|
|**--location**|string|The resource location.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|
|**--content**|any|The session content.|content|content|

#### <a name="IntegrationAccountSessionsCreateOrUpdate#Update">Command `az logic integration-account-session update`</a>

##### <a name="ParametersIntegrationAccountSessionsCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--session-name**|string|The integration account session name.|session_name|sessionName|
|**--location**|string|The resource location.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|
|**--content**|any|The session content.|content|content|

#### <a name="IntegrationAccountSessionsDelete">Command `az logic integration-account-session delete`</a>

##### <a name="ExamplesIntegrationAccountSessionsDelete">Example</a>
```
az logic integration-account-session delete --integration-account-name "testia123" --resource-group "testrg123" \
--session-name "testsession123-ICN"
```
##### <a name="ParametersIntegrationAccountSessionsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--integration-account-name**|string|The integration account name.|integration_account_name|integrationAccountName|
|**--session-name**|string|The integration account session name.|session_name|sessionName|

### group `az logic integration-service-environment`
#### <a name="IntegrationServiceEnvironmentsListByResourceGroup">Command `az logic integration-service-environment list`</a>

##### <a name="ExamplesIntegrationServiceEnvironmentsListByResourceGroup">Example</a>
```
az logic integration-service-environment list --resource-group "testResourceGroup"
```
##### <a name="ParametersIntegrationServiceEnvironmentsListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group**|string|The resource group.|resource_group|resourceGroup|
|**--top**|integer|The number of items to be included in the result.|top|$top|

#### <a name="IntegrationServiceEnvironmentsListBySubscription">Command `az logic integration-service-environment list`</a>

##### <a name="ExamplesIntegrationServiceEnvironmentsListBySubscription">Example</a>
```
az logic integration-service-environment list
```
##### <a name="ParametersIntegrationServiceEnvironmentsListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="IntegrationServiceEnvironmentsGet">Command `az logic integration-service-environment show`</a>

##### <a name="ExamplesIntegrationServiceEnvironmentsGet">Example</a>
```
az logic integration-service-environment show --name "testIntegrationServiceEnvironment" --resource-group \
"testResourceGroup"
```
##### <a name="ParametersIntegrationServiceEnvironmentsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group**|string|The resource group.|resource_group|resourceGroup|
|**--integration-service-environment-name**|string|The integration service environment name.|integration_service_environment_name|integrationServiceEnvironmentName|

#### <a name="IntegrationServiceEnvironmentsCreateOrUpdate#Create">Command `az logic integration-service-environment create`</a>

##### <a name="ExamplesIntegrationServiceEnvironmentsCreateOrUpdate#Create">Example</a>
```
az logic integration-service-environment create --location "brazilsouth" --encryption-configuration \
"{\\"encryptionKeyReference\\":{\\"keyName\\":\\"testKeyName\\",\\"keyVault\\":{\\"id\\":\\"/subscriptions/f34b22a3-220\
2-4fb1-b040-1332bd928c84/resourceGroups/testResourceGroup/providers/Microsoft.KeyVault/vaults/testKeyVault\\"},\\"keyVe\
rsion\\":\\"13b261d30b984753869902d7f47f4d55\\"}}" --network-configuration "{\\"accessEndpoint\\":{\\"type\\":\\"Intern\
al\\"},\\"subnets\\":[{\\"id\\":\\"/subscriptions/f34b22a3-2202-4fb1-b040-1332bd928c84/resourceGroups/testResourceGroup\
/providers/Microsoft.Network/virtualNetworks/testVNET/subnets/s1\\"},{\\"id\\":\\"/subscriptions/f34b22a3-2202-4fb1-b04\
0-1332bd928c84/resourceGroups/testResourceGroup/providers/Microsoft.Network/virtualNetworks/testVNET/subnets/s2\\"},{\\\
"id\\":\\"/subscriptions/f34b22a3-2202-4fb1-b040-1332bd928c84/resourceGroups/testResourceGroup/providers/Microsoft.Netw\
ork/virtualNetworks/testVNET/subnets/s3\\"},{\\"id\\":\\"/subscriptions/f34b22a3-2202-4fb1-b040-1332bd928c84/resourceGr\
oups/testResourceGroup/providers/Microsoft.Network/virtualNetworks/testVNET/subnets/s4\\"}]}" --sku name="Premium" \
capacity=2 --name "testIntegrationServiceEnvironment" --resource-group "testResourceGroup"
```
##### <a name="ParametersIntegrationServiceEnvironmentsCreateOrUpdate#Create">Parameters</a> 
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
|**--encryption-configuration**|object|The encryption configuration.|encryption_configuration|encryptionConfiguration|

#### <a name="IntegrationServiceEnvironmentsUpdate">Command `az logic integration-service-environment update`</a>

##### <a name="ExamplesIntegrationServiceEnvironmentsUpdate">Example</a>
```
az logic integration-service-environment update --sku name="Developer" capacity=0 --tags tag1="value1" --name \
"testIntegrationServiceEnvironment" --resource-group "testResourceGroup"
```
##### <a name="ParametersIntegrationServiceEnvironmentsUpdate">Parameters</a> 
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
|**--encryption-configuration**|object|The encryption configuration.|encryption_configuration|encryptionConfiguration|

#### <a name="IntegrationServiceEnvironmentsDelete">Command `az logic integration-service-environment delete`</a>

##### <a name="ExamplesIntegrationServiceEnvironmentsDelete">Example</a>
```
az logic integration-service-environment delete --name "testIntegrationServiceEnvironment" --resource-group \
"testResourceGroup"
```
##### <a name="ParametersIntegrationServiceEnvironmentsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group**|string|The resource group.|resource_group|resourceGroup|
|**--integration-service-environment-name**|string|The integration service environment name.|integration_service_environment_name|integrationServiceEnvironmentName|

#### <a name="IntegrationServiceEnvironmentsRestart">Command `az logic integration-service-environment restart`</a>

##### <a name="ExamplesIntegrationServiceEnvironmentsRestart">Example</a>
```
az logic integration-service-environment restart --name "testIntegrationServiceEnvironment" --resource-group \
"testResourceGroup"
```
##### <a name="ParametersIntegrationServiceEnvironmentsRestart">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group**|string|The resource group.|resource_group|resourceGroup|
|**--integration-service-environment-name**|string|The integration service environment name.|integration_service_environment_name|integrationServiceEnvironmentName|

### group `az logic integration-service-environment-managed-api`
#### <a name="IntegrationServiceEnvironmentManagedApisList">Command `az logic integration-service-environment-managed-api list`</a>

##### <a name="ExamplesIntegrationServiceEnvironmentManagedApisList">Example</a>
```
az logic integration-service-environment-managed-api list --integration-service-environment-name \
"testIntegrationServiceEnvironment" --resource-group "testResourceGroup"
```
##### <a name="ParametersIntegrationServiceEnvironmentManagedApisList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group**|string|The resource group.|resource_group|resourceGroup|
|**--integration-service-environment-name**|string|The integration service environment name.|integration_service_environment_name|integrationServiceEnvironmentName|

#### <a name="IntegrationServiceEnvironmentManagedApisGet">Command `az logic integration-service-environment-managed-api show`</a>

##### <a name="ExamplesIntegrationServiceEnvironmentManagedApisGet">Example</a>
```
az logic integration-service-environment-managed-api show --api-name "servicebus" --integration-service-environment-nam\
e "testIntegrationServiceEnvironment" --resource-group "testResourceGroup"
```
##### <a name="ParametersIntegrationServiceEnvironmentManagedApisGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group**|string|The resource group name.|resource_group|resourceGroup|
|**--integration-service-environment-name**|string|The integration service environment name.|integration_service_environment_name|integrationServiceEnvironmentName|
|**--api-name**|string|The api name.|api_name|apiName|

#### <a name="IntegrationServiceEnvironmentManagedApisDelete">Command `az logic integration-service-environment-managed-api delete`</a>

##### <a name="ExamplesIntegrationServiceEnvironmentManagedApisDelete">Example</a>
```
az logic integration-service-environment-managed-api delete --api-name "servicebus" --integration-service-environment-n\
ame "testIntegrationServiceEnvironment" --resource-group "testResourceGroup"
```
##### <a name="ParametersIntegrationServiceEnvironmentManagedApisDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group**|string|The resource group.|resource_group|resourceGroup|
|**--integration-service-environment-name**|string|The integration service environment name.|integration_service_environment_name|integrationServiceEnvironmentName|
|**--api-name**|string|The api name.|api_name|apiName|

#### <a name="IntegrationServiceEnvironmentManagedApisPut">Command `az logic integration-service-environment-managed-api put`</a>

##### <a name="ExamplesIntegrationServiceEnvironmentManagedApisPut">Example</a>
```
az logic integration-service-environment-managed-api put --api-name "servicebus" --integration-service-environment-name\
 "testIntegrationServiceEnvironment" --resource-group "testResourceGroup"
```
##### <a name="ParametersIntegrationServiceEnvironmentManagedApisPut">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group**|string|The resource group name.|resource_group|resourceGroup|
|**--integration-service-environment-name**|string|The integration service environment name.|integration_service_environment_name|integrationServiceEnvironmentName|
|**--api-name**|string|The api name.|api_name|apiName|

### group `az logic integration-service-environment-managed-api-operation`
#### <a name="IntegrationServiceEnvironmentManagedApiOperationsList">Command `az logic integration-service-environment-managed-api-operation list`</a>

##### <a name="ExamplesIntegrationServiceEnvironmentManagedApiOperationsList">Example</a>
```
az logic integration-service-environment-managed-api-operation list --api-name "servicebus" \
--integration-service-environment-name "testIntegrationServiceEnvironment" --resource-group "testResourceGroup"
```
##### <a name="ParametersIntegrationServiceEnvironmentManagedApiOperationsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group**|string|The resource group.|resource_group|resourceGroup|
|**--integration-service-environment-name**|string|The integration service environment name.|integration_service_environment_name|integrationServiceEnvironmentName|
|**--api-name**|string|The api name.|api_name|apiName|

### group `az logic integration-service-environment-network-health`
#### <a name="IntegrationServiceEnvironmentNetworkHealthGet">Command `az logic integration-service-environment-network-health show`</a>

##### <a name="ExamplesIntegrationServiceEnvironmentNetworkHealthGet">Example</a>
```
az logic integration-service-environment-network-health show --integration-service-environment-name \
"testIntegrationServiceEnvironment" --resource-group "testResourceGroup"
```
##### <a name="ParametersIntegrationServiceEnvironmentNetworkHealthGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group**|string|The resource group.|resource_group|resourceGroup|
|**--integration-service-environment-name**|string|The integration service environment name.|integration_service_environment_name|integrationServiceEnvironmentName|

### group `az logic integration-service-environment-sku`
#### <a name="IntegrationServiceEnvironmentSkusList">Command `az logic integration-service-environment-sku list`</a>

##### <a name="ExamplesIntegrationServiceEnvironmentSkusList">Example</a>
```
az logic integration-service-environment-sku list --integration-service-environment-name \
"testIntegrationServiceEnvironment" --resource-group "testResourceGroup"
```
##### <a name="ParametersIntegrationServiceEnvironmentSkusList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group**|string|The resource group.|resource_group|resourceGroup|
|**--integration-service-environment-name**|string|The integration service environment name.|integration_service_environment_name|integrationServiceEnvironmentName|

### group `az logic workflow`
#### <a name="WorkflowsListByResourceGroup">Command `az logic workflow list`</a>

##### <a name="ExamplesWorkflowsListByResourceGroup">Example</a>
```
az logic workflow list --resource-group "test-resource-group"
```
##### <a name="ParametersWorkflowsListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--top**|integer|The number of items to be included in the result.|top|$top|
|**--filter**|string|The filter to apply on the operation. Options for filters include: State, Trigger, and ReferencedResourceId.|filter|$filter|

#### <a name="WorkflowsListBySubscription">Command `az logic workflow list`</a>

##### <a name="ExamplesWorkflowsListBySubscription">Example</a>
```
az logic workflow list
```
##### <a name="ParametersWorkflowsListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="WorkflowsGet">Command `az logic workflow show`</a>

##### <a name="ExamplesWorkflowsGet">Example</a>
```
az logic workflow show --resource-group "test-resource-group" --name "test-workflow"
```
##### <a name="ParametersWorkflowsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|

#### <a name="WorkflowsCreateOrUpdate#Create">Command `az logic workflow create`</a>

##### <a name="ExamplesWorkflowsCreateOrUpdate#Create">Example</a>
```
az logic workflow create --resource-group "test-resource-group" --endpoints-configuration-workflow \
location="brazilsouth" properties={"definition":{"$schema":"https://schema.management.azure.com/providers/Microsoft.Log\
ic/schemas/2016-06-01/workflowdefinition.json#","actions":{"Find_pet_by_ID":{"type":"ApiConnection","inputs":{"path":"/\
pet/@{encodeURIComponent(\'1\')}","method":"get","host":{"connection":{"name":"@parameters(\'$connections\')[\'test-cus\
tom-connector\'][\'connectionId\']"}}},"runAfter":{}}},"contentVersion":"1.0.0.0","outputs":{},"parameters":{"$connecti\
ons":{"type":"Object","defaultValue":{}}},"triggers":{"manual":{"type":"Request","inputs":{"schema":{}},"kind":"Http"}}\
},"integrationAccount":{"id":"/subscriptions/34adfa4f-cedf-4dc0-ba29-b6d1a69ab345/resourceGroups/test-resource-group/pr\
oviders/Microsoft.Logic/integrationAccounts/test-integration-account"},"parameters":{"$connections":{"value":{"test-cus\
tom-connector":{"connectionId":"/subscriptions/34adfa4f-cedf-4dc0-ba29-b6d1a69ab345/resourceGroups/test-resource-group/\
providers/Microsoft.Web/connections/test-custom-connector","connectionName":"test-custom-connector","id":"/subscription\
s/34adfa4f-cedf-4dc0-ba29-b6d1a69ab345/providers/Microsoft.Web/locations/brazilsouth/managedApis/test-custom-connector"\
}}}}} tags={} --name "test-workflow"
```
##### <a name="ParametersWorkflowsCreateOrUpdate#Create">Parameters</a> 
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
|**--access-control-triggers**|object|The access control configuration for invoking workflow triggers.|triggers|triggers|
|**--access-control-contents**|object|The access control configuration for accessing workflow run contents.|contents|contents|
|**--access-control-actions**|object|The access control configuration for workflow actions.|actions|actions|
|**--access-control-workflow-management**|object|The access control configuration for workflow management.|workflow_management|workflowManagement|
|**--endpoints-configuration-workflow**|object|The workflow endpoints.|workflow|workflow|
|**--endpoints-configuration-connector**|object|The connector endpoints.|connector|connector|

#### <a name="WorkflowsUpdate">Command `az logic workflow update`</a>

##### <a name="ExamplesWorkflowsUpdate">Example</a>
```
az logic workflow update --resource-group "test-resource-group" --name "test-workflow"
```
##### <a name="ParametersWorkflowsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|

#### <a name="WorkflowsDelete">Command `az logic workflow delete`</a>

##### <a name="ExamplesWorkflowsDelete">Example</a>
```
az logic workflow delete --resource-group "test-resource-group" --name "test-workflow"
```
##### <a name="ParametersWorkflowsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|

#### <a name="WorkflowsDisable">Command `az logic workflow disable`</a>

##### <a name="ExamplesWorkflowsDisable">Example</a>
```
az logic workflow disable --resource-group "test-resource-group" --name "test-workflow"
```
##### <a name="ParametersWorkflowsDisable">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|

#### <a name="WorkflowsEnable">Command `az logic workflow enable`</a>

##### <a name="ExamplesWorkflowsEnable">Example</a>
```
az logic workflow enable --resource-group "test-resource-group" --name "test-workflow"
```
##### <a name="ParametersWorkflowsEnable">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|

#### <a name="WorkflowsGenerateUpgradedDefinition">Command `az logic workflow generate-upgraded-definition`</a>

##### <a name="ExamplesWorkflowsGenerateUpgradedDefinition">Example</a>
```
az logic workflow generate-upgraded-definition --target-schema-version "2016-06-01" --resource-group \
"test-resource-group" --name "test-workflow"
```
##### <a name="ParametersWorkflowsGenerateUpgradedDefinition">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--target-schema-version**|string|The target schema version.|target_schema_version|targetSchemaVersion|

#### <a name="WorkflowsListCallbackUrl">Command `az logic workflow list-callback-url`</a>

##### <a name="ExamplesWorkflowsListCallbackUrl">Example</a>
```
az logic workflow list-callback-url --key-type "Primary" --not-after "2018-04-19T16:00:00Z" --resource-group \
"testResourceGroup" --name "testWorkflow"
```
##### <a name="ParametersWorkflowsListCallbackUrl">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--not-after**|date-time|The expiry time.|not_after|notAfter|
|**--key-type**|choice|The key type.|key_type|keyType|

#### <a name="WorkflowsListSwagger">Command `az logic workflow list-swagger`</a>

##### <a name="ExamplesWorkflowsListSwagger">Example</a>
```
az logic workflow list-swagger --resource-group "testResourceGroup" --name "testWorkflowName"
```
##### <a name="ParametersWorkflowsListSwagger">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|

#### <a name="WorkflowsMove">Command `az logic workflow move`</a>

##### <a name="ExamplesWorkflowsMove">Example</a>
```
az logic workflow move --id "subscriptions/34adfa4f-cedf-4dc0-ba29-b6d1a69ab345/resourceGroups/newResourceGroup/provide\
rs/Microsoft.Logic/workflows/newWorkflowName" --resource-group "testResourceGroup" --name "testWorkflow"
```
##### <a name="ParametersWorkflowsMove">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--id**|string|The resource id.|id|id|

#### <a name="WorkflowsRegenerateAccessKey">Command `az logic workflow regenerate-access-key`</a>

##### <a name="ExamplesWorkflowsRegenerateAccessKey">Example</a>
```
az logic workflow regenerate-access-key --key-type "Primary" --resource-group "testResourceGroup" --name \
"testWorkflowName"
```
##### <a name="ParametersWorkflowsRegenerateAccessKey">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--key-type**|choice|The key type.|key_type|keyType|

#### <a name="WorkflowsValidateByLocation">Command `az logic workflow validate-by-location`</a>

##### <a name="ExamplesWorkflowsValidateByLocation">Example</a>
```
az logic workflow validate-by-location --location "brazilsouth" --resource-group "test-resource-group" \
--resource-location "brazilsouth" --definition "{\\"$schema\\":\\"https://schema.management.azure.com/providers/Microso\
ft.Logic/schemas/2016-06-01/workflowdefinition.json#\\",\\"actions\\":{},\\"contentVersion\\":\\"1.0.0.0\\",\\"outputs\
\\":{},\\"parameters\\":{},\\"triggers\\":{}}" --name "test-workflow"
```
##### <a name="ParametersWorkflowsValidateByLocation">Parameters</a> 
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
|**--access-control-triggers**|object|The access control configuration for invoking workflow triggers.|triggers|triggers|
|**--access-control-contents**|object|The access control configuration for accessing workflow run contents.|contents|contents|
|**--access-control-actions**|object|The access control configuration for workflow actions.|actions|actions|
|**--access-control-workflow-management**|object|The access control configuration for workflow management.|workflow_management|workflowManagement|
|**--endpoints-configuration-workflow**|object|The workflow endpoints.|workflow|workflow|
|**--endpoints-configuration-connector**|object|The connector endpoints.|connector|connector|

#### <a name="WorkflowsValidateByResourceGroup">Command `az logic workflow validate-by-resource-group`</a>

##### <a name="ExamplesWorkflowsValidateByResourceGroup">Example</a>
```
az logic workflow validate-by-resource-group --resource-group "test-resource-group" --location "brazilsouth" \
--definition "{\\"$schema\\":\\"https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workfl\
owdefinition.json#\\",\\"actions\\":{},\\"contentVersion\\":\\"1.0.0.0\\",\\"outputs\\":{},\\"parameters\\":{},\\"trigg\
ers\\":{}}" --name "test-workflow"
```
##### <a name="ParametersWorkflowsValidateByResourceGroup">Parameters</a> 
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
|**--access-control-triggers**|object|The access control configuration for invoking workflow triggers.|triggers|triggers|
|**--access-control-contents**|object|The access control configuration for accessing workflow run contents.|contents|contents|
|**--access-control-actions**|object|The access control configuration for workflow actions.|actions|actions|
|**--access-control-workflow-management**|object|The access control configuration for workflow management.|workflow_management|workflowManagement|
|**--endpoints-configuration-workflow**|object|The workflow endpoints.|workflow|workflow|
|**--endpoints-configuration-connector**|object|The connector endpoints.|connector|connector|

### group `az logic workflow-run`
#### <a name="WorkflowRunsList">Command `az logic workflow-run list`</a>

##### <a name="ExamplesWorkflowRunsList">Example</a>
```
az logic workflow-run list --resource-group "test-resource-group" --workflow-name "test-workflow"
```
##### <a name="ParametersWorkflowRunsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--top**|integer|The number of items to be included in the result.|top|$top|
|**--filter**|string|The filter to apply on the operation. Options for filters include: Status, StartTime, and ClientTrackingId.|filter|$filter|

#### <a name="WorkflowRunsGet">Command `az logic workflow-run show`</a>

##### <a name="ExamplesWorkflowRunsGet">Example</a>
```
az logic workflow-run show --resource-group "test-resource-group" --run-name "08586676746934337772206998657CU22" \
--workflow-name "test-workflow"
```
##### <a name="ParametersWorkflowRunsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--run-name**|string|The workflow run name.|run_name|runName|

#### <a name="WorkflowRunsCancel">Command `az logic workflow-run cancel`</a>

##### <a name="ExamplesWorkflowRunsCancel">Example</a>
```
az logic workflow-run cancel --resource-group "test-resource-group" --run-name "08586676746934337772206998657CU22" \
--workflow-name "test-workflow"
```
##### <a name="ParametersWorkflowRunsCancel">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--run-name**|string|The workflow run name.|run_name|runName|

### group `az logic workflow-run-action`
#### <a name="WorkflowRunActionsList">Command `az logic workflow-run-action list`</a>

##### <a name="ExamplesWorkflowRunActionsList">Example</a>
```
az logic workflow-run-action list --resource-group "test-resource-group" --run-name "08586676746934337772206998657CU22"\
 --workflow-name "test-workflow"
```
##### <a name="ParametersWorkflowRunActionsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--run-name**|string|The workflow run name.|run_name|runName|
|**--top**|integer|The number of items to be included in the result.|top|$top|
|**--filter**|string|The filter to apply on the operation. Options for filters include: Status.|filter|$filter|

#### <a name="WorkflowRunActionsGet">Command `az logic workflow-run-action show`</a>

##### <a name="ExamplesWorkflowRunActionsGet">Example</a>
```
az logic workflow-run-action show --action-name "HTTP" --resource-group "test-resource-group" --run-name \
"08586676746934337772206998657CU22" --workflow-name "test-workflow"
```
##### <a name="ParametersWorkflowRunActionsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--run-name**|string|The workflow run name.|run_name|runName|
|**--action-name**|string|The workflow action name.|action_name|actionName|

#### <a name="WorkflowRunActionsListExpressionTraces">Command `az logic workflow-run-action list-expression-trace`</a>

##### <a name="ExamplesWorkflowRunActionsListExpressionTraces">Example</a>
```
az logic workflow-run-action list-expression-trace --action-name "testAction" --resource-group "testResourceGroup" \
--run-name "08586776228332053161046300351" --workflow-name "testFlow"
```
##### <a name="ParametersWorkflowRunActionsListExpressionTraces">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--run-name**|string|The workflow run name.|run_name|runName|
|**--action-name**|string|The workflow action name.|action_name|actionName|

### group `az logic workflow-run-action-repetition`
#### <a name="WorkflowRunActionRepetitionsList">Command `az logic workflow-run-action-repetition list`</a>

##### <a name="ExamplesWorkflowRunActionRepetitionsList">Example</a>
```
az logic workflow-run-action-repetition list --action-name "testAction" --resource-group "testResourceGroup" \
--run-name "08586776228332053161046300351" --workflow-name "testFlow"
```
##### <a name="ParametersWorkflowRunActionRepetitionsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--run-name**|string|The workflow run name.|run_name|runName|
|**--action-name**|string|The workflow action name.|action_name|actionName|

#### <a name="WorkflowRunActionRepetitionsGet">Command `az logic workflow-run-action-repetition show`</a>

##### <a name="ExamplesWorkflowRunActionRepetitionsGet">Example</a>
```
az logic workflow-run-action-repetition show --action-name "testAction" --repetition-name "000001" --resource-group \
"testResourceGroup" --run-name "08586776228332053161046300351" --workflow-name "testFlow"
```
##### <a name="ParametersWorkflowRunActionRepetitionsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--run-name**|string|The workflow run name.|run_name|runName|
|**--action-name**|string|The workflow action name.|action_name|actionName|
|**--repetition-name**|string|The workflow repetition.|repetition_name|repetitionName|

#### <a name="WorkflowRunActionRepetitionsListExpressionTraces">Command `az logic workflow-run-action-repetition list-expression-trace`</a>

##### <a name="ExamplesWorkflowRunActionRepetitionsListExpressionTraces">Example</a>
```
az logic workflow-run-action-repetition list-expression-trace --action-name "testAction" --repetition-name "000001" \
--resource-group "testResourceGroup" --run-name "08586776228332053161046300351" --workflow-name "testFlow"
```
##### <a name="ParametersWorkflowRunActionRepetitionsListExpressionTraces">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--run-name**|string|The workflow run name.|run_name|runName|
|**--action-name**|string|The workflow action name.|action_name|actionName|
|**--repetition-name**|string|The workflow repetition.|repetition_name|repetitionName|

### group `az logic workflow-run-action-repetition-request-history`
#### <a name="WorkflowRunActionRepetitionsRequestHistoriesList">Command `az logic workflow-run-action-repetition-request-history list`</a>

##### <a name="ExamplesWorkflowRunActionRepetitionsRequestHistoriesList">Example</a>
```
az logic workflow-run-action-repetition-request-history list --action-name "HTTP_Webhook" --repetition-name "000001" \
--resource-group "test-resource-group" --run-name "08586776228332053161046300351" --workflow-name "test-workflow"
```
##### <a name="ParametersWorkflowRunActionRepetitionsRequestHistoriesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--run-name**|string|The workflow run name.|run_name|runName|
|**--action-name**|string|The workflow action name.|action_name|actionName|
|**--repetition-name**|string|The workflow repetition.|repetition_name|repetitionName|

#### <a name="WorkflowRunActionRepetitionsRequestHistoriesGet">Command `az logic workflow-run-action-repetition-request-history show`</a>

##### <a name="ExamplesWorkflowRunActionRepetitionsRequestHistoriesGet">Example</a>
```
az logic workflow-run-action-repetition-request-history show --action-name "HTTP_Webhook" --repetition-name "000001" \
--request-history-name "08586611142732800686" --resource-group "test-resource-group" --run-name \
"08586776228332053161046300351" --workflow-name "test-workflow"
```
##### <a name="ParametersWorkflowRunActionRepetitionsRequestHistoriesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--run-name**|string|The workflow run name.|run_name|runName|
|**--action-name**|string|The workflow action name.|action_name|actionName|
|**--repetition-name**|string|The workflow repetition.|repetition_name|repetitionName|
|**--request-history-name**|string|The request history name.|request_history_name|requestHistoryName|

### group `az logic workflow-run-action-request-history`
#### <a name="WorkflowRunActionRequestHistoriesList">Command `az logic workflow-run-action-request-history list`</a>

##### <a name="ExamplesWorkflowRunActionRequestHistoriesList">Example</a>
```
az logic workflow-run-action-request-history list --action-name "HTTP_Webhook" --resource-group "test-resource-group" \
--run-name "08586776228332053161046300351" --workflow-name "test-workflow"
```
##### <a name="ParametersWorkflowRunActionRequestHistoriesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--run-name**|string|The workflow run name.|run_name|runName|
|**--action-name**|string|The workflow action name.|action_name|actionName|

#### <a name="WorkflowRunActionRequestHistoriesGet">Command `az logic workflow-run-action-request-history show`</a>

##### <a name="ExamplesWorkflowRunActionRequestHistoriesGet">Example</a>
```
az logic workflow-run-action-request-history show --action-name "HTTP_Webhook" --request-history-name \
"08586611142732800686" --resource-group "test-resource-group" --run-name "08586776228332053161046300351" \
--workflow-name "test-workflow"
```
##### <a name="ParametersWorkflowRunActionRequestHistoriesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--run-name**|string|The workflow run name.|run_name|runName|
|**--action-name**|string|The workflow action name.|action_name|actionName|
|**--request-history-name**|string|The request history name.|request_history_name|requestHistoryName|

### group `az logic workflow-run-action-scope-repetition`
#### <a name="WorkflowRunActionScopeRepetitionsList">Command `az logic workflow-run-action-scope-repetition list`</a>

##### <a name="ExamplesWorkflowRunActionScopeRepetitionsList">Example</a>
```
az logic workflow-run-action-scope-repetition list --action-name "for_each" --resource-group "testResourceGroup" \
--run-name "08586776228332053161046300351" --workflow-name "testFlow"
```
##### <a name="ParametersWorkflowRunActionScopeRepetitionsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--run-name**|string|The workflow run name.|run_name|runName|
|**--action-name**|string|The workflow action name.|action_name|actionName|

#### <a name="WorkflowRunActionScopeRepetitionsGet">Command `az logic workflow-run-action-scope-repetition show`</a>

##### <a name="ExamplesWorkflowRunActionScopeRepetitionsGet">Example</a>
```
az logic workflow-run-action-scope-repetition show --action-name "for_each" --repetition-name "000000" \
--resource-group "testResourceGroup" --run-name "08586776228332053161046300351" --workflow-name "testFlow"
```
##### <a name="ParametersWorkflowRunActionScopeRepetitionsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--run-name**|string|The workflow run name.|run_name|runName|
|**--action-name**|string|The workflow action name.|action_name|actionName|
|**--repetition-name**|string|The workflow repetition.|repetition_name|repetitionName|

### group `az logic workflow-run-operation`
#### <a name="WorkflowRunOperationsGet">Command `az logic workflow-run-operation show`</a>

##### <a name="ExamplesWorkflowRunOperationsGet">Example</a>
```
az logic workflow-run-operation show --operation-id "ebdcbbde-c4db-43ec-987c-fd0f7726f43b" --resource-group \
"testResourceGroup" --run-name "08586774142730039209110422528" --workflow-name "testFlow"
```
##### <a name="ParametersWorkflowRunOperationsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--run-name**|string|The workflow run name.|run_name|runName|
|**--operation-id**|string|The workflow operation id.|operation_id|operationId|

### group `az logic workflow-trigger`
#### <a name="WorkflowTriggersList">Command `az logic workflow-trigger list`</a>

##### <a name="ExamplesWorkflowTriggersList">Example</a>
```
az logic workflow-trigger list --resource-group "test-resource-group" --workflow-name "test-workflow"
```
##### <a name="ParametersWorkflowTriggersList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--top**|integer|The number of items to be included in the result.|top|$top|
|**--filter**|string|The filter to apply on the operation.|filter|$filter|

#### <a name="WorkflowTriggersGet">Command `az logic workflow-trigger show`</a>

##### <a name="ExamplesWorkflowTriggersGet">Example</a>
```
az logic workflow-trigger show --resource-group "test-resource-group" --trigger-name "manual" --workflow-name \
"test-workflow"
```
##### <a name="ParametersWorkflowTriggersGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--trigger-name**|string|The workflow trigger name.|trigger_name|triggerName|

#### <a name="WorkflowTriggersGetSchemaJson">Command `az logic workflow-trigger get-schema-json`</a>

##### <a name="ExamplesWorkflowTriggersGetSchemaJson">Example</a>
```
az logic workflow-trigger get-schema-json --resource-group "testResourceGroup" --trigger-name "testTrigger" \
--workflow-name "testWorkflow"
```
##### <a name="ParametersWorkflowTriggersGetSchemaJson">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--trigger-name**|string|The workflow trigger name.|trigger_name|triggerName|

#### <a name="WorkflowTriggersListCallbackUrl">Command `az logic workflow-trigger list-callback-url`</a>

##### <a name="ExamplesWorkflowTriggersListCallbackUrl">Example</a>
```
az logic workflow-trigger list-callback-url --resource-group "test-resource-group" --trigger-name "manual" \
--workflow-name "test-workflow"
```
##### <a name="ParametersWorkflowTriggersListCallbackUrl">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--trigger-name**|string|The workflow trigger name.|trigger_name|triggerName|

#### <a name="WorkflowTriggersReset">Command `az logic workflow-trigger reset`</a>

##### <a name="ExamplesWorkflowTriggersReset">Example</a>
```
az logic workflow-trigger reset --resource-group "testResourceGroup" --trigger-name "testTrigger" --workflow-name \
"testWorkflow"
```
##### <a name="ParametersWorkflowTriggersReset">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--trigger-name**|string|The workflow trigger name.|trigger_name|triggerName|

#### <a name="WorkflowTriggersRun">Command `az logic workflow-trigger run`</a>

##### <a name="ExamplesWorkflowTriggersRun">Example</a>
```
az logic workflow-trigger run --resource-group "test-resource-group" --trigger-name "manual" --workflow-name \
"test-workflow"
```
##### <a name="ParametersWorkflowTriggersRun">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--trigger-name**|string|The workflow trigger name.|trigger_name|triggerName|

#### <a name="WorkflowTriggersSetState">Command `az logic workflow-trigger set-state`</a>

##### <a name="ExamplesWorkflowTriggersSetState">Example</a>
```
az logic workflow-trigger set-state --resource-group "testResourceGroup" --source id="subscriptions/34adfa4f-cedf-4dc0-\
ba29-b6d1a69ab345/resourceGroups/sourceResGroup/providers/Microsoft.Logic/workflows/sourceWorkflow/triggers/sourceTrigg\
er" --trigger-name "testTrigger" --workflow-name "testWorkflow"
```
##### <a name="ParametersWorkflowTriggersSetState">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--trigger-name**|string|The workflow trigger name.|trigger_name|triggerName|
|**--source**|object|The source.|source|source|

### group `az logic workflow-trigger-history`
#### <a name="WorkflowTriggerHistoriesList">Command `az logic workflow-trigger-history list`</a>

##### <a name="ExamplesWorkflowTriggerHistoriesList">Example</a>
```
az logic workflow-trigger-history list --resource-group "testResourceGroup" --trigger-name "testTriggerName" \
--workflow-name "testWorkflowName"
```
##### <a name="ParametersWorkflowTriggerHistoriesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--trigger-name**|string|The workflow trigger name.|trigger_name|triggerName|
|**--top**|integer|The number of items to be included in the result.|top|$top|
|**--filter**|string|The filter to apply on the operation. Options for filters include: Status, StartTime, and ClientTrackingId.|filter|$filter|

#### <a name="WorkflowTriggerHistoriesGet">Command `az logic workflow-trigger-history show`</a>

##### <a name="ExamplesWorkflowTriggerHistoriesGet">Example</a>
```
az logic workflow-trigger-history show --history-name "08586676746934337772206998657CU22" --resource-group \
"testResourceGroup" --trigger-name "testTriggerName" --workflow-name "testWorkflowName"
```
##### <a name="ParametersWorkflowTriggerHistoriesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--trigger-name**|string|The workflow trigger name.|trigger_name|triggerName|
|**--history-name**|string|The workflow trigger history name. Corresponds to the run name for triggers that resulted in a run.|history_name|historyName|

#### <a name="WorkflowTriggerHistoriesResubmit">Command `az logic workflow-trigger-history resubmit`</a>

##### <a name="ExamplesWorkflowTriggerHistoriesResubmit">Example</a>
```
az logic workflow-trigger-history resubmit --history-name "testHistoryName" --resource-group "testResourceGroup" \
--trigger-name "testTriggerName" --workflow-name "testWorkflowName"
```
##### <a name="ParametersWorkflowTriggerHistoriesResubmit">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--trigger-name**|string|The workflow trigger name.|trigger_name|triggerName|
|**--history-name**|string|The workflow trigger history name. Corresponds to the run name for triggers that resulted in a run.|history_name|historyName|

### group `az logic workflow-version`
#### <a name="WorkflowVersionsList">Command `az logic workflow-version list`</a>

##### <a name="ExamplesWorkflowVersionsList">Example</a>
```
az logic workflow-version list --resource-group "test-resource-group" --workflow-name "test-workflow"
```
##### <a name="ParametersWorkflowVersionsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--top**|integer|The number of items to be included in the result.|top|$top|

#### <a name="WorkflowVersionsGet">Command `az logic workflow-version show`</a>

##### <a name="ExamplesWorkflowVersionsGet">Example</a>
```
az logic workflow-version show --resource-group "test-resource-group" --version-id "08586676824806722526" \
--workflow-name "test-workflow"
```
##### <a name="ParametersWorkflowVersionsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--version-id**|string|The workflow versionId.|version_id|versionId|

### group `az logic workflow-version-trigger`
#### <a name="WorkflowVersionTriggersListCallbackUrl">Command `az logic workflow-version-trigger list-callback-url`</a>

##### <a name="ExamplesWorkflowVersionTriggersListCallbackUrl">Example</a>
```
az logic workflow-version-trigger list-callback-url --key-type "Primary" --not-after "2017-03-05T08:00:00Z" \
--resource-group "testResourceGroup" --trigger-name "testTriggerName" --version-id "testWorkflowVersionId" \
--workflow-name "testWorkflowName"
```
##### <a name="ParametersWorkflowVersionTriggersListCallbackUrl">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--workflow-name**|string|The workflow name.|workflow_name|workflowName|
|**--version-id**|string|The workflow versionId.|version_id|versionId|
|**--trigger-name**|string|The workflow trigger name.|trigger_name|triggerName|
|**--not-after**|date-time|The expiry time.|not_after|notAfter|
|**--key-type**|choice|The key type.|key_type|keyType|
