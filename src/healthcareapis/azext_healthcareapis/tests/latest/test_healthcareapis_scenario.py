# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
from azure.cli.testsdk import ScenarioTest
from .. import try_manual, raise_if, calc_coverage
from azure.cli.testsdk import ResourceGroupPreparer
from azure.cli.testsdk import StorageAccountPreparer

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

# Env setup
@try_manual
def setup(test, rg):
    # TODO set up kv and private endpoint/vnets for cmk and private link respectively
    # figure out how to set up authentication configuration
    test.cmd('az keyvault create --name "{keyvaultname}" --resource-group "{rg}" --location "{testingLocation}" --enable-purge-protection')
    test.cmd('az keyvault set-policy --name "{keyvaultname}" --key-permissions get wrapKey unwrapKey --object-id a232010e-820c-4083-83bb-3ace5fc29d0b')
    #test.cmd('az kevault key create --name "somekey" --vault-name "{keyvaultname}')
    pass

#todo add more property validation
#todo remove unnecesarry required parameter from documentation
@try_manual
def step_healthcareapiscreateminimalparameters(test, rg):
    test.cmd('az healthcareapis service create '
             '--resource-group "{rg}" '
             '--resource-name "{minimalParams}" '
             '--kind "fhir-Stu3" '
             '--location "{testingLocation}" ',
             checks=[
                test.check("name", "{minimalParams}", case_sensitive=False),
                test.check("location", "{testingLocation}", case_sensitive=False),
                test.check("kind", "fhir-Stu3", case_sensitive=False),
                test.check("properties.authenticationConfiguration.smartProxyEnabled", False),
                test.check("properties.corsConfiguration.allowCredentials", False),
                test.check("properties.cosmosDbConfiguration.offerThroughput", 1000),
                test.check("properties.provisioningState", "Succeeded"),
                test.check("properties.publicNetworkAccess", "Enabled", case_sensitive=False),
             ])

#todo add more property validation and parameters
#todo remove unecessary parameters from command
@try_manual
def step_healthcareapiscreatemaximumparameters(test, rg):
    #Need to add keyvault key uri
    #need to add access policies
    testFhir = test.cmd('az healthcareapis service create '
             '--resource-group "{rg}" '
             '--resource-name "{maximumParams}" '
             '--identity-type "SystemAssigned" '
             '--kind "{fhirr4}" '
             '--location "{testingLocation}" '
             '--authentication-configuration authority="https://login.microsoftonline.com/6c4a34fb-44bb-4cc7-bf56-9b4e264f1891" audience="https://{maximumParams}.azurehealthcareapis.com" smart-proxy-enabled=false '
             '--cors-configuration allow-credentials=false headers="*" max-age=1440 methods="DELETE" methods="GET" methods="OPTIONS" methods="PATCH" methods="POST" methods="PUT" origins="*" '
             '--cosmos-db-configuration offer-throughput=1500 '
             '--export-configuration-storage-account-name "{sg}" '
             '--public-network-access "Disabled" ',
             checks=[
                test.check("identity.type", "SystemAssigned", case_sensitive=False),
                test.check("kind", "{fhirr4}"),
                test.check("location", "{testingLocation}", case_sensitive=False),
                test.check("name", "{maximumParams}", case_sensitive=False),
                test.check("properties.authenticationConfiguration.smartProxyEnabled", False),
                test.check("properties.corsConfiguration.allowCredentials", False),
                test.check("properties.corsConfiguration.maxAge", 1440),
                test.check("properties.cosmosDbConfiguration.offerThroughput", 1500),
                test.check("properties.exportConfiguration.storageAccountName", "{sg}", case_sensitive=False),
                test.check("properties.provisioningState", "Succeeded"),
                test.check("properties.publicNetworkAccess", "Disabled", case_sensitive=False),
             ]).get_output_in_json()

    corsConfiguration = testFhir['properties']['corsConfiguration']
    assert len(corsConfiguration['headers']) == 1
    assert len(corsConfiguration['origins']) == 1
    assert corsConfiguration['headers'][0] == "*"
    assert corsConfiguration['origins'][0] == "*"
    assert len(corsConfiguration['methods']) == 6
    assert "DELETE" in corsConfiguration['methods']
    assert "GET" in corsConfiguration['methods']
    assert "OPTIONS" in corsConfiguration['methods']
    assert "PATCH" in corsConfiguration['methods']
    assert "POST" in corsConfiguration['methods']
    assert "PUT" in corsConfiguration['methods']


#todo add more property validation and parameters
@try_manual
def step_healthcareapisupdatemaximumparameters(test, rg):
    #Need to add keyvault key uri
    #need to add access policies

    #shouldn't change anything other than identity type
    testFhir = test.cmd('az healthcareapis service create '
             '--resource-group "{rg}" '
             '--resource-name "{maximumParams}" '
             '--identity-type "None" '
             '--kind "{fhirr4}" '
             '--location "{testingLocation}" ',
             checks=[
                test.check("identity.type", "None", case_sensitive=False),
                test.check("kind", "{fhirr4}"),
                test.check("location", "{testingLocation}", case_sensitive=False),
                test.check("name", "{maximumParams}", case_sensitive=False),
                test.check("properties.authenticationConfiguration.smartProxyEnabled", False),
                test.check("properties.corsConfiguration.allowCredentials", False),
                test.check("properties.corsConfiguration.maxAge", 1440),
                test.check("properties.cosmosDbConfiguration.offerThroughput", 1500),
                test.check("properties.exportConfiguration.storageAccountName", "{sg}", case_sensitive=False),
                test.check("properties.provisioningState", "Succeeded"),
                test.check("properties.publicNetworkAccess", "Disabled", case_sensitive=False),
             ]).get_output_in_json()

    corsConfiguration = testFhir['properties']['corsConfiguration']
    assert len(corsConfiguration['headers']) == 1
    assert len(corsConfiguration['origins']) == 1
    assert corsConfiguration['headers'][0] == "*"
    assert corsConfiguration['origins'][0] == "*"
    assert len(corsConfiguration['methods']) == 6
    assert "DELETE" in corsConfiguration['methods']
    assert "GET" in corsConfiguration['methods']
    assert "OPTIONS" in corsConfiguration['methods']
    assert "PATCH" in corsConfiguration['methods']
    assert "POST" in corsConfiguration['methods']
    assert "PUT" in corsConfiguration['methods']

    #shouldn't change anything other than public network access
    testFhir = test.cmd('az healthcareapis service create '
             '--resource-group "{rg}" '
             '--resource-name "{maximumParams}" '
             '--public-network-access "Enabled" '
             '--kind "{fhirr4}" '
             '--location "{testingLocation}" ',
             checks=[
                test.check("identity.type", "None", case_sensitive=False),
                test.check("kind", "{fhirr4}"),
                test.check("location", "{testingLocation}", case_sensitive=False),
                test.check("name", "{maximumParams}", case_sensitive=False),
                test.check("properties.authenticationConfiguration.smartProxyEnabled", False),
                test.check("properties.corsConfiguration.allowCredentials", False),
                test.check("properties.corsConfiguration.maxAge", 1440),
                test.check("properties.cosmosDbConfiguration.offerThroughput", 1500),
                test.check("properties.exportConfiguration.storageAccountName", "{sg}", case_sensitive=False),
                test.check("properties.provisioningState", "Succeeded"),
                test.check("properties.publicNetworkAccess", "Enabled", case_sensitive=False),
             ]).get_output_in_json()

    corsConfiguration = testFhir['properties']['corsConfiguration']
    assert len(corsConfiguration['headers']) == 1
    assert len(corsConfiguration['origins']) == 1
    assert corsConfiguration['headers'][0] == "*"
    assert corsConfiguration['origins'][0] == "*"
    assert len(corsConfiguration['methods']) == 6
    assert "DELETE" in corsConfiguration['methods']
    assert "GET" in corsConfiguration['methods']
    assert "OPTIONS" in corsConfiguration['methods']
    assert "PATCH" in corsConfiguration['methods']
    assert "POST" in corsConfiguration['methods']
    assert "PUT" in corsConfiguration['methods']
    

#todo list all the resources and make sure at least two were created
@try_manual
def step_servicelist(test, rg):
    test.cmd('az healthcareapis service list ',
    checks=[
    ])
    pass


@try_manual
def step_serviceget(test, rg):
    test.cmd('az healthcareapis service show --resource-group "{rg}" --resource-name "{maximumParams}"',
    checks=[
        test.check("name", "{maximumParams}", case_sensitive=False),
        test.check("location", "{testingLocation}", case_sensitive=False),
        test.check("kind", "{fhirr4}"),
        test.check("properties.corsConfiguration.allowCredentials", False),
    ])
    
    pass


@try_manual
def step_servicelistbyresourcegroup(test, rg):
    test.cmd('az healthcareapis service list --resource-group "{rg}"',
    checks=[
    ])
    pass


@try_manual
def step_servicedelete(test, rg):
    test.cmd('az healthcareapis service delete '
    '--resource-group "{rg}" '
    '--resource-name "{minimalParams}" '
    '--yes ',
    checks=[
    ])
    pass


# EXAMPLE: OperationsList
@try_manual
def step_operationslist(test, rg):
    # EXAMPLE NOT FOUND!
    pass


# EXAMPLE: OperationResultsGet
@try_manual
def step_operationresultsget(test, rg):
    # EXAMPLE NOT FOUND!
    pass


# Env cleanup
@try_manual
def cleanup(test, rg):
    pass


# Testcase
@try_manual
def call_scenario(test, rg):
    setup(test, rg)
    step_healthcareapiscreateminimalparameters(test, rg)
    step_healthcareapiscreatemaximumparameters(test, rg)
    step_healthcareapisupdatemaximumparameters(test, rg)
    step_operationresultsget(test, rg)
    step_serviceget(test, rg)
    step_servicelistbyresourcegroup(test, rg)
    # for the subscription that I was testing under there was too many instances
    # step_servicelist(test, rg)
    step_operationslist(test, rg)
    step_servicedelete(test, rg)
    cleanup(test, rg)


@try_manual
class HealthcareApisManagementClientScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='clitesthealthcareapis_rgname'[:7], key='rg', parameter_name='rg')
    @StorageAccountPreparer(name_prefix='clitesthealthcareapis_existingStorageAccount'[:7], key='sa',
                            resource_group_parameter_name='rg', parameter_name='sg')
    def test_healthcareapis(self, rg, sg):

        self.kwargs.update({
            'subscription_id': self.get_subscription_id()
        })

        self.kwargs.update({
            'keyvaultname': self.create_random_name(prefix='clikv', length=10),
            'myPrivateEndpointConnection': 'myConnection',
            'myAttachedDatabaseConfiguration3': 'default',
            'fhirr4': 'fhir-R4',
            'testingLocation': 'westus2',
            'minimalParams': self.create_random_name(prefix='climinparams', length=18),
            'maximumParams': self.create_random_name(prefix='climaxparams', length=24),
            'sg': sg,
        })

        call_scenario(self, rg)
        calc_coverage(__file__)
        raise_if()
