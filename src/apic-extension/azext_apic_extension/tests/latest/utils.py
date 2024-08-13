# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk.preparers import NoTrafficRecordingPreparer, SingleValueReplacer, get_dummy_cli, CliTestError, ResourceGroupPreparer

class ApicServicePreparer(NoTrafficRecordingPreparer, SingleValueReplacer):
    def __init__(self, name_prefix='clitest', length=24,
                 parameter_name='service_name', resource_group_parameter_name='resource_group', key='s',
                 enable_system_assigned_identity=False):
        super(ApicServicePreparer, self).__init__(name_prefix, length)
        self.cli_ctx = get_dummy_cli()
        self.resource_group_parameter_name = resource_group_parameter_name
        self.parameter_name = parameter_name
        self.enable_system_assigned_identity = enable_system_assigned_identity
        self.key = key

    def create_resource(self, name, **kwargs):
        group = self._get_resource_group(**kwargs)

        template = 'az apic create --name {} -g {}'

        if self.enable_system_assigned_identity:
            template += ' --identity \'{{type:SystemAssigned}}\''

        cmd=template.format(name, group)
        print(cmd)
        self.live_only_execute(self.cli_ctx, cmd)

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

class ApicMetadataPreparer(NoTrafficRecordingPreparer, SingleValueReplacer):
    def __init__(self, name_prefix='clitest', length=24,
                 parameter_name='metadata_name', resource_group_parameter_name='resource_group',
                 apic_service_parameter_name='service_name',
                 schema='{"type":"boolean", "title":"Public Facing"}',
                 assignments='[{entity:api,required:true,deprecated:false},{entity:environment,required:true,deprecated:false},{entity:deployment,required:true,deprecated:false}]',
                 key='m'):
        super(ApicMetadataPreparer, self).__init__(name_prefix, length)
        self.cli_ctx = get_dummy_cli()
        self.resource_group_parameter_name = resource_group_parameter_name
        self.api_service_parameter_name = apic_service_parameter_name
        self.parameter_name = parameter_name
        self.schema = schema
        self.assignments = assignments
        self.key = key

    def create_resource(self, name, **kwargs):
        group = self._get_resource_group(**kwargs)
        service = self._get_apic_service(**kwargs)

        template = 'az apic metadata create -g {} -n {} --metadata-name {} --schema \'{}\' --assignments \'{}\''
        cmd = template.format(group, service, name, self.schema, self.assignments)
        print(cmd)
        self.live_only_execute(self.cli_ctx, cmd)

        self.test_class_instance.kwargs[self.key] = name
        return {self.parameter_name: name}

    def remove_resource(self, name, **kwargs):
        # ResourceGroupPreparer will delete everything
        pass

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs.get(self.resource_group_parameter_name)
        except KeyError:
            template = 'To create an API Center metadata a resource group is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ResourceGroupPreparer.__name__))

    def _get_apic_service(self, **kwargs):
        try:
            return kwargs.get(self.api_service_parameter_name)
        except KeyError:
            template = 'To create an API Center metadata a API Center service is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ApicServicePreparer.__name__))

class ApicEnvironmentPreparer(NoTrafficRecordingPreparer, SingleValueReplacer):
    def __init__(self, name_prefix='clitest', length=24,
                 parameter_name='environment_id', resource_group_parameter_name='resource_group',
                 apic_service_parameter_name='service_name', key='e'):
        super(ApicEnvironmentPreparer, self).__init__(name_prefix, length)
        self.cli_ctx = get_dummy_cli()
        self.resource_group_parameter_name = resource_group_parameter_name
        self.api_service_parameter_name = apic_service_parameter_name
        self.parameter_name = parameter_name
        self.key = key

    def create_resource(self, name, **kwargs):
        group = self._get_resource_group(**kwargs)
        service = self._get_apic_service(**kwargs)

        template = 'az apic environment create -g {} -n {} --environment-id {} --title "test environment" --type testing'
        cmd = template.format(group, service, name)
        print(cmd)
        self.live_only_execute(self.cli_ctx, cmd)

        self.test_class_instance.kwargs[self.key] = name
        return {self.parameter_name: name}

    def remove_resource(self, name, **kwargs):
        # ResourceGroupPreparer will delete everything
        pass

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs.get(self.resource_group_parameter_name)
        except KeyError:
            template = 'To create an API Center environment a resource group is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ResourceGroupPreparer.__name__))

    def _get_apic_service(self, **kwargs):
        try:
            return kwargs.get(self.api_service_parameter_name)
        except KeyError:
            template = 'To create an API Center environment an API Center service is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ApicServicePreparer.__name__))

class ApicApiPreparer(NoTrafficRecordingPreparer, SingleValueReplacer):
    def __init__(self, name_prefix='clitest', length=24,
                 parameter_name='api_id', resource_group_parameter_name='resource_group',
                 apic_service_parameter_name='service_name', key='api'):
        super(ApicApiPreparer, self).__init__(name_prefix, length)
        self.cli_ctx = get_dummy_cli()
        self.resource_group_parameter_name = resource_group_parameter_name
        self.api_service_parameter_name = apic_service_parameter_name
        self.parameter_name = parameter_name
        self.key = key

    def create_resource(self, name, **kwargs):
        group = self._get_resource_group(**kwargs)
        service = self._get_apic_service(**kwargs)

        template = 'az apic api create -g {} -n {} --api-id {} --title "Echo API" --type rest'
        cmd = template.format(group, service, name)
        print(cmd)
        self.live_only_execute(self.cli_ctx, cmd)

        self.test_class_instance.kwargs[self.key] = name
        return {self.parameter_name: name}

    def remove_resource(self, name, **kwargs):
        # ResourceGroupPreparer will delete everything
        pass

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs.get(self.resource_group_parameter_name)
        except KeyError:
            template = 'To create an API Center API a resource group is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ResourceGroupPreparer.__name__))

    def _get_apic_service(self, **kwargs):
        try:
            return kwargs.get(self.api_service_parameter_name)
        except KeyError:
            template = 'To create an API Center API an API Center service is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ApicServicePreparer.__name__))

class ApicVersionPreparer(NoTrafficRecordingPreparer, SingleValueReplacer):
    def __init__(self, name_prefix='clitest', length=24,
                 parameter_name='version_id', resource_group_parameter_name='resource_group',
                 apic_service_parameter_name='service_name', apic_api_parameter_name='api_id',
                 key='v'):
        super(ApicVersionPreparer, self).__init__(name_prefix, length)
        self.cli_ctx = get_dummy_cli()
        self.resource_group_parameter_name = resource_group_parameter_name
        self.apic_service_parameter_name = apic_service_parameter_name
        self.parameter_name = parameter_name
        self.apic_api_parameter_name = apic_api_parameter_name
        self.key = key

    def create_resource(self, name, **kwargs):
        group = self._get_resource_group(**kwargs)
        service = self._get_apic_service(**kwargs)
        api = self._get_apic_api(**kwargs)

        template = 'az apic api version create -g {} -n {} --api-id {} --version-id {} --lifecycle-stage production --title "v1.0.0"'
        cmd = template.format(group, service, api, name)
        print(cmd)
        self.live_only_execute(self.cli_ctx, cmd)

        self.test_class_instance.kwargs[self.key] = name
        return {self.parameter_name: name}

    def remove_resource(self, name, **kwargs):
        # ResourceGroupPreparer will delete everything
        pass

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs.get(self.resource_group_parameter_name)
        except KeyError:
            template = 'To create an API Center API a resource group is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ResourceGroupPreparer.__name__))

    def _get_apic_service(self, **kwargs):
        try:
            return kwargs.get(self.apic_service_parameter_name)
        except KeyError:
            template = 'To create an API Center API an API Center service is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ApicServicePreparer.__name__))

    def _get_apic_api(self, **kwargs):
        try:
            return kwargs.get(self.apic_api_parameter_name)
        except KeyError:
            template = 'To create an API Center Version an API Center API is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ApicApiPreparer.__name__))
        
class ApicDefinitionPreparer(NoTrafficRecordingPreparer, SingleValueReplacer):
    def __init__(self, name_prefix='clitest', length=24,
                 parameter_name='definition_id', resource_group_parameter_name='resource_group',
                 apic_service_parameter_name='service_name', apic_api_parameter_name='api_id',
                 apic_version_parameter_name='version_id', key='d'):
        super(ApicDefinitionPreparer, self).__init__(name_prefix, length)
        self.cli_ctx = get_dummy_cli()
        self.resource_group_parameter_name = resource_group_parameter_name
        self.apic_service_parameter_name = apic_service_parameter_name
        self.parameter_name = parameter_name
        self.apic_api_parameter_name = apic_api_parameter_name
        self.apic_version_parameter_name = apic_version_parameter_name
        self.key = key

    def create_resource(self, name, **kwargs):
        group = self._get_resource_group(**kwargs)
        service = self._get_apic_service(**kwargs)
        api = self._get_apic_api(**kwargs)
        version = self._get_apic_version(**kwargs)

        template = 'az apic api definition create -g {} -n {} --api-id {} --version-id {} --definition-id {} --title "OpenAPI"'
        cmd = template.format(group, service, api, version, name)
        print(cmd)
        self.live_only_execute(self.cli_ctx, cmd)

        self.test_class_instance.kwargs[self.key] = name
        return {self.parameter_name: name}

    def remove_resource(self, name, **kwargs):
        # ResourceGroupPreparer will delete everything
        pass

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs.get(self.resource_group_parameter_name)
        except KeyError:
            template = 'To create an API Center API a resource group is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ResourceGroupPreparer.__name__))

    def _get_apic_service(self, **kwargs):
        try:
            return kwargs.get(self.apic_service_parameter_name)
        except KeyError:
            template = 'To create an API Center API an API Center service is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ApicServicePreparer.__name__))

    def _get_apic_api(self, **kwargs):
        try:
            return kwargs.get(self.apic_api_parameter_name)
        except KeyError:
            template = 'To create an API Center Version an API Center API is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ApicApiPreparer.__name__))
        
    def _get_apic_version(self, **kwargs):
        try:
            return kwargs.get(self.apic_version_parameter_name)
        except KeyError:
            template = 'To create an API Center Definition an API Center Version is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ApicVersionPreparer.__name__))
        
class ApicDeploymentPreparer(NoTrafficRecordingPreparer, SingleValueReplacer):
    def __init__(self, name_prefix='clitest', length=24,
                 parameter_name='deployment_id', resource_group_parameter_name='resource_group',
                 apic_service_parameter_name='service_name', apic_api_parameter_name='api_id',
                 apic_version_parameter_name='version_id', apic_definition_parameter_name='definition_id',
                 apic_environment_parameter_name='environment_id', key='dep'):
        super(ApicDeploymentPreparer, self).__init__(name_prefix, length)
        self.cli_ctx = get_dummy_cli()
        self.resource_group_parameter_name = resource_group_parameter_name
        self.apic_service_parameter_name = apic_service_parameter_name
        self.parameter_name = parameter_name
        self.apic_api_parameter_name = apic_api_parameter_name
        self.apic_version_parameter_name = apic_version_parameter_name
        self.apic_definition_parameter_name = apic_definition_parameter_name
        self.apic_environment_parameter_name = apic_environment_parameter_name
        self.key = key

    def create_resource(self, name, **kwargs):
        group = self._get_resource_group(**kwargs)
        service = self._get_apic_service(**kwargs)
        api = self._get_apic_api(**kwargs)
        version = self._get_apic_version(**kwargs)
        definition = self._get_apic_definition(**kwargs)
        environment = self._get_apic_environment(**kwargs)

        template = 'az apic api deployment create -g {} -n {} --api-id {} --definition-id /workspaces/default/apis/{}/versions/{}/definitions/{} --environment-id /workspaces/default/environments/{} --deployment-id {} --title "test deployment" --server \'{{"runtimeUri":["https://example.com"]}}\''
        cmd = template.format(group, service, api, api, version, definition, environment, name)
        print(cmd)
        self.live_only_execute(self.cli_ctx, cmd)

        self.test_class_instance.kwargs[self.key] = name
        return {self.parameter_name: name}

    def remove_resource(self, name, **kwargs):
        # ResourceGroupPreparer will delete everything
        pass

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs.get(self.resource_group_parameter_name)
        except KeyError:
            template = 'To create an API Center Deployment a resource group is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ResourceGroupPreparer.__name__))

    def _get_apic_service(self, **kwargs):
        try:
            return kwargs.get(self.apic_service_parameter_name)
        except KeyError:
            template = 'To create an API Center Deployment an API Center service is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ApicServicePreparer.__name__))

    def _get_apic_api(self, **kwargs):
        try:
            return kwargs.get(self.apic_api_parameter_name)
        except KeyError:
            template = 'To create an API Center Deployment an API Center API is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ApicApiPreparer.__name__))
        
    def _get_apic_version(self, **kwargs):
        try:
            return kwargs.get(self.apic_version_parameter_name)
        except KeyError:
            template = 'To create an API Center Deployment an API Center Version is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ApicVersionPreparer.__name__))
        
    def _get_apic_definition(self, **kwargs):
        try:
            return kwargs.get(self.apic_definition_parameter_name)
        except KeyError:
            template = 'To create an API Center Deployment an API Center Definition is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ApicDefinitionPreparer.__name__))
        
    def _get_apic_environment(self, **kwargs):
        try:
            return kwargs.get(self.apic_environment_parameter_name)
        except KeyError:
            template = 'To create an API Center Deployment an API Center Environment is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise CliTestError(template.format(ApicEnvironmentPreparer.__name__))
