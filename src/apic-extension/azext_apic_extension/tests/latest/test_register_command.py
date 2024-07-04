# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from .utils import ApicServicePreparer, ApicEnvironmentPreparer
from .constants import TEST_REGION

current_dir = os.path.dirname(os.path.realpath(__file__))
test_assets_dir = os.path.join(current_dir, 'test_assets')

class RegisterCommandTests(ScenarioTest):

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    def test_register_with_yml_spec(self):
        self.kwargs.update({
          'spec_file': os.path.join(test_assets_dir, 'petstore.yaml')
        })
        self.cmd('az apic api register -g {rg} -n {s} -l "{spec_file}"')

        # verify command results
        self.cmd('az apic api show -g {rg} -n {s} --api-id swaggerpetstore', checks=[
            self.check('description', 'API Description'), # default value when spec does not have description
            self.check('summary', 'API Description'), # default value when spec does not have summary
            self.check('kind', 'rest'),
            self.check('contacts', []),
            self.check('customProperties', {}),
            self.check('kind', 'rest'),
            self.check('license.name', 'MIT'),
            self.check('lifecycleStage', 'design'), # default value assigned by APIC
            self.check('name', 'swaggerpetstore'),
            self.check('title', 'Swagger Petstore')
        ])

        self.cmd('az apic api version show -g {rg} -n {s} --api-id swaggerpetstore --version-id 1-0-0', checks=[
            self.check('lifecycleStage', 'design'), # hard coded now
            self.check('name', '1-0-0'),
            self.check('title', '1-0-0'),
        ])

        self.cmd('az apic api definition show -g {rg} -n {s} --api-id swaggerpetstore --version-id 1-0-0 --definition-id openapi', checks=[
            self.check('description', 'API Description'), # default value when spec does not have description
            self.check('name', 'openapi'), # hard coded when spec is swagger or openapi
            self.check('specification.name', 'openapi'),
            self.check('specification.version', '3-0-0'),
            self.check('title', 'openapi'),
        ])

        self.cmd('az apic api definition export-specification -g {rg} -n {s} --api-id swaggerpetstore --version-id 1-0-0 --definition-id openapi --file-name test_register_with_yml_spec.yml')

        try:
            exported_file_path = "test_register_with_yml_spec.yml"
            with open(exported_file_path, 'r') as file:
                exported_content = file.read()

            input_file_path = self.kwargs['spec_file']
            with open(input_file_path, 'r') as file:
                input_content = file.read()

            assert exported_content == input_content, "The exported content is not the same as the input file."
        finally:
            os.remove(exported_file_path)

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    def test_register_with_json_spec(self):
        self.kwargs.update({
          'spec_file': os.path.join(test_assets_dir, 'petstore.json')
        })
        self.cmd('az apic api register -g {rg} -n {s} -l "{spec_file}"')

        # verify command results
        self.cmd('az apic api show -g {rg} -n {s} --api-id swaggerpetstore-openapi30', checks=[
            self.check('contacts[0].email', 'apiteam@swagger.io'),
            self.check('description', 'This is a sample Pet Store Server based on the OpenAPI 3.0 specification.  You can find out more about\nSwagger at [http://swagger.io](http://swagger.io). In the third iteration of the pet store, we\'ve switched to the design first approach!\nYou can now help us improve the API whether it\'s by making changes to the definition itself or to the code.\nThat way, with time, we can improve the API in general, and expose some of the new features in OAS3.\n\nSome useful links:\n- [The Pet Store repository](https://github.com/swagger-api/swagger-petstore)\n- [The source API definition for the Pet Store](https://github.com/swagger-api/swagger-petstore/blob/master/src/main/resources/openapi.yaml)'),
            self.check('kind', 'rest'),
            self.check('license.name', 'Apache 2.0'),
            self.check('license.url', 'http://www.apache.org/licenses/LICENSE-2.0.html'),
            self.check('lifecycleStage', 'design'),
            self.check('name', 'swaggerpetstore-openapi30'),
            self.check('summary', 'This is a sample Pet Store Server based on the OpenAPI 3.0 specification.  You can find out more about\nSwagger at [http://swagger.io](http://swagger.io). In the third iteration of the pet store, we\'ve'),
            self.check('title', 'Swagger Petstore - OpenAPI 3.0'),
        ])

        self.cmd('az apic api version show -g {rg} -n {s} --api-id swaggerpetstore-openapi30 --version-id 1-0-19', checks=[
            self.check('lifecycleStage', 'design'),
            self.check('name', '1-0-19'),
            self.check('title', '1-0-19'),
        ])

        self.cmd('az apic api definition show -g {rg} -n {s} --api-id swaggerpetstore-openapi30 --version-id 1-0-19 --definition-id openapi', checks=[
            self.check('description', 'This is a sample Pet Store Server based on the OpenAPI 3.0 specification.  You can find out more about\nSwagger at [http://swagger.io](http://swagger.io). In the third iteration of the pet store, we\'ve switched to the design first approach!\nYou can now help us improve the API whether it\'s by making changes to the definition itself or to the code.\nThat way, with time, we can improve the API in general, and expose some of the new features in OAS3.\n\nSome useful links:\n- [The Pet Store repository](https://github.com/swagger-api/swagger-petstore)\n- [The source API definition for the Pet Store](https://github.com/swagger-api/swagger-petstore/blob/master/src/main/resources/openapi.yaml)'),
            self.check('name', 'openapi'),
            self.check('specification.name', 'openapi'),
            self.check('specification.version', '3-0-2'),
            self.check('title', 'openapi'),
        ])

        self.cmd('az apic api definition export-specification -g {rg} -n {s} --api-id swaggerpetstore-openapi30 --version-id 1-0-19 --definition-id openapi --file-name test_register_with_json_spec.yml')

        try:
            exported_file_path = "test_register_with_json_spec.yml"
            with open(exported_file_path, 'r') as file:
                exported_content = file.read()

            input_file_path = self.kwargs['spec_file']
            with open(input_file_path, 'r') as file:
                input_content = file.read()

            assert exported_content == input_content, "The exported content is not the same as the input file."
        finally:
            os.remove(exported_file_path)

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    def test_register_with_long_openapi_description(self):
        self.kwargs.update({
          'spec_file': os.path.join(test_assets_dir, 'spec_with_long_description.json')
        })
        self.cmd('az apic api register -g {rg} -n {s} -l "{spec_file}"')

        # verify command results
        self.cmd('az apic api show -g {rg} -n {s} --api-id swaggerpetstore-openapi30', checks=[
            self.check('description', 'This is a sample Pet Store Server based on the OpenAPI 3.0 specification.  You can find out more about\nSwagger at [http://swagger.io](http://swagger.io). In the third iteration of the pet store, we\'ve switched to the design first approach!\nYou can now help us improve the API whether it\'s by making changes to the definition itself or to the code.\nThat way, with time, we can improve the API in general, and expose some of the new features in OAS3.\n\nSome useful links:\n- [The Pet Store repository](https://github.com/swagger-api/swagger-petstore)\n- [The source API definition for the Pet Store](https://github.com/swagger-api/swagger-petstore/blob/master/src/main/resources/openapi.yaml)This is a sample Pet Store Server based on the OpenAPI 3.0 specification.  You can find out more about\nSwagger at [http://swagger.io](http://swagger.io). In the third iteration of the pet store, we\'ve switched to the design first approach!\nYou can now help us improve the API whether it\'s by making changes to the')
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicEnvironmentPreparer()
    def test_examples_register_with_json_spec(self):
        self.kwargs.update({
          'spec_file': os.path.join(test_assets_dir, 'petstore.json')
        })
        self.cmd('az apic api register -g {rg} -n {s} --api-location "{spec_file}" --environment-id {e}')

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicEnvironmentPreparer()
    def test_examples_register_with_yml_spec(self):
        self.kwargs.update({
          'spec_file': os.path.join(test_assets_dir, 'petstore.yml')
        })
        self.cmd('az apic api register -g {rg} -n {s} --api-location "{spec_file}" --environment-id {e}')
