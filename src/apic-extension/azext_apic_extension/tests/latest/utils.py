# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk.preparers import NoTrafficRecordingPreparer, SingleValueReplacer, get_dummy_cli, CliTestError, ResourceGroupPreparer

class ApicServicePreparer(NoTrafficRecordingPreparer, SingleValueReplacer):
    def __init__(self, name_prefix='clitest', length=24,
                 parameter_name='service_name', resource_group_parameter_name='resource_group', key='s'):
        super(ApicServicePreparer, self).__init__(name_prefix, length)
        self.cli_ctx = get_dummy_cli()
        self.resource_group_parameter_name = resource_group_parameter_name
        self.parameter_name = parameter_name
        self.key = key

    def create_resource(self, name, **kwargs):
        group = self._get_resource_group(**kwargs)

        template = 'az apic service create --name {} -g {}'
        print(template.format(name, group))
        self.live_only_execute(self.cli_ctx, template.format(name, group))

        self.test_class_instance.kwargs[self.key] = name
        return {self.parameter_name: name}

    def remove_resource(self, name, **kwargs):
        # ResourceGroupPreparer will delete everything
        pass

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs.get(self.resource_group_parameter_name)
        except KeyError:
            template = 'To create a API Center service a resource group is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ResourceGroupPreparer.__name__))
