# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, StorageAccountPreparer, JMESPathCheck, NoneCheck,
                               api_version_constraint)
from azure.cli.testsdk.scenario_tests.decorators import AllowLargeResponse
from azure.cli.core.azclierror import ValidationError
from azure.core.exceptions import HttpResponseError


class ProviderHubScenario(ScenarioTest):

    def __init__(self, method_name, config_file=None, recording_dir=None, recording_name=None,
                 recording_processors=None,
                 replay_processors=None, recording_patches=None, replay_patches=None):
        super(ProviderHubScenario, self).__init__(
            method_name
        )
        self.kwargs.update({
            'subscription_id': self.get_subscription_id()
        })

        self.kwargs.update({
            'providerNamespace': 'Private.VPTest',
            'resourceType': 'employees',
            'customRolloutName': 'canaryTesting01',
            'defaultRolloutName': 'cliDefaultRollout',
            'region': 'eastus2euap',
            'notificationRegistration': 'testNotificationRegistration',
            'nestedResourceType': 'nestedResourceType',
            'skuName': 'default'
        })

    # EXAMPLE: /providerhub/post/GenerateManifest
    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_manifest')
    def test_step_manifest_generate(self, resource_group):
        self.cmd('az providerhub manifest generate --provider-namespace "{providerNamespace}"')
    
    # EXAMPLE: /providerhub/post/CheckinManifest
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_manifest')
    def test_step_manifest_checkin(self, resource_group):
        self.cmd('az providerhub manifest checkin --provider-namespace "{providerNamespace}" --environment "Canary"')
    
    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_authorized_application')
    def test_step_authorized_application_create(self, resource_group):
        self.cmd('az providerhub authorized-application create '
                '-n "8b51e6a7-7814-42bd-aa17-3fb1837b3b7a" '
                '--data-authorizations "[{{role:ServiceOwner}}]"  '
                '--provider-namespace "{providerNamespace}" ')

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_authorized_application')
    def test_step_authorized_application_show(self, resource_group):
        self.cmd('az providerhub authorized-application show '
                 '-n "8b51e6a7-7814-42bd-aa17-3fb1837b3b7a" '
                '--provider-namespace "{providerNamespace}"')

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_authorized_application')
    def test_step_authorized_application_list(self, resource_group):
        self.cmd('az providerhub authorized-application list '
                 '--provider-namespace "{providerNamespace}"')

    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_authorized_application')
    def test_step_authorized_application_delete(self, resource_group):
        self.cmd('az providerhub authorized-application delete -y '
                 '-n "8b51e6a7-7814-42bd-aa17-3fb1837b3b7a" '
                '--provider-namespace "{providerNamespace}" ')

    # EXAMPLE: /CustomRollouts/put/CustomRollouts_CreateOrUpdate
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_custom_rollout')
    def test_step_custom_rollout_create(self, resource_group):
        self.cmd('az providerhub custom-rollout create '
                '--provider-namespace "{providerNamespace}" '
                '--rollout-name "{customRolloutName}" '
                '--canary region="EastUS2EUAP" region="centraluseuap"')

    # EXAMPLE: /CustomRollouts/get/CustomRollouts_Get
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_custom_rollout')
    def test_step_custom_rollout_show(self, resource_group):
        self.cmd('az providerhub custom-rollout show '
                '--provider-namespace "{providerNamespace}" '
                '--rollout-name "{customRolloutName}"')

    # EXAMPLE: /CustomRollouts/get/CustomRollouts_ListByProviderRegistration
    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_custom_rollout')
    def test_step_custom_rollout_list(self, resource_group):
        self.cmd('az providerhub custom-rollout list '
                '--provider-namespace "{providerNamespace}"')
        
    # EXAMPLE: /DefaultRollouts/put/DefaultRollouts_CreateOrUpdate
    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_default_rollout')
    def test_step_default_rollout_create(self, resource_group):
        self.cmd('az providerhub default-rollout create '
                '--provider-namespace "{providerNamespace}" '
                '--rollout-name "{defaultRolloutName}" ')
        
    # EXAMPLE: /DefaultRollouts/get/DefaultRollouts_Get
    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_default_rollout')
    def test_step_default_rollout_show(self, resource_group):
        self.cmd('az providerhub default-rollout show '
                '--provider-namespace "{providerNamespace}" '
                '--rollout-name "{defaultRolloutName}"')


    # EXAMPLE: /DefaultRollouts/get/DefaultRollouts_ListByProviderRegistration
    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_default_rollout')
    def test_step_default_rollout_list(self, resource_group):
        self.cmd('az providerhub default-rollout list '
                '--provider-namespace "{providerNamespace}"')


    # EXAMPLE: /DefaultRollouts/post/DefaultRollouts_Stop
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_default_rollout')
    def test_step_default_rollout_stop(self, resource_group):
        self.cmd('az providerhub default-rollout stop '
                '--provider-namespace "{providerNamespace}" '
                '--rollout-name "{defaultRolloutName}"')


    # EXAMPLE: /DefaultRollouts/delete/DefaultRollouts_Delete
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_default_rollout')
    def test_step_default_rollout_delete(self, resource_group):
        self.cmd('az providerhub default-rollout delete -y '
                '--provider-namespace "{providerNamespace}" '
                '--rollout-name "{defaultRolloutName}"')
        
    # EXAMPLE: /Operations/put/Operations_CreateOrUpdate
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_operations')
    def test_step_operation_create(self, resource_group):
        self.cmd('az providerhub operation create '
                '--contents "[{{\\"name\\":\\"Private.VPTest/Employees/Read\\",\\"display\\":{{\\"default\\":{{\\"description\\":\\"Rea'
                'd employees\\",\\"operation\\":\\"Gets/List employee resources\\",\\"provider\\":\\"Private.VPTest\\",'
                '\\"resource\\":\\"Employees\\"}}}}}}]" --provider-namespace "{providerNamespace}"')

    # EXAMPLE: /Operations/get/Operations_ListByProviderRegistration
    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_operations')
    def test_step_operation_list(self, resource_group):
        self.cmd('az providerhub operation list '
                '--provider-namespace "{providerNamespace}"')


    # EXAMPLE: /Operations/delete/Operations_Delete
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_operations')
    def test_step_operation_delete(self, resource_group):
        self.cmd('az providerhub operation delete -y '
                '--provider-namespace "{providerNamespace}"')
        

    # EXAMPLE: /ProviderRegistrations/put/ProviderRegistrations_CreateOrUpdate
    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_provider_registration')
    def test_step_provider_registration_create(self, resource_group):
        self.cmd('az providerhub provider-registration create '
                '--token-auth-configuration authentication-scheme="PoP" signed-request-scope="ResourceUri" '
                '--service-tree-infos service-id="d1b7d8ba-05e2-48e6-90d6-d781b99c6e69" '
                'component-id="d1b7d8ba-05e2-48e6-90d6-d781b99c6e69" '
                '--capabilities effect="Allow" quota-id="CSP_2015-05-01" '
                '--capabilities effect="Allow" quota-id="CSP_MG_2017-12-01" '
                '--manifest-owners "SPARTA-PlatformServiceAdministrator" '
                '--incident-contact-email "rpaascore@microsoft.com" '
                '--incident-routing-service "Resource Provider Service as a Service" '
                '--incident-routing-team "RPaaS" '
                '--provider-version "2.0" '
                '--provider-type "Hidden, Internal" '
                '--provider-namespace "{providerNamespace}" '
                '--metadata {{\\"BypassManifestValidation\\":true}}')

    # EXAMPLE: /ProviderRegistrations/put/ProviderRegistrations_CreateOrUpdate
    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_provider_registration')
    def test_step_provider_registration_update(self, resource_group):
        self.cmd('az providerhub provider-registration update '
                '--token-auth-configuration authentication-scheme="PoP" signed-request-scope="ResourceUri" '
                '--service-tree-infos service-id="d1b7d8ba-05e2-48e6-90d6-d781b99c6e69" '
                'component-id="d1b7d8ba-05e2-48e6-90d6-d781b99c6e69" '
                '--capabilities effect="Allow" quota-id="CSP_2015-05-01" '
                '--capabilities effect="Allow" quota-id="CSP_MG_2017-12-01" '
                '--manifest-owners "SPARTA-PlatformServiceAdministrator" '
                '--incident-contact-email "rpaascore@microsoft.com" '
                '--incident-routing-service "Resource Provider Service as a Service" '
                '--incident-routing-team "RPaaS" '
                '--provider-version "2.0" '
                '--provider-type "Hidden, Internal" '
                '--provider-namespace "{providerNamespace}" '
                '--metadata {{\\"BypassManifestValidation\\":true}}')

    # EXAMPLE: /ProviderRegistrations/get/ProviderRegistrations_Get
    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_provider_registration')
    def test_step_provider_registration_show(self, resource_group):
        self.cmd('az providerhub provider-registration show '
                '--provider-namespace "{providerNamespace}"')


    # EXAMPLE: /ProviderRegistrations/get/ProviderRegistrations_List
    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_provider_registration')
    def test_step_provider_registration_list(self, resource_group):
        self.cmd('az providerhub provider-registration list')


    # EXAMPLE: /ProviderRegistrations/post/ProviderRegistrations_GenerateOperations
    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_provider_registration')
    def test_step_provider_registration_generate_operation(self, resource_group):
        self.cmd('az providerhub provider-registration generate-operation '
                '--provider-namespace "{providerNamespace}"')


    # EXAMPLE: /ProviderRegistrations/delete/ProviderRegistrations_Delete
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_provider_registration')
    def test_step_provider_registration_delete(self, resource_group):
        with self.assertRaises(HttpResponseError):
            self.cmd('az providerhub provider-registration delete -y '
                '--provider-namespace "{providerNamespace}" ')

    # EXAMPLE: /ResourceTypeRegistration/put/ResourceTypeRegistration_CreateOrUpdate
    @AllowLargeResponse(size_kb=10240)
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_resource_type_registration')
    def test_step_resource_type_registration_create(self, resource_group):
        self.cmd('az providerhub resource-type-registration create '
                '--endpoints "[{{api-versions:[2019-01-01],locations:[WestUS]}}]" '
                '--regionality "Regional" '
                '--provider-namespace "{providerNamespace}" '
                '--resource-type "extensionresourcetype" '
                '--routing-type "ProxyOnly, Extension" ')

    # EXAMPLE: /ResourceTypeRegistration/put/ResourceTypeRegistration_CreateOrUpdate
    @AllowLargeResponse(size_kb=10240)
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_resource_type_registration')
    def test_step_resource_type_registration_update(self, resource_group):
        self.cmd('az providerhub resource-type-registration update '
                '--endpoints "[{{api-versions:[2019-01-01],locations:[WestUS]}}]" '
                '--regionality "Regional" '
                '--provider-namespace "{providerNamespace}" '
                '--resource-type "extensionresourcetype" '
                '--routing-type "ProxyOnly, Extension" ')

    # EXAMPLE: /ResourceTypeRegistrations/get/ResourceTypeRegistrations_ListByProviderRegistration
    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_resource_type_registration')
    def test_step_resource_type_registration_list(self, resource_group):
        self.cmd('az providerhub resource-type-registration list '
                '--provider-namespace "{providerNamespace}"')


    # EXAMPLE: /ResourceTypeRegistrations/get/ResourceTypeRegistrations_Get
    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_resource_type_registration')
    def test_step_resource_type_registration_show(self, resource_group):  
        self.cmd('az providerhub resource-type-registration show '
                '--provider-namespace "{providerNamespace}" '
                '--resource-type "extensionresourcetype"')
        
    # EXAMPLE: /ResourceTypeRegistrations/get/ResourceTypeRegistrations_Get
    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_resource_type_registration')
    def test_step_resource_type_registration_delete(self, resource_group):  
        self.cmd('az providerhub resource-type-registration delete -y '
                '--provider-namespace "{providerNamespace}" '
                '--resource-type "extensionresourcetype"')


    # EXAMPLE: /ResourceTypeRegistration/put/ResourceTypeRegistration_CreateOrUpdate
    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_resource_type_registration')
    def test_step_nested_resource_type_registration_create(self, resource_group):
        self.cmd('az providerhub resource-type-registration create '
                '--endpoints "[{{api-versions:[2019-01-01],locations:[WestUS]}}]" '
                '--regionality "Regional" '
                '--routing-type "ProxyOnly" '
                '--provider-namespace "{providerNamespace}" '
                '--enable-async-operation false '
                '--template-deployment-options {{preflight-supported:true,preflight-options:[DefaultValidationOnly,continueDeploymentOnFailure]}} '
                '--resource-type "employees/resourcetyperegistrations/{nestedResourceType}"', checks=[
                    self.check("name", "employees/NestedResourceType", case_sensitive=False),
                    self.check("properties.routingType", "ProxyOnly", case_sensitive=False),
                    self.check("properties.regionality", "Regional", case_sensitive=False)
        ])


    # EXAMPLE: /ResourceTypeRegistration/put/ResourceTypeRegistration_CreateOrUpdate
    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_resource_type_registration')
    def test_step_nested_resource_type_registration_extensions_create(self, resource_group):
        self.cmd('az providerhub resource-type-registration create '
                '--endpoints "[{{\\"api-versions\\":[\\"2019-01-01\\"],\\"locations\\":[\\"WestUS\\"],\\"extensions\\":[{{\\"endpointUri\\":\\"https://contoso-test-extension-endpoint.com\\",\\"extensionCategories\\":[\\"ResourceReadValidate\\",\\"ResourceDeletionValidate\\"]}}]}}]" '
                '--regionality "Regional" '
                '--routing-type "ProxyOnly" '
                '--provider-namespace "{providerNamespace}" '
                '--enable-async-operation false '
                '--template-deployment-options {{preflight-supported:true,preflight-options:[DefaultValidationOnly,continueDeploymentOnFailure]}} '
                '--resource-type "employees/resourcetyperegistrations/{nestedResourceType}"',
                checks = [
                self.check("name", "employees/NestedResourceType", case_sensitive=False),
                self.check("properties.routingType", "ProxyOnly", case_sensitive=False),
                self.check("properties.regionality", "Regional", case_sensitive=False)
            ])


    # EXAMPLE: /ResourceTypeRegistration/delete/ResourceTypeRegistration_Delete
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_resource_type_registration')
    def test_step_nested_resource_type_registration_delete(self, resource_group):
        self.cmd('az providerhub resource-type-registration delete -y '
                '--provider-namespace "{providerNamespace}" '
                '--resource-type "{resourceType}/resourcetyperegistrations/{nestedResourceType}"')


    # EXAMPLE: /ResourceTypeRegistrations/get/ResourceTypeRegistrations_Get
    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_resource_type_registration')
    def test_step_nested_resource_type_registration_show(self, resource_group):
        self.cmd('az providerhub resource-type-registration show '
                '--provider-namespace "{providerNamespace}" '
                '--resource-type "{resourceType}/resourcetyperegistrations/nestedResourceTypeFirst"')


    # EXAMPLE: /NotificationRegistrations/put/NotificationRegistrations_CreateOrUpdate
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_notification')
    def test_step_notification_registration_create(self, resource_group):
        self.cmd('az providerhub notification-registration create '
                '--name "{notificationRegistration}" '
                '--included-events "*/write" "Microsoft.Contoso/employees/delete" '
                '--message-scope "RegisteredSubscriptions" '
                '--notification-endpoints "[{{notification-destination:/subscriptions/ac6bcfb5-3dc1-491f-95a6-646b89bf3e88/resourceGroups/mgmtexp-eastus/providers/Microsoft.EventHub/namespaces/unitedstates-mgmtexpint/eventhubs/armlinkednotifications,locations:[EastUS]}}]" '
                '--notification-mode "EventHub" '
                '--provider-namespace "{providerNamespace}"',
                checks = [
                self.check("name", "{notificationRegistration}", case_sensitive=False),
                self.check("properties.messageScope", "RegisteredSubscriptions", case_sensitive=False),
                self.check("properties.notificationMode", "EventHub", case_sensitive=False)
            ])


    # EXAMPLE: /NotificationRegistrations/get/NotificationRegistrations_Get
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_notification')
    def test_step_notification_registration_show(self, resource_group):
        self.cmd('az providerhub notification-registration show '
                '--name "{notificationRegistration}" '
                '--provider-namespace "{providerNamespace}"',
                checks = [
                self.check("name", "{notificationRegistration}", case_sensitive=False),
                self.check("properties.messageScope", "RegisteredSubscriptions", case_sensitive=False),
                self.check("properties.notificationMode", "EventHub", case_sensitive=False),
            ])


    # EXAMPLE: /NotificationRegistrations/get/NotificationRegistrations_ListByProviderRegistration
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_notification')
    def test_step_notification_registration_list(self, resource_group):
        self.cmd('az providerhub notification-registration list '
                '--provider-namespace "{providerNamespace}"',
                checks = [
                self.check('length(@)', 1),
            ])


    # EXAMPLE: /NotificationRegistrations/delete/NotificationRegistrations_Delete
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_notification')
    def test_step_notification_registration_delete(self, resource_group):
        self.cmd('az providerhub notification-registration delete -y '
                '--name "{notificationRegistration}" '
                '--provider-namespace "{providerNamespace}"')

    # EXAMPLE: /Skus/put/Skus_CreateOrUpdate
    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_sku')
    def test_step_sku_create(self, resource_group):
        self.cmd('az providerhub sku create '
                '--sku-settings "[{{\\"name\\":\\"freeSku\\"}}]" '
                '--provider-namespace "{providerNamespace}" '
                '--resource-type "{resourceType}" '
                '--sku "{skuName}"')


    # EXAMPLE: /Skus/put/Skus_CreateOrUpdateNestedResourceTypeFirst
    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_sku')
    def test_step_sku_create2(self, resource_group):
        self.cmd('az providerhub sku nested-resource-type-first create '
                 '--nested-resource-type-first "nestedResourceTypeFirst" '
                '--sku-settings "[{{\\"name\\":\\"freeSku\\",\\"kind\\":\\"Standard\\",\\"tier\\":\\"Tier1\\"}},{{\\"name'
                '\\":\\"premiumSku\\",\\"costs\\":[{{\\"meterId\\":\\"xxx\\"}}],\\"kind\\":\\"Premium\\",\\"tier\\":\\"Tie'
                'r2\\"}}]" '
                '--provider-namespace "{providerNamespace}" '
                '--resource-type "{resourceType}" '
                '--sku "{skuName}"')


    # EXAMPLE: /Skus/put/Skus_CreateOrUpdateNestedResourceTypeSecond
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_sku')
    def test_step_sku_create3(self, resource_group):
        self.cmd('az providerhub sku nested-resource-type-second create '
                '--nested-resource-type-first "nestedResourceTypeFirst" '
                '--nested-resource-type-second "nestedResourceTypeSecond" '
                '--sku-settings "[{{\\"name\\":\\"freeSku\\",\\"kind\\":\\"Standard\\",\\"tier\\":\\"Tier1\\"}},{{\\"name'
                '\\":\\"premiumSku\\",\\"costs\\":[{{\\"meterId\\":\\"xxx\\"}}],\\"kind\\":\\"Premium\\",\\"tier\\":\\"Tie'
                'r2\\"}}]" '
                '--provider-namespace "{providerNamespace}" '
                '--resource-type "{resourceType}" '
                '--sku "{skuName}"')


    # EXAMPLE: /Skus/put/Skus_CreateOrUpdateNestedResourceTypeThird
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_sku')
    def test_step_sku_create4(self, resource_group):
        self.cmd('az providerhub sku nested-resource-type-third create '
                '--nested-resource-type-first "nestedResourceTypeFirst" '
                '--nested-resource-type-second "nestedResourceTypeSecond" '
                '--nested-resource-type-third "nestedResourceTypeThird" '
                '--sku-settings "[{{\\"name\\":\\"freeSku\\",\\"kind\\":\\"Standard\\",\\"tier\\":\\"Tier1\\"}},{{\\"name'
                '\\":\\"premiumSku\\",\\"costs\\":[{{\\"meterId\\":\\"xxx\\"}}],\\"kind\\":\\"Premium\\",\\"tier\\":\\"Tie'
                'r2\\"}}]" '
                '--provider-namespace "{providerNamespace}" '
                '--resource-type "{resourceType}" '
                '--sku "{skuName}"')


    # EXAMPLE: /Skus/get/Skus_Get
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_sku')
    def test_step_sku_show(self, resource_group):
        self.cmd('az providerhub sku show '
                '--provider-namespace "{providerNamespace}" '
                '--resource-type "{resourceType}" '
                '--sku "{skuName}"')


    # EXAMPLE: /Skus/get/Skus_GetNestedResourceTypeFirst
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_sku')
    def test_step_sku_show_nested_resource_type_first(self, resource_group):
        self.cmd('az providerhub sku nested-resource-type-first show '
                '--nested-resource-type-first "nestedResourceTypeFirst" '
                '--provider-namespace "{providerNamespace}" '
                '--resource-type "{resourceType}" '
                '--sku "{skuName}"')


    # EXAMPLE: /Skus/get/Skus_GetNestedResourceTypeSecond
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_sku')
    def test_step_sku_show_nested_resource_type_second(self, resource_group):
        self.cmd('az providerhub sku nested-resource-type-second show '
                '--nested-resource-type-first "nestedResourceTypeFirst" '
                '--nested-resource-type-second "nestedResourceTypeSecond" '
                '--provider-namespace "{providerNamespace}" '
                '--resource-type "{resourceType}" '
                '--sku "{skuName}"')


    # EXAMPLE: /Skus/get/Skus_GetNestedResourceTypeThird
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_sku')
    def test_step_sku_show_nested_resource_type_third(self, resource_group):
        self.cmd('az providerhub sku nested-resource-type-third show '
                '--nested-resource-type-first "nestedResourceTypeFirst" '
                '--nested-resource-type-second "nestedResourceTypeSecond" '
                '--nested-resource-type-third "nestedResourceTypeThird" '
                '--provider-namespace "{providerNamespace}" '
                '--resource-type "{resourceType}" '
                '--sku "{skuName}"')


    # EXAMPLE: /Skus/get/Skus_ListByResourceTypeRegistrations
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_sku')
    def test_step_sku_list(self, resource_group):
        self.cmd('az providerhub sku list '
                '--provider-namespace "{providerNamespace}" '
                '--resource-type "{resourceType}"')


    # EXAMPLE: /Skus/get/Skus_ListByResourceTypeRegistrationsNestedResourceTypeFirst
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_sku')
    def test_step_sku_list2(self, resource_group):
        self.cmd('az providerhub sku nested-resource-type-first list '
                '--nested-resource-type-first "nestedResourceTypeFirst" '
                '--provider-namespace "{providerNamespace}" '
                '--resource-type "{resourceType}"')


    # EXAMPLE: /Skus/get/Skus_ListByResourceTypeRegistrationsNestedResourceTypeSecond
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_sku')
    def test_step_sku_list3(self, resource_group):
        self.cmd('az providerhub sku nested-resource-type-second list '
                '--nested-resource-type-first "nestedResourceTypeFirst" '
                '--nested-resource-type-second "nestedResourceTypeSecond" '
                '--provider-namespace "{providerNamespace}" '
                '--resource-type "{resourceType}"')


    # EXAMPLE: /Skus/get/Skus_ListByResourceTypeRegistrationsNestedResourceTypeThird
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_sku')
    def test_step_sku_list4(self, resource_group):
        self.cmd('az providerhub sku nested-resource-type-third list '
                '--nested-resource-type-first "nestedResourceTypeFirst" '
                '--nested-resource-type-second "nestedResourceTypeSecond" '
                '--nested-resource-type-third "nestedResourceTypeThird" '
                '--provider-namespace "{providerNamespace}" '
                '--resource-type "{resourceType}"')


    # EXAMPLE: /Skus/delete/Skus_Delete
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_sku')
    def test_step_sku_delete(self, resource_group):
        self.cmd('az providerhub sku delete -y '
                '--provider-namespace "{providerNamespace}" '
                '--resource-type "{resourceType}" '
                '--sku "{skuName}"')


    # EXAMPLE: /Skus/delete/Skus_DeleteNestedResourceTypeFirst
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_sku')
    def test_step_sku_delete2(self, resource_group):
        self.cmd('az providerhub sku nested-resource-type-first delete -y '
                '--nested-resource-type-first "nestedResourceTypeFirst" '
                '--provider-namespace "{providerNamespace}" '
                '--resource-type "{resourceType}" '
                '--sku "{skuName}"')


    # EXAMPLE: /Skus/delete/Skus_DeleteNestedResourceTypeSecond
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_sku')
    def test_step_sku_delete3(self, resource_group):
        self.cmd('az providerhub sku nested-resource-type-second delete -y '
                '--nested-resource-type-first "nestedResourceTypeFirst" '
                '--nested-resource-type-second "nestedResourceTypeSecond" '
                '--provider-namespace "{providerNamespace}" '
                '--resource-type "{resourceType}" '
                '--sku "{skuName}"')


    # EXAMPLE: /Skus/delete/Skus_DeleteNestedResourceTypeThird
    @ResourceGroupPreparer(name_prefix='cli_test_azure_providerhub_sku')
    def test_step_sku_delete4(self, resource_group):
        self.cmd('az providerhub sku nested-resource-type-third delete -y '
                '--nested-resource-type-first "nestedResourceTypeFirst" '
                '--nested-resource-type-second "nestedResourceTypeSecond" '
                '--nested-resource-type-third "nestedResourceTypeThird" '
                '--provider-namespace "{providerNamespace}" '
                '--resource-type "{resourceType}" '
                '--sku "{skuName}"')
