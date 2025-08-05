# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import jmespath
import collections
from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from azure.cli.testsdk.checkers import JMESPathCheck
from azure.cli.testsdk.exceptions import JMESPathCheckAssertionError
from .utils import ApicServicePreparer, ApimServicePreparer
from .constants import TEST_REGION, AWS_ACCESS_KEY_LINK, AWS_SECRET_ACCESS_KEY_LINK, AWS_REGION, USERASSIGNED_IDENTITY

# override the JMESPathCheck class to support checking multiple possible values as a list
class JMESPathCheckAny(JMESPathCheck):
    def __init__(self, query, expected_results, case_sensitive=True):
        super().__init__(query, expected_results, case_sensitive)
        if not isinstance(expected_results, list):
            raise ValueError("expected_results should be a list of possible values")

    def __call__(self, execution_result):
        json_value = execution_result.get_output_in_json()
        actual_value = jmespath.search(self._query, json_value, jmespath.Options(collections.OrderedDict))
        if self._case_sensitive:
            if actual_value not in [result for result in self._expected_result]:
                raise JMESPathCheckAssertionError(self._query, self._expected_result, actual_value, execution_result.output)
        else:
            if actual_value.lower() not in [result.lower() for result in self._expected_result]:
                raise JMESPathCheckAssertionError(self._query, self._expected_result, actual_value, execution_result.output)

class IntegrationCommandTests(ScenarioTest):
    # override the check method to support checking multiple possible values
    def check(self, query, expected_results, case_sensitive=True):
        query = self._apply_kwargs(query)
        expected_results = self._apply_kwargs(expected_results)
        
        if isinstance(expected_results, list):
            return JMESPathCheckAny(query, expected_results, case_sensitive)
        else:
            return JMESPathCheck(query, expected_results, case_sensitive)

    # TODO: change the location to TEST_REGION when the APIC resource provider is available in all regions
    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApimServicePreparer()
    def test_integration_create_apim(self):
        if self.is_live:
            # prepare test data
            self.kwargs.update({
                'integration_name': self.create_random_name(prefix='cli', length=8)
            })

            if self.kwargs['use_system_assigned_identity'] or not self.is_live:
                self.cmd('az apic integration create apim -g {rg} -n {s} --azure-apim {apim_name} -i {integration_name}')
            else:
                self.cmd('az apic integration create apim -g {rg} -n {s} --azure-apim {apim_name} -i {integration_name} --msi-resource-id "{usi_id}"')

            # verify command results
            self.cmd('az apic integration show -g {rg} -n {s} -i {integration_name}', checks=[
                self.check('apiSourceType', 'AzureApiManagement'),
                self.check('name', '{integration_name}'),
                self.check('linkState.state', list(['initializing', 'syncing']))
            ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer(user_assigned_identity=USERASSIGNED_IDENTITY)
    def test_integration_create_aws(self):
        if self.is_live:
            # prepare test data
            self.kwargs.update({
                'integration_name': self.create_random_name(prefix='cli', length=8),
                'usi_id': USERASSIGNED_IDENTITY,
                'access_key_link': AWS_ACCESS_KEY_LINK,
                'secret_access_key_link': AWS_SECRET_ACCESS_KEY_LINK,
                'aws_region': AWS_REGION
            })

            self.cmd('az apic integration create aws -g {rg} -n {s} -i {integration_name} --aws-access-key-reference {access_key_link} --aws-region {aws_region} --aws-secret-access-key-reference {secret_access_key_link}')

            # verify command results
            self.cmd('az apic integration show -g {rg} -n {s} -i {integration_name}', checks=[
                self.check('apiSourceType', 'AmazonApiGateway'),
                self.check('name', '{integration_name}'),
                self.check('linkState.state', list(['initializing', 'syncing']))
            ])

