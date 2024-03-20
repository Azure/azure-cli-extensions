# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import time
import yaml
import json
import tempfile
from azure.cli.command_modules.containerapp._utils import format_location

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck, JMESPathCheckExists, live_only, StorageAccountPreparer)

from .common import TEST_LOCATION, STAGE_LOCATION

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

class ContainerappEnvIdentityTests(ScenarioTest):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, random_config_dir=True, **kwargs)

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northeurope")
    def test_containerapp_env_identity_e2e(self, resource_group):
        # MSI is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use eastus as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))

        user_identity_name1 = self.create_random_name(prefix='env-msi1', length=24)
        user_identity_name2 = self.create_random_name(prefix='env-msi2', length=24)
        user_identity_id1 = self.cmd('identity create -g {} -n {}'.format(resource_group, user_identity_name1)).get_output_in_json()["id"]
        user_identity_id2 = self.cmd('identity create -g {} -n {}'.format(resource_group, user_identity_name2)).get_output_in_json()["id"]

        env_name = self.create_random_name(prefix='containerapp-e2e-env', length=24)
        self.cmd('containerapp env create -g {} -n {} --mi-system-assigned --mi-user-assigned {} {} --logs-destination none'.format(resource_group, env_name, user_identity_id1, user_identity_id2))
        
        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()
        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        self.cmd('containerapp env identity show -g {} -n {}'.format(resource_group, env_name), checks=[
            JMESPathCheck('type', 'SystemAssigned, UserAssigned'),
            JMESPathCheckExists(f'userAssignedIdentities."{user_identity_id1}"'),
            JMESPathCheckExists(f'userAssignedIdentities."{user_identity_id2}"')
        ])

        self.cmd('containerapp env identity remove --user-assigned {} -g {} -n {}'.format(user_identity_name1, resource_group, env_name), checks=[
            JMESPathCheck('type', 'SystemAssigned, UserAssigned'),
            JMESPathCheckExists(f'userAssignedIdentities."{user_identity_id2}"')
        ])

        self.cmd('containerapp env identity remove --system-assigned --user-assigned {} -g {} -n {}'.format(user_identity_name2, resource_group, env_name), checks=[
            JMESPathCheck('type', 'None'),
        ])

        self.cmd('containerapp env identity assign --system-assigned --user-assigned {} {} -g {} -n {}'.format(user_identity_name1, user_identity_name2, resource_group, env_name), checks=[
            JMESPathCheck('type', 'SystemAssigned, UserAssigned'),
            JMESPathCheckExists(f'userAssignedIdentities."{user_identity_id1}"'),
            JMESPathCheckExists(f'userAssignedIdentities."{user_identity_id2}"')
        ])

        self.cmd('containerapp env identity remove --system-assigned -g {} -n {}'.format(resource_group, env_name), checks=[
            JMESPathCheck('type', 'UserAssigned'),
            JMESPathCheckExists(f'userAssignedIdentities."{user_identity_id1}"'),
            JMESPathCheckExists(f'userAssignedIdentities."{user_identity_id2}"')
        ])

        self.cmd('containerapp env identity assign --system-assigned -g {} -n {}'.format(resource_group, env_name), checks=[
            JMESPathCheck('type', 'SystemAssigned, UserAssigned'),
        ])

        self.cmd('containerapp env identity remove --user-assigned {} {} -g {} -n {}'.format(user_identity_name1, user_identity_name2, resource_group, env_name), checks=[
            JMESPathCheck('type', 'SystemAssigned'),
        ])

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northeurope")
    def test_containerapp_env_identity_system(self, resource_group):
        # MSI is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use eastus as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))

        env_name = self.create_random_name(prefix='containerapp-e2e-env', length=24)
        
        self.cmd('containerapp env create -g {} -n {} --mi-system-assigned --logs-destination none'.format(resource_group, env_name))

        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        self.cmd('containerapp env identity show -g {} -n {}'.format(resource_group, env_name), checks=[
            JMESPathCheck('type', 'SystemAssigned'),
        ])

        self.cmd('containerapp env identity remove --system-assigned -g {} -n {}'.format(resource_group, env_name), checks=[
            JMESPathCheck('type', 'None'),
        ])

        self.cmd('containerapp env identity assign --system-assigned -g {} -n {}'.format(resource_group, env_name), checks=[
            JMESPathCheck('type', 'SystemAssigned'),
        ])

        self.cmd('containerapp env identity remove --system-assigned -g {} -n {}'.format(resource_group, env_name), checks=[
            JMESPathCheck('type', 'None'),
        ])

        self.cmd('containerapp env show -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('name', env_name),
        ])

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northeurope")
    def test_containerapp_env_identity_user(self, resource_group):
        # MSI is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use eastus as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))

        user_identity_name1 = self.create_random_name(prefix='env-msi1', length=24)
        user_identity_name2 = self.create_random_name(prefix='env-msi2', length=24)
        user_identity_id1 = self.cmd('identity create -g {} -n {}'.format(resource_group, user_identity_name1)).get_output_in_json()["id"]
        user_identity_id2 = self.cmd('identity create -g {} -n {}'.format(resource_group, user_identity_name2)).get_output_in_json()["id"]

        env_name = self.create_random_name(prefix='containerapp-e2e-env', length=24)
        self.cmd('containerapp env create -g {} -n {} --mi-user-assigned {} {} --logs-destination none'.format(resource_group, env_name, user_identity_id1, user_identity_id2))

        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()
        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        self.cmd('containerapp env identity show -g {} -n {}'.format(resource_group, env_name), checks=[
            JMESPathCheck('type', 'UserAssigned'),
            JMESPathCheckExists(f'userAssignedIdentities."{user_identity_id1}"'),
            JMESPathCheckExists(f'userAssignedIdentities."{user_identity_id2}"')
        ])

        self.cmd('containerapp env identity assign --system-assigned -g {} -n {}'.format(resource_group, env_name), checks=[
            JMESPathCheck('type', 'SystemAssigned, UserAssigned'),
        ])
        
        self.cmd('containerapp env identity remove --user-assigned {} -g {} -n {}'.format(user_identity_name1, resource_group, env_name), checks=[
            JMESPathCheck('type', 'SystemAssigned, UserAssigned'),
            JMESPathCheckExists(f'userAssignedIdentities."{user_identity_id2}"')
        ])
        
        self.cmd('containerapp env identity remove --user-assigned {} -g {} -n {}'.format(user_identity_name2, resource_group, env_name), checks=[
            JMESPathCheck('type', 'SystemAssigned'),
        ])

        self.cmd('containerapp env identity remove --system-assigned -g {} -n {}'.format(resource_group, env_name), checks=[
            JMESPathCheck('type', 'None'),
        ])

        self.cmd('containerapp env identity show -g {} -n {}'.format(resource_group, env_name), checks=[
            JMESPathCheck('type', 'None'),
        ])

        self.cmd('containerapp env identity assign --user-assigned {} -g {} -n {}'.format(user_identity_name1, resource_group, env_name), checks=[
            JMESPathCheck('type', 'UserAssigned'),
            JMESPathCheckExists(f'userAssignedIdentities."{user_identity_id1}"')
        ])

        self.cmd('containerapp env identity show -g {} -n {}'.format(resource_group, env_name), checks=[
            JMESPathCheck('type', 'UserAssigned'),
            JMESPathCheckExists(f'userAssignedIdentities."{user_identity_id1}"')
        ])

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="westeurope")
    def test_containerapp_env_msi_custom_domains(self, resource_group):
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))
        env_name = self.create_random_name(prefix='containerapp-env', length=24)

        verification_id = self.cmd('az containerapp show-custom-domain-verification-id').output
        key_vault_name = self.create_random_name(prefix='capp-kv-', length=24)
        cert_name = self.create_random_name(prefix='akv-cert-', length=24)

        # create azure keyvault
        self.cmd(f"keyvault create -g {resource_group} -n {key_vault_name}")

        # create an App service domain and update its txt records
        contacts = os.path.join(TEST_DIR, 'domain-contact.json')
        zone_name = "{}.com".format(env_name)
        subdomain_1 = "devtest"
        txt_name_1 = "asuid.{}".format(subdomain_1)
        hostname_1 = "{}.{}".format(subdomain_1, zone_name)
        self.cmd("appservice domain create -g {} --hostname {} --contact-info=@'{}' --accept-terms".format(resource_group, zone_name, contacts)).get_output_in_json()
        self.cmd('network dns record-set txt add-record -g {} -z {} -n {} -v {}'.format(resource_group, zone_name, txt_name_1, verification_id)).get_output_in_json()
    
        defaultPolicy = self.cmd("keyvault certificate get-default-policy").get_output_in_json()
        defaultPolicy["x509CertificateProperties"]["subject"] = f"CN=*.{hostname_1}"
        defaultPolicy["secretProperties"]["contentType"] = "application/x-pem-file"
        
        temp = tempfile.NamedTemporaryFile(prefix='capp_', suffix='_tmp', mode="w+", delete=False)
        temp.write(json.dumps(defaultPolicy, default=lambda o: dict((key, value) for key, value in o.__dict__.items() if value), allow_nan=False))
        temp.close()

        time.sleep(5)

        # create a self assigned certificate in the keyvault
        cert = self.cmd('keyvault certificate create --vault-name {} -n {} -p @"{}"'.format(key_vault_name, cert_name, temp.name)).get_output_in_json()
        akv_secret_url = cert["target"].replace("certificates", "secrets")

        user_identity_name1 = self.create_random_name(prefix='env-msi1', length=24)
        identity_json = self.cmd('identity create -g {} -n {}'.format(resource_group, user_identity_name1)).get_output_in_json()
        user_identity_id1 = identity_json["id"]
        principal_id1 = identity_json["principalId"]

        # assign secret permissions to the user assigned identity
        self.cmd(f"keyvault set-policy -n {key_vault_name} -g {resource_group} --object-id {principal_id1} --secret-permissions get list")

        # create an environment with custom domain and user assigned identity
        self.cmd('containerapp env create -g {} -n {} --mi-user-assigned {} --logs-destination none --dns-suffix {} --certificate-identity {} --certificate-akv-url {}'.format(
            resource_group, env_name, user_identity_id1, hostname_1, user_identity_id1, akv_secret_url))

        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        self.cmd(f'containerapp env show -n {env_name} -g {resource_group}', checks=[
            JMESPathCheck('name', env_name),
            JMESPathCheck('properties.customDomainConfiguration.dnsSuffix', hostname_1),
            JMESPathCheck('properties.customDomainConfiguration.certificateKeyVaultProperties.identity', user_identity_id1),
            JMESPathCheck('properties.customDomainConfiguration.certificateKeyVaultProperties.keyVaultUrl', akv_secret_url),
        ])

        # update env with custom domain using file and password
        tmpFile = os.path.join(tempfile.gettempdir(), "{}.pem".format(env_name))
        self.cmd(f'keyvault secret download --vault-name {key_vault_name} -n {cert_name} -f "{tmpFile}"')
        self.cmd('containerapp env update -g {} -n {} --certificate-file "{}"'.format(
            resource_group, env_name, tmpFile))
        self.cmd(f'containerapp env show -n {env_name} -g {resource_group}', checks=[
            JMESPathCheck('name', env_name),
            JMESPathCheck('properties.customDomainConfiguration.dnsSuffix', hostname_1),
            JMESPathCheck('properties.customDomainConfiguration.certificateKeyVaultProperties', None),
        ])

        # update env with custom domain using msi
        self.cmd('containerapp env update -g {} -n {} --certificate-identity {} --certificate-akv-url {}'.format(
            resource_group, env_name, user_identity_id1, akv_secret_url))
        self.cmd(f'containerapp env show -n {env_name} -g {resource_group}', checks=[
            JMESPathCheck('name', env_name),
            JMESPathCheck('properties.customDomainConfiguration.dnsSuffix', hostname_1),
            JMESPathCheck('properties.customDomainConfiguration.certificateKeyVaultProperties.identity', user_identity_id1),
            JMESPathCheck('properties.customDomainConfiguration.certificateKeyVaultProperties.keyVaultUrl', akv_secret_url),
        ])

        # remove temp file
        os.remove(temp.name)
        os.remove(tmpFile)

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="westeurope")
    def test_containerapp_env_msi_certificate(self, resource_group):
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))
        env_name = self.create_random_name(prefix='capp-env', length=24)
        key_vault_name = self.create_random_name(prefix='capp-kv-', length=24)
        cert_name = self.create_random_name(prefix='akv-cert-', length=24)
        # create azure keyvault
        self.cmd(f"keyvault create -g {resource_group} -n {key_vault_name}")
        defaultPolicy = self.cmd("keyvault certificate get-default-policy").get_output_in_json()
        defaultPolicy["x509CertificateProperties"]["subject"] = f"CN=*.contoso.com"
        defaultPolicy["secretProperties"]["contentType"] = "application/x-pem-file"
        
        temp = tempfile.NamedTemporaryFile(prefix='capp_', suffix='_tmp', mode="w+", delete=False)
        temp.write(json.dumps(defaultPolicy, default=lambda o: dict((key, value) for key, value in o.__dict__.items() if value), allow_nan=False))
        temp.close()
        time.sleep(5)
        # create a self assigned certificate in the keyvault
        cert = self.cmd('keyvault certificate create --vault-name {} -n {} -p @"{}"'.format(key_vault_name, cert_name, temp.name)).get_output_in_json()
        akv_secret_url = cert["target"].replace("certificates", "secrets")
        # create an environment with custom domain and user assigned identity
        self.cmd('containerapp env create -g {} -n {} --mi-system-assigned --logs-destination none'.format(
            resource_group, env_name))
        
        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()
        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()
        # assign secret permissions to the system assigned identity
        principal_id = containerapp_env["identity"]["principalId"]
        self.cmd(f"keyvault set-policy -n {key_vault_name} -g {resource_group} --object-id {principal_id} --secret-permissions get list")
        
        containerapp_cert_name = self.create_random_name(prefix='containerapp-cert', length=24)
        cert = self.cmd(f"containerapp env certificate upload -g {resource_group} -n {env_name} -c {containerapp_cert_name}  --akv-url {akv_secret_url}", checks=[
            JMESPathCheck('type', "Microsoft.App/managedEnvironments/certificates"),
        ]).get_output_in_json()
        containerapp_cert_id = cert["id"]
        containerapp_cert_thumbprint = cert["properties"]["thumbprint"]
        containerapp_cert_location = cert["location"]
        self.cmd(
            'containerapp env certificate list -n {} -g {} -l "{}"'.format(env_name, resource_group, containerapp_cert_location),
            checks=[
                JMESPathCheck('length(@)', 1),
                JMESPathCheck('[0].properties.certificateKeyVaultProperties.keyVaultUrl', akv_secret_url),
                JMESPathCheck('[0].properties.certificateKeyVaultProperties.identity', "system"),
                JMESPathCheck('[0].properties.thumbprint', containerapp_cert_thumbprint),
                JMESPathCheck('[0].name', containerapp_cert_name),
                JMESPathCheck('[0].id', containerapp_cert_id),
            ])
        tmpFile = os.path.join(tempfile.gettempdir(), "{}.pem".format(env_name))
        self.cmd(f'keyvault secret download --vault-name {key_vault_name} -n {cert_name} -f "{tmpFile}"')
        containerapp_cert_name = self.create_random_name(prefix='containerapp-cert', length=24)
        self.cmd('containerapp env certificate upload -g {} -n {} -c {} --certificate-file "{}"'.format(
            resource_group, env_name, containerapp_cert_name, tmpFile), checks=[
                JMESPathCheck('type', "Microsoft.App/managedEnvironments/certificates"),
                JMESPathCheck('properties.certificateKeyVaultProperties', None),
            ])
        
        containerapp_cert_name = self.create_random_name(prefix='containerapp-cert', length=24)
        self.cmd(f"containerapp env certificate upload -g {resource_group} -n {env_name} -c {containerapp_cert_name} --akv-url {akv_secret_url}", checks=[
            JMESPathCheck('type', "Microsoft.App/managedEnvironments/certificates"),
            JMESPathCheck('properties.certificateKeyVaultProperties.keyVaultUrl', akv_secret_url),
            JMESPathCheck('properties.certificateKeyVaultProperties.identity', "system"),
        ])
        # remove temp file
        os.remove(temp.name)
        os.remove(tmpFile)

    @AllowLargeResponse(8192)
    @live_only()
    @ResourceGroupPreparer(location="westeurope")
    def test_containerapp_env_msi_certificate_random_name(self, resource_group):
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))
        env_name = self.create_random_name(prefix='capp-env', length=24)
        key_vault_name = self.create_random_name(prefix='capp-kv-', length=24)
        cert_name = self.create_random_name(prefix='akv-cert-', length=24)
        # create azure keyvault
        self.cmd(f"keyvault create -g {resource_group} -n {key_vault_name}")
        defaultPolicy = self.cmd("keyvault certificate get-default-policy").get_output_in_json()
        defaultPolicy["x509CertificateProperties"]["subject"] = f"CN=*.contoso.com"
        defaultPolicy["secretProperties"]["contentType"] = "application/x-pem-file"
        
        temp = tempfile.NamedTemporaryFile(prefix='capp_', suffix='_tmp', mode="w+", delete=False)
        temp.write(json.dumps(defaultPolicy, default=lambda o: dict((key, value) for key, value in o.__dict__.items() if value), allow_nan=False))
        temp.close()
        time.sleep(5)
        # create a self assigned certificate in the keyvault
        cert = self.cmd('keyvault certificate create --vault-name {} -n {} -p @"{}"'.format(key_vault_name, cert_name, temp.name)).get_output_in_json()
        akv_secret_url = cert["target"].replace("certificates", "secrets")


        user_identity_name = self.create_random_name(prefix='env-msi', length=24)
        identity_json = self.cmd('identity create -g {} -n {}'.format(resource_group, user_identity_name)).get_output_in_json()
        user_identity_id = identity_json["id"]
        principal_id = identity_json["principalId"]
        # assign secret permissions to the user assigned identity
        self.cmd(f"keyvault set-policy -n {key_vault_name} -g {resource_group} --object-id {principal_id} --secret-permissions get list")

        # create an environment with custom domain and user assigned identity
        self.cmd('containerapp env create -g {} -n {} --mi-user-assigned {} --logs-destination none'.format(
            resource_group, env_name, user_identity_id))
        
        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()
        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()
        
        cert = self.cmd(f"containerapp env certificate upload -g {resource_group} -n {env_name} --akv-url {akv_secret_url} --identity {user_identity_id}", checks=[
            JMESPathCheck('type', "Microsoft.App/managedEnvironments/certificates"),
        ]).get_output_in_json()
        containerapp_cert_name = cert["name"]
        containerapp_cert_id = cert["id"]
        containerapp_cert_thumbprint = cert["properties"]["thumbprint"]
        containerapp_cert_location = cert["location"]
        self.cmd(
            'containerapp env certificate list -n {} -g {} -l "{}"'.format(env_name, resource_group, containerapp_cert_location),
            checks=[
                JMESPathCheck('length(@)', 1),
                JMESPathCheck('[0].properties.certificateKeyVaultProperties.keyVaultUrl', akv_secret_url),
                JMESPathCheck('[0].properties.certificateKeyVaultProperties.identity', user_identity_id),
                JMESPathCheck('[0].properties.thumbprint', containerapp_cert_thumbprint),
                JMESPathCheck('[0].name', containerapp_cert_name),
                JMESPathCheck('[0].id', containerapp_cert_id),
            ])
    

class ContainerappEnvScenarioTest(ScenarioTest):
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northeurope")
    def test_containerapp_env_e2e(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        env_name = self.create_random_name(prefix='containerapp-e2e-env', length=24)
        logs_workspace_name = self.create_random_name(prefix='containerapp-env', length=24)

        logs_workspace_id = self.cmd('monitor log-analytics workspace create -g {} -n {} -l eastus'.format(resource_group, logs_workspace_name)).get_output_in_json()["customerId"]
        logs_workspace_key = self.cmd('monitor log-analytics workspace get-shared-keys -g {} -n {}'.format(resource_group, logs_workspace_name)).get_output_in_json()["primarySharedKey"]

        self.cmd('containerapp env create -g {} -n {} --logs-workspace-id {} --logs-workspace-key {}'.format(resource_group, env_name, logs_workspace_id, logs_workspace_key))

        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        self.cmd('containerapp env list -g {}'.format(resource_group), checks=[
            JMESPathCheck('length(@)', 1),
            JMESPathCheck('[0].name', env_name),
        ])

        self.cmd('containerapp env show -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('name', env_name),
        ])

        self.cmd('containerapp env delete -g {} -n {} --yes'.format(resource_group, env_name))

        self.cmd('containerapp env list -g {}'.format(resource_group), checks=[
            JMESPathCheck('length(@)', 0),
        ])

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="australiaeast")
    def test_containerapp_env_la_dynamic_json(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))
        logs_workspace_name = self.create_random_name(prefix='containerapp-env', length=24)

        logs_workspace_id = self.cmd('monitor log-analytics workspace create -g {} -n {} -l eastus'.format(resource_group, logs_workspace_name)).get_output_in_json()["customerId"]
        logs_workspace_key = self.cmd('monitor log-analytics workspace get-shared-keys -g {} -n {}'.format(resource_group, logs_workspace_name)).get_output_in_json()["primarySharedKey"]

        default_env_name = self.create_random_name(prefix='containerapp-env', length=24)
        self.cmd('containerapp env create -g {} -n {} --logs-workspace-id {} --logs-workspace-key {} --logs-destination log-analytics -j'.format(resource_group, default_env_name, logs_workspace_id, logs_workspace_key), checks=[
            JMESPathCheck('name', default_env_name),
            JMESPathCheck('properties.appLogsConfiguration.destination', "log-analytics"),
            JMESPathCheck('properties.appLogsConfiguration.logAnalyticsConfiguration.dynamicJsonColumns', True),
        ])

        default_env_name2 = self.create_random_name(prefix='containerapp-env', length=24)
        self.cmd('containerapp env create -g {} -n {} --logs-workspace-id {} --logs-workspace-key {} -j false'.format(resource_group, default_env_name2, logs_workspace_id, logs_workspace_key),checks=[
            JMESPathCheck('name', default_env_name2),
            JMESPathCheck('properties.appLogsConfiguration.destination', "log-analytics"),
            JMESPathCheck('properties.appLogsConfiguration.logAnalyticsConfiguration.dynamicJsonColumns', False),
        ])

        env_name = self.create_random_name(prefix='containerapp-env', length=24)

        self.cmd('containerapp env create -g {} -n {} --logs-workspace-id {} --logs-workspace-key {} --logs-destination log-analytics'.format(resource_group, env_name, logs_workspace_id, logs_workspace_key))

        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        self.cmd('containerapp env show -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('name', env_name),
            JMESPathCheck('properties.appLogsConfiguration.destination', "log-analytics"),
            JMESPathCheck('properties.appLogsConfiguration.logAnalyticsConfiguration.customerId', logs_workspace_id),
            JMESPathCheck('properties.appLogsConfiguration.logAnalyticsConfiguration.dynamicJsonColumns', False),
        ])

        self.cmd('containerapp env update -g {} -n {} -j'.format(resource_group, env_name))

        self.cmd('containerapp env show -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('name', env_name),
            JMESPathCheck('properties.appLogsConfiguration.destination', "log-analytics"),
            JMESPathCheck('properties.appLogsConfiguration.logAnalyticsConfiguration.customerId', logs_workspace_id),
            JMESPathCheck('properties.appLogsConfiguration.logAnalyticsConfiguration.dynamicJsonColumns', True),
        ])

        self.cmd('containerapp env update -g {} -n {}'.format(resource_group, env_name))

        self.cmd('containerapp env show -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('name', env_name),
            JMESPathCheck('properties.appLogsConfiguration.destination', "log-analytics"),
            JMESPathCheck('properties.appLogsConfiguration.logAnalyticsConfiguration.customerId', logs_workspace_id),
            JMESPathCheck('properties.appLogsConfiguration.logAnalyticsConfiguration.dynamicJsonColumns', True),
        ])

        self.cmd('containerapp env update -g {} -n {} -j false'.format(resource_group, env_name))

        self.cmd('containerapp env show -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('name', env_name),
            JMESPathCheck('properties.appLogsConfiguration.destination', "log-analytics"),
            JMESPathCheck('properties.appLogsConfiguration.logAnalyticsConfiguration.customerId', logs_workspace_id),
            JMESPathCheck('properties.appLogsConfiguration.logAnalyticsConfiguration.dynamicJsonColumns', False),
        ])

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northeurope")
    @live_only()  # encounters 'CannotOverwriteExistingCassetteException' only when run from recording (passes when run live)
    def test_containerapp_env_dapr_components(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        env_name = self.create_random_name(prefix='containerapp-e2e-env', length=24)
        dapr_comp_name = self.create_random_name(prefix='dapr-component', length=24)
        logs_workspace_name = self.create_random_name(prefix='containerapp-env', length=24)

        logs_workspace_id = self.cmd('monitor log-analytics workspace create -g {} -n {} -l eastus'.format(resource_group, logs_workspace_name)).get_output_in_json()["customerId"]
        logs_workspace_key = self.cmd('monitor log-analytics workspace get-shared-keys -g {} -n {}'.format(resource_group, logs_workspace_name)).get_output_in_json()["primarySharedKey"]

        self.cmd('containerapp env create -g {} -n {} --logs-workspace-id {} --logs-workspace-key {}'.format(resource_group, env_name, logs_workspace_id, logs_workspace_key))

        import tempfile

        file_ref, dapr_file = tempfile.mkstemp(suffix=".yml")

        dapr_yaml = """
        name: statestore
        componentType: state.azure.blobstorage
        version: v1
        metadata:
        - name: accountName
          secretRef: storage-account-name
        secrets:
        - name: storage-account-name
          value: storage-account-name
        """

        daprloaded = yaml.safe_load(dapr_yaml)

        with open(dapr_file, 'w') as outfile:
            yaml.dump(daprloaded, outfile, default_flow_style=False)

        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        self.cmd('containerapp env dapr-component set -n {} -g {} --dapr-component-name {} --yaml {}'.format(env_name, resource_group, dapr_comp_name, dapr_file.replace(os.sep, os.sep + os.sep)), checks=[
            JMESPathCheck('name', dapr_comp_name),
        ])

        os.close(file_ref)

        self.cmd('containerapp env dapr-component list -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('length(@)', 1),
            JMESPathCheck('[0].name', dapr_comp_name),
        ])

        self.cmd('containerapp env dapr-component show -n {} -g {} --dapr-component-name {}'.format(env_name, resource_group, dapr_comp_name), checks=[
            JMESPathCheck('name', dapr_comp_name),
            JMESPathCheck('properties.version', 'v1'),
            JMESPathCheck('properties.secrets[0].name', 'storage-account-name'),
            JMESPathCheck('properties.metadata[0].name', 'accountName'),
            JMESPathCheck('properties.metadata[0].secretRef', 'storage-account-name'),
        ])

        self.cmd('containerapp env dapr-component remove -n {} -g {} --dapr-component-name {}'.format(env_name, resource_group, dapr_comp_name))

        self.cmd('containerapp env dapr-component list -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('length(@)', 0),
        ])

        # Invalid pubsub service type should throw an error.
        self.cmd('containerapp env dapr-component init -n {} -g {} --pubsub {}'.format(env_name, resource_group, "invalid1"), expect_failure=True)

        # Invalid statestore service type should throw an error.
        self.cmd('containerapp env dapr-component init -n {} -g {} --statestore {}'.format(env_name, resource_group, "invalid2"), expect_failure=True)

        # Should create a Redis statestore and pubsub components as default.
        output_json = self.cmd('containerapp env dapr-component init -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('length(@)', 2),
            JMESPathCheck('message', "Operation successful."),
            JMESPathCheck('length(resources.daprComponents)', 2), # Redis statestore and pubsub components
            JMESPathCheck('length(resources.devServices)', 1), # Single Redis instance
        ]).get_output_in_json()
        self.assertIn("daprComponents/statestore", output_json["resources"]["daprComponents"][0])
        self.assertIn("daprComponents/pubsub", output_json["resources"]["daprComponents"][1])
        self.assertIn("containerapps/dapr-redis", output_json["resources"]["devServices"][0])

        # Should not create a Redis statestore and pubsub components if they already exist.
        output_json = self.cmd('containerapp env dapr-component init -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('length(@)', 2),
            JMESPathCheck('message', "Operation successful."),
            JMESPathCheck('length(resources.daprComponents)', 2), # Redis statestore and pubsub components
            JMESPathCheck('length(resources.devServices)', 1), # Single Redis instance
        ]).get_output_in_json()
        self.assertIn("daprComponents/statestore", output_json["resources"]["daprComponents"][0])
        self.assertIn("daprComponents/pubsub", output_json["resources"]["daprComponents"][1])
        self.assertIn("containerapps/dapr-redis", output_json["resources"]["devServices"][0])

        # Redis statestore should be correctly created.
        self.cmd('containerapp env dapr-component show --dapr-component-name {} -n {} -g {}'.format("statestore", env_name, resource_group), checks=[
            JMESPathCheck('name', "statestore"),
            JMESPathCheck('properties.componentType', "state.redis"),
            JMESPathCheck('length(properties.metadata)', 1),
            JMESPathCheck('properties.metadata[0].name', "actorStateStore"),
            JMESPathCheck('properties.metadata[0].value', "true"),
            JMESPathCheck('properties.serviceComponentBind.name', "dapr-redis"),
            JMESPathCheck('properties.serviceComponentBind.serviceId', output_json["resources"]["devServices"][0]),
            JMESPathCheck('properties.serviceComponentBind.metadata.DCI_SB_CREATED_BY', "azcli_azext_containerapp_daprutils"),
            JMESPathCheck('properties.version', "v1"),
        ])

        # Redis pubsub should be correctly created.
        self.cmd('containerapp env dapr-component show --dapr-component-name {} -n {} -g {}'.format("pubsub", env_name, resource_group), checks=[
            JMESPathCheck('name', "pubsub"),
            JMESPathCheck('properties.componentType', "pubsub.redis"),
            JMESPathCheck('length(properties.metadata)', 0),
            JMESPathCheck('properties.serviceComponentBind.name', "dapr-redis"),
            JMESPathCheck('properties.serviceComponentBind.serviceId', output_json["resources"]["devServices"][0]),
            JMESPathCheck('properties.serviceComponentBind.metadata.DCI_SB_CREATED_BY', "azcli_azext_containerapp_daprutils"),
            JMESPathCheck('properties.version', "v1"),
        ])

    @ResourceGroupPreparer(location="eastus")
    def test_containerapp_env_infrastructure_rg(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        env = self.create_random_name(prefix='env', length=24)
        vnet = self.create_random_name(prefix='name', length=24)
        infra_rg = self.create_random_name(prefix='irg', length=24)

        vnet_location = TEST_LOCATION
        if format_location(vnet_location) == format_location(STAGE_LOCATION):
            vnet_location = "centralus"

        self.cmd(f"az network vnet create --address-prefixes '14.0.0.0/23' -g {resource_group} -n {vnet} --location {vnet_location}")
        sub_id = self.cmd(f"az network vnet subnet create --address-prefixes '14.0.0.0/23' --delegations Microsoft.App/environments -n sub -g {resource_group} --vnet-name {vnet}").get_output_in_json()["id"]

        self.cmd(f'containerapp env create -g {resource_group} -n {env} -s {sub_id} -i {infra_rg} --enable-workload-profiles true --logs-destination none')

        containerapp_env = self.cmd(f'containerapp env show -g {resource_group} -n {env}').get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd(f'containerapp env show -g {resource_group} -n {env}').get_output_in_json()

        self.cmd(f'containerapp env show -n {env} -g {resource_group}', checks=[
            JMESPathCheck('name', env),
            JMESPathCheck('properties.infrastructureResourceGroup', infra_rg),
        ])

        self.cmd(f'containerapp env delete -n {env} -g {resource_group} --yes')

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northeurope")
    def test_containerapp_env_mtls(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        env_name = self.create_random_name(prefix='containerapp-e2e-env', length=24)
        logs_workspace_name = self.create_random_name(prefix='containerapp-env', length=24)

        logs_workspace_id = self.cmd('monitor log-analytics workspace create -g {} -n {} -l eastus'.format(resource_group, logs_workspace_name)).get_output_in_json()["customerId"]
        logs_workspace_key = self.cmd('monitor log-analytics workspace get-shared-keys -g {} -n {}'.format(resource_group, logs_workspace_name)).get_output_in_json()["primarySharedKey"]

        self.cmd('containerapp env create -g {} -n {} --logs-workspace-id {} --logs-workspace-key {} --enable-mtls'.format(resource_group, env_name, logs_workspace_id, logs_workspace_key))

        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        self.cmd('containerapp env show -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('name', env_name),
            JMESPathCheck('properties.peerAuthentication.mtls.enabled', True),
        ])

        self.cmd('containerapp env update -g {} -n {} --enable-mtls false'.format(resource_group, env_name))

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        self.cmd('containerapp env show -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('name', env_name),
            JMESPathCheck('properties.peerAuthentication.mtls.enabled', False),
        ])

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northeurope")
    def test_containerapp_env_usages(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        result = self.cmd('containerapp list-usages').get_output_in_json()
        usages = result["value"]
        self.assertEqual(len(usages), 1)
        self.assertEqual(usages[0]["name"]["value"], "ManagedEnvironmentCount")
        self.assertGreater(usages[0]["limit"], 0)
        self.assertGreaterEqual(usages[0]["usage"], 0)

        env_name = self.create_random_name(prefix='containerapp-e2e-env', length=24)
        logs_workspace_name = self.create_random_name(prefix='containerapp-env', length=24)

        logs_workspace_id = self.cmd('monitor log-analytics workspace create -g {} -n {} -l eastus'.format(resource_group, logs_workspace_name)).get_output_in_json()["customerId"]
        logs_workspace_key = self.cmd('monitor log-analytics workspace get-shared-keys -g {} -n {}'.format(resource_group, logs_workspace_name)).get_output_in_json()["primarySharedKey"]

        self.cmd('containerapp env create -g {} -n {} --logs-workspace-id {} --logs-workspace-key {} --enable-mtls'.format(resource_group, env_name, logs_workspace_id, logs_workspace_key))

        containerapp_env = self.cmd(
            'containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd(
                'containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        self.cmd('containerapp env show -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('name', env_name)
        ])

        result = self.cmd('containerapp env list-usages --id {}'.format(containerapp_env["id"])).get_output_in_json()
        usages = result["value"]
        self.assertEqual(len(usages), 4)
        self.assertGreater(usages[0]["limit"], 0)
        self.assertGreaterEqual(usages[0]["usage"], 0)


class ContainerappEnvLocationNotInStageScenarioTest(ScenarioTest):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, random_config_dir=True, **kwargs)

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="australiaeast")
    def test_containerapp_env_logs_e2e(self, resource_group):
        # azure-monitor is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use eastus as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))

        env_name = self.create_random_name(prefix='containerapp-env', length=24)
        logs_workspace_name = self.create_random_name(prefix='containerapp-env', length=24)

        logs_workspace_id = self.cmd('monitor log-analytics workspace create -g {} -n {} -l eastus'.format(resource_group, logs_workspace_name)).get_output_in_json()["customerId"]
        logs_workspace_key = self.cmd('monitor log-analytics workspace get-shared-keys -g {} -n {}'.format(resource_group, logs_workspace_name)).get_output_in_json()["primarySharedKey"]

        self.cmd('containerapp env create -g {} -n {} --logs-workspace-id {} --logs-workspace-key {} --logs-destination log-analytics'.format(resource_group, env_name, logs_workspace_id, logs_workspace_key))

        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        self.cmd('containerapp env show -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('name', env_name),
            JMESPathCheck('properties.appLogsConfiguration.destination', "log-analytics"),
            JMESPathCheck('properties.appLogsConfiguration.logAnalyticsConfiguration.customerId', logs_workspace_id),
        ])

        storage_account_name = self.create_random_name(prefix='cappstorage', length=24)
        storage_account = self.cmd('storage account create -g {} -n {} --https-only'.format(resource_group, storage_account_name)).get_output_in_json()["id"]
        self.cmd('containerapp env update -g {} -n {} --logs-destination azure-monitor --storage-account {}'.format(resource_group, env_name, storage_account))

        env = self.cmd('containerapp env show -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('name', env_name),
            JMESPathCheck('properties.appLogsConfiguration.destination', "azure-monitor"),
        ]).get_output_in_json()

        diagnostic_settings = self.cmd('monitor diagnostic-settings show --name diagnosticsettings --resource {}'.format(env["id"])).get_output_in_json()

        self.assertEqual(storage_account in diagnostic_settings["storageAccountId"], True)

        self.cmd('containerapp env update -g {} -n {} --logs-destination none'.format(resource_group, env_name))

        self.cmd('containerapp env show -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('name', env_name),
            JMESPathCheck('properties.appLogsConfiguration.destination', None),
        ])

        self.cmd('containerapp env update -g {} -n {} --logs-workspace-id {} --logs-workspace-key {} --logs-destination log-analytics'.format(resource_group, env_name, logs_workspace_id, logs_workspace_key))

        self.cmd('containerapp env show -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('name', env_name),
            JMESPathCheck('properties.appLogsConfiguration.destination', "log-analytics"),
            JMESPathCheck('properties.appLogsConfiguration.logAnalyticsConfiguration.customerId', logs_workspace_id),
        ])

        self.cmd('containerapp env create -g {} -n {} --logs-destination azure-monitor --storage-account {}'.format(resource_group, env_name, storage_account))

        env = self.cmd('containerapp env show -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('name', env_name),
            JMESPathCheck('properties.appLogsConfiguration.destination', "azure-monitor"),
        ]).get_output_in_json()

        diagnostic_settings = self.cmd('monitor diagnostic-settings show --name diagnosticsettings --resource {}'.format(env["id"])).get_output_in_json()

        self.assertEqual(storage_account in diagnostic_settings["storageAccountId"], True)

        self.cmd('containerapp env create -g {} -n {} --logs-destination none'.format(resource_group, env_name))

        self.cmd('containerapp env show -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('name', env_name),
            JMESPathCheck('properties.appLogsConfiguration.destination', None),
        ])

        self.cmd('containerapp env update -g {} -n {} --logs-destination none --no-wait'.format(resource_group, env_name))

        self.cmd('containerapp env show -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('name', env_name),
            JMESPathCheck('properties.appLogsConfiguration.destination', None),
        ])

    @AllowLargeResponse(8192)
    @live_only()  # encounters 'CannotOverwriteExistingCassetteException' only when run from recording (passes when run live)
    @ResourceGroupPreparer(location="westeurope")
    def test_containerapp_env_custom_domains(self, resource_group):
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))
        env_name = self.create_random_name(prefix='containerapp-env', length=24)
        logs_workspace_name = self.create_random_name(prefix='containerapp-env', length=24)

        logs_workspace_id = self.cmd('monitor log-analytics workspace create -g {} -n {} -l eastus'.format(resource_group, logs_workspace_name)).get_output_in_json()["customerId"]
        logs_workspace_key = self.cmd('monitor log-analytics workspace get-shared-keys -g {} -n {}'.format(resource_group, logs_workspace_name)).get_output_in_json()["primarySharedKey"]

        self.cmd('containerapp env create -g {} -n {} --logs-workspace-id {} --logs-workspace-key {}'.format(resource_group, env_name, logs_workspace_id, logs_workspace_key))

        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        # create an App service domain and update its txt records
        contacts = os.path.join(TEST_DIR, 'domain-contact.json')
        zone_name = "{}.com".format(env_name)
        subdomain_1 = "devtest"
        subdomain_2 = "clitest"
        txt_name_1 = "asuid.{}".format(subdomain_1)
        txt_name_2 = "asuid.{}".format(subdomain_2)
        hostname_1 = "{}.{}".format(subdomain_1, zone_name)
        hostname_2 = "{}.{}".format(subdomain_2, zone_name)
        verification_id = containerapp_env["properties"]["customDomainConfiguration"]["customDomainVerificationId"]
        self.cmd("appservice domain create -g {} --hostname {} --contact-info=@'{}' --accept-terms".format(resource_group, zone_name, contacts)).get_output_in_json()
        self.cmd('network dns record-set txt add-record -g {} -z {} -n {} -v {}'.format(resource_group, zone_name, txt_name_1, verification_id)).get_output_in_json()
        self.cmd('network dns record-set txt add-record -g {} -z {} -n {} -v {}'.format(resource_group, zone_name, txt_name_2, verification_id)).get_output_in_json()

        # upload cert, add hostname & binding
        pfx_file = os.path.join(TEST_DIR, 'cert.pfx')
        pfx_password = 'test12'

        self.cmd('containerapp env create -g {} -n {} --logs-workspace-id {} --logs-workspace-key {} --dns-suffix {} --certificate-file "{}" --certificate-password {}'.format(resource_group, env_name, logs_workspace_id, logs_workspace_key, hostname_1, pfx_file, pfx_password))

        self.cmd(f'containerapp env show -n {env_name} -g {resource_group}', checks=[
            JMESPathCheck('name', env_name),
            JMESPathCheck('properties.customDomainConfiguration.dnsSuffix', hostname_1),
        ])

    @AllowLargeResponse(8192)
    @live_only()  # encounters 'CannotOverwriteExistingCassetteException' only when run from recording (passes when run live)
    @ResourceGroupPreparer(location="westeurope")
    def test_containerapp_env_update_custom_domains(self, resource_group):
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))

        env_name = self.create_random_name(prefix='containerapp-env', length=24)
        logs_workspace_name = self.create_random_name(prefix='containerapp-env', length=24)

        logs_workspace_id = self.cmd('monitor log-analytics workspace create -g {} -n {} -l eastus'.format(resource_group, logs_workspace_name)).get_output_in_json()["customerId"]
        logs_workspace_key = self.cmd('monitor log-analytics workspace get-shared-keys -g {} -n {}'.format(resource_group, logs_workspace_name)).get_output_in_json()["primarySharedKey"]

        self.cmd('containerapp env create -g {} -n {} --logs-workspace-id {} --logs-workspace-key {}'.format(resource_group, env_name, logs_workspace_id, logs_workspace_key))

        containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        # create an App service domain and update its txt records
        contacts = os.path.join(TEST_DIR, 'domain-contact.json')
        zone_name = "{}.com".format(env_name)
        subdomain_1 = "devtest"
        subdomain_2 = "clitest"
        txt_name_1 = "asuid.{}".format(subdomain_1)
        txt_name_2 = "asuid.{}".format(subdomain_2)
        hostname_1 = "{}.{}".format(subdomain_1, zone_name)
        hostname_2 = "{}.{}".format(subdomain_2, zone_name)
        verification_id = containerapp_env["properties"]["customDomainConfiguration"]["customDomainVerificationId"]
        self.cmd("appservice domain create -g {} --hostname {} --contact-info=@'{}' --accept-terms".format(resource_group, zone_name, contacts)).get_output_in_json()
        self.cmd('network dns record-set txt add-record -g {} -z {} -n {} -v {}'.format(resource_group, zone_name, txt_name_1, verification_id)).get_output_in_json()
        self.cmd('network dns record-set txt add-record -g {} -z {} -n {} -v {}'.format(resource_group, zone_name, txt_name_2, verification_id)).get_output_in_json()

        # upload cert, add hostname & binding
        pfx_file = os.path.join(TEST_DIR, 'cert.pfx')
        pfx_password = 'test12'

        self.cmd('containerapp env update -g {} -n {} --dns-suffix {} --certificate-file "{}" --certificate-password {}'.format(resource_group, env_name, hostname_1, pfx_file, pfx_password))

        self.cmd(f'containerapp env show -n {env_name} -g {resource_group}', checks=[
            JMESPathCheck('name', env_name),
            JMESPathCheck('properties.customDomainConfiguration.dnsSuffix', hostname_1),
        ])

        self.cmd('containerapp env update -g {} -n {} --dns-suffix {}'.format(resource_group, env_name, hostname_2))

        self.cmd(f'containerapp env show -n {env_name} -g {resource_group}', checks=[
            JMESPathCheck('name', env_name),
            JMESPathCheck('properties.customDomainConfiguration.dnsSuffix', hostname_2),
        ])

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northeurope")
    @live_only()  # passes live but hits CannotOverwriteExistingCassetteException when run from recording
    def test_containerapp_env_internal_only_e2e(self, resource_group):
        # network is not available in North Central US (Stage), if the TEST_LOCATION is "northcentralusstage", use eastus as location
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))

        env = self.create_random_name(prefix='env', length=24)
        logs = self.create_random_name(prefix='logs', length=24)
        vnet = self.create_random_name(prefix='name', length=24)

        self.cmd(f"az network vnet create --address-prefixes '14.0.0.0/23' -g {resource_group} -n {vnet}")
        sub_id = self.cmd(f"az network vnet subnet create --address-prefixes '14.0.0.0/23' --delegations Microsoft.App/environments -n sub -g {resource_group} --vnet-name {vnet}").get_output_in_json()["id"]

        logs_id = self.cmd(f"monitor log-analytics workspace create -g {resource_group} -n {logs} -l eastus").get_output_in_json()["customerId"]
        logs_key = self.cmd(f'monitor log-analytics workspace get-shared-keys -g {resource_group} -n {logs}').get_output_in_json()["primarySharedKey"]

        self.cmd(f'containerapp env create -g {resource_group} -n {env} --logs-workspace-id {logs_id} --logs-workspace-key {logs_key} --internal-only -s {sub_id}')

        containerapp_env = self.cmd(f'containerapp env show -g {resource_group} -n {env}').get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd(f'containerapp env show -g {resource_group} -n {env}').get_output_in_json()

        self.cmd(f'containerapp env show -n {env} -g {resource_group}', checks=[
            JMESPathCheck('name', env),
            JMESPathCheck('properties.vnetConfiguration.internal', True),
        ])

    @AllowLargeResponse(8192)
    @live_only()  # encounters 'CannotOverwriteExistingCassetteException' only when run from recording (passes when run live)
    @ResourceGroupPreparer(location="northeurope")
    def test_containerapp_env_certificate_e2e(self, resource_group):
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))

        env_name = self.create_random_name(prefix='containerapp-e2e-env', length=24)
        logs_workspace_name = self.create_random_name(prefix='containerapp-env', length=24)

        logs_workspace_id = self.cmd(
            'monitor log-analytics workspace create -g {} -n {} -l eastus'.format(resource_group,
                                                                                  logs_workspace_name)).get_output_in_json()[
            "customerId"]
        logs_workspace_key = self.cmd(
            'monitor log-analytics workspace get-shared-keys -g {} -n {}'.format(resource_group,
                                                                                 logs_workspace_name)).get_output_in_json()[
            "primarySharedKey"]

        self.cmd(
            'containerapp env create -g {} -n {} --logs-workspace-id {} --logs-workspace-key {}'.format(resource_group,
                                                                                                        env_name,
                                                                                                        logs_workspace_id,
                                                                                                        logs_workspace_key))

        containerapp_env = self.cmd(
            'containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd(
                'containerapp env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        self.cmd('containerapp env certificate list -g {} -n {}'.format(resource_group, env_name), checks=[
            JMESPathCheck('length(@)', 0),
        ])

        # test that non pfx or pem files are not supported
        txt_file = os.path.join(TEST_DIR, 'cert.txt')
        self.cmd(
            'containerapp env certificate upload -g {} -n {} --certificate-file "{}"'.format(resource_group, env_name,
                                                                                             txt_file),
            expect_failure=True)

        # test pfx file with password
        pfx_file = os.path.join(TEST_DIR, 'cert.pfx')
        pfx_password = 'test12'
        cert = self.cmd('containerapp env certificate upload -g {} -n {} --certificate-file "{}" --password {}'.format(
            resource_group, env_name, pfx_file, pfx_password), checks=[
            JMESPathCheck('type', "Microsoft.App/managedEnvironments/certificates"),
        ]).get_output_in_json()

        cert_name = cert["name"]
        cert_id = cert["id"]
        cert_thumbprint = cert["properties"]["thumbprint"]
        cert_location = cert["location"]

        self.cmd(
            'containerapp env certificate list -n {} -g {} -l "{}"'.format(env_name, resource_group, cert_location),
            checks=[
                JMESPathCheck('length(@)', 1),
                JMESPathCheck('[0].properties.thumbprint', cert_thumbprint),
                JMESPathCheck('[0].name', cert_name),
                JMESPathCheck('[0].id', cert_id),
            ])

        # list certs with a wrong location
        self.cmd(
            'containerapp env certificate upload -g {} -n {} --certificate-file "{}"'.format(resource_group, env_name,
                                                                                             pfx_file),
            expect_failure=True)

        self.cmd('containerapp env certificate list -n {} -g {} --certificate {}'.format(env_name, resource_group,
                                                                                         cert_name), checks=[
            JMESPathCheck('length(@)', 1),
            JMESPathCheck('[0].name', cert_name),
            JMESPathCheck('[0].id', cert_id),
            JMESPathCheck('[0].properties.thumbprint', cert_thumbprint),
        ])

        self.cmd(
            'containerapp env certificate list -n {} -g {} --certificate {}'.format(env_name, resource_group, cert_id),
            checks=[
                JMESPathCheck('length(@)', 1),
                JMESPathCheck('[0].name', cert_name),
                JMESPathCheck('[0].id', cert_id),
                JMESPathCheck('[0].properties.thumbprint', cert_thumbprint),
            ])

        self.cmd('containerapp env certificate list -n {} -g {} --thumbprint {}'.format(env_name, resource_group,
                                                                                        cert_thumbprint), checks=[
            JMESPathCheck('length(@)', 1),
            JMESPathCheck('[0].name', cert_name),
            JMESPathCheck('[0].id', cert_id),
            JMESPathCheck('[0].properties.thumbprint', cert_thumbprint),
        ])

        # create a container app
        ca_name = self.create_random_name(prefix='containerapp', length=24)
        app = self.cmd('containerapp create -g {} -n {} --environment {} --ingress external --target-port 80'.format(
            resource_group, ca_name, env_name)).get_output_in_json()

        # create an App service domain and update its DNS records
        contacts = os.path.join(TEST_DIR, 'domain-contact.json')
        zone_name = "{}.com".format(ca_name)
        subdomain_1 = "devtest"
        txt_name_1 = "asuid.{}".format(subdomain_1)
        hostname_1 = "{}.{}".format(subdomain_1, zone_name)
        verification_id = app["properties"]["customDomainVerificationId"]
        fqdn = app["properties"]["configuration"]["ingress"]["fqdn"]
        self.cmd(
            "appservice domain create -g {} --hostname {} --contact-info=@'{}' --accept-terms".format(resource_group,
                                                                                                      zone_name,
                                                                                                      contacts)).get_output_in_json()
        self.cmd('network dns record-set txt add-record -g {} -z {} -n {} -v {}'.format(resource_group, zone_name,
                                                                                        txt_name_1,
                                                                                        verification_id)).get_output_in_json()
        self.cmd('network dns record-set cname create -g {} -z {} -n {}'.format(resource_group, zone_name,
                                                                                subdomain_1)).get_output_in_json()
        self.cmd('network dns record-set cname set-record -g {} -z {} -n {} -c {}'.format(resource_group, zone_name,
                                                                                          subdomain_1,
                                                                                          fqdn)).get_output_in_json()

        # add hostname without binding, it is a Private key certificates
        self.cmd('containerapp hostname add -g {} -n {} --hostname {}'.format(resource_group, ca_name, hostname_1),
                 checks={
                     JMESPathCheck('length(@)', 1),
                     JMESPathCheck('[0].name', hostname_1),
                     JMESPathCheck('[0].bindingType', "Disabled"),
                 })
        self.cmd('containerapp hostname add -g {} -n {} --hostname {}'.format(resource_group, ca_name, hostname_1),
                 expect_failure=True)
        self.cmd('containerapp env certificate list -g {} -n {} -c {} -p'.format(resource_group, env_name, cert_name),
                 checks=[
                     JMESPathCheck('length(@)', 1),
                 ])

        # create a managed certificate
        self.cmd('containerapp env certificate create -n {} -g {} --hostname {} -v cname -c {}'.format(env_name,
                                                                                                       resource_group,
                                                                                                       hostname_1,
                                                                                                       cert_name),
                 checks=[
                     JMESPathCheck('type', "Microsoft.App/managedEnvironments/managedCertificates"),
                     JMESPathCheck('name', cert_name),
                     JMESPathCheck('properties.subjectName', hostname_1),
                 ]).get_output_in_json()

        self.cmd('containerapp env certificate list -g {} -n {} -m'.format(resource_group, env_name), checks=[
            JMESPathCheck('length(@)', 1),
        ])
        self.cmd('containerapp env certificate list -g {} -n {} -c {}'.format(resource_group, env_name, cert_name),
                 checks=[
                     JMESPathCheck('length(@)', 2),
                 ])

        self.cmd(
            'containerapp env certificate delete -n {} -g {} --certificate {} --yes'.format(env_name, resource_group,
                                                                                            cert_name),
            expect_failure=True)
        self.cmd(
            'containerapp env certificate delete -n {} -g {} --thumbprint {} --yes'.format(env_name, resource_group,
                                                                                           cert_thumbprint))
        self.cmd(
            'containerapp env certificate delete -n {} -g {} --certificate {} --yes'.format(env_name, resource_group,
                                                                                            cert_name))
        self.cmd('containerapp env certificate list -g {} -n {}'.format(resource_group, env_name), checks=[
            JMESPathCheck('length(@)', 0),
        ])

        self.cmd('containerapp hostname bind -g {} -n {} --hostname {} --environment {} -v cname'.format(resource_group,
                                                                                                         ca_name,
                                                                                                         hostname_1,
                                                                                                         env_name))
        certs = self.cmd('containerapp env certificate list -g {} -n {}'.format(resource_group, env_name), checks=[
            JMESPathCheck('length(@)', 1),
        ]).get_output_in_json()
        self.cmd(
            'containerapp env certificate delete -n {} -g {} --certificate {} --yes'.format(env_name, resource_group,
                                                                                            certs[0]["name"]),
            expect_failure=True)

        self.cmd(
            'containerapp hostname delete -g {} -n {} --hostname {} --yes'.format(resource_group, ca_name, hostname_1))
        self.cmd(
            'containerapp env certificate delete -n {} -g {} --certificate {} --yes'.format(env_name, resource_group,
                                                                                            certs[0]["name"]))
        self.cmd('containerapp env certificate list -g {} -n {}'.format(resource_group, env_name), checks=[
            JMESPathCheck('length(@)', 0),
        ])

    @ResourceGroupPreparer(location="southcentralus")
    def test_containerapp_env_certificate_upload_with_certificate_name(self, resource_group):
        location = TEST_LOCATION
        if format_location(location) == format_location(STAGE_LOCATION):
            location = "eastus"
        self.cmd('configure --defaults location={}'.format(location))

        env_name = self.create_random_name(prefix='containerapp-e2e-env', length=24)

        self.cmd('containerapp env create -g {} -n {} --logs-destination none'.format(resource_group, env_name))
        self.cmd('containerapp env certificate list -g {} -n {}'.format(resource_group, env_name), checks=[
            JMESPathCheck('length(@)', 0),
        ])

        # test that non pfx or pem files are not supported
        txt_file = os.path.join(TEST_DIR, 'cert.txt')
        self.cmd('containerapp env certificate upload -g {} -n {} --certificate-file "{}"'.format(resource_group, env_name, txt_file), expect_failure=True)

        # test pfx file with password
        pfx_file = os.path.join(TEST_DIR, 'cert.pfx')
        pfx_password = 'test12'
        cert_pfx_name = self.create_random_name(prefix='cert-pfx', length=24)
        cert = self.cmd(
            'containerapp env certificate upload -g {} -n {} -c {} --certificate-file "{}" --password {}'.format(
                resource_group, env_name, cert_pfx_name, pfx_file, pfx_password), checks=[
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('name', cert_pfx_name),
                JMESPathCheck('type', "Microsoft.App/managedEnvironments/certificates"),
            ]).get_output_in_json()

        cert_name = cert["name"]
        cert_id = cert["id"]
        cert_thumbprint = cert["properties"]["thumbprint"]

        self.cmd('containerapp env certificate list -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('length(@)', 1),
            JMESPathCheck('[0].properties.thumbprint', cert_thumbprint),
            JMESPathCheck('[0].name', cert_name),
            JMESPathCheck('[0].id', cert_id),
        ])

        # upload without password will fail
        self.cmd('containerapp env certificate upload -g {} -n {} --certificate-file "{}"'.format(resource_group, env_name, pfx_file), expect_failure=True)

        self.cmd(
            'containerapp env certificate list -n {} -g {} --certificate {}'.format(env_name, resource_group,
                                                                                    cert_name), checks=[
                JMESPathCheck('length(@)', 1),
                JMESPathCheck('[0].name', cert_name),
                JMESPathCheck('[0].id', cert_id),
                JMESPathCheck('[0].properties.thumbprint', cert_thumbprint),
            ])

        self.cmd(
            'containerapp env certificate list -n {} -g {} --certificate {}'.format(env_name, resource_group,
                                                                                    cert_id), checks=[
                JMESPathCheck('length(@)', 1),
                JMESPathCheck('[0].name', cert_name),
                JMESPathCheck('[0].id', cert_id),
                JMESPathCheck('[0].properties.thumbprint', cert_thumbprint),
            ])

        self.cmd(
            'containerapp env certificate list -n {} -g {} --thumbprint {}'.format(env_name, resource_group,
                                                                                   cert_thumbprint), checks=[
                JMESPathCheck('length(@)', 1),
                JMESPathCheck('[0].name', cert_name),
                JMESPathCheck('[0].id', cert_id),
                JMESPathCheck('[0].properties.thumbprint', cert_thumbprint),
            ])

        self.cmd('containerapp env certificate delete -n {} -g {} --thumbprint {} --certificate {} --yes'.format(
            env_name, resource_group, cert_thumbprint, cert_name), expect_failure=False)
        self.cmd('containerapp env certificate list -g {} -n {}'.format(resource_group, env_name), checks=[
            JMESPathCheck('length(@)', 0),
        ])
        self.cmd('containerapp env delete -g {} -n {} --yes'.format(resource_group, env_name), expect_failure=False)
