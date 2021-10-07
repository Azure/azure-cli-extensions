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
    pass


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


@try_manual
def step_healthcareapiscreatemaximumparameters(test, rg):
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


@try_manual
def step_healthcareapisupdatemaximumparameters(test, rg):

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
                            test.check("properties.corsConfiguration.maxAge", None),
                            test.check("properties.cosmosDbConfiguration.offerThroughput", 1000),
                            test.check("properties.exportConfiguration.storageAccountName", None),
                            test.check("properties.provisioningState", "Succeeded"),
                            test.check("properties.publicNetworkAccess", "Enabled", case_sensitive=False),
                            test.check("properties.secondaryLocations", None),
                        ]).get_output_in_json()

    corsConfiguration = testFhir['properties']['corsConfiguration']
    assert len(corsConfiguration['headers']) == 0
    assert len(corsConfiguration['origins']) == 0
    assert len(corsConfiguration['methods']) == 0

    accessPolicies = testFhir['properties']['accessPolicies']
    assert len(accessPolicies) == 0

    privateEndpointConnections = testFhir['properties']['accessPolicies']
    assert len(privateEndpointConnections) == 0

    acrConfiguration = testFhir['properties']['acrConfiguration']['loginServers']
    assert len(acrConfiguration) == 0

    testFhir = test.cmd('az healthcareapis service create '
                        '--resource-group "{rg}" '
                        '--resource-name "{maximumParams}" '
                        '--public-network-access "Disabled" '
                        '--kind "{fhirr4}" '
                        '--location "{testingLocation}" ',
                        checks=[
                            test.check("identity.type", "None", case_sensitive=False),
                            test.check("kind", "{fhirr4}"),
                            test.check("location", "{testingLocation}", case_sensitive=False),
                            test.check("name", "{maximumParams}", case_sensitive=False),
                            test.check("properties.authenticationConfiguration.smartProxyEnabled", False),
                            test.check("properties.corsConfiguration.allowCredentials", False),
                            test.check("properties.corsConfiguration.maxAge", None),
                            test.check("properties.cosmosDbConfiguration.offerThroughput", 1000),
                            test.check("properties.exportConfiguration.storageAccountName", None),
                            test.check("properties.provisioningState", "Succeeded"),
                            test.check("properties.publicNetworkAccess", "Disabled", case_sensitive=False),
                            test.check("properties.secondaryLocations", None),
                        ]).get_output_in_json()

    corsConfiguration = testFhir['properties']['corsConfiguration']
    assert len(corsConfiguration['headers']) == 0
    assert len(corsConfiguration['origins']) == 0
    assert len(corsConfiguration['methods']) == 0

    accessPolicies = testFhir['properties']['accessPolicies']
    assert len(accessPolicies) == 0

    privateEndpointConnections = testFhir['properties']['accessPolicies']
    assert len(privateEndpointConnections) == 0

    acrConfiguration = testFhir['properties']['acrConfiguration']['loginServers']
    assert len(acrConfiguration) == 0


@try_manual
def step_servicelist(test, rg):
    test.cmd('az healthcareapis service list ',
             checks=[])
    pass


@try_manual
def step_serviceget(test, rg):
    test.cmd('az healthcareapis service show '
             '--resource-group "{rg}" '
             '--resource-name "{maximumParams}"',
             checks=[
                 test.check("name", "{maximumParams}", case_sensitive=False),
                 test.check("location", "{testingLocation}", case_sensitive=False),
                 test.check("kind", "{fhirr4}"),
                 test.check("properties.corsConfiguration.allowCredentials", False),
             ])
    pass


@try_manual
def step_servicelistbyresourcegroup(test, rg):
    test.cmd('az healthcareapis service list '
             '--resource-group "{rg}"',
             checks=[])
    pass


@try_manual
def step_servicedelete(test, rg):
    test.cmd('az healthcareapis service delete '
             '--resource-group "{rg}" '
             '--resource-name "{minimalParams}" '
             '--yes ',
             checks=[])
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
    # this caused the script to crash
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
